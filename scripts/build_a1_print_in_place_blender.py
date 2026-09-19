"""Run through Blender's GUI console. Model coordinates are print-ready mm."""
import bpy, bmesh, json, math, struct, traceback
from pathlib import Path
from mathutils import Vector, Matrix
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'print_in_place'
P = json.loads((ROOT/'scripts/a1_topper_profiles.json').read_text())

def active(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active=o

def mesh_obj(name,verts,faces):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    return obj

def extrude(name,key,z0,z1):
    vv=[];ff=[]
    for part in P[key]:
        v=part['v'];n=len(v);o=len(vv)
        vv.extend([(x,y,z0) for x,y in v]);vv.extend([(x,y,z1) for x,y in v])
        for a,b,c in part['f']:ff.extend([(o+c,o+b,o+a),(o+n+a,o+n+b,o+n+c)])
        for loop in part['loops']:
            ids=[min(range(n),key=lambda j:(v[j][0]-x)**2+(v[j][1]-y)**2) for x,y in loop]
            for a,b in zip(ids,ids[1:]+ids[:1]):ff.append((o+a,o+b,o+n+b,o+n+a))
    return mesh_obj(name,vv,ff)

def boolean(obj,cut,op='DIFFERENCE'):
    active(obj);m=obj.modifiers.new(op+' '+cut.name,'BOOLEAN')
    m.operation=op;m.solver='MANIFOLD';m.object=cut
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cut,do_unlink=True)

def loft(name,rings):
    n=len(rings[0]);assert all(len(r)==n for r in rings)
    v=[p for r in rings for p in r]
    f=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
    for k in range(len(rings)-1):
        for i in range(n):
            j=(i+1)%n;f.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
    return mesh_obj(name,v,f)

def socket():
    c=23.4;w=2.4;root2=math.sqrt(2)
    def radius(y):return 17-(y+32)*6/80
    def outer(y):
        r=radius(y)+w;peak=c+root2*r
        return [(-r,y,3.8),(r,y,3.8),(r,y,peak-r),(0,y,peak),(-r,y,peak-r)]
    def inner(y):
        r=radius(y);peak=c+root2*r
        return [(-r,y,c-r),(r,y,c-r),(r,y,peak-r),(0,y,peak),(-r,y,peak-r)]
    o=loft('Integral tapered socket',[outer(-32),outer(48)])
    boolean(o,loft('34 to 22 mm circular clearance bore',[inner(-32.2),inner(48.2)]))
    for y in [-18,22]:
        diamond=[(y, c-2.5),(y+2.5,c),(y,c+2.5),(y-2.5,c)]
        boolean(o,loft('5 mm diamond tie holes',[
            [(-22,a,b) for a,b in diamond],[(22,a,b) for a,b in diamond]]))
    return o

def material(name,rgb):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    node=m.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*rgb,1);node.inputs['Roughness'].default_value=.38
    return m

def engrave_back(body):
    """Deboss the attribution in the exposed upper-right rear shoulder."""
    curve=bpy.data.curves.new('Attribution cutter','FONT')
    curve.body='christopherbrown.io'
    # Convert the system font to mesh; no font file is embedded or distributed.
    font_path=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    assert font_path.exists(), 'Install Arial Bold or set font_path to its local TTF'
    font=bpy.data.fonts.load(str(font_path));curve.font=font
    curve.size=5;curve.extrude=.5;curve.resolution_u=10;curve.fill_mode='BOTH'
    cutter=bpy.data.objects.new('Recessed christopherbrown.io',curve)
    bpy.context.collection.objects.link(cutter);active(cutter)
    bpy.ops.object.convert(target='MESH')
    cutter=bpy.context.object
    coords=[v.co.copy() for v in cutter.data.vertices]
    low=Vector(tuple(min(p[i] for p in coords) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in coords) for i in range(3)))
    factor=47.5/(high.x-low.x)
    center=(low+high)/2
    for v in cutter.data.vertices:
        v.co.x=(v.co.x-center.x)*factor+47
        v.co.y=(v.co.y-center.y)*factor+23
        v.co.z=3.4+(v.co.z-low.z)/(high.z-low.z)*.8
    bm=bmesh.new();bm.from_mesh(cutter.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(cutter.data);bm.free()
    cutter.data.update();bpy.context.view_layer.update()
    cutter_stats=stats(cutter)
    assert cutter_stats['nonmanifold_edges']==0, cutter_stats
    # Public footprint permits an independent clearance and tool-width check.
    cutter.data.calc_loop_triangles()
    top=[[[*cutter.data.vertices[i].co] for i in t.vertices]
         for t in cutter.data.loop_triangles
         if all(abs(cutter.data.vertices[i].co.z-4.2)<1e-5 for i in t.vertices)]
    (OUT/'engraving_measurements.json').write_text(json.dumps({
        'text':'christopherbrown.io',
        'font':'Arial Bold; converted to mesh, font not distributed',
        'width_mm':47.5,'height_mm':(high.y-low.y)*factor,
        'center_xy_mm':[47,23],'back_surface_z_mm':4,
        'floor_z_mm':3.4,'depth_mm':.6,
        'remaining_thickness_above_front_inlays_mm':2.4,
        'cutter_mesh':cutter_stats,
        'top_triangles_mm':top,
    },indent=2)+'\n')
    boolean(body,cutter)
    unused=bpy.data.curves.get('Attribution cutter')
    if unused is not None and unused.users==0:bpy.data.curves.remove(unused)
    if font.users==0:bpy.data.fonts.remove(font)

def stl(path,objects):
    ts=[]
    for o in objects:
        o.data.calc_loop_triangles()
        ts.extend([[o.matrix_world@o.data.vertices[i].co for i in t.vertices] for t in o.data.loop_triangles])
    with open(path,'wb') as f:
        f.write(b'Roanoke Star A1 | mm | face down'.ljust(80,b' '));f.write(struct.pack('<I',len(ts)))
        for a,b,c in ts:
            norm=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*norm,*a,*b,*c,0))

def stats(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    d={'dimensions_mm':list(o.dimensions),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
       'boundary_edges':sum(e.is_boundary for e in bm.edges),'volume_mm3':bm.calc_volume(signed=True),
       'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'scale':list(o.scale)}
    bm.free();return d

def look(o,target):
    direction=(Vector(target)-o.location).normalized()
    right=direction.cross(Vector((0,1,0))).normalized();up=right.cross(direction)
    o.rotation_euler=Matrix((right,up,-direction)).transposed().to_euler()

def render_view(name,loc,target=(0,0,10),scale=236):
    cam=bpy.context.scene.camera;cam.location=loc;cam.data.ortho_scale=scale;look(cam,target)
    bpy.context.scene.render.filepath=str(OUT/'previews'/name)
    bpy.ops.render.render(write_still=True)

def main():
    for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC'
    scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
    dark=material('01 | Navy PLA | integral body',(.018,.028,.05))
    white=material('02 | White PLA | tubes and backing bands',(.93,.94,.92))
    body=extrude('RoanokeStar_Body','outline',0,4)
    boolean(body,socket(),'UNION')
    engrave_back(body)
    # Save the exact outer solid before partitioning it by filament. This avoids
    # unnecessary coincident-interface triangulation in the geometry reference.
    # This unpartitioned STL loses the contrasting tube pattern in one color.
    stl(OUT/'roanoke_star_A1_geometry_reference.stl',[body])
    boolean(body,extrude('Matching fused white inlay cavities','white_material',0,1.0))
    lights=extrude('RoanokeStar_Tube_Sections','white_material',0,1.0)
    # Boolean operations can leave an empty material slot at index zero.
    # Explicitly reset the slots so every face uses its intended filament color.
    for obj, mat in [(body, dark), (lights, white)]:
        obj.data.materials.clear();obj.data.materials.append(mat)
        for poly in obj.data.polygons:poly.material_index=0
    body['assembly_required']=False;body['printer']='Bambu Lab A1 + AMS lite'
    body['print_orientation']='Front face on bed, Z >= 0; integral roofed socket'
    body['accuracy']='Outline and tube schedule are photo-based approximations; not a surveyed replica'
    for obj in [body,lights]:
        obj['license']='CC BY-NC-SA 4.0'
        obj['license_url']='https://creativecommons.org/licenses/by-nc-sa/4.0/'
        obj['creator']='christopherrbrown3 | christopherbrown.io'
    body['rear_attribution']='christopherbrown.io | recessed 0.6 mm'
    lights['construction']='Actual separate material volumes fused in the same print; no loose inserts or post-print assembly'
    lights['tube_width_mm']=1.8;lights['inlay_depth_mm']=1.0
    lights['backing_bands']=3;lights['tube_dark_outline_mm']=.6
    for o in [body,lights]:
        active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.update()
    (OUT/'blender_validation.json').write_text(json.dumps({o.name:stats(o) for o in [body,lights]},indent=2)+'\n')
    stl(OUT/'body_material.stl',[body]);stl(OUT/'white_tube_material.stl',[lights])
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.4,.44,.52,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    scene.view_settings.view_transform='AgX'
    bpy.ops.object.camera_add(location=(0,0,-440));cam=bpy.context.object;cam.name='Preview_Camera'
    cam.data.type='ORTHO';cam.data.clip_end=2000;scene.camera=cam
    for name,loc,power,size in [('Key',(-150,200,-260),2300000,230),('Fill',(180,30,-170),1200000,180),('Rear',(-100,130,240),2000000,180)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
        o.data.energy=power;o.data.shape='DISK';o.data.size=size;look(o,(0,0,10))
    for obj in scene.objects:
        if obj.type in ['CAMERA','LIGHT']:obj.hide_set(True)
    for name,file in [('A1_BUILD_SOURCE.py','scripts/build_a1_print_in_place_blender.py'),
                      ('A1_PROFILE_REPORT.json','print_in_place/profile_measurements.json')]:
        if name in bpy.data.texts:bpy.data.texts.remove(bpy.data.texts[name])
        t=bpy.data.texts.new(name);t.write((ROOT/file).read_text())
    active(body)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'roanoke_star_A1.blend'))
    (OUT/'BUILD_COMPLETE.txt').write_text('A1 single-print model built through Blender GUI. Validation pending.\n')

try:main()
except Exception:
    (OUT/'BUILD_ERROR.txt').write_text(traceback.format_exc());raise
