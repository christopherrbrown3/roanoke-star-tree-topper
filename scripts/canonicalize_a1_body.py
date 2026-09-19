"""Canonicalize both material meshes before GUI re-import and BVH checking."""
from pathlib import Path
import hashlib, json
import numpy as np
import trimesh
import manifold3d as mf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'print_in_place'
(ROOT/'tmp').mkdir(exist_ok=True)
reports={}
for label,filename in [('body','body_material.stl'),('white','white_tube_material.stl')]:
    path=OUT/filename
    before=trimesh.load(path)
    solid=mf.Manifold(mf.Mesh(np.asarray(before.vertices,np.float32),
                             np.asarray(before.faces,np.uint32)))
    assert solid.status()==mf.Error.NoError
    data=solid.to_mesh()
    after=trimesh.Trimesh(data.vert_properties[:,:3],data.tri_verts,process=True)
    assert after.is_watertight and after.is_winding_consistent
    assert after.body_count==before.body_count
    assert abs(after.volume-before.volume)<.001
    assert np.max(np.abs(after.bounds-before.bounds))<1e-5
    assert after.area_faces.min()>1e-10
    reports[label]={
        'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'before_triangles':len(before.faces),'after_triangles':len(after.faces),
        'before_minimum_triangle_area_mm2':float(before.area_faces.min()),
        'after_minimum_triangle_area_mm2':float(after.area_faces.min()),
        'volume_change_mm3':float(after.volume-before.volume),
        'maximum_bounds_change_mm':float(np.max(np.abs(after.bounds-before.bounds))),
        'watertight':bool(after.is_watertight),
        'connected_solids':int(after.body_count),
    }
    (ROOT/f'tmp/a1_canonical_{label}.json').write_text(json.dumps({'v':after.vertices.tolist(),'f':after.faces.tolist()}))
report={'date':'2026-09-13','method':'Manifold canonical triangulation; both materials returned to Blender and rechecked without changing intersection tolerances','materials':reports}
(OUT/'canonicalization_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
