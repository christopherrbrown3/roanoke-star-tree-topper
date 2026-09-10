#!/usr/bin/env python3

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union
import trimesh


ROOT = Path("/Users/chris/Codex Projects/roanoke-star-tree-topper")
MODEL_DIR = ROOT / "models"
REVIEW_DIR = ROOT / "review"

OUT_STAR_STL = MODEL_DIR / "mill_mountain_star_topper_star_white.stl"
OUT_SCAFFOLD_STL = MODEL_DIR / "mill_mountain_star_topper_scaffold_dark.stl"
OUT_ASSEMBLY_STL = MODEL_DIR / "mill_mountain_star_topper_assembly.stl"
OUT_PREVIEW_FRONT = REVIEW_DIR / "mill_mountain_star_topper_front.png"
OUT_PREVIEW_SIDE = REVIEW_DIR / "mill_mountain_star_topper_side.png"
OUT_REPORT = REVIEW_DIR / "mill_mountain_star_topper_review.txt"


# Global sizing tuned to fit a Bambu A1 bed safely.
PLANAR_SCALE = 0.88

# Star silhouette tuned against the frontal reference photo.
OUTER_RADIUS = 126.0
STAR_SCALES = (1.00, 0.77, 0.54)

# Landmark-specific outer silhouette traced from the strongest frontal references.
BASE_STAR_POINTS = [
    (0.0, 126.0),
    (21.7, 37.3),
    (122.5, 37.3),
    (32.7, -15.3),
    (64.8, -102.0),
    (0.0, -40.7),
    (-64.8, -102.0),
    (-32.7, -15.3),
    (-122.5, 37.3),
    (-21.7, 37.3),
]

# White star body.
VISIBLE_RING_WIDTH = 5.7
STAR_BODY_DEPTH = (0.0, 2.9)
BULB_RELIEF_DEPTH = (-0.45, 0.35)
BULB_SPACING = 7.9
BULB_RADIUS = 0.44
BULB_ROW_FACTORS = (0.24, 0.68)
BULB_ROW_PHASES = (0.0, 3.9)

# Hidden structural backplate, intended for a matte-black filament.
BACKPLATE_EDGE_INSET = 1.25
BACKPLATE_DEPTH = (2.9, 4.5)

# Rear mount integrated into the backplate. The upper depth intentionally overlaps
# the socket body so the dark rear part exports as one connected solid.
PLATE_DEPTH = (4.5, 14.8)
LOWER_STEM_TOP = -61.0
LOWER_STEM_BOTTOM = -86.0

# Mounting socket integrated into the scaffold.
SOCKET_BOTTOM_Z = -92.0
SOCKET_TOP_Z = -36.0
SOCKET_BACK_SHIFT = 25.0
SOCKET_OUTER_RX_BOTTOM = 12.5
SOCKET_OUTER_RY_BOTTOM = 11.8
SOCKET_OUTER_RX_TOP = 8.2
SOCKET_OUTER_RY_TOP = 8.1
SOCKET_WALL = 2.4
SOCKET_SLIT_DEG = 62.0
SOCKET_SECTIONS = 18
# Hidden ribs bridge the plate into the socket so the cone can't detach as a
# separate shell in the AMS dark body.
SOCKET_RIB_DEPTH = (9.8, 17.0)


def flatten_polygons(geom):
    if geom.is_empty:
        return
    if isinstance(geom, Polygon):
        yield geom
    elif isinstance(geom, (MultiPolygon, GeometryCollection)):
        for sub in geom.geoms:
            yield from flatten_polygons(sub)
    else:
        raise TypeError(f"Unsupported geometry: {geom.geom_type}")


def star_points(scale: float) -> list[tuple[float, float]]:
    return [(x * scale, z * scale) for x, z in BASE_STAR_POINTS]


def star_centerline(scale: float) -> LineString:
    pts = star_points(scale)
    return LineString(pts + [pts[0]])


def star_polygon(scale: float) -> Polygon:
    return Polygon(star_points(scale))


def buffer_line_segments(segments: list[tuple[tuple[float, float], tuple[float, float]]], width: float):
    buffered = []
    for a, b in segments:
        buffered.append(LineString([a, b]).buffer(width / 2.0, cap_style=2, join_style=2, mitre_limit=4.0))
    return unary_union(buffered).buffer(0)


def star_ring(scale: float, width: float) -> Polygon:
    outer = star_polygon(scale)
    inner = outer.buffer(-width, join_style=2, mitre_limit=20.0)
    if inner.is_empty:
        return outer
    return outer.difference(inner)


def build_visible_star_geom():
    return GeometryCollection([star_ring(scale, VISIBLE_RING_WIDTH) for scale in STAR_SCALES])


def build_hidden_backer_geom():
    backplate = star_polygon(STAR_SCALES[0]).buffer(-BACKPLATE_EDGE_INSET, join_style=2, mitre_limit=20.0)
    return GeometryCollection([backplate.buffer(0)])


def sample_closed_line(line: LineString, spacing: float, offset: float) -> list[tuple[float, float]]:
    length = line.length
    points = []
    d = offset
    while d < length:
        p = line.interpolate(d)
        points.append((p.x, p.y))
        d += spacing
    return points


def bulb_tracks(scale: float) -> list[tuple[LineString, float]]:
    outer = star_polygon(scale)
    tracks = []
    for factor, phase in zip(BULB_ROW_FACTORS, BULB_ROW_PHASES):
        inset = outer.buffer(-VISIBLE_RING_WIDTH * factor, join_style=2, mitre_limit=20.0)
        if inset.is_empty:
            continue
        tracks.append((LineString(list(inset.exterior.coords)), phase))
    if not tracks:
        tracks.append((star_centerline(scale), 0.0))
    return tracks


def build_bulb_geom():
    bulbs = []
    for scale in STAR_SCALES:
        for track, phase in bulb_tracks(scale):
            for x, z in sample_closed_line(track, BULB_SPACING, phase):
                bulbs.append(Point(x, z).buffer(BULB_RADIUS, resolution=8))
    return unary_union(bulbs)


def build_scaffold_geom():
    return GeometryCollection([])


def build_mount_plate_geom():
    core = box(-3.6, LOWER_STEM_BOTTOM, 3.6, -56.0)
    lower_tie = box(-6.4, -60.0, 6.4, -56.0)
    upper_flare = Polygon([(-3.6, -56.0), (-12.0, -49.0), (12.0, -49.0), (3.6, -56.0)])
    return unary_union([core, lower_tie, upper_flare])


def polygon_mesh(geom, y0: float, y1: float):
    meshes = []
    depth = y1 - y0
    for poly in flatten_polygons(geom):
        mesh = trimesh.creation.extrude_polygon(poly, depth)
        verts = mesh.vertices.copy()
        mesh.vertices = np.column_stack((verts[:, 0], verts[:, 2] + y0, verts[:, 1]))
        mesh.fix_normals()
        meshes.append(mesh)
    if len(meshes) == 1:
        return meshes[0]
    merged = trimesh.util.concatenate(meshes)
    merged.fix_normals()
    return merged


def mesh_from_triangles(triangles):
    vertices = []
    faces = []
    for a, b, c in triangles:
        base = len(vertices)
        vertices.extend([a, b, c])
        faces.append([base, base + 1, base + 2])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    return mesh


def tri_normal(a, b, c):
    ab = b - a
    ac = c - a
    n = np.cross(ab, ac)
    norm = np.linalg.norm(n)
    return n / norm if norm else np.zeros(3)


def add_triangle(tris, a, b, c):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    if np.linalg.norm(np.cross(b - a, c - a)) > 1e-9:
        tris.append((a, b, c))


def section_loop(rx_outer, ry_outer, wall, slit_deg, y_center):
    slit_half = math.radians(slit_deg / 2.0)
    outer_start = math.pi / 2.0 + slit_half
    outer_end = math.pi / 2.0 - slit_half + 2.0 * math.pi
    outer_angles = np.linspace(outer_start, outer_end, 56)

    inner_rx = rx_outer - wall
    inner_ry = ry_outer - wall
    inner_start = math.pi / 2.0 - slit_half
    inner_end = math.pi / 2.0 + slit_half - 2.0 * math.pi
    inner_angles = np.linspace(inner_start, inner_end, 56)

    outer = [(rx_outer * math.cos(t), y_center + ry_outer * math.sin(t)) for t in outer_angles]
    inner = [(inner_rx * math.cos(t), y_center + inner_ry * math.sin(t)) for t in inner_angles]
    return outer + inner


def triangulate_loop_2d(loop):
    poly = Polygon(loop)
    mesh = trimesh.creation.triangulate_polygon(poly)
    vertices_2d, faces = mesh
    return vertices_2d, faces


def build_socket_mesh():
    sections = []
    z_values = np.linspace(SOCKET_BOTTOM_Z, SOCKET_TOP_Z, SOCKET_SECTIONS)
    for z in z_values:
        t = (z - SOCKET_BOTTOM_Z) / (SOCKET_TOP_Z - SOCKET_BOTTOM_Z)
        rx = SOCKET_OUTER_RX_BOTTOM + (SOCKET_OUTER_RX_TOP - SOCKET_OUTER_RX_BOTTOM) * t
        ry = SOCKET_OUTER_RY_BOTTOM + (SOCKET_OUTER_RY_TOP - SOCKET_OUTER_RY_BOTTOM) * t
        loop = section_loop(rx, ry, SOCKET_WALL, SOCKET_SLIT_DEG, SOCKET_BACK_SHIFT)
        sections.append([np.array([x, y, z]) for x, y in loop])

    tris = []
    for a_sec, b_sec in zip(sections[:-1], sections[1:]):
        n = len(a_sec)
        for i in range(n):
            a = a_sec[i]
            b = a_sec[(i + 1) % n]
            c = b_sec[(i + 1) % n]
            d = b_sec[i]
            add_triangle(tris, a, b, c)
            add_triangle(tris, a, c, d)

    top_verts_2d, top_faces = triangulate_loop_2d([(p[0], p[1]) for p in sections[-1]])
    for face in top_faces:
        a = np.array([top_verts_2d[face[0]][0], top_verts_2d[face[0]][1], SOCKET_TOP_Z])
        b = np.array([top_verts_2d[face[1]][0], top_verts_2d[face[1]][1], SOCKET_TOP_Z])
        c = np.array([top_verts_2d[face[2]][0], top_verts_2d[face[2]][1], SOCKET_TOP_Z])
        add_triangle(tris, a, b, c)

    bottom_verts_2d, bottom_faces = triangulate_loop_2d([(p[0], p[1]) for p in sections[0]])
    for face in bottom_faces:
        a = np.array([bottom_verts_2d[face[0]][0], bottom_verts_2d[face[0]][1], SOCKET_BOTTOM_Z])
        b = np.array([bottom_verts_2d[face[1]][0], bottom_verts_2d[face[1]][1], SOCKET_BOTTOM_Z])
        c = np.array([bottom_verts_2d[face[2]][0], bottom_verts_2d[face[2]][1], SOCKET_BOTTOM_Z])
        add_triangle(tris, c, b, a)

    return mesh_from_triangles(tris)


def build_socket_ribs_mesh():
    left_rib = box(-5.8, SOCKET_BOTTOM_Z + 10.0, -3.4, SOCKET_TOP_Z - 8.0)
    right_rib = affinity.scale(left_rib, xfact=-1, yfact=1, origin=(0, 0))
    return polygon_mesh(unary_union([left_rib, right_rib]), *SOCKET_RIB_DEPTH)


def scale_mesh_planar(mesh: trimesh.Trimesh, factor: float):
    scaled = mesh.copy()
    scaled.apply_transform(
        np.array(
            [
                [factor, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, factor, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
    )
    return scaled


def draw_projection(polys, out_path: Path, size=(1800, 1800), background=(248, 245, 238)):
    all_points = []
    for _, _, geom in polys:
        for poly in flatten_polygons(geom):
            all_points.extend(list(poly.exterior.coords))
            for hole in poly.interiors:
                all_points.extend(list(hole.coords))

    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    pad = 40
    sx = (size[0] - 2 * pad) / (max_x - min_x)
    sy = (size[1] - 2 * pad) / (max_y - min_y)
    scale = min(sx, sy)

    def tx(pt):
        x, y = pt
        px = pad + (x - min_x) * scale
        py = size[1] - pad - (y - min_y) * scale
        return (px, py)

    img = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(img)
    for fill, outline, geom in polys:
        for poly in flatten_polygons(geom):
            draw.polygon([tx(p) for p in poly.exterior.coords], fill=fill, outline=outline)
            for hole in poly.interiors:
                draw.line([tx(p) for p in hole.coords], fill=outline, width=1)
    img.save(out_path)


def validate_mesh(mesh: trimesh.Trimesh):
    return {
        "watertight": mesh.is_watertight,
        "is_volume": mesh.is_volume,
        "faces": len(mesh.faces),
        "extents": mesh.extents.tolist(),
    }


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    visible_star = build_visible_star_geom()
    hidden_backer = build_hidden_backer_geom()
    bulb_geom = build_bulb_geom()
    scaffold_geom = build_scaffold_geom()
    plate_geom = build_mount_plate_geom()

    # White star part.
    star_mesh_parts = [
        polygon_mesh(visible_star, *STAR_BODY_DEPTH),
        polygon_mesh(bulb_geom, *BULB_RELIEF_DEPTH),
    ]
    for mesh in star_mesh_parts:
        mesh.fix_normals()
    star_mesh = trimesh.boolean.union(star_mesh_parts, engine="manifold")
    star_mesh = scale_mesh_planar(star_mesh, PLANAR_SCALE)
    star_mesh.export(OUT_STAR_STL)

    # Dark backplate part.
    scaffold_mesh_parts = [
        polygon_mesh(hidden_backer, *BACKPLATE_DEPTH),
        polygon_mesh(plate_geom, *PLATE_DEPTH),
        build_socket_mesh(),
        build_socket_ribs_mesh(),
    ]
    for mesh in scaffold_mesh_parts:
        mesh.fix_normals()
    scaffold_mesh = trimesh.boolean.union(scaffold_mesh_parts, engine="manifold")
    scaffold_mesh = scale_mesh_planar(scaffold_mesh, PLANAR_SCALE)
    scaffold_mesh.export(OUT_SCAFFOLD_STL)

    # Single-color fallback assembly. Nudge the rear body forward very slightly so the
    # boolean has real overlap instead of a coplanar seam at the star/backplate interface.
    assembly_star = star_mesh.copy()
    assembly_scaffold = scaffold_mesh.copy()
    assembly_scaffold.apply_translation([0.0, -0.05, 0.0])
    assembly_mesh = trimesh.boolean.union([assembly_star, assembly_scaffold], engine="manifold")
    assembly_mesh.export(OUT_ASSEMBLY_STL)

    # Previews: scaffold first, star second.
    preview_star = affinity.scale(visible_star, xfact=PLANAR_SCALE, yfact=PLANAR_SCALE, origin=(0, 0))
    preview_bulbs = affinity.scale(bulb_geom, xfact=PLANAR_SCALE, yfact=PLANAR_SCALE, origin=(0, 0))
    preview_hidden_backer = affinity.scale(hidden_backer, xfact=PLANAR_SCALE, yfact=PLANAR_SCALE, origin=(0, 0))

    draw_projection(
        [
            ((34, 44, 36), (18, 22, 18), preview_hidden_backer),
            ((244, 244, 242), (175, 175, 170), preview_star),
            ((222, 222, 218), (196, 196, 190), preview_bulbs),
        ],
        OUT_PREVIEW_FRONT,
    )

    side_geom = unary_union(
        [
            box(BULB_RELIEF_DEPTH[0], -114.0 * PLANAR_SCALE, STAR_BODY_DEPTH[1], 132.0 * PLANAR_SCALE),
            box(BACKPLATE_DEPTH[0], -114.0 * PLANAR_SCALE, BACKPLATE_DEPTH[1], 132.0 * PLANAR_SCALE),
            box(PLATE_DEPTH[0], SOCKET_BOTTOM_Z * PLANAR_SCALE, PLATE_DEPTH[1], SOCKET_TOP_Z * PLANAR_SCALE),
        ]
    )
    draw_projection(
        [((214, 225, 240), (30, 44, 71), side_geom)],
        OUT_PREVIEW_SIDE,
        size=(1400, 1800),
    )

    star_info = validate_mesh(star_mesh)
    scaffold_info = validate_mesh(scaffold_mesh)
    assembly_info = validate_mesh(assembly_mesh)

    report = f"""Mill Mountain Star Tree Topper Review
====================================

Outputs
- White star STL: {OUT_STAR_STL}
- Dark scaffold STL: {OUT_SCAFFOLD_STL}
- Single-color assembly STL: {OUT_ASSEMBLY_STL}
- Front preview: {OUT_PREVIEW_FRONT}
- Side preview: {OUT_PREVIEW_SIDE}

Design revisions from feedback
- Split into separate AMS-friendly color bodies.
- Rebuilt the star rings from a landmark-specific traced silhouette instead of a generic regular-star formula.
- Retuned the nested-star spacing against the frontal reference photos for a clearer outer/middle/inner step.
- Removed the visible scaffold and replaced it with a recessed black backplate that captures all three rings structurally.
- Added dual-row bulb texture so each ring reads more like paired light runs instead of a single dotted track.

White star body
- Watertight: {star_info['watertight']}
- Volume mesh: {star_info['is_volume']}
- Face count: {star_info['faces']}
- Extents (mm): {star_info['extents']}

Dark backplate body
- Watertight: {scaffold_info['watertight']}
- Volume mesh: {scaffold_info['is_volume']}
- Face count: {scaffold_info['faces']}
- Extents (mm): {scaffold_info['extents']}

Combined single-color assembly
- Watertight: {assembly_info['watertight']}
- Volume mesh: {assembly_info['is_volume']}
- Face count: {assembly_info['faces']}
- Extents (mm): {assembly_info['extents']}

Accuracy notes
- The final star ring ratios are tuned to approximately {STAR_SCALES[0]:.2f} / {STAR_SCALES[1]:.2f} / {STAR_SCALES[2]:.2f} from outer to inner.
- The white star remains the dominant front-facing geometry.
- The black backplate is inset so it reads as darkness behind the star rather than as a visible plaque.

Structural review
- Main remaining weak points are still the top apex and the two outer side points of the visible star.
- Those points are now backed by a continuous masked backplate, which captures the inner ring and supports all three layers.
- The mount load is distributed through the backplate and lower plate before reaching the visible white star.

Bambu A1 print notes
- Use the white star STL as the white AMS body.
- Use the scaffold STL as the black AMS backplate body.
- Import both STLs together into Bambu Studio as one multi-part object.
- If you prefer a single-color print, use the assembly STL.
- Recommended nozzle: 0.4 mm.
- Recommended layer height: 0.20 mm.
- Recommended perimeters: 4.
- Recommended infill: 10 to 15 percent gyroid.
- Supports should be limited mainly to the rear socket zone.

If the first print shows too much flex
- Increase only the hidden backplate thickness or lower mount depth first.
- Do not thicken the visible white ring lines unless appearance clearly demands it.
"""
    OUT_REPORT.write_text(report)
    print(report)


if __name__ == "__main__":
    main()
