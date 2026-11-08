"""Onion-skin check: base in red, registered variant in cyan. usage: onion.py out.png base var [base var ...]"""
import sys

import cv2
import numpy as np

out, pairs = sys.argv[1], sys.argv[2:]
tiles = []
for b, v in zip(pairs[::2], pairs[1::2]):
    B = cv2.imread(b, -1)
    V = cv2.resize(cv2.imread(v, -1), (B.shape[1], B.shape[0]))

    def g(im):
        a = im[:, :, 3:4] / 255.0
        return (im[:, :, :3].mean(2, keepdims=True) * a + 255 * (1 - a))[:, :, 0]
    t = np.dstack([g(V), g(V), g(B)]).astype(np.uint8)
    s = 520 / max(t.shape[:2])
    tiles.append(cv2.resize(t, (int(t.shape[1] * s), int(t.shape[0] * s))))
h = max(t.shape[0] for t in tiles)
tiles = [np.pad(t, ((0, h - t.shape[0]), (0, 4), (0, 0))) for t in tiles]
cv2.imwrite(out, np.hstack(tiles))
