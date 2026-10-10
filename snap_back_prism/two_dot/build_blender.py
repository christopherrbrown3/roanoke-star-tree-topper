"""Build the full two-dot revision through live Blender MCP in a new scene."""
import bpy
import bmesh
from mathutils import Vector, Matrix

HERE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/two_dot'
SCENE_NAME = 'Roanoke Star | preferred two-dot back'
BUILDER_MARK = {'text': 'christopherbrown.io', 'width_mm': 72., 'depth_mm': 1.,
                'center_xy_mm': [0., 5.5], 'surface_z_mm': 60.,
                'font_path': '/System/Library/Fonts/Supplemental/Arial Bold.ttf'}
K = {}


def restore():
    K.update(scene=bpy.data.scenes.get(SCENE_NAME),
        body_col=bpy.data.collections.get('TWO DOT | front shell'),
        lid_col=bpy.data.collections.get('TWO DOT | detachable back'),
        body=bpy.data.objects.get('Two-dot | navy shell'),
        white=bpy.data.objects.get('Two-dot | original white bands'),
        lid=bpy.data.objects.get('Two-dot | six tested latches'),
        dark_mat=bpy.data.materials.get('Two-dot | navy PLA'),
        white_mat=bpy.data.materials.get('Two-dot | white PLA'))
    assert K['scene'] is not None
    bpy.context.window.scene = K['scene']


def active(obj):
    for other in bpy.context.view_layer.objects:
        other.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def load(key, name, collection, canonical=False):
    folder = '/' if canonical else '/construction/'
    bpy.ops.wm.stl_import(filepath=HERE+folder+key+'.stl', global_scale=1., use_scene_unit=False)
    obj = bpy.context.object
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def boolean(obj, cutter, operation='DIFFERENCE'):
    active(obj)
    modifier = obj.modifiers.new(operation+' '+cutter.name, 'BOOLEAN')
    assert operation in [item.identifier for item in modifier.bl_rna.properties['operation'].enum_items]
    assert 'MANIFOLD' in [item.identifier for item in modifier.bl_rna.properties['solver'].enum_items]
    modifier.operation = operation
    modifier.solver = 'MANIFOLD'
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def color(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0


def material(name, rgba):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = next(node for node in result.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = .48
    result.diffuse_color = rgba
    return result


def export(obj, key):
    active(obj)
    bpy.ops.wm.stl_export(filepath=HERE+'/'+key+'.stl', export_selected_objects=True,
                          global_scale=1., use_scene_unit=False, apply_modifiers=True)


def setup():
    assert bpy.data.scenes.get(SCENE_NAME) is None, 'The two-dot revision already exists.'
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    assert 'METRIC' in [item.identifier for item in scene.unit_settings.bl_rna.properties['system'].enum_items]
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    scene['selected_connector'] = 'two_dot, 0.50 mm engagement'
    scene['user_feedback'] = 'They both work. Slight edge to two dots though.'
    scene['selected_sample_physically_tested'] = True
    scene['full_topper_physically_tested'] = False
    scene['original_face_preserved'] = True
    scene['bottom_opening_width_mm'] = 100.
    K['scene'] = scene
    for key, name in [('body_col', 'TWO DOT | front shell'), ('lid_col', 'TWO DOT | detachable back')]:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
        K[key] = collection
    K['dark_mat'] = material('Two-dot | navy PLA', (.012, .025, .051, 1))
    K['white_mat'] = material('Two-dot | white PLA', (.88, .90, .86, 1))


def build_body():
    collection = K['body_col']
    body = load('body_blank', 'Two-dot | navy shell', collection)
    for key in ['open_cavity', 'tube_holes', 'bottom_mouth', 'catch_windows']:
        boolean(body, load(key, key, collection))
    white = load('white_face', 'Two-dot | original white bands', collection)
    cutter = white.copy()
    cutter.data = white.data.copy()
    collection.objects.link(cutter)
    boolean(body, cutter)
    color(body, K['dark_mat'])
    color(white, K['white_mat'])
    body['catch_windows'] = 6
    K.update(body=body, white=white)
    export(body, 'body_navy')
    export(white, 'body_white_face')
    print('Full two-dot shell built and exported.')


def build_back():
    collection = K['lid_col']
    lid = load('lid_blank', 'Two-dot | six tested latches', collection)
    boolean(lid, load('locating_rim', 'Locating rim', collection), 'UNION')
    for i in range(1, 7):
        boolean(lid, load('hook_'+str(i), 'Tested hook '+str(i), collection), 'UNION')
    color(lid, K['white_mat'])
    lid['radial_fit_gap_mm'] = .55
    lid['retention_engagement_mm'] = .5
    lid['clip_beam_length_mm'] = 30.
    lid['selected_sample_physically_tested'] = True
    lid['full_topper_physically_tested'] = False
    K['lid'] = lid
    export(lid, 'construction/back_unmarked_reference')
    engrave_back(lid)
    export(lid, 'snap_back')
    print('Full two-dot back built with six copies of the tested hook.')


def engrave_back(lid):
    """Deboss a larger builder mark into the outside of the rear cover."""
    assert 'builder_mark_text' not in lid, 'Rebuild from the unmarked back before engraving again.'
    mark = BUILDER_MARK
    curve = bpy.data.curves.new('Two-dot builder mark cutter', 'FONT')
    curve.body = mark['text']
    font = bpy.data.fonts.load(mark['font_path'])
    curve.font = font
    curve.size = 5.
    curve.extrude = .5
    curve.resolution_u = 10
    # Keep the native closed-fill default; text-curve fill enums vary by version.
    cutter = bpy.data.objects.new('Two-dot | inset christopherbrown.io cutter', curve)
    K['lid_col'].objects.link(cutter)
    active(cutter)
    assert 'MESH' in [item.identifier for item in bpy.ops.object.convert.get_rna_type().properties['target'].enum_items]
    bpy.ops.object.convert(target='MESH')
    cutter = bpy.context.object
    coords = [vertex.co.copy() for vertex in cutter.data.vertices]
    low = Vector(tuple(min(point[i] for point in coords) for i in range(3)))
    high = Vector(tuple(max(point[i] for point in coords) for i in range(3)))
    factor = mark['width_mm'] / (high.x-low.x)
    center = (low+high)/2
    floor = mark['surface_z_mm']-mark['depth_mm']
    for vertex in cutter.data.vertices:
        vertex.co.x = (vertex.co.x-center.x)*factor + mark['center_xy_mm'][0]
        vertex.co.y = (vertex.co.y-center.y)*factor + mark['center_xy_mm'][1]
        vertex.co.z = floor + (vertex.co.z-low.z)/(high.z-low.z)*(mark['depth_mm']+.2)
    mesh = bmesh.new()
    mesh.from_mesh(cutter.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=1e-5)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    assert all(edge.is_manifold for edge in mesh.edges), 'Builder mark cutter must be closed.'
    mesh.to_mesh(cutter.data)
    mesh.free()
    cutter.data.update()
    export(cutter, 'construction/builder_mark_cutter')
    boolean(lid, cutter)
    lid['builder_mark_text'] = mark['text']
    lid['builder_mark_width_mm'] = mark['width_mm']
    lid['builder_mark_height_mm'] = (high.y-low.y)*factor
    lid['builder_mark_depth_mm'] = mark['depth_mm']
    lid['builder_mark_remaining_wall_mm'] = floor-58.4
    if curve.users == 0:
        bpy.data.curves.remove(curve)
    if font.users == 0:
        bpy.data.fonts.remove(font)
    print('Inset builder mark: '+mark['text']+', '+str(mark['width_mm'])+' mm wide, '+str(mark['depth_mm'])+' mm deep.')


def finish():
    active(K['body'])
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                region = area.spaces.active.region_3d
                region.view_location = Vector((0, 0, 26))
                region.view_distance = 320
                region.view_rotation = (Vector((0, 0, 26))-Vector((220, -160, -330))).to_track_quat('-Z', 'Y')
                if 'ORTHO' in [item.identifier for item in region.bl_rna.properties['view_perspective'].enum_items]:
                    region.view_perspective = 'ORTHO'
                shading = area.spaces.active.shading
                if 'MATERIAL' in [item.identifier for item in shading.bl_rna.properties['color_type'].enum_items]:
                    shading.color_type = 'MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/two_dot_topper.blend')
    print('Saved the separate full two-dot topper revision.')


def import_canonical():
    for key, name, collection, mat in [
        ('body_navy', 'Two-dot | navy shell', K['body_col'], K['dark_mat']),
        ('body_white_face', 'Two-dot | original white bands', K['body_col'], K['white_mat']),
        ('snap_back', 'Two-dot | six tested latches', K['lid_col'], K['white_mat']),
    ]:
        old = bpy.data.objects.get(name)
        props = {key: old[key] for key in old.keys()}
        bpy.data.objects.remove(old, do_unlink=True)
        obj = load(key, name, collection, canonical=True)
        color(obj, mat)
        for prop, value in props.items():
            obj[prop] = value
    restore()
    finish()
