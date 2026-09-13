# Roanoke Star tree topper

A miniature of Roanoke's Mill Mountain Star, designed for one two-color print on a **Bambu Lab A1 with AMS lite**. The 200 mm topper carries **130 individual white tube sections**, arranged along six paths in three pairs, on a dark body with an integral rear tree socket. The colors are separate solid volumes that fuse during printing; no assembly is required.

![Orthographic front render of the current two-color topper](print_in_place/previews/front.png)

**Current status — 13 September 2026:** the parallel tube-path correction has been rebuilt in Blender, checked, and exported to STL and 3MF. The linked model files and previews show the corrected version. Bambu Studio validation is deferred at the owner's request, and no physical test print has been made. The landmark's exact angles and tube-joint schedule remain unverified; this is a documented photographic reconstruction, not a certified scale replica.

## Start here

| File | Purpose |
|---|---|
| [Two-color 3MF](print_in_place/roanoke_star_A1.3mf) | Current model: one build object with two material volumes, positioned face-down. Standard 3MF; no saved Bambu slicing profile or toolpath. |
| [Editable Blender scene](print_in_place/roanoke_star_A1.blend) | Millimeter-scale model, material assignments, cameras, and embedded project notes. |
| [Design report](print_in_place/DESIGN_REPORT.md) | Dimensions, integral mount, printing assumptions, validation, and limitations. |
| [Rebuild guide](scripts/REBUILD.md) | Profile preparation, Blender GUI construction, and independent checks. |

The current files are in **`print_in_place/`**. The older `final/` folder contains an assembly-based candidate retained as design history; its name does not indicate the current release.

## From a Christmas promotion to a city landmark

The connection to a Christmas tree topper is part of the Star's history. The Roanoke Merchants Association commissioned it for the 1949 Christmas season, and it was first illuminated on **November 23, 1949**. What began as a seasonal attraction became a lasting landmark above the city. The City of Roanoke records the Star's height as **88.5 feet**. [City history](https://www.roanokeva.gov/1329/Roanoke-Star)

Roy C. Kinsey Sign Company built the sign, working with Roanoke Iron & Bridge Works on the steel structure. Historical accounts name Robert Little as its designer, although they disagree on his middle initial. An anniversary interview describes the full-scale Star being assembled flat on the ground at Roanoke's airport, then taken apart, transported up Mill Mountain, and erected on its tower. That fabrication history helped guide the search for shop and erection drawings. [1982 historical account, pp. 88–90](https://www.virginiaroom.org/digital/files/original/67/6354/JHSWV_11_02_1982.pdf), [WDBJ interview preserved by Virginia Tech](https://scholar.lib.vt.edu/VA-news/WDBJ-7/script_archives/99/1199/112899/112899.m.htm)

The landmark is more complex than a single star outline. The City describes **three nested structural stars** carrying multiple neon sets. In the all-white views used for this project, six dominant illuminated contours appear as three close pairs. That arrangement, including the smaller central star, is the feature the topper aims to preserve. Six paths describe the visible pattern; they are not a count of all glass pieces or electrical circuits. [City description](https://www.roanokeva.gov/1329/Roanoke-Star)

## How the star was researched

The project combines official records, historical accounts, more than fifteen reviewed photographs and views, the user's additional research, and a reference photograph of another printed interpretation. Research notes preserve the source links and the reasoning behind each design choice.

**Proportions and perspective.** City photographs, aerial views, Wikimedia images, and Ben Schumin's ground-level photographs were compared. Views from the observation deck look upward; they compress vertical distances and can make the apex appear wider. Oblique views also change spacing across the face. Early tracing and perspective-corrected overlays were therefore audited rather than accepted as proof of the physical angles. The [accuracy audit](research/ACCURACY_AUDIT.md) demonstrates why different symmetric shapes can fit the same photograph under different perspective transforms.

**Dimensions and angles.** The documented 88.5-foot height is the scale reference. Width remains disputed: the Smithsonian inventory gives approximately **88.5 × 84.5 feet**, while the City's art catalog lists **1062 × 1200 inches**, equivalent to 88.5 × 100 feet, without a dimensioned elevation clarifying the axes. The current candidate retains the 84.5/88.5 proportion as an explicit assumption. Neither a regular pentagram nor the supplied 60°-apex hypothesis has been established as the landmark's actual geometry. [Smithsonian inventory](https://siris-artinventories.si.edu/ipac20/ipac.jsp?booklistformat=&profile=ariall&session=1761P49582NO9.272492&uri=full%3D3100001~%21334963~%210), [City art catalog](https://www.artworkarchive.com/profile/roanoke-arts/artwork/roanoke-star)

The [parallel-path correction](research/PARALLEL_PATH_CORRECTION.md) records the 13 September repair of converging tube rows, including a [before/after detail](research/parallel_path_comparison.png). All corresponding edges in the model now share exact directions; nested offsets are fitted to the previous traces.

The [angle worksheet](research/ANGLE_WORKSHEET.md) separates polygon interior angles, signed exterior turns, and outside sectors. Its [coordinate-derived CSV](research/candidate_angles.csv) records all six candidate paths. Those are measurements of this model, not recovered original specifications.

**Individual tubes.** Close photographs show shorter neon sections, interruptions along straight runs, and illuminated bends around corners. A high-resolution Commons image provides candidate interruptions near the quarter points of one long run. The model carries that observation into a rounded, segmented appearance, with lit corners and dark gaps along straight portions. Mirroring and repeating that schedule elsewhere is a modeling inference: the photos do not reveal every joint, and a dark mark can also be a support or occlusion. The 130-section count belongs to this print. [Tube-layout research](research/tube_layout_research_luna.md), [pixel observations](research/tube_joint_observations.json), [Schumin close-up series](https://www.schuminweb.com/photography/roanoke-star-night/), [Commons photograph](https://commons.wikimedia.org/wiki/File:Mill_Mountain_Star_Neon_Lights.JPG)

**Original plans.** The search covered the Virginia DHR National Register nomination, NPS asset records, the City's public Engineering plan repository, Virginia Room finding aids, and modern restoration-report leads. No dimensioned Star elevation or original shop drawing was located in the material examined. The online DHR file omits Exhibits B–F, whose contents are unknown; the Virginia Room index identifies relevant Kinsey, Iron & Bridge Works, and Mill Mountain files whose contents remain uninspected. The [plan-search log](research/PLAN_SEARCH.md) records the actual coverage and promising next leads. [Archive inquiry drafts](research/ARCHIVE_REQUEST_DRAFTS.md) are preserved but have not been sent.

The [review of the user's research](research/USER_RESEARCH_REVIEW.md) explains which findings were retained, which remain hypotheses, and why centerline spacing must be distinguished from clear gaps. The supplied desk-print photograph guided the individual-tube appearance; it was not treated as a measured elevation or imported as a source mesh.

## Designed for one A1 print

![Three-quarter render showing the tube pattern and integral mount](print_in_place/previews/three_quarter.png)

| Feature | Current model |
|---|---:|
| Height × width × total depth | 200.00 × 190.96 × 50.84 mm |
| Structural backing | 4.0 mm |
| White tube sections | 130; 1.8 mm wide; 1.0 mm deep |
| Closest clear separation between white sections | 1.200 mm |
| Integral socket length | 80 mm |
| Nominal circular clearance, lower → upper | Ø34 → Ø22 mm |
| Minimum socket wall | 2.4 mm |

The white sections are **flush inlays** with rounded ends. Printing the decorated face against the bed gives both colors the same surface finish, keeps the small sections supported, and confines color changes to the first five 0.20 mm layers. The continuous dark backing then carries the integral socket. Its house-shaped bore and diamond tie holes use sloped roofs to avoid broad unsupported ceilings.

Use two compatible PLA spools, a 0.4 mm nozzle, and a 0.20 mm layer height. The proposed starting process is four walls, five top and bottom layers, and 15% gyroid infill, with supports disabled and the prime tower enabled. Keep the model face-down and map both color volumes as parts of **one object**. Inspect the first five layers, the transition to dark-only material, socket roof, and tie holes before printing. Slicer confirmation is still pending; these are starting settings rather than a tested print profile.

The socket slides over the tree leader. Optional ties through the rear holes provide retention; no model parts need to be joined. Real branch fit and balance require a physical test. The solid-volume PLA estimate is approximately 107 g before accounting for infill or purge; it is not a slicer weight estimate.

## Validation and project history

The [mesh report](print_in_place/mesh_validation.json) records watertight, consistently wound material meshes, no duplicate or zero-area triangles, and one connected fused outer solid. The [intersection check](print_in_place/self_intersections.json) found zero non-adjacent triangle-intersection candidates. Material volumes fill the outer solid within export precision, the nominal tapered mandrel clears the socket, and the mesh has no above-bed surface beyond the chosen 45° overhang limit. The standard 3MF also passes a geometry round-trip check.

These checks establish digital geometry quality. Printer-specific slicing, physical strength, tree fit, and fidelity to a measured landmark elevation are separate checks and remain open.

`research/` contains the evidence and attribution; `scripts/` contains the construction and validation code; `print_in_place/` contains the current model and previews. Earlier studies in `final/`, `design/`, `models/`, `review/`, and the root `Roanoke_Star_*` files preserve the progression from generic-star studies to photographic reconstruction, continuous inserts, and the current segmented, integral design.

## Reference rights

Third-party photographs and archival documents retain their original rights. Source attribution is recorded in [SOURCES.md](research/SOURCES.md), [GEOMETRY_REVIEW.md](research/GEOMETRY_REVIEW.md), and the individual research notes. Supplied files are preserved with [provenance hashes](research/user_provided/PROVENANCE.json). This private repository does not grant permission to republish reference material or imply a public license.
