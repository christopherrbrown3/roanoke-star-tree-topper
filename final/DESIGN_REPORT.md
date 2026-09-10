# Roanoke Star Christmas tree topper

**Work in progress — 10 September 2026.** The user has not accepted the landmark geometry. The current photographic reconstruction is not verified as an exact replica. The latest light export also has 163 self-intersection candidates awaiting a Blender rebuild of the prepared source fix. Existing exports and previews are retained as candidates, not an approved print release. See [the accuracy audit](../research/ACCURACY_AUDIT.md).

## Research and accuracy

The real star is **88.5 ft high × 84.5 ft wide**, according to the [Smithsonian inventory](https://nmaahc.si.edu/object/siris_ari_334963). The [City of Roanoke](https://www.roanokeva.gov/1329/Roanoke-Star) describes three nested frames carrying multiple sets of clear neon tubing. The [Virginia historic-register nomination](https://www.dhr.virginia.gov/VLR_to_transfer/PDFNoms/128-0352_Roanoke_Star_1999_Final_Nomination.pdf) documents the rear steel support structure.

Fifteen distinct reference views were reviewed, including city photographs, two Wikimedia views, a tourism aerial, and several Ben Schumin drone and ground photographs. The primary measurement source was the [city's nearly frontal aerial](https://www.roanokeva.gov/ImageRepository/Document?documentID=13604). Its six visible illuminated paths were independently traced and projectively corrected using bilateral symmetry, horizontal shoulders, corresponding paired edges, and the published aspect ratio. Ground-level photographs were treated as upward-looking views and were not directly traced for frontal proportions.

A separate [8064 × 5376 drone photograph](https://www.schuminweb.com/photo_features/aerial-view-of-the-roanoke-star/) provided an image-space comparison, which does not independently establish metric accuracy. Reprojection error fell from 29.10 to 15.81 image pixels compared with the previous design. The currently inferred outer apex is about **36.7°**, and the three frame heights are approximately **100% / 70.3% / 39.5%** before the small manufacturing border allowance. Each of the six paths has its own coordinates; the inner paths are not generic scaled stars.

Six visible contours represent the landmark's all-white appearance at this scale, not every individual neon tube or every color-circuit combination. This is a photographic reconstruction, not a surveyed replica. The maximum adjustment when averaging photographic left/right asymmetry was 1.38 mm on the normalized 200 mm reconstruction. That is an uncertainty indicator, not a guaranteed physical accuracy.

The full photo inventory, method, traced overlay, and independent comparison are in [GEOMETRY_REVIEW.md](../research/GEOMETRY_REVIEW.md).

## Finished dimensions

| Feature | Final value |
|---|---:|
| Overall height | 199.997 mm, nominal 200 mm |
| Overall width | 190.960 mm |
| Overall depth, including mount | 47.536 mm |
| Rear backing plate | 3.2 mm |
| Raised dark channel surround | 5.0 mm total depth from rear face |
| Assembled star face thickness | 6.4 mm |
| White insert thickness | 2.6 mm |
| Nominal white line width | 1.8 mm, with rounded path corners |
| Channel engagement depth | 1.2 mm |
| Nominal locating clearance | 0.30 mm per side; measured profile minimum 0.299 mm |
| Minimum gaps within the three white pairs | 1.45 / 0.93 / 1.52 mm |
| Minimum gaps between pairs | 3.47 / 4.06 mm |

The gap figures are minima across complete paths. Spacing varies around the outlines, as in the measured reference.

The solid-geometry volume is **93.55 cm³**, equivalent to approximately **116 g in solid PLA** at 1.24 g/cm³. Individual solid PLA estimates are 67.8 g backing, 17.0 g lights, and 31.2 g mount. Using PETG for the mount makes the mixed-material solid estimate approximately 117 g. Actual sliced weight depends on shells, infill, and material density and should be lower with the recommended infill. Hardware is excluded.

## Tree mount and balance

- Tapered through-bore: **34 mm lower opening, 22 mm upper opening, 80 mm insertion depth**.
- Nominal radial wall: **2.4 mm**; 3 mm rear relief slot provides limited flex.
- Two levels of **4 mm transverse tie holes**, 40 mm apart, for zip ties or floral wire.
- Removable flange with **four 2.5 mm diameter × 6 mm long plastic-thread pan-head screws**. Flange holes are 2.9 mm; backing pilots are 2.0 mm diameter with 2.8 mm usable blind depth.
- Two 4 mm locating keys seat in 4.6 mm pockets with approximately 0.30 mm side and 0.20 mm end clearance.
- The entire socket and flange are concealed in the orthographic front view. The flange is shifted down to remain inside the corrected star silhouette.

The solid-model center of mass is centered horizontally and approximately **19.5 mm in front of the socket axis**. The corresponding solid-PLA gravity moment is about **0.022 N·m**. The sleeve sits close behind the plate; tie retention at both levels is still needed to resist forward lean. A slender artificial leader or small natural branch may need a compressible shim and ties. This is an adjustable tapered mount, not a claim of a universal friction fit or tested load capacity.

## Printing

All individual STLs are already oriented for printing, in millimeters. Use a **0.4 mm nozzle and 0.2 mm layers**. A 220 × 220 mm bed accommodates the star with a modest brim.

| Part | Orientation | Material | Perimeters | Infill | Supports | Brim |
|---|---|---|---:|---:|---|---|
| `roanoke_star_base.stl` | Flat rear face on bed; channels upward | Navy/black PLA or PLA+ | 4 | 15% gyroid | None intended | Optional 3 mm |
| `roanoke_star_lights.stl` | Flat as exported; all six outline loops on bed | White PLA or PLA+ | 3 | 100% | None | None normally; avoid brims that merge the narrow gaps |
| `roanoke_star_tree_mount.stl` | Large mouth on bed; socket axis vertical | PETG preferred; PLA+ acceptable | 5 | 20% gyroid | None intended | 6 mm |

Use five top and bottom layers for the base, and four for the mount. The thin white rails will be mostly or entirely perimeter material. Let the bed cool before lifting them, and support the long arms during removal.

The socket's lower flange/web transitions are inclined for upright printing. The locating keys create short 1.2 mm projections, and the 4 mm tie holes require short bridges. No long suspended bridge or enclosed support cavity is designed in. Confirm the toolpaths with your printer profile; a previous Bambu Studio command-line slicing attempt crashed, so no successful slicer run or print-time estimate is claimed.

The combined STL and the 3MF show the assembled relationship. **Use the individual STLs for printing.** The 3MF preserves named objects and two materials; it is not a printer-specific sliced project or ready-to-run G-code.

## Assembly

1. Remove any first-layer flare or strings from the channels, white rails, keys, and screw holes.
2. Dry-fit the six white outlines, largest to smallest, with all top points facing upward. The paired recess boundaries locate each outline. Lower them straight into the open channels; do not force a tight fit.
3. Lift each outline, add a few small dots of adhesive suitable for your filament to the channel floor, and reseat it. Glue provides final retention; the recesses provide alignment.
4. Seat the two rear mounting keys and install the four 2.5 × 6 mm plastic-thread screws by hand. Check that the chosen screw engages the pilot without excessive force, and stop when the flange seats.
5. Fit the large socket mouth over the tree leader. Add a shim if needed and secure it through both tie-hole levels. Adjust the ties until the star stands upright.

## Intentional changes from the landmark

- A thin dark backing replaces the open steel lattice to keep the topper rigid and provide print-flat channels.
- Six continuous white rails reproduce the visible paired outline pattern; individual tube segments, brackets, wiring, and electrical equipment are omitted.
- Rails are thickened to 1.8 mm and tips have small rounded transitions for visibility and FDM durability.
- The light paths are reduced approximately 2.2–2.3% to make room for a rounded protective perimeter while preserving the finished 200 × 190.96 mm envelope.
- Six separate closed loops replace connecting webs that were visible in the earlier preview. They remain a single white color group, and preserve the open gaps at the tips.
- The steel tower is replaced by a hidden tapered tree socket with keys, screws, and ties.
- Opposing vertices are symmetrized and shoulders leveled to remove residual photographic skew.

## Validation status — incomplete

The retained candidate meshes pass watertightness, winding, positive-volume, duplicate-face, degenerate-triangle, and assembled collision checks. The lights contain six intentional closed loops. The assembly has eight intentional solids.

However, `self_intersection_check.json` reports **163 light-mesh candidates**, so this is not a passed release. The source now removes the problematic three-dimensional light bevel while retaining the rounded two-dimensional path corners. That change has not yet been rebuilt in Blender because the Mac is locked.

The last report and previews predate this source change. Regenerate the Blender meshes, all exports and previews, self-intersection check, insertion/bore checks, and 3MF validation before any print release. Retained JSON records describe the existing files, not the unexecuted change.

Separately, the geometric fidelity criterion remains unresolved. A free perspective fit is insufficient to prove exact face-on proportions. No physical test print or successful printer-specific slicing has been completed.

## Files and editing

- `roanoke_star_tree_topper.blend`: editable named meshes, six hidden reference curves, packed city reference photo, source text, and measured profiles.
- `roanoke_star_base.stl`, `roanoke_star_lights.stl`, `roanoke_star_tree_mount.stl`: printable parts in bed orientation.
- `roanoke_star_assembled.stl`: assembled reference.
- `roanoke_star_tree_topper.3mf`: assembled named objects and color materials.
- `../previews/front.png`, `three_quarter.png`, `rear.png`: final Blender renders.
- JSON validation records: dimensions, topology, assembly fit, insertion paths, bore, and 3MF checks.
- `../scripts/`: reconstruction, profile generation, Blender construction/cleanup, export and validation scripts.

The Blender meshes remain directly editable. To regenerate changed dimensions, update the profile/build scripts and rerun the documented sequence in `../scripts/REBUILD.md`; the source is also embedded in the blend. The final meshes have their manufacturing booleans and bevels applied for reliable export.
