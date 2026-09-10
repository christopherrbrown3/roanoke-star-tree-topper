from pathlib import Path
src=Path('/path/to/src/Codex Projects/roanoke-star-tree-topper/scripts/build_roanoke_blender.py').read_text().split('try:main()')[0]
exec(src)
parts=[bpy.data.objects[n] for n in ['RoanokeStar_Base','RoanokeStar_Lights','Tree_Mount']]
for o in parts:
 bm=bmesh.new();bm.from_mesh(o.data)
 for v in bm.verts:
  for z in [0,3.2,3.8,4.6,5,6.4]:
   if abs(v.co.z-z)<.002:v.co.z=z
 for _ in range(3):
  bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.001)
 for v in bm.verts:
  for z in [0,3.2,3.8,4.6,5,6.4]:
   if abs(v.co.z-z)<.002:v.co.z=z
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
base,lights,mount=parts
bpy.context.view_layer.update()
(OUT/'blender_validation.json').write_text(json.dumps({o.name:stats(o) for o in parts},indent=2))
stl(OUT/'roanoke_star_base.stl',[base]);stl(OUT/'roanoke_star_lights.stl',[lights],[Matrix.Translation((0,0,-3.8))]);stl(OUT/'roanoke_star_tree_mount.stl',[mount],[Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,32),(0,0,0,1)))]);stl(OUT/'roanoke_star_assembled.stl',parts)
# Hide presentation rig in modeling viewport, keeping it in renders.
for o in bpy.context.scene.objects:
 if o.type in ['LIGHT','CAMERA']:o.hide_set(True)
active(base)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'roanoke_star_tree_topper.blend'))
