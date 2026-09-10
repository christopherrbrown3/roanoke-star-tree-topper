import numpy as np,json
from pathlib import Path
from scipy.optimize import least_squares
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
new=np.array(json.load(open(ROOT/'research/accurate_light_paths.json'))['six_paths_mm'])[[0,2,4]]
oldp=np.array(json.load(open(ROOT/'final/profile_measurements.json'))['shape_points_mm'])[:-1];old=np.array([oldp*s for s in [1,.72,.44]])
obs=np.array(json.load(open(ROOT/'research/reconstructed_geometry.json'))['raw_front_face_points_px'])

def fit(q,target):
 a=q.reshape(-1,2)/100;b=target.reshape(-1,2);center=b.mean(0);scale=np.ptp(b,axis=0).max();b=(b-center)/scale
 def proj(h):
  M=np.array([*h,1.]).reshape(3,3);v=np.c_[a,np.ones(len(a))]@M.T;return v[:,:2]/v[:,2,None]
 sol=least_squares(lambda h:(proj(h)-b).ravel(),[.5,0,0,0,-.5,0,0,0])
 pred=proj(sol.x)*scale+center
 return float(np.sqrt(np.mean(np.square(pred-target.reshape(-1,2))))),pred.reshape(3,10,2)
report={}
for name,q in [('previous',old),('reconstructed',new)]:
 rms,pred=fit(q,obs);report[name]={'rms_pixels':rms,'normalized_to_200mm':rms/np.ptp(obs.reshape(-1,2),axis=0).max()*200}
 if name=='reconstructed':
  im=Image.open(ROOT/'research/references/schumin_aerial_2024.webp').convert('RGB');d=ImageDraw.Draw(im)
  for points in pred:d.line([tuple(p) for p in points]+[tuple(points[0])],fill='#ff66ff',width=5)
  im.crop((3350,1100,5640,3440)).resize((1145,1170)).save(ROOT/'research/independent_aerial_overlay.jpg')
(ROOT/'research/reference_fit_comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
