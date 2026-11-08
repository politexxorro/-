"""Photo strip prop built from the four approved booth photos (no AI text possible)."""
import cv2
import numpy as np

W, PAD = 420, 22
ph = []
for i in range(1, 5):
    im = cv2.imread(f'shots/shot03/raw/photo{i}_v1.png')[:, :, :3]
    h, w = im.shape[:2]
    c = im[:, (w - int(h * 1.25)) // 2:(w + int(h * 1.25)) // 2]  # 5:4 crop around the couple
    ph.append(cv2.resize(c, (W - 2 * PAD, int((W - 2 * PAD) * 0.8)), interpolation=cv2.INTER_AREA))
hh = sum(p.shape[0] for p in ph) + PAD * 5 + 40
strip = np.full((hh, W, 4), 255, np.uint8)
strip[:, :, :3] = (250, 251, 252)
y = PAD
for p in ph:
    strip[y:y + p.shape[0], PAD:PAD + p.shape[1], :3] = p
    y += p.shape[0] + PAD
# soft rounded corners
m = np.zeros((hh, W), np.uint8)
cv2.rectangle(m, (8, 0), (W - 9, hh - 1), 255, -1)
cv2.rectangle(m, (0, 8), (W - 1, hh - 9), 255, -1)
for cx, cy in [(8, 8), (W - 9, 8), (8, hh - 9), (W - 9, hh - 9)]:
    cv2.circle(m, (cx, cy), 8, 255, -1)
strip[:, :, 3] = m
cv2.imwrite('props/photostrip_v1.png', strip)
print(strip.shape)
