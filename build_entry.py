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
Heights per FOR Rev 1 (coordination 11.09.26, coord/heights.json): entry ceiling 10'-8" center with a 10'-4" soffit band at the walls (A-205,
A-401), so the walls read 10'-4" with the crown held 4" down and an LED cove over it; powder room 10'-8" (A-205), crown to the ceiling.
Front door 01 head 9'-0" (A-600 D01); interior heads 8'-0" (A-600)."""
import sys, math
sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std

from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG
from idd_std import INK, MID, TRIM
from build_kitchen import H, CR, TOP, tag
from build_mud import IN, r8, F, x_of, para_block, door_leaf, NLH
from build_kitchen import NOTE, wrap
import base_rev1 as BR, keyclip as KC
# review 11.09.26: every elevation carries an overall floor-to-ceiling dimension outside its chain
_E_dim_v = E.ElevationView.dim_v
def _dim_v_overall(self, y0i, y1i, x_pt, pts_i, side='r'):
    _E_dim_v(self, y0i, y1i, x_pt, pts_i, side)
    if len(pts_i) > 2 and pts_i[-1] - pts_i[0] >= 90:
        _E_dim_v(self, pts_i[0], pts_i[-1], x_pt + (18 if side == 'r' else -18), [pts_i[0], pts_i[-1]], side)
if not getattr(E.ElevationView, '_overall_patched', False):
    E.ElevationView.dim_v = _dim_v_overall; E.ElevationView._overall_patched = True


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

def arched_cased(v, x, w, spring, cs=None):
    """Cased opening with a semicircular head (owner 11.09.26: the hall doorway arched): opening line, casing following the arch with its
    backband, jambs to the floor. The head springs at `spring`; the casing stays under the crown."""
    cs = CS if cs is None else cs
    r = w / 2; cx = x + w / 2
    def arc(rr, lw, c=None):
        pts = [(cx - rr * math.cos(math.radians(a)), spring + rr * math.sin(math.radians(a))) for a in range(0, 181, 6)]
        C._poly(v, pts, lw, c, close=False)
    for xx in (x, x + w): C._line(v, (xx, 0), (xx, spring), C.OUTLINE)
    arc(r, C.OUTLINE)
    for xx in (x - cs, x + w + cs): C._line(v, (xx, 0), (xx, spring), C.OUTLINE)
    arc(r + cs, C.OUTLINE)
    for xx in (x - cs + 1.0, x + w + cs - 1.0): C._line(v, (xx, 0), (xx, spring), C.FINE, MID)        # backband
    arc(r + cs - 1.0, C.FINE, MID)
    C._line(v, (x - cs, spring), (x, spring), C.FINE, MID); C._line(v, (x + w, spring), (x + w + cs, spring), C.FINE, MID)   # springer joint
    return spring + r + cs

def jib_door_p(v, x, w, head, hinge='R'):
    """Hidden jib door seen from the wall it hides in (owner 11.09.26: recessed hidden door): the leaf flush with the wall, its joint drawn as
    a fine line, swing marks dashed (it swings away), touch latch, no casing; base and crown run across it."""
    C._rect(v, x, 0, x + w, head, C.FINE, INK)
    h_, f_ = (x + w, x) if hinge == 'R' else (x, x + w)
    C._line(v, (f_, 0), (h_, head / 2), C.FINE, INK, '[6 4] 0'); C._line(v, (f_, head), (h_, head / 2), C.FINE, INK, '[6 4] 0')
    # touch latch: nothing shows on the face

def glass_leaf_p(v, x, w, head, swing='L', toward=False, glass='hammered', rows=2):
    """Wood door leaf, 2 x 2 lites over one raised panel (owner 11.09.26: the front door like his photo, hammered glass), with the set's
    swing-mark rule (solid toward the viewer, dashed away) and the lever on the lock rail."""
    st, rail_b, rail_t, lock, mid = 4.5, 9.0, 4.5, 36.0, 5.0
    C._rect(v, x, 0, x + w, head, C.OUTLINE)
    C._rect(v, x + st, rail_b, x + w - st, lock - mid, C.MED); C._rect(v, x + st + 1.5, rail_b + 1.5, x + w - st - 1.5, lock - mid - 1.5, C.FINE, MID)
    C._rect(v, x + st, lock, x + w - st, head - rail_t, C.MED)
    C.glazing(v, x + st + 0.75, lock + 0.75, x + w - st - 0.75, head - rail_t - 0.75, glass=glass, divided=(rows > 1), cols=1 if rows <= 1 else 2, rows=max(1, rows))
    hinge, far = (x, x + w) if swing == 'L' else (x + w, x)
    d = None if toward else '[6 4] 0'
    C._line(v, (far, 0), (hinge, head / 2), C.FINE, INK, d); C._line(v, (far, head), (hinge, head / 2), C.FINE, INK, d)
    lever = far - 3 if far > hinge else far + 3; ly = lock - mid / 2
    C._ellipse(v, lever, ly, 0.9, 0.9, C.FINE); C._line(v, (lever, ly), (lever + (-3.5 if far > hinge else 3.5), ly), C.MED)

def gilt_mirror(v, x, w, y, h, fr=4.0, crest=10.0):
    """Ornate gilt mirror (owner 11.09.26 photo): an arched-top frame with a beaded sight edge, shoulder scrolls at the spring line, a carved
    crest of C-scrolls and a fan of leaves over the apex, scroll feet at the bottom corners, the glass with a soft reflection. h is overall,
    crest included. Drawn as an indication: the piece is sourced, sizes follow the find."""
    hb = h - crest                                   # frame body height, the crest sits on top
    r = w / 2; spring = y + hb - r; cx = x + w / 2
    def arch_path(inset):
        rr = r - inset
        pts = [(x + inset, y + inset), (x + inset, spring)]
        pts += [(cx - rr * math.cos(math.radians(a)), spring + rr * math.sin(math.radians(a))) for a in range(0, 181, 5)]
        pts += [(x + w - inset, spring), (x + w - inset, y + inset)]
        return pts
    C._poly(v, arch_path(0.0), C.OUTLINE, fill=(1, 1, 1))
    for inset, lw, c in ((1.0, C.MED, None), (2.0, C.FINE, MID), (fr - 0.8, C.FINE, MID), (fr, C.MED, None)):
        C._poly(v, arch_path(inset), lw, c)
    # beads along the sight edge
    rr = r - fr + 0.45
    for a in range(4, 177, 8):
        C._ellipse(v, cx - rr * math.cos(math.radians(a)), spring + rr * math.sin(math.radians(a)), 0.32, 0.32, C.FINE)
    yy = y + fr + 1.5
    while yy < spring:
        for xx in (x + fr - 0.45, x + w - fr + 0.45): C._ellipse(v, xx, yy, 0.32, 0.32, C.FINE)
        yy += 2.6
    # shoulder scrolls at the spring line, both sides
    for sgn, ex in ((-1, x), (1, x + w)):
        pts = [(ex, spring + 3.0), (ex + sgn * 1.6, spring + 2.2), (ex + sgn * 2.2, spring + 0.6), (ex + sgn * 1.6, spring - 0.9),
               (ex + sgn * 0.4, spring - 1.0), (ex + sgn * 0.3, spring + 0.2), (ex + sgn * 1.0, spring + 0.6)]
        C._poly(v, pts, C.MED, close=False)
        pts = [(ex, spring - 3.0), (ex + sgn * 1.4, spring - 4.5), (ex + sgn * 1.0, spring - 6.0), (ex, spring - 6.5)]
        C._poly(v, pts, C.FINE, close=False)
    # carved scallops along the upper arch (rococo edge), then the crest: a cartouche on the apex, C-scrolls either side, a fan of leaves
    for a_ in list(range(28, 76, 8)) + list(range(108, 156, 8)):
        ex_, ey_ = cx - r * math.cos(math.radians(a_)), spring + r * math.sin(math.radians(a_))
        C._arc(v, ex_, ey_, 1.1, a_ - 80, a_ + 80, C.FINE)
    ay = y + hb; k = 1.2                              # apex of the frame; crest scale (fan top 9.7" over the apex)
    C._poly(v, [(cx - 3.2 * k, ay - 1.0), (cx - 3.6 * k, ay + 2.2 * k), (cx - 2.2 * k, ay + 4.4 * k), (cx, ay + 5.2 * k), (cx + 2.2 * k, ay + 4.4 * k),
                (cx + 3.6 * k, ay + 2.2 * k), (cx + 3.2 * k, ay - 1.0)], C.OUTLINE, fill=(1, 1, 1))
    C._ellipse(v, cx, ay + 2.2 * k, 1.5 * k, 1.8 * k, C.FINE)
    for sgn in (-1, 1):
        pts = [(cx + sgn * 3.4 * k, ay + 0.4), (cx + sgn * 6.0 * k, ay + 0.6), (cx + sgn * 8.2 * k, ay + 2.0 * k), (cx + sgn * 8.6 * k, ay + 3.8 * k),
               (cx + sgn * 7.4 * k, ay + 4.6 * k), (cx + sgn * 6.3 * k, ay + 3.9 * k), (cx + sgn * 6.7 * k, ay + 3.0 * k), (cx + sgn * 7.5 * k, ay + 3.3 * k)]
        C._poly(v, pts, C.MED, close=False)
        pts = [(cx + sgn * 3.0 * k, ay + 4.0 * k), (cx + sgn * 4.6 * k, ay + 5.4 * k), (cx + sgn * 4.4 * k, ay + 6.8 * k), (cx + sgn * 3.3 * k, ay + 7.0 * k)]
        C._poly(v, pts, C.FINE, close=False)
    fy = ay + 5.2 * k
    for k_ in range(-3, 4):                          # the fan of leaves
        a = math.radians(90 + k_ * 17); C._line(v, (cx, fy), (cx + 2.6 * k * math.cos(a), fy + 2.6 * k * math.sin(a)), C.FINE)
    C._arc(v, cx, fy, 2.9 * k, 30, 150, C.MED)
    # scroll feet at the bottom corners and a pendant at the bottom center
    for sgn, ex in ((1, x), (-1, x + w)):
        C._poly(v, [(ex + sgn * 0.5, y + 0.2), (ex + sgn * 2.6, y - 1.2), (ex + sgn * 4.6, y - 0.6), (ex + sgn * 4.2, y + 0.4)], C.MED, close=False)
    # reflection on the glass
    C._line(v, (x + fr + 4, spring + r * 0.5), (x + w * 0.40, y + fr + 6), C.FINE, (0.75, 0.75, 0.75))
    C._line(v, (x + fr + 8, spring + r * 0.5), (x + w * 0.52, y + fr + 6), C.FINE, (0.75, 0.75, 0.75))

def linear_sconce(v, cx, cy, w=24.0):
    """Modern linear LED sconce (owner 11.09.26: 'more modern light'): a slim 1-1/4" bar on two short stems, CL at cy."""
    C._rect(v, cx - w / 2, cy - 0.625, cx + w / 2, cy + 0.625, C.OUTLINE, fill=(1, 1, 1))
    C._line(v, (cx - w / 2 + 0.5, cy - 0.3), (cx + w / 2 - 0.5, cy - 0.3), C.FINE, MID)
    for sx in (cx - w / 2 + 3.0, cx + w / 2 - 3.0):
        C._rect(v, sx - 0.35, cy + 0.625, sx + 0.35, cy + 2.0, C.FINE); C._rect(v, sx - 1.0, cy + 2.0, sx + 1.0, cy + 2.6, C.FINE)

def cloud(v, x0, y0, x1, y1, pad=2.0, at='tr', L=None):
    """Revision cloud; with L given it stays inside the wall (0..L) so it never crosses the cut walls or the dimension strings."""
    if L is not None: x0, x1 = max(x0 - pad, 1.5), min(x1 + pad, L - 1.5); pad = 0.0
    C.rev_cloud(v, x0, y0, x1, y1, pad=pad, tag_at=at)

# ------------------------------------------------------------------ FOR coordination 11.09.26: real heights, crown with LED cove, wall-hung smart toilets
H_ENTRY = 124.0                                  # FOR A-205 / A-401: 10'-8" center, 10'-4" soffit band at the walls (the wall height seen in elevation)
H_POWDER = 128.0                                 # FOR A-205: 10'-8"
COVE_GAP = 4.0                                   # owner 11.09.26: crown held 4" down, concealed LED strip on its top washing the ceiling
COVE = False                                     # set per sheet in build()
HEAD01 = 108.0                                   # FOR A-600 D01: 9'-0" head
def shell(v, L, crown=(), base=(), cut_left=True, cut_right=True):
    """Wall shell at the module height H; with COVE the crown sits COVE_GAP under the ceiling with the LED strip drawn on its top."""
    top = H - (COVE_GAP if COVE else 0.0)
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    for a, b in base: C.base(v, a, b)
    for a, b in crown:
        C.crown(v, a, b, top)
        if COVE:
            C._rect(v, a, top, b, top + 0.75, C.FINE, MID)                                   # LED channel on the crown top
            C._line(v, (a, top + 1.4), (b, top + 1.4), C.FINE, MID, '[2 1.5] 0')              # light wash, dashed
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    if cut_left: v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    if cut_right: v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=(0.3, 0.3, 0.3))
def crown_bottom(): return H - (COVE_GAP if COVE else 0.0) - CR
def casing_capped(v, x, w, head, top, cs=None):
    """Door casing whose head band stops at `top` (the crown's underside): the 9'-0" front door in the 10'-4" entry."""
    cs = CS if cs is None else cs; hb = max(0.5, min(cs, top - head))
    C._rect(v, x - cs, 0, x, head + hb, C.OUTLINE); C._rect(v, x + w, 0, x + w + cs, head + hb, C.OUTLINE); C._rect(v, x - cs, head, x + w + cs, head + hb, C.OUTLINE)
    C._rect(v, x - 0.25, 0, x + w + 0.25, head + 0.25, C.FINE, MID)
    for xx in (x - cs + 1.0, x + w + cs - 1.0): C._line(v, (xx, 0), (xx, head + hb - 0.5), C.FINE, (0.68, 0.68, 0.68))
    return head + hb
WH_RIM = 16.0                                    # wall-hung bowl: seat 16" AFF (set on the carrier; 15" to 19" adjustable)
def wallhung_front(v, cx, w=15.0):
    """Wall-hung smart toilet seen from the front: the floating bowl and seat, no tank, the flush plate on the wall above (owner 11.09.26)."""
    C._poly(v, [(cx - w / 2, WH_RIM), (cx - w / 2 + 1.5, 8.0), (cx - 3.0, 6.0), (cx + 3.0, 6.0), (cx + w / 2 - 1.5, 8.0), (cx + w / 2, WH_RIM)], C.OUTLINE, fill=(1, 1, 1))
    C._ellipse(v, cx, WH_RIM, w / 2, 1.0, C.OUTLINE, fill=(1, 1, 1))
    C._rect(v, cx - w / 2 + 1.0, WH_RIM + 1.0, cx + w / 2 - 1.0, WH_RIM + 3.0, C.OUTLINE, fill=(1, 1, 1))        # the smart seat housing
    flush_plate(v, cx, 44.0)
def wallhung_profile(v, x, facing='L', length=22.0):
    """Wall-hung smart toilet from the side: bowl cantilevered off the wall at x, seat housing at the back, floor clear under it."""
    d = -1 if facing == 'L' else 1; fx = x + d * length
    C._poly(v, [(x, WH_RIM + 1.0), (fx, WH_RIM + 1.0), (fx, WH_RIM), (fx - d * 1.5, WH_RIM - 5.0), (fx - d * 6.0, WH_RIM - 9.0), (x + d * 6.0, 7.0), (x, 7.0)],
            C.OUTLINE, fill=(1, 1, 1))
    C._rect(v, x, WH_RIM + 1.0, x + d * 7.0, WH_RIM + 4.0, C.OUTLINE, fill=(1, 1, 1))
    C._line(v, (x + d * 7.0, WH_RIM - 0.5), (fx - d * 2.0, WH_RIM - 0.5), C.FINE, MID)
    C._rect(v, x, 44.0 - 4.5, x + d * 0.6, 44.0 + 4.5, C.MED, fill=(1, 1, 1))                                      # flush plate edge
def flush_plate(v, cx, cy, w=9.75, h=6.5):
    C._rect(v, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, C.MED, fill=(1, 1, 1))
    C._rect(v, cx - w / 2 + 0.6, cy - h / 2 + 0.6, cx - 0.3, cy + h / 2 - 0.6, C.FINE, MID); C._rect(v, cx + 0.3, cy - h / 2 + 0.6, cx + w / 2 - 0.6, cy + h / 2 - 0.6, C.FINE, MID)
T_GFCI = (-8.0, 14.0)                            # smart-seat GFCI: 8" north of the toilet CL (5/ID-502), CL 1'-2", beside the carrier (clear of the vanity GFCI)

OUT = '/home/claude/flrwork/261105.HD102.EntryPowderPilot.pdf'
ISSUE = '11.05.26'
HEAD = 96.0; CS = TRIM['casing']
HC = HEAD + CS                                   # top of the head casing, 8'-5": the mirror tops line up with it

# ------------------------------------------------------------------ entry
FW, FE, FN, FS, FS2, JOG = 736.50, 953.28, 1152.54, 1269.96, 1251.96, 889.32   # FOR's drywall faces (11.06.26 recheck); JOG: the return's face
MIR_W, MIR_H = 52.0, 86.0                        # entry mirror (owner 11.09.26: large hung gilt mirror, his red box): 4'-4" x 7'-2" overall, crest included
MIR_T = 104.0                                    # top of the crest 8'-8", 8" under the crown
MIR_B = MIR_T - MIR_H                            # bottom 1'-6": the duplex moves beside the mirror
ARCH_SPRING = 78.0                               # hall opening arched (owner 11.09.26): semicircular head springing at 6'-6", the casing 3" under the crown
OUTLET = 18.0

def entry_north(v):
    L = r8((FE - FW) / IN)
    op = x_of(780.7, 859.1, n=FW); op = (r8(op[0]), r8(op[1]))
    shell(v, L, crown=[(0, L)], base=[(0, op[0] - CS), (op[1] + CS, L)])
    top = arched_cased(v, op[0], op[1] - op[0], ARCH_SPRING)
    apex = ARCH_SPRING + (op[1] - op[0]) / 2
    assert top < crown_bottom() - 1.0, ('arch casing hits the crown', top)
    tag(v, (op[0] + op[1]) / 2, 50.0, 'HALL BEYOND', 5.0, MID)
    ox = (op[1] + L) / 2; C.outlet(v, ox, OUTLET)
    cloud(v, op[0] - CS, 3.0, op[1] + CS, top)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, op[0], op[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUTLET, ARCH_SPRING, apex, H]))
    return ('%s ARCHED CASED OPENING TO THE HALL, SEMICIRCULAR HEAD SPRINGING AT %s, TOP OF THE OPENING %s, 5" CASING FOLLOWS THE ARCH. '
            'DUPLEX CL 1\'-6" CENTERED ON THE SOLID WALL. PT-01. CEILING 10\'-4" AT THE WALLS, 10\'-8" CENTER (FOR A-205). CM-01 CROWN WITH LED COVE ABOVE, SEE 4/ID-502.' % (F(op[1] - op[0]), F(ARCH_SPRING), F(apex)))
def entry_east(v):
    L = r8((FS2 - FN) / IN)
    d = x_of(1195.7, 1243.7, n=FN); d = (r8(d[0]), r8(d[0]) + 32.0)
    shell(v, L, crown=[(0, L)], base=[(0, d[0] - CS)])
    C.casing(v, d[0], d[1] - d[0], HEAD)
    door_leaf_p(v, d[0], d[1] - d[0], HEAD, panels=2, swing='R', toward=False)          # swings into the powder room, away
    tag(v, (d[0] + d[1]) / 2, HC + 5.5, 'POWDER ROOM DOOR', 5.0, MID)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, HEAD, HC, H]))
    return ('POWDER ROOM DOOR: %s x 8\'-0" TWO-PANEL, SWINGS INTO THE POWDER ROOM, 5" CASING, LEVER. PT-01. CEILING 10\'-4" AT THE WALLS, 10\'-8" CENTER (FOR A-205). CM-01 CROWN WITH LED COVE ABOVE, SEE 4/ID-502.' % F(d[1] - d[0]))
def entry_south(v):
    L = r8((FE - FW) / IN); n = FE
    jg = r8((n - JOG) / IN)
    o11 = (r8((jg - 32.0) / 2), r8((jg - 32.0) / 2) + 32.0)                          # centered on the wall, west of FOR's
    shift = (948.72 - ((FE + JOG) / 2 + 16.0 * IN)) / IN
    d01 = x_of(749.15, 833.15, True, n); d01 = (r8(d01[0]), r8(d01[0]) + 56.0)        # FOR's 4'-8" leaf centered between its jambs 746.2 / 836.2
    cs11 = CS
    shell(v, L, crown=[(0, L)], base=[(0, d01[0] - CS), (d01[1] + CS, L)])            # the base runs across the hidden office door
    jib_door_p(v, o11[0], o11[1] - o11[0], HEAD, hinge='R')                             # hidden jib door, swings into the office, away
    tag(v, (o11[0] + o11[1]) / 2, HEAD + 5.5, 'OFFICE DOOR, HIDDEN', 5.0, MID)
    C._line(v, (jg, 0), (jg, H - CR), C.OUTLINE)                                    # the return: the office door wall is 12" nearer
    ctop = casing_capped(v, d01[0], d01[1] - d01[0], HEAD01, crown_bottom())       # FOR A-600: 9'-0" head; the head casing dies into the crown
    hw = (d01[1] - d01[0]) / 2                                                       # a pair (owner 11.09.26), both leaves swing out, away
    glass_leaf_p(v, d01[0], hw, HEAD01, swing='L', rows=1); glass_leaf_p(v, d01[0] + hw, hw, HEAD01, swing='R', rows=1)   # owner 11.09.26: one pane per leaf, no muntins
    tag(v, (d01[0] + d01[1]) / 2, HEAD01 + 1.2, '01 FRONT DOOR', 5.0, MID, box=True)   # over the head casing, clear of the frame (review 3)
    cloud(v, o11[0], 3.0, o11[1], HEAD + 8.0, at='tl'); cloud(v, d01[0] - CS - 6.0, 3.0, d01[1] + CS, ctop)   # encloses the switch beside the casing (review 2)
    so = (jg + d01[0] - CS) / 2; C.outlet(v, so, OUTLET)
    C.switch(v, d01[0] - CS - 3.0, 48.0, 'S')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, o11[0], o11[1], jg, d01[0], d01[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUTLET, 48.0, HEAD, HEAD01, H]))
    return ('FRONT DOOR 01: PAIR OF %s x 9\'-0" WOOD LEAVES (FOR A-600 HEAD), ONE HAMMERED-GLASS LITE PER LEAF (NO MUNTINS) OVER ONE RAISED PANEL, TEMPERED, SWING OUT, 5" CASING, THE HEAD CASING DIES INTO THE CROWN. '
            'OFFICE DOOR: %s x 8\'-0" HIDDEN JIB DOOR, FLUSH IN THE WALL, CONCEALED HINGES, TOUCH LATCH, NO CASING, BASE AND CROWN RUN ACROSS, '
            'PAINTED PT-01 WITH THE WALL, CENTERED ON ITS WALL, SWINGS INTO THE OFFICE. SWITCH CL 4\'-0" AT THE FRONT DOOR. DUPLEX CL 1\'-6". PT-01. CEILING 10\'-4" AT THE WALLS, 10\'-8" CENTER (FOR A-205). CM-01 CROWN WITH LED COVE ABOVE, SEE 4/ID-502.'
            % (F(hw), F(o11[1] - o11[0])))
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
    gilt_mirror(v, x0, MIR_W, MIR_B, MIR_H)
    import idd_sheet as _IS; _lw = _IS.ps(5.0); _tw = FREG.text_length('ORNATE GILT MIRROR', fontsize=5.0) * 1.1   # mask the reflection lines behind the label (review 2)
    v.rect(v.X(L / 2) - _tw / 2 - 3, v.Y(MIR_B + 12.0) - _lw * 1.1, v.X(L / 2) + _tw / 2 + 3, v.Y(MIR_B + 12.0) + 3, 0, fill=(1, 1, 1))
    tag(v, L / 2, MIR_B + 12.0, 'ORNATE GILT MIRROR', 5.0, MID)
    ox_ = x0 / 2; C.outlet(v, ox_, OUTLET)                                           # duplex centered in the wall beside the mirror
    cloud(v, ox_ - 3.5, OUTLET - 4.0, x0 + MIR_W + 1.0, MIR_T)                    # one cloud: the larger mirror and the moved duplex (review 2)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, ox_, x0, x0 + MIR_W, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, OUTLET, MIR_B, MIR_T, H]))
    return ('LARGE HUNG MIRROR, ORNATE GILT FRAME, ARCHED TOP WITH A CARVED CREST, ABOUT 4\'-4" W x 7\'-2" H OVERALL, TOP AT 8\'-8", '
            'ON A FRENCH CLEAT WITH MASONRY ANCHORS INTO THE CMU. SOURCED: THE SIZE FOLLOWS THE FIND. DUPLEX CL 1\'-6" CENTERED IN THE WALL BESIDE IT. PT-01. CEILING 10\'-4" AT THE WALLS, 10\'-8" CENTER (FOR A-205). CM-01 CROWN WITH LED COVE ABOVE, SEE 4/ID-502.')

# ------------------------------------------------------------------ powder room
PW, PE0, PN, PS = 960.2, 1046.2, 1147.2, 1252.0
PE = 1049.2 - 4.125 * IN                         # the east wall furred out on 2x4: 3-1/2" studs and 5/8" board on FOR's CMU
T_CL = 15.0                                      # FOR's toilet CL, 15" off the north wall (14-15/16" measured)
VN = r8((PS - PN) / IN) - 39.0                   # FOR's 3'-3" vanity, tight to the south wall
V_D = 18.0; SLAB = 1.25; V_TOP = 34.0 - SLAB; V_BOX = 14.0     # V_TOP is the box top, the stone finished at 2'-10"
SPL = 41.0                                       # stone splash to 3'-5", the mirror stands on it
P_MW = 30.0; P_MB = SPL; P_MH = HC - SPL         # powder mirror 2'-6" x 5'-0", 3'-5" to 8'-5"
FAU = 38.0                                       # wall faucet CL 3'-2"
BAR = 105.0                                      # linear sconce CL 8'-9", 4" over the mirror (owner 11.09.26: more modern light)
CHAIR = 38.0                                     # chair rail top 3'-2", all four walls (owner 11.09.26: about 3'-0"); the wall-hung toilet's flush plate sits above it
P_GFCI = 26.0                                    # GFCI CL 2'-2" on the wall at the left end of the vanity (owner 11.09.26: off the splash)

def rail(v, a, b):
    """Powder room chair rail between a and b, top at CHAIR."""
    if b - a > 0.5: C.chair_rail(v, a, b, CHAIR - TRIM['cap'])
def pt4_tag(v, x, y):
    tag(v, x, y, 'PT-04', 6.0, INK, box=True)

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
    wallhung_front(v, T_CL)                                                          # owner 11.09.26: wall-hung smart toilet on an in-wall carrier
    C.outlet(v, T_CL + T_GFCI[0], T_GFCI[1], 'GFCI')
    vanity_float(v, vx0, vx1 - vx0, sc)
    C._rect(v, vx0, V_TOP + SLAB, vx1, SPL, C.MED, fill=(1, 1, 1))                    # stone splash
    C.faucet_wall(v, sc, FAU)
    C.mirror_framed(v, mx, P_MW, P_MB, P_MH, frame=2.5)
    linear_sconce(v, sc, BAR, w=24.0)
    rail(v, 0, vx0)
    gx = vx0 - 3.0; C.outlet(v, gx, P_GFCI, 'GFCI')
    wc_tag(v, T_CL, 70.0); pt4_tag(v, sc, 12.5)                     # under the floating vanity
    cloud(v, 0, CHAIR - TRIM['cap'] - 1.0, vx0, CHAIR + 1.0, pad=1.5, at='tl', L=L)
    cloud(v, gx - 2.5, P_GFCI - 6.0, gx + 2.5, P_GFCI + 4.0, pad=0.5, at='tl')
    cloud(v, sc - 13.0, BAR - 2.0, sc + 13.0, BAR + 3.0, pad=1.5, L=L)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, T_CL, vx0, mx, mx + P_MW, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, V_TOP - V_BOX, P_GFCI, V_TOP + SLAB, SPL, HC, BAR, H]))
    return ('FLOATING VANITY %s x %s, STONE TOP AT 2\'-10", 14" DRAWER BOX ON A STEEL BRACKET, UNDERMOUNT BOWL. WALL FAUCET CL 3\'-2", 7" STONE SPLASH. '
            'FRAMED MIRROR %s x 5\'-0" ON THE SPLASH, 24" MODERN LINEAR LED SCONCE CL 8\'-9". GFCI CL 2\'-2" ON THE WALL AT THE LEFT END OF THE VANITY. '
            'CHAIR RAIL AT 3\'-2" TO THE VANITY. PT-04 BELOW, WC-02 ABOVE. WALL-HUNG SMART TOILET ON AN IN-WALL CARRIER, SEAT 1\'-4", FLUSH PLATE CL 3\'-8", GFCI FOR THE SEAT CL 1\'-2", 8" OFF THE BOWL CL. '
            'WALL FURRED DEEP ENOUGH FOR THE CARRIER, VERIFY. CEILING 10\'-8" (FOR A-205), CM-01 CROWN TO THE CEILING.' % (F(vx1 - vx0), F(V_D), F(P_MW)))
def powder_north(v):
    L = r8((PE - PW) / IN)
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    rail(v, 0, L)
    wallhung_profile(v, L, facing='L')
    C.paper_holder(v, L - 22.0 - 8.0, 26.0)
    wc_tag(v, L / 2 - 6.0, 70.0); pt4_tag(v, 9.0, 18.0)
    cloud(v, 0, CHAIR - TRIM['cap'] - 1.0, L, CHAIR + 1.0, pad=1.5, at='tl', L=L)      # the rail only, clear of the toilet
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, L - 22.0 - 8.0, L - 22.0, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 26.0, WH_RIM, CHAIR, 44.0, H]))
    return ('WALL-HUNG SMART TOILET, SEAT 1\'-4", FLUSH PLATE CL 3\'-8". PAPER HOLDER CL 2\'-2", 8" AHEAD OF THE BOWL. VANITY LEFT OFF THIS VIEW (ID-773 2). CHAIR RAIL AT 3\'-2", PT-04 BELOW, WC-02 ABOVE.')
def powder_south(v):
    L = r8((PE - PW) / IN)
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    rail(v, V_D + 0.5, L)                                           # dies into the vanity end
    vanity_end(v, 0.0, V_D, 'R')
    C.towel_ring(v, V_D / 2, 52.0)
    wc_tag(v, L / 2 + 6.0, 70.0); pt4_tag(v, L / 2 + 6.0, 18.0)
    cloud(v, V_D + 1.0, 12.0, L, CHAIR + 1.0, pad=1.5, L=L)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, V_D / 2, V_D, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, V_TOP + SLAB, SPL, 52.0, HC, H]))
    return ('HAND TOWEL RING CL 4\'-4" OVER THE VANITY END. FLOOR STOP 4" OFF THE WALL. CHAIR RAIL AT 3\'-2", PT-04 BELOW, WC-02 ABOVE.')
def powder_west(v):
    L = r8((PS - PN) / IN)
    d = x_of(1195.7, 1243.7, True, PS); d = (r8(d[0]), r8(d[0]) + 32.0)
    cs = min(CS, d[0])
    shell(v, L, crown=[(0, L)], base=[(d[1] + CS, L)])
    C.casing(v, d[0], d[1] - d[0], HEAD, cs=cs) if cs < CS else C.casing(v, d[0], d[1] - d[0], HEAD)
    door_leaf_p(v, d[0], d[1] - d[0], HEAD, panels=2, swing='L', toward=True)            # swings into the powder room, toward the viewer
    tag(v, (d[0] + d[1]) / 2, HC + 5.5, 'POWDER ROOM DOOR', 5.0, MID)
    rail(v, 0, d[0] - cs); rail(v, d[1] + CS, L)
    C.switch(v, d[1] + CS + 2.5, 48.0, 'S'); C.switch(v, d[1] + CS + 6.0, 48.0, 'F')
    wc_tag(v, (d[1] + CS + L) / 2 + 3.0, 70.0); pt4_tag(v, (d[1] + CS + L) / 2 + 3.0, 18.0)
    cloud(v, d[1] + CS, 12.0, L, CHAIR + 1.0, pad=1.5, L=L)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d[0], d[1], L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, CHAIR, 48.0, HEAD, HC, H]))
    return ('POWDER ROOM DOOR: %s x 8\'-0" TWO-PANEL, SWINGS IN, PRIVACY LEVER, 5" CASING. DOOR, CASING, BASE AND CROWN PT-03 HIGH-GLOSS LACQUER. '
            'LIGHT AND FAN (TIMER) SWITCHES CL 4\'-0". CHAIR RAIL AT 3\'-2" PT-03, PT-04 BELOW, WC-02 ABOVE.' % F(d[1] - d[0]))

# ------------------------------------------------------------------ enlarged powder room plan, ID-773 (owner review 11.07.26: fill the sheet)
PLAN_K = 2.0                                     # 1/2" TO 1'-0" (FOR heights 11.09.26: the 10'-8" elevations take the band): FOR is 1.5 pt per inch, the plan 3 pt per inch
POWDER_LIST = ['FLOOR: ST-02 MARBLE, HONED (EMERALD GREEN OPTION), WALL TO WALL UNDER THE VANITY.',
               'WALLS: CHAIR RAIL AT 3\'-2" ON ALL FOUR WALLS. BELOW: PT-04 DEEP PAINT COLOR, TO SELECT. ABOVE: WC-02 DECORATIVE WALLCOVERING TO THE CROWN.',
               'CEILING 10\'-8" (FOR A-205). CEILING, CROWN, CHAIR RAIL, BASE, CASING AND DOOR: PT-03 HIGH-GLOSS LACQUER. CM-01 CROWN TO THE CEILING.',
               'VANITY: FLOATING, 3\'-3" x 1\'-6", STONE TOP AT 2\'-10", UNDERMOUNT BOWL, WALL FAUCET CL 3\'-2".',
               'MIRROR: FRAMED, 2\'-6" x 5\'-0", ON THE 7" STONE SPLASH. MODERN LINEAR LED SCONCE 24" CL 8\'-9".',
               'TOILET: WALL-HUNG SMART TOILET ON AN IN-WALL CARRIER, CL 1\'-3" OFF THE NORTH WALL, FLUSH PLATE CL 3\'-8", SEAT GFCI CL 1\'-2" 8" OFF THE BOWL CL. PAPER HOLDER CL 2\'-2".',
               'HAND TOWEL RING CL 4\'-4" OVER THE VANITY END. GFCI CL 2\'-2" ON THE WALL AT THE LEFT END OF THE VANITY.',
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
    q0, q1 = P(PE - 22.0 * IN, tc - 11.0), P(PE - 0.5, tc + 11.0)                    # wall-hung bowl, 22" off the wall, no tank (carrier in the wall)
    o = sh.p.new_shape(); o.draw_oval(fitz.Rect(q0, q1)); o.finish(color=INK, width=0.7, fill=(1, 1, 1)); o.commit()
    # floating vanity, 3'-3" x 1'-6", tight to the south wall, its bowl and the wall faucet
    vy0 = PN + VN * IN
    R(PE - V_D * IN, vy0, PE, PS, width=0.9, color=INK, fill=(1, 1, 1))
    bc = (vy0 + PS) / 2
    q0, q1 = P(PE - V_D * IN + 5.0, bc - 12.0), P(PE - 4.0, bc + 12.0)
    o = sh.p.new_shape(); o.draw_oval(fitz.Rect(q0, q1)); o.finish(color=INK, width=0.5); o.commit()
    m0, m1 = P(PE - 1.5, bc - P_MW / 2 * IN), P(PE - 1.5, bc + P_MW / 2 * IN); sh.line(m0, m1, 1.6, INK)       # the mirror on the wall
    # labels and tags
    c_ = P((PW + PE - V_D * IN) / 2, PN + 52.0)
    sh.rect((c_[0] - 40.0, c_[1] - 9.5, c_[0] + 40.0, c_[1] + 3.0), width=0, color=None, fill=(1, 1, 1))      # mask: the door arc runs behind the label (review 11.09.26)
    sh.text(c_[0], c_[1], 'POWDER ROOM', 10.0, INK, align='c', spacing=0.6, raw=True)
    c_ = P((PW + PE - V_D * IN) / 2 - 6.0, PN + 70.0); sh.tag_stack(c_[0], c_[1], ['WC-02', 'PT-04', 'CM-01'], lead=0, sides='')
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
    cap = P(FE, WS); sh.text(cap[0], cap[1] + 22, 'POWDER ROOM PLAN, 1/2" TO 1\'-0"', 10.0, INK, bold=True, spacing=0.6, raw=True)
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
    ty = HDR_Y + 8 + max(24.0, (FR.y1 - 6 - HDR_Y - 8 - (T(749.15, 1327.0)[1] - clip_disp.y0) * k) / 2)   # plan and the front door swing centered top to bottom
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
    q0, q1 = P(PE - 22.0 * IN, 1158.9), P(PE - 0.5, 1180.6); o = sh.p.new_shape(); o.draw_oval(fitz.Rect(min(q0[0], q1[0]), min(q0[1], q1[1]), max(q0[0], q1[0]), max(q0[1], q1[1]))); o.finish(color=INK, width=0.6, fill=(1, 1, 1)); o.commit()
    R(PE - V_D * IN, 1193.4, PE, PS, width=0.8, color=INK, fill=(1, 1, 1))                                    # the floating vanity
    p, q = P(PE - V_D * IN, 1193.4), P(PE, PS); sh.line(p, q, 0.3, MID, dashes='[2 1.5] 0'); p, q = P(PE, 1193.4), P(PE - V_D * IN, PS); sh.line(p, q, 0.3, MID, dashes='[2 1.5] 0')
    def swing(hx, hy, r, a0, a1, open_at):
        pts = [P(hx + r * math.cos(math.radians(a)), hy + r * math.sin(math.radians(a))) for a in range(int(a0), int(a1) + 1, 3)]
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(*q) for q in pts]); s_.finish(color=INK, width=0.4, closePath=False); s_.commit()
        o_ = P(hx + r * math.cos(math.radians(open_at)), hy + r * math.sin(math.radians(open_at))); h_ = P(hx, hy); sh.line(h_, o_, 0.8, INK)
    p_, q_ = P(746.6, 1285.6), P(835.8, 1372.0)                                              # FOR's single leaf and arc out, kept inside the frame
    wr = fitz.Rect(min(p_[0], q_[0]), min(p_[1], q_[1]), max(p_[0], q_[0]), max(p_[1], q_[1])) & fitz.Rect(FR.x0 + 2, FR.y0 + 2, FR.x1 - 2, FR.y1 - 2)
    sh.rect(wr, width=0, color=(1, 1, 1), fill=(1, 1, 1))
    swing(749.15, 1285.0, 42.0, 0, 90, 90); swing(833.15, 1285.0, 42.0, 90, 180, 90)            # front door 01: a pair (owner 11.09.26), both swing out
    import idd_sheet as IS
    def kcloud(x0, y0, x1, y1, at='tr'):
        a_, b_ = P(x0, y0), P(x1, y1); IS.rev_cloud_pt(sh.p, fitz.Rect(min(a_[0], b_[0]) - 6, min(a_[1], b_[1]) - 6, max(a_[0], b_[0]) + 6, max(a_[1], b_[1]) + 6), '1', tag_at=at)
    kcloud(746.0, 1272.0, 836.5, 1328.0)                                                     # front door pair
    kcloud(FW, my - MIR_W / 2 * IN - 3, FW + 20.0, my + MIR_W / 2 * IN + 3, at='tl')         # larger mirror
    R(899.0, 1259.4, 951.0, 1312.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))                 # FOR's office door leaf and arc out
    ox0 = (FE + JOG) / 2 - 24.0
    # FOR's door 11 frame replaced: the wall re-poched, the jambs redrawn at the centered position
    R(JOG + 0.6, FS2, FE - 0.3, 1258.92, width=0, color=WG, fill=WG)
    R(ox0, FS2 - 0.3, ox0 + 48.0, 1262.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))
    # hidden jib door (owner 11.09.26): no casing, the leaf flush in the wall, so no jamb blocks drawn
    swing(ox0, 1258.9, 48.0, 0, 90, 90)            # office door 11 centered on its wall, hinged west, swings into the office
    kcloud(ox0 - 4.0, 1253.0, ox0 + 50.0, 1308.0)                                            # hidden office door
    R(1046.0, 1136.0, 1052.0, 1147.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))               # FOR's ticks above the powder room wall
    R(953.5, 1126.0, 1062.0, 1140.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))               # FOR's stubs past the powder room north wall
    for txt, x, y, s in (('ENTRY', 800, 1205, 12.0), ('POWDER ROOM', 985, 1190, 9.0)):
        q = P(x, y); sh.text(q[0], q[1], txt, s, INK, align='c', spacing=0.6, raw=True)
    for txt, x, y in (('HALL', 820, 1138),):
        q = P(x, y); sh.text(q[0], q[1], txt, 7.5, MID, align='c', raw=True)
    q = P(FW + 3.0, my); sh.text(q[0] + 8, q[1] + 2.7, 'GILT MIRROR', 7.5, MID, raw=True)                    # beside the mirror
    for n_, (x, y) in {'01': (800, 1300)}.items():
        q = P(x, y); s_ = sh.p.new_shape(); s_.draw_oval(fitz.Rect(q[0] - 12, q[1] - 8, q[0] + 12, q[1] + 8)); s_.finish(color=INK, width=0.5, fill=(1, 1, 1)); s_.commit()
        sh.text(q[0], q[1] + 2.9, n_.strip(), 8.0, INK, align='c', raw=True)
    for txt, x, y in (('HIDDEN OFFICE DOOR', 921, 1318),):
        q = P(x, y); sh.text(q[0], q[1], txt, 7.5, INK, align='c', raw=True)
    q = P(FE, 1219.7); sh.text(q[0] - 8, q[1] + 2.7, 'POWDER ROOM DOOR', 7.5, INK, align='r', raw=True)        # at the door, in the entry
    q = P(845, 1222); quad_marker(sh, q[0], q[1], 'ID-772', {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    q = P(978, 1166); quad_marker(sh, q[0], q[1], 'ID-773', {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    nx, ny = target.x0 - 40, target.y0 + 22
    ybot = max(target.y1, P(749.15, 1327.0)[1], P(833.15, 1285.0)[1])              # the front door swing hangs below the plan at the left
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
             '1. POWDER ROOM EAST WALL FURRED ON 2x4 WITH 5/8" BOARD FOR THE WALL FAUCET AND DRAIN. THE TOILET MOVES WITH IT.',
             '2. POWDER ROOM VANITY FLOATING, 3\'-3" x 1\'-6".',
             '3. OFFICE DOOR A HIDDEN JIB, NO CASING, CENTERED ON ITS %s WALL, %s WEST OF FOR\'S.' % (F((FE - JOG) / IN), F((948.72 - ((FE + JOG) / 2 + 16.0 * IN)) / IN)),
             '4. ENTRY MIRROR ON A FRENCH CLEAT WITH MASONRY ANCHORS INTO THE CMU.',
             '5. FRONT DOOR 01: WOOD PAIR, ONE HAMMERED LITE A LEAF, 9\'-0" (FOR: METAL PIVOT).',
             '6. HALL OPENING ARCHED, SPRING LINE 6\'-6". VERIFY THE HEADER WITH FOR.',
             '7. POWDER ROOM TOILET WALL-HUNG, SMART SEAT (FOR HAS FLOOR-MOUNTED).',
             (True, 'FINISHES'),
             'ENTRY: FLOOR TL-01 CHECKERED PORCELAIN ON THE DIAGONAL. WALLS PT-01. CEILING 10\'-8", 10\'-4" BAND. CM-01 WITH LED COVE (4/ID-502). TRIM PT-01.',
             'POWDER ROOM: FLOOR ST-02 MARBLE. CHAIR RAIL AT 3\'-2": PT-04 BELOW, WC-02 ABOVE. CEILING 10\'-8". TRIM AND DOOR PT-03. PLAN ON ID-773.',
]
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
    global H, COVE
    for sid, title, tl, views in sheets:
        H, COVE = (H_ENTRY, True) if sid == 'ID-772' else (H_POWDER, False)
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
