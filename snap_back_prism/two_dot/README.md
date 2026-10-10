This is the full topper revision using the **two-dot connector** that the user slightly preferred after both test pairs worked. The original release, one-piece prism, earlier snap-back experiment, and printed test pairs are preserved.

The front retains the same 200 mm face, original white bands, and 130 light apertures. The star remains 60 mm deep with the same 100 mm bottom opening. The back has six 30 mm cantilever arms, 1.6 mm bending width, 2 mm relief, 8 mm hooks, 0.55 mm guide clearance, and 0.50 mm engagement. The shell has matching 9.2 mm catch windows. The hook meshes are direct transforms of the tested two-dot hook.

The outside of the rear cover has an inset **christopherbrown.io** builder mark, 72 mm wide, about 6.9 mm tall, and 1.0 mm deep. It is 52% wider and 67% deeper than the original 47.5 mm / 0.6 mm mark. The lettering retains a 0.6 mm floor and clears the vents and clips. Arial Bold is converted to mesh; the font file is not distributed.

![Recessed builder mark on the outside of the back cover](previews/builder_mark_detail.png)

![Full two-dot topper](previews/assembled.png)

Bambu Studio 02.05.00.66 sliced both matching plates for the A1, 0.4 mm nozzle, Generic PLA, and 0.20 mm layers:

| Plate | Estimated time | Filament |
|---|---:|---:|
| Front shell | 3 h 39 min | 92.59 g |
| Detachable back with builder mark | 59 min 42 sec | 28.93 g |
| **Total** | **About 4 h 39 min** | **121.52 g** |

Times include startup for both plates. Neither requires supports. The front has a 4 mm brim and a purge tower for its face colors; the back has neither. The engraving appears through layer 5 at 1.0 mm, and its floor closes at layer 6 at 1.2 mm. The front package is unchanged from its previous verified slice. See [slicer_validation.json](slicer_validation.json) for package hashes and observed results. The new full topper has not been sent to the printer.

- [front_shell_A1.3mf](front_shell_A1.3mf): matching front shell, face down; navy on project filament 1 and original white bands on project filament 2.
- [snap_back_A1.3mf](snap_back_A1.3mf): matching back, outer face down with clips up; white on project filament 2.
- [two_dot_topper.blend](two_dot_topper.blend): separate editable scene built through Blender MCP.
- [parameters.json](parameters.json) and [mesh_validation.json](mesh_validation.json): dimensions, coupon comparisons, mesh integrity, assembly clearance, and package checks.
- [builder_mark_validation.json](builder_mark_validation.json): actual engraved-floor and removed-material comparisons, dimensions, and clearances.

Use both plates from this directory. The wider hooks require these matching shell windows. Map project filaments to the desired physical AMS slots before sending a full print. The successful individual test used slot A1, synced as Generic PLA Silk, magenta; the supplied full topper projects retain the original navy/white color scheme.

The individual connectors worked in the user's physical test. The assembled full topper and combined force of its six latches still need a physical check. Assembly, tree opening, and deflected-hook corridor checks are geometric checks; they do not predict force. Thermal and incandescent-light compatibility remain unverified.

![Back with the six preferred latches](previews/back_inside.png)

![Outside of the marked cover](previews/back_outside.png)

Rebuild by running `python3 snap_back_prism/two_dot/prepare.py`, then send the definitions in `build_blender.py` through Blender MCP: call `setup()` and `build_body()`, then resend the definitions, call `restore()`, `build_back()`, and `finish()`. The mark uses `/System/Library/Fonts/Supplemental/Arial Bold.ttf` on macOS; update the font path if rebuilding elsewhere. Run `validate_and_package.py`, then reimport its cleaned STLs through `restore()` and `import_canonical()`. Re-slice each changed package in Bambu Studio. To recreate previews, send `preview_blender.py` after the build definitions and `restore()`, call `setup_studio()` once, then `render_preview()` or `render_builder_mark()`.

Original model and adaptation: christopherrbrown3 / christopherbrown.io, CC BY-NC-SA 4.0. See the repository's `LICENSE`.
