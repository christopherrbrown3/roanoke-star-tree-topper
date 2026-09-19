# Roanoke Star Tree Topper

Roanoke’s Mill Mountain Star, in miniature. This 200 mm Christmas tree topper brings the landmark’s distinctive neon pattern to a single two-color print: **130 individual tube sections on three white star-shaped bands**, a dark body, and an integrated tree mount.

**One print · Two colors · No assembly**

![Front render showing three white backing bands and individually outlined white tubes](print_in_place/previews/front.png)

Designed for the **Bambu Lab A1 with AMS lite**, with editable Blender source, a two-filament 3MF project, and a documented research and validation process.

## Download

| File | Use |
|---|---|
| **[Download the two-color 3MF](print_in_place/roanoke_star_A1.3mf)** | One object, face-down, with filament 1 assigned to the dark body and filament 2 to the white face details. |
| [Blender construction scene](print_in_place/roanoke_star_A1.blend) | Editable construction checkpoint; predates the final mesh cleanup in the STL and 3MF exports. |
| [Dark body STL](print_in_place/body_material.stl) + [white face STL](print_in_place/white_tube_material.stl) | Alternative material meshes with a shared origin. Import together as parts of one object. |
| [Design report](print_in_place/DESIGN_REPORT.md) | Detailed dimensions, mount geometry, material layout, and validation results. |

The 3MF includes the A1 0.4 mm printer configuration, two Generic PLA filaments, and 0.20 mm process settings. It contains editable geometry rather than a pre-sliced toolpath. All print files and renders are in [`print_in_place/`](print_in_place/).

**Validation scope:** the current STL and 3MF meshes pass the documented geometry checks. Bambu Studio has displayed the two-filament setup on import; sliced-layer verification is incomplete. Use the STL or 3MF files for printing—the Blender download is a construction checkpoint whose final scene/export synchronization is incomplete. See the [release status](print_in_place/RELEASE_STATUS.json).

## Designed around the tubes

The individual white sections give the face its character. Rounded ends and small dark breaks suggest separate lengths of neon, while continuous bends carry the light around the star’s points and recesses. Three white bands echo the pale backing frames visible in daylight photographs. A **0.6 mm dark outline** separates each tube from its backing, preserving the individual-tube appearance with only two filaments.

Each nested tube outline uses a constant inward offset from the outer path, keeping corresponding runs parallel through every corner—including the two lower side notches. The [spacing review](research/SPACING_REVIEW.md) compares the model with the primary aerial reference and explains why the existing tube positions were retained. The broader white backing bands leave approximately **1.6 mm of dark space** between the three star groups.

The tubes and backing bands are **flush inlays**, 1.0 mm deep; each tube is 1.8 mm wide. Both colors meet the build plate, giving the decorated face a consistent finish. The dark outlines provide visual definition without raised details or small unsupported bridges. A continuous 4 mm body joins the inlays and rear socket into one finished part. Color changes are confined to the first five layers at a 0.20 mm layer height.

![Three-quarter render of the two-color topper and its integrated rear mount](print_in_place/previews/three_quarter.png)

The tapered socket sits behind the star’s silhouette. Its sloped roof and diamond-shaped tie holes are designed around face-down FDM printing. The topper slides over the tree leader; the holes provide attachment points for optional retaining ties.

The back carries **`christopherbrown.io` recessed 0.6 mm** into the upper shoulder, clear of the socket. The lettering leaves 2.4 mm of material above the front inlays.

![Rear detail of the recessed christopherbrown.io attribution](print_in_place/previews/rear_detail.png)

## Print specifications

| Specification | Value |
|---|---|
| Target printer | Bambu Lab A1 with AMS lite |
| Overall size, height × width × depth | 200.00 × 190.96 × 50.84 mm |
| Materials | Two compatible PLA colors; navy or black body and tube outlines, white tubes and bands |
| Nozzle / layer height | 0.4 mm / 0.20 mm |
| Orientation | Decorated face flat against the build plate |
| Tube layout | 130 sections along six outlines in three pairs, on three white bands |
| Tube width / inlay depth | 1.8 mm / 1.0 mm |
| Break between consecutive tube sections | 1.20 mm |
| Dark outline around each tube | 0.60 mm |
| Clear space between white backing bands | 1.595 / 1.667 mm |
| Backing thickness | 4.0 mm |
| Integrated socket | 80 mm long; nominal circular clearance tapers from Ø34 to Ø22 mm |
| Socket wall thickness | 2.4 mm minimum |

1. Open the 3MF **as a project** in Bambu Studio. Its two parts are already assigned: filament 1 is dark, filament 2 is white. Map those project filaments to the appropriate AMS lite spools. If using the STLs, import both as parts of one object, preserve their shared position, and assign the colors.
2. Keep the decorated face on the build plate. Use the A1 0.4 mm nozzle configuration and a 0.20 mm layer height.
3. The project uses four walls, five top and bottom layers, 15% gyroid infill, Arachne walls, and a prime tower, with supports disabled. Select your actual build plate; the included setting is Textured PEI.
4. Check the sliced preview for all white sections, clear gaps, and the socket roof before printing. Size the tree leader to the socket and use the rear tie holes where additional retention is useful.

The owner successfully printed the earlier tube-only face from the two material STLs. The white backing bands and recessed signature are newer changes; that earlier print does not establish the revised face's physical performance. The included validation records the geometry and the scope of the slicer checks.

## A Christmas landmark since 1949

The Star’s connection to Christmas is original to its story. The Roanoke Merchants Association commissioned it for the **1949 Christmas season**, and it was first illuminated on **November 23, 1949**. The seasonal attraction became a lasting landmark above the city. The City of Roanoke records its height as **88.5 feet**. [City of Roanoke history](https://www.roanokeva.gov/1329/Roanoke-Star)

Roy C. Kinsey Sign Company built the sign, working with Roanoke Iron & Bridge Works on its steel structure. Historical accounts credit Robert Little with the design. An anniversary interview describes the full-scale Star being assembled flat on the ground at Roanoke’s airport, taken apart, transported up Mill Mountain, and erected on its tower. [1982 historical account, pp. 88–90](https://www.virginiaroom.org/digital/files/original/67/6354/JHSWV_11_02_1982.pdf), [WDBJ interview preserved by Virginia Tech](https://scholar.lib.vt.edu/VA-news/WDBJ-7/script_archives/99/1199/112899/112899.m.htm)

The landmark contains **three nested structural stars** carrying multiple neon sets. In the all-white views studied for this project, six prominent illuminated contours form three close pairs. That layered pattern is the basis of the topper’s face. [City description](https://www.roanokeva.gov/1329/Roanoke-Star)

## Research behind the model

The design draws on municipal records, historical accounts, archival finding aids, and **more than fifteen photographs and views**. A reference photograph of another printed interpretation helped establish the desired individual-tube appearance. The geometry and print construction were developed for this project.

**Photographs and perspective.** City images, aerial photographs, Wikimedia sources, and Ben Schumin’s close-up series were compared across viewpoints and lighting modes. Observation-deck photographs look upward, which compresses vertical spacing and changes apparent angles. Oblique views also distort the spacing from one side to the other. The project’s [perspective audit](research/ACCURACY_AUDIT.md) examines those effects and explains why matching one photograph cannot establish the landmark’s physical dimensions.

**Proportions and angles.** The documented 88.5-foot height anchors the research. Published widths differ: the Smithsonian inventory records approximately **88.5 × 84.5 feet**, while the City’s art catalog lists **1062 × 1200 inches**, equivalent to 88.5 × 100 feet, without a dimensioned elevation clarifying the axes. The model uses the 84.5/88.5 proportion as its photographic reconstruction basis. Its [angle worksheet](research/ANGLE_WORKSHEET.md) and [coordinate table](research/candidate_angles.csv) make the resulting geometry inspectable. [Smithsonian inventory](https://siris-artinventories.si.edu/ipac20/ipac.jsp?booklistformat=&profile=ariall&session=1761P49582NO9.272492&uri=full%3D3100001~%21334963~%210), [City art catalog](https://www.artworkarchive.com/profile/roanoke-arts/artwork/roanoke-star)

**Parallel tube paths.** A shared set of edge directions governs all six outlines. Constant inward offsets preserve parallel spacing along straight runs and through the interior corners. The [construction notes](research/PARALLEL_PATH_CORRECTION.md) document the offset distances and include a [before-and-after corner detail](research/parallel_path_comparison.png).

**Individual neon sections.** Close photographs show interruptions along straight runs and illuminated bends around corners. A high-resolution Commons photograph provided observations of breaks near the quarter points of one long run. Those observations informed the rounded sections and dark gaps; symmetry and repetition complete the model’s pattern. The **130-section count describes this print**, rather than an inventory of the landmark’s glass tubes or electrical circuits. [Tube-layout study](research/TUBE_LAYOUT.md), [recorded image observations](research/tube_joint_observations.json), [Schumin close-up series](https://www.schuminweb.com/photography/roanoke-star-night/), [Commons photograph](https://commons.wikimedia.org/wiki/File:Mill_Mountain_Star_Neon_Lights.JPG)

**Archival research.** The original-plan search examined the Virginia DHR National Register nomination, NPS asset records, the City’s public Engineering plan repository, Virginia Room finding aids, and restoration-report references. No original dimensioned Star elevation or shop drawing was located in the material reviewed. The [archive search record](research/PLAN_SEARCH.md) identifies the collections examined and distinguishes document contents from catalog listings.

This is a **photo-informed interpretation of the Roanoke Star**. Exact landmark angles and the complete neon-joint schedule are not established by the available sources; the documented coordinates and section counts specify the model itself.

## Geometry validation

The current material meshes are checked against the construction profiles and complete outer solid. The included reports record:

- Watertight material meshes with consistent winding and no duplicate or zero-area triangles.
- One connected dark body and 133 white solids—130 tube sections and three backing bands—that together form a single connected print.
- Zero non-adjacent triangle-intersection candidates in either material mesh.
- Material coverage matching the complete outer solid within export precision.
- Clearance for the nominal tapered socket mandrel and geometry within the chosen 45° overhang limit.
- The engraved lettering's actual floor, depth, and clearance from the socket, checked against its construction footprint.
- A standard 3MF geometry round trip, two filament definitions, and explicit part-to-filament assignments.

See the [mesh report](print_in_place/mesh_validation.json) and [intersection results](print_in_place/self_intersections.json) for the measurements. The [scene/export status](print_in_place/scene_export_validation.json) distinguishes the current exports from the saved Blender checkpoint. The [rebuild guide](scripts/REBUILD.md) documents profile generation, Blender construction, export, and validation.

## Explore the project

| Directory | Contents |
|---|---|
| [`print_in_place/`](print_in_place/) | A1 model, material meshes, Blender scene, rendered views, and validation reports |
| [`scripts/`](scripts/) | Reproducible geometry construction, packaging, and checks |
| [`research/`](research/) | Sources, photograph analysis, angle measurements, and archival research |

`main` contains the integrated, single-print design shown above. Superseded models and development drafts are retained in Git history.

## Credits and reference material

Project by [christopherrbrown3](https://github.com/christopherrbrown3). Historical and visual references include the City of Roanoke, Virginia DHR, Roanoke Public Libraries’ Virginia Room, the Smithsonian inventory, Virginia Tech’s WDBJ archive, Ben Schumin, and Wikimedia Commons contributors.

Reference photographs and archival documents are linked from their original publishers. This repository includes the project's model renders, geometry diagrams, research notes, and source attribution; it does not redistribute reference photos or photo-based crops and overlays. See the [source credits](research/SOURCES.md), [photograph inventory](research/GEOMETRY_REVIEW.md), and [supplied-reference provenance](research/user_provided/PROVENANCE.json). Third-party materials retain their respective copyrights and license terms.

## Model license

The original model design, geometry data, and downloadable Blender, STL, and 3MF files are licensed under **[Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)**. You may share and adapt the model for noncommercial purposes with attribution; adaptations must use the same license. See [LICENSE](LICENSE) for the complete terms.

Suggested attribution: **Roanoke Star Tree Topper by [christopherrbrown3](https://github.com/christopherrbrown3) · [christopherbrown.io](https://christopherbrown.io) · CC BY-NC-SA 4.0**. Identify any changes when sharing an adaptation.

This model license does not relicense third-party reference materials or the historical landmark itself. The back of the model carries recessed `christopherbrown.io` lettering.
