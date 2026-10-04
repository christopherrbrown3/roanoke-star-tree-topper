"""Verify real diffuser thickness and package white/black A1 print projects."""
import ast
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
BASE = H.parent
SOURCE = BASE / 'two_dot'
C = json.loads((H / 'parameters.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solid(mesh):
    result = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32), np.asarray(mesh.faces, np.uint32)))
    assert result.status() == mf.Error.NoError, result.status()
    return result


def mesh_of(value):
    result = value.to_mesh()
    return trimesh.Trimesh(result.vert_properties[:, :3], result.tri_verts, process=True)


def difference(a, b):
    return abs((a-b).volume())+abs((b-a).volume())


def extrusion(shape, z0, z1):
    polygons = [shape] if shape.geom_type == 'Polygon' else list(shape.geoms)
    solids = []
    for polygon in polygons:
        if polygon.area < 1e-8:
            continue
        mesh = trimesh.creation.extrude_polygon(polygon, z1-z0, engine='earcut')
        mesh.apply_translation([0, 0, z0])
        solids.append(solid(mesh))
    return mf.Manifold.batch_boolean(solids, mf.OpType.Add)


def front(mesh, z=0):
    triangles = mesh.triangles
    faces = triangles[np.all(np.abs(triangles[:, :, 2]-z) < 1e-5, axis=1)]
    return unary_union([Polygon(t[:, :2]) for t in faces])


meshes = {}
solids = {}
stats = {}
for key in ['body_black', 'body_white_diffused', 'test_black', 'test_white']:
    original = trimesh.load(H / (key+'.stl'))
    value = solid(original).simplify(1e-5)
    mesh = mesh_of(value)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert mesh.area_faces.min() > 1e-10
    assert abs(mesh.volume-original.volume) < .02
    assert np.max(np.abs(mesh.bounds-original.bounds)) < .0001
    mesh.export(H / (key+'.stl'))
    meshes[key] = mesh
    solids[key] = solid(mesh)
    stats[key] = {'watertight': True, 'connected_solids': int(mesh.body_count),
                  'triangles': len(mesh.faces), 'volume_mm3': float(mesh.volume),
                  'sha256': sha(H / (key+'.stl'))}

original_black = solid(trimesh.load(SOURCE / 'body_navy.stl'))
original_white = solid(trimesh.load(SOURCE / 'body_white_face.stl'))
back = solid(trimesh.load(SOURCE / 'snap_back.stl'))
profiles = json.loads((ROOT / 'scripts/a1_topper_profiles.json').read_text())
outline = Polygon(profiles['outline'][0]['loops'][0])
windows = unary_union([Polygon(p['loops'][0]) for p in profiles['white_tube_sections']])
bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in profiles['white_backing_bands']])
continuous = []
for profile in profiles['white_backing_bands']:
    holes = [Polygon(loop) for loop in profile['loops'][1:]]
    central_star = max(holes, key=lambda polygon: polygon.area)
    continuous.append(Polygon(profile['loops'][0], [central_star.exterior.coords]))
continuous = unary_union(continuous)
assert len(continuous.geoms) == 3 and all(len(p.interiors) == 1 for p in continuous.geoms)
white_region = extrusion(continuous, 0, 1)
expected_black = original_black-white_region
black_difference = difference(solids['body_black'], expected_black)
assert black_difference < .01
membranes = extrusion(windows, 0, .4)
expected_white = white_region-extrusion(windows, .4, 1)
white_difference = difference(solids['body_white_diffused'], expected_white)
assert white_difference < .01
assert abs((solids['body_white_diffused'] ^ extrusion(windows, .4001, 4)).volume()) < .01
assert len(windows.geoms) == 130
assert len(solids['body_white_diffused'].decompose()) == len(expected_white.decompose()) == 3
front_white_difference = front(meshes['body_white_diffused']).symmetric_difference(continuous).area
membrane_floor_difference = front(meshes['body_white_diffused'], .4).symmetric_difference(windows).area
assert front_white_difference < .05 and membrane_floor_difference < .05
former_outlines = continuous.difference(unary_union([bands, windows]))
visible_outline_black_area = front(meshes['body_black']).intersection(former_outlines).area
assert visible_outline_black_area < .01
body = solids['body_black']+solids['body_white_diffused']
assert len(body.decompose()) == 1
assert abs((solids['body_black'] ^ solids['body_white_diffused']).volume()) < .01
assert abs((body ^ back).volume()) < .01
combined_shape_difference = difference(body, original_black+original_white+membranes)
assert combined_shape_difference < .01
face_difference = front(mesh_of(body)).symmetric_difference(outline).area
assert face_difference < .05
mesh_of(body).export(H / 'front_shell_fused.stl')

sample = box(-30, -20, 30, 20)
sample_volume = extrusion(sample, -.1, 4)
border = extrusion(box(-32, -22, 32, 22).difference(sample), 0, 4)
assert difference(solids['test_black'], (expected_black ^ sample_volume)+border) < .01
assert difference(solids['test_white'], expected_white ^ sample_volume) < .01
assert abs((solids['test_black'] ^ solids['test_white']).volume()) < .01
test_fused = solids['test_black']+solids['test_white']
assert len(test_fused.decompose()) == 1
assert np.max(np.abs(mesh_of(test_fused).extents-[64, 44, 4])) < .0001
assert front(mesh_of(test_fused)).symmetric_difference(box(-32, -22, 32, 22)).area < .01

report = {'status': 'passed', 'geometry': stats,
          'black_vs_original_shell_minus_continuous_white_face_difference_mm3': black_difference,
          'white_vs_three_continuous_stars_with_0_4mm_windows_difference_mm3': white_difference,
          'combined_shape_vs_previous_diffused_front_difference_mm3': combined_shape_difference,
          'continuous_white_star_count': 3, 'visible_bulb_outline_black_area_mm2': visible_outline_black_area,
          'former_black_outline_area_replaced_mm2': former_outlines.area,
          'diffused_windows': 130, 'diffuser_thickness_mm': .4, 'printed_layers_at_0_2mm': 2,
          'front_white_profile_difference_mm2': front_white_difference,
          'membrane_inside_surface_difference_mm2': membrane_floor_difference,
          'filled_front_outline_difference_mm2': face_difference,
          'front_shell_connected_solids': 1, 'test_sample_connected_solids': 1,
          'test_sample_size_mm': [64, 44, 4], 'test_sample_real_scale': True,
          'test_sample_complete_windows': C['print_sample']['complete_windows'],
          'two_dot_back_and_builder_mark': 'unchanged; use ../two_dot/snap_back_A1.3mf',
          'source_back_sha256': sha(SOURCE / 'snap_back.stl'),
          'physical_light_transmission_tested': False, 'packages': {}}

# Extract package-writing helpers only; never execute the preserved baseline build.
source = (BASE / 'validate_and_package.py').read_text()
for node in ast.parse(source).body:
    if isinstance(node, ast.FunctionDef) and node.name in {'el', 'meta', 'print_mesh', 'package'}:
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(BASE / 'validate_and_package.py'), 'exec'))
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
with zipfile.ZipFile(SOURCE / 'front_shell_A1.3mf') as archive:
    template = {name: archive.read(name) for name in archive.namelist()}
    original_settings = json.loads(archive.read('Metadata/project_settings.config'))
# These projects explicitly use white filament 1 and black filament 2.
original_settings.update(filament_colour=['#FFFFFF', '#000000'],
    flush_volumes_matrix=['0', '300', '600', '0'],
    flush_volumes_vector=['140', '140', '140', '140'])


def white_black_package(filename, title, parts):
    package(filename, title, parts, prime=True, brim=0.)
    with zipfile.ZipFile(H / filename) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    model = ET.fromstring(entries['3D/3dmodel.model'])
    material = model.find('./{'+NS+'}resources/{'+NS+'}basematerials')
    for item, (name, colour) in zip(material, [('White PLA A1', '#FFFFFFFF'), ('Black PLA A2', '#000000FF')]):
        item.set('name', name)
        item.set('displaycolor', colour)
    for item in model.findall('{'+NS+'}metadata'):
        if item.attrib.get('name') == 'Description':
            item.text = 'Three continuous white stars without visible bulb outlines. Hidden 130 bulb windows have 0.4 mm white skins; white surround is 1 mm with black baffles behind it. White filament 1 / AMS A1; black filament 2 / AMS A2. Physical diffusion test pending.'
    entries['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(H / filename, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 4, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    report['packages'][filename]['sha256'] = sha(H / filename)
    report['packages'][filename]['project_filaments'] = {'1': 'white / AMS A1', '2': 'black / AMS A2'}


white_black_package('diffused_front_A1.3mf', 'Continuous white star front', [
    (print_mesh(meshes['body_white_diffused']), 'Three continuous white stars and hidden 0.4 mm bulbs', 1, [128, 128, 0]),
    (print_mesh(meshes['body_black']), 'Black shell with matching two-dot catches', 2, [128, 128, 0]),
])
white_black_package('diffuser_test_A1.3mf', 'Continuous star diffuser test', [
    (print_mesh(meshes['test_white']), 'Continuous white face and hidden two-layer bulbs A1', 1, [128, 128, 0]),
    (print_mesh(meshes['test_black']), 'Black frame and 2 mm handling border A2', 2, [128, 128, 0]),
])
(H / 'mesh_validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
