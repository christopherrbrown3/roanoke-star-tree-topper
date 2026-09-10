from pathlib import Path
import numpy as np,json,math
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter1d
from scipy.signal import find_peaks
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'research/references/city_aerial_original.jpg').convert('RGB');arr=np.array(im).astype(float);bright=arr.min(axis=2)
center=np.array([551.,738.]);pts=[];angles=[]
# Keep only rays with six separated bright tracks; missing neon segments are excluded.
for deg in np.arange(-90,270,.35):
 a=math.radians(deg);r=np.arange(8,310,.25);xy=center+r[:,None]*np.array([math.cos(a),math.sin(a)])
 val=map_coordinates(bright,[xy[:,1],xy[:,0]],order=1,mode='nearest');val=gaussian_filter1d(val,1)
 ids,pr=find_peaks(val,height=185,prominence=27,distance=12)
 if len(ids)==6:
  pts.append(xy[ids[::-1]]);angles.append(deg)
pts=np.array(pts);angles=np.array(angles)
# Shared angular sectors leave a margin around each corner; fitted lines intersect to recover vertices.
vertices_deg=np.array([-90,-56,-20,3,49,90,129,177,199,238,270])
paths=[];errors=[]
for track in range(6):
 lines=[];res=[]
 for i in range(10):
  a,b=vertices_deg[i],vertices_deg[i+1];mask=(angles>a+4)&(angles<b-4);p=pts[mask,track]
  if len(p)<3:raise RuntimeError((track,i,len(p)))
  # Iterative robust orthogonal line fit filters residual tube joints and support glints.
  for _ in range(4):
   c=p.mean(axis=0);_,_,vt=np.linalg.svd(p-c);n=vt[-1];d=-(c@n);err=np.abs(p@n+d);p=p[err<max(.65,np.percentile(err,85))]
  lines.append([*n,d]);res.extend(err.tolist())
 v=[]
 for i in range(10):
  l0=lines[(i-1)%10];l1=lines[i];v.append(np.linalg.solve([l0[:2],l1[:2]],[-l0[2],-l1[2]]).tolist())
 paths.append(v);errors.append(float(np.sqrt(np.mean(np.square(res)))))
report={'source':'https://www.roanokeva.gov/ImageRepository/Document?documentID=13604','method':'Bright-track radial sampling, six-peak ray selection, robust edge fitting and adjacent-line intersection. Source coordinates remain perspective-distorted; never used unrectified as manufacturing geometry.','qualified_rays':len(angles),'six_track_vertices_px':paths,'edge_fit_rms_pixels':errors}
(ROOT/'research/city_six_light_paths.json').write_text(json.dumps(report,indent=2));print('qualified rays',len(angles),'edge RMS',errors);print(np.round(paths,1))
canvas=im.copy();d=ImageDraw.Draw(canvas)
for i,path in enumerate(paths):d.line([tuple(p) for p in path]+[tuple(path[0])],fill=['#ff66ff','#ff66ff','#66ff66','#66ff66','#ffff00','#ffff00'][i],width=1)
canvas.crop((250,450,820,960)).resize((1140,1020)).save(ROOT/'research/city_trace_overlay.png')
