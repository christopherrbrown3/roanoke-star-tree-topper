"""Validate the meshes and package explicit Bambu part-to-filament assignments."""
import hashlib,json,math,zipfile
from datetime import date
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
                           for p in prepared['white_material']])
triangles=parts[1].triangles
bottom=triangles[np.all(np.abs(triangles[:,:,2])<1e-7,axis=1)]
actual_front=unary_union([Polygon(t[:,:2]) for t in bottom])
front_difference=actual_front.symmetric_difference(expected_front).area
assert front_difference<.05, f'Stale or incorrect tube STL: front difference {front_difference} mm2'
assert all(m.is_watertight and m.is_winding_consistent for m in parts)
assert parts[0].body_count==1 and parts[1].body_count==len(prepared['white_material'])
assert all(m.area_faces.min()>1e-10 for m in parts)
assert all(len(m.faces)==len(np.unique(np.sort(m.faces,axis=1),axis=0)) for m in parts)
intersections=json.loads((OUT/'self_intersections.json').read_text())
assert all(r['nonadjacent_triangle_intersection_candidates']==0 for r in intersections.values())
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

# Check the actual engraved floor rather than only trusting the text cutter.
engraving=json.loads((OUT/'engraving_measurements.json').read_text())
lettering=unary_union([Polygon(np.asarray(t)[:,:2]) for t in engraving['top_triangles_mm']])
floor_faces=parts[0].triangles[np.all(np.abs(parts[0].triangles[:,:,2]-3.4)<1e-5,axis=1)]
actual_floor=unary_union([Polygon(t[:,:2]) for t in floor_faces])
floor_difference=actual_floor.symmetric_difference(lettering).area
assert floor_difference<.01, f'Missing or incorrect engraving: {floor_difference} mm2'
outline=Polygon(prepared['outline'][0]['loops'][0])
mount_foot=Polygon([(-19.4,-32),(19.4,-32),(13.4,48),(-13.4,48)])
assert lettering.difference(outline).area<1e-6
assert lettering.distance(mount_foot)>7
assert all(not p.buffer(-.2).is_empty for p in lettering.geoms)
engraving_check={
    'text':engraving['text'],'depth_mm':.6,
    'actual_floor_difference_from_lettering_mm2':floor_difference,
    'clearance_to_socket_mm':lettering.distance(mount_foot),
    'clearance_to_outline_mm':lettering.distance(outline.boundary),
    'remaining_material_above_front_inlays_mm':2.4,
    'all_glyph_components_accommodate_0_4mm_tool':True,
}

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

report={'date':date.today().isoformat(),'material_meshes':dict(zip(['dark_body','white_tube_sections'],map(stats,parts))),
        'white_stl_front_difference_from_current_profiles_mm2':front_difference,
        'engraving':engraving_check,
        'fused_print':stats(fused),'material_overlap_mm3':overlap,
        'material_coverage_difference_from_outer_solid_mm3':coverage_difference,
        'dimensions_mm':fused.extents.tolist(),'solid_PLA_estimate_g':fused.volume*.00124,
        'center_of_mass_mm':fused.center_mass.tolist(),
        'socket_axis_depth_mm':23.4,
        'center_of_mass_forward_of_socket_axis_mm':23.4-fused.center_mass[2],
        'gravity_moment_Nm_solid_PLA':fused.volume*1.24e-6*9.80665*(23.4-fused.center_mass[2])/1000,
        'surface_area_over_45deg_overhang_above_bed_mm2':float(np.sum(fused.area_faces[bad])),
        'mandrel_radial_allowance_mm':.05,'mandrel_overlap_mm3':mandrel_overlap,
        'physical_print_tested':False,
        'prior_revision_print_evidence':'Owner reports a successful two-color STL print of the unengraved tube-only face; current backing-band revision has not been physically printed.',
        'slicer_validation_complete':False,
        'landmark_geometry_verified':False,'tube_joint_schedule_verified':False}

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
def el(parent,name,attrs=None,text=None):
    e=ET.SubElement(parent,'{'+NS+'}'+name,attrs or {});e.text=text;return e
model=ET.Element('{'+NS+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US',
                               'xmlns:BambuStudio':'http://schemas.bambulab.com/package/2021'})
# Bambu's importer gates its native metadata parser on this compatibility tag.
# Core basematerial display colors alone do not assign AMS filaments.
el(model,'metadata',{'name':'Application'},'BambuStudio-02.05.00.66')
el(model,'metadata',{'name':'BambuStudio:3mfVersion'},'1')
el(model,'metadata',{'name':'Title'},'Roanoke Star | A1 + AMS lite | one print, no assembly')
el(model,'metadata',{'name':'Designer'},'christopherrbrown3 | christopherbrown.io')
el(model,'metadata',{'name':'Copyright'},'2026 christopherrbrown3 | christopherbrown.io')
el(model,'metadata',{'name':'License'},'CC BY-NC-SA 4.0')
el(model,'metadata',{'name':'LicenseTerms'},'CC BY-NC-SA 4.0; https://creativecommons.org/licenses/by-nc-sa/4.0/')
el(model,'metadata',{'name':'Description'},'One face-down print. Filament 1: dark integral body and tube outlines. Filament 2: white tubes and backing bands. Recessed christopherbrown.io on back. Photo-informed geometry; see report.')
resources=el(model,'resources');materials=el(resources,'basematerials',{'id':'1'})
el(materials,'base',{'name':'Navy PLA','displaycolor':'#142338FF'})
el(materials,'base',{'name':'White PLA','displaycolor':'#F0F2ECFF'})
part_names=['Dark body and mount','White tubes and backing bands']
for i,(name,m) in enumerate(zip(part_names,parts),2):
    obj=el(resources,'object',{'id':str(i),'name':name,'type':'model','pid':'1','pindex':str(i-2)})
    me=el(obj,'mesh');v=el(me,'vertices')
    for point in m.vertices:el(v,'vertex',{k:f'{x:.8f}' for k,x in zip('xyz',point)})
    f=el(me,'triangles')
    for a,b,c in m.faces:el(f,'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
obj=el(resources,'object',{'id':'4','type':'model','name':'Roanoke Star A1 — single print'})
components=el(obj,'components')
for i in [2,3]:el(components,'component',{'objectid':str(i)})
build=el(model,'build');el(build,'item',{'objectid':'4','transform':'1 0 0 0 1 0 0 0 1 128 128 0'})
content='<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/><Default Extension="txt" ContentType="text/plain"/></Types>'
rels='<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'

settings=ET.Element('config')
def metadata(parent,key,value):
    return ET.SubElement(parent,'metadata',{'key':key,'value':str(value)})
assembly=ET.SubElement(settings,'object',{'id':'4'})
metadata(assembly,'name','Roanoke Star A1')
metadata(assembly,'extruder',1)
ET.SubElement(assembly,'metadata',{'face_count':str(sum(len(m.faces) for m in parts))})
for resource_id,filament,name,m in zip([2,3],[1,2],part_names,parts):
    # These IDs reference mesh resources, not ordinal positions. Bambu's
    # _generate_volumes_new matches VolumeMetadata.subobject_id to the mesh ID.
    part=ET.SubElement(assembly,'part',{'id':str(resource_id),'subtype':'normal_part'})
    metadata(part,'name',name)
    metadata(part,'extruder',filament)
    metadata(part,'matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    ET.SubElement(part,'mesh_stat',{'face_count':str(len(m.faces)),
        'edges_fixed':'0','degenerate_facets':'0','facets_removed':'0',
        'facets_reversed':'0','backwards_edges':'0'})
plate=ET.SubElement(settings,'plate')
metadata(plate,'plater_id',1);metadata(plate,'plater_name','Roanoke Star A1')
metadata(plate,'locked','false')
metadata(plate,'bed_type','Textured PEI Plate')
metadata(plate,'filament_map_mode','Auto For Flush')
# Both project filaments feed the A1's same physical extruder through AMS lite.
metadata(plate,'filament_maps','1 1');metadata(plate,'filament_volume_maps','0 0')
instance=ET.SubElement(plate,'model_instance')
metadata(instance,'object_id',4);metadata(instance,'instance_id',0)
assemble=ET.SubElement(settings,'assemble')
ET.SubElement(assemble,'assemble_item',{'object_id':'4','instance_id':'0',
    'transform':'1 0 0 0 1 0 0 0 1 128 128 0','offset':'0 0 0'})
project_settings=json.loads((ROOT/'scripts/a1_bambu_settings.json').read_text())
assert project_settings['filament_settings_id']==['Generic PLA @BBL A1']*2
assert project_settings['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
# Bambu merges project settings into installed system presets. Values omitted
# from this native dirty-key list are reset to the system preset on import.
# Entries are ordered: print process, each project filament, printer.
overrides=project_settings['different_settings_to_system']
assert len(overrides)==len(project_settings['filament_settings_id'])+2
required_overrides={'wall_loops','wall_generator','bottom_shell_layers',
                    'sparse_infill_pattern','brim_type','enable_support'}
assert required_overrides <= set(overrides[0].split(';'))
archive=OUT/'roanoke_star_A1.3mf'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    # Stable ZIP metadata lets native-slicer evidence identify the exact package
    # across rebuilds that do not change its geometry or configuration.
    def write_entry(name,data):
        info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644 << 16
        z.writestr(info,data)
    write_entry('[Content_Types].xml',content);write_entry('_rels/.rels',rels)
    write_entry('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
    write_entry('Metadata/model_settings.config',ET.tostring(settings,encoding='utf-8',xml_declaration=True))
    write_entry('Metadata/project_settings.config',json.dumps(project_settings,indent=2))
    write_entry('Metadata/LICENSE.txt',(ROOT/'LICENSE').read_bytes())
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
    native=ET.fromstring(z.read('Metadata/model_settings.config'))
    native_parts=native.find("object[@id='4']").findall('part')
    assignments={int(p.get('id')):int(p.find("metadata[@key='extruder']").get('value')) for p in native_parts}
    assert assignments=={2:1,3:2}
    assert [int(c.get('objectid')) for c in r.findall('.//{'+NS+'}component')]==list(assignments)
    loaded_settings=json.loads(z.read('Metadata/project_settings.config'))
    assert len(loaded_settings['filament_colour'])==len(assignments)==2
    assert loaded_settings['different_settings_to_system']==overrides
    assert native.find("plate/metadata[@key='bed_type']").get('value')=='Textured PEI Plate'
report['standard_3mf']={'one_build_object':True,'material_volumes':2,'roundtrip_mesh_validation':True,
                        'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
report['bambu_project']={'format_version':1,'compatibility_version':'02.05.00.66',
    'explicit_part_filaments':assignments,'project_filaments':2,
    'printer':'Bambu Lab A1 0.4 nozzle','layer_height_mm':.2,
    'plate':'Textured PEI Plate','supports':False,'prime_tower':True,
    'explicit_process_overrides':overrides[0].split(';'),
    'license_embedded':True,'contains_sliced_toolpath':False}
slicer_report=OUT/'slicer_validation.json'
if slicer_report.exists():
    evidence=json.loads(slicer_report.read_text())
    report['slicer_validation_complete']=(
        evidence.get('status')=='passed' and
        evidence.get('source_3mf_sha256')==report['standard_3mf']['sha256'])
    if report['slicer_validation_complete']:
        report['slicer_validation_report']='slicer_validation.json'
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
