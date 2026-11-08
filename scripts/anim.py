"""2D limited-animation compositor (numpy/OpenCV).

All images are float32 premultiplied RGBA in [0,1]. Characters are flat drawings; motion comes from swapping
drawings (on 2s/3s), flat mesh-style deformation of a drawing (remap), and per-layer placement. Camera and
particles/light run on 1s. No 3D anywhere.
"""
from functools import lru_cache

import cv2
import numpy as np

W, H = 1920, 1080
FPS = 24


# ---------- IO ----------
@lru_cache(maxsize=64)
def load(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise FileNotFoundError(path)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGRA)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    im = im[:, :, [2, 1, 0, 3]].astype(np.float32) / 255.0  # BGRA -> RGBA
    im[:, :, :3] *= im[:, :, 3:4]
    return im


def to_u8_bgr(rgb):
    return (np.clip(rgb, 0, 1)[:, :, ::-1] * 255 + 0.5).astype(np.uint8)


# ---------- compositing ----------
def over(dst, src):
    dst *= (1.0 - src[:, :, 3:4])
    dst += src
    return dst


def stack_parts(base, parts):
    """Face-kit parts (same size as base) composited onto the base drawing."""
    out = base.copy()
    for p in parts:
        over(out, p)
    return out


def mat(scale=1.0, rot=0.0, pivot=(0, 0), pos=(0, 0)):
    """2x3 affine: source pivot -> canvas pos, with uniform scale and rotation (deg, ccw)."""
    a = np.deg2rad(rot)
    c, s = np.cos(a) * scale, np.sin(a) * scale
    px, py = pivot
    return np.array([[c, s, pos[0] - c * px - s * py],
                     [-s, c, pos[1] + s * px - c * py]], np.float32)


def cam_mat(zoom=1.0, center=(W / 2, H / 2), shift=(0, 0), parallax=1.0):
    """Orthographic 2D camera: zoom about `center`, then shift; parallax scales both for depth layers."""
    z = 1 + (zoom - 1) * parallax
    cx, cy = center
    return np.array([[z, 0, W / 2 - z * cx + shift[0] * parallax],
                     [0, z, H / 2 - z * cy + shift[1] * parallax]], np.float32)


def compose(m_cam, m_layer):
    a = np.vstack([m_cam, [0, 0, 1]])
    b = np.vstack([m_layer, [0, 0, 1]])
    return (a @ b)[:2].astype(np.float32)


def place(img, m, size=(W, H)):
    return cv2.warpAffine(img, m, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


# ---------- flat deformations (the 2D "lattice") ----------
def deform(img, dx=None, dy=None):
    h, w = img.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    mx = gx if dx is None else gx - dx
    my = gy if dy is None else gy - dy
    return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def field_breath(shape, top, bottom, amp, x_range=None):
    """Chest rise: rows between top..bottom lift progressively, everything above `top` lifts by amp."""
    h, w = shape[:2]
    y = np.arange(h, dtype=np.float32)
    f = np.clip((bottom - y) / max(1, bottom - top), 0, 1)
    dy = np.repeat((-amp * f)[:, None], w, 1)
    if x_range is not None:
        x = np.arange(w, dtype=np.float32)
        x0, x1, soft = x_range
        wx = np.clip((x - x0) / soft, 0, 1) * np.clip((x1 - x) / soft, 0, 1)
        dy *= wx[None, :]
    return dy


def field_rotate(shape, pivot, angle_deg, radius):
    """Rotate content around pivot, fading out with distance > radius (head tilt / nod)."""
    h, w = shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    px, py = pivot
    a = np.deg2rad(angle_deg)
    rx, ry = gx - px, gy - py
    wgt = np.clip(1.0 - (np.sqrt(rx ** 2 + ry ** 2) - radius) / radius, 0, 1) * (gy < py + radius * 0.3)
    wgt = cv2.GaussianBlur(wgt.astype(np.float32), (0, 0), radius * 0.15)
    nx = np.cos(a) * rx - np.sin(a) * ry
    ny = np.sin(a) * rx + np.cos(a) * ry
    return (nx - rx) * wgt, (ny - ry) * wgt


def color_mask(img, rgb_list, tol=0.12, blur=6):
    """Soft mask of pixels near any of the given colours (straight RGB 0-1)."""
    a = img[:, :, 3:4]
    s = np.where(a > 1e-3, img[:, :, :3] / np.maximum(a, 1e-3), 0)
    m = np.zeros(img.shape[:2], np.float32)
    for c in rgb_list:
        d = np.sqrt(((s - np.array(c, np.float32)) ** 2).sum(2))
        m = np.maximum(m, np.clip(1 - d / tol, 0, 1))
    m *= img[:, :, 3]
    return cv2.GaussianBlur(m, (0, 0), blur)


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ---------- lighting layers (on top of the drawing; base colours untouched underneath) ----------
def light_layer(layer, light_dir=1, shadow_rgb=(0.93, 0.78, 0.72), shadow_amt=0.18, rim_rgb=(1.0, 0.85, 0.62),
                rim_amt=0.55, rim_px=7, x0=0, x1=W):
    """Cel-style lighting on a placed character layer (canvas space).

    shadow: two-tone multiply that ramps toward the side away from the light.
    rim: thin warm rim on silhouette edges facing the light.
    """
    a = layer[:, :, 3]
    if a.max() < 1e-3:
        return layer
    x = np.linspace(0, 1, W, dtype=np.float32)
    t = np.clip((x * W - x0) / max(1, x1 - x0), 0, 1)
    ramp = (1 - t) if light_dir > 0 else t
    tone = np.where(ramp > 0.55, 1.0, ramp / 0.55 * 0.5).astype(np.float32)  # two steps: core + deep
    mult = 1 - shadow_amt * tone[None, :, None] * (1 - np.array(shadow_rgb, np.float32))[None, None, :] / 0.3
    out = layer.copy()
    out[:, :, :3] *= np.clip(mult, 0, 1)
    sh = np.zeros_like(a)
    if light_dir > 0:
        sh[:, :-rim_px] = a[:, rim_px:]
    else:
        sh[:, rim_px:] = a[:, :-rim_px]
    rim = np.clip(a - sh, 0, 1)
    rim = cv2.GaussianBlur(rim, (0, 0), 1.6) * a
    out[:, :, :3] += rim[:, :, None] * np.array(rim_rgb, np.float32) * rim_amt
    return out


def contact_shadow(shape_alpha, strength=0.25, blur=14, offset=(0, 6)):
    a = np.roll(shape_alpha, offset, axis=(0, 1))
    a = cv2.GaussianBlur(a, (0, 0), blur) * strength
    return a


# ---------- environment FX (on 1s) ----------
class Dust:
    def __init__(self, n, seed, region=(0, 0, W, H)):
        r = np.random.default_rng(seed)
        x0, y0, x1, y1 = region
        self.p = np.c_[r.uniform(x0, x1, n), r.uniform(y0, y1, n)].astype(np.float32)
        self.v = np.c_[r.normal(0.25, 0.25, n), r.normal(-0.12, 0.15, n)].astype(np.float32)
        self.size = r.uniform(1.2, 3.4, n)
        self.ph = r.uniform(0, 6.28, n)
        self.region = region

    def render(self, f, mask=None, gain=0.9):
        canvas = np.zeros((H, W), np.float32)
        x0, y0, x1, y1 = self.region
        pos = self.p + self.v * f + np.c_[np.sin(f * 0.05 + self.ph) * 6, np.cos(f * 0.04 + self.ph) * 4]
        pos[:, 0] = x0 + (pos[:, 0] - x0) % (x1 - x0)
        pos[:, 1] = y0 + (pos[:, 1] - y0) % (y1 - y0)
        tw = 0.55 + 0.45 * np.sin(f * 0.21 + self.ph * 3)
        for (x, y), s, b in zip(pos, self.size, tw):
            cv2.circle(canvas, (int(x), int(y)), int(max(1, s)), float(b), -1, cv2.LINE_AA)
        canvas = cv2.GaussianBlur(canvas, (0, 0), 1.3)
        if mask is not None:
            canvas *= (0.25 + 0.75 * mask)
        return canvas * gain


def ray_mask(src, angles_deg, widths_deg, length=2600, seed=0):
    """Soft god-ray wedges from a point (window)."""
    m = np.zeros((H, W), np.float32)
    for ang, wd in zip(angles_deg, widths_deg):
        a0, a1 = np.deg2rad(ang - wd / 2), np.deg2rad(ang + wd / 2)
        pts = np.array([src, (src[0] + length * np.cos(a0), src[1] + length * np.sin(a0)),
                        (src[0] + length * np.cos(a1), src[1] + length * np.sin(a1))], np.int32)
        layer = np.zeros((H, W), np.float32)
        cv2.fillConvexPoly(layer, pts, 1.0, cv2.LINE_AA)
        m = np.maximum(m, layer)
    gx, gy = np.meshgrid(np.arange(W), np.arange(H))
    d = np.sqrt((gx - src[0]) ** 2 + (gy - src[1]) ** 2)
    m *= np.clip(1.2 - d / 1700, 0, 1)
    return cv2.GaussianBlur(m, (0, 0), 22)


def radial_lines(center, n, r0, r1, f, seed=3, thickness=3):
    r = np.random.default_rng(seed + f)
    m = np.zeros((H, W), np.float32)
    for _ in range(n):
        a = r.uniform(0, 2 * np.pi)
        a0 = r0 * r.uniform(0.9, 1.2)
        p0 = (int(center[0] + a0 * np.cos(a)), int(center[1] + a0 * np.sin(a)))
        p1 = (int(center[0] + r1 * np.cos(a)), int(center[1] + r1 * np.sin(a)))
        cv2.line(m, p0, p1, 1.0, int(r.integers(1, thickness + 1)), cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 0.8)


# ---------- final compositor (per frame) ----------
_vig = None


def finish(rgb, f, grade=(1.02, 1.0, 0.97), lift=(0.008, 0.004, 0.0), bloom=0.16, grain=0.025, ca=1.0,
           vignette=0.28, seed=0):
    global _vig
    out = rgb * np.array(grade, np.float32) + np.array(lift, np.float32)
    # bloom on bright areas (windows, sun, rims)
    small = cv2.resize(out, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bright = np.clip((small.max(2, keepdims=True) - 0.86) / 0.14, 0, 1) * small
    glow = cv2.GaussianBlur(bright, (0, 0), 9) + cv2.GaussianBlur(bright, (0, 0), 24)
    out = out + cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    # chromatic aberration (edges only, ~1px)
    if ca:
        mr = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + 0.0012 * ca)
        mb = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 - 0.0012 * ca)
        out[:, :, 0] = cv2.warpAffine(out[:, :, 0], mr, (W, H), borderMode=cv2.BORDER_REFLECT)
        out[:, :, 2] = cv2.warpAffine(out[:, :, 2], mb, (W, H), borderMode=cv2.BORDER_REFLECT)
    if _vig is None:
        gx, gy = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
        _vig = (np.sqrt(gx ** 2 * 0.8 + gy ** 2) / 1.3).astype(np.float32)
    out *= (1 - vignette * np.clip(_vig, 0, 1) ** 2.2)[:, :, None]
    if grain:
        r = np.random.default_rng(seed * 100003 + f)
        n = r.normal(0, grain, (H // 2, W // 2)).astype(np.float32)
        out += cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None]
    return np.clip(out, 0, 1)
