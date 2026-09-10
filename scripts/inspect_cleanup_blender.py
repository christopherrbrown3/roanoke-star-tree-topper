import bpy,bmesh,json
from pathlib import Path
out={}
for name in ['RoanokeStar_Base','RoanokeStar_Lights','Tree_Mount']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0002)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0002)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 out[name]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-9 for f in bm.faces),'volume':bm.calc_volume()}
 bm.to_mesh(o.data);bm.free()
 o.data.materials.clear();o.data.materials.append(bpy.data.materials['Warm white | physical light inserts' if name=='RoanokeStar_Lights' else 'Midnight navy | base and mount'])
 for p in o.data.polygons:p.material_index=0
Path('/path/to/src/Codex Projects/roanoke-star-tree-topper/final/cleanup_test.json').write_text(json.dumps(out,indent=2))
