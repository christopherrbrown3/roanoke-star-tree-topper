"""Check the revised connectors and reuse the existing native A1 package writer."""
import ast
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as mf
import numpy as np
import trimesh

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
C = json.loads((H / 'parameters.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solid(mesh):
    result = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32), np.asarray(mesh.faces, np.uint32)))
    assert result.status() == mf.Error.NoError, result.status()
    return result


def clean(key):
    mesh = trimesh.load(H / (key + '.stl'))
    output = solid(mesh).simplify(1e-5).to_mesh()
    result = trimesh.Trimesh(output.vert_properties[:, :3], output.tri_verts, process=True)
    assert result.is_watertight and result.is_winding_consistent and result.body_count == 1
    assert result.area_faces.min() > 1e-10
    assert abs(result.volume - mesh.volume) < .01
    result.export(H / (key + '.stl'))
    return result


report = {'status': 'passed', 'trials': {}, 'packages': {},
          'physical_trial_complete': (H / 'physical_fit.json').exists()}
meshes = {}
for trial in C['trials']:
    key = trial['id']
    base = meshes[key + '_catch'] = clean(key + '_catch')
    cap = meshes[key + '_back'] = clean(key + '_back')
    base_solid, cap_solid = solid(base), solid(cap)
    seated = abs((base_solid ^ cap_solid).volume())
    assert seated < .001, (key, seated)
    hook = solid(trimesh.load(H / 'construction' / (key + '_hook.stl')))
    floor = solid(trimesh.load(H / 'construction' / (key + '_floor.stl')))
    wall = solid(trimesh.load(H / 'construction' / (key + '_wall.stl')))
    engagement = (wall ^ hook).volume()
    assert engagement > .1, (key, engagement)
    # Check the tip/head corridor using a conservative rigid displacement.
    # This is a geometric check, not a model of bending or insertion force.
    shifted = hook.translate([0, trial['engagement_mm'] + .1, 0])
    collision = max(abs((base_solid ^ shifted.translate([0, 0, float(z)])).volume())
                    for z in np.linspace(0, 6.3, 32))
    assert collision < .001, (key, collision)
    assert abs((floor ^ cap_solid).volume()) < .001
    report['trials'][key] = {
        'engagement_mm': trial['engagement_mm'], 'guide_gap_mm': C['common']['guide_gap_mm'],
        'seated_overlap_mm3': seated, 'deflected_hook_sweep_max_overlap_mm3': collision,
        'sweep_scope': '32 axial positions with rigid hook displaced inward by engagement + 0.10 mm; excludes elastic forces',
        'undercut_engagement_mm3': engagement,
        'catch': {'watertight': True, 'connected_solids': 1, 'sha256': sha(H / (key + '_catch.stl'))},
        'cap': {'watertight': True, 'connected_solids': 1, 'sha256': sha(H / (key + '_back.stl'))},
    }

# Extract only the packaging helper definitions. Executing the parent script
# would regenerate the original plates and their validation files.
source = (H.parent / 'validate_and_package.py').read_text()
tree = ast.parse(source)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in {'el', 'meta', 'print_mesh', 'package'}:
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(H.parent / 'validate_and_package.py'), 'exec'))
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
with zipfile.ZipFile(H.parent / 'connector_sample_A1.3mf') as archive:
    template = {name: archive.read(name) for name in archive.namelist()}
    original_settings = json.loads(archive.read('Metadata/project_settings.config'))

parts = []
for trial, row in zip(C['trials'], [103, 143]):
    key, dots = trial['id'], trial['dots']
    parts.extend([
        (print_mesh(meshes[key + '_catch'], z_origin=48.5), f'{dots} dot catch', 2, [98, row, 0]),
        (print_mesh(meshes[key + '_back'], flip=True), f'{dots} dot cap', 2, [158, row + 20, 0]),
    ])
package('connector_fit_v2_A1.3mf', 'Connector fit v2 - one and two dots', parts, prime=False, brim=0.)
assert sha(H.parent / 'connector_sample_A1.3mf') == C['baseline_sample_sha256']
report['baseline_sample_unchanged'] = True
(H / 'mesh_validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
