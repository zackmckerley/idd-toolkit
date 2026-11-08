import sys
"""Master bathroom, REDRAWN ON FOR REV 1 (A-202 REV 1, 10.23.26) 11.06.26. Option A language (furniture vanities, framed mirrors, cylinder sconces, painted walls,
WT-02 tile in the shower and tub alcove only). Drawn with idd_components.
Sheets: ID-730 key plan with the elevation markers; ID-731 room elevations 1-4; ID-732 shower and tub alcove; ID-733 water closet.
Geometry measured off FOR's A-202 REV 1 vectors and a 400 dpi raster (FOR sheet pt, 1.5 pt per inch, plan north up the sheet):
  west face x 446.2, east face 689.2 (13'-6"), north face y 1080.0, south face 1291.0 (finished, the block at 1294.0)
  W.I.C. opening north wall 540.7 to 594.7 (3'-0", FOR a pocket door); FOR's built-in vanities 447.1 to 529.4 and 605.9 to 688.2 (4'-7")
  pocket door to the bedroom, east wall, 1128.1 to 1182.1 (3'-0"); terrace door pair, west wall, 1113.1 to 1197.1 (4'-8")
  alcove line: north face 1198.6, south face 1205.5; west stub 446.1 to 452.8; shower pier 505.4 to 519.1
  shower 446.2 to 512.2 x 1205.5 to 1291.0 (3'-8" x 4'-9"), FOR's 15" corner seat 489.7 to 512.2 x 1268.5 to 1291.0, valve at y 1248.2,
  ceiling shower head, center drain; shower window, west wall, 1220.5 to 1276.0 (3'-1")
  tub alcove 519.1 to 616.2 (5'-4-3/4"), FOR's 60" x 32" tub 522.7 to 612.7, window 522.7 to 612.7 (5'-0") centered
  water closet 623.16 to 686.4 (3'-6-1/8", FOR's drywall faces), FOR's door 2'-6" leaf 634.8 to 679.6 hinged east, toilet 643.4 to 665.4 (within 1/4" of center)
PLAN below: inches from the room's west wall face (x) and north wall face (y). Output: 261105.HD102.MasterBathPilot.pdf"""
import pymupdf as fitz
import idd_elevations as E, idd_components as C
SWING_DASH = '[2 1.5] 0'
_SOLID = [False]
def _line_open(v, a, b, w=C.MED, c=None, dashes=None):
    """C._line without closePath (a closed two-point path is stroked out and back, which fills a dash pattern solid).
    Swing dashes drop when the door being drawn swings toward the viewer."""
    c = INK if c is None else c
    if dashes == SWING_DASH and _SOLID[0]: dashes = None
    sh_ = v.p.new_shape(); sh_.draw_line(fitz.Point(v.X(a[0]), v.Y(a[1])), fitz.Point(v.X(b[0]), v.Y(b[1])))
    sh_.finish(color=c, width=w, dashes=dashes, closePath=False); sh_.commit()
C._line = _line_open
def leaf(v, x, w, head, panels, swing, toward):
    """Door leaf with the set's swing rule: solid swing marks toward the viewer, dashed away."""
    _SOLID[0] = toward
    try: C.door_leaf(v, x, w, head, panels=panels, swing=swing)
    finally: _SOLID[0] = False
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT, TRIM

OUT = '/home/claude/flrwork/261105.HD102.MasterBathPilot.pdf'
H = 120.0                 # ceiling, VERIFY
HEAD, SILL = 96.0, 48.0   # door and window heads, bath window sills, VERIFY
CS = TRIM['casing']
CTR, FAUCET, MIR_B, MIR_T, SCONCE = 34.0, 40.0, 44.0, HEAD + CS, 66.0   # mirror top on the top of the head casing
TILE = (48, 96)           # WT-02 large-format porcelain slab, 48 x 96 panels set vertical, seams as drawn
WHITE = (1, 1, 1); BEYOND = (0.55, 0.55, 0.55)

# ---- plan, inches from FOR REV 1 (see the docstring)
def FX(x): return round((x - 446.2) / 1.5 * 8) / 8   # to the nearest 1/8", so every dimension string closes
def FY(y): return round((y - 1080.0) / 1.5 * 8) / 8
ROOM_W, ROOM_D = FX(689.2), FY(1291.0)    # 13'-6" x 11'-8-5/8"
WIC_X, WIC_W = FX(540.7), 36.0            # FOR's 3'-0" opening in the north wall, 5'-3" from each corner
VAN_W = 51.0                              # furniture vanities, centered on each wall segment between the corner and the opening casing
VAN_GAP = (WIC_X - CS - VAN_W) / 2        # 3-1/2 in. each side with the 5 in. casing
VAN_L, VAN_R = (VAN_GAP, VAN_W), (ROOM_W - VAN_GAP - VAN_W, VAN_W)
GFCI_OFF, GFCI_CL = 15.5, 42.0             # GFCI duplex in the outboard margin between the mirror and the sconce, CL 3'-6"
TBAR_Y, TBAR_W = CTR - 3.5, 18.0           # 18" hand towel bar on each vanity's apron (the side walls are a pocket and a 3-1/2" gap)
MIR_W, SC_OFF = 25.0, 6.0                 # mirror 25" wide, sconces 6" outside it: the outer sconce backplates 8-1/4" clear of the corners
PD_Y0, PD_Y1 = FY(1128.1), FY(1182.1)     # FOR's 3'-0" pocket door in the east wall (from the north face)
FRONT_Y0, FRONT_Y1 = FY(1198.6), FY(1205.5) # alcove line: the water closet front wall and the piers, 4-5/8"
ALC_D = ROOM_D - FRONT_Y1                 # alcove depth, 56.7
WC_DOOR = 30.0                            # FOR's 2'-6" water closet door leaf
WC_IN = (FX(623.16), FX(686.4))           # water closet interior (plan x) between FOR's drywall faces, 3'-6-1/8"
WC_CTR = (WC_IN[0] + WC_IN[1]) / 2
WC_D0 = round((WC_CTR - WC_DOOR / 2) * 8) / 8
WC_D = (WC_D0, WC_D0 + WC_DOOR)            # the door centered on the water closet within 1/16" on the 1/8" grid
WC_SHIFT = round((FX(657.2) - (WC_D[0] + WC_DOOR / 2)) * 8) / 8   # west of FOR's leaf (634.8 to 679.6, center 657.2)
PIER_SH = (FX(505.4), FX(519.1))          # pier between the shower opening and the tub alcove (plan x), 9-1/8"
STUB_SH = (0.0, 4.5)                      # stub at the west wall where the shower glass lands, 446.1 to 452.8 = 4-1/2"
TUB_WALL = (FX(519.1), FX(616.2))         # tub alcove (plan x), 5'-4-3/4", FOR's 5'-0" window centered, 2-3/8" each side
TUB_L = 58.0                              # 58" freestanding tub in place of FOR's 60": 3-3/8" each side to clean behind
TUB_CL = ((TUB_WALL[1] - TUB_WALL[0]) - TUB_L) / 2
PIER_WC = (TUB_WALL[1], WC_D[0])          # pier between the tub alcove and the water closet door (plan x)
SH_IN = (0.0, FX(512.2))                  # shower interior (plan x), 3'-8"
TER_Y0, TER_Y1 = FY(1113.1), FY(1197.1)   # terrace door opening in the west wall (from the north face), 4'-8"
SWIN_Y0, SWIN_Y1 = FY(1220.5), FY(1276.0) # shower window in the west wall (from the north face), 3'-1"
TOILET_W = FX(665.4) - FX(643.4)          # 14-5/8" toilet, tank against the south wall, centered on the water closet
TOILET_X = (WC_CTR - TOILET_W / 2, WC_CTR + TOILET_W / 2)
SH_DOOR = 28.0                            # frameless glass shower door hinged on the pier, the rest of the front one fixed panel to the stub
VALVE_FOR = FY(1248.2) - FY(1205.5)       # FOR's valve, 2'-4-1/2" in from the alcove line on the shower's east partition
VALVE_IN = 15.0                           # moved to 15" from the glass so it is reached from the door without stepping into the spray
SEAM_SH = 34.0                            # the shower east wall slab seam, clear of the valve, the slide bar and the ceiling head
SEAT = 15.0                               # FOR's triangular corner seat in the SE corner of the shower, 15" legs, top 17" AFF (VERIFY)
SEAT_H = 17.0
WIN_M = ((TUB_WALL[1] - TUB_WALL[0]) - 60.0) / 2   # tub window margins, 2-3/8"

def sx(plan_x): return ROOM_W - plan_x    # looking south: view x runs east to west
def wx(plan_y): return ROOM_D - plan_y    # looking west: view x runs south to north

def shell(v, L, crown=(), base=(), cut_left=True, cut_right=True):
    """Floor, ceiling, cut end walls, crown and base runs (lists of (x0, x1))."""
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    for a, b in base: C.base(v, a, b)
    for a, b in crown: C.crown(v, a, b, H)
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    if cut_left: v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    if cut_right: v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=(0.3, 0.3, 0.3))

def towel_ring(v, cx, cy):
    C._ellipse(v, cx, cy - 4, 3.0, 3.0, C.OUTLINE); C._ellipse(v, cx, cy, 1.1, 1.1, C.FINE, MID)
def robe_hook(v, cx, cy):
    C._rect(v, cx - 1.0, cy - 1.0, cx + 1.0, cy + 1.0, C.FINE); C._line(v, (cx, cy - 1.0), (cx, cy - 3.0), C.OUTLINE); C._ellipse(v, cx, cy - 3.3, 0.6, 0.6, C.FINE)
def tile_cap(v, x0, x1, y=HEAD): C._line(v, (x0, y), (x1, y), C.OUTLINE)
def seat_front(v, x0, w):
    """FOR's triangular corner seat seen on its wall: a 1-1/2" slab top at SEAT_H, white so it masks the tile joints behind it."""
    C._rect(v, x0, SEAT_H - 1.5, x0 + w, SEAT_H, C.OUTLINE, fill=WHITE); C.shadow(v, x0, x0 + w, SEAT_H - 1.5)
def seat_side(v, x, side):
    """The corner seat seen end on from the other wall of the corner: its 15" leg along the wall."""
    a, b = (x, x + SEAT) if side == 'R' else (x - SEAT, x)
    C._rect(v, a, SEAT_H - 1.5, b, SEAT_H, C.OUTLINE, fill=WHITE); C.shadow(v, a, b, SEAT_H - 1.5)
def ceiling_head(v, cx, w=12.0):
    """A flush ceiling rain head seen edge on: a thin disc at the ceiling with its trim ring."""
    C._rect(v, cx - w / 2, H - 1.0, cx + w / 2, H, C.OUTLINE, fill=WHITE); C._line(v, (cx - w / 2 - 1, H), (cx + w / 2 + 1, H), C.MED)
def slide_bar(v, cx, y0=40.0, y1=76.0):
    """A 36" hand shower slide bar with the hand shower parked on it and the hose to the elbow below."""
    C._rect(v, cx - 0.4, y0, cx + 0.4, y1, C.OUTLINE, fill=WHITE)
    for y in (y0, y1): C._ellipse(v, cx, y, 0.9, 0.9, C.OUTLINE, fill=WHITE)
    C._rect(v, cx - 1.2, y1 - 9, cx + 1.2, y1 - 3, C.OUTLINE, fill=WHITE); C._ellipse(v, cx, y1 - 2.0, 1.6, 1.0, C.OUTLINE, fill=WHITE)
    C._ellipse(v, cx, y0 - 4.0, 1.0, 1.0, C.OUTLINE, fill=WHITE)
def finish_tag(v, x, y, s): v.text(v.X(x), v.Y(y), s, 5.2, MID, align='c')
def _dim_v(self, y0i, y1i, x_pt, pts_i, side='r'):
    """E.ElevationView.dim_v with the fit test on the printed label width: a label longer than its segment is set level, beside the string."""
    ys = [self.Y(q) for q in pts_i]
    E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
    self.line((x_pt, ys[0]), (x_pt, ys[-1]), 0.4)
    for y in ys:
        self.line((x_pt - 3, y), (x_pt + 3, y), 0.4); self.line((x_pt - 1.8, y + 1.8), (x_pt + 1.8, y - 1.8), 0.6)
    flip = False; last = None
    for a, b in zip(pts_i, pts_i[1:]):
        if b - a < 0.5: continue
        cy = (self.Y(a) + self.Y(b)) / 2; seg = (b - a) * self.k; t = E.ftin(b - a)
        sz = 5.5 if seg >= 26 else 5.0
        if self.F.text_length(t, fontsize=sz) + 6 > seg:
            off = 6.0
            if last and abs(last[0] - cy) < 8: off = last[1] + 4.0         # next to the previous level label, not on it
            w = self.text(x_pt + off if side == 'r' else x_pt - off, cy + 2.2, t, 5.0, align='l' if side == 'r' else 'r')
            if off == 6.0: self.line((x_pt + 1.0 if side == 'r' else x_pt - 1.0, cy), (x_pt + 5.0 if side == 'r' else x_pt - 5.0, cy), 0.3)
            last = (cy, off + w); continue
        last = None
        short = seg < 26
        x_text = x_pt - 2.5 if side == 'r' else x_pt + 7.5
        if short and flip: x_text = x_pt + 7.5 if side == 'r' else x_pt - 2.5
        self.text(x_text, cy, t, sz, align='c', rotate=90)
        flip = not flip if short else False
E.ElevationView.dim_v = _dim_v

def dimh(v, x0i, x1i, y_pt, pts_i):
    """E.ElevationView.dim_h, except a label wider than its segment is set above the string, clear of the ticks (end segments
    start at the outer tick so nothing runs into the cut wall or FIN. FLR.)."""
    xs = [v.X(q) for q in pts_i]
    E.check_string(pts_i, v.w.get('room'), v.w.get('view'))
    v.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
    for x in xs:
        v.line((x, y_pt - 3), (x, y_pt + 3), 0.4); v.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)
    segs = list(zip(pts_i, pts_i[1:]))
    for i, (a, b) in enumerate(segs):
        if b - a < 0.5: continue
        t = E.ftin(b - a); sz = 5.0 if (b - a) * v.k < 26 else 5.5
        w = v.F.text_length(t, fontsize=sz); room = (b - a) * v.k
        if w + 7 <= room: v.text((v.X(a) + v.X(b)) / 2, y_pt - 2.5, t, sz, align='c'); continue
        if i == 0: v.text(v.X(a) - 4.0, y_pt + 2.2, t, 5.0, align='r')           # in line with the string, outside the end tick
        elif i == len(segs) - 1: v.text(v.X(b) + 4.0, y_pt + 2.2, t, 5.0)
        else: v.text((v.X(a) + v.X(b)) / 2, y_pt - 5.5, t, 5.0, align='c')      # above, clear of the tick tops
def slab(v, x0, x1, seams, h0=0, h1=H, course=96.0):
    """WT-02 48 x 96 slab: vertical seams where given, the horizontal seam at 8'-0"."""
    for xs in seams: C._line(v, (xs, h0), (xs, h1), C.FINE, C.TILE)
    if h0 < course < h1: C._line(v, (x0, course), (x1, course), C.FINE, C.TILE)
def shower_front(v, x, w, h=96, door_w=28):
    """Frameless 1/2" tempered front: the door hinged on the pier (left) on two wall-mount glass hinges, a fixed panel to the stub.
    Swing marks meet at the hinge side, the pull at the latch side, header channel across the top."""
    C._rect(v, x, 0, x + w, h, C.OUTLINE); C._line(v, (x, h), (x + w, h), C.MED)
    C._rect(v, x + door_w + 0.4, 0.6, x + w - 0.6, h - 0.6, C.FINE, LIGHT)                    # fixed panel
    C._rect(v, x + 0.5, 0.5, x + door_w, h - 1.0, C.OUTLINE); C._rect(v, x + 1.1, 1.1, x + door_w - 0.6, h - 1.6, C.FINE, LIGHT)
    hx, lx = x + 0.5, x + door_w
    C._line(v, (lx, 0.5), (hx, h / 2), C.FINE, MID); C._line(v, (lx, h - 1.0), (hx, h / 2), C.FINE, MID)   # swings out, toward the room: solid
    for hy in (12, h - 12): C._rect(v, x - 1.6, hy - 1.8, x + 1.4, hy + 1.8, C.MED, fill=WHITE)   # wall-mount hinges on the pier
    C._rect(v, lx - 3.4, 36, lx - 2.2, 48, C.OUTLINE)                                            # 12" pull
    for i in range(2): C._line(v, (x + 4 + i * 2.5, h - 6), (x + 4 + i * 2.5 + 8, h - 16), C.FINE, C.PALE)
def casing_north_only(v, x, w, head):
    """The terrace pair's casing where the south jamb is 1" off the alcove wall: head and north leg only, the south jamb wrapped."""
    cs = CS
    C._rect(v, x + w, 0, x + w + cs, head + cs, C.OUTLINE); C._rect(v, 0, head, x + w + cs, head + cs, C.OUTLINE)
    C._line(v, (x + w + cs, head + cs), (x + w, head), C.FINE, MID); C._rect(v, 0, 0, x, head, C.FINE, MID)
    C._rect(v, x - 0.25, 0, x + w + 0.25, head + 0.25, C.FINE, MID)

# ================================================================== room elevations (ID-731)
def north(v):
    L = ROOM_W
    shell(v, L, crown=[(0, L)], base=[(VAN_L[0] + VAN_W, WIC_X - CS), (WIC_X + WIC_W + CS, VAN_R[0])])   # no base behind the vanities
    C.door_pair(v, WIC_X, WIC_W, HEAD, panels=1)
    for (x, w), side in ((VAN_L, -1), (VAN_R, 1)):
        C.vanity_furniture(v, x, w, h=CTR, legs=True, drawers=3, faucet_style='wall')
        mx = x + w / 2; mw = MIR_W
        C.mirror_framed(v, mx - mw / 2, mw, MIR_B, MIR_T - MIR_B)
        for s in (mx - mw / 2 - SC_OFF, mx + mw / 2 + SC_OFF): C.sconce(v, s, SCONCE, 'cylinder')
        C.outlet(v, mx + side * GFCI_OFF, GFCI_CL, 'GFCI')                     # outboard mirror margin, within 3' of the basin
        C.towel_bar(v, mx, y=TBAR_Y, w=TBAR_W)                                  # hand towels on the vanity front (the east wall is the pocket)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, VAN_L[0], VAN_L[0] + VAN_W / 2, VAN_L[0] + VAN_W, WIC_X - CS, WIC_X + WIC_W + CS, VAN_R[0], VAN_R[0] + VAN_W / 2, VAN_R[0] + VAN_W, L]))
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TRIM['base'], CTR, FAUCET, MIR_B, SCONCE, HEAD, MIR_T, H - TRIM['crown'], H]))
    return ['51" PAINTED FURNITURE VANITIES, STONE TOPS, WALL FAUCETS CL 3\'-4". FRAMED MIRRORS 25" x 57", TOP AT 8\'-5". SCONCES CL 5\'-6".',
            'W.I.C.: PAIR OF 1\'-6" PAINTED DOORS. GFCI CL 3\'-6" AT EACH VANITY. 18" TOWEL BAR ON EACH VANITY APRON. PT-02, CM-01.']

def east(v):
    L = FRONT_Y0
    shell(v, L, crown=[(0, L)], base=[(20.1, PD_Y0 - CS), (PD_Y1 + CS, L)])
    C.casing(v, PD_Y0, PD_Y1 - PD_Y0, HEAD); C.door_leaf(v, PD_Y0, PD_Y1 - PD_Y0, HEAD, panels=1, swing=None)
    C._rect(v, 0.0, TRIM['base'], PD_Y0 - CS, HEAD, C.FINE, LIGHT, dashes='[2 1.5] 0'); v.text(v.X((PD_Y0 - CS) / 2 + 4), v.Y(80), 'POCKET', 5.0, MID, align='c')
    C._rect(v, 0, 0, 20.1, CTR, C.FINE, WHITE, fill=WHITE)
    C.vanity_end(v, 0, depth=20.1, h=CTR, open_to='R')
    SWX = (PD_Y1 + CS + L) / 2; C.switch(v, SWX, 48.0, 'S/F')               # light and fan, latch side, bath face
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, 20.1, PD_Y0, PD_Y1, L]))
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, CTR, 48.0, HEAD, H - TRIM['crown'], H]))
    return ['DOOR 19: 3\'-0" x 8\'-0" POCKET DOOR, POCKET DASHED. NOTHING FIXED TO THE POCKET WALL.',
            'LIGHT AND FAN SWITCHES (2-GANG) CL 4\'-0" AT THE LATCH SIDE. PT-02, CM-01.']

def south(v):
    """The front plane at the alcove line as the room sees it: one painted wall with the water closet door, the open tub alcove
    and the glass-fronted shower. What is inside the alcoves is drawn lightly, as beyond; their own elevations are on ID-732 and ID-733."""
    L = ROOM_W
    wc_door = (sx(WC_D[1]), sx(WC_D[0]))                                   # centered on the water closet, 7-1/8" to the corner
    pier_wc = (sx(PIER_WC[1]), sx(PIER_WC[0]))
    tub = (sx(TUB_WALL[1]), sx(TUB_WALL[0]))
    pier_sh = (sx(PIER_SH[1]), sx(PIER_SH[0]))
    sh_open = (sx(PIER_SH[0]), sx(STUB_SH[1]))
    stub = (sx(STUB_SH[1]), L)
    shell(v, L, crown=[(0, pier_wc[1]), (pier_sh[0], L)], base=[(0, wc_door[0]), (wc_door[1], pier_wc[1]), pier_sh, stub])
    # beyond, lightly: tub alcove back wall (tile line, window, tub) and the shower back wall (niche)
    keep = (C.INK, C.MID); C.INK = BEYOND; C.MID = BEYOND
    win = (tub[0] + WIN_M, tub[1] - WIN_M)
    C.window(v, win[0], win[1] - win[0], SILL, HEAD, lites=3, trim=False)
    C.tub_filler_wall(v, (tub[0] + tub[1]) / 2, 30); C.freestanding_tub(v, (tub[0] + tub[1]) / 2 - TUB_L / 2, TUB_L, 22, filler=None)
    shc = (sx(SH_IN[1]) + sx(SH_IN[0])) / 2; C.niche(v, shc - 12, 24, 58, 12, shelves=0)
    C.INK, C.MID = keep
    # header wall over the shower glass, same as over the water closet door: masks what is beyond above 8'-0"
    C._rect(v, sh_open[0], HEAD, sh_open[1], H, C.FINE, WHITE, fill=WHITE); C.crown(v, sh_open[0], sh_open[1], H)
    C._line(v, (sh_open[0], HEAD), (sh_open[1], HEAD), C.OUTLINE)
    # the alcove openings: heavy jamb lines with a shadow on the recess side
    for (a, b), top in ((tub, H), (sh_open, HEAD)):
        C._line(v, (a, 0), (a, top), C.HEAVY); C._line(v, (b, 0), (b, top), C.HEAVY)
        C._line(v, (a + 0.6, 0), (a + 0.6, top), C.FINE, LIGHT); C._line(v, (b - 0.6, 0), (b - 0.6, top), C.FINE, LIGHT)
    # shower glass: frameless 1/2" tempered front, the 28 in. door hinged on the pier (left), one fixed panel to the stub
    fin = sh_open[1] - sh_open[0] - SH_DOOR
    shower_front(v, sh_open[0], sh_open[1] - sh_open[0], HEAD, SH_DOOR)
    finish_tag(v, sh_open[0] + 10.5, 5.5, '1/2" TEMPERED')   # low on the hinge side, clear of the swing lines
    # water closet door in the front wall, hinged at the east jamb; robe hook on the pier
    C.casing(v, wc_door[0], WC_DOOR, HEAD); leaf(v, wc_door[0], WC_DOOR, HEAD, 2, 'L', toward=False)
    robe_hook(v, (pier_wc[0] + CS + pier_wc[1]) / 2, 68)                          # centered on the pier clear of the casing
    finish_tag(v, (tub[0] + tub[1]) / 2, 108, 'TUB ALCOVE BEYOND, SEE ID-732')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, wc_door[0], wc_door[1], pier_wc[1], tub[1], sh_open[0], sh_open[0] + SH_DOOR, sh_open[1], L]))
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 36, 48, HEAD, H - TRIM['crown'], H]))
    return ['WATER CLOSET DOOR 2\'-6", SEE ID-733. TUB ALCOVE WT-02 SLAB, SEE ID-732. DOUBLE ROBE HOOK CL 5\'-8".',
            'SHOWER: 1/2" TEMPERED GLASS, 8\'-0" HIGH, 28" DOOR ON WALL HINGES, %s FIXED PANEL. PAINTED HEADER ABOVE.' % E.ftin(round(fin * 8) / 8)]

def west(v):
    """West wall from the shower stub to the north corner; the shower side wall is drawn with the shower on ID-732."""
    L = FRONT_Y0
    stub = (0.0, FRONT_Y1 - FRONT_Y0)                    # 0 to 4.8, 3.9 in. proud
    door = (FRONT_Y0 - TER_Y1, FRONT_Y0 - TER_Y0)        # 1.1 to 56.8
    shell(v, L, crown=[(0, L)], base=[(door[1] + CS, L)])
    w_ = door[1] - door[0]; casing_north_only(v, door[0], w_, HEAD)
    leaf(v, door[0], w_ / 2, HEAD, 'glass', 'L', toward=False); leaf(v, door[0] + w_ / 2, w_ / 2, HEAD, 'glass', 'R', toward=False)
    finish_tag(v, door[1] - 12.0, 12.5, 'TEMPERED')   # south leaf, below its lower swing line
    C._rect(v, L - 20.1, 0, L, CTR, C.FINE, WHITE, fill=WHITE)              # the north casing and the base break behind the vanity
    C.vanity_end(v, L, depth=20.1, h=CTR, open_to='L')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, door[0], door[1], L]))
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, CTR, HEAD, H - TRIM['crown'], H]))
    return ['TERRACE DOORS: PAIR OF 2\'-4" FULL-LITE DOORS, 8\'-0" HEAD, TEMPERED IMPACT GLASS. SOUTH JAMB WRAPPED, NO CASING.',
            'PT-02, CM-01. SHOWER SIDE WALL, SEE ID-732.']

# ================================================================== shower (ID-732), all faces WT-02 floor to ceiling
def shower_west(v):
    """Shower side wall with the window, looking west: back wall at the left, glass line at the right."""
    L = ALC_D
    win = (wx(SWIN_Y1), wx(SWIN_Y0))
    shell(v, L, cut_right=False)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.window(v, win[0], win[1] - win[0], SILL, HEAD, lites=2, trim=False)
    sw = FRONT_Y1 - FRONT_Y0                                           # the stub's end, the alcove wall's 4-1/2" thickness
    C.pilaster(v, L, sw, H, shadow_side='L'); C.tile_grid(v, L, L + sw, 0, H, TILE, show=[(L, L + sw, 0, H)])
    C.glass_edge(v, L, HEAD)
    dimh(v, 0, L + sw, v.Y(0) + 14, E.snap_points([0, win[0], win[1], L, L + sw], tol=0.3))
    v.dim_v(0, H, v.X(L + sw) + 14, E.snap_points([0, SILL, HEAD, H]))
    return ['WT-02 SLAB 48" x 96", FLOOR TO CEILING, SEAMS AS DRAWN.',
            'WINDOW 3\'-1" x 4\'-0", 4\'-0" SILL, TEMPERED. SLAB SILL, SLOPED.']

def shower_south(v):
    L = SH_IN[1] - SH_IN[0]
    shell(v, L)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.niche(v, L / 2 - 12, 24, 58, 12, shelves=0)
    seat_front(v, 0, SEAT)                                             # the SE corner is at the left looking south
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, SEAT, L / 2 - 12, L / 2 + 12, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SEAT_H, 58, 70, H]))
    return ['WT-02 SLAB, SEAM AT 8\'-0". NICHE 24" x 12" x 3-1/2", SILL AT 4\'-10".',
            'CORNER SEAT, 15" LEGS, SLAB TOP AT 1\'-5". LINEAR DRAIN AT THIS WALL.']

def shower_east(v):
    """The partition to the tub alcove, looking east: glass line at the left, back wall at the right."""
    L = ALC_D
    shell(v, L, cut_left=False)
    slab(v, 0, L, [SEAM_SH])
    pw = FRONT_Y1 - FRONT_Y0                                           # the pier's 4-1/2" jog at the alcove line, where the glass lands
    v.x_left = -pw
    C.pilaster(v, -pw, pw, H, shadow_side='R'); C.tile_grid(v, -pw, 0, 0, H, TILE, show=[(-pw, 0, 0, H)])
    C.valve(v, VALVE_IN, 48)
    ceiling_head(v, L / 2)
    slide_bar(v, VALVE_IN + 7.0)
    seat_side(v, L, 'L')
    C.glass_edge(v, -pw / 2, HEAD)
    dimh(v, -pw, L, v.Y(0) + 14, E.snap_points([-pw, 0, VALVE_IN, VALVE_IN + 7.0, L - SEAT, L], tol=0.3))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SEAT_H, 40, 48, 76, HEAD, H]))
    return ['VALVE CL 4\'-0", %s FROM THE GLASS. HAND SHOWER ON A 36" SLIDE BAR.' % E.ftin(VALVE_IN),
            '12" CEILING RAIN HEAD. WT-02 SLAB, SEAMS AT %s AND 8\'-0".' % E.ftin(SEAM_SH)]

# ================================================================== tub alcove (ID-732), WT-02 to 8'-0", PT-02 and crown above
def tub_south(v):
    L = TUB_WALL[1] - TUB_WALL[0]
    shell(v, L)
    sm = [L / 2 - 24, L / 2 + 24]                                       # a 48" panel centered behind the filler, equal pieces each side
    slab(v, 0, L, sm)
    C.window(v, WIN_M, L - 2 * WIN_M, SILL, HEAD, lites=3, trim=False)
    C.tub_filler_wall(v, L / 2, 30); C.freestanding_tub(v, TUB_CL, TUB_L, 22, filler=None)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, WIN_M, L - WIN_M, L]))
    dimh(v, 0, L, v.Y(0) + 31, E.snap_points([0, TUB_CL, L - TUB_CL, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 22, 30, SILL, HEAD, H]))
    return ['WT-02 SLAB, 48" PANEL CENTERED. WINDOW 5\'-0" x 4\'-0", 4\'-0" SILL, TEMPERED.',
            '58" FREESTANDING TUB, CENTERED. WALL FILLER CL 2\'-6" WITH HAND SHOWER.']

def tub_side(v, which):
    """Alcove side walls. West: back wall at the left. East: back wall at the right. 24 in. towel bar at the room end."""
    L = ALC_D
    shell(v, L, cut_right=(which == 'E'), cut_left=(which == 'W'))
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    if which == 'W':
        C.freestanding_tub(v, 0.5, 32.9, 22, filler=None); C.towel_bar(v, L - 22, 48, 24)
        pts = [0, 32.9, L - 34, L - 10, L]
    else:
        C.freestanding_tub(v, L - 33.4, 32.9, 22, filler=None); C.towel_bar(v, 22, 48, 24)
        pts = [0, 10, 34, L - 32.9, L]
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points(pts))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 22, 48, H]))
    side = 'WEST' if which == 'W' else 'EAST'
    return ['WT-02 SLAB FLOOR TO CEILING.', '24" TOWEL BAR CL 4\'-0" AT THE ROOM END.']

# ================================================================== water closet (ID-733), PT-02, crown, base
def wc_south(v):
    L = WC_IN[1] - WC_IN[0]
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    tx = WC_IN[1] - TOILET_X[1]; C.toilet(v, tx, TOILET_X[1] - TOILET_X[0])   # looking south from the water closet's own east face
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, tx + (TOILET_X[1] - TOILET_X[0]) / 2, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 31.5, H - TRIM['crown'], H]))
    return ['TOILET CENTERED ON THE WALL. PT-02, CM-01.']

def wc_east(v):
    """Looking east inside the water closet: door wall at the left, toilet in profile at the right."""
    L = ALC_D
    shell(v, L, crown=[(0, L)], base=[(0, L)], cut_left=True)
    C.toilet_profile(v, L, facing='L', length=28.7)
    C.paper_holder(v, L - 28.7 - 8, 26)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, L - 28.7 - 8, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 26, H - TRIM['crown'], H]))
    return ['PAPER HOLDER CL 2\'-2", 8" AHEAD OF THE BOWL.', 'PT-02, CM-01.']

def wc_north(v):
    """Inside the water closet looking north: the door wall, hinge at the east jamb (right)."""
    L = WC_IN[1] - WC_IN[0]
    door_x = WC_D[0] - WC_IN[0]
    shell(v, L, crown=[(0, L)], base=[(0, door_x - CS)])
    C.casing(v, door_x, WC_DOOR, HEAD); leaf(v, door_x, WC_DOOR, HEAD, 2, 'R', toward=True)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, door_x, door_x + WC_DOOR, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, HEAD, H - TRIM['crown'], H]))
    return ['2\'-6" TWO-PANEL DOOR, CENTERED, PRIVACY SET, SWINGS IN,', 'HINGE-PIN STOP AT 90 DEGREES. PT-02, CM-01.']

def wc_west(v):
    """Inside the water closet looking west: the partition to the tub alcove, door wall at the right."""
    L = ALC_D
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    C.toilet_profile(v, 0, facing='R', length=28.7)
    C.switch(v, L - 4.0, 48.0, 'S/F')                                      # light and fan, at the latch side of the door (west jamb)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, 28.7, L - 4.0, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 48.0, H - TRIM['crown'], H]))
    return ['LIGHT AND FAN SWITCHES (2-GANG) CL 4\'-0"', 'AT THE LATCH SIDE. PT-02, CM-01.']

# ================================================================== key plan (ID-730)
KP_CONTENT = (12.0, 12.0, 1267.0, 1029.0)    # the drawn plan inside the clip at 1" (door swings and walls), measured from a render
def key_plan(sh):
    """Base plan clip of the master bathroom at 3/4 in. scale, centered, with every elevation marker and the towel hardware."""
    import compose_plans as CP
    src = fitz.open(CP.BASE_KEY); sp = src[1]
    clip_disp = fitz.Rect(78, 833, 318, 1030)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    k = 16.0 / 3                                                 # 3/16 -> 1" (the wide 11 x 17 sheet, owner 11.07.26)
    tw, th = clip_disp.width * k, clip_disp.height * k
    ax0, ay0, ax1, ay1 = FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6
    tx = FR.x0 + 24 - KP_CONTENT[0]                                        # the plan at the left, the notes in the column to its right
    gh = (KP_CONTENT[3] - KP_CONTENT[1]) + 24 + 4 + 14                      # plan, gap, scale bar, its foot numbers
    ty = FR.y0 + 24 + max(0.0, ((FR.y1 - 36) - (FR.y0 + 24) - gh) / 2) - KP_CONTENT[1]
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    sh.p.show_pdf_page(target, src, 1, clip=u, rotate=90)
    xref = sh.p.get_contents()[0]; st = sh.p.parent.xref_stream(xref).decode('latin1')
    parts = st.split('q ')
    for i in range(1, len(parts)):
        if 'Do' in parts[i]: parts[i] = f'{target.x0:.2f} {sh.p.rect.height - target.y1:.2f} {target.width:.2f} {target.height:.2f} re W n ' + parts[i]
    sh.p.parent.update_stream(xref, 'q '.join(parts).encode('latin1'))
    sys.path.insert(0, '/home/claude/flrwork/rev1'); import keyclip as KC
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(2, ['MASTER BATH', 'MASTER SHOWER', 'WATER CLOSET'])), 'key plan clip'
    PT_IN = 180 / 160 * k
    import base_rev1 as BR
    _o = BR.transform(2)(446.2, 1080.0)
    def P(x_in, y_in): return (target.x0 + (_o[0] - clip_disp.x0) * k + x_in * PT_IN, target.y0 + (_o[1] - clip_disp.y0) * k + y_in * PT_IN)
    # cover the base plan's room label and write our own
    a, b = P(40, 28), P(124, 60); sh.rect((a[0], a[1], b[0], b[1]), width=0, color=WHITE, fill=WHITE)
    lx, ly = P(80, 44); sh.text(lx, ly, 'MASTER BATH', 13.0, INK, align='c')
    # ---- this design drawn over FOR's base (FOR's elements masked where ours replace them)
    WG = (0.353, 0.353, 0.353)
    def R_(x0, y0, x1, y1, fill=WHITE, w=0, c=WHITE, dashes=None):
        p0, p1 = P(min(x0, x1), min(y0, y1)), P(max(x0, x1), max(y0, y1)); sh.rect((p0[0], p0[1], p1[0], p1[1]), width=w, color=c, fill=fill, dashes=dashes)
    def L_(a, b, w=0.6, c=INK, dashes=None): sh.line(P(*a), P(*b), w, c, dashes=dashes)
    def arc(cx, cy, r, a0, a1, w=0.4):
        import math
        pts = [fitz.Point(*P(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t)))) for t in range(int(a0), int(a1) + 1, 3)]
        s_ = sh.p.new_shape(); s_.draw_polyline(pts); s_.finish(color=INK, width=w, closePath=False); s_.commit()
    # vanities: FOR's two 4'-7" built-ins out, our two 51" furniture pieces centered, basin and wall faucet
    R_(0.3, 0.25, WIC_X - 0.3, 21.5); R_(WIC_X + WIC_W + 0.3, 0.25, ROOM_W - 0.3, 21.5)
    for x, w in (VAN_L, VAN_R):
        R_(x, 0.0, x + w, 20.1, fill=WHITE, w=0.8, c=INK)
        cx_ = x + w / 2; R_(cx_ - 8.5, 4.5, cx_ + 8.5, 16.0, fill=WHITE, w=0.5, c=INK); L_((cx_, 0.0), (cx_, 5.5), 0.8)
        L_((cx_ - TBAR_W / 2, 21.0), (cx_ + TBAR_W / 2, 21.0), 1.6)                  # towel bar on the apron
    # W.I.C.: FOR's pocket leaf out of the wall, a pair of 1'-6" doors swinging into the closet
    R_(41.0, -9.6, WIC_X, -6.9, fill=WG, c=WG); R_(WIC_X, -9.6, WIC_X + WIC_W, -6.9)
    for hx, a0, a1 in ((WIC_X, 270, 360), (WIC_X + WIC_W, 180, 270)):
        L_((hx, -0.2), (hx, -0.2 - WIC_W / 2), 0.8); arc(hx, -0.2, WIC_W / 2, a0, a1)
    # water closet: FOR's door, leaf and toilet out; the opening moved to center the 2'-6" door, hinged east, swinging in; toilet centered
    R_(121.0, FRONT_Y0 - 0.05, 158.6, FRONT_Y1 + 0.05, fill=WG, c=WG); R_(121.0, FRONT_Y0 - 0.6, 158.6, FRONT_Y0 - 0.05); R_(WC_IN[0] + 0.3, FRONT_Y1 + 0.05, WC_IN[1] - 0.3, FRONT_Y1 + 0.6)
    R_(WC_D[0] - 1.88, FRONT_Y0 - 0.45, WC_D[1] + 1.88, FRONT_Y1 + 0.45)
    for j0, j1 in ((WC_D[0] - 1.88, WC_D[0]), (WC_D[1], WC_D[1] + 1.88)): R_(j0, FRONT_Y0, j1, FRONT_Y1, fill=WHITE, w=0.5, c=INK)
    R_(WC_IN[0] + 0.3, FRONT_Y1 + 0.3, WC_IN[1] - 0.3, ROOM_D - 0.3)
    L_((WC_D[1], FRONT_Y1), (WC_D[1], FRONT_Y1 + WC_DOOR), 0.8); arc(WC_D[1], FRONT_Y1, WC_DOOR, 90, 180)
    tw = 20.0; R_(WC_CTR - tw / 2, ROOM_D - 8.5, WC_CTR + tw / 2, ROOM_D - 0.5, fill=WHITE, w=0.6, c=INK)    # tank
    import math
    pts = [fitz.Point(*P(WC_CTR + 7.3 * math.cos(math.radians(t)), ROOM_D - 8.5 - 10.3 + 10.3 * math.sin(math.radians(t)))) for t in range(0, 361, 10)]
    s_ = sh.p.new_shape(); s_.draw_polyline(pts); s_.finish(color=INK, width=0.6, fill=WHITE, closePath=True); s_.commit()
    # shower: FOR's X to a center drain, valve and front out; the 1/2" glass front, 28" door hung on the pier, the fixed panel,
    # the valve 1'-3" from the glass, a linear drain at the back wall, FOR's 15" corner seat
    R_(0.3, FRONT_Y1 + 0.3, SH_IN[1] - 0.3, ROOM_D - 0.3)
    R_(SH_IN[1] - 0.5, FRONT_Y1 + 20.0, SH_IN[1] - 0.05, FRONT_Y1 + 37.0)                       # FOR's valve trim off the partition face
    R_(-0.05, FRONT_Y0 - 0.05, STUB_SH[1], FRONT_Y1 + 0.05, fill=WG, c=WG)
    R_(STUB_SH[1], FRONT_Y0 - 0.45, PIER_SH[0], FRONT_Y1 + 0.45)
    gy = (FRONT_Y0 + FRONT_Y1) / 2; fx = PIER_SH[0] - SH_DOOR
    L_((STUB_SH[1], gy), (fx, gy), 1.6); L_((fx, gy), (PIER_SH[0], gy), 0.5, MID)
    L_((PIER_SH[0], gy), (PIER_SH[0], gy - SH_DOOR), 1.2); arc(PIER_SH[0], gy, SH_DOOR, 180, 270)
    sx_ = SH_IN[1]; vy = FRONT_Y1 + VALVE_IN
    R_(sx_ - 1.2, vy - 3.0, sx_, vy + 3.0, fill=WHITE, w=0.6, c=INK); L_((sx_ - 1.2, vy), (sx_ - 3.0, vy), 0.8)
    R_(2.0, ROOM_D - 4.0, SH_IN[1] - SEAT - 1.0, ROOM_D - 2.0, fill=WHITE, w=0.5, c=INK)          # linear drain
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(*P(SH_IN[1], ROOM_D - SEAT)), fitz.Point(*P(SH_IN[1], ROOM_D)), fitz.Point(*P(SH_IN[1] - SEAT, ROOM_D))]); s_.finish(color=INK, width=0.6, fill=WHITE, closePath=True); s_.commit()
    # tub alcove: FOR's 60" tub out, the 58" freestanding tub centered, the wall-mounted filler at the back wall
    R_(TUB_WALL[0] + 0.3, FRONT_Y1 + 0.3, TUB_WALL[1] - 0.3, ROOM_D - 0.3)
    t0 = (TUB_WALL[0] + TUB_WALL[1]) / 2 - TUB_L / 2; ty0, ty1 = FY(1239.96), FY(1288.02)
    for inset, w_ in ((0.0, 0.9), (2.0, 0.4)):
        rr = fitz.Rect(*P(t0 + inset, ty0 + inset), *P(t0 + TUB_L - inset, ty1 - inset))
        s_ = sh.p.new_shape(); s_.draw_rect(rr, radius=0.45); s_.finish(color=INK, width=w_, fill=WHITE); s_.commit()
    fc = (TUB_WALL[0] + TUB_WALL[1]) / 2; R_(fc - 1.5, ROOM_D - 1.6, fc + 1.5, ROOM_D, fill=WHITE, w=0.6, c=INK); L_((fc, ROOM_D - 1.6), (fc, ROOM_D - 6.0), 0.8)
    # FOR's clipped ticks past the south wall at the southeast corner
    R_(96.0, ROOM_D + 8.6, ROOM_W + 20.0, ROOM_D + 22.0)
    R_(TUB_WALL[0] + 2.6, ROOM_D + 9.3, TUB_WALL[1] + 4, ROOM_D + 18.0)          # the terrace edge below the tub window: not this room
    # markers: (number, sheet, direction, plan x, plan y)
    marks = [(1, 'ID-731', 'N', 80, 58), (2, 'ID-731', 'E', 94, 70), (3, 'ID-731', 'S', 80, 82), (4, 'ID-731', 'W', 66, 70),
             (1, 'ID-732', 'W', 14, 110), (2, 'ID-732', 'S', 21.5, 120), (3, 'ID-732', 'E', 29, 110),
             (4, 'ID-732', 'W', 66, 97), (5, 'ID-732', 'S', 80, 97), (6, 'ID-732', 'E', 94, 97),
             (1, 'ID-733', 'N', 123.5, 104), (2, 'ID-733', 'E', 153, 122), (3, 'ID-733', 'S', 123.5, 133.5), (4, 'ID-733', 'W', 125, 121)]
    for n, sheet, d, x, y in marks:
        cx, cy = P(x, y); sh.elev_marker(cx, cy, n, sheet, d, r=24.0)
    g = INK
    def bar(x0, y0, x1, y1, label, side='R'):
        a, b = P(x0, y0), P(x1, y1); sh.line(a, b, 2.0, g)
        if side == 'R': sh.text(b[0] + 5, (a[1] + b[1]) / 2 + 2, label, 6.0, g)
        else: sh.text(b[0] - 5, (a[1] + b[1]) / 2 + 2, label, 6.0, g, align='r')   # into the alcove, clear of the water closet partition
    bar(49.5, FRONT_Y1 + 10, 49.5, FRONT_Y1 + 34, 'TB 24"')
    bar(110.6, FRONT_Y1 + 10, 110.6, FRONT_Y1 + 34, 'TB 24"', side='L')
    for x, y, lab in (((PIER_WC[0] + PIER_WC[1] - CS) / 2, FRONT_Y0 - 1.5, 'RH'),):
        px, py = P(x, y); sh.rect((px - 3, py - 3, px + 3, py + 3), width=0.6, color=g, fill=WHITE)
        if x > 100: sh.text(px - 6, py + 2.5, lab, 6.0, g, align='r')       # the east wall: label to the room side
        else: sh.text(px + 6, py + 2.5, lab, 6.0, g)
    # room labels, door tags, north arrow and scale bar
    for (x_, y_), t_ in (((21.5, 97.0), 'SHOWER'), ((80.0, 124.0), 'TUB'), ((155.0, 133.0), 'W.C.')):
        q_ = P(x_, y_); sh.text(q_[0], q_[1] + 3, t_, 9.0, INK, align='c', raw=True)
    from idd_sheet import _FR
    for (x_, y_), t_ in (((155.0, 50.0), '19'),):
        q_ = P(x_, y_); hw = _FR.text_length(t_, fontsize=8) / 2 + 4
        sh.rect((q_[0] - hw, q_[1] - 6.5, q_[0] + hw, q_[1] + 6.5), width=0.6, color=INK, fill=WHITE)
        sh.text(q_[0], q_[1] + 2.9, t_, 8, INK, align='c', raw=True)
    cx0, cy1 = target.x0 + KP_CONTENT[0], target.y0 + KP_CONTENT[3]          # the plan's left edge and bottom
    ft = PT_IN * 12; bx, by = FR.x0 + 36, cy1 + 24 + 4                         # scale bar 24 pt under the plan, 36 pt in from the frame
    for i in range(5): sh.rect((bx + i * ft, by - 4, bx + (i + 1) * ft, by), 0.4, INK, INK if i % 2 == 0 else WHITE)
    for i in range(6): sh.text(bx + i * ft, by + 10, "%d'" % i, 7.5, MID, align='c', raw=True)
    sh.text(bx + 5 * ft + 16, by + 1, '1" TO 1\'-0"', 9, INK, raw=True)
    assert by + 12 <= FR.y1 - 36, ('scale bar too close to the frame', by)
    na = (bx + 5 * ft + 130, by - 2)
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(*na), 13); s_.finish(color=INK, width=0.6, fill=WHITE); s_.commit()
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(na[0], na[1] - 13), fitz.Point(na[0] + 6, na[1] + 8), fitz.Point(na[0], na[1] + 3), fitz.Point(na[0] - 6, na[1] + 8), fitz.Point(na[0], na[1] - 13)])
    s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
    sh.text(na[0] + 20, na[1] + 3.5, 'N', 9, INK, raw=True)
    sh.text(na[0] + 52, by + 1, 'FLOOR 2 KEY PLAN, 1" TO 1\'-0"', 10.0, INK, bold=True, spacing=0.6, raw=True)   # caption on the line under the plan
    for g_ in sh.p.get_drawings():
        r_ = g_['rect']
        if any(it[0] == 'c' for it in g_['items']) and r_.x1 < P(0, 0)[0] and P(0, TER_Y0)[1] - 6 < r_.y0 and r_.y1 < P(0, TER_Y1)[1] + 6:
            s_ = sh.p.new_shape()
            for it in g_['items']:
                if it[0] == 'c': s_.draw_bezier(*it[1:5])
            s_.finish(color=INK, width=0.4, closePath=False); s_.commit()
    from idd_sheet import FREG as _F
    x = target.x0 + KP_CONTENT[2] + 44; xr = TB_X - 24
    BODY, HEAD, LH = 9.5, 10.5, 14.5                     # print about 6 and 7 pt
    lines = []                                           # (dx, text, size, bold, advance)
    def para(t, indent=0.0, num=None):
        words = t.split(); cur = ''; first = True
        for w_ in words:
            c_ = (cur + ' ' + w_).strip()
            if _F.text_length(c_, fontsize=BODY) > xr - x - indent and cur:
                lines.append((indent, cur, BODY, False, LH, num if first else None)); first = False; cur = w_
            else: cur = c_
        lines.append((indent, cur, BODY, False, LH, num if first else None))
    lines.append((0, 'LEGEND', HEAD, True, LH + 3, None))
    para('TB  TOWEL BAR'); para('RH  DOUBLE ROBE HOOK')
    lines.append((0, '', BODY, False, 18, None))
    lines.append((0, "CHANGES FROM FOR'S PLAN", HEAD, True, LH + 3, None))
    for i, ln in enumerate(('TWO 51" FURNITURE VANITIES, CENTERED.',
               'W.I.C.: PAIR OF 1\'-6" SWING DOORS.',
               'W.C. DOOR CENTERED ON THE W.C. WALL.',
               'SHOWER: 28" GLASS DOOR ON THE PIER, LINEAR DRAIN AT THE BACK WALL, HAND SHOWER.',
               'SHOWER VALVE %s FROM THE GLASS.' % E.ftin(VALVE_IN),
               '58" FREESTANDING TUB, WALL-MOUNTED FILLER.',
               'WT-02 SLAB FLOOR TO CEILING IN THE SHOWER AND TUB ALCOVE.')):
        para(ln, indent=16, num='%d.' % (i + 1)); lines.append((0, '', BODY, False, 4, None))
    colh = sum(l_[4] for l_ in lines)
    pt0, pb0 = target.y0 + KP_CONTENT[1], target.y0 + KP_CONTENT[3]          # the column centered on the plan
    y = (pt0 + pb0) / 2 - colh / 2 + 10
    for dx, t_, sz, bd, adv, num in lines:
        if num: sh.text(x, y, num, sz, MID)
        if t_: sh.text(x + dx, y, t_, sz, INK if bd else MID, bold=bd)
        y += adv
    assert y < FR.y1 - 24, ('key plan notes run off the sheet', y)

ROOM = ((1, 'NORTH ELEVATION - MASTER BATH', ROOM_W, north), (2, 'EAST ELEVATION - MASTER BATH', FRONT_Y0, east),
        (3, 'SOUTH ELEVATION - MASTER BATH', ROOM_W, south), (4, 'WEST ELEVATION - MASTER BATH', FRONT_Y0, west))
ALCOVES = ((1, 'SHOWER - WEST WALL', ALC_D + FRONT_Y1 - FRONT_Y0, shower_west), (2, 'SHOWER - SOUTH WALL', SH_IN[1], shower_south), (3, 'SHOWER - EAST WALL', ALC_D, shower_east),
           (4, 'TUB ALCOVE - WEST WALL', ALC_D, lambda v: tub_side(v, 'W')), (5, 'TUB ALCOVE - SOUTH WALL', TUB_WALL[1] - TUB_WALL[0], tub_south),
           (6, 'TUB ALCOVE - EAST WALL', ALC_D, lambda v: tub_side(v, 'E')))
WC = ((1, 'WATER CLOSET - NORTH WALL', WC_IN[1] - WC_IN[0], wc_north), (2, 'WATER CLOSET - EAST WALL', ALC_D, wc_east),
      (3, 'WATER CLOSET - SOUTH WALL', WC_IN[1] - WC_IN[0], wc_south), (4, 'WATER CLOSET - WEST WALL', ALC_D, wc_west))

ML, MR, TOP, MB = 42.0, 52.0, 24.0, 44.0     # room around an elevation: FIN. FLR. at the left, the height string at the right, title and notes, the length strings

NOTE_BLOCK = 36.0     # two note lines and the gap to the top of the elevation

def fit(cell, L, k):
    """Floor-line origin: the notes, the elevation and its strings centered as one group under the title bar; asserted to fit."""
    x0, y0, x1, y1 = cell; Wpt, Hpt = L * k, H * k
    assert Wpt + ML + MR <= x1 - x0 and Hpt + TOP + MB + 22 <= y1 - y0, ('elevation does not fit its cell', L, k)
    top = y0 + 16 + 6; g = NOTE_BLOCK + Hpt + MB
    gy0 = top + max(0.0, (y1 - top - g) / 2)
    return x0 + ML + (x1 - x0 - ML - MR - Wpt) / 2, gy0 + NOTE_BLOCK + Hpt

def cells_row(frame, lengths, k, y0=None, y1=None):
    """One row of cells, each as wide as its view needs plus an equal share of what is left, so every view has the same air."""
    fx0, fy0, fx1, fy1 = frame; y0 = fy0 if y0 is None else y0; y1 = fy1 if y1 is None else y1
    need = [L * k + ML + MR for L in lengths]; spare = (fx1 - fx0 - sum(need)) / len(need)
    assert spare >= 0, ('row does not fit', lengths, k)
    out = []; x = fx0
    for n_ in need: out.append((x, y0, x + n_ + spare, y1)); x += n_ + spare
    return out

def best_k(frame, rows):
    """The largest standard scale at which every row fits the frame (rows: lists of view lengths), one scale for the sheet."""
    fx0, fy0, fx1, fy1 = frame; rh = (fy1 - fy0) / len(rows)
    for name in ('1', '3/4', '1/2', '3/8'):
        k = E.SCALES[name]
        if all(sum(L * k + ML + MR for L in r) <= fx1 - fx0 for r in rows) and H * k + TOP + MB + 22 <= rh: return name, k
    raise ValueError('no scale fits')

SCALE_TXT = {'1': '1" TO 1\'-0"', '3/4': '3/4" TO 1\'-0"', '1/2': '1/2" TO 1\'-0"', '3/8': '3/8" TO 1\'-0"'}

def draw_views(sh, frame, views, rows, note_size=6.0):
    """views laid out in rows (a list of view counts per row) at the largest standard scale that fits; returns the scale name."""
    name, k = best_k(frame, [[v[2] for v in views[sum(rows[:i]):sum(rows[:i + 1])]] for i in range(len(rows))])
    fx0, fy0, fx1, fy1 = frame; rh = (fy1 - fy0) / len(rows); cells = []
    for i, n_ in enumerate(rows):
        vs = views[sum(rows[:i]):sum(rows[:i]) + n_]
        cells += cells_row(frame, [v[2] for v in vs], k, fy0 + i * rh, fy0 + (i + 1) * rh)
    for cell, (n, title, L, fn) in zip(cells, views):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: ' + SCALE_TXT[name])
        spec = {'room': 'MASTER BATH', 'view': title, 'length': L, 'ceiling': H}
        origin = fit(cell, L, k)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        notes = fn(v)
        v.text(v.X(getattr(v, 'x_left', 0)) - 6, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        from idd_sheet import FREG as _F
        assert len(notes) <= 2, (title, 'more than 2 note lines')
        ny = origin[1] - H * k - NOTE_BLOCK + 10 + (2 - len(notes)) * 10
        for ln in notes:
            assert _F.text_length(ln, fontsize=note_size) <= cell[2] - cell[0] - 16, (title, 'note too long', ln)
            sh.text(cell[2] - 8, ny, ln, note_size, MID, align='r'); ny += 10
    return name

REVS = (('0', '11.02.26', 'ISSUED FOR REVIEW'),)
def build():
    import idd_sheet, idd_std
    idd_sheet.EXTRA_REVS = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', '11.06.26', 'REDRAWN ON FOR REV 1')]   # runtime only, the module is untouched
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    doc = fitz.open()
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    s0 = Sheet(doc); s0.frame('MASTER BATH ELEVATIONS', 'KEY PLAN, SCALE: 1" TO 1\'-0"', ['MASTER BATH', 'ELEVATIONS KEY PLAN'], 'ID-730', revisions=REVS, legend_rule=False)
    key_plan(s0)
    # every view at the largest standard scale its sheet allows (the wide 11 x 17 sheet, owner 11.07.26); the title block carries the scale
    for title_, no_, views_, rows_ in ((['INTERIOR ELEVATIONS', 'MASTER BATH'], 'ID-731', (ROOM[0], ROOM[1], ROOM[2], ROOM[3]), [2, 2]),
                                       (['INTERIOR ELEVATIONS', 'MASTER BATH SHOWER & TUB'], 'ID-732', ALCOVES, [3, 3]),
                                       (['INTERIOR ELEVATIONS', 'MASTER BATH WATER CLOSET'], 'ID-733', WC, [4])):
        name_, _ = best_k(frame, [[v[2] for v in views_[sum(rows_[:i]):sum(rows_[:i + 1])]] for i in range(len(rows_))])
        s_ = Sheet(doc); s_.frame('MASTER BATH ELEVATIONS', 'SCALE: ' + SCALE_TXT[name_], title_, no_, revisions=REVS, legend_rule=False)
        draw_views(s_, frame, views_, rows_)
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
