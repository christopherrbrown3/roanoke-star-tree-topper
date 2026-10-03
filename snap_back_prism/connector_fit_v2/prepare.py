"""Prepare two connector trials after the first print stopped short of seating."""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
(HERE / "construction").mkdir(exist_ok=True)
COMMON = {
    "wall_mm": 1.2,
    "cap_mm": 1.6,
    "guide_gap_mm": 0.55,
    "beam_width_mm": 1.6,
    "beam_length_mm": 30.0,
    "beam_relief_mm": 2.0,
    "lead_in_length_mm": 1.6,
    "hook_width_mm": 8.0,
    "window_width_mm": 9.2,
    "window_z_mm": [52.2, 55.1],
    "wall_top_z_mm": 58.4,
    "hook_tip_z_mm": 52.4,
    "hook_peak_z_mm": [54.0, 54.4],
    "guide_depth_mm": 3.0,
    "test_base_xy_mm": [48.0, 20.0],
    "grip_width_mm": 18.0,
    "grip_height_mm": 1.2,
    "grip_edge_bevel_mm": 1.0,
}
TRIALS = [
    {"id": "one_dot", "dots": 1, "engagement_mm": 0.30, "description": "Gentler catch"},
    {"id": "two_dot", "dots": 2, "engagement_mm": 0.50, "description": "Firmer catch"},
]


def rounded_rect(x0, y0, x1, y1, radius=0.35):
    return box(x0 + radius, y0 + radius, x1 - radius, y1 - radius).buffer(radius, quad_segs=8)


def extrude(shape, z0, z1, name):
    polygons = [shape] if shape.geom_type == "Polygon" else list(shape.geoms)
    meshes = []
    for polygon in polygons:
        mesh = trimesh.creation.extrude_polygon(polygon, height=z1-z0, engine="earcut")
        mesh.apply_translation([0, 0, z0])
        assert mesh.is_watertight and mesh.volume > 0
        meshes.append(mesh)
    trimesh.util.concatenate(meshes).export(HERE / "construction" / (name + ".stl"))


def across_x(profile, x0, x1, name):
    mesh = trimesh.creation.extrude_polygon(profile, height=x1-x0, engine="earcut")
    vertices = mesh.vertices.copy()
    mesh.vertices = np.column_stack([vertices[:, 2] + x0, vertices[:, 0], vertices[:, 1]])
    assert mesh.is_watertight and mesh.volume > 0
    mesh.export(HERE / "construction" / (name + ".stl"))


outer = COMMON["wall_mm"] + COMMON["guide_gap_mm"]
inner = outer + COMMON["beam_width_mm"]
notch = unary_union([
    rounded_rect(-18, -3, 13, outer, radius=0.6),
    rounded_rect(-18, inner, 13, inner + COMMON["beam_relief_mm"], radius=0.6),
    box(12, -3, 13, inner + COMMON["beam_relief_mm"]),
])
for trial in TRIALS:
    key = trial["id"]
    dots = unary_union([Point(-10 + 3.5*i, 11).buffer(1.0, quad_segs=12)
                        for i in range(trial["dots"])])
    extrude(rounded_rect(-24, 0, 24, 20, radius=1), 48.5, 50.1, key + "_floor")
    extrude(box(-24, 0, 24, COMMON["wall_mm"]), 50, 58.4, key + "_wall")
    extrude(box(3.4, -0.5, 12.6, outer + 0.1), *COMMON["window_z_mm"], key + "_window")
    extrude(dots, 50.05, 50.5, key + "_floor_dots")
    extrude(rounded_rect(-9, 16, 9, 20, radius=0.5), 50.05, 51.3, key + "_floor_grip")
    across_x(Polygon([(19, 48.4), (20.2, 48.4), (20.2, 49.7), (19, 48.5)]),
             -9, 9, key + "_floor_bevel")
    extrude(rounded_rect(-24, 0, 24, 20, radius=1).difference(notch), 58.4, 60, key + "_cap")
    extrude(box(-24, outer, 24, inner).difference(box(-19, 0, 14, inner + 2.0)),
            55.4, 58.5, key + "_rim")
    extrude(dots, 58.0, 58.45, key + "_cap_dots")
    extrude(rounded_rect(-9, 16, 9, 20, radius=0.5), 57.2, 58.45, key + "_cap_grip")
    across_x(Polygon([(19, 60.1), (20.2, 60.1), (20.2, 58.8), (19, 60.0)]),
             -9, 9, key + "_cap_bevel")
    nose = COMMON["wall_mm"] - trial["engagement_mm"]
    return_length = outer - nose  # Preserve the printable 45-degree return ramp.
    profile = Polygon([
        (inner, 52.4), (outer, 52.4), (nose, 54.0), (nose, 54.4),
        (outer, 54.4 + return_length), (outer, 58.5), (inner, 58.5),
    ])
    across_x(profile, 4, 12, key + "_hook")
    trial["minimum_nominal_hook_displacement_mm"] = trial["engagement_mm"]
    trial["entry_ramp_radial_travel_mm"] = return_length

manifest = {
    "revision": 2,
    "reported_baseline_result": "User reported: stops short or needs too much force; does not quite snap.",
    "reported_handling_issue": "The small pieces were hard to get off the plate. Maybe make the bases a little bigger for the tests",
    "baseline_sample_sha256": hashlib.sha256((HERE.parent / "connector_sample_A1.3mf").read_bytes()).hexdigest(),
    "common": COMMON,
    "trials": TRIALS,
    "new_trials_physically_tested": (HERE / "physical_fit.json").exists(),
}
if (HERE / "physical_fit.json").exists():
    manifest["physical_fit"] = json.loads((HERE / "physical_fit.json").read_text())
(HERE / "parameters.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
