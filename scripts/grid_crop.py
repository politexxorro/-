"""Crop a region of a reference, upscale 3x and draw a 20px coordinate grid (for picking sample points)."""
import sys
from PIL import Image, ImageDraw

f, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
s = 3
im = Image.open(f).convert('RGB').crop((x0, y0, x1, y1)).resize(((x1 - x0) * s, (y1 - y0) * s), Image.NEAREST)
d = ImageDraw.Draw(im)
for x in range(x0 - x0 % 20 + 20, x1, 20):
    d.line([((x - x0) * s, 0), ((x - x0) * s, im.height)], fill=(0, 255, 0) if x % 100 else (255, 0, 0), width=1)
    if x % 100 == 0:
        d.text(((x - x0) * s + 2, 2), str(x), fill=(255, 0, 0))
for y in range(y0 - y0 % 20 + 20, y1, 20):
    d.line([(0, (y - y0) * s), (im.width, (y - y0) * s)], fill=(0, 255, 0) if y % 100 else (255, 0, 0), width=1)
    if y % 100 == 0:
        d.text((2, (y - y0) * s + 2), str(y), fill=(255, 0, 0))
im.save(out)
