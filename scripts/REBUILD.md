# Rebuilding and validating the A1 model

The current deliverables are in `print_in_place/`. The A1 rebuild uses the included numerical profiles and does not require reference photographs. The A1 revision uses two solid material regions in one fused print and an integral mount. Bambu Studio validation is deferred at the owner's request.

Use Python 3 with numpy, scipy, Pillow, shapely, trimesh, mapbox-earcut, and manifold3d installed. The GUI build was performed in Blender 5.2.1 LTS. The new scripts resolve the repository location from `__file__`.

1. Run `python3 scripts/prepare_a1_print_in_place.py`. This reads the six candidate paths from `research/photographic_paths.json`, fits exact parallel inward offsets, generates the rounded outline and 130 segmented inlay profiles, and records dimensions and the section schedule. The source record contains only the measured path coordinates and their provenance.
2. Open Blender's Python console and execute the build using the actual checkout path. The build replaces the scene's objects, so use the project scene rather than an unrelated unsaved file.

   ```python
   __file__ = '/absolute/path/to/roanoke-star-tree-topper/scripts/build_a1_print_in_place_blender.py'
   exec(compile(open(__file__).read(), __file__, 'exec'))
   ```

3. Run `python3 scripts/canonicalize_a1_body.py` in the shell to repair coplanar Boolean triangulation. Then execute `scripts/apply_a1_canonical_body_blender.py` in the same Blender GUI console using the `__file__` pattern. It returns the repaired backing to Blender and re-exports it. Finally execute `scripts/check_a1_blender.py` there; it checks both actual color meshes for non-adjacent triangle intersections without adding an exclusion tolerance.
4. Run `python3 scripts/validate_package_a1.py` in the shell. It validates the exported material meshes, their coverage of the unpartitioned outer solid, overhangs, tapered mandrel clearance, and standard 3MF round-trip geometry. Inspect the reports; successful execution is required.
5. Render the previews in the same Blender console:

   ```python
   render_view('front.png', (0, 0, -440), (0, 0, 0), 234)
   render_view('three_quarter.png', (245, 100, -360), (0, 0, 12), 248)
   render_view('rear.png', (150, 75, 390), (0, 0, 18), 248)
   render_view('side.png', (440, 0, 22), (0, 0, 22), 234)
   ```

6. Inspect all four images. Update the reports and `print_in_place/RELEASE_STATUS.json` to match the evidence. Execute `scripts/finalize_a1_blender.py` in the GUI console using the same `__file__` pattern. It checks that scene exports match the validated STLs, embeds current reports and scripts, and saves an upright front view.

The geometry-reference STL is the complete outer solid before color partitioning. A monochrome print loses the contrasting tube pattern. The two material STLs retain the identical origin and belong to one multipart object; do not auto-arrange or print them independently.

Mesh validity and landmark accuracy are separate criteria. Changes to inferred paths require additional evidence; see [the accuracy audit](../research/ACCURACY_AUDIT.md). A physical print is still needed to evaluate surface quality, strength, branch fit, and retention.
