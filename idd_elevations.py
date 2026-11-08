"""Interior elevation generator for the interior-design-drawings skill.

An elevation is generated from a wall spec (dict) built from the room model, never traced by hand:
    wall = {
      'room': 'MASTER BATH', 'view': 'SOUTH',            # title: direction the viewer faces
      'length': 162.0, 'ceiling': 120.0,                 # inches, from the plan and the architectural set
      'floor_to_ceiling_note': '10\'-0" AFF',
      'base': 8.5, 'crown': 8.0, 'chair_rail': None,     # trim heights in inches (None = none)
      'openings': [{'type': 'door', 'x': 12.0, 'w': 36.0, 'head': 96.0, 'sill': 0.0, 'swing': 'L', 'casing': 5.0},
                   {'type': 'window', 'x': 90.0, 'w': 48.0, 'head': 96.0, 'sill': 36.0}],
      'items': [{'kind': 'base_cab', 'x': 0, 'w': 72, 'h': 34.5, 'counter': 1.5, 'doors': 3},
                {'kind': 'upper_cab', 'x': 0, 'w': 72, 'y': 54, 'h': 36, 'doors': 3},
                {'kind': 'tub', 'x': 0, 'w': 60, 'h': 22}, {'kind': 'toilet', 'x': 100, 'w': 18, 'h': 30},
                {'kind': 'mirror', 'x': 20, 'w': 30, 'y': 42, 'h': 36}, {'kind': 'sconce', 'x': 60, 'y': 66},
                {'kind': 'niche', 'x': 20, 'w': 24, 'y': 48, 'h': 12}, {'kind': 'tv', 'x': 40, 'w': 65, 'y': 40, 'h': 38}],
      'finishes': [{'code': 'WT-02', 'x0': 0, 'x1': 162, 'y0': 0, 'y1': 120, 'hatch': 'tile', 'module': (12, 24), 'setout': 'center'},
                   {'code': 'PT-02', 'x0': 0, 'x1': 162, 'y0': 0, 'y1': 120, 'hatch': None}],
      'notes': ['BLOCKING AT 36" TO 42" AFF FOR GRAB BAR'],
      'breaks': ('wall', 'wall'),                        # 'wall' = adjacent wall shown as a thick jamb, 'break' = continues
    }
All dimensions in inches. Finished floor is the datum. The renderer draws at a given scale (pt per inch).
"""
import math
import pymupdf as fitz

INK = (0.2, 0.2, 0.2); MID = (0.45, 0.45, 0.45); LIGHT = (0.7, 0.7, 0.7); HATCH = (0.78, 0.78, 0.78)
SCALES = {'1/4': 18.0 / 12, '3/8': 27.0 / 12, '1/2': 36.0 / 12, '3/4': 54.0 / 12, '1': 72.0 / 12}   # pt per inch

def ftin(inches):
    inches = round(inches * 8) / 8
    f = int(inches // 12); i = inches - 12 * f
    if abs(i - round(i)) < 1e-6:
        s = f'{int(round(i))}"'
    else:
        whole = int(i); frac = i - whole; num = int(round(frac * 8)); den = 8
        while num % 2 == 0 and num: num //= 2; den //= 2
        s = f'{whole}-{num}/{den}"' if (whole or f) else f'{num}/{den}"'   # 2'-0-1/4", never 2'-1/4"
    return f"{f}'-{s}" if f else s

def snap_points(pts, tol=1.0):
    """Sorted, deduplicated dimension points: anything within tol of a neighbour collapses onto it (ends are kept exactly)."""
    pts = sorted(set(round(v * 8) / 8 for v in pts))
    if len(pts) < 2: return pts
    out = [pts[0]]
    for v in pts[1:-1]:
        if v - out[-1] >= tol and pts[-1] - v >= tol: out.append(v)
    out.append(pts[-1])
    return out

DIM_LOG = []
def check_string(pts, room=None, view=None):
    """Every dimension string must close: the segments shown (each rounded to 1/8 in.) sum to the overall shown, within 1/8 in."""
    r8 = lambda v: round(v * 8) / 8
    segs = [r8(b - a) for a, b in zip(pts, pts[1:]) if b - a >= 0.5]
    overall = r8(pts[-1] - pts[0])
    ok = abs(sum(segs) - overall) <= 0.125 + 1e-6
    DIM_LOG.append({'room': room, 'view': view, 'segments': segs, 'overall': overall, 'ok': ok})
    assert ok, ('dimension string does not close', room, view, segs, overall)

class ElevationView:
    """Draws one elevation inside a cell on a PyMuPDF page (unrotated page, y down)."""
    def __init__(self, page, font, fontname, origin, scale_pt_per_in, wall):
        self.p, self.F, self.fn = page, font, fontname
        self.ox, self.oy = origin          # display point of the finished-floor line at the wall's left end
        self.k = scale_pt_per_in
        self.w = wall
    # --- coordinate helpers: wall inches -> page points (x right, y up)
    def X(self, xi): return self.ox + xi * self.k
    def Y(self, yi): return self.oy - yi * self.k
    def line(self, a, b, width=0.5, color=INK, dashes=None):
        sh = self.p.new_shape(); sh.draw_line(fitz.Point(a), fitz.Point(b)); sh.finish(color=color, width=width, dashes=dashes); sh.commit()
    def rect(self, x0, y0, x1, y1, width=0.5, color=INK, fill=None, dashes=None):
        sh = self.p.new_shape(); sh.draw_rect(fitz.Rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
        sh.finish(color=color, fill=fill, width=width, dashes=dashes); sh.commit()
    def text(self, x, y, s, size=6.5, color=INK, align='l', rotate=0, bold=False):
        from idd_sheet import remap, ps, _FR, _FB, BOLD_BUF, take_scale
        s = take_scale(self.p, remap(s), 'SHEET'); size = ps(size)
        if not s: return
        from idd_sheet import NOTE_INK
        if color == MID: color = NOTE_INK
        f, fn = (_FB, 'cgb') if bold else (_FR, self.fn)
        if bold and 'cgb' not in [x_[4] for x_ in self.p.get_fonts()]: self.p.insert_font(fontname='cgb', fontbuffer=BOLD_BUF)
        missing = [c for c in s if not f.has_glyph(ord(c))]
        assert not missing, (s, missing)
        w = f.text_length(s, fontsize=size)
        if rotate == 0:
            if align == 'c': x -= w / 2
            if align == 'r': x -= w
        else:  # 90: text runs upward, anchor is the bottom of the run
            if align == 'c': y += w / 2
        self.p.insert_text((x, y), s, fontsize=size, fontname=fn, color=color, rotate=rotate)
        return w
    # --- dimension strings (architectural: extension lines, slash ticks, text above the line)
    def dim_h(self, x0i, x1i, y_pt, pts_i, offset_lines=True):
        """Horizontal string at page y_pt through the sorted inch positions pts_i (first and last are the ends)."""
        xs = [self.X(v) for v in pts_i]
        check_string(pts_i, self.w.get('room'), self.w.get('view'))
        self.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
        for v, x in zip(pts_i, xs):
            self.line((x, y_pt - 3), (x, y_pt + 3), 0.4)            # tick (short perpendicular)
            self.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)   # architectural slash
        flip = False
        for a, b in zip(pts_i, pts_i[1:]):
            if b - a < 0.5: continue
            if (b - a) * self.k < 8:   # a segment narrower than its label: stack the label above the string
                self.text((self.X(a) + self.X(b)) / 2, y_pt - 9.5, ftin(b - a), 5.0, align='c'); continue
            short = (b - a) * self.k < 26
            sz = 5.5 if not short else 5.0
            y_text = y_pt - 2.5 if not (short and flip) else y_pt + 6.5
            self.text((self.X(a) + self.X(b)) / 2, y_text, ftin(b - a), sz, align='c')
            flip = not flip if short else False
    def dim_v(self, y0i, y1i, x_pt, pts_i, side='r'):
        ys = [self.Y(v) for v in pts_i]
        check_string(pts_i, self.w.get('room'), self.w.get('view'))
        self.line((x_pt, ys[0]), (x_pt, ys[-1]), 0.4)
        for v, y in zip(pts_i, ys):
            self.line((x_pt - 3, y), (x_pt + 3, y), 0.4)
            self.line((x_pt - 1.8, y + 1.8), (x_pt + 1.8, y - 1.8), 0.6)
        flip = False
        for a, b in zip(pts_i, pts_i[1:]):
            if b - a < 0.5: continue
            cy = (self.Y(a) + self.Y(b)) / 2
            if (b - a) * self.k < 16:                                  # too short to hold its label: set it beside the string, clear of the ticks
                self.text(x_pt + 8 if side == "r" else x_pt - 8, cy, ftin(b - a), 5.0, align="c", rotate=90); continue
            short = (b - a) * self.k < 26
            sz = 5.5 if not short else 5.0
            x_text = x_pt - 2.5 if side == 'r' else x_pt + 7.5
            if short and flip: x_text = x_pt + 7.5 if side == 'r' else x_pt - 2.5     # alternate short labels to the other side of the line
            self.text(x_text, cy, ftin(b - a), sz, align='c', rotate=90)
            flip = not flip if short else False
    # --- hatches clipped to a rect in inches
    def hatch_tile(self, x0, x1, y0, y1, module=(12, 24), setout='center', grout=0.125):
        """Tile grid, nominal module, set out from the center of the run (symmetrical cuts) or the left edge."""
        mw, mh = module
        X0, X1, Y0, Y1 = self.X(x0), self.X(x1), self.Y(y1), self.Y(y0)
        # vertical joints: center a tile or a joint on the run, whichever leaves the larger end cut (no slivers)
        L = x1 - x0; cx = (x0 + x1) / 2
        cut_tile_centered = (L / 2) % mw            # end cut when a tile is centered
        cut_joint_centered = (L / 2 - mw / 2) % mw if L >= mw else 0
        if setout == 'left':
            vx = [x0 + i * mw for i in range(1, int(L // mw) + 1)]
        elif cut_tile_centered >= cut_joint_centered:
            n = int(L // mw) + 1; vx = [cx + (i + 0.5) * mw for i in range(-n, n)]
        else:
            n = int(L // mw) + 1; vx = [cx + i * mw for i in range(-n, n + 1)]
        for v in vx:
            if x0 < v < x1: self.line((self.X(v), Y0), (self.X(v), Y1), 0.25, HATCH)
        # horizontal courses from the floor (full tile at the floor, cut at the ceiling)
        v = y0 + mh
        while v < y1:
            self.line((X0, self.Y(v)), (X1, self.Y(v)), 0.25, HATCH); v += mh
        self.rect(X0, Y0, X1, Y1, 0.3, MID)
    def hatch_wood(self, x0, x1, y0, y1, vertical=True, pitch=6.0):
        X0, X1, Y0, Y1 = self.X(x0), self.X(x1), self.Y(y1), self.Y(y0)
        if vertical:
            v = x0 + pitch
            while v < x1: self.line((self.X(v), Y0), (self.X(v), Y1), 0.25, HATCH); v += pitch
        else:
            v = y0 + pitch
            while v < y1: self.line((X0, self.Y(v)), (X1, self.Y(v)), 0.25, HATCH); v += pitch
    def hatch_stone(self, x0, x1, y0, y1, seed=3):
        import random
        rnd = random.Random(seed); X0, X1, Y0, Y1 = self.X(x0), self.X(x1), self.Y(y1), self.Y(y0)
        sh = self.p.new_shape()
        for k in range(max(3, int((X1 - X0 + Y0 - Y1) / 25))):
            x, y = rnd.uniform(X0, X1), rnd.uniform(Y1, Y0); ang = rnd.uniform(0, math.pi); L = rnd.uniform(0.4, 1.0) * max(X1 - X0, Y0 - Y1)
            for i in range(6):
                ang += rnd.uniform(-0.4, 0.4); nx, ny = x + math.cos(ang) * L / 6, y + math.sin(ang) * L / 6
                nx = min(max(nx, X0), X1); ny = min(max(ny, Y1), Y0)
                sh.draw_line(fitz.Point(x, y), fitz.Point(nx, ny)); x, y = nx, ny
        sh.finish(color=HATCH, width=0.25); sh.commit()
    def hatch_panels(self, x0, x1, y0, y1, module=36.0, stile=3.5):
        """Painted wood paneling: stiles and rails with a recessed field, module centered on the run."""
        X0, X1, Y0, Y1 = self.X(x0), self.X(x1), self.Y(y1), self.Y(y0)
        self.rect(X0, Y0, X1, Y1, 0.4, MID)
        L = x1 - x0; n = max(1, int(round(L / module))); m = L / n
        for i in range(n):
            px0, px1 = x0 + i * m + stile, x0 + (i + 1) * m - stile
            self.rect(self.X(px0), self.Y(y1 - stile), self.X(px1), self.Y(y0 + stile), 0.35, MID)
            self.rect(self.X(px0 + 1.5), self.Y(y1 - stile - 1.5), self.X(px1 - 1.5), self.Y(y0 + stile + 1.5), 0.25, LIGHT)
    # --- items
    def draw_item(self, it):
        k = it['kind']; x = it.get('x', 0); w = it.get('w', 0); y = it.get('y', 0); h = it.get('h', 0)
        if k == 'base_cab':
            self.rect(self.X(x), self.Y(0), self.X(x + w), self.Y(h), 0.6)
            self.rect(self.X(x), self.Y(h), self.X(x + w), self.Y(h + it.get('counter', 1.5)), 0.6)   # counter
            self.line((self.X(x), self.Y(4)), (self.X(x + w), self.Y(4)), 0.4)                      # toe kick
            n = it.get('doors', 2); dw = w / n
            for i in range(n):
                self.rect(self.X(x + i * dw + 1), self.Y(5), self.X(x + (i + 1) * dw - 1), self.Y(h - 1), 0.35)
        elif k == 'upper_cab':
            self.rect(self.X(x), self.Y(y), self.X(x + w), self.Y(y + h), 0.6)
            n = it.get('doors', 2); dw = w / n
            for i in range(n):
                self.rect(self.X(x + i * dw + 1), self.Y(y + 1), self.X(x + (i + 1) * dw - 1), self.Y(y + h - 1), 0.35)
        elif k == 'tub':
            self.rect(self.X(x), self.Y(0), self.X(x + w), self.Y(h), 0.6)
            self.rect(self.X(x + 2), self.Y(h - 2), self.X(x + w - 2), self.Y(h), 0.35)
        elif k == 'toilet':
            cx = x + w / 2
            self.rect(self.X(cx - w / 2), self.Y(0), self.X(cx + w / 2), self.Y(h * 0.5), 0.5)      # bowl
            self.rect(self.X(cx - w / 2 + 1), self.Y(h * 0.5), self.X(cx + w / 2 - 1), self.Y(h), 0.5)   # tank
        elif k == 'vanity':
            self.rect(self.X(x), self.Y(0), self.X(x + w), self.Y(h), 0.6)
            self.line((self.X(x), self.Y(4)), (self.X(x + w), self.Y(4)), 0.4)
            self.rect(self.X(x), self.Y(h), self.X(x + w), self.Y(h + it.get('counter', 1.25)), 0.6)
        elif k == 'mirror':
            self.rect(self.X(x), self.Y(y), self.X(x + w), self.Y(y + h), 0.6)
            self.line((self.X(x + 2), self.Y(y + h - 2)), (self.X(x + w - 2), self.Y(y + 2)), 0.3, LIGHT)
        elif k == 'sconce':
            cx, cy = self.X(x), self.Y(y)
            sh = self.p.new_shape(); sh.draw_circle(fitz.Point(cx, cy), 2.0 * self.k); sh.finish(color=INK, width=0.5); sh.commit()
            self.line((cx, cy + 2.0 * self.k), (cx, cy + 5.0 * self.k), 0.5)
        elif k == 'niche':
            self.rect(self.X(x), self.Y(y), self.X(x + w), self.Y(y + h), 0.6)
            self.rect(self.X(x + 1), self.Y(y + 1), self.X(x + w - 1), self.Y(y + h - 1), 0.3, MID)
        elif k == 'tv':
            self.rect(self.X(x), self.Y(y), self.X(x + w), self.Y(y + h), 0.6, dashes='[3 2] 0')
            self.text((self.X(x) + self.X(x + w)) / 2, (self.Y(y) + self.Y(y + h)) / 2 + 2, 'TV', 6, MID, align='c')
        elif k == 'fireplace':
            self.rect(self.X(x), self.Y(0), self.X(x + w), self.Y(h), 0.7)
            ow, oh = it.get('opening', (42, 30))
            cx = x + w / 2
            self.rect(self.X(cx - ow / 2), self.Y(it.get('hearth', 0)), self.X(cx + ow / 2), self.Y(it.get('hearth', 0) + oh), 0.6, fill=(0.93, 0.93, 0.93))
        elif k == 'shelves':
            self.rect(self.X(x), self.Y(y), self.X(x + w), self.Y(y + h), 0.6)
            n = it.get('n', 4)
            for i in range(1, n):
                yy = y + h * i / n
                self.line((self.X(x), self.Y(yy)), (self.X(x + w), self.Y(yy)), 0.4)
        elif k == 'tall_cab':
            self.rect(self.X(x), self.Y(0), self.X(x + w), self.Y(h), 0.6)
            self.line((self.X(x), self.Y(4)), (self.X(x + w), self.Y(4)), 0.4)
            n = it.get('doors', 2); dw = w / n
            for i in range(n):
                self.rect(self.X(x + i * dw + 1), self.Y(5), self.X(x + (i + 1) * dw - 1), self.Y(h - 1), 0.35)
        elif k == 'shower_glass':
            self.rect(self.X(x), self.Y(0), self.X(x + w), self.Y(h), 0.5, dashes='[2 1.5] 0')
            self.line((self.X(x + 2), self.Y(2)), (self.X(x + w - 2), self.Y(h - 2)), 0.3, LIGHT)
            self.text(self.X(x + w / 2), self.Y(h / 2), 'GLASS', 5.5, MID, align='c')
        elif k == 'box':
            self.rect(self.X(x), self.Y(y), self.X(x + w), self.Y(y + h), it.get('lw', 0.5), dashes=it.get('dashes'))
    def draw_opening(self, o):
        x, w, head, sill = o['x'], o['w'], o['head'], o.get('sill', 0)
        cs = o.get('casing', 0)
        L = self.w['length']
        csl, csr = min(cs, max(0.0, x)), min(cs, max(0.0, L - x - w))      # casing never runs past the end of the wall
        if o['type'] == 'door':
            self.rect(self.X(x), self.Y(sill), self.X(x + w), self.Y(head), 0.7)
            if cs: self.rect(self.X(x - csl), self.Y(sill), self.X(x + w + csr), self.Y(head + cs), 0.5)
            # door leaf (or a pair) with a simple two-panel layout and the swing as a dashed V
            leaves = [(x, x + w)] if not o.get('pair') else [(x, x + w / 2), (x + w / 2, x + w)]
            for i, (lx0, lx1) in enumerate(leaves):
                self.rect(self.X(lx0 + 3), self.Y(10), self.X(lx1 - 3), self.Y(head - 6), 0.35, MID)
                self.rect(self.X(lx0 + 3), self.Y(head - 6 - 0.3 * (head - 16) + 4), self.X(lx1 - 3), self.Y(head - 6), 0.35, MID)
                if o.get('pair'): hinge, far = (lx0, lx1) if i == 0 else (lx1, lx0)
                else:
                    hinge = x if o.get('swing', 'L') == 'L' else x + w
                    far = x + w if hinge == x else x
                self.line((self.X(hinge), self.Y(sill)), (self.X(far), self.Y((head + sill) / 2)), 0.3, MID, dashes='[2 1.5] 0')
                self.line((self.X(hinge), self.Y(head)), (self.X(far), self.Y((head + sill) / 2)), 0.3, MID, dashes='[2 1.5] 0')
        elif o['type'] == 'jib':
            self.rect(self.X(x), self.Y(sill), self.X(x + w), self.Y(head), 0.4, MID, dashes='[3 2] 0')
            self.text(self.X(x + w / 2), self.Y(head / 2), 'JIB DOOR', 5.0, MID, align='c')
        elif o['type'] == 'window':
            self.rect(self.X(x), self.Y(sill), self.X(x + w), self.Y(head), 0.7)
            if cs: self.rect(self.X(x - csl), self.Y(sill - cs), self.X(x + w + csr), self.Y(head + cs), 0.5)
            n = o.get('lites', 2); lw = w / n
            for i in range(n):
                self.rect(self.X(x + i * lw + 1.5), self.Y(sill + 1.5), self.X(x + (i + 1) * lw - 1.5), self.Y(head - 1.5), 0.35, MID)
                gx0, gy0 = self.X(x + i * lw + 3), self.Y(head - 3); self.line((gx0, gy0), (gx0 + 5, gy0 + 7), 0.25, LIGHT)
        else:  # cased opening / archway
            self.rect(self.X(x), self.Y(sill), self.X(x + w), self.Y(head), 0.7)
            if o.get('arch'):
                r = w / 2; cx = x + r
                sh = self.p.new_shape(); sh.draw_sector(fitz.Point(self.X(cx), self.Y(head - r)), fitz.Point(self.X(x + w), self.Y(head - r)), -180, fullSector=False)
                sh.finish(color=INK, width=0.7); sh.commit()
    # --- the full view
    def draw(self, tag_fn=None, number='1', show_dims=True, cell=None):
        w = self.w; L, H = w['length'], w['ceiling']; X0, X1, Y0, Y1 = self.X(0), self.X(L), self.Y(0), self.Y(H)
        # finishes (back to front): hatch zones first
        for f in w.get('finishes', []):
            h = f.get('hatch')
            if h == 'tile': self.hatch_tile(f['x0'], f['x1'], f['y0'], f['y1'], f.get('module', (12, 24)), f.get('setout', 'center'))
            elif h == 'wood': self.hatch_wood(f['x0'], f['x1'], f['y0'], f['y1'], f.get('vertical', True))
            elif h == 'stone': self.hatch_stone(f['x0'], f['x1'], f['y0'], f['y1'])
            elif h == 'panels': self.hatch_panels(f['x0'], f['x1'], f['y0'], f['y1'], f.get('module', 36.0))
        # trims
        tiled = [(f['x0'], f['x1']) for f in w.get('finishes', []) if f.get('hatch') in ('tile', 'stone')]
        def cut(runs, a0, a1): return [seg for a, b in runs for seg in ((a, min(b, a0)), (max(a, a1), b)) if seg[1] - seg[0] > 0.5]
        if w.get('base'):
            runs = [(0.0, L)]
            for a0, a1 in tiled: runs = cut(runs, a0, a1)                       # no wood base inside a tiled alcove
            for o in w.get('openings', []):
                if o.get('sill', 0) == 0: runs = cut(runs, o['x'], o['x'] + o['w'])   # no base across a door
            for a, b in runs:
                self.rect(self.X(a), Y0, self.X(b), self.Y(w['base']), 0.5); self.line((self.X(a), self.Y(w['base'] * 0.7)), (self.X(b), self.Y(w['base'] * 0.7)), 0.3, MID)
        if w.get('crown'):
            # crown stops at full-height openings (open to the adjacent room) and at tile or stone that runs to the ceiling
            runs = [(0.0, L)]
            for o in w.get('openings', []):
                if o.get('open'): runs = cut(runs, o['x'], o['x'] + o['w'])
            for f in w.get('finishes', []):
                if f.get('hatch') in ('tile', 'stone') and f['y1'] >= H - 0.1: runs = cut(runs, f['x0'], f['x1'])
            for a, b in runs:
                self.rect(self.X(a), self.Y(H - w['crown']), self.X(b), Y1, 0.5)
                for f in ((0.3, 0.62, 0.8) if w['crown'] > 7 else (0.55,)):   # built-up crown (frieze, bed mould, crown) reads as three members
                    self.line((self.X(a), self.Y(H - w['crown'] * f)), (self.X(b), self.Y(H - w['crown'] * f)), 0.3, MID)
        if w.get('chair_rail'): self.rect(X0, self.Y(w['chair_rail']), X1, self.Y(w['chair_rail'] + 2.5), 0.5)
        for o in w.get('openings', []): self.draw_opening(o)
        for it in w.get('items', []): self.draw_item(it)
        # wall boundary: floor, ceiling, and the adjacent walls (thick jambs) or break lines
        self.line((X0 - 6, Y0), (X1 + 6, Y0), 1.2)                       # finished floor line
        self.line((X0, Y1), (X1, Y1), 0.9)                               # ceiling line
        for side, x in zip(w.get('breaks', ('wall', 'wall')), (X0, X1)):
            if side == 'wall':
                dx = -4 if x == X0 else 4
                self.rect(x, Y0, x + dx, Y1, 0.6, fill=(0.35, 0.35, 0.35))
            else:
                zz = [(x, Y0), (x + 2, Y0 + (Y1 - Y0) * 0.45), (x - 2, Y0 + (Y1 - Y0) * 0.55), (x, Y1)]
                sh = self.p.new_shape(); sh.draw_polyline([fitz.Point(q) for q in zz]); sh.finish(color=INK, width=0.6); sh.commit()
        # finish tags
        if tag_fn:
            for f in w.get('finishes', []):
                tx, ty = f.get('tag_at', ((f['x0'] + f['x1']) / 2, (f['y0'] + f['y1']) * 0.5))
                tag_fn(self.X(tx), self.Y(ty), f['code'])
        # dimensions: overall and inner strings, finished floor as datum
        if show_dims:
            h_pts = sorted({0, L} | {o['x'] for o in w.get('openings', [])} | {o['x'] + o['w'] for o in w.get('openings', [])}
                           | {it['x'] for it in w.get('items', []) if it['kind'] in ('base_cab', 'upper_cab', 'vanity', 'tub', 'fireplace', 'shelves')}
                           | {it['x'] + it['w'] for it in w.get('items', []) if it['kind'] in ('base_cab', 'upper_cab', 'vanity', 'tub', 'fireplace', 'shelves')})
            h_pts = snap_points(h_pts)
            self.dim_h(0, L, Y0 + 14, h_pts)
            if len(h_pts) > 2: self.dim_h(0, L, Y0 + 24, [0, L])
            v_pts = sorted({0, H} | {o['head'] for o in w.get('openings', [])} | {o.get('sill', 0) for o in w.get('openings', []) if o.get('sill', 0) > 0}
                           | {it.get('y', 0) + it.get('h', 0) for it in w.get('items', []) if it['kind'] in ('base_cab', 'vanity', 'tub')}
                           | {it['y'] for it in w.get('items', []) if it['kind'] in ('upper_cab', 'mirror', 'niche')}
                           | {it['y'] + it['h'] for it in w.get('items', []) if it['kind'] in ('upper_cab', 'niche')}
                           | ({w['crown'] and (H - w['crown'])} - {None, 0}) | ({w.get('chair_rail')} - {None}))
            v_pts = snap_points([v for v in v_pts if v is not None and 0 <= v <= H])
            self.dim_v(0, H, X1 + 14, v_pts)
            if len(v_pts) > 2: self.dim_v(0, H, X1 + 26, [0, H])
            # centerlines for wall-mounted fixtures (sconces, niche) on the top string
            for it in w.get('items', []):
                if it['kind'] == 'sconce':
                    self.line((self.X(it['x']), Y1 - 6), (self.X(it['x']), self.Y(it['y'])), 0.3, MID, dashes='[3 2] 0')
                    self.text(self.X(it['x']), Y1 - 8, 'CL ' + ftin(it['x']), 5.0, MID, align='c')
                    if it['x'] > L / 2: self.text(self.X(it['x']) - 3, self.Y(it['y']) - 3, ftin(it['y']) + ' AFF', 5.0, MID, align='r')
                    else: self.text(self.X(it['x']) + 3, self.Y(it['y']) - 3, ftin(it['y']) + ' AFF', 5.0, MID)
        # datum label
        self.text(X0 - 6, Y0 + 7, 'FIN. FLR.', 5.0, MID, align='r')
        # notes: top-right of the cell under the title bar, right-aligned
        if cell:
            nx, ny = cell[2] - 8, cell[1] + 28
        else:
            nx, ny = X1 + 40, Y1 - 14
        for n in w.get('notes', []):
            self.text(nx, ny, n, 5.5, MID, align='r'); ny += 8

def title_bar(page, font, fontname, cell, number, title, scale_label):
    """Title strip across the top of a cell: view number, title in the serif, scale at the right."""
    from idd_sheet import remap, _FR, _FS, SERIF_BUF
    if 'srf' not in [x_[4] for x_ in page.get_fonts()]: page.insert_font(fontname='srf', fontbuffer=SERIF_BUF)
    x0, y0, x1, y1 = cell
    sh = page.new_shape(); sh.draw_rect(fitz.Rect(x0, y0, x1, y1)); sh.finish(color=LIGHT, width=0.4); sh.commit()
    sh = page.new_shape(); sh.draw_line(fitz.Point(x0, y0 + 16), fitz.Point(x1, y0 + 16)); sh.finish(color=LIGHT, width=0.4); sh.commit()
    from idd_sheet import take_scale
    n = str(number)
    title = take_scale(page, remap(str(title)), 'VIEW ' + n)
    take_scale(page, remap(scale_label.replace(' = ', ' TO ')), 'PLAN' if 'PLAN' in title else 'VIEW ' + n)   # scales print in the title block only
    page.insert_text((x0 + 6, y0 + 12.2), n, fontsize=10, fontname='srf', color=(0.85, 0.35, 0.1))
    xt = x0 + 6 + _FS.text_length(n, fontsize=10) + 6
    room = x1 - 10 - xt
    sz = 10.0
    while _FS.text_length(title, fontsize=sz) > room and sz > 7.0: sz -= 0.25
    page.insert_text((xt, y0 + 12.2), title, fontsize=sz, fontname='srf', color=INK)

def layout_cells(frame, cols, rows, gap=0):
    """Split a frame rect into a grid of cells (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = frame; cw = (x1 - x0) / cols; ch = (y1 - y0) / rows
    return [(x0 + c * cw, y0 + r * ch, x0 + (c + 1) * cw, y0 + (r + 1) * ch) for r in range(rows) for c in range(cols)]

def fit_origin(cell, wall, k, margin_l=46, margin_b=44, top=24):
    """Floor-line origin so the elevation (plus dimension strings) sits centered in the cell; asserts it fits."""
    x0, y0, x1, y1 = cell
    Wpt, Hpt = wall['length'] * k, wall['ceiling'] * k
    assert Wpt + margin_l + 60 <= x1 - x0 and Hpt + top + margin_b <= y1 - y0, ('elevation does not fit the cell at this scale', wall['room'], wall['view'])
    ox = x0 + (x1 - x0 - Wpt - 60 + margin_l) / 2 + 10
    oy = y1 - margin_b - (y1 - y0 - top - margin_b - Hpt) / 2
    return ox, oy

def best_scale(cell, wall, prefer=('1/2', '3/8', '1/4'), margin_l=46, margin_b=44, top=24):
    """Largest standard scale at which the wall fits the cell. Prefer 1/2" for kitchens, baths and millwork."""
    x0, y0, x1, y1 = cell
    for name in prefer:
        k = SCALES[name]
        if wall['length'] * k + margin_l + 60 <= x1 - x0 and wall['ceiling'] * k + top + margin_b <= y1 - y0:
            return name, k
    raise ValueError(f"{wall['room']} {wall['view']} does not fit the cell at 1/4\"; use a full-width cell")
