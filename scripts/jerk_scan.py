"""Scan a render for per-frame luminance diffs: find pose-pop frames vs cuts."""
import sys

import cv2
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else 'final.mp4'
cap = cv2.VideoCapture(src)
prev = None
diffs = []
while True:
    ok, fr = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(cv2.resize(fr, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    if prev is not None:
        diffs.append(float(np.abs(g - prev).mean()))
    prev = g
cap.release()
d = np.array(diffs)
print('frames', len(d) + 1, 'mean', d.mean().round(2), 'p90', np.percentile(d, 90).round(2),
      'p99', np.percentile(d, 99).round(2), 'max', d.max().round(2))
print('diff>6:', (d > 6).sum(), ' diff>10:', (d > 10).sum(), ' diff>25 (cuts?):', (d > 25).sum())
np.save('/tmp/diffs.npy', d)
top = np.argsort(d)[::-1][:40]
for i in sorted(top):
    print(f'f{i + 1:5d}  t={(i + 1) / 24:6.2f}s  diff={d[i]:.1f}')
