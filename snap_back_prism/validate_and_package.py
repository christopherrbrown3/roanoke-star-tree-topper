"""Independent checks and separate A1 plates for body, back, and snap sample."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

H=Path(__file__).resolve().parent; ROOT=H.parent
C=json.loads((H/'parameters.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def solid(m):
    s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
    assert s.status()==mf.Error.NoError,s.status()
    return s
keys=['body_navy','body_white_face','snap_back','coupon_catch','coupon_back']
meshes={k:trimesh.load(H/(k+'.stl')) for k in keys}
solids={k:solid(m) for k,m in meshes.items()}
stats={}
for k,m in meshes.items():
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    assert m.area_faces.min()>1e-10
    assert m.body_count==(3 if k=='body_white_face' else 1)
    stats[k]={'watertight':True,'connected_solids':int(m.body_count),'triangles':len(m.faces),
              'volume_mm3':float(m.volume),'sha256':sha(H/(k+'.stl'))}
body=solids['body_navy']+solids['body_white_face']
assert len(body.decompose())==1
body_overlap=(solids['body_navy']^solids['body_white_face']).volume()
seated=(body^solids['snap_back']).volume()
coupon_overlap=(solids['coupon_catch']^solids['coupon_back']).volume()
assert abs(body_overlap)<.01 and abs(seated)<.01 and abs(coupon_overlap)<.01
out=body.to_mesh(); fused=trimesh.Trimesh(out.vert_properties[:,:3],out.tri_verts,process=True)
assert fused.is_watertight and fused.body_count==1
fused.export(H/'front_shell_fused.stl')

P=json.loads((ROOT/'scripts/a1_topper_profiles.json').read_text())
outline=Polygon(P['outline'][0]['loops'][0])
tubes=unary_union([Polygon(p['loops'][0]) for p in P['white_tube_sections']])
bands=unary_union([Polygon(p['loops'][0],p['loops'][1:]) for p in P['white_backing_bands']])
def front(m):
    triangles=m.triangles
    selected=triangles[np.all(np.abs(triangles[:,:,2])<1e-7,axis=1)]
    return unary_union([Polygon(t[:,:2]) for t in selected])
actual=unary_union([front(meshes[k]) for k in ['body_navy','body_white_face']])
face_diff=actual.symmetric_difference(outline.difference(tubes)).area
band_diff=front(meshes['body_white_face']).symmetric_difference(bands).area
slots=outline.difference(actual).buffer(0)
slot_count=sum(p.area>.05 for p in slots.geoms)
assert face_diff<.05 and band_diff<.05 and slot_count==130
mouth=solid(trimesh.load(ROOT/'pentagrammic_prism/construction/bottom_mouth.stl'))
assert abs((mouth^body).volume())<.01
assert abs((mouth^solids['snap_back']).volume())<.01
leader=solid(trimesh.load(ROOT/'pentagrammic_prism/construction/tree_leader_clearance_reference.stl'))
assert abs((leader^(body+solids['snap_back'])).volume())<.01

# This checks the geometric insertion corridor, not elastic deformation or force.
hook_solids=[solid(trimesh.load(H/'construction'/f'hook_{i+1}.stl')) for i in range(6)]
all_hooks=mf.Manifold.batch_boolean(hook_solids,mf.OpType.Add)
rigid_back=solids['snap_back']-all_hooks
max_swept=0.
for z in np.linspace(0,6.2,32):
    max_swept=max(max_swept,abs((body^rigid_back.translate([0,0,float(z)])).volume()))
    for hook,clip in zip(hook_solids,C['clips']):
        n=np.array(clip['outward_xy'])
        displacement=C['maximum_assembly_deflection_mm']
        moved=hook.translate([-float(n[0])*displacement,-float(n[1])*displacement,float(z)])
        max_swept=max(max_swept,abs((body^moved).volume()))
assert max_swept<.01,max_swept
# The relaxed noses occupy real catch undercuts when the windows are filled.
walls=solid(trimesh.load(H/'construction/body_blank.stl'))-solid(trimesh.load(H/'construction/open_cavity.stl'))
engagement=(walls^all_hooks).volume()
assert engagement>1.

report={'status':'passed','geometry':stats,'front_shell_connected_solids':1,
 'assembled_material_overlap_mm3':seated,'body_material_overlap_mm3':body_overlap,
 'sample_seated_overlap_mm3':coupon_overlap,'original_face_difference_mm2':face_diff,
 'original_white_bands_difference_mm2':band_diff,'matching_front_apertures':slot_count,
 'bottom_mouth_clear':True,'tree_leader_reference_clear':True,
 'fully_deflected_hook_sweep_max_collision_mm3':max_swept,
 'hook_sweep_scope':f"32 axial positions with hook heads rigidly translated {C['maximum_assembly_deflection_mm']} mm inward; not a flexural simulation",
 'relaxed_hook_undercut_engagement_volume_mm3':engagement,
 'solid_PLA_estimate_g':float((body.volume()+solids['snap_back'].volume())*.00124),
 'sample_solid_PLA_estimate_g':float((solids['coupon_catch'].volume()+solids['coupon_back'].volume())*.00124),
 'physical_snap_fit_tested':False,'retention_force_tested':False,'thermal_tested':False,
 'incandescent_compatibility_verified':False,'packages':{}}

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def el(parent,name,attrs=None): return ET.SubElement(parent,'{'+NS+'}'+name,attrs or {})
def meta(parent,key,value): return ET.SubElement(parent,'metadata',{'key':key,'value':str(value)})
with zipfile.ZipFile(ROOT/'pentagrammic_prism/roanoke_star_prism_A1.3mf') as z:
    template={n:z.read(n) for n in z.namelist()}
    original_settings=json.loads(z.read('Metadata/project_settings.config'))

def print_mesh(m,flip=False,z_origin=0.):
    m=m.copy()
    if flip:
        m.apply_transform(np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,60],[0,0,0,1]],float))
    else: m.apply_translation([0,0,-z_origin])
    assert m.bounds[0,2]>-.00001
    return m

def package(filename,title,parts,prime=True,brim=4.):
    # Each part is (mesh, name, filament, translation). Separate printable
    # objects are used only for the two connector-sample pieces.
    entries=dict(template)
    model=ET.Element('{'+NS+'}model',{'unit':'millimeter','xmlns:BambuStudio':'http://schemas.bambulab.com/package/2021'})
    for key,value in {'Application':'BambuStudio-02.05.00.66','BambuStudio:3mfVersion':'1',
       'Title':title,'Designer':'christopherrbrown3 | christopherbrown.io',
       'License':'CC BY-NC-SA 4.0','Description':'Experimental snap-back prism. Physical snap fit and thermal validation pending.'}.items():
        e=el(model,'metadata',{'name':key});e.text=value
    resources=el(model,'resources'); mats=el(resources,'basematerials',{'id':'1'})
    el(mats,'base',{'name':'Navy PLA','displaycolor':'#142338FF'})
    el(mats,'base',{'name':'White PLA','displaycolor':'#F0F2ECFF'})
    config=ET.Element('config'); build=el(model,'build')
    assembly_id=20
    groups={}
    for rid,(mesh,name,filament,translation) in enumerate(parts,2):
        obj=el(resources,'object',{'id':str(rid),'name':name,'type':'model','pid':'1','pindex':str(filament-1)})
        me=el(obj,'mesh');vs=el(me,'vertices');ts=el(me,'triangles')
        for point in mesh.vertices: el(vs,'vertex',{k:f'{v:.8f}' for k,v in zip('xyz',point)})
        for a,b,c in mesh.faces:el(ts,'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
        groups.setdefault(tuple(translation),[]).append((rid,mesh,name,filament))
    plate=ET.SubElement(config,'plate')
    for key,value in {'plater_id':1,'plater_name':title,'locked':'false','bed_type':'Textured PEI Plate',
        'filament_map_mode':'Auto For Flush','filament_maps':'1 1','filament_volume_maps':'0 0'}.items():meta(plate,key,value)
    assemble=ET.SubElement(config,'assemble')
    for offset,group in groups.items():
        aid=assembly_id;assembly_id+=1
        obj=el(resources,'object',{'id':str(aid),'name':title,'type':'model'});cs=el(obj,'components')
        native=ET.SubElement(config,'object',{'id':str(aid)})
        meta(native,'name',title);meta(native,'extruder',group[0][3])
        ET.SubElement(native,'metadata',{'face_count':str(sum(len(p[1].faces) for p in group))})
        for rid,m,name,filament in group:
            el(cs,'component',{'objectid':str(rid)})
            part=ET.SubElement(native,'part',{'id':str(rid),'subtype':'normal_part'})
            meta(part,'name',name);meta(part,'extruder',filament)
            meta(part,'matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
            ET.SubElement(part,'mesh_stat',{'face_count':str(len(m.faces)), 'edges_fixed':'0',
              'degenerate_facets':'0','facets_removed':'0','facets_reversed':'0','backwards_edges':'0'})
        placement='1 0 0 0 1 0 0 0 1 '+' '.join(str(v) for v in offset)
        el(build,'item',{'objectid':str(aid),'transform':placement})
        instance=ET.SubElement(plate,'model_instance');meta(instance,'object_id',aid);meta(instance,'instance_id',0)
        ET.SubElement(assemble,'assemble_item',{'object_id':str(aid),'instance_id':'0','transform':placement,'offset':'0 0 0'})
    settings=json.loads(json.dumps(original_settings))
    updates={'enable_support':'0','brim_width':str(brim),'brim_type':'outer_only',
       'enable_prime_tower':'1' if prime else '0','prime_tower_width':'24',
       'prime_tower_brim_width':'2','wipe_tower_x':['20'],'wipe_tower_y':['215']}
    settings.update(updates)
    different=set(settings['different_settings_to_system'][0].split(';'));different.update(updates)
    settings['different_settings_to_system'][0]=';'.join(sorted(different))
    entries['3D/3dmodel.model']=ET.tostring(model,encoding='utf-8',xml_declaration=True)
    entries['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    entries['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    file=H/filename
    with zipfile.ZipFile(file,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in entries.items():
            info=zipfile.ZipInfo(name,date_time=(2026,10,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,value)
    with zipfile.ZipFile(file) as z:
        assert z.testzip() is None
        reopened=ET.fromstring(z.read('3D/3dmodel.model'))
        mesh_objects=[o for o in reopened.findall('./{'+NS+'}resources/{'+NS+'}object') if o.find('{'+NS+'}mesh') is not None]
        for obj,(expected,_,_,_) in zip(mesh_objects,parts):
            me=obj.find('{'+NS+'}mesh')
            v=[[float(e.attrib[k]) for k in 'xyz'] for e in me.findall('.//{'+NS+'}vertex')]
            f=[[int(e.attrib[k]) for k in ['v1','v2','v3']] for e in me.findall('.//{'+NS+'}triangle')]
            actual=trimesh.Trimesh(v,f,process=True)
            assert actual.is_watertight and abs(actual.volume-expected.volume)<.01
    report['packages'][filename]={'sha256':sha(file),'roundtrip_passed':True,
       'build_objects':len(groups),'support_enabled':False,'GUI_slice_complete':False}

package('front_shell_A1.3mf','Snap prism front shell',[
    (print_mesh(meshes['body_navy']),'Navy front shell',1,[128,128,0]),
    (print_mesh(meshes['body_white_face']),'Original white face bands',2,[128,128,0])])
package('snap_back_A1.3mf','Snap prism detachable white back',[
    (print_mesh(meshes['snap_back'],flip=True),'White back with six clips',2,[128,128,0])],prime=False,brim=0.)
package('connector_sample_A1.3mf','Snap connector sample',[
    (print_mesh(meshes['coupon_catch'],z_origin=48.5),'Sample catch wall',2,[103,128,0]),
    (print_mesh(meshes['coupon_back'],flip=True),'Sample spring back',2,[153,128,0])],prime=False,brim=0.)
(H/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
