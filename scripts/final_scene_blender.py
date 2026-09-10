"""Keep the delivered blend tidy, with current source texts and a front view."""
import bpy
from pathlib import Path
ROOT=Path('/Users/chris/Codex Projects/roanoke-star-tree-topper')
for t in list(bpy.data.texts):
 if any(t.name.startswith(n) for n in ['BUILD_SOURCE.py','README','MEASURED_PATHS.json','TOPPER_PROFILES.json','DESIGN_REPORT.md']):bpy.data.texts.remove(t)
for name,file in [('BUILD_SOURCE.py','scripts/build_roanoke_blender.py'),('MEASURED_PATHS.json','final/profile_measurements.json'),('TOPPER_PROFILES.json','scripts/topper_profiles.json'),('DESIGN_REPORT.md','final/DESIGN_REPORT.md')]:
 t=bpy.data.texts.new(name);t.write((ROOT/file).read_text())
t=bpy.data.texts.new('README');t.write('Final corrected Roanoke Star topper: six independently measured outline inserts in three pairs. Three named object groups, two physical colors. All mesh coordinates/export units are millimeters. See DESIGN_REPORT.md for printing, mounting, validation, and accuracy limits. Hidden Reference_Geometry contains the six editable paths and the packed city aerial. All three printable groups are watertight. The light group intentionally contains six closed loops. Individual STLs are oriented for printing; the 3MF and assembled STL show assembly positions.')
bpy.data.orphans_purge(do_recursive=True)
cam=bpy.context.scene.camera;cam.location=(0,0,440);cam.data.ortho_scale=235;look(cam,(0,0,0))
active(bpy.data.objects['RoanokeStar_Base'])
bpy.context.area.type='VIEW_3D'
s=bpy.context.area.spaces.active;s.region_3d.view_distance=285;s.region_3d.view_location=(0,0,0);s.clip_end=2000;s.shading.color_type='MATERIAL'
from mathutils import Quaternion
s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'final/roanoke_star_tree_topper.blend'))
