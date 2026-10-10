"""Create an inexpensive fit/lighting prototype from the same fused shell."""
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import trimesh

H = Path(__file__).resolve().parent
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
with zipfile.ZipFile(H/'roanoke_star_prism_A1.3mf') as z:
    entries = {name: z.read(name) for name in z.namelist()}
model = ET.fromstring(entries['3D/3dmodel.model'])
resources = model.find('{'+NS+'}resources')
for child in list(resources):
    resources.remove(child)

def el(parent, name, attrs=None):
    return ET.SubElement(parent, '{'+NS+'}'+name, attrs or {})
materials = el(resources, 'basematerials', {'id': '1'})
el(materials, 'base', {'name': 'White PLA', 'displaycolor': '#F0F2ECFF'})
fused = trimesh.load(H/'roanoke_star_prism.stl')
assert fused.is_watertight and fused.body_count == 1
c = json.loads((H/'parameters.json').read_text())
fused.apply_transform(trimesh.transformations.rotation_matrix(math.radians(c['print_tilt_x_deg']), [1, 0, 0]))
fused.apply_translation([0, -np.mean(fused.bounds[:, 1]), -fused.bounds[0, 2]])
obj = el(resources, 'object', {'id': '2', 'name': 'Single-color hollow shell', 'type': 'model', 'pid': '1', 'pindex': '0'})
me = el(obj, 'mesh')
vs = el(me, 'vertices', {})
for point in fused.vertices:
    el(vs, 'vertex', {k: f'{v:.8f}' for k, v in zip('xyz', point)})
ts = el(me, 'triangles', {})
for a, b, d in fused.faces:
    el(ts, 'triangle', {'v1': str(a), 'v2': str(b), 'v3': str(d)})
assembly = el(resources, 'object', {'id': '4', 'name': 'Roanoke Star single-color prototype', 'type': 'model'})
el(el(assembly, 'components', {}), 'component', {'objectid': '2'})
for metadata in model.findall('{'+NS+'}metadata'):
    if metadata.get('name') == 'Title':
        metadata.text = 'Roanoke Star - single-color fit and lighting prototype'
    if metadata.get('name') == 'Description':
        metadata.text = 'Same hollow prism and 130 holes, printed in one color. Original white-band color contrast is omitted.'

native = ET.fromstring(entries['Metadata/model_settings.config'])
obj = native.find("object[@id='4']")
obj.find("metadata[@key='name']").set('value', 'Roanoke Star single-color prototype')
obj.find('metadata[@face_count]').set('face_count', str(len(fused.faces)))
for part in list(obj.findall('part')):
    obj.remove(part)
part = ET.SubElement(obj, 'part', {'id': '2', 'subtype': 'normal_part'})
for key, value in {'name': 'Single-color hollow shell', 'extruder': '1',
                   'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'}.items():
    ET.SubElement(part, 'metadata', {'key': key, 'value': value})
ET.SubElement(part, 'mesh_stat', {'face_count': str(len(fused.faces)), 'edges_fixed': '0',
    'degenerate_facets': '0', 'facets_removed': '0', 'facets_reversed': '0', 'backwards_edges': '0'})
for key, value in {'filament_maps': '1', 'filament_volume_maps': '0',
                   'plater_name': 'Single-color hollow prism'}.items():
    native.find("plate/metadata[@key='"+key+"']").set('value', value)

project = json.loads(entries['Metadata/project_settings.config'])
overrides = project['different_settings_to_system']
for key, value in list(project.items()):
    # Printer motion arrays contain standard/quiet-mode pairs. They are not
    # filament vectors and must remain intact when reducing filament count.
    if (isinstance(value, list) and len(value) == 2
            and not key.startswith('machine_')
            and key not in {'extruder_ams_count', 'start_end_points',
                            'default_filament_colour'}):
        project[key] = [value[0]]
project['filament_colour'] = ['#F0F2EC']
project['enable_prime_tower'] = '0'
project['flush_volumes_matrix'] = [0]
project['flush_volumes_vector'] = project['flush_volumes_vector'][:2]
project['different_settings_to_system'] = [overrides[0]+';enable_prime_tower', overrides[1], overrides[-1]]
entries['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
entries['Metadata/model_settings.config'] = ET.tostring(native, encoding='utf-8', xml_declaration=True)
entries['Metadata/project_settings.config'] = json.dumps(project, indent=2).encode()
output = H/'roanoke_star_prism_A1_single_color.3mf'
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, value in entries.items():
        info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, value)
with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    m = ET.fromstring(z.read('3D/3dmodel.model'))
    me = m.find('./{'+NS+'}resources/{'+NS+'}object/{'+NS+'}mesh')
    v = [[float(e.attrib[k]) for k in 'xyz'] for e in me.findall('.//{'+NS+'}vertex')]
    f = [[int(e.attrib[k]) for k in ['v1', 'v2', 'v3']] for e in me.findall('.//{'+NS+'}triangle')]
    readback = trimesh.Trimesh(v, f, process=True)
    assert readback.is_watertight and readback.body_count == 1
    assert abs(readback.volume-fused.volume) < .01
    assert len(m.findall('.//{'+NS+'}build/{'+NS+'}item')) == 1
    assert len(json.loads(z.read('Metadata/project_settings.config'))['filament_colour']) == 1
r = {'status': 'passed', 'same_fused_shell': True, 'one_build_object': True,
     'connected_solids': 1, 'filaments': 1, 'prime_tower': False,
     'color_contrast_omitted': True, 'roundtrip_passed': True,
     'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
(H/'single_color_package_validation.json').write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(r, indent=2))
