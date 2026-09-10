from pathlib import Path
src=Path('/Users/chris/Codex Projects/roanoke-star-tree-topper/scripts/build_roanoke_blender.py').read_text().split('try:main()')[0]
exec(src.replace("mod.solver='EXACT'","mod.solver='MANIFOLD'"))
out={}
base=extrude('Test_Base','outline',0,3.2);out['initial']=stats(base)
for i in range(3):
 boolean(base,extrude('band',f'band{i}',3.1,5),'UNION');out[f'band{i}']=stats(base)
for i in range(3):
 boolean(base,extrude('pocket',f'pocket{i}',3.8,5.6));out[f'pocket{i}']=stats(base)
for x in [-21,21]:
 for y in [16,26]:boolean(base,cylinder('pilot',1,3,(x,y,1.3)))
for x in [-13,13]:boolean(base,box('key',(x,6,.6),(4.6,4.6,1.6)))
out['before_bevel']=stats(base)
bevel(base,.15)
bm=bmesh.new();bm.from_mesh(base.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0002);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0002);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(base.data);bm.free()
out['final']=stats(base)
(OUT/'base_debug.json').write_text(json.dumps(out,indent=2))
