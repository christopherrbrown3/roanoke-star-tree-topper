# Bambu A1 two-color slicer setup

Research date: 2026-09-12

Scope: local, offline preparation and validation for one face-down Roanoke Star tree topper print on a Bambu Lab A1 with a 0.4 mm nozzle and AMS Lite. No printer connection, print submission, user-setting mutation, or model edit was performed.

## Result

Use Bambu Studio's GUI for the final slice. The installed macOS CLI is not a reliable route on this host: `--help` works, but `--info`, `--slice 0` on the existing 3MF, and `--slice 0` on an STL all exit with status 139 (SIGSEGV) after `Initializing StaticPrintConfigs`. The result directories remain empty. This agrees with BambuStudio's open macOS CLI segmentation-fault report for the same command family: <https://github.com/bambulab/BambuStudio/issues/9968>.

The safe deterministic workflow is therefore: prepare and map the two-color project in the GUI, save a new local Bambu project 3MF, click **Slice plate** for local preview, and save the sliced project or exported G-code locally only. Do not use **Send** or **Print**.

## Installed local capability

Executable:

```text
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio
```

The app bundle is universal (arm64 and x86_64), reports `BambuStudio-02.05.00.66` in `--help`, and has bundle version `02.05.00.66`.

The app's bundled BBL profile root is:

```text
/Applications/BambuStudio.app/Contents/Resources/profiles/BBL
```

The installed local system profile mirror is:

```text
/Users/chris/Library/Application Support/BambuStudio/system/BBL
```

The current BambuStudio user config already contains an A1 0.4 setup with four filament slots. This is evidence that the profile is locally available; it is not a reason to edit that config.

## Exact A1 profiles

Use these names in the GUI:

| Role | Profile | Local evidence |
|---|---|---|
| Printer | `Bambu Lab A1 0.4 nozzle` | `BBL/machine/Bambu Lab A1 0.4 nozzle.json`; `printer_model` is `Bambu Lab A1`, `printer_variant` is `0.4`, `nozzle_diameter` is `0.4`, `printable_height` is 256 mm, and the inherited bed is 256 × 256 mm. |
| Process | `0.20mm Standard @BBL A1` | `BBL/process/0.20mm Standard @BBL A1.json`; it inherits `fdm_process_single_0.20` and is compatible with the A1 0.4 profile. The inherited common values are 0.20 mm layer height, 0.20 mm initial layer, 2 wall loops, 3 bottom shell layers, 15% grid infill, and supports disabled. |
| Dark filament | `Bambu PLA Basic @BBL A1` | `BBL/filament/Bambu PLA Basic @BBL A1.json`; compatible with A1 0.4/0.6/0.8. Inherited material is Bambu Lab PLA with 0.98 flow ratio and 21 mm³/s maximum volumetric speed. |
| White filament | `Bambu PLA Basic @BBL A1` | Use the same known-compatible material profile, then map the physical white spool to the second AMS Lite slot. |

Other locally installed PLA profiles include `Generic PLA @BBL A1`, `Bambu PLA Matte @BBL A1`, `Bambu PLA Tough @BBL A1`, `Bambu PLA Silk @BBL A1`, and `PolyLite PLA @BBL A1`. For this small two-material transition, two instances of the same Bambu PLA Basic profile give the clearest compatibility baseline and avoid introducing a third material family. The machine profile's `default_filament_profile` is `Bambu PLA Basic @BBL A1` and its `default_print_profile` is `0.20mm Standard @BBL A1`.

The common A1 process profile has `enable_prime_tower: 1`. Keep the prime tower enabled for the first validation slice. The model changes color only in the first five 0.20 mm layers, but the nozzle still needs a clean dark-to-white and white-to-dark transition; reducing purge before inspecting the Preview is not deterministic.

## Recommended GUI sequence

1. Launch Bambu Studio and choose `Bambu Lab A1`, `0.4 mm nozzle`, and the standard nozzle variant. Keep the work offline and skip any device or cloud action.

2. Open the final one-piece two-color project 3MF. It should contain one build plate and the dark body/mount plus white front inlay volumes. If the project is a standard 3MF with only per-face `displaycolor` values, use the import color dialog to map the two colors explicitly and then save it as a new Bambu project. BambuStudio 2.5 has open reports that standard 3MF color import can convert object colors into Color Painting or mis-handle partially colored meshes, so verify the result in Preview: <https://github.com/bambulab/BambuStudio/issues/9666> and <https://github.com/bambulab/BambuStudio/issues/9629>.

3. In **Prepare**, select the `0.20mm Standard @BBL A1` process. Confirm the model is face-down: the colored front is on the build plate, the integral tapered rear mount rises from the back, and no assembly parts are present.

4. In the object/part list, map the dark solid body and tapered mount to the dark PLA slot and the white capsule inlays to the white PLA slot. If a standard-3MF import does not expose unambiguous part assignments, re-import the dark and white watertight volumes as one multipart object and assign each part with the part-level Filament selector. Save this mapped state as a new project 3MF before slicing.

5. In the filament panel, use exactly two AMS Lite slots. Keep Bambu PLA Basic for both and set their displayed colors to the actual dark and white spools. Leave the generated flushing values at their material defaults for the first slice. Do not hand-edit `BambuStudio.conf`.

6. Keep supports disabled. Keep the prime tower enabled for the first validation. Any later purge reduction should be made per project only, and only after Preview confirms that white remains clean at the inlay boundary; the default prime tower is the conservative setting for this dark-under-white geometry.

7. Click **Slice plate**. In **Preview**, inspect the first five layers and the transition after layer 5:

   - layers 1–5 show both the white inlays and dark body;
   - layer 6 and above show dark only;
   - the mount remains dark and continuous;
   - no support is generated;
   - there is one plate and one printable object, with no separate printable assembly parts.

8. Use **File > Save Project As** (or the equivalent project save action) to write a new local filename such as `roanoke_star_a1_0p20_two_color_sliced.3mf`. If a standalone toolpath is needed for inspection, export it to the same local working directory. Do not click **Send**, **Print**, or a device queue action.

## Package validation after GUI save

The repository's current `final/roanoke_star_tree_topper.3mf` is only a minimal standard 3MF: it has `[Content_Types].xml`, `_rels/.rels`, and `3D/3dmodel.model`, with two `basematerials` entries and three object build items. It has no Bambu `Metadata/` directory and is therefore an assembly reference, not a sliced Bambu project.

For the new GUI-saved project, perform these local checks:

```sh
unzip -t /path/to/roanoke_star_a1_0p20_two_color_sliced.3mf
unzip -Z1 /path/to/roanoke_star_a1_0p20_two_color_sliced.3mf | sort
```

The package should contain Bambu project metadata such as `Metadata/project_settings.config`, `Metadata/model_settings.config`, and `Metadata/print_profile.config`, plus the plate preview/slice artifacts produced by the GUI. BambuStudio's own 3MF reader names these metadata paths in source: <https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Format/bbs_3mf.cpp>.

For the model XML, parse `3D/3dmodel.model` and confirm:

```text
unit="millimeter"
two material entries for dark and white
all expected dark/white volumes present as build items on one plate
no extra assembly-only light/base/mount objects
```

For a compact XML-only check without Bambu Studio, this read-only Python snippet reports the package's materials, objects, and build items:

```sh
python3 - <<'PY'
import zipfile
import xml.etree.ElementTree as ET

path = "/path/to/roanoke_star_a1_0p20_two_color_sliced.3mf"
ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read("3D/3dmodel.model"))
print("materials", [x.attrib for x in root.findall(".//m:base", ns)])
print("objects", [x.attrib for x in root.findall(".//m:object", ns)])
print("build", [x.attrib for x in root.findall(".//m:item", ns)])
PY
```

## CLI record and decision

`--help` is the only reliable local CLI probe. It documents `--slice`, `--outputdir`, `--export-3mf`, `--load-settings`, and `--load-filaments`, and states that command-line settings override loaded settings, which override settings embedded in the 3MF. The official command-line page is <https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage>.

The documented command shape would be:

```sh
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio \
  --slice 0 --debug 2 \
  --outputdir /private/tmp/bambu-a1-slice-check \
  /path/to/project.3mf
```

On this host and installed version it exits 139 before producing a result. The same happened for `--info` and for an STL input. There is also an official report of a silent CLI crash when `--load-settings` is combined with 3MF input, including the absence of a result file: <https://github.com/bambulab/BambuStudio/issues/10402>. A separate 02.05.00.66 report documents malformed model settings emitted by CLI profile loading: <https://github.com/bambulab/BambuStudio/issues/9699>. Do not build the deliverable around headless slicing until a later installed Bambu Studio version is separately tested.
