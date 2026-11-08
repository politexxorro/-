"""Scene 4 «Внезапный дождь» (0:48–1:08), 480 frames @24. Cold blue-grey grade.

  4A   0– 23  pause: first drops hit asphalt, ripples (1s)
  4B  24– 71  both look up (Она 3, Он 3), blink, rain starts thickening
  4C  72–119  from behind running away holding hands: a/b on 2s + squash/stretch, speed lines, shake
  4D 120–143  CU sneakers in the puddle: a/b on 2s, splashes on 1s
  4E 144–191  side MS running & laughing: a/b on 2s, fast pan
  4F 192–287  under the awning, wet, panting & laughing: breath a/b on 3s, wet hair overlay
  4G 288–383  she shivers (2s), he puts her hood on: k1 -> k2 -> k3 on 3s
  4H 384–479  foreheads touch, eyes closed (Она 6, Он 6): hold w/ breathing on 3s, drops freeze, bokeh glow
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import anim as A  # noqa: E402
import rainfx as RF  # noqa: E402
from scene_lib import L, W, H, FPS, bg, breathe, cached, char, ease, put, q, run, sway  # noqa

R, K, LOC = 'shots/shot04/raw/', 'shots/shot04/kit/', 'locations/rain/'
N = 480
COLD = dict(light_dir=1, shadow_rgb=A.hexrgb('#B9BEDC'), shadow_amt=0.2, rim_rgb=(0.8, 0.88, 1.0), rim_amt=0.3)
HAIR = [A.hexrgb('#5A4237'), A.hexrgb('#443329'), A.hexrgb('#634432'), A.hexrgb('#1A1A1A'), A.hexrgb('#2D2A29')]
RAIN = RF.Rain(seed=4)
RAIN_LIGHT = RF.Rain(n=(60, 30, 10), seed=5)
RIP = RF.Ripples(46, (0, 560, W, H), seed=3)
RIP_CU = RF.Ripples(30, (0, 300, W, H), seed=6, period=14)


def wet_char(path, parts=(), deform=None, key=None, amt=0.2):
    def d(sh, deform=deform):
        return deform(sh) if deform else (None, None)
    img = char(path, parts, deform, key=key)
    return cached(('wet', path, tuple(parts), key, amt), lambda: RF.wet(img, HAIR, amt))


def add_rain(rgb, f, dens=1.0, freeze=0.0, t_freeze=0, layer=None):
    r = (layer or RAIN).render(f, freeze, t_freeze) * dens
    return rgb * (1 - 0.35 * r[:, :, None]) + r[:, :, None] * np.array([0.85, 0.9, 1.0]) * 0.6 + 0 * r[:, :, None]


def sh_a(f, rec):
    out = bg(LOC + 'asphalt_cu_v1.png', A.cam_mat(1.05, (900, 560)))[:, :, :3]
    rp = RF.Ripples(int(6 + f * 1.4), (0, 300, W, H), seed=6, period=14).render(f)
    rgb = out + rp[:, :, None] * 0.55
    rgb = add_rain(rgb, f, 0.25 + 0.5 * f / 24, layer=RAIN_LIGHT)
    rec.update(body='— (кадр-пауза)', fx='первые капли, круги (1s)')
    return rgb


def sh_b(f, rec):
    out = bg(LOC + 'street_rain_v1.png', A.cam_mat(1.15, (900, 520)), 3)
    f2 = q(f, 24, 2)
    parts = [K + 'lookup_blink.png'] if 52 <= f2 < 56 else []
    amp = 2.0 * np.sin((f2 - 24) / 6)
    img = wet_char(R + 'couple_lookup_v1.png', parts, breathe(amp, 0.5), key=round(amp, 2), amt=0.06 * (f - 24) / 48)
    put(out, img, A.cam_mat(1.0 + 0.04 * ease((f - 24) / 48)), 0.9, (370, 30), COLD)
    rgb = out[:, :, :3] + RIP.render(f)[:, :, None] * 0.3
    rgb = add_rain(rgb, f, 0.35 + 0.65 * ease((f - 24) / 48))
    rec.update(body='couple_lookup (Она 3, Он 3)', she_eyes='моргание' if parts else 'вверх', fx='дождь усиливается')
    return rgb


def run_phase(f, f0, a, b):
    """4-state run cycle on 2s: a, a-stretch, b, b-squash."""
    st = ((q(f, f0, 2) - f0) // 2) % 4
    src = [a, a, b, b][st]
    sy = [0, -10, 0, 8][st]
    return src, st, sy


def sh_c(f, rec):
    r = np.random.default_rng(f)
    shake = (r.normal(0, 4), r.normal(0, 3))
    out = bg(LOC + 'street_rain_deep_v1.png', A.cam_mat(1.15 + 0.08 * ease((f - 72) / 48), (840, 560), shake), 1.5)
    src, st, sy = run_phase(f, 72, R + 'run_back_a_v1.png', K + 'run_back_b.png')
    img = wet_char(src, (), sway(0, sy, 0.0), key=(st, sy), amt=0.12)
    s = 0.62 - 0.08 * ease((f - 72) / 48)       # running away -> smaller
    put(out, img, A.cam_mat(1.0, (960, 540), shake), s, (960 - img.shape[1] * s / 2, 1080 - img.shape[0] * s + 40),
        COLD)
    rgb = out[:, :, :3]
    ln = A.radial_lines((960, 420), 30, 520, 1500, f, seed=12, thickness=2)
    rgb = rgb + ln[:, :, None] * 0.18 + RIP.render(f)[:, :, None] * 0.3
    rgb = add_rain(rgb, f)
    rec.update(body=f'run_back фаза {st} (2s)', fx='линии скорости, тряска, дождь', cam='со спины')
    return rgb


def sh_d(f, rec):
    out = bg(LOC + 'asphalt_cu_v1.png', A.cam_mat(1.25, (700 + (f - 120) * 9, 640)), 0)
    f2 = q(f, 120, 2)
    st = ((f2 - 120) // 4) % 2
    src = R + 'feet_splash_a_v1.png' if st == 0 else K + 'feet_splash_b.png'
    img = wet_char(src, (), None, key=st, amt=0.0)
    put(out, img, A.cam_mat(1.0), 1.15, (-60, 60), COLD)
    rgb = out[:, :, :3]
    sp = RF.splash(f, 122, (620, 1000), 46, 1) + RF.splash(f, 130, (1500, 990), 46, 2)
    rgb = rgb + sp[:, :, None] * np.array([0.85, 0.92, 1.0]) * 0.9
    rgb = add_rain(rgb, f, 0.8)
    rec.update(body=f'feet_splash_{"ab"[st]} (2s)', fx='брызги (1s)', cam='CU ноги')
    return rgb


def sh_e(f, rec):
    out = bg(LOC + 'street_rain_v1.png', A.cam_mat(1.3, (300 + (f - 144) * 16, 500)), 4)
    src, st, sy = run_phase(f, 144, R + 'run_side_a_v1.png', K + 'run_side_b.png')
    img = wet_char(src, (), sway(0, sy), key=(st, sy), amt=0.16)
    put(out, img, A.cam_mat(1.0), 1.12, (60, 80), COLD)
    rgb = out[:, :, :3]
    ln = np.zeros((H, W), np.float32)
    rr = np.random.default_rng(f)
    for _ in range(26):
        y = int(rr.uniform(80, 1000))
        x = int(rr.uniform(0, 1500))
        cv2.line(ln, (x, y), (x + int(rr.uniform(200, 500)), y), 1.0, 2, cv2.LINE_AA)
    rgb = rgb + cv2.GaussianBlur(ln, (0, 0), 1)[:, :, None] * 0.22
    rgb = add_rain(rgb, f)
    rec.update(body=f'run_side фаза {st} (2s), смех (Она 1, Он 1)', fx='быстрая панорама, линии', cam='MS сбоку')
    return rgb


def sh_f(f, rec):
    out = bg(LOC + 'awning_v1.png', A.cam_mat(1.1, (980, 600)), 2.5)
    f3 = q(f, 192, 3)
    st = ((f3 - 192) // 9) % 2          # panting: 9f in / 9f out
    src = R + 'awning_a_v1.png' if st == 0 else K + 'awning_b.png'
    img = wet_char(src, (), sway(1.5 * np.sin(f3 / 3), 0), key=(st, round(np.sin(f3 / 3), 2)), amt=0.2)
    put(out, img, A.cam_mat(1.0), 1.05, (150, 80), COLD)
    rgb = out[:, :, :3]
    rgb = add_rain(rgb, f, 0.9)
    rec.update(body=f'awning_{"ab"[st]} (тяжело дышат, 3s)', fx='мокрые волосы (оверлей), дождь за навесом')
    return rgb


def sh_g(f, rec):
    out = bg(LOC + 'awning_v1.png', A.cam_mat(1.35, (1000, 560)), 6)
    f3 = q(f, 288, 3)
    if f3 < 324:
        src = R + 'hood_k1_v1.png' if (f3 // 3) % 2 == 0 else K + 'hood_shiver.png'   # shiver on 3s
        nm = 'hood_k1 (дрожит)'
    elif f3 < 345:
        src, nm = K + 'hood_k2.png', 'hood_k2 (капюшон на полпути)'
    else:
        src, nm = K + 'hood_k3.png', 'hood_k3 (капюшон надет)'
    amp = 1.5 * np.sin((f3 - 288) / 8)
    img = wet_char(src, (), breathe(amp, 0.55), key=round(amp, 2), amt=0.2)
    put(out, img, A.cam_mat(1.0 + 0.04 * ease((f - 288) / 96)), 1.0, (190, 80), COLD)
    rgb = add_rain(out[:, :, :3], f, 0.6)
    rec.update(body=nm + ' (3s)', cam='MCU, медленный наезд')
    return rgb


def sh_h(f, rec):
    out = bg(LOC + 'bokeh_rain_v1.png', A.cam_mat(1.1, (960, 540)), 12)
    f3 = q(f, 384, 3)
    st = ((f3 - 384) // 18) % 2
    src = R + 'foreheads_v1.png' if st == 0 else K + 'foreheads_breath.png'
    img = wet_char(src, (), None, key=st, amt=0.15)
    put(out, img, A.cam_mat(1.0 + 0.05 * ease((f - 384) / 96)), 1.25, (-10, -110), dict(COLD, rim_amt=0.35))
    rgb = out[:, :, :3]
    freeze = ease((f - 384) / 30)
    rgb = add_rain(rgb, f, 0.8, freeze=freeze, t_freeze=384)
    glow = np.clip(cv2.GaussianBlur(rgb, (0, 0), 30) - 0.35, 0, 1)
    rgb = rgb + glow * 0.12 * freeze
    sp = SPARK.render(f) * freeze
    rgb = rgb + sp[:, :, None] * np.array([0.9, 0.95, 1.0]) * 0.6
    rec.update(body=f'foreheads (Она 6, Он 6) дыхание {"ab"[st]} (3s)', fx=f'капли застывают {freeze:.2f}, свечение')
    return rgb


SPARK = A.Dust(60, 9)
GRADE = dict(grade=(0.9, 0.97, 1.08), lift=(0.0, 0.01, 0.03), bloom=0.22)
SHOTS = [(0, 24, sh_a, '4A', GRADE), (24, 72, sh_b, '4B', GRADE), (72, 120, sh_c, '4C', GRADE),
         (120, 144, sh_d, '4D', GRADE), (144, 192, sh_e, '4E', GRADE), (192, 288, sh_f, '4F', GRADE),
         (288, 384, sh_g, '4G', GRADE), (384, 480, sh_h, '4H', dict(GRADE, grade=(0.95, 0.98, 1.06)))]

if __name__ == '__main__':
    run(SHOTS, N, 'shots/shot04/render/shot04_picture_v1.mp4', seed=4)
