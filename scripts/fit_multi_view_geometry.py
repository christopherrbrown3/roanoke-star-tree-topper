import json,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1]
aerial=np.array(json.loads((ROOT/'research/reconstructed_geometry.json').read_text())['raw_front_face_points_px'])
night=np.array([
[(925,98),(1092,420),(1607,425),(1210,684),(1489,1220),(924,870),(376,1227),(628,684),(238,426),(755,420)],
[(925,205),(1053,464),(1445,466),(1113,650),(1322,1049),(924,771),(527,1049),(734,651),(403,469),(794,465)],
[(926,365),(1000,522),(1227,524),(1020,625),(1124,844),(925,729),(721,844),(827,625),(622,524),(850,522)]],float)*2592/1824
observed=[aerial,night]
def shape(p,outer=False):
 if outer:a,b,c,d,e,f=p;top,tip,bottom=100,200*84.5/88.5/2,-100
 else:top,a,b,tip,c,d,e,bottom,f=p
 return np.array([(0,top),(a,b),(tip,b),(c,d),(e,bottom),(0,f),(-e,bottom),(-c,d),(-tip,b),(-a,b)])
outer=np.array([23,25,33,-20,60,-50.]);base=shape(outer,True)
init=list(outer)
for s in [.7,.4]:
 q=(base-[0,-10])*s+[0,-10];init+=list([q[0,1],q[1,0],q[1,1],q[2,0],q[3,0],q[3,1],q[4,0],q[4,1],q[5,1]])
# Camera (yaw relative to plane, pitch relative to plane, image roll, tx, ty, tz).
init+= [25,14.3,0,40,-35,530, 0,-35,0,3,-10,345]
def shapes(p):return np.stack([shape(p[:6],True),shape(p[6:15]),shape(p[15:24])])
def project(q,camera,k):
 yaw,pitch,roll,tx,ty,tz=camera;theta=math.radians(yaw);pitch=math.radians(pitch);roll=math.radians(roll)
 u=np.array([math.cos(theta),math.sin(theta)*math.sin(pitch),-math.sin(theta)*math.cos(pitch)]);v=np.array([0,-math.cos(pitch),-math.sin(pitch)])
 xyz=q[...,0,None]*u+q[...,1,None]*v+np.array([tx,ty,tz])
 c,s=math.cos(roll),math.sin(roll);xy=xyz[...,:2]@np.array([[c,-s],[s,c]]).T
 return xy/xyz[...,2,None]*k[0]+np.array(k[1:])
K=[(5376,4032,2688),(6.2/25.4*11520,1296,972)]
def residual(p):
 q=shapes(p);r=[]
 for i,obs in enumerate(observed):r.extend(((project(q,p[24+6*i:30+6*i],K[i])-obs)/5).ravel())
 # Metadata is an orientation check, not a rigid calibration after image processing.
 r.append((p[25]-14.3)/5)
 return r
fit=least_squares(residual,init,max_nfev=3000,loss='soft_l1',f_scale=2)
q=shapes(fit.x)
report={'method':'Joint pinhole reprojection fit to high aerial and low ground references; each frame measured independently; left-right symmetry and horizontal shoulders enforced; published external H/W anchored. Photographic reconstruction, not a measured engineering drawing.','frame_outer_contours_mm':q.tolist(),'cameras':fit.x[24:].reshape(2,6).tolist(),'reprojection_rms_pixels':[float(np.sqrt(np.mean((project(q,fit.x[24+6*i:30+6*i],K[i])-observed[i])**2))) for i in range(2)],'projected_points_pixels':[project(q,fit.x[24+6*i:30+6*i],K[i]).tolist() for i in range(2)],'observed_points_pixels':[aerial.tolist(),night.tolist()]}
(ROOT/'research/multiview_geometry.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['projected_points_pixels','observed_points_pixels']},indent=2))
