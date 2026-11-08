"""Smoothing pass: replace the first frame of each new drawing hold with an optical-flow
midpoint of (last hold frame, new frame). Pops become two half-steps; cuts (shot changes
from xsheet records) and continuous motion (pans, 1s smears) are left untouched.

usage: python3 scripts/smooth_pass.py <in.mp4> <xsheet_records.json> <out.mp4> [n_frames]
"""
import json
import subprocess
import sys

import cv2
import numpy as np

POP_T = 6.0        # mean grey diff (320x180) that counts as a pop
CALM_RATIO = 0.6   # previous boundary must be this much calmer (else: continuous motion)

src, recs_path, dst = sys.argv[1], sys.argv[2], sys.argv[3]
limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
shots = [r.get('shot') for r in json.load(open(recs_path))]

dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)


def grey(fr):
    return cv2.cvtColor(cv2.resize(fr, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32)


def half_warp(a, b):
    """Midpoint of a->b: warp both halfway along DIS flow (computed at half res), average."""
    h, w = a.shape[:2]
    ga = cv2.cvtColor(cv2.resize(a, (w // 2, h // 2)), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, (w // 2, h // 2)), cv2.COLOR_BGR2GRAY)
    fab = dis.calc(ga, gb, None)
    fba = dis.calc(gb, ga, None)
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))

    def warp(img, fl):
        fx = cv2.resize(fl[:, :, 0], (w, h)) * 2
        fy = cv2.resize(fl[:, :, 1], (w, h)) * 2
        return cv2.remap(img, gx + fx * 0.5, gy + fy * 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    return cv2.addWeighted(warp(a, fab), 0.5, warp(b, fba), 0.5, 0)


cap = cv2.VideoCapture(src)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}',
                         '-r', '24', '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                         '-pix_fmt', 'yuv420p', dst], stdin=subprocess.PIPE)
prev = prev_g = None
prev_diff = 0.0
n_pop = 0
i = 0
while i < limit:
    ok, fr = cap.read()
    if not ok:
        break
    out = fr
    if prev is not None:
        g = grey(fr)
        d = float(np.abs(g - prev_g).mean())
        same_shot = i < len(shots) and shots[i] == shots[i - 1]
        if same_shot and d > POP_T and prev_diff < CALM_RATIO * d:
            out = half_warp(prev, fr)
            n_pop += 1
        prev_diff = d
        prev_g = g
    else:
        prev_g = grey(fr)
    proc.stdin.write(out.tobytes())
    prev = fr  # original frame: holds stay anchored to real drawings
    i += 1
cap.release()
proc.stdin.close()
proc.wait()
print(f'{dst}: {i} frames, {n_pop} pops smoothed', flush=True)
