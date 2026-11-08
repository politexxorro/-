"""Scene 5 «Автомат с игрушками» (1:08–1:24), 384 frames @24. Neon pink-violet.

  5A   0– 95  POV: plush cat in the machine (slow push) | her MCU: love-struck eyes, blink, sparkles
  5B  96–239  montage: he focuses (2s) | claw drops the cat (1s) | angry (Он 5, shake 2s) | claw empty | sad (Он 2)
  5C 240–311  last coin (1s) | silence | claw lifts the cat... and it drops into the chute (bounce)
  5D 312–383  he holds out the cat «Для тебя.» (lipsync 2s) | she surprised (Она 3) -> happy (Она 1) | hug
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import anim as A  # noqa: E402
from scene_lib import L, RHUBARB, W, H, FPS, bg, breathe, cached, char, ease, lipsync, put, q, run, sway  # noqa

R, K, LOC = 'shots/shot05/raw/', 'shots/shot05/kit/', 'locations/arcade/'
N = 384
NEON = dict(light_dir=-1, shadow_rgb=A.hexrgb('#D7B5E8'), shadow_amt=0.16, rim_rgb=(1.0, 0.6, 0.9), rim_amt=0.45)
CAT, CLAW, CLAW_C = 'props/cat_plush_v1.png', 'props/claw_v1.png', 'props/claw_closed_v1.png'


def prop(out, path, cx, cy, s, rot=0.0, cam=None):
    img = L(path)
    m = A.mat(s, rot, (img.shape[1] / 2, img.shape[0] / 2), (cx, cy))
    A.over(out, A.place(img, A.compose(cam if cam is not None else A.cam_mat(1.0), m)))


def machine(f, f0, claw_x, claw_y, closed, cat=None, z=1.0):
    cam = A.cam_mat(z, (960, 540))
    out = bg(LOC + 'claw_inside_v1.png', cam)
    if cat:
        prop(out, CAT, cat[0], cat[1], 0.30, cat[2] if len(cat) > 2 else 0, cam)
    cl = L(CLAW_C if closed else CLAW)
    s = 0.42
    # cable from top
    cable = np.zeros((H, W, 4), np.float32)
    cv2.line(cable, (int(claw_x), -10), (int(claw_x), int(claw_y - cl.shape[0] * s * 0.45)), (0.55, 0.55, 0.6, 1), 3,
             cv2.LINE_AA)
    A.over(out, A.place(cable, cam))
    prop(out, CLAW_C if closed else CLAW, claw_x, claw_y, s, 0, cam)
    return out


def sh_a(f, rec):
    if f < 36:
        z = 1.0 + 0.08 * ease(f / 36)
        out = bg(LOC + 'claw_inside_v1.png', A.cam_mat(z, (900, 560)))
        prop(out, CAT, 840, 560, 0.32, 0, A.cam_mat(z, (900, 560)))
        tw = 0.5 + 0.5 * np.sin(f * 0.6)
        rgb = out[:, :, :3] + SP.render(f)[:, :, None] * np.array([1, 0.8, 1]) * 0.5 * tw
        rec.update(body='— POV: котик в автомате', cam=f'push {z:.3f}', fx='блики')
        return rgb
    out = bg(LOC + 'arcade_wide_v1.png', A.cam_mat(1.3, (1100, 500)), 9)
    f3 = q(f, 36, 3)
    parts = [K + 'she_love_blink.png'] if 60 <= f3 < 69 else []   # slow dreamy blink (9f)
    amp = 2.0 * np.sin((f3 - 36) / 6)
    img = char(R + 'she_love_v1.png', parts, breathe(amp, 0.5), key=round(amp, 2))
    put(out, img, A.cam_mat(1.0 + 0.04 * ease((f - 36) / 60)), 1.0, (190, 70), NEON)
    rgb = out[:, :, :3]
    hearts = HEARTS.render(f)
    rgb = rgb + hearts[:, :, None] * np.array([1.0, 0.6, 0.85]) * 0.9
    rec.update(body='she_love (влюблённые глаза, 3s)', she_eyes='медленное моргание' if parts else 'сияют',
               fx='искорки', cam='MCU')
    return rgb


def he_shot(f, f0, src, parts=(), shake=0.0, rec=None, label=''):
    out = bg(LOC + 'arcade_wide_v1.png', A.cam_mat(1.25, (700, 520)), 8)
    f2 = q(f, f0, 2)
    jx = shake * (1 if (f2 // 2) % 2 else -1)
    wig = 2.0 * np.sin(f2 / 2.0)
    img = char(src, parts, sway(jx + wig, 0, 0.3), key=(round(jx + wig, 1),))
    put(out, img, A.cam_mat(1.0), 1.05, (40, 60), NEON)
    rec.update(body=label)
    return out[:, :, :3]


def sh_b(f, rec):
    if f < 132:
        parts = [K + 'he_claw_blink.png'] if 112 <= f < 116 else []
        return he_shot(f, 96, R + 'he_claw_k1_v1.png', parts, 0, rec, 'he_claw_k1 (сосредоточен, джойстик 2s)')
    if f < 156:   # claw lifts the cat, it slips
        t = (f - 132) / 24
        cy = 520 - 140 * ease(min(t * 2, 1))
        slip = t > 0.5
        cat = (840, cy + 120, 0) if not slip else (840 + 30 * (t - 0.5), 560 * min(1, (t - 0.5) * 4) + (cy + 120) *
                                                    (1 - min(1, (t - 0.5) * 4)), 25 * (t - 0.5))
        out = machine(f, 132, 840, cy, not slip, cat)
        rec.update(body='— клешня роняет котика (1s)')
        return out[:, :, :3]
    if f < 180:
        return he_shot(f, 156, K + 'he_claw_angry.png', (), 4.0, rec, 'he_claw_angry (Он 5, тряска 2s)')
    if f < 204:   # second fail: claw closes on nothing
        t = (f - 180) / 24
        cy = 300 + 220 * np.sin(np.pi * t)
        out = machine(f, 180, 700, cy, t > 0.5, (840, 560, 0))
        rec.update(body='— клешня пустая (1s)')
        return out[:, :, :3]
    return he_shot(f, 204, K + 'he_claw_sad.png', (), 0, rec, 'he_claw_sad (Он 2)')


def sh_c(f, rec):
    if f < 264:
        out = bg(LOC + 'claw_front_v1.png', A.cam_mat(1.1, (1330, 560)))
        t = (f - 240) / 24
        coin = np.zeros((H, W, 4), np.float32)
        cx, cy = 1600 - 180 * ease(t * 1.3), 380 + 120 * ease(t * 1.3)
        if t < 0.8:
            cv2.ellipse(coin, (int(cx), int(cy)), (38, 38 if t < 0.5 else max(6, int(38 * (1 - (t - 0.5) * 3)))), 0, 0,
                        360, (0.95, 0.78, 0.3, 1), -1, cv2.LINE_AA)
            cv2.ellipse(coin, (int(cx), int(cy)), (28, 28 if t < 0.5 else 4), 0, 0, 360, (0.75, 0.55, 0.15, 1), 2,
                        cv2.LINE_AA)
        A.over(out, coin)
        rec.update(body='— последняя монетка (1s)', cam='CU панель')
        return out[:, :, :3]
    t = (f - 264) / 48
    if t < 0.45:      # grab and lift
        u = t / 0.45
        cy = 300 + 220 * np.sin(np.pi * min(u * 1.6, 1) / 2) if u < 0.6 else 520 - 260 * ease((u - 0.6) / 0.4)
        closed = u > 0.55
        cat = (840, cy + 120, 0) if closed else (840, 560, 0)
        out = machine(f, 264, 840 if u < 0.6 else 840 + 380 * ease((u - 0.6) / 0.4), cy, closed, cat, 1.05)
    else:             # carried to the chute, opens, falls with bounce
        u = (t - 0.45) / 0.55
        x = 1220
        cy = 260
        if u < 0.25:
            cat = (x, cy + 120, 0)
            out = machine(f, 264, x, cy, True, cat, 1.05)
        else:
            v = (u - 0.25) / 0.75
            fall = min(1, v * 2.2) ** 2
            yc = cy + 120 + (900 - cy - 120) * fall
            if v > 0.45:
                yc -= 60 * abs(np.sin((v - 0.45) * 14)) * np.exp(-(v - 0.45) * 6)
            out = machine(f, 264, x, cy, False, (x, yc, 20 * v), 1.05)
    rec.update(body='— клешня поднимает котика → падает в лоток (1s)', fx='тишина')
    return out[:, :, :3]


GIVE_MAP = {'M': 'M', 'half': 'E', 'E': 'E', 'A': 'A', 'O': 'O'}


def sh_d(f, rec):
    if f < 352:
        out = bg(LOC + 'arcade_wide_v1.png', A.cam_mat(1.3, (800, 500)), 9)
        m = lipsync('audio/lipsync/04_he_082_v1.json', 326, GIVE_MAP, f)
        parts = [K + f'he_give_mouth_{m}.png'] if m else []
        f2 = q(f, 312, 2)
        bob = 3 * np.sin((f2 - 312) / 5)
        img = char(R + 'he_give_v1.png', parts, sway(0, bob, 0.2), key=round(bob, 1))
        put(out, img, A.cam_mat(1.0), 0.95, (380, 40), NEON)
        rgb = out[:, :, :3] + SP.render(f)[:, :, None] * np.array([1, 0.9, 0.7]) * 0.6
        rec.update(body='he_give (Он 1, торжество)', he_mouth=m or 'улыбка', fx='искорки')
        return rgb
    out = bg(LOC + 'arcade_wide_v1.png', A.cam_mat(1.3, (1200, 500)), 9)
    if f < 366:
        f2 = q(f, 352, 2)
        parts = [K + 'she_cat_happy.png'] if f2 >= 358 else []
        img = char(R + 'she_cat_surprise_v1.png', parts, sway(0, -4 if f2 < 356 else 0), key=f2 < 356)
        put(out, img, A.cam_mat(1.0), 0.9, (380, 60), NEON)
        rec.update(body='she_cat_surprise' + (' + happy (Она 1)' if parts else ' (Она 3)'))
        rgb = out[:, :, :3]
        if f2 < 356:
            rgb = rgb + A.radial_lines((960, 400), 30, 380, 1300, f2, seed=2)[:, :, None] * 0.5
        return rgb
    f3 = q(f, 366, 3)
    img = char(R + 'hug_cat_v1.png', (), breathe(2.0 * np.sin((f3 - 366) / 4), 0.5), key=f3)
    put(out, img, A.cam_mat(1.0), 0.95, (340, 40), NEON)
    rgb = out[:, :, :3] + HEARTS.render(f)[:, :, None] * np.array([1.0, 0.6, 0.85]) * 0.9
    rec.update(body='hug_cat (объятие с котиком)', fx='блёстки')
    return rgb


SP = A.Dust(50, 21)
HEARTS = A.Dust(30, 22, region=(300, 100, 1600, 900))
GR = dict(grade=(1.03, 0.97, 1.05), lift=(0.012, 0.0, 0.02), bloom=0.22)
SHOTS = [(0, 96, sh_a, '5A', GR), (96, 240, sh_b, '5B', GR), (240, 312, sh_c, '5C', GR), (312, 384, sh_d, '5D', GR)]

if __name__ == '__main__':
    run(SHOTS, N, 'shots/shot05/render/shot05_picture_v1.mp4', seed=5)
