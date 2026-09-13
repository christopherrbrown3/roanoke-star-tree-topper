"""Check nonadjacent triangle intersections in the actual Blender color meshes."""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
out={}
for name in ['RoanokeStar_Body','RoanokeStar_Tube_Sections']:
    m=bpy.data.objects[name].data;m.calc_loop_triangles()
    vertices=[v.co.copy() for v in m.vertices]
    faces=[tuple(t.vertices) for t in m.loop_triangles]
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True,epsilon=0)
    candidates=[]
    for a,b in tree.overlap(tree):
        if a>=b or set(faces[a])&set(faces[b]):continue
        candidates.append([a,b])
    out[name]={'nonadjacent_triangle_intersection_candidates':len(candidates),
               'examples':candidates[:20],'extra_distance_exclusion_mm':0}
(Path(__file__).resolve().parents[1]/'print_in_place/self_intersections.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
