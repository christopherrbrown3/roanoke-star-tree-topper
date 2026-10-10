"""Narrow the continuous white frames without moving any v2 diffuser window.

The physical shell, tree opening, catches, and marked back are retained.
Pass --keep-white-outer-edge to retain the previous white perimeter treatment.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import trimesh

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
BASE = H.parent
SOURCE = BASE / 'proportions_v2'
MARGIN = 1.0
SKIN = .4
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
spec = importlib.util.spec_from_file_location('v2_geometry_helpers', SOURCE / 'build.py')
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
solid, mesh_of, extrusion, difference, front = (
    common.solid, common.mesh_of, common.extrusion, common.difference, common.front)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def profile(poly):
    return {'loops': [list(poly.exterior.coords)[:-1]] +
            [list(ring.coords)[:-1] for ring in poly.interiors]}


def main():
    global report, template, original_settings
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keep-white-outer-edge', action='store_true')
    keep_edge = parser.parse_args().keep_white_outer_edge
    (H / 'previews').mkdir(exist_ok=True)
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in [
        SOURCE / name for name in ['parameters.json', 'profiles.json',
        'body_black.stl', 'body_white_diffused.stl', 'front_shell_fused.stl',
        'snap_back.stl', 'snap_back_A1.3mf', 'front_shell_A1.3mf']]}
    params = json.loads((SOURCE / 'parameters.json').read_text())
    old_profiles = json.loads((SOURCE / 'profiles.json').read_text())
    paths = np.asarray(params['six_paths_mm'])
    outline = Polygon(old_profiles['outline'][0]['loops'][0])
    windows = [Polygon(p['loops'][0]) for p in old_profiles['white_tube_sections']]
    all_windows = unary_union(windows)
    assert len(windows) == len(all_windows.geoms) == 130
    bands = []
    for i in [0, 2, 4]:
        outside = outline if keep_edge and i == 0 else Polygon(paths[i]).buffer(MARGIN, quad_segs=16)
        band = outside.difference(Polygon(paths[i+1]).buffer(-MARGIN, quad_segs=16))
        assert band.is_valid and len(band.interiors) == 1
        bands.append(band)
    white_face = unary_union(bands)
    assert len(white_face.geoms) == 3
    assert all_windows.difference(white_face).area < 1e-7
    minimum_window_margin = min(w.distance(white_face.boundary) for w in windows)
    # Rounded polygons are faceted; nominal 0.1 mm clearance measures
    # approximately 0.0987 mm at some end-cap vertices.
    assert minimum_window_margin > .098
    profiles = {'outline': old_profiles['outline'],
                'white_backing_bands': [profile(p) for p in bands],
                'white_tube_sections': old_profiles['white_tube_sections']}
    (H / 'profiles.json').write_text(json.dumps(profiles, separators=(',', ':'))+'\n')
    fused_mesh = trimesh.load(SOURCE / 'front_shell_fused.stl')
    fused = solid(fused_mesh)
    white = extrusion(white_face, 0, 1)-extrusion(all_windows, SKIN, 1.1)
    black = fused-white
    assert len(white.decompose()) == 3
    values = {'body_black': black, 'body_white_diffused': white}
    meshes, stats, canonicalization = {}, {}, {}
    for key, value in values.items():
        raw = mesh_of(value.simplify(1e-5))
        canonical = solid(raw)
        tolerance = 1e-4 if key == 'body_black' else 0.
        if tolerance:
            canonical = canonical.set_tolerance(tolerance).simplify(tolerance)
        mesh = mesh_of(canonical)
        assert abs(mesh.volume-raw.volume) < .01
        assert np.max(abs(mesh.bounds-raw.bounds)) < .0001
        assert difference(solid(mesh), value) < .01
        meshes[key] = mesh
        mesh.export(H / (key+'.stl'))
        stats[key] = {'watertight': True, 'triangles': len(mesh.faces),
                      'connected_solids': int(mesh.body_count),
                      'volume_mm3': float(mesh.volume), 'sha256': sha(H / (key+'.stl'))}
        canonicalization[key] = {'export_tolerance_mm': tolerance,
                                'before_triangles': len(raw.faces), 'after_triangles': len(mesh.faces)}
    final_black, final_white = [solid(meshes[key]) for key in values]
    assert abs((final_black ^ final_white).volume()) < .01
    assert difference(final_black+final_white, fused) < .01
    white_face_diff = front(meshes['body_white_diffused'], 0).symmetric_difference(white_face).area
    window_floor_diff = front(meshes['body_white_diffused'], SKIN).symmetric_difference(all_windows).area
    assert max(white_face_diff, window_floor_diff) < .05
    membrane = extrusion(all_windows, 0, SKIN)
    assert difference(final_white ^ extrusion(all_windows, -.1, 4.1), membrane) < .01
    back = solid(trimesh.load(SOURCE / 'snap_back.stl'))
    assert abs((fused ^ back).volume()) < .01
    for name in ['front_shell_fused.stl', 'snap_back.stl', 'snap_back_A1.3mf']:
        shutil.copyfile(SOURCE / name, H / name)
        assert sha(H / name) == sha(SOURCE / name)
    # Face-treatment widths are measured normal to the straight shoulder.
    widths = [float(paths[i, 1, 1]-paths[i+1, 1, 1]+2*MARGIN) for i in [0, 2, 4]]
    if keep_edge:
        widths[0] += 2.2-MARGIN
    gaps = [float(paths[i, 1, 1]-paths[i+1, 1, 1]-2*MARGIN) for i in [1, 3]]
    minimum_gaps = [bands[i].distance(bands[i+1]) for i in [0, 1]]
    assert min(minimum_gaps) > 2.8
    params.update(revision='thinner white frames and wider visible gaps, based on daylight frame faces',
        profile_file='profiles.json', source_profile_sha256=sha(H / 'profiles.json'),
        previous_v2_profile_sha256=sha(SOURCE / 'profiles.json'),
        white_internal_margin_mm=MARGIN, outer_white_silhouette_margin_mm=2.2 if keep_edge else MARGIN,
        preserve_outer_white_edge=keep_edge, nominal_black_outer_border_mm=0. if keep_edge else 1.2,
        white_band_widths_at_shoulders_mm=widths,
        shoulder_and_lower_clear_gaps_between_white_bands_mm=gaps,
        minimum_clear_gaps_between_white_bands_mm=minimum_gaps,
        minimum_white_margin_beyond_hidden_windows_mm=minimum_window_margin,
        centerline_paths_changed_from_v2=False, hidden_windows_changed_from_v2=False,
        source_black_mesh_sha256=sha(SOURCE / 'body_black.stl'),
        revised_geometry_physically_tested=False)
    params['unlit_face'].pop('black_outline_area_replaced_mm2', None)
    (H / 'parameters.json').write_text(json.dumps(params, indent=2)+'\n')
    report = {'status': 'passed', 'geometry': stats, 'canonicalization': canonicalization,
        'continuous_white_star_count': 3, 'diffused_windows': 130,
        'diffuser_thickness_mm': SKIN, 'layers_at_0_2mm': 2,
        'white_band_widths_at_shoulders_mm': widths,
        'shoulder_and_lower_clear_gaps_between_white_bands_mm': gaps,
        'minimum_clear_gaps_between_white_bands_mm': minimum_gaps,
        'minimum_white_margin_beyond_hidden_windows_mm': minimum_window_margin,
        'white_face_difference_mm2': white_face_diff, 'window_floor_difference_mm2': window_floor_diff,
        'fused_shell_byte_identical_to_v2': True, 'marked_back_byte_identical': True,
        'seated_back_collision_mm3': abs((fused ^ back).volume()),
        'originals_and_v2_unchanged': source_hashes, 'packages': {}}
    package_source = BASE / 'validate_and_package.py'
    for node in ast.parse(package_source.read_text()).body:
        if isinstance(node, ast.FunctionDef) and node.name in {'el', 'meta', 'print_mesh', 'package'}:
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(package_source), 'exec'), globals())
    ET.register_namespace('', NS)
    with zipfile.ZipFile(SOURCE / 'front_shell_A1.3mf') as archive:
        template = {name: archive.read(name) for name in archive.namelist()}
        original_settings = json.loads(archive.read('Metadata/project_settings.config'))
    package('front_shell_A1.3mf', 'Roanoke thinner frames spacing v3', [
        (print_mesh(meshes['body_white_diffused']), 'Thinner continuous white stars and unchanged 0.4 mm diffuser floors A1', 1, [128, 128, 0]),
        (print_mesh(meshes['body_black']), 'Black shell and tested two-dot catches A2', 2, [128, 128, 0]),
    ], prime=True, brim=0.)
    with zipfile.ZipFile(H / 'front_shell_A1.3mf') as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    model = ET.fromstring(entries['3D/3dmodel.model'])
    materials = model.find('./{'+NS+'}resources/{'+NS+'}basematerials')
    for item, (name, color) in zip(materials, [('White PLA A1', '#FFFFFFFF'), ('Black PLA A2', '#000000FF')]):
        item.set('name', name); item.set('displaycolor', color)
    for item in model.findall('{'+NS+'}metadata'):
        if item.attrib.get('name') == 'Description':
            item.text = 'Thinner continuous white frames and wider dark gaps. Original v2 light windows and physical shell retained. White filament 1 / A1, black filament 2 / A2. Fits unchanged christopherbrown.io marked two-dot back. Draft spacing treatment, not physically tested.'
    entries['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(H / 'front_shell_A1.3mf', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    report['packages']['front_shell_A1.3mf']['sha256'] = sha(H / 'front_shell_A1.3mf')
    assert all(sha(ROOT / name) == value for name, value in source_hashes.items())
    (H / 'mesh_validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'originals_and_v2_unchanged'}, indent=2))


if __name__ == '__main__':
    main()
