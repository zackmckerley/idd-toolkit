import re, random, io
import pymupdf as fitz
from fontTools.ttLib import TTFont
from shapely.geometry import Polygon, box, MultiPolygon
from shapely.ops import unary_union
from geo import polys_from as _pf
from geo import layer_union, is_gray

SRC = '/mnt/user-data/uploads/3807f371-Flooring_Plans.pdf'
OUT = '/home/claude/flrwork/261101.3350THOMAS.FlooringPlans-Rev1.pdf'
FT = 13.5          # points per foot at 3/16" = 1'-0"
PLANK = FT / 2     # ~6" plank face, matches existing hatch (6.72)
PLANK_LEN = FT * 4
TILE = FT          # 12" grid
HATCH = '0.87451 0.87451 0.87451'
TILEC = '0.80 0.80 0.80'

doc = fitz.open(SRC)

# ---------- fonts (embedded Century Gothic subsets) ----------
REG_BUF = doc.extract_font(807)[3]
BOLD_BUF = doc.extract_font(703)[3]
FREG = fitz.Font(fontbuffer=REG_BUF)
FBOLD = fitz.Font(fontbuffer=BOLD_BUF)

def glyph_map(xref):
    f = TTFont(io.BytesIO(doc.extract_font(xref)[3]))
    cm = f.getBestCmap()
    order = f.getGlyphOrder()
    g2c = {}
    for c, n in sorted(cm.items(), reverse=True):   # lowest code point wins ('-' over soft hyphen)
        g2c[f.getGlyphID(n)] = chr(c)
    c2g = {chr(c): f.getGlyphID(n) for c, n in cm.items()}
    return g2c, c2g

# ---------- helpers ----------
def to_stream(page, X, Y):
    u = fitz.Point(X, Y) * page.derotation_matrix
    return u.x / 0.12, (1584 - u.y) / 0.12

def path_ops(page, geom):
    ops = []
    polys = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for pg in polys:
        if pg.is_empty:
            continue
        for ring in [pg.exterior] + list(pg.interiors):
            pts = list(ring.coords)
            x, y = to_stream(page, *pts[0])
            ops.append(f'{x:.1f} {y:.1f} m')
            for px, py in pts[1:]:
                x, y = to_stream(page, px, py)
                ops.append(f'{x:.1f} {y:.1f} l')
            ops.append('h')
    return '\n'.join(ops)

def line_op(page, a, b):
    x0, y0 = to_stream(page, *a); x1, y1 = to_stream(page, *b)
    return f'{x0:.1f} {y0:.1f} m {x1:.1f} {y1:.1f} l'

def region(page, geom, fill, pattern=None, seed=1):
    """White (or colored) fill clipped to geom, then optional hatch."""
    if geom.is_empty:
        return ''
    s = ['q', path_ops(page, geom), 'W* n', f'{fill} rg', f'{fill} RG']
    x0, y0, x1, y1 = geom.bounds
    s.append(path_ops(page, box(x0 - 2, y0 - 2, x1 + 2, y1 + 2)) + '\nf')
    if pattern == 'plank':
        rnd = random.Random(seed)
        s += [f'{HATCH} RG', '1 w', '1 J']
        lines = []
        X = x0 - (x0 % PLANK)
        col = 0
        while X <= x1 + PLANK:
            lines.append(line_op(page, (X, y0 - 1), (X, y1 + 1)))
            off = rnd.uniform(0, PLANK_LEN)
            Y = y0 - PLANK_LEN + off
            while Y <= y1:
                if Y >= y0:
                    lines.append(line_op(page, (X, Y), (X + PLANK, Y)))
                Y += PLANK_LEN
            X += PLANK; col += 1
        s.append('\n'.join(l + ' S' for l in lines))
    elif pattern == 'diag':
        s += [f'{HATCH} RG', '1 w', '0 J']
        lines = []
        step = TILE * 2 ** 0.5          # 12" tiles set on the diagonal
        span = (x1 - x0) + (y1 - y0)
        c = x0 + y0 - ((x0 + y0) % step) - step
        while c <= x1 + y1 + step:      # x + y = c
            lines.append(line_op(page, (c - y0 + 1, y0 - 1), (c - y1 - 1, y1 + 1))); c += step
        c = x0 - y1 - ((x0 - y1) % step) - step
        while c <= x1 - y0 + step:      # x - y = c
            lines.append(line_op(page, (c + y0 - 1, y0 - 1), (c + y1 + 1, y1 + 1))); c += step
        s.append('\n'.join(l + ' S' for l in lines))
    elif pattern == 'tile':
        s += [f'{TILEC} RG', '1 w', '0 J']
        lines = []
        X = x0 - (x0 % TILE)
        while X <= x1 + TILE:
            lines.append(line_op(page, (X, y0 - 1), (X, y1 + 1))); X += TILE
        Y = y0 - (y0 % TILE)
        while Y <= y1 + TILE:
            lines.append(line_op(page, (x0 - 1, Y), (x1 + 1, Y))); Y += TILE
        s.append('\n'.join(l + ' S' for l in lines))
    s.append('Q')
    return '\n'.join(s)

def insert_after_gray(page, content):
    """Insert content right after the gray (a-bro hatch 2) fill block so walls,
    doors and fixtures still draw on top."""
    for xref in page.get_contents():
        s = doc.xref_stream(xref).decode('latin1')
        i = s.find('0.79216 0.79216 0.79216 rg')
        if i < 0:
            continue
        # block that actually holds the fills starts at the BDC after the color set
        b = s.find('BDC', i)
        e = s.find('EMC', b)
        # sanity: the block must contain fill-and-stroke ops
        assert ' b\n' in s[b:e] or '\nb\n' in s[b:e], 'gray block not found'
        s = s[:e + 3] + '\nq\n' + content + '\nQ\n' + s[e + 3:]
        doc.update_stream(xref, s.encode('latin1'))
        return
    raise RuntimeError('no gray block')

def edit_text(page, edits):
    """edits: list of (match_text, display_point_near, action) where action is
    None (delete) or replacement text. Matches a Tj whose decoded text equals
    match_text and whose Tm origin is within 4pt of the given display point."""
    fonts = {}
    for f in page.get_fonts():
        fonts[f[4]] = f[0]
    maps = {k: glyph_map(v) for k, v in fonts.items()}
    done = []
    for xref in page.get_contents():
        s = doc.xref_stream(xref).decode('latin1')
        cur_font = None
        out = []; pos = 0; changed = False
        tok = re.compile(r'/(F\d+) [\d.]+ Tf|([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) Tm|<([0-9a-fA-F]+)> Tj')
        tm = None
        for m in tok.finditer(s):
            if m.group(1):
                cur_font = m.group(1); continue
            if m.group(2) is not None:
                tm = (float(m.group(6)), float(m.group(7))); continue
            hx = m.group(8)
            g2c, c2g = maps[cur_font]
            gids = [int(hx[i:i + 4], 16) for i in range(0, len(hx), 4)]
            txt = ''.join(g2c.get(g, '?') for g in gids)
            if tm is None:
                continue
            u = fitz.Point(tm[0] * 0.12, 1584 - tm[1] * 0.12) * page.rotation_matrix
            for k, (mt, near, act) in enumerate(edits):
                if k in done or txt != mt:
                    continue
                if near is not None and abs(u.x - near[0]) + abs(u.y - near[1]) > 6:
                    continue
                if act is None:
                    rep = ''
                else:
                    rep = '<' + ''.join(f'{c2g[c]:04x}' for c in act) + '> Tj'
                out.append(s[pos:m.start()]); out.append(rep); pos = m.end()
                done.append(k); changed = True
                break
        if changed:
            out.append(s[pos:])
            doc.update_stream(xref, ''.join(out).encode('latin1'))
    missing = [edits[k][:2] for k in range(len(edits)) if k not in done]
    assert not missing, f'unmatched text edits: {missing}'

def text_origin(page, txt):
    """display-space origin (baseline-left) of every span equal to txt"""
    res = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                t = ''.join(c['c'] for c in sp['chars'])
                if t == txt:
                    o = fitz.Point(sp['origin']) * page.rotation_matrix
                    res.append(((o.x, o.y), sp['size'], fitz.Rect(sp['bbox']) * page.rotation_matrix))
    return res

# ---------- drawing API (display coords -> unrotated) ----------
class Draw:
    def __init__(self, page):
        self.p = page; self.D = page.derotation_matrix
        page.insert_font(fontname='cgr', fontbuffer=REG_BUF)
        page.insert_font(fontname='cgb', fontbuffer=BOLD_BUF)
    def P(self, x, y):
        return fitz.Point(x, y) * self.D
    def text(self, x, y, s, size, color, bold=False, align='l'):
        f = FBOLD if bold else FREG
        fake = bold and not all(FBOLD.has_glyph(ord(c)) for c in s)   # bold subset lacks the glyph: stroke the regular one
        if fake:
            f = FREG
        w = f.text_length(s, fontsize=size)
        if align == 'c': x -= w / 2
        if align == 'r': x -= w
        kw = dict(render_mode=2, border_width=0.045) if fake else {}
        self.p.insert_text(self.P(x, y), s, fontsize=size, fontname='cgr' if (fake or not bold) else 'cgb',
                           color=color, rotate=270, **kw)
        return w
    def line(self, pts, width, color):
        sh = self.p.new_shape()
        sh.draw_polyline([self.P(*q) for q in pts])
        sh.finish(color=color, width=width, closePath=False, lineCap=1)
        sh.commit()
    def rect(self, r, width=0.48, color=None, fill=None):
        sh = self.p.new_shape()
        q = [self.P(r[0], r[1]), self.P(r[2], r[1]), self.P(r[2], r[3]), self.P(r[0], r[3])]
        sh.draw_polyline(q + [q[0]])
        sh.finish(color=color, fill=fill, width=width, closePath=True)
        sh.commit()
    def tag(self, cx, cy, code, lead=11.0, flip=False, sides='lr'):
        """Finish tag matching the designer's: boxed code with dog-leg leaders."""
        g = (0.251, 0.251, 0.251)
        size = 5.8748
        w = FREG.text_length(code, fontsize=size)
        bw, bh = w + 1.0, 7.4
        x0, x1 = cx - bw / 2, cx + bw / 2
        y0, y1 = cy - bh / 2, cy + bh / 2
        self.rect((x0, y0, x1, y1), width=0.48, color=g)
        self.text(cx, cy + 2.1, code, size, g, align='c')
        d = lead * 0.87
        sgn = -1 if flip else 1
        if 'l' in sides:
            self.line([(x0, cy), (x0 - 4.7, cy), (x0 - 4.7 - d * 1.15, cy - sgn * d)], 0.3, g)
        if 'r' in sides:
            self.line([(x1, cy), (x1 + 4.7, cy), (x1 + 4.7 + d * 1.15, cy + sgn * d)], 0.3, g)
    def tag_stack(self, cx, cy, codes, lead=11.0, sides='lr'):
        """Two stacked boxes (designer's WD-02 / SL-01 style): leader off the top-left and bottom-right."""
        g = (0.251, 0.251, 0.251); size = 5.8748; bh = 7.4; pitch = bh + 0.9
        w = max(FREG.text_length(c, fontsize=size) for c in codes) + 1.0
        x0, x1 = cx - w / 2, cx + w / 2
        tops = [cy - pitch / 2 - bh / 2, cy + pitch / 2 - bh / 2]
        for c, y0 in zip(codes, tops):
            self.rect((x0, y0, x1, y0 + bh), width=0.48, color=g)
            self.text(cx, y0 + bh / 2 + 2.1, c, size, g, align='c')
        d = lead * 0.87
        if 'l' in sides:
            yl = tops[0] + bh / 2
            self.line([(x0, yl), (x0 - 4.7, yl), (x0 - 4.7 - d * 1.15, yl - d)], 0.3, g)
        if 'r' in sides:
            yr = tops[1] + bh / 2
            self.line([(x1, yr), (x1 + 4.7, yr), (x1 + 4.7 + d * 1.15, yr + d)], 0.3, g)

def copy_image(src_page, xref, dst_page, disp_rect):
    img = doc.extract_image(xref)['image']
    r = fitz.Rect(disp_rect) * dst_page.derotation_matrix
    r.normalize()
    dst_page.insert_image(r, stream=img)


PAINT = re.compile(r'(?<=\s)(S|s|f\*?|F|B\*?|b\*?)(?=\s)')
def neutralize(txt):
    """Keep graphics-state ops, drop everything that paints (paths, text, images)."""
    txt = PAINT.sub('n', txt)
    txt = re.sub(r'<[0-9a-fA-F]*>\s*Tj', '', txt)
    txt = re.sub(r'\[[^\]]*\]\s*TJ', '', txt)
    txt = re.sub(r'/\w+\s+Do', '', txt)
    return txt

def strip_oc(page, layer_name):
    """Remove everything drawn on one CAD layer (optional-content group)."""
    props = doc.xref_get_key(page.xref, 'Resources/Properties')[1]
    tags = [k for k, x in re.findall(r'/(oc\d+) (\d+) 0 R', props)
            if doc.xref_get_key(int(x), 'Name')[1].strip('()') == layer_name]
    assert tags, layer_name
    n = 0
    for xref in page.get_contents():
        st = doc.xref_stream(xref).decode('latin1'); out = []; pos = 0
        for m in re.finditer(r'/OC /(oc\d+) BDC', st):
            if m.group(1) not in tags:
                continue
            e = st.find('EMC', m.end())
            out.append(st[pos:m.end()]); out.append(neutralize(st[m.end():e])); pos = e; n += 1
        if out:
            out.append(st[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    return n

def strip_text_in(page, rect, keep=()):
    """Delete every Tj whose origin falls inside a display-space rect."""
    rect = fitz.Rect(rect); n = 0
    tok = re.compile(r'([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) Tm|<([0-9a-fA-F]+)> Tj')
    for xref in page.get_contents():
        st = doc.xref_stream(xref).decode('latin1'); out = []; pos = 0; tm = None
        for m in tok.finditer(st):
            if m.group(1) is not None:
                tm = (float(m.group(5)), float(m.group(6))); continue
            if tm is None:
                continue
            u = fitz.Point(tm[0] * 0.12, 1584 - tm[1] * 0.12) * page.rotation_matrix
            if rect.contains(u):
                out.append(st[pos:m.start()]); pos = m.end(); n += 1
        if out:
            out.append(st[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    return n

def legend_row(dr, y0, base_off, code, title, sub, img, color):
    sw = (742.0, y0, 805.0, y0 + 63.0)
    if img:
        copy_image(doc[1], img, dr.p, sw)
    else:
        dr.rect(sw, width=0, color=None, fill=(0.93, 0.925, 0.91))
        for k in range(1, 4):
            dr.line([(742.0 + 15.75 * k, y0), (742.0 + 15.75 * k, y0 + 63.0)], 0.4, (1, 1, 1))
            dr.line([(742.0, y0 + 15.75 * k), (805.0, y0 + 15.75 * k)], 0.4, (1, 1, 1))
    base = y0 + base_off
    w = dr.text(822.2, base, code, 11.0257, color, bold=True)
    dr.text(822.2 + w, base, title, 11.0257, color)
    for i, t in enumerate(sub):
        dr.text(858.4, base + 13.4 * (i + 1), t, 11.0257, color)

def oc_tags(page, layer_name):
    props = doc.xref_get_key(page.xref, 'Resources/Properties')[1]
    return [k for k, x in re.findall(r'/(oc\d+) (\d+) 0 R', props)
            if doc.xref_get_key(int(x), 'Name')[1].strip('()') == layer_name]

def insert_after_block(page, xref, block_index, content):
    """Insert content right after the block_index-th /OC block of one content stream (0-based)."""
    st = doc.xref_stream(xref).decode('latin1')
    ms = list(re.finditer(r'/OC /(oc\d+) BDC', st))
    end = st.find('EMC', ms[block_index].end())
    st = st[:end + 3] + '\nq\n' + content + '\nQ\n' + st[end + 3:]
    doc.update_stream(xref, st.encode('latin1'))

def insert_after_layer(page, layer_name, content):
    """Insert content right after the LAST block of a CAD layer."""
    tags = oc_tags(page, layer_name); assert tags, layer_name
    for xref in reversed(page.get_contents()):
        st = doc.xref_stream(xref).decode('latin1')
        last = None
        for m in re.finditer(r'/OC /(oc\d+) BDC', st):
            if m.group(1) in tags:
                last = st.find('EMC', m.end())
        if last is not None:
            st = st[:last + 3] + '\nq\n' + content + '\nQ\n' + st[last + 3:]
            doc.update_stream(xref, st.encode('latin1')); return
    raise RuntimeError('layer block not found')

TOK = re.compile(r'(?P<num>[-+]?(?:\d+\.\d*|\.\d+|\d+))|(?P<hex><[0-9a-fA-F]*>)|(?P<arr>\[[^\]]*\])|(?P<name>/[^\s\[\]<>/(]*)|(?P<op>[A-Za-z\'\"][A-Za-z0-9\*\'\"]*)')
PAINT_OPS = {'S', 's', 'f', 'F', 'f*', 'B', 'B*', 'b', 'b*'}

def strip_paths_in(page, rect, layer_name, exclude=None):
    """Neutralize every path on one layer whose points all fall inside rect (display coords).
    Paths lying entirely inside `exclude` are kept."""
    rect = fitz.Rect(rect); tags = oc_tags(page, layer_name); assert tags, layer_name
    exclude = fitz.Rect(exclude) if exclude else None
    R = page.rotation_matrix; n = 0
    for xref in page.get_contents():
        st = doc.xref_stream(xref).decode('latin1'); out = []; pos = 0; changed = False
        for m in re.finditer(r'/OC /(oc\d+) BDC', st):
            if m.group(1) not in tags:
                continue
            e = st.find('EMC', m.end())
            seg = st[m.end():e]
            nums = []; pts = []; dirty = False; in_cm = False; edits = []
            for t in TOK.finditer(seg):
                if t.group('num'):
                    nums.append(float(t.group('num'))); continue
                op = t.group('op')
                if op is None:
                    nums = []; continue
                if in_cm and op in ('m', 'l', 'c', 'v', 'y', 're'):
                    pass
                elif op in ('m', 'l') and len(nums) >= 2:
                    pts.append(nums[-2:])
                elif op == 're' and len(nums) >= 4:
                    x, y, w, h = nums[-4:]; pts += [[x, y], [x + w, y + h]]
                elif op == 'c' and len(nums) >= 6:
                    pts += [nums[0:2], nums[2:4], nums[4:6]]
                elif op in ('v', 'y') and len(nums) >= 4:
                    pts += [nums[0:2], nums[2:4]]
                elif op == 'cm':
                    if len(nums) >= 6:
                        pts.append(nums[-2:]); in_cm = True   # transformed group: judge it by its origin only
                    else:
                        dirty = True
                elif op in PAINT_OPS or op == 'n':
                    if op != 'n' and pts and not dirty:
                        dp = [fitz.Point(x * 0.12, 1584 - y * 0.12) * R for x, y in pts]
                        ok = all(rect.contains(q) for q in dp)
                        if ok and exclude is not None and all(exclude.contains(q) for q in dp):
                            ok = False
                        if ok:
                            edits.append((t.start(), t.end()))
                    pts = []; dirty = False; in_cm = False
                elif op == 'Q':
                    dirty = False; in_cm = False
                nums = []
            if edits:
                piece = []; p0 = 0
                for a, b in edits:
                    piece.append(seg[p0:a]); piece.append('n'); p0 = b
                piece.append(seg[p0:])
                out.append(st[pos:m.end()]); out.append(''.join(piece)); pos = e; changed = True; n += len(edits)
        if changed:
            out.append(st[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    return n

EDGE = '0.45 0.45 0.45'   # border edge lines: darker than the hatch so the band reads at print scale
BAND_FILL = '0.875 0.875 0.875'   # same gray the designer used for her Floor 1 bands
JOINT_FT = 4.0                    # butt joint across the border board every 4 ft
def band(page, poly, width, edge_w=3.0, miters=True, joints=True):
    """Border band inside poly drawn as a wood board: gray fill, inner and outer edge lines,
    butt joints across the band every JOINT_FT, miter lines at corners."""
    from shapely.geometry import Point as _Pt
    inner = poly.buffer(-width, join_style=2)
    ring = poly.difference(inner)
    s = [region(page, ring, BAND_FILL), 'q', f'{EDGE} RG', f'{edge_w} w', '0 J']
    lines = []
    ic = list(inner.exterior.coords)
    oc_all = list(poly.exterior.coords)
    for a, b in zip(ic, ic[1:]):
        lines.append(line_op(page, a, b))
    for a, b in zip(oc_all, oc_all[1:]):
        lines.append(line_op(page, a, b))
    if miters:
        oc = oc_all[:-1]
        for k, o in enumerate(oc):
            pa, pb = oc[k - 1], oc[(k + 1) % len(oc)]
            ux, uy = o[0] - pa[0], o[1] - pa[1]; vx, vy = pb[0] - o[0], pb[1] - o[1]
            cross = ux * vy - uy * vx; dot = ux * vx + uy * vy
            import math
            if abs(math.degrees(math.atan2(cross, dot))) < 10:   # not a corner, no miter
                continue
            i = min(ic, key=lambda q: (q[0] - o[0]) ** 2 + (q[1] - o[1]) ** 2)
            lines.append(line_op(page, o, i))
    if joints:
        step = JOINT_FT * FT
        for a, b in zip(ic, ic[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = (dx * dx + dy * dy) ** 0.5
            if L < step * 0.75:
                continue
            ux, uy = dx / L, dy / L
            # outward normal: the one whose test point lands inside the ring
            for nx, ny in ((-uy, ux), (uy, -ux)):
                tp = _Pt(a[0] + ux * L / 2 + nx * width / 2, a[1] + uy * L / 2 + ny * width / 2)
                if ring.contains(tp):
                    break
            n_j = int(L // step)
            off = (L - n_j * step) / 2 + step / 2 if n_j > 0 else L / 2
            d = off
            while d < L - step * 0.25:
                px, py = a[0] + ux * d, a[1] + uy * d
                q0 = (px, py); q1 = (px + nx * width, py + ny * width)
                if ring.buffer(0.2).contains(_Pt(*q1)):
                    lines.append(line_op(page, q0, q1))
                d += step
    s.append('\n'.join(l + ' S' for l in lines)); s.append('Q')
    return '\n'.join(s), inner

STRIP_FILL = '0.55 0.55 0.55'   # SL-01 brass strip reads as a dark line
def band_ring(page, outer, inner, width, cut=None, strip=None, edge_w=3.0):
    """Border drawn from the designer's own ring polygons (outer boundary and inner boundary) as a wood board:
    gray fill, edge lines, butt joints every JOINT_FT, miters at corners. `cut` geometry is removed from the
    ring (an opening where the floor runs continuous). `strip` is an optional (strip_outer, strip_inner) pair
    for a metal strip drawn as a dark band at the inner edge. All lines are clipped to the ring."""
    import math
    from shapely.geometry import LineString as _LS, Point as _Pt
    ring = outer.difference(inner)
    if cut is not None:
        ring = ring.difference(cut)
    clipper = ring.buffer(0.25)
    segs = []
    def add(a, b):
        g = _LS([a, b]).intersection(clipper)
        if g.is_empty: return
        gs = [g] if g.geom_type == 'LineString' else [q for q in g.geoms if q.geom_type == 'LineString']
        for q in gs:
            c = list(q.coords)
            if len(c) >= 2 and _LS(c).length > 0.3:
                segs.append((c[0], c[-1]))
    ic = list(inner.exterior.coords); oc_all = list(outer.exterior.coords)
    for a, b in zip(ic, ic[1:]): add(a, b)
    for a, b in zip(oc_all, oc_all[1:]): add(a, b)
    oc = oc_all[:-1]
    for k, o in enumerate(oc):
        pa, pb = oc[k - 1], oc[(k + 1) % len(oc)]
        ux, uy = o[0] - pa[0], o[1] - pa[1]; vx, vy = pb[0] - o[0], pb[1] - o[1]
        if abs(math.degrees(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy))) < 10: continue
        i = min(ic, key=lambda q: (q[0] - o[0]) ** 2 + (q[1] - o[1]) ** 2)
        if ((i[0] - o[0]) ** 2 + (i[1] - o[1]) ** 2) ** 0.5 < width * 1.6: add(o, i)
    step = JOINT_FT * FT
    for a, b in zip(ic, ic[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = (dx * dx + dy * dy) ** 0.5
        if L < step * 0.75: continue
        ux, uy = dx / L, dy / L
        for nx, ny in ((-uy, ux), (uy, -ux)):
            if ring.contains(_Pt(a[0] + ux * L / 2 + nx * width / 2, a[1] + uy * L / 2 + ny * width / 2)): break
        n_j = int(L // step); d = (L - n_j * step) / 2 + step / 2 if n_j > 0 else L / 2
        while d < L - step * 0.25:
            px, py = a[0] + ux * d, a[1] + uy * d
            add((px, py), (px + nx * width, py + ny * width)); d += step
    s = [region(page, ring, BAND_FILL)]
    if strip is not None:
        so, si = strip
        sr = so.difference(si)
        if cut is not None: sr = sr.difference(cut)
        s.append(region(page, sr, STRIP_FILL))
    s += ['q', f'{EDGE} RG', f'{edge_w} w', '0 J', '\n'.join(line_op(page, a, b) + ' S' for a, b in segs), 'Q']
    return '\n'.join(s)

def planks_xs(page, geom, xs, y0, y1, seed=1, joint_len=PLANK_LEN):
    """White fill clipped to geom, vertical plank lines at the given x positions, staggered joints."""
    rnd = random.Random(seed)
    s = ['q', path_ops(page, geom), 'W* n', '1 1 1 rg', '1 1 1 RG']
    bx0, by0, bx1, by1 = geom.bounds
    s.append(path_ops(page, box(bx0 - 2, by0 - 2, bx1 + 2, by1 + 2)) + '\nf')
    s += [f'{HATCH} RG', '1 w', '1 J']
    lines = []
    xs = sorted(xs)
    for i, X in enumerate(xs):
        lines.append(line_op(page, (X, y0 - 1), (X, y1 + 1)))
        if i + 1 < len(xs):
            Y = y0 - joint_len + rnd.uniform(0, joint_len)
            while Y <= y1:
                if Y >= y0:
                    lines.append(line_op(page, (X, Y), (xs[i + 1], Y)))
                Y += joint_len
    s.append('\n'.join(l + ' S' for l in lines)); s.append('Q')
    return '\n'.join(s)

def veins(page, geom, seed=1, density=11.0):
    """Marble: white fill plus a few soft random veins, matching the designer's ST-01 look."""
    import math
    rnd = random.Random(seed)
    s = ['q', path_ops(page, geom), 'W* n', '1 1 1 rg', '1 1 1 RG']
    bx0, by0, bx1, by1 = geom.bounds
    s.append(path_ops(page, box(bx0 - 2, by0 - 2, bx1 + 2, by1 + 2)) + '\nf')
    s += [f'{HATCH} RG', '1 w', '1 J', '1 j']
    w, h = bx1 - bx0, by1 - by0
    n = max(3, int((w + h) / density))
    ops = []
    for k in range(n):
        # start on a random edge, wander across at a shallow random angle
        x, y = bx0 + rnd.uniform(0, w), by0 + rnd.uniform(0, h)
        ang = rnd.uniform(0, math.pi)
        L = rnd.uniform(0.6, 1.4) * max(w, h)
        steps = 6
        pts = [(x, y)]
        for i in range(steps):
            ang += rnd.uniform(-0.45, 0.45)
            x += math.cos(ang) * L / steps; y += math.sin(ang) * L / steps
            pts.append((x, y))
        for a, b in zip(pts, pts[1:]):
            ops.append(line_op(page, a, b) + ' S')
    s.append('\n'.join(ops)); s.append('Q')
    return '\n'.join(s)

def revision_row(dr, desc):
    col = (0.353, 0.353, 0.353)
    y = 842.9
    dr.text(1417.2, y, '1', 7.5, col, align='c')
    dr.text(1451.4, y, '11.01.26', 7.5, col, align='c')
    size = min(7.0, 89.0 / FREG.text_length(desc, fontsize=1.0))
    dr.text(1475.5, y, desc, size, col)

def find(page, txt, color=None, size=None):
    out = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                if sp['text'] == txt and (color is None or sp['color'] == color) and (size is None or abs(sp['size'] - size) < 0.05):
                    o = fitz.Point(sp['origin']) * page.rotation_matrix
                    out.append((round(o.x, 2), round(o.y, 2)))
    return out


# =====================================================================
# PAGE id02 (1st floor): guest bedroom to WD-01, porcelain tile tag rename
# =====================================================================
p1 = doc[1]
G1 = layer_union(1, is_gray)
bed_r = box(91.0, 514.0, 297.0, 641.5)
gbath_r = box(91.0, 641.5, 216.2, 714.5)       # guest bath (left room)
gclos_r = box(216.2, 641.5, 297.7, 714.5)      # guest closet (right room)
entry_r = box(497.0, 974.7, 620.0, 1124.5)     # unnamed room by the powder room
bed = G1.intersection(bed_r)
boh = G1.difference(unary_union([bed_r, gbath_r, gclos_r, entry_r]))   # rooms at the rear exterior door are outside
insert_after_gray(p1, '\n'.join([
    region(p1, bed, '1 1 1', 'plank', seed=7),
    region(p1, G1.intersection(gclos_r), '1 1 1', 'plank', seed=3),
    region(p1, G1.intersection(entry_r), '1 1 1', 'plank', seed=5),
    region(p1, G1.intersection(gbath_r), '1 1 1', 'tile'),
    region(p1, boh, '1 1 1', 'tile'),      # TL-04 plain porcelain, 24x24 shown as 12" module for clarity
]))

# kitchen: the designer tagged the field with the border wood (WD-02); field is WD-01
kitchen_field = [o for o in find(p1, 'WD-02') if o in [(324.84, 218.04), (149.88, 369.0)]]   # the two single tags in the field; the stacked corner tags stay WD-02
assert len(kitchen_field) == 2, kitchen_field
# stairs: landing at the foot of the stair stays ST-01 (designer's marble hatch); the flight is WD-01
flight_tag = [o for o in find(p1, 'WD-02') if o == (580.68, 714.12)]
assert len(flight_tag) == 1, [o for o in find(p1, 'WD-02') if o[0] > 560]
edit_text(p1, [('WD-02', kitchen_field[0], 'WD-01'), ('WD-02', kitchen_field[1], 'WD-01'),
               ('WD-02', flight_tag[0], 'WD-01')])
print('tread veins removed', strip_paths_in(p1, (574.0, 770.0, 616.0, 855.5), 'A-PATT-2LIT-C254'))
print('island tag paths removed', strip_paths_in(p1, (118, 338, 190, 392), 'a-tag fnshs'))
print('island tag text removed', strip_text_in(p1, (140, 360, 180, 385)))


# great room -> piano room: floor runs through the opening, no border across it.
# Geometry from the designer's rings: great room WD-02 band y 661.08-668.04 with the SL-01 strip 660.48-661.08;
# piano room band x 402.8-409.8 / 560.6-567.5 with the strip to 410.4 / 560.0, field x 410.4-560.0, y 668.4-880.8.
print('tag paths removed', strip_paths_in(p1, (505, 662, 592, 704), 'a-tag fnshs'))
print('tag text removed', strip_text_in(p1, (520, 676, 562, 700)))
# exact plank positions of the great room field (the two rooms must read as one floor)
_M1 = p1.rotation_matrix; gr_xs = set()
for _x in p1.get_drawings():
    if _x.get('layer') == 'a-fin flr' and _x['type'] == 's':
        for it in _x['items']:
            if it[0] == 'l':
                a_, b_ = it[1] * _M1, it[2] * _M1
                if abs(a_.x - b_.x) < 0.05 and min(a_.y, b_.y) > 449 and max(a_.y, b_.y) < 661.5 and max(a_.y, b_.y) - min(a_.y, b_.y) > 100 and 410.4 < a_.x < 560.0:
                    gr_xs.add(round(a_.x, 2))
gr_xs = sorted(gr_xs); assert 18 < len(gr_xs) < 26, gr_xs
print('piano field hatch removed', strip_paths_in(p1, (410.0, 668.2, 560.3, 881.0), 'a-fin flr'))
# Piano room field is the designer's inner ring (5304), NOT a bounding box: the stair's first run sits in a
# notch at the SE corner (x 487-560, y 832.4-880.8) and the border wraps it. Filling the box painted over the run.
PIANO_FIELD = Polygon([(410.4, 660.48), (560.0, 660.48), (560.0, 832.4), (487.0, 832.4),
                       (487.0, 880.8), (410.4, 880.8)])
# the run's treads carried the designer's marble veins; treads are WD-01, so the veins go (landing keeps its stone)
print('lower run veins removed', strip_paths_in(p1, (493.5, 839.0, 567.6, 889.0), 'A-PATT-2LIT-C254'))
ops = [region(p1, box(409.8, 660.3, 560.6, 668.9), '1 1 1'),           # no band or strip across the opening
       planks_xs(p1, PIANO_FIELD, gr_xs, 660.48, 880.8, seed=23)]
hl = [line_op(p1, (409.8, 661.08), (409.8, 669.0)), line_op(p1, (410.4, 660.48), (410.4, 669.0)),
      line_op(p1, (560.6, 661.08), (560.6, 669.0)), line_op(p1, (560.0, 660.48), (560.0, 669.0)),
      line_op(p1, (402.8, 668.04), (410.4, 660.48)), line_op(p1, (567.5, 668.04), (560.0, 660.48))]
ops += ['q', f'{EDGE} RG', '3 w', '0 J', '\n'.join(l + ' S' for l in hl), 'Q']
# Floor 1 borders (kitchen, great room, piano) redrawn as wood boards with the SL-01 strip, from the designer's rings
_src1 = fitz.open(SRC)[1]; _dr1 = _src1.get_drawings()   # indices from the untouched source
def _ring(idxs):
    ps = []
    for i in idxs: ps += _pf(_dr1[i], _src1.rotation_matrix)
    u = unary_union(ps); g = u if u.geom_type == 'Polygon' else max(u.geoms, key=lambda q: q.area)
    return Polygon(g.exterior).simplify(0.05)
OPENING = box(409.8, 660.3, 560.6, 668.9)
pi_o, pi_s, pi_i = _ring([5291]), _ring([5292]), _ring([5293])
gr_o, gr_i = _ring([5435]), _ring([5439]); gr_s = gr_i.buffer(0.6, join_style=2)
k_o, k_s, k_i = _ring([5548, 5550, 5552, 5554, 5556]), _ring([5557, 5559, 5561]), _ring([5562, 5564, 5566])
assert abs(pi_o.area - 32773) < 50 and abs(gr_o.area - 69612) < 50 and abs(k_o.area - 87203) < 50
ops += [band_ring(p1, pi_o, pi_s, 6.9, cut=OPENING, strip=(pi_s, pi_i)),
        band_ring(p1, gr_o, gr_s, 6.8, cut=OPENING, strip=(gr_s, gr_i))]
# Draw order matters: the designer's rings sit in stream 729 (blocks 267 piano, 271 great room) and the tags follow in
# block 272 and stream 728. Insert right after the great room ring so the tags and their leaders draw on top of the bands.
insert_after_block(p1, 729, 271, '\n'.join(ops))
insert_after_block(p1, 728, 10, band_ring(p1, k_o, k_s, 6.9, strip=(k_s, k_i)))   # kitchen ring is 728 block 10

# PT-01 (porcelain) collides with PT-01 (paint) on id07 -> TL-01
edit_text(p1, [
    ('PT-01', None, 'TL-01'),            # foyer tag
    ('PT-01', None, 'TL-01'),            # pantry tag
    ('PT-01', None, 'TL-01'),            # legend code
    ('Coconut Grove, FL 33143', None, 'Coconut Grove, FL 33133'),
])


# keep the legend code flush with its "_" after the PT->TL swap (TL-01 is 1.3pt narrower)
for xref in p1.get_contents():
    s_ = doc.xref_stream(xref).decode('latin1')
    cur = None; out = []; pos = 0
    for m in re.finditer(r'/(F\d+) [\d.]+ Tf|<0037002f001000130014> Tj', s_):
        if m.group(1):
            cur = m.group(1); continue
        if cur == 'F3':
            out.append(s_[pos:m.start()]); out.append('[<0037> -30 <002f> -30 <0010> -30 <0013> -30 <0014>] TJ'); pos = m.end()
    if out:
        out.append(s_[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))

# =====================================================================
# PAGE id07 (2nd floor)
# =====================================================================
p2 = doc[2]
G2 = layer_union(2, is_gray)
bath3 = box(114.0, 140.0, 194.1, 278.9)
bath2 = box(114.0, 278.9, 194.1, 411.0)
mbath = box(116.0, 854.7, 307.6, 1019.0)
ahu = box(266.0, 620.5, 309.8, 667.0)
stair = box(484.0, 679.5, 576.0, 733.0)      # top landing only; the flight below it stays clean
flight_top = box(519.5, 733.0, 576.5, 769.0)   # top treads of the flight: no floor hatch on treads
wood2 = G2.difference(unary_union([bath3, bath2, ahu, stair, flight_top]))

# W.I.C.: herringbone out, straight planks in
wic = box(124.0, 670.6, 306.0, 851.3)
safe = box(521.2, 856.3, 573.8, 903.8)
print('wic herringbone removed', strip_paths_in(p2, (123.0, 669.5, 307.0, 852.5), 'a-fin flr'))
print('safe closet herringbone removed', strip_paths_in(p2, (520.5, 855.5, 574.5, 904.5), 'a-fin flr'))

# master suite outline (designer's fill polygon) -> WD-02 border, door openings squared off
_ms = [x for x in p2.get_drawings() if x.get('layer') == 'a-fin flr' and x['type'] == 'fs'][0]
suite = Polygon(unary_union(_pf(_ms, p2.rotation_matrix)).exterior)   # the fill is drawn as a hairline ring
TV_UNIT = box(312.0, 807.5, 333.1, 875.0)         # TV unit on the west wall: furniture, so the border runs behind it
for lyr in ('a-furniture', 'a-rug'):
    print(lyr, 'removed', strip_paths_in(p2, (305, 728, 576, 1023), lyr, exclude=(311.5, 807.0, 333.6, 875.5)))
# square off every door notch exactly at the wall line (a 0.5 pt step at a box edge makes a jog in the band)
suite = suite.difference(unary_union([box(316, 729, 358, 735.72),        # hall door, north wall
                                      box(305, 892, 312.72, 933.5),      # bath door, west wall
                                      box(348, 958.68, 417, 964),        # terrace door, south wall
                                      box(483, 1014.96, 552, 1022),      # terrace door, south wall
                                      box(515.7, 855.5, 574.5, 909.5)])) # safe closet
suite = suite.simplify(0.3)
suite_band, suite_inner = band(p2, suite, 6.75)
suite_band += '\n' + region(p2, TV_UNIT, '1 1 1')   # the unit sits on the floor; its outline draws on top

# hall: WD-01 field, WD-02 border with SL-01 strip, running across every door
hall = G2.intersection(box(313.2, 413.8, 484.0, 730.7)).difference(stair).simplify(0.3)
hall_band, hall_inner = band(p2, hall, 5.0)

content = '\n'.join([
    region(p2, wood2, '1 1 1', 'plank', seed=11),
    region(p2, wic, '1 1 1', 'plank', seed=17),
    region(p2, safe, '1 1 1', 'plank', seed=19),
    suite_band,
    hall_band,
    region(p2, G2.intersection(bath3), '1 1 1', 'tile'),
    region(p2, G2.intersection(bath2), '1 1 1', 'tile'),
    region(p2, mbath, '1 1 1', 'tile'),
    veins(p2, G2.intersection(stair), seed=5),
    region(p2, G2.intersection(flight_top), '1 1 1'),
    region(p2, G2.intersection(ahu), '0.79216 0.79216 0.79216'),
])
insert_after_gray(p2, content)

# interior elevation markers (master bath, master suite, W.I.C.)
print('elev blocks removed', strip_oc(p2, 'a-elev mrk'))
print('elev text removed', sum(strip_text_in(p2, r) for r in [(190, 780, 245, 830), (385, 865, 435, 915), (185, 915, 240, 965)]))
# wall paint schedule: swatches + text
walls_origin = find(p2, 'WALLS')[0]
pt01_origin = find(p2, 'PT-01')[0]
for xref in p2.get_contents():
    st = doc.xref_stream(xref).decode('latin1')
    if re.search(r'/Xop[234] Do', st):
        doc.update_stream(xref, neutralize(st).encode('latin1'))
print('legend text removed', strip_text_in(p2, (730, 45, 1390, 340)))

edits = []
for txt, color, size in [('W.I.C.', 0xff8c1a, None), ('MASTER', 0xff8c1a, None), ('BATHRM', 0xff8c1a, None)]:
    for o in find(p2, txt, color, size):
        edits.append((txt, o, None))
# small overlapping "MASTER / BEDROOM" sitting on top of "MASTER SUITE"
for txt in ('MASTER', 'BEDROOM'):
    for o in find(p2, txt, 0x404040, 10.1825):
        if 350 < o[0] < 450 and 830 < o[1] < 880:
            edits.append((txt, o, None))
# duplicate TERRACE at the bedroom terrace (the one sitting on the chairs)
for o in find(p2, 'TERRACE', 0x404040, 11.7491):
    if o[0] > 450:
        edits.append(('TERRACE', o, None))
# WIC / master bath dimensions were copy-pasted (both read 15'-6" x 16'-2")
dims = [o for o in find(p2, '15\'-6" x 16\'-2"')]
dims.sort(key=lambda o: o[1])
assert len(dims) == 2, dims
wic_dim, mb_dim = dims
edits.append(('15\'-6" x 16\'-2"', wic_dim, None))
edits.append(('15\'-6" x 16\'-2"', mb_dim, None))
edits.append(('Coconut Grove, FL 33143', None, 'Coconut Grove, FL 33133'))
edits.append(('FINISH FLOOR PLAN  -  DIMENSIONS & WALL TAGS', None, 'FINISH FLOOR PLAN  -  FLOOR TAGS & FLOOR FINISH SCHEDULE'))
edits.append(('2nd FLOOR, DIMENSIONS,', None, '2nd FLOOR - FINISH PLAN,'))
edits.append(('FINISHES TAGS & MATERIALS', None, 'FLOOR TAGS'))
edits.append(('SCHEDULE', find(p2, 'SCHEDULE')[0], None))
print('page2 edits', edits)
edit_text(p2, edits)

# ---------- page 2 overlays: text, tags, legend ----------
d2 = Draw(p2)
dark = (0.251, 0.251, 0.251)
d2.text(316.0, 566.0, 'HALL', 9.4, dark, align='c')      # hall unnamed on the designer's sheet
# replacement dimensions, centered where the old ones sat
OLDW = FREG.text_length('15\'-6" x 16\'-2"', fontsize=10.1825)
d2.text(wic_dim[0] + OLDW / 2, wic_dim[1], '13\'-6" x 13\'-5"', 10.1825, dark, align='c')
d2.text(mb_dim[0] + OLDW / 2, mb_dim[1], '13\'-6" x 11\'-8"', 10.1825, dark, align='c')
ms_dim = find(p2, '15\' x 17\'-6"')
assert len(ms_dim) == 1, ms_dim
edit_text(p2, [('15\' x 17\'-6"', ms_dim[0], None)])
MSW = FREG.text_length('15\' x 17\'-6"', fontsize=11.749)
d2.text(ms_dim[0][0] + MSW / 2, ms_dim[0][1], '15\'-0" x 16\'-5"', 11.749, dark, align='c')

tags2 = [
    (268.0, 262.0, 'WD-01'),   # bedroom 3
    (242.0, 520.0, 'WD-01'),   # bedroom 2
    (245.0, 625.0, 'WD-01'),   # den / playroom
    (338.0, 470.0, 'WD-01'),   # hall
    (214.5, 733.0, 'WD-01'),   # W.I.C.
    (445.0, 777.0, 'WD-01'),   # master suite (between linen closet wall and rug)
    (158.0, 268.0, 'TL-02'),   # bath 3 (inside the door, clear of label, toilet and vanity)
    (158.0, 398.0, 'TL-02'),   # bath 2
    (548.0, 820.0, 'WD-01'),   # stair treads and risers
    (214.5, 871.0, 'TL-03'),   # master bath
    (546.0, 712.0, 'ST-01'),   # stair
]
TAG_LEAD = {(158.0, 268.0): 3.0, (158.0, 398.0): 3.0, (214.5, 871.0): 6.0, (338.0, 470.0): 7.0,
            (546.0, 712.0): 6.0, (445.0, 777.0): 5.0, (548.0, 820.0): 5.0}
TAG_SIDES = {(445.0, 777.0): 'r', (548.0, 820.0): 'l', (158.0, 268.0): 'l', (158.0, 398.0): 'l'}
for x, y, c in tags2:
    d2.tag(x, y, c, lead=TAG_LEAD.get((x, y), 11.0), sides=TAG_SIDES.get((x, y), 'lr'))
d2.tag(362.0, 905.0, 'WD-02', lead=31.0, sides='l')   # master suite border, leader lands on the band below the TV unit
d2.tag(430.0, 700.0, 'WD-02', lead=17.0, sides='r', flip=True)    # hall border, leader lands on the band at the open-to-below rail

# legend: FLOORS block takes the place of the removed WALLS block
grey = (0.451, 0.451, 0.451)
p1imgs = {round((fitz.Rect(i['bbox']) * p1.rotation_matrix).y0): i['xref'] for i in p1.get_image_info(xrefs=True)}
WOOD_IMG = p1imgs[416]; MARBLE_IMG = p1imgs[173]
d2.text(walls_origin[0], walls_origin[1], 'FLOORS', 12.53, grey, bold=True)
off2 = pt01_origin[1] - 92.6
WOOD2_IMG = p1imgs[497]; SL_IMG = p1imgs[335]
legend_row(d2, 92.6, off2, 'WD-01', '_ WOOD FLOORS', ['FINISH & SIZE T.B.C.', 'HERRINGBONE IN MASTER SUITE ONLY'], WOOD_IMG, grey)
legend_row(d2, 173.4, off2, 'WD-02', '_ WOOD FLOORS - BORDER', ['FINISH & SIZE T.B.C.', 'HALL & MASTER SUITE'], WOOD2_IMG, grey)
legend_row(d2, 254.2, off2, 'SL-01', '_ SCHLUTER - BORDER', ['GOLD', 'HALL ONLY'], SL_IMG, grey)
legend_row(d2, 335.0, off2, 'TL-02', '_ PORCELAIN TILE - BATHROOMS 2 & 3', ['FINISH & SIZE T.B.C.'], None, grey)
legend_row(d2, 415.8, off2, 'TL-03', '_ PORCELAIN TILE - MASTER BATH', ['FINISH & SIZE T.B.C.'], None, grey)
legend_row(d2, 496.6, off2, 'ST-01', '_ MARBLE FLOORS - STAIRS', ['T.B.C.'], MARBLE_IMG, grey)
revision_row(d2, '2ND FLOOR FINISHES & BORDERS')

# ---------- page 1 overlays ----------
# piano room SW corner: the designer's SL-01/WD-02 border tag sat under the new plank fill; its leaders dangled
print('piano corner tag paths removed', strip_paths_in(p1, (395, 850, 470, 900), 'a-tag fnshs'))
print('piano corner tag text removed', strip_text_in(p1, (395, 850, 470, 900)))
d1 = Draw(p1)
d1.tag_stack(445.0, 870.0, ['SL-01', 'WD-02'], lead=23.8, sides='l')   # piano room border + brass strip, leader on the west band
# PIANO ROOM label lives in an earlier stream than the plank fill and was painted over: strip it and redraw on top
print('piano label removed', strip_text_in(p1, (460, 738, 505, 764)))
d1.text(483.2, 749.6, 'PIANO', 10.1832, dark, align='c')
d1.text(483.2, 758.8, 'ROOM', 10.1832, dark, align='c')
d1.text(195.0, 566.0, 'GUEST', 10.1825, dark, align='c')
d1.text(195.0, 576.6, 'BEDROOM', 10.1825, dark, align='c')
d1.tag(195.0, 597.0, 'WD-01')
# room names the designer left off this base (they are on her wall sheet, offset (2.6, 22.7) from this one)
for cx, base, t in [(201.9, 456.3, 'PANTRY'), (355.9, 726.3, 'LAUNDRY'), (263.9, 781.3, 'SERVICE'), (263.9, 789.3, 'AREA'),
                    (145.4, 771.3, 'PET'), (145.4, 780.3, 'AREA'), (558.4, 1058.3, 'OFFICE'), (204.4, 975.3, 'CARPORT'),
                    (414.4, 1093.3, 'FRONT PORCH')]:
    d1.text(cx, base, t, 9.4, dark, align='c')
d1.tag(200.0, 392.0, 'WD-01', lead=6.0, sides='l')   # kitchen field, below the island
d1.tag(591.0, 812.0, 'WD-01', sides='')                 # stair treads and risers
for x, y, c, lead in [(170.0, 690.0, 'TL-02', 7.0),   # guest bath
                      (245.0, 704.0, 'WD-01', 4.0),   # guest closet
                      (558.0, 1076.0, 'WD-01', 11.0), # office
                      (266.0, 806.0, 'TL-04', 9.0),   # service area / back of house
                      (354.0, 866.0, 'TL-04', 5.0)]:  # storage closet
    d1.tag(x, y, c, lead=lead)
g1c = (0.353, 0.353, 0.353)
wd02 = [o for o in find(p1, 'WD-02') if o[0] > 800][0]
legend_row(d1, 578.0, wd02[1] - 497.0, 'TL-02', '_ PORCELAIN TILE - BATHROOMS', ['FINISH & SIZE T.B.C.'], None, g1c)
revision_row(d1, 'FINISH TAGS & BORDERS')

doc.save(OUT, garbage=3, deflate=True)
print('saved', OUT)
