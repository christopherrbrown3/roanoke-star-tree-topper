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
    collection = bpy.data.collections.new('CONTINUOUS | preview studio, not printed')
    scene.collection.children.link(collection)
    world = bpy.data.worlds.new('Continuous preview world')
    scene.world = world
    world.use_nodes = True
    shader = next(node for node in world.node_tree.nodes if node.type == 'BACKGROUND')
    shader.inputs[0].default_value = (.16, .19, .24, 1)
    shader.inputs[1].default_value = .5
    data = bpy.data.cameras.new('Continuous preview camera')
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
        light = bpy.data.lights.new('Continuous preview '+name, type='AREA')
        assert 'DISK' in [item.identifier for item in light.bl_rna.properties['shape'].enum_items]
        light.shape = 'DISK'
        light.energy = energy
        light.size = size
        obj = bpy.data.objects.new(light.name, light)
        collection.objects.link(obj)
        obj.location = location
        look_at(obj, (0, 0, 26))
    collection.hide_viewport = True



def render_diffused():
    scene = K['scene']
    camera = K['camera']
    for key in ['sample_black', 'sample_white']:
        K[key].hide_render = True
    scene.render.filepath = HERE+'/previews/assembled.png'
    bpy.ops.render.render(write_still=True)
    for key in ['body', 'white', 'lid']:
        K[key].hide_render = True
    for key in ['sample_black', 'sample_white']:
        K[key].hide_render = False
    camera.location = (40, 115, -160)
    look_at(camera, (0, 145, 2))
    camera.data.ortho_scale = 80
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 750
    scene.render.filepath = HERE+'/previews/test_face.png'
    bpy.ops.render.render(write_still=True)
    camera.location = (40, 115, 160)
    look_at(camera, (0, 145, 2))
    scene.render.filepath = HERE+'/previews/test_inside.png'
    bpy.ops.render.render(write_still=True)
    for key in ['body', 'white', 'lid']:
        K[key].hide_render = False
    for key in ['sample_black', 'sample_white']:
        K[key].hide_render = True
    camera.location = (190, -100, -420)
    look_at(camera, (0, 0, 26))
    camera.data.ortho_scale = 265
    scene.render.resolution_y = 1000
    print('Rendered full diffused star and both sides of the actual print sample.')
