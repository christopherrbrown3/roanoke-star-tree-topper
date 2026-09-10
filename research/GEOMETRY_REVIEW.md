# Roanoke Star geometry review — corrected reconstruction

Status: superseded by `ACCURACY_AUDIT.md` on 10 September 2026. The following records the photographic reconstruction method, not a verified exact geometry. The user has not accepted the result.

## Published dimensions and structure

The [City of Roanoke](https://www.roanokeva.gov/1329/Roanoke-Star) describes an 88.5-foot star with three nested frames, each carrying three to five sets of clear neon tubing. The [Smithsonian inventory](https://nmaahc.si.edu/object/siris_ari_334963) records 88.5 feet high by 84.5 feet wide. This gives a width of **190.96 mm at 200 mm height**.

The [Virginia Department of Historic Resources nomination](https://www.dhr.virginia.gov/VLR_to_transfer/PDFNoms/128-0352_Roanoke_Star_1999_Final_Nomination.pdf) describes the substantial steel lattice support. This rear tower is omitted from the topper and replaced with a concealed removable tree socket.

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

## Corrected geometry

Before the small manufacturing perimeter allowance:

| Feature | Reconstructed value |
|---|---:|
| Outer-frame apex angle | 36.66° |
| Three frame outer heights | 200.00 / 140.68 / 79.09 mm |
| Three frame outer widths | 190.96 / 136.28 / 77.89 mm |
| Outer shoulder height (origin at height midpoint) | +31.83 mm |
| Outer bottom valley | −46.02 mm |
| Outer lower point x coordinates | ±65.58 mm |
| Six apex angles | 34.78–36.66° |

The center star and each paired path have independently measured coordinates. They are not generic five-point star primitives, constant radial scale copies, or a direct trace of a low-angle photograph.

## Manufacturing translation

- Preserve the 200 × 190.96 mm backing envelope, with a 2.2 mm rounded perimeter allowance around slightly reduced light paths.
- Use 1.8 mm nominal white rails, six separate closed-loop inserts arranged in three pairs. Earlier connecting webs were removed after render review to preserve the gaps at the tips.
- Preserve varying gaps. The minimum visible within-pair gaps are 1.45, 0.93, and 1.52 mm; the minimum gaps between the pairs are 3.47 and 4.06 mm. These are minima over the entire outlines, not uniform spacing values.
- Seat the inserts in 1.2 mm deep channels with approximately 0.30 mm clearance per side. The triangulated 2D profiles measure 0.299 mm minimum clearance due to rounded polygon discretization.
- Keep a 3.2 mm rear plate, 5.0 mm raised channel tops, and 6.4 mm assembled front thickness. Inserts are 2.6 mm thick overall.
- Use a removable 80 mm deep socket with 34/22 mm nominal bore and 2.4 mm radial wall. Shift the attachment flange down 3 mm to conceal it behind the revised silhouette. The full socket-and-flange front projection has zero area outside the backing outline.
- Use four 2.5 × 6 mm plastic-thread pan-head screws, 2.9 mm flange holes, 2.0 mm blind pilots, and two locating keys with 0.30 mm side clearance. The revised support web meets the sleeve wall without intentionally intruding into its bore.

These manufacturing figures were carried into the final Blender model. Some digital checks passed, but the light self-intersection check remains unresolved; see the current design report.

## Review artifacts

- `city_trace_overlay.png`: six measured paths over the primary photograph.
- `rectified_six_paths.png`: corrected face-on centerline diagram.
- `independent_aerial_overlay.jpg`: independent drone-photo projection check.
- `accurate_light_paths.json`: complete six-path reconstruction and fit parameters.
- `../final/profile_measurements.json`: prepared manufacturing path coordinates and measured 2D gaps/clearances.

Photo attribution: city aerial credited to its City of Roanoke source; Schumin photographs credited to Ben Schumin; Wikimedia Neon Lights photograph credited to TampAGS for AGS Media, CC BY-SA 3.0, 17 November 2008. Overlays are cropped/annotated research comparisons, not original photographs. See linked source pages for applicable photo rights.
