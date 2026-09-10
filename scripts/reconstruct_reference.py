from pathlib import Path
import numpy as np, json, math
from scipy.optimize import least_squares
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
# Measured on the 1565 x 1600 display of a 2290 x 2340 crop from the original 8064 x 5376 image.
# Source crop origin (3350,1100); all points follow the front face, not rear structural rails.
obs=np.array([
[(746,95),(884,676),(1488,729),(949,1005),(1138,1560),(707,1154),(306,1404),(474,944),(80,586),(554,638)],
[(733,340),(830,751),(1255,784),(870,966),(1001,1365),(709,1067),(431,1255),(554,925),(273,677),(610,719)],
[(724,576),(778,818),(1026,839),(804,928),(884,1168),(711,981),(554,1102),(640,904),(463,767),(654,792)]],dtype=float)
raw=obs*np.array([2290/1565,2340/1600])+np.array([3350,1100])
f=8064*24/36;cx=4032;cy=2688;pitch=math.radians(14.3)
def rectify(theta):
 t=math.radians(theta);u=np.array([math.cos(t),math.sin(t)*math.sin(pitch),-math.sin(t)*math.cos(pitch)]);v=np.array([0,-math.cos(pitch),-math.sin(pitch)]);n=np.cross(u,v)
 rays=np.concatenate([(raw-np.array([cx,cy]))/f,np.ones((3,10,1))],axis=2)
 xyz=rays/(rays@n)[...,None]
 q=np.stack([xyz@u,xyz@v],axis=2)
 return q,u,v,n
# Fit yaw by bilateral symmetry and the documented 84.5/88.5 overall aspect ratio.
def residual(v):
 q,*_=rectify(v[0]);outer=q[0];h=np.ptp(outer[:,1]);axis=np.mean(q[:,[0,5],0]);r=[]
 for p in q:
  for a,b in [(1,9),(2,8),(3,7),(4,6)]:r.extend([(p[a,0]+p[b,0]-2*axis)/h,(p[a,1]-p[b,1])/h])
 r.append((np.ptp(outer[:,0])/h-84.5/88.5)*2)
 return r
fit=least_squares(residual,[20],bounds=(-60,60));q,u,v,n=rectify(fit.x[0]);q[:,:,0]-=np.mean(q[:,[0,5],0]);q[:,:,1]-=np.min(q[0,:,1]);q*=200/np.ptp(q[0,:,1])
symmetric=q.copy()
for p in symmetric:
 for a,b in [(1,9),(2,8),(3,7),(4,6)]:
  x=(p[a,0]-p[b,0])/2;y=(p[a,1]+p[b,1])/2;p[a]=[x,y];p[b]=[-x,y]
 p[0,0]=p[5,0]=0
# Global scale uses documented width. Numerical image estimates are retained separately.
pre_width=np.ptp(symmetric[0,:,0]);symmetric[:,:,0]*=(200*84.5/88.5)/pre_width
report={'source':'https://www.schuminweb.com/photo_features/aerial-view-of-the-roanoke-star/','original_image_size':[8064,5376],'focal_px_from_24mm_equivalent':f,'gimbal_pitch_degrees':-14.3,'fitted_plane_yaw_degrees':float(fit.x[0]),'reconstructed_pre_width_constraint_mm':float(pre_width),'raw_front_face_points_px':raw.tolist(),'rectified_unaveraged_mm':q.tolist(),'symmetric_frame_outer_contours_mm':symmetric.tolist(),'normalized_symmetry_rms':float(np.sqrt(np.mean(np.square(residual(fit.x))))) }
(ROOT/'research/reconstructed_geometry.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:val for k,val in report.items() if k not in ['raw_front_face_points_px','rectified_unaveraged_mm']},indent=2))
# Annotated source trace: orange/green/blue are measured contours, not camera-corrected shape superposed in raw space.
im=Image.open(ROOT/'research/references/aerial_2024_geometry_crop.png').convert('RGB');d=ImageDraw.Draw(im)
colors=['#ff7a19','#59ffb0','#46bfff']
for i,points in enumerate(raw):
 pp=points-[3350,1100];d.line([tuple(pt) for pt in pp]+[tuple(pp[0])],fill=colors[i],width=4)
 for j,(x,y) in enumerate(pp):d.ellipse((x-7,y-7,x+7,y+7),fill=colors[i]);d.text((x+10,y+6),f'{i+1}.{j}',fill='black',stroke_width=2,stroke_fill='white')
im.save(ROOT/'research/reference_trace_overlay.png')
