"""Split a phase sheet (transparent PNG) into separate phases by empty alpha columns.
usage: python3 scripts/split_sheet.py sheet.png out_prefix [expected_n]
Writes out_prefix_p1.png ... trimmed to a common height (sheet height) so phases keep vertical registration.
"""
import sys

import numpy as np
from PIL import Image

src, prefix = sys.argv[1], sys.argv[2]
n_exp = int(sys.argv[3]) if len(sys.argv) > 3 else None
im = Image.open(src).convert('RGBA')
a = np.array(im)[:, :, 3]
col = (a > 40).sum(0) > 3
# find runs of filled columns, merge runs separated by < 12px gaps
runs, start = [], None
for x, v in enumerate(col):
    if v and start is None:
        start = x
    if not v and start is not None:
        runs.append([start, x])
        start = None
if start is not None:
    runs.append([start, len(col)])
merged = []
for r in runs:
    if merged and r[0] - merged[-1][1] < 12:
        merged[-1][1] = r[1]
    else:
        merged.append(r)
merged = [r for r in merged if r[1] - r[0] > 60]
if n_exp and len(merged) != n_exp:
    # fall back: cut at the n_exp-1 widest minima of column coverage
    cov = (a > 40).sum(0).astype(float)
    w = len(cov) // n_exp
    cuts = [int(np.argmin(cov[i * w - w // 3:i * w + w // 3]) + i * w - w // 3) for i in range(1, n_exp)]
    edges = [0] + cuts + [len(cov)]
    merged = [[edges[i], edges[i + 1]] for i in range(n_exp)]
    print('fallback cuts', cuts)
for i, (x0, x1) in enumerate(merged, 1):
    out = f'{prefix}_p{i}.png'
    im.crop((max(0, x0 - 4), 0, min(im.width, x1 + 4), im.height)).save(out)
    print(out, x0, x1)
