# Angle worksheet — current parallel-path candidate, 13 September 2026

**These are calculated angles of the current model, not measured angles of the landmark.** No 1949 or modern dimensioned elevation has been located.

The source is `../print_in_place/profile_measurements.json`. Full values for all six paths are in `candidate_angles.csv`. The 13 September correction derives all six paths from exact parallel offsets of the outer candidate edge lines. All corresponding angles therefore match. Left/right pairs are mirrored, but the shape is not constrained to five-fold rotational symmetry. See [the parallel-path correction](PARALLEL_PATH_CORRECTION.md) for the prior errors and chosen offsets.

## Angle conventions

- **Interior:** angle inside the star polygon; greater than 180° at a concave notch.
- **Exterior turn:** 180° minus the interior; positive at a tip and negative at a notch. This is the conventional signed polygon turn, with outward tips positive regardless of the stored vertex order.
- **Outside sector:** 360° minus the interior. At a notch this is the small visible opening between its sides. This is different from the exterior turn.

For a regular pentagram-derived star only, the interior tip is 36°, the interior notch is 252°, exterior turns are +144° / −72°, and the outside sectors are 324° / 108°. Those values are a mathematical comparison, not evidence about the Roanoke Star.

## Current outer path

| Vertex (clockwise from top) | Interior | Exterior turn | Outside sector |
|---|---:|---:|---:|
| 1. Top tip | 36.62° | +143.38° | 323.38° |
| 2. Upper-right notch | 251.69° | -71.69° | 108.31° |
| 3. Right tip | 39.11° | +140.89° | 320.89° |
| 4. Lower-right notch | 249.00° | -69.00° | 111.00° |
| 5. Lower-right tip | 32.40° | +147.60° | 327.60° |
| 6. Bottom notch | 258.97° | -78.97° | 101.03° |
| 7. Lower-left tip | 32.40° | +147.60° | 327.60° |
| 8. Lower-left notch | 249.00° | -69.00° | 111.00° |
| 9. Left tip | 39.11° | +140.89° | 320.89° |
| 10. Upper-left notch | 251.69° | -71.69° | 108.31° |

The interior angles sum to 1440° and the signed exterior turns to 360° for each ten-vertex path. These identities check the calculation; they do not validate the reconstructed shape.

A perspective projection generally changes angles. Bilateral symmetry and an overall width/height ratio do not uniquely recover metric geometry from an uncalibrated image. See [the accuracy audit](ACCURACY_AUDIT.md) and [the review of the new research](USER_RESEARCH_REVIEW.md).

## New 60° hypothesis

The supplied research proposes edge directions 0°, ±30°, ±60° and a 60° top apex. It supplies no rectification calibration, source pixel coordinates for the edge fits, residuals, or uncertainty for these angles. Treat this as unverified. Edge directions alone also do not fix shoulder lengths, leg lengths or nested offsets.

Source SHA-256: `01011ab9585d2f56a1e46e2991aa97cc0026d3547e0e660f842bbcb75297f356`
