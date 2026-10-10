"""Build only the two revised coupons in a separate live Blender scene."""
import bpy
from mathutils import Matrix, Vector

HERE = '/Users/chris/Codex Projects/roanoke-star-tree-topper/snap_back_prism/connector_fit_v2'
SCENE_NAME = 'Connector fit v2 | one and two dots'


def active(obj):
    for other in bpy.context.view_layer.objects:
        other.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def load(name):
    bpy.ops.wm.stl_import(filepath=HERE + '/construction/' + name + '.stl',
                          global_scale=1, use_scene_unit=False)
    return bpy.context.object


def boolean(obj, cutter, operation):
    active(obj)
    modifier = obj.modifiers.new(operation, 'BOOLEAN')
    assert operation in [item.identifier for item in modifier.bl_rna.properties['operation'].enum_items]
    assert 'MANIFOLD' in [item.identifier for item in modifier.bl_rna.properties['solver'].enum_items]
    modifier.operation = operation
    modifier.solver = 'MANIFOLD'
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def export(obj, name):
    active(obj)
    bpy.ops.wm.stl_export(filepath=HERE + '/' + name + '.stl', export_selected_objects=True,
                          global_scale=1, use_scene_unit=False, apply_modifiers=True)


def setup():
    assert bpy.data.scenes.get(SCENE_NAME) is None, 'The fit trial scene already exists.'
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    assert 'METRIC' in [item.identifier for item in scene.unit_settings.bl_rna.properties['system'].enum_items]
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    scene['reported_baseline_result'] = 'Stops short or needs too much force'
    scene['new_trials_physically_tested'] = False
    material = bpy.data.materials.new('Connector trial | white PLA')
    material.use_nodes = True
    shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (.88, .90, .86, 1)
    shader.inputs['Roughness'].default_value = .5
    material.diffuse_color = (.88, .90, .86, 1)


def build_trial(key, dots, row_y):
    material = bpy.data.materials.get('Connector trial | white PLA')
    assert material is not None
    base = load(key + '_floor')
    boolean(base, load(key + '_wall'), 'UNION')
    boolean(base, load(key + '_window'), 'DIFFERENCE')
    boolean(base, load(key + '_floor_dots'), 'UNION')
    boolean(base, load(key + '_floor_grip'), 'UNION')
    boolean(base, load(key + '_floor_bevel'), 'DIFFERENCE')
    base.name = str(dots) + ' dot | catch wall'
    cap = load(key + '_cap')
    boolean(cap, load(key + '_rim'), 'UNION')
    boolean(cap, load(key + '_hook'), 'UNION')
    boolean(cap, load(key + '_cap_dots'), 'UNION')
    boolean(cap, load(key + '_cap_grip'), 'UNION')
    boolean(cap, load(key + '_cap_bevel'), 'DIFFERENCE')
    cap.name = str(dots) + ' dot | flexible cap'
    for obj in (base, cap):
        obj.data.materials.clear()
        obj.data.materials.append(material)
        obj['trial_id'] = key
    export(base, key + '_catch')
    export(cap, key + '_back')
    base.location = (-30, row_y - 10, -48.5)
    cap.matrix_world = Matrix(((1, 0, 0, 30), (0, -1, 0, row_y + 10), (0, 0, -1, 60), (0, 0, 0, 1)))
    print('Built and exported ' + key)


def finish():
    scene = bpy.context.scene
    target = Vector((0, 0, 4))
    viewpoint = Vector((65, -95, 90))
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != 'VIEW_3D':
                continue
            region = area.spaces.active.region_3d
            region.view_location = target
            region.view_distance = 125
            region.view_rotation = (target - viewpoint).to_track_quat('-Z', 'Y')
            if 'ORTHO' in [item.identifier for item in region.bl_rna.properties['view_perspective'].enum_items]:
                region.view_perspective = 'ORTHO'
            shading = area.spaces.active.shading
            if 'MATERIAL' in [item.identifier for item in shading.bl_rna.properties['color_type'].enum_items]:
                shading.color_type = 'MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=HERE + '/connector_fit_v2.blend')
    print('Saved separate connector trials file.')
