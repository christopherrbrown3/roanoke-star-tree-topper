"""Canonicalize only this variant's exports before native Blender re-import."""
import hashlib
import json
from pathlib import Path
import manifold3d as mf
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
reports = {}
for filename in ['dark_shell.stl', 'white_details.stl', 'roanoke_star_prism.stl']:
    path = HERE/filename
    before = trimesh.load(path)
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    s = mf.Manifold(mf.Mesh(np.asarray(before.vertices, np.float32),
                            np.asarray(before.faces, np.uint32)))
    assert s.status() == mf.Error.NoError
    d = s.simplify(1e-5).to_mesh()
    after = trimesh.Trimesh(d.vert_properties[:, :3], d.tri_verts, process=True)
    assert after.is_watertight and after.is_winding_consistent
    assert after.body_count == before.body_count
    assert abs(after.volume-before.volume) < .001
    assert np.max(np.abs(after.bounds-before.bounds)) < 1e-5
    after.export(path)
    reports[filename] = {
        'source_sha256': source_hash, 'triangles_before': len(before.faces),
        'triangles_after': len(after.faces), 'watertight': True,
        'volume_change_mm3': float(after.volume-before.volume),
        'connected_solids': int(after.body_count),
        'minimum_triangle_area_mm2': float(after.area_faces.min()),
    }
    if filename == 'white_details.stl':
        for key, mask in [
            ('canonical_white_face', np.max(after.triangles[:, :, 2], axis=1) < 2),
            ('canonical_white_reflector', np.min(after.triangles[:, :, 2], axis=1) > 50),
        ]:
            m = after.submesh([np.flatnonzero(mask)], append=True)
            assert m.is_watertight
            m.export(HERE/'construction'/f'{key}.stl')
(HERE/'canonicalization_report.json').write_text(json.dumps(reports, indent=2)+'\n')
print(json.dumps(reports, indent=2))
