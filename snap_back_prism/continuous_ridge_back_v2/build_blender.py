"""Inspect the new back alongside the unmodified V3 front through Blender MCP."""
import json
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/continuous_ridge_back_v2'
SOURCE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/spacing_v3'
SCENE_NAME = 'Roanoke Star | continuous ridge back v2 - doubled tabs'
K = {}


def active(obj):
    for other in bpy.context.view_layer.objects:
        other.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = .55
    mat.diffuse_color = color
    return mat


def setup():
    assert bpy.data.scenes.get(SCENE_NAME) is None
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    assert 'METRIC' in [item.identifier for item in scene.unit_settings.bl_rna.properties['system'].enum_items]
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    printable = bpy.data.collections.new('CONTINUOUS RIDGE V2 | printable back')
    reference = bpy.data.collections.new('CONTINUOUS RIDGE V2 | unchanged shell reference')
    for collection in [printable, reference]:
        scene.collection.children.link(collection)
    white = material('Continuous ridge v2 | white PLA', (.91, .925, .90, 1))
    black = material('Continuous ridge v2 | existing black shell', (.008, .009, .011, 1))
    for key, path, name, collection, mat in [
        ('back', HERE+'/continuous_ridge_back.stl', 'Continuous ridge v2 | six fixed tabs and uninterrupted ridge', printable, white),
        ('black', SOURCE+'/body_black.stl', 'Continuous ridge v2 | unchanged printed black shell', reference, black),
        ('white', SOURCE+'/body_white_diffused.stl', 'Continuous ridge v2 | unchanged printed front stars', reference, white),
    ]:
        bpy.ops.wm.stl_import(filepath=path, global_scale=1., use_scene_unit=False)
        obj = bpy.context.object
        obj.name = name
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collection.objects.link(obj)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        obj['source_mesh_file'] = path.rsplit('/', 1)[-1]
        K[key] = obj
    K['back']['attachment'] = 'continuous 0.8 mm ridge with six integral fixed tapered tabs, doubled 2.10 mm projection; no relieved flexures'
    K['back']['tab_width_mm'] = 8.
    K['back']['ridge_thickness_mm'] = .8
    K['back']['ridge_to_wall_clearance_mm'] = .55
    K['back']['ridge_depth_mm'] = 6.
    K['back']['tab_engagement_mm'] = 1.55
    K['back']['tab_projection_from_ridge_mm'] = 2.10
    K['back']['previous_tab_projection_from_ridge_mm'] = 1.05
    K['back']['upper_catch_boss_clearance_z_mm'] = 55.0
    K['back']['builder_mark_text'] = 'christopherbrown.io'
    K['back']['builder_mark_depth_mm'] = 1.
    K['back']['physical_fit_tested'] = True
    K['back']['physical_fit_confirmation_date'] = '2026-10-16'
    K['back']['physical_fit_notes'] = 'Owner reports printed v2 locks onto the existing spacing_v3 front; deformation and durability remain unvalidated.'
    K['back']['PLA_deformation_validated'] = False
    scene['existing_printed_shell_changed'] = False
    scene['physical_grip_test_pending'] = False
    scene['durability_test_pending'] = True
    K.update(scene=scene, reference=reference)
    active(K['back'])
    print('Loaded the continuous-ridge back and unchanged front in a separate scene.')


def validate():
    output = {}
    for key in ['back', 'black', 'white']:
        obj = K[key]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        boundary = sum(edge.is_boundary for edge in bm.edges)
        nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
        volume = bm.calc_volume(signed=True)
        bm.free()
        assert boundary == nonmanifold == 0 and volume > 0
        obj.data.calc_loop_triangles()
        vertices = [v.co.copy() for v in obj.data.vertices]
        triangles = [tuple(t.vertices) for t in obj.data.loop_triangles]
        tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0)
        overlaps = [(a, b) for a, b in tree.overlap(tree)
                    if a < b and not set(triangles[a]) & set(triangles[b])]
        assert not overlaps, (key, overlaps[:8])
        output[key] = {'boundary_edges': boundary, 'non_manifold_edges': nonmanifold,
            'volume_mm3': volume, 'nonadjacent_triangle_intersection_candidates': len(overlaps)}
    validation={'status':'passed','meshes':output}
    print('BLENDER_VALIDATION '+json.dumps(validation))


def restore():
    scene = bpy.data.scenes[SCENE_NAME]
    bpy.context.window.scene = scene
    K['scene'] = scene
    for key, name in [
        ('back', 'Continuous ridge v2 | six fixed tabs and uninterrupted ridge'),
        ('black', 'Continuous ridge v2 | unchanged printed black shell'),
        ('white', 'Continuous ridge v2 | unchanged printed front stars'),
    ]:
        K[key] = bpy.data.objects[name]
    K['reference'] = bpy.data.collections['CONTINUOUS RIDGE V2 | unchanged shell reference']
    if scene.camera is not None:
        K['camera'] = scene.camera


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = K['scene']
    try:
        scene.render.engine = 'CYCLES'
    except TypeError as error:
        raise RuntimeError('Cycles not available: '+str(error))
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    assert 'PNG' in [i.identifier for i in scene.render.image_settings.bl_rna.properties['file_format'].enum_items]
    scene.render.image_settings.file_format = 'PNG'
    world = bpy.data.worlds.new('Continuous ridge v2 studio')
    world.use_nodes = True
    background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    background.inputs[0].default_value = (.065, .08, .105, 1)
    background.inputs[1].default_value = .45
    scene.world = world
    helpers = bpy.data.collections.new('CONTINUOUS RIDGE V2 | preview helpers')
    scene.collection.children.link(helpers)
    camera_data = bpy.data.cameras.new('Continuous ridge v2 preview camera')
    assert 'ORTHO' in [i.identifier for i in camera_data.bl_rna.properties['type'].enum_items]
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 235
    camera_data.clip_end = 3000
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    helpers.objects.link(camera)
    scene.camera = camera
    K['camera'] = camera
    for name, location, energy, size in [
        ('Key', (-120, 180, -240), 2100000, 180),
        ('Fill', (140, -120, -200), 1100000, 160),
        ('Rear', (-120, 80, 240), 2400000, 160),
    ]:
        data = bpy.data.lights.new('Continuous ridge v2 '+name, type='AREA')
        data.energy = energy
        data.size = size
        obj = bpy.data.objects.new(data.name, data)
        helpers.objects.link(obj)
        obj.location = location
        aim(obj, (0, 0, 50))
    helpers.hide_viewport = True


def render_inside():
    K['reference'].hide_render = True
    K['back'].hide_render = False
    K['back'].location = (0, 0, 0)
    camera = K['camera']
    camera.location = (150, -100, -330)
    aim(camera, (0, 0, 51))
    camera.data.ortho_scale = 245
    K['scene'].render.filepath = HERE+'/previews/back_inside.png'
    bpy.ops.render.render(write_still=True)
    print('Rendered the real back mesh from the inside, showing the continuous ridge and six integral fixed tabs.')


def render_outside():
    camera = K['camera']
    camera.location = (0, 0, 350)
    aim(camera, (0, 0, 59))
    camera.data.ortho_scale = 220
    K['scene'].render.filepath = HERE+'/previews/back_outside.png'
    bpy.ops.render.render(write_still=True)
    print('Rendered the retained inset builder mark.')


def render_exploded():
    K['reference'].hide_render = False
    K['back'].location.z = 28
    camera = K['camera']
    camera.location = (185, -105, 390)
    aim(camera, (0, 0, 45))
    camera.data.ortho_scale = 260
    K['scene'].render.filepath = HERE+'/previews/exploded.png'
    bpy.ops.render.render(write_still=True)
    K['back'].location.z = 0
    print('Rendered the new cover with the unchanged front shell.')


def save():
    K['reference'].hide_render = True
    K['reference'].hide_viewport = True
    K['back'].location = (0, 0, 0)
    active(K['back'])
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                region = area.spaces.active.region_3d
                region.view_location = Vector((0, 0, 50))
                region.view_distance = 300
                region.view_rotation = (Vector((0, 0, 50))-Vector((150, -100, -330))).to_track_quat('-Z', 'Y')
                if 'ORTHO' in [i.identifier for i in region.bl_rna.properties['view_perspective'].enum_items]:
                    region.view_perspective = 'ORTHO'
                shading = area.spaces.active.shading
                if 'MATERIAL' in [i.identifier for i in shading.bl_rna.properties['color_type'].enum_items]:
                    shading.color_type = 'MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=HERE+'/continuous_ridge_back.blend')
    print('Saved the separate editable back revision.')


def render_direct_and_detail():
    import math
    K['reference'].hide_render = True
    K['camera'].location = (0, 0, -350)
    K['camera'].rotation_euler = (math.pi, 0, math.pi)
    K['camera'].data.ortho_scale = 220
    K['scene'].render.filepath = HERE+'/previews/back_inside_direct.png'
    bpy.ops.render.render(write_still=True)
    K['camera'].location = (80, 75, 18)
    aim(K['camera'], (66.4, 31, 55))
    K['camera'].data.ortho_scale = 33
    K['scene'].render.filepath = HERE+'/previews/fixed_tab_detail.png'
    bpy.ops.render.render(write_still=True)
