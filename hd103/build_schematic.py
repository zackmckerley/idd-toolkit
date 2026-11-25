"""2191 SW 23rd St (HD103): owner's schematic plans, both floors, redrawn from FOR Architecture's 11.24.26 presentation.

Program changes from FOR (owner 11.24.26): 2-car garage, scullery, mudroom downstairs, laundry upstairs, 10' x 25' pool in the
courtyard running into the rear yard, larger primary bath and closets, about 3,700 SF under air.

Coordinates: feet, lot origin at the SW corner of the lot rectangle (x east, y north). Lot 95'-0" x 74'-6" with a 25' radius corner
at SW 22nd Ave and SW 23rd St. Rooms are given on an exterior-face grid; interior polygons are derived (8" exterior, 4-1/2" interior
walls) and handed to idd_planspec, which draws the walls, doors and windows.

FOR's plan is raster (5400 x 3600 px images in the PDF). Scale read at 37.40 px/ft on the 95'-0" north line; the 74'-6" east line
read 74.47' (0.04%). Every lot and setback figure here is scaled from that image, not from a survey.

    python3 hd103/build_schematic.py OUTDIR
"""
import sys, os, json, math
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import unary_union
import idd_std, idd_sheet, idd_planspec
from idd_sheet import Sheet, FR, TB_X, W, H, ps, fix_soft_hyphen, print_ink
from idd_std import LW

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work2191'
os.makedirs(OUT, exist_ok=True)
DATE = '11.24.26'
FILE = '261124.2191SW23.SchematicPlans'

idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE
idd_sheet.REVS = [('0', DATE, 'OWNER SCHEMATIC')]
idd_sheet.remap = lambda s: s          # no ID sheet numbers on this set

T_EXT, T_INT = 8.0 / 12, 4.5 / 12          # wall thickness, ft
LOT_W, LOT_D, R_CORNER = 95.0, 74.5, 25.0
SET = {'W': 20.0, 'S': 10.0, 'N': 7.5, 'E': 7.5}   # FOR's setback lines as drawn (VERIFY: see open items)
LOT_AREA_PA = 7077                           # county record (brokerone.io citing Miami-Dade PA), gross of the corner radius

# ------------------------------------------------------------------ design (exterior-face grid, ft)
F1 = [  # name, x0, y0, x1, y1, kind
    ('DINING', 21.5, 15.0, 40.5, 26.5, 'dining'),
    ('KITCHEN', 21.5, 26.5, 40.5, 43.0, 'kitchen'),
    ('LIVING', 21.5, 43.0, 40.5, 64.0, 'living'),
    ('COAT', 40.5, 15.0, 46.5, 19.5, 'closet'),
    ('ENTRY', 40.5, 19.5, 46.5, 26.0, 'entry'),
    ('POWDER', 40.5, 26.0, 46.5, 31.0, 'powder'),
    ('SCULLERY', 40.5, 31.0, 46.5, 40.5, 'kitchen'),
    ('FOYER', 46.5, 19.5, 57.5, 32.0, 'entry'),
    ('STAIR', 57.5, 15.0, 65.5, 27.5, 'stair'),
    ('MUDROOM', 57.5, 27.5, 65.5, 36.5, 'hall'),
    ('GALLERY', 57.5, 36.5, 72.0, 41.5, 'hall'),
    ('GARAGE', 65.5, 15.0, 87.5, 36.5, 'room'),
    ('GUEST BEDROOM', 72.0, 36.5, 87.5, 50.0, 'bedroom'),
    ('GUEST CLOSET', 72.0, 50.0, 79.0, 56.0, 'closet'),
    ('GUEST BATH', 79.0, 50.0, 87.5, 58.5, 'bath'),
]
F1_OPEN = [('DINING', 'KITCHEN'), ('KITCHEN', 'LIVING'), ('ENTRY', 'FOYER'), ('ENTRY', 'DINING'), ('STAIR', 'FOYER'), ('MUDROOM', 'GALLERY')]
F2 = [
    ('PRIMARY BATH', 21.5, 21.0, 40.5, 31.5, 'bath'),
    ('PRIMARY DRESSING', 21.5, 31.5, 46.5, 40.5, 'closet'),
    ('PRIMARY BEDROOM', 21.5, 40.5, 40.5, 56.0, 'bedroom'),
    ('BEDROOM 3', 40.5, 15.0, 51.5, 27.5, 'bedroom'),
    ('BATH 3', 51.5, 15.0, 57.5, 27.5, 'bath'),
    ('STAIR', 57.5, 15.0, 65.5, 27.5, 'stair'),
    ('LAUNDRY', 65.5, 15.0, 72.0, 27.5, 'laundry'),
    ('CLOSET 2', 72.0, 15.0, 79.0, 24.0, 'closet'),
    ('BATH 2', 79.0, 15.0, 87.5, 24.0, 'bath'),
    ('BEDROOM 2', 72.0, 24.0, 87.5, 36.5, 'bedroom'),
    ('HALL', 40.5, 27.5, 72.0, 31.5, 'hall'),
    ('BEDROOM 4', 46.5, 31.5, 60.0, 44.0, 'bedroom'),
    ('CLOSET 4', 60.0, 31.5, 66.0, 37.5, 'closet'),
    ('LINEN', 66.0, 31.5, 72.0, 37.5, 'closet'),
    ('BATH 4', 60.0, 37.5, 72.0, 44.0, 'bath'),
]
F2_OPEN = [('STAIR', 'HALL')]

# openings: (room, side, a, b, type, extra) with a..b the global coordinate range along the wall (x for N/S, y for E/W)
O1 = [
    ('FOYER', 'S', 50.0, 54.0, 'door', {'hinge': 'L'}),             # 4'-0" pivot entry door
    ('FOYER', 'N', 47.5, 56.5, 'slider', {}),                        # 9' slider to the loggia
    ('FOYER', 'W', 26.0, 26.0, None, {}),
    ('POWDER', 'E', 27.0, 29.67, 'door', {'hinge': 'R', 'swing': 'out'}),
    ('COAT', 'N', 41.25, 45.75, 'pair', {'swing': 'out'}),
    ('SCULLERY', 'W', 33.0, 37.0, 'opening', {}),
    ('SCULLERY', 'N', 41.4, 44.4, 'door', {'hinge': 'L', 'swing': 'out'}),
    ('SCULLERY', 'E', 34.0, 37.5, 'window', {'sill': 36}),           # pass-through to the summer kitchen
    ('LIVING', 'E', 46.0, 61.0, 'slider', {}),
    ('LIVING', 'N', 25.0, 37.0, 'window', {}),
    ('LIVING', 'W', 49.0, 57.0, 'window', {'sill': 60}),
    ('DINING', 'W', 18.0, 24.0, 'window', {}),
    ('DINING', 'S', 25.0, 37.0, 'window', {}),
    ('STAIR', 'S', 59.5, 63.5, 'window', {}),
    ('MUDROOM', 'E', 31.0, 34.0, 'door', {'hinge': 'R', 'swing': 'out'}),
    ('MUDROOM', 'W', 28.0, 31.0, 'opening', {}),
    ('GALLERY', 'N', 58.5, 71.0, 'slider', {}),
    ('GALLERY', 'W', 37.5, 40.5, 'door', {'hinge': 'L', 'swing': 'out'}),
    ('GALLERY', 'E', 37.5, 40.17, 'door', {'hinge': 'L', 'swing': 'out'}),   # into the guest bedroom
    ('GARAGE', 'S', 68.5, 84.5, 'opening', {}),                     # 16'-0" garage door
    ('GUEST BEDROOM', 'W', 42.5, 48.5, 'slider', {}),
    ('GUEST BEDROOM', 'E', 38.5, 41.5, 'door', {'hinge': 'L'}),       # side entry (FOR's note)
    ('GUEST BEDROOM', 'E', 43.5, 48.0, 'window', {}),
    ('GUEST BEDROOM', 'N', 73.0, 75.5, 'door', {'hinge': 'R'}),       # closet
    ('GUEST BEDROOM', 'N', 80.0, 82.67, 'door', {'hinge': 'L'}),      # bath
    ('GUEST BATH', 'N', 82.0, 85.0, 'window', {'sill': 60}),
    ('GUEST CLOSET', 'W', 51.5, 54.5, 'window', {'sill': 60}),
]
O2 = [
    ('PRIMARY DRESSING', 'S', 41.25, 45.25, 'pair', {}),              # suite entry from the hall
    ('PRIMARY DRESSING', 'N', 35.0, 39.0, 'opening', {}),
    ('PRIMARY BATH', 'N', 34.5, 38.5, 'opening', {}),
    ('PRIMARY DRESSING', 'W', 33.5, 38.5, 'window', {'sill': 72}),
    ('PRIMARY BEDROOM', 'N', 24.0, 38.0, 'slider', {}),              # to the terrace
    ('PRIMARY BEDROOM', 'E', 45.0, 53.0, 'window', {}),              # pool view
    ('PRIMARY BATH', 'W', 23.0, 29.0, 'window', {'sill': 72}),
    ('PRIMARY BATH', 'S', 24.0, 29.0, 'window', {'sill': 60}),
    ('BEDROOM 3', 'N', 42.0, 44.67, 'door', {'hinge': 'L'}),
    ('BEDROOM 3', 'E', 23.5, 26.17, 'door', {'hinge': 'L'}),
    ('BEDROOM 3', 'S', 42.5, 49.5, 'window', {}),
    ('BATH 3', 'S', 53.0, 56.0, 'window', {'sill': 60}),
    ('LAUNDRY', 'N', 66.25, 68.92, 'door', {'hinge': 'L'}),
    ('LAUNDRY', 'S', 67.0, 70.5, 'window', {'sill': 48}),
    ('BEDROOM 2', 'W', 28.0, 30.67, 'door', {'hinge': 'R'}),
    ('BEDROOM 2', 'S', 73.0, 75.5, 'door', {'hinge': 'L'}),
    ('BEDROOM 2', 'S', 80.0, 82.67, 'door', {'hinge': 'R'}),
    ('BEDROOM 2', 'E', 26.5, 34.5, 'window', {}),
    ('BATH 2', 'E', 18.0, 21.0, 'window', {'sill': 60}),
    ('CLOSET 2', 'S', 74.0, 77.0, 'window', {'sill': 60}),
    ('BEDROOM 4', 'S', 56.75, 59.42, 'door', {'hinge': 'R'}),
    ('BEDROOM 4', 'E', 33.0, 35.67, 'door', {'hinge': 'R'}),
    ('BEDROOM 4', 'E', 40.0, 42.67, 'door', {'hinge': 'L'}),
    ('BEDROOM 4', 'N', 48.5, 58.0, 'window', {}),
    ('BATH 4', 'N', 64.0, 69.0, 'window', {'sill': 60}),
    ('LINEN', 'S', 67.5, 70.5, 'pair', {}),
]

# ------------------------------------------------------------------ geometry
def interiors(rooms, open_pairs):
    """Interior polygons (ft): the room rectangle inside the building footprint shrunk by the exterior wall, less a 4-1/2" band on
    every shared line that is not an open pair. Returns {name: Polygon}."""
    rects = {r[0]: box(r[1], r[2], r[3], r[4]) for r in rooms}
    foot = unary_union(list(rects.values()))
    inner = foot.buffer(-T_EXT, join_style=2)
    openset = {frozenset(p) for p in open_pairs}
    bands = []
    names = list(rects)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sh = rects[a].boundary.intersection(rects[b].boundary)
            if sh.is_empty or sh.length < 1e-6: continue
            if frozenset((a, b)) in openset: continue
            bands.append(sh.buffer(T_INT / 2, cap_style=2, join_style=2))
    cut = unary_union(bands) if bands else Polygon()
    out = {}
    for n, r in rects.items():
        g = r.intersection(inner).difference(cut)
        if g.geom_type != 'Polygon':
            g = max(g.geoms, key=lambda q: q.area)
        g = Polygon([(round(x, 4), round(y, 4)) for x, y in g.exterior.coords]).simplify(0.001)
        out[n] = g
    return rects, foot, out

def to_spec(rooms, open_pairs, openings, n):
    rects, foot, polys = interiors(rooms, open_pairs)
    kinds = {r[0]: r[5] for r in rooms}
    srooms = [{'name': nm, 'kind': kinds[nm], 'poly': [[x * 12, y * 12] for x, y in list(pg.exterior.coords)[:-1]]} for nm, pg in polys.items()]
    sops = []
    for (nm, side, a, b, typ, ex) in openings:
        if typ is None: continue
        pts = list(polys[nm].exterior.coords)[:-1]
        face = None
        for e in idd_planspec.room_edges([[x * 12, y * 12] for x, y in pts]):
            if e['side'] != side: continue
            (ax, ay), (bx, by) = [(c[0] / 12, c[1] / 12) for c in (e['a'], e['b'])]
            if side in 'NS' and min(ax, bx) - 0.01 <= a and b <= max(ax, bx) + 0.01: face = ay
            if side in 'EW' and min(ay, by) - 0.01 <= a and b <= max(ay, by) + 0.01: face = ax
            if face is not None: break
        assert face is not None, ('opening on no edge', nm, side, a, b)
        pos = {'N': (a, face), 'S': (b, face), 'E': (face, b), 'W': (face, a)}[side]
        w = b - a
        o = {'room': nm, 'side': side, 'pos': [round(pos[0] * 12, 3), round(pos[1] * 12, 3)], 'w': round(w * 12, 2), 'type': typ, 'head': 96}
        o.update({k: v for k, v in ex.items()})
        if typ == 'window': o.setdefault('sill', 24)
        sops.append(o)
    return {'n': n, 'ceiling': 120, 'rooms': srooms, 'openings': sops, 'fixtures': []}, rects, foot, polys

spec1, R1, FOOT1, P1 = to_spec(F1, F1_OPEN, O1, 1)
spec2, R2, FOOT2, P2 = to_spec(F2, F2_OPEN, O2, 2)
spec = {'project': {'name': 'VILLA SHENANDOAH', 'number': 'HD103', 'address': '2191 SW 23RD ST'}, 'scale': '3/16',
        'wall': {'exterior': 8.0, 'interior': 4.5}, 'floors': [spec1, spec2]}
json.dump(spec, open(os.path.join(OUT, 'spec.json'), 'w'), indent=1)

_orig_insert_text = fitz.Page.insert_text
fitz.Page.insert_text = lambda *a, **k: 0          # the base carries walls and openings only; labels are drawn on the sheet
base, models = idd_planspec.build(spec)
fitz.Page.insert_text = _orig_insert_text
base.save(os.path.join(OUT, FILE.replace('SchematicPlans', 'Base') + '.pdf'))
for m in models: json.dump(m, open(os.path.join(OUT, 'model_f%d.json' % m['floor']), 'w'), indent=1)

# ------------------------------------------------------------------ areas (exterior faces)
OUTDOOR_COVERED = {'COVERED ENTRY': box(46.5, 15.0, 57.5, 19.5), 'LOGGIA': box(46.5, 32.0, 57.5, 40.5)}
POOL = box(47.0, 44.5, 57.0, 69.5)
TERRACE = box(21.5, 56.0, 40.5, 64.0)
def ac_area(rects, skip=('GARAGE',)):
    return unary_union([g for n, g in rects.items() if n not in skip]).area
A1 = ac_area(R1); A2 = ac_area(R2); AG = R1['GARAGE'].area
LOT_NET = LOT_W * LOT_D - (R_CORNER ** 2 - math.pi * R_CORNER ** 2 / 4)
COV1 = unary_union(list(R1.values()) + list(OUTDOOR_COVERED.values()) + list(R2.values())).area   # second-story space counts on the first story
COV2 = unary_union(list(R2.values())).area
FOR = {'g': 1735, 's': 1706, 'garage': 272, 'entry': 90, 'terrace': 215}
LOT = Polygon([(R_CORNER, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D), (0, R_CORNER)] +
              [(R_CORNER - R_CORNER * math.cos(t), R_CORNER - R_CORNER * math.sin(t)) for t in [i * (math.pi / 2) / 48 for i in range(1, 48)]])
DECK_POLY = Polygon([(40.5, 40.5), (57.5, 40.5), (57.5, 41.5), (72.0, 41.5), (72.0, 56.0), (79.0, 56.0), (79.0, 58.5), (72.0, 58.5),
                     (72.0, 71.0), (40.5, 71.0)]).difference(box(21.5, 43, 40.5, 64))
HARD = unary_union([unary_union(list(R1.values()) + list(OUTDOOR_COVERED.values())), DECK_POLY, POOL, box(67.5, 0, 85.5, 15), box(50.5, 0, 53.5, 15),
                    box(89.0, 58.0, 93.5, 70.0), box(89.0, 40.0, 93.5, 52.0)]).intersection(LOT)
GREEN = LOT.area - HARD.area
AREAS = {'green': GREEN, 'lot_poly': LOT.area, 'A1': A1, 'A2': A2, 'AC': A1 + A2, 'garage': AG, 'cov1': COV1, 'cov2': COV2, 'lot_net': LOT_NET,
         'pool': POOL.area, 'terrace': TERRACE.area, 'entry': OUTDOOR_COVERED['COVERED ENTRY'].area, 'loggia': OUTDOOR_COVERED['LOGGIA'].area}
json.dump({k: round(v, 1) for k, v in AREAS.items()}, open(os.path.join(OUT, 'areas.json'), 'w'), indent=1)

# ------------------------------------------------------------------ sheet helpers
K = 13.5                                    # pt per ft, 3/16" = 1'-0"
SX, SY = 175.0, 1104.0                       # sheet point of the lot origin (SW 22nd Ave label clear of the frame)
PLAN_X1 = 1460.0                             # side column (north arrow, scale, area box) from SIDE_X
SIDE_X = 1478.0
def S(x, y): return (SX + x * K, SY - y * K)
INK = (0, 0, 0); GREY = (0.35, 0.35, 0.35); LITE = (0.6, 0.6, 0.6); POOLC = (0.80, 0.90, 0.97); DECK = (0.94, 0.94, 0.92)

def ftin(v):
    t = int(round(v * 12)); f, i = divmod(t, 12)
    return "%d'-%d\"" % (f, i)

def place_base(sh, page_no, rects_floor):
    """Place the planspec base 1:1 so its inch coordinates land on the lot coordinates."""
    m = models[page_no]; r0 = m['rooms'][0]
    nm = r0['name']; pg = (P1 if page_no == 0 else P2)[nm]
    bx0, by0, bx1, by1 = pg.bounds                     # ft
    ptx, pty = r0['bounds_pt'][0], r0['bounds_pt'][1]  # base page point of (x0, y1)
    ox, oy = ptx - bx0 * K, pty + by1 * K
    sx, sy = S(0, 0)
    src = base[page_no].rect
    dx, dy = sx - ox, sy - oy
    sh.p.show_pdf_page(fitz.Rect(dx, dy, dx + src.width, dy + src.height), base, page_no)

class Pen:
    def __init__(self, sheet): self.s = sheet; self.p = sheet.p
    def poly(self, pts, w=0.5, c=INK, fill=None, dash=None, close=True):
        sh = self.p.new_shape(); sh.draw_polyline([fitz.Point(*S(*q)) for q in pts] + ([fitz.Point(*S(*pts[0]))] if close else []))
        sh.finish(color=c, fill=fill, width=w, dashes=dash, closePath=False); sh.commit()
    def rect(self, x0, y0, x1, y1, **k): self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **k)
    def line(self, a, b, w=0.5, c=INK, dash=None): self.poly([a, b], w=w, c=c, dash=dash, close=False)
    def circle(self, x, y, r, w=0.4, c=INK, fill=None):
        sh = self.p.new_shape(); sh.draw_circle(fitz.Point(*S(x, y)), r * K); sh.finish(color=c, fill=fill, width=w); sh.commit()
    def oval(self, x0, y0, x1, y1, w=0.4, c=INK):
        a, b = S(x0, y1), S(x1, y0)
        sh = self.p.new_shape(); sh.draw_oval(fitz.Rect(a[0], a[1], b[0], b[1])); sh.finish(color=c, width=w); sh.commit()
    def text(self, x, y, s, size=7.0, bold=False, align='c', c=INK, raw=False):
        px, py = S(x, y); return self.s.text(px, py, s, size, c, bold=bold, align=align, raw=raw)
    def label(self, x, y, name, dims=None, size=8.0):
        self.text(x, y, name, size, bold=True)
        if dims: self.text(x, y - 0.95, dims, size - 1.0)

def room_dims(pg):
    x0, y0, x1, y1 = pg.bounds; return '%s x %s' % (ftin(x1 - x0), ftin(y1 - y0))

# fixtures -----------------------------------------------------------
def toilet(pn, x, y, facing):
    """x, y = center of the tank back against the wall; facing = direction the bowl points."""
    dx, dy = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
    tw, td, bl, bw = 1.75, 0.6, 1.9, 1.25
    if dy:
        pn.rect(x - tw / 2, y if dy > 0 else y - td, x + tw / 2, y + td if dy > 0 else y, w=0.4)
        yb = y + dy * td; pn.oval(x - bw / 2, min(yb, yb + dy * (bl - td)), x + bw / 2, max(yb, yb + dy * (bl - td)))
    else:
        pn.rect(x if dx > 0 else x - td, y - tw / 2, x + td if dx > 0 else x, y + tw / 2, w=0.4)
        xb = x + dx * td; pn.oval(min(xb, xb + dx * (bl - td)), y - bw / 2, max(xb, xb + dx * (bl - td)), y + bw / 2)

def sink(pn, x, y, r=0.6): pn.oval(x - r, y - r * 0.75, x + r, y + r * 0.75)

def counter(pn, x0, y0, x1, y1, sinks=()):
    pn.rect(x0, y0, x1, y1, w=0.5)
    for (sx_, sy_) in sinks: sink(pn, sx_, sy_)

def shower(pn, x0, y0, x1, y1, glass_side=None):
    pn.rect(x0, y0, x1, y1, w=0.4)
    pn.line((x0, y0), (x1, y1), w=0.25, c=GREY); pn.line((x0, y1), (x1, y0), w=0.25, c=GREY)

def tub(pn, x0, y0, x1, y1):
    pn.rect(x0, y0, x1, y1, w=0.5); pn.oval(x0 + 0.35, y0 + 0.35, x1 - 0.35, y1 - 0.35, w=0.4)

def bed(pn, x0, y0, x1, y1, head='S'):
    pn.rect(x0, y0, x1, y1, w=0.4, c=GREY)
    if head in 'NS':
        yp = y0 + 1.4 if head == 'S' else y1 - 1.4
        pn.line((x0, yp), (x1, yp), w=0.3, c=GREY)
    else:
        xp = x0 + 1.4 if head == 'W' else x1 - 1.4
        pn.line((xp, y0), (xp, y1), w=0.3, c=GREY)

def rod(pn, x0, y0, x1, y1, d=2.0, side='N'):
    """Closet run: shelf line at d from the wall and a dashed rod line."""
    if side in 'NS':
        y = y0 - d if side == 'N' else y0 + d
        pn.line((x0, y), (x1, y), w=0.35); pn.line((x0, (y + y0) / 2), (x1, (y + y0) / 2), w=0.3, c=GREY, dash='[2 1.5] 0')
    else:
        x = x0 - d if side == 'E' else x0 + d
        pn.line((x, y0), (x, y1), w=0.35); pn.line(((x + x0) / 2, y0), ((x + x0) / 2, y1), w=0.3, c=GREY, dash='[2 1.5] 0')

def car(pn, x0, y0):
    pn.rect(x0, y0, x0 + 6.2, y0 + 16.0, w=0.35, c=GREY)
    pn.rect(x0 + 0.6, y0 + 4.5, x0 + 5.6, y0 + 10.5, w=0.3, c=GREY)

def stair_ground(pn):
    # U-stair: flight 1 west half rising south from the foyer, landing at the front wall, flight 2 east half rising north to the hall
    x0, x1, xm = 57.5, 65.31, 61.405
    y_land, y_top = 15.67 + 3.33, 27.31
    pn.rect(x0 + 0.1, 15.67, x1, y_top, w=0.0001, c=(1, 1, 1))
    pn.line((xm, y_land), (xm, y_top), w=0.6)
    pn.line((x0 + 0.1, y_land), (x1, y_land), w=0.45)
    tr = (y_top - y_land) / 9
    for i in range(1, 9):
        y = y_land + i * tr
        pn.line((x0 + 0.1, y), (xm, y), w=0.35)
        pn.line((xm, y), (x1, y), w=0.35)
    # cut line on flight 2 and the direction arrows
    pn.line((xm, y_land + 4.3 * tr), (x1, y_land + 5.6 * tr), w=0.5)
    pn.line((x0 + 1.9, y_top - 0.4), (x0 + 1.9, y_land + 0.6), w=0.4)
    pn.poly([(x0 + 1.6, y_land + 1.2), (x0 + 1.9, y_land + 0.6), (x0 + 2.2, y_land + 1.2)], w=0.4, close=False)
    pn.text(x0 + 2.0, y_top + 0.25 - 1.6, 'UP', 6.5, align='l')

def stair_upper(pn):
    x0, x1, xm = 57.5, 65.31, 61.405
    y_land, y_top = 15.67 + 3.33, 27.5
    pn.line((xm, y_land), (xm, y_top), w=0.6)
    pn.line((x0 + 0.67, y_land), (x1, y_land), w=0.45)
    tr = (27.31 - y_land) / 9
    for i in range(1, 9):
        y = y_land + i * tr
        pn.line((x0 + 0.67, y), (xm, y), w=0.35); pn.line((xm, y), (x1, y), w=0.35)
    pn.line((xm + 1.9, y_top - 0.4), (xm + 1.9, y_land + 0.6), w=0.4)
    pn.poly([(xm + 1.6, y_land + 1.2), (xm + 1.9, y_land + 0.6), (xm + 2.2, y_land + 1.2)], w=0.4, close=False)
    pn.text(xm + 2.1, y_top - 1.6, 'DN', 6.5, align='l')
    pn.line((x0 + 0.67, y_top), (xm, y_top), w=1.0)          # guard at the hall over flight 1
    pn.text((x0 + xm) / 2, y_top + 0.35, '42" GUARD', 6.0)

# site --------------------------------------------------------------
def lot_outline(pn, w=1.0, c=INK):
    pts = [(0, LOT_D), (LOT_W, LOT_D), (LOT_W, 0), (R_CORNER, 0)]
    arc = [(R_CORNER - R_CORNER * math.sin(t), R_CORNER - R_CORNER * math.cos(t)) for t in [i * (math.pi / 2) / 24 for i in range(25)]]
    pn.poly(pts + arc + [(0, R_CORNER)], w=w, c=c, dash='[10 2 2 2] 0')

def site(pn, sheet_floor):
    lot_outline(pn)
    for (x, y) in [(0, LOT_D), (LOT_W, LOT_D), (LOT_W, 0), (R_CORNER, 0), (0, R_CORNER)]:
        pn.circle(x, y, 0.35, w=0.6, fill=(1, 1, 1))
    # setback lines (FOR)
    d = '[4 3] 0'
    pn.line((SET['W'], 26.0), (SET['W'], LOT_D - SET['N']), w=0.4, c=GREY, dash=d)
    pn.line((26.0, SET['S']), (LOT_W - SET['E'], SET['S']), w=0.4, c=GREY, dash=d)
    pn.line((SET['W'], LOT_D - SET['N']), (LOT_W - SET['E'], LOT_D - SET['N']), w=0.4, c=GREY, dash=d)
    pn.line((LOT_W - SET['E'], SET['S']), (LOT_W - SET['E'], LOT_D - SET['N']), w=0.4, c=GREY, dash=d)
    # streets and sidewalks
    pn.line((-6.0, 30.0), (-6.0, LOT_D + 3), w=0.4, c=GREY)
    pn.line((30.0, -4.0), (LOT_W + 3, -4.0), w=0.4, c=GREY)
    pn.text(-3.0, 50.0, '', 7)
    sx, sy = S(-7.2, 52.0); pn.s.p.insert_text((sx, sy), 'S.W. 22ND AVENUE', fontsize=ps(10), fontname='cgb', rotate=90, color=INK)
    pn.text(62.0, -5.6, 'S.W. 23RD STREET', 9, bold=True)
    pn.text(-3.0, 66.0, '', 7)
    sx, sy = S(-2.2, 66.0); pn.s.p.insert_text((sx, sy), '6\' SIDEWALK', fontsize=ps(6), fontname='cg', rotate=90, color=GREY)
    pn.text(40.0, -2.8, "4' SIDEWALK", 6, c=GREY)
    if sheet_floor == 1:
        # driveway, walk, pool, deck, equipment
        pn.poly([(67.5, -4.0), (85.5, -4.0), (85.5, 15.0), (67.5, 15.0)], w=0.4, c=GREY, fill=DECK)
        pn.text(76.5, 7.0, 'DRIVEWAY', 7, c=GREY)
        pn.rect(50.5, -4.0, 53.5, 15.0, w=0.4, c=GREY, fill=DECK)
        deck = Polygon([(40.5, 40.5), (57.5, 40.5), (57.5, 41.5), (72.0, 41.5), (72.0, 56.0), (79.0, 56.0), (79.0, 58.5), (72.0, 58.5),
                        (72.0, 71.0), (40.5, 71.0)]).difference(box(21.5, 43, 40.5, 64))
        pn.poly(list(deck.exterior.coords)[:-1], w=0.4, c=GREY, fill=DECK)
        pn.rect(*POOL.bounds, w=0.9, fill=POOLC)
        pn.rect(47.75, 45.25, 56.25, 68.75, w=0.35, c=GREY)
        pn.line((47.75, 49.25), (56.25, 49.25), w=0.35, c=GREY, dash='[3 2] 0')
        pn.text(52.0, 47.0, 'SUN SHELF', 6.5, c=GREY)
        pn.text(52.0, 58.5, "10'-0\" x 25'-0\"", 8, bold=True); pn.text(52.0, 57.3, 'POOL', 8, bold=True)
        pn.text(64.5, 52.5, 'POOL DECK', 7.5, c=GREY)
        pn.rect(89.0, 58.0, 93.5, 70.0, w=0.4, c=GREY)
        pn.text(91.25, 64.6, 'POOL', 6, c=GREY); pn.text(91.25, 63.5, 'EQUIP.', 6, c=GREY); pn.text(91.25, 62.4, 'AND', 6, c=GREY); pn.text(91.25, 61.3, 'GEN.', 6, c=GREY)
        pn.rect(89.0, 40.0, 93.5, 52.0, w=0.4, c=GREY)
        pn.text(91.25, 46.6, 'A/C', 6, c=GREY); pn.text(91.25, 45.5, 'UNITS', 6, c=GREY)
        # privacy wall line along SW 22nd Ave, north and east lines (behind the corner radius)
        pn.line((1.0, R_CORNER + 2.0), (1.0, LOT_D - 1.0), w=1.4, c=GREY)
        pn.line((1.0, LOT_D - 1.0), (LOT_W - 1.0, LOT_D - 1.0), w=1.4, c=GREY)
        pn.line((LOT_W - 1.0, LOT_D - 1.0), (LOT_W - 1.0, 17.0), w=1.4, c=GREY)
        pn.text(3.4, 48.0, '', 7)
        sx, sy = S(2.6, 33.0); pn.s.p.insert_text((sx, sy), 'MASONRY PRIVACY WALL + HEDGE (HEIGHT: VERIFY)', fontsize=ps(6), fontname='cg', rotate=90, color=GREY)

def dim_h(pn, x0, x1, y, txt=None, up=True):
    pn.line((x0, y), (x1, y), w=0.4)
    for x in (x0, x1): pn.line((x - 0.35, y - 0.35), (x + 0.35, y + 0.35), w=0.6); pn.line((x, y - 0.6), (x, y + 0.6), w=0.3)
    pn.text((x0 + x1) / 2, y + (0.35 if up else -1.15), txt or ftin(x1 - x0), 7)

def dim_v(pn, y0, y1, x, txt=None, left=True):
    pn.line((x, y0), (x, y1), w=0.4)
    for y in (y0, y1): pn.line((x - 0.35, y - 0.35), (x + 0.35, y + 0.35), w=0.6); pn.line((x - 0.6, y), (x + 0.6, y), w=0.3)
    sx, sy = S(x - (0.35 if left else -1.15), (y0 + y1) / 2)
    t = txt or ftin(y1 - y0)
    pn.s.p.insert_text((sx, sy + idd_sheet.FREG.text_length(t, 7) / 2), t, fontsize=ps(7), fontname='cg', rotate=90, color=INK)

def north_arrow(sheet, x, y):
    p = sheet.p
    sh = p.new_shape(); sh.draw_circle(fitz.Point(x, y), 16); sh.finish(color=INK, width=0.6); sh.commit()
    sh = p.new_shape(); sh.draw_polyline([fitz.Point(x, y - 22), fitz.Point(x + 7, y + 10), fitz.Point(x, y + 4), fitz.Point(x - 7, y + 10), fitz.Point(x, y - 22)])
    sh.finish(color=INK, fill=INK, width=0.4); sh.commit()
    sheet.text(x, y + 30, 'NORTH', 7, INK, bold=True, align='c')

def wrap(s, width, size):
    words = s.split(); out = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if idd_sheet._FR.text_length(t, fontsize=size) > width and cur: out.append(cur); cur = w_
        else: cur = t
    out.append(cur); return out

def sf(v): return '{:,.0f} SF'.format(v)

# ------------------------------------------------------------------ frame (copied from idd_sheet.Sheet.frame, coordinated-with text for this project)
class SheetHD103(Sheet):
    def frame2(self, title_lines, sheet_no, scale='3/16" TO 1\'-0"'):
        self.frame(None, scale, title_lines, sheet_no, legend_rule=False, plan_x1=PLAN_X1)
        # replace the Casa Grove coordinated-with lines
        hits = [r for t in ('A-201 AND A-202, REV 1, 10.23.26',) for r in self.p.search_for(t)]
        for r in hits:
            self.p.add_redact_annot(r + (-1, -1, 1, 1), fill=(1, 1, 1))
        self.p.apply_redactions(images=0, graphics=0)
        for r in hits:
            self.text(r.x0, r.y1 - 2.2, 'PRESENTATION, 11.24.26 (RASTER)', 9, INK, raw=True)

# ------------------------------------------------------------------ sheets
doc = fitz.open()

def ground_sheet():
    sh = SheetHD103(doc); pn = Pen(sh)
    sh.frame2(['SCHEMATIC PLAN', 'GROUND FLOOR AND SITE'], 'SK-1')
    site(pn, 1)
    for nm, g in OUTDOOR_COVERED.items():
        pn.rect(*g.bounds, w=0.4, c=GREY, dash='[4 2] 0', fill=DECK)
    place_base(sh, 0, R1)
    # fixtures ---------------------------------------------------
    # kitchen: tall wall (refrigerator, freezer, pantry) and range run on the west wall, island with sink
    pn.rect(22.17, 27.0, 24.17, 33.5, w=0.5, fill=(0.85, 0.85, 0.85)); pn.text(24.5, 30.0, 'REF / FRZ COLUMNS', 5.5, align='l')
    counter(pn, 22.17, 33.5, 24.17, 42.6)
    pn.rect(22.17, 36.0, 24.17, 40.0, w=0.5); pn.text(24.5, 37.8, '48" RANGE', 5.5, align='l')
    pn.rect(28.5, 30.5, 33.0, 40.0, w=0.6); sink(pn, 29.9, 35.25, 0.7)
    for yy in (31.8, 34.0, 36.2, 38.4): pn.circle(34.0, yy, 0.65, w=0.35, c=GREY)
    # scullery: counter on the east wall with sink, dishwasher; pantry shelves on the south end
    counter(pn, 43.83, 31.3, 45.83, 40.0, sinks=[(44.83, 35.75)])
    pn.text(44.0, 38.6, '', 6)
    # summer kitchen in the loggia
    counter(pn, 47.0, 33.0, 49.0, 39.8); pn.rect(47.0, 35.0, 49.0, 37.5, w=0.4); pn.text(48.0, 36.0, 'GRILL', 5.5)
    # dining table
    pn.rect(26.5, 18.5, 35.5, 22.0, w=0.4, c=GREY)
    # powder
    toilet(pn, 44.3, 30.81, 'S'); counter(pn, 40.69, 26.4, 42.19, 28.9, sinks=[(41.44, 27.65)])
    # coat closet rod
    rod(pn, 40.69, 17.0, 45.83, 17.0, d=0.0, side='S')
    # mudroom lockers and bench on the west wall facing the loggia
    pn.rect(58.17, 32.2, 59.67, 36.3, w=0.5); pn.text(58.42, 34.0, '', 6)
    for yy in (33.2, 34.25, 35.3): pn.line((58.17, yy), (59.67, yy), w=0.3, c=GREY)
    pn.text(60.0, 34.0, 'LOCKERS', 5.5, align='l')
    stair_ground(pn)
    # garage
    car(pn, 68.0, 17.5); car(pn, 77.5, 17.5)
    # guest suite
    bed(pn, 76.5, 37.2, 81.5, 43.9, head='S')
    toilet(pn, 86.83, 52.0, 'W'); counter(pn, 79.4, 53.8, 81.2, 58.0, sinks=[(80.3, 55.9)])
    shower(pn, 82.4, 54.8, 86.83, 57.83)
    rod(pn, 72.67, 55.33, 78.6, 55.33, d=2.0, side='N')
    # room labels ---------------------------------------------------
    L = {'DINING': (31.0, 24.4), 'KITCHEN': (36.6, 41.4), 'LIVING': (31.0, 54.0), 'COAT': (43.5, 15.9), 'ENTRY': (43.5, 22.8),
         'POWDER': (41.95, 29.55), 'SCULLERY': (42.2, 38.8), 'FOYER': (52.0, 25.5), 'STAIR': (61.4, 24.5), 'MUDROOM': (62.3, 31.0),
         'GALLERY': (64.8, 38.6), 'GARAGE': (76.5, 26.0), 'GUEST BEDROOM': (80.0, 46.5), 'GUEST CLOSET': (75.5, 51.2), 'GUEST BATH': (83.3, 51.4)}
    small = {'COAT', 'ENTRY', 'POWDER', 'SCULLERY', 'GUEST CLOSET', 'STAIR'}
    for nm, (x, y) in L.items():
        g = P1[nm]
        if nm in ('DINING', 'KITCHEN', 'LIVING'):
            pn.label(x, y, nm, '%s x %s' % (ftin(g.bounds[2] - g.bounds[0]), ftin(g.bounds[3] - g.bounds[1])))
        elif nm in small: pn.text(x, y, nm, 6.0, bold=True)
        else: pn.label(x, y, nm, room_dims(g), 7.0)
    pn.text(43.15, 29.1, '', 6)
    pn.text(52.0, 36.8, 'COVERED LOGGIA', 7.0, bold=True); pn.text(52.0, 35.8, 'SUMMER KITCHEN', 6.0)
    pn.text(52.0, 16.8, 'COVERED ENTRY', 6.5, bold=True)
    pn.text(42.2, 37.6, 'SINK, DW', 5.5)
    pn.text(58.42, 37.2 - 1.9, '', 6)
    pn.text(35.0, 27.6, '', 6)
    # dimensions --------------------------------------------------------
    dim_h(pn, 21.5, 87.5, 71.8)
    dim_h(pn, 0, 21.5, 33.0, None)
    dim_v(pn, 0, 15.0, 44.0, None)
    dim_v(pn, 64.0, LOT_D, 30.0, None)
    dim_v(pn, 69.5, LOT_D, 59.0, "5'-0\"", left=False)
    dim_h(pn, 87.5, LOT_W, 30.0, "7'-6\"")
    dim_v(pn, 15.0, 64.0, 17.5)
    side(sh, 1)
    return sh

def upper_sheet():
    sh = SheetHD103(doc); pn = Pen(sh)
    sh.frame2(['SCHEMATIC PLAN', 'SECOND FLOOR'], 'SK-2')
    site(pn, 2)
    # roof below and the pool for orientation
    foot1 = unary_union(list(R1.values()) + list(OUTDOOR_COVERED.values()))
    for g in (foot1.geoms if hasattr(foot1, 'geoms') else [foot1]):
        pn.poly(list(g.exterior.coords)[:-1], w=0.4, c=LITE, dash='[5 3] 0')
    pn.rect(*POOL.bounds, w=0.5, c=LITE, fill=(0.93, 0.96, 0.99))
    pn.rect(*TERRACE.bounds, w=0.5, c=GREY, fill=DECK)
    pn.line((21.5, 64.0), (40.5, 64.0), w=1.2); pn.line((21.5, 56.0), (21.5, 64.0), w=1.2); pn.line((40.5, 56.0), (40.5, 64.0), w=1.2)
    place_base(sh, 1, R2)
    # primary bath: wet room (freestanding tub and shower behind glass) on the west, double vanity south, vanity north, water closet
    pn.rect(22.17, 21.67, 29.0, 31.31, w=0.5)
    pn.line((29.0, 21.67), (29.0, 31.31), w=0.9, c=(0.3, 0.45, 0.6))
    tub(pn, 23.0, 22.4, 28.6, 25.4)
    pn.circle(25.5, 29.0, 0.5, w=0.4)
    pn.text(25.6, 27.2, 'WET ROOM', 6.5, bold=True)
    counter(pn, 29.6, 21.67, 36.4, 23.67, sinks=[(31.4, 22.67), (34.6, 22.67)])
    counter(pn, 29.6, 29.31, 33.6, 31.31, sinks=[(31.6, 30.31)])
    pn.line((36.9, 26.6), (40.31, 26.6), w=0.9); pn.line((36.9, 21.67), (36.9, 23.9), w=0.9); pn.line((36.9, 26.4), (36.9, 26.6), w=0.9)
    pn.line((36.9, 23.9), (36.9, 26.4), w=0.3, c=GREY, dash='[2 1.5] 0'); toilet(pn, 38.6, 21.67, 'N')
    pn.text(38.6, 25.0, 'WC', 6, bold=True)
    # dressing room: wardrobes both walls
    for (a, b) in ((22.17, 34.3), (38.7, 40.31)):
        pn.rect(a, 31.69, b, 33.69, w=0.45); pn.line((a, 32.69), (b, 32.69), w=0.3, c=GREY, dash='[2 1.5] 0')
    for (a, b) in ((22.17, 34.8), ):
        pn.rect(a, 38.31, b, 40.31, w=0.45); pn.line((a, 39.31), (b, 39.31), w=0.3, c=GREY, dash='[2 1.5] 0')
    pn.rect(27.0, 35.4, 31.5, 36.6, w=0.35, c=GREY)
    # bedrooms
    bed(pn, 25.45, 40.69, 31.79, 47.35, head='S')
    for xx in (23.3, 32.0): pn.rect(xx, 40.69, xx + 2.0, 42.2, w=0.35, c=GREY)
    bed(pn, 41.17, 18.4, 47.84, 23.4, head='W')
    bed(pn, 77.3, 29.8, 82.3, 36.31, head='N')
    bed(pn, 46.69, 35.0, 53.36, 40.0, head='W')
    # bath 3 (linear), bath 2, bath 4
    toilet(pn, 54.5, 27.31, 'S'); counter(pn, 55.31, 20.0, 57.31, 23.5, sinks=[(56.31, 21.75)]); shower(pn, 51.69, 15.67, 57.31, 19.4)
    toilet(pn, 86.83, 21.5, 'W'); counter(pn, 79.19, 18.0, 81.19, 22.3, sinks=[(80.19, 20.15)]); shower(pn, 82.0, 15.67, 86.83, 19.0)
    toilet(pn, 62.0, 37.69, 'N'); counter(pn, 62.8, 41.81, 66.6, 43.33, sinks=[(64.7, 42.57)]); shower(pn, 67.0, 37.69, 71.33, 43.33)
    rod(pn, 72.19, 15.67, 72.19, 23.0, d=2.0, side='W'); rod(pn, 78.81, 15.67, 78.81, 23.81, d=2.0, side='E')
    rod(pn, 60.19, 37.31, 65.81, 37.31, d=2.0, side='N'); rod(pn, 65.81, 31.69, 65.81, 37.31, d=2.0, side='E')
    # laundry: washer, dryer, sink, folding counter
    counter(pn, 69.81, 15.67, 71.81, 26.0, sinks=[(70.81, 24.6)])
    pn.rect(69.81, 16.0, 71.81, 18.4, w=0.4); pn.text(70.81, 17.0, 'W', 6, bold=True)
    pn.rect(69.81, 18.6, 71.81, 21.0, w=0.4); pn.text(70.81, 19.6, 'D', 6, bold=True)
    pn.rect(65.69, 15.67, 67.2, 22.0, w=0.35, c=GREY)
    stair_upper(pn)
    L = {'PRIMARY BATH': (34.2, 27.6), 'PRIMARY DRESSING': (30.5, 37.4), 'PRIMARY BEDROOM': (31.0, 51.0), 'BEDROOM 3': (45.8, 24.9),
         'BATH 3': (54.5, 22.1), 'LAUNDRY': (67.6, 24.6), 'CLOSET 2': (75.5, 19.8), 'BATH 2': (83.4, 22.6), 'BEDROOM 2': (79.8, 26.6),
         'HALL': (51.5, 29.1), 'BEDROOM 4': (52.6, 35.6), 'CLOSET 4': (63.0, 33.2), 'LINEN': (69.0, 34.3), 'BATH 4': (63.2, 39.6)}
    small = {'BATH 3', 'CLOSET 2', 'CLOSET 4', 'LINEN', 'HALL', 'LAUNDRY', 'BATH 2', 'BATH 4'}
    for nm, (x, y) in L.items():
        if nm in small: pn.text(x, y, nm, 6.0, bold=True)
        else: pn.label(x, y, nm, room_dims(P2[nm]), 7.0)
    pn.text(31.0, 61.0, 'TERRACE', 7.5, bold=True); pn.text(31.0, 59.9, sf(TERRACE.area).replace(' SF', ' SF') + ', 42" GUARD', 6.0)
    pn.text(31.0, 18.0, 'ROOF BELOW', 6.5, c=GREY)
    pn.text(80.0, 46.0, 'ROOF BELOW', 6.5, c=GREY)
    dim_h(pn, 21.5, 87.5, 71.8)
    dim_v(pn, 15.0, 56.0, 17.5)
    side(sh, 2)
    return sh

def side(sh, floor):
    """Side column: north arrow, graphic scale, the area box for the sheet."""
    north_arrow(sh, SIDE_X + 70, 120)
    sh.scale_bar(SIDE_X + 6, 200, pt_per_ft=K, label='3/16" TO 1\'-0"')
    y = 250
    rows = [('GROUND FLOOR A/C', sf(A1)), ('SECOND FLOOR A/C', sf(A2)), ('TOTAL UNDER AIR', sf(A1 + A2)), ('GARAGE (2 CARS)', sf(AG))]
    if floor == 2: rows.append(('TERRACE', sf(TERRACE.area)))
    else: rows += [('COVERED ENTRY', sf(AREAS['entry'])), ('COVERED LOGGIA', sf(AREAS['loggia'])), ('POOL', "10'-0\" x 25'-0\"")]
    y = legend_block(sh, y, 'AREAS', rows, x=SIDE_X, xr=TB_X - 14)
    rows = ['To the exterior face of the walls. FOR 11.24.26: 3,441 SF under air.', 'See SK-0 for the area comparison, the Miami 21 check, every change from FOR and the open items.']
    legend_block(sh, y, 'NOTES', rows, x=SIDE_X, xr=TB_X - 14)

def legend_block(sheet, y, title, rows, x=None, xr=None, size=7.2, lead=10.5):
    x = x if x is not None else SIDE_X; xr = xr if xr is not None else TB_X - 12
    sheet.text(x, y, title, size + 1.3, INK, bold=True, raw=True); y += lead + 2.5
    for r in rows:
        if isinstance(r, tuple):
            sheet.text(x, y, r[0], size, INK, raw=True)
            if len(r) > 2:
                sheet.text(xr - (xr - x) * 0.17, y, r[1], size, INK, align='r', raw=True); sheet.text(xr, y, r[2], size, INK, align='r', raw=True)
            else:
                sheet.text(xr, y, r[1], size, INK, align='r', raw=True)
            y += lead
        else:
            for ln in wrap(r, xr - x - 2, size):
                sheet.text(x, y, ln, size, INK, raw=True); y += lead * 0.92
            y += 3.0
    return y + 10

def summary_sheet():
    sh = SheetHD103(doc)
    sh.frame2(['PROGRAM, AREAS AND CHANGES', 'FROM FOR 11.24.26'], 'SK-0', scale='NOT TO SCALE')
    g = P1['GARAGE'].bounds; gc = '%s x %s' % (ftin(g[2] - g[0]), ftin(g[3] - g[1]))
    pb = P2['PRIMARY BATH'].bounds; pbc = '%s x %s' % (ftin(pb[2] - pb[0]), ftin(pb[3] - pb[1]))
    pdr = P2['PRIMARY DRESSING'].bounds; pdc = '%s x %s' % (ftin(pdr[2] - pdr[0]), ftin(39.83 - 31.69))
    pbr = P2['PRIMARY BEDROOM'].bounds; pbrc = '%s x %s' % (ftin(pbr[2] - pbr[0]), ftin(pbr[3] - pbr[1]))
    wr = P1['LIVING'].bounds; wrc = ftin(wr[2] - wr[0])
    c1, c2, c3 = 70.0, 600.0, 1130.0; cw = 470.0
    y = 96
    sh.text(c1, y, 'VILLA SHENANDOAH, OWNER SCHEMATIC', 16, INK, serif=True, raw=True)
    sh.text(c1, y + 20, 'Redrawn from FOR Architecture\'s presentation of 11.24.26 with the owner\'s program changes. For FOR to verify and redraw.', 10, INK, raw=True)
    y = 160
    rows = [('', 'FOR 11.24', 'SCHEME'),
            ('Ground floor under air', '{:,}'.format(FOR['g']), '{:,.0f}'.format(A1)),
            ('Second floor under air', '{:,}'.format(FOR['s']), '{:,.0f}'.format(A2)),
            ('Total under air', '{:,}'.format(FOR['g'] + FOR['s']), '{:,.0f}'.format(A1 + A2)),
            ('Garage', '{:,} (1 car)'.format(FOR['garage']), '{:,.0f} (2 cars)'.format(AG)),
            ('Covered entry', '{:,}'.format(FOR['entry']), '{:,.0f}'.format(AREAS['entry'])),
            ('Covered loggia', 'none', '{:,.0f}'.format(AREAS['loggia'])),
            ('Second floor terrace', '{:,}'.format(FOR['terrace']), '{:,.0f}'.format(TERRACE.area)),
            ('Pool', 'about 7.5 x 14 (scaled)', "10' x 25'"),
            ('Bedrooms / baths', '5 + den / 5.5', '5 / 5.5'),
            'SF to the exterior face of the walls. FOR\'s figures are as printed on its plans. A scaled check of FOR\'s second floor gave 1,717 SF against its 1,706, so the two are measured the same way. At $1,000/SF the scheme is about $%s.' % ('{:,.2f}MM'.format((A1 + A2) / 1000))]
    y1 = legend_block(sh, y, 'AREAS (SF)', rows, x=c1, xr=c1 + cw, size=8.5, lead=13.5)
    pct1 = COV1 / LOT_AREA_PA * 100; pct1n = COV1 / LOT_NET * 100
    pct2 = COV2 / LOT_AREA_PA * 100; pct2n = COV2 / LOT_NET * 100
    rows = [('Lot, county record', sf(LOT_AREA_PA)), ('Lot, scaled, less the 25\' corner radius', sf(LOT_NET)),
            ('First story coverage, 50% max.', '%s   %.1f%% / %.1f%%' % (sf(COV1), pct1, pct1n)),
            ('Second story, 30% max. if T3-R or T3-L', '%s   %.1f%% / %.1f%%' % (sf(COV2), pct2, pct2n)),
            ('Green space, 25% min. (est.)', '%s   %.0f%% of net lot' % (sf(GREEN), GREEN / LOT_NET * 100)),
            'Percentages are on the county lot area, then on the scaled net lot. First story coverage includes the garage, covered entry, loggia and the second floor where it overhangs the ground floor. Pool setbacks (Miami 21 5.3.1.g): 20\' principal front, 10\' secondary front, 5\' side and rear.']
    y1 = legend_block(sh, y1, 'MIAMI 21 CHECK (VERIFY WITH FOR)', rows, x=c1, xr=c1 + cw, size=8.5, lead=13.5)
    opens = ['A. Survey and transect (T3-R, T3-L or T3-O). Every lot and setback figure here is scaled from FOR\'s raster plan, not a survey.',
             'B. Which frontage is principal. Miami 21 T3 lists a 20\' principal front, 10\' secondary front and 20\' rear setback. FOR\'s lines (20\' west, 10\' south, 7\'-6" north and east) imply a corner-lot reading the drawings do not state. Confirm before FOR redraws: a 20\' rear setback would move the house.',
             'C. Pool barrier per the Florida residential pool safety act, privacy wall heights at both street frontages, driveway width in the first layer, green space minimum.',
             'D. Stair: 20 risers at about 6-13/16" for a 10\'-0" ceiling and a 16" floor. Two 3\'-6" flights fit the 11\'-8" run with a 3\'-4" landing; FOR to confirm the floor depth.',
             'E. Bedroom 4 and the dressing room cantilever 2\'-6" to 3\'-6" over the loggia and pool deck; structure by FOR\'s engineer.',
             'F. Kitchen has no window of its own (the range wall faces SW 22nd Ave). Light comes from the living room and court sliders; FOR to study a clerestory over the range run.']
    legend_block(sh, y1, 'OPEN ITEMS FOR FOR', opens, x=c1, xr=c1 + cw, size=8.5, lead=13.5)
    notes1 = ['1. Garage widened to 2 cars, %s clear with a 16\'-0" door. It takes the width FOR used for the laundry and pantry, and the east wall moves to FOR\'s 7\'-6" setback line.' % gc,
              '2. Mudroom between the garage and the foyer, with lockers and a bench. It also links the foyer to the gallery and the guest suite.',
              '3. Scullery behind the kitchen, with a sink, dishwasher and pantry shelving. A cased opening connects it to the kitchen, a door to the pool deck and a pass-through window to the summer kitchen.',
              '4. Pool enlarged to 10\'-0" x 25\'-0" with a sun shelf. It runs north from the loggia into the rear yard and stops 5\'-0" off the north line.',
              '5. Covered loggia with a summer kitchen between the foyer and the pool, roofed by Bedroom 4.',
              '6. Great room widened from about 15\'-5" to %s clear by moving the west wall 3\'-9" toward SW 22nd Ave. It stays 1\'-6" inside FOR\'s 20\'-0" setback line.' % wrc,
              '7. Laundry moved upstairs. The powder room opens off the foyer.',
              '8. Stair moved to the front of the house, open to the foyer, with a tall window on SW 23rd St.',
              '9. Guest suite kept on the ground floor with FOR\'s side entry, now with sliders to the pool court.']
    legend_block(sh, 160, 'GROUND FLOOR (SK-1)', notes1, x=c2, xr=c2 + cw, size=8.5, lead=13.5)
    notes2 = ['1. Primary suite: the bedroom, dressing room and bath are set in line, entered through double doors from the hall.',
              '2. Primary bedroom %s clear, with sliders to the terrace over the living room and a window east to the pool.' % pbrc,
              '3. Dressing room %s clear between the wardrobes, with about 40 LF of hanging on both walls and a bench. FOR had his and hers closets of about 7\'-6" x 5\'-6" each (scaled).' % pdc.replace(ftin(39.83 - 31.69), ftin(39.83 - 31.69)),
              '4. Primary bath %s clear (FOR: about 13\'-6" x 6\'-5", scaled): a wet room with a freestanding tub and shower behind one glass wall, a 6\'-10" double vanity, a second vanity and a separate water closet.' % pbc,
              '5. Laundry upstairs beside the bedrooms, with a washer, dryer, sink and folding counter.',
              '6. Bedrooms 2, 3 and 4 each have their own bath. Bedrooms 2 and 4 have walk-in closets, and Bedroom 4 looks over the pool. A linen closet is off the hall.',
              '7. FOR\'s den is gone. Its area went to the laundry and the larger primary suite, which keeps the second floor under the 30% cap and the house near 3,700 SF.']
    legend_block(sh, 160, 'SECOND FLOOR (SK-2)', notes2, x=c3, xr=c3 + cw * 0.97, size=8.5, lead=13.5)
    thumbnails(sh)
    return sh

def thumbnails(sh):
    """FOR's plans and the scheme side by side at one scale (FOR's raster cropped to its lot corners)."""
    from PIL import Image
    s_ = 3.6; gap = 26.0; x0 = 70.0; ytop = 806.0; py = ytop + 76.5 * s_
    sh.text(x0, ytop - 46, 'FOR 11.24.26 AND THE SCHEME, SAME SCALE', 10, INK, bold=True, raw=True)
    sh.text(x0, ytop - 31, 'FOR\'s plans are cropped from its presentation (raster) and credited to FOR Architecture Co. North is up.', 8, INK, raw=True)
    panels = [('FOR, GROUND FLOOR', ('/home/claude/deck/img_p3_11.png', 1115, 3020), '1,735 SF under air, 1-car garage'),
              ('SCHEME, GROUND FLOOR', 0, '{:,.0f} SF under air, 2-car garage'.format(A1)),
              ('FOR, SECOND FLOOR', ('/home/claude/deck/img_p4_22.png', 1126, 3020), '1,706 SF under air, 4 bedrooms and den'),
              ('SCHEME, SECOND FLOOR', 1, '{:,.0f} SF under air, 4 bedrooms and laundry'.format(A2))]
    for i, (title, src, sub) in enumerate(panels):
        px = x0 + 2.0 * s_ + i * (99.0 * s_ + gap)
        if isinstance(src, tuple):
            fn, X0, Y0 = src; ppf = 37.40
            im = Image.open(fn).convert('L')
            box_ = (int(X0 - 2 * ppf), int(Y0 - 76.5 * ppf), int(X0 + 97 * ppf), int(Y0 + 2 * ppf))
            crop = im.crop(box_); outp = os.path.join(OUT, 'thumb_%d.png' % i); crop.resize((crop.width // 3, crop.height // 3)).save(outp)
            sh.p.insert_image(fitz.Rect(px - 2 * s_, py - 76.5 * s_, px + 97 * s_, py + 2 * s_), filename=outp)
        else:
            src_doc = fitz.open(PLANS_TMP); pg_ = src_doc[src]
            a = S(-2.0, 76.5); b = S(97.0, -2.0)
            sh.p.show_pdf_page(fitz.Rect(px - 2 * s_, py - 76.5 * s_, px + 97 * s_, py + 2 * s_), src_doc, src, clip=fitz.Rect(a[0], a[1], b[0], b[1]))
        sh.text(px - 2 * s_, ytop - 10, title, 8.5, INK, bold=True, raw=True)
        sh.text(px - 2 * s_, py + 2 * s_ + 14, sub, 8, INK, raw=True)

ground_sheet(); upper_sheet()
PLANS_TMP = os.path.join(OUT, '_plans_tmp.pdf'); fix_soft_hyphen(doc); doc.save(PLANS_TMP)
summary_sheet(); fix_soft_hyphen(doc); doc.move_page(len(doc) - 1, 0)
fix_soft_hyphen(doc)
full = os.path.join(OUT, FILE + '.pdf')
doc.save(full, garbage=3, deflate=True)
print('saved', full, {k: round(v) for k, v in AREAS.items()})
