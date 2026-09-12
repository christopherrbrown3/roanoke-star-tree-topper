"""Executed in Blender's GUI Python console. Dimensions are millimeters."""
import bpy, bmesh, math, json, struct, traceback
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path('/Users/chris/Codex Projects/roanoke-star-tree-topper')
OUT=ROOT/'final'; PRE=ROOT/'previews'
P=json.loads((ROOT/'scripts/topper_profiles.json').read_text())

def active(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def mesh_obj(name,v,f):
    m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    return o

def extrude(name,key,lo,hi):
    vv=[];ff=[]
    for part in P[key]:
        v=part['v'];n=len(v);offset=len(vv)
        vv.extend([(x,y,lo) for x,y in v]);vv.extend([(x,y,hi) for x,y in v])
        for a,b,c in part['f']:
            ff.extend([(offset+c,offset+b,offset+a),(offset+n+a,offset+n+b,offset+n+c)])
        for loop in part['loops']:
            ids=[min(range(n),key=lambda j:(v[j][0]-x)**2+(v[j][1]-y)**2) for x,y in loop]
            for a,b in zip(ids,ids[1:]+ids[:1]):ff.append((offset+a,offset+b,offset+n+b,offset+n+a))
    return mesh_obj(name,vv,ff)

def boolean(obj,cut,op='DIFFERENCE'):
    active(obj);mod=obj.modifiers.new(op+' '+cut.name,'BOOLEAN');mod.operation=op;mod.solver='MANIFOLD';mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)

def bevel(obj,w=.15):
    clean(obj)
    active(obj);m=obj.modifiers.new('Manufacturing edge break','BEVEL');m.width=w;m.segments=2;m.limit_method='ANGLE';m.angle_limit=.35
    bpy.ops.object.modifier_apply(modifier=m.name)
    clean(obj)

def clean(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0002)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0002)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free()

def box(name,center,size):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o

def cylinder(name,rad,depth,loc,axis='Z',vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=rad,depth=depth,location=loc);o=bpy.context.object;o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    active(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o

def material(name,color,rough=.4):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
    return m

def cone_socket():
    # Four concentric section rings define an open through-bore; all walls closed.
    n=128;v=[]
    for y,r in [(-32,19.4),(48,13.4),(-32,17),(48,11)]:
        v.extend([(r*math.cos(t*2*math.pi/n),y,-21.8+r*math.sin(t*2*math.pi/n)) for t in range(n)])
    f=[]
    for i in range(n):
        j=(i+1)%n
        f.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh_obj('Tree_Mount',v,f)

def evaluated_mesh(o):
    deps=bpy.context.evaluated_depsgraph_get();return o.evaluated_get(deps).to_mesh()

def triangles(o,transform=None):
    m=evaluated_mesh(o);m.calc_loop_triangles();M=transform if transform is not None else o.matrix_world
    return [[M@m.vertices[i].co for i in t.vertices] for t in m.loop_triangles]

def stl(path,objects,matrices=None):
    ts=[]
    for idx,o in enumerate(objects):ts.extend(triangles(o,matrices[idx] if matrices else None))
    with open(path,'wb') as f:
        f.write(b'Roanoke Star | units: mm'.ljust(80,b' '));f.write(struct.pack('<I',len(ts)))
        for a,b,c in ts:
            n=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*n,*a,*b,*c,0))

def stats(o):
    m=evaluated_mesh(o);bm=bmesh.new();bm.from_mesh(m)
    result={'dimensions_mm':list(o.dimensions),'volume_mm3':bm.calc_volume(signed=True),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'wire_edges':sum(e.is_wire for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'vertices':len(bm.verts),'faces':len(bm.faces),'scale':list(o.scale)}
    bm.free();return result

def look(o,point):
    direction=(Vector(point)-o.location).normalized();right=direction.cross(Vector((0,1,0))).normalized();up=right.cross(direction)
    o.rotation_euler=Matrix((right,up,-direction)).transposed().to_euler()

def render_view(name,loc,target=(0,8,-5),scale=245):
    cam=bpy.context.scene.camera;cam.location=loc;cam.data.ortho_scale=scale;look(cam,target)
    bpy.context.scene.render.filepath=str(PRE/name);bpy.ops.render.render(write_still=True)

def main():
    for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
    for coll in list(bpy.data.collections):
        if coll.name.startswith('Reference_Geometry'):bpy.data.collections.remove(coll)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
    navy=material('Midnight navy | base and mount',(.018,.041,.075),.32);white=material('Warm white | physical light inserts',(.91,.93,.88),.28)
    base=extrude('RoanokeStar_Base','outline',0,3.2)
    for i in range(3):boolean(base,extrude('Raised channel surround',f'band{i}',3.1,5),'UNION')
    for i in range(3):boolean(base,extrude('0.30 mm clearance pocket',f'pocket{i}',3.8,5.6))
    # Blind screw pilots and locating pockets from rear.
    for x in [-21,21]:
        for y in [13,23]:boolean(base,cylinder('Blind 2.0 mm pilot',1,3,(x,y,1.3)))
    for x in [-13,13]:boolean(base,box('4.6 mm key pocket',(x,3,.6),(4.6,4.6,1.6)))
    bevel(base,.15);base.data.materials.clear();base.data.materials.append(navy)
    base['plate_mm']=3.2;base['channel_top_mm']=5.0;base['channel_floor_mm']=3.8;base['clearance_per_side_mm']=.3
    inserts=[]
    for i in range(3):
        o=extrude(f'Light_Frame_{i+1}',f'rails{i}',3.8,6.4)
        # Rounded 2D rail corners preserve the path without fragile bevel miters.
        inserts.append(o)
    active(inserts[0])
    for o in inserts:o.select_set(True)
    bpy.ops.object.join();lights=bpy.context.object;lights.name='RoanokeStar_Lights';lights.data.materials.clear();lights.data.materials.append(white)
    lights['intentional_shells']=6;lights['minimum_rail_width_mm']=1.8;lights['insert_height_mm']=2.6;lights['geometry_basis']='Unverified photographic reconstruction; six traced paths, assumed rectification; see ACCURACY_AUDIT.md';lights['assembly']='Six outline inserts in three pairs, one white color group; glue after dry fitting.'
    mount=cone_socket()
    boolean(mount,box('Rear relief slot',(0,8,-39),(3,82,15)))
    # Central support web: 45 degree underside from tube into flange.
    webv=[]
    for y,half_width,back,front in [(-15,1,-4.4,-3.8),(-6,10,-5.35,0),(28,10,-7.9,0)]:
        webv.extend([(-half_width,y,back),(half_width,y,back),(half_width,y,front),(-half_width,y,front)])
    webf=[(3,2,1,0),(8,9,10,11)]
    for level in range(2):
        for i in range(4):
            j=(i+1)%4;a=level*4;webf.append((a+i,a+j,a+4+j,a+4+i))
    boolean(mount,mesh_obj('Inclined socket web',webv,webf),'UNION')
    boolean(mount,extrude('Mount flange','flange',-3.2,0),'UNION')
    for x in [-21,21]:
        for y in [13,23]:boolean(mount,cylinder('2.9 mm screw clearance',1.45,6,(x,y,-1.5)))
    for x in [-13,13]:boolean(mount,box('Locating key',(x,3,-.5),(4,4,3.4)),'UNION')
    for y in [-19,21]:boolean(mount,cylinder('4 mm tie holes',2,46,(0,y,-21.8),'X'))
    bevel(mount,.18);mount.data.materials.clear();mount.data.materials.append(navy)
    mount['nominal_bore_mm']='34 lower / 22 upper';mount['insertion_depth_mm']=80;mount['wall_radial_mm']=2.4;mount['hardware']='4 x 2.5 mm diameter x 6 mm long plastic-thread pan-head screws';mount['print_orientation']='Large mouth on bed, socket axis vertical'
    for o in [base,lights,mount]:
        active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for face in o.data.polygons:face.material_index=0
    # Preserve editable 2D paths and reference photo without adding export geometry.
    ref=bpy.data.collections.new('Reference_Geometry');scene.collection.children.link(ref);ref.hide_render=True;ref.hide_viewport=True
    measure=json.loads((OUT/'profile_measurements.json').read_text())
    for i,coords in enumerate(measure['six_paths_mm']):
        c=bpy.data.curves.new(f'Measured light path {i+1}','CURVE');c.dimensions='2D';sp=c.splines.new('POLY');sp.points.add(len(coords)-1)
        for pt,(x,y) in zip(sp.points,coords):pt.co=(x,y,0,1)
        sp.use_cyclic_u=True;o=bpy.data.objects.new(c.name,c);ref.objects.link(o)
    photo=ROOT/'research/references/city_aerial_original.jpg'
    if photo.exists():
        img=bpy.data.images.load(str(photo));img.pack();o=bpy.data.objects.new('City photo | near frontal aerial',None);o.empty_display_type='IMAGE';o.data=img;o.empty_display_size=240;ref.objects.link(o)
    txt=bpy.data.texts.new('BUILD_SOURCE.py');txt.write(Path(__file__).read_text())
    txt=bpy.data.texts.new('MEASURED_PATHS.json');txt.write((OUT/'profile_measurements.json').read_text())
    txt=bpy.data.texts.new('TOPPER_PROFILES.json');txt.write((ROOT/'scripts/topper_profiles.json').read_text())
    txt=bpy.data.texts.new('README');txt.write('All dimensions in mm. Final three printable object groups. Six closed white outline inserts intentionally share one object. Source profiles and reconstruction parameters are saved alongside this blend. Dark socket is hidden from the front. Exported individual STL files are already oriented on the bed. See DESIGN_REPORT.md for screws, print settings and validation limits.')
    # Numerical Blender validation, with independent export audit performed afterward.
    bpy.context.view_layer.update();validation={o.name:stats(o) for o in [base,lights,mount]}
    (OUT/'blender_validation.json').write_text(json.dumps(validation,indent=2))
    stl(OUT/'roanoke_star_base.stl',[base])
    stl(OUT/'roanoke_star_lights.stl',[lights],[Matrix.Translation((0,0,-3.8))])
    # Rotate assembled Y-axis socket upright onto its large opening.
    M=Matrix.Translation((0,0,32))@Matrix.Rotation(math.pi/2,4,'X')
    stl(OUT/'roanoke_star_tree_mount.stl',[mount],[M])
    stl(OUT/'roanoke_star_assembled.stl',[base,lights,mount])
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world.color=(.25,.25,.25);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.4,.5,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    scene.view_settings.view_transform='AgX'
    bpy.ops.object.camera_add(location=(0,8,430));cam=bpy.context.object;cam.name='Preview_Camera';cam.data.type='ORTHO';cam.data.lens=50;cam.data.clip_end=2000;scene.camera=cam
    for name,loc,power,size in [('Key',(-150,200,260),2300000,230),('Fill',(180,30,170),1200000,180),('Rim',(-100,130,-240),2000000,180)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;look(o,(0,0,0))
    active(base)
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=285;area.spaces.active.region_3d.view_location=(0,8,0);area.spaces.active.clip_end=2000;area.spaces.active.shading.color_type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'roanoke_star_tree_topper.blend'))
    (OUT/'BUILD_COMPLETE.txt').write_text('Blender model created, validated numerically, saved and STL files exported.\n')
    return
    render_view('front.png',(0,8,440),(0,8,0),235)
    render_view('three_quarter.png',(245,110,360),(0,8,-9),248)
    render_view('rear.png',(150,75,-390),(0,8,-12),245)
    (OUT/'RENDERS_COMPLETE.txt').write_text('Three assembled views rendered in Blender.\n')
try:main()
except Exception:
    (OUT/'BUILD_ERROR.txt').write_text(traceback.format_exc());raise
