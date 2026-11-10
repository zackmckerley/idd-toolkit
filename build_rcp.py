"""Reflected ceiling plans and lighting plans, coordinated with FOR's Rev 1 set (owner 11.09.26: "Did you add RCPs with lighting?").

ID-121 / ID-122  REFLECTED CEILING PLAN, FLOOR 1 / FLOOR 2
ID-131 / ID-132  LIGHTING AND SWITCHING PLAN, FLOOR 1 / FLOOR 2
ID-406           POOL HOUSE RCP AND LIGHTING

Base: the same neutral base, scale (3/16") and sheet position as ID-101 / ID-102 (build_finish_rev1.place_base), so the sheets overlay.
FOR's ceiling and lighting content comes from A-205 / A-206 (vector), moved onto our sheet: plan = RCP display + OFFSET (phase correlation of
the two wall masks: RCP sheets sit about 209 pt left of the plan sheets). A-206 carries layers (L-RECESS, L-PENDENT, ...); A-205 has none, so
each A-205 path is classed by the signature of the same symbol on A-206's layers. Ours is drawn over it: ceiling heights and zones from
coord/heights.json, crown and the LED cove (owner: crown stays, LED cove on top where FOR shows cove, 4/ID-502), soffits (1/ID-501), and the
wall lights our elevations add or change (FOR's that ours replaces are left out)."""
import sys, re, glob, json, math, collections
sys.path[:0] = ['/home/claude/flrwork', '/home/claude/flrwork/rev1']
import pymupdf as fitz
from shapely.geometry import Point, box, Polygon, LineString
from shapely.ops import unary_union, polylabel
import build_finish_rev1 as FN
import idd_std, idd_sheet
from idd_sheet import Sheet, fix_soft_hyphen, FREG
from idd_std import INK, MID, LIGHT

OUT = '/home/claude/flrwork/261109.HD102.RCP-Lighting.pdf'
D = '/tmp/coord/for/REV 1_3350 Thomas Ave_SS Permit Set/ARCHITECTURE S&S/'
SRC = {1: 'A-205', 2: 'A-206'}
OFFSET = {1: (208.1, 0.8), 2: (209.2, 1.1)}          # FOR plan pt = FOR RCP display pt + OFFSET
GREY = (0.62, 0.62, 0.62); DARKG = (0.35, 0.35, 0.35); WHITE = (1, 1, 1)
LX0, LX1, LX2 = FN.LX0, FN.LX1, FN.LX2

# ------------------------------------------------------------------ FOR content
CLASS = {'L-RECESS': 'recess', 'L-PENDENT': 'pendant', 'L- WALL WASHER': 'washer', 'L- WALL SCONCE': 'sconce', 'L-SCONCE (DASH)': 'sconce',
         'L-OUTLET': 'outlet', 'TRAZZO LUCES - EQUIPOS 3': 'tray', 'TRAZZO LUCES - EQUIPOS 13': 'tray',      # TRAZZO = FOR's ceiling linework, not switches
         'RCP-proposed|TRAZZO LUCES - EQUIPOS 3': 'tray', 'RCP-proposed|TRAZZO LUCES - EQUIPOS 13': 'tray',
         'RCP-proposed|SWITCH-SYMBOL': 'switch', 'RCP-proposed|L-1 Lights': 'strip', 'A-OVERHEAD': 'ceiling', 'A-CLNG-PATT': 'ceiling',
         'RCP-proposed|A-ANNO-SYMB': 'anno', 'A-ANNO-SYMB': 'anno', 'A-SYMBOL': 'anno'}

def page(fl):
    return fitz.open(glob.glob(D + SRC[fl] + '_*')[0])[0]

def sig(d, M):
    its = d['items']; r = d['rect'] * M
    return (''.join(sorted(set(i[0] for i in its))), len(its), round(r.width * 2) / 2, round(r.height * 2) / 2, round(d.get('width') or 0, 2), d['type'], bool(d.get('fill')))

_SIGMAP = None
def sigmap():
    """signature -> class, from A-206's lighting layers (most common class per signature)."""
    global _SIGMAP
    if _SIGMAP is None:
        p = page(2); M = p.rotation_matrix; c = collections.defaultdict(collections.Counter)
        for d in p.get_drawings():
            k = CLASS.get(d.get('layer') or '')
            if k and k not in ('ceiling', 'anno', 'tray', 'switch'): c[sig(d, M)][k] += 1
        _SIGMAP = {s: v.most_common(1)[0][0] for s, v in c.items()}
    return _SIGMAP

def for_items(fl):
    """[(class, drawing, center_plan)] for FOR's lighting content on floor fl, in FOR plan coordinates."""
    p = page(fl); M = p.rotation_matrix; ox, oy = OFFSET[fl]; sm = sigmap(); out = []
    for d in p.get_drawings():
        r = d['rect'] * M; c = ((r.x0 + r.x1) / 2 + ox, (r.y0 + r.y1) / 2 + oy)
        if fl == 2: k = CLASS.get(d.get('layer') or '')
        else:
            k = sm.get(sig(d, M))
            if k is None and d.get('dashes') not in (None, '[] 0', '') and d['type'] == 's' and max(r.width, r.height) > 30: k = 'dashed'
        q = (r.x0 + ox, r.y0 + oy, r.x1 + ox, r.y1 + oy)
        if d['type'] == 's' and d.get('dashes') in (None, '[] 0') and any(all(abs(a - b) < 2.0 for a, b in zip(q, t)) for t in TRAY[fl]): k = 'tray'
        if k: out.append((k, d, c, r))
    return out

def for_words(fl):
    p = page(fl); M = p.rotation_matrix; ox, oy = OFFSET[fl]; out = []
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                t = s['text'].strip()
                if not t: continue
                o = fitz.Point(s['origin']) * M
                out.append((t, (o.x + ox, o.y + oy), s['size'], l['dir']))
    return out

def mapper(fl):
    f = FN.to_sheet(fl); p = page(fl); M = p.rotation_matrix; ox, oy = OFFSET[fl]
    def T(pt):
        q = fitz.Point(pt) * M; return fitz.Point(*f(q.x + ox, q.y + oy))
    return T, f

def draw_for(sh, d, T, color, scale=0.75):
    s = sh.p.new_shape()
    for it in d['items']:
        k = it[0]
        if k == 'l': s.draw_line(T(it[1]), T(it[2]))
        elif k == 'c': s.draw_bezier(T(it[1]), T(it[2]), T(it[3]), T(it[4]))
        elif k == 're':
            r = it[1]; q = [T(r.tl), T(r.tr), T(r.br), T(r.bl)]; s.draw_polyline(q + [q[0]])
        elif k == 'qu':
            q = it[1]; pts = [T(q.ul), T(q.ur), T(q.lr), T(q.ll)]; s.draw_polyline(pts + [pts[0]])
    fill = color if d.get('fill') else None
    w = max(0.25, (d.get('width') or 0.5) * scale) if d['type'] != 'f' else 0
    dash = d.get('dashes') if d.get('dashes') not in (None, '[] 0') else None
    s.finish(color=color if d['type'] != 'f' else None, fill=fill, width=w, dashes=dash, closePath=bool(d.get('closePath')))
    s.commit()

ESRC = {1: 'E-300', 2: 'E-301'}
EDIR = '/tmp/coord/for/REV 1_3350 Thomas Ave_SS Permit Set/MEP S&S/'
TRAY = {1: [(374, 668, 601, 787), (754, 1170, 935, 1252), (914, 1277, 1028, 1424)],          # FOR's tray (band) edges, FOR plan pt
        2: [(562, 155, 747, 357), (472, 475, 674, 620), (708, 928, 1038, 1207), (784, 573, 1029, 826)]}

def epage(fl):
    return fitz.open(EDIR + ESRC[fl] + '.pdf')[0]

def e_delta(fl):
    """E-300 / E-301 display pt -> A-205 / A-206 display pt: the median offset of the matched L1 tags (same sheet layout)."""
    a, e = page(fl), epage(fl)
    def pts(p):
        M = p.rotation_matrix; return [fitz.Point(w[0], w[1]) * M for w in p.get_text('words') if w[4] == 'L1']
    A, E_ = pts(a), pts(e); c = collections.Counter()
    for x in A:
        for y in E_: c[(round(x.x - y.x), round(x.y - y.y))] += 1
    (dx, dy), _n = c.most_common(1)[0]
    ds = [(x.x - y.x, x.y - y.y) for x in A for y in E_ if abs(x.x - y.x - dx) < 1.5 and abs(x.y - y.y - dy) < 1.5]
    ds.sort(); mx = sorted(d[0] for d in ds)[len(ds) // 2]; my = sorted(d[1] for d in ds)[len(ds) // 2]
    return mx, my

def e_switches(fl):
    """FOR's switches from E-300 / E-301: each S glyph (a 20-segment path at 1.08 pt) with the small strokes and subscripts around it.
    Returns [(center_plan, [drawings], [(text, plan pt, size)])] in FOR plan coordinates, plus the E display -> plan offset."""
    p = epage(fl); M = p.rotation_matrix; dx, dy = e_delta(fl); ox, oy = OFFSET[fl]; dr = p.get_drawings()
    small = []
    for d in dr:
        r = d['rect'] * M
        if max(r.width, r.height) <= 9.2 and d.get('dashes') in (None, '[] 0') and (d.get('width') or 0) <= 1.1: small.append((d, r))
    words = [(fitz.Rect(w[:4]) * M, w[4]) for w in p.get_text('words')]
    out = []
    for d, r in small:
        if len(d['items']) != 20 or abs((d.get('width') or 0) - 1.08) > 0.01 or not (5.8 <= r.width <= 8.8 and 5.8 <= r.height <= 8.8): continue
        c = fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        win = fitz.Rect(c.x - 7, c.y - 9, c.x + 9, c.y + 9)
        cl = [dd for dd, rr in small if win.contains((rr.tl + rr.br) / 2)]
        tx = [(t, (rr.x0 + dx + ox, rr.y1 + dy + oy), rr.height) for rr, t in words if win.intersects(rr) and re.fullmatch(r'(3|4|D|3D|WP|M|K|LV|P|T)+', t)]
        out.append(((c.x + dx + ox, c.y + dy + oy), cl, tx))
    return out, (dx + ox, dy + oy)

# ------------------------------------------------------------------ our data
COVE = {1: ['ENTRY', 'OFFICE', 'GUEST BEDROOM'], 2: ['BEDROOM 2', 'BEDROOM 3', 'MASTER BEDROOM']}       # FOR's L11 / L12 coves -> CM-01 + LED cove
CROWN = {1: ['KITCHEN AND DINING', 'PANTRY', 'LIVING ROOM', 'GUEST BATHROOM', 'LAUNDRY AND BACK HALL', 'LAUNDRY', 'POWDER ROOM'],
         2: ['BATH 2', 'BATH 3', 'DEN / PLAYROOM', 'HALL', 'MASTER BATH']}
CEIL = {1: {'KITCHEN AND DINING': ("10'-4\"", None), 'PANTRY': ("10'-8\"", None), 'LIVING ROOM': ("10'-8\"", None),
            'GUEST BEDROOM': ("10'-8\"", "10'-4\" BAND"), 'GUEST BATHROOM': ("10'-8\"", None), 'W.I.C.': ("10'-8\"", None),
            'LAUNDRY AND BACK HALL': ("10'-8\"", None), 'LAUNDRY': ("10'-8\"", None), 'UTILITY ROOM': ("10'-8\"", None),
            'STORAGE': ("10'-8\"", None), 'CLOSET': ("10'-8\"", None), 'ENTRY': ("10'-8\"", "10'-4\" BAND"), 'POWDER ROOM': ("10'-8\"", None),
            'OFFICE': ("10'-8\"", "10'-4\" BAND")},
        2: {'BATH 3': ("9'-10\"", None), 'BATH 2': ("9'-10\"", None), 'BEDROOM 3': ("9'-10\"", "9'-6\" BAND"), 'BEDROOM 2': ("9'-10\"", "9'-6\" BAND"),
            'DEN / PLAYROOM': ("9'-10\"", None), 'HALL': ("9'-6\"", None), 'W.I.C.': ("9'-6\"", None), 'MASTER BATH': ("9'-10\"", None),
            'MASTER BEDROOM': ("9'-10\"", "9'-6\" BAND")}}
TAG_AT = {(1, 'LIVING ROOM'): (690, 640)}
SMALL = {}           # rooms too small for a tag: covered by a note            # room -> FOR plan pt override for the ceiling tag (filled after the first look)
NO_FOR_SCONCE = {1: ['POWDER ROOM', 'GUEST BATHROOM'], 2: ['BATH 2', 'BATH 3']}        # vanity sconces replaced by our LED mirror / linear sconce
VOID_2 = (774, 568, 1046, 832)
VOID_TXT = (528.5, 552.0)                 # sheet pt: center of FOR's open-to-above cross on the floor 1 base
AP = (622.8, 956.0, 682.8, 992.0)         # 40" x 24" dehumidifier access panel (M-100), FOR plan pt: just north of the second L3 from the east, clear of it        # the living room's open-to-above, FOR plan pt on floor 2

def our_lights(fl):
    """(type, kind, FOR plan geometry, label side). kind: 'sconce' point on a wall with a wall direction, 'line' run, 'mirror' run."""
    if fl == 1:
        return [('LS1', 'sconce_line', ((1044, 1193), (1044, 1217)), 'POWDER ROOM: 24" LINEAR SCONCE OVER THE MIRROR, CL 8\'-9" (ID-212)'),
                ('LM1', 'mirror', ((366, 903), (392, 903)), 'GUEST BATH: BACKLIT LED MIRROR (ID-262)'),
                ('LS2', 'line', ((360, 216), (360, 330)), None), ('LS2', 'line', ((360, 383), (360, 497)), 'RANGE WALL: LED UNDER THE STONE SHELVES (ID-241)'),
                ('LS2', 'line', ((398, 176), (428, 176)), None), ('LS2', 'line', ((596, 176), (626, 176)), 'END PANTRIES: IN-CABINET LED, GLASS SHELVES (ID-241)'),
                ('LS2', 'line', ((560, 535), (630, 535)), 'SOUTH RUN: LED UNDER THE STONE SHELVES (ID-242)'),
                ('LS2', 'line', ((362, 556), (362, 634)), None), ('LS2', 'line', ((610, 556), (610, 616)), None),
                ('LS2', 'line', ((382, 630), (594, 630)), 'PANTRY: LED IN THE GLASS UPPERS\' TOP RAILS, THREE WALLS (ID-244)')]
    return [('LM1', 'mirror', ((448, 154), (448, 178)), 'BATH 3: BACKLIT LED MIRROR (ID-352)'),
            ('LM1', 'mirror', ((448, 415), (448, 439)), 'BATH 2: BACKLIT LED MIRROR (ID-342)'),
            ('SC1', 'sconce', None, 'MASTER BEDROOM: SC1 IN THE NARROW PANELS 1\'-1" FROM EACH CORNER OF THE HEADBOARD WALL (ID-312)'),
            ('SC1', 'sconce', None, 'MASTER BATH: SC1 EACH SIDE OF BOTH MIRRORS, 6" OUTSIDE THEM, CL 5\'-6" (ID-321)'),
            ('LS2', 'line', ((905, 1226), (905, 1281)), 'MASTER NOOK: LED UNDER THE BOOKCASE ARCH, TOUCH DIMMER IN THE HEAD, DRIVER IN THE CABINET (ID-313)'),
            # master W.I.C. (ID-330 to 333): LED at every shelf front and in the showcase, the run fronts in closet inches x 1.5 from (446.1, 832.0)
            ('LS2', 'line', ((482.1, 868.0), (654.0, 868.0)), None), ('LS2', 'line', ((482.1, 868.0), (482.1, 930.1)), None),
            ('LS2', 'line', ((482.1, 1002.1), (482.1, 1064.2)), None), ('LS2', 'line', ((654.0, 868.0), (654.0, 1064.2)), 'MASTER W.I.C.: LED AT EVERY SHELF FRONT AND IN THE SHOWCASE (ID-331, ID-332)'),
            ('LM1', 'mirror', ((448.0, 954.1), (448.0, 978.1)), 'MASTER W.I.C.: BACKLIT LED MIRROR AT THE VANITY (ID-332)')]

FIXTURES = [   # type, description, source, note
    ('L1', 'RECESSED DOWNLIGHT, 3-1/2" APERTURE (L1a IC-RATED ON FLOOR 2)', 'FOR', 'A-207a; KITCHEN ROW AT THE ISLAND FOLLOWS THE ISLAND 4-5/8" EAST'),
    ('L2', 'RECESSED DOWNLIGHT, WET LOCATION (SHOWERS, TUBS)', 'FOR', 'A-207a'),
    ('L3', 'RECESSED DOWNLIGHT, SMALL APERTURE (CLOSETS, PANTRY, LAUNDRY)', 'FOR', 'A-207a'),
    ('L4', 'RECESSED SOFFIT DOWNLIGHT (EXTERIOR)', 'FOR', 'A-207a; ENTRY BAND TAG IS FOR\'S ERROR: LED COVE LC1 THERE'),
    ('L7', 'LED TAPE, STAIR RAIL', 'FOR', 'A-207a'),
    ('L8', 'LED TAPE, WET RATED (NICHES, LAUNDRY, BACK HALL)', 'FOR', 'A-207a; NONE WHERE NO CABINET IS ABOVE'),
    ('L9', 'LED TAPE, UNDER CABINET', 'FOR', 'REPLACED BY LS2 IN THE KITCHEN (NO UPPERS ON THE RANGE WALL)'),
    ('L19', 'WALL-MOUNTED FIXTURE, MOTION SENSOR', 'FOR', 'AHU ROOM AND COAT CLOSET 13 (A-207a); CLEAR OF THE 5\'-6" SHELF (ID-251)'),
    ('L13', 'LED TAPE, CLOSET MILLWORK', 'FOR', 'MASTER W.I.C.: REPLACED BY LS2 AT THE MILLWORK SHELVES AND SHOWCASE (ID-330 TO 333)'),
    ('L14', 'LED COVE, HIGH OUTPUT (FOR TAG)', 'FOR', 'MASTER W.I.C. HEADER AS TAGGED ON A-206; A-207a CALLS L14 THE MASTER COVE: FOR TO CONFIRM'),
    ('L16', 'TRIMLESS WALL WASHER (ART WALLS)', 'FOR', 'CENTER ON THE ART; CLEAR OF HIDDEN DOOR 16'),
    ('L17', 'EXTERIOR WALL LIGHT', 'FOR', 'A-207a'),
    ('LC1', 'LED COVE ON THE CROWN TOP, 2700K, DIMMABLE, CONTINUOUS', 'ID', 'REPLACES FOR\'S L11, L12, L14 COVES; 4/ID-502'),
    ('LS1', 'LINEAR WALL SCONCE, 24", OVER THE MIRROR, ON A J-BOX', 'ID', 'POWDER ROOM; REPLACES FOR\'S TWO SIDE SCONCES (ID-212)'),
    ('LS2', 'LED TAPE IN A CHANNEL, UNDER STONE SHELVES / IN CABINETS', 'ID', 'KITCHEN, PANTRY, MASTER NOOK BOOKCASE; DRIVERS ACCESSIBLE (ID-241, ID-242, ID-244, ID-313)'),
    ('LM1', 'BACKLIT LED MIRROR, HARDWIRED, DIMMABLE', 'ID', 'GUEST BATH, BATHS 2 AND 3, MASTER W.I.C. VANITY (ID-332); REPLACES FOR\'S VANITY SCONCES'),
    ('SC1', 'DECORATIVE WALL SCONCE ON A J-BOX', 'ID', 'MASTER BEDROOM AND MASTER BATH; SELECTION BY OWNER, HEIGHTS PER THE ELEVATIONS'),
    ('P1', 'DECORATIVE PENDANT ON A J-BOX (ISLAND x3)', 'ID', 'ON FOR\'S J-BOXES, SHIFTED WITH THE ISLAND; HANG 2\'-6" TO 3\'-0" ABOVE THE TOP'),
    ('CH1', 'CHANDELIER ON A J-BOX (CENTER TO SPACE)', 'ID', 'FOR\'S J-BOXES: DINING, ENTRY, GALLERY, OFFICE, BEDROOMS, DEN, MASTER BATH, W.I.C., LIVING'),
]

# ------------------------------------------------------------------ drawing helpers
def poly_inset(g, d):
    h = g.buffer(-d, join_style=2)
    return h if not h.is_empty else g

def outline(sh, g, w, color, dashes=None):
    for p in (list(g.geoms) if hasattr(g, 'geoms') else [g]):
        if p.is_empty: continue
        pts = [fitz.Point(x, y) for x, y in p.exterior.coords]
        s = sh.p.new_shape(); s.draw_polyline(pts); s.finish(color=color, width=w, dashes=dashes, closePath=True); s.commit()

def ceil_tag(sh, x, y, lines):
    w = max(FREG.f.text_length(t, fontsize=7.0) for t in lines) + 8; h = 8.6 * len(lines) + 4
    r = fitz.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    sh.p.draw_rect(r, color=INK, fill=WHITE, width=0.5)
    for i, t in enumerate(lines):
        sh.text(x, r.y0 + 8.6 + 8.6 * i, t, 7.0, INK, align='c', raw=True)
    return r

def sym_sconce(sh, x, y, nx, ny, tag=None):
    """Wall sconce: half disc on the wall face, opening into the room (nx, ny = into-room unit normal)."""
    s = sh.p.new_shape(); r = 3.2
    a0 = math.degrees(math.atan2(ny, nx)) - 90
    pts = [fitz.Point(x + r * math.cos(math.radians(a0 + t)), y + r * math.sin(math.radians(a0 + t))) for t in range(0, 181, 15)]
    s.draw_polyline(pts + [pts[0]]); s.finish(color=INK, fill=INK, width=0.4, closePath=True); s.commit()
    if tag: sh.text(x + nx * 9, y + ny * 9 + 2, tag, 5.5, INK, align='c', raw=True)

def sym_line(sh, a, b, tag=None, mirror=False, ok=None):
    if mirror:
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L * 2.4, dx / L * 2.4
        q = [fitz.Point(a[0], a[1]), fitz.Point(b[0], b[1]), fitz.Point(b[0] + nx, b[1] + ny), fitz.Point(a[0] + nx, a[1] + ny)]
        s = sh.p.new_shape(); s.draw_polyline(q + [q[0]]); s.finish(color=INK, fill=(0.85, 0.85, 0.85), width=0.6, closePath=True); s.commit()
    else:
        sh.line(a, b, 1.6, INK, dashes='[6 2 1.5 2] 0')
    if tag:
        if abs(b[0] - a[0]) > abs(b[1] - a[1]) and not mirror:        # horizontal run: tag over its west end, clear of FOR's end switches
            x0 = min(a[0], b[0]); sh.text(x0, a[1] + 7.5, tag, 5.5, INK, raw=True)
        else:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            if not mirror and abs(b[1] - a[1]) > abs(b[0] - a[0]): my = min(a[1], b[1]) + 4      # vertical run: tag at its north end, clear of the fixtures
            if ok is None or ok(mx + 16, my - 3, mx, my): sh.text(mx + 4, my, tag, 5.5, INK, raw=True)
            else: sh.text(mx - 4, my, tag, 5.5, INK, align='r', raw=True)        # the room is on the west side

# ------------------------------------------------------------------ sheets
def base(sh, fl, f):
    FN.place_base(sh, fl)
    if fl == 1:
        FN.cover_south_run(sh)
        sh.p.add_redact_annot(fitz.Rect(150.0, 385.5, 262.0, 405.0))       # the KITCHEN LAYOUT note sits under FOR's downlights here; the cabinetry box carries the reference
        sh.p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    FN.revisions(sh, fl, f, False, rcp=True); FN.wall_hung_toilets(sh, fl, f, False)

def ceiling_layer(sh, fl, f, R, items, words, T, kinds, drop):
    """FOR's content of the given kinds, minus `drop`."""
    for k, d, c, r in items:
        if k not in kinds or drop(k, c, d, r): continue
        draw_for(sh, d, T, INK if k not in ('switch',) else DARKG)
    tagre = re.compile(r'^(L\d{1,2}[a-c]?|SD|EF|C-1|CENTER TO|SPACE|ON CENTER|ATTIC|SCUTTLE|22 x 36)$')
    obst = occupied(sh)
    for t, (x, y), size, dr in words:
        if not tagre.match(t) or drop('text', (x, y), t, None): continue
        X, Y = f(x, y); fs = max(5.0, size * 0.75); w = fitz.get_text_length(t, 'helv', fs)
        for dx, dy in ((0, 0), (0, 7), (0, -7), (9, 0), (-9, 0), (0, 13), (0, -13), (14, 7), (-14, -7)):
            r = fitz.Rect(X + dx, Y + dy - fs * 0.8, X + dx + w, Y + dy + 1)
            if not any(r.intersects(o) for o in obst): break
        else: continue
        sh.text(X + dx, Y + dy, t, fs, INK, raw=True); obst.append(r)

def access_panel(sh, f, color):
    r = FN.rect_sheet(AP, f); x0, y0, x1, y1 = r.bounds
    sh.p.draw_rect(fitz.Rect(x0, y0, x1, y1), color=color, fill=WHITE, width=0.6)
    sh.line((x0, y0), (x1, y1), 0.3, color); sh.line((x0, y1), (x1, y0), 0.3, color)
    sh.text((x0 + x1) / 2, (y0 + y1) / 2 + 2.5, 'AP', 7.0, color, align='c', raw=True)

def draw_trays(sh, fl, items_all, T, color, width):
    """FOR's tray (band) edges, matched by their FOR plan extents."""
    for k, d, c, r in items_all:
        if k != 'tray': continue
        q = (r.x0 + OFFSET[fl][0], r.y0 + OFFSET[fl][1], r.x1 + OFFSET[fl][0], r.y1 + OFFSET[fl][1])
        if any(all(abs(a - b) < 2.0 for a, b in zip(q, t)) for t in TRAY[fl]):
            draw_for(sh, d, T, color, scale=width / 0.72)
            TRAY_SEEN.add((fl, tuple(round(v) for v in q)))

TRAY_SEEN = set(); NSW = {}

def draw_switches(sh, fl, f, inside):
    """FOR's switches (E-300 / E-301) in grey, glyphs and subscripts as FOR drew them."""
    sw, (ex, ey) = e_switches(fl); p = epage(fl); M = p.rotation_matrix
    def TE(pt):
        q = fitz.Point(pt) * M; return fitz.Point(*f(q.x + ex, q.y + ey))
    done = set(); txt = set(); n = 0
    for c, cl, tx in sw:
        if not inside.contains(Point(c)): continue
        n += 1
        for d in cl:
            if id(d) in done: continue
            done.add(id(d)); draw_for(sh, d, TE, DARKG, scale=0.8)
        for t, (x, y), h in tx:
            key = (t, round(x), round(y))
            if key in txt: continue
            txt.add(key); X, Y = f(x, y); sh.text(X, Y, t, max(4.2, h * 0.75 * 0.85), DARKG, raw=True)
    return n

def occupied(sh):
    return [fitz.Rect(w[:4]) + (-0.8, -0.8, 0.8, 0.8) for w in sh.p.get_text('words')]

def place_tag(sh, g, lines, obst, prefer=None, must=True):
    """A ceiling tag inside room g (sheet pt), clear of words already on the sheet; nearest the room's pole (or `prefer`)."""
    w = max(FREG.f.text_length(t, fontsize=7.0) for t in lines) + 8; h = 8.6 * len(lines) + 4
    gg = g if g.geom_type == 'Polygon' else max(g.geoms, key=lambda q: q.area)
    c = polylabel(gg, 1.0) if prefer is None else Point(prefer)
    inner = gg.buffer(-3)
    best = None
    for rad in range(0, 160, 6):
        for k in range(max(1, rad // 3)):
            a = 2 * math.pi * k / max(1, rad // 3); x = c.x + rad * math.cos(a); y = c.y + 18 + rad * math.sin(a)
            r = fitz.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if not inner.contains(box(r.x0, r.y0, r.x1, r.y1)): continue
            if any(r.intersects(o) for o in obst): continue
            best = (x, y); break
        if best: break
    if best is None:
        if not must: return None
        best = (c.x, c.y + 18)
    r = ceil_tag(sh, best[0], best[1], lines); obst.append(r + (-2, -2, 2, 2)); return r

# ------------------------------------------------------------------ review 11.09.26: our switching, fixtures and the coordination layer
TXT = 7.0                      # every tag and label on these sheets: 7 pt minimum (review 11.09.26)
TXTC = (0.25, 0.25, 0.25)      # relocated room names
# Rooms our elevations cover: their switching is ours (the elevations govern); FOR's E-300 / E-301 switching there is listed for FOR, not drawn.
ELEV = {1: ['KITCHEN AND DINING', 'PANTRY', 'GUEST BEDROOM', 'GUEST BATHROOM', 'LAUNDRY AND BACK HALL', 'LAUNDRY', 'UTILITY ROOM', 'ENTRY',
            'POWDER ROOM', 'LIVING ROOM'],
        2: ['BATH 3', 'BATH 2', 'BEDROOM 3', 'BEDROOM 2', 'MASTER BATH', 'MASTER SHOWER', 'WATER CLOSET', 'MASTER BEDROOM']}
GALLERY_Y = 845.0              # floor 1: the living room polygon south of this is the gallery and stair (ID-270 not drawn): FOR's switching stays there
# Our switches from the elevations, FOR plan pt on the wall face, into-room normal, label, source (computed from each builder's plan constants)
OUR_SW = {1: [((653.3, 137.0), (0, 1), 'S/D', '1/ID-241'), ((635.2, 540.4), (0, -1), 'S/D', 'ID-242'), ((459.7, 550.9), (0, 1), 'S', 'ID-244'),
              ((845.1, 1270.0), (0, -1), 'S', 'ID-211'), ((960.2, 1181.9), (1, 0), 'S/F', 'ID-212'), ((753.7, 1041.1), (-1, 0), 'S', 'ID-251'),
              ((738.7, 949.4), (0, -1), 'S', 'ID-252'), ((481.1, 1016.8), (-1, 0), 'S', 'ID-253'), ((614.7, 650.6), (0, 1), 'S3', 'ID-261'),
              ((619.2, 731.4), (-1, 0), 'S3', 'ID-261'), ((424.4, 804.7), (0, -1), 'S2', 'ID-261')],
          2: [((686.7, 637.4), (0, -1), 'S3', 'ID-341'), ((691.2, 527.6), (-1, 0), 'S3', 'ID-341'), ((759.7, 137.0), (0, 1), 'S3', 'ID-351'),
              ((698.2, 445.0), (1, 0), 'S3', 'ID-351'), ((469.8, 449.5), (0, -1), 'S', 'ID-342'), ((535.5, 203.2), (-1, 0), 'S', 'ID-352'),
              ((688.8, 1194.2), (-1, 0), 'S/F', 'ID-322'), ((623.2, 1211.4), (1, 0), 'S/F', 'ID-323'), ((777.2, 919.1), (0, 1), 'S3', 'ID-311'),
              ((973.2, 978.5), (-1, 0), 'S4', 'ID-312'), ((698.1, 1202.7), (1, 0), 'S3', 'ID-312'), ((1037.1, 1290.8), (0, -1), 'S', 'ID-313')]}
ISL_SHIFT_PT = 4.625 * 1.5     # the island and its pendants 4-5/8" east of FOR's (ID-243)
P1_FOR = [(511.0, 321.0), (511.0, 357.0), (511.0, 393.0)]       # FOR's three island J-boxes (A-205)
SC1 = {1: [], 2: [((973.16, 993.5), (-1, 0)), ((973.16, 1196.4), (-1, 0)),                          # headboard wall, 1'-1" from each corner (ID-312)
               ((461.95, 1080.2), (0, 1)), ((517.45, 1080.2), (0, 1)), ((617.95, 1080.2), (0, 1)), ((673.45, 1080.2), (0, 1))]}   # vanity mirrors (ID-321)
LS1 = {1: [((1044.0, 1205.0), (-1, 0))], 2: []}
SHOWER_L2 = ((480.0, 1248.0), (480.0, 1230.0))                  # master shower: FOR's L2 moves 1'-0" north, off the rain head (ID-322)
DROP_SCONCE_ROOMS = {1: ['GUEST BEDROOM', 'POWDER ROOM', 'GUEST BATHROOM'],
                     2: ['BEDROOM 2', 'BEDROOM 3', 'DEN / PLAYROOM', 'MASTER BEDROOM', 'MASTER BATH', 'BATH 2', 'BATH 3']}
DROP_SCONCE_AT = {1: [(924.0, 1054.0)], 2: []}                     # the stair sconce on our lower-flight half wall (ID-230 note 7)
L8_DROP_ROOMS = ['LAUNDRY', 'LAUNDRY AND BACK HALL']             # no cabinets above the laundry sink or the lockers
L19_AT = [(606.0, 1067.0), (667.0, 1067.0), (720.0, 1067.0)]     # FOR's wall-mounted motion fixtures, AHU room and coat closet 13
# FOR's supply diffusers (3-3/4" thick) and return grilles (6") from M-100 / M-101; the ones that clash move (center from -> to, FOR plan pt)
MDELTA = {1: (-71.82, -38.28), 2: (-60.6, -32.88)}
MSRC = {1: 'M-100', 2: 'M-101'}
DIFF_MOVE = {1: [((375, 728), (401, 728), 'GUEST BEDROOM RETURN OFF THE DRAPERY POCKET'), ((971, 1440), (971, 1405), 'OFFICE RETURN OFF THE DRAPERY POCKET')],
             2: [((742, 242), (719, 242), 'BEDROOM 3 SUPPLY OFF THE DRAPERY POCKET'), ((953, 1095), (919, 1095), 'MASTER RETURN 3\'-0" OFF THE HEADBOARD WALL'),
                 ((572, 629), (572, 592), 'BEDROOM 2 SUPPLY OFF THE HEADBOARD WALL')]}
# 5" drapery pockets (C-1) where our elevations call for them, FOR plan pt rect; label side into the room
POCKETS = {1: [((356.5, 650.8, 364.0, 804.2), 'C-1', 'ID-261'), ((896.5, 1442.0, 1045.8, 1449.5), 'C-1', 'FOR A-205'),
               ((751.2, 206.0, 757.2, 507.0), 'C-1', 'ID-242')],
           2: [((446.5, 457.1, 454.0, 637.4), 'C-1', 'ID-341'), ((756.7, 137.0, 764.2, 376.0), 'C-1', 'ID-351'),
               ((698.1, 1208.4, 896.1, 1215.9), 'C-1', 'ID-311'), ((914.1, 1283.3, 1046.1, 1290.8), 'C-1', 'ID-313'),
               ((774.0, 568.0, 1046.0, 575.5), 'C-1', 'ID-232')]}
CH1_AT = {1: [(695, 357), (487, 727), (791, 1211), (971, 1351), (868, 957)],            # FOR's chandelier J-boxes (the cross symbols)
          2: [(906, 701), (568, 971), (860, 1064), (568, 1155), (569, 548), (654, 256), (614, 726)]}
NOOK_TAG = (900.0, 1218.0, 1044.0, 1288.0)                       # the master nook, 9'-6" (FOR)
FORLIST = {1: [], 2: []}                                         # FOR switching not drawn (rooms our elevations cover)


def text_rect(x, y, t, size, align='l'):
    w = FREG.f.text_length(t, fontsize=size) * 1.04
    x0 = x - (w if align == 'r' else w / 2 if align == 'c' else 0)
    return fitz.Rect(x0, y - size * 0.78, x0 + w, y + size * 0.24)

class Pre(list):
    def add(self, r): self.append(fitz.Rect(r))

def promote(sh, pre):
    pl = Placer(sh)
    for r in pre: pl.add(r)
    return pl

class InkMap:
    """The sheet as drawn so far, rendered once: how much of a rectangle is already inked (walls, linework, symbols)."""
    K = 72.0 / 72.0
    def __init__(self, page, clip=fitz.Rect(30, 60, 760, 1180)):
        import numpy as np
        self.clip = clip; pm = page.get_pixmap(dpi=72, clip=clip, alpha=False, colorspace=fitz.csGRAY)
        self.a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.stride)[:, :pm.width] < 170
    def ink(self, r):
        x0 = int(max(0, r.x0 - self.clip.x0)); x1 = int(min(self.a.shape[1], r.x1 - self.clip.x0)); y0 = int(max(0, r.y0 - self.clip.y0)); y1 = int(min(self.a.shape[0], r.y1 - self.clip.y0))
        if x1 <= x0 or y1 <= y0: return 1.0
        return float(self.a[y0:y1, x0:x1].mean())

class Placer:
    """Obstacles on one sheet (words and symbols, sheet pt) and the placement of tags clear of them."""
    def __init__(self, sh, plan_x1=760.0):
        self.sh = sh; self.x1 = plan_x1
        self.obst = [fitz.Rect(w[:4]) + (-0.6, -0.6, 0.6, 0.6) for w in sh.p.get_text('words') if w[0] < plan_x1]
        self.inkmap = InkMap(sh.p)
    def add(self, r): self.obst.append(fitz.Rect(r))
    def hits(self, r): return sum((r & o).get_area() for o in self.obst if r.intersects(o)) + 150.0 * max(0.0, self.inkmap.ink(r) - 0.015) * r.get_area()
    def text(self, cands, t, size=TXT, color=INK, align='l', force=True, bold=False, within=None):
        """cands: [(x, y)] baseline anchors in order of preference; within: a sheet polygon the tag must sit in (when any candidate does)."""
        best = None
        if within is not None:
            ok = [(x, y) for x, y in cands if within.contains(box(*text_rect(x, y, t, size, align)))]
            cands = ok or cands
        for x, y in cands:
            r = text_rect(x, y, t, size, align)
            h = self.hits(r)
            if h == 0: best = (x, y, r); break
            if best is None or h < best[3 if len(best) > 3 else 0]: best = (x, y, r, h)
        if best is None: return None
        if len(best) > 3 and not force: return None
        x, y, r = best[:3]
        self.sh.text(x, y, t, size, color, align=align, bold=bold, raw=True); self.add(r + (-0.8, -0.8, 0.8, 0.8)); return r

def leader(sh, r, X, Y, color=DARKG, gap=10.0):
    """A thin leader from a tag to its item when the tag had to sit away from it."""
    if r is None: return
    px = min(max(X, r.x0), r.x1); py = min(max(Y, r.y0 - 1), r.y1 + 1)
    if math.hypot(px - X, py - Y) < gap: return
    sh.line((px, py), (X, Y), 0.35, color)

def toward(X, Y, nx, ny, w, h=TXT):
    """Tag anchors off a wall item, into the room first (nx, ny), then along the wall either side."""
    out = []
    for d in (7.0, 12.0, 18.0, 26.0):
        cx, cy = X + nx * d, Y + ny * d
        if nx: out += [(cx - (w if nx < 0 else 0), cy + 2.5), (cx - (w if nx < 0 else 0), cy - 5), (cx - (w if nx < 0 else 0), cy + 10)]
        else: out += [(cx - w / 2, cy + (6 if ny > 0 else -1)), (cx - w / 2 + 8, cy + (6 if ny > 0 else -1)), (cx - w / 2 - 8, cy + (6 if ny > 0 else -1))]
    tx, ty = -ny, nx
    for d in (9.0, 15.0):
        for sgn in (1, -1):
            cx, cy = X + tx * d * sgn + nx * 4, Y + ty * d * sgn + ny * 4
            out.append((cx - (w if tx * sgn < 0 else 0) if tx else cx - w / 2, cy + 2.5))
    return out

def around(X, Y, rad=7.0, w=10.0):
    """Tag anchors around a symbol at (X, Y): right, left, below, above, then the diagonals and further out."""
    out = []
    for k in (1.0, 1.7, 2.5, 3.5, 4.5):
        r = rad * k
        out += [(X + r, Y + 2.5), (X - r - w, Y + 2.5), (X - w / 2, Y + r + 5), (X - w / 2, Y - r), (X + r, Y + r + 3), (X + r, Y - r + 2),
                (X - r - w, Y + r + 3), (X - r - w, Y - r + 2)]
    return out

def sym_rect(f, r_plan, pad=1.0):
    a = f(r_plan[0], r_plan[1]); b = f(r_plan[2], r_plan[3])
    return fitz.Rect(min(a[0], b[0]) - pad, min(a[1], b[1]) - pad, max(a[0], b[0]) + pad, max(a[1], b[1]) + pad)

def room_of(R, c, tol=14.0):
    p = Point(c); n, g = min(R.items(), key=lambda kv: kv[1].distance(p))
    return n if g.distance(p) <= tol else None

def relocate_names(sh, syms, Rs, plan_x1=760.0):
    """FOR's room names in the base that a symbol lands on: white them out and set them again clear of the symbols (review 11.09.26)."""
    words = [w for w in sh.p.get_text('words') if w[0] < plan_x1 and re.fullmatch(r"[A-Z][A-Z.&/']*\d?|\d|/", w[4])]
    im = InkMap(sh.p)
    moved = set(); out = []
    for i, w in enumerate(words):
        if i in moved: continue
        wr = fitz.Rect(w[:4])
        if not any(wr.intersects(s) for s in syms): continue
        # the label block: words of the same height stacked or in line with this one
        h = wr.height; grp = {i}; changed = True
        while changed:
            changed = False
            for j, u in enumerate(words):
                if j in grp: continue
                ur = fitz.Rect(u[:4])
                if abs(ur.height - h) > 1.2: continue
                if any(abs(ur.y0 - fitz.Rect(words[k][:4]).y0) < 1.5 * h + 1 and (ur.x0 < fitz.Rect(words[k][:4]).x1 + 8 and ur.x1 > fitz.Rect(words[k][:4]).x0 - 8) for k in grp):
                    grp.add(j); changed = True
        moved |= grp
        gw = [words[k] for k in sorted(grp, key=lambda k: (round(words[k][1]), words[k][0]))]
        bb = fitz.Rect(gw[0][:4])
        for u in gw[1:]: bb |= fitz.Rect(u[:4])
        room = None
        for n, g in Rs.items():
            if g.contains(Point((bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2)): room = g; break
        others = [fitz.Rect(u[:4]) for k, u in enumerate(words) if k not in grp]
        best = None
        for lim in (0.01, 0.05):
            for rad in range(2, 90, 3):
                for k in range(16):
                    a = 2 * math.pi * k / 16; dx, dy = rad * math.cos(a), rad * math.sin(a)
                    nb = bb + (dx, dy, dx, dy)
                    if room is not None and not room.buffer(-1.0).contains(box(nb.x0, nb.y0, nb.x1, nb.y1)): continue
                    if any(nb.intersects(s) for s in syms) or any(nb.intersects(o) for o in others) or im.ink(nb + (-1, -1, 1, 1)) - (0.0 if not nb.intersects(bb) else im.ink(bb)) > lim: continue
                    best = (dx, dy); break
                if best: break
            if best: break
        one = None
        if best is None:            # a tight room: the name on one line, anywhere clear in the room (its old place included)
            t1 = ' '.join(u[4] for u in gw); size1 = h / 1.16; w1 = FREG.f.text_length(t1, fontsize=size1) + 1
            cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
            for lim in (0.02, 0.08):
                for rad in range(0, 60, 2):
                    for k in range(24 if rad else 1):
                        a = 2 * math.pi * k / 24; dx, dy = rad * math.cos(a), rad * math.sin(a)
                        nb = fitz.Rect(cx - w1 / 2 + dx, cy - h / 2 + dy, cx + w1 / 2 + dx, cy + h / 2 + dy)
                        if room is not None and not room.buffer(-1.0).contains(box(nb.x0, nb.y0, nb.x1, nb.y1)): continue
                        if any(nb.intersects(s) for s in syms) or any(nb.intersects(o) for o in others): continue
                        if im.ink(nb + (-1, -1, 1, 1)) > lim + (im.ink(bb) if nb.intersects(bb) else 0.0): continue
                        one = (nb, t1, size1); break
                    if one: break
                if one: break
            if one is None: continue
        for u in gw: sh.p.add_redact_annot(fitz.Rect(u[:4]) + (0.3, 0.3, -0.3, -0.3))      # the name goes from the base, not just covered
        sh.p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        if one is not None:
            nb, t1, size1 = one; sh.text((nb.x0 + nb.x1) / 2, nb.y1 - h * 0.22, t1, size1, TXTC, align='c', raw=True); out.append(t1); continue
        size = h / 1.16
        lines = {}
        for u in gw: lines.setdefault(round(u[1] / 2), []).append(u)
        for _k, ln in sorted(lines.items()):
            t = ' '.join(u[4] for u in sorted(ln, key=lambda u: u[0])); r0 = fitz.Rect(ln[0][:4])
            for u in ln[1:]: r0 |= fitz.Rect(u[:4])
            sh.text((r0.x0 + r0.x1) / 2 + best[0], r0.y1 - h * 0.22 + best[1], t, size, TXTC, align='c', raw=True)
        out.append(' '.join(u[4] for u in gw))
    return out

def m_diffusers(fl):
    """FOR's supply diffusers and return grilles: [(kind, plan rect)], kind 'S' (3-3/4" face) or 'R' (6")."""
    p = fitz.open(EDIR + MSRC[fl] + '.pdf')[0]; M = p.rotation_matrix; dx, dy = MDELTA[fl]; ox, oy = OFFSET[fl]; out = []; seen = set()
    for d in p.get_drawings():
        if len(d['items']) != 1 or d['items'][0][0] != 'qu' or d['type'] != 's' or abs((d.get('width') or 0) - 0.72) > 0.01: continue
        r = d['rect'] * M; a, b = sorted((r.width, r.height))
        if not (3.0 <= a <= 7.0 and 15 <= b <= 150): continue
        q = (r.x0 + dx + ox, r.y0 + dy + oy, r.x1 + dx + ox, r.y1 + dy + oy); key = tuple(round(v) for v in q)
        if key in seen: continue
        seen.add(key); out.append(('R' if a > 5.0 else 'S', q))
    return out

def draw_diff(sh, f, q, color=(0.6, 0.6, 0.6), dashes=None):
    r = sym_rect(f, q, 0)
    sh.p.draw_rect(r, color=color, fill=(0.88, 0.88, 0.88) if dashes is None else None, width=0.45, dashes=dashes)
    if dashes is None:
        if r.width > r.height: sh.line((r.x0 + 1, (r.y0 + r.y1) / 2), (r.x1 - 1, (r.y0 + r.y1) / 2), 0.3, color)
        else: sh.line(((r.x0 + r.x1) / 2, r.y0 + 1), ((r.x0 + r.x1) / 2, r.y1 - 1), 0.3, color)
    return r

def draw_switch(sh, X, Y, color=INK):
    sh.text(X, Y + 3.4, '$', 10, color, align='c', raw=True)
    return fitz.Rect(X - 3.2, Y - 5.0, X + 3.2, Y + 5.0)

def p1_sym(sh, X, Y):
    sh.p.draw_circle(fitz.Point(X, Y), 4.5, color=INK, width=0.6)
    sh.line((X - 3.2, Y - 3.2), (X + 3.2, Y + 3.2), 0.5, INK); sh.line((X - 3.2, Y + 3.2), (X + 3.2, Y - 3.2), 0.5, INK)
    return fitz.Rect(X - 5, Y - 5, X + 5, Y + 5)

def downlight(sh, X, Y):
    sh.p.draw_circle(fitz.Point(X, Y), 4.5, color=INK, width=0.6); sh.p.draw_circle(fitz.Point(X, Y), 1.0, color=INK, fill=INK, width=0.3)
    return fitz.Rect(X - 5, Y - 5, X + 5, Y + 5)

def wall_sconce(sh, X, Y, nx, ny, w=0.0):
    """Wall light on a J-box: a bar on the wall face and a half disc into the room; w = a linear fixture's length (sheet pt)."""
    if w:
        tx, ty = -ny, nx
        sh.line((X - tx * w / 2 + nx * 1.0, Y - ty * w / 2 + ny * 1.0), (X + tx * w / 2 + nx * 1.0, Y + ty * w / 2 + ny * 1.0), 2.0, INK)
    sym_sconce(sh, X + nx * 1.2, Y + ny * 1.2, nx, ny)
    e = max(5.0, w / 2 + 1)
    return fitz.Rect(X - e, Y - e, X + e, Y + e)

def cluster(points, d=14.0):
    groups = []
    for p in points:
        for g in groups:
            if any(math.hypot(p[0] - q[0], p[1] - q[1]) < d for q in g): g.append(p); break
        else: groups.append([p])
    return [(sum(q[0] for q in g) / len(g), sum(q[1] for q in g) / len(g)) for g in groups]


def build():
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    doc = fitz.open()
    for fl in (1, 2):
        R = FN.RR.rooms(fl)
        T, f = mapper(fl); items = for_items(fl); words = for_words(fl)
        Rs = {k: FN.geom_to_sheet(g, f) for k, g in R.items()}
        inside = unary_union(list(R.values())).buffer(10)
        cove_g = unary_union([R[n] for n in COVE[fl] if n in R]).buffer(1.5)
        if fl == 2: cove_g = unary_union([cove_g, box(*VOID_2).buffer(2)])
        scg = unary_union([R[n] for n in DROP_SCONCE_ROOMS[fl] if n in R]).buffer(6)
        l8g = unary_union([R[n] for n in L8_DROP_ROOMS if n in R]).buffer(5) if fl == 1 else None
        kit = R.get('KITCHEN AND DINING')
        mbath = unary_union([R[n] for n in ('MASTER BATH', 'MASTER SHOWER', 'WATER CLOSET') if n in R]).buffer(4) if fl == 2 else None
        isl = [Point(p).buffer(6) for p in P1_FOR] if fl == 1 else []
        wicg = R['W.I.C.'].buffer(2) if fl == 2 and 'W.I.C.' in R else None      # the master closet: our LS2 / LM1 / CH1 per ID-330

        def drop(k, c, d, r):
            P = Point(c)
            if not inside.contains(P): return True
            if k == 'text':
                t = d
                if t in ('L11', 'L12', 'L14', 'L4') and cove_g.contains(P): return True      # FOR's cove tags: our LC1 instead
                if t == 'L9' and kit is not None and kit.buffer(8).contains(P): return True
                if t == 'L8' and l8g is not None and l8g.contains(P): return True              # no cabinets above (review 11.09.26)
                if t in ('CENTER TO', 'SPACE', 'ON CENTER'): return True                      # CH1 tag instead
                if t in ('L13', 'L14') and wicg is not None and wicg.contains(P): return True
                if t == 'C-1' and mbath is not None and mbath.contains(P): return True        # no pockets at the tub or the terrace door (owner)
                if t == 'L2' and fl == 2 and P.distance(Point(SHOWER_L2[0])) < 22: return True
                return False
            if k == 'dashed' and cove_g.contains(P): return True
            if k in ('dashed', 'strip') and wicg is not None and wicg.contains(P): return True     # FOR's L13 / L14 in the W.I.C.
            if k == 'sconce' and wicg is not None and wicg.contains(P) and not d.get('width') and min(r.width, r.height) < 1.5: return True   # FOR's L14 dashes
            if k == 'dashed' and fl == 1 and max(r.width, r.height) > 150: return True
            if k == 'strip' and cove_g.contains(P) and max(r.width, r.height) > 40: return True
            if k in ('dashed', 'strip') and kit is not None and kit.buffer(8).contains(P): return True     # FOR's L9: our LS2
            if k in ('dashed', 'strip') and l8g is not None and l8g.contains(P): return True
            if k == 'sconce' and cove_g.buffer(4).contains(P) and (max(r.width, r.height) > 40 or (not d.get('width') and len(d['items']) == 6 and min(r.width, r.height) < 1.5)): return True
            if k in ('sconce', 'outlet') and scg.contains(P): return True                     # FOR's sconces our design deletes or replaces (FOR list)
            if k == 'sconce' and any(P.distance(Point(q)) < 12 for q in DROP_SCONCE_AT[fl]): return True
            if k == 'pendant' and any(g.contains(P) for g in isl): return True                # FOR's island J-boxes: our P1, shifted with the island
            if k == 'recess' and fl == 2 and P.distance(Point(SHOWER_L2[0])) < 9: return True
            return False

        for kind_, size_ in (('recess', (11, 13.5)), ('washer', (8, 10)), ('sconce', (8, 10)), ('pendant', (8, 40))):
            if kind_ in SAMPLE: continue
            for k, d, c, r in items:
                if k == kind_ and size_[0] <= r.width <= size_[1] and not drop(k, c, d, r) and (kind_ != 'pendant' or abs(r.width - r.height) < 2):
                    grp = [(d2, T, f(*c)) for k2, d2, c2, r2 in items if k2 == kind_ and math.hypot(c2[0] - c[0], c2[1] - c[1]) < 9 and not drop(k2, c2, d2, r2)]
                    if len(grp) < 2 and kind_ == 'recess': continue
                    SAMPLE[kind_] = grp; break
        # FOR's chandelier J-boxes (not the island): CH1
        ch = CH1_AT[fl]
        # FOR's switches: ours govern where our elevations cover the room
        sw_e, (ex, ey) = e_switches(fl); keep_sw = []
        for c, cl, tx in sw_e:
            if not inside.contains(Point(c)): continue
            rn = room_of(R, c)
            covered = rn in ELEV[fl] and not (rn == 'LIVING ROOM' and c[1] > GALLERY_Y)
            near = any(math.hypot(c[0] - q[0][0], c[1] - q[0][1]) < 25 for q in OUR_SW[fl])
            if covered or near:
                FORLIST[fl].append((rn or 'HALL', ''.join(t for t, _p, _h in tx) or 'S')); continue
            keep_sw.append((c, ' '.join(dict.fromkeys(t for t, _p, _h in tx))))
        diffs = m_diffusers(fl)
        moves = {}
        for (a, b, note) in DIFF_MOVE[fl]:
            k_ = min(range(len(diffs)), key=lambda i: math.hypot((diffs[i][1][0] + diffs[i][1][2]) / 2 - a[0], (diffs[i][1][1] + diffs[i][1][3]) / 2 - a[1]))
            moves[k_] = (b, note)

        def symbols(kinds, lighting):
            """Sheet rects of every symbol the sheet will carry (for name relocation and tag placement)."""
            out = []
            for k, d, c, r in items:
                if k not in kinds or drop(k, c, d, r) or max(r.width, r.height) > 30: continue
                out.append(sym_rect(f, (r.x0 + OFFSET[fl][0], r.y0 + OFFSET[fl][1], r.x1 + OFFSET[fl][0], r.y1 + OFFSET[fl][1])))
            pts = [(p[0] + ISL_SHIFT_PT, p[1]) for p in (P1_FOR if fl == 1 else [])] + ([SHOWER_L2[1]] if fl == 2 else [])
            if lighting:
                pts += [q[0] for q in SC1[fl]] + [q[0] for q in LS1[fl]] + [c for c, _t in keep_sw]
                pts += [(q[0][0] + q[1][0] * 5.5 / 0.75, q[0][1] + q[1][1] * 5.5 / 0.75) for q in OUR_SW[fl]]
            for p in pts:
                X, Y = f(*p); out.append(fitz.Rect(X - 5.5, Y - 5.5, X + 5.5, Y + 5.5))
            if lighting:
                for typ, kind, geom, label in our_lights(fl):
                    if kind in ('line', 'mirror'): out.append(sym_rect(f, (min(geom[0][0], geom[1][0]), min(geom[0][1], geom[1][1]), max(geom[0][0], geom[1][0]), max(geom[0][1], geom[1][1])), 3))
                for (x, y), (nx, ny) in LS1[fl]:
                    X, Y = f(x, y); e = 24 * 1.125 / 2 + 3; out.append(fitz.Rect(X - e, Y - e, X + e, Y + e))
            return [r + (-1.5, -1.5, 1.5, 1.5) for r in out]

        def place_for_tags(pl, kinds):
            tagre = re.compile(r'^(L\d{1,2}[a-c]?|SD|EF|C-1|ATTIC|SCUTTLE|22 x 36)$')
            for t, (x, y), size, dr in words:
                if not tagre.match(t) or drop('text', (x, y), t, None): continue
                X, Y = f(x, y); w_ = FREG.f.text_length(t, fontsize=TXT)
                pl.text([(X, Y)] + [(X + dx, Y + dy) for dx, dy in ((0, 7), (0, -7), (8, 0), (-8, 0), (0, 12), (0, -12), (12, 6), (-12, -6), (-w_ - 4, 0), (w_ + 2, 0), (0, 17), (0, -17))], t)

        def ch_tags(pl):
            for c in ch:
                X, Y = f(*c); pl.text(around(X, Y, 8, FREG.f.text_length('CH1', fontsize=TXT)), 'CH1')

        # ================================================================ RCP
        sh = Sheet(doc)
        sh.frame('REFLECTED CEILING PLAN - FLOOR %d' % fl, 'SCALE: 3/16" TO 1\'-0"', ['REFLECTED CEILING PLAN', 'FLOOR %d' % fl], 'ID-12%d' % fl)
        base(sh, fl, f)
        rk = ('recess', 'pendant', 'washer', 'anno', 'outlet', 'strip', 'dashed')
        syms = symbols(rk, False)
        syms += [sym_rect(f, q, 1) for _k, q in diffs if inside.contains(Point((q[0] + q[2]) / 2, (q[1] + q[3]) / 2))] + [sym_rect(f, q, 1) for q, _l, _s in POCKETS[fl]]
        for i_, ((nx_, ny_), _n) in moves.items():
            q = diffs[i_][1]; dq = (nx_ - (q[0] + q[2]) / 2, ny_ - (q[1] + q[3]) / 2); syms.append(sym_rect(f, (q[0] + dq[0], q[1] + dq[1], q[2] + dq[0], q[3] + dq[1]), 1))
        relocate_names(sh, syms, Rs)
        for name in CROWN[fl] + COVE[fl]:
            if name not in Rs: continue
            outline(sh, poly_inset(Rs[name], 3.75), 0.5, INK, dashes='[3 1.5] 0')
            if name in COVE[fl]: outline(sh, poly_inset(Rs[name], 6.0), 0.9, INK, dashes='[1.2 1.2] 0')
        if fl == 2:
            v = FN.rect_sheet(VOID_2, f); outline(sh, poly_inset(v, 3.75), 0.5, INK, '[3 1.5] 0'); outline(sh, poly_inset(v, 6.0), 0.9, INK, '[1.2 1.2] 0')
        if fl == 1:      # soffits over the full-height cabinets: 9" soffit, crown across (1/ID-501)
            K = [rr for tag, rr, _l in FN.CABINETS[1] if tag == 'K']
            for rr in (K[0], K[2]): hatch_soffit(sh, FN.rect_sheet(rr, f))
            for rr in ((356.22, 550.92, 375.72, 620.46), (599.7, 550.92, 619.2, 620.46), (356.22, 620.46, 619.2, 639.96)):
                hatch_soffit(sh, FN.rect_sheet(rr, f))
        draw_trays(sh, fl, items, T, INK, 0.6)
        pl = Pre()
        for q, lab, _src in POCKETS[fl]:
            r = sym_rect(f, q, 0); sh.p.draw_rect(r, color=INK, width=0.5); pl.add(r)
        for i, (kind, q) in enumerate(diffs):
            c = ((q[0] + q[2]) / 2, (q[1] + q[3]) / 2)
            if not inside.contains(Point(c)): continue
            if i in moves:
                (nx_, ny_), note = moves[i]; dq = (nx_ - c[0], ny_ - c[1]); q2 = (q[0] + dq[0], q[1] + dq[1], q[2] + dq[0], q[3] + dq[1])
                r0 = draw_diff(sh, f, q, dashes='[1.5 1.5] 0'); r1 = draw_diff(sh, f, q2, color=DARKG)
                sh.line(((r0.x0 + r0.x1) / 2, (r0.y0 + r0.y1) / 2), ((r1.x0 + r1.x1) / 2, (r1.y0 + r1.y1) / 2), 0.4, DARKG, dashes='[1 1] 0')
                pl.add(r0); pl.add(r1)
            else: pl.add(draw_diff(sh, f, q))
        for k, d, c, r in items:
            if k in rk and not drop(k, c, d, r): draw_for(sh, d, T, INK)
        P1 = []
        if fl == 1:
            for p in P1_FOR:
                X, Y = f(p[0] + ISL_SHIFT_PT, p[1]); pl.add(p1_sym(sh, X, Y)); P1.append((X, Y))
            access_panel(sh, f, INK)
            pl.add(sym_rect(f, AP, 1))
        if fl == 2:
            X, Y = f(*SHOWER_L2[1]); pl.add(downlight(sh, X, Y))
        for s_ in syms: pl.add(s_)
        pl = promote(sh, pl)
        # tags: ceiling first (largest), then the fixtures, the pockets and the moved diffusers
        for name, (h, band) in CEIL[fl].items():
            if name not in Rs: continue
            g = Rs[name]; pt = TAG_AT.get((fl, name))
            lines = ['CLG ' + h] + ([band] if band else []) + ['GYP. PT-01'] + (['CM-01 + LC1'] if name in COVE[fl] else ['CM-01'] if name in CROWN[fl] else [])
            r_ = place_tag(sh, g, lines, pl.obst, prefer=f(*pt) if pt else None, must=False)
            if r_ is None: r_ = place_tag(sh, g, ['CLG ' + h], pl.obst, prefer=f(*pt) if pt else None, must=False)
            if r_ is None: SMALL.setdefault(fl, []).append(name)
        if fl == 1:
            X, Y = VOID_TXT; pl.text([(X, Y - 9)], 'OPEN TO ABOVE', TXT, align='c'); pl.text([(X, Y)], "CLG 22'-8\", SEE ID-122", TXT, align='c')
            place_tag(sh, FN.rect_sheet((760, 940, 965, 1050), f), ['GALLERY', "SLOPED 9'-0\"", "TO 10'-8\"", 'GYP. PT-01'], pl.obst)
        if fl == 2:
            place_tag(sh, FN.rect_sheet(VOID_2, f), ['LIVING ROOM BELOW', "CLG 22'-8\"", "22'-4\" BAND", 'CM-02 + LC1'], pl.obst)
            place_tag(sh, FN.rect_sheet(NOOK_TAG, f), ["CLG 9'-6\"", 'GYP. PT-01', 'CM-01'], pl.obst)
        place_for_tags(pl, rk)
        ch_tags(pl)
        for X, Y in P1: pl.text(around(X, Y, 8, 12), 'P1')
        if fl == 2: X, Y = f(*SHOWER_L2[1]); pl.text(around(X, Y, 8, 10), 'L2')
        for q, lab, _src in POCKETS[fl]:
            r = sym_rect(f, q, 0); cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            cands = ([(cx, r.y1 + 9), (cx, r.y0 - 3)] if r.width > r.height else [(r.x1 + 3 + FREG.f.text_length(lab, fontsize=TXT) / 2, cy + 2.5), (r.x0 - 3 - FREG.f.text_length(lab, fontsize=TXT) / 2, cy + 2.5)])
            cands += [(x_, y_ + d_) for x_, y_ in cands[:2] for d_ in (-20, 20, -40, 40, -60, 60)]
            rm = [g for g in Rs.values() if g.buffer(6).intersects(box(r.x0, r.y0, r.x1, r.y1))]
            rm = max(rm, key=lambda g: g.intersection(box(r.x0 - 8, r.y0 - 8, r.x1 + 8, r.y1 + 8)).area) if rm else None
            lr = pl.text(cands, 'C-1', TXT, align='c', within=rm.buffer(-1) if rm is not None else None)
            tx_ = min(max((lr.x0 + lr.x1) / 2, r.x0), r.x1) if lr else cx; ty_ = min(max((lr.y0 + lr.y1) / 2, r.y0), r.y1) if lr else cy
            leader(sh, lr, tx_, ty_, INK, 6.0)
        for i, ((nx_, ny_), note) in moves.items():
            X, Y = f(nx_, ny_); rm = [g for g in Rs.values() if g.contains(Point(X, Y))]
            w_ = FREG.f.text_length('MOVE (FOR/MECH)', fontsize=TXT)
            lr = pl.text([(X + 6, Y + 2.5), (X - 6 - w_, Y + 2.5), (X - w_ / 2, Y + 14), (X - w_ / 2, Y - 8)] + around(X, Y, 12, w_), 'MOVE (FOR/MECH)', TXT, DARKG, within=rm[0].buffer(-1) if rm else None)
            leader(sh, lr, X, Y, DARKG, 12.0)
        rcp_legend(sh, fl)

        # ================================================================ lighting
        sh = Sheet(doc)
        sh.frame('LIGHTING AND SWITCHING PLAN - FLOOR %d' % fl, 'SCALE: 3/16" TO 1\'-0"', ['LIGHTING AND SWITCHING PLAN', 'FLOOR %d' % fl], 'ID-13%d' % fl)
        base(sh, fl, f)
        lk = ('recess', 'pendant', 'washer', 'sconce', 'strip', 'dashed')
        syms = symbols(lk, True)
        relocate_names(sh, syms, Rs)
        for name in COVE[fl]:
            if name in Rs: outline(sh, poly_inset(Rs[name], 6.0), 0.9, INK, dashes='[1.2 1.2] 0')
        if fl == 2: outline(sh, poly_inset(FN.rect_sheet(VOID_2, f), 6.0), 0.9, INK, '[1.2 1.2] 0')
        draw_trays(sh, fl, items, T, GREY, 0.45)
        pl = Pre()
        for k, d, c, r in items:
            if k in lk and not drop(k, c, d, r): draw_for(sh, d, T, INK)
        if fl == 1:
            access_panel(sh, f, DARKG); pl.add(sym_rect(f, AP, 1))
        for s_ in syms: pl.add(s_)
        P1 = []
        if fl == 1:
            for p in P1_FOR:
                X, Y = f(p[0] + ISL_SHIFT_PT, p[1]); p1_sym(sh, X, Y); P1.append((X, Y))
        if fl == 2: X, Y = f(*SHOWER_L2[1]); downlight(sh, X, Y)
        for (x, y), (nx, ny) in SC1[fl]:
            X, Y = f(x, y); wall_sconce(sh, X, Y, nx, ny)
        for (x, y), (nx, ny) in LS1[fl]:
            X, Y = f(x, y); wall_sconce(sh, X, Y, nx, ny, w=24 * 1.125)
        swr = []
        for (x, y), (nx, ny), lab, _src in OUR_SW[fl]:
            X, Y = f(x, y); X, Y = X + nx * 5.5, Y + ny * 5.5; swr.append((X, Y, lab, nx, ny)); pl.add(draw_switch(sh, X, Y))
        kept = []; merged = []
        for c, lab in keep_sw:
            for m in merged:
                if math.hypot(c[0] - m[0][0], c[1] - m[0][1]) < 12: m[1].append(lab); break
            else: merged.append([c, [lab]])
        keep_sw = [(c, ' '.join(x for x in labs if x)) for c, labs in merged]
        for c, lab in keep_sw:
            X, Y = f(*c); pl.add(draw_switch(sh, X, Y, DARKG)); kept.append((X, Y, lab))
        # our runs (LS2, LM1) drawn before the tags
        runs = []
        for typ, kind, geom, label in our_lights(fl):
            if kind in ('sconce', 'sconce_line'): continue
            a = f(*geom[0]); b = f(*geom[1]); sym_line(sh, a, b, None, mirror=(kind == 'mirror')); runs.append((typ, a, b))
            pl.add(fitz.Rect(min(a[0], b[0]) - 2, min(a[1], b[1]) - 2, max(a[0], b[0]) + 2, max(a[1], b[1]) + 2))
        pl = promote(sh, pl)
        # tags
        notes = []
        if fl == 1:
            X, Y = VOID_TXT; pl.text([(X, Y), (X, Y - 12), (X, Y + 12)], 'OPEN TO ABOVE, SEE ID-132', TXT, align='c')
        for name in COVE[fl] + (['LIVING'] if fl == 2 else []):
            g = FN.rect_sheet(VOID_2, f) if name == 'LIVING' else Rs[name]
            ring = poly_inset(g, 13.0); ring = ring if ring.geom_type == 'Polygon' else max(ring.geoms, key=lambda q: q.area)
            ext = ring.exterior; cands = [ext.interpolate(t / 40.0, normalized=True) for t in range(40)]
            cands.sort(key=lambda p: (p.y, p.x))
            pl.text([(p.x - 6, p.y + 2.5) for p in cands], 'LC1', within=g.buffer(-1))
        for X, Y, lab, nx, ny in swr:
            w_ = FREG.f.text_length(lab, fontsize=TXT)
            rm = [g for g in Rs.values() if g.contains(Point(X, Y))]
            lr = pl.text(toward(X - nx * 5.5, Y - ny * 5.5, nx, ny, w_)[3:] + toward(X - nx * 5.5, Y - ny * 5.5, nx, ny, w_)[:3] + around(X, Y, 6, w_), lab, within=rm[0].buffer(-1) if rm else None)
            leader(sh, lr, X, Y, INK, 12.0)
        for (x, y), (nx, ny) in SC1[fl]:
            X, Y = f(x, y); w_ = FREG.f.text_length('SC1', fontsize=TXT); pl.text(toward(X, Y, nx, ny, w_) + around(X + nx * 4, Y + ny * 4, 7, w_), 'SC1')
        for (x, y), (nx, ny) in LS1[fl]:
            X, Y = f(x, y); w_ = FREG.f.text_length('LS1', fontsize=TXT); pl.text(toward(X, Y, nx, ny, w_) + around(X + nx * 4, Y + ny * 4, 8, w_), 'LS1')
        place_for_tags(pl, lk)
        ch_tags(pl)
        for X, Y in P1: pl.text(around(X, Y, 8, 12), 'P1')
        if fl == 2: X, Y = f(*SHOWER_L2[1]); pl.text(around(X, Y, 8, 10), 'L2')
        for typ, a, b in runs:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ends = [(a[0] + 4, a[1] + 9), (a[0] - 18, a[1] + 9), (b[0] + 4, b[1] + 9), (b[0] - 18, b[1] - 3), (mx + 5, my + 2.5), (mx - 18, my + 2.5)]
            rm = [g for g in Rs.values() if g.buffer(4).contains(Point(mx, my))]
            pl.text(ends + around(mx, my, 10, 16), typ, within=rm[0].buffer(-1) if rm else None)
        notes += [label for typ, kind, geom, label in our_lights(fl) if label]
        for X, Y, lab in kept:
            if lab: pl.text(around(X, Y, 6, FREG.f.text_length(lab, fontsize=TXT)), lab, TXT, DARKG)
        for t in ('L19',):
            if fl == 1 and not any(w[0] == 'L19' for w in words):
                for p in L19_AT: X, Y = f(*p); pl.text(around(X, Y, 7, 12), 'L19')
        # L16 tags, one per washer
        wpts = cluster([c for k, d, c, r in items if k == 'washer' and 8 <= r.width <= 10 and abs(r.width - r.height) < 3 and not drop(k, c, d, r)], 10.0)
        for c in wpts:
            X, Y = f(*c); pl.text(around(X, Y, 7, 14), 'L16')
        lighting_legend(sh, fl, notes)
    pool_house(doc)
    fix_soft_hyphen(doc)
    doc.set_metadata({'title': 'Casa Grove ID-121, ID-122, ID-131, ID-132, ID-406: RCP and lighting, coordinated with FOR Rev 1', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, len(doc))
    for fl in (1, 2): print('FOR switching not drawn, floor', fl, collections.Counter(r for r, _t in FORLIST[fl]))

def hatch_soffit(sh, g):
    b = g.bounds; s = sh.p.new_shape(); step = 4.0
    x = b[0] - (b[3] - b[1])
    while x < b[2]:
        ln = LineString([(x, b[3]), (x + (b[3] - b[1]), b[1])]).intersection(g)
        if not ln.is_empty and ln.geom_type == 'LineString':
            (x0, y0), (x1, y1) = ln.coords[0], ln.coords[-1]; s.draw_line(fitz.Point(x0, y0), fitz.Point(x1, y1))
        x += step
    s.finish(color=GREY, width=0.3); s.commit()
    outline(sh, g, 0.5, INK)

def legend_block(sh, title, rows, y, notes=(), x=None):
    x = LX0 if x is None else x
    sh.text(x, y, title, idd_std.TXT['header'], INK, bold=True, spacing=1.0); y += 22
    for sym, text in rows:
        sym(sh, x + 12, y - 3)
        for i, t in enumerate(FN.wrap_raw(text, 8.0, LX1 - x - 52)):
            sh.text(x + 40, y + 10.5 * i, t, 8.0, INK, raw=True)
        y += 10.5 * max(1, len(FN.wrap_raw(text, 8.0, LX1 - x - 52))) + 9
    if notes:
        y += 6; sh.text(x, y, 'NOTES', idd_std.TXT['header'], INK, bold=True, spacing=1.0); y += 20
        for i, n in enumerate(notes, 1):
            ls = FN.wrap_raw(n, 8.0, LX1 - x - 22)
            sh.text(x, y, '%d.' % i, 8.0, INK, raw=True)
            for j, t in enumerate(ls): sh.text(x + 16, y + 10.5 * j, t, 8.0, INK, raw=True)
            y += 10.5 * len(ls) + 5
    return y

def _crown(sh, x, y): sh.line((x - 10, y), (x + 10, y), 0.5, INK, dashes='[3 1.5] 0')
def _cove(sh, x, y): sh.line((x - 10, y - 2), (x + 10, y - 2), 0.5, INK, dashes='[3 1.5] 0'); sh.line((x - 10, y + 1.5), (x + 10, y + 1.5), 0.9, INK, dashes='[1.2 1.2] 0')
def _tag(sh, x, y): r = fitz.Rect(x - 13, y - 6.5, x + 13, y + 6.5); sh.p.draw_rect(r, color=INK, width=0.5); sh.text(x, y + 2.5, "9'-10\"", 7.0, INK, align='c', raw=True)
def _trayl(sh, x, y): sh.line((x - 10, y), (x + 10, y), 0.6, INK)
def _soff(sh, x, y):
    r = fitz.Rect(x - 10, y - 5, x + 10, y + 5); s = sh.p.new_shape()
    for i in range(6): s.draw_line(fitz.Point(r.x0 + i * 4, r.y1), fitz.Point(min(r.x1, r.x0 + i * 4 + 10), max(r.y0, r.y1 - 10)))
    s.finish(color=GREY, width=0.3); s.commit(); sh.p.draw_rect(r, color=INK, width=0.5)
SAMPLE = {}                     # FOR's own symbols, drawn in the legends exactly as on the plans: kind -> [(drawing, T, sheet center)]
def _sample(kind):
    def fn(sh, x, y):
        if kind not in SAMPLE: return
        for d, T_, c in SAMPLE[kind]:
            draw_for(sh, d, lambda pt, T_=T_, c=c: fitz.Point(T_(pt).x - c[0] + x, T_(pt).y - c[1] + y), INK)
    return fn
def _down(sh, x, y): downlight(sh, x, y)
def _sc(sh, x, y): wall_sconce(sh, x, y + 3, 0, -1)
def _ls(sh, x, y): wall_sconce(sh, x, y + 3, 0, -1, w=20)
def _lstrip(sh, x, y): sh.line((x - 12, y), (x + 12, y), 1.6, INK, dashes='[6 2 1.5 2] 0')
def _mirror(sh, x, y): sym_line(sh, (x - 10, y), (x + 10, y), None, mirror=True)
def _switch(sh, x, y): draw_switch(sh, x, y)
def _switchg(sh, x, y): draw_switch(sh, x, y, DARKG)
def _pend(sh, x, y): p1_sym(sh, x, y)
def _ch(sh, x, y):
    sh.p.draw_circle(fitz.Point(x, y), 4.5, color=INK, width=0.6); sh.line((x - 7, y), (x + 7, y), 0.5, INK); sh.line((x, y - 7), (x, y + 7), 0.5, INK)
def _sd(sh, x, y): sh.text(x, y + 2.5, 'SD', 7.0, INK, align='c', raw=True)
def _ef(sh, x, y): sh.text(x, y + 2.5, 'EF', 7.0, INK, align='c', raw=True)
def _ap(sh, x, y):
    r = fitz.Rect(x - 12, y - 7, x + 12, y + 7); sh.p.draw_rect(r, color=INK, width=0.6); sh.line((r.x0, r.y0), (r.x1, r.y1), 0.3, INK); sh.line((r.x0, r.y1), (r.x1, r.y0), 0.3, INK)
def _pocket(sh, x, y): sh.p.draw_rect(fitz.Rect(x - 12, y - 2.5, x + 12, y + 2.5), color=INK, width=0.5)
def _diff(sh, x, y):
    sh.p.draw_rect(fitz.Rect(x - 12, y - 2, x + 12, y + 2), color=(0.6, 0.6, 0.6), fill=(0.88, 0.88, 0.88), width=0.45); sh.line((x - 11, y), (x + 11, y), 0.3, (0.6, 0.6, 0.6))
def _ret(sh, x, y):
    sh.p.draw_rect(fitz.Rect(x - 12, y - 3.5, x + 12, y + 3.5), color=(0.6, 0.6, 0.6), fill=(0.88, 0.88, 0.88), width=0.45); sh.line((x - 11, y), (x + 11, y), 0.3, (0.6, 0.6, 0.6))
def _move(sh, x, y):
    sh.p.draw_rect(fitz.Rect(x - 13, y - 2, x - 3, y + 2), color=(0.6, 0.6, 0.6), width=0.45, dashes='[1.5 1.5] 0')
    sh.p.draw_rect(fitz.Rect(x + 3, y - 2, x + 13, y + 2), color=DARKG, fill=(0.88, 0.88, 0.88), width=0.45); sh.line((x - 3, y), (x + 3, y), 0.4, DARKG, dashes='[1 1] 0')

def rcp_legend(sh, fl):
    rows = [(_tag, 'CEILING HEIGHT ABOVE FINISH FLOOR (FOR A-205 / A-206), FINISH, CROWN. "BAND": THE PERIMETER SOFFIT HEIGHT.'),
            (_crown, 'CM-01 CROWN MOLDING, TO THE CEILING (CM-02 1\'-0" IN THE LIVING ROOM).'),
            (_cove, 'CM-01 / CM-02 CROWN HELD 4" BELOW THE CEILING WITH LED COVE LC1 ON ITS TOP (4/ID-502). REPLACES FOR\'S L11, L12, L14 COVE.'),
            (_trayl, 'BAND EDGE: THE PERIMETER BAND (SOFFIT) STEPS UP 4" TO THE FIELD (FOR\'S TRAY).'),
            (_soff, '9" DRYWALL SOFFIT OVER FULL-HEIGHT CABINETS, FLUSH WITH THE CABINET FACE, CROWN ACROSS (1/ID-501).'),
            (_sample('recess'), 'RECESSED DOWNLIGHT (FOR SYMBOL), TYPE TAGGED (FOR A-207a); SCHEDULE ON ID-131 / ID-132.'),
            (_ch, 'CHANDELIER J-BOX CH1, CENTERED IN THE SPACE (FOR).'),
            (_pend, 'ISLAND PENDANT P1 ON A J-BOX, 4-5/8" EAST OF FOR\'S WITH THE ISLAND (ID-243).'),
            (_sd, 'SD SMOKE DETECTOR, SD/CO COMBINATION SMOKE AND CO (FOR, AS TAGGED).'),
            (_ef, 'EF EXHAUST FAN (FOR M-100 / M-101). NO EXHAUST FAN IN THE DOG ROOM (OWNER).'),
            (_diff, 'SUPPLY DIFFUSER (FOR M-100 / M-101, GREY).'),
            (_ret, 'RETURN GRILLE (FOR M-100 / M-101, GREY).'),
            (_move, 'MOVE (FOR/MECH): FOR\'S LOCATION DASHED, OURS SOLID, CLEAR OF THE DRAPERY POCKET, COVE BAND OR HEADBOARD WALL.'),
            (_pocket, 'C-1 MOTORIZED DRAPERY POCKET, 5" (FOR A-403), FULL WIDTH OF THE WALL WHERE OUR ELEVATIONS CALL FOR DRAPERY; POWER AT EACH.')]
    if fl == 1: rows.append((_ap, 'AP: 40" x 24" DEHUMIDIFIER ACCESS PANEL (M-100), CLEAR OF THE L3.'))
    notes = ['CEILINGS 5/8" SAG-RESISTANT GYPSUM BOARD, PT-01 FLAT; MOISTURE-RESISTANT IN WET AREAS (FOR GENERAL NOTE).',
             'CEILING HEIGHTS ARE FOR\'S (A-205, A-206, CLG TAGS ON M-100 / M-101). FOR TO CONFIRM THE TAGS QUESTIONED IN THE COORDINATION MEMO.',
             'KEEP DIFFUSERS, RETURNS, FANS AND DETECTORS CLEAR OF CROWN, COVE, SOFFITS, ART WALLS, DRAPERY POCKETS AND PENDANTS.',
             'NO REVISION CLOUDS ON THIS ISSUE (OWNER).']
    if SMALL.get(fl): notes.insert(2, 'CEILING HEIGHT NOT TAGGED (ROOM TOO SMALL): %s, %s.' % (', '.join(SMALL[fl]), {1: "10'-8\"", 2: "9'-6\""}[fl]))
    if fl == 1: notes.insert(2, 'GALLERY: SLOPED CEILING 9\'-0" AT THE WALLS TO 10\'-8" FLAT (FOR A-411).')
    if fl == 2:
        notes.insert(2, 'LIVING ROOM DOUBLE HEIGHT: 22\'-8" FIELD, 22\'-4" BAND AT THE WINDOW WALL (FOR A-403), CM-02 + LC1.')
        notes.insert(3, 'MASTER BATH: NO DRAPERY POCKET AT THE TUB WINDOW OR THE TERRACE DOOR (STONE TO THE CEILING, OWNER). THE SHOWER L2 SITS 1\'-0" OFF THE RAIN HEAD.')
    legend_block(sh, 'CEILING LEGEND', rows, 64, notes)

def lighting_legend(sh, fl, notes_extra):
    y = 64
    sh.text(LX0, y, 'FIXTURE SCHEDULE', idd_std.TXT['header'], INK, bold=True, spacing=1.0); y += 18
    cols = [LX0, LX0 + 34, LX0 + 270, LX0 + 304]
    for x, t in zip(cols, ('TYPE', 'DESCRIPTION', 'BY', 'NOTES')): sh.text(x, y, t, 7.0, INK, bold=True, raw=True)
    y += 4; sh.line((LX0, y), (LX1, y), 0.5, INK); y += 10
    for typ, desc, src, note in FIXTURES:
        d_ = FN.wrap_raw(desc, 7.0, 230); n_ = FN.wrap_raw(note, 7.0, LX1 - cols[3] - 4)
        sh.text(cols[0], y, typ, 7.0, INK, bold=True, raw=True); sh.text(cols[2], y, src, 7.0, INK, raw=True)
        for i, t in enumerate(d_): sh.text(cols[1], y + 9 * i, t, 7.0, INK, raw=True)
        for i, t in enumerate(n_): sh.text(cols[3], y + 9 * i, t, 7.0, INK, raw=True)
        y += 9 * max(len(d_), len(n_)) + 4
        sh.line((LX0, y - 8.2), (LX1, y - 8.2), 0.25, LIGHT)
    y += 14
    rows = [(_sample('recess'), 'CEILING DOWNLIGHT (FOR SYMBOL, TYPE TAGGED).'),
            (_ch, 'CHANDELIER CH1 ON FOR\'S J-BOX, CENTERED IN THE SPACE.'),
            (_pend, 'ISLAND PENDANT P1 ON A J-BOX.'),
            (_sample('washer'), 'L16 TRIMLESS WALL WASHER, AIMED AT THE WALL (FOR SYMBOL).'),
            (_sample('sconce'), 'FOR\'S WALL FIXTURE ON A J-BOX (L19, FOR SCONCES WE KEEP).'),
            (_sc, 'SC1 DECORATIVE SCONCE ON A J-BOX, ON THE WALL; HEIGHT PER THE ELEVATIONS.'),
            (_ls, 'LS1 24" LINEAR SCONCE ON A J-BOX OVER THE MIRROR.'),
            (_lstrip, 'LED TAPE OR COVE (LC1, LS2; FOR L7 / L8 / L13).'),
            (_mirror, 'LM1 BACKLIT LED MIRROR, FEED BEHIND THE MIRROR.'),
            (_switch, 'SWITCH PER OUR ELEVATIONS, CL 4\'-0" UNLESS NOTED: S SINGLE POLE, S2 TWO-GANG (LIGHT AND FAN), S3 THREE-WAY, S4 FOUR-WAY, '
                      'D DIMMER, F FAN, S/D, S/F TWO DEVICES SIDE BY SIDE. LC1 AND DECORATIVE FIXTURES ON DIMMERS.'),
            (_switchg, 'FOR\'S SWITCHING (E-300 / E-301, GREY: 3 THREE-WAY, D DIMMER, 3D THREE-WAY DIMMER) IN ROOMS WE HAVE NOT ELEVATED YET.')]
    notes = ['FIXTURES FOR SHOWS THAT OURS DOES NOT CHANGE ARE ADOPTED AS DRAWN BY FOR (A-205, A-206); FOR\'S FIXTURES AND SWITCHING WE REPLACE OR DELETE ARE '
             'LEFT OFF THIS PLAN AND LISTED FOR FOR (COORDINATION MEMO).'] + notes_extra + \
            (['ISLAND PENDANTS P1: FOR\'S THREE J-BOXES MOVE 4-5/8" EAST WITH THE ISLAND (ID-243).',
              'STAIR: FOR\'S SCONCE ON THE LOWER-FLIGHT WALL (OUR HALF WALL, ID-230 NOTE 7) IS DELETED.',
              'NO L8 AT THE LAUNDRY SINK OR THE BACK HALL LOCKERS: NO CABINETS ABOVE.',
              'ENTRY, OFFICE, GUEST BEDROOM: LC1 ON THE CROWN IN PLACE OF FOR\'S L11 / L4 BAND.']
             if fl == 1 else
             ['BEDROOMS 2 AND 3, DEN: FOR\'S WALL SCONCES DELETED (OUR ELEVATIONS SHOW NONE).',
              'BEDROOMS 2, 3, MASTER BEDROOM, LIVING ROOM: LC1 ON THE CROWN IN PLACE OF FOR\'S L12 / L14.',
              'MASTER W.I.C.: LS2 IN THE MILLWORK FOR FOR\'S L13, CH1 OVER THE ISLAND, LM1 AT THE VANITY (ID-330 TO 333).'])
    legend_block(sh, 'SYMBOLS', rows, y, notes)

# ------------------------------------------------------------------ pool house
def pool_house(doc):
    import build_poolhouse_rcp as PH
    PH.sheet(doc)

if __name__ == '__main__':
    build()
