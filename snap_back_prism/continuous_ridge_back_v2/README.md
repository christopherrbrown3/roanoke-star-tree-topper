# Continuous Ridge Back v2

This revision keeps the approved continuous-ridge back and doubles only the outward projection of its six fixed tabs. The v1 tab projection was 1.05 mm from the ridge; v2 is 2.10 mm. Each tab remains 8 mm wide and aligns with one of the six catch windows in the existing `spacing_v3` shell.

## Files

- [Bambu Studio A1 project](continuous_ridge_back_A1.3mf)
- [Printable STL](continuous_ridge_back_print.stl)
- [Blender scene](continuous_ridge_back.blend)
- [Inside view](previews/back_inside_direct.png)
- [Tab detail](previews/fixed_tab_detail.png)
- [Additional inside view](previews/back_inside.png)
- [Build parameters](parameters.json)
- [Revision comparison](revision_comparison.json)
- [Mesh validation](mesh_validation.json)
- [Bambu slice audit](slicer_validation.json)
- [Slice audit script](audit_slices.py)

## Fit geometry

The six window openings in the existing shell are 9.2 mm wide along the tangent and span Z=52.2–55.1 mm. Each tab is centered at the opening's actual center (the source clip anchor plus 8 mm along its tangent), leaving 0.6 mm clearance on each side. The longer nose engages 1.55 mm into the shell wall and extends 0.35 mm past the shell's outer surface. A small trim caps the outer boss at Z=55.0 mm, leaving 0.1 mm below the window top while keeping the ridge and tab ramps intact.

The tab pieces are fixed and integral with the ridge. The design has no hinges, sliding catches, or spring-relief slots. Installation still depends on manually flexing the PLA back and/or shell. The first printed version did not lock reliably, which prompted this projection change. On 2026-10-16, the owner confirmed that printed v2 locks onto the existing `spacing_v3` front. This confirms fit for the owner's printed parts; no cycle count, retention-force, or long-term durability test was reported.

## Unchanged back geometry

The 1.6 mm back plate, 0.8 mm-thick by 6 mm-deep inset ridge, ridge-to-shell gap, 100 mm bottom mouth, eight vents, and recessed `christopherbrown.io` mark are retained from v1. The ridge and marked-plate construction meshes match v1 byte-for-byte. The ridge stops at the two edges of the existing mouth.

## Checks and print settings

The exported back is one watertight connected solid. Its assembly check uses the unchanged `spacing_v3/front_shell_fused.stl`; all six tabs have zero modeled intersection with the shell. These checks establish rigid seated clearance and alignment. The owner's printed v2 fit test confirmed that the tabs lock to the existing `spacing_v3` front; insertion force, cycle life, retention-force, and long-term durability were not measured.

Bambu Studio sliced the single back on the A1 0.4 mm profile at 0.20 mm layers, outside face down on Textured PEI, with supports disabled. The native slice is 38 layers / 7.6 mm, estimated at 58m54s and 30.78 g. The slice audit found extrusion paths in each of the six tab cross-sections. The owner subsequently printed v2 and confirmed the fit and lock on the existing `spacing_v3` front; this does not establish cycle life or long-term durability.

The rebuild guard hashes only the committed geometry, profile, template, and packaging files that the build scripts read. See `preservation_before.json` and `preservation_validation.json` for that explicit input list and result.
