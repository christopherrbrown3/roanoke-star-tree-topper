The original connector print stopped short of seating or required excessive force, according to the user's physical test. These two small revised samples address insertion before changing the full topper.

**Physical result:** the user reported, “They both work. Slight edge to two dots though.” The **two-dot, 0.50 mm engagement** connector is the selected profile for the [full topper revision](../two_dot/README.md). The result applies to individual connector pairs printed using A1's Generic PLA Silk profile. See [physical_fit.json](physical_fit.json).

Both use a larger cantilever latch: a 30 mm arm with a 1.6 mm width in the bending direction and an 8 mm broad hook. The original used an approximately 18 mm arm, 1.2 mm width, and 4.6 mm hook. The new guide clearance is 0.55 mm (original: 0.30 mm), with 2 mm of relief beside the arm, a 1.6 mm entry ramp, and a wider catch window. The one-dot pair has 0.30 mm catch engagement; the two-dot pair has 0.50 mm. The original had 0.45 mm engagement.

The test bases are now 48 × 20 mm, compared with 28 × 10 mm, with rounded corners, a thickened grip at the far edge, and a 1 mm bevel underneath that edge. The bevel provides a starting point for lifting after the plate cools and is flexed. These handling features are outside the mating surfaces.

Match the dots on each wall and cap. Try one dot first, then two dots. Turn the cap over so the hook points down, align the hook with the window, and press the cap over the wall. Report whether it seats fully, holds after release, and survives removal. For comparable retries, use the same filament as the test being compared.

The matching A1 project is `connector_fit_v2_A1.3mf`, with a 0.4 mm nozzle and 0.20 mm layers, without supports or a prime tower. Digital checks do not establish physical fit or holding force. The original connector, full topper, and original release files are preserved.

Bambu Studio 02.05.00.66 initially sliced the saved project successfully: **29 min 15 sec and 8.85 g of white PLA**, including startup. There are 50 layers, with a maximum height of 10 mm. See `slicer_validation.json` for the package hash and observed results.

On October 3, 2026, the user requested printing with **AMS slot A1**. Its synced profile was **Generic PLA Silk, magenta**. All four parts were assigned to that profile and re-sliced in Bambu Studio: **32 min 49 sec and 8.85 g**. The send dialog confirmed A1, and the printer accepted the job and began heatbed preheating. Bed leveling and flow dynamics calibration were enabled; timelapse was off. The saved 3MF was not overwritten with these runtime filament changes. This test uses a different filament from the original white sample, so material may also affect the physical fit result.

The research and choice of mechanism are recorded in [research.md](research.md). These are new trial dimensions, not a copy of a downloaded model or a physically proven topper latch.

Rebuild with `python3 snap_back_prism/connector_fit_v2/prepare.py`, then execute `build_blender.py` definitions through Blender MCP and call `setup()`, `build_trial('one_dot', 1, -15)`, `build_trial('two_dot', 2, 15)`, and `finish()`. Run `validate_and_package.py` locally and slice the resulting project in Bambu Studio.

Original model and adaptation: christopherrbrown3 / christopherbrown.io, CC BY-NC-SA 4.0. See the repository's `LICENSE`.
