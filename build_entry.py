"""Entry (Zack's foyer) and powder room, floor 1, designed elevations on FOR REV 1. Owner 11.05.26: entry walls neutral with one large
framed mirror 5'-0" wide on the wall perpendicular to the front door (the west wall: the east wall carries the powder room door); the
powder room is the one dramatic room in a neutral house: floating vanity, framed mirror, wall-mounted faucet, a dark botanical wallcovering.
Sheets: ID-771 key plan and notes, ID-772 entry, ID-773 powder room. Output: 261105.HD102.EntryPowderPilot.pdf

Measured from FOR's vectors (A-WALL-*, A-DOOR), FOR sheet pt, 1.5 pt per inch, plan north = up the FOR sheet:
  entry       x 736.8 (west face) to 953.0 (powder room wall face); north face 1152.8; south face 1270.0 west of 893.2, 1252.0 east of it
  north       wall 736.8 to 780.7, cased opening to the hall 780.7 to 859.1, wall 859.1 to 953.0 (the stair rises north behind it)
  south       front door 01 leaf 751.0 to 835.0 (4'-8", hinged west, swings out), wall to 893.2, return to the 1252.0 face at 893.2, office
              door 11 leaf 900.8 to 948.8 (2'-8", hinged west, swings into the office), 4.2 pt to the corner
  east        powder room door 11 leaf 1195.7 to 1243.7 (2'-8", hinged south, swings into the powder room), wall to 1252.0
  powder room x 960.2 (west face) to 1046.2 (east face, 2" of furring and board on FOR's B2 CMU, block at 1049.2), y 1147.2 to 1252.0
              (4'-9-3/8" x 5'-9-7/8"); FOR's toilet on the east wall CL 1169.6 (15" off the north wall); FOR's vanity on the east wall 1193.4 to
              1252.0 (3'-3"), 1016.2 to 1046.2 (1'-8" deep), bowl CL 1222.0. The east wall is furred out on 2x4 for the wall faucet: face 1043.0
Heights assumed (VERIFY): ceiling 10'-0", door heads 8'-0"."""
import sys, math
sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG
from idd_std import INK, MID, TRIM
from build_kitchen import H, CR, TOP, shell, tag
from build_mud import IN, r8, F, x_of, para_block, door_leaf, NLH
from build_kitchen import NOTE, wrap
import base_rev1 as BR, keyclip as KC

# ------------------------------------------------------------------ 11 x 17 layout helpers (owner 11.07.26: drawings span the page, scale with room, bigger tags)
def draw_views(sh, cells, views, scale='1/2', ceiling=None):
    """Each view with its notes as one block centered in its cell, so a tall cell has no gap between the notes and the drawing."""
    ceiling = ceiling or H
    k = E.SCALES[scale]
    for cell, (n, title, L, fn, extra) in zip(cells, views):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" TO 1\'-0"' % scale)
        spec = {'room': 'ENTRY', 'view': title, 'length': L + extra, 'ceiling': ceiling}
        probe = E.ElevationView(Sheet(fitz.open()).p, sh.font, sh.fontname, (0, 0), k, spec)
        text = fn(probe)
        width = min(cell[2] - cell[0] - 16, 660)
        lines_ = wrap(text, NOTE, width) if text else []
        top = 30 + len(lines_) * NLH + 8
        need = top + ceiling * k + 44
        d = max(0.0, (cell[3] - cell[1] - need) / 2 - 12)
        inner = (cell[0], cell[1] + d, cell[2], cell[3] - d)
        origin = E.fit_origin(inner, spec, k, top=top)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        fn(v)
        v.text(v.X(0) - 6, v.Y(0) - 2.5, 'FIN. FLR.', 5.0, MID, align='r')
        ny = inner[1] + 30
        for ln in lines_: sh.text(cell[2] - 8, ny, ln, NOTE, MID, align='r'); ny += NLH

def cells_row(frame, needs):
    """One row of cells, widths in proportion to what each view needs."""
    x0, y0, x1, y1 = frame; tot = sum(needs); out = []; x = x0
    for w in needs:
        cw = (x1 - x0) * w / tot; out.append((x, y0, x + cw, y1)); x += cw
    return out

def quad_marker(sh, cx, cy, sheet, views, r=28.0):
    """Room marker for the print: sheet number in the center, a view number toward each wall, an arrow outside; text grows with r."""
    f = r / 18.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.7, fill=(1, 1, 1)); s_.commit()
    sh.text(cx, cy + 3.5, sheet.replace('ID-', ''), 10.0, INK, align='c', raw=True)                 # view and sheet numbers 10 pt and up (print 6.5 pt)
    for d_, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d_]
        tip = (cx + dx * (r + 6 * f), cy + dy * (r + 6 * f))
        b1 = (cx + dx * r - dy * 3.5 * f, cy + dy * r + dx * 3.5 * f); b2 = (cx + dx * r + dy * 3.5 * f, cy + dy * r - dx * 3.5 * f)
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
        sh.text(cx + dx * r * 0.7, cy + dy * r * 0.7 + 3.8, str(n), 11.0, INK, align='c', raw=True)

def scale_bar(sh, x0, y, pt_per_ft, label, feet=5):
    """Graphic scale starting at x0 (under its plan's lower left): one-foot blocks, feet marks under, the label at the bar's right end."""
    x1 = x0 + feet * pt_per_ft
    for i in range(feet):
        sh.rect((x0 + i * pt_per_ft, y - 5, x0 + (i + 1) * pt_per_ft, y), 0.4, INK, INK if i % 2 == 0 else (1, 1, 1))
    for i in range(feet + 1):
        sh.text(x0 + i * pt_per_ft, y + 11, "%d'" % i, 7.0, MID, align='c')
    sh.text(x1 + 14, y - 0.5, label, 9.0, INK, raw=True)
    return fitz.Rect(x0 - 6, y - 6, x1 + 100, y + 13)

def door_leaf_p(v, x, w, head, panels=2, swing='L', toward=False):
    """The set's swing-mark rule (solid when the door swings toward the viewer, dashed when away), with a dash long enough to
    read at 65% on the 11 x 17 print (a 2 / 1.5 dash read as a solid line on the steep marks of a narrow leaf)."""
    C._rect(v, x, 0, x + w, head, C.OUTLINE)
    st, rail_b, rail_t, mid = 4.5, 9, 4.5, 4.5
    split = rail_b + (head - rail_t - rail_b) * 0.62
    for y0, y1 in ((rail_b, split - mid / 2), (split + mid / 2, head - rail_t)):
        C._rect(v, x + st, y0, x + w - st, y1, C.MED); C._rect(v, x + st + 0.75, y0 + 0.75, x + w - st - 0.75, y1 - 0.75, C.FINE, MID)
    hinge, far = (x, x + w) if swing == 'L' else (x + w, x)
    d = None if toward else '[6 4] 0'
    C._line(v, (far, 0), (hinge, head / 2), C.FINE, INK, d); C._line(v, (far, head), (hinge, head / 2), C.FINE, INK, d)
    lever = far - 3 if far > hinge else far + 3
    C._ellipse(v, lever, 38, 0.9, 0.9, C.FINE); C._line(v, (lever, 38), (lever + (-3.5 if far > hinge else 3.5), 38), C.MED)

OUT = '/home/claude/flrwork/261105.HD102.EntryPowderPilot.pdf'
ISSUE = '11.05.26'
HEAD = 96.0; CS = TRIM['casing']
HC = HEAD + CS                                   # top of the head casing, 8'-5": the mirror tops line up with it

# ------------------------------------------------------------------ entry
FW, FE, FN, FS, FS2, JOG = 736.50, 953.28, 1152.54, 1269.96, 1251.96, 889.32   # FOR's drywall faces (11.06.26 recheck); JOG: the return's face
MIR_W, MIR_H = 36.0, 60.0                        # entry mirror, vintage frame, about 3'-0" x 5'-0" overall, 3'-5" to 8'-5" (owner 11.06.26)
MIR_B = HC - MIR_H
OUTLET = 18.0

def entry_north(v):
    L = r8((FE - FW) / IN)
    op = x_of(780.7, 859.1, n=FW); op = (r8(op[0]), r8(op[1]))
    shell(v, L, crown=[(0, L)], base=[(0, op[0] - CS), (op[1] + CS, L)])
    C.cased_opening(v, op[0], op[1] - op[0], HEAD)
    tag(v, (op[0] + op[1]) / 2, 60.0, 'HALL BEYOND', 5.0, MID)
    ox = (op[1] + L) / 2; C.outlet(v, ox, OUTLET)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, op[0], op[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUTLET, HEAD, HC, H]))
    return ('%s CASED OPENING TO THE HALL, 5" CASING, HEAD 8\'-0". DUPLEX CL 1\'-6" CENTERED ON THE SOLID WALL. PT-01, CM-01 CROWN.' % F(op[1] - op[0]))
def entry_east(v):
    L = r8((FS2 - FN) / IN)
    d = x_of(1195.7, 1243.7, n=FN); d = (r8(d[0]), r8(d[0]) + 32.0)
    shell(v, L, crown=[(0, L)], base=[(0, d[0] - CS)])
    C.casing(v, d[0], d[1] - d[0], HEAD)
    door_leaf_p(v, d[0], d[1] - d[0], HEAD, panels=2, swing='R', toward=False)          # swings into the powder room, away
    tag(v, (d[0] + d[1]) / 2, HC + 5.5, 'POWDER ROOM DOOR', 5.0, MID)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, HEAD, HC, H]))
    return ('POWDER ROOM DOOR: %s x 8\'-0" TWO-PANEL, SWINGS INTO THE POWDER ROOM, 5" CASING, LEVER. PT-01, CM-01 CROWN.' % F(d[1] - d[0]))
def entry_south(v):
    L = r8((FE - FW) / IN); n = FE
    jg = r8((n - JOG) / IN)
    o11 = (r8((jg - 32.0) / 2), r8((jg - 32.0) / 2) + 32.0)                          # centered on the wall, west of FOR's
    shift = (948.72 - ((FE + JOG) / 2 + 16.0 * IN)) / IN
    d01 = x_of(749.15, 833.15, True, n); d01 = (r8(d01[0]), r8(d01[0]) + 56.0)        # FOR's 4'-8" leaf centered between its jambs 746.2 / 836.2
    cs11 = CS
    shell(v, L, crown=[(0, L)], base=[(o11[1] + cs11, d01[0] - CS), (d01[1] + CS, L)])
    C.casing(v, o11[0], o11[1] - o11[0], HEAD)
    door_leaf_p(v, o11[0], o11[1] - o11[0], HEAD, panels=2, swing='R', toward=False)    # swings into the office, away
    tag(v, (o11[0] + o11[1]) / 2, HC + 5.5, 'OFFICE DOOR', 5.0, MID)
    C._line(v, (jg, 0), (jg, H - CR), C.OUTLINE)                                    # the return: the office door wall is 12" nearer
    C.casing(v, d01[0], d01[1] - d01[0], HEAD)
    door_leaf_p(v, d01[0], d01[1] - d01[0], HEAD, panels=2, swing='R', toward=False)    # swings out, away
    tag(v, (d01[0] + d01[1]) / 2, HC + 5.5, '01 FRONT DOOR', 5.0, MID)
    so = (jg + d01[0] - CS) / 2; C.outlet(v, so, OUTLET)
    C.switch(v, d01[0] - CS - 3.0, 48.0, 'S')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, o11[0], o11[1], jg, d01[0], d01[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUTLET, 48.0, HEAD, HC, H]))
    return ('FRONT DOOR 01: %s x 8\'-0", SWINGS OUT, 5" CASING. OFFICE DOOR: %s x 8\'-0" TWO-PANEL, CENTERED ON ITS WALL, SWINGS INTO THE OFFICE. '
            'SWITCH CL 4\'-0" AT THE FRONT DOOR. DUPLEX CL 1\'-6". PT-01, CM-01 CROWN.' % (F(d01[1] - d01[0]), F(o11[1] - o11[0])))
def vintage_mirror(v, x, w, y, h, fr=4.5):
    """A vintage frame seen from the front: a 4-1/2" moulded frame (outer edge, a raised bead, the cove, a sight-edge lip), carved corner blocks
    and a cartouche at the top center, the glass with a soft reflection. Drawn as an indication: the piece is sourced, sizes follow the find."""
    C._rect(v, x, y, x + w, y + h, C.OUTLINE, fill=(1, 1, 1))
    for d, wgt in ((1.0, C.MED), (2.75, C.FINE), (fr - 0.75, C.FINE), (fr, C.MED)):
        C._rect(v, x + d, y + d, x + w - d, y + h - d, wgt)
    for cx, cy in ((x, y), (x + w - fr, y), (x, y + h - fr), (x + w - fr, y + h - fr)):
        C._rect(v, cx + 0.6, cy + 0.6, cx + fr - 0.6, cy + fr - 0.6, C.FINE); C._ellipse(v, cx + fr / 2, cy + fr / 2, 1.1, 1.1, C.FINE)
    mx = x + w / 2
    C._poly(v, [(mx - 6, y + h - 0.5), (mx - 4.5, y + h + 2.5), (mx - 1.5, y + h + 4.0), (mx, y + h + 4.5), (mx + 1.5, y + h + 4.0), (mx + 4.5, y + h + 2.5), (mx + 6, y + h - 0.5)],
            C.MED, fill=(1, 1, 1))
    C._ellipse(v, mx, y + h + 1.5, 1.4, 1.4, C.FINE)
    C._line(v, (x + fr + 3, y + h - fr - 3), (x + w * 0.42, y + fr + 3), C.FINE, (0.75, 0.75, 0.75))
    C._line(v, (x + fr + 6, y + h - fr - 3), (x + w * 0.55, y + fr + 3), C.FINE, (0.75, 0.75, 0.75))
def entry_west(v):
    L = r8((FS - FN) / IN); x0 = math.floor((L - MIR_W) / 2 * 8) / 8
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    vintage_mirror(v, x0, MIR_W, MIR_B, MIR_H)
    tag(v, L / 2, MIR_B - 5.0, 'VINTAGE FRAMED MIRROR', 5.0, MID)
    C.outlet(v, L / 2, OUTLET)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, x0, x0 + MIR_W, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUTLET, MIR_B, HC, H]))
    return ('VINTAGE FRAMED MIRROR, 3\'-0" W x 5\'-0" H MAX., TOP AT 8\'-5", FRENCH CLEAT TO CMU. DUPLEX CL 1\'-6" CENTERED UNDER IT. PT-01, CM-01 CROWN.')

# ------------------------------------------------------------------ powder room
PW, PE0, PN, PS = 960.2, 1046.2, 1147.2, 1252.0
PE = 1049.2 - 4.125 * IN                         # the east wall furred out on 2x4: 3-1/2" studs and 5/8" board on FOR's CMU
T_CL = 15.0                                      # FOR's toilet CL, 15" off the north wall (14-15/16" measured)
VN = r8((PS - PN) / IN) - 39.0                   # FOR's 3'-3" vanity, tight to the south wall
V_D = 18.0; SLAB = 1.25; V_TOP = 34.0 - SLAB; V_BOX = 14.0     # V_TOP is the box top, the stone finished at 2'-10"
SPL = 41.0                                       # stone splash to 3'-5", the mirror stands on it
P_MW = 30.0; P_MB = SPL; P_MH = HC - SPL         # powder mirror 2'-6" x 5'-0", 3'-5" to 8'-5"
FAU = 38.0                                       # wall faucet CL 3'-2"
BAR = 108.0                                      # bar light CL 9'-0", its shades clear of the mirror frame

def wc_tag(v, x, y):
    tag(v, x, y, 'WC-02', 6.0, INK, box=True)

def vanity_float(v, x, w, sc):
    """Floating vanity seen from the front: stone top, a 14" two-drawer box, LED under it, the sink hidden, no deck faucet (the faucet is in the wall)."""
    C._rect(v, x, V_TOP - V_BOX, x + w, V_TOP, C.OUTLINE, fill=(1, 1, 1))
    dh = V_BOX / 2
    for i in range(2):
        y0 = V_TOP - V_BOX + i * dh; C._rect(v, x + 0.5, y0 + 0.5, x + w - 0.5, y0 + dh - 0.5, C.MED)
        C._line(v, (x + w / 2 - 4, y0 + dh - 1.2), (x + w / 2 + 4, y0 + dh - 1.2), C.OUTLINE)
    C._line(v, (x + 1, V_TOP - V_BOX - 0.6), (x + w - 1, V_TOP - V_BOX - 0.6), C.FINE, (0.6, 0.6, 0.6), '[1.5 1.5] 0')
    C._rect(v, x, V_TOP, x + w, V_TOP + SLAB, C.OUTLINE, fill=(1, 1, 1)); C.shadow(v, x, x + w, V_TOP)
    C.basin_hidden(v, sc, V_TOP, 17, 6)

def vanity_end(v, x, d, facing):
    """The floating vanity seen from its end, depth d from the wall at x (facing: the room side, 'R' or 'L'), white so it masks what is behind."""
    a, b = (x, x + d) if facing == 'R' else (x - d, x)
    C._rect(v, a, V_TOP - V_BOX, b, V_TOP, C.OUTLINE, fill=(1, 1, 1))
    nose = (b, b + 0.5) if facing == 'R' else (a - 0.5, a)
    C._rect(v, min(a, nose[0]), V_TOP, max(b, nose[1]), V_TOP + SLAB, C.OUTLINE, fill=(1, 1, 1))
    w0, w1 = (x, x + 0.75) if facing == 'R' else (x - 0.75, x)
    C._rect(v, w0, V_TOP + SLAB, w1, SPL, C.MED, fill=(1, 1, 1))                      # the splash edge
    m0, m1 = (x, x + 1.25) if facing == 'R' else (x - 1.25, x)
    C._rect(v, m0, P_MB, m1, P_MB + P_MH, C.MED, fill=(1, 1, 1))                      # the mirror edge

def powder_east(v):
    L = r8((PS - PN) / IN); vx0, vx1 = VN, L
    sc = (vx0 + vx1) / 2; mx = sc - P_MW / 2
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    C.toilet(v, T_CL - 7.5, 15)
    vanity_float(v, vx0, vx1 - vx0, sc)
    C._rect(v, vx0, V_TOP + SLAB, vx1, SPL, C.MED, fill=(1, 1, 1))                    # stone splash
    C.faucet_wall(v, sc, FAU)
    C.mirror_framed(v, mx, P_MW, P_MB, P_MH, frame=2.5)
    C.bar_light(v, sc, BAR, w=24.0)
    C.outlet(v, vx0 + 2.6, 37.75, None, horizontal=True)
    wc_tag(v, T_CL, 70.0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, T_CL, vx0, mx, mx + P_MW, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, V_TOP - V_BOX, V_TOP + SLAB, SPL, HC, BAR, H]))
    return ('FLOATING VANITY %s x %s, STONE TOP AT 2\'-10", 14" DRAWER BOX ON A STEEL BRACKET, UNDERMOUNT BOWL. WALL FAUCET CL 3\'-2", 7" STONE SPLASH. '
            'FRAMED MIRROR %s x 5\'-0" ON THE SPLASH, 24" BAR LIGHT CL 9\'-0". GFCI ON THE SPLASH. WALL FURRED ON 2x4. WC-02.' % (F(vx1 - vx0), F(V_D), F(P_MW)))
def powder_north(v):
    L = r8((PE - PW) / IN)
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    C.toilet_profile(v, L, facing='L')
    C.paper_holder(v, L - 28.7 - 8.0, 26.0)
    wc_tag(v, L / 2 - 6.0, 70.0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, L - 28.7 - 8.0, L - 28.7, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 26.0, H]))
    return ('PAPER HOLDER CL 2\'-2", 8" AHEAD OF THE BOWL. VANITY LEFT OFF THIS VIEW (ID-773 2). WC-02 BASE TO CROWN.')
def powder_south(v):
    L = r8((PE - PW) / IN)
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    vanity_end(v, 0.0, V_D, 'R')
    C.towel_ring(v, V_D / 2, 52.0)
    wc_tag(v, L / 2 + 6.0, 70.0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, V_D / 2, V_D, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, V_TOP + SLAB, SPL, 52.0, HC, H]))
    return ('HAND TOWEL RING CL 4\'-4" OVER THE VANITY END. FLOOR STOP 4" OFF THE WALL. WC-02 BASE TO CROWN.')
def powder_west(v):
    L = r8((PS - PN) / IN)
    d = x_of(1195.7, 1243.7, True, PS); d = (r8(d[0]), r8(d[0]) + 32.0)
    cs = min(CS, d[0])
    shell(v, L, crown=[(0, L)], base=[(d[1] + CS, L)])
    C.casing(v, d[0], d[1] - d[0], HEAD, cs=cs) if cs < CS else C.casing(v, d[0], d[1] - d[0], HEAD)
    door_leaf_p(v, d[0], d[1] - d[0], HEAD, panels=2, swing='L', toward=True)            # swings into the powder room, toward the viewer
    tag(v, (d[0] + d[1]) / 2, HC + 5.5, 'POWDER ROOM DOOR', 5.0, MID)
    C.switch(v, d[1] + CS + 2.5, 48.0, 'S'); C.switch(v, d[1] + CS + 6.0, 48.0, 'F')
    wc_tag(v, (d[1] + CS + L) / 2 + 3.0, 70.0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 48.0, HEAD, HC, H]))
    return ('POWDER ROOM DOOR: %s x 8\'-0" TWO-PANEL, SWINGS IN, PRIVACY LEVER, 5" CASING. DOOR, CASING, BASE AND CROWN PT-03 HIGH-GLOSS LACQUER. '
            'LIGHT AND FAN (TIMER) SWITCHES CL 4\'-0". WC-02.' % F(d[1] - d[0]))

# ------------------------------------------------------------------ enlarged powder room plan, ID-773 (owner review 11.07.26: fill the sheet)
PLAN_K = 3.0                                     # 3/4" TO 1'-0": FOR is 1.5 pt per inch, the plan 4.5 pt per inch
POWDER_LIST = ['FLOOR: ST-02 MARBLE, HONED (EMERALD GREEN OPTION), WALL TO WALL UNDER THE VANITY.',
               'WALLS: WC-02 WALLCOVERING, BASE TO CROWN, ALL FOUR WALLS. CM-01 CROWN.',
               'CEILING, CROWN, BASE, CASING AND DOOR: PT-03 HIGH-GLOSS LACQUER.',
               'VANITY: FLOATING, 3\'-3" x 1\'-6", STONE TOP AT 2\'-10", UNDERMOUNT BOWL, WALL FAUCET CL 3\'-2".',
               'MIRROR: FRAMED, 2\'-6" x 5\'-0", ON THE 7" STONE SPLASH. BAR LIGHT 24" CL 9\'-0".',
               'TOILET: CL 1\'-3" OFF THE NORTH WALL, ON THE FURRED EAST WALL. PAPER HOLDER CL 2\'-2".',
               'HAND TOWEL RING CL 4\'-4" OVER THE VANITY END. GFCI ON THE SPLASH.',
               'EAST WALL FURRED OUT ON 2x4 WITH 5/8" BOARD ON FOR\'S CMU FOR THE VALVE AND DRAIN.',
               'DOOR: 2\'-8" x 8\'-0" TWO-PANEL, SWINGS IN, PRIVACY LEVER. LIGHT AND FAN (TIMER) SWITCHES CL 4\'-0".']

def powder_plan(sh, x0, y0, x1, y1):
    """The powder room at 3/4" with its fixtures and finishes, centered in the band left of a finishes list."""
    WN, WS, WE = PN - 9.0, FS2 + 6.96, 1061.2                     # wall outer faces in FOR pt (north 6", south 4-5/8", CMU 8")
    pw, ph = (WE - FE) * PLAN_K, (WS - WN) * PLAN_K
    list_w = 560.0; gap = 90.0
    tot = pw + 70 + gap + list_w
    ox = x0 + max(0.0, (x1 - x0 - tot) / 2) + 40; oy = y0 + max(26.0, (y1 - y0 - ph - 30) / 2)
    assert oy + ph + 28 < y1 + 1, ('powder plan does not fit the band', oy + ph + 28, y1)
    def P(x, y): return (ox + (x - FE) * PLAN_K, oy + (y - WN) * PLAN_K)
    def R(a, b, c, d, **kw):
        p_, q_ = P(a, b), P(c, d); sh.rect((min(p_[0], q_[0]), min(p_[1], q_[1]), max(p_[0], q_[0]), max(p_[1], q_[1])), **kw)
    WG = (0.353, 0.353, 0.353)
    # walls
    R(FE, WN, WE, PN, width=0, color=WG, fill=WG)                                  # north
    R(FE, PS, WE, WS, width=0, color=WG, fill=WG)                                  # south
    R(FE, PN, PW, 1193.7, width=0, color=WG, fill=WG); R(FE, 1245.7, PW, PS, width=0, color=WG, fill=WG)   # west, the door opening between
    R(1049.2, PN, WE, PS, width=0, color=WG, fill=WG)                              # FOR's CMU
    R(PE, PN, 1049.2, PS, width=0.4, color=INK, fill=(0.80, 0.80, 0.80))            # the 2x4 furring
    # door 2'-8", hinged south, swings in
    h_ = P(PW, 1243.7); o_ = P(PW + 48.0, 1243.7); sh.line(h_, o_, 1.0, INK)
    pts = [fitz.Point(*P(PW + 48.0 * math.sin(math.radians(a)), 1243.7 - 48.0 * math.cos(math.radians(a)))) for a in range(0, 91, 3)]
    sh_ = sh.p.new_shape(); sh_.draw_polyline(pts); sh_.finish(color=INK, width=0.5, closePath=False); sh_.commit()
    # toilet on the furred wall, CL 15" off the north wall
    tc = PN + T_CL * IN
    R(PE - 11.25, tc - 15.0, PE, tc + 15.0, width=0.7, color=INK, fill=(1, 1, 1))
    q0, q1 = P(PE - 11.25 - 31.0, tc - 12.0), P(PE - 11.25, tc + 12.0)
    o = sh.p.new_shape(); o.draw_oval(fitz.Rect(q0, q1)); o.finish(color=INK, width=0.7, fill=(1, 1, 1)); o.commit()
    # floating vanity, 3'-3" x 1'-6", tight to the south wall, its bowl and the wall faucet
    vy0 = PN + VN * IN
    R(PE - V_D * IN, vy0, PE, PS, width=0.9, color=INK, fill=(1, 1, 1))
    bc = (vy0 + PS) / 2
    q0, q1 = P(PE - V_D * IN + 5.0, bc - 12.0), P(PE - 4.0, bc + 12.0)
    o = sh.p.new_shape(); o.draw_oval(fitz.Rect(q0, q1)); o.finish(color=INK, width=0.5); o.commit()
    m0, m1 = P(PE - 1.5, bc - P_MW / 2 * IN), P(PE - 1.5, bc + P_MW / 2 * IN); sh.line(m0, m1, 1.6, INK)       # the mirror on the wall
    # labels and tags
    c_ = P((PW + PE - V_D * IN) / 2, PN + 52.0); sh.text(c_[0], c_[1], 'POWDER ROOM', 10.0, INK, align='c', spacing=0.6, raw=True)
    c_ = P((PW + PE - V_D * IN) / 2 - 6.0, PN + 70.0); sh.tag_stack(c_[0], c_[1], ['WC-02', 'CM-01'], lead=0, sides='')
    c_ = P((PW + PE - V_D * IN) / 2 - 6.0, PS - 14.0); sh.tag(c_[0], c_[1], 'ST-02', lead=0, sides='')
    q = P(PE - V_D * IN / 2, vy0 - 6.0); sh.text(q[0], q[1], 'VANITY', 7.5, INK, align='c', raw=True)
    q = P(PE - 1.5, bc - P_MW / 2 * IN - 3.0); sh.text(q[0] - 4, q[1], 'MIRROR', 7.5, INK, align='r', raw=True)
    # dimensions: east-west across the top, north-south down the east side
    def dim(a, b, at, horiz=True, label=None):
        if horiz:
            p0, p1 = (a, at), (b, at); sh.line(p0, p1, 0.4, INK)
            for xx in (a, b): sh.line((xx - 3, at + 3), (xx + 3, at - 3), 0.6, INK)
            sh.text((a + b) / 2, at - 4, label, 8.0, INK, align='c', raw=True)
        else:
            sh.line((at, a), (at, b), 0.4, INK)
            for yy in (a, b): sh.line((at - 3, yy + 3), (at + 3, yy - 3), 0.6, INK)
            sh.text(at + 6, (a + b) / 2 + 3, label, 8.0, INK, raw=True)
    ty = P(PW, WN)[1] - 12
    dim(P(PW, 0)[0], P(PE, 0)[0], ty, True, F((PE - PW) / IN))
    rx = P(WE, 0)[0] + 16
    for a, b in ((PN, tc), (tc, vy0), (vy0, PS)): dim(P(0, a)[1], P(0, b)[1], rx, False, F((b - a) / IN))
    dim(P(0, PN)[1], P(0, PS)[1], rx + 52, False, F((PS - PN) / IN))
    cap = P(FE, WS); sh.text(cap[0], cap[1] + 22, 'POWDER ROOM PLAN, 3/4" TO 1\'-0"', 10.0, INK, bold=True, spacing=0.6, raw=True)
    # the finishes and fixtures list beside the plan
    lx = rx + 52 + 90 + gap - 40
    ly = oy + 8
    sh.text(lx, ly, 'POWDER ROOM: FINISHES AND FIXTURES', 10.0, INK, bold=True, spacing=0.6, raw=True); ly += 22
    for i, t_ in enumerate(POWDER_LIST):
        for j, ln in enumerate(wrap(t_, 9.5, min(list_w, x1 - lx - 10))):
            sh.text(lx + (0 if j == 0 else 0), ly, ln, 9.5, INK, raw=True); ly += 13.5
        ly += 4
    assert ly < y1, ('powder list runs off the sheet', ly, y1)

# ------------------------------------------------------------------ key plan, ID-771
def key_plan(sh):
    src = fitz.open('/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'); sp = src[0]
    T = BR.transform(1); a, b = T(722, 1132), T(1062, 1300)
    clip_disp = fitz.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])); k = 16.0 / 3          # 1" TO 1'-0": as large as the 11 x 17 sheet allows
    u = clip_disp * sp.derotation_matrix; u.normalize()
    ax0, ax1 = FR.x0 + 14, TB_X - 14
    tw, th = clip_disp.width * k, clip_disp.height * k
    ty = HDR_Y + 8 + max(24.0, (FR.y1 - 6 - HDR_Y - 8 - (T(749.15, 1369.0)[1] - clip_disp.y0) * k) / 2)   # plan and the front door swing centered top to bottom
    target = fitz.Rect(ax0 + (ax1 - ax0 - tw) / 2, ty, ax0 + (ax1 - ax0 - tw) / 2 + tw, ty + th)
    sh.p.show_pdf_page(target, src, 0, clip=u, rotate=90)
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(1, ['ENTRY', 'POWDER ROOM'], pad=9.0, doors=True)), 'key plan clip'
    def P(x, y): d = T(x, y); return (target.x0 + (d[0] - clip_disp.x0) * k, target.y0 + (d[1] - clip_disp.y0) * k)
    def R(x0, y0, x1, y1, **kw):
        p, q = P(x0, y0), P(x1, y1); sh.rect((min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])), **kw)
    my = (FN + FS) / 2
    R(FW, my - MIR_W / 2 * IN, FW + 3.0, my + MIR_W / 2 * IN, width=0.8, color=INK, fill=(1, 1, 1))            # the entry mirror
    WG = (0.353, 0.353, 0.353)
    R(1002.0, 1158.0, PE0, 1181.2, width=0, color=(1, 1, 1), fill=(1, 1, 1)); R(1015.8, 1193.0, PE0, PS, width=0, color=(1, 1, 1), fill=(1, 1, 1))   # FOR's toilet and vanity out
    R(PE, PN, PE0 + 0.3, PS, width=0, color=WG, fill=WG)                                                      # the 2x4 furring
    sh_ = 1046.2 - PE                                                                                         # the toilet moves with the wall
    q0, q1 = P(1002.4 - sh_, 1158.9), P(1037.6 - sh_, 1180.6); o = sh.p.new_shape(); o.draw_oval(fitz.Rect(min(q0[0], q1[0]), min(q0[1], q1[1]), max(q0[0], q1[0]), max(q0[1], q1[1]))); o.finish(color=INK, width=0.6, fill=(1, 1, 1)); o.commit()
    R(1027.0 - sh_, 1158.7, PE - 0.4, 1180.6, width=0.6, color=INK, fill=(1, 1, 1))
    R(PE - V_D * IN, 1193.4, PE, PS, width=0.8, color=INK, fill=(1, 1, 1))                                    # the floating vanity
    p, q = P(PE - V_D * IN, 1193.4), P(PE, PS); sh.line(p, q, 0.3, MID, dashes='[2 1.5] 0'); p, q = P(PE, 1193.4), P(PE - V_D * IN, PS); sh.line(p, q, 0.3, MID, dashes='[2 1.5] 0')
    def swing(hx, hy, r, a0, a1, open_at):
        pts = [P(hx + r * math.cos(math.radians(a)), hy + r * math.sin(math.radians(a))) for a in range(int(a0), int(a1) + 1, 3)]
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(*q) for q in pts]); s_.finish(color=INK, width=0.4, closePath=False); s_.commit()
        o_ = P(hx + r * math.cos(math.radians(open_at)), hy + r * math.sin(math.radians(open_at))); h_ = P(hx, hy); sh.line(h_, o_, 0.8, INK)
    swing(749.15, 1285.0, 84.0, 0, 90, 90)         # front door 01, hinged west, swings out
    R(899.0, 1259.4, 951.0, 1312.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))                 # FOR's office door leaf and arc out
    ox0 = (FE + JOG) / 2 - 24.0
    # FOR's door 11 frame replaced: the wall re-poched, the jambs redrawn at the centered position
    R(JOG + 0.6, FS2, FE - 0.3, 1258.92, width=0, color=WG, fill=WG)
    R(ox0, FS2 - 0.3, ox0 + 48.0, 1262.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))
    for jx in (ox0 - 3.0, ox0 + 48.0): R(jx, FS2, jx + 3.0, 1258.92, width=0.4, color=INK, fill=(1, 1, 1))
    swing(ox0, 1258.9, 48.0, 0, 90, 90)            # office door 11 centered on its wall, hinged west, swings into the office
    R(1046.0, 1136.0, 1052.0, 1147.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))               # FOR's ticks above the powder room wall
    R(953.5, 1126.0, 1062.0, 1140.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))               # FOR's stubs past the powder room north wall
    for txt, x, y, s in (('ENTRY', 800, 1205, 12.0), ('POWDER ROOM', 985, 1190, 9.0)):
        q = P(x, y); sh.text(q[0], q[1], txt, s, INK, align='c', spacing=0.6, raw=True)
    for txt, x, y in (('HALL', 820, 1138),):
        q = P(x, y); sh.text(q[0], q[1], txt, 7.5, MID, align='c', raw=True)
    q = P(FW + 3.0, my); sh.text(q[0] + 8, q[1] + 2.7, 'VINTAGE MIRROR', 7.5, MID, raw=True)                 # beside the mirror
    for n_, (x, y) in {'01': (800, 1300)}.items():
        q = P(x, y); s_ = sh.p.new_shape(); s_.draw_oval(fitz.Rect(q[0] - 12, q[1] - 8, q[0] + 12, q[1] + 8)); s_.finish(color=INK, width=0.5, fill=(1, 1, 1)); s_.commit()
        sh.text(q[0], q[1] + 2.9, n_.strip(), 8.0, INK, align='c', raw=True)
    for txt, x, y in (('OFFICE DOOR', 921, 1318),):
        q = P(x, y); sh.text(q[0], q[1], txt, 7.5, INK, align='c', raw=True)
    q = P(FE, 1219.7); sh.text(q[0] - 8, q[1] + 2.7, 'POWDER ROOM DOOR', 7.5, INK, align='r', raw=True)        # at the door, in the entry
    q = P(845, 1222); quad_marker(sh, q[0], q[1], 'ID-772', {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    q = P(978, 1166); quad_marker(sh, q[0], q[1], 'ID-773', {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    nx, ny = target.x0 - 40, target.y0 + 22
    ybot = max(target.y1, P(749.15, 1369.0)[1], P(833.15, 1285.0)[1])              # the front door swing hangs below the plan at the left
    cx0 = P(960.2, 1252.0)[0]                                                        # the lower right, under the powder room: scale bar, then the notes
    sb = scale_bar(sh, cx0, target.y1 + 40, 72.0, '1" TO 1\'-0"')
    sh._notes_at = (cx0, sb.y1 + 30)
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(nx, ny - 14), fitz.Point(nx + 6.5, ny + 6.5), fitz.Point(nx, ny + 1.3), fitz.Point(nx - 6.5, ny + 6.5), fitz.Point(nx, ny - 14)]); s_.finish(color=INK, fill=INK, width=0.4); s_.commit()
    sh.text(nx, ny + 19, 'N', 9.0, INK, align='c', raw=True)
    sh.text(target.x0, ybot + 26, 'FLOOR 1 KEY PLAN, 1" TO 1\'-0"', 10.0, INK, bold=True, spacing=0.6, raw=True)   # caption under the plan
    return fitz.Rect(target.x0, target.y0, target.x1, max(ybot, sb.y1))


def notes(sh, y0, x0=None):
    x0 = x0 if x0 is not None else FR.x0 + 14; x1 = TB_X - 14
    items = [(True, 'CHANGES FROM FOR\'S PLAN'),
             '1. POWDER ROOM EAST WALL FURRED OUT ON 2x4 WITH 5/8" BOARD (FACE 2-1/8" INTO THE ROOM) FOR THE WALL FAUCET AND DRAIN. THE TOILET MOVES WITH THE WALL.',
             '2. POWDER ROOM VANITY FLOATING, 3\'-3" x 1\'-6".',
             '3. OFFICE DOOR CENTERED ON ITS %s WALL, %s WEST OF FOR\'S.' % (F((FE - JOG) / IN), F((948.72 - ((FE + JOG) / 2 + 16.0 * IN)) / IN)),
             '4. ENTRY MIRROR ON A FRENCH CLEAT WITH MASONRY ANCHORS INTO THE CMU.',
             '',
             (True, 'FINISHES'),
             'ENTRY: FLOOR TL-01 CHECKERED PORCELAIN ON THE DIAGONAL. WALLS PT-01. CROWN CM-01. CEILING PT-01. DOORS AND TRIM PT-01 SATIN.',
             'POWDER ROOM: FLOOR ST-02 MARBLE. WALLS WC-02, BASE TO CROWN. CEILING, CROWN, TRIM AND DOOR PT-03 LACQUER. ENLARGED PLAN ON ID-773.',
             '',
             (True, 'VIEWS'),
             'ENTRY: FOUR WALLS ON ID-772 (MARKER IN THE ENTRY). POWDER ROOM: FOUR WALLS AND THE PLAN ON ID-773.']
    y_end = para_block(sh, x0, y0, items, x1 - x0, size=10.0)
    assert y_end < FR.y1 - 8, ('notes run off the sheet', y_end)

def build():
    import idd_sheet; idd_sheet.EXTRA_REVS[:] = []
    idd_std.PROJECT['date'] = '11.06.26'
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    doc = fitz.open()
    rev = (('0', ISSUE, 'ISSUED FOR REVIEW'), ('1', '11.06.26', 'REV 1 CHECK, FOR FACES'))
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    sh = Sheet(doc); sh.frame('ENTRY AND POWDER ROOM ELEVATIONS', 'KEY PLAN, SCALE: 1" TO 1\'-0"', ['ENTRY AND POWDER ROOM', 'ELEVATIONS KEY PLAN'], 'ID-771', revisions=rev, legend_rule=False)
    t = key_plan(sh); notes(sh, sh._notes_at[1], sh._notes_at[0])
    sheets = [('ID-772', 'ENTRY ELEVATIONS', ['INTERIOR ELEVATIONS', 'ENTRY'],
               [(1, 'NORTH ELEVATION - HALL OPENING', r8((FE - FW) / IN), entry_north, 0), (2, 'EAST ELEVATION - POWDER ROOM DOOR', r8((FS2 - FN) / IN), entry_east, 0),
                (3, 'SOUTH ELEVATION - FRONT DOOR', r8((FE - FW) / IN), entry_south, 0), (4, 'WEST ELEVATION - FRAMED MIRROR', r8((FS - FN) / IN), entry_west, 0)]),
              ('ID-773', 'POWDER ROOM ELEVATIONS', ['INTERIOR ELEVATIONS', 'POWDER ROOM'],
               [(1, 'NORTH ELEVATION', r8((PE - PW) / IN), powder_north, 0), (2, 'EAST ELEVATION - VANITY AND TOILET', r8((PS - PN) / IN), powder_east, 0),
                (3, 'SOUTH ELEVATION', r8((PE - PW) / IN), powder_south, 0), (4, 'WEST ELEVATION - DOOR', r8((PS - PN) / IN), powder_west, 0)])]
    for sid, title, tl, views in sheets:
        if sid == 'ID-772':                     # entry: 12'-0" walls, two rows at 1/2" (3/4" is 9" too tall for two rows)
            sc = '1/2'; cells = E.layout_cells(frame, 2, 2)   # frame top is 24 pt under the border (HDR_Y + 8)
        else:                                   # powder room: four short walls in one row at 3/4" (1" needs 1924 pt across, the sheet has 1586)
            sc = '3/4'; k_ = E.SCALES[sc]
            cells = cells_row(frame, [L * k_ + 106 for _, _, L, _, _ in views])
            need = 0.0
            for c_, (n_, t_, L_, fn_, ex_) in zip(cells, views):              # the tallest view with its notes sets the row height
                pr = E.ElevationView(Sheet(fitz.open()).p, FREG, 'cg', (0, 0), k_, {'room': 'ENTRY', 'view': t_, 'length': L_, 'ceiling': H})
                ln_ = wrap(fn_(pr), NOTE, min(c_[2] - c_[0] - 16, 660))
                need = max(need, 30 + len(ln_) * NLH + 8 + H * k_ + 44)
            h_ = need + 24                                                     # the row is only as tall as the views, at the top of the sheet
            cells = [(c_[0], frame[1], c_[2], frame[1] + h_) for c_ in cells]
        s = Sheet(doc); s.frame(title, 'SCALE: %s" TO 1\'-0"' % sc, tl, sid, revisions=rev, legend_rule=False)
        draw_views(s, cells, views, scale=sc)
        if sid == 'ID-773': powder_plan(s, frame[0], cells[0][3] + 4, frame[2], frame[3] - 4)
    fix_soft_hyphen(doc); doc.set_metadata({'title': 'Casa Grove entry and powder room ID-771 to ID-773', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
