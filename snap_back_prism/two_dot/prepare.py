"""Adapt the user-preferred two-dot connector to the full star perimeter."""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from shapely.affinity import affine_transform
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
(H / 'construction').mkdir(exist_ok=True)
(H / 'previews').mkdir(exist_ok=True)
ROOT = H.parents[1]
BASE = H.parent
TRIAL = BASE / 'connector_fit_v2'
S = json.loads((ROOT / 'scripts/a1_topper_profiles.json').read_text())
P = json.loads((ROOT / 'pentagrammic_prism/profiles.json').read_text())
tested = json.loads((TRIAL / 'parameters.json').read_text())
feedback = json.loads((TRIAL / 'physical_fit.json').read_text())
assert feedback['selected_trial'] == 'two_dot'
common = tested['common']
selected = next(t for t in tested['trials'] if t['id'] == 'two_dot')
wall = common['wall_mm']
outer = wall + common['guide_gap_mm']
inner = outer + common['beam_width_mm']
rear = common['wall_top_z_mm']
C = {
    'revision': 'full topper with preferred two-dot connector',
    'depth_mm': 60., 'front_wall_mm': 4., 'side_wall_mm': wall,
    'back_wall_mm': common['cap_mm'], 'body_rear_z_mm': rear,
    'bottom_opening_width_mm': 100., 'clip_count': 6,
    'clip_beam_radial_width_mm': common['beam_width_mm'],
    'clip_beam_effective_length_mm': common['beam_length_mm'],
    'clip_beam_relief_mm': common['beam_relief_mm'],
    'radial_fit_gap_mm': common['guide_gap_mm'],
    'retention_engagement_mm': selected['engagement_mm'],
    'nominal_clip_deflection_mm': selected['engagement_mm'],
    'maximum_assembly_deflection_mm': selected['engagement_mm'] + .1,
    'entry_ramp_radial_travel_mm': outer - (wall - selected['engagement_mm']),
    'clip_tip_z_mm': common['hook_tip_z_mm'],
    'clip_nose_start_z_mm': common['hook_peak_z_mm'][0],
    'clip_nose_end_z_mm': common['hook_peak_z_mm'][1],
    'clip_stem_return_z_mm': common['hook_peak_z_mm'][1] + outer - (wall - selected['engagement_mm']),
    'clip_hook_width_mm': common['hook_width_mm'],
    'catch_window_z_mm': common['window_z_mm'],
    'catch_window_width_mm': common['window_width_mm'],
    'locating_rim_depth_mm': common['guide_depth_mm'],
    'body_print_orientation': 'front face down',
    'lid_print_orientation': 'outer face down; clips up',
    'support_enabled': False, 'selected_sample_physically_tested': True,
    'full_topper_physically_tested': False, 'thermal_tested': False,
    'user_feedback': feedback['user_feedback'],
    'test_filament': feedback['print_filament'],
    'source_profile_sha256': hashlib.sha256((ROOT / 'scripts/a1_topper_profiles.json').read_bytes()).hexdigest(),
    'tested_hook_sha256': hashlib.sha256((TRIAL / 'construction/two_dot_hook.stl').read_bytes()).hexdigest(),
    'clips': json.loads((BASE / 'parameters.json').read_text())['clips'],
}
outline = Polygon(S['outline'][0]['loops'][0])
inside = outline.buffer(-wall, join_style=2)
tubes = unary_union([Polygon(p['loops'][0]) for p in S['white_tube_sections']])
bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in S['white_backing_bands']])
mouth = Polygon(P['bottom_mouth'][0]['loops'][0])
vents = unary_union([Polygon(p['loops'][0]) for p in P['rear_vents']])


def local_geom(shape, clip):
    c, t, n = (np.asarray(clip[k]) for k in ['center_xy', 'tangent_xy', 'outward_xy'])
    return affine_transform(shape, [t[0], -n[0], t[1], -n[1], c[0], c[1]])


def rounded_rect(x0, y0, x1, y1, radius=.6):
    return box(x0+radius, y0+radius, x1-radius, y1-radius).buffer(radius, quad_segs=8)


def extrude(shape, z0, z1, key):
    polygons = [shape] if shape.geom_type == 'Polygon' else list(shape.geoms)
    meshes = []
    for polygon in polygons:
        if polygon.area < 1e-8:
            continue
        mesh = trimesh.creation.extrude_polygon(polygon, height=z1-z0, engine='earcut')
        mesh.apply_translation([0, 0, z0])
        assert mesh.is_watertight and mesh.volume > 0
        meshes.append(mesh)
    trimesh.util.concatenate(meshes).export(H / 'construction' / (key+'.stl'))


notch = unary_union([
    rounded_rect(-18, -3, 13, outer),
    rounded_rect(-18, inner, 13, inner+common['beam_relief_mm']),
    box(12, -3, 13, inner+common['beam_relief_mm']),
])
notches = unary_union([local_geom(notch, c) for c in C['clips']])
window = box(3.4, -.5, 12.6, outer+.1)
windows = unary_union([local_geom(window, c) for c in C['clips']])
rim = outline.buffer(-outer, join_style=2).difference(outline.buffer(-inner, join_style=2))
rim = rim.difference(mouth).difference(unary_union([
    local_geom(box(-19, -2, 14, inner+2.), c) for c in C['clips']
]))
lid = outline.difference(vents).difference(notches)
assert lid.geom_type == 'Polygon' and lid.is_valid
for clip in C['clips']:
    assert local_geom(box(-18, outer, 12, inner), clip).difference(outline).area < 1e-7

extrude(outline, 0, rear, 'body_blank')
extrude(inside, C['front_wall_mm'], C['depth_mm'], 'open_cavity')
extrude(tubes, -.2, 4.2, 'tube_holes')
extrude(mouth, 4, 60, 'bottom_mouth')
extrude(windows, *C['catch_window_z_mm'], 'catch_windows')
extrude(bands, 0, 1, 'white_face')
extrude(lid, rear, 60, 'lid_blank')
extrude(rim, rear-common['guide_depth_mm'], rear+.1, 'locating_rim')

# Transform the exact hook mesh that was used for the successful two-dot test.
tested_hook = trimesh.load(TRIAL / 'construction/two_dot_hook.stl')
for i, clip in enumerate(C['clips'], 1):
    c, t, n = (np.asarray(clip[k]) for k in ['center_xy', 'tangent_xy', 'outward_xy'])
    mesh = tested_hook.copy()
    xy = c[None, :] + mesh.vertices[:, 0, None]*t[None, :] - mesh.vertices[:, 1, None]*n[None, :]
    mesh.vertices = np.column_stack([xy, mesh.vertices[:, 2]])
    if mesh.volume < 0:
        mesh.invert()
    assert mesh.is_watertight and mesh.volume > 0
    mesh.export(H / 'construction' / ('hook_'+str(i)+'.stl'))

(H / 'parameters.json').write_text(json.dumps(C, indent=2)+'\n')
print(json.dumps(C, indent=2))
