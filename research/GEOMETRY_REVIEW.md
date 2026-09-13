# Photograph review and perspective reconstruction

This document records the photographic evidence and reconstruction method. The [accuracy audit](ACCURACY_AUDIT.md) explains the limits of inferring physical geometry from uncalibrated photographs.

## Published dimensions and structure

The [City of Roanoke](https://www.roanokeva.gov/1329/Roanoke-Star) describes an 88.5-foot star with three nested frames, each carrying three to five sets of clear neon tubing. The [Smithsonian inventory](https://nmaahc.si.edu/object/siris_ari_334963) records 88.5 feet high by 84.5 feet wide. This gives a width of **190.96 mm at 200 mm height**.

The [Virginia Department of Historic Resources nomination](https://www.dhr.virginia.gov/VLR_to_transfer/PDFNoms/128-0352_Roanoke_Star_1999_Final_Nomination.pdf) describes the substantial steel lattice support. This rear tower is omitted from the topper and replaced with an integrated tree socket.

## Photographs actually examined

The expanded comparison includes the following distinct views, with different uses rather than equal geometric weight:

| Reference | View and use |
|---|---|
| [City aerial, original 2600 × 1461](https://www.roanokeva.gov/ImageRepository/Document?documentID=13604) | Primary measurement source: nearly frontal white illumination, six visible paths in three pairs. Mild perspective is corrected. |
| [Ben Schumin aerial, 13 June 2024](https://www.schuminweb.com/photo_features/aerial-view-of-the-roanoke-star/) | Independent high-resolution 8064 × 5376 check of frame vertices and support depth. Oblique and viewed from above. |
| [Schumin travel series](https://www.schuminweb.com/life-and-times/adventures-in-tennessee-part-7/), image 393 | Ground-level oblique, framing and tubing details; not directly traced for proportions. |
| Same series, image 399 | More distant aerial, overall proportions. |
| Same series, image 400 | Oblique aerial from one side. |
| Same series, image 401 | Oblique aerial from the opposite side. |
| Same series, image 429 | Very distant city/ridge view, recognizability and silhouette. |
| Same series, image 430 | Overhead/edge view, rear support and depth. |
| [Wikimedia: Roanoke star](https://commons.wikimedia.org/wiki/File:Roanoke_star.jpg) | Low-angle close view; tube and frame placement only. |
| [Wikimedia: Mill Mountain Star Neon Lights](https://commons.wikimedia.org/wiki/File:Mill_Mountain_Star_Neon_Lights.JPG) | Low-angle colored illumination; color circuits and tube placement. The colored mode does not illuminate the same visible paths as the all-white view. |
| [Visit Virginia's Blue Ridge](https://www.visitroanokeva.com/things-to-do/attractions/roanoke-star/), patriotic aerial | Additional oblique aerial proportion check. |
| City image 13600 | Rear steel support. |
| City image 13601 | Underside, deliberately excluded from frontal tracing. |
| City image 13602 | Low-angle front, deliberately excluded from frontal tracing. |
| City image 13603 | Distant night appearance. |

The city screenshots and the original city aerial are the same view and are not counted as different photographs. Six visible illuminated contours are an interpretation of the all-white display at this scale; they are not a claim that the landmark contains only six individual neon tubes.

## Perspective treatment

1. Extract six bright centerline paths from the original city aerial. Radial peak detection provides 596 accepted six-peak samples. Each path's ten straight segments are fitted independently; segment intersections define the vertices. The median-quality edge fitting is approximately 0.19–0.25 image pixels RMS per path. This is tracing precision, not physical dimensional accuracy.
2. Fit a projective correction using bilateral symmetry, horizontal shoulder segments, and approximately parallel corresponding segments within each pair. Anchor the overall width-to-height ratio to the published dimensions. Do not assume that all six stars are scaled copies.
3. Average opposing vertices to remove photographic asymmetry. The largest resulting adjustment is 1.38 mm on the 200 mm normalized reconstruction.
4. Reproject the three outer frame paths onto a separate high-resolution drone image. The revised fit has 15.81 pixel RMS error versus 29.10 pixels for the earlier geometry, about a 46% reduction. This is an independent visual consistency check; differences between a lit tube centerline and a steel frame edge, image distortion, and manual landmark selection remain.
5. Use ground-level photographs to check tubing and support details, not to dictate frontal angles. The 2024 drone file records a 14.3° downward gimbal angle, but metadata alone was insufficient to determine a precise front-plane correction and was not used as an exact calibration.

This is a measured photographic reconstruction, not a surveyed replica. No engineering drawing establishing every vertex was located. Numerical fit results must not be interpreted as a guaranteed millimeter accuracy of the real landmark.

## Relationship to the print model

The [photographic path record](photographic_paths.json) preserves the centerline coordinates used as input to the current design. The [parallel-path construction](PARALLEL_PATH_CORRECTION.md) derives consistent inward offsets from those coordinates. Current manufacturing dimensions, the integrated mount, and validation are documented in the [A1 design report](../print_in_place/DESIGN_REPORT.md).

The [original reconstruction data](accurate_light_paths.json) supports the perspective audit. Reference photographs and annotated photo comparisons are linked through the [source inventory](SOURCES.md); they are not redistributed in the repository.
