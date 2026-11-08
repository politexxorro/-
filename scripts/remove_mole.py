"""Remove the girl's under-eye mole (client decision 2026-11-08) from her drawings by local inpainting.

Detection: small dark blob whose surrounding ring is almost entirely skin-coloured (eyes, lashes, lip lines
fail this test). Only that blob is repainted with the surrounding skin; everything else is untouched.
Originals stay in raw/; cleaned copies go to shots/shot01/clean/ with the same file names.
usage: python3 scripts/remove_mole.py file.png [...]
"""
import sys
from pathlib import Path

import cv2
import numpy as np

SKIN = np.array([0xF2, 0xBE, 0x9F], np.float32) / 255  # bible: her skin
OUT = Path('shots/shot01/clean')


def clean(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    bgr = im[:, :, :3]
    a = im[:, :, 3] if im.shape[2] == 4 else np.full(im.shape[:2], 255, np.uint8)
    rgb = bgr[:, :, ::-1].astype(np.float32) / 255
    lum = rgb.mean(2)
    dark = ((lum < 0.30) & (a > 128)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    skin_d = np.sqrt(((rgb - SKIN) ** 2).sum(2))
    scale = max(im.shape[:2]) / 1300
    mask = np.zeros(dark.shape, np.uint8)
    found, cand = [], []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if not (6 * scale ** 2 <= area <= 500 * scale ** 2) or max(w, h) > 3 * min(w, h) + 3:
            continue
        comp = (lab == i).astype(np.uint8)
        r1 = cv2.dilate(comp, np.ones((int(9 * scale) | 1,) * 2, np.uint8))
        r0 = cv2.dilate(comp, np.ones((3, 3), np.uint8))
        ring = (r1 > 0) & (r0 == 0)
        if ring.sum() == 0:
            continue
        frac = (skin_d[ring] < 0.13).mean()
        if frac > 0.85:
            cand.append((float(frac), comp, (int(x + w / 2), int(y + h / 2), int(area), round(float(frac), 2))))
    # the mole is the single blob most completely surrounded by skin
    if cand:
        frac, comp, info = max(cand, key=lambda c: c[0])
        if frac >= 0.95:
            mask = cv2.dilate(comp, np.ones((int(5 * scale) | 1,) * 2, np.uint8))
            found = [info]
    out = im.copy()
    if found:
        out[:, :, :3] = cv2.inpaint(bgr, mask, max(3, int(4 * scale)), cv2.INPAINT_TELEA)
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / Path(path).name), out)
    return found


for p in sys.argv[1:]:
    print(Path(p).name, clean(p))
