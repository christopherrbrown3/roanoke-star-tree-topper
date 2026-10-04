This variant closes all **130 light windows** with a **0.4 mm white skin**, flush with the front face. At the supplied 0.20 mm layer height, each diffuser is two printed layers. The face prints down, so the skins are printed against the plate. The original white edging is 1 mm thick; only the light windows use the thinner skin.

![Unlit diffused star face](previews/assembled.png)

The 200 mm outline, 60 mm depth, 100 mm bottom entrance, and preferred two-dot connector are retained. Use the marked back from [../two_dot/snap_back_A1.3mf](../two_dot/snap_back_A1.3mf). Its inset `christopherbrown.io` mark remains 72 mm wide and 1 mm deep. The original release and earlier open-window designs are preserved.

- [diffused_front_A1.3mf](diffused_front_A1.3mf): full front shell, white on project filament 1 / AMS A1 and black on project filament 2 / AMS A2.
- [diffuser_test_A1.3mf](diffuser_test_A1.3mf): 64 × 44 × 4 mm sample at actual scale, with six complete windows and further cropped windows from the real face. A 2 mm black handling border joins the sample and provides larger edges for removal.
- [diffused_topper.blend](diffused_topper.blend): editable Blender scene containing the full topper and the test sample.
- [parameters.json](parameters.json), [mesh_validation.json](mesh_validation.json), and [slicer_validation.json](slicer_validation.json): design dimensions, independent geometric comparisons, and actual Bambu toolpath checks.

![Actual-size test face](previews/test_face.png)

![Inside of the sample showing recessed thin windows](previews/test_inside.png)

Bambu Studio 02.05.00.66 sliced the test for the A1 with a 0.4 mm nozzle and Generic PLA profiles, at 0.20 mm layers. The test uses 20 layers, no supports or brim, and a prime tower. The estimate is **50 min 59 sec and 12.84 g**, including startup and purging. G-code inspection confirms that each of the six intact sample windows receives white extrusion on layers 1 and 2 only, and no black extrusion inside it.

The test was sent on 2026-10-04 to printer **3DP-039-922** as **Star_diffuser_test_0.4mm**. Bambu's Device view confirmed the active job homing, at layer 0/20, with a 65 °C bed target. Print completion and the physical light test are pending.

The physical materials requested for this print are **white in A1 and black in A2**. The printer's saved A1 registration still reports magenta PLA Silk. For sending this test, a separate temporary print copy uses that old nominal color to make Bambu automatically select A1; its extrusion settings remain Generic PLA and its geometry is identical to the white/black project. Both physical slot assignments were verified in the send dialog. The canonical projects and previews here use white and black.

The membranes and complete front are connected to the surrounding shell. Their dimensions and exported meshes have been checked; actual brightness, diffusion, and unlit appearance require inspecting the physical sample with the intended lights. The assembled full topper and the force of all six clips remain to be tested.

To rebuild, run `python3 snap_back_prism/diffused/prepare.py`. Send `build_blender.py` through Blender MCP and call `setup()`, `build()`, and `finish()`. Run `validate_and_package.py`, then reimport the canonical meshes through Blender MCP with `restore()` and `import_canonical()`. The rear cover is imported directly from the preferred two-dot revision. Render the actual meshes with `preview_blender.py`, `setup_studio()`, `render_diffused()`, and `finish()`.

After slicing the sample, export the plate sliced file in Bambu Studio and run `python3 snap_back_prism/diffused/audit_sliced_test.py /absolute/path/to/sample.gcode.3mf`. This checks the material and layer count from actual extrusion instructions. Re-slice every changed project before printing.

Original model and adaptation: christopherrbrown3 / christopherbrown.io, CC BY-NC-SA 4.0. See the repository's `LICENSE`.
