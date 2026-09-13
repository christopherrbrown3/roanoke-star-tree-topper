"""Draw a geometry comparison of the right lower notch; not a photo edit."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
before=json.loads((ROOT/'research/photographic_paths.json').read_text())['six_paths_mm']
after=json.loads((ROOT/'print_in_place/profile_measurements.json').read_text())['six_paths_mm']
font_path=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
def font(size):
    return ImageFont.truetype(str(font_path),size) if font_path.exists() else ImageFont.load_default(size=size)

im=Image.new('RGB',(1400,930),'#f1f3f5');draw=ImageDraw.Draw(im)
draw.text((50,30),'Parallel tubes through the lower side notches',font=font(36),fill='#172a3a')
draw.text((50,83),'Right notch enlarged below; the left correction is mirrored.',font=font(22),fill='#506274')
for x0,paths,title,subtitle in [
    (50,before,'Before: independent photo traces','Up to 2.65 degrees of divergence within a pair'),
    (730,after,'After: shared parallel edge offsets','Corresponding straight edges match to numerical precision')]:
    draw.text((x0,137),title,font=font(27),fill='#172a3a')
    draw.text((x0,179),subtitle,font=font(18),fill='#506274')
    panel=Image.new('RGB',(620,610),'#182b3e');pd=ImageDraw.Draw(panel)
    # Identical metric crop and scale in each panel. The continuous strokes show
    # the row geometry; actual model tube interruptions are intentionally omitted.
    def xy(point):
        x,y=point
        return ((x-5)*13.0,(9-y)*13.0)
    for path in paths:
        pts=[xy(p) for p in path+path[:1]]
        pd.line(pts,fill='#f2f1ea',width=23,joint='curve')
    im.paste(panel,(x0,215))
draw.text((50,850),'Continuous tube rows shown for comparison; section breaks omitted.',font=font(21),fill='#34495e')
draw.text((50,882),'The correction verifies model parallelism. Landmark angles and absolute spacing remain unverified.',font=font(19),fill='#506274')
im.save(ROOT/'research/parallel_path_comparison.png')
