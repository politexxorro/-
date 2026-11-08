"""QA comparison sheet: reference faces vs frames of each scene (Section 13/14 of RULES)."""
import glob

import cv2
import numpy as np

rows = []
refs = ['characters/approved/she_emotions_nomole.png', 'characters/approved/he_emotions_hoodie_v1.png',
        'characters/approved/height_sheet_v2.png']


def tile(p, w=360, h=203):
    im = cv2.imread(p)
    return cv2.resize(im, (w, h))


row = [tile(r) for r in refs] + [np.zeros((203, 360, 3), np.uint8)] * 2
rows.append(np.hstack(row))
for s in range(1, 8):
    st = sorted(glob.glob(f'shots/shot0{s}/render/stills/f*.png'))
    pick = [st[int(i * (len(st) - 1) / 4)] for i in range(5)] if len(st) >= 5 else st + [st[-1]] * (5 - len(st))
    r = [tile(p) for p in pick]
    cv2.putText(r[0], f'SCENE {s}', (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    rows.append(np.hstack(r))
cv2.putText(rows[0], 'REFERENCE', (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.imwrite('qa_comparison.jpg', np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
