"""Secondary bedrooms on FOR REV 1, one sheet per room in place of the typical sheet (261102.HD102.TypicalBedroom.pdf, drawn on the
designer's base). Owner 11.07.26 (room blocks): ID-260 guest bedroom and guest bath key plan, ID-261 guest bedroom (738A); ID-340 bedroom 2
and bath 2 key plan, ID-341 bedroom 2 (738B); ID-350 bedroom 3 and bath 3 key plan, ID-351 bedroom 3 (738C). The baths' elevations are ID-262,
ID-342 and ID-352 (build_baths_rev1.py).
The design language is the typical sheet's (Zack 11.02.26): dado wainscot only, 3" cap with its top at 3'-4", wallpaper WC-01 above to
the CM-01 crown, outlets vertical CL 1'-6" centered in the dado boxes, no sconces, a TV-ready power and data outlet CL 5'-0" opposite the
bed, tall windows (stool 1'-6", head 8'-0", VERIFY), trim from the trim block. Output: 261106.HD102.Bedrooms.pdf

PLAN, measured from FOR's vectors (A-DOOR, A-WINDOW, A-WALL-*) and a 576 dpi raster scan of the partitions, FOR sheet pt, 1.5 pt per inch,
plan north = up the FOR sheet:
  GUEST BEDROOM (A-201)  west face 356.2 (CMU block 341.2 to 353.2), east face 619.2 (partition 619.2 to 626.2), north face 650.6
                         (partition 640.0 to 650.6), south face 804.7 (partition 804.7 to 815.2): 14'-7-3/8" x 8'-6-3/4"
      east     entry 16: leaf 742.7 to 796.7 (3'-0", arc r 54), hinged south, swings in
      west     exterior door 02: leaf 751.1 to 799.1 (2'-8", arc r 48), hinged south, swings out; window 656.6 to 730.1 (4'-1")
      south    W.I.C. door 11: leaf 550.3 to 598.3 (2'-8", jambs 547.3 to 601.3), hinged east, swings into the W.I.C.;
               bath door 11: leaf 364.4 to 412.4 (2'-8", jambs 361.4 to 415.4), hinged west, swings into the bath
  BEDROOM 2 (A-202)      west face 446.2 (CMU 431.2 to 443.2), east face 691.2 (partition 691.2 to 698.2), north face 457.1 (bath 2 wall
                         450.1 to 457.1, the built-in front A-NEW-MILLWORK 457.1), south face 637.4 (partition 637.4 to 644.3):
                         13'-7-3/8" x 10'-0-1/4"
      north    bath 2 door 20: leaf 480.7 to 528.7 (2'-8", arc r 48), hinged east, swings into the bath; wall end 531.7 to 543.1;
               FOR's built-in cabinets 543.1 to 691.2 (8'-2-3/4" x 2'-0", 419.6 to 457.1), facing the room
      east     entry 24: leaf 465.4 to 516.4 (2'-10", arc r 51), hinged north, swings in; open, it stands 6-1/2" off the built-in fronts
      west     windows 469.2 to 508.2 and 586.3 to 625.3 (2'-2" each, block gaps), 8" from each end, 52" pier
  BEDROOM 3 (A-202)      west face 543.1 (bath 3 wall 536.2 to 543.1), east face 764.2 (drywall on CMU 767.2 to 779.2), north face 137.0
                         (CMU 122.0 to 134.0), south face 376.0 (the built-in front): 12'-3-3/8" x 13'-3-3/8"
      vestibule x 698.2 (the stub wall 691.2 to 698.2) to 764.2, y 376.0 to 449.5: 3'-8" x 4'-1", open to the room
      north    no openings
      east     the window pair 214.9 to 356.9 (block gap 7'-10-5/8", two units), the wall runs on into the vestibule to 449.5
      south    FOR's built-in cabinets 543.1 to 691.2 (8'-2-3/4" x 2'-0", 376.0 to 413.2); the vestibule's back wall with entry 24:
               leaf 705.7 to 756.7 (2'-10", arc r 51), hinged east, swings in (north)
      west     bath 3 door 20: leaf 144.5 to 192.5 (2'-8", arc r 48), hinged north, swings into the bath
Heights per FOR Rev 1 (coordination 11.09.26, coord/heights.json): guest bedroom ceiling 10'-8" (A-205, 10'-4" cove band), bedrooms 2 and 3
9'-10" (A-206, 9'-6" band). Owner 11.09.26: crown kept, held 4" below the ceiling with an LED cove on its top (FOR's L11/L12 cove).
Windows per FOR A-600, heads 8'-0": D (guest) 4'-1" x 6'-2-1/4", sill 1'-9-3/4"; J x2 (bedroom 2) 2'-2-1/2" x 4'-4-5/8", sill 3'-7-3/8";
H (bedroom 3) 8'-0" x 6'-0" XO slider, sill 2'-0". D, H and J are FOR's egress windows."""
import sys, math
sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std
import idd_sheet
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, TRIM
from build_kitchen import wrap, NOTE
from idd_sheet import ps
NOTE_LH = ps(NOTE) + 2.2                     # line pitch for the printed note size

def draw_views(sh, cells, views, scale='1/2', ceiling=None):
    """build_kitchen.draw_views with the line pitch set for the 11 x 17 print size."""
    k = E.SCALES[scale]
    for cell, (n, title, L, fn, extra) in zip(cells, views):
        h0, c0 = H, COVE
        if hasattr(fn, 'h'): set_room(fn.h)                                   # a view at FOR's band height (review 11.09.26)
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" TO 1\'-0"' % scale)
        spec = {'room': 'BEDROOM', 'view': title, 'length': L + extra, 'ceiling': ceiling or H}
        probe = E.ElevationView(Sheet(fitz.open()).p, sh.font, sh.fontname, (0, 0), k, spec)
        text = fn(probe) + ((' ' + fn.note) if hasattr(fn, 'note') else '')
        width = min(cell[2] - cell[0] - 16, 660)
        lines_ = wrap(text, NOTE, width)
        top = 28 + len(lines_) * NOTE_LH + 10
        origin = E.fit_origin(cell, spec, k, top=top)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        fn(v)
        v.dim_v(0, H, v.X(L + extra) + 40, [0, H])                             # overall height, floor to ceiling (review 11.09.26)
        v.text(v.X(0) - 6, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 30
        for ln in lines_: sh.text(cell[2] - 8, ny, ln, NOTE, MID, align='r'); ny += NOTE_LH
        set_room(h0, c0)

def para_block(sh, x, y, paras, width, size=NOTE, lh=None, head_color=INK):
    lh = lh or ps(size) + 2.2
    for p_ in paras:
        head = isinstance(p_, tuple); text = p_[1] if head else p_
        if text == '': y += lh / 2; continue
        for ln in wrap(text, size, width): sh.text(x, y, ln, size, head_color if head else MID, bold=head); y += lh
    return y

def quad_marker(sh, cx, cy, sheet, views, r=24.0):
    """Four-way elevation marker sized for the 11 x 17 print (owner 11.07.26: bigger tags): radius 24, text scaled with the radius."""
    f = r / 16.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.8, fill=(1, 1, 1)); s_.commit()
    sh.text(cx, cy + 2.5 * f, sheet.replace('ID-', ''), 7.0 * f, INK, align='c', raw=True)
    for d, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d]
        tip = (cx + dx * (r + 7 * f), cy + dy * (r + 7 * f))
        b1 = (cx + dx * r - dy * 4.0 * f, cy + dy * r + dx * 4.0 * f); b2 = (cx + dx * r + dy * 4.0 * f, cy + dy * r - dx * 4.0 * f)
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
        sh.text(cx + dx * r * 0.70, cy + dy * r * 0.70 + 2.5 * f, str(n), 7.0 * f, INK, align='c', raw=True)

def plan_label(sh, t, title, pt_per_ft, label):
    """Under a key plan: its title, then the scale bar with 24 pt of clear space above it (owner 11.07.26: the scale had no room)."""
    sh.text(t.x0, t.y1 + 30, title, 8.0, INK)
    sh.scale_bar(t.x0, t.y1 + 62, pt_per_ft=pt_per_ft, label=label)
    return t.y1 + 74
import base_rev1 as BR, keyclip as KC
OUT = '/home/claude/flrwork/261106.HD102.Bedrooms.pdf'
ISSUE = '11.06.26'
IN = 1.5
H = 120.0; HEAD = 96.0; COVE = 4.0                 # H set per room by set_room(); COVE: crown top this far below the ceiling, LED on top
CS = TRIM['casing']; BASE = TRIM['base']; CAP = TRIM['dado']; M = TRIM['margin']; CR = TRIM['crown']
SILL = 18.0; OUT_CL = 18.0; SW = 48.0; TV_CL = 60.0; EM = 6.0
S3_BED = 34.0                                    # bedside three-way CL 2'-10": plate top 3'-0-1/4", 3/4" under the cap (underside 3'-1")
UW_CL = 11.0                                     # duplex under a window: horizontal, CL 11" between the base (8-1/2") and the apron (1'-1-1/2")
NS = 24.0; NS_GAP = 1.0; HB_W, HB_H = 76.0, 54.0
TOP = H - COVE - CR - 1.0                        # built-in top, 1" scribe under the crown

def set_room(h, cove=4.0):
    """Room height per FOR (coordination 11.09.26) and the crown cove drop; the built-in top follows."""
    global H, COVE, TOP
    H, COVE = h, cove; TOP = H - COVE - CR - 1.0

H_F1, H_F2 = 128.0, 118.0
SILL_D, SILL_J, SILL_H = 21.75, 43.375, 24.0       # FOR A-600: D 1'-9-3/4", J 3'-7-3/8", H 2'-0" (heads 8'-0")
TOE = 4.0; RAIL = 84.0

def r8(x): return round(x * 8) / 8
def F(x): return E.ftin(r8(x))
def tag(v, x, y, s, size=5.0, c=MID, box=False):
    if box:
        w = v.F.text_length(s, fontsize=size); hz = ps(size)
        v.p.draw_rect(fitz.Rect(v.X(x) - w / 2 - 2.5, v.Y(y) - hz * 0.95, v.X(x) + w / 2 + 2.5, v.Y(y) + 2.2), color=MID, fill=(1, 1, 1), width=0.4)
    v.text(v.X(x), v.Y(y), s, size, c, align='c')

def dimh(v, y, pts):
    """Horizontal string as E.dim_h, but a label wider than its segment is set below the string, clear of the ticks."""
    E.check_string(pts, v.w.get('room'), v.w.get('view'))
    xs = [v.X(p) for p in pts]
    v.line((xs[0], y), (xs[-1], y), 0.4)
    for x in xs:
        v.line((x, y - 3), (x, y + 3), 0.4); v.line((x - 1.8, y + 1.8), (x + 1.8, y - 1.8), 0.6)
    last = -1e9                                                                # right edge of the last label set below the string
    for a, b in zip(pts, pts[1:]):
        if b - a < 0.5: continue
        s_ = E.ftin(r8(b - a)); seg = (b - a) * v.k; mid = (v.X(a) + v.X(b)) / 2
        sz = 5.5 if seg >= 30 else 5.0; wl = v.F.text_length(s_, fontsize=sz)
        if wl + 6 <= seg: v.text(mid, y - 2.5, s_, sz, align='c'); continue
        x = max(mid, last + wl / 2 + 4)                                         # below the string, clear of the ticks and the last label
        v.line((mid, y + 1.5), (x, y + 6.0), 0.3, MID)
        v.text(x, y + 12.0, s_, 5.0, align='c'); last = x + wl / 2

def shell(v, L, base=None, crown=None, right='cut'):
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    for a, b in (base if base is not None else [(0, L)]):
        if b - a > 0.5: C.base(v, a, b)
    for a, b in (crown if crown is not None else [(0, L)]):
        C.crown(v, a, b, H - COVE)
        if COVE > 0: C._line(v, (a + 1.0, H - COVE + 0.6), (b - 1.0, H - COVE + 0.6), C.FINE, MID, '[1.5 1.0] 0')   # LED strip on the crown top
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    if right == 'cut': v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    else: v.line((X1, Y0), (X1, Y1), 0.9)                                   # an outside corner: the wall ends, the room beyond

def casing2(v, x, w, head, csl=CS, csr=CS, sill=0):
    """C.casing with each leg its own width: a leg narrowed at a corner butts the 5" head, a 5" leg miters into it."""
    C._rect(v, x - csl, sill, x, head + CS, C.OUTLINE); C._rect(v, x + w, sill, x + w + csr, head + CS, C.OUTLINE)
    C._rect(v, x - csl, head, x + w + csr, head + CS, C.OUTLINE)
    if csl == CS: C._line(v, (x - csl, head + CS), (x, head), C.FINE, MID)
    else: C._line(v, (x - csl, head), (x, head), C.FINE, MID)
    if csr == CS: C._line(v, (x + w + csr, head + CS), (x + w, head), C.FINE, MID)
    else: C._line(v, (x + w, head), (x + w + csr, head), C.FINE, MID)
    C._rect(v, x - 0.25, sill, x + w + 0.25, head + 0.25, C.FINE, MID)
    C._line(v, (x - csl + 1.0, sill), (x - csl + 1.0, head + CS - 1.0), C.FINE, C.LIGHT); C._line(v, (x + w + csr - 1.0, sill), (x + w + csr - 1.0, head + CS - 1.0), C.FINE, C.LIGHT)
    C._line(v, (x - csl + 1.0, head + CS - 1.0), (x + w + csr - 1.0, head + CS - 1.0), C.FINE, C.LIGHT)

def window2(v, x, w, lites=1, csl=CS, csr=CS, lo=None, hi=None, sill=None, apron=True, hung=False):
    """C.window with its own leg widths, the stool horns kept inside the wall (lo, hi). sill: FOR's sill for this window (A-600);
    apron=False where the stool sits just above the dado cap."""
    SILL = globals()['SILL'] if sill is None else sill
    casing2(v, x, w, HEAD, csl, csr, SILL)
    s0, s1 = x - csl - 0.75, x + w + csr + 0.75
    if lo is not None: s0 = max(s0, lo)
    if hi is not None: s1 = min(s1, hi)
    C._rect(v, s0, SILL - 1.5, s1, SILL, C.OUTLINE)
    if apron: C._rect(v, x - csl + 0.5, SILL - 1.5 - TRIM['cap'], x + w + csr - 0.5, SILL - 1.5, C.OUTLINE)
    C._rect(v, x, SILL, x + w, HEAD, C.OUTLINE); lw = w / lites
    if hung:                                                                  # single hung: lower sash under a meeting rail, fixed upper (review 11.09.26)
        mr = r8((SILL + HEAD) / 2)
        C._rect(v, x + 1.25, mr - 1.0, x + w - 1.25, mr + 1.0, C.MED, fill=(1, 1, 1))
        for a_, b_ in ((SILL + 1.25, mr - 1.0), (mr + 1.0, HEAD - 1.25)):
            C._rect(v, x + 1.25, a_, x + w - 1.25, b_, C.MED); C.glazing(v, x + 1.25, a_, x + w - 1.25, b_)
    else:
      for i in range(lites):
        gx = x + i * lw; C._rect(v, gx + 1.25, SILL + 1.25, gx + lw - 1.25, HEAD - 1.25, C.MED)
        C.glazing(v, gx + 1.25, SILL + 1.25, gx + lw - 1.25, HEAD - 1.25)        # divided lites (owner 11.09.26: all windows and glass doors match)
    cx0 = x - csl if lo is None else max(x - csl, lo + 2.0); cx1 = x + w + csr if hi is None else min(x + w + csr, hi - 2.0)   # cloud kept inside the wall, clear of the dimension string
    C.rev_cloud(v, cx0, SILL - 1.5 - (TRIM['cap'] if apron else 0), cx1, HEAD + CS, pad=2.0)

def under_window(v, x):
    C.outlet(v, x, UW_CL, horizontal=True)

def door(v, x, w, hinge, label=None, csl=CS, csr=CS, swing_in=False):
    """Door with casing. The swing marks meet at the hinge side, solid when the door swings toward the viewer (into the room),
    dashed when it swings away."""
    casing2(v, x, w, HEAD, csl, csr)
    st, rb, rt = 4.5, 9, 4.5                                                   # the leaf, as C.door_leaf (one panel), without its dashed marks
    C._rect(v, x, 0, x + w, HEAD, C.OUTLINE)
    C._rect(v, x + st, rb, x + w - st, HEAD - rt, C.MED); C._rect(v, x + st + 0.75, rb + 0.75, x + w - st - 0.75, HEAD - rt - 0.75, C.FINE, MID)
    h_, far = (x, x + w) if hinge == 'L' else (x + w, x)
    dash = None if swing_in else '[5 3.5] 0'                                   # solid toward the viewer, dashed away
    C._line(v, (far, 0), (h_, HEAD / 2), C.FINE, MID, dash); C._line(v, (far, HEAD), (h_, HEAD / 2), C.FINE, MID, dash)
    lever = far - 3 if far > h_ else far + 3
    C._ellipse(v, lever, 38, 0.9, 0.9, C.FINE); C._line(v, (lever, 38), (lever + (-3.5 if far > h_ else 3.5), 38), C.MED)
    if label: tag(v, x + w / 2, HEAD + CS + 2.2, label)          # between the head casing and the crown (review 11.09.26)

def sw(v, cx, cy):
    """Switch plate with its tag below the plate, clear of the cap."""
    C.switch(v, cx, cy, None); v.text(v.X(cx), v.Y(cy - 2.25) + 6.2, 'S3', 5.0, MID, align='c')

def usb(v, cx):
    C._rect(v, cx - 1.4, OUT_CL - 2.25, cx + 1.4, OUT_CL + 2.25, C.OUTLINE, INK, fill=(1, 1, 1), dashes='[1.2 0.8] 0')   # behind the nightstand

def wardrobe(v, a, b, tv=None):
    """FOR's built-in drawn as painted inset millwork: 1" scribes, a 4" recessed toe, two tall door pairs to 7'-0", a rail, upper pairs
    to 9'-3" under the crown. tv = (pair index from the left, 'L' or 'R' leaf): TV-ready power and data on the back panel behind that
    leaf at CL 5'-0" (dashed)."""
    C._rect(v, a, 0, b, TOP, C.OUTLINE, fill=(1, 1, 1))
    C._rect(v, a + 1.0, 0.5, b - 1.0, TOE, C.MED)
    inner = b - a - 2.0; n = 2 if inner > 72 else 1; w = inner / n
    for i in range(n):
        x = a + 1.0 + i * w
        K.door_pair_cab(v, x, w, TOE, RAIL); K.door_pair_cab(v, x, w, RAIL + 1.0, TOP - 0.5, pulls=False)
    C._line(v, (a, TOP), (b, TOP), C.OUTLINE)
    if tv:
        i, leaf = tv; c = a + 1.0 + i * w + (w / 4 if leaf == 'L' else 3 * w / 4)
        C._rect(v, c - 6.0, TV_CL - 3.0, c + 6.0, TV_CL + 3.0, C.FINE, MID, dashes='[2 1.5] 0')
        tag(v, c, TV_CL + 6.0, 'TV-READY', 5.0, MID, box=True)
        return c

def dado(v, L, cuts, centered=None, em=None):
    return C.panel_wall(v, 0, L, H, openings=cuts, centered=centered, end_margin=em, dado=True, target=24.0, upper=False)

def outer_outlets(v, boxes):
    if not boxes: return []
    xs = sorted({(boxes[0][0] + boxes[0][1]) / 2, (boxes[-1][0] + boxes[-1][1]) / 2})
    for x in xs: C.outlet(v, x, OUT_CL)
    return xs

def paper(v, L, x=None, y=104.0):
    tag(v, L / 2 if x is None else x, y, 'WC-01', 6.0, INK, box=True)

def bed_wall(v, L, bc, s3_at):
    """Headboard wall: bed centered on bc, 24" nightstands 1" off the bed, USB duplexes in the dado boxes behind them, the bedside
    three-way CL 2'-10" in the end margin nearest the entry (s3_at 'L' or 'R')."""
    boxes = dado(v, L, [], centered=bc, em=EM)
    C.bed_king(v, bc, HB_W, HB_H)
    n0, n1 = bc - HB_W / 2 - NS_GAP - NS, bc + HB_W / 2 + NS_GAP
    C.nightstand(v, n0, NS); C.nightstand(v, n1, NS)
    for nc in (n0 + NS / 2, n1 + NS / 2):
        bx = min(boxes, key=lambda b_: abs((b_[0] + b_[1]) / 2 - nc)); usb(v, (bx[0] + bx[1]) / 2)
    sw(v, EM / 2 if s3_at == 'L' else L - EM / 2, S3_BED)
    paper(v, L, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, n0, n0 + NS, bc, n1, n1 + NS, L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, S3_BED, CAP, HB_H, H - COVE - CR, H - COVE, H]))

BED_TXT = ('BED CENTERED, USB DUPLEX BEHIND EACH NIGHTSTAND CL 1\'-6", BEDSIDE THREE-WAY CL 2\'-10". '
           'DADO WAINSCOT, CAP AT 3\'-4", WC-01 ABOVE, CM-01 CROWN WITH LED COVE ABOVE, SEE 4/ID-502.')

# ------------------------------------------------------------------ guest bedroom, ID-738A
GW, GE, GN, GS = 356.2, 619.2, 650.6, 804.7
def guest_north(v):
    L = r8((GE - GW) / IN)
    shell(v, L); bed_wall(v, L, L / 2, 'R')
    return 'HEADBOARD WALL. ' + BED_TXT

def guest_east(v):
    L = r8((GS - GN) / IN)
    d = (r8((742.7 - GN) / IN), r8((742.7 - GN) / IN) + 36.0)
    shell(v, L, base=[(0, d[0] - CS)])
    door(v, d[0], 36.0, 'R', '16', swing_in=True)
    boxes = dado(v, L, [(d[0] - CS, L)])
    outer_outlets(v, boxes[:1]); sw(v, d[0] - CS - M / 2 - 0.5, SW)
    paper(v, L, x=d[0] / 2)
    dimh(v, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, SW, CAP, HEAD, HEAD + CS, H - COVE, H]))
    return 'ENTRY 16, %s x 8\'-0", SWINGS IN. THREE-WAY DIMMER CL 4\'-0" AT THE LATCH. WC-01 ABOVE THE CAP.' % F(36.0)

def guest_south(v):
    L = r8((GE - GW) / IN); n = GE
    wic = (r8((n - 598.3) / IN), r8((n - 598.3) / IN) + 32.0)
    bath = (r8((n - 412.4) / IN), r8((n - 412.4) / IN) + 32.0)
    shell(v, L, base=[(0, wic[0] - CS), (wic[1] + CS, bath[0] - CS), (bath[1] + CS, L)])
    door(v, wic[0], 32.0, 'L', '11 W.I.C.'); door(v, bath[0], 32.0, 'R', '11 BATH')
    boxes = dado(v, L, [(0, wic[1] + CS), (bath[0] - CS, L)], centered=(wic[1] + bath[0]) / 2)
    c = (wic[1] + CS + bath[0] - CS) / 2
    outer_outlets(v, boxes)
    C.outlet(v, c - 6, TV_CL); C.data_jack(v, c + 6, TV_CL)
    C._rect(v, c - 24, TV_CL - 12, c + 24, TV_CL + 12, C.FINE, MID, dashes='[3 2] 0')
    bx = bath[0] - CS - 3.0                                                     # bath light and fan, two-gang, at the latch (hinge west)
    C._rect(v, bx - 2.4, SW - 2.25, bx + 2.4, SW + 2.25, C.OUTLINE, fill=(1, 1, 1))
    for dx_ in (-1.1, 1.1): C._rect(v, bx + dx_ - 0.45, SW - 1.0, bx + dx_ + 0.45, SW + 1.0, C.FINE)
    v.text(v.X(bx), v.Y(SW - 2.25) + 6.2, 'S2', 5.0, MID, align='c')
    tag(v, c, TV_CL + 16, 'TV-READY, BLOCKING (DASHED)')
    paper(v, L, x=c, y=100.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, wic[0], wic[1], c, bath[0], bath[1], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, SW, TV_CL, HEAD, HEAD + CS, H - COVE, H]))
    return ('W.I.C. DOOR 11 AND BATH DOOR 11, %s x 8\'-0". TV-READY POWER AND DATA (2 CAT6, 1 COAX) CL 5\'-0", 2x10 BLOCKING. '
            'BATH LIGHT AND FAN SWITCHES (S2) CL 4\'-0" AT THE BATH DOOR LATCH.' % F(32.0))

def guest_west(v):
    L = r8((GS - GN) / IN); n = GS
    d = (r8((n - 799.1) / IN), r8((n - 799.1) / IN) + 32.0)
    w = (r8((n - 730.1) / IN), r8((n - 730.1) / IN) + r8((730.1 - 656.6) / IN))
    dcs = r8(d[0] - 0.25); wcs = r8(L - w[1] - 0.25)                                  # the two corner legs only: 3-1/2" and 3-3/4"
    gap = w[0] - CS - (d[1] + CS)
    shell(v, L, base=[(d[1] + CS, L)])
    door(v, d[0], 32.0, 'L', '02', csl=dcs)
    window2(v, w[0], w[1] - w[0], csr=wcs, hi=L, sill=SILL_D, hung=True)
    under_window(v, (w[0] + w[1]) / 2)
    mr = r8((SILL_D + HEAD) / 2); gx0, gx1, gy0, gy1 = w[0] + 1.25, w[1] - 1.25, SILL_D + 1.25, mr - 1.0
    nc, nr = C.lite_grid(gx1 - gx0, gy1 - gy0); pw_, ph_ = (gx1 - gx0) / nc, (gy1 - gy0) / nr
    tag(v, gx0 + pw_ / 2, gy0 + ph_ / 2 - 1.0, 'TEMPERED', 4.5, INK, box=True)   # centered in a lower pane, clear of the muntins
    C._rect(v, 0, H - 4, L, H, C.FINE, MID, dashes='[2 1.5] 0')
    paper(v, L, x=(w[0] + w[1]) / 2, y=106.5)
    dimh(v, v.Y(0) + 14, E.snap_points([0, d[0], d[1], w[0], w[1], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, UW_CL, SILL_D, HEAD, HEAD + CS, H - 4, H]))
    return ('EXTERIOR DOOR 02 AND WINDOW D PER FOR A-600 (EGRESS), 4\'-1" x 6\'-2-1/4" SINGLE HUNG, IMPACT-RATED, TEMPERED. STOOL 1\'-9-3/4", HEAD 8\'-0". CORNER CASING LEGS NARROWED AS DIMENSIONED. '
            'NO DADO. DUPLEX UNDER THE WINDOW CL 11". DRAPERY POCKET 4" FULL WIDTH (DASHED).')

# ------------------------------------------------------------------ bedroom 2, ID-738B
B2W, B2E, B2N, B2S = 446.2, 691.2, 457.1, 637.4
def b2_north(v):
    L = r8((B2E - B2W) / IN)
    d = (r8((480.7 - B2W) / IN), r8((480.7 - B2W) / IN) + 32.0)
    bi = (r8((543.1 - B2W) / IN), L)
    shell(v, L, base=[(0, d[0] - CS), (d[1] + CS, bi[0])])
    door(v, d[0], 32.0, 'R', '20 BATH 2')
    tvx = wardrobe(v, bi[0], bi[1], tv=(0, 'L'))
    boxes = dado(v, L, [(d[0] - CS, L)])
    seg = [b_ for b_ in boxes if b_[1] <= d[0] - CS]
    ox = (seg[0][0] + seg[0][1]) / 2 if seg else (d[0] - CS) / 2
    C.outlet(v, ox, OUT_CL)
    paper(v, L, x=d[0] / 2 + 2, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, d[0], d[1], bi[0], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TOE, OUT_CL, TV_CL, RAIL, HEAD, TOP, H]))
    return ('BATH 2 DOOR 20, %s x 8\'-0". BUILT-IN: PAINTED INSET, 2\'-0" DEEP, 4" TOE, TALL PAIRS TO 7\'-0" WITH ROD AND SHELF, UPPERS TO %s UNDER THE CROWN. '
            'TV-READY POWER AND DATA BEHIND THE WEST LEAF CL 5\'-0".' % (F(32.0), F(TOP)))

def b2_east(v):
    L = r8((B2S - B2N) / IN)
    d = (r8((465.4 - B2N) / IN), r8((465.4 - B2N) / IN) + 34.0)
    shell(v, L, base=[(d[1] + CS, L)])
    door(v, d[0], 34.0, 'L', '24', swing_in=True)
    boxes = dado(v, L, [(0, d[1] + CS)])
    outer_outlets(v, boxes); sw(v, d[1] + CS + M / 2 + 0.5, SW)
    paper(v, L, x=(d[1] + L) / 2, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, SW, CAP, HEAD, HEAD + CS, H - COVE, H]))
    return 'ENTRY 24, %s x 8\'-0", SWINGS IN. THREE-WAY DIMMER CL 4\'-0" AT THE LATCH. WC-01 ABOVE THE CAP.' % F(34.0)

def b2_south(v):
    L = r8((B2E - B2W) / IN)
    shell(v, L); bed_wall(v, L, L / 2, 'L')
    return 'HEADBOARD WALL. ' + BED_TXT

def b2_west(v):
    L = r8((B2S - B2N) / IN); n = B2S
    ws = [(r8((n - 625.3) / IN), r8((n - 625.3) / IN) + 26.0), (r8((n - 508.2) / IN), r8((n - 508.2) / IN) + 26.0)]
    shell(v, L)
    boxes = dado(v, L, [], centered=L / 2)                                     # FOR's sills (3'-7-3/8") clear the cap: the dado runs under the windows
    for a, b in ws: window2(v, a, b - a, lites=1, sill=SILL_J, apron=False)
    pier = [bx for bx in boxes if ws[0][1] < bx[0] and bx[1] < ws[1][0]]
    if pier: C.outlet(v, (pier[len(pier) // 2][0] + pier[len(pier) // 2][1]) / 2, OUT_CL)
    C._rect(v, 0, H - 4, L, H, C.FINE, MID, dashes='[2 1.5] 0')
    paper(v, L, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, ws[0][0], ws[0][1], ws[1][0], ws[1][1], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, SILL_J, HEAD, HEAD + CS, H - 4, H]))
    return ('TWO WINDOWS J PER FOR A-600 (EGRESS), 2\'-2-1/2" x 4\'-4-5/8", IMPACT-RATED, STOOL 3\'-7-3/8", HEAD 8\'-0", 5" CASING, '
            'STOOL ABOVE THE DADO CAP, NO APRON, DADO CONTINUOUS UNDER THE WINDOWS. DRAPERY POCKET 4" FULL WIDTH (DASHED).')

# ------------------------------------------------------------------ bedroom 3, ID-738C
B3W, B3E, B3N, B3S, VW, VS = 543.1, 764.2, 137.0, 376.0, 698.2, 449.5
def b3_north(v):
    L = r8((B3E - B3W) / IN)
    shell(v, L); bed_wall(v, L, L / 2, 'R')
    return 'HEADBOARD WALL. ' + BED_TXT

def b3_east(v):
    L = r8((VS - B3N) / IN)
    w = (r8((214.9 - B3N) / IN), r8((214.9 - B3N) / IN) + r8((356.9 - 214.9) / IN))
    vs = r8((B3S - B3N) / IN)
    shell(v, L)
    window2(v, w[0], w[1] - w[0], lites=2, sill=SILL_H)
    boxes = dado(v, L, [(w[0] - CS, w[1] + CS)])
    for b_ in (boxes[0], min((b_ for b_ in boxes if b_[0] > w[1]), key=lambda b_: b_[0])): C.outlet(v, (b_[0] + b_[1]) / 2, OUT_CL)
    under_window(v, (w[0] + w[1]) / 2)
    C._line(v, (vs, 0.3), (vs, H - COVE - CR), C.FINE, MID, '[3 2] 0'); tag(v, (vs + L) / 2, 80.0, 'VESTIBULE')
    C._rect(v, 0, H - 4, L, H, C.FINE, MID, dashes='[2 1.5] 0')
    paper(v, L, x=w[0] / 2, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, w[0], (w[0] + w[1]) / 2, w[1], vs, L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, UW_CL, OUT_CL, SILL_H, CAP, HEAD, HEAD + CS, H - 4, H]))
    return ('WINDOW H PER FOR A-600 (EGRESS), 8\'-0" x 6\'-0" XO SLIDER, IMPACT-RATED, STOOL 2\'-0" (MEETS THE 24" MINIMUM, NO LIMITER), '
            'HEAD 8\'-0", ONE 5" CASING. DUPLEX UNDER THE WINDOW CL 11". '
            'DRAPERY POCKET 4" FULL WIDTH (DASHED).')

def b3_south(v):
    L = r8((B3E - B3W) / IN); n = B3E
    vo = r8((n - VW) / IN)                                                     # the vestibule opening, 3'-8"
    st = r8((n - 691.2) / IN)                                                  # the stub wall end
    d = (r8((n - 756.7) / IN), r8((n - 756.7) / IN) + 34.0)
    shell(v, L, base=[], crown=[(0, L)])
    C._rect(v, vo, 0, st, H - COVE - CR, C.OUTLINE, (0.3, 0.3, 0.3), fill=(0.3, 0.3, 0.3))   # the stub wall, cut
    door(v, d[0], 34.0, 'L', None, swing_in=True)
    tag(v, vo / 2, 104.5, 'ENTRY 24, 4\'-1" BEYOND', 5.0, MID, box=True)
    tvx = wardrobe(v, st, L, tv=(0, 'L'))
    dimh(v, v.Y(0) + 14, E.snap_points([0, d[0], d[1], vo, st, L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TOE, TV_CL, RAIL, HEAD, TOP, H]))
    return ('ENTRY 24 IN THE VESTIBULE, %s x 8\'-0", SWINGS IN. BUILT-IN: PAINTED INSET, 2\'-0" DEEP, TALL PAIRS TO 7\'-0", UPPERS TO %s UNDER THE CROWN. '
            'TV-READY POWER AND DATA BEHIND THE EAST LEAF CL 5\'-0".' % (F(34.0), F(TOP)))

def b3_west(v):
    L = r8((B3S - B3N) / IN); n = B3S
    d = (r8((n - 192.5) / IN), r8((n - 192.5) / IN) + 32.0)
    shell(v, L, base=[(0, d[0] - CS)])
    door(v, d[0], 32.0, 'R', '20 BATH 3')
    boxes = dado(v, L, [(d[0] - CS, L)])
    outer_outlets(v, boxes)
    paper(v, L, x=d[0] / 2, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, HEAD, HEAD + CS, H - COVE, H]))
    return 'BATH 3 DOOR 20, %s x 8\'-0". DADO WAINSCOT, WC-01 ABOVE THE CAP.' % F(32.0)

def b3_vest(v):
    L = r8((VS - B3S) / IN)                                                    # the stub wall's east face, 4'-1"
    shell(v, L, right='end')
    boxes = dado(v, L, [], em=EM)
    sx = EM / 2; sw(v, sx, SW)
    ox = (boxes[-1][0] + boxes[-1][1]) / 2; C.outlet(v, ox, OUT_CL)
    paper(v, L, x=L / 2 + 4, y=104.0)
    dimh(v, v.Y(0) + 14, E.snap_points([0, sx, ox, L], tol=0.5)); dimh(v, v.Y(0) + 42, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, SW, H - COVE - CR, H - COVE, H]))
    return 'VESTIBULE STUB WALL. THREE-WAY DIMMER CL 4\'-0", DUPLEX CL 1\'-6". WC-01 ABOVE THE CAP.'

def key_plan(sh, floor, rect, names_list, target_xy, k):
    src = fitz.open('/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'); sp = src[floor - 1]
    T = BR.transform(floor); a, b = T(rect[0], rect[1]), T(rect[2], rect[3])
    clip_disp = fitz.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
    u = clip_disp * sp.derotation_matrix; u.normalize()
    tw, th = clip_disp.width * k, clip_disp.height * k
    target = fitz.Rect(target_xy[0], target_xy[1], target_xy[0] + tw, target_xy[1] + th)
    for names in names_list:
        sh.p.show_pdf_page(target, src, floor - 1, clip=u, rotate=90)
        assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(floor, names, pad=9.0, doors=True)), 'key plan clip'
    def P(x, y): d_ = T(x, y); return (target.x0 + (d_[0] - clip_disp.x0) * k, target.y0 + (d_[1] - clip_disp.y0) * k)
    return target, P

def kp_toilet_wall(sh, P, wall, cl, axis, sign, IN_=1.5):
    """Wall-hung toilet in the key plan (review 11.09.26, as on ID-262/342/352): FOR's floor-mount toilet and tank whited out, a bowl off
    the wall face, the carrier dashed in the wall. FOR pt; axis 'x': the wall is vertical at x=wall, the bowl projects along x by sign."""
    import math
    def Q(d, t): return P(wall + sign * d * IN_, cl + t * IN_) if axis == 'x' else P(cl + t * IN_, wall + sign * d * IN_)
    def R(a, b): return fitz.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
    sh.p.draw_rect(R(Q(0.4, -11.5), Q(31.0, 11.5)), color=None, fill=(1, 1, 1), width=0)
    sh.p.draw_rect(R(Q(-6.0, -10.0), Q(0.0, 10.0)), color=INK, width=0.4, dashes='[2 1.5] 0')
    pts = [Q(0.0, -7.0), Q(6.0, -7.25)] + [Q(6.0 + 15.0 * math.sin(math.radians(t_)), -7.25 * math.cos(math.radians(t_))) for t_ in range(0, 181, 10)] + [Q(0.0, 7.0)]
    sh.polyline(pts, 0.6, INK, close=True)
    sh.polyline([Q(8.0 + 10.5 * math.sin(math.radians(t_)), -5.0 * math.cos(math.radians(t_))) for t_ in range(0, 181, 10)], 0.4, INK, close=False)
KP_TOILETS = {'ID-260': (905.2, 431.85, 'y', -1), 'ID-340': (446.5, 369.0, 'x', 1), 'ID-350': (446.5, 218.1, 'x', 1)}   # from build_baths_rev1 key plans

def wipe(sh, P, x0, y0, x1, y1):
    """Mask a stray piece of the neighbouring room left inside the clip pad (FOR pt)."""
    p, q = P(x0, y0), P(x1, y1)
    sh.p.draw_rect(fitz.Rect(min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])), color=None, fill=(1, 1, 1), width=0)

def mark_builtin(sh, P, x0, y0, x1, y1):
    p, q = P(x0, y0), P(x1, y1); r = (min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1]))
    sh.rect(r, width=0.8, color=INK, fill=(1, 1, 1)); sh.line((r[0], r[1]), (r[2], r[3]), 0.3, MID); sh.line((r[0], r[3]), (r[2], r[1]), 0.3, MID)

def ref_marker(sh, cx, cy, sheet, r=20.0):
    """Four-way reference marker, the finish plans' style: the room's elevations and key plan are on the sheet shown."""
    f = r / 9.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.8, fill=(1, 1, 1)); s_.commit()
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        tip = fitz.Point(cx + dx * (r + 4.5 * f), cy + dy * (r + 4.5 * f))
        b1 = fitz.Point(cx + dx * r - dy * 2.6 * f, cy + dy * r + dx * 2.6 * f); b2 = fitz.Point(cx + dx * r + dy * 2.6 * f, cy + dy * r - dx * 2.6 * f)
        s_ = sh.p.new_shape(); s_.draw_polyline([b1, tip, b2, b1]); s_.finish(color=INK, width=0.3, fill=INK); s_.commit()
    sh.text(cx, cy - 1.2 * f, 'SEE', 4.4 * f, INK, align='c', raw=True); sh.text(cx, cy + 5.4 * f, sheet.replace('ID-', ''), 5.2 * f, INK, align='c', raw=True)

def view_marker(sh, cx, cy, number, sheet, direction, r=24.0):
    """Single elevation marker in the quad markers' proportions: view number over sheet number, arrow toward the wall."""
    f = r / 16.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.8, fill=(1, 1, 1)); s_.commit()
    sh.line((cx - r, cy), (cx + r, cy), 0.5, INK)
    sh.text(cx, cy - 4.0 * f, str(number), 8.0 * f, INK, align='c', raw=True)
    sh.text(cx, cy + 10.5 * f, sheet.replace('ID-', ''), 7.0 * f, INK, align='c', raw=True)
    dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[direction]
    tip = (cx + dx * (r + 7 * f), cy + dy * (r + 7 * f))
    b1 = (cx + dx * r - dy * 4.0 * f, cy + dy * r + dx * 4.0 * f); b2 = (cx + dx * r + dy * 4.0 * f, cy + dy * r - dx * 4.0 * f)
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()

def bar(sh, x, y, ppf, label, feet=5):
    """Graphic scale for the print: one bar a foot, labeled at every foot, the scale named to its right."""
    for i in range(feet):
        sh.rect((x + i * ppf, y - 6, x + (i + 1) * ppf, y), 0.4, INK, INK if i % 2 == 0 else (1, 1, 1))
    for i in range(feet + 1): sh.text(x + i * ppf, y + 14, f"{i}'", 8.0, INK, align='c', raw=True)
    if label: sh.text(x + feet * ppf + 14, y - 0.5, label, 9.0, INK, raw=True)

def north(sh, nx, ny):
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(nx, ny - 16), fitz.Point(nx + 7, ny + 7), fitz.Point(nx, ny + 1.5), fitz.Point(nx - 7, ny + 7), fitz.Point(nx, ny - 16)]); s_.finish(color=INK, fill=INK, width=0.4); s_.commit()
    sh.text(nx, ny + 21, 'N', 9.0, INK, align='c', raw=True)

def text_len(txt, s):
    from idd_sheet import _FR
    return _FR.text_length(txt, fontsize=s)

STANDARD = [(True, 'BEDROOM STANDARD'),
            'DADO WAINSCOT: BASE 8-1/2", CAP TOP AT 3\'-4". WALLPAPER WC-01 ABOVE TO THE CM-01 CROWN.',
            'TRIM PT-01 SATIN. DOORS 8\'-0" SINGLE PANEL, 5" CASING.',
            'WINDOWS PER FOR A-600: HEAD 8\'-0", SILLS AS SCHEDULED, STOOL AND APRON (NO APRON WHERE THE STOOL CLEARS THE CAP).',
            'CEILINGS PER FOR: 10\'-8" FLOOR 1, 9\'-10" FLOOR 2. CM-01 CROWN HELD 4" BELOW THE CEILING, LED COVE ON ITS TOP (FOR\'S COVE), SEE 4/ID-502.',
            'DUPLEX CL 1\'-6" IN A DADO BOX. SWITCHES CL 4\'-0".',
            'TV-READY POWER AND DATA CL 5\'-0" OPPOSITE THE BED.']

K34 = 4.0                                                                       # 3/16" base to 3/4" TO 1'-0"
SUITES = {   # sheet: floor, base rect (FOR pt), rooms clipped, room labels, quad marker, bath reference, single markers, masks, changes
    'ID-260': dict(floor=1, rect=(286, 628, 640, 922), names=['GUEST BEDROOM', 'GUEST BATHROOM', 'W.I.C.'],
                   title=['GUEST BEDROOM AND', 'GUEST BATH KEY PLAN'], plan='FLOOR 1 KEY PLAN', door02=True,
                   labels=[('GUEST BEDROOM', 487, 700, 9.0), ('GUEST BATHROOM', 381, 866, 9.0), ('W.I.C.', 570, 883, 9.0)], quad=(470, 755, 'ID-738A'), ref=(428, 843, 'ID-740'), single=[],
                   dark=[(431.0, 640.4, 445.0, 650.3), (612.0, 640.4, 628.0, 650.3), (429.5, 805.0, 443.5, 814.9)], white=[(450.0, 620.0, 545.0, 639.5)], sheet_white=[(528.0, 1048.5, 562.0, 1060.0), (669.0, 1048.5, 703.0, 1060.0)],
                   bath='GUEST BATH: ELEVATIONS AND TILE ON ID-262.',
                   changes=['GUEST WEST WALL: CORNER CASING LEGS 3-1/2" AND 3-3/4".', 'GUEST WEST WINDOW TEMPERED.']),
    'ID-340': dict(floor=2, rect=(425, 289, 705, 646), names=['BEDROOM 2', 'BATH 2'],
                   title=['BEDROOM 2 AND BATH 2', 'KEY PLAN'], plan='FLOOR 2 KEY PLAN',
                   labels=[('BEDROOM 2', 560, 600, 9.0), ('BUILT-IN', 617, 441, 9.0)], quad=(600, 545, 'ID-738B'), ref=(513, 367, 'ID-739'), single=[],
                   built=[(543.1, 419.6, 691.2, 457.1)], dark=[], white=[(518.0, 644.5, 531.0, 651.7)],
                   bath='BATH 2: ELEVATIONS AND TILE ON ID-342.',
                   changes=['BUILT-IN: PAINTED INSET WARDROBE TO 8\'-9" UNDER THE CROWN (FOR CEILING 9\'-10").', 'TV-READY OUTLET ON THE BUILT-IN BACK PANEL.']),
    'ID-350': dict(floor=2, rect=(425, 115, 785, 458), names=['BEDROOM 3', 'BATH 3'],
                   title=['BEDROOM 3 AND BATH 3', 'KEY PLAN'], plan='FLOOR 2 KEY PLAN',
                   labels=[('BEDROOM 3', 640, 220, 9.0), ('BUILT-IN', 617, 397, 9.0)], quad=(655, 300, 'ID-738C'), ref=(513, 217, 'ID-739A'),
                   single=[(724.8, 383.9, 5, 'ID-738C', 'W')], built=[(543.1, 376.0, 691.2, 413.2)], dark=[], white=[(428.0, 299.9, 540.0, 314.0), (524.0, 328.0, 535.8, 352.0)], sheet_white=[(416.0, 788.0, 427.3, 800.0)],
                   bath='BATH 3: ELEVATIONS AND TILE ON ID-352.',
                   changes=['BUILT-IN: PAINTED INSET WARDROBE TO 8\'-9" UNDER THE CROWN (FOR CEILING 9\'-10").', 'TV-READY OUTLET ON THE BUILT-IN BACK PANEL.',
                            'SWITCH AND DUPLEX ON THE VESTIBULE STUB WALL.'])}

def suite_sheet(sh, d):
    """One suite's key plan at 3/4" on the left, its title, graphic scale and notes in a column on the right, the pair centered."""
    k = K34; ax0, ax1, ay0, ay1 = FR.x0 + 6, TB_X - 10, HDR_Y + 8, FR.y1 - 6
    T = BR.transform(d['floor']); a_, b_ = T(*d['rect'][:2]), T(*d['rect'][2:])
    pw, ph = abs(b_[0] - a_[0]) * k, abs(b_[1] - a_[1]) * k
    gap = 64.0; colw = min(470.0, ax1 - ax0 - 52 - pw - gap)                  # the notes column takes what the plan leaves, up to 470 pt
    x0 = max(ax0 + 52, ax0 + (ax1 - ax0 - pw - gap - colw) / 2)
    CAPH = 26.0                                                                    # the caption under the plan (review 11.07.26)
    y0 = ay0 + max(24.0, (ay1 - ay0 - ph - CAPH) / 2)
    assert y0 + ph + CAPH <= ay1, ('key plan and caption do not fit', d['title'], y0 + ph + CAPH - ay1)
    assert ph <= ay1 - ay0 and x0 + pw + gap + colw <= ax1, ('key plan does not fit', d['title'])
    t, P = key_plan(sh, d['floor'], d['rect'], [d['names']], (x0, y0), k)
    for r_ in d['dark']:
        p_, q_ = P(r_[0], r_[1]), P(r_[2], r_[3]); sh.p.draw_rect(fitz.Rect(p_, q_), color=None, fill=(90 / 255,) * 3, width=0)
    for r_ in d['white']: wipe(sh, P, *r_)
    for r_ in d.get('sheet_white', []): sh.p.draw_rect(fitz.Rect(r_), color=None, fill=(1, 1, 1), width=0)   # wall stubs past the clip, sheet pt
    for r_ in d.get('built', []): mark_builtin(sh, P, *r_)
    kt = next((v_ for k_, v_ in KP_TOILETS.items() if SUITES.get(k_) is d), None)
    if kt: kp_toilet_wall(sh, P, *kt)
    for txt, x, y, s in d['labels']:
        q = P(x, y)
        if txt == 'BUILT-IN': w_ = text_len(txt, s) + 8; sh.p.draw_rect(fitz.Rect(q[0] - w_ / 2, q[1] - s - 2.5, q[0] + w_ / 2, q[1] + 3.5), color=None, fill=(1, 1, 1), width=0)
        sh.text(q[0], q[1], txt, s, INK, align='c', raw=True)
    x, y, sid = d['quad']; q = P(x, y); quad_marker(sh, q[0], q[1], sid, {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    x, y, sid = d['ref']; q = P(x, y); ref_marker(sh, q[0], q[1], sid)
    for x, y, n, sid, dr in d['single']: q = P(x, y); view_marker(sh, q[0], q[1], n, sid, dr)
    north(sh, t.x0 - 30, t.y0 + 20)
    if d.get('door02'):                                    # exterior door 02 (2'-8", hinged south, swings out): FOR's leaf and swing, tagged
        a, b = P(293.2, 796.6), P(341.2, 799.1)
        g = sh.p.new_shape(); g.draw_rect(fitz.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))); g.finish(color=INK, width=0.6, fill=(1, 1, 1))
        g.draw_polyline([fitz.Point(*P(341.2 + 48 * math.cos(math.radians(t_)), 799.1 + 48 * math.sin(math.radians(t_)))) for t_ in range(180, 271, 5)])
        g.finish(color=INK, width=0.4, closePath=False); g.commit()
        q = P(374, 778); g = sh.p.new_shape(); g.draw_oval(fitz.Rect(q[0] - 13, q[1] - 8.5, q[0] + 13, q[1] + 8.5)); g.finish(color=INK, width=0.6, fill=(1, 1, 1)); g.commit()
        sh.text(q[0], q[1] + 3.3, '02', 9.0, INK, align='c', raw=True)
    sh.text(t.x0, t.y1 + 20, d["plan"], 11.0, INK, bold=True, spacing=0.8, raw=True)
    cx = t.x1 + gap
    paras = list(STANDARD) + ['', (True, 'CHANGES FROM FOR\'S PLAN')] + ['%d. %s' % (i + 1, c) for i, c in enumerate(d['changes'])] + \
            ['', (True, 'BATH'), d['bath']]
    hn = para_block(Sheet(fitz.open()), 0, 0, paras, colw, size=10.0, lh=14.0)      # the notes' height, measured on a scratch page
    hcol = 62 + hn                                                                # graphic scale, rule, then the notes
    cy = max(ay0 + 24, (t.y0 + t.y1) / 2 - hcol / 2)                             # the column centered on the plan (review 11.07.26)
    bar(sh, cx, cy + 6, 54.0, '')
    sh.line((cx, cy + 36), (cx + colw, cy + 36), 0.4, (0.7, 0.7, 0.7))
    y_end = para_block(sh, cx, cy + 62, paras, colw, size=10.0, lh=14.0)
    assert y_end < ay1 - 4, ('notes run off the sheet', y_end)
    return t

GUEST_BAND = 124.0; F2_BAND = 114.0                                      # FOR A-205 guest bedroom 10'-4" cove band; A-206 9'-6" window band
for _f in (b2_west, b3_east): _f.h = F2_BAND; _f.note = 'CEILING 9\'-6" BAND AT THE WINDOW WALL (FOR A-206), 9\'-10" BEYOND.'
for _f in (guest_north, guest_east, guest_south, guest_west): _f.note = 'CEILING 10\'-4" BAND AT THE WALLS (FOR A-205), 10\'-8" AT THE CENTER.'

def build():
    idd_std.PROJECT['date'] = ISSUE
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    doc = fitz.open()
    idd_sheet.EXTRA_REVS[:] = []                                         # rows listed here in date order
    rev = (('0', '11.02.26', 'TYPICAL SHEET ISSUED'), ('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', ISSUE, 'PER ROOM ON REV 1'))
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    def row(y0, y1, needs):
        """Cells across the frame width in proportion to what each view needs at 1/2" (wall plus the dimension margins)."""
        tot = sum(needs); x = frame[0]; out = []
        for n_ in needs:
            w_ = (frame[2] - frame[0]) * n_ / tot; out.append((x, y0, x + w_, y1)); x += w_
        return out
    cells4 = E.layout_cells(frame, 2, 2)
    ym = (frame[1] + frame[3]) / 2; need = lambda L: L * E.SCALES['1/2'] + 106
    cells5 = row(frame[1], ym, [need((B3E - B3W) / IN), need((VS - B3N) / IN)]) + row(ym, frame[3], [need((B3E - B3W) / IN), need((B3S - B3N) / IN), need((VS - B3S) / IN)])
    sheets = [('ID-738A', 'GUEST BEDROOM ELEVATIONS', ['INTERIOR ELEVATIONS', 'GUEST BEDROOM'], cells4,
               [(1, 'NORTH ELEVATION - HEADBOARD WALL', r8((GE - GW) / IN), guest_north, 0), (2, 'EAST ELEVATION - ENTRY 16', r8((GS - GN) / IN), guest_east, 0),
                (3, 'SOUTH ELEVATION - W.I.C. AND BATH', r8((GE - GW) / IN), guest_south, 0), (4, 'WEST ELEVATION - DOOR 02 AND WINDOW', r8((GS - GN) / IN), guest_west, 0)]),
              ('ID-738B', 'BEDROOM 2 ELEVATIONS', ['INTERIOR ELEVATIONS', 'BEDROOM 2'], cells4,
               [(1, 'NORTH ELEVATION - BATH 2 AND BUILT-IN', r8((B2E - B2W) / IN), b2_north, 0), (2, 'EAST ELEVATION - ENTRY 24', r8((B2S - B2N) / IN), b2_east, 0),
                (3, 'SOUTH ELEVATION - HEADBOARD WALL', r8((B2E - B2W) / IN), b2_south, 0), (4, 'WEST ELEVATION - WINDOWS', r8((B2S - B2N) / IN), b2_west, 0)]),
              ('ID-738C', 'BEDROOM 3 ELEVATIONS', ['INTERIOR ELEVATIONS', 'BEDROOM 3'], cells5,
               [(1, 'NORTH ELEVATION - HEADBOARD WALL', r8((B3E - B3W) / IN), b3_north, 0), (2, 'EAST ELEVATION - WINDOWS', r8((VS - B3N) / IN), b3_east, 0),
                (3, 'SOUTH ELEVATION - BUILT-IN AND VESTIBULE', r8((B3E - B3W) / IN), b3_south, 0), (4, 'WEST ELEVATION - BATH 3', r8((B3S - B3N) / IN), b3_west, 0),
                (5, 'VESTIBULE WEST - SWITCH', r8((VS - B3S) / IN), b3_vest, 0)])]
    keyp = {'ID-738A': 'ID-260', 'ID-738B': 'ID-340', 'ID-738C': 'ID-350'}     # owner 11.07.26: each suite's key plan opens its block of ten
    for sid, title, tl, cells, views in sheets:
        kid = keyp[sid]; d = SUITES[kid]
        s = Sheet(doc); s.frame(' '.join(d['title']), 'SCALE: 3/4" TO 1\'-0"', d['title'], kid, revisions=rev, legend_rule=False)
        suite_sheet(s, d)
        set_room(GUEST_BAND if d['floor'] == 1 else H_F2)                 # FOR's ceiling at the walls: the guest bedroom's 10'-4" band (review 11.09.26)
        s = Sheet(doc); s.frame(title, 'SCALE: 1/2" TO 1\'-0"', tl, sid, revisions=rev, legend_rule=False)
        draw_views(s, cells, views, scale='1/2')
    fix_soft_hyphen(doc)
    doc.set_metadata({'title': 'Casa Grove guest bedroom ID-260, ID-261, bedroom 2 ID-340, ID-341, bedroom 3 ID-350, ID-351', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
