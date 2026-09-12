"""Report polygon angles without changing the unverified landmark reconstruction."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/accurate_light_paths.json'
OUT = ROOT / 'research'
NAMES = ['Top tip', 'Upper-right notch', 'Right tip', 'Lower-right notch',
         'Lower-right tip', 'Bottom notch', 'Lower-left tip', 'Lower-left notch',
         'Left tip', 'Upper-left notch']

def angle_rows(points, path_number):
    area2 = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
    winding = 1 if area2 > 0 else -1
    rows = []
    for i,b in enumerate(points):
        a,c = points[i-1],points[(i+1)%len(points)]
        u = (b[0]-a[0], b[1]-a[1])
        v = (c[0]-b[0], c[1]-b[1])
        signed_turn = math.degrees(math.atan2(u[0]*v[1]-u[1]*v[0], u[0]*v[0]+u[1]*v[1]))
        exterior = winding*signed_turn
        interior = 180-exterior
        rows.append(dict(path=path_number,vertex=i+1,name=NAMES[i],x_mm=b[0],y_mm=b[1],
                         interior_deg=interior,exterior_turn_deg=exterior,
                         outside_sector_deg=360-interior))
    assert abs(sum(r['interior_deg'] for r in rows)-1440) < 1e-9
    assert abs(sum(r['exterior_turn_deg'] for r in rows)-360) < 1e-9
    return rows

data = json.loads(SOURCE.read_text())
rows = [row for i,points in enumerate(data['six_paths_mm']) for row in angle_rows(points,i+1)]
with (OUT/'candidate_angles.csv').open('w',newline='') as f:
    w = csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

lines = ['# Angle worksheet — unverified candidate, 12 September 2026', '',
         '**These are calculated angles of the existing photographic reconstruction, not measured angles of the landmark.** No 1949 or modern dimensioned elevation has been located. This worksheet does not select a new geometry.', '',
         'The source is `accurate_light_paths.json`, before the manufacturing border allowance. Full values for all six paths are in `candidate_angles.csv`. Left/right pairs are mirrored, but the shape is not constrained to five-fold rotational symmetry.', '',
         '## Angle conventions', '',
         '- **Interior:** angle inside the star polygon; greater than 180° at a concave notch.',
         '- **Exterior turn:** 180° minus the interior; positive at a tip and negative at a notch. This is the conventional signed polygon turn, with outward tips positive regardless of the stored vertex order.',
         '- **Outside sector:** 360° minus the interior. At a notch this is the small visible opening between its sides. This is different from the exterior turn.', '',
         'For a regular pentagram-derived star only, the interior tip is 36°, the interior notch is 252°, exterior turns are +144° / −72°, and the outside sectors are 324° / 108°. Those values are a mathematical comparison, not evidence about the Roanoke Star.', '',
         '## Current outer path', '',
         '| Vertex (clockwise from top) | Interior | Exterior turn | Outside sector |',
         '|---|---:|---:|---:|']
for r in rows[:10]:
    lines.append(f"| {r['vertex']}. {r['name']} | {r['interior_deg']:.2f}° | {r['exterior_turn_deg']:+.2f}° | {r['outside_sector_deg']:.2f}° |")
lines += ['', 'The interior angles sum to 1440° and the signed exterior turns to 360° for each ten-vertex path. These identities check the calculation; they do not validate the reconstructed shape.', '',
          'A perspective projection generally changes angles. Bilateral symmetry and an overall width/height ratio do not uniquely recover metric geometry from an uncalibrated image. See [the accuracy audit](ACCURACY_AUDIT.md) and [the review of the new research](USER_RESEARCH_REVIEW.md).', '',
          '## New 60° hypothesis', '',
          'The supplied research proposes edge directions 0°, ±30°, ±60° and a 60° top apex. It supplies no rectification calibration, source pixel coordinates for the edge fits, residuals, or uncertainty for these angles. Treat this as unverified. Edge directions alone also do not fix shoulder lengths, leg lengths or nested offsets.', '',
          f'Source SHA-256: `{hashlib.sha256(SOURCE.read_bytes()).hexdigest()}`', '']
(OUT/'ANGLE_WORKSHEET.md').write_text('\n'.join(lines))
print('\n'.join(lines[lines.index('## Current outer path'):lines.index('## Current outer path')+14]))
