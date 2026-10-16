# Complete snap-back topper project

[Download the complete Bambu Studio A1 project](complete_topper_A1.3mf). It contains the light-diffusing front and its compatible continuous-ridge v2 rear cover as two separate build plates:

- **Plate 1 — Front shell:** two-color front, white project filament 1 and black project filament 2.
- **Plate 2 — Back plate, V2 doubled tabs:** white rear cover, project filament 1.

Open the 3MF as a project in Bambu Studio. Slice each plate independently; you can print both plates from this one file or select only the part you need. For a replacement rear cover with an existing `spacing_v3` front, the [standalone back project](../continuous_ridge_back_v2/continuous_ridge_back_A1.3mf) is also available. The [standalone front project](../spacing_v3/front_shell_A1.3mf) remains available as well.

Both plates were opened and sliced in native Bambu Studio on the A1 0.4 mm profile at 0.20 mm layers with supports off and Textured PEI plate settings. Plate 1 sliced at 292 layers / 58.4 mm, 3 h 51 min, 94.84 g including purge, and six filament changes; its purge tower is present. Plate 2 sliced at 38 layers / 7.6 mm, 58 min 54 sec, and 30.78 g using white filament only; the slicer omits the tower. No print was sent. Full structural and slicer details are in [package_validation.json](package_validation.json).

The front and back meshes are byte-identical to their separately validated source projects. `package.py` rebuilds the combined project with the standard Python library. This is a project package, not a new combined mesh; each plate retains its own source geometry and print orientation.
