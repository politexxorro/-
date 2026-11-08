"""Compare pop magnitudes old vs new at previously detected within-shot boundaries."""
import cv2
import numpy as np


def diffs(src):
    cap = cv2.VideoCapture(src)
    prev = None
    out = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(fr, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            out.append(float(np.abs(g - prev).mean()))
        prev = g
    cap.release()
    return np.array(out)


old = diffs('final_1080p_share.mp4')
new = diffs('final.mp4')
np.save('/tmp/old.npy', old)
np.save('/tmp/new.npy', new)
cuts = {336, 720, 1152, 1632, 2016, 2448}
sel = [i for i in range(len(old)) if old[i] > 10 and not any(abs(i + 1 - c) < 2 for c in cuts)
       and (i == 0 or old[i - 1] < 0.6 * old[i])]
print('within-shot pops in old:', len(sel))
print('old mean step at pops:', round(old[sel].mean(), 1), ' max:', round(old[sel].max(), 1))
print('new mean step at same:', round(new[sel].mean(), 1), ' max:', round(new[sel].max(), 1))
print('new local max (i-1..i+1):', round(np.maximum(np.maximum(new[[max(0, i - 1) for i in sel]], new[sel]),
                                                    new[[min(len(new) - 1, i + 1) for i in sel]]).mean(), 1))
