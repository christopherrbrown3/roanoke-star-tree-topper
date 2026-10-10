"""Build the experiment in live Blender through MCP, preserving existing scenes."""
import bpy
import bmesh
from mathutils import Vector, Matrix

HERE='/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism'
C={'radial_fit_gap_mm':.3,'retention_engagement_mm':.45}
K={}

def restore():
    K.update(scene=bpy.data.scenes.get('Roanoke Star | snap-back experiment'),
      body_col=bpy.data.collections.get('PRINT 1 | face-down body'),
      lid_col=bpy.data.collections.get('PRINT 2 | detachable white back'),
      coupon_col=bpy.data.collections.get('PRINT TEST | connector sample'),
      studio=bpy.data.collections.get('SNAP STUDIO | not printed'),
      body=bpy.data.objects.get('Snap body | navy shell'),
      white=bpy.data.objects.get('Snap body | original white face bands'),
      lid=bpy.data.objects.get('Snap back | six planar spring clips'),
      coupon_body=bpy.data.objects.get('Sample | catch wall'),
      coupon_lid=bpy.data.objects.get('Sample | spring back'),
      dark_mat=bpy.data.materials.get('Filament 1 | navy structural shell'),
      white_mat=bpy.data.materials.get('Filament 2 | white face bands and interior reflector'),
      camera=bpy.data.objects.get('Snap preview camera'))

def active(obj):
    for o in bpy.context.view_layer.objects: o.select_set(False)
    obj.hide_set(False); obj.select_set(True)
    bpy.context.view_layer.objects.active=obj

def enum(owner,prop,value):
    valid=[i.identifier for i in owner.bl_rna.properties[prop].enum_items]
    assert value in valid,(prop,value,valid)
    if prop=='operation': owner.operation=value
    elif prop=='solver': owner.solver=value
    elif prop=='system': owner.system=value
    elif prop=='type': owner.type=value
    elif prop=='shape': owner.shape=value
    elif prop=='file_format': owner.file_format=value
    elif prop=='color_type': owner.color_type=value
    else: raise ValueError(prop)

def load_mesh(key,name,col):
    bpy.ops.wm.stl_import(filepath=HERE+'/construction/'+key+'.stl',global_scale=1.,use_scene_unit=False)
    o=bpy.context.object; o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    return o

def boolean(o,cutter,op='DIFFERENCE'):
    active(o); mod=o.modifiers.new(op+' '+cutter.name,'BOOLEAN')
    enum(mod,'operation',op); enum(mod,'solver','MANIFOLD'); mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

def color(obj,mat):
    obj.data.materials.clear(); obj.data.materials.append(mat)
    for p in obj.data.polygons: p.material_index=0

def export(key,objects):
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.wm.stl_export(filepath=HERE+'/'+key+'.stl',export_selected_objects=True,
      global_scale=1.,use_scene_unit=False,apply_modifiers=True,evaluation_mode='DAG_EVAL_VIEWPORT')

def setup():
    assert bpy.data.scenes.get('Roanoke Star | snap-back experiment') is None, 'Use a Blender file without a previous snap-back scene when rebuilding.'
    scene=bpy.data.scenes.new('Roanoke Star | snap-back experiment')
    bpy.context.window.scene=scene
    for key,name in [('body_col','PRINT 1 | face-down body'),('lid_col','PRINT 2 | detachable white back'),
                     ('coupon_col','PRINT TEST | connector sample'),('studio','SNAP STUDIO | not printed')]:
        c=bpy.data.collections.new(name); scene.collection.children.link(c); K[key]=c
    K['scene']=scene
    K['dark_mat']=bpy.data.materials.get('Filament 1 | navy structural shell')
    K['white_mat']=bpy.data.materials.get('Filament 2 | white face bands and interior reflector')
    assert K['dark_mat'] and K['white_mat']
    enum(scene.unit_settings,'system','METRIC'); scene.unit_settings.scale_length=.001
    scene['design']='Experimental two-piece face-down prism with six in-plane spring clips'
    scene['physical_snap_fit_tested']=False; scene['thermal_tested']=False
    scene['original_face_preserved']=True; scene['bottom_opening_width_mm']=100.
    print('Separate snap-back scene created.')

def build_body():
    c=K['body_col']; body=load_mesh('body_blank','Snap body | navy shell',c)
    for key in ['open_cavity','tube_holes','bottom_mouth','catch_windows']:
        boolean(body,load_mesh(key,key,c))
    white=load_mesh('white_face','Snap body | original white face bands',c)
    cutter=white.copy(); cutter.data=white.data.copy(); c.objects.link(cutter)
    boolean(body,cutter)
    color(body,K['dark_mat']); color(white,K['white_mat'])
    body['rear_open']=True; body['catch_windows']=6
    K.update(body=body,white=white)
    export('body_navy',[body]); export('body_white_face',[white])
    print('Face-down front shell built with original face and open rear.')

def build_back():
    c=K['lid_col']; lid=load_mesh('lid_blank','Snap back | six planar spring clips',c)
    boolean(lid,load_mesh('locating_rim','Locating rim',c),'UNION')
    for i in range(6): boolean(lid,load_mesh('hook_'+str(i+1),'Clip '+str(i+1),c),'UNION')
    color(lid,K['white_mat']); K['lid']=lid
    lid['radial_fit_gap_mm']=C['radial_fit_gap_mm']; lid['retention_engagement_mm']=C['retention_engagement_mm']
    lid['clip_beams_print_in_XY_plane']=True; lid['physical_fit_tested']=False
    export('snap_back',[lid])
    c=K['coupon_col']; base=load_mesh('coupon_floor','Sample | catch wall',c)
    boolean(base,load_mesh('coupon_wall','Sample wall',c),'UNION')
    boolean(base,load_mesh('coupon_window','Sample window',c))
    cap=load_mesh('coupon_lid','Sample | spring back',c)
    boolean(cap,load_mesh('coupon_rim','Sample locating rim',c),'UNION')
    boolean(cap,load_mesh('coupon_hook','Sample snap',c),'UNION')
    color(base,K['dark_mat']); color(cap,K['white_mat'])
    K.update(coupon_body=base,coupon_lid=cap)
    export('coupon_catch',[base]); export('coupon_back',[cap])
    c.hide_render=True; c.hide_viewport=True
    print('Snap back and small connector sample built.')

def look(o,target):
    d=(Vector(target)-o.location).normalized()
    right=d.cross(Vector((0,1,0))).normalized(); up=right.cross(d)
    o.rotation_euler=Matrix((right,up,-d)).transposed().to_euler()

def finish():
    s=K['scene']; c=K['studio']
    try: s.render.engine='CYCLES'
    except TypeError as exc: raise RuntimeError('Cycles unavailable') from exc
    s.cycles.samples=24; s.cycles.use_denoising=True
    s.render.resolution_x=1200; s.render.resolution_y=1200; s.render.resolution_percentage=100
    enum(s.render.image_settings,'file_format','PNG')
    world=bpy.data.worlds.new('Snap studio world'); s.world=world; world.use_nodes=True
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs[0].default_value=(.16,.19,.24,1); bg.inputs[1].default_value=.5
    camera_data=bpy.data.cameras.new('Snap preview camera'); enum(camera_data,'type','ORTHO')
    camera_data.ortho_scale=270; camera_data.clip_end=3000
    camera=bpy.data.objects.new('Snap preview camera',camera_data); c.objects.link(camera)
    camera.location=(260,-160,-360); look(camera,(0,0,26)); s.camera=camera; K['camera']=camera
    for name,loc,power,size in [('Key',(-150,220,-260),2200000,240),
                               ('Fill',(180,-40,-170),1400000,170),
                               ('Rim',(-100,120,240),2300000,180)]:
        d=bpy.data.lights.new('Snap studio '+name,type='AREA'); enum(d,'shape','DISK')
        d.energy=power; d.size=size
        o=bpy.data.objects.new(d.name,d); c.objects.link(o); o.location=loc; look(o,(0,0,26))
    c.hide_viewport=True
    active(K['body'])
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                r=area.spaces.active.region_3d; r.view_distance=435
                r.view_location=Vector((0,0,26)); r.view_rotation=camera.rotation_euler.to_quaternion()
                valid=[i.identifier for i in r.bl_rna.properties['view_perspective'].enum_items]
                if 'ORTHO' in valid: r.view_perspective='ORTHO'
                enum(area.spaces.active.shading,'color_type','MATERIAL')
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/snap_back_prism.blend')
    print('Separate editable snap-back experiment saved.')

def render_view(name,loc,target=(0,0,26),scale=270,explode=0):
    K['lid'].location.z=explode
    cam=K['camera']; cam.location=loc; cam.data.ortho_scale=scale; look(cam,target)
    K['scene'].render.filepath=HERE+'/previews/'+name
    bpy.ops.render.render(write_still=True)
    K['lid'].location.z=0
    print('Rendered '+name)

def import_canonical():
    for key,name,col,mat in [('body_navy','Snap body | navy shell',K['body_col'],K['dark_mat']),
       ('body_white_face','Snap body | original white face bands',K['body_col'],K['white_mat']),
       ('snap_back','Snap back | six planar spring clips',K['lid_col'],K['white_mat']),
       ('coupon_catch','Sample | catch wall',K['coupon_col'],K['dark_mat']),
       ('coupon_back','Sample | spring back',K['coupon_col'],K['white_mat'])]:
        old=bpy.data.objects.get(name)
        properties={k:old[k] for k in old.keys()}
        bpy.data.objects.remove(old,do_unlink=True)
        bpy.ops.wm.stl_import(filepath=HERE+'/'+key+'.stl',global_scale=1.,use_scene_unit=False)
        o=bpy.context.object; o.name=name
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o); color(o,mat)
        for k,v in properties.items(): o[k]=v
    restore()
    K['coupon_col'].hide_viewport=True
    active(K['body'])
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/snap_back_prism.blend')
