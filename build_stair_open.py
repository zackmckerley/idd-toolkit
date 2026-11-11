"""ID-756, the open stair (owner 11.10.26): "I'd like to open up this area ... aluminum railing at the stairs. When the stairs turn to go
up further, I'd like to open up the wall too, so you can see the stairs going up. You can move the door ... as open as possible."
Picks (11.10.26): keep the storage under the stairs, vertical pickets, matte black.

What changes from FOR REV 1 (A-201, A-411):
  - FOR's 5" wall along the lower flight comes out; the flight gets an aluminum picket guard on its open (north) side.
  - Closet 27's west wall, along the east flight, is cut down to a knee wall that follows the stair's underside; above it the
    side is open to the 10'-8" head, the flight's cut stringer and oak treads show, and the guard runs up the flight. The closet
    stays under the stair.
  - Door 27 moves north to the full-height part of the wall under the northeast landing (the only place a 6'-8" door fits).
  - FOR's sconce on that wall moves to the stairwell's east wall; the tray's east slope is dropped so the opening runs to 10'-8".

Numbers are FOR's (build_great_rev1b PLAN block), converted to the living world: X = (x_pt - 626.2) / 1.5 east, Y = (844.5 - y_pt) / 1.5
north of the south gallery line. In the elevation looking east, u = -Y (inches south of the gallery line, north at the left)."""
import math
import pymupdf as fitz
import build_great_rev1b as G
import idd_elevations as E, idd_components as C
from idd_sheet import Sheet, FR, TB_X
from idd_std import INK, MID
from build_kitchen import wrap

W_ = lambda xp: (xp - 626.2) / 1.5                # FOR floor 1 x to world X
N_ = lambda yp: (844.5 - yp) / 1.5                # FOR floor 1 y to world Y
RS = G.R_RISER; LSE = G.LAND_SE; LNE = G.LAND_NE; ST = G.STRUCT; HEAD = G.SOFFIT
TREAD = 11.0
XE = W_(G.R1_E)                                   # 280.0, the east wall face (the stair's east wall)
XCW0, XCW1 = W_(G.R1_CW[0]), W_(G.R1_CW[1])        # 230.7, 236.7: closet 27's west wall, now the knee wall
U_KW = -N_(G.R1_KW[2])                            # 147.3: the knee wall's south end (FOR's 5" wall started here)
U_LF = -N_(G.R1_KW[3])                            # 152.3: the lower flight's north edge (FOR's 5" wall's south face)
U_S = -N_(G.R1_S)                                 # 196.7: the south wall face (the entry wall)
X_LF0, X_LF1 = W_(G.R1_LF[0]), W_(G.R1_LF[1])     # 169.4, 235.4: the lower flight's bottom and top risers
U_TOP = -N_(G.R2_HS)                              # 45.1: the east flight's top riser at the northeast landing (floor 2 hall's south wall)
U_BOT = U_TOP + 9 * TREAD                         # 144.1: its first riser at the southeast landing (10 risers, 9 treads)
U_N = 6.0                                         # the gallery beam's back face, the north end of the wall
BEAM = (-N_(850.4), -N_(865.0))                   # FOR's concrete block beam across closet 27's north end (A-WALL-BLOCK 850.4 to 862.4) and its drywall (865):
                                                  # 3-3/4" to 13-5/8" south; it stays (owner 11.10.26: "the door will have to be adjacent to it")
DOOR_W, DOOR_H = 28.0, 80.0                       # door 27 as FOR (2'-4"), 6'-8"
U_D0 = round(BEAM[1] * 8) / 8 + 0.125             # its north jamb against the beam's drywall face
U_D1 = U_D0 + DOOR_W
U_OPEN = U_D1 + 3.5 + 3.5                         # the opening's north return: the casing, then 3-1/2" of wall (the top riser is at 45.1)
U_OLD = (-N_(976.6), -N_(933.4))                  # FOR's door 27 (59.4 to 88.1 south)
MOVED = round((U_OLD[0] + U_OLD[1]) / 2 - (U_D0 + U_D1) / 2)    # centerline to centerline, to the inch (3'-10")
GPOST = 2.0; GPICK = 0.75; GCLR = 3.75; GTOP = 36.0; GRAIL = 2.5; GBOT = 2.5   # bottom rail 1" to 2-1/2" over the nosing line (6" triangle, review 11.10.26)
BLACK = (0.08, 0.08, 0.08)


def nose(u):
    """The east flight's nosing line at u (inches south of the gallery line): 58-1/2" at the first nosing, 10'-4-5/16" at the top."""
    return LSE + RS + (U_BOT - u) * RS / TREAD


def under(u): return nose(u) - ST


def _clip_seg(a, b, zmax):
    """The part of segment a-b at or below zmax (the 10'-8" head hides the rest), or None."""
    (u0, z0), (u1, z1) = a, b
    if z0 > zmax and z1 > zmax: return None
    if z0 > zmax: u0, z0 = u0 + (u1 - u0) * (zmax - z0) / (z1 - z0), zmax
    if z1 > zmax: u1, z1 = u0 + (u1 - u0) * (zmax - z0) / (z1 - z0), zmax
    return (u0, z0), (u1, z1)


def stair_elev(v):
    """View 8: the south end looking east at closet 27's wall, cut at X 160 (west of the lower flight)."""
    L = U_S + 6.0
    G.floor_line(v, 0, L)
    # ---- beyond, grey: the stairwell's east wall with its handrail, the southeast landing behind the lower flight
    with G.beyond():
        for a, b in ((( U_BOT, nose(U_BOT) + 36.0), (U_TOP, nose(U_TOP) + 36.0)),):
            s = _clip_seg(a, b, HEAD - 0.5)
            if s: C._line(v, s[0], s[1], C.MED)
        C._line(v, (U_BOT, LSE + 36.0), (U_S, LSE + 36.0), C.MED)                # the handrail level round the landing
        C._line(v, (U_BOT, LSE), (U_S, LSE), C.MED)                              # the landing's edge behind the lower flight
        G.tag(v, (U_LF + U_S) / 2 + 4, LSE + 30.0, 'WALL HANDRAIL BEYOND, 3\'-0"', 5.0, G.GREY, box=True)
    # ---- the knee wall under the east flight (painted, closet 27 behind it), its top on the stair's underside
    kw = [(U_OPEN, 0), (U_OPEN, under(U_OPEN)), (U_BOT, under(U_BOT)), (U_BOT, LSE - 1.0), (U_LF, LSE - 1.0), (U_LF, 0)]   # it runs on to the lower flight
    C._poly(v, kw, C.OUTLINE, fill=G.WHITE)
    C.base(v, U_OPEN, U_LF)
    # ---- the east flight's cut stringer (painted) and oak treads, seen from the open side
    pts = [(U_BOT, LSE)]
    for i in range(1, 11):
        u_i = U_BOT - TREAD * (i - 1); z_i = LSE + i * RS
        pts += [(u_i, z_i), (max(u_i - TREAD, U_TOP), z_i)]
    pts += [(U_TOP, under(U_TOP)), (U_BOT, under(U_BOT))]
    for a, b in zip(pts, pts[1:]):
        s = _clip_seg(a, b, HEAD)
        if s: C._line(v, s[0], s[1], C.OUTLINE)
    C._line(v, (U_TOP, under(U_TOP)), (U_BOT, under(U_BOT)), C.FINE, MID)     # the reveal where the stringer meets the knee wall
    for i in range(1, 11):                                                       # treads 1" thick, 1" nosing, returned on the open end
        u_i = U_BOT - TREAD * (i - 1); z_i = LSE + i * RS
        if z_i <= HEAD: C._rect(v, max(u_i - TREAD, U_TOP), z_i - 1.0, u_i + 1.0, z_i, C.MED, fill=(0.86, 0.8, 0.72))
    C._rect(v, U_BOT, LSE - 1.0, U_LF, LSE, C.MED, fill=(0.86, 0.8, 0.72))       # the landing's oak edge
    # ---- the full-height wall north of the opening (it hides the flight's top), door 27 against the concrete beam
    C._rect(v, 0, 0, U_OPEN, HEAD, C.OUTLINE, fill=G.WHITE)
    C.casing(v, U_D0, DOOR_W, DOOR_H, cs=3.5); C.door_leaf(v, U_D0, DOOR_W, DOOR_H, panels=2, swing=None, pull='R')
    C.base(v, 0, U_D0 - 3.5); C.base(v, U_D1 + 3.5, U_OPEN)
    for a_, b_ in (((BEAM[0], DOOR_H + 3.5), (BEAM[0], under(U_TOP))), ((BEAM[1], DOOR_H + 3.5), (BEAM[1], under(U_TOP))), ((BEAM[0], under(U_TOP)), (BEAM[1], under(U_TOP))),
                   ((BEAM[0], 8.5), (BEAM[0], DOOR_H + 3.5)), ((BEAM[1], 8.5), (BEAM[1], DOOR_H + 3.5))):
        G.hid(v, a_, b_, C.FINE, MID)                                            # FOR's block beam beyond the wall face (hidden)
    # ---- the guard: level along the landing's edge, raked up the flight, clipped at the 10'-8" head
    posts = [U_LF - 1.0, U_BOT - 1.0]
    n_ = max(1, math.ceil((U_BOT - 1.0 - (U_OPEN + 1.0)) / 72.0))
    posts += [U_BOT - 1.0 - k * (U_BOT - U_OPEN - 2.0) / n_ for k in range(1, n_ + 1)]
    def g_nose(u): return LSE if u >= U_BOT else nose(u)
    def top(u): return g_nose(u) + GTOP
    # rails: the level run over the landing and the raked run up the flight
    for z_off, h in ((GTOP - GRAIL, GRAIL), (GBOT - 1.5, 1.5)):
        segs = [((U_LF - 1.0, LSE + z_off), (U_BOT - 1.0, LSE + z_off)), ((U_BOT - 1.0, nose(U_BOT - 1.0) + z_off), (U_OPEN + 1.0, nose(U_OPEN + 1.0) + z_off))]
        for a, b in segs:
            s0 = _clip_seg(a, b, HEAD); s1 = _clip_seg((a[0], a[1] + h), (b[0], b[1] + h), HEAD)
            if s0 and s1: C._poly(v, [s0[0], s0[1], s1[1], s1[0]], C.MED, BLACK, fill=BLACK)
            elif s0: C._line(v, s0[0], s0[1], C.MED, BLACK)
    # pickets between posts at 3-3/4" clear
    for a, b in zip(sorted(posts, reverse=True), sorted(posts, reverse=True)[1:]):
        lo, hi = b + GPOST / 2, a - GPOST / 2
        n = max(1, math.ceil((hi - lo - GCLR) / (GPICK + GCLR) - 1e-6)); clr = (hi - lo - n * GPICK) / (n + 1)
        x = lo + clr
        for _ in range(n):
            c_ = x + GPICK / 2; z0 = g_nose(c_) + GBOT; z1 = min(top(c_) - GRAIL, HEAD)
            if z0 < HEAD: C._rect(v, x, z0, x + GPICK, z1, C.FINE, BLACK, fill=BLACK)
            x += GPICK + clr
    u_c = U_BOT - (HEAD - GTOP - LSE - RS) * TREAD / RS                       # where the top rail meets the head
    C._rect(v, U_OPEN + 1.0, HEAD - 1.5, u_c, HEAD, C.MED, BLACK, fill=BLACK)     # 1-1/2" channel under the header takes the pickets
    for c in posts:
        z0 = g_nose(c) - 1.0; z1 = min(top(c) + 0.75, HEAD)
        if z0 < HEAD: C._rect(v, c - GPOST / 2, z0, c + GPOST / 2, z1, C.OUTLINE, BLACK, fill=BLACK)
    # ---- the lower flight seen from its foot: seven risers stacked, its north stringer and guard end-on
    for k in range(1, 8):
        C._rect(v, U_LF, (k - 1) * RS, U_S, k * RS - 1.0, C.FINE, fill=G.WHITE)
        C._rect(v, U_LF, k * RS - 1.0, U_S, k * RS, C.MED, fill=(0.86, 0.8, 0.72))
    C._rect(v, U_LF - 2.5, RS, U_LF - 0.5, LSE + GTOP + 0.75, C.OUTLINE, BLACK, fill=BLACK)   # the lower flight's posts, end on
    # ---- the cut: the gallery beam and floor 2 over the south end, the tray's south slope, the entry wall
    G.poche(v, 0, U_N, HEAD, G.FF2)
    sl0 = U_S - G.SLOPE_RUN
    C._poly(v, [(0, HEAD), (sl0, HEAD), (U_S, G.SLOPE0), (U_S, G.FF2), (0, G.FF2)], C.HEAVY, INK, fill=G.POCHE)
    G.poche(v, U_S, L, 0, G.FF2)
    C._line(v, (U_OPEN, HEAD), (U_KW, HEAD), C.HEAVY)                               # the head of the opening, 10'-8"
    # ---- tags, in clear field with leaders
    def lead(a, t, lines_, c=INK):
        C._line(v, a, (t[0], t[1] + 2.0), C.FINE, c); v.p.draw_circle(fitz.Point(v.X(a[0]), v.Y(a[1])), 0.9, color=c, fill=c, width=0)
        for j, s_ in enumerate(lines_): G.tag(v, t[0], t[1] - 6.0 * j, s_, 5.0, c, box=True)
    lead((U_D0 + DOOR_W / 2, 60.0), (92.0, 64.0), ['DOOR 27, MOVED ABOUT %s NORTH,' % E.ftin(MOVED), 'AGAINST FOR\'S CONCRETE BEAM;', 'CLOSET 27 STAYS UNDER THE STAIR'])
    lead(((BEAM[0] + BEAM[1]) / 2, under(U_TOP)), (26.0, HEAD - 7.0), ['CONC. BEAM BEYOND (FOR), STAYS'], MID)
    lead((112.0, HEAD - 0.75), (176.0, 106.0), ['OPEN TO THE STAIR, HEAD 10\'-8",', 'PICKETS INTO A CHANNEL AT THE HEAD'])
    lead((U_BOT - 12.0, nose(U_BOT - 12.0) + GTOP + 1.0), (176.0, 93.0), ['ALUMINUM PICKET GUARD, MATTE', 'BLACK, 3\'-0" OVER THE NOSINGS'])
    lead((126.0, nose(126.0) - 4.0), (122.0, 36.0), ['PAINTED CUT STRINGER,', 'OAK TREADS'], MID)
    G.tag(v, (U_OPEN + U_BOT) / 2, 16, 'KNEE WALL, PT-02, ON THE STAIR\'S UNDERSIDE', 5.0, MID, box=True)
    G.tag(v, (U_LF + U_S) / 2, LSE + 8, 'LOWER FLIGHT, 7 RISERS', 5.0, MID, box=True)
    G.tag(v, (U_LF + U_S) / 2, LSE + 15, 'SE LANDING +4\'-3-3/16"', 5.0, MID, box=True)
    G.tag(v, U_S - 22.0, 117.0, 'TRAY (FOR), AT THE CUT', 4.5, G.GREY, box=True)
    y1 = v.Y(0) + 16; y2 = y1 + 27
    v.dim_h(0, L, y1, E.snap_points([0, U_D0, U_D1, U_OPEN, U_KW, U_LF, U_S]))
    v.dim_h(0, L, y2, E.snap_points([0, BEAM[1], U_TOP, U_BOT, U_S]))
    v.dim_v(0, HEAD, v.X(L) + 30, E.snap_points([0, DOOR_H, under(U_OPEN), HEAD]))
    return ('CLOSET 27\'S WEST WALL CUT DOWN TO A KNEE WALL ON THE EAST FLIGHT\'S UNDERSIDE, OPEN ABOVE IT TO THE 10\'-8" HEAD: THE FLIGHT\'S PAINTED '
            'CUT STRINGER AND OAK TREADS SHOW, THE GUARD RUNS UP IT. CLOSET 27 STAYS UNDER THE STAIR; DOOR 27 MOVED ABOUT %s NORTH (CENTERLINE) TO THE FULL-HEIGHT WALL '
            'UNDER THE NORTHEAST LANDING, ITS NORTH JAMB AGAINST FOR\'S CONCRETE BEAM, WHICH STAYS (6\'-8" DOOR). STAIR PER FOR A-411: 21 RISERS AT 7-5/16", 11" TREADS. '
            'THE CUT IS WEST OF THE LOWER FLIGHT, THROUGH THE SOUTH END\'S TRAY; OVER THE TOP OF THE LOWER FLIGHT AND THE SOUTHEAST LANDING THE CEILING IS 11\'-0" '
            '(FOR: 10\'-11-1/4" MIN., 6\'-8" HEADROOM). FOR\'S SCONCE ON THIS WALL MOVES TO THE STAIRWELL\'S EAST WALL, 6\'-6" ABOVE THE NOSINGS (VERIFY).    '
            'ALUMINUM GUARD (OWNER 11.10.26: VERTICAL PICKETS, MATTE BLACK): 2" SQUARE POSTS AT THE ENDS, THE CORNERS AND 6\'-0" O.C. MAX., 1-1/2" x 2-1/2" TOP RAIL '
            '3\'-0" ABOVE THE NOSINGS AND AT THE LANDING (FBC R312.1.2: 34" MIN. ON A STAIR), 1-1/2" BOTTOM RAIL 1" OVER THE NOSING LINE (6" SPHERE AT THE '
            'TREAD, RISER AND RAIL TRIANGLE, FBC R312.1.3), 3/4" SQUARE PICKETS AT 3-3/4" CLEAR MAX. (4" SPHERE), POSTS SIDE-MOUNTED TO THE STRINGER; WHERE THE TOP RAIL MEETS '
            'THE 10\'-8" HEAD IT ENDS AT A POST AND THE PICKETS RUN INTO A 1-1/2" CHANNEL FASTENED TO THE HEADER (DETAIL BY THE FABRICATOR), POWDER-COATED MATTE BLACK TO MATCH THE '
            'GALLERY GUARD, DESIGNED BY THE FABRICATOR\'S ENGINEER (FBC R301.5: 200 LB AT THE TOP RAIL, 50 LB ON 1 SQ FT AT THE INFILL). WALL HANDRAILS 1-1/2" ROUND, '
            '3\'-0" ABOVE THE NOSINGS, EVERY FLIGHT, CONTINUOUS ROUND THE SOUTHEAST LANDING (FOR A-411). CLOSET 27 UNDER THE STAIR: 1/2" GYPSUM ON ITS WALLS AND THE '
            'STAIR\'S UNDERSIDE (FBC R302.7). FOR TO CONFIRM: THE KNEE WALL AND STRINGER FRAMING, THE HEADER AT 10\'-8", DOOR 27\'S NEW LOCATION, THE SCONCE MOVE.' % E.ftin(MOVED))


def stair_plan(sh, cell, k):
    """View 7: the south end and the stair, floor 1, cut at 4'-0" (the upper flight and landings dashed), north up."""
    X0, Y0 = 150.0, -212.0                                   # plan window: X 150 to 294, Y -212 to +12
    PW, PH = 294.0 - X0, 12.0 - Y0
    E.title_bar(sh.p, sh.font, sh.fontname, cell, 7, 'PARTIAL PLAN - THE SOUTH END AND THE STAIR, FLOOR 1', 'SCALE: 1/2" TO 1\'-0"')
    spec = {'room': 'SOUTH END', 'view': 'STAIR PLAN', 'length': PW, 'ceiling': PH}
    ox, oy = E.fit_origin(cell, spec, k, top=40, margin_b=70)
    v = E.ElevationView(sh.p, sh.font, sh.fontname, (ox, oy), k, spec)
    P = lambda X, Y: (X - X0, Y - Y0)                        # world inches to view inches
    def rect(x0, y0, x1, y1, w=C.OUTLINE, c=None, fill=None, dashes=None):
        a, b = P(x0, y0), P(x1, y1); C._rect(v, a[0], a[1], b[0], b[1], w, c, fill, dashes)
    def line(x0, y0, x1, y1, w=C.MED, c=None, dashes=None):
        C._line(v, P(x0, y0), P(x1, y1), w, c, dashes)
    def tag(X, Y, s, size=5.0, c=MID, box=True): G.tag(v, *P(X, Y), s, size, c, box)
    # walls, cut: the east wall, the entry wall, closet 27's north wall at the gallery line, the knee wall's full-height north part
    rect(XE, -208.7, XE + 12.0, 12.0, C.HEAVY, INK, G.POCHE)
    rect(155.3, -U_S - 6.0, XE, -U_S, C.HEAVY, INK, G.POCHE)
    rect(XCW0, -U_N, XE, 0.0, C.HEAVY, INK, G.POCHE)
    rect(XCW0, -U_D0, XCW1, -U_N, C.HEAVY, INK, G.POCHE); rect(XCW0, -U_OPEN, XCW1, -U_D1, C.HEAVY, INK, G.POCHE)
    rect(XCW0, -U_LF, XCW1, -U_OPEN, C.OUTLINE, INK, G.SEC)           # the knee wall, run on to the lower flight; below the cut at its south end
    rect(XCW1, -BEAM[0], XE, -BEAM[1], C.HEAVY, INK, (0.55, 0.55, 0.55))   # FOR's concrete block beam and its drywall, stays
    line(150.0, 0.0, XCW0, 0.0, C.FINE, MID, '[4 2] 0'); line(150.0, -U_N, XCW0, -U_N, C.FINE, MID, '[4 2] 0')   # the gallery beam over the opening
    tag(190.0, 4.0, 'LIVING ROOM', 6.0, INK, False)
    tag(190.0, -3.0, 'BEAM OVER, HEAD 10\'-8"', 4.5, MID, False)
    # door 27, moved: hinged at its north jamb, swings west into the south end
    hx, hy = XCW0, -U_D0
    rect(hx - DOOR_W, hy - 1.75, hx, hy, C.OUTLINE, INK, G.WHITE)              # the leaf, open 90 degrees
    C._arc(v, *P(hx, hy), DOOR_W, 180, 270, C.FINE)
    for yy in (-U_D0, -U_D1): line(XCW0 - 0.75, yy, XCW0, yy, C.FINE)
    # FOR's door 27 and 5" wall, removed (dashed)
    rect(XCW0, -U_OLD[1], XCW1, -U_OLD[0], C.FINE, MID, None, '[2 1.5] 0')
    rect(W_(G.R1_KW[0]), -U_LF, W_(G.R1_KW[1]), -U_KW, C.FINE, MID, None, '[2 1.5] 0')
    # the lower flight (below the cut), the southeast landing, the east flight to the cut, then dashed above it
    rect(X_LF0, -U_S, X_LF1, -U_LF, C.MED)
    for i in range(1, 6): x_ = X_LF0 + i * TREAD; line(x_, -U_S, x_, -U_LF, C.MED)
    for i in range(1, 11):
        y_ = -(U_BOT - TREAD * (i - 1)); line(XCW1, y_, XE, y_, C.FINE, MID, '[5 3] 0')   # the east flight, above the 4'-0" cut
    rect(XCW1, -U_TOP, XE, -BEAM[1], C.FINE, MID, None, '[5 3] 0')                 # the northeast landing, over the closet
    for i in range(4): x_ = XCW1 - TREAD * i; line(x_, -U_TOP, x_, -U_D0 + 1.0, C.FINE, MID, '[5 3] 0')   # the top flight, over the south end
    tag(XCW1 - 22.0, -9.6, 'TOP FLIGHT OVER', 4.0, MID, True)
    tag((XCW1 + XE) / 2, -24.0, 'CLOSET 27 UNDER', 5.0, INK); tag((XCW1 + XE) / 2, -30.0, 'THE STAIR', 5.0, INK)
    tag((XCW1 + XE) / 2, -7.6, 'CONC. BEAM (FOR), STAYS', 4.0, G.WHITE, False)
    tag((XCW1 + XE) / 2, -40.0, 'NE LANDING ABOVE', 4.5, MID, False)
    tag(258.0, -186.0, 'SE LANDING', 5.0, MID); tag(258.0, -192.0, '+4\'-3-3/16"', 4.5, MID, False)
    # the run: UP arrow from the foot of the lower flight
    a = [(X_LF0 + 4.0, -174.5), (257.0, -174.5), (257.0, -U_BOT + 4.0)]
    C._poly(v, [P(*p) for p in a], C.MED, INK, close=False)
    tx, ty = P(257.0, -U_BOT + 4.0); C._poly(v, [(tx - 2.0, ty - 5.0), (tx, ty), (tx + 2.0, ty - 5.0)], C.MED, INK, fill=INK)
    tag(X_LF0 + 14.0, -180.0, 'UP 21R', 5.0, INK, False)
    # the guard: along the lower flight's open side, round the landing's edge, up the east flight on the knee wall
    gy, gx = -(U_LF - 1.0), XCW1 - 1.0
    gl = [(X_LF0 + 1.0, gy), (gx, gy), (gx, -(U_OPEN + 1.0))]
    C._poly(v, [P(*p) for p in gl], 2.2, BLACK, close=False)
    posts = [(X_LF0 + 1.0, gy), ((X_LF0 + gx) / 2, gy), (gx, gy), (gx, -(U_BOT - 1.0))]
    n_ = max(1, math.ceil((U_BOT - U_OPEN - 2.0) / 72.0))
    posts += [(gx, -(U_BOT - 1.0 - j * (U_BOT - U_OPEN - 2.0) / n_)) for j in range(1, n_ + 1)]
    for px, py in posts: rect(px - 1.0, py - 1.0, px + 1.0, py + 1.0, C.FINE, BLACK, BLACK)
    # wall handrails, dashed, on the entry wall and the east wall
    line(X_LF0, -U_S + 2.25, XE - 2.25, -U_S + 2.25, C.FINE, INK, '[3 1.5] 0'); line(XE - 2.25, -U_S + 2.25, XE - 2.25, -U_TOP, C.FINE, INK, '[3 1.5] 0')
    # tags with leaders
    def leader(X, Y, Xt, Yt, lines_, c=INK):
        a_, b_ = P(X, Y), P(Xt, Yt); C._line(v, a_, (b_[0], b_[1] + 1.5), C.FINE, c)
        v.p.draw_circle(fitz.Point(v.X(a_[0]), v.Y(a_[1])), 0.9, color=c, fill=c, width=0)
        for j, s_ in enumerate(lines_): tag(Xt, Yt - 5.5 * j, s_, 5.0, c, True)
    leader(205.0, gy, 196.0, -128.0, ['ALUMINUM PICKET GUARD, MATTE BLACK,', '3\'-0" OVER THE NOSINGS (NEW)'])
    leader(gx, -100.0, 205.0, -96.0, ['KNEE WALL ON THE STAIR\'S', 'UNDERSIDE, OPEN ABOVE (NEW)'])
    leader(200.0, -U_KW - 2.5, 186.0, -143.0, ['FOR\'S 5" WALL, REMOVED'], MID)
    leader(XCW0 - 0.5, -(U_OLD[0] + U_OLD[1]) / 2, 204.0, -72.0, ['FOR\'S DOOR 27, MOVED'], MID)
    leader(XCW0 - 14.0, -U_D0 - 0.9, 178.0, -48.0, ['DOOR 27, 2\'-4" x 6\'-8",', 'MOVED ABOUT %s NORTH,' % E.ftin(MOVED), 'AGAINST THE CONC. BEAM'])
    tag(186.0, -74.0, 'SOUTH END', 7.0, INK, True)
    # dimensions along the west face of the knee wall
    xp = v.X(P(158.0, 0)[0])
    v.dim_v(0, PH, xp, E.snap_points([P(0, -U_S)[1], P(0, -U_LF)[1], P(0, -U_OPEN)[1], P(0, -U_D1)[1], P(0, -U_D0)[1], P(0, 0)[1]]), side='l')
    yp = v.Y(P(0, -U_S - 6.0)[1]) + 18
    v.dim_h(0, PW, yp, E.snap_points([P(X_LF0, 0)[0], P(X_LF1, 0)[0], P(XE, 0)[0]]))
    # the elevation marker for view 8, looking east at the knee wall
    cx, cy = v.X(P(212.0, -112.0)[0]), v.Y(P(212.0, -112.0)[1])
    sh.p.draw_circle(fitz.Point(cx, cy), 26.0, color=None, fill=G.WHITE, width=0); G.marker(sh, cx, cy, 8, 'ID-756', 'E', r=20.0)
    v.text(v.X(P(150.0, 0)[0]), v.Y(P(0, -U_S - 6.0)[1]) + 46, 'FLOOR 1, CUT AT 4\'-0". DASHED: ABOVE THE CUT, OR REMOVED. GREY: THE KNEE WALL, BELOW THE CUT.', 6.0, MID, align='l')
    # north arrow, top right
    C._poly(v, [P(266.0, 2.0), P(270.0, 2.0), P(268.0, 8.0)], C.FINE, INK, fill=INK); G.tag(v, *P(268.0, 9.5), 'N', 6.0, INK)
    return v


def sheet(doc, rev):
    """ID-756: view 7 (plan) at the left, view 8 (elevation looking east) at the right, both at 1/2"."""
    sh = Sheet(doc); sh.frame('LIVING ROOM ELEVATIONS', 'SCALE: 1/2" TO 1\'-0"', ['LIVING ROOM', 'THE STAIR, OPENED'], 'ID-756', revisions=rev, legend_rule=False)
    cells = E.layout_cells(G.FRAME, 2, 1)
    k = E.SCALES['1/2']
    stair_plan(sh, cells[0], k)
    G.draw_views(sh, [cells[1]], [(8, 'ELEVATION - THE STAIR SIDE, LOOKING EAST (CLOSET 27 WALL OPENED)', U_S + 6.0, G.FF2, stair_elev)], scale='1/2')
    return sh
