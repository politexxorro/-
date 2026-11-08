"""Generic drawing-kit builder (anti-jitter).

Config JSON: list of entries
  {"base": path, "var": path, "out": path, "mode": "part", "roi": [x0,y0,x1,y1]}   # fractions of base size
      -> only the changed pixels inside roi, feathered (face parts: eyes, mouths, blush)
  {"base": path, "var": path, "out": path, "mode": "full", "anchor": [x0,y0,x1,y1]}
      -> whole variant drawing, registered to base using only the anchor region (e.g. head+torso that did not move)
usage: python3 scripts/kit.py config.json
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np


def load(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    return im


def gray(im):
    a = im[:, :, 3:4] / 255.0
    return (im[:, :, :3].mean(2, keepdims=True) * a + 128 * (1 - a))[:, :, 0].astype(np.float32)


def register(base, var, region, motion=cv2.MOTION_AFFINE):
    h, w = base.shape[:2]
    var = cv2.resize(var, (w, h), interpolation=cv2.INTER_AREA)
    x0, y0, x1, y1 = region
    m = np.zeros((h, w), np.uint8)
    m[y0:y1, x0:x1] = 255
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        _, warp = cv2.findTransformECC(gray(base), gray(var), warp, motion,
                                       (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), m, 5)
    except cv2.error as e:
        print('   ECC failed -> identity', str(e)[:80])
    reg = cv2.warpAffine(var, warp, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return reg, warp


def part(base, reg, roi_px):
    h, w = base.shape[:2]
    x0, y0, x1, y1 = roi_px
    diff = np.abs(reg[:, :, :3].astype(int) - base[:, :, :3].astype(int)).max(2)
    diff = np.maximum(diff, np.abs(reg[:, :, 3].astype(int) - base[:, :, 3].astype(int)))
    ch = np.zeros((h, w), np.uint8)
    ch[y0:y1, x0:x1] = (diff[y0:y1, x0:x1] > 28).astype(np.uint8) * 255
    k = max(3, int(0.012 * w)) | 1
    ch = cv2.morphologyEx(ch, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    ch = cv2.dilate(ch, np.ones((k, k), np.uint8))
    roi_m = np.zeros((h, w), np.float32)
    roi_m[y0:y1, x0:x1] = 1
    roi_m = cv2.GaussianBlur(roi_m, (0, 0), k / 2)
    mask = np.clip(cv2.GaussianBlur(ch.astype(np.float32) / 255, (0, 0), k / 3) * roi_m * 1.4, 0, 1)
    out = reg.copy()
    out[:, :, 3] = (mask * (reg[:, :, 3] / 255.0) * 255).astype(np.uint8)
    return out


SKIN = [np.array(c[::-1], np.float32) for c in [(0xF1, 0xB2, 0x8F), (0xF2, 0xBE, 0x9F)]]  # BGR, him / her


def face_box(im, grow=0.10):
    """Bounding box of the face: the highest large skin-coloured blob (hands are lower / smaller)."""
    bgr = im[:, :, :3].astype(np.float32)
    d = np.min([np.sqrt(((bgr - s) ** 2).sum(2)) for s in SKIN], 0)
    m = ((d < 40) & (im[:, :, 3] > 200)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    h, w = m.shape
    best = None
    for i in range(1, n):
        x, y, bw, bh, area = st[i]
        if area < 0.004 * h * w:
            continue
        score = area / (1 + 0.004 * y)
        if best is None or score > best[0]:
            best = (score, x, y, bw, bh)
    _, x, y, bw, bh = best
    gx, gy = int(bw * grow), int(bh * grow)
    return max(0, x - gx), max(0, y - int(bh * 0.25)), min(w, x + bw + gx), min(h, y + bh + gy)


def main(cfg_path):
    cfg = json.load(open(cfg_path))
    for e in cfg:
        base, var = load(e['base']), load(e['var'])
        h, w = base.shape[:2]
        fr = e.get('roi') or e.get('anchor') or [0, 0, 1, 1]
        if fr == 'face':
            px = face_box(base)
        else:
            px = (int(fr[0] * w), int(fr[1] * h), int(fr[2] * w), int(fr[3] * h))
        if e['mode'] == 'part':
            pad = int(0.15 * max(w, h))
            reg, warp = register(base, var, (max(0, px[0] - pad), max(0, px[1] - pad), px[2] + pad, px[3] + pad))
            out = part(base, reg, px)
        else:
            reg, warp = register(base, var, px)
            out = reg
        Path(e['out']).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(e['out'], out)
        print(f"{Path(e['out']).name:34s} {e['mode']:4s} shift=({warp[0, 2]:+.1f},{warp[1, 2]:+.1f}) "
              f"scale≈{warp[0, 0]:.3f}")


if __name__ == '__main__':
    main(sys.argv[1])
