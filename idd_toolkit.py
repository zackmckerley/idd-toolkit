"""
idd_toolkit.py  -  helpers for producing interior design drawings from a vector PDF base plan.
Proven on the Casa Grove flooring set (PyMuPDF 1.26/2.0, shapely 2.x). Copy into the skill as scripts/idd_toolkit.py.

Coordinate systems
- "display" coords: what you see on the rotated page, origin top-left, points. All public functions take display coords.
- PDF user space: unrotated page, origin bottom-left. CAD plots usually set "0.12 0 0 0.12 0 0 cm" once at the
  top of the first content stream, so raw stream numbers are in units of SCALE pt (detect it, do not assume).
Scale: 3/16" = 1'-0" means 13.5 pt per foot; 1/4" = 18 pt per foot; 1/2" = 36 pt per foot.
"""
import io, re, math, random
import pymupdf as fitz
from fontTools.ttLib import TTFont
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union

PT_PER_FT = {'3/16': 13.5, '1/4': 18.0, '1/8': 9.0, '1/2': 36.0, '3/4': 54.0, '3/8': 27.0}
HATCH = '0.87451 0.87451 0.87451'   # light hatch gray used by AutoCAD plots for floor patterns
EDGE = '0.45 0.45 0.45'             # border edge lines: dark enough to read at print scale

# ----------------------------------------------------------------------------- inspection
def inspect(doc):
    """Print what you need before editing: page sizes, rotation, layers, fonts, images."""
    for i, p in enumerate(doc):
        print(f'page {i}: rect={p.rect} rotation={p.rotation} streams={p.get_contents()}')
        props = doc.xref_get_key(p.xref, 'Resources/Properties')[1]
        layers = {k: doc.xref_get_key(int(x), 'Name')[1].strip('()') for k, x in re.findall(r'/(oc\d+) (\d+) 0 R', props)}
        print('  layers:', sorted(set(layers.values())))
        print('  fonts:', [(f[0], f[3]) for f in p.get_fonts()])
        print('  images:', [(im['xref'], [round(v) for v in fitz.Rect(im['bbox']) * p.rotation_matrix]) for im in p.get_image_info(xrefs=True)])
        print('  text sample:', p.get_text()[:300].replace('\n', ' | '))

def stream_scale(doc, page):
    """Detect the top-level cm scale of the first content stream (0.12 for most AutoCAD plots)."""
    s = doc.xref_stream(page.get_contents()[0]).decode('latin1')
    m = re.search(r'([\d.]+) 0 0 ([\d.]+) 0 0 cm', s[:200])
    return float(m.group(1)) if m else 1.0

def layer_union(page, pred, scale=None):
    """Union of filled drawings on a layer as shapely geometry (display coords). pred(drawing) -> bool."""
    M = page.rotation_matrix; ps = []
    for x in page.get_drawings():
        if pred(x):
            ps += polys_from(x, M)
    return unary_union(ps)

def polys_from(x, M):
    """Polygons from a drawing's path items, split at discontinuities and closed rings."""
    pts, out = [], []
    for it in x['items']:
        if it[0] == 'l':
            a, b = it[1] * M, it[2] * M
            if pts and (abs(pts[-1][0] - a.x) > 1e-3 or abs(pts[-1][1] - a.y) > 1e-3 or
                        (len(pts) > 2 and abs(pts[-1][0] - pts[0][0]) < 1e-3 and abs(pts[-1][1] - pts[0][1]) < 1e-3)):
                out.append(pts); pts = []
            if not pts: pts.append((a.x, a.y))
            pts.append((b.x, b.y))
        elif it[0] == 're':
            r = it[1] * M; out.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
        elif it[0] == 'qu':
            q = it[1] * M; out.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)])
    if pts: out.append(pts)
    res = []
    for o in out:
        if len(o) >= 3:
            pg = Polygon(o).buffer(0)
            if pg.area > 1e-4: res.append(pg)
    return res

def rays(walls, x, y, far=400):
    """Distance from (x, y) to the wall geometry in four directions. Room width = L + R."""
    P = Point(x, y); res = {}
    for name, (dx, dy) in dict(L=(-1, 0), R=(1, 0), U=(0, -1), D=(0, 1)).items():
        it = LineString([(x, y), (x + dx * far, y + dy * far)]).intersection(walls)
        res[name] = round(P.distance(it), 2) if not it.is_empty else None
    return res

def ftin(pt, pt_per_ft):
    i = round(pt / pt_per_ft * 12); return f"{i // 12}'-{i % 12}\""

# ----------------------------------------------------------------------------- content-stream editing
def oc_tags(doc, page, layer_name):
    props = doc.xref_get_key(page.xref, 'Resources/Properties')[1]
    return [k for k, x in re.findall(r'/(oc\d+) (\d+) 0 R', props)
            if doc.xref_get_key(int(x), 'Name')[1].strip('()') == layer_name]

def glyph_map(doc, xref):
    """glyph id <-> char for an embedded subset font. Lowest code point wins so '-' beats soft hyphen."""
    f = TTFont(io.BytesIO(doc.extract_font(xref)[3])); cm = f.getBestCmap()
    g2c = {}
    for c, n in sorted(cm.items(), reverse=True):
        g2c[f.getGlyphID(n)] = chr(c)
    c2g = {chr(c): f.getGlyphID(n) for c, n in cm.items()}
    return g2c, c2g

def text_origins(page, txt, color=None, size=None):
    """Display-space baseline origins of every span equal to txt."""
    out = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                if sp['text'].replace('\xad', '-') == txt and (color is None or sp['color'] == color) and (size is None or abs(sp['size'] - size) < 0.05):
                    o = fitz.Point(sp['origin']) * page.rotation_matrix
                    out.append((round(o.x, 2), round(o.y, 2)))
    return out

def edit_text(doc, page, edits, scale=0.12):
    """edits: [(match_text, near_origin_or_None, replacement_or_None)]. Rewrites <hex> Tj strings in place.
    Replacement must use glyphs present in the same subset font (check with glyph_map)."""
    fonts = {f[4]: f[0] for f in page.get_fonts()}
    maps = {k: glyph_map(doc, v) for k, v in fonts.items()}
    H = page.rect.height if page.rotation in (0, 180) else page.rect.width
    done = []
    tok = re.compile(r'/(F\d+) [\d.]+ Tf|([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) Tm|<([0-9a-fA-F]+)> Tj')
    for xref in page.get_contents():
        s = doc.xref_stream(xref).decode('latin1'); cur = None; out = []; pos = 0; changed = False; tm = None
        for m in tok.finditer(s):
            if m.group(1): cur = m.group(1); continue
            if m.group(2) is not None: tm = (float(m.group(6)), float(m.group(7))); continue
            hx = m.group(8); g2c, c2g = maps[cur]
            txt = ''.join(g2c.get(int(hx[i:i + 4], 16), '?') for i in range(0, len(hx), 4))
            if tm is None: continue
            u = fitz.Point(tm[0] * scale, H - tm[1] * scale) * page.rotation_matrix
            for k, (mt, near, act) in enumerate(edits):
                if k in done or txt != mt: continue
                if near is not None and abs(u.x - near[0]) + abs(u.y - near[1]) > 6: continue
                rep = '' if act is None else '<' + ''.join(f'{c2g[c]:04x}' for c in act) + '> Tj'
                out.append(s[pos:m.start()]); out.append(rep); pos = m.end(); done.append(k); changed = True; break
        if changed:
            out.append(s[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    missing = [edits[k][:2] for k in range(len(edits)) if k not in done]
    assert not missing, f'unmatched text edits: {missing}'

def strip_text_in(doc, page, rect, scale=0.12):
    """Delete every Tj whose origin falls inside a display rect."""
    rect = fitz.Rect(rect); n = 0
    H = page.rect.height if page.rotation in (0, 180) else page.rect.width
    tok = re.compile(r'([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) Tm|<([0-9a-fA-F]+)> Tj')
    for xref in page.get_contents():
        st = doc.xref_stream(xref).decode('latin1'); out = []; pos = 0; tm = None
        for m in tok.finditer(st):
            if m.group(1) is not None: tm = (float(m.group(5)), float(m.group(6))); continue
            if tm is None: continue
            if rect.contains(fitz.Point(tm[0] * scale, H - tm[1] * scale) * page.rotation_matrix):
                out.append(st[pos:m.start()]); pos = m.end(); n += 1
        if out:
            out.append(st[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    return n

TOK = re.compile(r'(?P<num>[-+]?(?:\d+\.\d*|\.\d+|\d+))|(?P<hex><[0-9a-fA-F]*>)|(?P<arr>\[[^\]]*\])|(?P<name>/[^\s\[\]<>/(]*)|(?P<op>[A-Za-z\'\"][A-Za-z0-9\*\'\"]*)')
PAINT_OPS = {'S', 's', 'f', 'F', 'f*', 'B', 'B*', 'b', 'b*'}

def strip_paths_in(doc, page, rect, layer_name, exclude=None, scale=0.12):
    """Neutralize (paint op -> 'n') every path on one CAD layer whose points all fall inside rect.
    Paths entirely inside `exclude` are kept. Paths touching a 'cm' are skipped (coordinates unreliable)."""
    rect = fitz.Rect(rect); exclude = fitz.Rect(exclude) if exclude else None
    tags = oc_tags(doc, page, layer_name); assert tags, layer_name
    R = page.rotation_matrix; H = page.rect.height if page.rotation in (0, 180) else page.rect.width; n = 0
    for xref in page.get_contents():
        st = doc.xref_stream(xref).decode('latin1'); out = []; pos = 0; changed = False
        for m in re.finditer(r'/OC /(oc\d+) BDC', st):
            if m.group(1) not in tags: continue
            e = st.find('EMC', m.end()); seg = st[m.end():e]
            nums, pts, dirty, in_cm, edits = [], [], False, False, []
            for t in TOK.finditer(seg):
                if t.group('num'): nums.append(float(t.group('num'))); continue
                op = t.group('op')
                if op is None: nums = []; continue
                if in_cm and op in ('m', 'l', 'c', 'v', 'y', 're'):
                    pass
                elif op in ('m', 'l') and len(nums) >= 2: pts.append(nums[-2:])
                elif op == 're' and len(nums) >= 4:
                    x, y, w, h = nums[-4:]; pts += [[x, y], [x + w, y + h]]
                elif op == 'c' and len(nums) >= 6: pts += [nums[0:2], nums[2:4], nums[4:6]]
                elif op in ('v', 'y') and len(nums) >= 4: pts += [nums[0:2], nums[2:4]]
                elif op == 'cm':
                    if len(nums) >= 6:
                        pts.append(nums[-2:]); in_cm = True   # transformed group: judge it by its origin only
                    else:
                        dirty = True
                elif op in PAINT_OPS or op == 'n':
                    if op != 'n' and pts and not dirty:
                        dp = [fitz.Point(x * scale, H - y * scale) * R for x, y in pts]
                        ok = all(rect.contains(q) for q in dp)
                        if ok and exclude is not None and all(exclude.contains(q) for q in dp): ok = False
                        if ok: edits.append((t.start(), t.end()))
                    pts = []; dirty = False; in_cm = False
                elif op == 'Q': dirty = False; in_cm = False
                nums = []
            if edits:
                piece = []; p0 = 0
                for a, b in edits: piece.append(seg[p0:a]); piece.append('n'); p0 = b
                piece.append(seg[p0:])
                out.append(st[pos:m.end()]); out.append(''.join(piece)); pos = e; changed = True; n += len(edits)
        if changed:
            out.append(st[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    return n

def strip_layer(doc, page, layer_name):
    """Remove everything drawn on one layer (keeps the block so resources stay valid)."""
    tags = oc_tags(doc, page, layer_name); assert tags, layer_name; n = 0
    for xref in page.get_contents():
        st = doc.xref_stream(xref).decode('latin1'); out = []; pos = 0
        for m in re.finditer(r'/OC /(oc\d+) BDC', st):
            if m.group(1) not in tags: continue
            e = st.find('EMC', m.end()); body = st[m.end():e]
            body = re.sub(r'(?<=\s)(S|s|f\*?|F|B\*?|b\*?)(?=\s)', 'n', body)
            body = re.sub(r'<[0-9a-fA-F]*>\s*Tj', '', body); body = re.sub(r'\[[^\]]*\]\s*TJ', '', body); body = re.sub(r'/\w+\s+Do', '', body)
            out.append(st[pos:m.end()]); out.append(body); pos = e; n += 1
        if out: out.append(st[pos:]); doc.update_stream(xref, ''.join(out).encode('latin1'))
    return n

def insert_after_layer(doc, page, layer_name, content):
    """Insert raw content right after the LAST block of a layer (so later layers such as walls still draw on top)."""
    tags = oc_tags(doc, page, layer_name); assert tags, layer_name
    for xref in reversed(page.get_contents()):
        st = doc.xref_stream(xref).decode('latin1'); last = None
        for m in re.finditer(r'/OC /(oc\d+) BDC', st):
            if m.group(1) in tags: last = st.find('EMC', m.end())
        if last is not None:
            st = st[:last + 3] + '\nq\n' + content + '\nQ\n' + st[last + 3:]
            doc.update_stream(xref, st.encode('latin1')); return
    raise RuntimeError('layer block not found')

# ----------------------------------------------------------------------------- raw drawing in stream units
class Stream:
    """Builds raw content-stream ops in display coords for a page with a top-level cm scale."""
    def __init__(self, page, scale=0.12):
        self.p = page; self.s = scale; self.D = page.derotation_matrix
        self.H = page.rect.height if page.rotation in (0, 180) else page.rect.width
    def pt(self, X, Y):
        u = fitz.Point(X, Y) * self.D; return u.x / self.s, (self.H - u.y) / self.s
    def path(self, geom):
        ops = []
        for pg in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            if pg.is_empty: continue
            for ring in [pg.exterior] + list(pg.interiors):
                pts = list(ring.coords); x, y = self.pt(*pts[0]); ops.append(f'{x:.1f} {y:.1f} m')
                for px, py in pts[1:]:
                    x, y = self.pt(px, py); ops.append(f'{x:.1f} {y:.1f} l')
                ops.append('h')
        return '\n'.join(ops)
    def line(self, a, b):
        x0, y0 = self.pt(*a); x1, y1 = self.pt(*b); return f'{x0:.1f} {y0:.1f} m {x1:.1f} {y1:.1f} l'
    def fill(self, geom, rgb='1 1 1'):
        """Clip to geom and fill it (covers whatever was drawn there earlier)."""
        if geom.is_empty: return ''
        x0, y0, x1, y1 = geom.bounds
        return '\n'.join(['q', self.path(geom), 'W* n', f'{rgb} rg', self.path(box(x0 - 2, y0 - 2, x1 + 2, y1 + 2)) + '\nf', 'Q'])
    def lines(self, geom, segs, color=HATCH, w=1, cap=1):
        if not segs: return ''
        return '\n'.join(['q', self.path(geom), 'W* n', f'{color} RG', f'{w} w', f'{cap} J', '\n'.join(self.line(a, b) + ' S' for a, b in segs), 'Q'])

# patterns: each returns raw ops (white fill + lines) clipped to geom, display coords
def planks(S, geom, xs=None, pitch=6.72, plank_len=54.0, seed=1, horizontal=False):
    """Straight plank hatch. Pass xs (exact line positions) to match an existing floor so boards run continuous."""
    rnd = random.Random(seed); x0, y0, x1, y1 = geom.bounds
    if horizontal:  # rotate the problem
        return planks_h(S, geom, pitch, plank_len, seed)
    if xs is None:
        xs = []; X = x0 - (x0 % pitch)
        while X <= x1 + pitch: xs.append(X); X += pitch
    xs = sorted(xs); segs = []
    for i, X in enumerate(xs):
        segs.append(((X, y0 - 1), (X, y1 + 1)))
        if i + 1 < len(xs):
            Y = y0 - plank_len + rnd.uniform(0, plank_len)
            while Y <= y1:
                if Y >= y0: segs.append(((X, Y), (xs[i + 1], Y)))
                Y += plank_len
    return S.fill(geom) + '\n' + S.lines(geom, segs)

def planks_h(S, geom, pitch=6.72, plank_len=54.0, seed=1):
    rnd = random.Random(seed); x0, y0, x1, y1 = geom.bounds; segs = []
    ys = []; Y = y0 - (y0 % pitch)
    while Y <= y1 + pitch: ys.append(Y); Y += pitch
    for i, Y in enumerate(ys):
        segs.append(((x0 - 1, Y), (x1 + 1, Y)))
        if i + 1 < len(ys):
            X = x0 - plank_len + rnd.uniform(0, plank_len)
            while X <= x1:
                if X >= x0: segs.append(((X, Y), (X, ys[i + 1])))
                X += plank_len
    return S.fill(geom) + '\n' + S.lines(geom, segs)

def tile(S, geom, module=13.5, offset=(0, 0)):
    """Square tile grid (module in pt; 13.5 = 12" at 3/16")."""
    x0, y0, x1, y1 = geom.bounds; segs = []
    X = x0 - ((x0 - offset[0]) % module)
    while X <= x1 + module: segs.append(((X, y0 - 1), (X, y1 + 1))); X += module
    Y = y0 - ((y0 - offset[1]) % module)
    while Y <= y1 + module: segs.append(((x0 - 1, Y), (x1 + 1, Y))); Y += module
    return S.fill(geom) + '\n' + S.lines(geom, segs, color='0.80 0.80 0.80', cap=0)

def diagonal_tile(S, geom, module=13.5):
    """Tile set on the diagonal (checkerboard look)."""
    x0, y0, x1, y1 = geom.bounds; step = module * 2 ** 0.5; segs = []
    c = x0 + y0 - ((x0 + y0) % step) - step
    while c <= x1 + y1 + step: segs.append(((c - y0 + 1, y0 - 1), (c - y1 - 1, y1 + 1))); c += step
    c = x0 - y1 - ((x0 - y1) % step) - step
    while c <= x1 - y0 + step: segs.append(((c + y0 - 1, y0 - 1), (c + y1 + 1, y1 + 1))); c += step
    return S.fill(geom) + '\n' + S.lines(geom, segs, cap=0)

def herringbone(S, geom, w=4.5, L=27.0):
    """Herringbone: vertical strips of width L/sqrt2, alternating +45/-45 lines spaced w*sqrt2."""
    x0, y0, x1, y1 = geom.bounds; strip = L / 2 ** 0.5; sp = w * 2 ** 0.5; segs = []
    X = x0 - (x0 % strip); k = 0
    while X < x1:
        segs.append(((X, y0 - 1), (X, y1 + 1)))
        sign = 1 if k % 2 == 0 else -1
        c = y0 - sign * X - ((y0 - sign * X) % sp) - sp * 2
        while c < y1 - sign * X + sp * 2:   # line y = sign*x + c within the strip
            a = (X, sign * X + c); b = (X + strip, sign * (X + strip) + c); segs.append((a, b)); c += sp
        X += strip; k += 1
    return S.fill(geom) + '\n' + S.lines(geom, segs, cap=0)

def veins(S, geom, seed=1, density=11.0):
    """Marble: a few soft wandering veins."""
    rnd = random.Random(seed); x0, y0, x1, y1 = geom.bounds; w, h = x1 - x0, y1 - y0; segs = []
    for k in range(max(3, int((w + h) / density))):
        x, y = x0 + rnd.uniform(0, w), y0 + rnd.uniform(0, h); ang = rnd.uniform(0, math.pi); Ln = rnd.uniform(0.6, 1.4) * max(w, h)
        for i in range(6):
            ang += rnd.uniform(-0.45, 0.45); nx, ny = x + math.cos(ang) * Ln / 6, y + math.sin(ang) * Ln / 6
            segs.append(((x, y), (nx, ny))); x, y = nx, ny
    return S.fill(geom) + '\n' + S.lines(geom, segs)

def band(S, poly, width, edge_w=3.0, miters=True):
    """Border band inside poly: white band, inner-edge line, miter lines at every corner. Returns (ops, inner_poly).
    Square off door notches and subtract built-in footprints from poly first."""
    inner = poly.buffer(-width, join_style=2); ring = poly.difference(inner); segs = []
    ic = list(inner.exterior.coords)
    segs += list(zip(ic, ic[1:]))
    if miters:
        for o in list(poly.exterior.coords)[:-1]:
            segs.append((o, min(ic, key=lambda q: (q[0] - o[0]) ** 2 + (q[1] - o[1]) ** 2)))
    return S.fill(ring) + '\n' + S.lines(ring.buffer(0.6), segs, color=EDGE, w=edge_w, cap=0), inner

# ----------------------------------------------------------------------------- page overlays (tags, text, legend)
class Draw:
    """Overlay drawing on top of everything, display coords, using an embedded TTF buffer (e.g. the plan's own font)."""
    def __init__(self, page, font_buf, bold_buf=None):
        self.p = page; self.D = page.derotation_matrix; self.rot = page.rotation
        self.F = fitz.Font(fontbuffer=font_buf); self.FB = fitz.Font(fontbuffer=bold_buf) if bold_buf else None
        page.insert_font(fontname='idr', fontbuffer=font_buf)
        if bold_buf: page.insert_font(fontname='idb', fontbuffer=bold_buf)
    def P(self, x, y): return fitz.Point(x, y) * self.D
    def text(self, x, y, s, size, color=(0.25, 0.25, 0.25), bold=False, align='l', spacing=0.0):
        f = self.FB if (bold and self.FB) else self.F
        missing = [c for c in s if not f.has_glyph(ord(c))]
        fake = bold and (not self.FB or missing)
        if fake: f = self.F; missing = [c for c in s if not f.has_glyph(ord(c))]
        assert not missing, (s, missing)
        w = sum(f.text_length(c, fontsize=size) for c in s) + spacing * (len(s) - 1) if spacing else f.text_length(s, fontsize=size)
        if align == 'c': x -= w / 2
        if align == 'r': x -= w
        kw = dict(render_mode=2, border_width=size * 0.0042) if fake else {}
        name = 'idr' if (fake or not bold) else 'idb'
        rot = {0: 0, 90: 90, 180: 180, 270: 270}[self.rot]
        if spacing:
            cx = x
            for c in s:
                self.p.insert_text(self.P(cx, y), c, fontsize=size, fontname=name, color=color, rotate=rot, **kw); cx += f.text_length(c, fontsize=size) + spacing
        else:
            self.p.insert_text(self.P(x, y), s, fontsize=size, fontname=name, color=color, rotate=rot, **kw)
        return w
    def line(self, pts, width, color):
        sh = self.p.new_shape(); sh.draw_polyline([self.P(*q) for q in pts]); sh.finish(color=color, width=width, closePath=False, lineCap=1); sh.commit()
    def rect(self, r, width=0.48, color=None, fill=None):
        sh = self.p.new_shape(); q = [self.P(r[0], r[1]), self.P(r[2], r[1]), self.P(r[2], r[3]), self.P(r[0], r[3])]
        sh.draw_polyline(q + [q[0]]); sh.finish(color=color, fill=fill, width=width, closePath=True); sh.commit()
    def circle(self, cx, cy, r, width=0.5, color=(0.25, 0.25, 0.25), fill=None):
        sh = self.p.new_shape(); sh.draw_circle(self.P(cx, cy), r); sh.finish(color=color, fill=fill, width=width); sh.commit()
    def tag(self, cx, cy, code, lead=11.0, sides='lr', size=5.8748):
        """Boxed finish tag with dog-leg leaders (AutoCAD interior-design style)."""
        g = (0.251, 0.251, 0.251); w = self.F.text_length(code, fontsize=size) + 1.0; bh = 7.4
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - bh / 2, cy + bh / 2
        self.rect((x0, y0, x1, y1), width=0.48, color=g); self.text(cx, cy + 2.1, code, size, g, align='c'); d = lead * 0.87
        if 'l' in sides: self.line([(x0, cy), (x0 - 4.7, cy), (x0 - 4.7 - d * 1.15, cy - d)], 0.3, g)
        if 'r' in sides: self.line([(x1, cy), (x1 + 4.7, cy), (x1 + 4.7 + d * 1.15, cy + d)], 0.3, g)
    def tag_stack(self, cx, cy, codes, lead=11.0, sides='lr', size=5.8748):
        g = (0.251, 0.251, 0.251); bh = 7.4; pitch = bh + 0.9; w = max(self.F.text_length(c, fontsize=size) for c in codes) + 1.0
        x0, x1 = cx - w / 2, cx + w / 2; tops = [cy - pitch / 2 - bh / 2, cy + pitch / 2 - bh / 2]
        for c, y0 in zip(codes, tops):
            self.rect((x0, y0, x1, y0 + bh), width=0.48, color=g); self.text(cx, y0 + bh / 2 + 2.1, c, size, g, align='c')
        d = lead * 0.87
        if 'l' in sides: yl = tops[0] + bh / 2; self.line([(x0, yl), (x0 - 4.7, yl), (x0 - 4.7 - d * 1.15, yl - d)], 0.3, g)
        if 'r' in sides: yr = tops[1] + bh / 2; self.line([(x1, yr), (x1 + 4.7, yr), (x1 + 4.7 + d * 1.15, yr + d)], 0.3, g)
    # RCP / lighting symbols (sizes in pt; at 3/16" a 6" can = 6.75 pt diameter)
    def downlight(self, cx, cy, r=3.4, tag=None):
        self.circle(cx, cy, r, fill=(0.6, 0.6, 0.6), color=(0.25, 0.25, 0.25))
        if tag: self.text(cx + r + 1.5, cy + 2, tag, 5.5)
    def pendant(self, cx, cy, r=5.0, tag=None):
        self.circle(cx, cy, r); self.circle(cx, cy, r * 0.45, fill=(0.25, 0.25, 0.25))
        if tag: self.text(cx + r + 1.5, cy + 2, tag, 5.5)
    def sconce(self, cx, cy, wall_dir=(0, -1), r=2.6, tag=None):
        self.circle(cx, cy, r); self.line([(cx, cy), (cx + wall_dir[0] * r * 1.8, cy + wall_dir[1] * r * 1.8)], 0.6, (0.25, 0.25, 0.25))
        if tag: self.text(cx + r + 1.5, cy + 2, tag, 5.5)
    def linear(self, x0, y0, x1, y1, tag=None):
        self.rect((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), width=0.6, color=(0.25, 0.25, 0.25), fill=(0.85, 0.85, 0.85))
        if tag: self.text(max(x0, x1) + 2, max(y0, y1), tag, 5.5)
    def switch(self, cx, cy, kind='S'):
        self.text(cx, cy + 2.5, kind, 7.0, bold=True, align='c')
    def switch_leg(self, pts):
        sh = self.p.new_shape(); sh.draw_polyline([self.P(*q) for q in pts]); sh.finish(color=(0.4, 0.4, 0.4), width=0.4, dashes='[2 1.5] 0'); sh.commit()
    def ceiling_tag(self, cx, cy, height_text, finish_code):
        self.rect((cx - 22, cy - 9, cx + 22, cy + 9), width=0.5, color=(0.25, 0.25, 0.25))
        self.line([(cx - 22, cy), (cx + 22, cy)], 0.4, (0.25, 0.25, 0.25))
        self.text(cx, cy - 2.5, finish_code, 6, align='c'); self.text(cx, cy + 6.5, height_text, 6, align='c')
    def elev_marker(self, cx, cy, sheet, letters='ABCD', r=7.5):
        """Segmented-circle interior elevation symbol: sheet number in the lower half, view letters around."""
        self.circle(cx, cy, r, width=0.6); self.line([(cx - r, cy), (cx + r, cy)], 0.6, (0.25, 0.25, 0.25))
        self.text(cx, cy + 5.5, sheet, 4.2, align='c')
        for L, (dx, dy) in zip(letters, [(0, -1), (1, 0), (0, 1), (-1, 0)]):
            self.text(cx + dx * (r + 4), cy + dy * (r + 4) + 2, L, 5, align='c')

# ----------------------------------------------------------------------------- sheet composition
def place_plan(out, new_page, src, pno, clip_disp, target_xy, H_src):
    """Place a region of a (rotated) source page at 1:1 on a new unrotated page, with a hard clip.
    PyMuPDF ignores `clip` when `rotate` is set, so the clip is added to the content stream by hand."""
    sp = src[pno]; u = clip_disp * sp.derotation_matrix; u.normalize()
    target = fitz.Rect(target_xy[0], target_xy[1], target_xy[0] + clip_disp.width, target_xy[1] + clip_disp.height)
    rot = {0: 0, 90: -90, 180: 180, 270: 90}[sp.rotation]
    new_page.show_pdf_page(target, src, pno, clip=u, rotate=rot)
    xref = new_page.get_contents()[-1]; st = out.xref_stream(xref).decode('latin1')
    assert st.count('Do') == 1, st
    H = new_page.rect.height
    st = st.replace('q ', f'q {target.x0:.2f} {H - target.y1:.2f} {target.width:.2f} {target.height:.2f} re W n ', 1)
    out.update_stream(xref, st.encode('latin1'))
    return target

def scale_bar(D, x, y, pt_per_ft, segs=(0, 2, 4, 8, 12, 16), label='GRAPHIC SCALE  3/16" TO 1\'-0"'):
    for i, (a, b) in enumerate(zip(segs, segs[1:])):
        D.rect((x + a * pt_per_ft, y, x + b * pt_per_ft, y + 6), width=0.5, color=(0.2, 0.2, 0.2), fill=(0.2, 0.2, 0.2) if i % 2 == 0 else (1, 1, 1))
    for v in segs: D.text(x + v * pt_per_ft, y + 15, str(v), 6.5, align='c')
    D.text(x + segs[-1] * pt_per_ft + 14, y + 6.5, 'FEET', 6.5); D.text(x, y - 4, label, 6.5, (0.45, 0.45, 0.45))

# ----------------------------------------------------------------------------- QA
def render_crops(doc, pno, crops, dpi=220, prefix='qa'):
    """crops: {'name': (x0,y0,x1,y1)} in display coords. Look at every one before delivering."""
    for name, r in crops.items():
        doc[pno].get_pixmap(dpi=dpi, clip=fitz.Rect(r)).save(f'{prefix}_{name}.png')

def text_report(doc, pno, must_not=(), must=()):
    t = doc[pno].get_text().replace('\xad', '-')
    codes = sorted(set(re.findall(r'\b(?:WD|TL|ST|SL|PT|WC|WP|WT|CP|CL|MT|GL|FB|L)-?\d\d?\b', t)))
    bad = [w for w in must_not if w in t]; missing = [w for w in must if w not in t]
    return {'codes': codes, 'stale_text_found': bad, 'missing_text': missing}

def pixel_diff(a_page, b_page, rect_a, offset=(0, 0), dpi=150):
    """Mean abs pixel difference between a source region and its placement on a new sheet. ~0 = same scale and position."""
    import numpy as np
    ra = fitz.Rect(rect_a); rb = ra + (offset[0], offset[1], offset[0], offset[1])
    a = a_page.get_pixmap(dpi=dpi, clip=ra); b = b_page.get_pixmap(dpi=dpi, clip=rb)
    A = np.frombuffer(a.samples, np.uint8).reshape(a.h, a.w, a.n); B = np.frombuffer(b.samples, np.uint8).reshape(b.h, b.w, b.n)
    h, w = min(a.h, b.h), min(a.w, b.w)
    return float(abs(A[:h, :w].astype(int) - B[:h, :w].astype(int)).mean())

# ----------------------------------------------------------------------------- DXF export (optional)
def rooms_to_dxf(path, rooms, layer='A-FLOR-IDEN', pt_per_ft=13.5):
    """Write room outlines (display pt) to DXF in inches on NCS layers so the model opens true-scale in CAD."""
    import ezdxf
    doc = ezdxf.new('R2018'); doc.layers.add(layer); msp = doc.modelspace(); k = 12.0 / pt_per_ft
    for name, poly in rooms.items():
        pts = [(x * k, -y * k) for x, y in poly.exterior.coords]
        msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': layer})
        c = poly.centroid; msp.add_text(name, dxfattribs={'layer': layer, 'height': 6}).set_placement((c.x * k, -c.y * k))
    doc.saveas(path)
