"""Prepare native Blender boolean inputs for a face-down snap-back experiment."""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
ROOT = H.parent
S = json.loads((ROOT/'scripts/a1_topper_profiles.json').read_text())
P = json.loads((ROOT/'pentagrammic_prism/profiles.json').read_text())
C = {'depth_mm': 60., 'front_wall_mm': 4., 'side_wall_mm': 1.2,
     'back_wall_mm': 1.6, 'body_rear_z_mm': 58.4, 'bottom_opening_width_mm': 100.,
     'clip_count': 6, 'clip_beam_radial_width_mm': 1.2,
     'clip_beam_effective_length_mm': 18., 'radial_fit_gap_mm': .3,
     'retention_engagement_mm': .45, 'maximum_assembly_deflection_mm': .75,
     'clip_tip_z_mm': 52.4, 'clip_nose_start_z_mm': 53.15,
     'clip_nose_end_z_mm': 53.7, 'clip_stem_return_z_mm': 54.45,
     'catch_window_z_mm': [52.4, 54.85], 'catch_window_width_mm': 5.4,
     'locating_rim_depth_mm': 3., 'lid_color': 'white',
     'body_print_orientation': 'front face down',
     'lid_print_orientation': 'outer face down; clips up', 'support_enabled': False,
     'physical_snap_tested': False, 'thermal_tested': False,
     'source_profile_sha256': hashlib.sha256((ROOT/'scripts/a1_topper_profiles.json').read_bytes()).hexdigest()}
wall=C['side_wall_mm']
outer=wall+C['radial_fit_gap_mm']
inner=outer+C['clip_beam_radial_width_mm']
tip=C['clip_tip_z_mm']
peak_z=C['clip_nose_end_z_mm']
rear=C['body_rear_z_mm']
C['maximum_assembly_deflection_mm']=C['radial_fit_gap_mm']+C['retention_engagement_mm']
C['clip_nose_start_z_mm']=tip+C['maximum_assembly_deflection_mm']
C['clip_stem_return_z_mm']=peak_z+C['maximum_assembly_deflection_mm']
C['catch_window_z_mm']=[tip,C['clip_stem_return_z_mm']+.4]
assert C['clip_nose_start_z_mm']<peak_z, 'Increase the axial nose length for this engagement.'
C['simple_beam_strain_estimate_percent'] = 100*1.5*C['clip_beam_radial_width_mm']*C['maximum_assembly_deflection_mm']/C['clip_beam_effective_length_mm']**2
outline = Polygon(S['outline'][0]['loops'][0])
inside = outline.buffer(-wall, join_style=2)
tubes = unary_union([Polygon(p['loops'][0]) for p in S['white_tube_sections']])
bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in S['white_backing_bands']])
mouth = Polygon(P['bottom_mouth'][0]['loops'][0])
vents = unary_union([Polygon(p['loops'][0]) for p in P['rear_vents']])
loop = np.asarray(outline.exterior.coords[:-1])
clips = []
for i in [25, 26, 53, 108, 135, 136]:
    a, b = loop[i], loop[(i+1)%len(loop)]
    t = (b-a)/np.linalg.norm(b-a)
    n = np.array([-t[1], t[0]])  # Original outline is clockwise.
    clips.append({'center_xy': ((a+b)/2).tolist(), 'tangent_xy': t.tolist(),
                  'outward_xy': n.tolist()})
C['clips'] = clips

def local_polygon(points, clip):
    c, t, n = (np.asarray(clip[k]) for k in ['center_xy','tangent_xy','outward_xy'])
    return Polygon([c+t*s-n*r for s, r in points])

def local_geom(g, clip):
    from shapely.affinity import affine_transform
    c, t, n = (np.asarray(clip[k]) for k in ['center_xy','tangent_xy','outward_xy'])
    return affine_transform(g, [t[0], -n[0], t[1], -n[1], c[0], c[1]])

def rounded_rect(x0,y0,x1,y1,r=.35):
    return box(x0+r,y0+r,x1-r,y1-r).buffer(r,quad_segs=8)

notch = unary_union([rounded_rect(-8,-3,11,outer),
                     rounded_rect(-8,inner,11,inner+1), box(10,-3,11,inner+1)])
notches = unary_union([local_geom(notch, c) for c in clips])
windows = unary_union([local_geom(box(5.6,-.5,11.,outer+.05), c) for c in clips])
rim = outline.buffer(-outer,join_style=2).difference(outline.buffer(-inner,join_style=2))
rim = rim.difference(mouth).difference(unary_union([local_geom(box(-9,-2,12,inner+1.5),c) for c in clips]))
lid = outline.difference(vents).difference(notches)
assert lid.geom_type == 'Polygon' and lid.is_valid

def extrude(g,z0,z1,key):
    polys = [g] if g.geom_type=='Polygon' else list(g.geoms)
    out=[]
    for p in polys:
        if p.area<1e-8: continue
        m=trimesh.creation.extrude_polygon(p,height=z1-z0,engine='earcut')
        m.apply_translation([0,0,z0]); assert m.is_watertight
        out.append(m)
    trimesh.util.concatenate(out).export(H/'construction'/f'{key}.stl')

def hook(clip, key, engagement=None):
    engagement=C['retention_engagement_mm'] if engagement is None else engagement
    outer_r=wall-engagement
    delta=outer-outer_r
    # Both axial ramps are 45 degrees; the nose enters a through-wall catch.
    profile=Polygon([(inner,tip),(outer,tip),(outer_r,tip+delta),
                     (outer_r,peak_z),(outer,peak_z+delta),(outer,rear+.1),(inner,rear+.1)])
    m=trimesh.creation.extrude_polygon(profile,height=4.6,engine='earcut')
    c,t,n=(np.asarray(clip[k]) for k in ['center_xy','tangent_xy','outward_xy'])
    vertices=m.vertices.copy()
    xy=c[None,:] + (vertices[:,2]+6.)[:,None]*t[None,:] - vertices[:,0,None]*n[None,:]
    m.vertices=np.column_stack([xy,vertices[:,1]])
    m.invert() if m.volume<0 else None
    assert m.is_watertight and m.volume>0
    m.export(H/'construction'/f'{key}.stl')

extrude(outline,0,rear,'body_blank')
extrude(inside,C['front_wall_mm'],C['depth_mm'],'open_cavity')
extrude(tubes,-.2,4.2,'tube_holes')
extrude(mouth,4,60,'bottom_mouth')
extrude(windows,*C['catch_window_z_mm'],'catch_windows')
extrude(bands,0,1,'white_face')
extrude(lid,rear,C['depth_mm'],'lid_blank')
extrude(rim,rear-C['locating_rim_depth_mm'],rear+.1,'locating_rim')
for i,c in enumerate(clips): hook(c,f'hook_{i+1}')

# A small local section reproduces the actual wall, window, arm, and hook.
sample={'center_xy':[0,0], 'tangent_xy':[1,0], 'outward_xy':[0,-1]}
extrude(box(-14,0,14,10),48.5,50.1,'coupon_floor')
extrude(box(-14,0,14,wall),50,rear,'coupon_wall')
extrude(box(5.6,-.5,11,outer+.05),*C['catch_window_z_mm'],'coupon_window')
extrude(box(-14,0,14,10).difference(notch),rear,C['depth_mm'],'coupon_lid')
extrude(box(-14,outer,14,inner).difference(box(-9,0,12,inner+1.5)),rear-C['locating_rim_depth_mm'],rear+.1,'coupon_rim')
hook(sample,'coupon_hook')
(H/'parameters.json').write_text(json.dumps(C,indent=2)+'\n')
print(json.dumps(C,indent=2))
