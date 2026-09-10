"""Remove zero-volume duplicate bevel topology through the Manifold kernel.
The resulting meshes are returned to Blender before the final exports are saved.
"""
from pathlib import Path
import json,numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'final';result={};audit={}
for name,file in [('RoanokeStar_Base','roanoke_star_base.stl'),('RoanokeStar_Lights','roanoke_star_lights.stl'),('Tree_Mount','roanoke_star_tree_mount.stl')]:
 m=trimesh.load(OUT/file)
 if name=='RoanokeStar_Lights':m.apply_translation([0,0,3.8])
 if name=='Tree_Mount':m.vertices=np.column_stack([m.vertices[:,0],m.vertices[:,2]-32,-m.vertices[:,1]])
 s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)));r=s.to_mesh();n=trimesh.Trimesh(r.vert_properties[:,:3],r.tri_verts,process=True)
 assert n.is_watertight and n.is_winding_consistent and abs(n.volume-m.volume)<.1
 result[name]={'v':n.vertices.tolist(),'f':n.faces.tolist()}
 audit[name]={'volume_change_mm3':float(n.volume-m.volume),'triangles':len(n.faces),'watertight':bool(n.is_watertight)}
(ROOT/'scripts/canonical_meshes.json').write_text(json.dumps(result));(OUT/'canonicalization_audit.json').write_text(json.dumps(audit,indent=2));print(audit)
