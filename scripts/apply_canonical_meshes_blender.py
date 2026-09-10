import bpy,json
from pathlib import Path
ROOT=Path('/Users/chris/Codex Projects/roanoke-star-tree-topper')
D=json.loads((ROOT/'scripts/canonical_meshes.json').read_text())
for name,p in D.items():
 o=bpy.data.objects[name];materials=list(o.data.materials);m=bpy.data.meshes.new(name+' validated mesh');m.from_pydata(p['v'],[],p['f']);m.update();o.data=m
 for mat in materials:m.materials.append(mat)
parts=[bpy.data.objects[n] for n in ['RoanokeStar_Base','RoanokeStar_Lights','Tree_Mount']]
exec('base,lights,mount=parts'+(ROOT/'scripts/finalize_roanoke_blender.py').read_text().split('base,lights,mount=parts')[1])
exec((ROOT/'scripts/check_self_intersections_blender.py').read_text())
