#!/usr/bin/env python3
"""Audit a Bambu Studio G-code export against the checked-in A1 settings.

This is intentionally a text-level audit.  It does not replace Bambu Studio's
GUI layer inspection or prove that the source 3MF and the G-code came from the
same saved scene.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "scripts" / "a1_bambu_settings.json"
SOURCE_3MF = ROOT / "print_in_place" / "roanoke_star_A1.3mf"
REQUIRED_SETTINGS = {
    "printer_model": "Bambu Lab A1",
    "printer_settings_id": "Bambu Lab A1 0.4 nozzle",
    "print_settings_id": "0.20mm Standard @BBL A1",
    "nozzle_diameter": "0.4",
    "layer_height": "0.2",
    "initial_layer_print_height": "0.2",
    "wall_loops": "4",
    "top_shell_layers": "5",
    "bottom_shell_layers": "5",
    "sparse_infill_density": "15%",
    "sparse_infill_pattern": "gyroid",
    "wall_generator": "arachne",
    "enable_support": "0",
    "enable_prime_tower": "1",
    "brim_type": "no_brim",
    "curr_bed_type": "Textured PEI Plate",
}
LAYER_RE = re.compile(r"^;\s*Z_HEIGHT:\s*([0-9]+(?:\.[0-9]+)?)\s*$")
HEADER_RE = re.compile(r"^;\s*([^=]+?)\s*=\s*(.*?)\s*$")
EXTRUSION_RE = re.compile(r"\bE(-?(?:\d+(?:\.\d*)?|\.\d+))\b")


class AuditError(Exception):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def list_value(value: str) -> list[str]:
    # Bambu uses semicolons for vector values and quotes individual strings.
    values = []
    for match in re.finditer(r'"(?:[^"\\]|\\.)*"|[^;]+', value):
        item = scalar(match.group(0).strip())
        if item:
            values.append(item)
    return values


def read_header(lines: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    header: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        if not line.startswith(";"):
            break
        match = HEADER_RE.match(line)
        if match:
            header[match.group(1).strip()] = match.group(2).strip()
    if not header:
        raise AuditError("G-code has no Bambu settings header")
    return header, {key: scalar(value) for key, value in header.items()}


def parse_model_extrusion(lines: list[str]):
    """Return positive model extrusion by Z and tool, excluding wipe towers."""
    current_z: float | None = None
    current_tool: int | None = None
    current_e = 0.0
    relative_e = False
    in_object = False
    in_tower = False
    in_flush = False
    extrusion: dict[float, Counter[int]] = defaultdict(Counter)
    for line in lines:
        stripped = line.strip()
        command = stripped.split(';', 1)[0].strip()
        if stripped == "; EXECUTABLE_BLOCK_END":
            break
        if stripped.startswith("; OBJECT_ID:"):
            in_object = True
        elif stripped.startswith("; EXCLUDE_OBJECT_END"):
            in_object = False
        elif stripped == "; WIPE_TOWER_START":
            in_tower = True
        elif stripped == "; WIPE_TOWER_END":
            in_tower = False
        elif stripped == "; FLUSH_START":
            in_flush = True
        elif stripped == "; FLUSH_END":
            in_flush = False
        if command == 'M83':
            relative_e = True
        elif command == 'M82':
            relative_e = False
        elif re.match(r"^G92\b", command):
            match = EXTRUSION_RE.search(command)
            if match:
                current_e = float(match.group(1))
        match = LAYER_RE.match(stripped)
        if match:
            current_z = round(float(match.group(1)), 3)
        if re.fullmatch(r"T\d+", command):
            current_tool = int(command[1:])
        # Bambu marks the initial model filament after the A1 calibration
        # macros (which can contain special T1000 commands).
        if re.fullmatch(r";VT[01]", stripped):
            current_tool = int(stripped[3:])
        if not re.match(r"^(?:G0|G1|G2|G3)\b", command):
            continue
        match = EXTRUSION_RE.search(command)
        if not match:
            continue
        e_value = float(match.group(1))
        e_delta = e_value if relative_e else e_value - current_e
        # Track the coordinate even during purge/travel so an absolute-E move
        # after a tool change cannot inherit an obsolete extrusion position.
        current_e = current_e + e_value if relative_e else e_value
        if not (in_object and not in_tower and not in_flush and
                current_z is not None and current_tool in (0, 1)):
            continue
        # E-only priming/retraction is not deposition. Require a planar move
        # (XY) or an arc's I/J coordinates in addition to positive extrusion.
        has_xy_or_arc = bool(re.search(r"\b(?:X|Y|I|J)-?(?:\d+(?:\.\d*)?|\.\d+)", command))
        if e_delta > 0 and has_xy_or_arc:
            extrusion[current_z][current_tool] += e_delta
    if not extrusion:
        raise AuditError("no positive T0/T1 model extrusion found outside wipe-tower sections")
    return extrusion


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def audit(gcode_path: Path, source_path: Path) -> dict:
    if not gcode_path.is_file():
        raise AuditError(f"G-code file not found: {gcode_path}")
    if not source_path.is_file():
        raise AuditError(f"source 3MF not found: {source_path}")
    try:
        settings = json.loads(SETTINGS_PATH.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read {SETTINGS_PATH}: {exc}") from exc
    lines = gcode_path.read_text(errors="replace").splitlines()
    header, _ = read_header(lines)
    failures: list[str] = []

    expected_header = {}
    for key in REQUIRED_SETTINGS:
        package_value = settings.get(key)
        if isinstance(package_value, list):
            if len(package_value) != 1:
                raise AuditError(f"package setting {key!r} is not a scalar: {package_value!r}")
            package_value = package_value[0]
        expected_header[key] = str(package_value)
    for key, expected in expected_header.items():
        actual = scalar(header.get(key, ""))
        require(actual == expected, f"{key}: expected {expected!r}, found {actual or '<missing>'!r}", failures)
    actual_colours = list_value(header.get("filament_colour", ""))
    expected_colours = settings.get("filament_colour")
    require(actual_colours == expected_colours,
            f"filament_colour: expected two configured colors {expected_colours!r}, found {actual_colours!r}", failures)
    filament_ids = list_value(header.get("filament_settings_id", ""))
    require(len(filament_ids) == 2, f"filament_settings_id: expected two configured filaments, found {filament_ids!r}", failures)

    configured = {
        "printer_settings_id": settings.get("printer_settings_id"),
        "filament_settings_id": settings.get("filament_settings_id"),
        "filament_colour": settings.get("filament_colour"),
    }
    require(configured["printer_settings_id"] == scalar(header.get("printer_settings_id", "")),
            "G-code printer preset differs from current package settings", failures)
    require(configured["filament_settings_id"] == filament_ids,
            "G-code filament presets differ from current package settings", failures)
    require(configured["filament_colour"] == actual_colours,
            "G-code filament colors differ from current package settings", failures)

    extrusion = parse_model_extrusion(lines)
    z_values = sorted(extrusion)
    white_z = [z for z in z_values if extrusion[z][1] > 0]
    expected_white_z = [0.2, 0.4, 0.6, 0.8, 1.0]
    require(white_z == expected_white_z,
            f"white model deposition: expected exactly Z={expected_white_z}, found {white_z}", failures)
    require(all(extrusion[z][0] > 0 for z in expected_white_z),
            "dark model extrusion is missing from one or more of the first five layers", failures)
    dark_later = [z for z in z_values if z > 1.0 and extrusion[z][0] > 0]
    require(bool(dark_later), "dark model extrusion does not persist after the white bands", failures)
    try:
        body_dimensions = json.loads((ROOT / "print_in_place" / "blender_validation.json").read_text())["RoanokeStar_Body"]["dimensions_mm"]
        body_z = float(body_dimensions[2])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read current body height from blender_validation.json: {exc}") from exc
    layer_height = float(expected_header["layer_height"])
    expected_top_layer = round(body_z / layer_height) * layer_height
    dark_z_max = max(dark_later, default=0)
    require(abs(dark_z_max - expected_top_layer) <= layer_height + 1e-6,
            f"dark model extrusion ends at Z={dark_z_max:.3f}, outside one {layer_height:g}mm layer of profile body height {body_z:.3f}", failures)

    layer_match = re.search(r"^;\s*total layer number:\s*(\d+)", "\n".join(lines), re.MULTILINE)
    time_match = re.search(r"^;\s*model printing time:\s*(.*?);\s*total estimated time:\s*(.*?)\s*$", "\n".join(lines), re.MULTILINE)
    weight_match = re.search(r"^;\s*total filament weight \[g\]\s*:\s*(.*?)\s*$", "\n".join(lines), re.MULTILINE)
    require(layer_match is not None, "missing total layer number header", failures)
    require(time_match is not None, "missing print-time header", failures)
    require(weight_match is not None, "missing filament-weight header", failures)
    if failures:
        raise AuditError("\n".join(failures))

    return {
        "gcode_sha256": sha256(gcode_path),
        "source_3mf_sha256": sha256(source_path),
        "gcode_file": gcode_path.name,
        "source_3mf_file": source_path.name,
        "header": {
            "model_printing_time": time_match.group(1),
            "total_estimated_time": time_match.group(2),
            "total_layers": int(layer_match.group(1)),
            "filament_weight_g": [float(value) for value in weight_match.group(1).split(",")],
        },
        "model_extrusion": {
            "white_z": expected_white_z,
            "dark_z_min": min(dark_later),
            "dark_z_max": dark_z_max,
            "model_z_min": min(z_values),
            "model_z_max": max(z_values),
            "profile_body_height_mm": body_z,
            "expected_top_layer_z": expected_top_layer,
            "model_layers_with_positive_extrusion": len(z_values),
        },
        "parsed_settings": {
            **{key: scalar(header.get(key, "")) for key in REQUIRED_SETTINGS},
            "filament_colour": actual_colours,
            "filament_settings_id": filament_ids,
        },
        "checks": {
            "settings_header": "pass",
            "model_tool_extrusion": "pass",
            "white_bands_confined_to_first_five_layers": "pass",
            "dark_persists_through_socket": "pass",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gcode", type=Path, help="Bambu Studio G-code export to audit")
    parser.add_argument("--output", type=Path, help="write the passing audit JSON here")
    parser.add_argument("--source-3mf", type=Path, default=SOURCE_3MF, help="source 3MF to hash")
    args = parser.parse_args(argv)
    try:
        result = audit(args.gcode, args.source_3mf)
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: A1 sliced G-code audit")
    if args.output:
        print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
