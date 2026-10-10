"""Check continuous white stars and two-layer windows in actual thinner-frame full-size G-code."""
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import zipfile

from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
package = Path(sys.argv[1])
profiles = json.loads((H / 'profiles.json').read_text())
crop = Polygon(profiles['outline'][0]['loops'][0])
windows = [Polygon(p['loops'][0]) for p in profiles['white_tube_sections']]
windows = [p for p in windows if crop.contains(p)]
assert len(windows) == 130
with zipfile.ZipFile(package) as archive:
    code = archive.read('Metadata/plate_1.gcode').decode()
    settings = json.loads(archive.read('Metadata/project_settings.config'))
# Bambu's global plate selector can differ from the explicit per-plate override.
# Verify the generated instructions, which are what the printer will execute.
assert re.search(r'^; curr_bed_type = Textured PEI Plate$', code, re.M)
assert float(settings['layer_height']) == float(settings['initial_layer_print_height']) == .2
assert str(settings['enable_support']) == '0'
assert str(settings['enable_prime_tower']) == '1'
assert settings['filament_settings_id'] == ['Generic PLA @BBL A1']*2
assert settings['flush_volumes_matrix'] == ['0', '300', '600', '0']
assert 'M190 S65' in code
full_layer_counts = [tuple(map(int, v)) for v in re.findall(r'^; layer num/total_layer_count: (\d+)/(\d+)$', code, re.M)]
full_z = [float(v) for v in re.findall(r'^; Z_HEIGHT: ([\d.]+)$', code, re.M)]
assert len(full_layer_counts) == 292 and full_layer_counts[-1] == (292, 292)
assert abs(max(full_z)-58.4) < 1e-6
header = '\n'.join(code.splitlines()[:100])
estimated_time = re.search(r'total estimated time: ([^\n]+)', header)
filament_grams = re.search(r'^; total filament weight \[g\] : (.+)$', header, re.M)
xy = [0., 0.]
layer = 0
tool = None
width = .42
relative_e = True
e_position = 0.
strokes = {}
layer_z = []
pending_z = None
for raw in code.splitlines():
    if raw.startswith('; layer num/total_layer_count:'):
        layer = int(raw.split(':')[1].strip().split('/')[0])
        if layer > 20:
            break
        assert pending_z is not None
        layer_z.append(pending_z)
    elif raw.startswith('; Z_HEIGHT:'):
        pending_z = float(raw.split(':')[1])
    elif raw.startswith('; LINE_WIDTH:'):
        width = float(raw.split(':')[1])
    line = raw.split(';')[0].strip()
    if not line:
        continue
    match = re.fullmatch(r'M620 S(\d+)A', line)
    if match:
        selected = int(match.group(1))
        if selected < 2:
            tool = selected
    if re.fullmatch(r'T[01]', line):
        tool = int(line[1:])
    if line == 'M83':
        relative_e = True
    elif line == 'M82':
        relative_e = False
    values = {key: float(value) for key, value in re.findall(r'([XYEIJ])(-?\d*\.?\d+)', line)}
    if line.startswith('G92'):
        e_position = values.get('E', e_position)
        continue
    command = line.split()[0]
    if command not in {'G0', 'G1', 'G2', 'G3'}:
        continue
    end = [values.get('X', xy[0]), values.get('Y', xy[1])]
    extrusion = values.get('E', 0.) if relative_e else values.get('E', e_position)-e_position
    if not relative_e:
        e_position = values.get('E', e_position)
    points = [xy, end]
    if command in {'G2', 'G3'} and ('I' in values or 'J' in values):
        center = [xy[0]+values.get('I', 0.), xy[1]+values.get('J', 0.)]
        radius = math.hypot(xy[0]-center[0], xy[1]-center[1])
        start = math.atan2(xy[1]-center[1], xy[0]-center[0])
        stop = math.atan2(end[1]-center[1], end[0]-center[0])
        sweep = (stop-start) % (2*math.pi) if command == 'G3' else -((start-stop) % (2*math.pi))
        count = max(2, math.ceil(abs(sweep)*radius/.1))
        points = [[center[0]+radius*math.cos(start+sweep*i/count),
                   center[1]+radius*math.sin(start+sweep*i/count)] for i in range(count+1)]
    if layer and tool in {0, 1} and extrusion > 0 and xy != end:
        # The sample is placed at (128,128); purging and the tower are elsewhere.
        path = LineString([(p[0]-128, p[1]-128) for p in points])
        if path.intersects(crop):
            # Extrusion beads have rounded ends; square line caps leave
            # artificial wedges at short hatching endpoints and corners.
            strokes.setdefault((layer, tool), []).append(path.buffer(width/2, cap_style=1))
    xy = end
coverage = {key: unary_union(value) for key, value in strokes.items()}
# On the bed-facing side, the complete star bands must be white, including
# the regions that used to form black outlines around the individual bulbs.
continuous_bands = []
for band in profiles['white_backing_bands']:
    central_opening = max(band['loops'][1:], key=lambda loop: Polygon(loop).area)
    continuous_bands.append(Polygon(band['loops'][0], [central_opening]))
face_core = unary_union(continuous_bands).intersection(crop).buffer(-.45)
face_checks = {}
for number in [1, 2]:
    white = coverage[(number, 0)].intersection(face_core).area / face_core.area
    black = coverage[(number, 1)].intersection(face_core).area
    # Buffered centerlines approximate bead coverage; normal solid hatching
    # leaves small gaps in this approximation. Missing bulb-size patches or
    # any remaining black keylines would fail these independent checks.
    assert white > .95, (number, white)
    assert black < .01, (number, black)
    face_checks[str(number)] = {'white_coverage': white, 'black_area_mm2': black}
combined_white = coverage[(1, 0)].union(coverage[(2, 0)])
checks = []
for index, window in enumerate(windows, 1):
    core = window.buffer(-.45)
    assert not core.is_empty
    white_layers = []
    black_layers = []
    fills = {}
    for number in range(1, 21):
        for material, present in [(0, white_layers), (1, black_layers)]:
            value = coverage.get((number, material))
            area = value.intersection(core).area if value is not None else 0.
            if area > .01:
                present.append(number)
            if material == 0 and number <= 2:
                fills[str(number)] = area/core.area
    assert white_layers == [1, 2], (index, white_layers)
    assert not black_layers, (index, black_layers)
    assert min(fills.values()) > .9, (index, fills)
    assert fills['2'] > .99, (index, fills)
    combined = combined_white.intersection(core).area/core.area
    assert combined > .999, (index, combined)
    checks.append({'window': index, 'white_extrusion_layers': white_layers,
                   'black_extrusion_layers': black_layers, 'inner_core_coverage': fills,
                   'combined_two_layer_core_coverage': combined})
assert len(layer_z) == 20 and abs(max(layer_z)-4.) < 1e-6
report = {'status': 'passed', 'slicer': 'Bambu Studio 02.05.00.66',
          'sliced_package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
          'gcode_sha256': hashlib.sha256(code.encode()).hexdigest(),
          'printer': 'Bambu Lab A1, 0.4 mm nozzle', 'layer_height_mm': .2,
          'audited_layers': 20, 'audited_max_z_mm': 4., 'full_layers': len(full_layer_counts), 'full_max_z_mm': max(full_z), 'build_plate': 'Textured PEI Plate',
          'bed_temperature_c': 65, 'filament_profiles': settings['filament_settings_id'],
          'declared_preview_colors': settings['filament_colour'],
          'requested_physical_filaments': {'A1': 'white', 'A2': 'black'},
          'continuous_white_stars': 3, 'visible_bulb_outlines': 0,
          'continuous_white_face_toolpath_checks': face_checks,
          'diffuser_thickness_mm': .4, 'window_toolpath_checks': checks,
          'coverage_scope': 'Extruded paths buffered by declared line width with round bead ends, clipped to window interiors inset 0.45 mm; arcs sampled every 0.1 mm. Coverage is a bead footprint approximation, not a physical airtightness test.',
          'source_front_sha256': hashlib.sha256((H / 'front_shell_A1.3mf').read_bytes()).hexdigest(),
          'native_estimated_time': estimated_time.group(1) if estimated_time else None,
          'native_filament_grams': filament_grams.group(1) if filament_grams else None,
          'print_started': False, 'revised_proportions_physically_tested': False}
(H / 'slicer_validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
