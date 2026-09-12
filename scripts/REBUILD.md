# Rebuilding and validating the candidate

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

On 12 September the source without the light-rail bevel was rebuilt through Blender's GUI, canonicalized, re-exported, checked, and rendered. It reports zero self-intersection candidates. The existing STL/BLEND exports now incorporate this repair. A subsequent segmented-tube design is in progress.

Mesh validity and landmark accuracy are separate release criteria. A printable solid may still have incorrect proportions.
