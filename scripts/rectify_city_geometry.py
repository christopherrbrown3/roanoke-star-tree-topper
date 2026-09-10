from pathlib import Path
import numpy as np,json,math
from scipy.optimize import least_squares
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
j=json.loads((ROOT/'research/city_six_light_paths.json').read_text());p=np.array(j['six_track_vertices_px']);uv=(p-[552,738])/500
# A projective correction inferred from repeated parallel tube paths and bilateral symmetry.
# Homography gauge: h00=1, h02=h12=0. Translation and overall scale are removed afterward.
def transform(v):
 b,d,e,g,h=v;den=1+g*uv[:,:,0]+h*uv[:,:,1]
 return np.stack([(uv[:,:,0]+b*uv[:,:,1])/den,(d*uv[:,:,0]+e*uv[:,:,1])/den],axis=2)
def residual(v):
 q=transform(v);height=np.ptp(q[0,:,1]);axis=q[:,[0,5],0].mean();r=[]
 for s in q:
  r.extend((s[[0,5],0]-axis)/height)
  for a,b in [(1,9),(2,8),(3,7),(4,6)]:r.extend([(s[a,0]+s[b,0]-2*axis)/height,(s[a,1]-s[b,1])/height])
  r.extend([(s[1,1]-s[2,1])/height,(s[9,1]-s[8,1])/height])
 for n in [0,2,4]:
  a=np.roll(q[n],-1,axis=0)-q[n];b=np.roll(q[n+1],-1,axis=0)-q[n+1]
  crosses=(a[:,0]*b[:,1]-a[:,1]*b[:,0])/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1))
  r.extend(crosses*.3)
 r.append((np.ptp(q[0,:,0])/height-84.5/88.5)*3)
 return r
fit=least_squares(residual,[0,0,1.15,0,0],max_nfev=3000,loss='soft_l1',f_scale=.01)
q=transform(fit.x);q[:,:,0]-=q[:,[0,5],0].mean();q[:,:,1]*=-1
q[:,:,1]-=(q[0,0,1]+np.mean(q[0,[4,6],1]))/2
q*=200/(q[0,0,1]-np.mean(q[0,[4,6],1]))
raw=q.copy()
for s in q:
 s[0,0]=s[5,0]=0
 for a,b in [(1,9),(2,8),(3,7),(4,6)]:
  x=(s[a,0]-s[b,0])/2;y=(s[a,1]+s[b,1])/2;s[a]=[x,y];s[b]=[-x,y]
 y=s[[1,2,8,9],1].mean();s[[1,2,8,9],1]=y
q[:,:,0]*=(200*84.5/88.5)/np.ptp(q[0,:,0])
angles=[]
for s in q:
 a=s[1]-s[0];b=s[-1]-s[0];angles.append(math.degrees(math.acos(np.dot(a,b)/np.linalg.norm(a)/np.linalg.norm(b))))
result={'source_image':j['source'],'method':'Projective rectification fitted to bilateral symmetry, horizontal shoulders, and parallel corresponding edges within each paired tube group. Six paths were independently extracted; none are scaled generic stars. Published 84.5/88.5 aspect ratio anchors metric scale.','rectification_parameters':fit.x.tolist(),'residual_rms_normalized':float(np.sqrt(np.mean(np.square(residual(fit.x))))),'six_paths_mm':q.tolist(),'unsymmetrized_paths_mm':raw.tolist(),'apex_angles_degrees':angles,'frame_pair_outer_heights_mm':[float(np.ptp(q[i,:,1])) for i in [0,2,4]],'frame_pair_outer_widths_mm':[float(np.ptp(q[i,:,0])) for i in [0,2,4]],'symmetrization_max_displacement_mm':float(np.max(np.linalg.norm(q-raw,axis=2)))}
(ROOT/'research/accurate_light_paths.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['six_paths_mm','unsymmetrized_paths_mm']},indent=2));print(np.round(q[[0,2,4]],2))
# A scale-free orthographic check diagram; manufacturing offsets are applied later.
im=Image.new('RGB',(1100,1150),'#132536');d=ImageDraw.Draw(im)
for s in q:
 pts=[(550+x*4.7,550-y*4.7) for x,y in s];d.line(pts+[pts[0]],fill='#f3f3eb',width=6)
im.save(ROOT/'research/rectified_six_paths.png')
