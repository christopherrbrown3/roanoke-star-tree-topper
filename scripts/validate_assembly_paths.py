from pathlib import Path
import numpy as np,trimesh,manifold3d as mf,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'final'
def solid(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
base=trimesh.load(OUT/'roanoke_star_base.stl');lights=trimesh.load(OUT/'roanoke_star_lights.stl');lights.apply_translation([0,0,3.8]);mount=trimesh.load(OUT/'roanoke_star_tree_mount.stl');mount.vertices=np.column_stack([mount.vertices[:,0],mount.vertices[:,2]-32,-mount.vertices[:,1]])
a,b,c=map(solid,[base,lights,mount]);r={'straight_insertion_overlap_mm3':{}}
for name,s,direction in [('lights',b,1),('mount',c,-1)]:
 vals={str(d):max(0.,float((a^s.translate([0,0,d*direction])).volume())) for d in [0,.1,.3,.6,1,1.3,2,4,10]}
 assert max(vals.values())<1e-5,vals
 r['straight_insertion_overlap_mm3'][name]=vals
# A near-nominal solid tapered mandrel must pass through the full bore without hitting the web.
n=128;v=[]
for y in [-31.9,47.9]:
 rad=17-.075*(y+32)-.05
 v += [[rad*np.cos(t*2*np.pi/n),y,-21.8+rad*np.sin(t*2*np.pi/n)] for t in range(n)]
f=[]
for i in range(n):
 j=(i+1)%n;f += [[i,j,n+j],[i,n+j,n+i]]
for i in range(1,n-1):f += [[0,i+1,i],[n,n+i,n+i+1]]
mandrel=trimesh.Trimesh(v,f);mandrel.fix_normals();vol=max(0.,float((solid(mandrel)^c).volume()));assert vol<1e-5,vol
r['tapered_bore_mandrel_overlap_mm3']=vol;r['mandrel_radial_test_allowance_mm']=.05
assembled=trimesh.load(OUT/'roanoke_star_assembled.stl');assert assembled.is_watertight
r['assembled_reference_stl']={'watertight':bool(assembled.is_watertight),'shells':len(assembled.split()),'dimensions_mm':assembled.extents.tolist()}
(OUT/'assembly_path_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
