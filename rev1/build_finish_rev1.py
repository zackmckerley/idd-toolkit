"""ID-101/102 floor finish plans and ID-201/202 wall finish plans on FOR's REV 1 base (A-201/A-202, 10.23.26), reissued 11.05.26.
Rooms come from FOR's walls (rooms_rev1.py), finishes from the 11.01.26 decisions carried to REV 1's rooms, the base from base_rev1.py,
elevation markers from the designed-room key plans (markers_display.json, written by rebuild_rooms.py).
Output: 261105.HD102.FinishPlans.pdf (ID-101, ID-102, ID-201, ID-202)."""
import json, math, random, sys
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, box, Point
from shapely.ops import unary_union, polylabel
from shapely import affinity
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG
from idd_std import INK, MID, LIGHT
import rooms_rev1 as RR, base_rev1 as BR

OUT = '/home/claude/flrwork/261105.HD102.FinishPlans.pdf'
OLD = '/home/claude/flrwork/261102.HD102.InteriorDesignSet.pdf'   # legend swatches come from the 11.02.26 sheets
BASE = '/home/claude/flrwork/261105.3350THOMAS.Base-clean.pdf'
MARKS = '/home/claude/flrwork/rev1/markers_display.json'
IN = 1.125                                   # sheet pt per inch at 3/16" = 1'-0"
SHIFT = {1: (2.6, 22.7), 2: (0.0, 0.0)}      # the 11.02.26 placement of each floor's base on the sheet (compose_plans.place_base)
TARGET = fitz.Rect(40, 76, 735, 1164)
DARK = (0.251, 0.251, 0.251)
HATCH = (0.80, 0.80, 0.80); GRID = (0.72, 0.72, 0.72); BAND = (0.875, 0.875, 0.875); EDGE = (0.45, 0.45, 0.45); STRIP = (0.55, 0.55, 0.55)
WHITE = (1, 1, 1)

# ------------------------------------------------------------------ geometry: FOR pt -> sheet pt
def to_sheet(floor):
    T = BR.transform(floor); dx, dy = SHIFT[floor]
    return lambda x, y: (T(x, y)[0] + 20 - dx, T(x, y)[1] + 4 - dy)

def geom_to_sheet(g, f):
    def ring(r): return [f(x, y) for x, y in r.coords]
    def poly(p): return Polygon(ring(p.exterior), [ring(i) for i in p.interiors])
    if g.is_empty: return g
    if g.geom_type == 'Polygon': return poly(g)
    if g.geom_type == 'MultiPolygon': return MultiPolygon([poly(p) for p in g.geoms])
    return unary_union([geom_to_sheet(x, f) for x in g.geoms])

def rect_sheet(r, f):
    x0, y0, x1, y1 = r; a = f(x0, y0); b = f(x1, y1)
    return box(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))

def polys(g):
    if g.is_empty: return []
    return list(g.geoms) if hasattr(g, 'geoms') else [g]

# ------------------------------------------------------------------ drawing primitives
def fill(sh, g, color, width=0, stroke=None):
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < 0.5: continue
        s = sh.p.new_shape()
        for r in [p.exterior] + list(p.interiors):
            pts = [fitz.Point(x, y) for x, y in r.coords]; s.draw_polyline(pts)
        s.finish(color=stroke, fill=color, width=width, even_odd=True, closePath=True); s.commit()

def lines_in(sh, g, segs, color, width):
    ml = MultiLineString(segs).intersection(g)
    s = sh.p.new_shape(); n = 0
    for ln in (ml.geoms if hasattr(ml, 'geoms') else [ml]):
        if ln.is_empty or ln.geom_type not in ('LineString', 'LinearRing'): continue
        c = list(ln.coords)
        if len(c) >= 2: s.draw_polyline([fitz.Point(*q) for q in c]); n += 1
    if n: s.finish(color=color, width=width, closePath=False); s.commit()

def planks(sh, g, seed=1, w=6.0, joint=48.0):
    """WD-01: boards north-south 6 in. face, butt joints at random 4 ft lengths, staggered strip to strip."""
    x0, y0, x1, y1 = g.bounds; rnd = random.Random(seed); P = w * IN; L = joint * IN
    segs = []; X = x0 - (x0 % P)
    while X <= x1 + P:
        segs.append([(X, y0 - 2), (X, y1 + 2)])
        Y = y0 - rnd.uniform(0, L)
        while Y < y1:
            Y += L * rnd.uniform(0.75, 1.25)
            if y0 < Y < y1: segs.append([(X, Y), (X + P, Y)])
        X += P
    lines_in(sh, g, segs, HATCH, 0.3)

def herringbone(sh, g, b=3.0, L=18.0):
    """WD-01 herringbone: 3 x 18 in. boards, axis north-south, centered on the room (columns of 45 degree boards, alternating)."""
    x0, y0, x1, y1 = g.bounds; c = L / math.sqrt(2) * IN; s = b * math.sqrt(2) * IN
    cx = (x0 + x1) / 2; n0 = int((x0 - cx) / c) - 1; n1 = int((x1 - cx) / c) + 1
    segs = []
    for k in range(n0, n1 + 1):
        a = cx + k * c; bb = a + c; sgn = 1 if k % 2 == 0 else -1
        segs.append([(a, y0 - 2), (a, y1 + 2)])
        Y = y0 - c - (y0 % s)
        while Y < y1 + c:
            segs.append([(a, Y), (bb, Y + sgn * c)] if sgn > 0 else [(a, Y + c), (bb, Y)]); Y += s
    lines_in(sh, g, segs, HATCH, 0.3)

def grid(sh, g, a=24.0, b=24.0, color=GRID, w=0.3, x_off=0.0):
    x0, y0, x1, y1 = g.bounds; A = a * IN; B = b * IN
    segs = []; X = x0 + x_off
    while X <= x1: segs.append([(X, y0 - 1), (X, y1 + 1)]); X += A
    Y = y0
    while Y <= y1: segs.append([(x0 - 1, Y), (x1 + 1, Y)]); Y += B
    lines_in(sh, g, segs, color, w)

def checker_diag(sh, g, t=12.0):
    """TL-01: 12 in. tiles set on the diagonal, checkered."""
    x0, y0, x1, y1 = g.bounds; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; T = t * IN
    R = max(x1 - x0, y1 - y0); n = int(R / T) + 2
    cells = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            if (i + j) % 2: continue
            sq = box(i * T, j * T, (i + 1) * T, (j + 1) * T)
            cells.append(affinity.translate(affinity.rotate(sq, 45, origin=(0, 0)), cx, cy))
    fill(sh, unary_union(cells).intersection(g), (0.89, 0.89, 0.89))
    segs = []
    for i in range(-2 * n, 2 * n + 1):
        d = i * T / math.sqrt(2) * math.sqrt(2)
        segs.append([(cx - R * 2, cy + d - R * 2 + 0), (cx + R * 2, cy + d + R * 2)])
    rot = [list(affinity.rotate(LineString([(cx - 2 * R, cy + k * T), (cx + 2 * R, cy + k * T)]), a, origin=(cx, cy)).coords)
           for k in range(-2 * n, 2 * n + 1) for a in (45, -45)]
    lines_in(sh, g, rot, (0.78, 0.78, 0.78), 0.25)

def veins(sh, g, seed=3, n=6):
    x0, y0, x1, y1 = g.bounds; rnd = random.Random(seed)
    fill(sh, g, (0.955, 0.955, 0.955))
    segs = []
    for _ in range(n):
        x = rnd.uniform(x0, x1); y = y0; pts = [(x, y)]; ang = rnd.uniform(1.1, 2.0)
        while y < y1 and x0 - 5 < x < x1 + 5:
            ang += rnd.uniform(-0.35, 0.35); x += math.cos(ang) * 6; y += abs(math.sin(ang)) * 6 + 1; pts.append((x, y))
        segs.append(pts)
    lines_in(sh, g, segs, (0.62, 0.62, 0.62), 0.35)

def band(sh, g, w_in, strip=False, open_=None):
    """WD-02 border inside the room's walls, mitered at every corner. open_: edges with no wall (a stair, a wide opening to another
    room): the border stops square at them and the field runs through."""
    w = w_in * IN; out = []
    for p in polys(g):
        ring_ = p.difference(p.buffer(-w, join_style=2, mitre_limit=10))
        if open_ is not None and not open_.is_empty: ring_ = ring_.difference(open_.buffer(w * 1.5, cap_style=2, join_style=2)).buffer(-0.6, join_style=2).buffer(0.6, join_style=2)
        ring_ = unary_union([q for q in polys(ring_) if q.geom_type == 'Polygon' and q.area > w * w * 1.5])
        if ring_.is_empty: out.append(p); continue
        ring_ = MultiPolygon(polys(ring_)) if ring_.geom_type != 'Polygon' else ring_
        fill(sh, ring_, BAND)
        inner = p.difference(ring_)
        # the field side of the band and its square stops, not the wall side
        edge = ring_.boundary.difference(p.boundary.buffer(0.3))
        segs = [list(e.coords) for e in (edge.geoms if hasattr(edge, 'geoms') else [edge]) if e.geom_type == 'LineString' and e.length > 0.6]
        if segs:
            s = sh.p.new_shape()
            for c in segs: s.draw_polyline([fitz.Point(*q) for q in c])
            s.finish(color=STRIP if strip else EDGE, width=0.9 if strip else 0.35, closePath=False); s.commit()
        # miters at the corners of the walls
        for r in [p.exterior] + list(p.interiors):
            pts = list(r.coords)[:-1]
            for i, v in enumerate(pts):
                a = pts[i - 1]; c = pts[(i + 1) % len(pts)]
                e1 = (v[0] - a[0], v[1] - a[1]); e2 = (c[0] - v[0], c[1] - v[1])
                l1 = math.hypot(*e1) or 1; l2 = math.hypot(*e2) or 1
                if l1 < w * 0.8 or l2 < w * 0.8: continue
                n1 = (-e1[1] / l1, e1[0] / l1); n2 = (-e2[1] / l2, e2[0] / l2)
                q = (v[0] + (n1[0] + n2[0]) * w, v[1] + (n1[1] + n2[1]) * w)
                if not p.buffer(0.2).contains(Point(q)):
                    q = (v[0] - (n1[0] + n2[0]) * w, v[1] - (n1[1] + n2[1]) * w)
                seg = LineString([v, q]).intersection(ring_.buffer(0.05))
                if not seg.is_empty and seg.length > 0.9 * math.hypot(q[0] - v[0], q[1] - v[1]):
                    lines_in(sh, ring_.buffer(0.05), [[v, q]], EDGE, 0.35)
        out.append(inner)
    return unary_union(out) if out else g

# ------------------------------------------------------------------ finish assignments (11.01.26 decisions carried to REV 1's rooms)
FLOOR = {
    1: {'KITCHEN AND DINING': ('WD-01', 'plank', 6.0, True), 'LIVING ROOM': ('WD-01', 'plank', 6.0, True),
        'PANTRY': ('TL-01', 'checker', 0, False), 'ENTRY': ('TL-01', 'checker', 0, False),
        'GUEST BEDROOM': ('WD-01', 'plank', 0, False), 'W.I.C.': ('WD-01', 'plank', 0, False), 'OFFICE': ('WD-01', 'plank', 0, False),
        'STAIR CLOSET': ('WD-01', 'plank', 0, False), 'CLOSET': ('TL-04', 'grid24', 0, False),
        'GUEST BATHROOM': ('TL-02', 'grid12', 0, False), 'POWDER ROOM': ('ST-02', 'veins', 0, False),
        'LAUNDRY AND BACK HALL': ('TL-04', 'grid24', 0, False), 'LAUNDRY': ('TL-04', 'grid24', 0, False), 'UTILITY ROOM': ('TL-04', 'grid24', 0, False),
        'STORAGE': ('TL-04', 'grid24', 0, False), 'AHU': ('TL-04', 'grid24', 0, False)},
    2: {'MASTER BEDROOM': ('WD-01', 'herring', 6.0, False), 'HALL': ('WD-01', 'plank', 4.5, False),
        'BEDROOM 2': ('WD-01', 'plank', 0, False), 'BEDROOM 3': ('WD-01', 'plank', 0, False), 'DEN / PLAYROOM': ('WD-01', 'plank', 0, False),
        'W.I.C.': ('WD-01', 'plank', 0, False), 'DEN CLOSET': ('WD-01', 'plank', 0, False), 'LINEN CLOSET': ('WD-01', 'plank', 0, False),
        'SAFE CLOSET': ('WD-01', 'plank', 0, False), 'AHU': ('WD-01', 'plank', 0, False),
        'BATH 2': ('TL-02', 'grid12', 0, False), 'BATH 3': ('TL-02', 'grid12', 0, False),
        'MASTER BATH': ('TL-03', 'grid24x48', 0, False), 'MASTER SHOWER': ('TL-03', 'mosaic', 0, False), 'WATER CLOSET': ('TL-03', 'grid24x48', 0, False)}}

# tag anchors (FOR pt): where each room's field tag sits, and where the border tag points
FIELD_TAG = {1: {'KITCHEN AND DINING': (590, 470), 'LIVING ROOM': (930, 790), 'PANTRY': (437, 576), 'ENTRY': (845, 1225), 'GUEST BEDROOM': (520, 770),
                 'W.I.C.': (556, 893), 'OFFICE': (990, 1395), 'STAIR CLOSET': (1013, 945), 'CLOSET': (700, 1108), 'GUEST BATHROOM': (381, 862),
                 'POWDER ROOM': (983, 1236), 'LAUNDRY AND BACK HALL': (656, 999), 'LAUNDRY': (700, 899), 'UTILITY ROOM': (430, 1030), 'STORAGE': (440, 1110),
                 'AHU': (606, 1108)},
             2: {'MASTER BEDROOM': (870, 1130), 'HALL': (730, 700), 'BEDROOM 2': (600, 600), 'BEDROOM 3': (740, 330), 'DEN / PLAYROOM': (640, 790),
                 'W.I.C.': (610, 1030), 'DEN CLOSET': (494, 668), 'LINEN CLOSET': (930, 945), 'SAFE CLOSET': (1013, 1128), 'AHU': (500, 812),
                 'BATH 2': (512, 386), 'BATH 3': (512, 207), 'MASTER BATH': (660, 1170), 'MASTER SHOWER': (478, 1275), 'WATER CLOSET': (668, 1270)}}
BORDER_TAG = {1: {'KITCHEN AND DINING': (754, 280), 'LIVING ROOM': (900, 560.5)}, 2: {'MASTER BEDROOM': (703, 1150), 'HALL': (700, 520)}}   # a point on the band

TAG_WEST = {(1, 'KITCHEN AND DINING'), (1, 'LAUNDRY')}   # tags whose leader points west (clear of a counter or sink on the east)

WALL = {   # wall tags (paint over crown), FOR's rooms
    1: {'KITCHEN AND DINING': ('PT-02', 'CM-01'), 'LIVING ROOM': ('PT-02', 'CM-02'), 'PANTRY': ('PT-02', 'CM-01'), 'ENTRY': ('PT-01', 'CM-01'),
        'GUEST BEDROOM': ('WC-01', 'CM-01'), 'W.I.C.': ('PT-02',), 'OFFICE': ('PT-02', 'CM-01'), 'STAIR CLOSET': ('PT-02',), 'CLOSET': ('PT-02',),
        'GUEST BATHROOM': ('PT-02', 'CM-01'), 'POWDER ROOM': ('WC-02', 'CM-01'), 'LAUNDRY AND BACK HALL': ('PT-02', 'CM-01'),
        'LAUNDRY': ('PT-02', 'CM-01'), 'UTILITY ROOM': ('FR-01',), 'STORAGE': ('PT-02',), 'AHU': ('PT-02',)},
    2: {'MASTER BEDROOM': ('WP-02', 'CM-01'), 'HALL': ('PT-02', 'CM-01'), 'BEDROOM 2': ('WC-01', 'CM-01'), 'BEDROOM 3': ('WC-01', 'CM-01'),
        'DEN / PLAYROOM': ('PT-02', 'CM-01'), 'W.I.C.': ('PT-02',), 'DEN CLOSET': ('PT-02',), 'LINEN CLOSET': ('PT-02',), 'SAFE CLOSET': ('PT-02',),
        'AHU': ('PT-02',), 'BATH 2': ('PT-02', 'CM-01'), 'BATH 3': ('PT-02', 'CM-01'), 'MASTER BATH': ('PT-02', 'CM-01'), 'WATER CLOSET': ('PT-02', 'CM-01')}}
WALL_TAG = {1: dict(FIELD_TAG[1], **{'LAUNDRY': (700, 904)}), 2: dict(FIELD_TAG[2])}

# special wall finish runs (FOR pt), each a polyline on the wall face, the code, the side the run is offset to (into the room)
SPECIAL = {
    1: [('WS-01', [(1046.2, 628.3), (1016.2, 628.3), (1016.2, 773.8), (1046.2, 773.8)], 'W', (1031, 701)),     # FOR REV 1's fireplace millwork
        ('WP-01', [(1046.2, 555.4), (1046.2, 628.3)], 'W', (1025, 612)), ('WP-01', [(1046.2, 773.8), (1046.2, 846.0)], 'W', (1025, 790)),
        ('WT-01', [(456.7, 815.5), (510.8, 815.5), (510.8, 905.0), (456.7, 905.0)], 'I', (484, 888))],
    2: [('WT-01', [(446.5, 244.6), (446.5, 289.8), (536.0, 289.8), (536.0, 244.6)], 'I', (469, 262)),
        ('WT-01', [(446.5, 342.6), (446.5, 297.2), (536.0, 297.2), (536.0, 342.6)], 'I', (469, 325)),
        ('WT-02', [(511.8, 1205.8), (511.8, 1290.8), (446.5, 1290.8), (446.5, 1205.8)], 'I', (479, 1236)),
        ('WT-02', [(519.5, 1205.8), (519.5, 1290.8), (615.8, 1290.8), (615.8, 1205.8)], 'I', (567, 1268))]}

ELEV_REF = {1: [(640, 300, 'ID-741'), (880, 760, 'ID-751'), (560, 1025, 'ID-761'), (760, 1215, 'ID-771'), (530, 690, 'ID-260')],
            2: [(610, 1185, 'ID-730'), (905, 1045, 'ID-734'), (520, 560, 'ID-340'), (700, 200, 'ID-350')]}   # one marker per key plan sheet

# markers at twice the size do not fit the small rooms at their first spot: placed clear in sheet points, with a leader into the room where needed
REF_PLACE = {(1, 2): ((252.7, 791.4), None), (1, 3): ((436.6, 956.3), None), (2, 0): ((185.3, 908.0), None)}

def ref_marker(sh, cx, cy, sheet, r=18.0, leader=None):
    """One marker per designed room: arrows four ways, the sheet whose key plan carries the room's view markers.
    Owner 11.07.26: twice the first size (r 9 to 18) so it reads on the 11 x 17 print."""
    f = r / 9.0
    if leader:
        lx, ly = leader; d_ = math.hypot(lx - cx, ly - cy); ux, uy = (lx - cx) / d_, (ly - cy) / d_
        sh.line((cx + ux * r, cy + uy * r), (lx, ly), 0.5, INK)
        q = sh.p.new_shape(); q.draw_circle(fitz.Point(lx, ly), 1.6); q.finish(color=INK, fill=INK, width=0.3); q.commit()
    s = sh.p.new_shape(); s.draw_circle(fitz.Point(cx, cy), r); s.finish(color=INK, width=0.8, fill=WHITE); s.commit()
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        tip = fitz.Point(cx + dx * (r + 4.5 * f), cy + dy * (r + 4.5 * f))
        b1 = fitz.Point(cx + dx * r - dy * 2.6 * f, cy + dy * r + dx * 2.6 * f); b2 = fitz.Point(cx + dx * r + dy * 2.6 * f, cy + dy * r - dx * 2.6 * f)
        s = sh.p.new_shape(); s.draw_polyline([b1, tip, b2, b1]); s.finish(color=INK, width=0.3, fill=INK); s.commit()
    sh.text(cx, cy - 1.2 * f, 'SEE', 4.4 * f, INK, align='c', raw=True); sh.text(cx, cy + 5.4 * f, sheet.replace('ID-', ''), 5.2 * f, INK, align='c', raw=True)

OPEN_EDGES = {1: {}, 2: {'HALL': [(695, 640, 695, 830)]}}   # wide openings with no wall: the border stops at the jambs, the field runs through (FOR pt)

NO_TAG = {1: {'STAIR CLOSET', 'CLOSET', 'AHU', 'STORAGE', 'W.I.C.'}, 2: {'DEN CLOSET', 'AHU', 'LINEN CLOSET', 'SAFE CLOSET', 'W.I.C.', 'BATH 2', 'BATH 3', 'WATER CLOSET'}}
NO_FLOOR_TAG = {1: {'STAIR CLOSET', 'CLOSET', 'AHU', 'STORAGE'}, 2: {'DEN CLOSET', 'AHU', 'LINEN CLOSET', 'SAFE CLOSET', 'WATER CLOSET'}}   # closets take the floor of the room they open to

STAIR_CODES = {1: (('WD-01', (930, 1105)), ('ST-01', (1015, 1105))), 2: (('WD-01', (1015, 990)), ('ST-01', (1015, 876)))}

# ------------------------------------------------------------------ legend
FLOOR_LEGEND = {
    1: [('WD-01', 'WOOD FLOORS - FIELD', ['FINISH & SIZE T.B.C.', 'ALSO STAIR TREADS & RISERS, TO MATCH FIELD'], (2, 90.0)),
        ('WD-02', 'WOOD FLOORS - BORDER', ['SINGLE 6" BOARD, FINISH TO MATCH WD-01', 'MITERED CORNERS, CONTINUOUS ACROSS DOORS'], (2, 148.1)),
        ('SL-01', 'SCHLUTER BORDER STRIP', ['SOLID BRASS, FLUSH WITH WOOD', 'FLOOR 1 ONLY'], (2, 206.0)),
        ('TL-01', 'PORCELAIN TILE - ENTRY & PANTRY', ['DARK/MEDIUM GRAY & WHITE', 'CHECKERED PATTERN, SET ON THE DIAGONAL'], (2, 264.0)),
        ('TL-02', 'PORCELAIN TILE - GUEST BATHROOM, BATHS 2 & 3', ['FINISH & SIZE T.B.C.', 'DCOF 0.42 MIN., MOSAIC AT SHOWER FLOORS'], (2, 322.0)),
        ('TL-04', 'PORCELAIN TILE - LAUNDRY, BACK HALL, UTILITY,', ['STORAGE & AHU CLOSET', 'WARM GRAY, 24x24 MATTE, DCOF 0.42 MIN.'], (2, 380.0)),
        ('ST-02', 'MARBLE - POWDER ROOM', ['EMERALD GREEN MARBLE (OPTION)', 'HONED FINISH, T.B.C.'], (2, 438.1)),
        ('ST-01', 'MARBLE - STAIR LANDING AND HEARTH, FLOOR 1', ['HONED FINISH, T.B.C.', 'HEARTH 5\'-6" x 1\'-8", FLUSH WITH THE FLOOR'], (2, 496.0))],
    2: [('WD-01', 'WOOD FLOORS - FIELD', ['FINISH & SIZE T.B.C.', 'HERRINGBONE IN MASTER BEDROOM ONLY, CENTERED ON ROOM', 'STAIR TREADS & RISERS TO MATCH FIELD'], (3, 90.1)),
        ('WD-02', 'WOOD FLOORS - BORDER', ['SINGLE BOARD, FINISH TO MATCH WD-01', '6" AT MASTER BEDROOM, 4-1/2" AT HALL & LANDING', 'NO SCHLUTER STRIP ON FLOOR 2'], (3, 151.6)),
        ('TL-02', 'PORCELAIN TILE - GUEST BATHROOM, BATHS 2 & 3', ['FINISH & SIZE T.B.C.', 'DCOF 0.42 MIN., MOSAIC AT SHOWER FLOORS'], (3, 213.1)),
        ('TL-03', 'PORCELAIN TILE - MASTER BATH', ['FINISH & SIZE T.B.C.', 'DCOF 0.42 MIN., MOSAIC AT SHOWER FLOOR'], (3, 271.1)),
        ('ST-01', 'MARBLE - STAIR LANDING AT FLOOR 2', ['HONED FINISH, T.B.C.'], (3, 329.0))]}
FLOOR_NOTES = [
    'ALL FLOOR FINISHES TO FINISH FLUSH WITH EACH OTHER. BUILD UP SUBFLOOR OR USE LEVELING UNDERLAYMENT AT TILE AREAS AS REQUIRED. NO RAISED THRESHOLDS.',
    'TRANSITIONS CENTERED UNDER DOORS IN THE CLOSED POSITION. FLUSH METAL TRANSITION PROFILE AT ALL WOOD-TO-TILE JOINTS, FINISH TO MATCH SL-01 ON FLOOR 1 AND ADJACENT WOOD ON FLOOR 2.',
    'WOOD FLOORING: GLUE-DOWN INSTALLATION WITH MOISTURE MITIGATION PER MANUFACTURER. ACCLIMATE ON SITE 7 DAYS MIN. RUN FIELD BOARDS IN THE DIRECTION SHOWN.',
    'WD-02 BORDER: SINGLE BOARD, MITERED CORNERS, RUNS CONTINUOUS ACROSS DOOR OPENINGS. FIELD BOARDS STOP AT BORDER. NO BORDER ALONG THE STAIR.',
    'CLOSETS, THE AHU CLOSET, STORAGE AND THE WATER CLOSET TAKE THE FLOOR OF THE ROOM THEY OPEN TO. THE MASTER CLOSET IS STRAIGHT-LAID WD-01.',
    'TILE: DCOF 0.42 MIN. (ANSI A326.3) AT ALL WET AREAS. MOSAIC OR 2x2 AT SHOWER FLOORS. RECTIFIED EDGES, 1/16" JOINTS, GROUT TO MATCH TILE.',
    'SUBMIT SAMPLES AND LAYOUT SHOP DRAWINGS FOR BORDERS AND PATTERNED AREAS BEFORE INSTALLATION.']
WALL_LEGEND = {
    1: [('PT-01', 'PAINT - SW 7005 PURE WHITE', ['CEILINGS (FLAT), UPPER CROWN, CASING, BASE & INTERIOR DOORS (SATIN)', 'ENTRY WALLS (EGGSHELL), PANELING WP-01 (SATIN)'], (4, 90.0)),
        ('PT-02', 'PAINT - SW 5971 SOLSTICE (OPTION 1)', ['WALLS & CROWN MOLDING THROUGHOUT U.N.O., EGGSHELL', 'OPTION 2: SW 9583 SANCTUARY'], (4, 148.0)),
        ('PT-03', 'PAINT - BM 2041-10 HUNTER GREEN', ['POWDER ROOM CEILING, CROWN, BASE, CASING AND DOOR', 'HIGH-GLOSS LACQUER'], (4, 206.0)),
        ('CM-01', 'CROWN MOLDING, 8" BUILT UP', ['PAINTED PT-02, UPPER MEMBER PT-01', 'ALL ROOMS OTHER THAN CLOSETS & MECHANICAL'], (4, 264.0)),
        ('CM-02', 'CROWN MOLDING, 12" BUILT UP - LIVING ROOM', ['THE DOUBLE-HEIGHT VOLUME, PAINTED PT-02, UPPER MEMBER PT-01', 'ELEVATIONS ID-752 TO ID-755'], (4, 264.0)),
        ('WS-01', 'STONE - LIVING ROOM FIREPLACE', ['NATURAL LIGHT MARBLE, HONED, SLAB T.B.C.', 'SURROUND, MANTEL AND BUILT-IN TOPS, ELEVATIONS ID-752, ID-755'], (4, 322.0)),
        ('WP-01', 'PAINTED WOOD PANELING - LIVING ROOM', ['FLANKING THE FIREPLACE, FULL HEIGHT, PAINTED PT-01 SATIN', 'ELEVATIONS ID-752, ID-755'], (4, 380.0)),
        ('WT-01', 'WALL TILE - GUEST BATHROOM, BATHS 2 & 3', ['TUB AND SHOWER ALCOVES, THREE WALLS TO CEILING', 'FINISH & SIZE T.B.C., GROUT TO MATCH, ELEVATIONS ID-262, ID-342, ID-352'], (4, 438.0)),
        ('WC-02', 'WALLCOVERING - POWDER ROOM', ['DARK-GROUND LARGE-SCALE BOTANICAL, METALLIC LINE', 'BASE TO CROWN, ELEVATIONS ID-773'], (4, 496.0)),
        ('WC-01', 'WALLCOVERING - BEDROOMS', ['GUEST BEDROOM (FLOOR 2: BEDROOMS 2 AND 3), ABOVE A PAINTED', 'DADO WAINSCOT, CAP AT 3\'-4", PT-01 SATIN, TO THE CROWN', 'PATTERN T.B.C., ELEVATIONS ID-738A'], (None, 0)),
        ('FR-01', 'FRP PANELS - UTILITY (DOG ROOM)', ['FULL HEIGHT, WHITE PEBBLED, PVC TRIMS, TL-04 COVE BASE', 'OVER MOISTURE-RESISTANT BOARD, ELEVATIONS ID-764'], (None, 0))],
    2: [('PT-01', 'PAINT - SW 7005 PURE WHITE', ['CEILINGS (FLAT), UPPER CROWN, CASING, BASE & INTERIOR DOORS (SATIN)'], (5, 90.0)),
        ('PT-02', 'PAINT - SW 5971 SOLSTICE (OPTION 1)', ['WALLS & CROWN MOLDING THROUGHOUT U.N.O., EGGSHELL', 'OPTION 2: SW 9583 SANCTUARY'], (5, 148.0)),
        ('CM-01', 'CROWN MOLDING, 8" BUILT UP', ['PAINTED PT-02, UPPER MEMBER PT-01', 'ALL ROOMS OTHER THAN CLOSETS & MECHANICAL'], (5, 206.0)),
        ('WC-01', 'WALLCOVERING - BEDROOMS', ['BEDROOMS 2 AND 3 (FLOOR 1: GUEST BEDROOM), ABOVE A PAINTED', 'DADO WAINSCOT, CAP AT 3\'-4", PT-01 SATIN, TO THE CROWN', 'PATTERN T.B.C., ELEVATIONS ID-738B, ID-738C'], (None, 0)),
        ('WP-02', 'PAINTED WOOD PANELING - MASTER BEDROOM', ['FULL-HEIGHT PICTURE-FRAME PANELS, EVERY WALL', 'PAINTED PT-02 SATIN, ELEVATIONS ID-734 TO ID-737'], (5, 264.0)),
        ('WT-01', 'WALL TILE - GUEST BATHROOM, BATHS 2 & 3', ['TUB ALCOVES, THREE WALLS TO CEILING', 'FINISH & SIZE T.B.C., GROUT TO MATCH, ELEVATIONS ID-262, ID-342, ID-352'], (5, 322.0)),
        ('WT-02', 'PORCELAIN SLAB - MASTER BATH', ['48" x 96" x 1/4", HONED', 'SHOWER AND TUB ALCOVE, THREE WALLS EACH, TO CEILING', 'ELEVATIONS ID-731 TO ID-733'], (5, 380.0))]}
WALL_NOTES = [
    'UNLESS NOTED: WALLS PT-02 EGGSHELL, CEILINGS PT-01 FLAT, CROWN PT-02 WITH UPPER MEMBER PT-01, CASING, BASE AND DOORS PT-01 SATIN. CLOSETS, STORAGE AND MECHANICAL PT-02, NO CROWN. BATHS 2 AND 3 AND THE WATER CLOSET PT-02 WITH CM-01.',
    'PAINT: ONE COAT PRIMER AND TWO FINISH COATS MINIMUM. GRILLES, ACCESS PANELS AND ELECTRICAL COVERS ON PAINTED WALLS TO BE PAINTED TO MATCH THE WALL.',
    'HEAVY DASHED LINES SHOW THE RUN OF EACH SPECIAL WALL FINISH IN PLAN. FINISHES RUN FULL HEIGHT, FLOOR TO CEILING, UNLESS NOTED. HEIGHTS, SET-OUTS AND PANEL MODULES PER INTERIOR ELEVATIONS.',
    'WALL TILE AND STONE: MITER OUTSIDE CORNERS, LEVEL SET-OUT FROM FINISHED FLOOR, MOVEMENT JOINTS PER TCNA EJ171, WATERPROOFING AT ALL WET WALLS. SHOP DRAWINGS FOR ALL STONE WALLS.',
    'WOOD PANELING: SHOP DRAWINGS FOR APPROVAL. PANEL MODULE CENTERED ON THE WALL UNLESS NOTED. FINISH SAMPLE APPROVED BEFORE FABRICATION.',
    'PAINT DRAW-DOWNS AND FINISH SAMPLES APPROVED BEFORE ORDERING.']

def wrap(text, size, width):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if FREG.text_length(t, fontsize=size) > width and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

LX0 = 790.0                                    # the legend runs from the plan to the title block in two columns (owner 11.07.26: use the whole sheet)
LX1 = idd_sheet.TB_X - 24.0
LCOL = (LX1 - LX0 - 36.0) / 2
LX2 = LX0 + LCOL + 36.0

def legend(sh, old, rows, title, notes, x=LX0, y=58.0):
    """Column 1: the finish schedule. Column 2: general notes, then the symbols and the scale. Returns the y where column 2 ends."""
    sh.text(x, y + 10.4, title, idd_std.TXT['header'], INK, bold=True, spacing=1.0)
    yy = 92.0; SW = 76.0; PITCH = min(124.0, (1150.0 - 92.0) / len(rows))     # swatches and text sized to fill the column and read on 11 x 17
    for code, head, subs, (pno, sy) in rows:
        if code == 'WC-02':                     # no swatch on the old sheet: a dark botanical ground with a metallic line
            sh.rect((x, yy, x + SW, yy + SW), 0.4, INK, fill=(0.10, 0.17, 0.14))
            for k_ in range(8):
                q = sh.p.new_shape(); q.draw_bezier(fitz.Point(x + 3 + 9.5 * k_, yy + SW - 2), fitz.Point(x + 14 + 9.5 * k_, yy + SW * 0.6), fitz.Point(x - 2 + 9.5 * k_, yy + SW * 0.35), fitz.Point(x + 9 + 9.5 * k_, yy + 2))
                q.finish(color=(0.70, 0.60, 0.36), width=0.7); q.commit()
        elif code == 'WC-01':                   # light ground, small repeat: a wallpaper to pick
            sh.rect((x, yy, x + SW, yy + SW), 0.4, INK, fill=(0.95, 0.94, 0.90))
            for r_ in range(6):
                for c_ in range(6):
                    q = sh.p.new_shape(); q.draw_circle(fitz.Point(x + 7 + 12.4 * c_ + (6 if r_ % 2 else 0), yy + 7 + 12.4 * r_), 1.6); q.finish(color=(0.62, 0.66, 0.60), fill=(0.62, 0.66, 0.60), width=0.2); q.commit()
        elif code == 'FR-01':                   # white pebbled panel with a PVC joint
            sh.rect((x, yy, x + SW, yy + SW), 0.4, INK, fill=(0.97, 0.97, 0.97))
            rnd = random.Random(5)
            for _ in range(140):
                q = sh.p.new_shape(); q.draw_circle(fitz.Point(x + 2 + rnd.random() * (SW - 4), yy + 2 + rnd.random() * (SW - 4)), 0.7); q.finish(color=(0.80, 0.80, 0.80), fill=(0.80, 0.80, 0.80), width=0.1); q.commit()
            sh.line((x + SW / 2, yy), (x + SW / 2, yy + SW), 0.8, (0.75, 0.75, 0.75))
        else:
            pix = old[pno].get_pixmap(dpi=300, clip=fitz.Rect(790, sy, 834, sy + 44))
            sh.p.insert_image(fitz.Rect(x, yy, x + SW, yy + SW), pixmap=pix)
            sh.rect((x, yy, x + SW, yy + SW), 0.3, LIGHT)
        tx = x + SW + 16; tw = LX0 + LCOL - tx
        hz = 12.0
        while FREG.f.text_length(code + '  ' + head, fontsize=hz) > tw and hz > 9: hz -= 0.25
        sh.text(tx, yy + 13, code + '  ' + head, hz, INK, raw=True)
        for i, s_ in enumerate(subs):
            sz = 10.0
            while FREG.f.text_length(s_, fontsize=sz) > tw and sz > 7.5: sz -= 0.25
            sh.text(tx, yy + 31 + 14 * i, s_, sz, MID, raw=True)
        yy += PITCH
    assert yy < 1180, ('schedule runs off the sheet', yy)
    sh.line((LX2 - 18, 76), (LX2 - 18, 1170), 0.4, LIGHT)
    x2 = LX2; yy = y + 10.4
    sh.text(x2, yy, 'GENERAL NOTES', idd_std.TXT['header'], INK, bold=True, spacing=1.0); yy = 92.0 + 13
    for i, n in enumerate(notes):
        ls = wrap_raw(n, 10.0, LCOL - 20)
        sh.text(x2, yy, f'{i + 1}.', 10.0, INK, raw=True)
        for l in ls: sh.text(x2 + 20, yy, l, 10.0, INK, raw=True); yy += 14
        yy += 6
    return yy

def wrap_raw(text, size, width):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if FREG.f.text_length(t, fontsize=size) > width and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def scale_block(sh, y):
    """The graphic scale, in the notes column with room around it (owner 11.07.26: not squeezed against the plan or the frame)."""
    sh.line((LX2, y), (LX1, y), 0.4, LIGHT); y += 30
    sh.text(LX2, y, 'GRAPHIC SCALE (SEE TITLE BLOCK)', idd_std.TXT['header'], INK, bold=True, spacing=1.0); y += 34
    k = 13.5; x = LX2 + 4                                   # 3/16" TO 1'-0": 13.5 pt per foot, 20 ft shown
    for i in range(20):
        fillc = INK if i % 2 == 0 else (1, 1, 1)
        if i >= 10 and i % 5: continue
        w_ = k if i < 10 else 5 * k
        sh.rect((x + i * k, y - 6, x + i * k + w_, y), 0.4, INK, fillc if i < 10 else ((1, 1, 1) if i == 10 else INK))
    for ft in (0, 5, 10, 15, 20): sh.text(x + ft * k, y + 14, f"{ft}'", 9.0, INK, align='c', raw=True)
    sh.text(x + 20 * k + 18, y - 0.5, '3/16" TO 1\'-0" ON THE FULL-SIZE SHEET. USE THE BAR ON THE 11 x 17 PRINT.', 9.0, MID, raw=True) if False else sh.text(x + 20 * k + 18, y - 0.5, '3/16" TO 1\'-0"', 10.0, INK, raw=True)
    return y + 30


ROOM_SHEET = {1: {'KITCHEN AND DINING': 'ID-240', 'PANTRY': 'ID-240', 'LIVING ROOM': 'ID-230', 'ENTRY': 'ID-210', 'POWDER ROOM': 'ID-210',
                  'GUEST BEDROOM': 'ID-260', 'GUEST BATHROOM': 'ID-260', 'LAUNDRY AND BACK HALL': 'ID-250', 'LAUNDRY': 'ID-250',
                  'UTILITY ROOM': 'ID-250', 'OFFICE': 'ID-220 TBD'},
              2: {'MASTER BEDROOM': 'ID-310', 'MASTER BATH': 'ID-320', 'MASTER SHOWER': 'ID-320', 'WATER CLOSET': 'ID-320',
                  'BEDROOM 2': 'ID-340', 'BATH 2': 'ID-340', 'BEDROOM 3': 'ID-350', 'BATH 3': 'ID-350', 'DEN / PLAYROOM': 'ID-360 TBD',
                  'HALL': 'ID-370 TBD', 'LINEN CLOSET': 'ID-370 TBD', 'W.I.C.': 'ID-330 TBD'}}
SPECIAL_BY_ROOM = {1: {'LIVING ROOM': 'WS-01, WP-01', 'GUEST BATHROOM': 'WT-01', 'GUEST BEDROOM': 'DADO PT-01'}, 2: {'BATH 2': 'WT-01', 'BATH 3': 'WT-01', 'MASTER BATH': 'WT-02', 'BEDROOM 2': 'DADO PT-01', 'BEDROOM 3': 'DADO PT-01'}}
ROOM_NAME = {'UTILITY ROOM': 'UTILITY (DOG ROOM)', 'W.I.C.': 'W.I.C.'}

def room_schedule(sh, x, y, width, fl, kind):
    """Room finish schedule: what each room gets, read with the plan. kind 'floor' or 'wall'."""
    sh.text(x, y, 'ROOM FINISH SCHEDULE', idd_std.TXT['header'], INK, bold=True, spacing=1.0); y += 24
    if kind == 'floor':
        cols = [('ROOM', 0.0), ('FLOOR', 0.37), ('BORDER', 0.66), ('STRIP', 0.87)]
        rows = []
        for name, (code, pat, bw, strip) in FLOOR[fl].items():
            if name in ('MASTER SHOWER',): continue
            b = ('WD-02, %s"' % ('6' if bw == 6.0 else '4-1/2')) if bw else '-'
            rows.append((ROOM_NAME.get(name, name), code + (' HERRINGBONE' if pat == 'herring' else ''), b, 'SL-01' if strip else '-'))
    else:
        cols = [('ROOM', 0.0), ('WALLS', 0.40), ('CROWN', 0.56), ('SPECIAL', 0.70), ('ELEVATIONS', 0.86)]
        rows = []
        for name, codes in WALL[fl].items():
            crown = next((c for c in codes if c.startswith('CM')), '-'); walls = codes[0]
            el = ROOM_SHEET[fl].get(name, '-').replace(' TBD', '')
            rows.append((ROOM_NAME.get(name, name), walls, crown, SPECIAL_BY_ROOM[fl].get(name, '-'), el + (' TBD' if 'TBD' in ROOM_SHEET[fl].get(name, '') else '')))
    for lab_, f_ in cols: sh.text(x + f_ * width, y, lab_, 8.0, MID, spacing=0.6, raw=True)
    y += 6; sh.line((x, y), (x + width, y), 0.5, INK); y += 15
    for r in rows:
        for (lab_, f_), v in zip(cols, r):
            w_ = width * ((cols[cols.index((lab_, f_)) + 1][1] if (lab_, f_) != cols[-1] else 1.0) - f_) - 6; sz = 9.5
            while FREG.f.text_length(v, fontsize=sz) > w_ and sz > 7.5: sz -= 0.25
            sh.text(x + f_ * width, y, v, sz, INK if 'TBD' not in v else MID, raw=True)
        y += 5; sh.line((x, y), (x + width, y), 0.3, LIGHT); y += 12.5
    return y

def place_room_schedule(sh, fl, kind, y1, y2):
    """The room finish schedule goes under whichever legend column ends higher, ruled off from it."""
    if y1 <= y2: x, y = LX0, y1
    else: x, y = LX2, y2
    sh.line((x, y + 6), (x + LCOL, y + 6), 0.4, LIGHT)
    yend = room_schedule(sh, x, y + 34, LCOL, fl, kind)
    assert yend < 1180, ('room schedule runs off the sheet', fl, kind, yend)

def place_base(sh, floor):
    src = fitz.open(BASE); pno = floor - 1; sp = src[pno]; dx, dy = SHIFT[floor]
    clip_disp = fitz.Rect(20 + dx, 72 + dy, 715 + dx, 1160 + dy)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    sh.p.show_pdf_page(TARGET, src, pno, clip=u, rotate=90)
    xref = sh.p.get_contents()[-1]; st = sh.p.parent.xref_stream(xref).decode('latin1')
    t = TARGET; H = sh.p.rect.height
    parts = st.split('q ')
    for i in range(1, len(parts)):
        if 'Do' in parts[i] and ' re W n ' not in parts[i][:80]:
            parts[i] = f'{t.x0:.2f} {H - t.y1:.2f} {t.width:.2f} {t.height:.2f} re W n ' + parts[i]
    sh.p.parent.update_stream(xref, 'q '.join(parts).encode('latin1'))

def run(sh, pts, side, f, code, tag_at):
    """A special wall finish run: heavy dashed line 2 pt into the room from the face, ticks at both ends, its tag."""
    P = [f(*q) for q in pts]
    ls = LineString(P)
    off = ls.parallel_offset(2.2, 'left' if side == 'W' else 'left', join_style=2)
    # choose the offset side that lies toward the tag point (the room)
    cand = [ls.parallel_offset(2.2, s, join_style=2) for s in ('left', 'right')]
    tp = Point(f(*tag_at)); off = min(cand, key=lambda g: g.distance(tp))
    c = list(off.coords) if off.geom_type == 'LineString' else [q for g in off.geoms for q in g.coords]
    if c and Point(c[0]).distance(Point(P[0])) > Point(c[-1]).distance(Point(P[0])): c = c[::-1]
    sh.polyline(c, 1.3, INK, dashes='[4 2] 0', close=False)
    for end, nxt in ((c[0], c[1]), (c[-1], c[-2])):
        vx, vy = nxt[0] - end[0], nxt[1] - end[1]; L = math.hypot(vx, vy) or 1; nx, ny = -vy / L, vx / L
        sh.line((end[0] - nx * 3, end[1] - ny * 3), (end[0] + nx * 3, end[1] + ny * 3), 0.8, INK)
    tx, ty = f(*tag_at); sh.tag(tx, ty, code, lead=0, sides='')

def build():
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    idd_sheet.EXTRA_REVS[:] = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', '11.06.26', 'POWDER ROOM WALLCOVERING')]
    old = fitz.open(OLD); doc = fitz.open()
    marks = json.load(open(MARKS))
    rooms = {fl: RR.rooms(fl) for fl in (1, 2)}
    global TH
    TH = {fl: {k: geom_to_sheet(g, to_sheet(fl)) for k, g in RR.thresholds(fl).items()} for fl in (1, 2)}
    for fl in (1, 2):
        f = to_sheet(fl)
        R = {k: geom_to_sheet(g, f) for k, g in rooms[fl].items()}
        treads = unary_union([rect_sheet(r, f) for r in RR.STAIRS[fl]['treads']]); landing = unary_union([rect_sheet(r, f) for r in RR.STAIRS[fl]['landing']])
        stair = unary_union([treads, landing])
        # ---------------- floor finish plan
        sh = Sheet(doc)
        sh.frame('FLOORING PLAN - FLOOR %d' % fl, 'SCALE: 3/16" TO 1\'-0"', ['FLOORING PLAN', 'FLOOR %d' % fl], 'ID-10%d' % fl, legend_header='FLOOR FINISH SCHEDULE' if False else None)
        for name, (code, pat, bw, strip) in FLOOR[fl].items():
            g = R[name].difference(stair) if name in ('LIVING ROOM', 'HALL') else R[name]
            opn = unary_union([stair] + [LineString([f(c[0], c[1]), f(c[2], c[3])]) for c in OPEN_EDGES[fl].get(name, [])])
            field = band(sh, g, bw, strip=strip, open_=opn) if bw else g
            if name in TH[fl]: field = unary_union([field, TH[fl][name].difference(stair)])
            for c in OPEN_EDGES[fl].get(name, []):     # close the hairline between the two rooms' fields at a wide opening
                field = unary_union([field, LineString([f(c[0], c[1]), f(c[2], c[3])]).buffer(1.6, cap_style=2)])
            seed = sum(map(ord, name))
            if pat == 'plank': planks(sh, field, seed)
            elif pat == 'herring': herringbone(sh, field)
            elif pat == 'checker': checker_diag(sh, field)
            elif pat == 'grid12': grid(sh, field, 12, 24)
            elif pat == 'grid24': grid(sh, field, 24, 24)
            elif pat == 'grid24x48': grid(sh, field, 24, 48)
            elif pat == 'mosaic': grid(sh, field, 2, 2, (0.82, 0.82, 0.82), 0.2)
            elif pat == 'veins': veins(sh, field, seed)
        fill(sh, treads, (0.93, 0.93, 0.93))          # WD-01 treads, both flights (nosings come from the base)
        veins(sh, landing, 7, 3)
        place_base(sh, fl)
        for name, (code, pat, bw, strip) in FLOOR[fl].items():
            if name in NO_FLOOR_TAG[fl]: continue
            if (fl, name) == (1, 'POWDER ROOM'):          # too small for its tag: tagged outside the east wall with a leader
                sh.line((604, 942), (686, 942), 0.5, INK); q_ = sh.p.new_shape(); q_.draw_circle(fitz.Point(604, 942), 1.6); q_.finish(color=INK, fill=INK, width=0.3); q_.commit()
                sh.tag(708, 942, code, lead=0, sides=''); continue
            x, y = f(*FIELD_TAG[fl][name]); sh.tag(x, y, code, lead=6.0, sides='l' if (fl, name) in TAG_WEST else 'r')
        for name, (x, y) in BORDER_TAG[fl].items():
            X, Y = f(x, y); codes = ['WD-02', 'SL-01'] if fl == 1 else ['WD-02']
            if (fl, name) in TAG_WEST: sh.tag_stack(X - 22, Y + 9, codes, lead=8.0, sides='r')
            else: sh.tag_stack(X + 22, Y + 9, codes, lead=8.0, sides='l')
        for code, (x, y) in STAIR_CODES[fl]: X, Y = f(x, y); sh.tag(X, Y, code, lead=0, sides='')
        if fl == 2: X, Y = f(730, 700); sh.text(X, Y - 15, 'HALL', 7.5, INK, align='c', raw=True)     # FOR leaves the hall unnamed
        if fl == 1:                                      # the fireplace hearth, ST-01 flush, 5'-6" x 1'-8" in front of the breast
            a_, b_ = f(986.2, 651.5), f(1016.2, 750.5); hr = fitz.Rect(min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1]))
            sh.rect(hr, 0.6, INK, fill=(1, 1, 1))
            k_ = hr.x0 - hr.height
            while k_ < hr.x1:
                p0 = fitz.Point(max(k_, hr.x0), hr.y1 - (max(k_, hr.x0) - k_)); p1 = fitz.Point(min(k_ + hr.height, hr.x1), hr.y1 - (min(k_ + hr.height, hr.x1) - k_))
                sh.line(p0, p1, 0.25, LIGHT); k_ += 6
            sh.tag((hr.x0 + hr.x1) / 2, (hr.y0 + hr.y1) / 2, 'ST-01', lead=0, sides='')
        yy = legend(sh, old, FLOOR_LEGEND[fl], 'FLOOR FINISH SCHEDULE', FLOOR_NOTES)
        y2 = scale_block(sh, yy + 14); place_room_schedule(sh, fl, 'floor', 92.0 + len(FLOOR_LEGEND[fl]) * min(124.0, (1150.0 - 92.0) / len(FLOOR_LEGEND[fl])), y2)
        # ---------------- wall finish plan
        sh = Sheet(doc)
        sh.frame('WALL FINISH PLAN - FLOOR %d' % fl, 'SCALE: 3/16" TO 1\'-0"', ['WALL FINISH PLAN', 'FLOOR %d' % fl], 'ID-11%d' % fl)
        place_base(sh, fl)
        for name, codes in WALL[fl].items():
            if name in NO_TAG[fl]: continue
            if (fl, name) == (1, 'POWDER ROOM'):          # too small for its tag: tagged from the entry with a leader
                sh.line((604, 942), (686, 942), 0.5, INK); q_ = sh.p.new_shape(); q_.draw_circle(fitz.Point(604, 942), 1.6); q_.finish(color=INK, fill=INK, width=0.3); q_.commit()
                sh.tag_stack(708, 942, list(codes), lead=0, sides=''); continue
            x, y = f(*WALL_TAG[fl][name]); sh.tag_stack(x, y, list(codes), lead=0, sides='')
        for code, pts, side, tag_at in SPECIAL[fl]: run(sh, pts, side, f, code, tag_at)
        if fl == 2: X, Y = f(730, 700); sh.text(X, Y - 15, 'HALL', 7.5, INK, align='c', raw=True)
        for i_, (x, y, sheet) in enumerate(ELEV_REF[fl]):
            if (fl, i_) in REF_PLACE: (X, Y), ld = REF_PLACE[(fl, i_)]
            else: (X, Y), ld = f(x, y), None
            ref_marker(sh, X, Y, sheet, leader=ld)
        yy = legend(sh, old, WALL_LEGEND[fl], 'WALL FINISH SCHEDULE', WALL_NOTES)
        x2 = LX2; sh.line((x2, yy + 8), (LX1, yy + 8), 0.4, LIGHT)
        yy += 30; sh.text(x2, yy, 'SYMBOLS', idd_std.TXT['header'], INK, bold=True, spacing=1.0); yy += 26
        sh.tag_stack(x2 + 13, yy + 4, ['PT-02', 'CM-01'], lead=0, sides='')
        sh.text(x2 + 56, yy + 3, 'WALL FINISH OVER CROWN. APPLIES TO EVERY WALL OF THE ROOM.', 10.0, INK, raw=True); yy += 34
        sh.line((x2 + 2, yy), (x2 + 26, yy), 1.3, INK, dashes='[4 2] 0'); sh.text(x2 + 56, yy + 3.5, 'EXTENT OF A SPECIAL WALL FINISH.', 10.0, INK, raw=True); yy += 40
        ref_marker(sh, x2 + 22, yy, 'ID-240' if fl == 1 else 'ID-310'); sh.text(x2 + 56, yy + 3.5, 'ROOM ELEVATIONS: SEE THE KEY PLAN ON THE SHEET SHOWN.', 10.0, INK, raw=True); yy += 38
        y2 = scale_block(sh, yy); place_room_schedule(sh, fl, 'wall', 92.0 + len(WALL_LEGEND[fl]) * min(124.0, (1150.0 - 92.0) / len(WALL_LEGEND[fl])), y2)
    # floor 1: FOR's south kitchen run (built-in oven, bar) is replaced by the kitchen cabinetry on ID-741
    for i in (0, 1):
        pg = doc[i]
        pg.add_redact_annot(fitz.Rect(195.0, 415.5, 319.6, 441.0))      # FOR's built-in oven and bar labels go, not just covered (searchable text)
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        pg.draw_rect(fitz.Rect(193.6, 409.5, 321.0, 442.2), color=None, fill=(1, 1, 1), overlay=True)
        pg.draw_rect(fitz.Rect(193.5, 414.2, 321.1, 442.3), color=INK, width=0.5, overlay=True)
        sh_ = Sheet.__new__(Sheet); sh_.p = pg; sh_.font, sh_.fontname = FREG, 'cg'
        if 'cg' not in [x_[4] for x_ in pg.get_fonts()]: pg.insert_font(fontname='cg', fontbuffer=idd_sheet.REG_BUF)
        sh_.text(257.3, 431.5, 'CABINETRY, SEE ID-741', 7.0, MID, align='c', raw=True)
        sh_.text(147.0, 393.0, 'KITCHEN LAYOUT, RANGE', 7.0, MID, align='l', raw=True); sh_.text(147.0, 402.5, 'AND WINDOWS PER ID-741', 7.0, MID, align='l', raw=True)
    doc.select([0, 2, 1, 3])                    # ID-101, ID-102, ID-201, ID-202
    fix_soft_hyphen(doc)
    doc.set_metadata({'title': 'Casa Grove ID-101, ID-102, ID-201, ID-202 on FOR REV 1', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
