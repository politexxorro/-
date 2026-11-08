"""Hand-drawn-style rain FX (all on 1s; environment only)."""
import cv2
import numpy as np

from anim import H, W


class Rain:
    """Three depth layers of slanted streaks; `freeze` (0..1) slows them into hanging drops."""

    def __init__(self, n=(260, 160, 70), seed=1, angle=12):
        r = np.random.default_rng(seed)
        self.layers = []
        for i, k in enumerate(n):
            depth = i / 2  # 0 far .. 1 near
            self.layers.append(dict(
                x=r.uniform(-200, W + 200, k), y=r.uniform(-H, H, k),
                v=r.uniform(38, 52, k) * (0.6 + 0.8 * depth),
                ln=r.uniform(22, 40, k) * (0.6 + 1.4 * depth),
                th=1 + int(depth * 2), a=0.25 + 0.3 * depth, blur=1.2 if i == 0 else (0.6 if i == 1 else 1.6)))
        self.ang = np.deg2rad(angle)

    def render(self, f, freeze=0.0, t_freeze=0):
        out = np.zeros((H, W), np.float32)
        for L in self.layers:
            m = np.zeros((H, W), np.float32)
            travel = L['v'] * (f if freeze == 0 else t_freeze + (f - t_freeze) * (1 - freeze) * 0.03)
            y = (L['y'] + travel) % (2 * H) - H * 0.5
            x = L['x'] - np.tan(self.ang) * travel
            x = (x + 200) % (W + 400) - 200
            ln = L['ln'] * (1 - 0.85 * freeze)
            for xi, yi, li in zip(x, y, ln):
                p0 = (int(xi), int(yi))
                p1 = (int(xi - np.sin(self.ang) * li), int(yi - np.cos(self.ang) * li))
                cv2.line(m, p0, p1, 1.0, L['th'], cv2.LINE_AA)
            out += cv2.GaussianBlur(m, (0, 0), L['blur']) * L['a']
        return np.clip(out, 0, 1)


class Ripples:
    def __init__(self, n, region, seed=2, period=18):
        r = np.random.default_rng(seed)
        x0, y0, x1, y1 = region
        self.c = np.c_[r.uniform(x0, x1, n), r.uniform(y0, y1, n)]
        self.ph = r.integers(0, period, n)
        self.period = period
        self.size = r.uniform(18, 40, n)

    def render(self, f):
        m = np.zeros((H, W), np.float32)
        for (x, y), ph, s in zip(self.c, self.ph, self.size):
            t = ((f + ph) % self.period) / self.period
            rr = int(4 + s * t)
            cv2.ellipse(m, (int(x), int(y)), (rr, max(1, int(rr * 0.35))), 0, 0, 360, (1 - t) * 0.9, 2, cv2.LINE_AA)
            if t < 0.15:
                cv2.circle(m, (int(x), int(y - 6)), 2, 1.0, -1, cv2.LINE_AA)
        return cv2.GaussianBlur(m, (0, 0), 0.8)


def splash(f, f0, origin, n=40, seed=0, spread=(9, 14)):
    """Puddle splash particles from origin at f0 (ballistic, on 1s)."""
    r = np.random.default_rng(seed)
    m = np.zeros((H, W), np.float32)
    t = f - f0
    if t < 0 or t > 18:
        return m
    ang = r.uniform(np.pi * 1.05, np.pi * 1.95, n)
    sp = r.uniform(*spread, n)
    for a, s in zip(ang, sp):
        x = origin[0] + np.cos(a) * s * t
        y = origin[1] + np.sin(a) * s * t + 1.1 * t * t
        cv2.circle(m, (int(x), int(y)), 3 if t < 8 else 2, 1.0, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 1.0) * (1 - t / 18)


def wet(img, hair_cols, amt=0.18):
    """Wet look as an overlay: hair darkened one tone + subtle specular streaks; base drawing untouched beneath."""
    import anim as A
    m = A.color_mask(img, hair_cols, 0.16, 2)
    out = img.copy()
    out[:, :, :3] *= (1 - amt * m)[:, :, None]
    return out
