"""Finish the deliverable in Blender's GUI without rebuilding its geometry."""
import bpy
import hashlib
import json
import struct
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'print_in_place'

def stl_bytes(obj):
    obj.data.calc_loop_triangles()
    triangles = obj.data.loop_triangles
    data = bytearray(b'Roanoke Star A1 | mm | face down'.ljust(80, b' '))
    data.extend(struct.pack('<I', len(triangles)))
    for triangle in triangles:
        a, b, c = [obj.matrix_world @ obj.data.vertices[i].co for i in triangle.vertices]
        normal = (b-a).cross(c-a).normalized()
        data.extend(struct.pack('<12fH', *normal, *a, *b, *c, 0))
    return bytes(data)

checks = {}
for name, filename in [('RoanokeStar_Body', 'body_material.stl'),
                       ('RoanokeStar_Tube_Sections', 'white_tube_material.stl')]:
    obj = bpy.data.objects[name]
    assert len(obj.data.materials) == 1 and obj.data.materials[0]
    assert all(p.material_index == 0 for p in obj.data.polygons)
    actual = stl_bytes(obj)
    assert actual == (OUT/filename).read_bytes(), f'Scene/export mismatch: {name}'
    checks[name] = {
        'scene_matches_validated_stl': True,
        'sha256': hashlib.sha256(actual).hexdigest(),
        'material': obj.data.materials[0].name,
        'all_faces_use_material_slot_zero': True,
    }
(OUT/'scene_export_validation.json').write_text(json.dumps(checks, indent=2)+'\n')

# Replace inherited notes from the superseded assembly scene.
for text in list(bpy.data.texts):
    bpy.data.texts.remove(text)
for filename in ['README.md', 'scripts/build_a1_print_in_place_blender.py',
                 'scripts/prepare_a1_print_in_place.py', 'scripts/a1_topper_profiles.json',
                 'scripts/check_a1_blender.py', 'scripts/validate_package_a1.py',
                 'scripts/finalize_a1_blender.py', 'print_in_place/profile_measurements.json',
                 'print_in_place/DESIGN_REPORT.md', 'print_in_place/RELEASE_STATUS.json',
                 'print_in_place/mesh_validation.json', 'print_in_place/self_intersections.json',
                 'print_in_place/scene_export_validation.json', 'research/ACCURACY_AUDIT.md',
                 'research/ANGLE_WORKSHEET.md', 'research/tube_joint_observations.json']:
    text = bpy.data.texts.new(Path(filename).name)
    text.write((ROOT/filename).read_text())

# Keep the six source paths editable as nonprinting, hidden reference curves.
ref = bpy.data.collections.get('Reference_Geometry')
if ref is None:
    ref = bpy.data.collections.new('Reference_Geometry')
    bpy.context.scene.collection.children.link(ref)
for obj in list(ref.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
paths = json.loads((OUT/'profile_measurements.json').read_text())['six_paths_mm']
for i, path in enumerate(paths, 1):
    curve = bpy.data.curves.new(f'Source path {i}', 'CURVE')
    curve.dimensions = '3D'
    spline = curve.splines.new('POLY')
    spline.points.add(len(path)-1)
    for point, (x, y) in zip(spline.points, path):
        point.co = (x, y, 0, 1)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(f'Reference_Path_{i}', curve)
    ref.objects.link(obj)
    obj['accuracy'] = 'Photo-based candidate; not a surveyed path'
ref.hide_viewport = True
ref.hide_render = True

scene = bpy.context.scene
camera = scene.camera
camera.location = (0, 0, -440)
camera.data.ortho_scale = 234
direction = (Vector((0, 0, 0))-camera.location).normalized()
right = direction.cross(Vector((0, 1, 0))).normalized()
up = right.cross(direction)
camera.rotation_euler = Matrix((right, up, -direction)).transposed().to_euler()
for obj in scene.objects:
    obj.select_set(False)
bpy.context.view_layer.objects.active = bpy.data.objects['RoanokeStar_Body']

area = bpy.context.area
area.type = 'VIEW_3D'
space = area.spaces.active
space.shading.type = 'SOLID'
space.shading.color_type = 'MATERIAL'
space.overlay.show_overlays = False
space.clip_end = 2000
space.region_3d.view_location = (0, 0, 0)
space.region_3d.view_distance = 285
space.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
space.region_3d.view_perspective = 'ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'roanoke_star_A1.blend'))
print('A1 scene saved: material slots verified, exports matched, current notes embedded.')
