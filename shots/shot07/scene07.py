"""Scene 7 «Вечер дома» (1:42–2:00), 432 frames @24. Warm amber lamp + garland, TV flicker.

  7A   0– 23  pause: twinkling garland
  7B  24–119  sofa, blanket, flickering screen light (1s), cat plush between them, breathing on 3s
  7C 120–215  she falls asleep on his shoulder (a -> k2 -> k3, Она 6), he smiles warmly (Он 4 w/o blush), slow blink
  7D 216–311  he pulls the blanket up (k4) and kisses the top of her head (k5), on 3s, sparkles
  7E 312–431  camera drifts to the side table: photo strip + cat, night city; VO whisper; hand-written title; fade
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import anim as A  # noqa: E402
from scene_lib import L, ROOT, W, H, FPS, bg, breathe, cached, char, ease, put, q, run, sway  # noqa

R, K, LOC = 'shots/shot07/raw/', 'shots/shot07/kit/', 'locations/home/'
N = 432
AMBER = dict(light_dir=-1, shadow_rgb=A.hexrgb('#E3B98C'), shadow_amt=0.16, rim_rgb=(1.0, 0.78, 0.45), rim_amt=0.55)
TITLE = 'Каждый день — с тобой'


def garland(f, pts, gain=0.8):
    m = np.zeros((H, W), np.float32)
    for i, (x, y) in enumerate(pts):
        b = 0.55 + 0.45 * np.sin(f * 0.25 + i * 1.9) * np.sin(f * 0.07 + i)
        cv2.circle(m, (x, y), 10, float(max(0, b)), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 14) * gain


def sh_a(f, rec):
    out = bg(LOC + 'garland_cu_v1.png', A.cam_mat(1.06, (960 + f * 2, 540)))[:, :, :3]
    g = garland(f, [(int(x), int(260 + 90 * np.sin(x / 300))) for x in range(150, 1800, 150)])
    rec.update(body='— (гирлянда мигает)', fx='мерцание (1s)')
    return out + g[:, :, None] * np.array([1.0, 0.75, 0.4]) * 0.6


def tv_light(f):
    r = np.random.default_rng(f // 2)
    return 0.06 + 0.05 * r.random()


def sofa(f, rec):
    z = 1.0 + 0.06 * ease((f - 24) / 288)
    cam = A.cam_mat(z, (960, 560))
    out = bg(LOC + 'living_evening_v1.png', A.cam_mat(1.25 * z, (900, 600)), 6)
    f3 = q(f, 24, 3)
    parts = []
    if f < 132:
        src, nm = R + 'sofa_a_v1.png', 'sofa_a (смотрят на экран)'
    elif f < 156:
        src, nm = K + 'sofa_k2.png', 'sofa_k2 (засыпает)'
    elif f < 216:
        src, nm = R + 'sofa_k3_v1.png', 'sofa_k3 (Она 6 на плече, Он 4 улыбается)'
        if 186 <= f3 < 195:
            parts = [K + 'sofa_k3_blink.png']
    elif f < 264:
        src, nm = K + 'sofa_k4.png', 'sofa_k4 (укрывает пледом)'
    else:
        src, nm = K + 'sofa_k5.png', 'sofa_k5 (целует в макушку)'
    amp = 1.6 * np.sin((f3 - 24) / 10)
    img = char(src, parts, breathe(amp, 0.5), key=round(amp, 2))
    put(out, img, cam, 1.0, (190, 70), AMBER)
    rgb = out[:, :, :3]
    tv = tv_light(f)
    rgb = rgb + tv * np.array([0.55, 0.7, 1.0]) * np.clip(np.linspace(1.2, 0.2, H)[:, None, None], 0, 1)
    g = garland(f, [(int(x), int(120 + 40 * np.sin(x / 260))) for x in range(80, 1900, 170)], 0.5)
    rgb = rgb + g[:, :, None] * np.array([1.0, 0.75, 0.4]) * 0.4
    if f >= 270:
        rgb = rgb + SPARK.render(f)[:, :, None] * np.array([1.0, 0.85, 0.6]) * 0.7 * min(1, (f - 270) / 10)
    rec.update(body=nm, he_eyes='медленное моргание' if parts else '—', fx='мерцание экрана (1s), гирлянда',
               cam=f'медленный наезд {z:.3f}')
    return rgb


def title_layer():
    def build():
        font = ImageFont.truetype(str(ROOT / 'fonts/Caveat.ttf'), 150)
        try:
            font.set_variation_by_axes([600])
        except Exception:
            pass
        im = Image.new('L', (W, 260), 0)
        d = ImageDraw.Draw(im)
        tw = d.textlength(TITLE, font=font)
        d.text(((W - tw) / 2, 40), TITLE, fill=255, font=font)
        a = np.array(im, np.float32) / 255
        xs = np.where(a.max(0) > 0.1)[0]
        return a, xs.min(), xs.max()
    return cached('title', build, cap=10 ** 6)


def sh_e(f, rec):
    t = ease((f - 312) / 90)
    out = bg(R + 'table_props_v1.png', A.cam_mat(1.25 - 0.12 * t, (700 + 260 * t, 560)))
    rgb = out[:, :, :3]
    g = garland(f, [(int(x), int(90 + 30 * np.sin(x / 200))) for x in range(900, 1900, 130)], 0.5)
    rgb = rgb + g[:, :, None] * np.array([1.0, 0.75, 0.4]) * 0.35
    a, x0, x1 = title_layer()
    p = (f - 336) / 66                                   # handwriting sweep over ~2.75 s
    if p > 0:
        edge = x0 + (x1 - x0 + 40) * min(p, 1.0)
        xs = np.arange(W, dtype=np.float32)
        reveal = np.clip((edge - xs) / 30, 0, 1)[None, :]
        lay = np.zeros((H, W), np.float32)
        y0 = 150
        lay[y0:y0 + a.shape[0]] = a * reveal
        glow = cv2.GaussianBlur(lay, (0, 0), 6)
        pen = np.zeros((H, W), np.float32)
        if p < 1:
            col = np.clip(int(edge), 0, W - 1)
            ys = np.where(a[:, max(0, col - 6):col + 1].max(1) > 0.3)[0]
            if len(ys):
                cv2.circle(pen, (col, int(y0 + ys.mean())), 9, 1.0, -1, cv2.LINE_AA)
                pen = cv2.GaussianBlur(pen, (0, 0), 7)
        shadow = cv2.GaussianBlur(np.roll(lay, (4, 3), (0, 1)), (0, 0), 4)
        rgb = rgb * (1 - 0.45 * shadow[:, :, None])
        rgb = rgb * (1 - lay[:, :, None]) + lay[:, :, None] * np.array([1.0, 0.96, 0.9])
        rgb = rgb + glow[:, :, None] * np.array([1.0, 0.8, 0.5]) * 0.35 + pen[:, :, None] * np.array([1, .9, .7]) * 1.2
    fade = np.clip((f - 408) / 23, 0, 1)
    rec.update(body='— (столик: фотополоска и котик)', fx=f'надпись от руки {min(max(p, 0), 1):.2f}' +
               (f', затемнение {fade:.2f}' if fade else ''), cam='проезд к столику')
    return np.clip(rgb, 0, 1) * (1 - fade)


SPARK = A.Dust(50, 41, region=(500, 50, 1500, 700))
GR = dict(grade=(1.05, 0.99, 0.92), lift=(0.015, 0.008, 0.0), bloom=0.25)
SHOTS = [(0, 24, sh_a, '7A', GR), (24, 312, sofa, '7B-D', GR), (312, 432, sh_e, '7E', GR)]

if __name__ == '__main__':
    run(SHOTS, N, 'shots/shot07/render/shot07_picture_v1.mp4', seed=7)
