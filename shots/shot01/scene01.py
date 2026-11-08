"""Scene 1 «Утро» — 15-second test (0:00–0:15), 360 frames @24fps.

Shots (frames):
  SH1   0– 95  wide room, push-in, rays + dust, duvet breathing (he is under it)
  SH2  96–191  bed level: he sleeps (Он 6, breathing on 3s); she enters, sly smile, pokes (on 2s)
  SH3 192–263  CU: eyes snap open (Он 3), smear on 1s, hair bounce on 2s, shake + surprise lines
  SH4a 264–311 her MCU: «Доброе утро, соня!» lipsync on 2s, blink, laugh (Она 1)
  SH4b 312–359 he smiles sleepily (Он 4 w/o blush), hides under pillow (on 3s/2s), fade out

usage: python3 shots/shot01/scene01.py [--preview] [--frames a:b] [--stills 10,120,...]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import anim as A  # noqa: E402

RAW = 'shots/shot01/raw/'
SHE = 'shots/shot01/clean/'   # her drawings with the mole removed (client decision)
KIT = 'characters/face_kit/shot01/'
LOC = 'locations/bedroom/'
W, H, FPS = A.W, A.H, A.FPS
N = 360
VOICE_START = 266          # «Доброе утро, соня!» at 11.083 s
LIPSYNC = json.load(open(ROOT / 'audio/lipsync/01_v1.json'))['mouthCues']
RHUBARB_TO_KIT = {'A': 'M', 'B': 'half', 'C': 'E', 'D': 'A', 'E': 'O', 'F': 'O', 'G': 'half', 'H': 'half', 'X': None}

WARM_SHADOW = A.hexrgb('#E9B49A')   # morning: warm peach shadows
RIM = (1.0, 0.86, 0.62)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def q(f, start, n):
    """Quantize frame to holds of n (2s/3s) relative to shot start."""
    return start + ((f - start) // n) * n


def L(path):
    return A.load(str(ROOT / path))


_cache = {}


def cached(key, fn):
    if key not in _cache:
        if len(_cache) > 40:
            _cache.clear()
        _cache[key] = fn()
    return _cache[key]


def bg_layer(path, blur, cam):
    img = cached(('bg', path, blur), lambda: _blur(L(path), blur))
    s = W / img.shape[1]
    return cv2.warpAffine(img, A.compose(cam, A.mat(s, pos=(0, 0))), (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


def _blur(img, s):
    return cv2.GaussianBlur(img, (0, 0), s) if s else img


def char(path, parts=(), deform=None, key=None):
    """Drawing + face-kit parts + flat deformation, cached per unique drawing state."""
    def build():
        img = A.stack_parts(L(path), [L(KIT + p + '.png') for p in parts])
        if deform:
            dx, dy = deform(img.shape)
            img = A.deform(img, dx, dy)
        return img
    return cached(('ch', path, tuple(parts), key), build)


# ---------------------------------------------------------------- shots
def sh1(f, rec):
    t = (f - 0) / 95
    z = 1.0 + 0.12 * ease(t)
    cam = A.cam_mat(z, center=(960 + 40 * ease(t), 540 + 80 * ease(t)))
    fb = q(f, 0, 3)
    amp = 2.6 * np.sin(2 * np.pi * fb / (3.4 * FPS))
    base = L(LOC + 'bedroom_wide_v1.png')
    bg = cached(('sh1bg', round(amp, 2)), lambda: A.deform(base, None, A.field_breath(
        base.shape, 470, 860, amp, x_range=(330, 1180, 120))))
    out = cv2.warpAffine(bg, A.compose(cam, A.mat(W / base.shape[1])), (W, H), borderMode=cv2.BORDER_REFLECT)
    rays = cached('rays1', lambda: A.ray_mask((330, 250), [24, 33, 41, 50], [5, 3, 6, 4]))
    flick = 0.85 + 0.15 * np.sin(f * 0.07)
    rays_c = A.place(rays[:, :, None].repeat(4, 2), cam)[:, :, 0]
    dust = DUST1.render(f, rays_c)
    rgb = out[:, :, :3] + rays_c[:, :, None] * np.array([1.0, 0.82, 0.55]) * 0.12 * flick
    rgb += dust[:, :, None] * np.array([1.0, 0.93, 0.8])
    rec.update(body='— (фон, одеяло дышит на 3)', cam=f'zoom {z:.3f}', fx='лучи, пылинки (1s)')
    return rgb


HE_SCALE, HE_POS = 1.1, (-30, 280)
HE_CHEEK = (610, 425)
SHE_S = 1.15
SHE_TIP = (5, 691)
SHE_LR = {'she_poke_p1': 484, 'she_poke_p2': 630, 'she_poke_p3': 754}


def she_pos(name):
    cx = HE_POS[0] + HE_CHEEK[0] * HE_SCALE
    cy = HE_POS[1] + HE_CHEEK[1] * HE_SCALE
    x3 = cx - SHE_S * SHE_TIP[0] + 4
    y = cy - SHE_S * SHE_TIP[1]
    return x3 + SHE_S * (SHE_LR['she_poke_p3'] - SHE_LR[name]), y


def sh2(f, rec):
    s0 = 96
    t = (f - s0) / 95
    z = 1.0 + 0.05 * ease(t)
    center = (900, 560)
    cam_bg, cam = A.cam_mat(z, center, parallax=0.6), A.cam_mat(z, center)
    cam_fg = A.cam_mat(z, center, parallax=1.3)
    out = bg_layer(LOC + 'bedroom_bedlevel_v1.png', 2.5, cam_bg)

    # --- him (on 3s): breathing + micro mouth, frown after the poke
    fb = q(f, s0, 3)
    amp = 3.2 * np.sin(2 * np.pi * (fb - s0) / (3.2 * FPS))
    parts = []
    if 104 <= f < 140:
        parts = ['he_sleep_mouth_open']
    if f >= 170:
        parts = ['he_sleep_frown']
    he = char(RAW + 'he_sleep_mid_v1.png', parts,
              lambda sh, a=amp: (None, A.field_breath(sh, 470, 887, a)), key=round(amp, 2))
    he_l = A.place(he, A.compose(cam, A.mat(HE_SCALE, pos=HE_POS)))

    # --- her (on 2s)
    she_l = None
    body = 'he_sleep_mid'
    if f >= 114:
        f2 = q(f, s0, 2)
        if f2 < 138:
            name = 'she_poke_p1'
        elif f2 < 150:
            name = 'she_poke_p2'
        else:
            name = 'she_poke_p3'
        x, y = she_pos(name)
        te = ease((f2 - 114) / 18)
        x += (1 - te) * 640
        y += (1 - te) * 30
        if name == 'she_poke_p3' and 164 <= f2 < 172:
            x -= 6                                   # press into the cheek
        sparts = ['she_poke_p1_eyes_closed'] if (name == 'she_poke_p1' and 130 <= f2 < 134) else []
        ang = 1.4 * np.sin((f2 - 150) / 8.0) if name == 'she_poke_p3' else 0.0
        img = char(SHE + name + '.png', sparts,
                   (lambda sh, a=ang: A.field_rotate(sh, (sh[1] * 0.55, sh[0] * 0.42), a, sh[0] * 0.35)) if ang else None,
                   key=round(ang, 2))
        she_l = A.place(img, A.compose(cam, A.mat(SHE_S, pos=(x, y))))
        body = f'he_sleep_mid + {name}'
        rec.update(she_eyes='закрыты' if sparts else 'эмоция 1 (хитрые)', she_mouth='лёгкая улыбка')
    he_l = A.light_layer(he_l, 1, WARM_SHADOW, 0.16, RIM, 0.35, x0=0, x1=1300)
    over(out, he_l)
    if she_l is not None:
        she_l = A.light_layer(she_l, 1, WARM_SHADOW, 0.16, RIM, 0.6, x0=500, x1=1600)
        over(out, she_l)
    over(out, A.place(fg_matte(), cam_fg))

    rays = cached('rays2', lambda: A.ray_mask((1470, 280), [128, 140, 151, 163], [5, 3, 6, 4]))
    dust = DUST2.render(f, rays)
    rgb = out[:, :, :3] + rays[:, :, None] * np.array([1.0, 0.82, 0.55]) * 0.08
    rgb += dust[:, :, None] * np.array([1.0, 0.93, 0.8]) * 0.8
    rec.update(body=body, he_eyes='закрыты (Он 6)', he_mouth='приоткрыт' if 'he_sleep_mouth_open' in parts else (
        'сжат (морщится)' if parts else 'закрыт'), he_brows='сведены' if f >= 170 else 'нейтр.',
               cam=f'zoom {z:.3f}', fx='лучи, пылинки, FG-одеяло DOF')
    return rgb


def over(dst, src):
    return A.over(dst, src)


def smear(img):
    h, w = img.shape[:2]
    m = A.mat(1.0)
    st = cv2.resize(img, (w, int(h * 1.10)))[int(h * 0.07):int(h * 0.07) + h]
    k = np.zeros((31, 1), np.float32)
    k[:, 0] = 1 / 31
    blur = cv2.filter2D(st, -1, k)
    wgt = np.clip(1 - np.arange(h) / (h * 0.65), 0, 1)[:, None, None].astype(np.float32)
    del m
    return blur * wgt + st * (1 - wgt)


def sh3(f, rec):
    s0 = 192
    z = 1.0
    center = (900, 540)
    shake = (0, 0)
    if 216 <= f < 228:
        r = np.random.default_rng(f)
        k = (228 - f) / 12
        shake = (r.normal(0, 9 * k), r.normal(0, 7 * k))
    cam_bg = A.cam_mat(1.25, (700, 600), shake, parallax=0.6)
    cam = A.cam_mat(z, center, shake)
    out = bg_layer(LOC + 'bedroom_bedlevel_v1.png', 9, cam_bg)
    pos = (-40, 40)
    s = 1.2
    if f < 216:
        fb = q(f, s0, 3)
        amp = 2.2 * np.sin(2 * np.pi * (fb - s0) / (3.0 * FPS))
        img = char(RAW + 'he_cu_closed_v1.png', (), lambda sh, a=amp: (None, A.field_breath(sh, 520, 887, a)),
                   key=round(amp, 2))
        rec.update(body='he_cu_closed', he_eyes='закрыты (Он 6)', he_mouth='закрыт', fx='—')
    elif f == 216:
        img = cached('smear', lambda: smear(L(RAW + 'he_cu_open_v1.png')))
        rec.update(body='he_cu_open SMEAR (1s)', he_eyes='широко (Он 3)', he_mouth='«о»', fx='вспышка, линии, тряска')
    else:
        f2 = q(f, 218, 2) if f >= 218 else f
        tt = (f2 - 217) / FPS
        bounce = 14 * np.exp(-tt * 5.5) * np.cos(tt * 26)
        if f == 217:
            bounce = 18

        def hair(sh, b=bounce):
            hgt = sh[0]
            y = np.arange(hgt, dtype=np.float32)
            wy = np.clip(1 - y / (hgt * 0.42), 0, 1) ** 1.5
            dy = np.repeat((-b * wy)[:, None], sh[1], 1)
            return None, dy
        img = char(RAW + 'he_cu_open_v1.png', (), hair, key=('hair', round(bounce, 1)))
        rec.update(body='he_cu_open', he_eyes='широко (Он 3)', he_mouth='«о»',
                   fx=f'волосы подпрыгивают ({bounce:+.0f}px, 2s)' + (', линии, тряска' if f < 228 else ''))
    lay = A.place(img, A.compose(cam, A.mat(s, pos=pos)))
    lay = A.light_layer(lay, 1, WARM_SHADOW, 0.14, RIM, 0.4, x0=0, x1=1500)
    over(out, lay)
    rgb = out[:, :, :3]
    if 216 <= f < 230:
        lines = A.radial_lines((640, 420), 46, 470, 1400, f)
        rgb = rgb + lines[:, :, None] * 0.75 * (1 - (f - 216) / 14)
    if f in (216, 217):
        rgb = rgb * (1 - (0.55 if f == 216 else 0.25)) + (0.55 if f == 216 else 0.25)
    rec.update(cam=f'CU, тряска {shake[0]:+.0f},{shake[1]:+.0f}' if f >= 216 and f < 228 else 'CU статика')
    return rgb


def mouth_at(f):
    """Lipsync on 2s: rhubarb cue under (frame + 1.5 lead) mapped to kit mouth."""
    f2 = q(f, VOICE_START - 2, 2)
    t = (f2 - VOICE_START + 1.5) / FPS
    for c in LIPSYNC:
        if c['start'] <= t < c['end']:
            return RHUBARB_TO_KIT[c['value']], c['value']
    return None, 'X'


def sh4a(f, rec):
    s0 = 264
    cam_bg = A.cam_mat(1.3, (1300, 470), parallax=1.0)
    out = bg_layer(LOC + 'bedroom_bedlevel_v1.png', 10, cam_bg)
    f2 = q(f, s0, 2)
    mouth, cue = mouth_at(f)
    eyes = None
    if 292 <= f2 < 294 or 298 <= f2 < 300:
        eyes = 'she_talk_eyes_half'
    elif 294 <= f2 < 298:
        eyes = 'she_talk_eyes_closed'
    laugh = f2 >= 302
    if laugh:
        mouth, eyes = 'laugh', 'she_talk_eyes_closed'
    elif mouth is None and f2 >= VOICE_START + 36:
        mouth = 'half'          # settling toward the laugh
    parts = ([eyes] if eyes else []) + ([f'she_talk_mouth_{mouth}'] if mouth else [])
    talking = VOICE_START - 2 <= f2 < VOICE_START + 36
    ang = (1.2 * np.sin((f2 - s0) / 5.0)) if talking else 0.0
    shake = (3.5 * (1 if (f2 // 2) % 2 else -1)) if laugh else 0.0
    hair_ph = np.sin((f2 - s0) / 7.0)

    def dfm(sh, a=ang, b=shake, hp=hair_ph):
        dx, dy = A.field_rotate(sh, (sh[1] * 0.47, sh[0] * 0.62), a, sh[0] * 0.33) if a else (None, None)
        bd = A.field_breath(sh, sh[0] * 0.55, sh[0], b)
        dy = bd if dy is None else dy + bd
        hm = cached('she_hairmask', lambda: A.color_mask(L(SHE + 'she_talk_base_v1.png'),
                                                          [A.hexrgb('#5A4237'), A.hexrgb('#443329'),
                                                           A.hexrgb('#634432')], 0.16, 8))
        yy = np.linspace(0, 1, sh[0], dtype=np.float32)[:, None]
        hx = 3.0 * hp * hm * yy ** 1.5
        dx = hx if dx is None else dx + hx
        return dx, dy
    img = char(SHE + 'she_talk_base_v1.png', parts, dfm, key=(round(ang, 2), shake, round(hair_ph, 2)))
    lay = A.place(img, A.mat(0.95, pos=(480, -40)))
    lay = A.light_layer(lay, 1, WARM_SHADOW, 0.15, RIM, 0.7, x0=600, x1=1500)
    over(out, lay)
    rgb = out[:, :, :3]
    rec.update(body='she_talk_base (деформация на 2)', she_eyes=eyes or 'эмоция 1 (весёлые)',
               she_mouth=(mouth or 'улыбка (отдых)') + f' [rhubarb {cue}]' if talking else (mouth or 'улыбка'),
               cam='MCU статика', fx='смех: плечи трясутся' if laugh else 'волосы качаются (2s)')
    return rgb


def sh4b(f, rec):
    s0 = 312
    out = bg_layer(LOC + 'bedroom_bedlevel_v1.png', 6, A.cam_mat(1.15, (1100, 560)))
    if f < 326:
        f3 = q(f, s0, 3)
        name = 'he_pillow_k1_v1'
        parts = ['he_pillow_k1_eyes_closed'] if 318 <= f3 < 324 else []
    elif f < 332:
        name, parts, f3 = 'he_pillow_k2_v1', [], q(f, 326, 2)
    else:
        name, parts, f3 = 'he_pillow_k3_v1', [], q(f, 332, 3)
    amp = 2.5 * np.sin(2 * np.pi * (f3 - s0) / (2.8 * FPS))
    img = char(RAW + name + '.png', parts, lambda sh, a=amp: (None, A.field_breath(sh, sh[0] * 0.55, sh[0], a)),
               key=round(amp, 2))
    s = W / img.shape[1] * 1.08
    lay = A.place(img, A.mat(s, pos=(-60, 1080 - img.shape[0] * s + 40)))
    lay = A.light_layer(lay, 1, WARM_SHADOW, 0.15, RIM, 0.4, x0=0, x1=1400)
    over(out, lay)
    rgb = out[:, :, :3]
    fade = np.clip((f - 344) / 15, 0, 1)
    rgb = rgb * (1 - fade)
    rec.update(body=name, he_eyes='закрыты' if parts else ('полуприкрыты (Он 4)' if name.endswith('k1_v1') else '—'),
               he_mouth='сонная улыбка' if 'k3' not in name else 'под подушкой', cam='MS статика',
               fx=f'затемнение {fade:.2f}' if fade else '—')
    return rgb


FG_CURVE = [(0, 905), (720, 900), (1000, 735), (1920, 690)]


def fg_matte():
    """Foreground duvet fold (DOF) trimmed by a matte curve: below his chin, above her waist cut."""
    def build():
        src = L('props/duvet_fg_v1.png')
        s = W / src.shape[1] * 1.12
        fg = A.place(src, A.mat(s, pos=(-60, -100)))
        xs = np.arange(W)
        yc = np.interp(xs, [p[0] for p in FG_CURVE], [p[1] for p in FG_CURVE])
        m = (np.arange(H)[:, None] >= yc[None, :]).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 14)
        fg = fg * m[:, :, None]
        return cv2.GaussianBlur(fg, (0, 0), 7)
    return cached('fgm', build)
DUST1 = A.Dust(110, 1)
DUST2 = A.Dust(80, 2)
SHOTS = [(0, 96, sh1, 'SH1'), (96, 192, sh2, 'SH2'), (192, 264, sh3, 'SH3'), (264, 312, sh4a, 'SH4a'),
         (312, 360, sh4b, 'SH4b')]


def render_frame(f):
    rec = {'f': f}
    for a, b, fn, name in SHOTS:
        if a <= f < b:
            rec['shot'] = name
            rgb = fn(f, rec)
            break
    grade = (1.02, 1.0, 0.97)
    rgb = A.finish(np.ascontiguousarray(rgb, np.float32), f, grade=grade, seed=1)
    return rgb, rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', default=f'0:{N}')
    ap.add_argument('--stills', default='')
    ap.add_argument('--out', default='shots/shot01/render/shot01_picture_v1.mp4')
    ap.add_argument('--no-video', action='store_true')
    a = ap.parse_args()
    f0, f1 = map(int, a.frames.split(':'))
    stills = {int(x) for x in a.stills.split(',') if x}
    Path('shots/shot01/render/stills').mkdir(parents=True, exist_ok=True)
    proc = None
    if not a.no_video:
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                                 '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                                 '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    recs = []
    for f in range(f0, f1):
        rgb, rec = render_frame(f)
        bgr = A.to_u8_bgr(rgb)
        if proc:
            proc.stdin.write(bgr.tobytes())
        if f in stills:
            cv2.imwrite(f'shots/shot01/render/stills/f{f:04d}.png', bgr)
        recs.append(rec)
        if f % 24 == 0:
            print('frame', f, flush=True)
    if proc:
        proc.stdin.close()
        proc.wait()
    json.dump(recs, open('shots/shot01/render/xsheet_records.json', 'w'), ensure_ascii=False)


if __name__ == '__main__':
    main()
