"""Correct the continuous diffuser face while preserving the tested enclosure.

Only the two inner upper triangles and white band margins change. Earlier
models, the original research coordinates, and the marked back are read-only.
"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon
from shapely.ops import substring, unary_union

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
BASE = H.parent
SOURCE = BASE / 'diffused'
BACK = BASE / 'two_dot'
MARGIN = 1.4
SKIN = .4
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solid(mesh):
    value = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32),
                                np.asarray(mesh.faces, np.uint32)))
    assert value.status() == mf.Error.NoError, value.status()
    return value


def mesh_of(value):
    result = value.to_mesh()
    mesh = trimesh.Trimesh(result.vert_properties[:, :3], result.tri_verts, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert mesh.area_faces.min() > 1e-10
    return mesh


def difference(a, b):
    return abs((a-b).volume()) + abs((b-a).volume())


def extrusion(shape, z0, z1):
    polys = [shape] if shape.geom_type == 'Polygon' else list(shape.geoms)
    values = []
    for polygon in polys:
        if polygon.area < 1e-8:
            continue
        mesh = trimesh.creation.extrude_polygon(polygon, z1-z0, engine='earcut')
        mesh.apply_translation([0, 0, z0])
        values.append(solid(mesh))
    return mf.Manifold.batch_boolean(values, mf.OpType.Add)


def front(mesh, z):
    faces = mesh.triangles[np.all(np.abs(mesh.triangles[:, :, 2]-z) < 1e-5, axis=1)]
    return unary_union([Polygon(face[:, :2]) for face in faces])


def headings(points):
    edges = np.roll(points, -1, axis=0)-points
    return np.degrees(np.arctan2(edges[:, 1], edges[:, 0]))


def offset(points, distance):
    edges = np.roll(points, -1, axis=0)-points
    normals = np.column_stack([edges[:, 1], -edges[:, 0]])
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    displacement = np.asarray([
        np.linalg.solve([normals[i-1], normals[i]], [distance, distance])
        for i in range(10)])
    return points + displacement


def profile(polygon):
    return {'loops': [list(polygon.exterior.coords)[:-1]] +
            [list(hole.coords)[:-1] for hole in polygon.interiors]}


def main():
    global report, template, original_settings
    (H / 'previews').mkdir(exist_ok=True)
    source_profiles = ROOT / 'scripts/a1_topper_profiles.json'
    source_measurements = ROOT / 'print_in_place/profile_measurements.json'
    research = ROOT / 'research/photographic_paths.json'
    old_report = json.loads(source_measurements.read_text())
    old = np.asarray(old_report['six_paths_mm'])
    raw = np.asarray(json.loads(research.read_text())['six_paths_mm'])
    assert sha(source_profiles) == json.loads((SOURCE / 'parameters.json').read_text())['source_profile_sha256']
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in [
        source_profiles, source_measurements, research,
        SOURCE / 'body_black.stl', SOURCE / 'body_white_diffused.stl',
        BACK / 'snap_back.stl', BACK / 'snap_back_A1.3mf']}

    # Restore the photo-derived apex and shoulder x coordinates only. Keep the
    # established horizontal shoulder heights and all lower vertices. Derive
    # each frame's paired row from that frame's own lines, so its two tracks
    # remain parallel without forcing every frame to share one apex angle.
    distances = old_report['parallel_path_correction']['offsets_from_outer_path_mm']
    paths = []
    upper_checks = []
    for i, name in [(0, 'outer'), (2, 'middle'), (4, 'inner')]:
        outer = old[i].copy()
        if i:
            outer[0, 1] = raw[i, 0, 1]
            outer[1, 0] = raw[i, 1, 0]
            outer[9, 0] = raw[i, 9, 0]
        gap = distances[i+1]-distances[i]
        inner = offset(outer, gap)
        assert max(abs(headings(outer)-headings(inner))) < 1e-10
        assert np.max(abs(outer[2:9]-old[i, 2:9])) < 1e-10
        assert np.max(abs(inner[2:9]-old[i+1, 2:9])) < 1e-10
        for path in [outer, inner]:
            assert Polygon(path).is_valid
            assert np.allclose(path * [-1, 1], path[[0, 9, 8, 7, 6, 5, 4, 3, 2, 1]], atol=1e-10)
        paths.extend([outer, inner])
        upper_checks.append({'frame': name, 'old_apex_y_mm': float(old[i, 0, 1]),
            'new_apex_y_mm': float(outer[0, 1]),
            'apex_raise_mm': float(outer[0, 1]-old[i, 0, 1]),
            'upper_point_height_mm': float(outer[0, 1]-outer[1, 1]),
            'reference_upper_point_height_mm': float(raw[i, 0, 1]-raw[i, 1, 1]),
            'paired_centerline_normal_spacing_mm': gap,
            'lower_vertex_max_change_mm': float(np.max(abs(inner[2:9]-old[i+1, 2:9])))})

    original_profiles = json.loads(source_profiles.read_text())
    outline = Polygon(original_profiles['outline'][0]['loops'][0])
    bands = []
    for i in [0, 2, 4]:
        # Retain the outermost white silhouette; reduce internal margins.
        outside = outline if i == 0 else Polygon(paths[i]).buffer(MARGIN, quad_segs=16)
        band = outside.difference(Polygon(paths[i+1]).buffer(-MARGIN, quad_segs=16))
        assert band.is_valid and band.geom_type == 'Polygon' and len(band.interiors) == 1
        bands.append(band)
    continuous = unary_union(bands)
    assert continuous.geom_type == 'MultiPolygon' and len(continuous.geoms) == 3
    minimum_gaps = [bands[i].distance(bands[i+1]) for i in [0, 1]]
    assert min(minimum_gaps) > 2.
    lower_gaps = [distances[2]-distances[1]-2*MARGIN,
                  distances[4]-distances[3]-2*MARGIN]

    # Regenerate the same 130 hidden bulb sections along the corrected tracks.
    # Counts, 1.8 mm tube width, 1.2 mm interruptions, and round ends are retained.
    fractions = [[.25, .5, .75], [.25, .5, .75], [.25, .5, .75],
                 [1/3, 2/3], [.5], [.5]]
    sections = []
    schedule = []
    for k, points in enumerate(paths):
        lengths = np.linalg.norm(np.roll(points, -1, axis=0)-points, axis=1)
        cumulative = np.r_[0, np.cumsum(lengths)]
        perimeter = cumulative[-1]
        cuts = []
        for edge, length in enumerate(lengths):
            positions = fractions[k] if edge < 5 else [1-q for q in reversed(fractions[k])]
            cuts.extend(float(cumulative[edge]+q*length) for q in positions)
            schedule.append({'path': k+1, 'edge': edge+1, 'fractions': positions})
        cuts.sort()
        doubled = LineString(points.tolist()+points.tolist()+[points[0].tolist()])
        for j, start in enumerate(cuts):
            end = cuts[(j+1) % len(cuts)] + (perimeter if j == len(cuts)-1 else 0)
            line = substring(doubled, start+1.5, end-1.5)
            assert line.length > 4
            window = line.buffer(.9, quad_segs=10, cap_style=1, join_style=1)
            assert window.is_valid and window.geom_type == 'Polygon'
            sections.append(window)
    windows = unary_union(sections)
    assert len(sections) == len(windows.geoms) == 130
    assert windows.difference(continuous).area < 1e-7
    assert min(window.distance(continuous.boundary) for window in sections) > .49
    profiles = {'outline': [profile(outline)],
                'white_backing_bands': [profile(p) for p in bands],
                'white_tube_sections': [profile(p) for p in sections]}
    (H / 'profiles.json').write_text(json.dumps(profiles, separators=(',', ':'))+'\n')

    previous_black = solid(trimesh.load(SOURCE / 'body_black.stl'))
    previous_white = solid(trimesh.load(SOURCE / 'body_white_diffused.stl'))
    previous_fused = previous_black + previous_white
    # Fill the old face windows, then cut corrected ones. Nothing above the
    # 4 mm front wall is changed, including catches, cavity, and tree entrance.
    blank = previous_fused + extrusion(outline, 0, 4)
    corrected_fused = blank - extrusion(windows, SKIN, 4.1)
    corrected_white = extrusion(continuous, 0, 1) - extrusion(windows, SKIN, 1.1)
    corrected_black = corrected_fused - corrected_white
    assert len(corrected_white.decompose()) == 3
    assert len(corrected_fused.decompose()) == 1
    assert abs((corrected_black ^ corrected_white).volume()) < .01
    assert difference(corrected_black+corrected_white, corrected_fused) < .01

    meshes = {}
    canonicalization = {}
    for key, value in [('body_black', corrected_black),
                       ('body_white_diffused', corrected_white),
                       ('front_shell_fused', corrected_fused)]:
        raw_mesh = mesh_of(value.simplify(1e-5))
        # Recast to the actual float32 export coordinates before triangulation.
        # At the stepped Z=1 color interface, a 0.0001 mm simplification removes
        # numeric slivers. The exported result is checked in Blender at zero
        # intersection epsilon, rather than excluding near-boundary candidates.
        canonical = solid(raw_mesh)
        tolerance = 1e-4 if key == 'body_black' else 0.
        if tolerance:
            canonical = canonical.set_tolerance(tolerance).simplify(tolerance)
        mesh = mesh_of(canonical)
        assert abs(mesh.volume-raw_mesh.volume) < .01
        assert np.max(abs(mesh.bounds-raw_mesh.bounds)) < .0001
        assert difference(solid(mesh), value) < .01
        meshes[key] = mesh
        canonicalization[key] = {'export_tolerance_mm': tolerance,
            'before_triangles': len(raw_mesh.faces), 'after_triangles': len(mesh.faces),
            'volume_change_mm3': float(mesh.volume-raw_mesh.volume)}
    final_black = solid(meshes['body_black'])
    final_white = solid(meshes['body_white_diffused'])
    assert abs((final_black ^ final_white).volume()) < .01
    assert difference(final_black+final_white, corrected_fused) < .01
    # Independent exported surface checks verify all hidden window floors.
    white_face_difference = front(meshes['body_white_diffused'], 0).symmetric_difference(continuous).area
    window_floor_difference = front(meshes['body_white_diffused'], SKIN).symmetric_difference(windows).area
    full_face_difference = front(meshes['front_shell_fused'], 0).symmetric_difference(outline).area
    assert max(white_face_difference, window_floor_difference, full_face_difference) < .05
    window_interiors = extrusion(windows, SKIN+.0001, 4.1)
    assert abs((corrected_fused ^ window_interiors).volume()) < .01
    membranes = extrusion(windows, 0, SKIN)
    assert difference(corrected_white ^ extrusion(windows, -.1, 4.1), membranes) < .01
    unchanged_region = mf.Manifold.cube([240, 240, 70]).translate([-120, -120, 4.001])
    enclosure_difference = difference(previous_fused ^ unchanged_region,
                                      corrected_fused ^ unchanged_region)
    assert enclosure_difference < .01
    back = solid(trimesh.load(BACK / 'snap_back.stl'))
    seated_overlap = abs((corrected_fused ^ back).volume())
    assert seated_overlap < .01
    mouth = solid(trimesh.load(ROOT / 'pentagrammic_prism/construction/bottom_mouth.stl'))
    leader = solid(trimesh.load(ROOT / 'pentagrammic_prism/construction/tree_leader_clearance_reference.stl'))
    assert abs((mouth ^ (corrected_fused+back)).volume()) < .01
    assert abs((leader ^ (corrected_fused+back)).volume()) < .01
    assert np.max(abs(meshes['front_shell_fused'].bounds-trimesh.load(SOURCE / 'front_shell_fused.stl').bounds)) < .0001
    stats = {}
    for key, mesh in meshes.items():
        mesh.export(H / (key+'.stl'))
        stats[key] = {'watertight': True, 'triangles': len(mesh.faces),
                      'connected_solids': int(mesh.body_count),
                      'volume_mm3': float(mesh.volume), 'sha256': sha(H / (key+'.stl'))}
    shutil.copyfile(BACK / 'snap_back.stl', H / 'snap_back.stl')
    shutil.copyfile(BACK / 'snap_back_A1.3mf', H / 'snap_back_A1.3mf')
    assert sha(H / 'snap_back.stl') == sha(BACK / 'snap_back.stl')
    assert sha(H / 'snap_back_A1.3mf') == sha(BACK / 'snap_back_A1.3mf')

    parameters = json.loads((SOURCE / 'parameters.json').read_text())
    parameters.update(revision='corrected inner upper points and clearer white-band spacing',
        profile_file='profiles.json', source_profile_sha256=sha(H / 'profiles.json'),
        original_profile_sha256=sha(source_profiles), six_paths_mm=[p.tolist() for p in paths],
        white_internal_margin_mm=MARGIN, outer_white_silhouette_margin_mm=2.2,
        upper_point_correction=upper_checks, minimum_clear_gaps_between_white_bands_mm=minimum_gaps,
        shoulder_and_lower_clear_gaps_between_white_bands_mm=lower_gaps,
        window_schedule=schedule, research_geometry_verified_against_survey=False,
        revised_geometry_physically_tested=False)
    parameters.pop('print_sample', None)
    parameters['diffuser']['physical_light_transmission_tested'] = True
    parameters['diffuser']['test_evidence'] = 'User reported good translucency and a good continuous-star sample; skin remains 0.4 mm.'
    (H / 'parameters.json').write_text(json.dumps(parameters, indent=2)+'\n')
    report = {'status': 'passed', 'geometry': stats, 'canonicalization': canonicalization,
        'upper_point_correction': upper_checks,
        'continuous_white_star_count': 3, 'diffused_windows': 130,
        'diffuser_thickness_mm': SKIN, 'layers_at_0_2mm': 2,
        'minimum_clear_gaps_between_white_bands_mm': minimum_gaps,
        'shoulder_and_lower_clear_gaps_between_white_bands_mm': lower_gaps,
        'white_face_difference_mm2': white_face_difference,
        'window_floor_difference_mm2': window_floor_difference,
        'filled_front_outline_difference_mm2': full_face_difference,
        'enclosure_above_front_wall_difference_mm3': enclosure_difference,
        'seated_back_collision_mm3': seated_overlap, 'bottom_mouth_clear': True,
        'tree_leader_reference_clear': True, 'marked_back_byte_identical': True,
        'source_files_unchanged': source_hashes, 'packages': {}}

    # Reuse only the established package writer functions, not baseline builds.
    package_source = BASE / 'validate_and_package.py'
    for node in ast.parse(package_source.read_text()).body:
        if isinstance(node, ast.FunctionDef) and node.name in {'el', 'meta', 'print_mesh', 'package'}:
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(package_source), 'exec'), globals())
    ET.register_namespace('', NS)
    with zipfile.ZipFile(SOURCE / 'diffused_front_A1.3mf') as archive:
        template = {name: archive.read(name) for name in archive.namelist()}
        original_settings = json.loads(archive.read('Metadata/project_settings.config'))
    package('front_shell_A1.3mf', 'Roanoke corrected proportions front', [
        (print_mesh(meshes['body_white_diffused']), 'White stars with corrected points and 0.4 mm diffusers A1', 1, [128, 128, 0]),
        (print_mesh(meshes['body_black']), 'Black shell with tested two-dot catches A2', 2, [128, 128, 0]),
    ], prime=True, brim=0.)
    with zipfile.ZipFile(H / 'front_shell_A1.3mf') as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    model = ET.fromstring(entries['3D/3dmodel.model'])
    materials = model.find('./{'+NS+'}resources/{'+NS+'}basematerials')
    for item, (name, color) in zip(materials, [('White PLA A1', '#FFFFFFFF'), ('Black PLA A2', '#000000FF')]):
        item.set('name', name)
        item.set('displaycolor', color)
    for item in model.findall('{'+NS+'}metadata'):
        if item.attrib.get('name') == 'Description':
            item.text = 'Taller inner upper points and wider dark gaps. Three continuous white stars, 130 hidden 0.4 mm diffuser windows. White filament 1 / A1, black filament 2 / A2. Fits the unchanged christopherbrown.io marked two-dot back. Revised proportions not physically tested.'
    entries['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(H / 'front_shell_A1.3mf', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    report['packages']['front_shell_A1.3mf']['sha256'] = sha(H / 'front_shell_A1.3mf')
    assert all(sha(ROOT / name) == value for name, value in source_hashes.items())
    (H / 'mesh_validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'source_files_unchanged'}, indent=2))


if __name__ == '__main__':
    main()
