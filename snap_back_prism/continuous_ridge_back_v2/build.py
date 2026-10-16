"""Continuous inset ridge and six integral fixed tabs for the printed V3 front.

Only this new revision directory is written. No relieved flexures or hinges.
Owner confirmed V2 locks onto the existing spacing_v3 front on 2026-10-16.
Clearance checks are geometric only; deformation and durability remain unvalidated.
"""
import ast
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
BASE = H.parent
SOURCE = BASE/'spacing_v3'
OLD = BASE/'two_dot'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
REAR, OUTSIDE = 58.4, 60.
WALL, GAP, RIDGE_THICKNESS = 1.2, .55, .8
RIDGE_DEPTH = 6.
TAB_WIDTH = 8.
PREVIOUS_PROJECTION = 1.05
TAB_PROJECTION = PREVIOUS_PROJECTION*2
ENGAGEMENT = TAB_PROJECTION-GAP
TAB_UPPER_CLEARANCE_Z = 55.0
TAB_UPPER_RADIAL_CLEARANCE = .1
report, template, original_settings = {}, {}, {}

# Private helpers travel with this revision; no earlier cover experiment is needed.
from geometry_helpers import (
    sha, solid, mesh_of, extrusion, placed, flat_faces, print_mesh, export_mesh,
)


def export(value, key):
    return export_mesh(value, H / (key+'.stl'))


def local_boss():
    """Integral fixed tab, no separate stem: entry and rear print ramps.

    Coordinates are inward distance from outside wall, and assembled Z.
    The nose projects exactly 2.10 mm beyond the unchanged ridge exterior.
    Trim the longer rear ramp at the existing catch upper edge, retaining
    0.1 mm clearance and continuous attachment to the unchanged ridge.
    """
    outer = WALL+GAP
    inner = outer+RIDGE_THICKNESS/2
    profile = Polygon([(outer,52.5),(WALL-ENGAGEMENT,54.),
                       (WALL-ENGAGEMENT,54.4),(outer,55.45),
                       (inner,55.45),(inner,52.5)])
    profile = profile.difference(box(-10,TAB_UPPER_CLEARANCE_Z,
                                     WALL+TAB_UPPER_RADIAL_CLEARANCE,70))
    assert profile.geom_type=='Polygon' and profile.is_valid
    mesh = trimesh.creation.extrude_polygon(profile,TAB_WIDTH,engine='earcut')
    v=mesh.vertices.copy()
    mesh.vertices=np.column_stack([v[:,2]+8.-TAB_WIDTH/2,v[:,0],v[:,1]])
    if mesh.volume < 0: mesh.invert()
    return mesh


def main():
    global report, template, original_settings
    (H/'previews').mkdir(exist_ok=True)
    (H/'construction').mkdir(exist_ok=True)
    before=json.loads((H/'preservation_before.json').read_text())
    assert all(sha(ROOT/p)==digest for p,digest in before.items())
    params=json.loads((SOURCE/'parameters.json').read_text())
    outline=Polygon(json.loads((SOURCE/'profiles.json').read_text())['outline'][0]['loops'][0])
    prism=json.loads((ROOT/'pentagrammic_prism/profiles.json').read_text())
    vents=unary_union([Polygon(p['loops'][0]) for p in prism['rear_vents']])
    mouth_shape=Polygon(prism['bottom_mouth'][0]['loops'][0])
    plate_shape=outline.difference(vents)
    plate=extrusion(plate_shape,REAR,OUTSIDE)
    mark_mesh=trimesh.load(OLD/'construction/builder_mark_cutter.stl')
    marked=plate-solid(mark_mesh)
    assert abs((plate-marked).volume()-153.59540798316627)<.01
    # No gaps at catches. The only interruption is the existing tree entrance.
    ridge_shape=outline.buffer(-(WALL+GAP),join_style=2).difference(
        outline.buffer(-(WALL+GAP+RIDGE_THICKNESS),join_style=2)).difference(mouth_shape)
    assert ridge_shape.geom_type=='Polygon' and len(ridge_shape.interiors)==0
    ridge=extrusion(ridge_shape,REAR-RIDGE_DEPTH,REAR+.2)
    ridge_mesh=export(ridge,'construction/continuous_ridge')
    boss=local_boss()
    tabs=[solid(placed(boss,c)) for c in params['clips']]
    for i,t in enumerate(tabs,1): export(t,f'construction/fixed_tab_{i}')
    all_tabs=mf.Manifold.batch_boolean(tabs,mf.OpType.Add)
    back=(marked+ridge+all_tabs).simplify(1e-5)
    mesh=export(back,'continuous_ridge_back')
    printable=print_mesh(mesh,flip=True)
    printable.export(H/'continuous_ridge_back_print.stl')
    for filename in ['continuous_ridge_back.stl','continuous_ridge_back_print.stl']:
        reopened=trimesh.load(H/filename)
        assert reopened.is_watertight and reopened.is_winding_consistent
        assert reopened.body_count==1 and reopened.area_faces.min()>1e-10
    export(marked,'construction/marked_plate')
    shell=solid(trimesh.load(SOURCE/'front_shell_fused.stl'))
    mouth=solid(trimesh.load(ROOT/'pentagrammic_prism/construction/bottom_mouth.stl'))
    leader=solid(trimesh.load(ROOT/'pentagrammic_prism/construction/tree_leader_clearance_reference.stl'))
    overlap=abs((back^shell).volume())
    assert overlap<.01,overlap
    assert abs((back^mouth).volume())<.01
    assert abs((back^leader).volume())<.01
    expected_outside=plate_shape.difference(flat_faces(mark_mesh,59.))
    surface_difference=flat_faces(mesh,OUTSIDE).symmetric_difference(expected_outside).area
    assert surface_difference<.05
    walls=extrusion(outline.difference(outline.buffer(-WALL,join_style=2)),4.,REAR)
    catches=[]
    for i,(tab,c) in enumerate(zip(tabs,params['clips']),1):
        interference=(tab^walls).volume()
        assert interference>1.,(i,interference)
        assert abs((tab^shell).volume())<.01
        catches.append({'tab':i,**c,'actual_window_center_xy':(np.asarray(c['center_xy'])+8*np.asarray(c['tangent_xy'])).tolist(),'window_width_mm':9.2,'tab_width_mm':TAB_WIDTH,
            'tangential_clearance_each_side_mm':.6,'window_z_mm':[52.2,55.1],
            'full_engagement_z_mm':[54.,54.4], 'radial_engagement_mm':ENGAGEMENT,
            'engagement_in_filled_wall_mm3':interference,'actual_shell_collision_mm3':abs((tab^shell).volume())})
    # Axial clearance of the ridge itself, excluding bosses which require
    # manual deformation during assembly. This deliberately claims no strain model.
    maximum_ridge_sweep=0.
    for z in np.linspace(0,RIDGE_DEPTH+.2,40):
        maximum_ridge_sweep=max(maximum_ridge_sweep,abs(((marked+ridge).translate([0,0,float(z)])^shell).volume()))
    assert maximum_ridge_sweep<.01
    report={'status':'passed','back':{'watertight':True,'connected_solids':1,
        'triangles':len(mesh.faces),'volume_mm3':mesh.volume,'geometry_sha256':sha(H/'continuous_ridge_back.stl'),
        'print_bounds_mm':printable.bounds.tolist()},'printed_shell_sha256':sha(SOURCE/'front_shell_fused.stl'),
        'assembled_back_to_shell_collision_mm3':overlap,
        'ridge_contiguous_components':1,'ridge_has_catch_relief_gaps':False,
        'ridge_axial_insertion_sweep_max_collision_mm3':maximum_ridge_sweep,
        'bottom_mouth_overlap_mm3':abs((back^mouth).volume()),
        'tree_leader_overlap_mm3':abs((back^leader).volume()),
        'outside_mark_and_vent_difference_mm2':surface_difference,
        'catch_alignment':catches,'physical_fit_tested':True,'physical_fit_confirmation_date':'2026-10-16',
        'physical_fit_notes':'Owner reports printed v2 locks onto the existing spacing_v3 front. No measured retention force, cycle count, creep or durability validation.',
        'PLA_deformation_validated':False,
        'validation_scope':'Rigid seated compatibility and ridge clearance only. Six fixed tabs require manual deformation; no insertion force, strain, creep or durability model.',
        'packages':{}}
    for node in ast.parse((BASE/'validate_and_package.py').read_text()).body:
        if isinstance(node,ast.FunctionDef) and node.name in {'el','meta','package'}:
            exec(compile(ast.Module(body=[node],type_ignores=[]),'package_helpers','exec'),globals())
    ET.register_namespace('',NS)
    with zipfile.ZipFile(SOURCE/'front_shell_A1.3mf') as archive:
        template={n:archive.read(n) for n in archive.namelist()}
        original_settings=json.loads(archive.read('Metadata/project_settings.config'))
    filename='continuous_ridge_back_A1.3mf'
    package(filename,'Roanoke continuous ridge back v2 - doubled tabs',[(printable,'White back with continuous ridge and six doubled fixed tabs',1,[128,128,0])],prime=False,brim=0.)
    with zipfile.ZipFile(H/filename) as archive: entries={n:archive.read(n) for n in archive.namelist()}
    model=ET.fromstring(entries['3D/3dmodel.model'])
    for item,(name,color) in zip(model.find('./{'+NS+'}resources/{'+NS+'}basematerials'),[('White PLA A1','#FFFFFFFF'),('Unused black PLA','#000000FF')]):
        item.set('name',name);item.set('displaycolor',color)
    for item in model.findall('{'+NS+'}metadata'):
        if item.get('name')=='Description': item.text='Continuous inset ridge, six fixed tabs with doubled 2.10 mm radial projection at existing V3 catches; upper boss trimmed for catch clearance. White project filament 1. Owner confirmed printed v2 locks onto the existing spacing_v3 front on 2026-10-16; deformation and durability remain unvalidated.'
    entries['3D/3dmodel.model']=ET.tostring(model,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(H/filename,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in entries.items(): archive.writestr(name,data)
    report['packages'][filename]['sha256']=sha(H/filename)
    config={'revision':'continuous ridge back v2 - doubled tab projection','front_shell':'existing printed spacing_v3, unchanged',
        'attachment':'six fixed tapered tabs integral with continuous inset ridge; manual shared cover/ridge deformation',
        'back_plate_thickness_mm':OUTSIDE-REAR,'back_plate_z_mm':[REAR,OUTSIDE],
        'ridge_thickness_mm':RIDGE_THICKNESS,'ridge_depth_mm':RIDGE_DEPTH,
        'ridge_outer_inset_from_outline_mm':WALL+GAP,'ridge_to_shell_inner_wall_clearance_mm':GAP,
        'ridge_continuity':'One uninterrupted ridge around available perimeter; terminates at the two edges of the existing 100 mm mouth; no bridge across tree opening.',
        'tab_count':6,'tab_width_mm':TAB_WIDTH,'tab_radial_engagement_mm':ENGAGEMENT,
        'previous_tab_projection_from_ridge_mm':PREVIOUS_PROJECTION,
        'tab_projection_from_ridge_mm':TAB_PROJECTION,'projection_multiplier':2.,
        'nose_beyond_shell_outer_surface_mm':ENGAGEMENT-WALL,
        'upper_catch_clearance_trim':{'max_z_for_outer_boss_mm':TAB_UPPER_CLEARANCE_Z,
            'radial_trim_limit_from_shell_outer_edge_mm':WALL+TAB_UPPER_RADIAL_CLEARANCE,
            'reason':'Longer unchanged ramp would intersect the top of the existing catch; remove only that boss wedge, retain continuous ridge/root.'},
        'tab_entry_ramp_z_mm':[52.5,54.],'tab_tangent_center_offset_from_clip_anchor_mm':8.,'tab_retaining_ramp_z_mm':[54.4,55.45],
        'tab_full_engagement_z_mm':[54.,54.4],'clips':params['clips'],
        'separate_moving_latches':False,'hinges':False,'spring_relief_cuts':False,
        'builder_mark':params['builder_mark'],'bottom_opening_width_mm':100.,'rear_vents_retained':8,
        'print_orientation':'outside face down; ridge and tabs up','printer':'Bambu Lab A1, 0.4 mm nozzle',
        'layer_height_mm':.2,'filament':'White PLA, project filament 1','support_enabled':False,
        'physical_fit_tested':True,'physical_fit_confirmation_date':'2026-10-16',
        'physical_fit_notes':'Owner reports printed v2 locks onto the existing spacing_v3 front. No measured retention force, cycle count, creep or durability validation.',
        'PLA_deformation_validated':False,
        'previous_v1_feedback':'User reports the original tab projection did not quite lock and requested doubling it; owner confirms printed v2 locks on the existing spacing_v3 front.'}
    (H/'parameters.json').write_text(json.dumps(config,indent=2)+'\n')
    (H/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    unchanged=all(sha(ROOT/p)==digest for p,digest in before.items())
    assert unchanged
    (H/'preservation_validation.json').write_text(json.dumps({'all_previous_files_unchanged':unchanged,'checked_file_count':len(before),'manifest':'preservation_before.json'},indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
