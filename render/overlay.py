"""Geometry check for an image-model finish: does the AI picture still match the Blender base?

    python3 render/overlay.py BASE.png AI.png OUT.png [--tol 6] [--grid 6x4]

The image model repaints materials well but is free to move geometry (Autodesk's 2025 test: Nano Banana
"reinterprets" stairs and railings where depth-conditioned models keep them). This script:
  1. resizes the AI image to the base, finds strong edges in both (Sobel magnitude, top 12 percent),
  2. counts, per cell of a grid, the base edges with no AI edge within --tol px (a moved, missing or
     shortened piece) and the AI edges with no base edge (an invented piece),
  3. writes OUT: the AI image greyed, base edges that survived in green, base edges lost in red,
     invented AI edges in blue, and the worst cells boxed with their scores.
A cell over 40 percent lost or invented is printed as CHECK. It does not judge materials or color; read
those against the chips. It flags where to look; the object-by-object check is still done by eye.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def edges(img, keep=0.12):
    g = np.asarray(img.convert('L').filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32)
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    m = np.hypot(gx, gy)
    return m > np.quantile(m, 1 - keep)


def dilate(mask, r):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            out |= np.roll(np.roll(mask, dy, 0), dx, 1)
    return out


def main(a):
    base_p, ai_p, out_p = a[:3]
    tol = int(a[a.index('--tol') + 1]) if '--tol' in a else 6
    gx_, gy_ = (int(v) for v in (a[a.index('--grid') + 1] if '--grid' in a else '6x4').split('x'))
    base = Image.open(base_p).convert('RGB')
    ai = Image.open(ai_p).convert('RGB')
    # the model may return another aspect (Nano Banana gave 1376 x 768 for a 1800 x 1125 base): crop the base to the
    # AI aspect about its center, then register with a small scale and shift search on edge overlap
    ra, rb = ai.width / ai.height, base.width / base.height
    if abs(ra - rb) > 0.01:
        if ra > rb:
            h = round(base.width / ra); t = (base.height - h) // 2; base = base.crop((0, t, base.width, t + h))
        else:
            w = round(base.height * ra); l_ = (base.width - w) // 2; base = base.crop((l_, 0, l_ + w, base.height))
        print(f'aspect differs: base cropped to {base.width} x {base.height} to match the AI image')
    W0 = 1200
    base = base.resize((W0, round(W0 * base.height / base.width)), Image.LANCZOS)
    ai = ai.resize(base.size, Image.LANCZOS)
    eb = edges(base); ea0 = edges(ai); best = (-1, 1.0, 0, 0)
    small_b = eb[::4, ::4]
    for sc in (0.94, 0.97, 1.0, 1.03, 1.06, 1.09, 1.12):
        w2, h2 = round(base.width * sc), round(base.height * sc)
        a2 = ai.resize((w2, h2), Image.BILINEAR)
        for dx in range(-24, 25, 8):
            for dy in range(-24, 25, 8):
                l_, t = (w2 - base.width) // 2 - dx, (h2 - base.height) // 2 - dy
                cand = Image.new('RGB', base.size); cand.paste(a2, (-l_, -t))
                e = edges(cand)[::4, ::4]
                score = (small_b & dilate(e, 1)).sum()
                if score > best[0]: best = (score, sc, dx, dy)
    _, sc, dx, dy = best
    w2, h2 = round(base.width * sc), round(base.height * sc)
    cand = Image.new('RGB', base.size); cand.paste(ai.resize((w2, h2), Image.LANCZOS), (-((w2 - base.width) // 2 - dx), -((h2 - base.height) // 2 - dy)))
    ai = cand
    print(f'registered: scale {sc}, shift {dx},{dy} px')
    ea = edges(ai)
    lost = eb & ~dilate(ea, tol)
    invented = ea & ~dilate(eb, tol)
    kept = eb & ~lost
    grey = np.asarray(ai.convert('L').convert('RGB'), dtype=np.float32) * 0.55 + 90
    o = grey.copy()
    o[kept] = (40, 170, 60)
    o[lost] = (220, 30, 30)
    o[invented] = (40, 90, 230)
    out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    H, W = eb.shape
    cells = []
    for j in range(gy_):
        for i in range(gx_):
            ys, ye = j * H // gy_, (j + 1) * H // gy_
            xs, xe = i * W // gx_, (i + 1) * W // gx_
            nb = eb[ys:ye, xs:xe].sum() or 1
            na = ea[ys:ye, xs:xe].sum() or 1
            pl = lost[ys:ye, xs:xe].sum() / nb
            pi = invented[ys:ye, xs:xe].sum() / na
            cells.append((max(pl, pi), pl, pi, i, j, (xs, ys, xe, ye)))
    tot_l = lost.sum() / max(1, eb.sum())
    tot_i = invented.sum() / max(1, ea.sum())
    print(f'whole image: {tot_l:.0%} of base edges lost, {tot_i:.0%} of AI edges invented (tol {tol}px)')
    for s, pl, pi, i, j, box in sorted(cells, reverse=True):
        flag = 'CHECK' if s > 0.40 else 'ok'
        print(f'cell col {i + 1} row {j + 1}: lost {pl:.0%}, invented {pi:.0%}  {flag}')
        if s > 0.40:
            d.rectangle(box, outline=(255, 200, 0), width=4)
            d.text((box[0] + 8, box[1] + 6), f'{pl:.0%} lost / {pi:.0%} new', fill=(255, 220, 0))
    out.save(out_p)
    print('wrote', out_p)


if __name__ == '__main__':
    main(sys.argv[1:])
