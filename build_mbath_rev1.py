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
def leaf(v, x, w, head, panels, swing, toward, **kw):
    """Door leaf with the set's swing rule: solid swing marks toward the viewer, dashed away."""
    _SOLID[0] = toward
    try: C.door_leaf(v, x, w, head, panels=panels, swing=swing, **kw)
    finally: _SOLID[0] = False
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
def _muntins(v, x0, y0, x1, y1, cols=None, rows=None, bar=0.875):
    """Muntin grid with every bar drawn once as a pair of lines at one weight: verticals run through, horizontals stop at them."""
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
    c_, r_ = C.lite_grid(x1 - x0, y1 - y0)
    cols = c_ if cols is None else cols; rows = r_ if rows is None else rows
    xs = [x0 + (x1 - x0) * i / cols for i in range(1, cols)]; ys = [y0 + (y1 - y0) * j / rows for j in range(1, rows)]
    for my in ys: C._rect(v, x0, my - bar / 2, x1, my + bar / 2, 0.01, WHITE, fill=WHITE)
    for mx in xs: C._rect(v, mx - bar / 2, y0, mx + bar / 2, y1, 0.01, WHITE, fill=WHITE)
    for mx in xs:
        for e in (-bar / 2, bar / 2): C._line(v, (mx + e, y0), (mx + e, y1), C.FINE)
    stops = [x0] + [e for mx in xs for e in (mx - bar / 2, mx + bar / 2)] + [x1]
    for my in ys:
        for e in (-bar / 2, bar / 2):
            for a, b in zip(stops[0::2], stops[1::2]): C._line(v, (a, my + e), (b, my + e), C.FINE)
C.muntins = _muntins
from idd_std import INK, MID, LIGHT, TRIM

OUT = '/home/claude/flrwork/261105.HD102.MasterBathPilot.pdf'
H = 118.0                 # FOR A-206 9'-10" (A-400 reads 9'-11"; FOR to confirm), coordination 11.09.26
HEAD, SILL = 96.0, 48.0   # door and window heads, bath window sills, VERIFY
CS = TRIM['casing']
CTR, FAUCET, MIR_B, MIR_T, SCONCE = 34.0, 40.0, 44.0, HEAD + CS, 66.0   # mirror top on the top of the head casing
TILE = (48, 96)           # ST-04 master bath marble (the vanity top stone, owner 11.09.26; was WT-02 porcelain), 48 x 96 panels set vertical, seams as drawn
TUB_SILL = 6.0            # FOR window L (A-600, A-301): 5'-0" x 7'-6" fixed, head 8'-0", sill 0'-6", impact, tempered
SWIN_SILL = 70.0          # FOR window K (A-600): 3'-1" x 2'-2" fixed over the shower, head 8'-0", sill 5'-10"
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
TER_Y0, TER_Y1 = FY(1113.1), FY(1197.1)   # FOR's terrace door opening in the west wall (from the north face), 4'-8"
TER_W = 42.0                              # owner 11.09.26 (second pass): the pair narrowed to 3'-6" (two 1'-9" leaves)
TER_C = FRONT_Y0 - (FRONT_Y1 - 20.1) / 2  # centered on the clear wall between the shower front wall stub and the vanity end, equal clear each side.
                                          # Not on the full wall face: equal 1'-6-1/2" piers would put the north jamb 1-1/2" behind the 20.1"-deep vanity end
TER_N, TER_S = TER_C - TER_W / 2, TER_C + TER_W / 2   # new north and south jambs (from the north face), 26-3/8" and 68-3/8"
SHD_W = WC_DOOR                           # owner 11.09.26: shower door opening the same as the water closet door's, 2'-6" x 8'-0", cased the same
SHD = (round(((SH_IN[0] + SH_IN[1]) / 2 - SHD_W / 2) * 8) / 8, round(((SH_IN[0] + SH_IN[1]) / 2 + SHD_W / 2) * 8) / 8)   # centered on the shower (plan x), 7" to 37"
SWIN_Y0, SWIN_Y1 = FY(1220.5), FY(1276.0) # shower window in the west wall (from the north face), 3'-1"
TOILET_W = FX(665.4) - FX(643.4)          # 14-5/8" toilet, tank against the south wall, centered on the water closet
TOILET_X = (WC_CTR - TOILET_W / 2, WC_CTR + TOILET_W / 2)
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
def tub_w(v, x, w, h=22):
    """The freestanding tub, filled white so the window (to 0'-6" AFF per FOR) and the slab joints behind it stop at its silhouette."""
    body = [(x, h), (x + 0.4, h - 6), (x + 1.4, h - 12), (x + 3.2, 5), (x + 5.5, 1.8), (x + 9, 0.8), (x + w - 9, 0.8), (x + w - 5.5, 1.8), (x + w - 3.2, 5), (x + w - 1.4, h - 12), (x + w - 0.4, h - 6), (x + w, h)]
    C._poly(v, [(x - 0.6, h)] + body + [(x + w + 0.6, h)], 0.1, WHITE, fill=WHITE)   # the body closed by its rim: the tub itself
    C.freestanding_tub(v, x, w, h, filler=None)
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
    """ST-04 48 x 96 slab: vertical seams where given, the horizontal seam at 8'-0"."""
    for xs in seams: C._line(v, (xs, h0), (xs, h1), C.FINE, C.TILE)
    if h0 < course < h1: C._line(v, (x0, course), (x1, course), C.FINE, C.TILE)
def glass_door(v, x, w, h, hinge='L'):
    """Owner 11.09.26: the shower door is one panel of hammered glass, no frame and no muntins: 1/2" tempered, two wall-mount glass
    hinges on the pier side, a 12" pull at the latch side, solid swing marks (it swings out, toward the viewer)."""
    C._rect(v, x + 0.25, 0.5, x + w - 0.25, h - 0.5, C.OUTLINE)
    C.hammered(v, x + 1.0, 1.2, x + w - 1.0, h - 1.2)
    hx, lx = (x + 0.25, x + w - 0.25) if hinge == 'L' else (x + w - 0.25, x + 0.25)
    C._line(v, (lx, 0.5), (hx, h / 2), C.FINE, MID); C._line(v, (lx, h - 0.5), (hx, h / 2), C.FINE, MID)
    for hy in (12, h - 12): C._rect(v, hx - 1.5, hy - 1.8, hx + 1.5, hy + 1.8, C.MED, fill=WHITE)
    px = lx - 3.0 if hinge == 'L' else lx + 1.8
    C._rect(v, px, 36, px + 1.2, 48, C.OUTLINE, fill=WHITE)
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
    C.arched_door_pair(v, WIC_X, WIC_W, HEAD - WIC_W / 2, panels=1, hw='pull')             # owner 11.09.26 PM: arched, apex at the 8'-0" head line
    C.rev_cloud(v, WIC_X - CS, 3.0, WIC_X + WIC_W + CS, HEAD + CS, pad=1.0)          # Harmon hinges (owner 11.09.26)
    from idd_sheet import _FR as _F
    tx_, ty_ = WIC_X + WIC_W / 2, HEAD + CS + 5.0; hw_ = (_F.text_length('19A', fontsize=7.0) / 2 + 3.0) / v.k; hh_ = 5.5 / v.k
    C._rect(v, tx_ - hw_, ty_ - hh_, tx_ + hw_, ty_ + hh_, 0.6, INK, fill=WHITE)      # door 19A (the door schedule, ID-002)
    v.text(v.X(tx_), v.Y(ty_) + 2.5, '19A', 7.0, INK, align='c')
    for (x, w), side in ((VAN_L, -1), (VAN_R, 1)):
        C.vanity_furniture(v, x, w, h=CTR, legs=True, drawers=3, faucet_style='wall')
        mx = x + w / 2; mw = MIR_W
        C.mirror_framed(v, mx - mw / 2, mw, MIR_B, MIR_T - MIR_B)
        for s in (mx - mw / 2 - SC_OFF, mx + mw / 2 + SC_OFF): C.sconce(v, s, SCONCE, 'cylinder')
        C.outlet(v, mx + side * GFCI_OFF, GFCI_CL, 'GFCI')                     # outboard mirror margin, within 3' of the basin
        # owner 11.09.26 evening: no towel bar on the vanities
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, VAN_L[0], VAN_L[0] + VAN_W / 2, VAN_L[0] + VAN_W, WIC_X - CS, WIC_X + WIC_W + CS, VAN_R[0], VAN_R[0] + VAN_W / 2, VAN_R[0] + VAN_W, L]))
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TRIM['base'], CTR, FAUCET, MIR_B, SCONCE, HEAD - WIC_W / 2, HEAD, MIR_T, H - TRIM['crown'], H]))
    return ['51" PAINTED FURNITURE VANITIES, ST-04 TOPS, WALL FAUCETS CL 3\'-4". FRAMED MIRRORS 25" x 57", TOP AT 8\'-5". SCONCES CL 5\'-6".',
            'W.I.C.: DOOR 19A, PAIR OF 1\'-6" PAINTED DOORS ON HARMON HINGES UNDER A SEMICIRCULAR ARCH, SPRING 6\'-6", APEX 8\'-0"; MIRROR TOPS ON THE ARCH CASING. GFCI CL 3\'-6" AT EACH VANITY. PT-02, CM-01.']

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
    shd = (sx(SHD[1]), sx(SHD[0]))                                       # shower door opening, the pier (hinge) side at the left
    shell(v, L, crown=[(0, pier_wc[1]), (pier_sh[0], L)], base=[(0, wc_door[0]), (wc_door[1], pier_wc[1]), (pier_sh[0], shd[0] - CS)])
    # beyond, lightly: tub alcove back wall (FOR's window L to 0'-6" AFF, tub in front of it)
    keep = (C.INK, C.MID); C.INK = BEYOND; C.MID = BEYOND
    win = (tub[0] + WIN_M, tub[1] - WIN_M)
    C.window(v, win[0], win[1] - win[0], TUB_SILL, HEAD, lites=3, trim=False)
    tub_w(v, (tub[0] + tub[1]) / 2 - TUB_L / 2, TUB_L, 22)
    C.INK, C.MID = keep
    # the tub alcove opening: heavy jamb lines with a shadow on the recess side
    for (a, b), top in ((tub, H),):
        C._line(v, (a, 0), (a, top), C.HEAVY); C._line(v, (b, 0), (b, top), C.HEAVY)
        C._line(v, (a + 0.6, 0), (a + 0.6, top), C.FINE, LIGHT); C._line(v, (b - 0.6, 0), (b - 0.6, top), C.FINE, LIGHT)
    # shower (owner 11.09.26): the front is a painted wall like the water closet's, a cased 2'-6" x 8'-0" opening (the W.C. door's size and casing),
    # one panel of hammered glass, no frame and no muntins (owner 11.09.26), hinged on the pier side, swinging out to the room
    C.casing(v, shd[0], SHD_W, HEAD); glass_door(v, shd[0], SHD_W, HEAD, 'L')
    C.rev_cloud(v, tub[0] + 1, 3.0, L - 1, HEAD + CS + 2, pad=1.0, tag_at='tl')   # the tub window (sill per FOR) and the shower front, one cloud
    # water closet door in the front wall, hinged at the east jamb; robe hook on the pier
    C.casing(v, wc_door[0], WC_DOOR, HEAD); leaf(v, wc_door[0], WC_DOOR, HEAD, 2, 'L', toward=False)
    robe_hook(v, (pier_wc[0] + CS + pier_wc[1]) / 2, 68)                          # centered on the pier clear of the casing
    finish_tag(v, (tub[0] + tub[1]) / 2, 108, 'TUB ALCOVE BEYOND, SEE ID-732')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, wc_door[0], wc_door[1], pier_wc[1], tub[1], shd[0], shd[1], L]))
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TUB_SILL, HEAD, H - TRIM['crown'], H]))
    return ['W.C. DOOR 2\'-6", SEE ID-733. TUB ALCOVE ST-04, WINDOW L SILL 0\'-6" PER FOR, SEE ID-732. ROBE HOOK CL 5\'-8".',
            'SHOWER: 2\'-6" x 8\'-0" ONE PANEL OF 1/2" HAMMERED TEMPERED GLASS, NO FRAME, NO MUNTINS, GLASS HINGES ON THE PIER SIDE, CASED AS THE W.C. DOOR, SWINGS OUT. PAINTED WALL.']

def west(v):
    """West wall from the shower stub to the north corner; the shower side wall is drawn with the shower on ID-732."""
    L = FRONT_Y0
    stub = (0.0, FRONT_Y1 - FRONT_Y0)                    # 0 to 4.8, 3.9 in. proud
    door = (FRONT_Y0 - TER_S, FRONT_Y0 - TER_N)         # 10-3/4" to 52-3/4": 3'-6", centered between the stub and the vanity end (owner 11.09.26)
    shell(v, L, crown=[(0, L)], base=[(door[1] + CS, L)])
    w_ = door[1] - door[0]; C.casing(v, door[0], w_, HEAD)                       # cased both sides now: 1-1/4" to the stub and to the vanity end
    for x_, sw_ in ((door[0], 'L'), (door[0] + w_ / 2, 'R')): leaf(v, x_, w_ / 2, HEAD, 'glass', sw_, toward=False)   # divided lites per the set rule
    tx_ = door[0] + w_ * 0.75 + 2.0; tw_ = v.F.text_length('TEMPERED', fontsize=5.2) / v.k
    C._rect(v, tx_ - tw_ / 2 - 0.6, 1.4, tx_ + tw_ / 2 + 0.6, 5.4, 0.01, WHITE, fill=WHITE)
    finish_tag(v, tx_, 2.2, 'TEMPERED')               # on the south leaf's bottom rail, clear of the swing lines
    C.rev_cloud(v, door[0] + 2.25, 7.0, door[1] + CS + 2.7, HEAD + CS + 5.5, pad=0.0)          # in the stile, the bottom rail, past the casing and under the crown: no line ridden
    C._rect(v, L - 20.1, 0, L, CTR, C.FINE, WHITE, fill=WHITE)              # the north casing and the base break behind the vanity
    C.vanity_end(v, L, depth=20.1, h=CTR, open_to='L')
    dimh(v, 0, L, v.Y(0) + 14, [0, stub[1], door[0], door[1], L - 20.1, L])        # equal clear to the stub and to the vanity end
    dimh(v, 0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, CTR, HEAD, H - TRIM['crown'], H]))
    return ['FOR\'S DOOR 10: PAIR OF 1\'-9" FULL-LITE DOORS (3\'-6", FOR 4\'-4"), DIVIDED LITES, 8\'-0" HEAD, TEMPERED IMPACT.',
            'CENTERED BETWEEN THE SHOWER FRONT WALL AND THE VANITY END, 6-1/4" CLEAR EACH SIDE, CASED BOTH SIDES. PT-02, CM-01. SHOWER SIDE WALL, SEE ID-732.']

# ================================================================== shower (ID-732), all faces WT-02 floor to ceiling
def shower_west(v):
    """Shower side wall with the window, looking west: back wall at the left, glass line at the right."""
    L = ALC_D                                                          # the front is a wall now (owner 11.09.26): cut at the right
    win = (wx(SWIN_Y1), wx(SWIN_Y0))
    shell(v, L)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.window(v, win[0], win[1] - win[0], SWIN_SILL, HEAD, lites=2, trim=False)
    C.rev_cloud(v, 1.5, 3.5, L - 1.5, H - 1.5, pad=0.5, tag_at='tl')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, win[0], win[1], L], tol=0.3))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SWIN_SILL, HEAD, H]))
    return ['ST-04 MARBLE SLAB 48" x 96", FLOOR TO CEILING, SEAMS AS DRAWN.',
            'FOR\'S WINDOW K, 3\'-1" x 2\'-2", SILL 5\'-10", HEAD 8\'-0", IMPACT, TEMPERED, DIVIDED LITES. SLAB SILL, SLOPED.']

def shower_south(v):
    L = SH_IN[1] - SH_IN[0]
    shell(v, L)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.niche(v, L / 2 - 12, 24, 58, 12, shelves=0)
    seat_front(v, 0, SEAT)                                             # the SE corner is at the left looking south
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, SEAT, L / 2 - 12, L / 2 + 12, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SEAT_H, 58, 70, H]))
    C.rev_cloud(v, 1.5, 3.5, L - 1.5, H - 1.5, pad=0.5, tag_at='tl')
    return ['ST-04 MARBLE SLAB, SEAM AT 8\'-0". NICHE 24" x 12" x 3-1/2", SILL AT 4\'-10".',
            'CORNER SEAT, 15" LEGS, SLAB TOP AT 1\'-5". LINEAR DRAIN AT THIS WALL.']

def shower_east(v):
    """The partition to the tub alcove, looking east: glass line at the left, back wall at the right."""
    L = ALC_D                                                          # the front is a wall now (owner 11.09.26): cut at the left
    shell(v, L)
    slab(v, 0, L, [SEAM_SH])
    C.valve(v, VALVE_IN, 48)
    ceiling_head(v, L / 2)
    slide_bar(v, VALVE_IN + 7.0)
    seat_side(v, L, 'L')
    C.rev_cloud(v, 1.5, 3.5, L - 1.5, H - 1.5, pad=0.5, tag_at='tl')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, VALVE_IN, VALVE_IN + 7.0, L - SEAT, L], tol=0.3))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SEAT_H, 40, 48, 76, HEAD, H]))
    return ['VALVE CL 4\'-0", %s FROM THE FRONT WALL. HAND SHOWER ON A 36" SLIDE BAR.' % E.ftin(VALVE_IN),
            '12" CEILING RAIN HEAD. ST-04 MARBLE SLAB, SEAMS AT %s AND 8\'-0".' % E.ftin(SEAM_SH)]

# ================================================================== tub alcove (ID-732), WT-02 to 8'-0", PT-02 and crown above
def tub_south(v):
    L = TUB_WALL[1] - TUB_WALL[0]
    shell(v, L)
    slab(v, 0, L, [])                                                  # the window takes the wall: ST-04 at the margins, below the sill and over the head
    C.window(v, WIN_M, L - 2 * WIN_M, TUB_SILL, HEAD, lites=3, trim=False)
    tub_w(v, TUB_CL, TUB_L, 22)                # the filler moves to the east side wall (the back wall is glass)
    C.rev_cloud(v, 1.5, 3.5, L - 1.5, H - 1.5, pad=0.5, tag_at='tl')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, WIN_M, L - WIN_M, L]))
    dimh(v, 0, L, v.Y(0) + 31, E.snap_points([0, TUB_CL, L - TUB_CL, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TUB_SILL, 22, HEAD, H]))
    return ['ST-04 MARBLE. FOR\'S WINDOW L, 5\'-0" x 7\'-6", SILL 0\'-6", HEAD 8\'-0", IMPACT, TEMPERED, DIVIDED LITES.',
            '58" FREESTANDING TUB, CENTERED. FILLER ON THE EAST SIDE WALL, VIEW 6.']

def tub_side(v, which):
    """Alcove side walls. West: back wall at the left. East: back wall at the right. 24 in. towel bar at the room end."""
    L = ALC_D
    shell(v, L, cut_right=(which == 'E'), cut_left=(which == 'W'))
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    if which == 'W':
        tub_w(v, 0.5, 32.9, 22); C.towel_bar(v, L - 22, 48, 24)
        pts = [0, 32.9, L - 34, L - 10, L]
    else:
        tub_w(v, L - 33.4, 32.9, 22); C.towel_bar(v, 22, 48, 24)
        FCX = round((L - 33.4 / 2) * 8) / 8                         # wall filler and hand shower centered on the tub's depth (the back wall is the window)
        C.tub_filler_wall(v, FCX, 30)
        pts = [0, 10, 34, L - 32.9, L]
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points(pts))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 22, 30, 48, H] if which == 'E' else [0, 22, 48, H]))
    side = 'WEST' if which == 'W' else 'EAST'
    C.rev_cloud(v, 1.5, 3.5, L - 1.5, H - 1.5, pad=0.5, tag_at='tl')
    if which == 'E': return ['ST-04 MARBLE FLOOR TO CEILING. WALL FILLER CL 2\'-6", HAND SHOWER.', '24" TOWEL BAR CL 4\'-0" AT THE ROOM END.']
    return ['ST-04 MARBLE FLOOR TO CEILING.', '24" TOWEL BAR CL 4\'-0" AT THE ROOM END.']


# ---- wall-hung smart toilet (owner 11.09.26 coordination: wall-hung smart toilets on in-wall carriers, GFCI for the seat)
WH_PROJ = 21.5     # bowl projection from the finished wall
WH_TOP = 16.5      # seat top AFF (carrier set; 15" to 19" adjustable)
FP_B, FP_T = 40.75, 47.25   # flush plate, CL 3'-8" to match ID-502 detail 5
GF_OFF, GF_CL = 8.0, 13.0   # smart-seat GFCI 8" beside the bowl centerline, CL 1'-1" (ID-502: 6" to 8", 12" to 15" AFF)
def wh_front(v, x, w):
    """Wall-hung bowl seen from the front: lid and seat, bowl tapering to its underside, flush plate on the wall above, no tank."""
    cx = x + w / 2
    C._poly(v, [(x + 0.6, WH_TOP - 1.2), (x + w - 0.6, WH_TOP - 1.2), (x + w - 1.6, 10.5), (cx + 3.2, 8.2), (cx - 3.2, 8.2), (x + 1.6, 10.5)], C.OUTLINE, fill=WHITE)
    C._rect(v, x, WH_TOP - 1.2, x + w, WH_TOP, C.OUTLINE, fill=WHITE)                  # seat and lid edge
    C._rect(v, cx - 4.75, FP_B, cx + 4.75, FP_T, C.OUTLINE, fill=WHITE)                # flush plate CL 3'-8" (ID-502 detail 5), carrier behind
    C._line(v, (cx, FP_B + 0.6), (cx, FP_T - 0.6), C.FINE)
    C._line(v, (x + 2, 8.6), (x + w - 2, 8.6), C.FINE, LIGHT)                          # shadow line under the floating bowl
def wh_profile(v, wall_x, facing='L'):
    """Wall-hung bowl in profile from the wall at wall_x, projecting left ('L') or right ('R'); flush plate proud of the wall."""
    d = -1 if facing == 'L' else 1
    X = lambda t: wall_x + d * t
    pts = [(X(0), 9.0), (X(0), WH_TOP - 1.2), (X(WH_PROJ), WH_TOP - 1.2), (X(WH_PROJ - 0.5), 13.0), (X(WH_PROJ - 3.0), 10.2), (X(9.0), 8.6), (X(4.0), 8.6)]
    C._poly(v, pts, C.OUTLINE, fill=WHITE)
    C._rect(v, X(0), WH_TOP - 1.2, X(WH_PROJ + 0.3), WH_TOP, C.OUTLINE, fill=WHITE)      # seat and lid
    C._rect(v, X(0), FP_B, X(0.75), FP_T, C.OUTLINE, fill=WHITE)                        # flush plate

# ================================================================== water closet (ID-733), PT-02, crown, base
def wc_south(v):
    L = WC_IN[1] - WC_IN[0]
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    tx = WC_IN[1] - TOILET_X[1]; tcx = tx + (TOILET_X[1] - TOILET_X[0]) / 2   # looking south from the water closet's own east face
    C.outlet(v, tcx - GF_OFF, GF_CL)                                           # smart seat power beside the bowl, partly behind it (FOR's GFI on this wall)
    wh_front(v, tx, TOILET_X[1] - TOILET_X[0])
    v.text(v.X(tcx - GF_OFF - 4.5), v.Y(GF_CL), 'GFCI', 5.0, align='r')
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, tcx - GF_OFF, tcx, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, GF_CL, WH_TOP, FP_B + 3.25, H - TRIM['crown'], H]))
    return ['WALL-HUNG SMART TOILET ON A CARRIER, FLUSH PLATE CL 3\'-8".', 'GFCI 8" BESIDE THE BOWL CL, CL 1\'-1". PT-02, CM-01.']

def wc_east(v):
    """Looking east inside the water closet: door wall at the left, toilet in profile at the right."""
    L = ALC_D
    shell(v, L, crown=[(0, L)], base=[(0, L)], cut_left=True)
    wh_profile(v, L, facing='L')
    C.paper_holder(v, L - WH_PROJ - 8, 26)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, L - WH_PROJ - 8, L - WH_PROJ, L]))
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
    wh_profile(v, 0, facing='R')
    C.switch(v, L - 4.0, 48.0, 'S/F')                                      # light and fan, at the latch side of the door (west jamb)
    dimh(v, 0, L, v.Y(0) + 14, E.snap_points([0, WH_PROJ, L - 4.0, L]))
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
    R_(WC_CTR - 4.75, ROOM_D - 0.9, WC_CTR + 4.75, ROOM_D - 0.3, fill=WHITE, w=0.5, c=INK)    # flush plate on the carrier wall, no tank (wall-hung)
    import math
    pts = [fitz.Point(*P(WC_CTR + 7.3 * math.cos(math.radians(t)), ROOM_D - 1.0 + 20.5 * math.sin(math.radians(t)))) for t in range(180, 361, 10)]   # wall-hung bowl, 21-1/2" from the wall
    s_ = sh.p.new_shape(); s_.draw_polyline(pts); s_.finish(color=INK, width=0.6, fill=WHITE, closePath=True); s_.commit()
    # shower: FOR's X to a center drain, valve and front out; the 1/2" glass front, 28" door hung on the pier, the fixed panel,
    # the valve 1'-3" from the glass, a linear drain at the back wall, FOR's 15" corner seat
    R_(0.3, FRONT_Y1 + 0.3, SH_IN[1] - 0.3, ROOM_D - 0.3)
    R_(SH_IN[1] - 0.5, FRONT_Y1 + 20.0, SH_IN[1] - 0.05, FRONT_Y1 + 37.0)                       # FOR's valve trim off the partition face
    R_(-0.05, FRONT_Y0 - 0.05, STUB_SH[1], FRONT_Y1 + 0.05, fill=WG, c=WG)
    R_(STUB_SH[1], FRONT_Y0 - 0.45, PIER_SH[0], FRONT_Y1 + 0.45)
    # owner 11.09.26: the shower front is a wall with a cased 2'-6" opening (the W.C. door's size), a hammered-glass door hinged on the pier side, swinging out
    for j0, j1 in ((STUB_SH[1], SHD[0]), (SHD[1], PIER_SH[0])): R_(j0, FRONT_Y0, j1, FRONT_Y1, fill=WHITE, w=0.5, c=INK)
    L_((SHD[1], FRONT_Y0), (SHD[1], FRONT_Y0 - SHD_W), 1.2); arc(SHD[1], FRONT_Y0, SHD_W, 180, 270)
    L_((SHD[0], (FRONT_Y0 + FRONT_Y1) / 2), (SHD[1], (FRONT_Y0 + FRONT_Y1) / 2), 0.3, MID)                    # threshold line
    import idd_sheet as _IS
    def cloud(x0, y0, x1, y1, tag_at='tr'):
        a_, b_ = P(x0, y0), P(x1, y1); _IS.rev_cloud_pt(sh.p, fitz.Rect(min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1])), tag_at=tag_at)
    cloud(SHD[0] - 3.0, FRONT_Y0 - SHD_W - 4.0, SHD[1] + 5.0, FRONT_Y0 - 4.0)          # the swing, in open space off the wall and jamb lines
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
    fyc = (ty0 + ty1) / 2                                                     # owner 11.09.26: the back wall is window to 1'-0" AFF, so the filler is on the east side wall
    R_(TUB_WALL[1] - 1.6, fyc - 1.5, TUB_WALL[1], fyc + 1.5, fill=WHITE, w=0.6, c=INK); L_((TUB_WALL[1] - 1.6, fyc), (TUB_WALL[1] - 8.0, fyc), 0.8)
    cloud(TUB_WALL[1] - 10, fyc - 6, TUB_WALL[1] + 3.0, fyc + 6)                  # the filler and its box; the right edge in the poche, the wall face crossed square
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
    for (x_, y_), t_ in (((155.0, 50.0), '19'), ((WIC_X + WIC_W / 2, 14.0), '19A')):      # 19A: the W.I.C. pair (ID-002)
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
    # owner 11.09.26: terrace pair narrowed to 3'-6" (two 1'-9" leaves), centered on the wall inside: FOR's leaves out, both jambs infilled
    px0, py_ = P(0, TER_Y0 - 6)[0], P(0, TER_Y0 - 6)[1]                      # the west wall's exterior face, read off FOR's poche north of the opening
    xs_ = [g_['rect'].x0 for g_ in sh.p.get_drawings() if g_.get('fill') is not None and g_['rect'].x0 < px0 - 20 and abs(g_['rect'].x1 - px0) < 3
           and g_['rect'].y0 <= py_ <= g_['rect'].y1]
    WALL_X = round((px0 - max(xs_)) / PT_IN * 8) / 8 if xs_ else 10.0
    XE = -WALL_X                                                              # exterior face of the west wall
    R_(XE - 32.0, TER_Y0 - 3.0, XE - 0.05, TER_Y1 + 3.0)                      # FOR's open leaves and swings, outside the wall
    R_(XE, TER_Y0, 0.6, TER_Y1)                                               # the opening through the wall, FOR's inside-face tick with it
    R_(XE - 0.8, TER_Y0 - 4.0, 0.0, TER_N, fill=WG, c=WG)                     # new wall north of the opening, lapped over FOR's jamb so the poche reads as one
    R_(XE - 0.8, TER_S, 0.0, TER_Y1 + 6.0, fill=WG, c=WG)                     # new wall south of the opening, filled to FOR's poche
    for yh, a0, a1, d in ((TER_N, 90, 180, 1), (TER_S, 180, 270, -1)):
        L_((XE, yh), (XE - TER_W / 2, yh), 0.8); arc(XE, yh, TER_W / 2, a0, a1)
    L_((XE, TER_N), (XE, TER_S), 0.3, MID)                                    # threshold
    for j0, j1 in ((TER_N - 1.75, TER_N), (TER_S, TER_S + 1.75)): R_(XE, j0, 0.0, j1, fill=WHITE, w=0.5, c=INK)   # door frame jambs through the wall
    L_((XE, TER_N), (0.0, TER_N), 0.5); L_((XE, TER_S), (0.0, TER_S), 0.5)
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
    for i, ln in enumerate(('TWO 51" FURNITURE VANITIES, CENTERED, ST-04 TOPS.',
               'W.I.C.: DOOR 19A, PAIR OF 1\'-6" SWING DOORS ON HARMON HINGES, SEMICIRCULAR ARCHED HEAD (SPRING 6\'-6", APEX 8\'-0").',
               'W.C. DOOR CENTERED ON THE W.C. WALL.',
               'SHOWER: THE GLASS FRONT IS A PAINTED WALL WITH A CASED 2\'-6" x 8\'-0" OPENING (THE W.C. DOOR\'S SIZE AND CASING), ONE-PANEL HAMMERED-GLASS DOOR, NO FRAME, NO MUNTINS, SWINGS OUT. LINEAR DRAIN AT THE BACK WALL, HAND SHOWER.',
               'SHOWER VALVE %s FROM THE FRONT WALL (FOR: 2\'-9" FROM ITS GLASS), LINEAR DRAIN AT THE BACK WALL (FOR: CENTER DRAIN), CEILING RAIN HEAD: FOR / PLUMBER TO RELOCATE, SLAB RECESS AND SLEEVES BEFORE THE POUR.' % E.ftin(VALVE_IN),
               '58" FREESTANDING TUB. FILLER ON THE ALCOVE EAST WALL: THE BACK WALL IS WINDOW. FLOOR 2 IS A SLAB: EVERY MOVED DRAIN SLEEVED BEFORE THE POUR.',
               'TUB WINDOW L AS FOR SCHEDULES IT: 5\'-0" x 7\'-6", SILL 0\'-6". W.C. DOOR 2\'-6" (FOR 2\'-8") TO MATCH THE SHOWER OPENING. WALL-HUNG SMART TOILET ON A CARRIER, GFCI BEHIND.',
               'TERRACE PAIR, FOR\'S DOOR 10, NARROWED TO 3\'-6" (TWO 1\'-9" LEAVES; A-202 DRAWS 4\'-8", A-600 READS 4\'-4"), CENTERED BETWEEN THE SHOWER FRONT WALL AND THE VANITY END (6-1/4" CLEAR EACH SIDE), WALL INFILLED BOTH SIDES.',
               'ST-04 MARBLE (THE VANITY TOP STONE) FLOOR TO CEILING IN THE SHOWER AND TUB ALCOVE.',
               'FLOOR: WD-01 HERRINGBONE WITH A WD-02 BORDER, SEE ID-102. SHOWER FLOOR TL-03 PORCELAIN MOSAIC.',
               'DIVIDED LITES ON EVERY WINDOW AND THE TERRACE PAIR; THE SHOWER DOOR IS ONE PANEL OF HAMMERED GLASS.')):
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
ALCOVES = ((1, 'SHOWER - WEST WALL', ALC_D, shower_west), (2, 'SHOWER - SOUTH WALL', SH_IN[1], shower_south), (3, 'SHOWER - EAST WALL', ALC_D, shower_east),
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
        v.dim_v(0, H, v.X(L) + 30, [0, H])                                     # overall, finish floor to ceiling (review 11.09.26)
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
