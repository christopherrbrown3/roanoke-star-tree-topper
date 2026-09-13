# FDM tube-segment design audit

**Historical design deliberation.** The current implementation is documented in [the A1 design report](../print_in_place/DESIGN_REPORT.md). The cassette and screw proposals below were superseded by the no-assembly requirement. The later print-in-place recommendation is a design study; actual dimensions and validation are in `print_in_place/`.

This is a manufacturing recommendation for the requested revision: six individually visible white tube runs with rounded ends and dark gaps, in the original two-color physical topper. It is based on the current profile and build scripts; it does not change the model.

## What the current design tells us

`prepare_topper_profiles.py` describes six independent closed paths. The prepared white rail is 1.8 mm wide, and the current dark base is a 3.2 mm plate with a 3.8 mm pocket floor and a 5.0 mm channel-surround top. The measured minimum visible gaps are 1.45, 0.93, and 1.52 mm within the three close pairs, followed by 3.47 and 4.06 mm between pairs. The existing export therefore has the right six-loop topology and useful clearances, but each loop is one continuous white outline.

The current straight-insertion check only proves that the finished solids do not overlap. It does not prove that a continuous carrier can be put into a completed dark face. A carrier hidden under dark bridges must have a real open insertion side. Front insertion would require threading a closed, non-flexible loop under many bridges and would be a poor assembly path.

## Recommended architecture: six rear-loaded cassettes

Use four layers of function, while keeping the same two visible material groups:

1. **Rear backing plate, dark, 3.2 mm.** This is the existing rigid star plate and carries the removable tree mount interface.
2. **Front mask, dark, 2.4 mm.** It supplies the visible dark field, individual windows, and the outside border. It is a separate print so its rear recess is genuinely open during assembly.
3. **Six white carrier cassettes, one per traced path.** Each cassette is one rigid planar loop, rather than a pile of loose dashes. It has a continuous 1.8 mm wide, 0.8–1.0 mm high hidden spine, with raised white capsule portions at the visible locations. The spine connects every capsule and is captured between the mask and the rear plate.
4. **Removable dark tree mount.** Retain the current tapered socket/flange and its four screw attachment. It remains independent of the face assembly.

The carriers load from the back of the front mask along the face normal. They do not slide along the star path and do not pass under a closed front bridge. The front mask is laid face-down on a flat surface, a carrier is lowered into its open rear recess while its capsules pass through the matching windows, and the rear backing is then screwed on. Removing the backing reverses the operation and makes the white parts serviceable.

### Layer stack and dimensions

Use these nominal dimensions in the next model iteration:

| Feature | Nominal value | Reason |
|---|---:|---|
| Rear backing | 3.2 mm | Retains current stiffness and mount relationship |
| Front mask | 2.4 mm | Enough face thickness for a clean dark field and window walls |
| Shared rear recess per close pair | 1.0 mm deep, 5.4–5.8 mm wide | Avoids a fragile 0.3–0.5 mm wall between paired carrier pockets |
| White hidden spine | 1.8 mm wide × 0.8–1.0 mm high | Two .4 mm lines minimum; rigid enough to handle as a cassette |
| White visible capsule | 1.7–1.8 mm wide | Preserves the current luminous line scale |
| Capsule window | 2.3–2.4 mm wide | 0.25–0.35 mm side clearance; use 2.3 mm where the two lines are closest |
| Capsule top relative to mask | 0.1–0.2 mm recessed | Prevents snagging while retaining a white face and slight shadow edge |
| Minimum end gap | 1.2 mm; target 1.5 mm | Remains visibly dark after elephant foot and string cleanup |
| Rear carrier vertical clearance | 0.15–0.25 mm | Allows insertion after normal FDM variation |
| Carrier locating clearance | 0.25–0.35 mm per side | Same practical range as the current 0.30 mm pockets |

The close pair windows need more care than the broad inter-pair gaps. With the current 0.93 mm minimum white-to-white gap, 1.8 mm capsules and 2.3 mm windows leave about 0.43 mm of dark mask between neighboring windows. That is a single reliable .4 mm nozzle wall if the slicer is allowed to keep it as a wall. A 2.4 mm window would leave only about 0.33 mm and should be reserved for locations where a wider opening is essential. Do not globally widen every window.

Use one shared rear recess for each close pair. This makes the underside of the front mask substantially stronger than six narrow, nearly touching channels. The individual windows on the front still define the six separate white paths. Add two or three small asymmetric locating nubs or shallow stops per cassette, hidden in the recess, if a dry fit allows lateral movement; keep their side clearance 0.3 mm and do not make them snap-fit tabs.

## How the segmented white parts work

Each white cassette is a single printable object with two heights. The continuous low spine is present around the whole traced path, including the dark gaps. At each visible position, a rounded capsule rises from the spine and reaches into its front-mask window. The low spine is behind the mask's opaque dark bridges, so it cannot be seen face-on; only the separated capsule tops are seen. This provides actual visible white dashes while retaining one handled part per traced loop.

Make each capsule a 2D capsule (straight body with two semicircular ends, radius approximately half the 1.7–1.8 mm width). Use a 1.5 mm nominal gap between capsule ends and move the end back 0.5–1.0 mm from a sharp traced vertex. The hidden spine remains continuous through corners. Segment long edges into roughly 14–22 mm visible portions and shorter edges into 8–14 mm portions, always enforcing the 1.2 mm minimum gap. The exact count may vary by path; the handling count remains six cassettes, not the number of visible capsules.

Print the cassette with the visible capsule faces upward. The capsule footprint is present from the first layer, and the narrower low spine simply terminates at the capsule ends; this produces no unsupported horizontal shelf. Use a small 0.1–0.15 mm top edge break only if it survives the narrow capsule windows. The rounded ends should be in the XY outline, not made by a fragile post-print bevel.

## Front mask and assembly path

The front mask should be one separate dark part with its capsule windows cut through the 2.4 mm face. Its rear recess opens completely toward the rear, and its recess roof is interrupted by the windows. This is the geometric condition that makes normal rear loading possible.

Print the front mask with the finished front face against a smooth build plate. This gives the face a clean finish and leaves the rear recesses upward and support-free during printing. Add a 0.2 mm lead-in chamfer on the rear side of each window; leave the front edge square or with only a 0.1 mm break so the dark border remains crisp. Apply first-layer horizontal expansion compensation or deburr the windows after printing, because first-layer flare is comparable to the 0.25–0.35 mm clearance.

Assembly order:

1. Print and deburr the front mask, six white cassettes, and rear backing. Test one capsule in one window before preparing all parts.
2. Put the front mask front-face down on a protected flat surface. The open rear recess is now facing upward.
3. Lower each complete white cassette into its pair recess from the rear. Match the capsules to their windows; do not force a carrier sideways through the windows. The low spine seats on the rear-plane datum and the capsule portions pass through the open windows.
4. Fit the rear backing with a shallow perimeter tongue/groove. Use four or six M2.5 self-tapping screws into dark rear bosses, with 0.3 mm through-hole clearance. The backing presses the carriers into the recess and traps them without glue. A glued seam is acceptable only if serviceability is unimportant.
5. Attach the existing removable tree mount to the backing with its current screw/flange arrangement. Mount retention and the tree leader ties remain separate from the face cassette assembly.

The rear backing should be removable because it is the only safe way to remove a carrier without bending a 200 mm loop. Do not make the rear plate the first permanently glued closure, and do not require the user to insert a closed carrier from the front.

## Printing and handling assessment

The architecture is support-free at the stated 0.4 mm nozzle and 0.2 mm layer height:

- Rear backing: flat on its rear face, 4 perimeters, 5 top/bottom layers, 15% infill.
- Front mask: front face on the bed, 4 perimeters, 5 top/bottom layers, no support. Window holes are open; the rear pair recesses are printed upward.
- White cassettes: flat, visible face upward, 4 perimeters or 100% infill in the narrow geometry, no support. The 0.8–1.0 mm low spine is two lines at minimum and is protected after assembly.
- Tree mount: keep the existing large-mouth-on-bed orientation, preferably PETG or a tough PLA+.

The white cassettes should be lifted from the bed with a broad scraper while supported by a thin sheet or tray. Their low spine is protected once the rear backing is fitted, but it is still the vulnerable step during handling. A full loop is more manageable than 10–30 loose dashes; six flat cassettes can be labeled by size and nested in a shallow tray during assembly.

The mask face is likely to be the tolerance limiter. Verify a small coupon containing the closest pair, one 2.3 mm window, one 1.8 mm spine, and a 1.5 mm capsule gap before exporting the complete face. At the stated clearances, a .2 mm layer profile should work, but first-layer flare, cooling, and slicer line-width settings can close the 0.43 mm dark wall. If the coupon closes, reduce capsule/window width locally or increase the traced close-pair separation by the smallest evidence-supported amount; do not remove the dark bridge globally.

## Tradeoffs and alternatives

This design adds a separate dark front mask and makes nine physical prints (rear backing, front mask, mount, and six white cassettes). The extra dark seam and assembly screws are the price of a real rear insertion path and serviceable white carriers. All dark parts remain one color group and can be printed together in one dark filament batch.

The simpler alternative is six independent segmented white chains placed directly into the current front pockets and held with adhesive. It has fewer dark parts, but every capsule gap becomes a loose handling feature, adhesive has to be applied without smearing the dark face, and a damaged dash requires front access or disassembly. Six continuous white loops are easiest to print and assemble, but they cannot show the requested tube gaps. Individual loose capsule inserts should therefore be reserved for a very small prototype or a coupon, not the final 200 mm topper.

## Recommendation

Adopt the six rear-loaded cassette architecture: a 3.2 mm dark rear backing, a 2.4 mm dark front mask with through-windows, and six white continuous-spine carriers with 1.7–1.8 mm rounded visible capsules and 1.2 mm minimum gaps. Use shared rear recesses for each close pair, 0.25–0.35 mm side clearances, and a screwed removable backing. This meets the two-color/no-LED requirement, gives each white dash a physically rounded end and a visible dark gap, and provides a credible support-free insertion path that does not depend on threading a buried carrier under front bridges.

## LATEST — superseding print-in-place A1 architecture

This section supersedes the earlier cassette, face-screw, and separate-mask recommendation. The new requirement is one fused print with no post-print assembly. The most robust choice is a single dark structural body with white capsule inlays in its first millimetre, followed by a dark backing and an integral rear sleeve. A Bambu Lab A1 has a 256 × 256 × 256 mm build volume and an included 0.4 mm nozzle, so the approximately 191 × 200 mm star fits with roughly 28–33 mm of bed margin in the two face directions. This is confirmed in the [official A1 technical specifications](https://bambulab.com/pl/a1/tech-specs) and [official A1 quick-start guide](https://cdn1.bambulab.com/documentation/quick-start-f507128172bdf/Quick%20start%20guide%20-%20A1%20combo-EN.pdf).

### Face and print sequence

Print the star face-down. Make the white runs actual rounded capsule islands, 1.7–1.8 mm wide, with a 1.2 mm minimum dark gap and a 1.5 mm target gap. Make the dark face field around them in the same first approximately 1.0 mm of height, then continue upward with the dark structural backing to a total face/body thickness of 4.0 mm. White and dark are therefore fused at the 1.0 mm interface; no carrier, adhesive, screw, or later insertion step exists. The visible front is the smooth build-plate side after the part is turned over. The capsule ends are rounded in XY, so the first-layer color boundary itself supplies the neon-like rounded appearance.

On an A1 with AMS Lite, represent the white islands and dark body as two color regions in the same object. The tool changes occur in the face layers and the remainder is dark. With a single filament path, achieving white and dark in the same first layer would require manual color changes and is not a reliable unattended workflow. The geometry itself is still one fused part.

Keep the dark perimeter and backing continuous under every white capsule. Do not create a continuous white tube web in the first layer: it would show through the dark gaps. Each capsule only needs dark material around it and dark backing behind it for fusion. Use four dark perimeters where the shape allows, and let the 1.7–1.8 mm white capsules print as solid narrow geometry. A 0.2 mm layer profile is appropriate; use a 0.2 mm first-layer horizontal expansion test because the closest existing pair gap is only 0.93 mm.

### Integral sleeve: straight-Y house bore

Keep the sleeve axis straight along star `Y`, from `y = -32 mm` to `y = +48 mm`, and place its center depth at `z = 23.4 mm` behind the face. Let `r(y)` taper linearly from 17.0 mm at the lower mouth to 11.0 mm at the upper end. Thus the inner bore has a 34 mm lower circular-mandrel equivalent and a 22 mm upper circular-mandrel equivalent.

Use the following inner cross-section in `(x, z)` at each `y`, with `c = 23.4` and `r = r(y)`:

```text
(-r, c-r)
(+r, c-r)
(+r, c + (sqrt(2)-1)r)
( 0, c + sqrt(2)r)
(-r, c + (sqrt(2)-1)r)
```

The bottom is flat, the side walls are vertical, and each roof facet has slope 1:1, exactly 45 degrees. This house/teardrop opening contains a circle of radius `r` centred at `z = 23.4`; the sloping roof is tangent to that circular clearance at the 45-degree points. It therefore preserves the requested equivalent clearance without asking the slicer to print a horizontal circular ceiling.

Offset the outer sleeve by a 2.4 mm wall. For a lower or upper radius `r`, use outer points:

```text
(-(r+2.4), 4.0)
( +(r+2.4), 4.0)
( +(r+2.4), c + (sqrt(2)-1)r + 2.4(sqrt(2)-1))
( 0, c + sqrt(2)r + 2.4sqrt(2))
(-(r+2.4), c + (sqrt(2)-1)r + 2.4(sqrt(2)-1))
```

At the lower mouth (`r = 17`) this gives an inner width of 34.0 mm, outer width 38.8 mm, inner bottom `z = 6.4`, and outer apex `z ≈ 50.83`. At the upper end (`r = 11`) it gives an inner width of 22.0 mm, outer width 26.8 mm, inner bottom `z = 12.4`, and outer apex `z ≈ 42.35`. The outer bottom is `z = 4.0` at both ends, so the sleeve's bottom floor grows from 2.4 mm to 8.4 mm as the bore tapers. That floor is intentional: it bonds the entire sleeve footprint to the top of the 4.0 mm star backing and prevents a long unsupported bridge.

The sleeve's lower and upper outer widths fit inside the existing star silhouette at `y = -32` and `y = +48`. The maximum 38.8 mm sleeve width and approximately 50.8 mm rear depth remain within the A1's 256 mm height envelope when the 191 × 200 mm star is printed flat. The sleeve is hidden in the front view by the opaque star body; its rear roof and floor are visible only from behind.

### Overhang and support audit

This cross-section is support-free under the stated print orientation:

- The star face is the bed contact surface. The first layers have no underside cavities.
- The sleeve floor is continuously fused to the 4.0 mm backing, so the growing lower floor is not a bridge.
- The sleeve sides are vertical.
- Both inner and outer roof facets are 45 degrees in the X–Z section. The radius taper is only 6 mm over 80 mm (4.3 degrees); the roof apex changes about 8.5 mm over 80 mm (6.1 degrees), so the combined roof plane is only about 45.3 degrees from vertical and remains a printable near-45-degree plane rather than becoming a horizontal ceiling.
- The mouth and end faces are open in Y. No support is required inside the bore, and a tree leader is inserted after printing through the lower mouth.

Use a 0.2 mm lead-in chamfer only on the lower bore mouth if the slicer preserves the 34 mm minimum opening. Do not round the roof into a circular ceiling; a circular horizontal bore is the feature most likely to create a sagging underside.

If the existing transverse tie holes are retained, make each 4.0 mm opening a diamond/teardrop in its Y–Z section: 4.0 mm equivalent width, a flat lower edge, vertical short sides, and a 45-degree rising roof. Place the opening at least 2.0 mm from the inner bore roof/floor and keep its outer wall continuous. A circular horizontal tie hole is unnecessary for the basic mount and should not be added solely for visual symmetry.

### Weight tradeoff

The house bore's shell cross-section is approximately 334.5 mm² at the lower end and 385.0 mm² at the upper end because the constant `z = 4` floor becomes thick at the small end. Integrating the linear taper over 80 mm gives roughly 29.7 cm³ of sleeve material, about 36.9 g in solid PLA at 1.24 g/cm³. This is close to the current separate mount volume (25.2 cm³) but eliminates its flange, screws, and assembly interface. A local 45-degree underside relief could save material, but it would either leave the upper sleeve unsupported or require a wide web that adds back most of the saved volume. The constant-bottom sleeve is the better print-in-place tradeoff.

The 4.0 mm dark star body over the 14,149.6 mm² outer outline is approximately 56.6 cm³ before the white inlay displacement. The segmented white islands occupy about 4–5 cm³ for an 80–90% visible fraction at 1.0 mm depth. A rough fused face-plus-sleeve estimate is therefore 90.5–91.5 cm³, or about 112–113 g in solid PLA, before infill and shell reductions. This is comparable to the old assembled solid estimate while removing a separate mount part and all face hardware. Actual sliced weight will be lower and depends on the A1 profile.

### Optional C-sleeve fallback

An open-backed C sleeve could reduce the thick floor and accept a branch from the side, but it weakens the rear support, exposes the tree leader to escape, and makes the printed mount less predictable under bending. It also provides no benefit when the tree leader can enter through the lower Y mouth. Use the closed 45-degree-roof house bore as the default; consider a C opening only if a real leader geometry cannot be threaded through an 80 mm tapered passage.

The print-in-place recommendation is therefore: one 4.0 mm dark star body, white rounded capsule inlays confined to the first 1.0 mm, and one integral 80 mm straight-Y sleeve with a 34-to-22 mm circular-mandrel-equivalent house bore, 2.4 mm walls, a continuously supported flat floor, and 45-degree roof facets. This latest architecture supersedes all earlier assembly recommendations in this file.

## Attachment screw location check

The following points are in the same `(x, y)` millimetre coordinates as `final/profile_measurements.json`. I treated a capsule window as the 2.1 mm white opening around a traced centerline (1.05 mm half-width), and measured the distance from each candidate center to both that window set and the current pair-recess set. The reported clearance is the smaller of those two distances. This is a center-to-feature check; a 5 mm boss consumes another 2.5 mm of that clearance.

| Point | Pair-recess clearance | Capsule-window clearance | Nearest outer silhouette edge | Use |
|---|---:|---:|---:|---|
| `(0, -1.5)` | 9.91 mm | 10.29 mm | 41.86 mm | Primary central screw |
| `(0, 44)` | 3.29 mm | 3.44 mm | 19.10 mm | Upper central screw |
| `(-27, -42)` / `(27, -42)` | 3.55 mm | 3.70 mm | 20.09 mm | Optional middle pair |
| `(-46.5, -71.5)` / `(46.5, -71.5)` | 3.67 mm | 3.82 mm | 10.73 mm | Preferred outer pair |

For four attachments use `(0, -1.5)`, `(0, 44)`, and the symmetric outer pair at `(+/-46.5, -71.5)`. This puts two screws in the central dark field and two far apart near the lower outer arms, which is the strongest simple anti-warp pattern found in the current silhouette. For six attachments add the symmetric middle pair at `(+/-27, -42)`.

The old pilot points `(+/-21, 13)` and `(+/-21, 23)` are poor locations for this faceplate: their nearest current pair-recess clearance is only about 0.21 and 0.42 mm respectively, and they sit inside the capsule/window exclusion. Do not reuse them for the new mask/backing joint.

Use a 2.9 mm rear clearance hole and a blind 2.0 mm pilot in a rearward dark boss on the front mask. A 5.0–6.0 mm boss diameter is reasonable at the listed points, with the boss entirely behind the mask face. The outer candidates are at least 3.29–3.67 mm from the raw forbidden feature, so they do not collide with a 5 mm boss, but they cannot provide a full additional 2 mm gap from the *edge* of that boss. A strict 2 mm edge gap would require 4.5 mm center clearance; the current measured silhouette has that only in the central dark area. This is a geometry limit, not a reason to move the outer screws into the white runs. If the design requires a literal 2 mm edge gap at every boss, use two central fasteners plus a perimeter tongue/groove, or revise the carrier/window geometry first.

### Face-stack mass estimate

For a comparable estimate, the current outer dark outline area is 14,149.6 mm², the three pair recesses total 8,914.9 mm², and the six continuous rail area is 5,268.0 mm². Assuming segmented windows expose about 80% of that rail area, the dark volumes are approximately:

- **Recommended 3.2 mm rear plate + 2.4 mm front mask with 1.0 mm rear recess:** 60.2 cm³, or about 74.7 g in solid PLA at 1.24 g/cm³. This includes through-window volume removal and the shared pair recesses, but excludes small screw bosses and holes.
- **Comparison 1.6 mm rear plate + 3.0 mm front mask with 1.2 mm rear recess:** 41.7 cm³, or about 51.8 g in solid PLA, before local bosses.

The recommended stack is therefore about **18.5 cm³ / 22.9 g heavier** in dark material. A 6 mm diameter boss that thickens a 1.6 mm rear plate locally to 3.2 mm adds only about 0.27 cm³ (0.34 g) for six bosses, so it does not change the comparison materially. Across a plausible 75–90% visible-window fraction, the stack difference remains about 18.3–18.8 cm³, or 22.7–23.3 g. The estimate is for face components; the tree mount and the white carrier mass are unchanged by this comparison.
