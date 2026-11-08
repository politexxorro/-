"""Build face-kit parts: register each variant drawing onto its base (ECC affine), then cut only the changed
pixels inside a face ROI with a feathered mask. Output: RGBA part, same size as base, transparent elsewhere.

usage: python3 scripts/face_kit.py  (config below)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

R = 'shots/shot01/raw/'
OUT = Path('characters/face_kit/shot01')
# base, variant, part name, ROI (fractions of base w,h: x0,y0,x1,y1)
CFG = [
    ('she_talk_base_v1', 'she_talk_mouth_A_v1', 'she_talk_mouth_A', (0.30, 0.42, 0.44, 0.53)),
    ('she_talk_base_v1', 'she_talk_mouth_O_v1', 'she_talk_mouth_O', (0.30, 0.42, 0.44, 0.53)),
    ('she_talk_base_v1', 'she_talk_mouth_E_v1', 'she_talk_mouth_E', (0.30, 0.42, 0.44, 0.53)),
    ('she_talk_base_v1', 'she_talk_mouth_M_v1', 'she_talk_mouth_M', (0.30, 0.42, 0.44, 0.53)),
    ('she_talk_base_v1', 'she_talk_mouth_half_v1', 'she_talk_mouth_half', (0.30, 0.42, 0.44, 0.53)),
    ('she_talk_base_v1', 'she_talk_mouth_laugh_v1', 'she_talk_mouth_laugh', (0.30, 0.42, 0.44, 0.53)),
    ('she_talk_base_v1', 'she_talk_eyes_closed_v1', 'she_talk_eyes_closed', (0.25, 0.30, 0.49, 0.41)),
    ('she_talk_base_v1', 'she_talk_eyes_half_v1', 'she_talk_eyes_half', (0.25, 0.30, 0.49, 0.41)),
    ('she_poke_p1', 'she_poke_p1_eyes_closed_v1', 'she_poke_p1_eyes_closed', (0.10, 0.13, 0.75, 0.32)),
    ('he_pillow_p1', 'he_pillow_p1_eyes_closed_v1', 'he_pillow_p1_eyes_closed', (0.20, 0.25, 0.55, 0.42)),
    ('he_sleep_mid_v1', 'he_sleep_mid_mouthopen_v1', 'he_sleep_mouth_open', (0.24, 0.38, 0.34, 0.50)),
    ('he_sleep_mid_v1', 'he_sleep_mid_frown_v1', 'he_sleep_frown', (0.17, 0.25, 0.34, 0.50)),
]


def load(name):
    im = cv2.imread(R + name + '.png', cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    return im


def register(base, var, roi_px):
    """Affine ECC on grayscale (composited on grey) restricted to an enlarged ROI."""
    var = cv2.resize(var, (base.shape[1], base.shape[0]), interpolation=cv2.INTER_AREA)

    def g(im):
        a = im[:, :, 3:4] / 255.0
        return (im[:, :, :3].mean(2, keepdims=True) * a + 128 * (1 - a))[:, :, 0].astype(np.float32)
    x0, y0, x1, y1 = roi_px
    h, w = base.shape[:2]
    pad = int(0.15 * max(w, h))
    m = np.zeros((h, w), np.uint8)
    m[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] = 255
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        _, warp = cv2.findTransformECC(g(base), g(var), warp, cv2.MOTION_AFFINE,
                                       (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), m, 5)
    except cv2.error as e:
        print('  ECC failed, identity:', e)
    reg = cv2.warpAffine(var, warp, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return reg, warp


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    for base_n, var_n, part, roi in CFG:
        base, var = load(base_n), load(var_n)
        h, w = base.shape[:2]
        roi_px = (int(roi[0] * w), int(roi[1] * h), int(roi[2] * w), int(roi[3] * h))
        reg, warp = register(base, var, roi_px)
        x0, y0, x1, y1 = roi_px
        diff = np.abs(reg[:, :, :3].astype(int) - base[:, :, :3].astype(int)).max(2)
        ch = np.zeros((h, w), np.uint8)
        ch[y0:y1, x0:x1] = (diff[y0:y1, x0:x1] > 28).astype(np.uint8) * 255
        k = max(3, int(0.012 * w)) | 1
        ch = cv2.morphologyEx(ch, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
        ch = cv2.dilate(ch, np.ones((k, k), np.uint8))
        # keep inside ROI with soft edge
        roi_m = np.zeros((h, w), np.float32)
        roi_m[y0:y1, x0:x1] = 1
        roi_m = cv2.GaussianBlur(roi_m, (0, 0), k / 2)
        mask = cv2.GaussianBlur(ch.astype(np.float32) / 255, (0, 0), k / 3) * roi_m
        mask = np.clip(mask * 1.4, 0, 1)
        part_im = reg.copy()
        part_im[:, :, 3] = (mask * (reg[:, :, 3] / 255.0) * 255).astype(np.uint8)
        cv2.imwrite(str(OUT / f'{part}.png'), part_im)
        nz = np.argwhere(ch > 0)
        bbox = [int(nz[:, 1].min()), int(nz[:, 0].min()), int(nz[:, 1].max()), int(nz[:, 0].max())] if len(nz) else None
        report[part] = {'base': base_n, 'variant': var_n, 'warp': warp.round(4).tolist(), 'changed_bbox': bbox}
        print(f'{part:28s} shift=({warp[0,2]:+.1f},{warp[1,2]:+.1f}) scale≈{warp[0,0]:.3f} bbox={bbox}')
    json.dump(report, open(OUT / 'face_kit.json', 'w'), indent=1)


if __name__ == '__main__':
    sys.exit(main())
