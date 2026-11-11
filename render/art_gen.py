"""Original staging paintings for the renders, generated stroke by stroke (no copied artwork): each writes a colour map and an
impasto height map to render/art/<name>_col.png and <name>_h.png. The owner gives a reference for mood and palette (11.11.26);
the composition here is our own.

    python3 render/art_gen.py            # all
    python3 render/art_gen.py meadow     # one
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'art')


def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


class Canvas:
    def __init__(self, w, h, ground, seed):
        self.w, self.h = w, h; self.rng = np.random.default_rng(seed)
        self.col = np.ones((h, w, 3)) * hexc(ground); self.hgt = np.zeros((h, w))
        self._streak = {}

    def streak(self, n, ang):
        """A brush-hair streak field n x n, hairs along `ang` (radians)."""
        base = ndi.gaussian_filter(self.rng.random((n, n)), sigma=(0.7, max(4.0, n / 10)))
        base = (base - base.min()) / (np.ptp(base) + 1e-9)
        return ndi.rotate(base, math.degrees(ang), reshape=False, order=1, mode='reflect')

    def stroke(self, pts, width, color, thick=1.0, dry=0.0, mix=None, alpha=1.0, vary=0.16):
        pts = np.asarray(pts, float)
        x0, y0 = np.floor(pts.min(0) - width).astype(int); x1, y1 = np.ceil(pts.max(0) + width).astype(int)
        x0c, y0c, x1c, y1c = max(x0, 0), max(y0, 0), min(x1, self.w), min(y1, self.h)
        if x1c - x0c < 2 or y1c - y0c < 2: return
        bw, bh = x1 - x0, y1 - y0
        m = Image.new('L', (bw, bh), 0); d = ImageDraw.Draw(m)
        loc = [(float(p[0] - x0), float(p[1] - y0)) for p in pts]
        d.line(loc, fill=255, width=max(1, int(width)), joint='curve')
        r = width / 2.0
        for p in (loc[0], loc[-1]): d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)
        mask = ndi.gaussian_filter(np.asarray(m, float) / 255.0, 0.8)
        dv = pts[-1] - pts[0]; ang = math.atan2(dv[1], dv[0]) if np.hypot(*dv) > 1e-6 else 0.0
        n = int(max(bw, bh) * 1.45) + 4
        st = self.streak(n, -ang); oy, ox = (n - bh) // 2, (n - bw) // 2; st = st[oy:oy + bh, ox:ox + bw]
        if dry > 0: mask = mask * np.clip((st - dry * 0.6) / (1 - dry * 0.6 + 1e-6) * 1.8, 0, 1)
        mask *= alpha
        c = hexc(color) if isinstance(color, str) else np.asarray(color, float)
        cc = np.clip(c[None, None, :] * (1 + vary * (st[..., None] - 0.5) * 2), 0, 1)
        if mix is not None:                                    # wet mixing: a second colour folded in along the hairs
            mc = hexc(mix); k = np.clip((st - 0.55) * 2.5, 0, 1)[..., None] * 0.7
            cc = cc * (1 - k) + mc[None, None, :] * k
        sl = (slice(y0c - y0, y1c - y0), slice(x0c - x0, x1c - x0)); tl = (slice(y0c, y1c), slice(x0c, x1c))
        a = mask[sl][..., None]
        self.col[tl] = self.col[tl] * (1 - a) + cc[sl] * a
        ridge = np.clip(mask[sl] * (1 - mask[sl]) * 4, 0, 1)
        self.hgt[tl] = self.hgt[tl] * (1 - 0.6 * mask[sl]) + mask[sl] * thick * (0.5 + 0.9 * st[sl]) + ridge * thick * 0.6

    def curve(self, x, y, ang, length, bend=0.0, n=10):
        pts = []; a = ang
        for i in range(n):
            pts.append((x, y)); x += math.cos(a) * length / (n - 1); y += math.sin(a) * length / (n - 1); a += bend / (n - 1)
        return pts

    def canvas_weave(self, k=0.035):
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        weave = (np.sin(xx * 1.9) * np.sin(yy * 1.9)) * 0.5 + 0.5
        self.col *= (1 - k + k * weave)[..., None]; self.hgt += weave * 0.08

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        Image.fromarray((np.clip(self.col, 0, 1) ** (1 / 1.0) * 255).astype(np.uint8)).save(os.path.join(OUT, name + '_col.png'))
        h = self.hgt - self.hgt.min(); h = h / (h.max() + 1e-9)
        Image.fromarray((h * 255).astype(np.uint8)).save(os.path.join(OUT, name + '_h.png'))


def landscape():
    """Over the TV, 36 x 96 in.: an impasto valley read vertically, a peach and coral sky, teal ridges, an ember horizon and a
    field of thick petals in red, orange, ochre, pink, mint and sky blue that grow toward the bottom."""
    W, H = 540, 1440; c = Canvas(W, H, '#F1D6C2', 11); R = c.rng
    sky = ['#F4DCC8', '#F6CDB6', '#F2B9A0', '#EFA184', '#F7E4D3', '#E98C6A', '#F3C7C0']
    for _ in range(260):
        y = R.uniform(0, 0.36 * H); x = R.uniform(-60, W)
        c.stroke(c.curve(x, y, R.normal(0.05, 0.25), R.uniform(80, 260), R.normal(0, 0.6)), R.uniform(10, 34),
                 sky[R.integers(len(sky))], thick=0.8, mix=sky[R.integers(len(sky))], dry=0.15)
    def ridge(x, base, amp, ph): return base + amp * (0.55 * np.sin(x / W * 5.1 + ph) + 0.3 * np.sin(x / W * 11.3 + 2 * ph) + 0.15 * np.sin(x / W * 23 + ph))
    for (base, amp, cols, ph) in ((0.34, 0.06, ['#3F7F7A', '#5E9C8F', '#2E6A6A', '#86B6A2'], 0.4),
                                  (0.42, 0.05, ['#1F5560', '#2C6B71', '#173F4A', '#4E8A80'], 2.1)):
        for _ in range(520):
            x = R.uniform(-20, W + 20); top = ridge(x, base * H, amp * H, ph)
            y = R.uniform(top, top + 0.09 * H); a = R.choice([-0.55, 0.55, -0.35, 0.35]) + R.normal(0, 0.15)
            c.stroke(c.curve(x, y, a, R.uniform(30, 90), R.normal(0, 0.3)), R.uniform(9, 22), cols[R.integers(len(cols))],
                     thick=1.2, mix=cols[R.integers(len(cols))])
        for _ in range(60):                                    # wine shadows in the folds
            x = R.uniform(0, W); top = ridge(x, base * H, amp * H, ph)
            c.stroke(c.curve(x, top + R.uniform(20, 70), R.uniform(-0.6, 0.6), R.uniform(30, 70)), R.uniform(8, 16),
                     R.choice(['#7A1E2B', '#5C1A26', '#9A2B2B']), thick=1.3)
    for _ in range(260):                                       # the ember horizon
        y = R.normal(0.505 * H, 0.018 * H); x = R.uniform(-40, W)
        c.stroke(c.curve(x, y, R.normal(0, 0.08), R.uniform(60, 180)), R.uniform(8, 20),
                 R.choice(['#E8471F', '#F06A2A', '#D8331E', '#F49A4A', '#C92A23']), thick=1.4, mix='#F7C06A')
    petals = ['#C8102E', '#E0301E', '#F06A1E', '#F2A31B', '#E7B23A', '#F4A7A0', '#EBC7BC', '#7FC4B4', '#5FA3C9', '#2C6E73',
              '#9E1B2F', '#F7E2C4', '#D9682B', '#B5D8CF']
    for i in range(1500):
        t = (i / 1500) ** 0.8; y = 0.52 * H + t * 0.5 * H + R.normal(0, 18); s = 0.35 + 1.1 * t
        x = R.uniform(-30, W + 30); a = -math.pi / 2 + R.normal(0, 0.45)
        col = petals[R.integers(len(petals))]
        c.stroke(c.curve(x, y + 40 * s, a, R.uniform(40, 110) * s, R.normal(0, 0.9)), R.uniform(18, 46) * s, col,
                 thick=2.2 + 1.5 * t, mix=petals[R.integers(len(petals))] if R.random() < 0.4 else None, vary=0.22)
    c.save('landscape')


def abstract():
    """West wall, 48 x 48 in.: a gestural abstract, palette-knife blocks of magenta, cobalt, cadmium yellow and white over a
    violet and navy ground, two sweeping indigo arcs, red and black scratches."""
    W = H = 1200; c = Canvas(W, H, '#5B3A8C', 23); R = c.rng
    ground = ['#6E4AA8', '#3C3F9E', '#8B4FB3', '#2A2F7A', '#B256A6', '#4A5DC4', '#C46FB5']
    for _ in range(420):
        c.stroke(c.curve(R.uniform(-100, W), R.uniform(-50, H + 50), R.normal(0, 0.5), R.uniform(120, 360), R.normal(0, 0.4)),
                 R.uniform(30, 80), ground[R.integers(len(ground))], thick=0.6, dry=0.25, mix=ground[R.integers(len(ground))])
    def block(x, y, w, h, col, ang=0.0, dry=0.3):
        n = int(max(w, h) / 9) + 2
        for k in range(n):                                       # knife pulls side by side make the block
            yy = y + (k + 0.5) * h / n
            c.stroke([(x, yy), (x + w, yy + w * math.tan(ang))], h / n * 1.6, col, thick=1.6, dry=dry, vary=0.25)
    blocks = [('#F4F3F1', 0.17, 0.07, 0.22, 0.30), ('#E5338E', 0.62, 0.10, 0.26, 0.24), ('#F7C21B', 0.11, 0.47, 0.20, 0.26),
              ('#1F57C3', 0.70, 0.02, 0.24, 0.18), ('#F4F3F1', 0.72, 0.27, 0.22, 0.20), ('#F7C21B', 0.58, 0.32, 0.12, 0.30),
              ('#C42A7A', 0.24, 0.63, 0.26, 0.24), ('#F26A1B', 0.60, 0.72, 0.24, 0.13), ('#1D2A7A', 0.02, 0.70, 0.22, 0.25),
              ('#E5338E', 0.42, 0.18, 0.15, 0.14), ('#2F86D9', 0.82, 0.62, 0.18, 0.30), ('#F4F3F1', 0.40, 0.38, 0.12, 0.10)]
    for (col, x, y, w, h) in blocks:
        block(x * W, y * H, w * W, h * H, col, R.normal(0, 0.05), dry=R.uniform(0.15, 0.45))
    for (cx, cy, r, a0, a1, col, wd) in ((0.95, 0.95, 0.62, math.pi * 1.02, math.pi * 1.48, '#1E2559', 70),
                                         (0.05, 1.05, 0.70, math.pi * 1.55, math.pi * 1.95, '#2A2F6E', 58),
                                         (0.52, 0.55, 0.46, math.pi * 0.95, math.pi * 1.35, '#D7263D', 14)):
        pts = [((cx + r * math.cos(a0 + (a1 - a0) * i / 30)) * W, (cy + r * math.sin(a0 + (a1 - a0) * i / 30)) * H) for i in range(31)]
        c.stroke(pts, wd, col, thick=2.0, dry=0.2, vary=0.3)
    for _ in range(70):                                        # scratches
        x, y = R.uniform(0, W), R.uniform(0, H)
        c.stroke(c.curve(x, y, R.uniform(0, math.pi), R.uniform(60, 260), R.normal(0, 0.5)), R.uniform(1.5, 3.5),
                 R.choice(['#111018', '#F4F3F1', '#D7263D', '#0E1640']), thick=0.4, vary=0.05)
    c.save('abstract')


def pinkfield():
    """South wall, 36 x 48 in.: a colour field, a warm pink ground over most of it, a dry cream band two thirds down, a thin
    rose line and a deep raspberry base, brushed on raw canvas."""
    W, H = 900, 1200; c = Canvas(W, H, '#E4558F', 37); R = c.rng
    for _ in range(900):
        y = R.uniform(-20, 0.66 * H)
        c.stroke(c.curve(R.uniform(-80, W), y, R.normal(0, 0.06), R.uniform(150, 420)), R.uniform(20, 50),
                 R.choice(['#E4558F', '#E8659A', '#DD4A86', '#EC77A6', '#E25C93']), thick=0.4, dry=0.35, vary=0.08)
    for _ in range(160):
        y = R.normal(0.685 * H, 0.012 * H)
        c.stroke(c.curve(R.uniform(-60, W), y, R.normal(0, 0.03), R.uniform(120, 360)), R.uniform(8, 22),
                 R.choice(['#F3E7E3', '#EDE0DA', '#F8F1EC', '#E9C9CF']), thick=0.7, dry=0.45, vary=0.1)
    for _ in range(140):
        y = R.uniform(0.705 * H, 0.735 * H)
        c.stroke(c.curve(R.uniform(-60, W), y, 0, R.uniform(150, 380)), R.uniform(8, 18),
                 R.choice(['#E0477F', '#D63A75']), thick=0.4, dry=0.3, vary=0.08)
    for _ in range(700):
        y = R.uniform(0.73 * H, H + 20)
        c.stroke(c.curve(R.uniform(-80, W), y, R.normal(0, 0.05), R.uniform(150, 420)), R.uniform(20, 46),
                 R.choice(['#B81D5B', '#A8174F', '#C02867', '#9E1449']), thick=0.4, dry=0.3, vary=0.1)
    c.canvas_weave(0.06); c.save('pinkfield')


def meadow():
    """The reading nook, 60 x 38 in.: a night meadow, a scraped deep green ground darkening to the bottom, fine grasses and
    wildflowers (marigold, coral, crimson, blush, cream) thickest in the lower half, a few floating higher."""
    W, H = 1500, 950; c = Canvas(W, H, '#2C4638', 51); R = c.rng
    for _ in range(900):
        y = R.uniform(-30, H + 30); t = y / H
        cols = ['#3E5E4C', '#36574A', '#2E4A3F', '#46685A', '#2A443A'] if t < 0.55 else ['#22382E', '#1B2E26', '#26402F', '#162620']
        c.stroke(c.curve(R.uniform(-100, W), y, R.normal(0, 0.25), R.uniform(80, 260), R.normal(0, 0.3)), R.uniform(20, 60),
                 cols[R.integers(len(cols))], thick=0.5, dry=0.35, vary=0.15)
    for _ in range(2600):                                       # grasses
        x = R.uniform(0, W); yb = H + 10; ht = R.uniform(0.15, 0.6) * H
        c.stroke(c.curve(x, yb, -math.pi / 2 + R.normal(0, 0.08), ht, R.normal(0, 0.25), n=8), R.uniform(1.2, 3.2),
                 R.choice(['#2F5A3A', '#3E6B3F', '#58784A', '#24452F', '#6E8A55', '#1E3A2A']), thick=0.5, vary=0.1)
    def flower(x, y, r, col, eye):
        k = int(R.integers(5, 9))
        for i in range(k):
            a = 2 * math.pi * i / k + R.normal(0, 0.15)
            c.stroke([(x + math.cos(a) * r * 0.2, y + math.sin(a) * r * 0.2), (x + math.cos(a) * r, y + math.sin(a) * r * 0.75)],
                     r * 0.75, col, thick=2.0, vary=0.2)
        c.stroke([(x - 1, y), (x + 1, y)], r * 0.55, eye, thick=2.4)
    fl = [('#F2A93B', '#7A4A12'), ('#F6C443', '#8A5A12'), ('#E8553A', '#5A1E12'), ('#C9283A', '#3A0E12'),
          ('#F2A3A8', '#B05060'), ('#F4EFE2', '#C9A13A'), ('#F08A3E', '#6A2E12')]
    for _ in range(170):
        t = min(1.0, abs(R.normal(0.62, 0.17))); x = R.uniform(30, W - 30); y = t * H
        if y > H - 30: continue
        r = R.uniform(7, 15) * (0.75 + 0.4 * (1 - t))
        c.stroke(c.curve(x, y, math.pi / 2 + R.normal(0, 0.1), H - y), 2.0, '#3F6B3E', thick=0.5)
        col, eye = fl[R.integers(len(fl))]; flower(x, y, r, col, eye)
    for _ in range(700):                                       # specks of small flowers low down
        x = R.uniform(0, W); y = R.uniform(0.55, 0.97) * H; r = R.uniform(1.5, 3.5)
        c.stroke([(x, y), (x + 1, y)], r * 2, R.choice(['#E46A7A', '#F4EFE2', '#D9384A', '#F2B04A', '#C77FB0']), thick=1.2)
    c.save('meadow')


ALLG = {'landscape': landscape, 'abstract': abstract, 'pinkfield': pinkfield, 'meadow': meadow}
if __name__ == '__main__':
    for k in (sys.argv[1:] or ALLG):
        ALLG[k](); print('wrote', k)
