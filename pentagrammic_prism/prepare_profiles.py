"""Prepare the hollow prism without writing to the existing A1 release."""
import hashlib
import json
from pathlib import Path

import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / 'scripts/a1_topper_profiles.json'
S = json.loads(SOURCE.read_text())

CONFIG = {
    'depth_mm': 60.0,
    'front_thickness_mm': 4.0,
    'side_wall_mm': 1.2,
    'rear_thickness_mm': 1.6,
    'front_white_depth_mm': 1.0,
    'interior_white_depth_mm': 0.8,
    'bottom_opening_width_mm': 100.0,
    'print_tilt_x_deg': 45.0,
    'assembly_required': False,
    'tube_apertures': 130,
    'tube_aperture_width_mm': 1.8,
    'source_profile_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
}

outline = Polygon(S['outline'][0]['loops'][0])
inside = outline.buffer(-CONFIG['side_wall_mm'], join_style=2)
tubes = unary_union([Polygon(p['loops'][0]) for p in S['white_tube_sections']])
assert inside.geom_type == 'Polygon' and inside.is_valid
assert tubes.difference(inside).area < 1e-8, 'Side walls would block the original tube apertures'

# The mouth follows the lower reentrant V rather than adding a socket under
# the original silhouette. Only its inward-facing rim is removed. The front,
# rear, and exterior edges of both lower points stay intact.
half_width = CONFIG['bottom_opening_width_mm'] / 2
lower_v_center_y = -47.85642076013411
lower_v_slope = -0.8239687491660907
mouth_overlap_mm = 4.0
mouth = Polygon([
    (-half_width, -130), (half_width, -130),
    (half_width, lower_v_center_y + lower_v_slope * half_width + mouth_overlap_mm),
    (0, lower_v_center_y + mouth_overlap_mm),
    (-half_width, lower_v_center_y + lower_v_slope * half_width + mouth_overlap_mm),
])

vent_centers = [(-6, 55), (6, 55), (-4, 70), (4, 70),
                (-20, 20), (20, 20), (-20, -12), (20, -12)]
vents = unary_union([Polygon([(x-3, y), (x, y-4), (x+3, y), (x, y+4)])
                     for x, y in vent_centers])
assert vents.difference(inside).area < 1e-8

def profile(geom):
    polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    out = []
    for p in polys:
        v, f = trimesh.creation.triangulate_polygon(p, engine='earcut')
        out.append({'v': v.tolist(), 'f': f.tolist(),
                    'loops': [list(p.exterior.coords)[:-1]] +
                             [list(h.coords)[:-1] for h in p.interiors]})
    return out

profiles = {k: S[k] for k in ['outline', 'white_tube_sections', 'white_backing_bands']}
profiles.update(inner_cavity=profile(inside), bottom_mouth=profile(mouth),
                rear_vents=profile(vents), inner_reflector=profile(inside.difference(vents)))
CONFIG['clear_depth_mm'] = CONFIG['depth_mm'] - CONFIG['front_thickness_mm'] - CONFIG['rear_thickness_mm']
CONFIG['outline_bounds_mm'] = list(outline.bounds)
CONFIG['tube_to_inside_wall_clearance_mm'] = tubes.distance(inside.boundary)
CONFIG['bottom_mouth_center_y_mm'] = lower_v_center_y
CONFIG['rear_vent_count'] = len(vent_centers)
CONFIG['rear_vent_area_mm2'] = vents.area
CONFIG['opening_shape'] = '100 mm wide, V-shaped mouth between the original lower points; not a 100 mm diameter circular bore'
HERE.mkdir(exist_ok=True)
(HERE/'previews').mkdir(exist_ok=True)
(HERE/'profiles.json').write_text(json.dumps(profiles, separators=(',', ':')))
(HERE/'parameters.json').write_text(json.dumps(CONFIG, indent=2) + '\n')

# Native STL import is available in Blender MCP safe mode. These are simple
# source extrusions; the hollow shell and material partition booleans are
# performed in the live Blender scene, through MCP.
(HERE/'construction').mkdir(exist_ok=True)
def extrusion(geom, z0, z1, key):
    polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    meshes = []
    for p in polys:
        m = trimesh.creation.extrude_polygon(p, height=z1-z0, engine='earcut')
        m.apply_translation([0, 0, z0])
        assert m.is_watertight and m.is_winding_consistent
        meshes.append(m)
    trimesh.util.concatenate(meshes).export(HERE/'construction'/f'{key}.stl')

bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in S['white_backing_bands']])
rear_start = CONFIG['depth_mm']-CONFIG['rear_thickness_mm']
extrusion(outline, 0, CONFIG['depth_mm'], 'outline')
extrusion(inside, CONFIG['front_thickness_mm'], rear_start, 'inner_cavity')
extrusion(tubes, -.2, CONFIG['front_thickness_mm']+.2, 'white_tube_sections')
extrusion(mouth, CONFIG['front_thickness_mm'], rear_start, 'bottom_mouth')
extrusion(vents, rear_start-.2, CONFIG['depth_mm']+.2, 'rear_vents')
extrusion(bands, 0, CONFIG['front_white_depth_mm'], 'white_backing_bands')
extrusion(inside.difference(vents), rear_start,
          rear_start+CONFIG['interior_white_depth_mm'], 'inner_reflector')
print(json.dumps(CONFIG, indent=2))
