"""Contact sheet: crop the same region from several images side by side (for face-kit review).
usage: python3 scripts/contact.py out.png x0 y0 x1 y1 cell_w img1 img2 ...
Region is in the coordinate frame of each image after resizing it to the first image's size.
"""
import sys

from PIL import Image, ImageDraw

out, x0, y0, x1, y1, cw = sys.argv[1], *map(int, sys.argv[2:7])
files = sys.argv[7:]
base = Image.open(files[0]).size
ch = int(cw * (y1 - y0) / (x1 - x0))
cols = min(4, len(files))
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * (ch + 18)), (60, 60, 60))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGBA').resize(base)
    bg = Image.new('RGBA', im.size, (235, 225, 215, 255))
    bg.alpha_composite(im)
    c = bg.crop((x0, y0, x1, y1)).resize((cw, ch))
    x, y = (i % cols) * cw, (i // cols) * (ch + 18)
    sheet.paste(c.convert('RGB'), (x, y + 18))
    d.text((x + 4, y + 3), f.split('/')[-1][:40], fill=(255, 255, 255))
sheet.save(out)
