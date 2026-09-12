# Angle worksheet — unverified candidate, 12 September 2026

**These are calculated angles of the existing photographic reconstruction, not measured angles of the landmark.** No 1949 or modern dimensioned elevation has been located. This worksheet does not select a new geometry.

The source is `accurate_light_paths.json`, before the manufacturing border allowance. Full values for all six paths are in `candidate_angles.csv`. Left/right pairs are mirrored, but the shape is not constrained to five-fold rotational symmetry.

## Angle conventions

- **Interior:** angle inside the star polygon; greater than 180° at a concave notch.
- **Exterior turn:** 180° minus the interior; positive at a tip and negative at a notch. This is the conventional signed polygon turn, with outward tips positive regardless of the stored vertex order.
- **Outside sector:** 360° minus the interior. At a notch this is the small visible opening between its sides. This is different from the exterior turn.

For a regular pentagram-derived star only, the interior tip is 36°, the interior notch is 252°, exterior turns are +144° / −72°, and the outside sectors are 324° / 108°. Those values are a mathematical comparison, not evidence about the Roanoke Star.

## Current outer path

| Vertex (clockwise from top) | Interior | Exterior turn | Outside sector |
|---|---:|---:|---:|
| 1. Top tip | 36.66° | +143.34° | 323.34° |
| 2. Upper-right notch | 251.67° | -71.67° | 108.33° |
| 3. Right tip | 39.08° | +140.92° | 320.92° |
| 4. Lower-right notch | 249.05° | -69.05° | 110.95° |
| 5. Lower-right tip | 32.41° | +147.59° | 327.59° |
| 6. Bottom notch | 258.92° | -78.92° | 101.08° |
| 7. Lower-left tip | 32.41° | +147.59° | 327.59° |
| 8. Lower-left notch | 249.05° | -69.05° | 110.95° |
| 9. Left tip | 39.08° | +140.92° | 320.92° |
| 10. Upper-left notch | 251.67° | -71.67° | 108.33° |

The interior angles sum to 1440° and the signed exterior turns to 360° for each ten-vertex path. These identities check the calculation; they do not validate the reconstructed shape.

A perspective projection generally changes angles. Bilateral symmetry and an overall width/height ratio do not uniquely recover metric geometry from an uncalibrated image. See [the accuracy audit](ACCURACY_AUDIT.md) and [the review of the new research](USER_RESEARCH_REVIEW.md).

## New 60° hypothesis

The supplied research proposes edge directions 0°, ±30°, ±60° and a 60° top apex. It supplies no rectification calibration, source pixel coordinates for the edge fits, residuals, or uncertainty for these angles. Treat this as unverified. Edge directions alone also do not fix shoulder lengths, leg lengths or nested offsets.

Source SHA-256: `62a33bdb01c18d3dc716f849486a6992bf850d4dcaea613d3e7e009a365d114d`
