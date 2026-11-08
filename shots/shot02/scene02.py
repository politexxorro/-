"""Scene 2 «Блинчики» (0:14–0:30), 384 frames @24.

  2A   0– 23  CU stove: pancake sizzling, steam (1s), slow push
  2B  24–119  kitchen two-shot: she whisks (cycle on 2s), he serious (breath on 3s) -> anticipation -> toss -> looks up
  2C 120–191  pancake falls (prop on 1s, flutter) -> impact frames 150-151 -> CU hold «Он 3» + flour dust
  2D 192–287  her laugh (2s shake) 192–215 | his comic pout + line «Это… так и задумано было.» at 216 (lipsync on 2s)
  2E 288–383  CU on 3s: she lifts pancake -> wipes flour off nose -> hand on cheek, blush 1→2→3, slow blink
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import anim as A  # noqa: E402
from scene_lib import L, RHUBARB, W, H, FPS, bg, breathe, cached, char, ease, lipsync, put, q, run, sway  # noqa

R, K, LOC = 'shots/shot02/raw/', 'shots/shot02/kit/', 'locations/kitchen/'
N = 384
LINE_START = 218
WARM = dict(light_dir=-1, shadow_rgb=A.hexrgb('#EDD2B8'), shadow_amt=0.13, rim_rgb=(1.0, 0.9, 0.7), rim_amt=0.5)
STEAM = None


def steam_layer(f, src=(830, 470), spread=260, n=7, gain=0.35):
    """Hand-drawn-ish steam wisps: soft sine ribbons rising (on 1s)."""
    m = np.zeros((H // 2, W // 2), np.float32)
    for i in range(n):
        ph = i * 1.7
        x0 = (src[0] - spread / 2 + spread * i / (n - 1)) / 2
        pts = []
        for k in range(26):
            yy = src[1] / 2 - k * 11 - (f * 1.6 + i * 37) % 60
            xx = x0 + 18 * np.sin(k * 0.35 + f * 0.08 + ph) * (k / 26 + 0.3)
            pts.append((xx, yy))
        pts = np.array(pts, np.int32)
        cv2.polylines(m, [pts], False, 1.0, 6, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 7)
    fade = np.clip(np.linspace(1.4, -0.2, H // 2)[:, None], 0, 1)
    return cv2.resize(m * fade, (W, H)) * gain


def sh_a(f, rec):
    z = 1.0 + 0.05 * ease(f / 24)
    cam = A.cam_mat(z, (900, 560))
    out = bg(LOC + 'kitchen_stove_cu_v1.png', cam)[:, :, :3]
    s = steam_layer(f)
    out = out + s[:, :, None] * np.array([1, 0.97, 0.92]) * (1 - out)
    rec.update(body='— (кадр-пауза)', cam=f'zoom {z:.3f}', fx='пар (1s)')
    return out


SHE_POS, SHE_S = (90, 205), 0.78
HE_POS, HE_S = (760, 70), 0.86
PAN_MOUTH = None


def pancake_path(f):
    """Pancake flight in two-shot canvas coords (on 1s): up out of frame, then down onto his head."""
    x0, y0 = 860, 830           # in pan (approx, canvas)
    head = (1150, 190)
    if f < 98:
        return None
    if f < 120:                  # going up
        t = (f - 98) / 22
        return (x0 + (head[0] - x0) * 0.4 * t, y0 - 1100 * (1 - (1 - t) ** 2), 360 * t * 2)
    if f < 150:                  # coming down from above
        t = (f - 120) / 30
        return (x0 + (head[0] - x0) * (0.4 + 0.6 * t), -120 + (head[1] + 120) * t ** 1.6, 720 + 520 * t)
    return None


def sh_b(f, rec):
    cam = A.cam_mat(1.0 + 0.03 * ease((f - 24) / 150), (1000, 520))
    if f >= 150:
        return None
    out = bg(LOC + 'kitchen_ms_v1.png', A.cam_mat(1.0 + 0.03 * ease((f - 24) / 150), (1000, 520), parallax=0.8), 1.5)
    # her: whisk cycle a-b-a-c on 2s, blink 70-75
    f2 = q(f, 24, 2)
    cyc = ['a', 'b', 'a', 'c'][(f2 // 2) % 4]
    she_base = R + 'she_whisk_a_v1.png'
    she_img = K + f'she_whisk_{cyc}.png' if cyc != 'a' else she_base
    parts = [K + 'she_whisk_blink.png'] if 70 <= f2 < 76 and cyc == 'a' else []
    if parts and cyc != 'a':
        parts = []
    lean = 3.0 * np.sin(f2 / 5.0)
    img = char(she_img, parts, sway(lean, 1.5 * abs(np.sin(f2 / 3.0))), key=(round(lean, 1), cyc))
    if f >= 102:  # she glances up at the flying pancake
        img = char(she_img, [], sway(lean, -6), key=('up', round(lean, 1), cyc))
    put(out, img, cam, SHE_S, SHE_POS, WARM)
    # him
    if f < 84:
        f3 = q(f, 24, 3)
        amp = 2.4 * np.sin(2 * np.pi * (f3 - 24) / (3.0 * FPS))
        hp = [K + 'he_flip_blink.png'] if 48 <= f3 < 54 else []
        img = char(R + 'he_flip_k1_v2.png', hp, breathe(amp), key=round(amp, 2))
        name = 'he_flip_k1 (серьёзен)'
    elif f < 96:
        f2 = q(f, 84, 2)
        img = char(K + 'he_flip_k2.png', (), sway(0, 4 + (f2 - 84) * 0.8), key=f2)
        name = 'he_flip_k2 (замах)'
    elif f < 102:
        img = char(K + 'he_flip_k3.png', (), sway(0, -6), key='k3')
        name = 'he_flip_k3 (бросок)'
    else:
        f2 = q(f, 102, 2)
        img = char(K + 'he_flip_k4.png', (), sway(0, 1.5 * np.sin(f2 / 4.0)), key=('k4', f2))
        name = 'he_flip_k4 (смотрит вверх, Он 3)'
    put(out, img, cam, HE_S, HE_POS, WARM)
    p = pancake_path(f)
    rgb = out[:, :, :3]
    if p is not None:
        pc = L('props/pancake_v1.png')
        sx = 0.22 * (0.75 + 0.25 * np.cos(np.deg2rad(p[2])))     # flip = squash on x
        m = A.compose(cam, A.mat(1.0, p[2] * 0.12, (pc.shape[1] / 2, pc.shape[0] / 2), (p[0], p[1])))
        m[:, 0] *= sx / 1.0
        m[:, 1] *= 0.22
        m[:, 2] = A.compose(cam, A.mat(1.0, pos=(p[0], p[1])))[:, 2] - (m[:, 0] * pc.shape[1] / 2 + m[:, 1] * pc.shape[0] / 2)
        lay = A.place(pc, m)
        o = np.dstack([rgb, np.ones((H, W), np.float32)])
        A.over(o, lay)
        rgb = o[:, :, :3]
        if 98 <= f < 104:  # speed lines on the toss
            ln = A.radial_lines((p[0], p[1] + 200), 26, 120, 700, f, seed=11, thickness=2)
            rgb = rgb + ln[:, :, None] * 0.35
    rec.update(body=f'she_whisk_{cyc} + {name}', she_eyes='закрыты' if parts else 'эмоция 1',
               fx='блин в полёте (1s)' if p else '—', cam='MS two-shot, медленный наезд')
    return rgb


def flour(f, f0, n=60, seed=5, origin=(860, 300)):
    r = np.random.default_rng(seed)
    pts = r.normal(0, 1, (n, 2)) * [160, 40] + origin
    vel = r.normal(0, 1, (n, 2)) * [1.4, 0.6] + [0, 2.2]
    m = np.zeros((H, W), np.float32)
    t = f - f0
    for (x, y), (vx, vy) in zip(pts, vel):
        cv2.circle(m, (int(x + vx * t), int(y + vy * t + 0.05 * t * t)), 2, 1.0, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 1.0) * max(0, 1 - t / 40)


def sh_c(f, rec):
    if f < 150:
        return sh_b(f, rec)
    if f < 152:   # impact frames: inverted flat silhouette + white flash
        out = np.full((H, W, 3), 1.0 if f == 150 else 0.08, np.float32)
        img = L(R + 'he_cu_pancake_v2.png')
        lay = A.place(img, A.mat(1.25, pos=(0, -60)))
        a = lay[:, :, 3:4]
        out = out * (1 - a) + a * (0.05 if f == 150 else 0.97)
        ln = A.radial_lines((960, 300), 60, 300, 1500, f, seed=9, thickness=4)
        out = out + ln[:, :, None] * (-0.9 if f == 150 else 0.9)
        rec.update(body='IMPACT (силуэт, 1s)', fx='вспышка, линии')
        return np.clip(out, 0, 1)
    shake = (0, 0)
    if f < 164:
        r = np.random.default_rng(f)
        k = (164 - f) / 12
        shake = (r.normal(0, 10 * k), r.normal(0, 8 * k))
    cam = A.cam_mat(1.0, (960, 540), shake)
    out = bg(LOC + 'kitchen_wall_cu_v1.png', A.cam_mat(1.15, (900, 500), shake), 4)
    f2 = q(f, 152, 2)
    squash = 10 * np.exp(-(f2 - 152) / 5.0) * np.cos((f2 - 152) / 1.5)  # pancake settles with a wobble
    img = char(R + 'he_cu_pancake_v2.png', (),
               lambda sh, s=squash: (None, s * np.clip(1 - np.arange(sh[0], dtype=np.float32)[:, None] / (sh[0] * 0.4),
                                                       0, 1) * np.ones((1, sh[1]), np.float32)), key=round(squash, 1))
    put(out, img, cam, 1.25, (0, -60), WARM)
    rgb = out[:, :, :3] + flour(f, 152)[:, :, None] * 0.9
    rec.update(body='he_cu_pancake (hold, Он 3)', he_eyes='удивлённые', fx='мука сыплется, блин оседает (2s)',
               cam='CU' + (', тряска' if f < 164 else ''))
    return rgb


POUT_MAP = {'M': 'M', 'half': 'half', 'E': 'E', 'A': 'A', 'O': 'O'}


def sh_d(f, rec):
    if f < 216:
        out = bg(LOC + 'kitchen_wall_cu_v1.png', A.cam_mat(1.1, (1000, 520)), 6)
        f2 = q(f, 192, 2)
        k = 'k1' if (f2 // 2) % 2 == 0 else 'k2'
        img = L(R + 'she_laugh_k1_v1.png') if k == 'k1' else L(K + 'she_laugh_k2.png')
        img = char(R + 'she_laugh_k1_v1.png' if k == 'k1' else K + 'she_laugh_k2.png', (),
                   sway(4 * (1 if (f2 // 4) % 2 else -1), 3), key=f2 % 8)
        put(out, img, A.cam_mat(1.0), 0.9, (420, 20), WARM)
        rec.update(body=f'she_laugh_{k} (смех, 2s)', she_eyes='зажмурены', she_mouth='смех (Она 1)')
        return out[:, :, :3]
    out = bg(LOC + 'kitchen_wall_cu_v1.png', A.cam_mat(1.1, (800, 520)), 6)
    mouth = lipsync('audio/lipsync/03_he_023_v1.json', LINE_START, POUT_MAP, f)
    f2 = q(f, 216, 2)
    after = f2 >= LINE_START + 56
    parts = []
    if after:
        parts.append(K + 'he_pout_mouth_smile.png')
    elif mouth:
        parts.append(K + f'he_pout_mouth_{mouth}.png')
    if 232 <= f2 < 236 or 280 <= f2 < 284:
        parts.append(K + 'he_pout_blink.png')
    nod = 2.0 * np.sin((f2 - 216) / 6.0) if not after else 0
    img = char(R + 'he_pout_base_v1.png', parts,
               lambda sh, a=nod: A.field_rotate(sh, (sh[1] * 0.5, sh[0] * 0.45), a, sh[0] * 0.3), key=round(nod, 2))
    put(out, img, A.cam_mat(1.0), 1.0, (420, 0), WARM)
    rec.update(body='he_pout (Он 5 комично)', he_mouth=(mouth or 'сжат') if not after else 'улыбка (сдался)',
               he_eyes='моргает' if any('blink' in p for p in parts) else 'нахмурен')
    return out[:, :, :3]


def sh_e(f, rec):
    z = 1.0 + 0.06 * ease((f - 288) / 96)
    cam = A.cam_mat(z, (900, 450))
    out = bg(LOC + 'kitchen_wall_cu_v1.png', A.cam_mat(1.2 * z, (900, 450)), 9)
    f3 = q(f, 288, 3)
    parts, alpha = [], []
    if f3 < 312:
        name, src = 'he_cu_k2 (снимает блин)', K + 'he_cu_k2.png'
    elif f3 < 336:
        name, src = 'he_cu_k3 (стирает муку)', K + 'he_cu_k3.png'
    else:
        name, src = 'he_cu_k4 (рука на щеке)', R + 'he_cu_k4_v1.png'
        lvl = min(1.0, (f3 - 342) / 30) if f3 >= 342 else 0
        lvl = [0, 0.35, 0.7, 1.0][int(np.ceil(lvl * 3))]  # three blush levels, stepped
        if lvl:
            parts.append(K + 'he_cu_k4_blush_raw.png')
            alpha.append(lvl)
        if 360 <= f3 < 372:                               # slow blink
            parts.append(K + 'he_cu_k4_blink_raw.png')
            alpha.append(1.0)
        rec.update(he_blush=f'{lvl:.2f}')
    amp = 1.8 * np.sin(2 * np.pi * (f3 - 288) / (2.6 * FPS))
    img = char(src, parts, breathe(amp, 0.6), key=round(amp, 2), part_alpha=alpha)
    put(out, img, cam, 1.25, (0, -60), WARM)
    rgb = out[:, :, :3]
    if f >= 348:  # soft romantic sparkles
        sp = SPARK.render(f) * min(1, (f - 348) / 12)
        rgb = rgb + sp[:, :, None] * np.array([1.0, 0.92, 0.75]) * 0.8
    rec.update(body=name, cam=f'CU, наезд {z:.3f}', fx='блёстки' if f >= 348 else '—')
    return rgb


SPARK = A.Dust(40, 7, region=(700, 100, 1700, 800))
SHOTS = [(0, 24, sh_a, '2A', None), (24, 120, sh_b, '2B', None), (120, 192, sh_c, '2C', None),
         (192, 288, sh_d, '2D', None), (288, 384, sh_e, '2E', None)]

if __name__ == '__main__':
    run(SHOTS, N, 'shots/shot02/render/shot02_picture_v1.mp4', seed=2)
