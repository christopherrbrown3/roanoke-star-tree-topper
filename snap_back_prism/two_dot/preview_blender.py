"""Render actual Blender CAD previews without changing print geometry."""
import bpy
from mathutils import Vector, Matrix


def look_at(obj, target):
    direction = (Vector(target)-obj.location).normalized()
    right = direction.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(direction)
    obj.rotation_euler = Matrix((right, up, -direction)).transposed().to_euler()


def setup_studio():
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
    collection = bpy.data.collections.new('TWO DOT | preview studio, not printed')
    scene.collection.children.link(collection)
    world = bpy.data.worlds.new('Two-dot preview world')
    scene.world = world
    world.use_nodes = True
    shader = next(node for node in world.node_tree.nodes if node.type == 'BACKGROUND')
    shader.inputs[0].default_value = (.16, .19, .24, 1)
    shader.inputs[1].default_value = .5
    data = bpy.data.cameras.new('Two-dot preview camera')
    assert 'ORTHO' in [item.identifier for item in data.bl_rna.properties['type'].enum_items]
    data.type = 'ORTHO'
    data.ortho_scale = 265
    data.clip_end = 3000
    camera = bpy.data.objects.new(data.name, data)
    collection.objects.link(camera)
    camera.location = (190, -100, -420)
    look_at(camera, (0, 0, 26))
    scene.camera = camera
    K['camera'] = camera
    for name, location, energy, size in [
        ('Key', (-150, 220, -260), 2200000, 240),
        ('Fill', (180, -40, -170), 1400000, 170),
        ('Rim', (-100, 120, 240), 2300000, 180),
    ]:
        light = bpy.data.lights.new('Two-dot preview '+name, type='AREA')
        assert 'DISK' in [item.identifier for item in light.bl_rna.properties['shape'].enum_items]
        light.shape = 'DISK'
        light.energy = energy
        light.size = size
        obj = bpy.data.objects.new(light.name, light)
        collection.objects.link(obj)
        obj.location = location
        look_at(obj, (0, 0, 26))
    collection.hide_viewport = True


def render_preview(name, viewpoint, back_only=False):
    camera = K['camera']
    camera.location = viewpoint
    look_at(camera, (0, 0, 26))
    K['body'].hide_render = back_only
    K['white'].hide_render = back_only
    K['scene'].render.filepath = HERE+'/previews/'+name+'.png'
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        K['body'].hide_render = False
        K['white'].hide_render = False
    print('Rendered '+name)


def render_builder_mark():
    """Show the real engraved mesh on the outside of the detachable cover."""
    scene = K['scene']
    camera = K['camera']
    original_scale = camera.data.ortho_scale
    original_resolution = (scene.render.resolution_x, scene.render.resolution_y)
    camera.location = (0, -75, 300)
    look_at(camera, (0, 5.5, 59.5))
    camera.data.ortho_scale = 110
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 600
    K['body'].hide_render = True
    K['white'].hide_render = True
    scene.render.filepath = HERE+'/previews/builder_mark_detail.png'
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        K['body'].hide_render = False
        K['white'].hide_render = False
        camera.data.ortho_scale = original_scale
        scene.render.resolution_x, scene.render.resolution_y = original_resolution
    print('Rendered builder_mark_detail')
