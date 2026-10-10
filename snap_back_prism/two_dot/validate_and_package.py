"""Verify the full revision matches the tested connector and write two A1 plates."""
import ast
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
BASE = H.parent
TRIAL = BASE / 'connector_fit_v2'
C = json.loads((H / 'parameters.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solid(mesh):
    result = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32), np.asarray(mesh.faces, np.uint32)))
    assert result.status() == mf.Error.NoError, result.status()
    return result


def clean(key):
    path = H / (key+'.stl')
    original = trimesh.load(path)
    result = solid(original).simplify(1e-5).to_mesh()
    mesh = trimesh.Trimesh(result.vert_properties[:, :3], result.tri_verts, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert mesh.area_faces.min() > 1e-10
    assert abs(mesh.volume-original.volume) < .02
    assert np.max(np.abs(mesh.bounds-original.bounds)) < .0001
    mesh.export(path)
    return mesh


keys = ['body_navy', 'body_white_face', 'snap_back']
meshes = {key: clean(key) if key == 'snap_back' else trimesh.load(H / (key+'.stl')) for key in keys}
solids = {key: solid(mesh) for key, mesh in meshes.items()}
stats = {}
for key, mesh in meshes.items():
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert mesh.area_faces.min() > 1e-10
    assert mesh.body_count == (3 if key == 'body_white_face' else 1)
    stats[key] = {'watertight': True, 'connected_solids': int(mesh.body_count),
                  'triangles': len(mesh.faces), 'volume_mm3': float(mesh.volume),
                  'sha256': sha(H / (key+'.stl'))}
body = solids['body_navy'] + solids['body_white_face']
assert len(body.decompose()) == 1
material_overlap = abs((solids['body_navy'] ^ solids['body_white_face']).volume())
seated_overlap = abs((body ^ solids['snap_back']).volume())
assert material_overlap < .01 and seated_overlap < .01
fused = body.to_mesh()
trimesh.Trimesh(fused.vert_properties[:, :3], fused.tri_verts, process=True).export(H / 'front_shell_fused.stl')

profiles = json.loads((ROOT / 'scripts/a1_topper_profiles.json').read_text())
outline = Polygon(profiles['outline'][0]['loops'][0])
tubes = unary_union([Polygon(p['loops'][0]) for p in profiles['white_tube_sections']])
bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in profiles['white_backing_bands']])


def front(mesh):
    triangles = mesh.triangles
    selected = triangles[np.all(np.abs(triangles[:, :, 2]) < 1e-7, axis=1)]
    return unary_union([Polygon(t[:, :2]) for t in selected])


actual_face = unary_union([front(meshes[key]) for key in ['body_navy', 'body_white_face']])
face_difference = actual_face.symmetric_difference(outline.difference(tubes)).area
band_difference = front(meshes['body_white_face']).symmetric_difference(bands).area
apertures = sum(p.area > .05 for p in outline.difference(actual_face).buffer(0).geoms)
assert face_difference < .05 and band_difference < .05 and apertures == 130
mouth = solid(trimesh.load(ROOT / 'pentagrammic_prism/construction/bottom_mouth.stl'))
leader = solid(trimesh.load(ROOT / 'pentagrammic_prism/construction/tree_leader_clearance_reference.stl'))
assert abs((mouth ^ (body+solids['snap_back'])).volume()) < .01
assert abs((leader ^ (body+solids['snap_back'])).volume()) < .01

# Verify the engraving in the exported solid, including the floor and exactly
# what material was removed, rather than trusting only the text cutter.
mark = C['builder_mark']
cutter_mesh = trimesh.load(H / 'construction/builder_mark_cutter.stl')
assert cutter_mesh.is_watertight and cutter_mesh.is_winding_consistent
cutter = solid(cutter_mesh)
unmarked_mesh = trimesh.load(H / 'construction/back_unmarked_reference.stl')
unmarked = solid(unmarked_mesh)
removed = unmarked-solids['snap_back']
expected_removed = unmarked ^ cutter
mark_difference = (removed-expected_removed).volume()+(expected_removed-removed).volume()
added_volume = abs((solids['snap_back']-unmarked).volume())
assert abs(mark_difference) < .01 and added_volume < .01
top = cutter_mesh.triangles[np.all(np.abs(cutter_mesh.triangles[:, :, 2]-(mark['surface_z_mm']+.2)) < 1e-5, axis=1)]
lettering = unary_union([Polygon(triangle[:, :2]) for triangle in top])
floor_triangles = meshes['snap_back'].triangles[
    np.all(np.abs(meshes['snap_back'].triangles[:, :, 2]-mark['floor_z_mm']) < 1e-5, axis=1)]
actual_floor = unary_union([Polygon(triangle[:, :2]) for triangle in floor_triangles])
floor_difference = actual_floor.symmetric_difference(lettering).area
assert floor_difference < .01, floor_difference
assert abs(cutter_mesh.extents[0]-mark['width_mm']) < 1e-4
assert abs((mark['surface_z_mm']-mark['floor_z_mm'])-mark['depth_mm']) < 1e-6
remaining_wall = mark['floor_z_mm']-C['body_rear_z_mm']
assert remaining_wall >= .59
vents = unary_union([Polygon(p['loops'][0]) for p in json.loads((ROOT / 'pentagrammic_prism/profiles.json').read_text())['rear_vents']])
assert lettering.difference(outline).area < 1e-6
assert lettering.distance(outline.boundary) > 12
assert lettering.distance(vents) > 6
glyphs = list(lettering.geoms) if lettering.geom_type == 'MultiPolygon' else [lettering]
assert all(not glyph.buffer(-.2).is_empty for glyph in glyphs)
builder_mark_check = {
    'text': mark['text'], 'font': mark['font'], 'location': 'outside of detachable rear cover',
    'width_mm': float(cutter_mesh.extents[0]), 'height_mm': float(cutter_mesh.extents[1]),
    'depth_mm': mark['depth_mm'], 'floor_z_mm': mark['floor_z_mm'],
    'remaining_wall_mm': remaining_wall, 'actual_floor_difference_mm2': floor_difference,
    'removed_geometry_difference_mm3': mark_difference, 'added_material_mm3': added_volume,
    'removed_volume_mm3': removed.volume(), 'clearance_to_outline_mm': lettering.distance(outline.boundary),
    'clearance_to_vents_mm': lettering.distance(vents), 'glyph_components_accommodate_0_4mm_tool': True,
    'cutter_sha256': sha(H / 'construction/builder_mark_cutter.stl'),
    'unmarked_reference_sha256': sha(H / 'construction/back_unmarked_reference.stl'),
}
(H / 'builder_mark_validation.json').write_text(json.dumps(builder_mark_check, indent=2)+'\n')

# Compare the actual full back, body wall, and hooks to the printed two-dot
# coupon in each clip's local coordinate system, excluding handling features.
# The comparison ends at the inner edge of the 2 mm beam relief. The star's
# existing rear vents are beyond that edge and are absent from the coupon.
comparison_depth = C['side_wall_mm'] + C['radial_fit_gap_mm'] + C['clip_beam_radial_width_mm'] + C['clip_beam_relief_mm']
patch = mf.Manifold.cube([34, comparison_depth, 8]).translate([-20, 0, 52])
tested_back = solid(trimesh.load(TRIAL / 'two_dot_back.stl')) ^ patch
tested_catch = solid(trimesh.load(TRIAL / 'two_dot_catch.stl')) ^ patch
tested_hook = solid(trimesh.load(TRIAL / 'construction/two_dot_hook.stl'))
hook_solids = []
clip_checks = []
for i, clip in enumerate(C['clips'], 1):
    center, tangent, normal = (np.asarray(clip[key]) for key in ['center_xy', 'tangent_xy', 'outward_xy'])
    transform = np.eye(4)
    transform[0, :2] = tangent
    transform[1, :2] = -normal
    transform[0, 3] = -tangent.dot(center)
    transform[1, 3] = normal.dot(center)
    local = {}
    for key in ['body_navy', 'snap_back']:
        mesh = meshes[key].copy()
        mesh.apply_transform(transform)
        local[key] = solid(mesh) ^ patch
    hook_mesh = trimesh.load(H / 'construction' / ('hook_'+str(i)+'.stl'))
    hook_solids.append(solid(hook_mesh))
    hook_mesh.apply_transform(transform)
    hook_difference = (solid(hook_mesh)-tested_hook).volume() + (tested_hook-solid(hook_mesh)).volume()
    back_difference = (local['snap_back']-tested_back).volume() + (tested_back-local['snap_back']).volume()
    catch_difference = (local['body_navy']-tested_catch).volume() + (tested_catch-local['body_navy']).volume()
    assert abs(hook_difference) < .01, (i, hook_difference)
    assert abs(back_difference) < .03, (i, back_difference)
    assert abs(catch_difference) < .03, (i, catch_difference)
    clip_checks.append({'clip': i, 'tested_hook_difference_mm3': hook_difference,
                        'tested_back_patch_difference_mm3': back_difference,
                        'tested_catch_patch_difference_mm3': catch_difference})

all_hooks = mf.Manifold.batch_boolean(hook_solids, mf.OpType.Add)
rigid_back = solids['snap_back'] - all_hooks
max_swept = 0.
for z in np.linspace(0, 6.3, 32):
    max_swept = max(max_swept, abs((body ^ rigid_back.translate([0, 0, float(z)])).volume()))
    for hook, clip in zip(hook_solids, C['clips']):
        normal = np.asarray(clip['outward_xy'])
        delta = C['maximum_assembly_deflection_mm']
        moved = hook.translate([-float(normal[0])*delta, -float(normal[1])*delta, float(z)])
        max_swept = max(max_swept, abs((body ^ moved).volume()))
assert max_swept < .01, max_swept
walls = solid(trimesh.load(H / 'construction/body_blank.stl')) - solid(trimesh.load(H / 'construction/open_cavity.stl'))
engagement = (walls ^ all_hooks).volume()
assert engagement > 1

report = {
    'status': 'passed', 'geometry': stats, 'front_shell_connected_solids': 1,
    'body_material_overlap_mm3': material_overlap, 'seated_overlap_mm3': seated_overlap,
    'original_face_difference_mm2': face_difference, 'original_white_bands_difference_mm2': band_difference,
    'matching_front_apertures': apertures, 'bottom_mouth_clear': True, 'tree_leader_reference_clear': True,
    'selected_connector': 'two_dot', 'six_clip_profile_comparisons': clip_checks,
    'clip_comparison_scope': 'Local tangent -20..14 mm, inward 0..5.35 mm, Z 52..60 mm: arm, relief, root, hook, guide and wall window; excludes rear vents beyond the relief edge and coupon handling features',
    'deflected_hook_sweep_max_overlap_mm3': max_swept,
    'hook_sweep_scope': '32 axial positions with hook heads rigidly translated 0.60 mm inward; excludes elastic forces',
    'relaxed_hook_undercut_engagement_volume_mm3': engagement,
    'selected_sample_physically_tested': True, 'full_topper_physically_tested': False,
    'retention_force_measured': False, 'thermal_tested': False, 'packages': {},
    'builder_mark': builder_mark_check,
}

# Reuse only package-writing definitions; running the baseline script would
# replace its preserved exports. Templates retain the original face colors.
source = (BASE / 'validate_and_package.py').read_text()
tree = ast.parse(source)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in {'el', 'meta', 'print_mesh', 'package'}:
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(BASE / 'validate_and_package.py'), 'exec'))
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
with zipfile.ZipFile(BASE / 'front_shell_A1.3mf') as archive:
    template = {name: archive.read(name) for name in archive.namelist()}
    original_settings = json.loads(archive.read('Metadata/project_settings.config'))
def existing_front_matches():
    """Retain a verified front package when only the rear mark changes."""
    path = H / 'front_shell_A1.3mf'
    if not path.exists():
        return False
    with zipfile.ZipFile(path) as archive:
        model = ET.fromstring(archive.read('3D/3dmodel.model'))
        settings = json.loads(archive.read('Metadata/project_settings.config'))
    mesh_objects = [obj for obj in model.findall('./{'+NS+'}resources/{'+NS+'}object')
                    if obj.find('{'+NS+'}mesh') is not None]
    if len(mesh_objects) != 2:
        return False
    for obj, key in zip(mesh_objects, ['body_navy', 'body_white_face']):
        mesh = obj.find('{'+NS+'}mesh')
        vertices = [[float(v.attrib[axis]) for axis in 'xyz'] for v in mesh.findall('.//{'+NS+'}vertex')]
        faces = [[int(f.attrib[axis]) for axis in ['v1', 'v2', 'v3']] for f in mesh.findall('.//{'+NS+'}triangle')]
        actual = solid(trimesh.Trimesh(vertices, faces, process=True))
        difference = (actual-solids[key]).volume()+(solids[key]-actual).volume()
        if abs(difference) >= .01:
            return False
    return all(str(settings[key]) == value for key, value in
               [('enable_support', '0'), ('enable_prime_tower', '1'), ('brim_width', '4.0')])


if existing_front_matches():
    report['packages']['front_shell_A1.3mf'] = {'sha256': sha(H / 'front_shell_A1.3mf'),
        'roundtrip_passed': True, 'build_objects': 1, 'support_enabled': False,
        'GUI_slice_complete': False, 'existing_matching_front_retained': True}
else:
    package('front_shell_A1.3mf', 'Two-dot topper front shell', [
        (print_mesh(meshes['body_navy']), 'Navy shell with tested catch windows', 1, [128, 128, 0]),
        (print_mesh(meshes['body_white_face']), 'Original white face bands', 2, [128, 128, 0]),
    ])
package('snap_back_A1.3mf', 'Two-dot topper detachable back', [
    (print_mesh(meshes['snap_back'], flip=True), 'White back with six preferred latches', 2, [128, 128, 0]),
], prime=False, brim=0.)
for filename in ['snap_back_A1.3mf']:
    with zipfile.ZipFile(H / filename) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    model = ET.fromstring(entries['3D/3dmodel.model'])
    for item in model.findall('{'+NS+'}metadata'):
        if item.attrib.get('name') == 'Description':
            item.text = 'Full topper using the user-preferred two-dot connector. Individual samples tested; assembled topper and thermal validation pending.'
            if filename == 'snap_back_A1.3mf':
                item.text += ' Outside rear cover includes inset christopherbrown.io builder mark, 72 mm wide and 1 mm deep.'
    entries['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(H / filename, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, value in entries.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, value)
    report['packages'][filename]['sha256'] = sha(H / filename)
(H / 'mesh_validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
