"""Build the separate diffuser revision using the live Blender MCP."""
import bpy
import bmesh
from mathutils import Vector

HERE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/diffused'
SOURCE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/two_dot'
SCENE_NAME = 'Roanoke Star | diffused two-dot face'
NAMES = {'body': 'Diffused | black shell', 'white': 'Diffused | white bands and two-layer windows',
         'lid': 'Diffused | marked two-dot back', 'sample_black': 'Diffuser test | black frame',
         'sample_white': 'Diffuser test | two-layer white windows'}
K = {}


def active(obj):
    for other in bpy.context.view_layer.objects:
        other.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def load(path, name, collection):
    bpy.ops.wm.stl_import(filepath=path, global_scale=1., use_scene_unit=False)
    obj = bpy.context.object
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def construction(key, name, collection):
    return load(HERE+'/construction/'+key+'.stl', name, collection)


def boolean(obj, cutter, operation):
    active(obj)
    modifier = obj.modifiers.new(operation+' '+cutter.name, 'BOOLEAN')
    assert 'MANIFOLD' in [item.identifier for item in modifier.bl_rna.properties['solver'].enum_items]
    modifier.operation = operation
    modifier.solver = 'MANIFOLD'
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def duplicate(obj, collection):
    copy = obj.copy()
    copy.data = obj.data.copy()
    collection.objects.link(copy)
    return copy


def material(name, rgba):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = next(n for n in result.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = .48
    result.diffuse_color = rgba
    return result


def color(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0


def export(obj, key):
    active(obj)
    bpy.ops.wm.stl_export(filepath=HERE+'/'+key+'.stl', export_selected_objects=True,
                          global_scale=1., use_scene_unit=False, apply_modifiers=True)


def setup():
    assert bpy.data.scenes.get(SCENE_NAME) is None, 'The diffuser revision already exists.'
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    scene['diffuser_thickness_mm'] = .4
    scene['diffuser_printed_layers'] = 2
    scene['layer_height_mm'] = .2
    scene['physical_light_transmission_tested'] = False
    scene['selected_connector'] = 'tested two-dot'
    K['scene'] = scene
    for key, name in [('body_col', 'DIFFUSED | full topper'), ('sample_col', 'DIFFUSED | print sample')]:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
        K[key] = collection
    K['black_mat'] = material('Diffused | black PLA A2', (.008, .009, .011, 1))
    K['white_mat'] = material('Diffused | white PLA A1', (.92, .94, .92, 1))


def restore():
    K.update(scene=bpy.data.scenes.get(SCENE_NAME),
             body_col=bpy.data.collections.get('DIFFUSED | full topper'),
             sample_col=bpy.data.collections.get('DIFFUSED | print sample'),
             black_mat=bpy.data.materials.get('Diffused | black PLA A2'),
             white_mat=bpy.data.materials.get('Diffused | white PLA A1'))
    for key, name in NAMES.items():
        K[key] = bpy.data.objects.get(name)
    assert K['scene'] is not None
    bpy.context.window.scene = K['scene']


def build():
    collection = K['body_col']
    body = load(SOURCE+'/body_navy.stl', NAMES['body'], collection)
    white = construction('white_skin_and_bands', NAMES['white'], collection)
    boolean(white, construction('white_upper_bands', 'Upper white bands', collection), 'UNION')
    lid = load(SOURCE+'/snap_back.stl', NAMES['lid'], collection)
    for obj, mat in [(body, K['black_mat']), (white, K['white_mat']), (lid, K['white_mat'])]:
        color(obj, mat)
    white['diffuser_thickness_mm'] = .4
    white['thin_window_count'] = 130
    lid['builder_mark_text'] = 'christopherbrown.io'
    lid['builder_mark_width_mm'] = 72.
    lid['builder_mark_depth_mm'] = 1.
    lid['selected_sample_physically_tested'] = True
    K.update(body=body, white=white, lid=lid)
    export(body, 'body_black')
    export(white, 'body_white_diffused')
    sample_col = K['sample_col']
    black_sample = duplicate(body, sample_col)
    black_sample.name = NAMES['sample_black']
    boolean(black_sample, construction('sample_crop', 'Black sample crop', sample_col), 'INTERSECT')
    boolean(black_sample, construction('sample_handling_border', 'Handling border', sample_col), 'UNION')
    white_sample = duplicate(white, sample_col)
    white_sample.name = NAMES['sample_white']
    boolean(white_sample, construction('sample_crop', 'White sample crop', sample_col), 'INTERSECT')
    export(black_sample, 'test_black')
    export(white_sample, 'test_white')
    black_sample.location.y = 145.
    white_sample.location.y = 145.
    K.update(sample_black=black_sample, sample_white=white_sample)
    print('Built full diffused front and a full-scale sample with a 2 mm handling border.')


def finish():
    active(K['white'])
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                region = area.spaces.active.region_3d
                region.view_location = Vector((0, 0, 26))
                region.view_distance = 340
                region.view_rotation = (Vector((0, 0, 26))-Vector((220, -160, -330))).to_track_quat('-Z', 'Y')
                region.view_perspective = 'ORTHO'
                area.spaces.active.shading.color_type = 'MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/diffused_topper.blend')
    print('Saved the separate diffused topper and test sample.')


def import_canonical():
    for key, meshkey, material_key, collection_key in [
        ('body', 'body_black', 'black_mat', 'body_col'),
        ('white', 'body_white_diffused', 'white_mat', 'body_col'),
        ('sample_black', 'test_black', 'black_mat', 'sample_col'),
        ('sample_white', 'test_white', 'white_mat', 'sample_col')]:
        old = K[key]
        props = {prop: old[prop] for prop in old.keys()}
        location = old.location.copy()
        bpy.data.objects.remove(old, do_unlink=True)
        obj = load(HERE+'/'+meshkey+'.stl', NAMES[key], K[collection_key])
        obj.location = location
        color(obj, K[material_key])
        for prop, value in props.items():
            obj[prop] = value
        K[key] = obj
    finish()
