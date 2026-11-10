"""REV 1 redraw (11.05.26) of the secondary baths, from build_baths.py. Designed elevations in the master bath language (ID-739 baths 2 and 3, ID-740 guest bath): furniture vanity with a
wall faucet, framed mirror with a bar light, WT-01 tile floor to ceiling in the wet alcove with no crown inside, doors and glass fronts
drawn one way, trim from the TRIM block, outlets and switches in the margins. Geometry from the room model off FOR's plan (the model
is good to the inch on these plain rectangular rooms; VERIFY on the sheets). Output: 261105.HD102.SecondaryBaths.pdf"""
import json, pymupdf as fitz
import idd_elevations as E, idd_components as C
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT, TRIM
import sys as _sys; _sys.path.insert(0, '/home/claude/flrwork/rev1')
import base_rev1 as BR, keyclip as KC
import idd_std, idd_sheet
idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
REVS = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', '11.05.26', 'REDRAWN ON FOR REV 1')]   # set only while build() runs

def quad_marker(sh, cx, cy, sheet, views, r=13.0):
    """One marker for a small room: the sheet number in the center, a view number toward each wall it looks at, an arrow outside."""
    s = sh.p.new_shape(); s.draw_circle(fitz.Point(cx, cy), r); s.finish(color=INK, width=0.6, fill=(1, 1, 1)); s.commit()
    sh.text(cx, cy + 1.8, sheet.replace('ID-', ''), 5.2, INK, align='c')
    for d, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d]
        tip = (cx + dx * (r + 6), cy + dy * (r + 6))
        b1 = (cx + dx * r - dy * 3.5, cy + dy * r + dx * 3.5); b2 = (cx + dx * r + dy * 3.5, cy + dy * r - dx * 3.5)
        s = sh.p.new_shape(); s.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s.finish(color=INK, width=0.4, fill=INK); s.commit()
        tx, ty = cx + dx * r * 0.66, cy + dy * r * 0.66 + 1.8
        sh.text(tx, ty, str(n), 5.2, INK, align='c')

OUT = '/home/claude/flrwork/261105.HD102.SecondaryBaths.pdf'
H = 120.0; HEAD = 96.0                  # H set per bath in _build(): FOR A-206 baths 2 and 3 9'-10", A-205 guest bath 10'-8" (coordination 11.09.26)
H_B23, H_G = 118.0, 128.0
CS = TRIM['casing']; BASE = TRIM['base']; CR = TRIM['crown']; M = TRIM['margin']
TILE = (24, 12)                        # WT-01 12 x 24 porcelain, set horizontal, joints centered
WHITE = (1, 1, 1); BEYOND = (0.55, 0.55, 0.55)
K = E.SCALES['1/2']                    # 11.07.26 wide sheet: 1/2" (3/4" needs 650 pt of height a view, two rows give 552)
K_LABEL = 'SCALE: 1/2" TO 1\'-0"'
VAN_H = 34.0; MIR = (32.0, 48.0); MIR_B = 48.0; OUT_CL = 42.0; SW = 48.0   # LED mirror 4'-0" to 8'-0", the bath window's sill and head
WIN_SILL = 59.0                        # FOR A-600 window I: 2'-2" x 3'-1", sill 4'-11", head 8'-0"; obscure tempered, drywall return, no casing

REV1 = json.load(open('/home/claude/flrwork/rev1/rooms_display.json'))   # FOR REV 1 room bounds, display space (key plans follow the new base)

def _wrap(text, size, width):
    from idd_sheet import FREG
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if FREG.text_length(t, fontsize=size) > width and cur: out.append(cur); cur = w
        else: cur = t
    return out + ([cur] if cur else [])

def model(floor, name):
    m = json.load(open(f'/home/claude/flrwork/model_f{floor}.json'))
    return next(r for r in m['rooms'] if r['name'] == name)

def tag(v, x, y, s, size=5.0, c=MID): v.text(v.X(x), v.Y(y), s, size, c, align='c')

def shell(v, L, crown=(), base=(), cut_left=True, cut_right=True):
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    for a, b in base: C.base(v, a, b)
    for a, b in crown: C.crown(v, a, b, H)
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    if cut_left: v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    if cut_right: v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=(0.3, 0.3, 0.3))

def beyond(fn):
    keep = (C.INK, C.MID); C.INK = BEYOND; C.MID = BEYOND
    try: fn()
    finally: C.INK, C.MID = keep

def tile(v, x0, x1, y0=0, y1=None):
    y1 = H if y1 is None else y1
    C.tile_grid(v, x0, x1, y0, y1, TILE, show=[(x0, x1, y0, y1)])

FLUSH_CL = 44.0; SEAT_GFCI = 14.0; SEAT_OFF = 8.0     # flush plate CL 3'-8" and the seat GFCI 8" off the bowl CL, per ID-502 detail 5 (review 11.09.26)
def wall_toilet(v, cx, w=14.5):
    """Wall-hung smart toilet on an in-wall carrier, seen from the front (owner 11.09.26): bowl off the floor, no tank, flush plate on the
    wall CL 3'-8", a GFCI for the seat 8" off the bowl CL at CL 1'-2", dashed behind the bowl."""
    C._poly(v, [(cx - w / 2, 15.5), (cx - w / 2 + 2.2, 7.0), (cx + w / 2 - 2.2, 7.0), (cx + w / 2, 15.5)], C.OUTLINE, fill=(1, 1, 1))
    C._ellipse(v, cx, 15.5, w / 2, 1.2, C.OUTLINE, fill=(1, 1, 1))
    C._line(v, (cx - w / 2, 17.0), (cx + w / 2, 17.0), C.OUTLINE); C._line(v, (cx - w / 2 + 1, 18.3), (cx + w / 2 - 1, 18.3), C.MED)
    C._rect(v, cx - 4.5, FLUSH_CL - 3.0, cx + 4.5, FLUSH_CL + 3.0, C.OUTLINE, fill=(1, 1, 1)); C._rect(v, cx - 1.6, FLUSH_CL - 1.6, cx + 1.6, FLUSH_CL + 1.6, C.FINE)
    gx = cx + SEAT_OFF                                                        # behind the bowl's edge: drawn dashed
    C._rect(v, gx - 1.4, SEAT_GFCI - 2.25, gx + 1.4, SEAT_GFCI + 2.25, C.FINE, MID, dashes='[1.5 1.0] 0')
    return gx

def vanity_wall(v, x, w, mirror_w=MIR[0]):
    """Furniture vanity with a deck faucet and a frameless LED mirror set to the window's height, centered on the vanity."""
    cx = x + w / 2
    C.vanity_furniture(v, x, w, VAN_H, legs=True, drawers=3, faucet_style='deck')
    C.mirror_led(v, cx - mirror_w / 2, mirror_w, MIR_B, MIR[1])
    return cx


def r8(x): return round(x * 8) / 8
def ft(x): return E.ftin(r8(x))
ACC = idd_std.ACCENT

def quad_marker(sh, cx, cy, sheet, views, r=24.0):
    """One marker for a small room: the sheet number in the center, a view number toward each wall it looks at, an arrow outside the circle.
    11.07.26: r 24 (owner: plan tags twice as big), text and arrows scale with r."""
    f = r / 16.0
    s = sh.p.new_shape(); s.draw_circle(fitz.Point(cx, cy), r); s.finish(color=INK, width=0.8, fill=(1, 1, 1)); s.commit()
    sh.text(cx, cy + 2.4 * f, sheet.replace('ID-', ''), 7.0 * f, INK, align='c', raw=True)
    for d, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d]
        a = 3.5 * f; tip = (cx + dx * (r + 6 * f), cy + dy * (r + 6 * f))
        b1 = (cx + dx * r - dy * a, cy + dy * r + dx * a); b2 = (cx + dx * r + dy * a, cy + dy * r - dx * a)
        s = sh.p.new_shape(); s.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s.finish(color=INK, width=0.4, fill=INK); s.commit()
        off = 0.74 * r if dx else 0.62 * r
        sh.text(cx + dx * off, cy + dy * off + 2.4 * f, str(n), 7.0 * f, INK, align='c', raw=True)

class View(E.ElevationView):
    """The house elevation view, with short vertical labels kept inside the string down to 12 pt (5" at 3/8")."""
    def dim_v(self, y0i, y1i, x_pt, pts_i, side='r'):
        ys = [self.Y(q) for q in pts_i]
        E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
        self.line((x_pt, ys[0]), (x_pt, ys[-1]), 0.4)
        for y in ys:
            self.line((x_pt - 3, y), (x_pt + 3, y), 0.4); self.line((x_pt - 1.8, y + 1.8), (x_pt + 1.8, y - 1.8), 0.6)
        out = 0
        for a, b in zip(pts_i, pts_i[1:]):
            if b - a < 0.5: continue
            cy = (self.Y(a) + self.Y(b)) / 2; s_ = E.ftin(b - a); seg = (b - a) * self.k
            if self.F.text_length(s_, fontsize=5.0) + 4 > seg:            # wider than its ticks: outside the string, staggered
                xo = (x_pt + 9 + 8 * out) if side == 'r' else (x_pt - 9 - 8 * out)
                self.text(xo, cy, s_, 5.0, align='c', rotate=90); out = 1 - out; continue
            out = 0
            x_text = x_pt - 2.5 if side == 'r' else x_pt + 7.5
            self.text(x_text, cy, s_, 5.0, align='c', rotate=90)

    def dim_h(self, x0i, x1i, y_pt, pts_i, offset_lines=True):
        y_pt += 4.0                                                     # strings 4 pt lower: room for labels stacked above, clear of the floor
        xs = [self.X(q) for q in pts_i]
        E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
        self.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
        for x in xs:
            self.line((x, y_pt - 3), (x, y_pt + 3), 0.4); self.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)
        last = -1e9
        for a, b in zip(pts_i, pts_i[1:]):
            if b - a < 0.5: continue
            s_ = E.ftin(b - a); seg = (b - a) * self.k; mid = (self.X(a) + self.X(b)) / 2
            w = self.F.text_length(s_, fontsize=5.0)
            if w + 3 > seg:                                             # wider than its ticks: above the string with a leader down to its segment
                cx = max(mid, last + 5 + w / 2)
                self.text(cx, y_pt - 10.5, s_, 5.0, align='c'); last = cx + w / 2
                self.line((cx, y_pt - 9.0), (mid, y_pt - 1.2), 0.3, MID); continue
            self.text(mid, y_pt - 2.5, s_, 5.0, align='c')

def window_return(v, x, w, sill, head):
    """Bath window on a drywall return: the opening and the sash, no casing and no outer line."""
    C._rect(v, x, sill, x + w, head, C.OUTLINE); C._rect(v, x + 1.25, sill + 1.25, x + w - 1.25, head - 1.25, C.MED)
    C.glazing(v, x + 1.25, sill + 1.25, x + w - 1.25, head - 1.25)         # divided lites (owner 11.09.26: all windows and glass doors match)
    C.rev_cloud(v, x, sill, x + w, head, pad=2.0)

def niche(v, x, w, y, h):
    """Tiled niche, no shelf."""
    C._rect(v, x, y, x + w, y + h, C.OUTLINE); C._rect(v, x + 0.75, y + 0.75, x + w - 0.75, y + h - 0.75, C.FINE, C.MID)

def mtag(v, x, y, s, size=5.0, c=MID):
    """A label on tile or glass: a white box behind it so no joint runs through the letters."""
    w = v.F.text_length(s, fontsize=size); X, Y = v.X(x), v.Y(y)
    v.rect(X - w / 2 - 1.5, Y - size * 0.9, X + w / 2 + 1.5, Y + size * 0.4, 0, color=WHITE, fill=WHITE)
    v.text(X, Y, s, size, c, align='c')

def ghost(v, x0, x1, y1, label=None):
    """An open door leaf standing in front of the wall: dashed outline."""
    v.rect(v.X(x0), v.Y(0), v.X(x1), v.Y(y1), 0.4, color=MID, dashes='[3 2] 0')
    if label: v.text(v.X((x0 + x1) / 2), v.Y(y1 / 2), label, 5.0, MID, align='c')

# ================================================================== baths 2 and 3 (floor 2), FOR REV 1, measured from A-202 REV 1 (FOR pt, 1.5 pt per inch)
# PLAN (re-measured 11.05.26): both rooms 5'-0" x 8'-6", tubs back to back on the shared wall (FOR 290.1 to 297.1).
#   bath 3  x 446.2 (west face, drywall on the block) to 536.2 (east face), y 137.0 (north face) to 290.1 (shared wall): 60" x 102"
#   bath 2  x 446.2 to 536.2, y 297.1 to 450.1 (south face). The east face is straight at 536.2 the full length (A-WALL-DRYWALL 536.22, 297.1 to
#           450.2): the 542 / 543 lines at y 413 to 457 are the far face, where the built-in partition meets the wall. No jog in the room.
#   tubs    60" x 30": bath 3 y 245.1 to 290.1, bath 2 y 297.1 to 342.1; valve at the west end (FOR 446.2, y 261 to 274 and 313 to 326)
#   toilets on the west wall: bath 3 CL y 218.1, bath 2 CL y 369.0
#   windows west wall: bath 3 y 198.5 to 237.5, bath 2 y 349.7 to 388.7: 26" wide, centered on the toilets
#   vanities FOR 36" x 20" tight to the end wall (bath 3 y 137 to 191, bath 2 y 396.2 to 450.2): drawn 36" x 18", 2" off the end wall
#   doors   bath 3: east wall, 2'-8" leaf y 144.5 to 192.5 (5" from the north corner), hinged north, swings in, rests 5" off the north wall
#           from x 488.2 (2'-4" from the west wall) to the east wall
#           bath 2: south wall, 2'-8" leaf x 480.7 to 528.7 (5" from the east corner), hinged east, swings in, rests 5" off the east wall
#           from y 402.1 (5'-10" from the shared wall) to the south wall
BW = 60.0; BD = 102.0
TUB_D = 30.0
ALC = BD - TUB_D                       # 72, the alcove line, from the vanity end wall
VAN = (2.0, 38.0)                      # vanity along the west wall, from the vanity end wall: 36", 2" off the wall
VAN_D = 18.0                           # vanity depth, so bath 2's latch casing and the leaf clear its end panel
MIRW = 30.0
TOI_C = 54.0                           # toilet CL from the vanity end wall: 16" to the vanity (15" min)
WIN = (41.0, 67.0)
GFCI = VAN[1] + 4.5                    # 42-1/2
VALVE = ALC + TUB_D / 2                # 87
SCREEN = 30.0
D2 = (5.0, 37.0)                       # bath 2 leaf on the south wall, from the east corner (FOR)
OPEN2 = (70.0, 102.0)                  # bath 2's open leaf along the east wall, from the shared wall
D3 = (5.0, 37.0)                       # bath 3 leaf on the east wall, from the north corner (FOR)
OPEN3 = (28.0, 60.0)                   # bath 3's open leaf along the north wall, from the west wall
PH_B = VAN_D / 2                       # paper holder, centered on the vanity end panel, 9" off the wall
TB_W = 24.0

def alcove_back(v, screen_at):
    L = BW
    shell(v, L)
    tile(v, 0, L, 20, H)
    niche(v, L / 2 - 12, 24, 56, 12)
    C.alcove_tub_front(v, 0, L, rim=20)
    sx = 0.0 if screen_at == 'L' else L - SCREEN
    C.glass_screen_face(v, sx, SCREEN, 20, 60)
    mtag(v, 18.0, 98, 'WT-01')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points(sorted({0, sx, sx + SCREEN, L / 2 - 12, L / 2 + 12, L})))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 20, 56, 68, 80, H]))
    side = 'LEFT' if screen_at == 'L' else 'RIGHT'
    return ['60" x 30" TUB, TILE APRON. WT-01 TO CEILING. NICHE 24" x 12", SILL 4\'-8".',
            '1/2" TEMPERED GLASS SCREEN 30" x 60". GRAB BAR BLOCKING 33" TO 36".']

def fixture_wall(v, flip):
    """The west wall (exterior, furred 2" at the tub). flip False: vanity at the viewer's left (bath 2); flip True: tub alcove at the left (bath 3)."""
    L = BD
    X = (lambda d: L - d) if flip else (lambda d: d)
    span = lambda a, b: (min(X(a), X(b)), max(X(a), X(b)))
    alc = span(ALC, BD); paint = span(0, ALC)
    shell(v, L, crown=[paint], base=[paint])
    tile(v, alc[0], alc[1], 20, H); C.schluter(v, X(ALC), 0, H)
    C.alcove_tub_end(v, L if not flip else 0, TUB_D, rim=20, open_to='L' if not flip else 'R')
    C.valve(v, X(VALVE), 48); C.tub_spout(v, X(VALVE), 26); C.shower_head(v, X(VALVE), 80)
    C.glass_edge(v, X(ALC), 80)
    w0, w1 = span(*WIN)
    window_return(v, w0, w1 - w0, WIN_SILL, HEAD)
    wall_toilet(v, X(TOI_C))
    v0, v1 = span(*VAN)
    cx = vanity_wall(v, v0, v1 - v0, mirror_w=MIRW)
    C.outlet(v, X(GFCI), OUT_CL)
    mtag(v, alc[0] + 7.5, 98, 'WT-01'); tag(v, (w0 + w1) / 2, 101, 'OBSCURE GLASS')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points(sorted({0, X(VAN[0]), cx, X(VAN[1]), X(TOI_C), X(ALC), X(VALVE), L})))
    v.dim_h(0, L, v.Y(0) + 31, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 20, 26, VAN_H, OUT_CL, MIR_B, WIN_SILL, 80, HEAD, H - CR, H]))
    a = 'SOUTH' if not flip else 'NORTH'
    return ['36" x 18" VANITY. LED MIRROR 30" x 48". GFCI 4-1/2" PAST VANITY, CL 3\'-6".',
            'WINDOW I PER FOR A-600, 2\'-2" x 3\'-1", SILL 4\'-11", OBSCURE TEMPERED. VALVE 4\'-0", SPOUT 2\'-2", HEAD 6\'-8".',
            'WALL-HUNG SMART TOILET ON A CARRIER, FLUSH PLATE CL 3\'-8", SEAT GFCI 8" OFF THE BOWL CL, CL 1\'-2" (DASHED, BEHIND THE BOWL), SEE 5/ID-502.']

# ---- bath 2 (south)
def b2_north(v): return alcove_back(v, 'L')
def b2_east(v):
    """Looking east, north at the left: the alcove side wall, the flat painted wall, the open door resting along the south end."""
    L = BD
    shell(v, L, crown=[(TUB_D, L)], base=[(TUB_D, L)])
    tile(v, 0, TUB_D, 20, H); C.schluter(v, TUB_D, 0, H)
    C.alcove_tub_end(v, 0, TUB_D, rim=20, open_to='R')
    tb = (TUB_D + OPEN2[0]) / 2
    C.towel_bar(v, tb, 48, TB_W)
    ghost(v, OPEN2[0], OPEN2[1], HEAD, 'DOOR, OPEN')
    mtag(v, 7.5, 98, 'WT-01')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, TUB_D, tb - TB_W / 2, tb + TB_W / 2, OPEN2[0], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 20, 48, HEAD, H - CR, H]))
    return ['WT-01 TO CEILING AT THE TUB. 24" TOWEL BAR CL 4\'-0".',
            'DOOR OPENS HERE (DASHED): FLOOR STOP, NOTHING ON THE WALL.']
def b2_south(v):
    """Looking south, east at the left: the door hinged east, the vanity end at the west corner."""
    L = BW
    dl = D2
    shell(v, L, crown=[(0, L)], base=[(dl[1] + CS, L)])
    C.casing(v, dl[0], dl[1] - dl[0], HEAD); leaf_in(v, dl[0], dl[1] - dl[0], 'L')
    C.robe_hook(v, (dl[0] + dl[1]) / 2, 66)
    sw = dl[1] + CS + M / 2
    C.switch(v, sw, SW, 'S')
    C.vanity_end(v, L, VAN_D, VAN_H, open_to='L')
    C.paper_holder(v, L - PH_B, 26)
    C.towel_ring(v, L - 6, 52)
    tag(v, (dl[0] + dl[1]) / 2, 105.5, 'DOOR TO BEDROOM 2')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, dl[0], dl[1], dl[1] + CS, L - 6, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 26, VAN_H, SW, 52, 66, HEAD, HEAD + CS, H - CR, H]))
    return ['2\'-8" x 8\'-0" DOOR. SWITCH CL 4\'-0". ROBE HOOK ON DOOR CL 5\'-6".',
            'PAPER HOLDER ON VANITY END CL 2\'-2". TOWEL RING CL 4\'-4".']
def b2_west(v): return fixture_wall(v, flip=False)

# ---- bath 3 (north)
def b3_north(v):
    L = BW
    shell(v, L, crown=[(0, L)], base=[(VAN_D, L)])
    C.vanity_end(v, 0, VAN_D, VAN_H, open_to='R')
    C.paper_holder(v, PH_B, 26)
    C.towel_ring(v, PH_B, 52)
    ghost(v, OPEN3[0], OPEN3[1], HEAD, 'DOOR, OPEN')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, PH_B, VAN_D, OPEN3[0], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 26, VAN_H, 52, HEAD, H - CR, H]))
    return ['PAPER HOLDER ON VANITY END CL 2\'-2". TOWEL RING CL 4\'-4".',
            'DOOR OPENS HERE (DASHED): FLOOR STOP, NOTHING ON THE WALL.']
def b3_east(v):
    L = BD
    shell(v, L, crown=[(0, ALC)], base=[(D3[1] + CS, ALC)])
    tile(v, ALC, L, 20, H); C.schluter(v, ALC, 0, H)
    C.alcove_tub_end(v, L, TUB_D, rim=20, open_to='L')
    C.casing(v, D3[0], D3[1] - D3[0], HEAD); leaf_in(v, D3[0], D3[1] - D3[0], 'L')
    C.robe_hook(v, (D3[0] + D3[1]) / 2, 66)
    sw = D3[1] + CS + M / 2
    C.switch(v, sw, SW, 'S')
    tb = (sw + 2 + ALC) / 2
    C.towel_bar(v, tb, 48, 18)
    tag(v, (D3[0] + D3[1]) / 2, 105.5, 'DOOR TO BEDROOM 3'); mtag(v, ALC + 7.5, 98, 'WT-01')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, D3[0], D3[1], D3[1] + CS, tb - 9, tb + 9, ALC, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 20, SW, 66, HEAD, HEAD + CS, H - CR, H]))
    return ['2\'-8" x 8\'-0" DOOR. SWITCH CL 4\'-0". ROBE HOOK ON DOOR CL 5\'-6".',
            '18" TOWEL BAR CL 4\'-0". WT-01 TO CEILING AT THE TUB.']
def b3_south(v): return alcove_back(v, 'R')
def b3_west(v): return fixture_wall(v, flip=True)

# ================================================================== guest bath (floor 1), FOR REV 1, measured from A-201 REV 1
# PLAN: x 356.2 (west face) to 511.2 (east face), y 815.2 (north face) to 905.2 (south face): 8'-7-1/4" x 5'-0" (FOR dims 8'-7" x 5'-0")
#   shower 457.2 to 511.2 (36") the full 5'-0", FOR's valve under the head on the south wall at x 484, center drain at 484, 864.6
#   toilet on the south wall, CL x 431.85 (4'-2-3/8" from the west corner); vanity 356.2 to 406.2 x 875.2 to 905.2 (33-3/8" x 20") at the west corner
#   door north wall, 2'-8" leaf hinged west at 364.4 (5-1/2" from the west corner), latch 412.4 (casing to 3'-6-1/2"), swings in along the west wall
GL = 103.25; GW = 60.0
MK_G = (387.0, 855.1); NM_G = (387.0, 872.5)   # 11.07.26: marker clear of the entry leaf and the glass swing, name in the room
_MK_OLD = (421.0, 847.0)                  # guest key plan marker, FOR pt: clear of the door swing, the glass swing, the toilet and the vanity
SHW = 36.0
GLASS = GL - SHW                       # 67-1/4, the glass line from the west corner
GDOOR = (5.5, 37.5)
GTOI_C = 50.375
GVAN = (2.0, 35.0); GVAN_D = 18.0           # FOR: 20", 18" like baths 2 and 3
GMIR = 24.0
GD_W = 24.0                            # shower door, 22" clear: its swing along the north wall starts 3/4" past the room door casing
OFFV = 12.0                            # offset valve on the east (back) wall, from the north wall
HDR = 4.0                              # the header wall over the glass front

def leaf_in(v, x, w, hinge):
    """Room door seen from inside the bath: it swings toward the viewer, so the swing marks are solid (set rule)."""
    C.door_leaf(v, x, w, HEAD, panels=1, swing=hinge)
    h_, far = (x, x + w) if hinge == 'L' else (x + w, x)
    C._line(v, (far, 0), (h_, HEAD / 2), C.FINE, MID); C._line(v, (far, HEAD), (h_, HEAD / 2), C.FINE, MID)

def header_cut(v, x):
    v.rect(v.X(x - HDR / 2), v.Y(HEAD), v.X(x + HDR / 2), v.Y(H), 0.6, fill=(0.3, 0.3, 0.3))

def glass_front(v, x, w, h=96, door_w=24.0, door_at='L', bar=None):
    """Frameless glass front: the swing door at one end hinged on the wall, one fixed panel. Swing lines dashed, apex at the hinge side."""
    dx = x if door_at == 'L' else x + w - door_w
    fx0, fx1 = (x + door_w, x + w) if door_at == 'L' else (x, x + w - door_w)
    C._rect(v, x, 0, x + w, h, C.OUTLINE); C._line(v, (x, h), (x + w, h), C.MED)
    C._rect(v, fx0 + 0.4, 0.6, fx1 - 0.6, h - 0.6, C.FINE, C.LIGHT)
    C._rect(v, dx, 0.5, dx + door_w, h - 1.0, C.OUTLINE); C._rect(v, dx + 0.6, 1.1, dx + door_w - 0.6, h - 1.6, C.FINE, C.LIGHT)
    hx, lx = (dx, dx + door_w) if door_at == 'L' else (dx + door_w, dx)
    for y in (0.5, h - 1.0): C._line(v, (lx, y), (hx, h / 2), C.FINE, C.MID)   # swings out, toward the viewer: solid
    for hy in (12, h - 12): C._rect(v, hx - 1.2, hy - 1.5, hx + 1.2, hy + 1.5, C.MED, fill=(1, 1, 1))
    px = lx - 3.4 if door_at == 'L' else lx + 2.2
    C._rect(v, px, 36, px + 1.2, 48, C.OUTLINE)
    if bar: C.towel_bar(v, (fx0 + fx1) / 2, 48, bar)
    for i in range(2): C._line(v, (fx1 - 14 + i * 2.5, h - 6), (fx1 - 14 + i * 2.5 + 8, h - 16), C.FINE, C.PALE)

def g_north(v):
    L = GL
    shell(v, L, crown=[(0, GLASS - HDR / 2)], base=[(GDOOR[1] + CS, GLASS)])
    tile(v, GLASS, L); C.schluter(v, GLASS, 0, H)
    header_cut(v, GLASS)
    C.casing(v, GDOOR[0], GDOOR[1] - GDOOR[0], HEAD); leaf_in(v, GDOOR[0], GDOOR[1] - GDOOR[0], 'L')
    C.robe_hook(v, (GDOOR[0] + GDOOR[1]) / 2, 66)
    ghost(v, GLASS - GD_W, GLASS, HEAD)
    v.text(v.X(GLASS - GD_W / 2), v.Y(62), 'GLASS DOOR,', 5.0, MID, align='c'); v.text(v.X(GLASS - GD_W / 2), v.Y(58), 'OPEN', 5.0, MID, align='c')
    C.glass_edge(v, GLASS, 96)
    v.text(v.X(GDOOR[0]), v.Y(105.5), 'DOOR TO GUEST BEDROOM', 5.0, MID); mtag(v, (GLASS + L) / 2, 102, 'WT-01, SHOWER')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, GDOOR[0], GDOOR[1], GDOOR[1] + CS, GLASS - GD_W, GLASS, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 66, HEAD, HEAD + CS, H - CR, H]))
    return ['2\'-8" x 8\'-0" DOOR. ROBE HOOK ON DOOR CL 5\'-6". SHOWER DOOR OPENS HERE.',
            'SWITCHES IN THE GUEST BEDROOM AT THE LATCH, CL 4\'-0".']

def g_east(v):
    L = GW
    shell(v, L)
    def far():
        tile(v, 0, L); niche(v, L / 2 - 12, 24, 48, 12)
        C.valve(v, OFFV, 48)
        C._rect(v, 2, 0, L - 2, 1.0, C.FINE)
    beyond(far)
    v.rect(v.X(0), v.Y(HEAD), v.X(L), v.Y(H), 0, color=WHITE, fill=WHITE)     # the painted header in the glass plane, in front of the tile
    C.crown(v, 0, L, H)
    v.line((v.X(0), v.Y(H)), (v.X(L), v.Y(H)), 0.9)
    glass_front(v, 0, L, HEAD, GD_W, 'L', bar=24.0)
    tag(v, L / 2, 101.5, 'PAINTED HEADER')
    mtag(v, (GD_W + L) / 2, 66, 'GLASS FRONT')   # under the glint marks, above the niche
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, OFFV, GD_W, (GD_W + L) / 2, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 48, 60, HEAD, H - CR, H]))
    return ['1/2" TEMPERED GLASS: 24" DOOR, 36" PANEL, TOWEL BAR CL 4\'-0".',
            'BEYOND: WT-01, VALVE CL 4\'-0", 1\'-0" FROM N. WALL, NICHE 24" x 12".']

def g_south(v):
    L = GL
    shell(v, L, crown=[(SHW + HDR / 2, L)], base=[(SHW, L)])
    tile(v, 0, SHW); C.schluter(v, SHW, 0, H)
    header_cut(v, SHW)
    C.shower_head(v, SHW / 2, 80)
    C.glass_edge(v, SHW, 96)
    tc = L - GTOI_C
    wall_toilet(v, tc)
    vx = (L - GVAN[1], L - GVAN[0])
    cx = vanity_wall(v, vx[0], vx[1] - vx[0], mirror_w=GMIR)
    C.outlet(v, vx[0] - 4.5, OUT_CL)
    mtag(v, SHW / 2, 102, 'WT-01, SHOWER')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, SHW / 2, SHW, tc, vx[0], cx, vx[1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, VAN_H, OUT_CL, MIR_B, 80, MIR_B + MIR[1], H - CR, H]))
    return ['SHOWER HEAD CL 6\'-8". 33" x 18" VANITY. LED MIRROR 24" x 48".',
            'GFCI 4-1/2" PAST VANITY, CL 3\'-6". WALL-HUNG SMART TOILET ON A CARRIER, FLUSH PLATE CL 3\'-8", SEAT GFCI 8" OFF THE BOWL CL, CL 1\'-2" (DASHED, BEHIND THE BOWL), SEE 5/ID-502.']

def g_west(v):
    L = GW
    shell(v, L, crown=[(0, L)], base=[(GVAN_D, L)])
    C.vanity_end(v, 0, GVAN_D, VAN_H, open_to='R')
    C.paper_holder(v, GVAN_D / 2, 26)
    C.towel_ring(v, GVAN_D / 2, 52)
    ghost(v, GW - 32.0, GW, HEAD, 'DOOR, OPEN')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, GVAN_D / 2, GVAN_D, GW - 32.0, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, BASE, 26, VAN_H, 52, HEAD, H - CR, H]))
    return ['PAPER HOLDER ON VANITY END CL 2\'-2". TOWEL RING CL 4\'-4".',
            'DOOR OPENS HERE (DASHED): NOTHING ON THE WALL.']

# ================================================================== key plans (FOR REV 1 base, clipped to the rooms, our changes drawn over it in the accent)
BASE_KEY = '/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'
def key_plan(sh, cell, floor, names, fbox, cover=(), k=4 / 3, pad=(14, 14, 70, 14), bottom=40):
    src = fitz.open(BASE_KEY); sp = src[floor - 1]
    T = BR.transform(floor)
    a, b = T(fbox[0], fbox[1]), T(fbox[2], fbox[3])
    clip_disp = fitz.Rect(a[0] - pad[0], a[1] - pad[1], b[0] + pad[2], b[1] + pad[3])
    u = clip_disp * sp.derotation_matrix; u.normalize()
    tw, th = clip_disp.width * k, clip_disp.height * k
    cx0, cy0, cx1, cy1 = cell
    assert tw <= cx1 - cx0 - 20 and th <= cy1 - cy0 - 30 - bottom, ('key plan does not fit', tw, th, cell)
    tx = cx0 + (cx1 - cx0 - tw) / 2; ty = cy0 + 30 + max(0.0, (cy1 - cy0 - 30 - bottom - th) / 2)
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    sh.p.show_pdf_page(target, src, floor - 1, clip=u, rotate=90)
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(floor, names, pad=9.0, doors=True)), 'key plan clip'
    def P(x, y): d = T(x, y); return (target.x0 + (d[0] - clip_disp.x0) * k, target.y0 + (d[1] - clip_disp.y0) * k)
    for x0, y0, x1, y1 in cover:
        p, q = P(x0, y0), P(x1, y1); sh.rect((min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])), width=0, color=WHITE, fill=WHITE)
    return target, P

def mask_outside(sh, t, P, box):
    """White out the key plan outside the room's own walls (box in FOR pt), so no neighbouring room shows."""
    a, b = P(box[0], box[1]), P(box[2], box[3])
    bx = fitz.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
    for r in ((t.x0 - 1, t.y0 - 1, t.x1 + 1, bx.y0), (t.x0 - 1, bx.y1, t.x1 + 1, t.y1 + 1), (t.x0 - 1, bx.y0, bx.x0, bx.y1), (bx.x1, bx.y0, t.x1 + 1, bx.y1)):
        sh.rect(r, width=0, color=WHITE, fill=WHITE)

def k_rect(sh, P, x0, y0, x1, y1, w=0.6, fill=None):
    p, q = P(x0, y0), P(x1, y1)
    sh.rect((min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])), width=w, color=ACC, fill=fill)
def k_line(sh, P, a, b, w=0.6, dashes=None):
    sh.line(P(*a), P(*b), w, ACC, dashes=dashes)
def k_arc(sh, P, c, r, a0, a1, w=0.4, dashes='[2 1.5] 0'):
    import math
    pts = [P(c[0] + r * math.cos(math.radians(t)), c[1] + r * math.sin(math.radians(t))) for t in [a0 + (a1 - a0) * i / 16 for i in range(17)]]
    sh.polyline(pts, w, ACC, dashes=dashes, close=False)
def k_toilet_wall(sh, P, wall, cl, axis, sign, IN_=1.5):
    """Wall-hung toilet in plan (review 11.09.26): FOR's floor-mount toilet and tank whited out, then a bowl off the wall face with the carrier
    dashed in the wall. axis 'x': the wall is vertical at x=wall, the bowl projects along x by sign; 'y': the wall is horizontal at y=wall."""
    import math
    def Q(d, t): return P(wall + sign * d * IN_, cl + t * IN_) if axis == 'x' else P(cl + t * IN_, wall + sign * d * IN_)
    a, b = Q(0.4, -11.5), Q(31.0, 11.5)                                         # mask FOR's symbol (tank and bowl)
    sh.rect((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), width=0, color=WHITE, fill=WHITE)
    a, b = Q(-6.0, -10.0), Q(0.0, 10.0)                                         # carrier in the furred wall, dashed
    sh.rect((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), width=0.4, color=ACC, dashes='[2 1.5] 0')
    pts = [Q(0.0, -7.0), Q(6.0, -7.25)] + [Q(6.0 + 15.0 * math.sin(math.radians(t_)), -7.25 * math.cos(math.radians(t_))) for t_ in range(0, 181, 10)] + [Q(0.0, 7.0)]
    sh.polyline(pts, 0.6, ACC, close=True)
    pts = [Q(8.0 + 10.5 * math.sin(math.radians(t_)), -5.0 * math.cos(math.radians(t_))) for t_ in range(0, 181, 10)]
    sh.polyline(pts, 0.4, ACC, close=False)

def k_vanity(sh, P, x0, y0, x1, y1):
    k_rect(sh, P, x0, y0, x1, y1, 0.6, WHITE)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = sh.p.new_shape(); a, b = P(cx - 7, cy - 9), P(cx + 7, cy + 9)
    s.draw_oval(fitz.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))); s.finish(color=ACC, width=0.4); s.commit()

def notes_block(sh, x0, y, width, lines, size=6.0, lh=None):
    from idd_sheet import ps
    lh = lh or ps(size) + 2.6
    paras = []
    for ln in lines:
        if paras and paras[-1] and ln and not paras[-1].rstrip().endswith(('.', ':', ')')): paras[-1] += ' ' + ln
        else: paras.append(ln)
    for ln in paras:
        if ln == '': y += lh * 0.6; continue
        for w in _wrap(ln, size, width): sh.text(x0, y, w, size, MID); y += lh
    return y

def draw_views(sh, cells, views, room, note_size=6.0):
    for cell, (n, title, L, fn) in zip(cells, views):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, K_LABEL)
        spec = {'room': room, 'view': title, 'length': L, 'ceiling': H}
        # the notes come from the view function, so draw once into a scratch page to read them, then size the top margin to fit them
        tmp = Sheet(fitz.open())
        notes = fn(View(tmp.p, tmp.font, tmp.fontname, (300, 600), K, spec))
        lines = _wrap(' '.join(notes), note_size, cell[2] - cell[0] - 16)
        from idd_sheet import ps
        lh = ps(note_size) + 2.6
        top = max(66, 30 + lh * len(lines) + 14)
        origin = E.fit_origin(cell, spec, K, top=top)
        v = View(sh.p, sh.font, sh.fontname, origin, K, spec)
        fn(v)
        v.dim_v(0, H, v.X(L) + 40, [0, H])                                     # overall height, floor to ceiling (review 11.09.26)
        v.text(v.X(0) - 6, v.Y(0) - 2.5, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 30
        for ln in lines: sh.text(cell[2] - 8, ny, ln, note_size, MID, align='r'); ny += lh

CHANGES_23 = ['CHANGES FROM FOR\'S PLAN (IN ORANGE):',
              '1. VANITIES 36" x 18", 2" OFF THE END WALL.',
              '2. FIXED GLASS SCREEN 30" x 60" ON EACH TUB AT THE VALVE END.']
CHANGES_G = ['CHANGES FROM FOR\'S PLAN (IN ORANGE):',
             '1. VANITY 33" x 18", 2" OFF THE WEST CORNER.',
             '2. GLASS FRONT: 24" DOOR HINGED ON THE NORTH WALL, 36" PANEL.',
             '3. LINEAR DRAIN AT THE EAST WALL.',
             '4. VALVE ON THE EAST WALL, 1\'-0" FROM THE NORTH WALL.',
             '5. LIGHT AND FAN SWITCHES IN THE GUEST BEDROOM.']
MATERIALS = ['VANITY: PAINTED, TURNED LEGS, STONE TOP, DECK FAUCET.',
             'MIRROR: FRAMELESS BACKLIT LED, 4\'-0" TO 8\'-0".',
             'WT-01: 12" x 24" PORCELAIN, HORIZONTAL, OVER MEMBRANE.',
             'SHOWER FLOORS: 2" x 2" MOSAIC, DCOF 0.42 MIN.',
             'GLASS: 1/2" TEMPERED, FRAMELESS, BRUSHED BRASS.',
             'BRASS EDGE TRIM AT TILE TO PAINT. NO CROWN AT TILE.',
             'WALLS PT-02, CROWN CM-01, BASE 8-1/2", CASING 5".',
             'CEILINGS PER FOR: BATHS 2 AND 3 9\'-10", GUEST BATH 10\'-8".',
             'TOILETS: WALL-HUNG SMART, IN-WALL CARRIER IN A FURRED CHASE.',
             'GFCI CL 3\'-6", SWITCHES CL 4\'-0", HUMIDITY FAN,',
             'WET-RATED DOWNLIGHT OVER EACH TUB AND SHOWER.',
             'TOWEL BARS 4\'-0", RINGS 4\'-4", HOOKS 5\'-6",',
             'PAPER HOLDERS 2\'-2".']

def build():
    keep = list(idd_sheet.EXTRA_REVS); idd_sheet.EXTRA_REVS[:] = REVS
    try: _build()
    finally: idd_sheet.EXTRA_REVS[:] = keep

KP_LABEL = {4 / 3: '1/4"', 2.0: '3/8"', 8 / 3: '1/2"', 4.0: '3/4"', 16 / 3: '1"'}
KP_PPF = 13.5                                   # the base is 3/16" (13.5 pt a foot): a key plan at k reads k x 13.5 pt a foot

def grid(frame, widths, key_h):
    """11.07.26 wide sheet: two columns of elevations sized to their walls (narrow walls get the narrow column), then a key column the rest
    of the width: the key plan cell on top (key_h tall) and the notes cell under it."""
    x0, y0, x1, y1 = frame; ym = (y0 + y1) / 2
    xa = x0 + widths[0]; xb = xa + widths[1]
    A = [(x0, y0, xa, ym), (x0, ym, xa, y1)]; B = [(xa, y0, xb, ym), (xa, ym, xb, y1)]
    return A, B, (xb, y0, x1, y0 + key_h), (xb, y0 + key_h, x1, y1)

def north_arrow(sh, nx, ny):
    """Plan north is up on every Helios sheet."""
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(nx, ny - 18), fitz.Point(nx + 8, ny + 8), fitz.Point(nx, ny + 2), fitz.Point(nx - 8, ny + 8), fitz.Point(nx, ny - 18)])
    s_.finish(color=INK, fill=INK, width=0.4); s_.commit()
    sh.text(nx, ny + 24, 'N', 10.0, INK, align='c', raw=True)

def kp_scale_bar(sh, x0, y, k, feet=4):
    """Graphic scale for a key plan: one-foot blocks, foot numbers under, the scale written to the right at 9 pt."""
    ppf = KP_PPF * k
    for i in range(feet):
        sh.rect((x0 + i * ppf, y - 6, x0 + (i + 1) * ppf, y), 0.4, INK, INK if i % 2 == 0 else (1, 1, 1))
    for i in range(feet + 1): sh.text(x0 + i * ppf, y + 13, "%d'" % i, 8.0, INK, align='c', raw=True)
    sh.text(x0 + feet * ppf + 16, y - 0.5, '%s TO 1\'-0"' % KP_LABEL[k], 9.0, INK, raw=True)

def kp_furniture(sh, t, k):
    """North arrow at the right and the scale bar at the left, both 30 pt under the plan (24 pt clear at least)."""
    y = t.y1 + 36
    kp_scale_bar(sh, t.x0, y, k)
    north_arrow(sh, t.x1 - 12, y - 4)
    return y + 30

BATHS = {   # sheet: room, FOR box of the room (inside faces), FOR labels and vanities covered, vanity, tub glass line, marker, room name (FOR pt)
    'ID-739': ('BATH 2', (446.5, 297.2, 535.8, 449.6), [(509, 348, 535.6, 374), (446.7, 396.6, 475.8, 449.7)],
               (446.2, 393.1, 473.2, 447.1), 342.1, (505.0, 368.0), (505.0, 391.5)),
    'ID-739A': ('BATH 3', (446.5, 137.2, 535.8, 288.2), [(509, 216, 535.6, 242), (446.7, 137.4, 475.8, 190.6)],
                (446.2, 140.0, 473.2, 194.0), 245.1, (505.0, 222.0), (505.0, 240.0)),
}

def _build():
    global H
    doc = fitz.open()
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)             # HDR_Y + 8 is 24 pt clear of the top frame (no header strip, 11.07.26)
    KB = 16 / 3                                                                # each bath's own key plan at 1" (11.07.26: one bath a sheet, each sheet stands alone)
    for sid, name, views in (
            ('ID-739', 'BATH 2', [(1, 'NORTH WALL - TUB ALCOVE', BW, b2_north), (2, 'EAST WALL - TOWEL BAR', BD, b2_east),
                                  (3, 'SOUTH WALL - DOOR TO BEDROOM 2', BW, b2_south), (4, 'WEST WALL - VANITY, TOILET, TUB', BD, b2_west)]),
            ('ID-739A', 'BATH 3', [(1, 'NORTH WALL - PAPER HOLDER, TOWEL RING', BW, b3_north), (2, 'EAST WALL - DOOR TO BEDROOM 3', BD, b3_east),
                                   (3, 'SOUTH WALL - TUB ALCOVE', BW, b3_south), (4, 'WEST WALL - TUB, TOILET, VANITY', BD, b3_west)])):
        H = H_B23                                                    # FOR A-206 (coordination 11.09.26)
        room, fbox, cover, van, glass, mk, nm = BATHS[sid]
        sh = Sheet(doc); sh.frame('%s ELEVATIONS' % name, 'AS NOTED', ['INTERIOR ELEVATIONS', name], sid, legend_rule=False)
        A, B, KC_, MC = grid(frame, (380, 520), 890)
        draw_views(sh, [A[0], B[0], A[1], B[1]], views, name)
        E.title_bar(sh.p, sh.font, sh.fontname, KC_, 5, 'FLOOR 2 KEY PLAN - %s' % name, 'SCALE: %s TO 1\'-0"' % KP_LABEL[KB])
        t, P = key_plan(sh, KC_, 2, [room], fbox, cover, k=KB, pad=(14, 14, 14, 14), bottom=70)
        mask_outside(sh, t, P, (fbox[0] - 12.5, fbox[1] - 7.5, fbox[2] + 7.5, fbox[3] + 7.5))   # nothing of the next room shows
        k_toilet_wall(sh, P, 446.5, 369.0 if sid == 'ID-739' else 218.1, 'x', 1)
        k_vanity(sh, P, *van)
        k_line(sh, P, (446.2, glass), (491.2, glass), 1.3)
        quad_marker(sh, *P(*mk), sid, {'N': 1, 'E': 2, 'S': 3, 'W': 4})
        X, Y = P(*nm); sh.text(X, Y, name, 10.0, INK, align='c', raw=True)
        kp_furniture(sh, t, KB)
        E.title_bar(sh.p, sh.font, sh.fontname, MC, 6, 'CHANGES, MATERIALS AND HEIGHTS', 'SECONDARY BATHS')
        y = notes_block(sh, MC[0] + 8, MC[1] + 30, MC[2] - MC[0] - 16, [CHANGES_23[0], CHANGES_23[1], '2. FIXED GLASS SCREEN 30" x 60" ON THE TUB AT THE VALVE END.'])
        notes_block(sh, MC[0] + 8, y + 8, MC[2] - MC[0] - 16, MATERIALS)
    # ---- ID-740 guest bath
    H = H_G                                                                    # FOR A-205 guest bath 10'-8"
    sh = Sheet(doc); sh.frame('GUEST BATHROOM ELEVATIONS', 'AS NOTED', ['INTERIOR ELEVATIONS', 'GUEST BATHROOM'], 'ID-740', legend_rule=False)
    KG = 16 / 3                                                                # key plan 1" (was 1/2")
    A, B, KC_, MC = grid(frame, (460, 320), 650)
    views = [(1, 'NORTH WALL - DOOR', GL, g_north), (2, 'EAST WALL - SHOWER, GLASS FRONT', GW, g_east),
             (3, 'SOUTH WALL - SHOWER HEAD, TOILET, VANITY', GL, g_south), (4, 'WEST WALL - PAPER HOLDER, TOWEL RING', GW, g_west)]
    draw_views(sh, [A[0], B[0], A[1], B[1]], views, 'GUEST BATHROOM')
    E.title_bar(sh.p, sh.font, sh.fontname, KC_, 5, 'FLOOR 1 KEY PLAN - GUEST BATHROOM', 'SCALE: %s TO 1\'-0"' % KP_LABEL[KG])
    t, P = key_plan(sh, KC_, 1, ['GUEST BATHROOM'], (356.2, 815.2, 511.2, 905.2),
                    [(419, 819, 452, 838), (356.4, 874.4, 407.0, 905.0), (457.9, 815.9, 510.5, 898.0)], k=KG, pad=(14, 14, 14, 14), bottom=70)
    mask_outside(sh, t, P, (344.4, 804.3, 518.0, 913.9))
    k_toilet_wall(sh, P, 905.2, 431.85, 'y', -1)
    k_vanity(sh, P, 359.2, 878.2, 408.7, 905.2)
    k_line(sh, P, (457.2, 851.2), (457.2, 905.2), 1.3)                                       # fixed panel
    k_line(sh, P, (457.2, 815.6), (421.2, 815.6), 1.3)                                       # the door, open along the north wall
    k_arc(sh, P, (457.2, 815.2), 36.0, 90, 180)                                              # its swing to the glass line
    k_rect(sh, P, 506.7, 819.2, 509.7, 901.2, 0.5)                                           # linear drain
    k_rect(sh, P, 511.6, 831.2, 514.6, 835.2, 0.3, ACC)                                      # offset valve
    quad_marker(sh, *P(MK_G[0], MK_G[1]), 'ID-740', {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    X, Y = P(*NM_G); sh.text(X, Y, 'GUEST BATHROOM', 10.0, INK, align='c', raw=True)
    kp_furniture(sh, t, KG)
    E.title_bar(sh.p, sh.font, sh.fontname, MC, 6, 'CHANGES, MATERIALS AND HEIGHTS', 'GUEST BATHROOM')
    y = notes_block(sh, MC[0] + 8, MC[1] + 30, MC[2] - MC[0] - 16, CHANGES_G)
    notes_block(sh, MC[0] + 8, y + 8, MC[2] - MC[0] - 16, [
        'SHOWER: CURBLESS, 1/4" PER FOOT TO THE LINEAR DRAIN.',
        'MEMBRANE TURNED UP 6". HEADER OVER GLASS 8\'-0" TO CEILING.',
        'BLOCKING FOR THE GLASS HINGES IN THE NORTH WALL.', ''] + MATERIALS)
    fix_soft_hyphen(doc)
    doc.set_metadata({'title': 'Casa Grove secondary baths ID-739, ID-739A, ID-740 (FOR REV 1)', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
