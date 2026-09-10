from pathlib import Path
import json, numpy as np, trimesh, manifold3d as mf
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'final'
files=['roanoke_star_base.stl','roanoke_star_lights.stl','roanoke_star_tree_mount.stl']
meshes=[trimesh.load(OUT/f) for f in files]
meshes[1].apply_translation([0,0,3.8])
M=trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0])@trimesh.transformations.translation_matrix([0,0,-32]);meshes[2].apply_transform(M)
def solid(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
report={'parts':{},'pair_intersections_mm3':{},'white_frame_intersections_mm3':[]}
for f,m in zip(files,meshes):
 s=solid(m)
 report['parts'][f]={'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'shells':len(m.split()),'degenerate_triangles':int((m.area_faces<1e-9).sum()),'duplicate_triangles':int(len(m.faces)-len(m.unique_faces().nonzero()[0])),'manifold_kernel_status':str(s.status()),'volume_cm3':m.volume/1000,'solid_PLA_g':m.volume*.00124,'center_of_mass_mm':m.center_mass.tolist(),'bounds_mm':m.bounds.tolist()}
for i in range(3):
 for j in range(i+1,3):report['pair_intersections_mm3'][files[i]+' + '+files[j]]=float((solid(meshes[i])^solid(meshes[j])).volume())
white=meshes[1].split()
for i in range(len(white)):
 for j in range(i+1,len(white)):report['white_frame_intersections_mm3'].append(float((solid(white[i])^solid(white[j])).volume()))
vols=np.array([m.volume for m in meshes]);com=sum(m.center_mass*m.volume for m in meshes)/sum(vols)
report['assembled']={'dimensions_mm':(np.max([m.bounds[1] for m in meshes],axis=0)-np.min([m.bounds[0] for m in meshes],axis=0)).tolist(),'volume_cm3':sum(vols)/1000,'solid_PLA_g':float(sum(vols)*.00124),'solid_PETG_g':float(sum(vols)*.00127),'center_of_mass_mm':com.tolist(),'socket_axis_depth_mm':-21.8,'center_of_mass_forward_of_socket_axis_mm':float(com[2]+21.8),'gravity_torque_Nm_solid_PLA':float(sum(vols)*.00124/1000*9.81*(com[2]+21.8)/1000)}
(OUT/'mesh_fit_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
