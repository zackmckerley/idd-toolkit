"""Colour grade for the finished renderings: pull the orange out of the wood (the scans run warm under AgX), a touch less
saturation overall, no change to whites. python3 render/grade.py in.png out.png"""
import sys, numpy as np
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
if '--wb' in sys.argv:   # neutralise a colour cast: the bright, low-saturation pixels (walls, trim) brought to a warm neutral
    a = np.array(im).astype(np.float32); mx = a.max(axis=2); mn = a.min(axis=2)
    m = (mx > 150) & ((mx - mn) < 40)
    if m.sum() > 1000:
        mean = a[m].mean(axis=0); tgt = mean.mean() * np.array([1.0, 0.985, 0.95])
        a = np.clip(a * (tgt / mean), 0, 255); im = Image.fromarray(a.astype(np.uint8))
hsv = np.array(im.convert('HSV')).astype(np.float32)
h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1], hsv[..., 2]
w = np.clip(1 - np.abs(h - 28) / 22, 0, 1)                     # weight: oranges and ambers (about 6 to 50 degrees)
s = s * (1 - 0.42 * w) * 0.93
hsv[..., 1] = np.clip(s, 0, 255)
Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB').save(sys.argv[2])
