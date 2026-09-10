# Roanoke Star tree topper

Private design workspace for a two-color, approximately 200 mm Christmas tree topper based on the Mill Mountain Star in Roanoke, Virginia.

**Status: work in progress. The landmark geometry is not verified as exact or accepted as final. Do not treat the current exports as an approved print release.**

The photographic outline reconstruction, editable Blender scene, printable candidate parts, research, and validation records are checked in so the work is reproducible and its limitations are visible.

## Current issues

1. **Geometric accuracy remains unresolved.** The previous free-homography comparison does not establish correct metric proportions. Different symmetric face-on shapes can give the same photograph after a different perspective transform. See [the accuracy audit](research/ACCURACY_AUDIT.md) and its [sensitivity diagram](research/projective_ambiguity_audit.png).
2. **The latest exported light mesh has 163 self-intersection candidates.** A source change removing the problematic rail bevel is prepared, but it still needs to be executed and verified in Blender. Watertightness alone does not resolve this check.
3. The latest requested Blender rebuild is blocked while the Mac is locked. Current preview images and exported meshes are retained as review candidates.
4. There has been no physical test print or successful printer-specific slicer validation.

## Files

| Location | Contents |
|---|---|
| `final/` | Most recent candidate BLEND, STL and 3MF files; design report and validation JSON. The directory name is historical, not a final-approval claim. |
| `previews/` | Front, three-quarter and rear candidate renders. |
| `research/` | Reference photos, source attribution, measured paths, comparison overlays, and accuracy audit. |
| `scripts/` | Reconstruction, Blender construction, export and validation scripts. |
| `design/`, `models/`, `review/`, root `Roanoke_Star_*` files | Earlier design studies retained for history; superseded by the current candidate. |
| `output/playwright/` | Reference captures used during research. |

The unrelated temporary working folder, caches, and Blender backup files are excluded from version control.

## Intended construction

A dark backing carries six white closed-loop inserts arranged in three pairs. A removable tapered rear socket attaches using keys and four small screws. The candidate envelope is approximately 200 × 191 × 47.5 mm. These are model dimensions, not a certificate that every landmark angle and gap has been recovered correctly.

See [the design report](final/DESIGN_REPORT.md) for dimensions and proposed printing/assembly, and [REBUILD.md](scripts/REBUILD.md) for the build sequence.

## Reference rights

Third-party photographs retain their original rights. Attribution and source links are in [GEOMETRY_REVIEW.md](research/GEOMETRY_REVIEW.md) and [SOURCES.md](research/SOURCES.md). Their inclusion here does not grant permission to republish them. No public release or license is implied by this private repository.
