# Review of supplied research and print reference — 12 September 2026

The user's two-color Christmas tree topper remains the target. The new desk-print photograph is an appearance reference. Its lighting enclosure and electrical design are outside the chosen design. The original Markdown is preserved without alteration. The photograph is represented by its source hash and provenance in [user_provided](user_provided/PROVENANCE.json); the image itself is excluded from the public repository.

## Findings to retain

- Three structural star frames are documented by the [City of Roanoke](https://www.roanokeva.gov/1329/Roanoke-Star).
- The all-white photographs support six dominant visible contours arranged in three close pairs, with larger spaces between pairs. The current candidate already models that topology. This is a visible-pattern interpretation, not a count of every physical glass tube or circuit.
- The supplied desk-print photo reinforces the dark face / white paired-outline appearance. It is oblique and cannot independently establish face-on angles, exact proportions, or spacing.
- The 88.5-foot star height has multiple historical and official sources. The supporting tower's 100-foot height is a separate dimension.
- Original drawings and recent engineering assessments remain valuable leads. They have not yet supplied verified vertex coordinates.

## Corrections and qualifications

| Supplied claim | Review | Consequence for CAD |
|---|---|---|
| The 84.5-foot width definitively proves the actual Star is not regular | The Smithsonian inventory records **approximate** dimensions. The [city art catalog](https://www.artworkarchive.com/profile/roanoke-arts/artwork/roanoke-star) gives **1062 × 1200 inches**, equivalent to 88.5 × 100 feet, without an engineering elevation or clear axis explanation. If 84.5 feet is confirmed as frontal star width, it is incompatible with an upright regular pentagram of height 88.5 feet. | Keep 84.5/88.5 as an explicit current modeling assumption; resolve the conflicting measurement sources before treating it as exact. Do not silently choose 100 feet either. |
| 0°, ±30°, ±60° edge families and a 60° apex | A photo-derived hypothesis, without the source coordinates, camera calibration, correction transform, residuals, or uncertainty needed to reproduce it. An apparent angle in a low-angle/oblique photo is not a physical angle. | Do not replace the candidate's inferred 36.66° apex with 60° on this evidence. Neither value is verified as the landmark's angle. |
| Inter-band **clear gap** is about 1.8 times paired-track spacing | The supplied pixel positions are **centerlines**. Their intervals are 13, 17, 16 pixels within pairs and 27, 28 pixels between pairs. The mean ratio is 27.5 / (46/3) = **1.79348**. | This is a ratio of cross-section centerline intervals. It is not a clear edge-to-edge gap ratio. Subtract the half-widths of adjacent lines to obtain clear gaps, and measure normal to the local edges in a metrically corrected image. |
| Frame sizes 1.00 / 0.74 / 0.43 | Useful hypotheses, but no reproducible fit data or dimensioned source accompanies them. The present candidate uses different independently traced paths. | Preserve the estimates as research; do not silently overwrite paths or force all nested contours to be scaled copies. |
| “3–5 sets” explains the electrical grouping | The city gives that wording, but the proposed interpretation of circuitry versus fabricated pieces is not established by a wiring/shop drawing. | Avoid claiming a complete historical tube or circuit layout. |

A low-angle photograph can foreshorten the vertical dimension and widen the apparent apex; yaw and roll add further distortion. A free homography can fit different underlying shapes to the same photo. Even several unconstrained homography overlays are insufficient proof of metric accuracy. See [ACCURACY_AUDIT.md](ACCURACY_AUDIT.md).

## Interior and exterior angles

[ANGLE_WORKSHEET.md](ANGLE_WORKSHEET.md) reports every vertex of the **current candidate**, with full calculations for all six paths in [candidate_angles.csv](candidate_angles.csv). Interior angle, signed exterior turn, and outside sector are separately defined. The worksheet is a transparent record of the model, not a recovered original specification.

## Design carried forward

The latest model in [print_in_place](../print_in_place/DESIGN_REPORT.md) has 130 white inlay sections along six paths in three pairs, a continuous dark backing, and an integral hidden tree socket. The user chose a single print with no assembly on a Bambu A1 with AMS lite. The white solids and dark body fuse in the same print; no removable inserts or mount fasteners are needed. The reference desk print's individual dash lengths are not treated as original neon segment dimensions. No LED enclosure, wiring, diffuser, or electronics has been added.

The earlier continuous-insert candidate's bevel repair passed its digital checks. The subsequent A1 model was also built in Blender's GUI: both actual color meshes report zero non-adjacent triangle-intersection candidates, and independent checks validate the fused solid and material coverage. Mesh validity does not establish landmark fidelity. Exact geometry remains unresolved, no physical test print has been performed, and Bambu Studio validation is deferred at the user's request.

## Provenance of the secondary print

The supplied kitchen-counter photograph has no verified model page or creator attribution in the task. The separately linked [MakerWorld model by Higgins](https://makerworld.com/en/models/380234-roanoke-star) calls itself a recreation and supplies no engineering provenance. It was not used as a dimension source or imported into the CAD. The page was publicly viewable; a failed automated fetch was not evidence of a paid model.

See [PLAN_SEARCH.md](PLAN_SEARCH.md) for archive findings and the scope of the material examined.
