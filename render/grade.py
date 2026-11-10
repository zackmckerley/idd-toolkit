"""Colour grade for the finished renderings.
    python3 render/grade.py in.png out.png [--wb] [--ref INSPIRATION.png [--ref-strength 0.7]]
Default: pull the orange out of the wood (the scans run warm under AgX), a touch less saturation overall, no change to whites.
--wb   neutralise a colour cast on the bright, low-saturation pixels (walls, trim), to a warm neutral.
--ref  grade to the owner's inspiration photograph (owner 11.09.26: "match the ceiling, cabinet, floor and stone colour to the
       image"): the render's light distribution in CIELAB is moved toward the reference's (mean and spread per channel, at
       --ref-strength), the way a photographer grades a set to a reference. It sets the overall key and warmth; it does not
       change which material is which. Use it after --wb, and check the four picks (ceiling, cabinets, floor, stone) against
       the reference side by side afterwards."""
import sys, numpy as np
from PIL import Image

a_ = sys.argv
im = Image.open(a_[1]).convert('RGB')
if '--wb' in a_:
    a = np.array(im).astype(np.float32); mx = a.max(axis=2); mn = a.min(axis=2)
    m = (mx > 150) & ((mx - mn) < 40)
    if m.sum() > 1000:
        mean = a[m].mean(axis=0); tgt = mean.mean() * np.array([1.0, 0.985, 0.95])
        a = np.clip(a * (tgt / mean), 0, 255); im = Image.fromarray(a.astype(np.uint8))
hsv = np.array(im.convert('HSV')).astype(np.float32)
h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1], hsv[..., 2]
w = np.clip(1 - np.abs(h - 28) / 22, 0, 1)                     # weight: oranges and ambers (about 6 to 50 degrees)
s = s * (1 - (0.0 if '--ref' in a_ else 0.42) * w) * (1.0 if '--ref' in a_ else 0.93)
hsv[..., 1] = np.clip(s, 0, 255)
im = Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')


def _to_lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def _from_lab(lab):
    fy = (lab[..., 0] + 16) / 116; fx = fy + lab[..., 1] / 500; fz = fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    Mi = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
    c = xyz @ Mi.T
    c = np.where(c > 0.0031308, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055, 12.92 * c)
    return np.clip(c * 255, 0, 255)


if '--ref' in a_:
    ref = np.array(Image.open(a_[a_.index('--ref') + 1]).convert('RGB')).astype(np.float32)
    k = float(a_[a_.index('--ref-strength') + 1]) if '--ref-strength' in a_ else 0.7
    src = np.array(im).astype(np.float32)
    ls, lr = _to_lab(src), _to_lab(ref)
    out = ls.copy()
    for c in range(3):
        ms, ss = ls[..., c].mean(), ls[..., c].std() + 1e-6
        mr, sr = lr[..., c].mean(), lr[..., c].std() + 1e-6
        moved = (ls[..., c] - ms) * (sr / ss) + mr
        out[..., c] = ls[..., c] * (1 - k) + moved * k
    im = Image.fromarray(_from_lab(out).astype(np.uint8))
    print('graded to', a_[a_.index('--ref') + 1], 'at', k)
if '--win' in a_:
    # window pull: inside the exterior-glass mask, take the view outside down by --win-ev stops (default 1.5) in linear light and give
    # back a little contrast, so the garden, pool and pool house read instead of a white sheet
    m = np.asarray(Image.open(a_[a_.index('--win') + 1]).convert('L').resize(im.size), np.float32)[..., None] / 255.0
    c = np.asarray(im, np.float32) / 255.0
    if '--ext' in a_:   # the bracketed exterior render from photoreal.py --winpull: real detail, not a darkened white
        ext_ = np.asarray(Image.open(a_[a_.index('--ext') + 1]).convert('RGB').resize(im.size), np.float32) / 255.0
        bev = float(a_[a_.index('--ext-ev') + 1]) if '--ext-ev' in a_ else 3.0
        # merge, do not swap: a dark view out (shaded planting) keeps the main exposure; only where the main frame clips does the
        # bracket's value (scaled back up by its stops) stand in; then one smooth shoulder brings the sky and the white pool house
        # under white. A straight swap darkened the already dark garden to black in the oblique view (11.10.26)
        _lin = lambda v: np.where(v > 0.04045, ((v + 0.055) / 1.055) ** 2.4, v / 12.92)
        _srgb = lambda v: np.where(v > 0.0031308, 1.055 * np.clip(v, 0, None) ** (1 / 2.4) - 0.055, 12.92 * v)
        ml_, el_ = _lin(c), _lin(ext_) * (2.0 ** bev)
        t_ = np.clip((ml_.max(axis=2, keepdims=True) - 0.55) / 0.35, 0, 1)          # how near the main frame is to clipping
        L_ = ml_ * (1 - t_) + np.maximum(el_, ml_) * t_
        # the shoulder: shadows (under 0.05 linear) as shot, the bracket's top (2^EV) to 0.92 (0.7 read as tinted glass), a power curve between them;
        # close to the plain bracket in the bright sky and the white pool house, and it never darkens shade (a log curve washed out)
        knee, Lm, top = 0.05, 2.0 ** bev, 0.92; g_ = np.log(knee / top) / np.log(knee / Lm)
        # the curve runs on luminance and the colour is scaled with it, so the garden keeps its colour (per channel it went grey)
        Y_ = (L_ * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(axis=2, keepdims=True)
        Yo = np.where(Y_ < knee, Y_, top * (np.clip(Y_, knee, None) / Lm) ** g_)
        pulled = np.clip(_srgb(np.clip(L_ * Yo / np.maximum(Y_, 1e-6), 0, 1)), 0, 1)
        ev = f'bracket merge ({bev:g} EV)'
    else:
        ev = float(a_[a_.index('--win-ev') + 1]) if '--win-ev' in a_ else 1.5
        lin_ = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92) * (2.0 ** -ev)
        pulled = np.where(lin_ > 0.0031308, 1.055 * np.clip(lin_, 0, None) ** (1 / 2.4) - 0.055, 12.92 * lin_)
        pulled = np.clip((pulled - 0.5) * 1.12 + 0.5, 0, 1)
    m = m * (float(a_[a_.index('--win-strength') + 1]) if '--win-strength' in a_ else 1.0)   # 0.5: half the pull (full read as tinted glass in the living room)
    im = Image.fromarray((np.clip(c * (1 - m) + pulled * m, 0, 1) * 255).astype(np.uint8))
    print('window pull', ev, 'stops on', round(float(m.mean()) * 100, 1), 'percent of the frame')
im.save(a_[2])
