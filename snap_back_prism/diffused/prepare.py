"""Prepare a separate diffused face and a full-scale 64 x 44 mm print sample."""
import hashlib
import json
from pathlib import Path

import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
SOURCE = H.parent / 'two_dot'
CONSTRUCTION = H / 'construction'
CONSTRUCTION.mkdir(parents=True, exist_ok=True)
PROFILES = ROOT / 'scripts/a1_topper_profiles.json'
S = json.loads(PROFILES.read_text())
bands = unary_union([Polygon(p['loops'][0], p['loops'][1:]) for p in S['white_backing_bands']])
windows = unary_union([Polygon(p['loops'][0]) for p in S['white_tube_sections']])
outline = Polygon(S['outline'][0]['loops'][0])
# Keep each original band's outside and central star opening, while filling
# the 130 smaller holes that originally contained the bulb's black outline.
continuous_bands = []
for profile in S['white_backing_bands']:
    holes = [Polygon(loop) for loop in profile['loops'][1:]]
    central_star = max(holes, key=lambda polygon: polygon.area)
    continuous_bands.append(Polygon(profile['loops'][0], [central_star.exterior.coords]))
continuous_bands = unary_union(continuous_bands)
assert len(continuous_bands.geoms) == 3
assert all(len(p.interiors) == 1 for p in continuous_bands.geoms)
assert windows.difference(continuous_bands).area < 1e-6
replaced_outlines = continuous_bands.difference(unary_union([bands, windows]))
skin = 0.4
sample = box(-30, -20, 30, 20)
border = box(-32, -22, 32, 22).difference(sample)
assert outline.contains(sample)


def extrude(shape, z0, z1, name):
    polygons = [shape] if shape.geom_type == 'Polygon' else list(shape.geoms)
    meshes = []
    for polygon in polygons:
        if polygon.area < 1e-8:
            continue
        mesh = trimesh.creation.extrude_polygon(polygon, z1-z0, engine='earcut')
        mesh.apply_translation([0, 0, z0])
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        meshes.append(mesh)
    trimesh.util.concatenate(meshes).export(CONSTRUCTION / (name+'.stl'))


extrude(continuous_bands, 0, skin, 'white_skin_and_bands')
extrude(continuous_bands.difference(windows), skin, 1, 'white_upper_bands')
extrude(continuous_bands, 0, 1, 'continuous_white_face_region')
extrude(sample, -0.1, 4, 'sample_crop')
extrude(border, 0, 4, 'sample_handling_border')
parameters = json.loads((SOURCE / 'parameters.json').read_text())
parameters['connector_test_filament'] = parameters.pop('test_filament')
parameters.update(
    revision='three continuous white stars with hidden two-layer bulb windows',
    unlit_face={'continuous_white_stars': 3, 'visible_bulb_outlines': 0,
                'white_surround_thickness_mm': 1.0,
                'black_outline_area_replaced_mm2': replaced_outlines.area,
                'black_baffles_retained_from_z_mm': 1.0},
    face_colours={'white': 'AMS A1', 'black': 'AMS A2'},
    diffuser={'thickness_mm': skin, 'layer_height_mm': 0.2, 'printed_layers': 2,
              'position': 'flush front surface, Z 0 to 0.4 mm', 'window_count': 130,
              'physical_light_transmission_tested': False},
    print_sample={'size_mm': [64, 44, 4], 'pattern_crop_xy_mm': [-30, -20, 30, 20],
                  'handling_border_mm': 2, 'scale': 1, 'complete_windows':
                  sum(sample.contains(p) for p in windows.geoms)},
    source_profile_sha256=hashlib.sha256(PROFILES.read_bytes()).hexdigest(),
    source_black_mesh_sha256=hashlib.sha256((SOURCE / 'body_navy.stl').read_bytes()).hexdigest(),
    source_back_mesh_sha256=hashlib.sha256((SOURCE / 'snap_back.stl').read_bytes()).hexdigest(),
)
(H / 'parameters.json').write_text(json.dumps(parameters, indent=2)+'\n')
print('Prepared three continuous white stars, 130 hidden 0.4 mm windows, and a 64 x 44 x 4 mm sample.')
