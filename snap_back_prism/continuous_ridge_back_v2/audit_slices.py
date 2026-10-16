"""Audit the saved Bambu Studio slice for the continuous-ridge back.

Usage: python3 audit_slices.py /path/to/back.gcode.3mf

The check confirms slicer settings and extrusion presence in all six fixed tab
cross-sections. Presence is geometric evidence only; it does not predict fit,
insertion force, PLA strain, retention, or durability.
"""
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh
from shapely.affinity import translate
from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def setting(gcode, key):
    match = re.search(r"^; " + re.escape(key) + r" = (.*)$", gcode, re.M)
    assert match, f"missing G-code setting: {key}"
    return match.group(1)


def extruding_midpoints(gcode):
    layer, x, y, relative_e = 0, 0.0, 0.0, False
    points = {}
    for line in gcode.splitlines():
        if line.startswith("; layer num/total_layer_count:"):
            layer = int(line.split(":", 1)[1].split("/", 1)[0])
            points.setdefault(layer, [])
        code = line.split(";", 1)[0].strip()
        if code == "M83":
            relative_e = True
        elif code == "M82":
            relative_e = False
        if not re.match(r"^G(?:0|1|2|3)\s", code):
            continue
        values = {k: float(v) for k, v in re.findall(
            r"([XYE])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))", code)}
        nx, ny = values.get("X", x), values.get("Y", y)
        if layer and values.get("E", 0) > 0 and ("X" in values or "Y" in values):
            assert relative_e, "this audit expects relative E motion"
            points[layer].append(((x + nx) / 2, (y + ny) / 2))
        x, y = nx, ny
    assert relative_e, "G-code did not use relative E"
    return points


def audit(path, source_project=None):
    path = Path(path).resolve()
    source_project = Path(source_project or HERE / "continuous_ridge_back_A1.3mf").resolve()
    with zipfile.ZipFile(path) as archive:
        gcode_names = [name for name in archive.namelist() if name.endswith(".gcode")]
        assert len(gcode_names) == 1, gcode_names
        gcode = archive.read(gcode_names[0]).decode("utf-8")
        plate = json.loads(archive.read("Metadata/plate_1.json"))
        slice_info = archive.read("Metadata/slice_info.config").decode("utf-8")
    # Sliced Bambu exports omit the model assembly transform, so read it from
    # the exact source project used to generate this slice.
    with zipfile.ZipFile(source_project) as project:
        project_settings = project.read("Metadata/model_settings.config").decode("utf-8")
        project_config = json.loads(project.read("Metadata/project_settings.config"))
    expected_color = project_config["filament_colour"][0]

    expected = {
        "printer_model": "Bambu Lab A1",
        "nozzle_diameter": "0.4",
        "layer_height": "0.2",
        "initial_layer_print_height": "0.2",
        "curr_bed_type": "Textured PEI Plate",
        "enable_support": "0",
        "enable_prime_tower": "0",
        "brim_width": "0",
    }
    actual = {key: setting(gcode, key) for key in expected}
    assert actual == expected, actual
    assert "M140 S65" in gcode and "M190 S65; ensure bed temp" in gcode
    assert expected_color in setting(gcode, "filament_colour").split(";")
    assert plate["filament_colors"] == [expected_color]
    assert plate["filament_ids"] == [0] and plate["first_extruder"] == 0
    assert plate["bed_type"] == "textured_plate"
    assert np.isclose(plate["nozzle_diameter"], 0.4)
    assert np.isclose(plate["bbox_objects"][0]["layer_height"], 0.2)
    assert re.search(r'<metadata key="support_used" value="false"', slice_info)
    assert not re.search(r"^; FEATURE: (?:Support|Prime tower)", gcode, re.M)

    layer_count = int(re.search(r"^; total layer number: (\d+)$", gcode, re.M).group(1))
    points = extruding_midpoints(gcode)
    root = ET.fromstring(project_settings)
    assemble = root.find("./assemble/assemble_item")
    transform = [float(value) for value in assemble.get("transform").split()]
    assert np.allclose(transform[:9], [1, 0, 0, 0, 1, 0, 0, 0, 1])
    plate_translation = transform[9:12]
    assert np.allclose(plate_translation, [128, 128, 0])
    printable = trimesh.load(HERE / "continuous_ridge_back_print.stl", force="mesh")
    expected_bbox = [printable.bounds[0, 0] + plate_translation[0],
                     printable.bounds[0, 1] + plate_translation[1],
                     printable.bounds[1, 0] + plate_translation[0],
                     printable.bounds[1, 1] + plate_translation[1]]
    assert np.allclose(plate["bbox_all"], expected_bbox, atol=0.01)
    checks = []
    for i in range(1, 7):
        mesh = trimesh.load(HERE / f"construction/fixed_tab_{i}.stl", force="mesh")
        # The sliced project's build transform is identity rotation and a
        # 128,128,0 mm plate translation. The printable STL flips Y and Z.
        mesh = mesh.copy()
        vertices = mesh.vertices.copy()
        vertices[:, 1] *= -1
        vertices[:, 2] = 60 - vertices[:, 2]
        mesh.vertices = vertices
        first = max(1, int(np.floor(mesh.bounds[0, 2] / 0.2)) + 1)
        last = min(layer_count, int(np.ceil(mesh.bounds[1, 2] / 0.2)))
        layers = []
        for layer in range(first, last + 1):
            z = 0.2 * (layer - 0.5)
            section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if section is None:
                continue
            polygons = [translate(Polygon(loop[:, :2]), plate_translation[0], plate_translation[1])
                        for loop in section.discrete
                        if Polygon(loop[:, :2]).area > 0.01]
            if not polygons:
                continue
            layer_points = np.asarray(points.get(layer, []))
            counts = []
            for polygon in polygons:
                x0, y0, x1, y1 = polygon.bounds
                near = layer_points[(layer_points[:, 0] >= x0 - 0.25) &
                                    (layer_points[:, 0] <= x1 + 0.25) &
                                    (layer_points[:, 1] >= y0 - 0.25) &
                                    (layer_points[:, 1] <= y1 + 0.25)]
                counts.append(sum(polygon.buffer(0.25).covers(Point(point))
                                  for point in near))
            assert counts and min(counts) > 0, (i, layer, counts)
            layers.append({"layer": layer, "motion_midpoints_per_section": counts})
        assert layers
        checks.append({
            "tab": i,
            "layers_checked": len(layers),
            "first_layer": layers[0]["layer"],
            "last_layer": layers[-1]["layer"],
            "minimum_motion_midpoints_per_section": min(
                min(item["motion_midpoints_per_section"]) for item in layers),
        })

    time = re.search(r"^; model printing time: (.*); total estimated time: (.*)$", gcode, re.M)
    weight = float(re.search(r"^; total filament weight \[g\] : ([0-9.]+)$", gcode, re.M).group(1))
    warnings = re.findall(r'<warning msg="([^"]+)" level="([^"]+)"', slice_info)
    report = {
        "status": "passed",
        "source": "Bambu Studio native slice; saved G-code project",
        "slice_file": str(path),
        "slice_sha256": sha(path),
        "source_project": str(source_project),
        "source_project_sha256": sha(source_project),
        "gcode_entry": gcode_names[0],
        "settings": actual,
        "bed_temperature_c": 65,
        "project_filament": {"slot": 1, "color": expected_color, "type": "PLA"},
        "support_enabled": False,
        "build_plate_transform": transform,
        "layer_count": layer_count,
        "maximum_height_mm": 7.6,
        "estimated_model_time": time.group(1),
        "estimated_total_time": time.group(2),
        "estimated_filament_g": weight,
        "warnings": [{"message": msg, "level": int(level)} for msg, level in warnings],
        "fixed_tab_extrusion_presence": {
            "all_six_tabs_passed": len(checks) == 6,
            "method": "Positive-E G-code motion midpoints within each tab's sliced STL cross-section, expanded 0.25 mm.",
            "limits": "Presence only; does not measure full coverage or mechanical performance.",
            "tabs": checks,
        },
        "print_sent": False,
        "physical_fit_tested": False,
        "pla_deformation_validated": False,
    }
    (HERE / "slicer_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    print(json.dumps(audit(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None), indent=2))
