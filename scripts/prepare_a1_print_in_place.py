"""Generate real colored solids for a single face-down A1/AMS lite print.

Photo-based outline remains unverified. Section counts and mirrored joints are
explicit manufacturing approximations, not a recovered neon shop schedule.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon
from shapely.ops import substring, unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'print_in_place'
OUT.mkdir(exist_ok=True)
(OUT/'previews').mkdir(exist_ok=True)
source = ROOT/'research/photographic_paths.json'
raw_paths = np.asarray(json.loads(source.read_text())['six_paths_mm'], dtype=float)

# A separate photo trace for each contour allowed the paired rows to converge,
# especially at the lower side notches. Derive every path from the SAME ten
# edge lines instead. Offset adjacent lines and intersect them at each corner;
# this preserves exact parallelism through concave as well as convex vertices.
master = raw_paths[0]
master_edges = np.roll(master, -1, axis=0)-master
normals = np.column_stack((master_edges[:, 1], -master_edges[:, 0]))
normals /= np.linalg.norm(normals, axis=1)[:, None]  # inward, clockwise outline
constants = np.sum(normals*master, axis=1)
vertex_offset_vectors = np.asarray([
    np.linalg.solve(np.asarray([normals[i-1], normals[i]]), [1., 1.])
    for i in range(len(master))
])
# Choose one normal offset per path by least-squares distance to its prior ten
# vertices. This is a model regularization, not a new physical measurement.
offsets = [float(np.sum(vertex_offset_vectors*(p-master)) /
                 np.sum(vertex_offset_vectors**2)) for p in raw_paths]
assert abs(offsets[0]) < 1e-12 and np.all(np.diff(offsets) > 1.8)
paths = [(master+d*vertex_offset_vectors).tolist() for d in offsets]
for points in paths:
    assert Polygon(points).is_valid

def headings(points):
    e = np.roll(points, -1, axis=0)-points
    return np.degrees(np.arctan2(e[:, 1], e[:, 0]))

parallel_error = max(float(np.max(np.abs(headings(np.asarray(p))-headings(master))))
                     for p in paths)
normal_error = max(float(np.max(np.abs(np.sum(normals*np.asarray(p), axis=1)-constants-d)))
                   for p, d in zip(paths, offsets))
assert parallel_error < 1e-10 and normal_error < 1e-10
assert all(np.allclose(np.asarray(p)*[-1, 1], np.asarray(p)[[0,9,8,7,6,5,4,3,2,1]], atol=1e-10)
           for p in paths)
parallel_report = {
    'method':'Exact inward offsets of the outer candidate edge lines; corner vertices are adjacent line intersections. Each distance minimizes squared displacement from the previous ten path vertices.',
    'offsets_from_outer_path_mm':offsets,
    'adjacent_centerline_normal_spacing_mm':np.diff(offsets).tolist(),
    'adjacent_clear_tube_spacing_mm':(np.diff(offsets)-1.8).tolist(),
    'maximum_corresponding_edge_angle_error_deg':parallel_error,
    'maximum_normal_offset_error_mm':normal_error,
    'previous_pair_max_edge_angle_errors_deg':[
        float(np.max(np.abs(headings(raw_paths[i])-headings(raw_paths[i+1]))))
        for i in [0,2,4]],
    'maximum_vertex_displacement_per_path_mm':[
        float(np.max(np.linalg.norm(np.asarray(p)-q, axis=1)))
        for p,q in zip(paths,raw_paths)],
    'scope':'Parallelism is verified for this model. Outer candidate angles, nested offsets and landmark fidelity remain unverified against a measured elevation.',
}
outline = Polygon(paths[0]).buffer(2.2,quad_segs=16)
profiles = {}

def put(name, geom):
    geom = geom.buffer(0)
    polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    result = []
    for p in polys:
        assert p.is_valid and p.area > 0
        v,f = trimesh.creation.triangulate_polygon(p,engine='earcut')
        result.append({'v':v.tolist(),'f':f.tolist(),
                       'loops':[list(p.exterior.coords)[:-1]]+
                               [list(h.coords)[:-1] for h in p.interiors]})
    profiles[name] = result

put('outline',outline)
tube_width = 1.8
dark_gap = 1.2
# Closest photographic reference shows approximately four pieces on the outer
# arm. Other counts and transfer to unseen rows remain stated approximations.
fractions_by_path = [[.25,.50,.75],[.25,.50,.75],
                     [.25,.50,.75],[1/3,2/3],[.5],[.5]]
segments = []
schedule = []
for k,points in enumerate(paths):
    p = np.asarray(points)
    edge_lengths = np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1)
    cumulative = np.r_[0,np.cumsum(edge_lengths)]
    perimeter = float(cumulative[-1])
    cuts = []
    for edge,length in enumerate(edge_lengths):
        # Mirror the same joint positions across the vertical axis, rather than
        # deriving asymmetry from an oblique photograph.
        frac = fractions_by_path[k]
        if edge >= 5: frac = [1-x for x in reversed(frac)]
        for q in frac:
            cuts.append(float(cumulative[edge]+q*length))
        schedule.append({'path':k+1,'edge_clockwise':edge+1,
                         'fractions':frac,'length_mm':float(length),
                         'status':'photo-informed approximation; not archival coordinates'})
    cuts.sort()
    twice = LineString(points+points+[points[0]])
    half_cut = (dark_gap+tube_width)/2
    for j,a in enumerate(cuts):
        b = cuts[(j+1)%len(cuts)] + (perimeter if j == len(cuts)-1 else 0)
        line = substring(twice,a+half_cut,b-half_cut)
        assert line.length > 4
        shape = line.buffer(tube_width/2,quad_segs=10,cap_style=1,join_style=1)
        assert shape.geom_type == 'Polygon' and shape.is_valid
        segments.append(shape)

white = unary_union(segments)
assert white.geom_type == 'MultiPolygon' and len(white.geoms) == len(segments)
assert white.difference(outline).area < 1e-8
put('white_tube_sections',white)
mount_foot = Polygon([(-19.4,-32),(19.4,-32),(13.4,48),(-13.4,48)])
assert mount_foot.difference(outline).area < 1e-8
report = {
    'date':'2026-09-13','target_printer':'Bambu Lab A1','ams_lite':True,
    'nozzle_mm':.4,'layer_height_mm':.2,'assembly_required':False,
    'orientation':'front face on the bed; integral mount grows upward',
    'tube_width_mm':tube_width,'tube_inlay_depth_mm':1.0,'straight_run_dark_gap_mm':dark_gap,
    'visible_tube_sections':len(segments),
    'sections_per_path':[10*len(x) for x in fractions_by_path],
    'body_thickness_mm':4.0,'outline_bounds_mm':list(outline.bounds),
    'minimum_tube_to_outline_mm':white.distance(outline.boundary),
    'minimum_segment_to_segment_mm':min(a.distance(b) for i,a in enumerate(segments) for b in segments[i+1:]),
    'white_front_area_mm2':white.area,'outline_area_mm2':outline.area,
    'mount':{'length_mm':80,'lower_circular_clearance_diameter_mm':34,
             'upper_circular_clearance_diameter_mm':22,'minimum_wall_mm':2.4,
             'axis_depth_mm':23.4,'roof_angle_deg':45,'tie_hole_diagonal_mm':5,
             'y_openings_mm':[-32,48],'front_projection_outside_star_mm2':0},
    'source_paths':'research/photographic_paths.json',
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'six_paths_mm':paths,
    'parallel_path_correction':parallel_report,
    'outline_verified_against_survey':False,
    'tube_joint_schedule_verified':False,
    'joint_evidence':'research/tube_joint_observations.json and research/TUBE_LAYOUT.md',
    'joint_limitations':'Visible interruptions may include supports. Image-space positions and mirrored/repeated transfer are approximate. No exact fabrication schedule was found.',
    'joint_schedule':schedule,
}
(OUT/'profile_measurements.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'scripts/a1_topper_profiles.json').write_text(json.dumps(profiles))
print(json.dumps({k:v for k,v in report.items() if k!='joint_schedule'},indent=2))
