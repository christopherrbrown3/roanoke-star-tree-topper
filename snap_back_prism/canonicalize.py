"""Resolve float32 export degeneracies without changing the intended solids."""
import hashlib
import json
from pathlib import Path
import manifold3d as mf
import numpy as np
import trimesh

H=Path(__file__).resolve().parent
reports={}
for key in ['body_navy','body_white_face','snap_back','coupon_catch','coupon_back']:
    file=H/(key+'.stl'); m=trimesh.load(file)
    s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
    assert s.status()==mf.Error.NoError,(key,s.status())
    raw=H/'construction/raw_exports'; raw.mkdir(exist_ok=True)
    (raw/(key+'.stl')).write_bytes(file.read_bytes())
    out=s.simplify(1e-5).to_mesh()
    cleaned=trimesh.Trimesh(out.vert_properties[:,:3],out.tri_verts,process=True)
    assert cleaned.is_watertight and cleaned.is_winding_consistent
    assert cleaned.area_faces.min()>1e-10
    assert abs(cleaned.volume-m.volume)<.02,(key,m.volume,cleaned.volume)
    assert np.max(np.abs(cleaned.bounds-m.bounds))<.0001
    cleaned.export(file)
    reports[key]={'watertight':True,'solids':int(cleaned.body_count),
       'volume_mm3':float(cleaned.volume),'triangles':len(cleaned.faces),
       'volume_change_mm3':float(cleaned.volume-m.volume),
       'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(H/'canonicalization_report.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
