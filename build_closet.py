"""Master closet (FOR's W.I.C., floor 2), the picked design (owner 11.09.26).
The owner picked a design from four reference renders (warm greige matte millwork with thin reveals, L-shaped open hanging in the corners
with LED under the shelf fronts and bronze rods, a center unit of textured drawer fronts with slim bronze bar pulls under lit glass shelves
on a linen back, a stone vanity top with upholstered poufs, a drawer island with a stone top), with his changes:
  1 doors on the upper cabinets (every upper over hanging and shelving, solid, greige; the LED at the shelf fronts below stays);
  2 upper cabinets over the vanity, vanity still 4'-0" (two seats, lit mirror between the uppers and the top);
  3 island drawers on the vanity (west) side, the other faces closed panels, stone top;
  4 north center: no countertop, drawers then the purse showcase straight to the ceiling (16 bags);
  5 doors on the dress hanging and the shoe area: bronze-framed clear glass, so the dresses and shoes stay on view.
Owner 11.09.26 PM: arched door 19A; south wall mirrors only; one-piece showcase shelves (no center upright); the chute lowered into a
cabinet under the 42" shelf with the upper hang and uppers over it; dresses south of the vanity, double hang north; island with waterfall
ends, two stacks of drawers (two over one deep).
Kept from the study: 16 bags, 36 pairs of shoes, the LAUNDRY CHUTE bay with its access door, FOR's 9'-6" ceiling, 3'-0" aisles, door 19 clear.
Room and chute: build_closet_study.py PLAN block (FOR A-202 / A-206 REV 1).
Output: 261109.HD102.MasterCloset.pdf, ID-330 key plan, ID-331 north and south, ID-332 east and west, ID-333 island and details."""
import sys, math, random
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen, _FR, _FB, take_scale
from idd_std import INK, MID, LIGHT
import build_closet_study as CS
from build_closet_study import W, D, H, DOOR_C, DOOR_W, CH_Y0, CH_Y1, CH_D, CROWN, L, R, P

OUT = '/home/claude/flrwork/261109.HD102.MasterCloset.pdf'
HEAVY, OUTLINE, MED, FINE = C.HEAVY, C.OUTLINE, C.MED, C.FINE
WHITE = (1, 1, 1); PALE = CS.PALE; GLOW = CS.GLOW; STONE = CS.STONE

# ---------------------------------------------------------------- the layout (inches; plan origin at the NW inside corner, x east, y south)
DN = 24.0            # north run depth (hanging corners, the showcase unit)
DW = 24.0            # west run depth (dress hanging, double hang)
DV = 22.0            # vanity depth
DE = 24.0            # east run depth (double hang, the chute, dresses, shoes)
DS = 14.0            # south wall shelving depth
TOP = H - CROWN      # 109.5: millwork tops, the crown above, soffit flush (1/ID-501 rule)
UP0 = 86.0           # upper cabinets: bottom shelf at 86" with LED at its front; solid doors 86" to 109-1/2"
ROD_HI, ROD_LO, ROD_LONG = 82.0, 41.0, 80.0
NA, NB = 48.0, W - 48.0                          # north wall: corner double hang 0..48, showcase 48..114.6, double hang 114.6..W
VY0, VY1 = (DN + D) / 2 - 24.0, (DN + D) / 2 + 24.0     # vanity 4'-0", centered on the open west wall (y 65.4 to 113.4)
VTOP = 30.0
SC_N, SC_ROWS = 2, 4                             # showcase: two bays, four rows, two bags a bay a row = 16
SC_TOP_DRW = 34.0                                # drawers 4" to 34", the showcase from 35" to the crown
SPRING = 78.0                                    # door 19A arched head (owner 11.09.26 PM): spring 6'-6", apex 8'-0" (the other heads)
CS19 = C.TRIM['casing']
MIR_TOP = SPRING + DOOR_W / 2 + CS19             # 8'-5": mirror tops on the arch casing apex, the line of the bath mirrors
# south wall: mirrors only, no millwork (owner 11.09.26 PM); each mirror from 2" off the run end panel to 2" off the casing
MIRR = ((DW + 2.0, DOOR_C - DOOR_W / 2 - CS19 - 2.0), (DOOR_C + DOOR_W / 2 + CS19 + 2.0, W - DE - 2.0))
ISL = (DOOR_C - 21.0, DN + 36.0, DOOR_C + 21.0, D - 33.0)   # island 3'-6" x 5'-1-3/4", 36" aisles, 33" to the south wall (door leaves)
EB = {'dbl': (DN, CH_Y0), 'chute': (CH_Y0, CH_Y1), 'dress': (CH_Y1, (CH_Y1 + D) / 2), 'shoes': ((CH_Y1 + D) / 2, D)}
CH_TOP = ROD_LO + 1.5                            # the chute cabinet stops under the lower shelf; upper hang and uppers run over it (owner)
# owner 11.09.26 PM: dresses on the left of the vanity (south, seen from the island), double hang on the right (north)
WB = {'dbl': (DN, VY0), 'vanity': (VY0, VY1), 'dress': (VY1, D)}

# ---------------------------------------------------------------- pieces in elevation
def toe(v, x0, x1): R(v, x0, 0, x1, 4.0, OUTLINE, fill=PALE)

def led(v, x0, x1, y): L(v, (x0 + 1.0, y - 0.6), (x1 - 1.0, y - 0.6), FINE, LIGHT, '[1.5 1] 0')

def texture(v, x0, y0, x1, y1, pitch=1.6):
    """MW-02 shagreen-look drawer front: a light field of small pebbles."""
    rnd = random.Random(int(x0 * 13 + y0 * 7)); y = y0 + pitch * 0.7; j = 0
    while y < y1 - pitch * 0.4:
        x = x0 + pitch * (0.5 if j % 2 else 1.0)
        while x < x1 - pitch * 0.4:
            C._ellipse(v, x + rnd.uniform(-0.2, 0.2), y, 0.32, 0.26, FINE, LIGHT); x += pitch
        y += pitch * 0.9; j += 1

def drawer_bank(v, x0, x1, y0, y1, n):
    """Inset drawers, MW-02 textured fronts, 1/8" reveals, a slim bronze bar pull centered on each."""
    R(v, x0, y0, x1, y1, OUTLINE)
    h_ = (y1 - y0) / n; g = 0.6
    for i in range(n):
        a = y0 + i * h_; R(v, x0 + g, a + g / 2, x1 - g, a + h_ - g / 2, FINE)
        texture(v, x0 + g + 0.8, a + 1.2, x1 - g - 0.8, a + h_ - 1.2)
        cx, cy = (x0 + x1) / 2, a + h_ * 0.62; pw = min(5.0, (x1 - x0) * 0.22)
        R(v, cx - pw, cy - 0.3, cx + pw, cy + 0.3, MED, fill=WHITE)

def slab_doors(v, x0, x1, y0, y1, n, pulls='low'):
    """Solid MW-01 slab doors with thin reveals and a slim vertical bronze pull at the meeting edges."""
    w = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * w, x0 + (i + 1) * w
        R(v, a, y0, b, y1, OUTLINE); R(v, a + 0.35, y0 + 0.35, b - 0.35, y1 - 0.35, FINE, LIGHT)
        px = b - 1.6 if i % 2 == 0 else a + 1.6
        py = y0 + 3.5 if pulls == 'low' else (y0 + y1) / 2
        R(v, px - 0.3, py, px + 0.3, py + 6.0, MED, fill=WHITE)

def glass_doors(v, x0, x1, y0, y1, n):
    """GL-01: narrow bronze frames, clear low-iron glass, a slim bronze pull at the meeting stiles."""
    w = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * w, x0 + (i + 1) * w
        R(v, a, y0, b, y1, OUTLINE); R(v, a + 1.0, y0 + 1.0, b - 1.0, y1 - 1.0, MED)
        L(v, (a + 2.5, y1 - 4), (a + (b - a) * 0.45, y1 - (y1 - y0) * 0.28), FINE, PALE)
        px = b - 0.5 if i % 2 == 0 else a + 0.5; cy = (y0 + y1) / 2
        R(v, px - 0.3, cy - 5, px + 0.3, cy + 5, MED, fill=WHITE)

def uppers(v, x0, x1, n=None):
    """Upper cabinet over a hanging or shelving bay: the shelf at 86" with LED at its front, solid doors to the crown."""
    n = n or max(1, round((x1 - x0) / 24.0))
    R(v, x0, UP0 - 1.0, x1, UP0, FINE, fill=WHITE); led(v, x0, x1, UP0 - 1.0)
    slab_doors(v, x0, x1, UP0, TOP, n)

def dbl_hang(v, x0, x1, seed=1):
    """Open double hang: rods at 82" and 41" (bronze), a shelf at 41-3/4", uppers above."""
    R(v, x0, 0, x1, TOP, OUTLINE)
    CS.hanging(v, x0 + 1, x1 - 1, ROD_HI, ROD_HI - 34, seed=seed); CS.hanging(v, x0 + 1, x1 - 1, ROD_LO, 6, seed=seed + 1)
    R(v, x0, ROD_HI + 1.5, x1, ROD_HI + 2.25, FINE, fill=WHITE)
    R(v, x0, ROD_LO + 1.5, x1, ROD_LO + 2.25, FINE, fill=WHITE); led(v, x0, x1, ROD_LO + 1.5)
    toe(v, x0, x1); uppers(v, x0, x1)

def dress_hang(v, x0, x1, seed=5):
    """Long hang for dresses behind GL-01 glass doors (owner 11.09.26), rod at 80", uppers above."""
    R(v, x0, 0, x1, TOP, OUTLINE)
    CS.hanging(v, x0 + 1.5, x1 - 1.5, ROD_LONG, 10, seed=seed)
    toe(v, x0, x1); glass_doors(v, x0, x1, 4.0, UP0 - 1.0, 2); uppers(v, x0, x1)

def end_run(v, x0, x1, label):
    CS.end_profile(v, x0, x1, top=H, label=label)

def crown(v, x0, x1): C.crown(v, x0, x1, H, drop=CROWN)

def tag(v, xi, yi, text, side, ylab, xr=None, size=6.5, xl=0.0):
    """A leader from a point on the view (inches) to a label in the margin: side 'l' (label right-aligned left of the view edge xl),
    'r' (label left-aligned at xr, past the dimensions) or 't' (label centered over the crown, ylab in inches above the floor)."""
    from idd_sheet import ps
    lines = text.split('\n'); lh = ps(size) * 1.2
    px, py = v.X(xi), v.Y(yi)
    if side == 't':
        qx, qy = px, v.Y(ylab)
        v.line((px, py), (qx, qy + 2), 0.35, INK)
        for i, t in enumerate(lines[::-1]): v.text(qx, qy - i * lh, t, size, INK, align='c')
    else:
        qy = v.Y(ylab)
        qx = v.X(xl) - 12 if side == 'l' else xr
        v.line((px, py), (qx, qy), 0.35, INK)
        y0 = qy + ps(size) * 0.35 - (len(lines) - 1) * lh / 2
        for i, t in enumerate(lines):
            if side == 'l': v.text(qx - 3, y0 + i * lh, t, size, INK, align='r')
            else: v.text(qx + 3, y0 + i * lh, t, size, INK)
    sh = v.p.new_shape(); sh.draw_circle(fitz.Point(px, py), 0.9); sh.finish(color=INK, fill=INK, width=0.2); sh.commit()

def overall(v, x_pt):
    """Floor to ceiling, outside the chain."""
    v.dim_v(0, H, x_pt, E.snap_points([0, H]))

# ---------------------------------------------------------------- 1 NORTH (from the bath through door 19; x 0 west to W east)
def north(v):
    end_run(v, 0, 0.01, None)
    crown(v, 0, W)
    dbl_hang(v, 0, NA, 11); dbl_hang(v, NB, W, 13)
    a, b = NA, NB; bw = (b - a) / SC_N
    R(v, a, 0, b, TOP, OUTLINE)
    toe(v, a, b)
    for i in range(SC_N): drawer_bank(v, a + i * bw, a + (i + 1) * bw, 4.0, SC_TOP_DRW, 4)
    R(v, a, SC_TOP_DRW, b, SC_TOP_DRW + 1.0, MED, fill=WHITE)                 # MW-01 drawer cap, no countertop (owner)
    y0 = SC_TOP_DRW + 1.0; rh = (TOP - y0) / SC_ROWS
    R(v, a + 0.75, y0, b - 0.75, TOP, FINE, fill=GLOW)                          # FB-01 linen back
    rnd = random.Random(7)
    x = a + 1.2
    while x < b - 1.0:                                                         # linen weave, light
        L(v, (x, y0 + 0.5), (x, TOP - 0.5), FINE, (0.9, 0.9, 0.88)); x += 2.2
    for j in range(SC_ROWS):
        ys = y0 + j * rh
        if j: R(v, a + 0.75, ys - 0.25, b - 0.75, ys + 0.25, FINE, fill=WHITE)   # GL-02 glass shelf
        led(v, a + 0.75, b - 0.75, ys + rh - (0.25 if j < SC_ROWS - 1 else 0))     # LED under the shelf above
        for k in range(4):                                                     # continuous shelf, no center upright (owner 11.09.26 PM)
                cx = a + (b - a) * (0.125 + 0.25 * k)
                CS.bag(v, cx, ys + 0.25, rnd.uniform(11.0, 13.5), min(rh - 4.5, rnd.uniform(10.0, 12.5)), rnd.randint(0, 5))
    L(v, (-2, 0), (W + 2, 0), HEAVY)
    return [0, NA, NB, W]

# ---------------------------------------------------------------- 2 SOUTH (door 19 wall, from the island; x 0 east to W west)
def south(v):
    crown(v, 0, W)
    end_run(v, 0, DE, 'EAST RUN'); end_run(v, W - DW, W, 'WEST RUN')
    for (p0, p1) in MIRR:                                                       # MR-01 flush mirrors, the only finish on this wall
        x0, x1 = W - p1, W - p0
        R(v, x0, 6.0, x1, MIR_TOP, OUTLINE, fill=PALE); R(v, x0 + 0.5, 6.5, x1 - 0.5, MIR_TOP - 0.5, FINE)
        L(v, (x0 + 3, MIR_TOP - 8), (x0 + (x1 - x0) * 0.55, MIR_TOP - 40), FINE, WHITE); L(v, (x0 + 7, MIR_TOP - 8), (x0 + (x1 - x0) * 0.7, MIR_TOP - 32), FINE, WHITE)
    dx = W - (DOOR_C + DOOR_W / 2)
    C.arched_door_pair(v, dx, DOOR_W, SPRING, panels=1, hw='pull')
    L(v, (-2, 0), (W + 2, 0), HEAVY)
    return [0, DE, W - MIRR[1][1], W - MIRR[1][0], W - (DOOR_C + DOOR_W / 2), W - (DOOR_C - DOOR_W / 2),
            W - MIRR[0][1], W - MIRR[0][0], W - DW, W]

# ---------------------------------------------------------------- 3 EAST (from the island; x 0 north to D south)
def east(v):
    crown(v, DN, D)
    end_run(v, 0, DN, 'NORTH RUN')
    R(v, D, 0, D + 6, H, HEAVY, fill=(0.3, 0.3, 0.3))
    c0, c1 = EB['chute']; a0 = EB['dbl'][0]
    # owner 11.09.26 PM: the chute drops into a low cabinet; the upper hang, its shelf and the uppers run across the bay and the chute
    R(v, a0, 0, c1, TOP, OUTLINE)
    CS.hanging(v, a0 + 1, c1 - 1, ROD_HI, ROD_HI - 34, seed=21); CS.hanging(v, a0 + 1, c0 - 1, ROD_LO, 6, seed=22)
    R(v, a0, ROD_HI + 1.5, c1, ROD_HI + 2.25, FINE, fill=WHITE)
    R(v, a0, CH_TOP, c1, CH_TOP + 0.75, FINE, fill=WHITE); led(v, a0, c1, CH_TOP)
    toe(v, a0, c1); uppers(v, a0, c1)
    L(v, (c0, 4.0), (c0, CH_TOP), MED)                                          # the chute cabinet side
    slab_doors(v, c0, c1, 4.0, CH_TOP, 1, pulls='mid')
    R(v, c0 + 2.6, 20.0, c1 - 2.6, 34.0, MED, d='[2 1.5] 0')                   # the intake behind the door
    d0, d1 = EB['dress']; dress_hang(v, d0, d1, seed=23)
    s0, s1 = EB['shoes']
    R(v, s0, 0, s1, TOP, OUTLINE)
    n = CS.shoe_tower(v, s0, s1, 'closed')
    glass_doors(v, s0, s1, 4.0, TOP, 2)
    L(v, (-2, 0), (D + 2, 0), HEAVY)
    return n, [0, DN, CH_Y0, CH_Y1, d1, D]

# ---------------------------------------------------------------- 4 WEST (the vanity, from the island; x 0 south to D north)
def west(v):
    crown(v, 0, D - DN)
    end_run(v, D - DN, D, 'NORTH RUN')
    R(v, -6, 0, 0, H, HEAVY, fill=(0.3, 0.3, 0.3))
    x_dbl = (D - WB['dbl'][1], D - WB['dbl'][0]); x_van = (D - VY1, D - VY0); x_dr = (D - WB['dress'][1], D - WB['dress'][0])
    dbl_hang(v, *x_dbl, seed=31)
    dress_hang(v, *x_dr, seed=33)
    a, b = x_van; cx = (a + b) / 2
    R(v, a, VTOP - 5.5, b, VTOP - 1.5, OUTLINE)
    for x0_, x1_ in ((a, cx), (cx, b)): drawer_bank(v, x0_, x1_, VTOP - 5.5, VTOP - 1.5, 1)
    R(v, a, 0, b, VTOP - 5.5, FINE, LIGHT, d='[2 1.5] 0')                       # one 48" knee space
    R(v, a, VTOP - 1.5, b, VTOP, OUTLINE, fill=STONE)                          # ST-06 top, held to the bay
    for c_ in (a + 12, b - 12): CS.stool(v, c_, seat=18.0, w=15.0, kind='drum')
    R(v, a + 4, 36.0, b - 4, 80.0, OUTLINE); R(v, a + 4.6, 36.6, b - 4.6, 79.4, FINE)   # LM1 lit mirror
    R(v, a + 3.4, 35.4, b - 3.4, 80.6, FINE, LIGHT, d='[1.5 1] 0')
    L(v, (a + 7, 74), (a + 18, 52), FINE, PALE)
    R(v, a, 0, b, TOP, FINE, None)
    uppers(v, a, b, 2)
    L(v, (-2, 0), (D + 2, 0), HEAVY)
    return [0, x_dr[1], x_van[1], x_dbl[1], D]

# ---------------------------------------------------------------- 5 to 8 the island faces (36" high, ST-06 top, 1" overhang)
ITOP = 36.0
WF = 1.5                     # ST-06 waterfall ends, 1-1/2", mitered to the top (owner 11.09.26 PM)
DRW_DEEP = 18.0              # the deep bottom drawer, 4" to 18"; two drawers above it to the sub-top at 33-3/4"
def veins(v, x0, y0, x1, y1, seed=3):
    rnd = random.Random(seed)
    for i in range(3):
        xa = x0 + (x1 - x0) * (0.2 + 0.3 * i) + rnd.uniform(-2, 2)
        pts = [(min(x1 - 0.5, max(x0 + 0.5, xa + (y1 - y) * 0.35 + rnd.uniform(-0.8, 0.8))), y) for y in (y1 - 0.3, (y0 + 2 * y1) / 3, (2 * y0 + y1) / 3, y0 + 0.3)]
        C._poly(v, pts, FINE, LIGHT, close=False)
def island_face(v, Lf, kind):
    """kind: 'drawers' (west, two stacks: two drawers over one deep drawer), 'panels' (east), 'end' (a waterfall end seen face-on)."""
    L(v, (-1, 0), (Lf + 1, 0), HEAVY)
    if kind == 'end':
        R(v, 0, 0, Lf, ITOP, OUTLINE, fill=STONE); L(v, (0.4, ITOP - 1.5), (Lf - 0.4, ITOP - 1.5), FINE, LIGHT)   # the miter seen as a line
        veins(v, 0, 0, Lf, ITOP, seed=int(Lf)); return
    toe(v, WF, Lf - WF)
    if kind == 'drawers':
        w = (Lf - 2 * WF) / 2
        for i in range(2):
            x0_ = WF + i * w
            drawer_bank(v, x0_, x0_ + w, 4.0, DRW_DEEP, 1)
            drawer_bank(v, x0_, x0_ + w, DRW_DEEP, ITOP - 2.25, 2)
    else:
        R(v, WF, 4.0, Lf - WF, ITOP - 1.5, OUTLINE)
        n = max(1, round((Lf - 2 * WF) / 21.0)); w = (Lf - 2 * WF) / n
        for i in range(n): R(v, WF + i * w + 0.35, 4.35, WF + (i + 1) * w - 0.35, ITOP - 1.85, FINE, LIGHT)
    R(v, 0, ITOP - 1.5, Lf, ITOP, OUTLINE, fill=STONE)
    for (a_, b_) in ((0, WF), (Lf - WF, Lf)):                                      # the waterfall legs, edge-on
        R(v, a_, 0, b_, ITOP, OUTLINE, fill=STONE)
    L(v, (0, ITOP), (WF, ITOP - 1.5), FINE, MID); L(v, (Lf, ITOP), (Lf - WF, ITOP - 1.5), FINE, MID)   # 45 degree miters

# ---------------------------------------------------------------- the plan (on the key plan sheet)
class PV(CS.PV):
    pass

def plan_overlay(sh, I, k):
    """Our millwork over FOR's base: runs, rods, glass doors, the chute, the vanity, the island, poufs, door 19, the chandelier."""
    def r(x0, y0, x1, y1, w=0.6, c=INK, fill=None, d=None):
        a, b = I(x0, y0), I(x1, y1); rr = fitz.Rect(a, b); rr.normalize()
        s = sh.p.new_shape(); s.draw_rect(rr); s.finish(color=c, width=w, fill=fill, dashes=d); s.commit()
    def ln(a, b, w=0.5, c=INK, d=None):
        s = sh.p.new_shape(); s.draw_line(fitz.Point(*I(*a)), fitz.Point(*I(*b))); s.finish(color=c, width=w, dashes=d); s.commit()
    def circ(cx, cy, rad, w=0.5, c=INK, d=None, fill=None):
        s = sh.p.new_shape(); s.draw_circle(fitz.Point(*I(cx, cy)), rad * k); s.finish(color=c, width=w, dashes=d, fill=fill); s.commit()
    def arc(cx, cy, rad, a0, a1, w=0.4):
        pts = [I(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), cy + rad * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
        s = sh.p.new_shape(); s.draw_polyline([fitz.Point(*q) for q in pts]); s.finish(color=INK, width=w, closePath=False); s.commit()
    F = (0.95, 0.95, 0.93)
    r(0, 0, W, DN, 0.7, fill=F); r(0, DN, DW, VY0, 0.7, fill=F); r(0, VY1, DW, D, 0.7, fill=F); r(0, VY0, DV, VY1, 0.7, fill=WHITE)
    r(W - DE, DN, W, D, 0.7, fill=F)
    for (p0, p1) in MIRR: r(p0, D - 0.75, p1, D, 0.9, fill=(0.75, 0.75, 0.75))
    # bay divisions
    for x in (NA, NB): ln((x, 0), (x, DN), 0.5)
    ln((W - DE, CH_Y0), (W, CH_Y0)); ln((W - DE, CH_Y1), (W, CH_Y1)); ln((W - DE, EB['shoes'][0]), (W, EB['shoes'][0]))
    ln((0, VY0), (DW, VY0)); ln((0, VY1), (DW, VY1))
    # rods (dashed) and glass door lines (front faces of the glass-door bays)
    D_ = '[3 2] 0'
    ln((2, DN / 2), (NA - 2, DN / 2), 0.4, MID, D_); ln((NB + 2, DN / 2), (W - 2, DN / 2), 0.4, MID, D_)
    ln((DW / 2, VY1 + 2), (DW / 2, D - 2), 0.4, MID, D_); ln((DW / 2, DN + 2), (DW / 2, VY0 - 2), 0.4, MID, D_)
    ln((W - DE / 2, DN + 2), (W - DE / 2, CH_Y0 - 2), 0.4, MID, D_); ln((W - DE / 2, EB['dress'][0] + 2), (W - DE / 2, EB['dress'][1] - 2), 0.4, MID, D_)
    for (y0, y1, x) in ((WB['dress'][0], WB['dress'][1], DW), (EB['dress'][0], EB['dress'][1], W - DE), (EB['shoes'][0], EB['shoes'][1], W - DE)):
        ln((x, y0 + 0.5), (x, y1 - 0.5), 1.4, (0.45, 0.35, 0.2))                 # GL-01 bronze-framed glass doors
    s0, s1 = EB['shoes']
    for f in (0.2, 0.4, 0.6, 0.8): ln((W - DE + 2, s0 + (s1 - s0) * f), (W - 2, s0 + (s1 - s0) * f), 0.3, MID)
    # the showcase: glass shelves shown dashed
    for y in (6, 12, 18): ln((NA + 1, y), (NB - 1, y), 0.3, MID, '[1.5 1.5] 0')
    # the chute shaft
    cx0 = W - CH_D; r(cx0, CH_Y0, W - 4.5, CH_Y1, 0.8, fill=WHITE); ln((cx0, CH_Y0), (W - 4.5, CH_Y1), 0.35); ln((cx0, CH_Y1), (W - 4.5, CH_Y0), 0.35)
    ln((W - DE / 2, CH_Y0 - 2), (W - DE / 2, CH_Y1 - 2), 0.4, MID, D_)                # the upper rod runs on over the chute cabinet
    # poufs and the island
    for c_ in (VY0 + 12, VY1 - 12): circ(DV + 9, c_, 7.5, 0.4, MID, '[2 1.5] 0')
    x0, y0, x1, y1 = ISL
    r(x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.9, fill=WHITE)                          # ST-06 top, 1" overhang on the long sides
    for (ya, yb) in ((y0 - 1, y0 - 1 + WF), (y1 + 1 - WF, y1 + 1)): r(x0 - 1, ya, x1 + 1, yb, 0.9, fill=(0.82, 0.82, 0.8))   # waterfall ends
    r(x0, y0 + 0.5, x1, y1 - 0.5, 0.4, MID, d='[2 1.5] 0')
    ln((x0, (y0 + y1) / 2), (x0 + 3, (y0 + y1) / 2), 0.4)                      # two drawer stacks, west face
    circ((x0 + x1) / 2, (y0 + y1) / 2, 14, 0.4, MID, '[2 1.5] 0')               # CH1 over the island
    # door 19, a pair swinging in
    for hx, sgn in ((DOOR_C - DOOR_W / 2, 1), (DOOR_C + DOOR_W / 2, -1)):
        ln((hx, D), (hx, D - DOOR_W / 2), 1.1)                                   # 1'-6" leaf, open
        arc(hx, D, DOOR_W / 2, 270, 360 if sgn > 0 else 180, 0.35)
    for yy in (D + 1.0, D + 4.5): ln((DOOR_C - DOOR_W / 2, yy), (DOOR_C + DOOR_W / 2, yy), 0.4, INK, '[3 2] 0')   # arched head above (dashed)

def key_sheet(doc):
    import compose_plans as CP, keyclip as KC, base_rev1 as BR, build_mud as BM
    sh = Sheet(doc); sh.frame('MASTER CLOSET', 'SCALE: 3/4" TO 1\'-0"', ['MASTER CLOSET', 'KEY PLAN'], 'ID-330', legend_rule=False)
    src = fitz.open(CP.BASE_KEY); sp = src[1]
    T = BR.transform(2)
    a = T(446.1 - 9, 832.0 - 9); b = T(690.0 + 9, 1064.2 + 40)
    clip_disp = fitz.Rect(a[0], a[1], b[0], b[1])
    u = clip_disp * sp.derotation_matrix; u.normalize()
    k = 4.0
    tw, th = clip_disp.width * k, clip_disp.height * k
    ax0, ay0, ax1, ay1 = FR.x0 + 6, FR.y0 + 24, TB_X - 10, FR.y1 - 6
    colx = ax1 - 660
    tx = max(ax0 + 110, ax0 + (colx - 50 - ax0 - tw) / 2); ty = ay0 + 60 + (ay1 - ay0 - 60 - th) / 2
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    sh.p.show_pdf_page(target, src, 1, clip=u, rotate=90)
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(2, ['W.I.C.'])), 'key plan clip'
    def O(xf, yf):
        d_ = T(xf, yf); return (target.x0 + (d_[0] - clip_disp.x0) * k, target.y0 + (d_[1] - clip_disp.y0) * k)
    def I(xi, yi): return O(446.1 + xi * 1.5, 832.0 + yi * 1.5)
    kk = abs(I(1, 0)[0] - I(0, 0)[0]) + abs(I(1, 0)[1] - I(0, 0)[1])         # sheet pt per closet inch
    # clear FOR's closet linework inside the room, keep its walls
    pa, pb = I(0.6, 0.6), I(W - 0.6, D - 0.6); rr = fitz.Rect(pa, pb); rr.normalize()
    sh.p.draw_rect(rr, color=None, fill=WHITE, width=0)
    plan_overlay(sh, I, kk)
    # FOR's single-leaf stub left in the wall at the door 19 opening: repaint the wall poche west of the jamb, white in the opening
    jx = I(DOOR_C - DOOR_W / 2, D)[0]; wy = I(0, D)[1]
    for dr in list(sh.p.get_drawings()):
        rr = dr['rect']
        if rr.y0 > wy + 1 and rr.y1 < wy + 40 and rr.height < 14 and rr.width > 60 and rr.x0 < jx < rr.x1 and (dr.get('width') or 0) > 1.0:
            sh.p.draw_rect(fitz.Rect(rr.x0 - 1.5, rr.y0 - 1.5, jx, rr.y1 + 1.5), color=None, fill=(0.353, 0.353, 0.353), width=0)
            sh.p.draw_rect(fitz.Rect(jx, rr.y0 - 1.5, rr.x1 + 1.5, rr.y1 + 1.5), color=None, fill=WHITE, width=0)
    # the laundry chute label in its bay, masked over the shaft
    cp = I(W - CH_D / 2 - 2.25, (CH_Y0 + CH_Y1) / 2)
    for i_, t_ in enumerate(('LAUNDRY', 'CHUTE')):
        w_ = _FB.text_length(t_, fontsize=7.0)
        sh.p.draw_rect(fitz.Rect(cp[0] - w_ / 2 - 2, cp[1] - 9 + i_ * 9, cp[0] + w_ / 2 + 2, cp[1] + i_ * 9), color=None, fill=WHITE, width=0)
        sh.text(cp[0] - w_ / 2, cp[1] - 2 + i_ * 9, t_, 7.0, INK, bold=True, raw=True)
    # labels
    def lab(xi, yi, t, size=8.0, bold=False, rot=False, mask=False):
        p = I(xi, yi)
        if rot:
            w = _FR.text_length(t, fontsize=size)
            if mask: sh.p.draw_rect(fitz.Rect(p[0] - size * 0.45 - 1.5, p[1] - w / 2 - 3, p[0] + size * 0.6 + 1.5, p[1] + w / 2 + 3), color=None, fill=WHITE, width=0)
            sh.p.insert_text((p[0] + size * 0.35, p[1] + w / 2), t, fontsize=size, fontname='helv', rotate=90, color=INK); return
        w = (_FB if bold else _FR).text_length(t, fontsize=size)
        sh.text(p[0] - w / 2, p[1] + size * 0.35, t, size, INK, bold=bold, raw=True)
    lab(W / 2, DN / 2 + 1, 'PURSE SHOWCASE, 16 BAGS', 8.0, True)
    lab(NA / 2, DN / 2 - 6, 'DOUBLE HANG', 7.0); lab((NB + W) / 2, DN / 2 - 6, 'DOUBLE HANG', 7.0)
    lab(DW / 2 + 4, (DN + VY0) / 2, 'DOUBLE HANG', 7.0, rot=True)
    lab(DV / 2 + 3, (VY0 + VY1) / 2, 'VANITY 4\'-0", ST-06', 7.5, True, rot=True)
    lab(DW / 2 + 4, (VY1 + D) / 2, 'DRESSES, GL-01', 7.0, rot=True)
    lab(W - DE / 2 + 4, (DN + CH_Y0) / 2 - 1, 'DOUBLE HANG', 7.0, rot=True)
    lab(W - DE / 2 + 4, sum(EB['dress']) / 2, 'DRESSES, GL-01', 7.0, rot=True)
    lab(W - DE / 2 + 4, sum(EB['shoes']) / 2, 'SHOES 36 PR, GL-01', 7.0, rot=True, mask=True)
    lab((ISL[0] + ISL[2]) / 2, ISL[1] + 9, 'ISLAND, WATERFALL', 8.0, True)
    lab((ISL[0] + ISL[2]) / 2, ISL[1] + 15, 'DRAWERS WEST', 6.8)
    lab((ISL[0] + ISL[2]) / 2, ISL[3] - 5, 'CH1 OVER', 6.8)
    for (p0, p1) in MIRR: lab((p0 + p1) / 2, D - 4, 'MR-01', 6.8)
    lab(DOOR_C, D + 11, 'DOOR 19A, ARCHED PAIR, HARMON HINGES', 7.0)
    # markers: one quad marker in each aisle is crowded; four single markers
    for (xi, yi, n, sn, d) in ((DOOR_C, DN + 12, 1, 'ID-331', 'N'), ((ISL[2] + W - DE) / 2, (ISL[1] + ISL[3]) / 2 + 2, 3, 'ID-332', 'E'),
                               ((DV + ISL[0]) / 2 + 2, VY1 + 12, 4, 'ID-332', 'W'), ((ISL[2] + W - DE) / 2, ISL[3] + 9, 2, 'ID-331', 'S')):
        p = I(xi, yi); BM.elev_marker(sh, p[0], p[1], n, sn, d, r=17.0)
    p = I((ISL[0] + ISL[2]) / 2, (ISL[1] + ISL[3]) / 2 + 2)
    BM.quad_marker(sh, p[0], p[1], 'ID-333', {'W': 5, 'E': 6, 'N': 7, 'S': 8}, r=17.0)
    # overall dimensions
    def dim(a_, b_, off, horiz=True, t=''):
        if horiz: A, B = I(a_, -off), I(b_, -off)
        else: A, B = I(-off, a_), I(-off, b_)
        sh.line(A, B, 0.5, INK)
        for q in (A, B):
            sh.line((q[0] - (0 if horiz else 4), q[1] - (4 if horiz else 0)), (q[0] + (0 if horiz else 4), q[1] + (4 if horiz else 0)), 0.5)
            sh.line((q[0] - 2.5, q[1] + 2.5), (q[0] + 2.5, q[1] - 2.5), 0.8)
        lab_ = t or E.ftin(abs(b_ - a_)); w = _FR.text_length(lab_, fontsize=8.5)
        if horiz: sh.text((A[0] + B[0]) / 2 - w / 2, A[1] - 4, lab_, 8.5, INK, raw=True)
        else:
            cy = (A[1] + B[1]) / 2
            sh.p.draw_rect(fitz.Rect(A[0] - w / 2 - 3, cy - 8, A[0] + w / 2 + 3, cy + 5), color=None, fill=WHITE, width=0)
            sh.text(A[0] - w / 2, cy + 3, lab_, 8.5, INK, raw=True)
    dim(0, W, 16, True, '13\'-6-5/8"')
    dim(0, D, 16, False, '12\'-10-3/4"')
    for (a_, b_) in ((0, DN), (DN, ISL[1]), (ISL[1], ISL[3]), (ISL[3], D)): dim(a_, b_, -W - 12 - 0, False) if False else None
    # aisle dimensions inside the plan (west, east, north, south of the island)
    def adim(a_, b_, at, horiz):
        A = I(a_, at) if horiz else I(at, a_); B = I(b_, at) if horiz else I(at, b_)
        sh.line(A, B, 0.4, MID)
        for q in (A, B): sh.line((q[0] - 2, q[1] + 2), (q[0] + 2, q[1] - 2), 0.7)
        t = E.ftin(b_ - a_); w = _FR.text_length(t, fontsize=7.0)
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        sh.p.draw_rect(fitz.Rect(mx - w / 2 - 2, my - 7, mx + w / 2 + 2, my + 3), color=None, fill=WHITE, width=0)
        sh.text(mx - w / 2, my + 1.5, t, 7.0, INK, raw=True)
    adim(DV, ISL[0], ISL[1] + 6, True); adim(ISL[2], W - DE, ISL[3] - 14, True)
    adim(DN, ISL[1], ISL[0] + 6, False); adim(ISL[3], D, ISL[0] - 5, False)
    # north arrow
    nx, ny = target.x1 + 26, target.y0 - 4
    sh.p.draw_circle(fitz.Point(nx, ny + 14), 9, color=INK, width=0.6)
    sh.p.draw_polyline([fitz.Point(nx, ny + 4), fitz.Point(nx + 5, ny + 20), fitz.Point(nx, ny + 16), fitz.Point(nx - 5, ny + 20), fitz.Point(nx, ny + 4)], color=INK, fill=INK, width=0.5)
    sh.text(nx - 3, ny - 1, 'N', 8, INK, bold=True, raw=True)
    sh.text(target.x0, target.y1 + 26, 'MASTER CLOSET PLAN', 10, INK, serif=True, raw=True)
    sh.text(target.x0, target.y1 + 40, 'SCALE: 3/4" TO 1\'-0"', 7.5, INK, raw=True)
    # notes column
    x = colx + 10; y = ay0 + 30; tw_ = ax1 - x - 10
    sh.text(x, y, 'MASTER CLOSET, THE OWNER\'S PICK (11.09.26)', 14, serif=True, raw=True); y += 28
    for head, lines in NOTES:
        sh.text(x, y, head, 9.0, INK, bold=True, raw=True); y += 14
        for t in lines:
            for i, ln_ in enumerate(CS.wrap(t, 8.0, tw_ - 14)):
                if i == 0: sh.text(x, y, '-', 8.0, INK, raw=True)
                sh.text(x + 11, y, ln_, 8.0, INK, raw=True); y += 11.2
        y += 9
    assert y < ay1 - 6, ('ID-330 notes run off the sheet', y, ay1)
    return sh

NOTES = [
    ('DESIGN', [
        'THE OWNER\'S PICK FROM HIS FOUR REFERENCE RENDERS: WARM GREIGE MATTE MILLWORK WITH THIN REVEALS, OPEN DOUBLE HANG IN THE CORNERS, BRONZE RODS, LED AT THE SHELF FRONTS, A DRAWER ISLAND WITH A STONE TOP.',
        'OWNER\'S CHANGES: SOLID DOORS ON EVERY UPPER CABINET; UPPERS OVER THE VANITY; VANITY 4\'-0"; ISLAND DRAWERS ON THE VANITY (WEST) SIDE, CLOSED PANELS ON THE OTHER FACES; NORTH CENTER WITH NO COUNTERTOP: DRAWERS, THEN THE PURSE SHOWCASE TO THE CEILING; DOORS ON THE DRESS HANGING AND THE SHOES.',
        'DRESS AND SHOE DOORS ARE BRONZE-FRAMED CLEAR GLASS (GL-01) SO THE DRESSES AND SHOES STAY ON VIEW. ALTERNATE: SOLID MW-01 PANELS.',
        'OWNER 11.09.26 PM: ARCHED OPENING TO THE BATH; MIRRORS ONLY ON THE SOUTH WALL; CONTINUOUS SHOWCASE SHELVES; HANGING OVER A LOWERED CHUTE; DRESSES SOUTH OF THE VANITY; ISLAND WITH WATERFALL ENDS AND WIDER DRAWERS.']),
    ('COUNTS AND CLEARANCES', [
        'PURSE SHOWCASE: 16 BAGS (FOUR ROWS OF FOUR), ONE CONTINUOUS GLASS SHELF A ROW WITH NO CENTER UPRIGHT, LED UNDER EACH, LINEN BACK, 18-5/8" A ROW.',
        'SHOES: 36 PAIRS, NINE PITCHED LIT SHELVES WITH A HEEL RAIL, FOUR PAIRS EACH, SOUTH END OF THE EAST RUN (TOP SHELVES TAKE A STEP STOOL).',
        'HANGING: DOUBLE HANG AT 82" AND 41" IN THE FOUR CORNERS OF THE RUNS; THE UPPER ROD RUNS ON OVER THE CHUTE CABINET; DRESSES AT 80" IN TWO GLASS-DOOR BAYS.',
        'VANITY 4\'-0" x 22", TOP AT 30", ONE 48" KNEE SPACE, TWO 24" SEATS (POUFS, N.I.C.). LIT MIRROR LM1, UPPERS ABOVE.',
        'ISLAND 3\'-6" x 5\'-1-3/4" x 36" HIGH, ST-06 WATERFALL ENDS; WEST FACE TWO STACKS OF TWO DRAWERS OVER ONE DEEP DRAWER. AISLES 3\'-0" MIN.; 2\'-9" TO THE SOUTH WALL.',
        'SOUTH WALL: FLUSH MIRRORS MR-01 EACH SIDE OF THE ARCHED DOOR 19A, 6" TO 8\'-5", NO CASEWORK; THE CROWN CONTINUES.']),
    ('MATERIALS', [
        'MW-01 GREIGE MATTE LACQUER MILLWORK, CASES, DOORS AND PANELS, 1/8" REVEALS (COLOR TO SELECT).',
        'MW-02 TEXTURED DRAWER FRONTS, SHAGREEN-LOOK EMBOSSED LEATHER OR TEXTURED LACQUER, GREIGE (SAMPLE TO OWNER).',
        'GL-01 GLASS DOORS: 3/4" BRONZE-FINISH ALUMINUM FRAME, 1/4" CLEAR LOW-IRON TEMPERED GLASS, CONCEALED HINGES.',
        'GL-02 GLASS SHELVES: 3/4" LAMINATED LOW-IRON, ONE PIECE ACROSS THE SHOWCASE, ON A CONCEALED BRONZE BACK CHANNEL. FB-01 LINEN-TEXTURE BACK PANEL.',
        'ST-06 STONE, VANITY TOP AND ISLAND TOP WITH WATERFALL ENDS, 1-1/2", MITERED, VEINS MATCHED (WHITE MARBLE, HONED, TO SELECT). MR-01 MIRROR, FLUSH.',
        'HARDWARE: SLIM BRONZE BAR PULLS, BRONZE OVAL RODS, SOFT-CLOSE FULL-EXTENSION SLIDES, CONCEALED SOFT-CLOSE HINGES.',
        'FLOOR PER ID-102. CROWN 4-1/2" ACROSS THE RUNS, SOFFIT FLUSH WITH THE CABINET FACE (1/ID-501). CEILING 9\'-6" (FOR A-206).']),
    ('COORDINATED WITH FOR (REV 1)', [
        'LIGHTING: LED TAPE IN CHANNELS AT EVERY SHELF FRONT AND IN THE SHOWCASE (ID TYPE LS2) IN PLACE OF FOR\'S L13; CH1 ON FOR\'S BOX OVER THE ISLAND; LM1 MIRROR. DRIVERS IN THE UPPERS, ON A DIMMER AT DOOR 19A (ID-132).',
        'LAUNDRY CHUTE: FOR\'S SHAFT IN THE EAST RUN STOPS AT 3\'-6": A LOW CABINET, INTAKE 1\'-8" TO 2\'-10" BEHIND ITS DOOR, HANGING AND UPPERS ABOVE. FOR TO CUT THE SHAFT DOWN (VENT IN THE WALL IF THE MAKER NEEDS ONE).',
        'POWER: A DUPLEX AT THE VANITY APRON AND ONE IN THE ISLAND (FLOOR BOX, FOR TO ADD); LED DRIVERS ON A SWITCHED CIRCUIT.',
        'DOOR 19A: PAIR ON HARMON HINGES, SEMICIRCULAR ARCHED HEAD, SPRING 6\'-6", APEX 8\'-0" (ID-002). FOR: ARCHED HEADER FRAMING.'])]

# ---------------------------------------------------------------- sheets
def cell_view(sh, cell, number, title, scale, length, k, draw, notes, room='MASTER CLOSET', view=''):
    x0, y0, x1, y1 = cell
    E.title_bar(sh.p, sh.font, sh.fontname, cell, number, title, scale)
    ty = y0 + 30
    for t in CS.wrap(notes, 7.0, x1 - x0 - 24): sh.text(x0 + 12, ty, t, 7.0, INK, raw=True); ty += 10
    vw = length * k; floor = min(y1 - 70, (ty + y1) / 2 + H * k / 2 + 30)
    ox = x0 + (x1 - x0 - vw - 60) / 2 + 10
    v = E.ElevationView(sh.p, sh.font, sh.fontname, (ox, floor), k, {'room': room, 'view': view or title, 'length': length, 'ceiling': H})
    assert v.Y(H) - 14 > ty, ('view runs into its notes', title, v.Y(H), ty)
    return v, floor

def ID331(doc):
    sh = Sheet(doc); sh.frame('MASTER CLOSET', 'SCALE: 1/2" TO 1\'-0"', ['MASTER CLOSET', 'NORTH AND SOUTH ELEVATIONS'], 'ID-331', legend_rule=False)
    fx0, fy0, fx1, fy1 = FR.x0 + 6, FR.y0 + 6, TB_X - 6, FR.y1 - 6; mx = (fx0 + fx1) / 2; k = E.SCALES['1/2']
    v, fl = cell_view(sh, (fx0, fy0, mx, fy1), 1, 'NORTH ELEVATION - PURSE SHOWCASE (FROM THE BATH)', 'SCALE: 1/2" TO 1\'-0"', W, k, north,
        'PURSE SHOWCASE (OWNER 11.09.26: NO COUNTERTOP, DRAWERS THEN THE SHOWCASE TO THE CEILING): MW-02 TEXTURED DRAWERS 4 HIGH TO 34", MW-01 CAP, THEN GL-02 '
        'GLASS SHELVES, ONE PIECE ACROSS WITH NO CENTER UPRIGHT (OWNER 11.09.26 PM), ON A FB-01 LINEN BACK, LED UNDER EACH SHELF, 16 BAGS (4 ROWS OF 4). CORNERS: OPEN DOUBLE HANG AT 82" AND 41", BRONZE RODS, '
        'UPPER CABINETS WITH SOLID MW-01 DOORS FROM 86" TO THE CROWN, LED AT THE SHELF FRONT BELOW THEM. CROWN 4-1/2" CONTINUOUS, SOFFIT FLUSH (1/ID-501).')
    pts = north(v)
    v.dim_h(0, W, fl + 14, E.snap_points(pts))
    y0s = SC_TOP_DRW + 1.0; rh = (TOP - y0s) / SC_ROWS
    v.dim_v(0, H, v.X(W) + 16, E.snap_points([0, 4.0, SC_TOP_DRW, y0s] + [y0s + j * rh for j in range(1, SC_ROWS)] + [TOP, H]))
    overall(v, v.X(W) + 40)
    xr = v.X(W) + 56
    tag(v, 8, 97, 'MW-01 UPPERS,\nSOLID DOORS', 'l', 97)
    tag(v, 5, ROD_HI + 1.9, 'SHELF WITH LED,\nBRONZE ROD', 'l', 80)
    tag(v, 5, 58, 'OPEN DOUBLE HANG', 'l', 58)
    tag(v, NA + 3, 21, 'MW-02 DRAWERS,\nBRONZE BAR PULLS', 'l', 21)
    tag(v, NA + 6, 107, 'PURSE SHOWCASE TO THE CROWN, 16 BAGS', 't', H + 9)
    tag(v, NB - 1.5, 101, 'FB-01 LINEN BACK', 'r', 101, xr)
    tag(v, NB - 1.5, y0s + rh, 'GL-02 GLASS SHELF, ONE\nPIECE, LED BELOW', 'r', y0s + rh + 6, xr)
    tag(v, NB - 1.5, SC_TOP_DRW + 0.5, 'MW-01 CAP,\nNO COUNTERTOP', 'r', SC_TOP_DRW + 2, xr)
    tag(v, NB - 3, 10, 'MW-02 DRAWERS\n4 HIGH, 4" TO 34"', 'r', 12, xr)
    v2, fl2 = cell_view(sh, (mx, fy0, fx1, fy1), 2, 'SOUTH ELEVATION - DOOR 19A (FROM THE ISLAND)', 'SCALE: 1/2" TO 1\'-0"', W, k, south,
        'DOOR 19A, PAIR OF 1\'-6" LEAVES UNDER A SEMICIRCULAR ARCH (OWNER 11.09.26 PM), SPRING 6\'-6", APEX 8\'-0", ARCHED CASING, HARMON HINGES (ID-002), SWINGS IN. '
        'EACH SIDE: A FLUSH MIRROR MR-01 FROM 6" TO 8\'-5" (THE CASING APEX AND THE BATH MIRROR TOPS), NO CASEWORK ON THIS WALL; THE CROWN CONTINUES. THE EAST AND WEST RUNS SEEN END-ON.')
    pts = south(v2)
    v2.dim_h(0, W, fl2 + 14, E.snap_points(pts))
    v2.dim_v(0, H, v2.X(W) + 16, E.snap_points([0, 6.0, SPRING, SPRING + DOOR_W / 2, MIR_TOP, TOP, H]))
    overall(v2, v2.X(W) + 40)
    xr2 = v2.X(W) + 56
    tag(v2, W - MIRR[1][1] + 3, 30, 'MR-01 MIRROR,\nFLUSH, 6" TO 8\'-5"', 'l', 30)
    tag(v2, W - (DOOR_C - DOOR_W / 2) - 3, 70, 'DOOR 19A, ARCHED PAIR,\nHARMON HINGES (ID-002)', 'r', 70, xr2)
    tag(v2, W - (DOOR_C - DOOR_W / 2) + 1.5, SPRING + 8, 'ARCHED CASING', 'r', SPRING + 18, xr2)
    tag(v2, W - 12, 30, 'WEST RUN, END PANEL', 'r', 30, xr2)
    return sh

def ID332(doc):
    sh = Sheet(doc); sh.frame('MASTER CLOSET', 'SCALE: 1/2" TO 1\'-0"', ['MASTER CLOSET', 'EAST AND WEST ELEVATIONS'], 'ID-332', legend_rule=False)
    fx0, fy0, fx1, fy1 = FR.x0 + 6, FR.y0 + 6, TB_X - 6, FR.y1 - 6; mx = (fx0 + fx1) / 2; k = E.SCALES['1/2']
    v, fl = cell_view(sh, (fx0, fy0, mx, fy1), 3, 'EAST ELEVATION - SHOES, DRESSES AND THE LAUNDRY CHUTE', 'SCALE: 1/2" TO 1\'-0"', D, k, east,
        'NORTH TO SOUTH: OPEN DOUBLE HANG; THE LAUNDRY CHUTE LOWERED INTO A CABINET UNDER THE 3\'-6" SHELF, MW-01 DOOR, INTAKE DASHED (OWNER 11.09.26 PM: THE UPPER '
        'ROD AND THE UPPERS RUN ON OVER IT; VERIFY THE INTAKE WITH THE CHUTE MAKER); DRESSES ON A ROD AT 80" BEHIND GL-01 BRONZE-FRAMED GLASS DOORS, AN UPPER WITH SOLID DOORS ABOVE; THE SHOE TOWER, 36 PAIRS ON NINE PITCHED '
        'LIT SHELVES, BEHIND FULL-HEIGHT GL-01 GLASS DOORS (OWNER 11.09.26: DOORS ON THE DRESSES AND SHOES; GLASS SO THEY STAY ON VIEW, SOLID IS THE ALTERNATE). '
        'VERTICAL DIMENSIONS ARE AT THE DOUBLE HANG AND THE CHUTE CABINET.')
    n, pts = east(v)
    assert n >= 32, n
    v.dim_h(0, D, fl + 14, E.snap_points(pts))
    v.dim_v(0, H, v.X(D) + 30, E.snap_points([0, 4.0, ROD_LO, CH_TOP, ROD_HI, UP0, TOP, H]))
    overall(v, v.X(D) + 54)
    xr = v.X(D) + 70
    tag(v, DN + 6, 97, 'MW-01 UPPERS,\nSOLID DOORS', 'l', 97)
    tag(v, DN + 3, 58, 'OPEN DOUBLE HANG', 'l', 66)
    tag(v, 6, 30, 'NORTH RUN, END PANEL', 'l', 30)
    tag(v, sum(EB['chute']) / 2, 62, 'UPPER HANG OVER THE CHUTE', 't', H + 9)
    tag(v, sum(EB['chute']) / 2 + 4, 12, 'CHUTE CABINET,\nINTAKE BEHIND', 'r', 12, v.X(D) + 70)
    tag(v, sum(EB['dress']) / 2 + 6, 60, 'DRESSES: ROD AT 80", GL-01 GLASS DOORS', 't', H + 18)
    tag(v, D - 2, 70, 'SHOES, %d PAIRS,\nFULL-HEIGHT\nGL-01 GLASS DOORS' % n, 'r', 70, xr)
    v2, fl2 = cell_view(sh, (mx, fy0, fx1, fy1), 4, 'WEST ELEVATION - THE VANITY', 'SCALE: 1/2" TO 1\'-0"', D, k, west,
        'VANITY 4\'-0" (OWNER), ST-06 STONE TOP AT 30", TWO SHALLOW MW-02 APRON DRAWERS, ONE 48" KNEE SPACE FOR TWO POUFS (N.I.C.). LM1 LIT MIRROR 40" x 44" BETWEEN '
        'THE TOP AND THE UPPERS (OWNER: UPPER CABINETS OVER THE VANITY), SOLID MW-01 DOORS TO THE CROWN, LED UNDER THEM. OWNER 11.09.26 PM: DRESSES ON THE LEFT (SOUTH) '
        'BEHIND GL-01 GLASS DOORS, OPEN DOUBLE HANG ON THE RIGHT (NORTH). DUPLEX IN THE APRON FOR A HAIR DRYER (FOR TO ADD).')
    pts = west(v2)
    v2.dim_h(0, D, fl2 + 14, E.snap_points(pts))
    v2.dim_v(0, H, v2.X(D) + 30, E.snap_points([0, VTOP - 5.5, VTOP, 36.0, 80.0, UP0, TOP, H]))
    overall(v2, v2.X(D) + 54)
    a, b = D - VY1, D - VY0
    xr2 = v2.X(D) + 70
    tag(v2, 5, 58, 'DRESSES BEHIND\nGL-01 GLASS DOORS', 'l', 66, xl=-6)
    tag(v2, a + 1.5, VTOP - 0.7, 'ST-06 STONE TOP AT 30"', 'l', 36, xl=-6)
    tag(v2, a + 3, VTOP - 3.5, 'MW-02 APRON DRAWERS', 'l', 24, xl=-6)
    tag(v2, a + 12, 9, 'POUF (N.I.C.)', 'l', 9, xl=-6)
    tag(v2, (a + b) / 2 + 6, 100, 'MW-01 UPPERS OVER THE VANITY, SOLID DOORS', 't', H + 9)
    tag(v2, b - 4.6, 64, 'LM1 LIT MIRROR\n40" x 44"', 'r', 64, xr2)
    tag(v2, D - DN - 3, 40, 'OPEN DOUBLE HANG', 'r', 40, xr2)
    return sh

def ID333(doc):
    sh = Sheet(doc); sh.frame('MASTER CLOSET', 'SCALE: AS NOTED', ['MASTER CLOSET', 'ISLAND AND DETAILS'], 'ID-333', legend_rule=False)
    fx0, fy0, fx1, fy1 = FR.x0 + 6, FR.y0 + 6, TB_X - 6, FR.y1 - 6
    k = E.SCALES['3/4']; Li = ISL[3] - ISL[1]; Wi = ISL[2] - ISL[0]
    top_h = 360.0
    cells = []; widths = [Li, Li, Wi, Wi]; tot = sum(w * k + 90 for w in widths); x = fx0 + (fx1 - fx0 - tot) / 2
    faces = ((5, 'ISLAND - WEST FACE, DRAWERS (FROM THE VANITY)', Li, 'drawers'), (6, 'ISLAND - EAST FACE', Li, 'panels'),
             (7, 'ISLAND - NORTH END, WATERFALL', Wi, 'end'), (8, 'ISLAND - SOUTH END, WATERFALL', Wi, 'end'))
    E.title_bar(sh.p, sh.font, sh.fontname, (fx0, fy0, fx1, fy0 + top_h), 5, 'ISLAND ELEVATIONS (VIEWS 5 TO 8)', 'SCALE: 3/4" TO 1\'-0"')
    note = ('ISLAND 3\'-6" x 5\'-1-3/4" x 36", ST-06 STONE TOP 1-1/2" WITH WATERFALL ENDS TO THE FLOOR, MITERED, VEINS MATCHED ACROSS THE MITER (OWNER 11.09.26 PM). '
            'WEST (VANITY) FACE: TWO STACKS OF WIDER MW-02 TEXTURED DRAWERS (OWNER: TWO, NOT THREE), EACH TWO DRAWERS OVER ONE DEEP DRAWER (4" TO 18"), SOFT-CLOSE FULL '
            'EXTENSION, VELVET-LINED TOP DRAWERS FOR JEWELRY. EAST FACE: CLOSED MW-01 PANELS WITH 1/8" REVEALS. RECESSED TOE BETWEEN THE WATERFALLS. CH1 OVER THE ISLAND ON FOR\'S BOX. A FLOOR BOX UNDER IT IF A CHARGING DRAWER IS WANTED (FOR TO ADD).')
    ty = fy0 + 30
    for t in CS.wrap(note, 7.0, fx1 - fx0 - 24): sh.text(fx0 + 12, ty, t, 7.0, INK, raw=True); ty += 10
    floor = fy0 + top_h - 60
    for (n, title, Lf, dr) in faces:
        v = E.ElevationView(sh.p, sh.font, sh.fontname, (x + 10, floor), k, {'room': 'MASTER CLOSET', 'view': title, 'length': Lf, 'ceiling': ITOP})
        island_face(v, Lf, dr)
        hp = {'drawers': [0, WF, Lf / 2, Lf - WF, Lf], 'panels': [0, WF, Lf - WF, Lf], 'end': [0, Lf]}[dr]
        vp = {'drawers': [0, 4.0, DRW_DEEP, ITOP - 1.5, ITOP], 'panels': [0, 4.0, ITOP - 1.5, ITOP], 'end': [0, ITOP - 1.5, ITOP]}[dr]
        v.dim_h(0, Lf, floor + 14, E.snap_points(hp))
        v.dim_v(0, ITOP, v.X(Lf) + 14, E.snap_points(vp))
        v.dim_v(0, ITOP, v.X(Lf) + 34, E.snap_points([0, ITOP]))
        sh.text(x + 10, floor + 40, '%d  %s' % (n, title), 7.5, INK, raw=True)
        if n > 5: take_scale(sh.p, 'SCALE: 3/4" TO 1\'-0"', 'VIEW %d' % n)
        x += Lf * k + 90
    # details
    dy0 = fy0 + top_h + 10; dw = (fx1 - fx0) / 3
    det = ((9, 'DRAWER SECTION', 'SCALE: 3" TO 1\'-0"', drawer_section), (10, 'GLASS SHELF WITH LED (SHOWCASE)', 'SCALE: 3" TO 1\'-0"', shelf_section),
           (11, 'GLASS DOOR FRAME, SECTION AT THE STILE', 'SCALE: 6" TO 1\'-0"', door_section))
    for i, (n, t, s, fn) in enumerate(det):
        cell = (fx0 + i * dw, dy0, fx0 + (i + 1) * dw, fy1)
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, t, s)
        fn(sh, cell)
    return sh

def _dl(sh, a, b, w=0.5, c=INK, d=None): sh.line(a, b, w, c, d)
def _dr(sh, x0, y0, x1, y1, w=0.6, c=INK, fill=None, d=None): sh.rect(fitz.Rect(x0, y0, x1, y1), w, c, fill, d)
def _note(sh, x, y, t, size=7.0): sh.text(x, y, t, size, INK, raw=True)
def _lead(sh, p, q, t, size=7.0, right=True):
    """Leader from p to the END of its note nearest p (never across the text). right: the note reads to the right of q."""
    w = _FR.text_length(t, fontsize=size * 1.05)
    tx = q[0] + 3 if right else q[0] - w - 3
    e0, e1 = tx - 2, tx + w + 2
    ax = e1 if abs(p[0] - e1) < abs(p[0] - e0) else e0
    sh.line(p, (ax, q[1]), 0.35, INK); s = sh.p.new_shape(); s.draw_circle(fitz.Point(*p), 0.9); s.finish(color=INK, fill=INK); s.commit()
    sh.text(tx, q[1] + 2.5, t, size, INK, raw=True)

BRONZE = (0.6, 0.5, 0.35); GLASS = (0.88, 0.95, 0.95); GREY = (0.85, 0.85, 0.85)

def _ddim(sh, p0, p1, off, label, horiz=True, size=6.8):
    """A dimension between two sheet points, offset off points (sign gives the side)."""
    if horiz:
        y = p0[1] + off; A, B = (p0[0], y), (p1[0], y)
        for p in (p0, p1): sh.line((p[0], p[1] + (2 if off > 0 else -2)), (p[0], y + (3 if off > 0 else -3)), 0.3, MID)
    else:
        x = p0[0] + off; A, B = (x, p0[1]), (x, p1[1])
        for p in (p0, p1): sh.line((p[0] + (2 if off > 0 else -2), p[1]), (x + (3 if off > 0 else -3), p[1]), 0.3, MID)
    sh.line(A, B, 0.4, INK)
    for q in (A, B): sh.line((q[0] - 2, q[1] + 2), (q[0] + 2, q[1] - 2), 0.7)
    w = _FR.text_length(label, fontsize=size)
    if horiz: sh.text((A[0] + B[0]) / 2 - w / 2, A[1] - 3, label, size, INK, raw=True)
    else:
        cy = (A[1] + B[1]) / 2
        sh.p.insert_text((A[0] - 3, cy + w / 2), label, fontsize=size, fontname='helv', rotate=90, color=INK)

def _break(sh, a, b):
    """A break line between two sheet points."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    pts = [a, (mx - ux * 4, my - uy * 4), (mx - ux * 2 - uy * 5, my - uy * 2 + ux * 5), (mx + ux * 2 + uy * 5, my + uy * 2 - ux * 5), (mx + ux * 4, my + uy * 4), b]
    sh.p.draw_polyline([fitz.Point(*p) for p in pts], color=INK, width=0.4)

def drawer_section(sh, cell):
    """Section through the top island drawer, west face: MW-02 inset front, dovetail box on undermount slides, velvet tray, ST-06 top over."""
    x0, y0, x1, y1 = cell; s = 18.0                                  # 3" = 1'-0"
    ox = x0 + 82; base = y0 + 130 + 12.5 * s                       # x: inches back from the face of the front; y: inches above the floor
    def P(x, y): return (ox + x * s, base - (y - 23.5) * s)
    def RR(xa, ya, xb, yb, w=0.6, fill=None, c=INK, d=None):
        a_, b_ = P(xa, ya), P(xb, yb); sh.rect(fitz.Rect(min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1])), w, c, fill, d)
    RR(-1.0, 34.5, 21.0, 36.0, 0.8, STONE)                           # ST-06 top, 1" overhang
    RR(0.75, 33.75, 21.0, 34.5, 0.6, GREY)                           # MW-01 sub-top
    RR(0.0, 26.0, 0.75, 33.625, 0.9, (0.8, 0.78, 0.74))              # MW-02 front, 1/8" reveal under the sub-top
    texture_x = [P(0.0, y) for y in (27.5, 29.0, 30.5, 32.0, 33.0)]
    RR(0.0, 23.5, 0.75, 25.875, 0.9, (0.8, 0.78, 0.74))              # the next front down
    RR(1.0, 26.75, 1.5, 32.75, 0.6); RR(19.0, 26.75, 19.5, 32.75, 0.6)     # box front and back, 1/2"
    RR(1.0, 26.75, 19.5, 27.25, 0.6)                                # box bottom, 1/2"
    RR(1.5, 27.25, 19.0, 28.25, 0.4, (0.93, 0.92, 0.9), MID)        # velvet tray
    sh.line(P(1.5, 26.45), P(19.0, 26.45), 1.4, MID)                 # undermount slide
    RR(20.25, 23.5, 21.0, 33.75, 0.6, GREY)                          # center divider, back of the west drawers
    RR(-1.0, 30.1, -0.35, 30.6, 0.7, BRONZE); RR(-0.35, 30.25, 0.0, 30.45, 0.5, BRONZE)   # bronze bar pull and post
    _break(sh, P(21.0, 36.6), P(21.0, 23.0))
    sh.line(P(-2.5, 23.5), P(21.5, 23.5), 0.3, LIGHT, '[3 2] 0')
    _ddim(sh, P(1.0, 26.75), P(19.5, 26.75), (y0 + 470) - P(0, 26.75)[1], '1\'-6-1/2" BOX, 18" SLIDES', True)
    _ddim(sh, P(0.0, 36.0), P(21.0, 36.0), -24, '1\'-9" TO THE CENTER (HALF THE 3\'-6" ISLAND)', True)
    _ddim(sh, P(0.0, 26.0), P(0.0, 33.625), -66, '7-5/8" FRONT', False)
    _ddim(sh, P(-1.0, 34.5), P(-1.0, 36.0), -40, '1-1/2"', False)
    top = P(0, 36)[1]; bot = P(0, 23.5)[1]
    _lead(sh, P(5, 35.3), (P(5, 0)[0], top - 52), 'ST-06 STONE TOP, 1-1/2", EASED EDGE', right=False)
    _lead(sh, P(18, 34.1), (P(18, 0)[0], top - 52), 'MW-01 SUB-TOP, 3/4"')
    _lead(sh, P(1.25, 31), (P(4, 0)[0], P(0, 31)[1]), 'DOVETAIL BOX, 1/2" SIDES')
    _lead(sh, P(11, 27.75), (P(11, 0)[0], bot + 24), 'VELVET TRAY (TOP DRAWERS)')
    _lead(sh, P(6, 26.45), (P(6, 0)[0], bot + 44), 'UNDERMOUNT SOFT-CLOSE, FULL EXTENSION')
    _lead(sh, P(20.6, 25), (P(20.6, 0)[0], bot + 62), 'MW-01 CENTER DIVIDER', right=False)
    _lead(sh, P(0.4, 30.5), (x0 + 14, bot + 90), 'MW-02 TEXTURED FRONT, 3/4"', right=True)
    _lead(sh, P(-0.7, 30.35), (x0 + 14, bot + 70), 'BRONZE BAR PULL', right=True)
    _note(sh, x0 + 14, y1 - 52, 'TOP DRAWER SHOWN. SIX DRAWERS, TWO STACKS OF 7-5/8" OVER 7-5/8" OVER 14";')
    _note(sh, x0 + 14, y1 - 40, 'FRONTS INSET IN THE MW-01 CASE, 1/8" REVEALS. EAST HALF OF THE ISLAND')
    _note(sh, x0 + 14, y1 - 28, 'BEHIND THE CENTER DIVIDER IS CLOSED STORAGE BEHIND THE EAST PANELS.')

def shelf_section(sh, cell):
    """Section through two showcase rows: 1/2" glass shelves on bronze pins, a bronze LED rail at each front, linen back."""
    x0, y0, x1, y1 = cell; s = 18.0
    ox = x0 + 150; base = y0 + 470                                   # base = the lower shelf's top
    rh = (TOP - SC_TOP_DRW - 1.0) / SC_ROWS
    def P(x, y): return (ox + x * s, base - y * s)
    def RR(xa, ya, xb, yb, w=0.6, fill=None, c=INK):
        a_, b_ = P(xa, ya), P(xb, yb); sh.rect(fitz.Rect(min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1])), w, c, fill)
    RR(14.0, -4.0, 14.75, rh + 3.0, 0.6, GLOW); RR(14.75, -4.0, 15.5, rh + 3.0, 0.6)     # FB-01 linen on a 3/4" panel
    for yy in (0.0, rh):
        RR(0.0, yy - 0.75, 13.25, yy, 0.6, GLASS)                    # GL-02, 3/4" laminated
        RR(-0.25, yy - 1.5, 0.75, yy, 0.8, BRONZE)                   # bronze LED rail at the front
        RR(13.25, yy - 1.0, 14.0, yy + 0.25, 0.5, BRONZE)            # concealed bronze back channel, full length
    a_ = P(0.25, rh - 1.5)
    for xx in (2.0, 6.0):                                            # light from the upper rail onto the bag below
        sh.line(a_, P(xx, 0.0), 0.35, LIGHT, '[1.5 1.5] 0')
    bx = 3.0; bw = 9.0; bh = 10.5                                    # a bag in section, for scale
    pts = [P(bx, 0), P(bx + bw, 0), P(bx + bw - 0.6, bh), P(bx + 0.6, bh)]
    sh.p.draw_polyline([fitz.Point(*p) for p in pts + [pts[0]]], color=MID, width=0.5)
    sh.p.draw_polyline([fitz.Point(*P(bx + 2.5 + 4 * (1 - math.cos(math.pi * i / 12)) / 2, bh + 3.2 * math.sin(math.pi * i / 12))) for i in range(13)], color=MID, width=0.5)
    _break(sh, P(-1.0, -4.0), P(16.0, -4.0)); _break(sh, P(-1.0, rh + 3.0), P(16.0, rh + 3.0))
    _ddim(sh, P(0, rh), P(0, 0), -60, '1\'-6-5/8" ROW', False)
    _ddim(sh, P(0, -1.5), P(14.0, -1.5), 40, '1\'-2" SHELF', True)
    _lead(sh, P(8, rh - 0.25), (P(8, rh)[0] - 20, P(8, rh)[1] - 36), 'GL-02 3/4" LAMINATED LOW-IRON, ONE PIECE ACROSS', right=False)
    _lead(sh, P(0.25, rh - 0.8), (x0 + 14, P(0, rh)[1] + 60), 'BRONZE RAIL WITH LED, 2700K', right=True)
    _lead(sh, P(14.4, rh + 1.5), (P(14.4, rh)[0] - 12, P(0, rh + 2)[1] - 58), 'FB-01 LINEN BACK ON A 3/4" PANEL', right=False)
    _lead(sh, P(13.6, -0.6), (P(13.0, 0)[0] - 6, P(0, 0)[1] + 34), 'CONCEALED BRONZE CHANNEL, FULL LENGTH', right=False)
    _lead(sh, P(bx + bw / 2, 5), (P(14, 0)[0] + 40, P(0, 5)[1]), 'BAG, FOR SCALE')
    _note(sh, x0 + 14, y1 - 40, 'FOUR ROWS AT 1\'-6-5/8", NO CENTER UPRIGHT; DRIVERS IN THE UPPERS; DIMMER AT 19A (ID-132).')
    _note(sh, x0 + 14, y1 - 28, 'THE RAIL HIDES THE TAPE AND THE SHELF EDGE; BAGS SIT ON THE GLASS, LIT FROM ABOVE.')

def door_section(sh, cell):
    """Plan section at the hinge stile of a GL-01 door: bronze aluminum frame overlaying the MW-01 side, 1/4" glass in a gasket."""
    x0, y0, x1, y1 = cell; s = 36.0                                  # 6" = 1'-0"
    ox = x0 + 150; oy = y0 + 380                                     # origin: outside face of the side panel at the front edge; y + is into the room
    def P(x, y): return (ox + x * s, oy + y * s)
    def RR(xa, ya, xb, yb, w=0.6, fill=None, c=INK):
        a_, b_ = P(xa, ya), P(xb, yb); sh.rect(fitz.Rect(min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1])), w, c, fill)
    RR(0.0, -5.0, 0.75, 0.0, 0.9, GREY)                              # MW-01 side panel, 3/4"
    RR(-0.75, -5.0, 0.0, 0.0, 0.6, GREY)                             # the neighbor bay's side (or the end panel)
    RR(0.125, 0.125, 0.875, 1.125, 0.9, BRONZE)                      # frame stile, 3/4" face x 1" deep, 1/8" off the case
    RR(0.875, 0.5, 6.0, 0.75, 0.6, GLASS)                            # 1/4" glass
    RR(0.875, 0.42, 1.25, 0.5, 0.4, INK); RR(0.875, 0.75, 1.25, 0.83, 0.4, INK)   # gasket
    RR(0.75, -2.25, 1.25, -0.5, 0.6, WHITE)                          # hinge plate on the inside of the side
    sh.line(P(1.0, -0.5), P(0.6, 0.125), 0.8, INK)                   # hinge arm to the frame
    _break(sh, P(6.0, 0.2), P(6.0, 1.05)); _break(sh, P(-1.2, -5.0), P(1.2, -5.0))
    _ddim(sh, P(0.125, 1.125), P(0.875, 1.125), 40, '3/4"', True)
    _ddim(sh, P(0.125, 0.125), P(0.125, 1.125), -30, '1"', False)
    _lead(sh, P(0.5, 0.9), (x0 + 14, P(0, 1)[1] + 70), '3/4" x 1" BRONZE-FINISH ALUMINUM FRAME', right=True)
    _lead(sh, P(4.0, 0.62), (P(4, 0)[0], P(4, 0)[1] - 70), '1/4" CLEAR LOW-IRON TEMPERED GLASS IN A GASKET')
    _lead(sh, P(1.0, -1.4), (P(2, 0)[0] + 20, P(0, -3.5)[1]), 'ALUMINUM-FRAME HINGE, SOFT-CLOSE, PLATE ON THE SIDE')
    _lead(sh, P(0.4, -3.5), (x0 + 14, P(0, -4.2)[1]), 'MW-01 SIDE PANEL, 3/4"', right=True)
    _note(sh, x0 + 14, y1 - 40, 'GL-01 ON THE DRESS BAYS (4" TO 7\'-1") AND THE SHOE TOWER (4" TO THE CROWN).')
    _note(sh, x0 + 14, y1 - 28, 'SLIM BRONZE BAR PULL AT THE MEETING STILES. ALTERNATE: SOLID MW-01 PANEL DOORS.')

def build():
    doc = fitz.open()
    key_sheet(doc); ID331(doc); ID332(doc); ID333(doc)
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, len(doc), 'sheets')

if __name__ == '__main__':
    build()
