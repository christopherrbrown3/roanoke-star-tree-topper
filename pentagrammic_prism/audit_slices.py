"""Record local Bambu Studio slicing evidence without committing G-code."""
import hashlib
import json
from pathlib import Path
import re

H = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(package, gcode):
    config = {}
    header = []
    layer_count = 0
    with gcode.open() as stream:
        for line in stream:
            if line.startswith('; ') and ' = ' in line:
                key, _, value = line[2:].partition(' = ')
                config[key] = value.strip()
            if line.startswith('; ') and len(header) < 12:
                header.append(line.strip())
            if line.startswith('; CHANGE_LAYER'):
                layer_count += 1
    text = '\n'.join(header)
    time = re.search(r'total estimated time: ([^\n]+)', text).group(1)
    weights = [float(n) for n in re.search(r'total filament weight \[g\] : ([^\n]+)', text).group(1).split(',')]
    layers = int(re.search(r'total layer number: (\d+)', text).group(1))
    expected = {'curr_bed_type': 'Textured PEI Plate', 'layer_height': '0.2',
                'nozzle_diameter': '0.4', 'wall_loops': '3', 'wall_generator': 'arachne'}
    for key, value in expected.items():
        assert config[key] == value, (key, config.get(key))
    return {'status': 'sliced_successfully', 'package_sha256': sha(package),
            'gcode_sha256': sha(gcode), 'Bambu_Studio_version': '02.05.00.66',
            'total_estimated_time': time, 'filament_weight_g': weights,
            'total_filament_g': round(sum(weights), 2), 'layers': layers,
            'max_z_mm': float(re.search(r'max_z_height: ([^\n]+)', text).group(1)),
            'settings': {k: config[k] for k in [*expected, 'printer_model', 'enable_support',
                'support_on_build_plate_only', 'support_type', 'brim_type', 'brim_width',
                'enable_prime_tower', 'filament_colour', 'filament_type']},
            'review_scope': 'Completed GUI slice and full preview; exported G-code header/configuration audited.',
            'print_sent': False, 'physical_print_tested': False}

if __name__ == '__main__':
    report = {'two_color': audit(H/'roanoke_star_prism_A1.3mf', H/'slicer_check/two_color.gcode')}
    report['two_color']['GUI_breakdown_g'] = {'model': 118.95, 'support': 15.58, 'purge': 459.97, 'tower': 66.99}
    report['two_color']['GUI_filament_changes'] = 910
    report['single_color'] = {'status': 'geometry_and_package_validated; GUI_slice_pending'}
    (H/'slicer_validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
