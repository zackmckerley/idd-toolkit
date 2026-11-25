"""Revise an architect's plan in place: the architect's own drawing stays the base and only the areas that change are edited.

Use this, not idd_planspec, whenever a plan already exists and the owner asks for changes to it (add a room, widen a wing,
enlarge a pool). idd_planspec draws a new plan from nothing and throws the architect's design away; the owner called that
result a butchered design (2191 SW 23rd St, 11.24.26). Here every pixel that is not edited is the architect's.

Coordinates are feet, x east and y north, from an origin picked on the drawing (a lot corner). Calibrate px_per_ft on a
dimensioned line and check it on a second one.

    p = Plan('floor1.png', px_per_ft=37.4, x0_px=1115, y0_px=3020)
    p.slide(20, 17.5, 28.6, 47.3, dx=-3, fill='smear')     # widen: slide a strip, the cut is filled from the still side
    p.white(62.9, 18.5, 68.4, 36)                           # clear a room that is being replanned
    p.wall(67.66, 18.5, 68.33, 38.5)                        # new exterior-weight wall (solid)
    p.partition(38.3, 18.5, 38.7, 27.2)                     # new interior partition in the architect's double-line style
    p.door(hinge=(41.2, 27.1), width=2.67, along='W', swing='N')
    p.label(41.9, 23, 'SCULLERY')
    p.change(1, (38.3, 18.5, 45.4, 27.3), 'Scullery replaces the pantry')
    p.save('floor1_rev.png'); p.save_marked('floor1_marked.png')

Stretching: a wall, window or counter that crosses the cut at right angles is continued by `fill='smear'` (the pixel column
on the still side of the cut is repeated). A hatch or dot pattern is continued by `fill='tile'` (the block beside the cut is
copied). Anything that runs along the cut (a wall parallel to it, furniture, text) must not sit on the cut: pick the cut
in clear floor or solid wall, look at the result, and move the cut if a piece was sliced.
"""
import math
from PIL import Image, ImageDraw, ImageFont

SANS = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'      # metric-compatible with Arial, the usual CAD plot font
SANS_B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
BLACK = (0, 0, 0); WHITE = (255, 255, 255); THIN = (60, 60, 60); FURN = (120, 120, 120)


class Plan:
    def __init__(self, path, px_per_ft, x0_px, y0_px):
        Image.MAX_IMAGE_PIXELS = None
        self.im = Image.open(path).convert('RGB'); self.orig = self.im.copy()
        self.k = float(px_per_ft); self.x0 = x0_px; self.y0 = y0_px
        self.d = ImageDraw.Draw(self.im); self.changes = []; self.label_px = 21

    # ---- coordinates
    def X(self, x): return int(round(self.x0 + x * self.k))
    def Y(self, y): return int(round(self.y0 - y * self.k))
    def box(self, x0, y0, x1, y1):
        return (self.X(min(x0, x1)), self.Y(max(y0, y1)), self.X(max(x0, x1)), self.Y(min(y0, y1)))
    def _redraw(self): self.d = ImageDraw.Draw(self.im)

    # ---- moving what the architect drew
    def slide(self, x0, y0, x1, y1, dx=0.0, dy=0.0, fill='white'):
        """Move the rectangle by (dx, dy) ft. The strip it leaves behind is filled: 'white', 'smear' (repeat the pixel row or
        column on the still side of the cut, so lines crossing the cut continue), or 'tile' (copy the block beside the cut)."""
        l, t, r, b = self.box(x0, y0, x1, y1); ox, oy = int(round(dx * self.k)), int(round(-dy * self.k))
        reg = self.im.crop((l, t, r, b))
        src = None
        if fill in ('smear', 'tile') and ox:
            w = abs(ox)
            if ox < 0: src = self.im.crop((r, t, r + (1 if fill == 'smear' else w), b)); vac = (r - w, t, r, b)
            else: src = self.im.crop((l - (1 if fill == 'smear' else w), t, l, b)); vac = (l, t, l + w, b)
        elif fill in ('smear', 'tile') and oy:
            h = abs(oy)
            if oy < 0: src = self.im.crop((l, b, r, b + (1 if fill == 'smear' else h))); vac = (l, b - h, r, b)
            else: src = self.im.crop((l, t - (1 if fill == 'smear' else h), r, t)); vac = (l, t, r, t + h)
        self.im.paste(WHITE, (l, t, r, b))
        self.im.paste(reg, (l + ox, t + oy))
        if src is not None:
            self.im.paste(src.resize((vac[2] - vac[0], vac[3] - vac[1]), Image.NEAREST), (vac[0], vac[1]))
        self._redraw()

    def copy(self, x0, y0, x1, y1, to_x, to_y, from_orig=True, rotate=0, flip=None):
        """Copy a piece (a fixture, a car, a door) to a new place; (to_x, to_y) is the new lower-left corner."""
        l, t, r, b = self.box(x0, y0, x1, y1)
        reg = (self.orig if from_orig else self.im).crop((l, t, r, b))
        if flip == 'h': reg = reg.transpose(Image.FLIP_LEFT_RIGHT)
        if flip == 'v': reg = reg.transpose(Image.FLIP_TOP_BOTTOM)
        if rotate: reg = reg.rotate(rotate, expand=True, fillcolor=WHITE)
        self.im.paste(reg, (self.X(to_x), self.Y(to_y) - reg.height)); self._redraw()

    def copy_from(self, other, x0, y0, x1, y1, to_x, to_y):
        """Copy a piece from another sheet of the same set (a washer from the ground floor to the second floor)."""
        reg = other.orig.crop(other.box(x0, y0, x1, y1))
        self.im.paste(reg, (self.X(to_x), self.Y(to_y) - reg.height)); self._redraw()

    def erase_line_v(self, x, y0, y1, half=0.15):
        """Take out a vertical line without cutting what crosses it: the strip is refilled from the pixel column beside it."""
        l, t, r, b = self.box(x - half, y0, x + half, y1)
        col = self.im.crop((l - 2, t, l - 1, b)); self.im.paste(col.resize((r - l, b - t), Image.NEAREST), (l, t)); self._redraw()

    # ---- drawing new work in the architect's hand
    def white(self, x0, y0, x1, y1): self.d.rectangle(self.box(x0, y0, x1, y1), fill=WHITE)
    def wall(self, x0, y0, x1, y1): self.d.rectangle(self.box(x0, y0, x1, y1), fill=BLACK)
    def partition(self, x0, y0, x1, y1, w=2):
        self.d.rectangle(self.box(x0, y0, x1, y1), fill=WHITE, outline=BLACK, width=w)
    def line(self, pts, w=2, color=THIN, dash=None):
        P = [(self.X(x), self.Y(y)) for x, y in pts]
        if not dash: self.d.line(P, fill=color, width=w); return
        on, off = dash
        for (ax, ay), (bx, by) in zip(P, P[1:]):
            L = math.hypot(bx - ax, by - ay); n = 0.0
            while n < L:
                m = min(n + on, L)
                self.d.line([(ax + (bx - ax) * n / L, ay + (by - ay) * n / L), (ax + (bx - ax) * m / L, ay + (by - ay) * m / L)], fill=color, width=w)
                n += on + off
    def rect(self, x0, y0, x1, y1, w=2, color=THIN, fill=None, dash=None):
        if dash: self.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], w, color, dash)
        else: self.d.rectangle(self.box(x0, y0, x1, y1), outline=color, width=w, fill=fill)
    def ellipse(self, x0, y0, x1, y1, w=2, color=THIN, fill=None):
        self.d.ellipse(self.box(x0, y0, x1, y1), outline=color, width=w, fill=fill)
    def rrect(self, x0, y0, x1, y1, r=0.5, w=2, color=THIN, fill=None):
        self.d.rounded_rectangle(self.box(x0, y0, x1, y1), radius=int(r * self.k), outline=color, width=w, fill=fill)
    def label(self, x, y, s, px=None, bold=False, color=BLACK, anchor='mm', rotate=0, bg=False):
        f = ImageFont.truetype(SANS_B if bold else SANS, px or self.label_px)
        lines = s.split('\n'); lh = int((px or self.label_px) * 1.1)
        if rotate:
            w = max(int(f.getlength(t)) for t in lines) + 8; h = lh * len(lines) + 8
            tmp = Image.new('RGBA', (w, h), (255, 255, 255, 0)); td = ImageDraw.Draw(tmp)
            for i, t in enumerate(lines): td.text((w / 2, 4 + lh * i + lh / 2), t, font=f, fill=color, anchor='mm')
            tmp = tmp.rotate(rotate, expand=True)
            self.im.paste(tmp, (self.X(x) - tmp.width // 2, self.Y(y) - tmp.height // 2), tmp); self._redraw(); return
        y0 = self.Y(y) - lh * (len(lines) - 1) / 2
        if bg:
            w = max(f.getlength(t) for t in lines) / 2 + 6
            self.d.rectangle((self.X(x) - w, y0 - lh / 2 - 2, self.X(x) + w, y0 + lh * (len(lines) - 0.5) + 2), fill=WHITE)
        for i, t in enumerate(lines): self.d.text((self.X(x), y0 + lh * i), t, font=f, fill=color, anchor=anchor)
    def door(self, hinge, width, along, swing, w=2):
        """Swing door: hinge point (ft), leaf width, `along` = direction from the hinge to the latch when closed (N/S/E/W),
        `swing` = the side it opens to. Draws the open leaf and the quarter arc in the architect's light line."""
        D = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}
        ax, ay = D[along]; sx, sy = D[swing]; hx, hy = hinge
        self.line([(hx, hy), (hx + sx * width, hy + sy * width)], w + 1, BLACK)
        pts = [(hx + (ax * math.cos(a) + sx * math.sin(a)) * width, hy + (ay * math.cos(a) + sy * math.sin(a)) * width)
               for a in [i * math.pi / 60 for i in range(31)]]
        self.line(pts, 1, FURN)
        self.line([(hx, hy), (hx + ax * width, hy + ay * width)], 1, FURN, dash=(8, 6))
    def bifold(self, x0, x1, y, side='S', w=2):
        """A pair of bifold leaves along a horizontal wall line at y, folding to `side`."""
        s = -1 if side == 'S' else 1; q = (x1 - x0) / 4.0
        for a in (x0, x1):
            d_ = 1 if a == x0 else -1
            self.line([(a, y), (a + d_ * q * 0.7, y + s * q * 0.7), (a + d_ * q * 1.4, y)], w, BLACK)
        self.line([(x0, y), (x1, y)], 1, FURN, dash=(8, 6))
    def pocket(self, a, b, w=2):
        self.line([a, b], 1, FURN, dash=(8, 6)); mx = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.line([a, mx], w + 2, BLACK)
    def window(self, x0, y0, x1, y1):
        """Glazing in a wall: the wall rectangle turns white with three light lines along its length."""
        l, t, r, b = self.box(x0, y0, x1, y1); self.d.rectangle((l, t, r, b), fill=WHITE, outline=BLACK, width=2)
        if (r - l) > (b - t):
            for f in (0.35, 0.65): self.d.line([(l, t + (b - t) * f), (r, t + (b - t) * f)], fill=THIN, width=2)
        else:
            for f in (0.35, 0.65): self.d.line([(l + (r - l) * f, t), (l + (r - l) * f, b)], fill=THIN, width=2)

    # ---- the record of what changed
    def change(self, n, rect, text, at=None):
        self.changes.append({'n': n, 'rect': rect, 'text': text, 'at': at})

    def save(self, path): self.im.save(path)

    def marked(self, tint=(255, 236, 170), alpha=0.55, bubble_px=30):
        """The revised plan with every changed area tinted and numbered. The clean plan is what gets built on;
        this one is what the owner and the architect review."""
        im = self.im.copy(); ov = Image.new('RGB', im.size, tint)
        mask = Image.new('L', im.size, 0); md = ImageDraw.Draw(mask)
        for c in self.changes:
            rs = c['rect'] if isinstance(c['rect'], list) else [c['rect']]
            for r in rs: md.rectangle(self.box(*r), fill=255)
        from PIL import ImageChops
        tinted = ImageChops.multiply(im, ov)
        im = Image.composite(Image.blend(im, tinted, alpha * 1.6 if alpha * 1.6 <= 1 else 1.0), im, mask)
        d = ImageDraw.Draw(im); f = ImageFont.truetype(SANS_B, int(bubble_px * 1.05))
        for c in self.changes:
            r0 = (c['rect'][0] if isinstance(c['rect'], list) else c['rect'])
            bx, by = c['at'] if c['at'] else (min(r0[0], r0[2]) + bubble_px * 0.9 / self.k, max(r0[1], r0[3]) - bubble_px * 0.9 / self.k)
            cx, cy = self.X(bx), self.Y(by)
            d.ellipse((cx - bubble_px, cy - bubble_px, cx + bubble_px, cy + bubble_px), fill=(200, 30, 45), outline=WHITE, width=3)
            d.text((cx, cy), str(c['n']), font=f, fill=WHITE, anchor='mm')
        return im

    def save_marked(self, path, **k): self.marked(**k).save(path)

    def routes(self, routes, stops=(), width=10, alpha=205):
        """The plan with movement routes drawn on it (a copy; the plan itself is not changed). Use it to test and to show a
        layout: every journey a person makes is drawn door to door through real openings, and a route that will not draw
        (through a wall, across a table, through another room's work zone) is a layout defect, not a drawing problem.
        routes: [(rgb, [(x, y), ...])] in feet, arrowhead at the end. stops: [(text, x, y, rgb)] numbered discs."""
        im = self.im.convert('RGBA'); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for color, pts in routes:
            px = [(self.X(x), self.Y(y)) for x, y in pts]; c = tuple(color) + (alpha,)
            d.line(px, fill=c, width=width, joint='curve')
            (ax, ay), (bx, by) = px[-2], px[-1]; L = math.hypot(bx - ax, by - ay) or 1; ux, uy = (bx - ax) / L, (by - ay) / L
            h = width * 2.6; tip = (bx + ux * h * 0.6, by + uy * h * 0.6)
            d.polygon([tip, (bx - ux * h * 0.5 - uy * h * 0.7, by - uy * h * 0.5 + ux * h * 0.7),
                       (bx - ux * h * 0.5 + uy * h * 0.7, by - uy * h * 0.5 - ux * h * 0.7)], fill=tuple(color) + (255,))
            r = width * 0.9; d.ellipse((px[0][0] - r, px[0][1] - r, px[0][0] + r, px[0][1] + r), fill=tuple(color) + (255,))
        out = Image.alpha_composite(im, ov).convert('RGB'); d = ImageDraw.Draw(out); f = ImageFont.truetype(SANS_B, 26)
        for text, x, y, color in stops:
            X, Y = self.X(x), self.Y(y); r = 21
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=WHITE, outline=tuple(color), width=4); d.text((X, Y), str(text), font=f, fill=tuple(color), anchor='mm')
        return out
    def crop_ft(self, x0, y0, x1, y1, marked=False):
        return (self.marked() if marked else self.im).crop(self.box(x0, y0, x1, y1))
