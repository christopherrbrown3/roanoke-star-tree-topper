"""Show why a photo homography is not an independent metric accuracy certificate.
These are sensitivity examples, not alternative recommendations or confidence bounds.
"""
from pathlib import Path
import json,numpy as np,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
q=np.array(json.loads((ROOT/'research/accurate_light_paths.json').read_text())['six_paths_mm'])
W=200*84.5/88.5
out=[];paths=[]
for k in [-.15,0,.15]:
 T=np.array([[1,0,0],[0,1,0],[0,k/100,1.]])
 h=np.concatenate([q,np.ones(q.shape[:-1]+(1,))],axis=2)@T.T
 p=h[:,:,:2]/h[:,:,2:]
 sx=W/np.ptp(p[0,:,0]);sy=200/np.ptp(p[0,:,1]);ty=-sy*(p[0,:,1].max()+p[0,:,1].min())/2
 A=np.array([[sx,0,0],[0,sy,ty],[0,0,1.]])
 U=A@T;hp=np.concatenate([q,np.ones(q.shape[:-1]+(1,))],axis=2)@U.T;p=hp[:,:,:2]/hp[:,:,2:]
 back=np.concatenate([p,np.ones(p.shape[:-1]+(1,))],axis=2)@np.linalg.inv(U).T;back=back[:,:,:2]/back[:,:,2:]
 a=p[0,1]-p[0,0];b=p[0,-1]-p[0,0];angle=math.degrees(math.acos(a@b/np.linalg.norm(a)/np.linalg.norm(b)))
 out.append({'example_parameter_k':k,'apex_angle_deg':angle,'shoulder_below_apex_mm':float(p[0,0,1]-p[0,2,1]),'frame_heights_mm':[float(np.ptp(p[i,:,1])) for i in [0,2,4]],'max_roundtrip_error_mm':float(np.max(abs(back-q))),'transform_from_current':U.tolist()});paths.append(p)
result={'purpose':'Counterexample: exact same photograph reprojection after composing each camera homography with the inverse deformation. Does not quantify actual error or propose new geometry.','assumptions_preserved':['bilateral symmetry','horizontal shoulders','overall published width-to-height ratio'],'missing_metric_evidence':['measured vertex/edge positions','calibrated camera pose/intrinsics or orthographic elevation'],'examples':out}
(ROOT/'research/projective_ambiguity_audit.json').write_text(json.dumps(result,indent=2))
im=Image.new('RGB',(1500,640),'#142637');d=ImageDraw.Draw(im)
try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
except OSError:font=ImageFont.load_default()
for i,(p,r) in enumerate(zip(paths,out)):
 for s in p:
  coords=[(250+i*500+x*2.05,305-y*2.05) for x,y in s];d.line(coords+[coords[0]],fill='#f1f2e9',width=3)
 title=['Sensitivity example A','Current reconstruction','Sensitivity example B'][i]
 d.text((i*500+36,535),title,font=font,fill='white')
 d.text((i*500+36,570),f"Apex {r['apex_angle_deg']:.1f}°; same photo projection",font=font,fill='#b8cbd7')
d.text((35,20),'Same photographic fit does not establish one exact face-on shape',font=font,fill='white')
im.save(ROOT/'research/projective_ambiguity_audit.png')
print(json.dumps(result,indent=2))
