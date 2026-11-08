"""Contact sheet of whole images (alpha over light grey) with names. usage: sheet.py out.jpg cols img...
"""
import sys

import cv2
import numpy as np

out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
cw = 1800 // cols
tiles = []
for f in files:
    im = cv2.imread(f, -1)
    if im.shape[2] == 4:
        a = im[:, :, 3:4] / 255.0
        im = (im[:, :, :3] * a + 215 * (1 - a)).astype(np.uint8)
    s = cw / im.shape[1]
    im = cv2.resize(im, (cw, int(im.shape[0] * s)))
    t = np.full((int(cw * 0.75) + 18, cw, 3), 50, np.uint8)
    h = min(im.shape[0], t.shape[0] - 18)
    t[18:18 + h] = im[:h]
    cv2.putText(t, f.split('/')[-1][:48], (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    tiles.append(t)
while len(tiles) % cols:
    tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]),
            [cv2.IMWRITE_JPEG_QUALITY, 85])
