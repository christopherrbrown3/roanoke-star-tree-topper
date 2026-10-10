"""Load and inspect the corrected actual solids in the user's live Blender."""
import json

import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/spacing_v3'
SCENE_NAME = 'Roanoke Star | thinner frames spacing v3'
K = {}


def look_at(obj, target):
    direction = (Vector(target)-obj.location).normalized()
    right = direction.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(direction)
    obj.rotation_euler = Matrix((right, up, -direction)).transposed().to_euler()


def material(name, color):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = next(node for node in result.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = .5
    result.diffuse_color = color
    return result


def setup():
    assert bpy.data.scenes.get(SCENE_NAME) is None, 'Revision scene already loaded; use restore().'
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    collection = bpy.data.collections.new('SPACING V3 | printable solids')
    scene.collection.children.link(collection)
    black = material('Spacing v3 | black PLA A2', (.008, .009, .011, 1))
    white = material('Spacing v3 | white PLA A1', (.92, .94, .92, 1))
    for key, filename, name, mat in [
        ('black', 'body_black.stl', 'Spacing v3 | black shell and catches A2', black),
        ('white', 'body_white_diffused.stl', 'Spacing v3 | white stars and 130 diffusers A1', white),
        ('back', 'snap_back.stl', 'Spacing v3 | christopherbrown.io marked two-dot back', white),
    ]:
        bpy.ops.wm.stl_import(filepath=HERE+'/'+filename, global_scale=1., use_scene_unit=False)
        obj = bpy.context.object
        obj.name = name
        for previous in list(obj.users_collection):
            previous.objects.unlink(obj)
        collection.objects.link(obj)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for face in obj.data.polygons:
            face.material_index = 0
        obj['source_mesh_file'] = filename
        K[key] = obj
    K['white']['diffuser_thickness_mm'] = .4
    K['white']['hidden_bulb_windows'] = 130
    K['white']['continuous_white_stars'] = 3
    K['white']['nominal_band_width_mm'] = 5.7
    K['white']['nominal_black_outer_border_mm'] = 1.2
    K['white']['hidden_windows_unchanged_from_v2'] = True
    K['back']['builder_mark_text'] = 'christopherbrown.io'
    K['back']['builder_mark_width_mm'] = 72.
    K['back']['builder_mark_depth_mm'] = 1.
    scene['layer_height_mm'] = .2
    scene['diffuser_printed_layers'] = 2
    scene['selected_connector'] = 'physically tested two-dot'
    scene['revised_proportions_physically_tested'] = False
    K['scene'] = scene
    print('Loaded the corrected front and the unchanged marked back in a separate scene.')


def validate():
    output = {}
    for key in ['black', 'white', 'back']:
        obj = K[key]
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
        boundary = sum(edge.is_boundary for edge in bm.edges)
        volume = bm.calc_volume(signed=True)
        bm.free()
        assert nonmanifold == boundary == 0 and volume > 0
        mesh.calc_loop_triangles()
        vertices = [vertex.co.copy() for vertex in mesh.vertices]
        triangles = [tuple(face.vertices) for face in mesh.loop_triangles]
        tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0)
        intersections = []
        for a, b in tree.overlap(tree):
            if a >= b or set(triangles[a]) & set(triangles[b]):
                continue
            intersections.append([a, b])
        assert not intersections, (key, intersections[:10])
        output[key] = {'non_manifold_edges': nonmanifold, 'boundary_edges': boundary,
                       'signed_volume_mm3': volume, 'triangles': len(triangles),
                       'nonadjacent_triangle_intersection_candidates': len(intersections)}
    print('VALIDATION_REPORT '+json.dumps({'status': 'passed', 'meshes': output}))


def restore():
    scene = bpy.data.scenes.get(SCENE_NAME)
    assert scene is not None
    bpy.context.window.scene = scene
    K['scene'] = scene
    for key, name in [('black', 'Spacing v3 | black shell and catches A2'),
                      ('white', 'Spacing v3 | white stars and 130 diffusers A1'),
                      ('back', 'Spacing v3 | christopherbrown.io marked two-dot back')]:
        K[key] = bpy.data.objects[name]
    if scene.camera is not None:
        K['camera'] = scene.camera


def reload_meshes():
    collection = bpy.data.collections['SPACING V3 | printable solids']
    for key, filename in [('black', 'body_black.stl'), ('white', 'body_white_diffused.stl')]:
        old = K[key]
        name = old.name
        mat = old.data.materials[0]
        props = {name: old[name] for name in old.keys()}
        bpy.data.objects.remove(old, do_unlink=True)
        bpy.ops.wm.stl_import(filepath=HERE+'/'+filename, global_scale=1., use_scene_unit=False)
        obj = bpy.context.object
        obj.name = name
        for previous in list(obj.users_collection):
            previous.objects.unlink(obj)
        collection.objects.link(obj)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for prop, value in props.items():
            obj[prop] = value
        K[key] = obj


def studio():
    scene = K['scene']
    try:
        scene.render.engine = 'CYCLES'
    except TypeError as error:
        raise RuntimeError('Cycles renderer unavailable') from error
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    assert 'PNG' in [item.identifier for item in scene.render.image_settings.bl_rna.properties['file_format'].enum_items]
    scene.render.image_settings.file_format = 'PNG'
    helpers = bpy.data.collections.new('SPACING V3 | preview studio, not printed')
    scene.collection.children.link(helpers)
    world = bpy.data.worlds.new('Spacing v3 studio world')
    world.use_nodes = True
    background = next(node for node in world.node_tree.nodes if node.type == 'BACKGROUND')
    background.inputs[0].default_value = (.16, .19, .24, 1)
    background.inputs[1].default_value = .5
    scene.world = world
    camera_data = bpy.data.cameras.new('Spacing v3 preview camera')
    assert 'ORTHO' in [item.identifier for item in camera_data.bl_rna.properties['type'].enum_items]
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 225
    camera_data.clip_end = 3000
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    helpers.objects.link(camera)
    scene.camera = camera
    K['camera'] = camera
    for name, location, energy, size in [
        ('Key', (-150, 220, -260), 2200000, 240),
        ('Fill', (180, -40, -170), 1400000, 170),
        ('Rear', (-100, 120, 240), 2300000, 180),
    ]:
        light = bpy.data.lights.new('Spacing v3 '+name, type='AREA')
        assert 'DISK' in [item.identifier for item in light.bl_rna.properties['shape'].enum_items]
        light.shape = 'DISK'
        light.energy = energy
        light.size = size
        obj = bpy.data.objects.new(light.name, light)
        helpers.objects.link(obj)
        obj.location = location
        look_at(obj, (0, 0, 26))
    helpers.hide_viewport = True


def render_front():
    camera = K['camera']
    camera.location = (0, 0, -360)
    look_at(camera, (0, 0, 0))
    camera.data.ortho_scale = 225
    K['scene'].render.filepath = HERE+'/previews/front.png'
    bpy.ops.render.render(write_still=True)
    print('Rendered the actual corrected front mesh.')


def render_assembled():
    camera = K['camera']
    camera.location = (190, -100, -420)
    look_at(camera, (0, 0, 26))
    camera.data.ortho_scale = 265
    K['scene'].render.filepath = HERE+'/previews/assembled.png'
    bpy.ops.render.render(write_still=True)
    print('Rendered the actual assembled topper.')


def save():
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    K['white'].select_set(True)
    bpy.context.view_layer.objects.active = K['white']
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                region = area.spaces.active.region_3d
                region.view_location = Vector((0, 0, 26))
                region.view_distance = 300
                region.view_rotation = (Vector((0, 0, 26))-Vector((0, 0, -360))).to_track_quat('-Z', 'Y')
                region.view_perspective = 'ORTHO'
                area.spaces.active.shading.color_type = 'MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/roanoke_star_spacing_v3.blend')
    print('Saved the separate editable Blender revision.')
