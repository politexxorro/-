"""Scene 3 «Фотобудка» (0:30–0:48), 432 frames @24.

  3A   0– 47  CU: hands in her hoodie pocket, walk sway on 2s, street bokeh drifting (1s)
  3B  48–119  side MS walk: drawings a/b on 3s (6f per step) + bob on 2s, street pans (parallax 2 layers, 1s)
  3C 120–191  she pulls him to the booth (pull a -> b on 2s, travel right), he surprised (Он 3)
  3D 192–383  4 flashes (white on 1s) -> each photo a stop-frame (slow push on 1s)
  3E 384–431  strip slides out of the slot (prop on 1s) -> she hugs the strip (Она 4), blush/blink/sparkles
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import anim as A  # noqa: E402
from scene_lib import L, W, H, FPS, bg, breathe, cached, char, ease, put, q, run, sway  # noqa

R, K, LOC = 'shots/shot03/raw/', 'shots/shot03/kit/', 'locations/street/'
N = 432
DAY = dict(light_dir=1, shadow_rgb=A.hexrgb('#D9D4E4'), shadow_amt=0.12, rim_rgb=(1.0, 0.97, 0.9), rim_amt=0.35)


def street_pan(f, f0, speed, blur, zoom=1.35, y=520):
    x = 300 + (f - f0) * speed
    return bg(LOC + 'street_wide_v1.png', A.cam_mat(zoom, (min(x, 1500), y)), blur)


def sh_a(f, rec):
    out = street_pan(f, 0, 2.2, 14, 1.4)
    f2 = q(f, 0, 2)
    ph = f2 / 6.0
    rot = 1.6 * np.sin(ph)
    bob = 7 * abs(np.sin(ph))
    img = L(R + 'hands_pocket_v1.png')
    put(out, img, A.cam_mat(1.0), 1.32, (960 + 6 * np.sin(ph), 600 - bob), DAY, rot=rot,
        pivot=(img.shape[1] / 2, img.shape[0] / 2))
    rec.update(body='hands_pocket (качание при ходьбе, 2s)', cam='CU, фон едет (1s)')
    return out[:, :, :3]


def sh_b(f, rec):
    out = street_pan(f, 48, 7.0, 2.0, 1.25, 470)
    f3 = q(f, 48, 3)
    step = ((f3 - 48) // 6) % 2
    src = R + 'couple_walk_a_v1.png' if step == 0 else K + 'couple_walk_b.png'
    parts = [K + 'couple_walk_blink.png'] if (step == 0 and 84 <= f3 < 90) else []
    f2 = q(f, 48, 2)
    bob = -6 * abs(np.sin((f2 - 48) / 12 * np.pi))
    hair = 2.5 * np.sin((f2 - 48) / 6.0)
    img = char(src, parts, sway(hair, 0), key=(round(hair, 1), step))
    put(out, img, A.cam_mat(1.0), 0.86, (500, 20 + bob), DAY)
    rec.update(body=f'couple_walk_{"ab"[step]} (шаг на 3s)', fx='фон панорамой (1s)',
               she_eyes='моргание' if parts else 'смотрит на него', cam='MS сбоку')
    return out[:, :, :3]


def sh_c(f, rec):
    t = ease((f - 120) / 72)
    out = bg(LOC + 'street_booth_v1.png', A.cam_mat(1.12 + 0.05 * t, (900 + 200 * t, 560)), 1.5)
    f2 = q(f, 120, 2)
    if f2 < 140:
        src, nm = R + 'couple_pull_a_v1.png', 'pull_a'
    else:
        src, nm = K + 'couple_pull_b.png', 'pull_b'
    flutter = 3 * np.sin(f2 / 2.5)
    img = char(src, (), sway(flutter, 0, 0.3), key=(round(flutter, 1), nm))
    x = -80 + 110 * ease((f2 - 120) / 72)
    put(out, img, A.cam_mat(1.0), 1.1, (x, 110), DAY)
    rgb = out[:, :, :3]
    if f2 >= 140:
        ln = A.radial_lines((2600, 560), 18, 1500, 2400, f2, seed=4, thickness=2)
        rgb = rgb + ln[:, :, None] * 0.25
    rec.update(body=nm + ' (2s)', he_eyes='Он 3', she_mouth='Она 1', cam='MS, слежение вправо')
    return rgb


def sh_d(f, rec):
    i = (f - 192) // 48
    k = (f - 192) % 48
    if k < 2:
        rec.update(body=f'ВСПЫШКА {i + 1} (1s)')
        return np.full((H, W, 3), 1.0, np.float32)
    img = L(R + f'photo{i + 1}_v1.png')
    z = 1.0 + 0.04 * (k / 48)
    out = np.zeros((H, W, 4), np.float32)
    put(out, img, A.cam_mat(z), W / img.shape[1] * 1.0, (0, (H - img.shape[0] * W / img.shape[1]) / 2))
    rgb = out[:, :, :3]
    fl = max(0, 1 - (k - 2) / 6)
    rgb = rgb * (1 - fl) + fl
    rec.update(body=f'photo{i + 1} (стоп-кадр)', fx=f'вспышка гаснет {fl:.2f}' if fl else '—', cam=f'push {z:.3f}')
    return rgb


def sh_e(f, rec):
    if f < 408:
        out = bg(LOC + 'booth_slot_cu_v1.png', A.cam_mat(1.05, (820, 520)))
        strip = L('props/photostrip_v1.png')
        t = ease((f - 386) / 20)
        s = 1.05
        slot_x, slot_y = 1126, 590
        ln = strip.shape[0] * s
        lay = A.place(strip, A.mat(s, pos=(slot_x - strip.shape[1] * s / 2, slot_y - ln + ln * 0.75 * t)))
        m = np.zeros((H, W, 1), np.float32)
        m[slot_y:] = 1                     # only the part already out of the slot is visible
        lay = lay * m
        A.over(out, lay)
        rec.update(body='— (полоска выезжает, 1s)', cam='CU лоток')
        return out[:, :, :3]
    out = bg(LOC + 'street_booth_v1.png', A.cam_mat(1.4, (1150, 450)), 10)
    f3 = q(f, 408, 3)
    parts = [K + 'she_strip_blink.png'] if 417 <= f3 < 423 else []
    amp = 2.2 * np.sin((f3 - 408) / 7.0)
    img = char(R + 'she_strip_hug_v2.png', parts, breathe(amp, 0.5), key=round(amp, 2))
    put(out, img, A.cam_mat(1.0 + 0.03 * ease((f - 408) / 24)), 0.85, (450, 20), DAY)
    rgb = out[:, :, :3] + SPARK.render(f)[:, :, None] * np.array([1.0, 0.85, 0.9]) * 0.7
    rec.update(body='she_strip_hug (Она 4, 3s)', she_eyes='моргание' if parts else 'полуприкрыты', fx='блёстки')
    return rgb


SPARK = A.Dust(50, 3, region=(500, 50, 1500, 900))
NEUTRAL = dict(grade=(1.0, 1.0, 1.0), lift=(0.004, 0.004, 0.006))
SHOTS = [(0, 48, sh_a, '3A', NEUTRAL), (48, 120, sh_b, '3B', NEUTRAL), (120, 192, sh_c, '3C', NEUTRAL),
         (192, 384, sh_d, '3D', dict(NEUTRAL, ca=0.5, vignette=0.15)), (384, 432, sh_e, '3E', NEUTRAL)]

if __name__ == '__main__':
    run(SHOTS, N, 'shots/shot03/render/shot03_picture_v1.mp4', seed=3)
