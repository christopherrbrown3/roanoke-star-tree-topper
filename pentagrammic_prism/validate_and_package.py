"""Independently verify the live-Blender exports and make an A1 3MF."""
import hashlib
import json
import math
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
C = json.loads((HERE/'parameters.json').read_text())
P = json.loads((ROOT/'scripts/a1_topper_profiles.json').read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def solid(mesh):
    out = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32),
                              np.asarray(mesh.faces, np.uint32)))
    assert out.status() == mf.Error.NoError, out.status()
    return out

def stats(mesh):
    assert mesh.is_watertight and mesh.is_winding_consistent
    assert mesh.volume > 0 and mesh.area_faces.min() > 1e-10
    assert len(np.unique(np.sort(mesh.faces, axis=1), axis=0)) == len(mesh.faces)
    return {'watertight': True, 'winding_consistent': True,
            'triangles': len(mesh.faces), 'connected_solids': int(mesh.body_count),
            'volume_mm3': float(mesh.volume),
            'minimum_triangle_area_mm2': float(mesh.area_faces.min())}

parts = [trimesh.load(HERE/f) for f in ['dark_shell.stl', 'white_details.stl']]
fused = trimesh.load(HERE/'roanoke_star_prism.stl')
assert parts[0].body_count == fused.body_count == 1
assert parts[1].body_count == 4  # Three original face bands plus the internal reflector.
material_stats = list(map(stats, parts))
fused_stats = stats(fused)
ss = list(map(solid, parts))
fs = solid(fused)
union = ss[0]+ss[1]
overlap = (ss[0] ^ ss[1]).volume()
coverage = ((union-fs)+(fs-union)).volume()
assert abs(overlap) < .01 and abs(coverage) < .02, (overlap, coverage)

outline = Polygon(P['outline'][0]['loops'][0])
tubes = unary_union([Polygon(p['loops'][0]) for p in P['white_tube_sections']])
bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in P['white_backing_bands']])

def front(mesh):
    triangles = mesh.triangles
    selected = triangles[np.all(np.abs(triangles[:, :, 2]) < 1e-7, axis=1)]
    return unary_union([Polygon(t[:, :2]) for t in selected])

actual_front = unary_union([front(p) for p in parts])
actual_white = front(parts[1])
front_diff = actual_front.symmetric_difference(outline.difference(tubes)).area
white_diff = actual_white.symmetric_difference(bands).area
actual_slots = outline.difference(actual_front).buffer(0)
assert front_diff < .05 and white_diff < .05, (front_diff, white_diff)
# Original outline rounding is float64, exported vertices are float32. Tiny
# contour slivers are measured above rather than counted as extra apertures.
large_slots = [p for p in actual_slots.geoms if p.area > .05]
assert len(large_slots) == C['tube_apertures'] == 130
assert unary_union(large_slots).symmetric_difference(tubes).area < .05

clearance_checks = {}
for key in ['inner_cavity', 'white_tube_sections', 'bottom_mouth', 'rear_vents']:
    cutter = solid(trimesh.load(HERE/'construction'/f'{key}.stl'))
    intersection = (fs ^ cutter).volume()
    assert abs(intersection) < .01, (key, intersection)
    clearance_checks[key+'_material_intrusion_mm3'] = intersection

# A slender tree leader can enter 100 mm through the mouth without a socket.
# This is a clearance test, not a claim that a rigid 100 mm cylinder fits the
# star's narrower waist. The broad inlet is intended for compressible foliage.
vertices, faces = [], []
count = 128
for y, radius in [(-43, 16.95), (57, 6.95)]:
    vertices.extend([(radius*math.cos(i*2*math.pi/count), y,
                      31.2+radius*math.sin(i*2*math.pi/count)) for i in range(count)])
for i in range(count):
    j = (i+1) % count
    faces.extend([(i, j, count+j), (i, count+j, count+i)])
for i in range(1, count-1):
    faces.extend([(0, i+1, i), (count, count+i, count+i+1)])
mandrel = trimesh.Trimesh(vertices, faces, process=True)
trimesh.repair.fix_normals(mandrel)
mandrel_overlap = (fs ^ solid(mandrel)).volume()
assert abs(mandrel_overlap) < .01
mandrel.export(HERE/'construction/tree_leader_clearance_reference.stl')

angle = math.radians(C['print_tilt_x_deg'])
transform = trimesh.transformations.rotation_matrix(angle, [1, 0, 0])
oriented = fused.copy()
oriented.apply_transform(transform)
shift = np.array([0, -np.mean(oriented.bounds[:, 1]), -oriented.bounds[0, 2]])
oriented.apply_translation(shift)
print_parts = []
for p in parts:
    m = p.copy()
    m.apply_transform(transform)
    m.apply_translation(shift)
    print_parts.append(m)
assert np.max(oriented.extents) < 210
bad = (oriented.triangles_center[:, 2] > .2) & (
    oriented.face_normals[:, 2] < -math.sin(math.radians(45.05)))
overhang_area = float(oriented.area_faces[bad].sum())
assert overhang_area < .01, overhang_area

report = {
    'status': 'passed', 'variant': 'Hollow pentagrammic prism',
    'construction': 'Native booleans and STL exports through Blender MCP, then canonical meshes returned to Blender',
    'dimensions_mm': fused.extents.tolist(),
    'print_dimensions_mm': oriented.extents.tolist(),
    'dark_material': material_stats[0], 'white_material': material_stats[1],
    'fused_object': fused_stats,
    'material_overlap_mm3': overlap, 'material_coverage_difference_mm3': coverage,
    'front_difference_from_original_except_tubes_mm2': front_diff,
    'white_bands_difference_from_original_mm2': white_diff,
    'matching_open_tube_apertures': len(large_slots),
    'tube_aperture_area_mm2': tubes.area,
    'bottom_opening_width_mm': C['bottom_opening_width_mm'],
    'bottom_opening_clear_depth_mm': C['clear_depth_mm'],
    'bottom_opening_shape': C['opening_shape'],
    'inner_waist_clear_width_mm': outline.buffer(-C['side_wall_mm']).intersection(
        LineString([(-110, -18), (110, -18)])).length,
    'tree_leader_reference': {'length_mm': 100, 'diameters_mm': [33.9, 13.9],
                              'material_collision_mm3': mandrel_overlap},
    'clearance_checks': clearance_checks,
    'print_tilt_x_deg': C['print_tilt_x_deg'],
    'surface_area_exceeding_45_05_deg_overhang_mm2': overhang_area,
    'solid_PLA_material_estimate_g': float(fused.volume*.00124),
    'physical_print_tested': False, 'tree_fit_tested': False,
    'thermal_tested': False, 'incandescent_compatibility_verified': False,
    'illumination_uniformity_tested': False,
    'source_profile_sha256': digest(ROOT/'scripts/a1_topper_profiles.json'),
    'export_hashes': {name: digest(HERE/name) for name in
                      ['dark_shell.stl', 'white_details.stl', 'roanoke_star_prism.stl']},
}

baseline = Path('/tmp/roanoke_prism_original_hashes.json')
if baseline.exists():
    originals = json.loads(baseline.read_text())
    changed = [name for name, expected in originals.items()
               if not (ROOT/name).exists() or digest(ROOT/name) != expected]
    assert not changed, 'Original files changed: '+str(changed)
    report['original_file_preservation'] = {'checked_files': len(originals), 'changed_files': []}

# Bambu-native multipart metadata preserves one assembled print and its two
# filament assignments. The package stores the proposed 45-degree orientation.
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
def el(parent, name, attrs=None, text=None):
    e = ET.SubElement(parent, '{'+NS+'}'+name, attrs or {})
    e.text = text
    return e

model = ET.Element('{'+NS+'}model', {'unit': 'millimeter',
    '{http://www.w3.org/XML/1998/namespace}lang': 'en-US',
    'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
for key, value in {
    'Application': 'BambuStudio-02.05.00.66', 'BambuStudio:3mfVersion': '1',
    'Title': 'Roanoke Star | Hollow prism | One piece',
    'Designer': 'christopherrbrown3 | christopherbrown.io',
    'License': 'CC BY-NC-SA 4.0',
    'Description': '200 mm original face; 130 open tube slots; 60 mm hollow prism; 100 mm lower V mouth. Physical fit and heat tests pending.',
}.items():
    el(model, 'metadata', {'name': key}, value)
resources = el(model, 'resources')
materials = el(resources, 'basematerials', {'id': '1'})
el(materials, 'base', {'name': 'Navy PLA', 'displaycolor': '#142338FF'})
el(materials, 'base', {'name': 'White PLA', 'displaycolor': '#F0F2ECFF'})
part_names = ['Dark hollow shell', 'White face bands and interior reflector']
for resource_id, name, m in zip([2, 3], part_names, print_parts):
    obj = el(resources, 'object', {'id': str(resource_id), 'name': name,
         'type': 'model', 'pid': '1', 'pindex': str(resource_id-2)})
    me = el(obj, 'mesh')
    verts = el(me, 'vertices')
    for point in m.vertices:
        el(verts, 'vertex', {k: f'{v:.8f}' for k, v in zip('xyz', point)})
    triangles = el(me, 'triangles')
    for a, b, c in m.faces:
        el(triangles, 'triangle', {'v1': str(a), 'v2': str(b), 'v3': str(c)})
obj = el(resources, 'object', {'id': '4', 'type': 'model', 'name': 'Roanoke Star hollow prism'})
components = el(obj, 'components')
for i in [2, 3]:
    el(components, 'component', {'objectid': str(i)})
build = el(model, 'build')
placement = '1 0 0 0 1 0 0 0 1 128 116 0'
el(build, 'item', {'objectid': '4', 'transform': placement})

settings = ET.Element('config')
def metadata(parent, key, value):
    return ET.SubElement(parent, 'metadata', {'key': key, 'value': str(value)})
assembly = ET.SubElement(settings, 'object', {'id': '4'})
metadata(assembly, 'name', 'Roanoke Star hollow prism')
metadata(assembly, 'extruder', 1)
ET.SubElement(assembly, 'metadata', {'face_count': str(sum(len(m.faces) for m in print_parts))})
for resource_id, filament, name, m in zip([2, 3], [1, 2], part_names, print_parts):
    part = ET.SubElement(assembly, 'part', {'id': str(resource_id), 'subtype': 'normal_part'})
    metadata(part, 'name', name)
    metadata(part, 'extruder', filament)
    metadata(part, 'matrix', '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    ET.SubElement(part, 'mesh_stat', {'face_count': str(len(m.faces)),
        'edges_fixed': '0', 'degenerate_facets': '0', 'facets_removed': '0',
        'facets_reversed': '0', 'backwards_edges': '0'})
plate = ET.SubElement(settings, 'plate')
for key, value in {'plater_id': 1, 'plater_name': 'Hollow prism - 45 degree tilt',
    'locked': 'false', 'bed_type': 'Textured PEI Plate',
    'filament_map_mode': 'Auto For Flush', 'filament_maps': '1 1',
    'filament_volume_maps': '0 0'}.items():
    metadata(plate, key, value)
instance = ET.SubElement(plate, 'model_instance')
metadata(instance, 'object_id', 4)
metadata(instance, 'instance_id', 0)
assemble = ET.SubElement(settings, 'assemble')
ET.SubElement(assemble, 'assemble_item', {'object_id': '4', 'instance_id': '0',
               'transform': placement, 'offset': '0 0 0'})

project = json.loads((ROOT/'scripts/a1_bambu_settings.json').read_text())
updates = {'wall_loops': '3', 'brim_type': 'outer_only', 'brim_width': '10',
    'brim_object_gap': '0', 'enable_support': '1', 'support_type': 'tree(auto)',
    'support_on_build_plate_only': '1', 'support_threshold_angle': '30',
    'wipe_tower_x': ['20'], 'wipe_tower_y': ['215']}
project.update(updates)
process_keys = set(project['different_settings_to_system'][0].split(';'))
process_keys.update(updates)
project['different_settings_to_system'][0] = ';'.join(sorted(process_keys))
(HERE/'a1_prism_settings.json').write_text(json.dumps(project, indent=2)+'\n')

content_types = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/><Default Extension="txt" ContentType="text/plain"/></Types>'
rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
archive = HERE/'roanoke_star_prism_A1.3mf'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    def write(name, data):
        info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, data)
    write('[Content_Types].xml', content_types)
    write('_rels/.rels', rels)
    write('3D/3dmodel.model', ET.tostring(model, encoding='utf-8', xml_declaration=True))
    write('Metadata/model_settings.config', ET.tostring(settings, encoding='utf-8', xml_declaration=True))
    write('Metadata/project_settings.config', json.dumps(project, indent=2))
    write('Metadata/LICENSE.txt', (ROOT/'LICENSE').read_bytes())

with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    loaded = ET.fromstring(z.read('3D/3dmodel.model'))
    assert len(loaded.findall('.//{'+NS+'}build/{'+NS+'}item')) == 1
    for obj, expected in zip(loaded.findall('./{'+NS+'}resources/{'+NS+'}object')[:2], print_parts):
        me = obj.find('{'+NS+'}mesh')
        v = [[float(e.attrib[k]) for k in 'xyz'] for e in me.findall('.//{'+NS+'}vertex')]
        f = [[int(e.attrib[k]) for k in ['v1', 'v2', 'v3']] for e in me.findall('.//{'+NS+'}triangle')]
        reopened = trimesh.Trimesh(v, f, process=True)
        assert reopened.is_watertight and abs(reopened.volume-expected.volume) < .01
    native = ET.fromstring(z.read('Metadata/model_settings.config'))
    assignments = {int(p.get('id')): int(p.find("metadata[@key='extruder']").get('value'))
                   for p in native.findall('object/part')}
    assert assignments == {2: 1, 3: 2}
report['package'] = {'sha256': digest(archive), 'one_build_object': True,
                      'filament_assignments': assignments, 'roundtrip_passed': True,
                      'slicer_validation_complete': False}
slice_evidence = HERE/'slicer_validation.json'
if slice_evidence.exists():
    evidence = json.loads(slice_evidence.read_text()).get('two_color', {})
    report['package']['slicer_validation_complete'] = (
        evidence.get('package_sha256') == digest(archive)
        and evidence.get('status') == 'sliced_successfully')
(HERE/'mesh_validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
