import sys
sys.path.insert(0, '/home/claude/flrwork/rev1')
"""Master bedroom designed elevations, YL option 2 language (full-height applied-moulding panels), per Zack 11.02.26, REDRAWN ON FOR REV 1
(A-202 REV 1, 10.23.26) 11.06.26: king bed with 18" nightstands on the 9'-9-3/8" headboard wall (owner 11.06.26); TV on the west wall on the
bed axis; bookcase in the reading nook; drapery in ceiling pockets at the terrace doors and the window; 10'-0" flat ceiling with crown; panels
hide the safe's jib door; 8'-0" heads. Sheets: ID-734 key plan, ID-735 north and east, ID-736 south and west, ID-737 nook.
Output: 261105.HD102.MasterBedroomPilot.pdf (the 11.05.26 issue kept as .prev)"""
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT, TRIM
import base_rev1 as BR

OUT = '/home/claude/flrwork/261105.HD102.MasterBedroomPilot.pdf'
H = 118.0; HEAD = 96.0
# Coordination with FOR Rev 1 (11.09.26): FOR's ceilings. Main room 9'-10" (A-401 sec 2; no CLG tag on A-206) inside an L-shaped
# LED cove (L12); the window wall is a 9'-6" band with the 5" curtain pocket; the nook (FOR's vestibule to D08) is 9'-6".
# Owner: crown stays with an LED cove on top of it, held 4" down from the ceiling (CH = crown top). Set per view in draw_view.
COVE = 4.0; CH = H - COVE
VIEW_H = {'north': (118.0, 114.0), 'niche': (118.0, 114.0), 'east': (118.0, 114.0), 'west': (118.0, 114.0),
          'south': (114.0, 114.0), 'nook_north': (114.0, 114.0), 'nook_east': (114.0, 114.0), 'nook_south': (114.0, 114.0), 'nook_west': (114.0, 114.0)}
POCKET_D = 5.0     # FOR's motorized curtain pocket, 5" (A-403 detail, A-206 note C-1)
CS = TRIM['casing']; BASE = TRIM['base']; CAP = TRIM['dado']; M = TRIM['margin']; OUT_CL = 18.0; SW = 48.0; SILL = 36.0   # FOR's window E: 5'-0" x 5'-0" casement, sill 3'-0", head 8'-0" (A-600, ID-003; coordination 11.09.26)   # trim block, 10 ft ceiling
WHITE = (1, 1, 1); BEYOND = (0.55, 0.55, 0.55)
IN = 1.5                               # FOR pt per inch (A-202 at 1/4" = 1'-0")

# ---- PLAN, FOR A-202 REV 1 sheet pt, measured from the drywall lines (raster scans at 8 px/pt) and the A-DOOR / A-WINDOW vectors
W_FACE = 698.1                         # main room and entry recess west wall face
E_FACE = 973.1625                      # headboard (east) wall face: FOR's 15'-3-3/8" overall (vector 973.1)
REC_N = 919.0625                       # FOR: west wall 16'-5-7/8", recess 3'-0-5/8" (vector 919.1): entry recess back (north) wall face
REC_E = 780.6                          # FOR's 4'-7" recess (vector 780.4): entry recess east side: the face of FOR's millwork niche and the 4-3/4" wall nib below it
NICHE = (780.6, 804.6, 919.0625, 967.0625)   # FOR's millwork niche on the recess east side, 1'-4" deep x 2'-8" long, 4-5/8" nib, opening west
N_MAIN = 974.0                         # main room north wall face (the linen closet front), coplanar with the nib
S_FACE = 1215.875                      # main room south wall face: FOR's 13'-5-1/4" room depth (vector 1215.75)
ENTRY = (712.4, 766.4)                 # door 18 leaf, 3'-0", hinged west (arc 712.4 to 766.4), swings into the recess
POCKET = (1127.9375, 1181.9375)        # FOR: 1'-10-5/8" from the south wall to the opening: bath pocket door opening on the west wall, 3'-0" leaf, pocket north (FOR's leaf 1095.5 to 1149.5)
WINDOW = (746.1, 836.1)                # south window frame, 5'-0", 3'-4" from the nook corner per FOR
NOOK_W, NOOK_E, NOOK_N, NOOK_S = 896.1, 1046.1, 1149.875, 1290.8   # FOR: south wall 11'-0", nook 8'-4", headboard wall 9'-9-1/4"   # reading nook faces; NOOK_W is also the main south wall's east end (outside corner)
JIB = (987.0, 1035.0)                  # FOR's hidden millwork door 21 on the nook north wall, 2'-8" leaf
FRENCH = (929.1, 1013.1)               # terrace pair, two 2'-4" leaves (FOR's leaf 42 pt), frame 926.2 to 1016.2
def inch(pt): return pt / IN
def f16(i):
    n = int(round(i * 16)); w, r = divmod(n, 16); d = 16
    while r and r % 2 == 0: r //= 2; d //= 2
    return (f'{w}-{r}/{d}"' if w else f'{r}/{d}"') if r else f'{w}"'
def D(x, y):
    """FOR pt to the base display space the key plan is clipped from."""
    return BR.transform(2)(x, y)

BOOK_D = 12.0                          # nook bookcase depth, 12" (was 14") so the west drapery stack stops at its side
ROOM_W = inch(E_FACE - W_FACE)         # 183.3
ROOM_D = inch(S_FACE - N_MAIN)         # 161.2
STRIP_D = inch(N_MAIN - REC_N)         # 36.6

def shell(v, L, crown=(), base=(), cut_left=True, cut_right=True):
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    for a, b in base: C.base(v, a, b)
    for a, b in crown:
        C.crown(v, a, b, CH)
        if CH < H - 0.5: C._line(v, (a, CH + 0.9), (b, CH + 0.9), C.FINE, MID, '[1 1] 0')   # LED strip on the crown top, cove gap above
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    if cut_left: v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    if cut_right: v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=(0.3, 0.3, 0.3))

def leaf_toward(v, *a, **kw):
    """Swing-mark rule: solid when the door swings toward the viewer (door_leaf draws them dashed, for a door swinging away)."""
    orig = C._line
    def ln(v_, a_, b_, w=C.MED, c=None, dashes=None): return orig(v_, a_, b_, w, c, None if dashes == '[2 1.5] 0' else dashes)
    C._line = ln
    try: C.door_leaf(v, *a, **kw)
    finally: C._line = orig

def leaf_away(fn, *a, **kw):
    """Swing-mark rule: dashed when the door swings away from the viewer. Long dashes so they still read as dashed on the 11 x 17 print."""
    orig = C._line
    def ln(v_, a_, b_, w=C.MED, c=None, dashes=None): return orig(v_, a_, b_, w, c, '[6 4] 0' if dashes == '[2 1.5] 0' else dashes)
    C._line = ln
    try: fn(*a, **kw)
    finally: C._line = orig

def beyond(fn):
    keep = (C.INK, C.MID); C.INK = BEYOND; C.MID = BEYOND
    try: fn()
    finally: C.INK, C.MID = keep

def recess_jambs(v, a, b, top=H):
    for x, side in ((a, 1), (b, -1)):
        C._line(v, (x, 0), (x, top), C.HEAVY); C._line(v, (x + 0.6 * side, 0), (x + 0.6 * side, top), C.FINE, LIGHT)

def tag(v, x, y, s): v.text(v.X(x), v.Y(y), s, 5.2, MID, align='c')
def tag_masked(v, x, y, s):
    """A tag on a white backing, for labels that must sit over grey beyond linework (review 11.09.26)."""
    w = fitz.get_text_length(s, fontname='helv', fontsize=5.2) * 1.08 + 4
    sh_ = v.p.new_shape(); sh_.draw_rect(fitz.Rect(v.X(x) - w / 2, v.Y(y) - 5.6, v.X(x) + w / 2, v.Y(y) + 1.8)); sh_.finish(color=None, fill=(1, 1, 1)); sh_.commit()
    tag(v, x, y, s)

# ================================================================== main room
def panels(v, x0, x1, openings=(), single=(), centered=None): C.panel_wall(v, x0, x1, CH, openings=openings, single=single, centered=centered)

def aligned_boxes(v, bays, upper=True, dado=True):
    """Upper and dado boxes on the same x extents (owner 11.09.26: the wainscot below matches the layout above). The cap comes from
    C.panel_wall(..., upper=False, dado=False); this draws the boxes with the same molding as C.panel_wall."""
    mold = TRIM['panel_mold']; m = TRIM['margin']; cap = TRIM['cap']; cap_top = TRIM['dado']; crown_b = CH - TRIM['crown']
    lo = (BASE + m, cap_top - cap - m); hi = (cap_top + m, crown_b - m)
    for a, b in bays:
        for (y0, y1), on in ((hi, upper), (lo, dado)):
            if not on: continue
            C._rect(v, a, y0, b, y1, C.MED); C._rect(v, a + mold, y0 + mold, b - mold, y1 - mold, C.FINE, MID)
    return list(bays)

def even_boxes(a, b, ma=None, mb=None, target=32.0):
    """The box layout C.panel_wall uses on a plain segment (equal boxes near the target width, margins between)."""
    m = TRIM['margin']; ma = m if ma is None else ma; mb = m if mb is None else mb
    inner = b - a - ma - mb
    if inner < target * 0.5: return []
    n = max(1, int(round((inner + m) / (target + m)))); w = (inner - m * (n - 1)) / n
    return [(a + ma + i * (w + m), a + ma + i * (w + m) + w) for i in range(n)]

def north(v):
    """Looking north, west at the left: the entry recess (door 18 from the hall, beyond), then the north wall in one plane (the linen
    closet front and the 4-3/4" nib below FOR's millwork niche), a solid paneled wall: the closet is served from the hall."""
    L = ROOM_W
    strip = (0.0, inch(REC_E - W_FACE))                   # 0 to 54.9, recessed 36.6 in.
    entry = (inch(ENTRY[0] - W_FACE), inch(ENTRY[1] - W_FACE))     # FOR's leaf, centered in the recess within 1/8"
    nib = strip[1] - entry[1] - CS
    sw_x = (entry[1] + CS + strip[1]) / 2                 # the 3-way on the 4-3/8" of recess back wall at the latch side
    def far():
        C.base(v, 0, entry[0] - CS); C.base(v, entry[1] + CS, strip[1]); C.crown(v, 0, strip[1], CH)
        C.casing(v, entry[0], entry[1] - entry[0], HEAD); leaf_toward(v, entry[0], entry[1] - entry[0], HEAD, panels=1, swing='L')   # door 18 swings into the recess, toward the viewer
        C.switch(v, sw_x, SW, 'S3')
    beyond(far)
    shell(v, L, crown=[(strip[1], L)], base=[(strip[1], L)])
    recess_jambs(v, strip[1], strip[1])
    db = C.panel_wall(v, strip[1], L, CH, centered=(strip[1] + L) / 2)
    oxs = [(a + b) / 2 for a, b in (db[0], db[-1])]         # outlets centered in the outer dado boxes
    for ox in oxs: C.outlet(v, ox)
    tag(v, strip[1] / 2, 102.2, 'ENTRY RECESS BEYOND, %s DEEP' % E.ftin(round(STRIP_D * 8) / 8))
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, entry[0], entry[1], strip[1]] + oxs + [L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, BASE, CAP, SW, HEAD, HEAD + CS, CH - TRIM['crown'], CH, H]))
    return ['LOOKING NORTH, WEST AT THE LEFT. ENTRY RECESS %s WIDE x %s DEEP (FOR REV 1) WITH FOR\'S 3\'-0" x 8\'-0" DOOR 18 FROM THE HALL, CENTERED IN THE RECESS' % (E.ftin(round(strip[1] * 8) / 8), E.ftin(round(STRIP_D * 8) / 8)),
            'AS FOR DRAWS IT, SINGLE PANEL, HINGED WEST, PRIVACY SET. S3 ON THE %s OF RECESS BACK WALL AT THE LATCH SIDE, CL 4\'-0", SINGLE GANG: ROOM CEILING LIGHTS, WITH THE S4 AT THE BED AND THE S3 AT DOOR 19.' % E.ftin(nib),
            'FOR\'S 1\'-4" x 2\'-8" MILLWORK NICHE OPENS WEST OFF THE RECESS EAST SIDE, EDGE-ON IN THIS VIEW: SEE VIEW 1A. NO DEVICES ON THE NICHE WALL.',
            'THE NORTH WALL IS ONE PLANE (THE LINEN CLOSET FRONT AND THE NIB BELOW THE NICHE): THE CLOSET IS SERVED FROM THE HALL, SOLID PANELED WALL ON THIS SIDE. TRIM PER',
            'THE 10\'-0" TRIM BLOCK: BASE 8-1/2", CROWN CM-01 8" DROP, CASING 5" WITH BACKBAND, CAP 3" WITH ITS TOP AT 3\'-4". PICTURE-FRAME PANELS, 2" MOULDING, ONE 4" MARGIN,',
            'DADO AND UPPER BOXES ON ALIGNED STILES. DUPLEX OUTLETS VERTICAL, CENTERED IN THE OUTER DADO BOXES, CL 1\'-6" AFF. PT-02.']

def niche(v):
    """Entry recess east side, looking east, north at the left: FOR's millwork niche (1'-4" deep), opening west into the recess."""
    L = STRIP_D                                              # 36.6: recess back wall to the room's north wall plane
    nw = inch(NICHE[3] - NICHE[2])                            # 31.9
    sill = CAP; head = sill + 3 * 17.625 + 4 * 0.75                # three equal 1'-5-5/8" openings: head 7'-11-7/8"
    shell(v, L, crown=[(0, L)], base=[(0, L)], cut_right=False)
    C._line(v, (L, 0), (L, H), C.HEAVY); C._line(v, (L - 0.6, 0), (L - 0.6, H), C.FINE, LIGHT)   # outside corner into the room
    C._rect(v, 0, CAP - 3, L, CAP, C.OUTLINE)                # cap, continuous below the niche
    C._rect(v, M, BASE + M, nw - M, CAP - 3 - M, C.FINE)     # one dado box below the niche
    C._rect(v, 0, sill, nw, head, C.OUTLINE)                 # niche opening, 3/4" flush edge
    C._rect(v, 0.75, sill + 0.75, nw - 0.75, head - 0.75, C.FINE, LIGHT)
    gap = (head - sill - 1.5 - 2 * 0.75) / 3                  # three equal openings between two 3/4" shelves
    shelf_y = [sill + 0.75 + gap, sill + 0.75 + 2 * gap + 0.75]
    for y in shelf_y: C._rect(v, 0.75, y, nw - 0.75, y + 0.75, C.MED)
    tag(v, nw / 2, 102, 'MILLWORK NICHE')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, nw, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, CAP - 3, CAP, head, CH - TRIM['crown'], CH, H]))
    v.dim_v(sill, head, v.X(0) - 14, E.snap_points([sill, sill + 0.75] + [y for y0 in shelf_y for y in (y0, y0 + 0.75)] + [head - 0.75, head], tol=0.5))   # the three equal openings
    return ['RECESS EAST SIDE, LOOKING EAST, NORTH AT THE LEFT. FOR\'S MILLWORK NICHE',
            '%s WIDE x 1\'-4" DEEP, FLUSH TO THE RECESS BACK WALL, %s NIB' % (E.ftin(round(nw * 8) / 8), E.ftin(round((L - nw) * 8) / 8)),
            'TO THE ROOM. OPENING 3\'-4" TO 7\'-11-7/8" AFF (FOR SHOWS PLAN ONLY,',
            'HEIGHTS PROPOSED, FOR TO CONFIRM), 3/4" FLUSH EDGE, TWO 3/4"',
            'FIXED SHELVES, THREE EQUAL OPENINGS OF %s, PAINTED PT-02. CAP, BASE AND' % E.ftin(gap),
            'CROWN RUN THROUGH. NO DEVICES ON THIS WALL (THE 3-WAY IS ON',
            'THE RECESS BACK WALL, VIEW 1). OWNER TO SAY THE USE.']

def east(v):
    """Headboard wall, looking east, north at the left. FOR REV 1 makes the wall 9'-9-3/8": the king with 18" nightstands (owner 11.06.26),
    the bed centered on the wall, the headboard the mattress width."""
    L = inch(NOOK_N - N_MAIN)                               # 117.3
    hb_w, hb_h = 76.0, 54.0
    bc = L / 2
    ns_w = 18.0; clear = (L - hb_w - 2 * ns_w) / 2          # 2.7
    EM = 6.0                                                # end margins 6 in. so the bedside switch clears the corner
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    C.panel_wall(v, 0, L, CH, upper=False, dado=False)          # the cap only
    NW = 14.0                                               # owner 11.09.26: narrow | wide | narrow, upper and dado aligned; the narrow boxes carry the sconces
    bays = [(EM, EM + NW), (EM + NW + M, L - EM - NW - M), (L - EM - NW, L - EM)]
    aligned_boxes(v, bays)
    C.rev_cloud(v, EM - 2, BASE + 1, L - EM + 2, CH - TRIM['crown'] - 1, pad=1.0, tag_at='tl')
    C.bed_king(v, bc, hb_w, hb_h)
    ns_h = 26.0
    C.nightstand(v, 0, ns_w, h=ns_h); C.nightstand(v, L - ns_w, ns_w, h=ns_h)
    sc_y = hb_h + 6
    sx_ = EM + NW / 2                                        # centered in the narrow box: 13" from each corner
    for sx in (sx_, L - sx_): C.sconce(v, sx, sc_y, 'shade')
    for ox in (ns_w / 2, L - ns_w / 2):
        v.rect(v.X(ox - 1.4), v.Y(OUT_CL + 2.25), v.X(ox + 1.4), v.Y(OUT_CL - 2.25), 0.45, INK, None, '[1.0 0.7] 0')   # behind the nightstand: dashed
        for dy in (1.1, -1.1): v.rect(v.X(ox - 0.45), v.Y(OUT_CL + dy + 0.45), v.X(ox + 0.45), v.Y(OUT_CL + dy - 0.45), 0.3, INK, None, '[0.6 0.5] 0')
        v.text(v.X(ox + 2.0), v.Y(OUT_CL) + 1.8, 'USB', 5.0, MID, align='l')   # tag beside the plate, clear of the drawer lines
    C.switch(v, EM / 2, 32.0, 'S4')                         # plate bottom 29-3/4", 3-3/4" over the 26" nightstand                         # north end margin, above the nightstand, reachable from the bed
    tag(v, bc, hb_h - 9, 'KING BED, HEADBOARD 6\'-4" x 4\'-6", N.I.C.')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, ns_w, bc - hb_w / 2, bc, bc + hb_w / 2, L - ns_w, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, BASE, ns_h, 32, CAP, hb_h, sc_y, CH - TRIM['crown'] - M, CH - TRIM['crown'], CH, H]))
    return ['HEADBOARD WALL, LOOKING EAST, NORTH AT THE LEFT. FOR REV 1 DEEPENS THE LINEN CLOSET, SO THE WALL IS %s (WAS 10\'-5"). A KING (76" MATTRESS) WITH TWO 18"' % E.ftin(round(L * 8) / 8),
            'NIGHTSTANDS (OWNER 11.06.26) LEAVES %s EACH SIDE OF THE HEADBOARD. THE BED IS CENTERED ON THE WALL, THE HEADBOARD THE MATTRESS WIDTH, 4\'-6" HIGH, THE' % E.ftin(round(clear * 8) / 8),
            'NIGHTSTANDS 18" WIDE x 26" HIGH IN THE CORNERS. UPPER AND DADO BOXES SET OUT FROM THE BED AXIS, 6" END MARGINS. SWING-ARM SCONCES CL 5\'-0" AFF (6" ABOVE THE',
            'HEADBOARD) CENTERED ON THE NIGHTSTANDS, HARDWIRED, INTEGRAL SWITCH ON EACH FIXTURE. DUPLEX WITH USB BEHIND EACH NIGHTSTAND, CENTERED ON IT, CL 1\'-6".',
            'S4 IN THE NORTH END MARGIN, CL 2\'-8", 3-3/4" OVER THE NIGHTSTAND: ROOM CEILING LIGHTS, FOUR-WAY WITH THE S3 AT THE ENTRY (VIEW 1) AND THE S3 AT DOOR 19',
            '(ID-736). THE SAFE CLOSET IS BEHIND THE SOUTH END OF THIS WALL, ITS DOOR ON THE NOOK SIDE (ID-737). CEILING FIXTURE ON THE RCP.']

def south(v):
    """Window wall, looking south, east at the left. The wall runs from the outside corner where the reading nook opens off the room
    (at the left) to the west wall; the window sill is the tall-window stool, the dado and cap stop at the casing."""
    L = inch(NOOK_W - W_FACE)                                # 132.1
    win = (inch(NOOK_W - WINDOW[1]), inch(NOOK_W - WINDOW[0]))   # 40.0 to 100.0
    wc = (win[0] + win[1]) / 2
    shell(v, L, crown=[(0, L)], base=[(0, L)], cut_left=False)
    recess_jambs(v, 0, 0)
    db = C.panel_wall(v, 0, L, CH, openings=[(win[0] - CS, win[1] + CS)], centered=wc)
    C.window(v, win[0], win[1] - win[0], SILL, HEAD, lites=3)           # divided lites, set rule (owner 11.09.26)
    ap = SILL - 1.5 - TRIM['cap']                                       # under the apron: one dado box, aligned with the casing
    C._rect(v, win[0] - CS + M, BASE + M, win[1] + CS - M, ap - M, C.MED); C._rect(v, win[0] - CS + M + 0.75, BASE + M + 0.75, win[1] + CS - M - 0.75, ap - M - 0.75, C.FINE, MID)
    C._rect(v, 0, H - POCKET_D, L, H, C.FINE, MID, dashes='[2 1.5] 0')   # FOR's 5" curtain pocket in the 9'-6" band, drapery itself not drawn
    oxs = [(a + b) / 2 for a, b in (db[0], db[-1])]
    for ox in oxs: C.outlet(v, ox)
    tag(v, wc, 104, 'CURTAIN POCKET 5", FULL WIDTH (FOR)')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, oxs[0], win[0] - CS, win[0], wc, win[1], win[1] + CS, oxs[1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, BASE, SILL, HEAD, HEAD + CS, CH - TRIM['crown'], H - POCKET_D, H]))
    return ['LOOKING SOUTH, EAST AT THE LEFT. THE WALL RUNS %s FROM THE OUTSIDE CORNER WHERE THE READING NOOK OPENS OFF THE ROOM (ID-737, NOT DRAWN) TO THE WEST WALL.' % E.ftin(round(L * 8) / 8),
            'FOR\'S WINDOW E, %s FROM THE CORNER: 5\'-0" x 5\'-0" CASEMENT, SILL 3\'-0", HEAD 8\'-0" (A-600). IMPACT-RATED,' % E.ftin(round(win[0] * 8) / 8),
            'CASED 5" WITH STOOL AND APRON, ONE DADO BOX UNDER THE APRON, THE BASE RUNS THROUGH. THE CAP AND THE BOXES STOP AT THE CASING EACH SIDE. THE WINDOW IS %s OFF THE WALL CENTER, SO THE' % E.ftin(round(abs(wc - L / 2) * 8) / 8),
            'BOXES BESIDE IT DIFFER. DRAPERY: FOR\'S 5" CEILING POCKET FULL WIDTH, TRAVERSE TRACK, SHEER AND BLACKOUT, STACKS 14" EACH SIDE OF THE CASING (N.I.C., NOT DRAWN).',
            'DUPLEX OUTLETS VERTICAL, CENTERED IN THE DADO BOX EACH SIDE OF THE WINDOW, CL 1\'-6". PT-02, CROWN CM-01, BASE.']

def west(v):
    """Looking west, south at the left: door 19, the bath pocket door (pocket north, latch and pull at the south edge), the wall-mounted
    TV on the bed axis with its blocking and power north of the pocket, the entry recess at the north end."""
    L = inch(S_FACE - REC_N)                                 # 197.9
    pd = (inch(S_FACE - POCKET[1]), inch(S_FACE - POCKET[0]))      # 22.6 to 58.6
    pocket_end = pd[1] + (pd[1] - pd[0])                     # 94.6: the leaf slides north into the wall
    blk = 97.0                                               # TV bracket blocking and the power box start north of the pocket end
    tvc = inch(S_FACE - (N_MAIN + NOOK_N) / 2)                # the bed axis: the bed is centered on the headboard wall
    tv_w = 55 * 0.872; tv_h = 55 * 0.49                      # 48 x 27
    tv_b = CAP + M + M; tv_cy = tv_b + tv_h / 2              # set one margin above the box bottom: CL 5'-1-1/2"
    half = tvc - (pd[1] + CS + M)                            # the big box runs from the pocket door casing margin and is centered on the TV
    bay = (tvc - half, tvc + half)
    strip = (inch(S_FACE - N_MAIN), L)
    sw = (pd[0] - CS) / 2                                    # the latch-side wall south of the casing
    shell(v, L, crown=[(0, L)], base=[(0, pd[0] - CS), (pd[1] + CS, L)])
    C.casing(v, pd[0], pd[1] - pd[0], HEAD); C.door_leaf(v, pd[0], pd[1] - pd[0], HEAD, panels=1, swing=None, pull='L')
    C._rect(v, pd[1], 0, pocket_end, HEAD, C.FINE, LIGHT, dashes='[2 1.5] 0')   # the pocket, hidden
    C.panel_wall(v, 0, L, CH, openings=[(pd[0] - CS, pd[1] + CS)], single=[bay], centered=tvc, dado=False)
    db = [bay] + even_boxes(bay[1], L, mb=M)                 # owner 11.09.26: one wide dado box under the TV box, the rest under the upper boxes
    aligned_boxes(v, db, upper=False)
    C.rev_cloud(v, bay[0], BASE, bay[1], tv_b + tv_h + 9)
    C._rect(v, tvc - tv_w / 2, tv_cy - tv_h / 2, tvc + tv_w / 2, tv_cy + tv_h / 2, C.OUTLINE, fill=(1, 1, 1))
    C._rect(v, tvc - tv_w / 2 + 0.6, tv_cy - tv_h / 2 + 0.6, tvc + tv_w / 2 - 0.6, tv_cy + tv_h / 2 - 0.6, C.FINE, MID)
    pwr = (blk + 3.0, blk + 9.0)                             # duplex and data jack behind the set, north of the pocket
    C.outlet(v, pwr[0], tv_cy - 4, horizontal=False); C.data_jack(v, pwr[1], tv_cy - 4)
    v.text(v.X(tvc), v.Y(tv_cy - 10), 'POWER AND DATA BEHIND THE SET', 5.0, MID, align='c')
    C.switch(v, sw, SW, 'S3')                                # no picture light (owner 11.09.26), so no dimmer
    oxs = [sw] + [(a + b) / 2 for a, b in db if a >= bay[1] - 0.5][:1]   # the latch-side wall below the 2-gang, and the first dado box north of the TV
    for ox in oxs: C.outlet(v, ox)
    tag(v, tvc, tv_cy + 6, '55" TV, ARTICULATING BRACKET')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, oxs[0], pd[0], pd[1], bay[0], tvc - tv_w / 2, tvc, tvc + tv_w / 2, bay[1]] + oxs[1:] + [strip[0], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, BASE, CAP, SW, tv_cy, tv_b + tv_h, HEAD, HEAD + CS, CH - TRIM['crown'], CH, H]))
    return ['LOOKING WEST, SOUTH AT THE LEFT. FOR\'S 3\'-0" x 8\'-0" POCKET DOOR 19 TO THE MASTER BATH, %s FROM THE SOUTH WALL, POCKET NORTH (DASHED), SINGLE PANEL, CASED,' % E.ftin(pd[0]),
            'RECESSED PULL AT THE SOUTH (LATCH) EDGE. 2-GANG ON THE %s OF WALL SOUTH OF THE CASING, CL 4\'-0": S3 ROOM CEILING LIGHTS (WITH THE ENTRY S3 AND THE BED S4),' % E.ftin(pd[0] - CS),
            '55" TV (48" x 27") ON AN ARTICULATING BRACKET, CENTERED ON THE BED AXIS (%s NORTH OF THE WALL\'S CENTER), CL %s AFF, IN ONE TALL BOX' % (E.ftin(round((tvc - L / 2) * 8) / 8), E.ftin(tv_cy)),
            '(%s x 5\'-4"). BRACKET BLOCKING AND THE POWER BOX ONLY NORTH OF %s FROM THE SOUTH WALL, CLEAR OF THE POCKET (IT ENDS AT %s). THE BOX BEHIND THE SET IS A DUPLEX' % (E.ftin(bay[1] - bay[0]), E.ftin(blk), E.ftin(pocket_end)),
            'CL %s AFF (BELOW 5\'-6") WITH A DATA JACK, CONDUIT TO THE DADO OUTLET. NO SCONCES (A SOUTH SCONCE WOULD LAND ON THE POCKET), NO PICTURE LIGHT (OWNER 11.09.26). ONE WIDE DADO BOX UNDER THE TV BOX. PANELS CONTINUE' % E.ftin(tv_cy - 4),
            'INTO THE ENTRY RECESS (SAME PLANE). DUPLEX OUTLETS VERTICAL, CL 1\'-6": BELOW THE 2-GANG, AND CENTERED IN THE FIRST DADO BOX NORTH OF THE TV. PT-02, CROWN CM-01, BASE.']

# ================================================================== reading nook (ID-737)
def nook_north(v):
    """Looking north from the nook: open to the room at the left (no wall), then one coplanar painted surface: the east wall's 4-3/4 in.
    end face and the safe wall, with the jib door centered on that whole surface."""
    L = inch(NOOK_E - NOOK_W)                                 # 99.9
    opn = (0.0, inch(E_FACE - NOOK_W)); face = (opn[1], L)   # the painted surface, 51.5 in.
    jw = inch(JIB[1] - JIB[0])                                # 32.0, FOR's 2'-8" leaf
    jib = (face[0] + 8.375, face[0] + 8.375 + jw)                 # 8-3/8" west, 8-1/4" east: centered within 1/16" on the 1/8" grid
    shift = jib[0] - inch(JIB[0] - NOOK_W)                    # west of FOR's location
    shell(v, L, crown=[face], base=[face], cut_left=False)
    recess_jambs(v, opn[1], opn[1])
    C.panel_wall(v, face[0], face[1], CH, single=[(jib[0] + M, jib[1] - M)], centered=(jib[0] + jib[1]) / 2)
    leaf_away(C.jib_door, v, jib[0], jib[1] - jib[0], HEAD)                  # swings into the safe closet, away from the viewer
    tag(v, opn[1] / 2, 110, 'OPEN TO THE BEDROOM')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, opn[1], jib[0], (jib[0] + jib[1]) / 2, jib[1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, CAP, HEAD, CH - TRIM['crown'], CH, H]))
    return ['NOOK NORTH WALL, LOOKING NORTH. OPEN TO THE BEDROOM AT THE LEFT (NO WALL). THE PAINTED SURFACE IS ONE PLANE %s WIDE: THE EAST WALL\'S END FACE AND THE' % E.ftin(round((face[1] - face[0]) * 8) / 8),
            'SAFE WALL. FOR\'S 2\'-8" x 8\'-0" HIDDEN DOOR 21 AS A JIB DOOR CENTERED ON THAT SURFACE (%s WEST, %s EAST, %s WEST OF FOR\'S LOCATION, FOR TO CONFIRM THE SAFE BEHIND IT): FLUSH LEAF, PANELS, CAP,' % (E.ftin(jib[0] - face[0]), E.ftin(face[1] - jib[1]), f16(abs(shift))),
            'BASE AND CROWN RUN ACROSS IT UNBROKEN, NO CASING, NO FACE HARDWARE, CONCEALED HINGES, TOUCH LATCH WITH MAGNETIC CATCH, 3/16" REVEAL AT THE EDGES HIDDEN',
            'IN THE 4" MARGINS. ONE UPPER BOX AND ONE DADO BOX ON THE DOOR, THE MARGINS EITHER SIDE ARE PLAIN WALL. NO DEVICES ON THIS WALL. PT-02, CROWN CM-01, BASE.']

def nook_east(v):
    """Exterior wall, looking east: the settee wall, left open to the bedroom side per Zack (no cut wall drawn)."""
    L = inch(NOOK_S - NOOK_N)                                 # 93.8
    ac = L / 2
    bw = (L - 3 * M) / 2                                    # owner 11.09.26: no art, no picture light; two upper and two dado boxes, aligned
    bays = [(M, M + bw), (L - M - bw, L - M)]
    shell(v, L, crown=[(0, L)], base=[(0, L)], cut_left=False)
    C.panel_wall(v, 0, L, CH, upper=False, dado=False)
    db = aligned_boxes(v, bays)
    C.rev_cloud(v, M - 2, BASE + 1, L - M + 2, CH - TRIM['crown'] - 1, pad=1.0, tag_at='tl')
    oxs = [(a + b) / 2 for a, b in db]
    for ox in oxs: C.outlet(v, ox)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, bays[0][0], oxs[0], bays[0][1], ac, bays[1][0], oxs[1], bays[1][1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, BASE, CAP, CH - TRIM['crown'], CH, H]))
    return ['NOOK EAST WALL (EXTERIOR), LOOKING EAST, NORTH AT THE LEFT. A SETTEE GOES HERE LATER (N.I.C., NOT DRAWN). NO ART, NO PICTURE LIGHT (OWNER 11.09.26).',
            'TWO UPPER AND TWO DADO BOXES, %s WIDE, ALIGNED. DUPLEX OUTLETS VERTICAL, CL 1\'-6", CENTERED IN THE DADO BOXES, FOR TABLE LAMPS. PT-02, CROWN CM-01, BASE.' % E.ftin(round(bw * 8) / 8)]

def nook_south(v):
    """Terrace doors, looking south, east at the left. The bookcase on the nook west wall stands 4" off this wall and is seen at the right;
    the drapery pocket and the west stack stop at its side."""
    L = inch(NOOK_E - NOOK_W)
    fd = (inch(NOOK_E - FRENCH[1]), inch(NOOK_E - FRENCH[0]))   # 22.0 to 78.0
    bk = L - BOOK_D                                             # bookcase side face
    st = bk - (fd[1] + CS)                                      # 5": the stacks, the same both sides
    stack = (fd[0] - CS - st, fd[1] + CS + st)
    shell(v, L, crown=[(0, L)], base=[(0, fd[0] - CS), (fd[1] + CS, L)])
    C.casing(v, fd[0], fd[1] - fd[0], HEAD)
    leaf_away(C.door_pair, v, fd[0], fd[1] - fd[0], HEAD - 2.0, panels='glass', cased=False)   # FOR's 8'-0" is the frame: leaves 7'-10" under a 2" head (review 11.09.26)
    C._rect(v, fd[0], HEAD - 2.0, fd[1], HEAD, C.OUTLINE)                          # frame head
    C.rev_cloud(v, fd[0] - CS, 1.5, fd[1] + CS, HEAD + CS, pad=1.5)
    C._rect(v, fd[0] - CS, 0, fd[1] + CS, 0.75, C.OUTLINE)   # threshold
    C.panel_wall(v, 0, L, CH, openings=[(fd[0] - CS, fd[1] + CS)])
    C._rect(v, 0, H - POCKET_D, bk, H, C.FINE, MID, dashes='[2 1.5] 0')   # FOR's 5" curtain pocket, east wall to the bookcase side
    C.switch(v, stack[0] / 2, SW, 'S')                         # open side of the east casing, clear of the stack
    C.outlet(v, fd[1] + CS + st / 2)                            # west of the casing, between it and the bookcase side
    C._rect(v, bk, 0, L, H, C.OUTLINE, fill=WHITE)             # bookcase side panel, in front of the wall, to the ceiling
    C.base(v, bk, L); C.crown(v, bk, L, CH)
    C._line(v, (bk, 31.25), (L, 31.25), C.FINE, MID)           # stone top line behind the side, for reference
    pass   # pocket noted in the view note (the rev 1 cloud runs where a tag would sit)
    v.text(v.X((bk + L) / 2) + 2.5, v.Y(60), 'BOOKCASE SIDE', 5.2, MID, align='c', rotate=90)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, stack[0], fd[0] - CS, fd[0], (fd[0] + fd[1]) / 2, fd[1], fd[1] + CS, bk, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUT_CL, BASE, 40, SW, HEAD, HEAD + CS, CH - TRIM['crown'], H]))
    return ['TERRACE DOORS, LOOKING SOUTH, EAST AT THE LEFT. FOR\'S DOOR 08: PAIR OF 2\'-4" x 7\'-10" FULL-LITE LEAVES IN A 5\'-0" x 8\'-0" FRAME, CENTERED ON THE NOOK AS FOR DRAWS THEM,',
            'SWING OUT, IMPACT-RATED LAMINATED GLASS, ALUMINUM OR FIBERGLASS FRAME, FLUSH ADA THRESHOLD 3/4", LEVER HANDLES CL 3\'-4", MULTIPOINT LOCK ON THE ACTIVE (WEST) LEAF,',
            'FLUSH BOLTS ON THE INACTIVE. CASED INSIDE, 5" WITH BACKBAND. PLAIN WALL EACH SIDE OF THE CASING, CAP, BASE AND CROWN RETURNING. THE BOOKCASE (VIEW 4) STANDS 4" OFF',
            'THIS WALL AT THE RIGHT: IT IS NARROWED TO 12" DEEP (WAS 14") AND THE WEST STACK STOPS AT ITS SIDE. DRAPERY: FOR\'S 5" CEILING POCKET FROM THE EAST WALL TO THE BOOKCASE,',
            'TRAVERSE TRACK, SHEER AND BLACKOUT, STACKS OVER THE CASING AND %s BEYOND EACH SIDE (N.I.C., NOT DRAWN). S: TERRACE LIGHTS, ON THE OPEN WALL EAST OF THE STACK, CL 4\'-0".' % E.ftin(st),
            'DUPLEX VERTICAL, CL 1\'-6", ON THE %s OF WALL WEST OF THE CASING (NEC 210.52 WALL SPACE, NOT IN THE BUILT-IN). PT-02, CROWN CM-01.' % E.ftin(st)]

def nook_west(v):
    """The bookcase wall, looking west, south at the left; the nook opens to the bedroom at the right, where the bedroom's west wall
    (the TV wall, ID-736) is seen 11 ft beyond."""
    Lw = inch(NOOK_S - S_FACE)                                # 50.0: the wall
    L = inch(NOOK_S - NOOK_N)                                 # 93.8: wall plus the opening to the bedroom
    bw = 42.0; bx = (Lw - bw) / 2
    pd = (inch(S_FACE - POCKET[1]), inch(S_FACE - POCKET[0]))  # door 19 in ID-736 view 4 terms (0 at the bedroom south wall)
    def B(x): return Lw + x                                    # ID-736 view 4 x to this view: the same direction, the south wall at Lw
    def far():                                                 # the bedroom west wall seen through the opening (ID-736 view 4, its south end)
        C.base(v, Lw, B(pd[0] - CS)); C.crown(v, Lw, L, CH)
        C._rect(v, Lw, CAP - 3, B(pd[0] - CS), CAP, C.OUTLINE)  # cap on the latch-side wall
        C._rect(v, B(pd[0] - CS), 0, B(pd[0]), HEAD + CS, C.OUTLINE); C._rect(v, B(pd[0] - CS), HEAD, L, HEAD + CS, C.OUTLINE)   # casing, cut at the opening
        C._line(v, (B(pd[0]), 0), (B(pd[0]), HEAD), C.OUTLINE); C._line(v, (B(pd[0]), HEAD), (L, HEAD), C.OUTLINE)   # door 19 leaf, runs on past the opening
        C._line(v, (B(pd[0]) + 4.5, 9), (B(pd[0]) + 4.5, HEAD - 4.5), C.MED); C._line(v, (B(pd[0]) + 4.5, 9), (L, 9), C.MED); C._line(v, (B(pd[0]) + 4.5, HEAD - 4.5), (L, HEAD - 4.5), C.MED)
        C._rect(v, B(pd[0]) + 2.3, 36, B(pd[0]) + 3.5, 40, C.OUTLINE)   # recessed pull at the south (latch) edge
        sw = (pd[0] - CS) / 2
        C.switch(v, B(sw), SW, 'S3'); C.outlet(v, B(sw))
    beyond(far)
    shell(v, Lw, crown=[(0, Lw)], base=[(0, bx), (bx + bw, Lw)], cut_right=False)
    C._line(v, (Lw, 0), (Lw, H), C.HEAVY); C._line(v, (Lw + 0.6, 0), (Lw + 0.6, H), C.FINE, LIGHT)   # outside corner of the nook wall
    v.line((v.X(Lw) - 8, v.Y(0)), (v.X(L) + 8, v.Y(0)), 1.2)
    spring = 80.0; top = 30.0; stone = 1.25
    C.arched_opening(v, bx, bw, spring)
    C.cabinet_lower(v, bx + 1.5, bw - 3, top, doors=2, pulls=False)
    C.shelves(v, bx + 1.5, bw - 3, top + stone, spring + 4, n=3)
    C._line(v, (bx + 1.5, spring + 4), (bx + bw - 1.5, spring + 4), C.FINE, LIGHT, '[1.5 1.5] 0')   # LED under the head
    C.outlet(v, bx + bw / 2, top + stone + 4.5, horizontal=True)   # on the back panel above the stone top, centered
    C.panel_wall(v, 0, Lw, CH, openings=[(bx - M, bx + bw + M)])
    tag(v, (Lw + L) / 2, 102.2, 'OPEN TO THE BEDROOM')     # the wall beyond is called out in the view note (review 11.09.26: the second label crossed the grey linework)
    sh = [top + stone + (spring + 4 - top - stone) * (i + 1) / 4 for i in range(3)]
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, bx, bx + bw, Lw, L]))
    v.dim_h(0, L, v.Y(0) + 27, E.snap_points([0, Lw, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, top + stone, top + stone + 4.5] + sh + [spring + 4, spring, spring + bw / 2, CH - TRIM['crown'], CH, H]))
    return ['NOOK WEST WALL: THE BOOKCASE, LOOKING WEST, SOUTH AT THE LEFT. THE NOOK WALL IS %s LONG AND ENDS AT AN OUTSIDE CORNER. RIGHT OF IT THE NOOK IS OPEN TO THE' % E.ftin(round(Lw * 8) / 8),
            'BEDROOM, AND THE BEDROOM\'S WEST WALL (ID-736 VIEW 4) IS SEEN %s BEYOND, DRAWN GREY: THE DUPLEX AND SWITCH, THE CASING AND DOOR 19.' % E.ftin(round(inch(NOOK_W - W_FACE) * 8) / 8),
            'ARCHED BUILT-IN 3\'-6" WIDE, CENTERED, 4" FROM EACH END, 12" DEEP (EXTERIOR WALL BEHIND, NO RECESS). 30" LOWER CABINET, TWO FLUSH DOORS ON TOUCH LATCHES (NO PULLS),',
            'ONE ADJUSTABLE SHELF INSIDE. 1-1/4" STONE TOP TO MATCH THE BATH, FLUSH WITH THE JAMBS. DUPLEX OUTLET HORIZONTAL ON THE BACK PANEL 4-1/2" ABOVE THE STONE, CENTERED',
            '(CHARGING, IN ADDITION TO THE WALL DUPLEX ON VIEW 3). THREE 1" ADJUSTABLE SHELVES ON 32 MM PINS AT EQUAL SPACING, 3/4" BACK PANEL, SPRING LINE 6\'-8", SEMICIRCULAR HEAD',
            'TO 8\'-5", 11" CLEAR TO THE CROWN. LED STRIP UNDER THE HEAD, DRIVER IN THE CABINET, TOUCH DIMMER IN THE HEAD. PAINTED PT-02 TO MATCH THE PANELS. CROWN CM-01 OVER THE ARCH AND AROUND THE CORNER, BASE',
            'RETURNS AT THE CABINET AND AROUND THE CORNER. NO BOXES ON THIS WALL: 4" MARGINS ONLY.']

# ================================================================== key plan (ID-734)
def key_plan(sh):
    import compose_plans as CP
    src = fitz.open(CP.BASE_KEY.replace('Base-clean', 'Base-furn')); sp = src[1]
    clip_disp = fitz.Rect(296, 722, 588, 1062)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    k = 8 / 3                                                  # 3/16 -> 1/2
    tw, th = clip_disp.width * k, clip_disp.height * k
    ax0, ay0, ax1, ay1 = FR.x0 + 6, FR.y0 + 24, TB_X - 10, FR.y1 - 6
    NCOL, GAP = 380.0, 40.0                                    # 11 x 17 sheet (11.07.26): a right-hand column (north arrow, changes, scale), the plan centered in the rest
    colx = ax1 - 20 - NCOL
    tx = ax0 + (colx - GAP - ax0 - tw) / 2; ty = ay0 + (ay1 - ay0 - th) / 2
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    dx, dy = tx - 291.667, ty - 164.667                         # the hand-placed items below were set on the 22 x 17 sheet's target: move them with it
    def O(x, y): return (x + dx, y + dy)
    sh.p.show_pdf_page(target, src, 1, clip=u, rotate=90)
    xref = sh.p.get_contents()[0]; st = sh.p.parent.xref_stream(xref).decode('latin1')
    parts = st.split('q ')
    for i in range(1, len(parts)):
        if 'Do' in parts[i]: parts[i] = f'{target.x0:.2f} {sh.p.rect.height - target.y1:.2f} {target.width:.2f} {target.height:.2f} re W n ' + parts[i]
    sh.p.parent.update_stream(xref, 'q '.join(parts).encode('latin1'))
    sys.path.insert(0, '/home/claude/flrwork/rev1'); import keyclip as KC
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(2, ['MASTER BEDROOM'])), 'key plan clip'
    for r_ in ((293.0, 758.0, 305.9, 778.0), (700.0, 975.0, 730.0, 979.5), (1036.0, 974.9, 1063.0, 979.5),
               (303.5, 202.0, 317.6, 264.0), (303.5, 521.0, 317.6, 587.0),        # bath fixtures beyond the west wall
               (901.3, 276.0, 924.0, 532.0),                                        # closet shelving beyond the east wall
               (565.0, 203.0, 656.0, 295.8)):                                       # linen closet, served from the hall   # clipped jamb at the window wall west end, wall-end ticks below the bookcase corner
        sh.rect((*O(r_[0], r_[1]), *O(r_[2], r_[3])), width=0, color=WHITE, fill=WHITE)
    def P(xpt, ypt): return (target.x0 + (xpt - clip_disp.x0) * k, target.y0 + (ypt - clip_disp.y0) * k)   # display coords
    def PF(x, y): return P(*D(x, y))                                                                         # FOR pt
    for hit in sh.p.search_for('MASTER BEDROOM') + sh.p.search_for('MASTER') + sh.p.search_for('BEDROOM'):
        if target.contains(hit): r = hit + (-4, -4, 4, 4); sh.rect((r.x0, r.y0, r.x1, r.y1), width=0, color=WHITE, fill=WHITE)
    lx, ly = P(414, 795); sh.text(lx, ly, 'MASTER BEDROOM', 13.0, INK, align='c')
    MX, MY, NX, NY = 387, 856, 520, 962                       # quad centers (base pt): the room clear of the bed, the nook clear of the bookcase
    marks = [(1, 'ID-735', 'N', MX, MY - 32), (2, 'ID-736', 'E', MX + 18, MY), (3, 'ID-735', 'S', MX, MY + 32), (4, 'ID-736', 'W', MX - 18, MY),
             (1, 'ID-737', 'N', NX, NY - 28), (2, 'ID-737', 'E', NX + 28, NY), (3, 'ID-737', 'S', NX, NY + 28), (4, 'ID-737', 'W', NX - 28, NY)]
    for n, sheet, d, x, y in marks:
        cx, cy = P(x, y); sh.elev_marker(cx, cy, n, sheet, d, r=24.0)
    mx_, my_ = O(450.0, 362.0)                                    # 1A: in the room clear of the door 18 swing, a leader from its arrow to the niche face
    sh.elev_marker(mx_, my_, '1A', 'ID-734', 'E', r=24.0)
    lx_, ly_ = O(501.0, 262.0); sh.line((mx_ + 31, my_), (lx_, ly_), 0.5, INK)
    q = sh.p.new_shape(); q.draw_circle(fitz.Point(lx_, ly_), 1.6); q.finish(color=INK, fill=INK, width=0.3); q.commit()
    def dtag(cx, cy, n):
        q = sh.p.new_shape(); q.draw_circle(fitz.Point(cx, cy), 10.0); q.finish(color=INK, width=0.6, fill=(1, 1, 1)); q.commit()
        sh.text(cx, cy + 3.2, n, 9.0, INK, align='c', raw=True)
    dtag(*O(420.0, 170.0), '18'); dtag(*O(358.0, 673.0), '19'); dtag(*O(961.5, 680.0), '21')
    sh.text(*O(969.0, 712.0), 'READING NOOK', 13.0, INK, align='c'); sh.text(*O(962.0, 606.0), 'SAFE CLOSET', 8.0, MID, align='c')
    NOTES_K = ['1. TV ON AN ARTICULATING BRACKET, WEST WALL, ON THE BED AXIS.', '2. ARCHED BOOKCASE, 12" DEEP, ON THE NOOK WEST WALL.',
               '3. KING BED WITH 18" NIGHTSTANDS, CENTERED ON THE HEADBOARD WALL.', '4. HIDDEN DOOR 21 IS A JIB DOOR, CENTERED ON THE NOOK NORTH WALL.',
               '5. ROOM LIGHTS SWITCHED AT THE ENTRY, THE BED AND DOOR 19.', '6. DRAPERY POCKETS AT THE WINDOW AND THE TERRACE DOORS.', '7. WINDOW E PER FOR: 5\'-0" x 5\'-0", SILL 3\'-0", HEAD 8\'-0".']
    NS, NL = 8.0, 15.0                                             # note size and pitch
    notes_k = wrap_note(sh.font, NOTES_K, NCOL, NS)
    VH = 120 * 4.5 + 58 + 16 + NOTE_LH * 3 + 16 + 30                 # view 1A cell at 3/4"
    stack = VH + 34 + 20 + NL * len(notes_k) + 46 + 20                # view 1A, changes, scale bar
    x = colx; y = (ay0 + ay1) / 2 - stack / 2
    nx, ny = target.x1 - 30, target.y0 + 44                        # north arrow beside the plan, in the clear corner over the nook
    q = sh.p.new_shape(); q.draw_circle(fitz.Point(nx, ny), 18.0); q.finish(color=INK, width=0.6); q.commit()
    q = sh.p.new_shape(); q.draw_polyline([fitz.Point(nx, ny - 15), fitz.Point(nx + 8, ny + 10), fitz.Point(nx, ny + 5), fitz.Point(nx - 8, ny + 10), fitz.Point(nx, ny - 15)])
    q.finish(color=INK, width=0.4, fill=INK); q.commit()
    sh.text(nx, ny - 24, 'N', 10.0, INK, bold=True, align='c', raw=True)
    sh.text((target.x0 + target.x1) / 2 - 60, target.y1 + 22, 'FLOOR 2 KEY PLAN', 10.0, INK, bold=True, raw=True)
    draw_view(sh, (x, y, x + NCOL, y + VH), NICHE_VIEW, '3/4'); y += VH + 34
    sh.text(x, y, "CHANGES FROM FOR'S PLAN", 8.0, INK, bold=True); y += 20
    for ln in notes_k: sh.text(x, y, ln, NS, MID); y += NL
    y += 34                                                        # graphic scale for the plan, 1/2" = 1'-0" (36 pt to the foot), 0 to 10 ft
    sh.rect((x, y - 5, x + 5 * 36, y), 0.5, INK, INK); sh.rect((x + 5 * 36, y - 5, x + 10 * 36, y), 0.5, INK, (1, 1, 1))
    for f_ in (0, 5, 10): sh.text(x + f_ * 36, y + 12, "%d'" % f_, 9.0, INK, align='c', raw=True)
    g = INK
    for (x0, y0, x1, y1, lab) in ((W_FACE, S_FACE - 2, NOOK_W, S_FACE - 2, 'DRAPERY POCKET, FULL WIDTH'), (NOOK_W + BOOK_D * IN, NOOK_S - 2, NOOK_E, NOOK_S - 2, 'DRAPERY POCKET, EAST WALL TO THE BOOKCASE')):
        a, b = PF(x0, y0), PF(x1, y1); sh.line(a, b, 2.0, g); sh.text((a[0] + b[0]) / 2, a[1] - 4, lab, 7.0, g, align='c')
    def box(x0, y0, x1, y1, w=0.8):
        a, b = PF(x0, y0), PF(x1, y1); sh.rect((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), width=w, color=g)
    by = (N_MAIN + NOOK_N) / 2
    box(E_FACE - 83 * IN, by - 38 * IN, E_FACE, by + 38 * IN)                 # king, 76 x 80 plus the 3" headboard
    box(E_FACE - 3 * IN, by - 38 * IN, E_FACE, by + 38 * IN, 0.5)
    for y0 in (N_MAIN, NOOK_N - 18 * IN): box(E_FACE - 16 * IN, y0, E_FACE, y0 + 18 * IN, 0.5)   # 18" nightstands
    bx_, by_ = PF(E_FACE - 44 * IN, by); sh.text(bx_, by_ + 3, 'KING BED', 8.0, g, align='c')
    box(W_FACE, by - 24 * IN, W_FACE + 3 * IN, by + 24 * IN)                 # 55" TV on its bracket, on the bed axis
    tx_, ty_ = PF(W_FACE + 6 * IN, by); sh.text(tx_, ty_ + 3, 'TV', 8.0, g)
    box(NOOK_W, S_FACE + 4 * IN, NOOK_W + BOOK_D * IN, NOOK_S - 4 * IN)      # bookcase 3'-6" x 12"
    kx_, ky_ = PF(NOOK_W + 15 * IN, (S_FACE + NOOK_S) / 2); sh.text(kx_, ky_ + 3, 'BOOKCASE', 8.0, g)

VIEWS = {'ID-735': ((1, 'NORTH ELEVATION - MASTER BEDROOM', ROOM_W, north), (3, 'SOUTH ELEVATION - MASTER BEDROOM', ROOM_W - inch(E_FACE - NOOK_W), south)),
         'ID-736': ((2, 'EAST ELEVATION - MASTER BEDROOM', inch(NOOK_N - N_MAIN), east), (4, 'WEST ELEVATION - MASTER BEDROOM', inch(S_FACE - REC_N), west)),
         'ID-737': ((1, 'READING NOOK - NORTH WALL', inch(NOOK_E - NOOK_W), nook_north), (2, 'READING NOOK - EAST WALL', inch(NOOK_S - NOOK_N), nook_east),
                    (3, 'READING NOOK - SOUTH WALL, TERRACE DOORS', inch(NOOK_E - NOOK_W), nook_south), (4, 'READING NOOK - WEST WALL, BOOKCASE', inch(NOOK_S - NOOK_N), nook_west))}
NICHE_VIEW = ('1A', 'ENTRY RECESS EAST SIDE, NICHE', STRIP_D, niche)       # drawn on the key plan sheet, beside the plan

# 11 x 17 review draft (11.07.26): short labels set clear of the ticks at the printed text size
def _dim_h(self, x0i, x1i, y_pt, pts_i, offset_lines=True):
    """Labels that fit sit over their segment. A short end segment is labeled outside its end, on the string.
    A short inner segment is labeled under the string with a leader to the segment, and the next string (the overall) drops clear of it."""
    y_pt += getattr(self, '_push', 0.0); self._push = 0.0
    xs = [self.X(v) for v in pts_i]
    E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
    self.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
    for x in xs: self.line((x, y_pt - 3), (x, y_pt + 3), 0.4); self.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)
    segs = [(a, b) for a, b in zip(pts_i, pts_i[1:]) if b - a >= 0.5]; last_r = -1e9; under = False
    for i, (a, b) in enumerate(segs):
        lab = E.ftin(b - a); seg = (b - a) * self.k; tw = self.F.text_length(lab, fontsize=5.5)
        if seg >= tw + 5: self.text((self.X(a) + self.X(b)) / 2, y_pt - 2.5, lab, 5.5, align='c'); continue
        tw = self.F.text_length(lab, fontsize=5.0)
        if i == 0 and a == pts_i[0]: self.text(self.X(a) - 5, y_pt + 2.3, lab, 5.0, align='r'); continue
        if i == len(segs) - 1 and b == pts_i[-1]: self.text(self.X(b) + 5, y_pt + 2.3, lab, 5.0, align='l'); continue
        xm = (self.X(a) + self.X(b)) / 2; xl = max(xm, last_r + tw / 2 + 4)
        self.line((xm, y_pt + 1.0), (xl, y_pt + 5.0), 0.3, MID)
        self.text(xl, y_pt + 11.5, lab, 5.0, align='c'); last_r = xl + tw / 2; under = True
    self._push = 10.0 if under else 0.0
def _dim_v(self, y0i, y1i, x_pt, pts_i, side='r'):
    """Short segments are labeled on the outer side of the string with a leader to the segment, stepped out when two meet."""
    ys = [self.Y(v) for v in pts_i]
    E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
    self.line((x_pt, ys[0]), (x_pt, ys[-1]), 0.4)
    for y in ys: self.line((x_pt - 3, y), (x_pt + 3, y), 0.4); self.line((x_pt - 1.8, y + 1.8), (x_pt + 1.8, y - 1.8), 0.6)
    prev_short = False; left = x_pt < self.X(0) + 1
    for a, b in zip(pts_i, pts_i[1:]):
        if b - a < 0.5: continue
        lab = E.ftin(b - a); cy = (self.Y(a) + self.Y(b)) / 2; seg = (b - a) * self.k
        if seg >= self.F.text_length(lab, fontsize=5.5) + 5:
            self.text(x_pt - 2.5 if side == 'r' else x_pt + 7.5, cy, lab, 5.5, align='c', rotate=90); prev_short = False; continue
        o = 8.0 if prev_short else 0.0
        if left:
            self.line((x_pt - 0.6, cy), (x_pt - 4.0 - o, cy), 0.3, MID); self.text(x_pt - 4.6 - o, cy, lab, 5.0, align='c', rotate=90)
        else:
            self.line((x_pt + 0.6, cy), (x_pt + 5.6 + o, cy), 0.3, MID); self.text(x_pt + 11 + o, cy, lab, 5.0, align='c', rotate=90)
        prev_short = not prev_short
E.ElevationView.dim_h = _dim_h; E.ElevationView.dim_v = _dim_v

# 11 x 17 review draft (11.07.26): build information only, two short lines per view
PRINT_NOTES = {
 'north': ['ENTRY RECESS, DOOR 18 3\'-0" x 8\'-0" CENTERED. S3 AT THE LATCH SIDE, CL 4\'-0" (ROOM LIGHTS, WITH S4 AT THE BED AND S3 AT DOOR 19).',
           'PICTURE-FRAME PANELS WP-02 (PAINTED PT-02), CAP AT 3\'-4", BASE. CEILING 9\'-10" (FOR): CROWN CM-01 HELD 4" DOWN, LED COVE ABOVE, SEE 4/ID-502. OUTLETS VERTICAL IN THE DADO BOXES, CL 1\'-6".', 'NICHE: SEE VIEW 1A ON ID-734.'],
 'niche': ['MILLWORK NICHE 1\'-4" DEEP, OPENING 3\'-4" TO 7\'-11-7/8".', 'TWO 3/4" FIXED SHELVES, EQUAL OPENINGS, PT-02.'],
 'east': ['KING BED CENTERED, 18" NIGHTSTANDS 26" HIGH. SWING-ARM SCONCES CL 5\'-0", CENTERED IN THE NARROW PANELS. PANELS NARROW, WIDE, NARROW, ALIGNED, THE WIDE ONE ON THE BED.',
          'DUPLEX WITH USB BEHIND EACH NIGHTSTAND, CL 1\'-6". S4 IN THE END MARGIN, CL 2\'-8". PANELS WP-02, CROWN CM-01 WITH LED COVE, SEE 4/ID-502.'],
 'south': ['FOR\'S WINDOW E, 5\'-0" x 5\'-0" CASEMENT, DIVIDED LITES, SILL 3\'-0", HEAD 8\'-0", IMPACT-RATED, CASED 5", ONE DADO BOX UNDER THE APRON. 9\'-6" CEILING BAND WITH FOR\'S 5" CURTAIN POCKET, FULL WIDTH.',
           'OUTLETS VERTICAL IN THE DADO BOX EACH SIDE OF THE WINDOW, CL 1\'-6". PANELS WP-02 (PAINTED PT-02), CROWN CM-01, BASE.'],
 'west': ['POCKET DOOR 19, 3\'-0" x 8\'-0", CASED, PULL AT THE SOUTH EDGE. S3 SOUTH OF THE CASING, CL 4\'-0".',
          '55" TV ON AN ARTICULATING BRACKET ON THE BED AXIS, DUPLEX AND DATA BEHIND IT, NO PICTURE LIGHT. ONE WIDE DADO BOX UNDER THE TV BOX, THE OTHERS ALIGNED. PANELS WP-02, CROWN CM-01 WITH LED COVE, SEE 4/ID-502.'],
 'nook_north': ['HIDDEN DOOR 21, 2\'-8" x 8\'-0", JIB DOOR: FLUSH LEAF, PANELS, CAP, BASE AND CROWN RUN ACROSS IT.',
                'CONCEALED HINGES, TOUCH LATCH, NO CASING. NO DEVICES. PANELS WP-02 (PAINTED PT-02), CROWN CM-01.'],
 'nook_east': ['NO ART, NO PICTURE LIGHT. TWO UPPER AND TWO DADO BOXES, ALIGNED.', 'OUTLETS VERTICAL CENTERED IN THE DADO BOXES, CL 1\'-6". PANELS WP-02 (PAINTED PT-02), CROWN CM-01, BASE.'],
 'nook_south': ['FOR\'S DOOR 08: PAIR OF 2\'-4" x 7\'-10" FULL-LITE LEAVES IN AN 8\'-0" FRAME, DIVIDED LITES, SWING OUT, IMPACT-RATED, TEMPERED. CASED 5". CEILING 9\'-6" (FOR).',
                'S TERRACE LIGHTS CL 4\'-0", DUPLEX CL 1\'-6". DRAPERY IN FOR\'S 5" CEILING POCKET. PANELS WP-02 (PAINTED PT-02), CROWN CM-01.'],
 'nook_west': ['ARCHED BOOKCASE 3\'-6" x 12" DEEP, 30" CABINET, STONE TOP, THREE SHELVES, LED UNDER THE ARCH.',
               'DUPLEX ON THE BACK PANEL ABOVE THE STONE. BOOKCASE PAINTED PT-02. BEDROOM WALL BEYOND IN GREY (ID-736 VIEW 4).'],
}

ML, MR = 42.0, 38.0                                   # room left of a view (FIN. FLR. label) and right of it (the height string and its labels)
NOTE_SZ, NOTE_LH = 6.5, 11.5

def wrap_note(font, lines, width, size):
    out = []
    for ln in lines:
        cur = ''
        for w_ in ln.split():
            t_ = (cur + ' ' + w_).strip()
            if font.text_length(t_, fontsize=size) > width and cur: out.append(cur); cur = w_
            else: cur = t_
        out.append(cur)
    return out

def draw_view(sh, cell, view, sc, with_notes=True):
    """One elevation in its cell: title bar, the drawing with its dimension strings, the notes under it, the group centered below the title."""
    n, title, L, fn = view; k = E.SCALES[sc]
    global H, CH
    H, CH = VIEW_H.get(fn.__name__, (118.0, 114.0))
    E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" = 1\'-0"' % sc)
    spec = {'room': 'MASTER BEDROOM', 'view': title, 'length': L, 'ceiling': H}
    ox = cell[0] + (cell[2] - cell[0] - L * k - ML - MR) / 2 + ML
    notes = wrap_note(sh.font, PRINT_NOTES.get(fn.__name__, []), cell[2] - ox - 10, NOTE_SZ) if with_notes else []
    blk = H * k + 58 + 16 + NOTE_LH * len(notes)                 # drawing, the two strings under it, gap, notes
    top = cell[1] + 16 + max(18.0, (cell[3] - cell[1] - 16 - blk) / 2); oy = top + H * k
    assert ox - ML >= cell[0] - 0.5 and ox + L * k + MR <= cell[2] + 0.5 and top + blk <= cell[3] - 6, ('view does not fit its cell', title)
    v = E.ElevationView(sh.p, sh.font, sh.fontname, (ox, oy), k, spec)
    fn(v)
    if fn.__name__ == 'niche': v.dim_v(0, H, v.X(spec['length']) + 30, [0, H])   # niche: the left side carries the shelf string, so the overall goes outside the right string
    else: v.dim_v(0, H, v.X(0) - 20, [0, H], side='l')                               # overall, at the left, finish floor to ceiling (review 11.09.26)
    v.text(v.X(0) - 6, v.Y(0) - 2.5, 'FIN. FLR.', 5.0, MID, align='r')
    ny = oy + 58 + 16
    for ln in notes: sh.text(ox, ny, ln, NOTE_SZ, MID); ny += NOTE_LH

def draw_row(sh, views, sc, y0, y1, x0, x1, with_notes=True):
    """Views side by side, each cell as wide as its view needs, the slack shared out."""
    k = E.SCALES[sc]; need = [L * k + ML + MR for (_, _, L, _) in views]
    slack = x1 - x0 - sum(need); assert slack >= 0, ('row does not fit at', sc, slack)
    xs = x0
    for view, w in zip(views, need):
        draw_view(sh, (xs, y0, xs + w + slack / len(views), y1), view, sc, with_notes); xs += w + slack / len(views)

# ---- floor 2 key plan inset for the elevation sheets (11.07.26 review: fill the band under the 3/4" pair)
CLIP = fitz.Rect(296, 722, 588, 1062)
MASKS_OLD = ((293.0, 758.0, 305.9, 778.0), (700.0, 975.0, 730.0, 979.5), (1036.0, 974.9, 1063.0, 979.5),
             (303.5, 202.0, 317.6, 264.0), (303.5, 521.0, 317.6, 587.0), (901.3, 276.0, 924.0, 532.0), (565.0, 203.0, 656.0, 295.8))
WALLS = {'N': ((W_FACE, N_MAIN), (E_FACE, N_MAIN)), 'S': ((W_FACE, S_FACE), (NOOK_W, S_FACE)),
         'E': ((E_FACE, N_MAIN), (E_FACE, NOOK_N)), 'W': ((W_FACE, REC_N), (W_FACE, S_FACE))}
ACC = (0.85, 0.35, 0.1)

def key_inset(sh, x0, y0, sheet):
    """The master bedroom at 3/16" (the base at 1:1), the walls this sheet draws in the accent color, their markers."""
    import compose_plans as CP, keyclip as KC
    from shapely.geometry import box
    src = fitz.open(CP.BASE_KEY.replace('Base-clean', 'Base-furn')); sp = src[1]
    u = CLIP * sp.derotation_matrix; u.normalize(); k = 1.0
    target = fitz.Rect(x0, y0, x0 + CLIP.width, y0 + CLIP.height)
    sh.p.show_pdf_page(target, src, 1, clip=u, rotate=90)
    assert KC.apply(sh.p, target, CLIP, k, KC.room_poly(2, ['MASTER BEDROOM'])), 'inset clip'
    assert KC.apply(sh.p, target, CLIP, k, box(CLIP.x0, CLIP.y0, CLIP.x1, CLIP.y1)), 'inset clip'
    def P(x, y): return (target.x0 + (x - CLIP.x0) * k, target.y0 + (y - CLIP.y0) * k)
    def PF(x, y): return P(*D(x, y))
    for r_ in MASKS_OLD:                                       # the same masks as the key plan (set there in 22 x 17 display space)
        a = P(296 + (r_[0] - 291.667) * 0.375, 722 + (r_[1] - 164.667) * 0.375); b = P(296 + (r_[2] - 291.667) * 0.375, 722 + (r_[3] - 164.667) * 0.375)
        sh.rect((a[0], a[1], b[0], b[1]), width=0, color=WHITE, fill=WHITE)
    for hit in sh.p.search_for('MASTER BEDROOM') + sh.p.search_for('MASTER') + sh.p.search_for('BEDROOM'):
        if target.contains(hit): r = hit + (-2, -2, 2, 2); sh.rect((r.x0, r.y0, r.x1, r.y1), width=0, color=WHITE, fill=WHITE)
    views = [v_ for v_ in VIEWS[sheet]]
    dirs = {'NORTH': 'N', 'SOUTH': 'S', 'EAST': 'E', 'WEST': 'W'}
    MX, MY = 387, 856
    off = {'N': (0, -24), 'S': (0, 24), 'E': (18, 0), 'W': (-18, 0)}
    for n, title, L, fn in views:
        d = dirs[title.split()[0]]
        a, b = WALLS[d]; pa, pb = PF(*a), PF(*b)
        sh.line(pa, pb, 3.0, ACC)                                 # the wall drawn on this sheet
        cx, cy = P(MX + off[d][0], MY + off[d][1]); sh.elev_marker(cx, cy, n, sheet, d, r=12.0)
    lx, ly = P(414, 795); sh.text(lx, ly, 'MASTER BEDROOM', 7.5, INK, align='c')
    nx, ny = target.x1 + 26, target.y0 + 30                       # north arrow beside the inset
    q = sh.p.new_shape(); q.draw_circle(fitz.Point(nx, ny), 12.0); q.finish(color=INK, width=0.6); q.commit()
    q = sh.p.new_shape(); q.draw_polyline([fitz.Point(nx, ny - 10), fitz.Point(nx + 5, ny + 7), fitz.Point(nx, ny + 3), fitz.Point(nx - 5, ny + 7), fitz.Point(nx, ny - 10)])
    q.finish(color=INK, width=0.4, fill=INK); q.commit()
    sh.text(nx, ny - 16, 'N', 8.0, INK, bold=True, align='c', raw=True)
    sh.text(target.x0, target.y1 + 20, 'FLOOR 2 KEY PLAN, 3/16" TO 1\'-0"', 9.0, INK, bold=True, raw=True)
    return target

def notes_band(sh, x0, x1, ycen, sheet):
    """The notes for the sheet's views, one column a view, larger than the in-cell notes."""
    views = VIEWS[sheet]; gap = 50.0; cw = (x1 - x0 - gap * (len(views) - 1)) / len(views)
    blocks = []
    for n, title, L, fn in views:
        blocks.append((n, title, wrap_note(sh.font, PRINT_NOTES[fn.__name__], cw, 8.0)))
    hmax = max(22 + 15 * len(b[2]) for b in blocks); y0 = ycen - hmax / 2
    for i, (n, title, lines) in enumerate(blocks):
        x = x0 + i * (cw + gap); y = y0
        sh.text(x, y, str(n), 11.0, ACC, serif=True, raw=True); sh.text(x + 16, y, title, 11.0, INK, serif=True, raw=True); y += 22
        for ln in lines: sh.text(x, y, ln, 8.0, MID); y += 15

def build():
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    idd_sheet.EXTRA_REVS[:] = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', '11.06.26', 'REDRAWN ON FOR REV 1')]
    doc = fitz.open()
    X0, Y0, X1, Y1 = FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6        # drawing area, 24 pt clear of the top frame
    s0 = Sheet(doc); s0.frame('MASTER BEDROOM ELEVATIONS', 'KEY PLAN, SCALE: 1/2" TO 1\'-0"', ['MASTER BEDROOM', 'ELEVATIONS KEY PLAN'], 'ID-734', legend_rule=False)
    key_plan(s0)
    for sheet in ('ID-735', 'ID-736'):                               # two walls a sheet at 3/4", side by side (two rows of 10'-0" walls need 3/4" x 2 = 1,216 pt), the key plan and notes under them
        sh = Sheet(doc); sh.frame('MASTER BEDROOM ELEVATIONS', 'SCALE: 3/4" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'MASTER BEDROOM'], sheet, legend_rule=False)
        CH = 16 + 18 + 118.0 * 4.5 + 58 + 16 + 8   # tallest view (9'-10")
        draw_row(sh, VIEWS[sheet], '3/4', Y0, Y0 + CH, X0, X1, with_notes=False)
        b0, b1 = Y0 + CH + 14, Y1; ih = CLIP.height + 26
        t = key_inset(sh, X0 + 24, b0 + (b1 - b0 - ih) / 2, sheet)
        notes_band(sh, t.x1 + 90, X1 - 24, (b0 + b1) / 2, sheet)
    sh = Sheet(doc); sh.frame('MASTER BEDROOM ELEVATIONS - READING NOOK', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'MASTER BEDROOM NOOK'], 'ID-737', legend_rule=False)
    for cell, view in zip(E.layout_cells((X0, Y0, X1, Y1), 2, 2), VIEWS['ID-737']): draw_view(sh, cell, view, '1/2')
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
