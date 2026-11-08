"""Scene 6 «Закат» (1:24–1:42), 432 frames @24. Golden-pink, backlit.

  6A   0– 23  pause: wires & sunset sky (slow pan 1s)
  6B  24–119  rear 3/4: sitting, sharing earbuds; wind a/b on 3s; camera slow lateral move (parallax)
  6C 120–215  she leans her head on his shoulder: sit -> mid -> lean on 3s (Она 6), breathing
  6D 216–335  MCU: he speaks looking at the sunset (Он 7) «Знаешь… я бы хотел…» lipsync on 2s, her eyes closed
  6E 336–431  she lifts head (Она 4) «Глупый… так и будет.» | silence | quick cheek kiss | he stunned (Он 3) -> smile (Он 4)
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import anim as A  # noqa: E402
from scene_lib import L, RHUBARB, W, H, FPS, bg, breathe, cached, char, ease, lipsync, put, q, run, sway  # noqa

R, K, LOC = 'shots/shot06/raw/', 'shots/shot06/kit/', 'locations/roof/'
N = 432
GOLD = dict(light_dir=1, shadow_rgb=A.hexrgb('#E2B7C9'), shadow_amt=0.16, rim_rgb=(1.0, 0.82, 0.55), rim_amt=0.75)
MAP_HE = {'M': 'M', 'half': 'E', 'E': 'E', 'A': 'A', 'O': 'A'}
MAP_SHE = {'M': 'M', 'half': 'E', 'E': 'E', 'A': 'A', 'O': 'O'}


def flare(rgb, sun, f, strength=0.5):
    """Soft anamorphic-free lens flare: ghosts along the sun->centre axis + warm haze."""
    m = np.zeros((H // 2, W // 2, 3), np.float32)
    sx, sy = sun[0] / 2, sun[1] / 2
    cx, cy = W / 4, H / 4
    for k, (t, r, c) in enumerate([(0.0, 90, (1, .85, .6)), (0.6, 22, (1, .6, .8)), (1.1, 40, (.7, .8, 1)),
                                   (1.5, 14, (1, .9, .6)), (1.9, 60, (1, .7, .9))]):
        x, y = sx + (cx - sx) * t * 2, sy + (cy - sy) * t * 2
        cv2.circle(m, (int(x), int(y)), r, c, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 12)
    m = cv2.resize(m, (W, H)) * strength * (0.9 + 0.1 * np.sin(f * 0.2))
    return rgb + m * (1 - rgb) * 0.8


def sh_a(f, rec):
    out = bg(LOC + 'sky_wires_v1.png', A.cam_mat(1.12, (880 + f * 3, 520)))
    rec.update(body='— (провода и небо)', cam='панорама (1s)')
    return out[:, :, :3]


def sh_bc(f, rec):
    t = ease((f - 24) / 192)
    cam_bg = A.cam_mat(1.15, (860 + 140 * t, 470))
    cam = A.cam_mat(1.0, (960 - 60 * t, 540))
    out = bg(LOC + 'roof_sunset_v1.png', cam_bg)
    f3 = q(f, 24, 3)
    if f < 144:
        src = R + 'roof_sit_v1.png' if ((f3 - 24) // 12) % 2 == 0 else K + 'roof_sit_wind.png'
        nm = 'roof_sit (ветер a/b, 3s)'
    elif f < 156:
        src, nm = K + 'roof_lean_mid.png', 'roof_lean_mid (голова на полпути)'
    else:
        src, nm = K + 'roof_lean.png', 'roof_lean (Она 6 на плече)'
    amp = 1.6 * np.sin((f3 - 24) / 9)
    img = char(src, (), breathe(amp, 0.45), key=round(amp, 2))
    put(out, img, cam, 1.0, (200, 140), GOLD)
    rgb = flare(out[:, :, :3], (960, 300), f, 0.35)
    rec.update(body=nm, cam='медленный проезд (1s)', fx='контровой свет, блик')
    return rgb


def sh_d(f, rec):
    z = 1.0 + 0.05 * ease((f - 216) / 120)
    out = bg(LOC + 'roof_sunset_v1.png', A.cam_mat(1.5, (1300, 420)), 10)
    m = lipsync('audio/lipsync/05_he_093_v1.json', 218, MAP_HE, f)
    parts = [K + f'roof_mcu_mouth_{m}.png'] if m else [K + 'roof_mcu_mouth_M.png']
    f2 = q(f, 216, 2)
    amp = 1.4 * np.sin((f2 - 216) / 10)
    img = char(R + 'roof_mcu_v1.png', parts, breathe(amp, 0.55), key=round(amp, 2))
    put(out, img, A.cam_mat(z, (960, 540)), 1.12, (100, 30), GOLD)
    rgb = flare(out[:, :, :3], (1700, 260), f, 0.3)
    rec.update(body='roof_mcu (Он 7 говорит, Она 6)', he_mouth=m or 'закрыт', cam=f'MCU наезд {z:.3f}')
    return rgb


def sh_e(f, rec):
    z = 1.05
    out = bg(LOC + 'roof_sunset_v1.png', A.cam_mat(1.5, (1300, 420)), 10)
    f2 = q(f, 336, 2)
    if f < 384:
        m = lipsync('audio/lipsync/06_she_098_v1.json', 338, MAP_SHE, f)
        parts = [K + f'roof_lift_mouth_{m}.png'] if m else []
        img = char(K + 'roof_lift.png', parts, breathe(1.2 * np.sin((f2 - 336) / 8), 0.55), key=(m, f2 % 16))
        nm = 'roof_lift (Она 4, говорит)' if f < 374 else 'roof_lift (пауза-тишина)'
    elif f < 396:
        img, nm = L(K + 'roof_kiss.png'), 'roof_kiss (поцелуй в щёку)'
    elif f < 414:
        img, nm = L(K + 'roof_after.png'), 'roof_after (Он 3 ошарашен)'
    else:
        img, nm = L(K + 'roof_after_smile.png'), 'roof_after_smile (Он 4)'
    put(out, img, A.cam_mat(z, (960, 540)), 1.12, (100, 30), GOLD)
    rgb = flare(out[:, :, :3], (1700, 260), f, 0.3)
    if f >= 384:
        sp = SPARK.render(f) * min(1, (f - 384) / 6)
        rgb = rgb + sp[:, :, None] * np.array([1.0, 0.85, 0.75]) * 0.9
    if 396 <= f < 400:   # surprise flash
        rgb = rgb * 0.6 + 0.4
    rec.update(body=nm, fx='блёстки' if f >= 384 else 'блик объектива')
    return rgb


SPARK = A.Dust(70, 31, region=(400, 50, 1600, 900))
GR = dict(grade=(1.06, 0.98, 0.95), lift=(0.02, 0.008, 0.01), bloom=0.28)
SHOTS = [(0, 24, sh_a, '6A', GR), (24, 216, sh_bc, '6B-C', GR), (216, 336, sh_d, '6D', GR), (336, 432, sh_e, '6E', GR)]

if __name__ == '__main__':
    run(SHOTS, N, 'shots/shot06/render/shot06_picture_v1.mp4', seed=6)
