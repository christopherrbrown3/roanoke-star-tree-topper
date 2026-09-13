"""Independent validation and one-object, two-material 3MF packaging."""
import hashlib,json,math,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import manifold3d as mf
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'print_in_place'

def solid(m):
    s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
    assert s.status()==mf.Error.NoError,s.status()
    return s

def mesh(s):
    p=s.to_mesh();return trimesh.Trimesh(p.vert_properties[:,:3],p.tri_verts,process=True)

parts=[trimesh.load(OUT/n) for n in ['body_material.stl','white_tube_material.stl']]
# Independently compare the actual STL's bed-facing triangles with the current
# prepared tube footprints. This prevents packaging stale exports after a path
# correction, even if both versions happen to have the same total volume.
prepared=json.loads((ROOT/'scripts/a1_topper_profiles.json').read_text())
expected_front=unary_union([Polygon(p['loops'][0],p['loops'][1:])
                           for p in prepared['white_tube_sections']])
triangles=parts[1].triangles
bottom=triangles[np.all(np.abs(triangles[:,:,2])<1e-7,axis=1)]
actual_front=unary_union([Polygon(t[:,:2]) for t in bottom])
front_difference=actual_front.symmetric_difference(expected_front).area
assert front_difference<.05, f'Stale or incorrect tube STL: front difference {front_difference} mm2'
assert all(m.is_watertight and m.is_winding_consistent for m in parts)
assert parts[0].body_count==1 and parts[1].body_count==130
ss=[solid(m) for m in parts]
fused=trimesh.load(OUT/'roanoke_star_A1_geometry_reference.stl')
assert fused.is_watertight and fused.is_winding_consistent and fused.body_count==1
material_union=ss[0]+ss[1]
coverage_difference=((material_union-solid(fused))+(solid(fused)-material_union)).volume()
assert abs(coverage_difference)<.001,coverage_difference
overlap=(ss[0]^ss[1]).volume()
assert abs(overlap)<1e-4,overlap
assert abs(fused.volume-sum(m.volume for m in parts))<.01
assert np.all(fused.extents<256) and fused.bounds[0,2]>=-1e-6

def stats(m):
    return {'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),
            'connected_solids':int(m.body_count),'triangles':len(m.faces),
            'zero_area_triangles':int(np.sum(m.area_faces<1e-10)),
            'duplicate_triangles':int(len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0))),
            'volume_cm3':float(m.volume/1000),'bounds_mm':m.bounds.tolist()}

# Check the actual fused surface; white/dark interfaces are internal, not overhangs.
angles=np.degrees(np.arcsin(np.clip(-fused.face_normals[:,2],-1,1)))
above_bed=np.min(fused.triangles[:,:,2],axis=1)>1e-4
bad=(angles>45.05)&above_bed&(fused.area_faces>1e-7)
assert np.sum(fused.area_faces[bad])<.01, np.sum(fused.area_faces[bad])

# The pentagonal bore contains a straight-axis circular tapered mandrel. Use a
# declared 0.05mm radial allowance to avoid treating tangency as interference.
n=256;vv=[]
for y,r in [(-32,16.95),(48,10.95)]:
    vv.extend([(r*math.cos(t*2*math.pi/n),y,23.4+r*math.sin(t*2*math.pi/n)) for t in range(n)])
ff=[]
for i in range(n):
    j=(i+1)%n;ff.extend([(i,j,n+j),(i,n+j,n+i)])
for i in range(1,n-1):ff.extend([(0,i+1,i),(n,n+i,n+i+1)])
mandrel=trimesh.Trimesh(vv,ff,process=True);trimesh.repair.fix_normals(mandrel)
mandrel_overlap=(solid(fused)^solid(mandrel)).volume()
assert abs(mandrel_overlap)<1e-4,mandrel_overlap

report={'date':'2026-09-13','material_meshes':dict(zip(['dark_body','white_tube_sections'],map(stats,parts))),
        'white_stl_front_difference_from_current_profiles_mm2':front_difference,
        'fused_print':stats(fused),'material_overlap_mm3':overlap,
        'material_coverage_difference_from_outer_solid_mm3':coverage_difference,
        'dimensions_mm':fused.extents.tolist(),'solid_PLA_estimate_g':fused.volume*.00124,
        'center_of_mass_mm':fused.center_mass.tolist(),
        'socket_axis_depth_mm':23.4,
        'center_of_mass_forward_of_socket_axis_mm':23.4-fused.center_mass[2],
        'gravity_moment_Nm_solid_PLA':fused.volume*1.24e-6*9.80665*(23.4-fused.center_mass[2])/1000,
        'surface_area_over_45deg_overhang_above_bed_mm2':float(np.sum(fused.area_faces[bad])),
        'mandrel_radial_allowance_mm':.05,'mandrel_overlap_mm3':mandrel_overlap,
        'physical_print_tested':False,'slicer_validation_complete':False,
        'landmark_geometry_verified':False,'tube_joint_schedule_verified':False}

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
def el(parent,name,attrs=None,text=None):
    e=ET.SubElement(parent,'{'+NS+'}'+name,attrs or {});e.text=text;return e
model=ET.Element('{'+NS+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
el(model,'metadata',{'name':'Title'},'Roanoke Star | A1 + AMS lite | one print, no assembly')
el(model,'metadata',{'name':'Description'},'Face-down single fused print. Navy integral body, white individual tube inlays. Outline and tube joint placement are photo-based approximations; see report.')
resources=el(model,'resources');materials=el(resources,'basematerials',{'id':'1'})
el(materials,'base',{'name':'Navy PLA','displaycolor':'#142338FF'})
el(materials,'base',{'name':'White PLA','displaycolor':'#F0F2ECFF'})
for i,(name,m) in enumerate(zip(['Integral body and mount','White tube sections'],parts),2):
    obj=el(resources,'object',{'id':str(i),'name':name,'type':'model','pid':'1','pindex':str(i-2)})
    me=el(obj,'mesh');v=el(me,'vertices')
    for point in m.vertices:el(v,'vertex',{k:f'{x:.8f}' for k,x in zip('xyz',point)})
    f=el(me,'triangles')
    for a,b,c in m.faces:el(f,'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
obj=el(resources,'object',{'id':'4','type':'model','name':'Roanoke Star A1 — single print'})
components=el(obj,'components')
for i in [2,3]:el(components,'component',{'objectid':str(i)})
build=el(model,'build');el(build,'item',{'objectid':'4','transform':'1 0 0 0 1 0 0 0 1 128 128 0'})
content='<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
rels='<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
archive=OUT/'roanoke_star_A1.3mf'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',content);z.writestr('_rels/.rels',rels)
    z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    r=ET.fromstring(z.read('3D/3dmodel.model'))
    assert len(r.findall('./{'+NS+'}build/{'+NS+'}item'))==1
    reconstructed=[]
    for o in r.findall('./{'+NS+'}resources/{'+NS+'}object'):
        me=o.find('{'+NS+'}mesh')
        if me is None:continue
        v=[[float(t.attrib[k]) for k in 'xyz'] for t in me.findall('./{'+NS+'}vertices/{'+NS+'}vertex')]
        f=[[int(t.attrib[k]) for k in ['v1','v2','v3']] for t in me.findall('./{'+NS+'}triangles/{'+NS+'}triangle')]
        m=trimesh.Trimesh(v,f,process=True);assert m.is_watertight;reconstructed.append(m)
    assert abs(sum(m.volume for m in reconstructed)-fused.volume)<.01
report['standard_3mf']={'one_build_object':True,'material_volumes':2,'roundtrip_mesh_validation':True,
                        'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
