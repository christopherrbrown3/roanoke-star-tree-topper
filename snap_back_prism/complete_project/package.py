"""Package the approved front and V2 back as two native Bambu Studio plates.

No mesh generation or reorientation. Requires only Python's standard library
and the two source 3MF projects committed beside this directory.

Plate spacing (256 * 1.2 mm) and model_instance/assemble representation were
checked against a native Bambu A1 two-plate project. Prime tower is a project
setting: retain the front's enabled setting; native slicing must verify that
Bambu omits it on the single-filament back plate.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
FRONT = BASE/'spacing_v3/front_shell_A1.3mf'
BACK = BASE/'continuous_ridge_back_v2/continuous_ridge_back_A1.3mf'
OUTPUT = HERE/'complete_topper_A1.3mf'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
Q = '{'+NS+'}'
ET.register_namespace('', NS)
TITLE = 'Roanoke Star complete topper - front and V2 back'
PLATE_OFFSET = 307.2


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {name:z.read(name) for name in z.namelist()}


def metadata(parent, key, value):
    for el in parent.findall('metadata'):
        if el.get('key') == key:
            el.set('value', str(value))
            return
    ET.SubElement(parent, 'metadata', {'key':key,'value':str(value)})


def mesh_digest(obj):
    """Hash exact coordinate/face strings, independent of XML whitespace."""
    mesh = obj.find(Q+'mesh')
    vertices = [tuple(v.get(k) for k in ('x','y','z')) for v in mesh.find(Q+'vertices')]
    triangles = [tuple(sorted(t.attrib.items())) for t in mesh.find(Q+'triangles')]
    return sha(json.dumps([vertices,triangles],separators=(',',':')).encode())


def shifted(transform, dx):
    values = transform.split()
    assert len(values) == 12
    values[9] = f'{float(values[9])+dx:g}'
    return ' '.join(values)


def main():
    source_hashes = {str(p.relative_to(BASE)):sha(p.read_bytes()) for p in (FRONT,BACK)}
    front,back = read(FRONT),read(BACK)
    fm,bm = [ET.fromstring(x['3D/3dmodel.model']) for x in (front,back)]
    fc,bc = [ET.fromstring(x['Metadata/model_settings.config']) for x in (front,back)]
    fs,bs = [json.loads(x['Metadata/project_settings.config']) for x in (front,back)]
    differing = {k for k in set(fs)|set(bs) if fs.get(k)!=bs.get(k)}
    assert differing == {'enable_prime_tower'}, differing
    assert fs['enable_prime_tower']=='1' and bs['enable_prime_tower']=='0'
    assert fs['enable_support']=='0' and fs['layer_height']=='0.2'
    assert fs['nozzle_diameter']==['0.4'] and fs['printer_model']=='Bambu Lab A1'
    assert fs['filament_colour']==['#FFFFFF','#000000']
    model,config = deepcopy(fm),deepcopy(fc)
    resources = model.find(Q+'resources')
    front_objects = {o.get('id'):o for o in fm.find(Q+'resources') if o.tag==Q+'object'}
    back_objects = {o.get('id'):o for o in bm.find(Q+'resources') if o.tag==Q+'object'}
    assert set(front_objects)=={'2','3','20'} and set(back_objects)=={'2','20'}
    # Mesh XML is copied without editing any vertex, face or painted property.
    id_map = {'2':'4','20':'21'}
    for obj in back_objects.values():
        obj=deepcopy(obj);obj.set('id',id_map[obj.get('id')])
        for component in obj.findall('./'+Q+'components/'+Q+'component'):
            component.set('objectid',id_map[component.get('objectid')])
        resources.append(obj)
    assert ET.tostring(fm.find('./'+Q+'resources/'+Q+'basematerials')) == ET.tostring(bm.find('./'+Q+'resources/'+Q+'basematerials')) or [x.get('displaycolor') for x in fm.find('./'+Q+'resources/'+Q+'basematerials')] == ['#FFFFFFFF','#000000FF']
    # Both source projects use material indices 0=white and 1=black.
    for obj in list(front_objects.values())+list(back_objects.values()):
        if obj.find(Q+'mesh') is not None:
            assert obj.get('pid')=='1' and obj.get('pindex') in ('0','1')
    assert back_objects['2'].get('pindex')=='0'
    item=deepcopy(bm.find(Q+'build/'+Q+'item'))
    item.set('objectid','21');item.set('transform',shifted(item.get('transform'),PLATE_OFFSET))
    model.find(Q+'build').append(item)
    for el in model.findall(Q+'metadata'):
        if el.get('name')=='Title':el.text=TITLE
        if el.get('name')=='Description':el.text='Complete two-plate A1 project: spacing_v3 white/black diffused front shell and owner-confirmed V2 white back with doubled fixed tabs. Print both plates; project filament 1 white PLA, filament 2 black PLA.'
    plate1=config.find('plate');metadata(plate1,'plater_name','Front shell')
    plate2=deepcopy(bc.find('plate'))
    metadata(plate2,'plater_id',2);metadata(plate2,'plater_name','Back plate - V2 doubled tabs')
    metadata(plate2.find('model_instance'),'object_id',21)
    config.insert(list(config).index(plate1)+1,plate2)
    objconf=deepcopy(bc.find('object'));objconf.set('id','21')
    for part in objconf.findall('part'):part.set('id',id_map[part.get('id')])
    config.append(objconf)
    assembly=deepcopy(bc.find('assemble/assemble_item'))
    assembly.set('object_id','21');assembly.set('transform',shifted(assembly.get('transform'),PLATE_OFFSET))
    config.find('assemble').append(assembly)
    settings=deepcopy(fs)
    for axis in ('wipe_tower_x','wipe_tower_y'):
        settings[axis]=[fs[axis][0],bs[axis][0]]
    entries=dict(front)
    entries['3D/3dmodel.model']=ET.tostring(model,encoding='utf-8',xml_declaration=True)
    entries['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    entries['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in entries.items():
            info=zipfile.ZipInfo(name,date_time=(2026,10,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)
    result=read(OUTPUT)
    outmodel=ET.fromstring(result['3D/3dmodel.model'])
    outobjects={o.get('id'):o for o in outmodel.find(Q+'resources') if o.tag==Q+'object'}
    checks=[]
    for source,oldid,newid,plate,filament in [(front_objects,'2','2',1,1),(front_objects,'3','3',1,2),(back_objects,'2','4',2,1)]:
        actual,expected=mesh_digest(outobjects[newid]),mesh_digest(source[oldid])
        assert actual==expected
        assert int(outobjects[newid].get('pindex'))+1==filament
        mesh=outobjects[newid].find(Q+'mesh')
        checks.append({'plate':plate,'object_id':newid,'filament':filament,
            'vertices':len(mesh.find(Q+'vertices')),'triangles':len(mesh.find(Q+'triangles')),
            'exact_source_mesh_sha256':actual,'source_mesh_identical':True})
    assert len(outmodel.find(Q+'build'))==2
    outconfig=ET.fromstring(result['Metadata/model_settings.config'])
    assert len(outconfig.findall('plate'))==2
    for plate,oid in zip(outconfig.findall('plate'),('20','21')):
        m=plate.find('model_instance/metadata[@key="object_id"]')
        assert m.get('value')==oid
    assert all(sha(p.read_bytes())==source_hashes[str(p.relative_to(BASE))] for p in (FRONT,BACK))
    report={'status':'structural checks passed; native slicing required','output':OUTPUT.name,
        'sha256':sha(OUTPUT.read_bytes()),'source_projects':source_hashes,
        'plates':[{'plate':1,'name':'Front shell','origin_mm':[0,0,0],'assembly_id':20,'build_transform':model.find(Q+'build')[0].get('transform')},
                  {'plate':2,'name':'Back plate - V2 doubled tabs','origin_mm':[PLATE_OFFSET,0,0],'assembly_id':21,'build_transform':item.get('transform')}],
        'mesh_checks':checks,'source_process_differences':['enable_prime_tower'],
        'combined_prime_tower_setting':'enabled globally; verify native slicer omits tower on single-filament back',
        'other_source_print_settings_preserved':True,'source_projects_unchanged':True,
        'native_GUI_validation_complete':False,'printing_performed':False}
    (HERE/'package_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
