"""Manufacturing profiles from six independently traced, rectified city-photo paths."""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import trimesh
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'research/accurate_light_paths.json').read_text())
width=200*84.5/88.5
paths=np.array(source['six_paths_mm'])*[(width-4.4)/width,(200-4.4)/200]
polys=[Polygon(path) for path in paths]
outline=polys[0].buffer(2.2,quad_segs=16)
profiles={}
def put(name,g):
    g=g.buffer(0)
    ps=[g] if g.geom_type=='Polygon' else list(g.geoms)
    out=[]
    for poly in ps:
        assert poly.is_valid and poly.area>0
        v,f=trimesh.creation.triangulate_polygon(poly,engine='earcut')
        out.append({'v':v.tolist(),'f':f.tolist(),'loops':[list(poly.exterior.coords)[:-1]]+[list(i.coords)[:-1] for i in poly.interiors]})
    profiles[name]=out
put('outline',outline)
rails=[LineString(list(path)+[path[0]]).buffer(.9,quad_segs=8,join_style=1) for path in paths]
feet=[]
pockets=[]
for i in range(3):
    outer,inner=polys[2*i:2*i+2]
    pair=unary_union(rails[2*i:2*i+2])
    bridges=[LineString([paths[2*i,j],paths[2*i+1,j]]).buffer(.8,cap_style=1,quad_segs=8) for j in [0,2,4,6,8]]
    foot=pair;assert foot.geom_type=='MultiPolygon' and len(foot.geoms)==2
    band=outer.buffer(2,quad_segs=8).difference(inner.buffer(-2,join_style=2)).intersection(outline)
    pocket=outer.buffer(1.2,quad_segs=8).difference(inner.buffer(-1.2,join_style=2))
    assert foot.difference(pocket).area<1e-7
    put(f'rails{i}',pair);put(f'foot{i}',foot);put(f'band{i}',band);put(f'pocket{i}',pocket)
    feet.append(foot);pockets.append(pocket)
# Flange is moved 3 mm down so its upper corners stay behind the silhouette.
flange=Polygon([(-10,-7),(10,-7),(26,9),(26,28),(-26,28),(-26,9)]).buffer(.6,quad_segs=8)
put('flange',flange)
projection=Polygon([(-19.4,-32),(19.4,-32),(13.4,48),(-13.4,48)])
put('mount_projection',projection)
outside=projection.union(flange).difference(outline).area
assert outside<1e-7,outside
report={'landmark_ft':{'height':88.5,'width':84.5},'source':'research/accurate_light_paths.json','six_paths_mm':paths.tolist(),'base_bounds':outline.bounds,'mount_outside_silhouette_mm2':outside,'rail_width_mm':1.8,'clearance_per_side_mm':.3,'rail_pair_min_visible_gaps_mm':[rails[2*i].distance(rails[2*i+1]) for i in range(3)],'inter_pair_min_visible_gaps_mm':[rails[2*i+1].distance(rails[2*i+2]) for i in range(2)],'pair_channel_min_separation_mm':[pockets[i].distance(pockets[i+1]) for i in range(2)],'foot_to_pocket_min_clearance_mm':[pockets[i].boundary.distance(feet[i]) for i in range(3)],'manufacturing_path_scale_xy':[(width-4.4)/width,.978]}
(ROOT/'final/profile_measurements.json').write_text(json.dumps(report,indent=2))
(ROOT/'scripts/topper_profiles.json').write_text(json.dumps(profiles))
print(json.dumps({k:v for k,v in report.items() if k!='six_paths_mm'},indent=2))
