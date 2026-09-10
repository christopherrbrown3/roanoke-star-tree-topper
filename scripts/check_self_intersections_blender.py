import bpy,json,bmesh
from mathutils.bvhtree import BVHTree
from pathlib import Path
out={}
for name in ['RoanokeStar_Base','RoanokeStar_Lights','Tree_Mount']:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
 verts=[v.co.copy() for v in m.vertices];faces=[tuple(t.vertices) for t in m.loop_triangles]
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0)
 candidates=[]
 for a,b in tree.overlap(tree):
  if a>=b or set(faces[a])&set(faces[b]):continue
  # Export uses a 1 micron weld; ignore contacts beneath that geometric precision.
  if min((verts[i]-verts[j]).length for i in faces[a] for j in faces[b])<.0011:continue
  candidates.append([a,b])
 out[name]={'nonadjacent_triangle_intersections':len(candidates),'examples':candidates[:20]}
Path('/Users/chris/Codex Projects/roanoke-star-tree-topper/final/self_intersection_check.json').write_text(json.dumps(out,indent=2))
