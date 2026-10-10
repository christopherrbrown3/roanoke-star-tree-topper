"""Execute through Blender MCP. All output stays in this variant directory.

Load this module, then call setup(), build_shell(), partition_colors(), and
finish(). The separate steps keep live Blender operations inspectable.
"""
import bpy
import bmesh
import json
import math
from mathutils import Vector, Matrix

# The caller supplies these from parameters.json when sending this source to
# execute_blender_code. No Python file access or external module loading is
# needed in the live MCP safe-mode runtime.
HERE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/pentagrammic_prism'
C = {'depth_mm': 60.0, 'front_thickness_mm': 4.0, 'side_wall_mm': 1.2,
     'rear_thickness_mm': 1.6, 'front_white_depth_mm': 1.0,
     'interior_white_depth_mm': .8, 'bottom_opening_width_mm': 100.0,
     'opening_shape': '100 mm wide V-shaped lower mouth; not a circular bore'}
K = {}

def restore():
    K.update(scene=bpy.data.scenes.get('Roanoke Star | hollow pentagrammic prism'),
             geometry=bpy.data.collections.get('PRINT | one fused object, two filaments'),
             references=bpy.data.collections.get('REFERENCE | original tube and outline profiles'),
             studio=bpy.data.collections.get('STUDIO | cameras and lights, not printed'),
             demo=bpy.data.collections.get('ILLUMINATION DEMO | illustrative bulbs, not printed'),
             body=bpy.data.objects.get('Prism | dark shell'),
             bands=bpy.data.objects.get('Prism | white original backing bands'),
             reflector=bpy.data.objects.get('Prism | white interior reflector'),
             fused=bpy.data.objects.get('REFERENCE | complete single-piece exterior'),
             dark=bpy.data.materials.get('Filament 1 | navy structural shell'),
             white=bpy.data.materials.get('Filament 2 | white face bands and interior reflector'),
             camera=bpy.data.objects.get('Prism preview camera'))

def enum_set(owner, prop, choice):
    values = [item.identifier for item in owner.bl_rna.properties[prop].enum_items]
    assert choice in values, (prop, choice, values)
    # Safe mode requires literal property access rather than dynamic setattr.
    if prop == 'operation':
        owner.operation = choice
    elif prop == 'solver':
        owner.solver = choice
    elif prop == 'system':
        owner.system = choice
    elif prop == 'length_unit':
        owner.length_unit = choice
    elif prop == 'file_format':
        owner.file_format = choice
    elif prop == 'type':
        owner.type = choice
    elif prop == 'shape':
        owner.shape = choice
    elif prop == 'color_type':
        owner.color_type = choice
    else:
        raise ValueError(prop)

def active(obj):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def mesh_obj(name, vertices, faces, collection=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    (collection or K['geometry']).objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    return obj

def extrude(name, key, z0, z1, collection=None):
    bpy.ops.wm.stl_import(filepath=HERE+'/construction/'+key+'.stl',
                          global_scale=1.0, use_scene_unit=False)
    obj = bpy.context.object
    obj.name = name
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    (collection or K['geometry']).objects.link(obj)
    return obj

def boolean(obj, cutter, operation='DIFFERENCE'):
    active(obj)
    mod = obj.modifiers.new(operation + ' | ' + cutter.name, 'BOOLEAN')
    enum_set(mod, 'operation', operation)
    enum_set(mod, 'solver', 'MANIFOLD')
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def material(name, color, roughness=.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    node = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    # Socket indices obtained from the connected add-on's node schema.
    node.inputs[0].default_value = (*color, 1)
    node.inputs[2].default_value = roughness
    return m

def look(obj, target):
    direction = (Vector(target)-obj.location).normalized()
    right = direction.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(direction)
    obj.rotation_euler = Matrix((right, up, -direction)).transposed().to_euler()

def export_stl(path, objects):
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                          global_scale=1.0, use_scene_unit=False,
                          apply_modifiers=True, evaluation_mode='DAG_EVAL_VIEWPORT')

def setup():
    assert HERE.endswith('/pentagrammic_prism')
    scene = bpy.data.scenes.get('Roanoke Star | hollow pentagrammic prism') or bpy.data.scenes.new('Roanoke Star | hollow pentagrammic prism')
    bpy.context.window.scene = scene
    geometry = bpy.data.collections.get('PRINT | one fused object, two filaments') or bpy.data.collections.new('PRINT | one fused object, two filaments')
    references = bpy.data.collections.get('REFERENCE | original tube and outline profiles') or bpy.data.collections.new('REFERENCE | original tube and outline profiles')
    studio = bpy.data.collections.get('STUDIO | cameras and lights, not printed') or bpy.data.collections.new('STUDIO | cameras and lights, not printed')
    demo = bpy.data.collections.get('ILLUMINATION DEMO | illustrative bulbs, not printed') or bpy.data.collections.new('ILLUMINATION DEMO | illustrative bulbs, not printed')
    for col in [geometry, references, studio, demo]:
        if col.name not in scene.collection.children:
            scene.collection.children.link(col)
    assert len(geometry.objects) == 0, 'Use a fresh Blender file when rebuilding this variant.'
    references.hide_render = True
    demo.hide_render = True
    enum_set(scene.unit_settings, 'system', 'METRIC')
    scene.unit_settings.scale_length = .001
    dark = material('Filament 1 | navy structural shell', (.018, .035, .065))
    white = material('Filament 2 | white face bands and interior reflector', (.92, .94, .92))
    K.update(scene=scene, geometry=geometry, references=references, studio=studio,
             demo=demo, dark=dark, white=white)
    scene['design'] = 'Hollow extrusion of the original five-point outline; not a tapered pyramid'
    scene['opening_width_mm'] = C['bottom_opening_width_mm']
    scene['depth_mm'] = C['depth_mm']
    scene['original_release_modified'] = False
    scene['thermal_validation'] = 'Not performed. Incandescent compatibility is unverified.'
    print('New variant scene created; existing scenes and release files preserved.')

def build_shell():
    references, dark = K['references'], K['dark']
    body = extrude('Prism | dark shell', 'outline', 0, C['depth_mm'])
    boolean(body, extrude('Hollow interior', 'inner_cavity', C['front_thickness_mm'],
                          C['depth_mm']-C['rear_thickness_mm']))
    boolean(body, extrude('130 original tube apertures', 'white_tube_sections', -.2,
                          C['front_thickness_mm']+.2))
    boolean(body, extrude('100 mm lower V mouth', 'bottom_mouth', C['front_thickness_mm'],
                          C['depth_mm']-C['rear_thickness_mm']))
    boolean(body, extrude('Eight rear ventilation openings', 'rear_vents',
                          C['depth_mm']-C['rear_thickness_mm']-.2, C['depth_mm']+.2))
    body.data.materials.clear()
    body.data.materials.append(dark)
    for poly in body.data.polygons:
        poly.material_index = 0
    body['minimum_side_wall_mm'] = C['side_wall_mm']
    body['front_wall_mm'] = C['front_thickness_mm']
    body['tube_apertures'] = 130
    body['opening_shape'] = C['opening_shape']
    fused = body.copy()
    fused.data = body.data.copy()
    fused.name = 'REFERENCE | complete single-piece exterior'
    references.objects.link(fused)
    fused.hide_set(True)
    fused.hide_render = True
    export_stl(HERE+'/roanoke_star_prism.stl', [fused])
    fused.hide_set(True)
    active(body)
    K.update(body=body, fused=fused)
    print('Hollow 60 mm prism, 130 through-holes, lower mouth and rear vents built.')

def partition_colors():
    body, geometry, white = K['body'], K['geometry'], K['white']
    bands = extrude('Prism | white original backing bands', 'white_backing_bands',
                    0, C['front_white_depth_mm'])
    bands.data.materials.append(white)
    band_cutter = bands.copy()
    band_cutter.data = bands.data.copy()
    band_cutter.name = 'White face volume partition'
    geometry.objects.link(band_cutter)
    boolean(body, band_cutter)
    z0 = C['depth_mm']-C['rear_thickness_mm']
    reflector = extrude('Prism | white interior reflector', 'inner_reflector',
                        z0, z0+C['interior_white_depth_mm'])
    reflector.data.materials.append(white)
    rc = reflector.copy()
    rc.data = reflector.data.copy()
    rc.name = 'White reflector volume partition'
    geometry.objects.link(rc)
    boolean(body, rc)
    body.data.materials.clear()
    body.data.materials.append(K['dark'])
    for poly in body.data.polygons:
        poly.material_index = 0
    for o in [body, bands, reflector]:
        o['manufacturing_units'] = 'millimeters'
        o['assembly_required'] = False
    export_stl(HERE+'/dark_shell.stl', [body])
    export_stl(HERE+'/white_details.stl', [bands, reflector])
    K.update(bands=bands, reflector=reflector)
    print('Original white bands retained; only the tube volumes are open. Two filament regions exported.')

def finish():
    scene, studio, body = K['scene'], K['studio'], K['body']
    try:
        scene.render.engine = 'CYCLES'
    except TypeError as exc:
        raise RuntimeError('Cycles render engine is unavailable') from exc
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 8
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    enum_set(scene.render.image_settings, 'file_format', 'PNG')
    scene.render.film_transparent = False
    world = bpy.data.worlds.new('Prism studio world')
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (.16, .19, .24, 1)
    bg.inputs[1].default_value = .5
    available = [i.identifier for i in scene.view_settings.bl_rna.properties['view_transform'].enum_items]
    if 'AgX' in available:
        scene.view_settings.view_transform = 'AgX'
    data = bpy.data.cameras.new('Prism preview camera')
    enum_set(data, 'type', 'ORTHO')
    data.ortho_scale = 254
    data.clip_end = 3000
    camera = bpy.data.objects.new('Prism preview camera', data)
    studio.objects.link(camera)
    camera.location = (260, -160, -360)
    look(camera, (0, 0, 26))
    scene.camera = camera
    K['camera'] = camera
    lights = []
    for name, loc, power, size in [
        ('Key', (-150, 220, -260), 2200000, 240),
        ('Fill', (180, -40, -170), 1400000, 170),
        ('Rim', (-100, 120, 240), 2300000, 180),
    ]:
        d = bpy.data.lights.new('Studio '+name, type='AREA')
        enum_set(d, 'shape', 'DISK')
        d.energy, d.size = power, size
        o = bpy.data.objects.new('Studio '+name, d)
        studio.objects.link(o)
        o.location = loc
        look(o, (0, 0, 24))
        lights.append(o)
    K['lights'] = lights
    studio.hide_viewport = True
    scene['parameters_json'] = json.dumps(C, indent=2)
    active(body)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_distance = 435
                area.spaces.active.region_3d.view_location = Vector((0, 0, 26))
                area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
                enum_set(area.spaces.active.shading, 'color_type', 'MATERIAL')
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/roanoke_star_prism.blend')
    print('Editable Blender variant saved separately.')

def render_view(name, location, target=(0, 0, 26), scale=254):
    scene, camera = K['scene'], K['camera']
    camera.location = location
    camera.data.ortho_scale = scale
    look(camera, target)
    scene.render.filepath = HERE+'/previews/'+name
    bpy.ops.render.render(write_still=True)
    print('Rendered '+name)

def add_demo_lights():
    demo = K['demo']
    bulb_positions = [(0, -27), (-25, -35), (25, -35), (-42, -65), (42, -65),
                      (-55, 17), (55, 17), (-25, 12), (25, 12), (0, 25), (0, 56)]
    for i, (x, y) in enumerate(bulb_positions):
        d = bpy.data.lights.new('Illustrative warm LED '+str(i+1), type='POINT')
        d.energy = 18000
        d.color = (1.0, .66, .32)
        d.shadow_soft_size = 3
        o = bpy.data.objects.new(d.name, d)
        demo.objects.link(o)
        o.location = (x, y, 33)
    demo['notice'] = 'Illustrative illumination, not a prediction of a specific light string or a heat test.'
    demo.hide_viewport = True
    print('Optional illumination demonstration lights created; excluded from print exports.')
