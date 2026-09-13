"""Run in the SAME Blender GUI console after build and canonicalization."""
import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'print_in_place'
assert callable(globals().get('stl')) and callable(globals().get('stats')), 'Run the GUI build first'
body=bpy.data.objects['RoanokeStar_Body']
materials=list(body.data.materials)
data=json.loads((ROOT/'tmp/a1_canonical_body.json').read_text())
mesh=bpy.data.meshes.new('Backing with repaired coplanar triangulation')
mesh.from_pydata(data['v'],[],data['f']);mesh.update()
body.data=mesh
for material in materials:mesh.materials.append(material)
body['triangulation']='Canonicalized coplanar Boolean faces; no change to tube path construction'
bpy.context.view_layer.update()
stl(OUT/'body_material.stl',[body])
lights=bpy.data.objects['RoanokeStar_Tube_Sections']
(OUT/'blender_validation.json').write_text(json.dumps({o.name:stats(o) for o in [body,lights]},indent=2)+'\n')
print('Canonical backing returned to Blender and exported. Run the intersection check next.')
