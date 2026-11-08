"""Shared scene-building helpers (on top of anim.py): cached drawings, placement, x-sheet records, render loop."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import anim as A  # noqa: E402

W, H, FPS = A.W, A.H, A.FPS
_cache = {}


def L(path):
    return A.load(str(ROOT / path))


def cached(key, fn, cap=24):
    if key not in _cache:
        if len(_cache) > cap:
            _cache.clear()
        _cache[key] = fn()
    return _cache[key]


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def q(f, start, n):
    """Hold drawings for n frames (2s / 3s) counted from `start`."""
    return start + ((f - start) // n) * n


def char(path, parts=(), deform=None, key=None, part_alpha=None):
    """Drawing + kit parts (each optionally with an alpha multiplier) + flat deformation."""
    pa = tuple(part_alpha or [1.0] * len(parts))

    def build():
        img = L(path).copy()
        for p, a in zip(parts, pa):
            A.over(img, L(p) * a)
        if deform:
            dx, dy = deform(img.shape)
            img = A.deform(img, dx, dy)
        return img
    return cached(('ch', path, tuple(parts), pa, key), build)


def breathe(amp, top=0.45):
    return lambda sh, a=amp: (None, A.field_breath(sh, sh[0] * top, sh[0], a))


def sway(dx_amp, dy_amp=0.0, top=0.0):
    """Whole-body drift weighted toward the head (lean / laugh shake)."""
    def f(sh, ax=dx_amp, ay=dy_amp):
        y = np.linspace(1, 0, sh[0], dtype=np.float32)[:, None]
        wgt = np.clip((y - top) / (1 - top + 1e-6), 0, 1) * np.ones((1, sh[1]), np.float32)
        return ax * wgt, ay * wgt
    return f


def bg(path, cam, blur=0):
    img = cached(('bg', path, blur), lambda: cv2.GaussianBlur(L(path), (0, 0), blur) if blur else L(path))
    s = W / img.shape[1] * 1.0
    m = A.compose(cam, A.mat(max(s, H / img.shape[0])))
    return cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def put(out, img, cam, scale, pos, light=None, rot=0.0, pivot=(0, 0)):
    lay = A.place(img, A.compose(cam, A.mat(scale, rot, pivot, pos)))
    if light:
        lay = A.light_layer(lay, **light)
    A.over(out, lay)
    return lay


def lipsync(path, start_frame, mapping, f, lead=1.5, hold=2):
    """Rhubarb cue at frame f (on `hold`s, opening `lead` frames early) -> kit mouth name or None."""
    cues = cached(('ls', path), lambda: json.load(open(ROOT / path))['mouthCues'], cap=10 ** 6)
    f2 = q(f, start_frame - 2, hold)
    t = (f2 - start_frame + lead) / FPS
    for c in cues:
        if c['start'] <= t < c['end']:
            return mapping.get(c['value'])
    return None


RHUBARB = {'A': 'M', 'B': 'half', 'C': 'E', 'D': 'A', 'E': 'O', 'F': 'O', 'G': 'half', 'H': 'half', 'X': None}


def run(shots, n_frames, out_default, finish_kw=None, seed=0):
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', default=f'0:{n_frames}')
    ap.add_argument('--stills', default='')
    ap.add_argument('--out', default=out_default)
    ap.add_argument('--no-video', action='store_true')
    a = ap.parse_args()
    f0, f1 = map(int, a.frames.split(':'))
    stills = {int(x) for x in a.stills.split(',') if x}
    rdir = Path(a.out).parent
    (rdir / 'stills').mkdir(parents=True, exist_ok=True)
    proc = None
    if not a.no_video:
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                                 '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                                 '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    recs = []
    for f in range(f0, f1):
        rec = {'f': f}
        for s0, s1, fn, name, fk in shots:
            if s0 <= f < s1:
                rec['shot'] = name
                rgb = fn(f, rec)
                kw = dict(finish_kw or {})
                kw.update(fk or {})
                break
        rgb = A.finish(np.ascontiguousarray(rgb, np.float32), f, seed=seed, **kw)
        bgr = A.to_u8_bgr(rgb)
        if proc:
            proc.stdin.write(bgr.tobytes())
        if f in stills:
            cv2.imwrite(str(rdir / 'stills' / f'f{f:04d}.png'), bgr)
        recs.append(rec)
        if f % 48 == 0:
            print('frame', f, flush=True)
    if proc:
        proc.stdin.close()
        proc.wait()
    if f0 == 0 and f1 == n_frames:
        json.dump(recs, open(rdir / 'xsheet_records.json', 'w'), ensure_ascii=False)
