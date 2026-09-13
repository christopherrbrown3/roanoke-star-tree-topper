# Rebuilding and validating the A1 model

The current deliverables are in `print_in_place/`. The A1 revision uses two solid material regions in one fused print and an integral mount. Bambu Studio validation is deferred at the owner's request.

Use Python 3 with numpy, scipy, Pillow, shapely, trimesh, mapbox-earcut, and manifold3d installed. The GUI build was performed in Blender 5.2.1 LTS. The new scripts resolve the repository location from `__file__`.

1. Run `python3 scripts/prepare_a1_print_in_place.py`. This reads the six candidate paths from `final/profile_measurements.json`, fits exact parallel inward offsets, generates the rounded outline and 130 segmented inlay profiles, and records dimensions and the section schedule. The dependency on `final/` preserves the traced paths, not the superseded assembly architecture.
2. Open Blender's Python console and execute the build using the actual checkout path. The build replaces the scene's objects, so use the project scene rather than an unrelated unsaved file.

   ```python
   __file__ = '/absolute/path/to/roanoke-star-tree-topper/scripts/build_a1_print_in_place_blender.py'
   exec(compile(open(__file__).read(), __file__, 'exec'))
   ```

3. In the same console, set `__file__` to `scripts/check_a1_blender.py` and execute it with the same pattern. It checks the actual Blender color meshes for non-adjacent triangle intersections.
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

# Earlier assembly candidate — historical workflow

The GUI build scripts currently contain the original workspace path in `ROOT`. Adjust it when cloning to a different location. The model is built in Blender's GUI Python console as requested; shell Python prepares 2D profiles and performs independent checks.

1. Use Python 3 with numpy, scipy, Pillow, shapely, trimesh, mapbox-earcut, and manifold3d installed.
2. `python3 scripts/prepare_topper_profiles.py` prepares the profiles from the current photographic reconstruction. Do not change the inferred landmark geometry without evidence; see `research/ACCURACY_AUDIT.md`.
3. In Blender's Python console, execute `scripts/build_roanoke_blender.py` with `__file__` set to its absolute path, then execute `scripts/finalize_roanoke_blender.py`.
4. Run `python3 scripts/canonicalize_exports.py` from the shell.
5. Execute `scripts/apply_canonical_meshes_blender.py` in the same Blender console. It returns canonicalized meshes to the scene, exports them, and reruns the self-intersection check.
6. Run `python3 scripts/validate_topper.py`, `python3 scripts/validate_assembly_paths.py`, and `python3 scripts/package_topper.py`.
7. Inspect every check result. The current self-intersection flag must reach zero through verified geometry fixes, not by suppressing candidates. Also require watertightness, correct winding, no duplicate/degenerate triangles, correct dimensions, and collision-free assembly.
8. In Blender, render the front, three-quarter and rear using `render_view` from the build script. Inspect orthographic front/side/rear and the assembled view.
9. Update the report and status to match the results, then execute `scripts/final_scene_blender.py` to embed current source/report text and save a tidy front-view scene.

On 12 September the source without the light-rail bevel was rebuilt through Blender's GUI, canonicalized, re-exported, checked, and rendered. It reports zero self-intersection candidates. The existing STL/BLEND exports now incorporate this repair. The single-print segmented model in print_in_place/ supersedes this assembly architecture.

Mesh validity and landmark accuracy are separate release criteria. A printable solid may still have incorrect proportions.
