# Mill Mountain Star Reference Pack

Fabrication-oriented research for a 3D-printable Christmas tree topper based on the Mill Mountain Star in Roanoke, Virginia.

This document is intentionally split into:

- `Source-backed facts`: directly supported by official or documentary sources.
- `Image-derived inferences`: conclusions drawn from city-hosted photos and the live StarCam imagery.
- `Conflicts / unknowns`: places where public records disagree or are too vague for exact CAD reconstruction.

## 1. Core Identity

- The landmark is the **Roanoke Star / Mill Mountain Star**, built for the 1949 Christmas season and first illuminated at **8:22 p.m. on November 23, 1949**.
- It was sponsored by the **Roanoke Merchants Association**.
- Builder: **Roy C. Kinsey** and sons **Roy Jr., Bob, and Warren** of Kinsey Sign Co.
- The steel support structure was designed by **Robert R. Little** of **Roanoke Iron and Bridge Works**.
- It was originally conceived as a Christmas-season installation but remained as a permanent city symbol.

## 2. Best Available Physical Dimensions

### Source-backed facts

- The most detailed published size record found is the Smithsonian Art Inventories entry:
  - star: **approximately 88.5 ft high x 84.5 ft wide**
  - support: **approximately 100 ft high**
  - medium: **neon, aluminum, and steel, painted**
  - base: **concrete**
- Plaque/transcribed facts carried in the Smithsonian inventory:
  - star weight: **10,000 lb**
  - steel support: **60,000 lb**
  - concrete base: **500,000 lb**
  - concrete base depth: **6.5 ft**
  - neon tubing: **2,000 ft**
  - electrical load: **17,500 watts**
  - elevation: **1,847 ft above sea level**
  - height above city: **1,045 ft**
  - visibility from air: **60 miles**
- The Virginia DHR / NRHP nomination also refers to the installation as a **70,000-lb structure** mounted on a **100-foot tower**.

### Image-derived inferences

- The star itself reads as a very large **open outline object**, not a filled face.
- The support is a **rear lattice frame** rather than a single center pole.
- The apparent overall depth of the star assembly is substantial because the outline members behave like trussed structural ribs.

### Conflicts / unknowns

- The Smithsonian inventory also lists a star depth of **2 inches**. That is almost certainly not the literal structural depth of the installed object, because city-hosted photos clearly show a deep trussed assembly with rear framing. Treat the `2 in deep` entry as unreliable for CAD.
- The Smithsonian inventory's published **88.5 ft high x 84.5 ft wide** proportion suggests a slightly taller-than-wide outline, but frontal photos make the star read as at least roughly balanced and possibly wider than tall. Until shop drawings turn up, use the published dimensions as a scale reference and the photos as the better silhouette reference.
- The exact engineering drawing set was not found in public sources, so the published height/width numbers should be treated as the best public reference, not as shop-drawing dimensions.

## 3. Canonical Shape

### Source-backed facts

- The star is described by the Smithsonian as a **five-pointed star**.
- The City of Roanoke states that the landmark is **actually three stars**:
  - a **small center star**
  - a **mid-sized frame**
  - the **largest outer frame**
- The City also states that **each frame contains three to five sets of clear neon tubes**.

### Image-derived inferences

- The composition is best understood as **three concentric, aligned, similarly shaped five-point star outlines**.
- All three stars share the same orientation:
  - **one point vertical at the top**
  - two lateral points
  - two lower points
- The three stars appear to be **coaxial and center-aligned**, not offset or rotated relative to one another.
- The shape reads much closer to a **classic pentagram-derived star outline** than to a sheriff-badge star or a broad, squat decorative star.
- The spacing between the three star outlines appears **deliberate and fairly regular**, especially around the upper arms and side points.
- The open negative space in the center is a major part of the visual identity. A filled star would not read as authentic.

### Modeling takeaways

- The later 3D topper should preserve these non-negotiables:
  - **five points**
  - **one point straight up**
  - **three nested star outlines**
  - **open center**
  - **layered outline look instead of a solid face**

## 4. Structural Form

### Source-backed facts

- The Smithsonian inventory describes the star as suspended from a **quadrilateral steel framework**.
- The DHR nomination identifies the support as a steel tower / structural framework designed by Roanoke Iron and Bridge Works.

### Image-derived inferences from city-hosted photos

- The visible support reads as a **broad rectangular rear lattice frame** with:
  - vertical side towers
  - diagonal cross-bracing
  - horizontal members
  - upper posts rising slightly above the star apex
- The star outline itself appears to be built from **structural ribs or box-truss-like members** rather than a flat sheet.
- The rear support is visually separate from the star outline and sits **behind** it, not centered through its face.
- Maintenance access is implied by the underside photos: there are dense interior members and walkable/serviceable-looking structural paths behind the illuminated outline.

### What matters for a printable miniature

- A literal full-scale copy of every rear brace is probably unnecessary at ornament scale.
- What matters visually is that the topper should hint at:
  - a **rear support scaffold**
  - a **deep outline frame**
  - the fact that the star is a **built structure**, not just a flat graphic symbol

## 5. Lighting Behavior

### Source-backed facts

- The star uses **clear neon tubing**.
- The city says the neon tubing built by Bob and Warren Kinsey is the tubing concept still used today.
- Standard display color is **white**.
- The city lights it **red, white, and blue** on:
  - Memorial Day
  - Flag Day (June 14)
  - July 4
  - September 11
  - Veterans Day (November 11)
- The DHR nomination records major restorations in **1971**, **1979**, **1987**, and **April-August 1997**.
- The 1997 work replaced the **2,000 ft of neon tubing and wiring** and repainted the star and structure.

### Image-derived inferences

- At night, the star reads as a bright, narrow, crisp line drawing suspended over the ridge.
- The visible effect is closer to **luminous linework** than to broad glowing panels.

### Modeling takeaways

- If the topper is later designed for illumination, the light should ideally read as:
  - narrow linear channels
  - bright white by default
  - optional patriotic variant

## 6. Site Position And Orientation

### Source-backed facts

- DHR location reference: **UTM Zone 17 / 594660E / 4123030N**.
- DHR describes the star as being atop Mill Mountain with the Roanoke River roughly **846 ft below** and downtown Roanoke about **1 mile to the north**.
- Roanoke Parks' Mill Mountain Park management plan places the star on the **northern side of the summit**.
- The City of Roanoke's StarCam page describes the camera view as a view of **downtown Roanoke from the Star's perspective**.

### Map-backed / image-backed inference

- A map-based coordinate used in secondary mapping sources is **37.25089, -79.93238**.
- Combining the official descriptions with the StarCam view and downtown relation, the safest orientation statement is:
  - the star faces **north toward downtown / the Roanoke Valley**
  - more precisely, the downtown bearing is roughly **north-northwest**

### Modeling takeaways

- For any later base or asymmetrical rear support treatment, assume the **display face is the north-facing side**.

## 7. Visual Evidence Captured In This Workspace

- Front / low-angle close view:
  - `output/playwright/mill-mountain-star-13602.png`
- Rear / underside support view:
  - `output/playwright/mill-mountain-star-13600.png`
- Interior underside structural view:
  - `output/playwright/mill-mountain-star-13601.png`
- Distant night silhouette:
  - `output/playwright/mill-mountain-star-13603.png`
- Broad oblique view with surrounding site and support context:
  - `output/playwright/mill-mountain-star-13604.png`
- Live StarCam outward view from the star:
  - `output/playwright/starcam-sc03.png`

## 8. Precision Notes For Later CAD Generation

- The public record is strong on **identity, construction era, lighting system, nested-star concept, support type, and headline dimensions**.
- The public record is weak on **exact member thicknesses, exact offset distances between the three stars, exact truss depth, and exact shop geometry**.
- For a historically faithful printable model, the safest approach will be:
  - lock in the **three-nested-five-point-star silhouette**
  - preserve the **open center**
  - preserve the **rear scaffold character**
  - treat exact member sizing as a reconstruction based on photos, not as a directly published dimension

## 9. Recommended Authenticity Priorities

If the goal is "reads immediately as the Mill Mountain Star" rather than "contains every real-world structural member," prioritize:

1. Three concentric star outlines instead of one.
2. An upright five-point star with a single vertical top apex.
3. Open linework rather than a filled star face.
4. A visible rear support scaffold or implied back frame.
5. White luminous-line presentation as the default visual state.

## 10. Source List

- City of Roanoke: [Roanoke Star](https://www.roanokeva.gov/1329/Roanoke-Star)
- City of Roanoke: [Mill Mountain StarCam](https://www.roanokeva.gov/1687/StarCam)
- Virginia Department of Historic Resources / NRHP nomination PDF: [Roanoke Star nomination](https://www.dhr.virginia.gov/VLR_to_transfer/PDFNoms/128-0352_Roanoke_Star_1999_Final_Nomination.pdf)
- Virginia Department of Historic Resources listing page: [Roanoke Star listing](https://www.dhr.virginia.gov/historic-registers/128-0352/)
- Smithsonian Art Inventories record: [Roanoke Star entry](https://siris-artinventories.si.edu/ipac20/ipac.jsp?aspect=Browse&index=OWNER&menu=search&profile=ariall&ri=17&session=1761P49582NO9.272492&source=~%21siartinventories&term=Mill+Mountain+Park%2C+Roanoke%2C+Virginia&uri=link%3D3100011~%21301008~%213100001~%213100002)
- Visit Virginia's Blue Ridge: [Roanoke Star attraction page](https://www.visitroanokeva.com/things-to-do/attractions/roanoke-star/)
- Roanoke Parks / Play Roanoke management plan PDF: [Mill Mountain Park Management Plan](https://www.playroanoke.com/wp-content/uploads/2023/12/Mill-Mountain-Park-Management-Plan-02.21.2006.pdf)
- Map-backed location reference: [Mapcarta: Roanoke Star](https://mapcarta.com/N4811270526)

## 11. Unresolved Questions Before Final Geometry Generation

- Exact ratio between the inner, middle, and outer star outlines.
- Exact cross-section depth and wall thickness of the outline members.
- Exact spacing and grouping of the neon tubes on each outline member.
- Exact attachment method between the star frame and the rear support lattice.
- Whether later repairs altered any visible tube spacing or framing details from the 1949 configuration.
