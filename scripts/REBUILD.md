# Rebuilding and validating the A1 model

The current deliverables are in `print_in_place/`. The A1 rebuild uses included numerical profiles and does not require reference photographs. It uses two material regions in one fused print, an integral mount, three white backing bands, and recessed rear attribution. The shell scripts require Python with NumPy, Shapely, Trimesh, Manifold3D, and mapbox-earcut. The Blender build uses a locally installed Arial Bold TTF for the lettering; the font file is not distributed.

Use Python 3 with numpy, scipy, Pillow, shapely, trimesh, mapbox-earcut, and manifold3d installed. The GUI build was performed in Blender 5.2.1 LTS. The new scripts resolve the repository location from `__file__`.

1. Run `python3 scripts/prepare_a1_print_in_place.py`. This reads the six candidate paths from `research/photographic_paths.json`, fits exact parallel inward offsets, generates the rounded outline and 130 segmented inlay profiles, and records dimensions and the section schedule. The source record contains only the measured path coordinates and their provenance.
2. Open Blender's Python console and execute the build using the actual checkout path. The build replaces the scene's objects, so use the project scene rather than an unrelated unsaved file.

   ```python
   __file__ = '/absolute/path/to/roanoke-star-tree-topper/scripts/build_a1_print_in_place_blender.py'
   exec(compile(open(__file__).read(), __file__, 'exec'))
   ```

3. Run `python3 scripts/canonicalize_a1_body.py` in the shell to repair coplanar triangulation in both materials. Then execute `scripts/apply_a1_canonical_body_blender.py` in the same Blender GUI console using the `__file__` pattern. It returns both repaired meshes to Blender and re-exports them. Finally execute `scripts/check_a1_blender.py` there; it checks both actual color meshes for non-adjacent triangle intersections without adding an exclusion tolerance.
4. Run `python3 scripts/validate_package_a1.py` in the shell. It validates material coverage, the engraved lettering, overhangs, mandrel clearance, and 3MF round-trip geometry. It packages Bambu part-to-filament assignments and the A1 preset snapshot in `a1_bambu_settings.json`. The snapshot uses Bambu Studio 02.05.00.66's built-in A1 and Generic PLA presets with this project's documented process settings. Inspect the reports; successful execution is required.
5. Render the previews in the same Blender console:

   ```python
   render_view('front.png', (0, 0, -440), (0, 0, 0), 234)
   render_view('three_quarter.png', (245, 100, -360), (0, 0, 12), 248)
   render_view('rear.png', (150, 75, 390), (0, 0, 18), 248)
   render_view('rear_detail.png', (47, 23, 220), (47, 23, 3.7), 62)
   render_view('side.png', (440, 0, 22), (0, 0, 22), 234)
   ```

6. Inspect all five images. Open the generated 3MF as a project in Bambu Studio and confirm filament 1 on the dark body and filament 2 on the white face. Confirm that the process retains four walls, five top and bottom layers, 15% gyroid infill, Arachne, and supports disabled. Slice and inspect the first five layers, both lower interior corners, the transition to the dark body, and the socket roof. Export G-code locally through File → Export → Export G-code; no printer connection or print command is needed. Run `python3 scripts/check_a1_sliced_gcode.py /path/to/export.gcode --output /path/to/checks.json` to check actual process values and model extrusion by color and height. Record the inspected package's SHA-256 and the separate visual observations in `print_in_place/slicer_validation.json`; the G-code audit alone does not establish which file was opened or whether the layers were visually inspected. Run `validate_package_a1.py` again to associate that evidence with the exact package. Update `print_in_place/RELEASE_STATUS.json` to match the evidence. Execute `scripts/finalize_a1_blender.py` in the GUI console using the same `__file__` pattern. It checks that scene exports match the validated STLs, embeds current reports, license, and scripts, and saves an upright front view.
7. Run `python3 scripts/sanitize_release_metadata.py` before sharing the files. It removes textual metadata from the rendered PNGs without changing their image data and replaces local home paths in the Blender file with same-length placeholders. Compressed Blender files require the `zstd` command. The script also checks the 3MF for local paths and account metadata.

The geometry-reference STL is the complete outer solid before color partitioning. A monochrome print loses the contrasting tube pattern. The two material STLs retain the identical origin and belong to one multipart object; do not auto-arrange or print them independently.

Mesh validity and landmark accuracy are separate criteria. Changes to inferred paths require additional evidence; see [the accuracy audit](../research/ACCURACY_AUDIT.md). The owner's successful print used the earlier tube-only face; the band-and-lettering revision still needs a physical print to evaluate its surface quality. Strength, branch fit, and retention are not established by geometry checks.
