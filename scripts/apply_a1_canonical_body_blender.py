"""Run in the SAME Blender GUI console after build and canonicalization."""
import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'print_in_place'
assert callable(globals().get('stl')) and callable(globals().get('stats')), 'Run the GUI build first'
objects=[]
for label,name,filename in [('body','RoanokeStar_Body','body_material.stl'),
                            ('white','RoanokeStar_Tube_Sections','white_tube_material.stl')]:
    obj=bpy.data.objects[name]
    materials=list(obj.data.materials)
    data=json.loads((ROOT/f'tmp/a1_canonical_{label}.json').read_text())
    mesh=bpy.data.meshes.new(f'{label} with canonical coplanar triangulation')
    mesh.from_pydata(data['v'],[],data['f']);mesh.update()
    obj.data=mesh
    for material in materials:mesh.materials.append(material)
    obj['triangulation']='Canonicalized coplanar faces; no change to path construction'
    bpy.context.view_layer.update()
    stl(OUT/filename,[obj]);objects.append(obj)
(OUT/'blender_validation.json').write_text(json.dumps({o.name:stats(o) for o in objects},indent=2)+'\n')
print('Canonical material meshes returned to Blender and exported.')
