"""Median colour at hand-picked points on the reference sheets (points chosen via grid_crop.py).

r = sampling radius: 2 -> 5x5 median for flat fills, 0 -> single pixel for thin lines.
"""
import statistics as st
from PIL import Image

R = 'characters/reference/'
PTS = {
    'she_emotions.png': {
        'skin': (170, 210, 2), 'skin_shadow_neck': (207, 267, 1), 'iris': (177, 170, 1), 'mole': (264, 190, 0),
        'mouth_inner': (210, 233, 1), 'lower_lip': (212, 247, 1), 'hair_light': (150, 133, 1), 'hair_dark': (300, 217, 1),
        'jaw_outline': (220, 274, 0), 'blush': (1310, 213, 2), 'lips_closed': (1340, 255, 0),
    },
    'she_fullbody_4views.png': {
        'hoodie': (120, 337, 2), 'hoodie_shadow': (310, 360, 1), 'tshirt': (227, 353, 2), 'hair': (173, 337, 1),
        'chain': (229, 280, 0), 'outline': (121, 267, 0), 'pants': (130, 893, 2), 'pants_stripe': (103, 927, 0),
        'sneaker': (160, 987, 2), 'sneaker_sole_insert': (160, 997, 1),
    },
    'he_emotions.png': {
        'skin': (153, 213, 2), 'iris': (170, 180, 0), 'hair': (220, 130, 1), 'mouth_inner': (210, 267, 1),
        'jacket': (50, 450, 2), 'piping': (60, 412, 0), 'tshirt': (200, 457, 2), 'chain': (207, 428, 0),
        'skin_neck': (200, 353, 2), 'neck_shadow': (200, 330, 1), 'blush': (1320, 227, 2), 'skin_s4': (1370, 260, 2),
    },
    'he_fullbody_4views.png': {
        'hoodie': (110, 250, 2), 'plaid_mix': (165, 250, 3), 'tshirt': (220, 267, 2), 'skin_neck': (200, 183, 2),
        'jeans': (110, 893, 2), 'jeans_shadow': (100, 932, 1), 'sneaker_white': (100, 987, 1), 'sneaker_grey': (157, 987, 1),
        'sneaker_sole': (120, 1005, 1),
    },
}
for f, d in PTS.items():
    im = Image.open(R + f).convert('RGB')
    print(f)
    for n, (x, y, r) in d.items():
        px = [im.getpixel((x + i, y + j)) for i in range(-r, r + 1) for j in range(-r, r + 1)]
        c = tuple(int(st.median(p[k] for p in px)) for k in range(3))
        print(f'  {n:20s} #{c[0]:02X}{c[1]:02X}{c[2]:02X}')
