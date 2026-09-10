from pathlib import Path
import numpy as np, trimesh, zipfile, xml.etree.ElementTree as ET, json, hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'final'
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def element(parent,name,attrib={},text=None):
 e=ET.SubElement(parent,'{'+ns+'}'+name,attrib);e.text=text;return e
model=ET.Element('{'+ns+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
element(model,'metadata',{'name':'Title'},'Roanoke Star Tree Topper — assembled three objects, two colors')
element(model,'metadata',{'name':'Description'},'Assembly reference with material assignments. Use individual STL files for pre-oriented support-minimized printing; light group contains six separate outline inserts in three pairs.')
resources=element(model,'resources');mats=element(resources,'basematerials',{'id':'1'})
element(mats,'base',{'name':'Midnight navy','displaycolor':'#142A42FF'});element(mats,'base',{'name':'Warm white','displaycolor':'#F0F2E9FF'})
parts=[]
for i,(file,name) in enumerate([('roanoke_star_base.stl','RoanokeStar_Base'),('roanoke_star_lights.stl','RoanokeStar_Lights'),('roanoke_star_tree_mount.stl','Tree_Mount')],2):
 mesh=trimesh.load(OUT/file)
 if i==3:mesh.apply_translation([0,0,3.8])
 if i==4:mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0])@trimesh.transformations.translation_matrix([0,0,-32]))
 parts.append(mesh)
 obj=element(resources,'object',{'id':str(i),'type':'model','name':name,'pid':'1','pindex':'1' if i==3 else '0'})
 m=element(obj,'mesh');v=element(m,'vertices')
 for x,y,z in mesh.vertices:element(v,'vertex',dict(zip(['x','y','z'],[f'{x:.7f}',f'{y:.7f}',f'{z:.7f}'])))
 fs=element(m,'triangles')
 for a,b,c in mesh.faces:element(fs,'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
build=element(model,'build')
for i in [2,3,4]:element(build,'item',{'objectid':str(i)})
content='''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''
rels='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
with zipfile.ZipFile(OUT/'roanoke_star_tree_topper.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',content);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
# Parse the saved file and verify reconstructed dimensions/topology, not just ZIP validity.
with zipfile.ZipFile(OUT/'roanoke_star_tree_topper.3mf') as z:
 assert z.testzip() is None
 root=ET.fromstring(z.read('3D/3dmodel.model'));checks=[]
 for obj in root.findall('.//{'+ns+'}object'):
  v=[[float(e.attrib[k]) for k in ['x','y','z']] for e in obj.findall('.//{'+ns+'}vertex')]
  f=[[int(e.attrib[k]) for k in ['v1','v2','v3']] for e in obj.findall('.//{'+ns+'}triangle')]
  m=trimesh.Trimesh(v,f,process=True);assert m.is_watertight
  checks.append({'name':obj.attrib['name'],'watertight':True,'triangles':len(f),'dimensions_mm':m.extents.tolist()})
(OUT/'3mf_validation.json').write_text(json.dumps(checks,indent=2))
print('3MF package and topology validation passed.')
