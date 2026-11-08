import sys
"""Kitchen and dining room, designed elevations, redrawn on FOR REV 1 (A-201, 10.23.26) floor 1, 11.06.26. Copy of build_kitchen2.py:
the room is 22'-8" x 20'-4-15/16", the refrigerator run on the main north face with 25" deep millwork to the jog at 15'-1-1/2", the 24" recess
east of it (7'-6-1/2", exterior door 05), the 15'-9" slider, the 9'-3" x 5'-5" island at FOR's position, the pantry 4'-11-3/8" deep entered
2'-3" from the west wall. Owner's picks 11.02.26 to 11.03.26 kept where they still fit (range wall study 3 B, columns, swing doors, shelving,
pantry study 4 A). build_kitchen.py is not edited: its constants are patched at run time below, before the names are imported.
Output: 261105.HD102.KitchenPilot.pdf (ID-741 to ID-745)"""
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG
from idd_std import INK, MID, LIGHT, TRIM
import build_kitchen as B
sys.path.insert(0, '/home/claude/flrwork/rev1'); import base_rev1 as BR

# ================================================================== PLAN: FOR REV 1, A-201 floor 1, sheet pt, 18 pt per foot (1.5 pt per in.)
# Measured from FOR's vectors 11.06.26. Room inches: x east from the west face, y south from the north face.
F_PT = 1.5                                   # FOR sheet pt per inch
F_W, F_N, F_E, F_S = 356.22, 173.04, 764.2, 540.42   # kitchen finished faces: west, north (main), east, south
F_JOG_X, F_JOG_Y = 628.44, 137.0             # the north wall jogs north 24" east of x 628.44 (the door 05 recess)
def fx(x): return (x - F_W) / F_PT           # FOR x to room inches
def fy(y): return (y - F_N) / F_PT           # FOR y to room inches
REVS = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', '11.06.26', 'REDRAWN ON FOR REV 1')]
_T = BR.transform(1)                         # FOR sheet pt to the display space of the key plan base (0.75, no rotation)
B.W_FACE, B.N_FACE = (float(c) for c in _T(F_W, F_N))   # 99.55, 185.47 (the old base: 99.6, 185.4)
B.KD = 244.9375                              # west wall 540.42 - 173.04 = 367.38 pt = 244.92, 20'-4-15/16"
B.RC = 122.4375                              # range axis, the wall's center less 1/32" so every edge lands on 1/16" (FOR's 26" range: y 337.4 to 376.0, center 356.7 = 122.4)
B.S_FACE = B.N_FACE + B.KD / B.PT
B.ISL_W = 49.0                               # island cabinet 49 deep (24 working bays + 25 behind): top 1 + 49 + 15 = 65, FOR's 5'-5" (x 456.72 to 554.22 = 97.5 pt)
B.OV = 15.0                                  # the 15" knee recess kept
B.ISL_TOP = 1.0 + B.ISL_W + B.OV             # 65
B.ISL_L = 110.9375                           # FOR's vectors y 273.54 to 439.92 = 166.38 pt = 110.92, 9'-2-15/16" (FOR's string 9'-3")
B.ISL_CAB = B.ISL_L - 2 * B.WF               # 107 between the 2" waterfalls
B.ISL_N = fy(273.54)                         # 67.0, FOR's north end: 3'-6" to the north run, its center 1/16" south of the range axis
ISL_SHIFT = 4.625                            # coordinator 11.06.26: the island moved east of FOR's 5'-7" so the range front to the island top is 42" (NKBA)
B.ISL_X = round(fx(456.72) * 16) / 16 + 1.0 + ISL_SHIFT   # 72.625 cabinet face, top edge 71.625 = 29.625 range depth + 42
B.ISL_BAYS = (35.25, B.SINK_CAB, B.DW_W, 11.6875)   # drawers, sink, dishwasher, trash = 106-15/16
B.SINK_CL = B.WF + B.ISL_BAYS[0] + B.SINK_CAB / 2  # 55.25, 1/4" north of the island center (the range axis)
B.APPLIANCES = [r if r[0] != 'A12' else ('A12', 'PANTRY SINK, 30" SINGLE BOWL UNDERMOUNT', 'ALLOWANCE', '30 x 18 x 10, 33" CABINET', 'DISPOSAL 120V, WALL FAUCET (FOR)')
                for r in B.APPLIANCES]
B.APPLIANCES = [r if r[0] != 'A9' else ('A9', 'MICROWAVE DRAWER, 30"', 'WOLF MD30 OR EQUAL', '30 x 16 x 23', 'IN THE PANTRY RUN (OWNER), 120V 15A') for r in B.APPLIANCES]
B.APPLIANCES = [r if r[0] != 'A10' else ('A10', 'UNDERCOUNTER REFRIGERATOR, PANEL READY', 'SUB-ZERO DEU2450 OR EQUAL', '24 x 34 x 24', 'PANTRY EAST RUN (OWNER), 120V 15A') for r in B.APPLIANCES]
B.APPLIANCES = [r if r[0] != 'A11' else ('A11', 'DISHWASHER 2, PANEL READY', 'MIELE G 7000 OR EQUAL', '24 x 34 x 24', 'PANTRY, BY THE SINK (OWNER), 120V 15A') for r in B.APPLIANCES]

from build_kitchen import (H, CR, CS, TOP, KD, TALL_D, BASE_D, RC, RANGE_W, RANGE_D, BREAST_W, BREAST_D, COL_W, S_TALL, NOTE, NOTE_LH, WHITE, WALL, PT,
                           W_FACE, N_FACE, S_FACE, ISL_X, ISL_N, ISL_W, ISL_L, ISL_CAB, WF, OV, ISL_TOP, ISL_BAYS, SINK_CL, SINK_W, SINK_CAB, DW_W, AISLE,
                           shell, base_run, tag, wrap, draw_views, para_block, draw_schedule, floor_line, Plan)

OUT = '/home/claude/flrwork/261105.HD102.KitchenPilot.pdf'
# ---- dimensions to 1/16" on these sheets (FOR's 20'-4-15/16" wall), run time only: idd_elevations is not edited
def _ftin16(inches):
    inches = round(inches * 16) / 16
    f = int(inches // 12); i = inches - 12 * f
    if abs(i - round(i)) < 1e-6: s = f'{int(round(i))}"'
    else:
        whole = int(i); num = int(round((i - whole) * 16)); den = 16
        while num % 2 == 0 and num: num //= 2; den //= 2
        s = f'{whole}-{num}/{den}"' if (whole or f) else f'{num}/{den}"'
    return f"{f}'-{s}" if f else s
def _snap16(pts, tol=1.0):
    pts = sorted(set(round(v * 16) / 16 for v in pts))
    if len(pts) < 2: return pts
    out = [pts[0]]
    for v in pts[1:-1]:
        if v - out[-1] >= tol and pts[-1] - v >= tol: out.append(v)
    out.append(pts[-1])
    return out
def _check16(pts, room=None, view=None):
    r = lambda v: round(v * 16) / 16
    segs = [r(b - a) for a, b in zip(pts, pts[1:]) if b - a >= 0.5]
    overall = r(pts[-1] - pts[0]); ok = abs(sum(segs) - overall) <= 1 / 16 + 1e-6
    E.DIM_LOG.append({'room': room, 'view': view, 'segments': segs, 'overall': overall, 'ok': ok})
    assert ok, ('dimension string does not close', room, view, segs, overall)
E.ftin, E.snap_points, E.check_string = _ftin16, _snap16, _check16
ISSUE = '11.06.26'
def ft(x): return E.ftin(x)
def f32(x):                                  # a small offset to 1/32": 1/4", 1/32"
    from fractions import Fraction
    q = Fraction(round(x * 32), 32)
    return f'{q.numerator}/{q.denominator}"' if q < 1 else inch(x)
def inch(x):                                 # inches only, to 1/8": 36-1/2"
    s = E.ftin(x)
    if "'" not in s: return s
    f, r = s.split("'-"); r = r.rstrip('"')
    w, _, fr = r.partition('-'); w = int(f) * 12 + int(w)
    return f'{w}-{fr}"' if fr else f'{w}"'
# ---- the room
ROOM_W = 272.0                               # fx(764.2) = 271.99, 22'-8"
N_RUN_D = 25.0                               # FOR's north run, 2'-1" deep (y 173.04 to 210.54 = 37.5 pt)
N_RUN_E = 181.5                              # fx(628.44) = 181.48: the run ends at the jog, 15'-1-1/2"
STEP = (F_N - F_JOG_Y) / F_PT                # 24.0: the recess east of the jog (FOR: 2'-0")
N_PANTRY = 39.5                              # each pantry cabinet: 26 column + 39-1/2 + 1-1/2 panel puts the refrigerator at 5'-7" (FOR's string, vector 67.24)
N_DOOR = (207.0625, 247.0625)                # fx(666.8), fx(726.8) = 207.05 to 247.05: door 05's 40" opening in the recess back wall
N_LEAF = 36.0; N_LEAF_X = (N_DOOR[0] + N_DOOR[1]) / 2 - N_LEAF / 2   # 209.05, a 3'-0" leaf centered in it
ARCH = (197.0, 255.0)                        # fx(651.66), fx(738.66) = 196.96 to 254.96: the 4'-10" opening, 1'-5" pier to the east wall (FOR)
E_LEN = STEP + KD                            # 268.9375 ((540.42 - 137.0) / 1.5 = 268.95): the east wall, recess back wall to the south wall
SLIDER = (52.0, 241.0)                       # (215.0 - 137.0) / 1.5 = 52.0, (498.48 - 137.0) / 1.5 = 240.99: FOR's 15'-9" slider 04, 4'-4" N, 2'-3-15/16" S (FOR's string 2'-4")
SLIDER_HEAD = 96.0
# ---- the south wall, west-face coordinates
P_OPEN = (27.0, 65.0)                        # fx(396.72), fx(453.72) = 27.0 to 65.0: FOR's 3'-2" opening, 2'-3" from the west wall, center 3'-10"
DW_COL = 26.0                                # drywall column, 26 x 26, at the NW and SW corners (owner 11.03.26)
VEST = (DW_COL, P_OPEN[1])                   # 26 to 65: the vestibule in front of the wall opening, closed by the swing doors
RET = (P_OPEN[1], P_OPEN[1] + 4.0)           # 65 to 69: drywall return, the doors' east jamb
MIDS = (RET[1], RET[1] + 60.0)               # 69 to 129: drawers 30 + 30, counter, open shelving, cabinets above (owner's 5'-0")
WPIER = (ARCH[0] - CS - 12.0, ARCH[0] - CS)  # 179.96 to 191.96: 1'-0" pier west of the arch casing, as the east side (1'-5" less the 5" casing)
TALLS = (MIDS[1], WPIER[0])                  # 129 to 179.96: two tall cabinets
TALL_W = (TALLS[1] - TALLS[0]) / 2           # 25.48 each
S_RUN_D = 25.0                               # FOR's south run, 2'-1" deep (y 502.92 to 540.42)
LINING = 0.75
GAP = 0.125
LEAF_W = (VEST[1] - VEST[0] - LINING - 3 * GAP) / 2     # 18-15/16
LEAF_H = TOP - 0.5 - GAP
MSHELF = (58.0, 72.0)
UP_B, UP_T = 54.0, 84.0; UPPER_W = 24.0
# ---- the pantry, inches from its west wall face and its north wall face (the kitchen wall, pantry side)
WALL_K = 7.0                                 # (550.92 - 540.42) / 1.5 = 7.0: the kitchen to pantry wall
PAN_W = 175.3125                             # (619.2 - 356.22) / 1.5 = 175.32, 14'-7-5/16"
PAN_D = 59.375                               # (639.96 - 550.92) / 1.5 = 59.36, 4'-11-3/8"
SCRIBE = 1.5
PANTRY_WALL_Y = KD + WALL_K                  # the pantry's north wall face in kitchen coordinates
UP_D = 13.0
END_D = BASE_D + 1.0                         # 25: FOR's end runs, 2'-1"
WALKWAY = PAN_D - END_D                      # 34.375, FOR's 2'-10" (y 550.92 to 602.46)
S_FACE_P = PAN_D - BASE_D                    # 35.375: the south run's cabinet face from the north wall
W_BAYS = (('', 0.75, 'scribe'), ('A12', 33.0, 'sink'), ('', S_FACE_P - 33.75, 'filler'))   # 33" sink cabinet, CL 17-1/4" (FOR: 576.69 - 550.92 = 17.2), filler 1-5/8"
E_BAYS = (('', 1.25, 'scribe'), ('A10', 24.0, 'uc'), ('', S_FACE_P - 26.25, 'tray'), ('', 1.0, 'filler'))   # tray 9-1/8"
S_RUN = (BASE_D, PAN_W - BASE_D)
S_BAYS = (('', 4.0, 'filler'), ('', 24.0, 'drawers'), ('A11', 24.0, 'dw'), ('A9', 30.0, 'mw'), ('', 15.0, 'pullout'),   # A11 and the 24 in. drawers swapped (review 11.06.26): the dishwasher 27 in. clear of the west run's counter edge
          ('', S_RUN[1] - S_RUN[0] - 4.0 - 24 - 24 - 30 - 15 - 4.0, 'drawers'), ('', 4.0, 'filler'))     # 26-5/16 drawers
S_UP = (UP_D, PAN_W - UP_D)
S_UP_BAYS = ((15.0, 1), (24.0, 2), (69.0, 'shelf'), (S_BAYS[5][1], 2), (15.0, 'R'))
W_UP_BAYS = ((0.75, 0), (33.0, 2), (S_FACE_P + BASE_D - UP_D - 33.75, 1))     # 12-5/8 single at the corner
E_UP_BAYS = ((1.25, 0), (36.0, 'wine'), (PAN_D - UP_D - 37.25, 'R'))          # 9-1/8 single at the corner
PSINK_CL = W_BAYS[0][1] + 16.5               # 17.25 from the north wall
FOR_DWMW = (66.5, 90.5)                      # fx(455.88), fx(491.88) = 66.44 to 90.44          # FOR's 24" "DW & MW" bay, 5'-6-1/2" to 7'-6-1/2" (not followed, see ID-745)
FOR_UCF = (94.75, 118.75)                    # fx(498.36), fx(534.36) = 94.76 to 118.76           # FOR's UC fridge on the south run, 7'-10-3/4" to 9'-10-3/4"
SEC = (0.88, 0.88, 0.88)
# ---- work triangle and aisles (center front to center front)
import math
RANGE_Y = KD - RC                            # 122.5: ID-742 draws the range RC from the SOUTH corner, so in plan (y from the north) it is here
TRI_R = (RANGE_D, RANGE_Y); TRI_S = (ISL_X - 1.0, ISL_N + SINK_CL); TRI_F = (DW_COL + N_PANTRY + 1.5 + COL_W / 2, N_RUN_D)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
LEG_RS, LEG_RF, LEG_FS = dist(TRI_R, TRI_S), dist(TRI_R, TRI_F), dist(TRI_F, TRI_S)
AISLE_RANGE = ISL_X - 1.0 - RANGE_D          # 37.375 range front to the island top
AISLE_W = ISL_X - 1.0 - (BASE_D + 1.0)       # 42 west counter edge to the island top
AISLE_N = ISL_N - N_RUN_D                    # 41.97 north run face to the island
AISLE_S = KD - S_RUN_D - (ISL_N + ISL_L)     # 42 island to the south counter edge
_rx = RC - RANGE_W / 2
W_STACKS_S = (_rx - S_TALL - 36.25, 36.25)   # 36-3/16 at the column, 36-1/4 at the range: within 1/16 of the north side
W_STACKS_N = ((KD - TALL_D - _rx - RANGE_W) / 2,) * 2   # 36-1/4 and 36-1/4
W_OUTLETS = tuple(RC + d * o for o in (86.4375, 60.0, BREAST_W / 2 + 3) for d in (-1, 1))   # mirrored about the range: 10 in. off the columns, 5'-0" and 2'-9" off the axis (3 in. outboard of the seams)
# pantry receptacles (NEC 210.52(C)(1)): along the counter wall line W, S, E no point more than 24 in. from one, a GFCI within 24 in. of each corner and run end
P_OUT_W = (4.5, 46.0)                        # west wall, from the north wall: north of the faucet levers, and in the SW corner (13-3/8 from it)
P_OUT_S = (18.0, 62.0, 106.0, 152.0)         # south wall, from the west wall: 44, 44, 46 apart, 18 and 23-5/16 from the corners
P_OUT_E = (12.0, 46.0)                       # east wall, from the north wall: over the beverage refrigerator, and in the SE corner
DIN_CLEAR = ROOM_W - 36.0 - 42.0 - (ISL_X - 1.0 + ISL_TOP)   # island top edge to a 42 in. table with 36 in. of chair room at the slider
PEND_X = ISL_X - 1.0 + ISL_TOP / 2           # the island's long axis
PEND_Y = tuple(ISL_N + ISL_L / 2 + d for d in (-33.0, 0.0, 33.0))

def grain(v, x0, y0, x1, y1):
    """Veneer: three light wavy grain lines across a door."""
    import math
    n = 3; h = y1 - y0
    for i in range(n):
        yy = y0 + h * (i + 1) / (n + 1)
        pts = [(x0 + 1.5 + (x1 - x0 - 3) * t / 12, yy + 0.6 * math.sin(t * 1.3 + i)) for t in range(13)]
        C._poly(v, pts, C.FINE, C.PALE, close=False)

def veneer_door(v, x, w, y0, y1, glass=False, pull='bar', hinge='L'):
    K._rect(v, x, y0, x + w, y1, K.OUTLINE); K.frame_opening(v, x + K.STILE, y0 + K.STILE, x + w - K.STILE, y1 - K.STILE)
    if glass: K._rect(v, x + K.STILE + 2.5, y0 + K.STILE + 2.5, x + w - K.STILE - 2.5, y1 - K.STILE - 2.5, K.FINE, MID); C._line(v, (x + 4, y1 - 6), (x + w * 0.45, y0 + 5), C.FINE, C.PALE)
    else: grain(v, x + K.STILE, y0 + K.STILE, x + w - K.STILE, y1 - K.STILE)
    px = x + w - K.STILE - 2.2 if hinge == 'L' else x + K.STILE + 2.2
    if pull == 'bar': K._line(v, (px, (y0 + y1) / 2 - 3), (px, (y0 + y1) / 2 + 3), K.OUTLINE)
    elif pull == 'long': K._line(v, (px, 30), (px, 66), K.OUTLINE); K._line(v, (px - 0.6, 30), (px - 0.6, 66), K.FINE, MID)

# ================================================================== north wall (looking north, west at the left): alcove run, wall, hall door
def north_wall(v):
    L = ROOM_W; RE = N_RUN_E
    shell(v, L, crown=[(0, L)], base=[(RE, N_LEAF_X - CS), (N_LEAF_X + N_LEAF + CS, L)])
    pantry_w = (RE - DW_COL - 2 * COL_W - 4.5) / 2                    # 39.49 each, between the drywall column and the jog
    C._line(v, (DW_COL, 0), (DW_COL, H - CR), C.OUTLINE)            # the NW drywall column, 1 in. proud of the run face
    def R(a, b, y0, y1): C._rect(v, a, y0, b, y1, C.OUTLINE, fill=SEC)   # the range wall run in front of it, cut (grey), as at the SW (ID-743)
    R(0, BASE_D - 3, 0, K.TOE); R(0, BASE_D, K.TOE, K.BOX_TOP); R(0, BASE_D + 1, K.BOX_TOP, K.COUNTER); R(0, 0.75, K.COUNTER, TOP)
    for y in B.SHELF_Y: R(0, 12.0, y, y + B.SHELF_T)
    tag(v, 12.5, 20, 'RANGE RUN, CUT', 5.0, MID)
    tag(v, DW_COL / 2, 66, 'DRYWALL', 5.0, INK, box=True); tag(v, DW_COL / 2, 60, 'COLUMN', 5.0, INK, box=True)
    x = DW_COL
    segs = [('P', pantry_w), ('panel', 1.5), ('R', COL_W), ('panel', 1.5), ('F', COL_W), ('panel', 1.5), ('P', pantry_w)]
    for kind, w in segs:
        if kind == 'P':
            K._rect(v, x, 0, x + w, TOP, K.OUTLINE); K.toe(v, x, x + w); dw = (w - 3 * K.STILE) / 2
            for i in range(2):
                dx = x + K.STILE + i * (dw + K.STILE); hinge = 'L' if i == 0 else 'R'
                veneer_door(v, dx - K.STILE, dw + 2 * K.STILE, K.TOE, UP_T, hinge=hinge)
                veneer_door(v, dx - K.STILE, dw + 2 * K.STILE, UP_T, TOP, hinge=hinge)
        elif kind == 'panel': K._rect(v, x, 0, x + w, TOP, K.MED)
        else:
            K._rect(v, x, 0, x + w, UP_T, K.OUTLINE); K.toe(v, x, x + w)
            veneer_door(v, x, w, K.TOE, UP_T, pull='long', hinge='L' if kind == 'R' else 'R')
            dw = (w - 3 * K.STILE) / 2
            for i in range(2): veneer_door(v, x + i * (dw + K.STILE), dw + 2 * K.STILE, UP_T, TOP, glass=True, hinge='L' if i == 0 else 'R')
            tag(v, x + w / 2, 60, 'A3 REFRIGERATOR' if kind == 'R' else 'A4 FREEZER', 5.0, INK, box=True)
        x += w
    C._line(v, (RE, 0), (RE, TOP), C.HEAVY)                         # the run's finished end at the jog
    C._line(v, (RE, TOP), (RE, H - CR), C.OUTLINE)                  # the jog corner above it, the recess 24 in. beyond
    tag(v, (RE + N_LEAF_X - CS) / 2, 104, '24" RECESS', 5.0, MID, box=True)
    C.casing(v, N_LEAF_X, N_LEAF, 96.0); C.door_leaf(v, N_LEAF_X, N_LEAF, 96.0, panels='glass', swing='R')
    tag(v, N_LEAF_X + N_LEAF / 2, 105, 'DOOR 05', 5.0, MID, box=True)         # over the head casing, clear of the leaf
    C.switch(v, N_LEAF_X - CS - 4, 48, 'S'); C.switch(v, N_LEAF_X - CS - 8, 48, 'D')
    f0 = DW_COL + pantry_w + 1.5; c0 = f0 + COL_W + 1.5
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, DW_COL, DW_COL + pantry_w, f0, f0 + COL_W, c0, c0 + COL_W, c0 + COL_W + 1.5, RE, N_LEAF_X - CS, N_LEAF_X, N_LEAF_X + N_LEAF, N_LEAF_X + N_LEAF + CS, L], tol=0.5))
    v.dim_h(0, L, v.Y(0) + 27, [0, RE, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, UP_T, 96, 96 + CS, TOP, H]))
    return ('NORTH WALL, LOOKING NORTH, WEST AT THE LEFT. THE REFRIGERATOR RUN SITS ON THE MAIN NORTH FACE FROM THE WEST WALL TO THE JOG '
            f'AT {ft(RE)}, 25" DEEP (FOR\'S 2\'-1"), IN THE OWNER\'S VENEER LANGUAGE: RIFT WHITE OAK VENEER (SPECIES AND STAIN TO PICK), FLUSH INSET DOORS. THE 24" '
            f'RECESS IS THE EAST {ft(L - RE)} BAY WITH THE EXTERIOR DOOR 05. FROM THE WEST: THE 26" x 26" DRYWALL COLUMN, PT-02, FLOOR TO CEILING WITH BASE AND CROWN, '
            'ON FOR\'S 2\'-1" CORNER BAY: IT TAKES THAT BAY AND 1" MORE, STANDS 1" PROUD OF THE RUN FACE AND OF THE RANGE RUN\'S COUNTER EDGE, AND BOTH RUNS DIE INTO '
            f'ITS SIDES (OWNER 11.03.26, ITS PAIR AT THE SW CORNER). {inch(pantry_w)} PANTRY CABINET WITH A PAIR OF TALL DOORS TOE TO 7\'-0", 1-1/2" PANEL, 36" PANEL-READY '
            f'REFRIGERATOR COLUMN A3 AT {ft(f0)} FROM THE WEST WALL, 1-1/2" PANEL, 36" FREEZER COLUMN A4, 1-1/2" PANEL, {inch(pantry_w)} PANTRY CABINET WITH A FINISHED '
            'VENEER END AT THE JOG. FOR DRAWS 3\'-6" PANTRIES AND A 6\'-0" PAIR WITHOUT PANELS: THE COLUMN AND THE OWNER\'S 1-1/2" PANELS TAKE 2-3/4" FROM EACH PANTRY, '
            'THE PAIR STARTS ON FOR\'S 5\'-7" STRING. TOP ROW 7\'-0" TO 9\'-3": SOLID VENEER OVER THE PANTRIES, FOUR GLASS DOORS WITH INTERIOR LIGHTING OVER THE '
            'REFRIGERATOR AND FREEZER. 1" SCRIBE, CROWN CM-01 CONTINUOUS OVER THE RUN, ROUND THE JOG AND ACROSS THE RECESS. RECESS BACK WALL PT-02 WITH BASE AND '
            'CROWN: THE 3\'-0" x 8\'-0" EXTERIOR DOOR 05 (FOR\'S 3\'-4" OPENING, LEAF CENTERED, FULL-LITE GLASS, 5" CASING, HINGED EAST, SWINGS OUT), KITCHEN SWITCH '
            f'AND DIMMER ON THE {ft(N_LEAF_X - CS - RE)} OF WALL WEST OF THE CASING, {ft(L - N_LEAF_X - N_LEAF - CS)} OF WALL EAST OF IT TO THE EAST WALL. THE WALL BEHIND '
            'THE RUN IS SOLID ON FOR REV 1 (STORAGE ROOMS NORTH OF IT, NO WINDOWS). APPLIANCE OUTLETS BEHIND THE REFRIGERATOR AND FREEZER, NOTHING ELSE ON THIS WALL. '
            'THE RANGE WALL RUN IS CUT (GREY) IN FRONT OF THE COLUMN.')

def arched_cased_opening(v, x, w, spring, r):
    """Cased opening with a segmental arched head: leg casings to the spring line, inner and outer arcs sharing one center."""
    import math
    cs = CS; cx = x + w / 2; cy = spring - math.sqrt(r ** 2 - (w / 2) ** 2)
    def arc(rr, xa, xb):
        a0 = math.atan2(math.sqrt(rr ** 2 - (xa - cx) ** 2), xa - cx); a1 = math.atan2(math.sqrt(rr ** 2 - (xb - cx) ** 2), xb - cx)
        return [(cx + rr * math.cos(a0 + (a1 - a0) * i / 30), cy + rr * math.sin(a0 + (a1 - a0) * i / 30)) for i in range(31)]
    inner = arc(r, x, x + w); outer = arc(r + cs, x - cs, x + w + cs)
    sp_out = cy + math.sqrt((r + cs) ** 2 - (w / 2 + cs) ** 2)
    C._rect(v, x - cs, 0, x, sp_out, C.OUTLINE); C._rect(v, x + w, 0, x + w + cs, sp_out, C.OUTLINE)
    C._poly(v, [(x, 0), (x, spring)] + inner + [(x + w, spring), (x + w, 0)], C.OUTLINE, close=False)
    C._poly(v, outer, C.OUTLINE, close=False)
    C._poly(v, arc(r + cs - 1.0, x - cs + 1.0, x + w + cs - 1.0), C.FINE, LIGHT, close=False)   # backband line
    C._line(v, (x - cs + 1.0, 0), (x - cs + 1.0, sp_out), C.FINE, LIGHT); C._line(v, (x + w + cs - 1.0, 0), (x + w + cs - 1.0, sp_out), C.FINE, LIGHT)

# ================================================================== south wall (looking south, east at the left): pier, arch, pier, tall cabinets, shelving, swing doors, column
def fake_leaf(v, x, w, hinge):  # x, w: the leaf in view inches
    """A swing door faced as cabinetry: one leaf 1/2 in. off the floor to 9'-3", the bottom 4-1/2 in. faced as the toe, grooves at 3'-0"
    and 7'-0" so it reads as the tall cabinets' three doors, a cabinet pull at the meeting stile, swing marks (the set's convention)."""
    K.toe(v, x, x + w)
    for y0, y1 in ((K.TOE, K.COUNTER), (K.COUNTER, UP_T), (UP_T, TOP)): K.single_door_cab(v, x, w, y0, y1, hinge=hinge)
    C._rect(v, x, 0.5, x + w, 0.5 + LEAF_H, C.OUTLINE)
    hx, fx = (x, x + w) if hinge == 'L' else (x + w, x)
    C._line(v, (fx, 0.5), (hx, TOP / 2), C.FINE, MID, '[2 1.5] 0'); C._line(v, (fx, 0.5 + LEAF_H), (hx, TOP / 2), C.FINE, MID, '[2 1.5] 0')   # meet at the hinge side

def tall_cab(v, x, w, hinge):
    K._rect(v, x, 0, x + w, TOP, K.OUTLINE); K.toe(v, x, x + w)
    for y0, y1 in ((K.TOE, K.COUNTER), (K.COUNTER, UP_T), (UP_T, TOP)): K.single_door_cab(v, x, w, y0, y1, hinge=hinge)

def south_wall(v):
    L = ROOM_W
    def X(w): return L - w                                              # plan inches from the west wall to view inches (east at the left)
    shell(v, L, crown=[(0, L)], base=[(0, X(ARCH[1] + CS)), (X(WPIER[1]), X(WPIER[0])), (X(RET[1]), X(RET[0]))])
    # arched opening to the hall, cased, segmental head, a 12 in. pier each side
    ax, aw = X(ARCH[1]), ARCH[1] - ARCH[0]
    arched_cased_opening(v, ax, aw, 86.0, aw * 0.62)
    tag(v, ax + aw / 2, 50, 'OPENING TO THE LIVING ROOM', 5.0, MID, box=True)
    C.switch(v, X(WPIER[1]) + 3.5, 48, 'S'); C.switch(v, X(WPIER[1]) + 8.5, 48, 'D')     # kitchen switch and dimmer on the west pier
    # two tall cabinets, 24 x 24, pulls meeting at the center
    t0 = X(TALLS[1]); tall_cab(v, t0, TALL_W, 'L'); tall_cab(v, t0 + TALL_W, TALL_W, 'R')
    tag(v, t0 + TALL_W / 2, 60, 'TALL CABINETS', 5.0, INK, box=True)
    # the shelving section: drawers, counter, slab to the cabinets above, two lit stone shelves, cabinets 7'-0" to 9'-3"
    m0, m1 = X(MIDS[1]), X(MIDS[0])
    base_run(v, m0, m1, [(30.0, 'drawers'), (30.0, 'drawers')]); K.counter(v, m0, m1)
    slab_clear(v, m0, m1, K.COUNTER, UP_T, keep=[((m0 + m1) / 2 - 14, (m0 + m1) / 2 + 14)])   # veins clear of the tag
    for y in MSHELF:
        K.floating_shelf(v, m0, m1 - m0, y, B.SHELF_T); C._line(v, (m0 + 2, y - 0.4), (m1 - 2, y - 0.4), C.FINE, LIGHT, '[1.5 1.5] 0')
    K.single_door_cab(v, m0, 30.0, UP_T, TOP, hinge='L'); K.single_door_cab(v, m0 + 30.0, 30.0, UP_T, TOP, hinge='R')
    K.light_rail(v, m0, m1, UP_T)
    tag(v, (m0 + m1) / 2, 66, 'OPEN SHELVES, LIT', 5.0, INK, box=True)
    for ox in (m0 + 12, m1 - 12): K.outlet_splash(v, ox)
    # the drywall return, the doors' east jamb
    C._rect(v, X(RET[1]), 0, X(RET[0]), H - CR, C.OUTLINE)
    # the pantry entrance: a pair of swing doors faced as cabinetry, closing the vestibule
    lx = X(VEST[1]) + GAP; fake_leaf(v, lx, LEAF_W, 'L'); fake_leaf(v, lx + LEAF_W + GAP, LEAF_W, 'R')
    C._rect(v, X(VEST[0] + LINING), 0, X(VEST[0]), TOP, C.FINE)                    # the jamb lining on the column
    tag(v, X((VEST[0] + VEST[1]) / 2), 30, f'SWING DOORS, PAIR {ft(VEST[1] - VEST[0])}', 5.0, INK, box=True)
    lx_ = X(DW_COL * 0.55)                                                          # on the SW column face, clear of the leaves, with a leader (review 11.07.26)
    tag(v, lx_, 47, 'WALL OPENING', 5.0, MID); tag(v, lx_, 42.5, '3\'-2" BEHIND', 5.0, MID)
    wl = FREG.text_length('WALL OPENING', fontsize=5.0) / v.k
    ex = lx_ - wl / 2 - 1.5 if X(VEST[1]) < lx_ else lx_ + wl / 2 + 1.5
    C._line(v, (ex, 45.5), (X((VEST[0] + VEST[1]) / 2), 23), C.FINE, MID)
    sh_ = v.p.new_shape(); sh_.draw_circle(fitz.Point(v.X(X((VEST[0] + VEST[1]) / 2)), v.Y(23)), 1.2); sh_.finish(color=MID, fill=MID, width=0.3); sh_.commit()
    C._line(v, (X(VEST[1]), TOP), (X(VEST[0]), TOP), C.OUTLINE)                       # the head, 9'-3", fascia above
    # the SW drywall column, its face above the range wall run, which the view cuts below the counter (grey)
    c0 = X(DW_COL)
    C._line(v, (c0, 0), (c0, H - CR), C.OUTLINE)
    def R(a, b, y0, y1): C._rect(v, X(b), y0, X(a), y1, C.OUTLINE, fill=SEC)
    R(0, BASE_D - 3, 0, K.TOE); R(0, BASE_D, K.TOE, K.BOX_TOP); R(0, BASE_D + 1, K.BOX_TOP, K.COUNTER); R(0, 0.75, K.COUNTER, TOP)
    for y in B.SHELF_Y: R(0, 12.0, y, y + B.SHELF_T)                                   # the range wall shelves, cut
    tag(v, c0 + DW_COL / 2, 66, 'DRYWALL', 5.0, INK, box=True); tag(v, c0 + DW_COL / 2, 60, 'COLUMN', 5.0, INK, box=True)
    tag(v, X(12.5), 20, 'RANGE RUN, CUT', 5.0, MID)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, X(ARCH[1] + CS), ax, ax + aw, X(ARCH[0] - CS), X(WPIER[0]), t0 + TALL_W, X(TALLS[0]), m0 + 30, m1,
                                               X(RET[0]), X(VEST[0]), L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.COUNTER, 42, MSHELF[0], MSHELF[1], UP_T, TOP, H]))
    return ('SOUTH WALL, LOOKING SOUTH, EAST AT THE LEFT, ON FOR REV 1 (OWNER COMMENTS 11.03.26 KEPT). FROM THE EAST: 1\'-0" PIER (FOR\'S 1\'-5" LESS THE '
            '5" CASING), THE 4\'-10" OPENING TO THE LIVING ROOM CASED WITH A SEGMENTAL ARCHED HEAD (SPRING 7\'-2", CROWN 8\'-4-3/4", FOR\'S OPENING, VERIFY THE HEAD, '
            'THE ARCH IS TRIM), THEN A 1\'-0" WALL PIER TO MATCH THE EAST SIDE (KITCHEN SWITCH AND DIMMER ON IT, CL 4\'-0"), THEN TWO '
            f'{inch(TALL_W)} x 24" TALL CABINETS TOE TO 9\'-3", PAINTED INSET, SINGLE DOORS SPLIT AT 3\'-0" AND 7\'-0", PULLS MEETING AT THE CENTER. THEN 5\'-0" OF '
            'SHELVING: TWO 30" INSET DRAWER STACKS, ST-03 COUNTER 25" DEEP (FOR\'S 2\'-1" RUN), SLAB SPLASH FROM THE COUNTER TO 7\'-0", TWO 2" x 12" DEEP ST-03 '
            'FLOATING SHELVES THE FULL 5\'-0" BETWEEN THE TALL CABINET SIDE AND THE RETURN, UNDERSIDES AT 4\'-10" AND 6\'-0", ON STEEL RODS INTO BLOCKING IN THE '
            'PANTRY WALL, LED IN THE FRONT EDGES, TWO 30" DOORS 7\'-0" TO 9\'-3", 24" DEEP AND FLUSH WITH THE TALL CABINETS SO THE SHELVING READS AS A NICHE, A LIGHT '
            'RAIL UNDER THEM, THE LED DRIVERS IN THAT UPPER CABINET, TWO GFCI CL 3\'-6". FOR\'S 3\'-0" BUILT-IN OVEN (14\'-0" TO 17\'-0" FROM THE EAST WALL) IS '
            'DROPPED (OWNER 11.06.26, THE OVENS STAY UNDER THE RANGE) AND FOR\'S 6\'-5" BAR IS THIS SHELVING AND THE TALL CABINETS. THEN A 4" PAINT-GRADE MILLWORK '
            'RETURN BY THE CABINETMAKER (3/4" PLYWOOD SKINS ON SOLID BLOCKING, ANCHORED TO THE WALL AND FLOOR) FROM THE CABINET FACE TO THE WALL, THE DOORS\' EAST '
            'JAMB. THEN THE PANTRY ENTRY: A PAIR OF ONE-WAY SWING DOORS IN THE CABINET FACE PLANE, EACH LEAF '
            f'{inch(LEAF_W)} x {ft(LEAF_H)} x 1-3/4" (PAINT-GRADE MDF CORE, HARDWOOD EDGES, BALANCED BOTH FACES), 1/2" UNDERCUT, 1/8" GAPS, FACED AS CABINETRY: THE '
            'TALL CABINETS\' 3\'-0" AND 7\'-0" BREAKS ROUTED IN, THE BOTTOM 4-1/2" FINISHED AS THE TOE, CABINET PULLS AT THE MEETING STILES, FLAT RECESSED PULLS '
            'ON THE PANTRY FACES. HINGED AT A 3/4" HARDWOOD JAMB LINING ON THE COLUMN AND AT THE RETURN, TOP AND BOTTOM PIVOTS (MILLWORKER TO PROPOSE, OWNER TO '
            'APPROVE), A 3/4" HARDWOOD HEAD JAMB WITH A STOP ON THE VESTIBULE SIDE AND MAGNETIC CATCHES, BOTTOM PIVOT PLATES SET IN WD-01, A MAGNETIC HOLD-OPEN ON '
            f'EACH SIDE. THEY SWING INTO A {ft(VEST[1] - VEST[0])} x 2\'-0" VESTIBULE AND PARK AGAINST ITS SIDES, BEHIND THEM FOR\'S 3\'-2" x 8\'-1" WALL OPENING, '
            f'{ft(P_OPEN[0])} TO {ft(P_OPEN[1])} FROM THE WEST WALL (CENTER {ft(sum(P_OPEN) / 2)}), WITH DRYWALL RETURNS AND NO DOOR, IN PLACE OF FOR\'S HIDDEN '
            'MILLWORK DOOR 17. A HEADER AT 9\'-3" WITH DRYWALL ABOVE TO THE CEILING CARRIES THE CROWN OVER THE LEAVES. THEN THE 26" x 26" DRYWALL COLUMN IN THE SW '
            'CORNER (OWNER 11.03.26), PT-02, 2" PROUD OF THE CABINET FACE AND 1" PROUD OF THE COUNTER EDGE, SEEN ABOVE THE RANGE WALL RUN AND ITS SHELVES, WHICH '
            'THE VIEW CUTS (GREY). CROWN CM-01 CONTINUOUS, 1" SCRIBE OVER THE CABINETS, 8-1/2" BASE ON THE PIERS AND THE RETURN. ALL CABINET AND LEAF FACES SOLID '
            'PAINTED: THE LEAVES CANNOT BE GLASS, SO THE WALL READS AS ONE PIECE OF MILLWORK.')

# ================================================================== east wall (looking east, north at the left): FOR's slider, drapery pocket
def east_wall(v):
    L = E_LEN
    shell(v, L, crown=[(0, L)], base=[(0, SLIDER[0]), (SLIDER[1], L)])
    x0, x1 = SLIDER
    C._rect(v, x0 - 1, 0, x1 + 1, SLIDER_HEAD + 1, C.OUTLINE)             # drywall return into the jamb and head, no casing
    pw = (x1 - x0) / 4
    for i in range(4):
        px = x0 + i * pw
        C._rect(v, px, 0.5, px + pw, SLIDER_HEAD, C.OUTLINE); C._rect(v, px + 2.5, 3, px + pw - 2.5, SLIDER_HEAD - 2.5, C.MED)
        C._line(v, (px + 5, SLIDER_HEAD - 8), (px + pw * 0.45, 40), C.FINE, C.PALE); C._line(v, (px + 9, SLIDER_HEAD - 8), (px + pw * 0.55, 40), C.FINE, C.PALE)
    C._rect(v, x0 + 2 * pw - 1.2, 34, x0 + 2 * pw - 0.2, 46, C.OUTLINE); C._rect(v, x0 + 2 * pw + 0.2, 34, x0 + 2 * pw + 1.2, 46, C.OUTLINE)   # meeting stile pulls
    C._rect(v, x0 - 14, H - 4, x1 + 14, H, C.FINE, MID, dashes='[2 1.5] 0')  # drapery pocket, stacks clear of the glass
    C.outlet(v, x0 / 2, 18); C.outlet(v, (x1 + L) / 2, 18)
    tag(v, (x0 + x1) / 2, 104, 'DRAPERY POCKET 4" x 4", N.I.C. DRAPERY', 5.0, MID, box=True)
    tag(v, x0 + 1.5 * pw, 50, 'FOR SLIDER, 4 PANELS', 5.0, MID, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, x0 - 14, x0, x0 + pw, x0 + 2 * pw, x0 + 3 * pw, x1, x1 + 14, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SLIDER_HEAD, H]))
    return (f'EAST WALL, LOOKING EAST, NORTH AT THE LEFT, {ft(L)} FROM THE RECESS BACK WALL TO THE SOUTH WALL. FOR\'S {ft(x1 - x0)} FOUR-PANEL SLIDER 04 '
            f'(FOUR EQUAL PANELS, {ft((x1 - x0) / 4)} NOMINAL, HEAD 8\'-0" ASSUMED, VERIFY), {ft(x0)} FROM THE RECESS BACK WALL AND {ft(L - x1)} FROM THE SOUTH WALL, '
            'DRYWALL RETURNS INTO THE JAMBS AND HEAD, NO CASING, SLAB SILL FLUSH WITH THE FLOOR (FOR). INTERIOR SCOPE: A 4" x 4" DRAPERY POCKET IN THE CEILING THE '
            'WIDTH OF THE SLIDER PLUS 14" EACH SIDE (STACKS CLEAR OF THE GLASS), ITS WALL SIDE 8" OFF THE WALL SO THE 7-1/4" CROWN PROJECTION CLEARS IT AND CM-01 '
            'RUNS CONTINUOUS (SHOWN DASHED IN PROJECTION, SEE THE MASTER BEDROOM POCKET DETAIL), DRAPERY N.I.C., 8-1/2" BASE RETURNING INTO THE JAMBS, PT-02 WALL. '
            'ONE DUPLEX OUTLET VERTICAL CL 1\'-6" IN EACH WALL SEGMENT BESIDE THE SLIDER (NEC 210.52(A), BOTH SEGMENTS ARE OVER 2\'-0"). PENDANTS AND DOWNLIGHTS ON THE RCP.')

# ================================================================== pantry
def lower_bays(v, x0, bays):
    """Base cabinets from x0 in the given (tag, width, kind) bays, toe continuous; returns the bay lines."""
    K.toe(v, x0, x0 + sum(w for _, w, _ in bays)); cx = x0; xs = []
    for tagname, w, kind in bays:
        xs.append(cx)
        if kind == 'drawers': K.drawer_stack(v, cx, w, 3)
        elif kind == 'sink': K.sink_cab(v, cx, w)
        elif kind == 'dw': K._rect(v, cx, K.TOE, cx + w, K.BOX_TOP, K.OUTLINE); K.frame_opening(v, cx + K.STILE, K.TOE + K.STILE, cx + w - K.STILE, K.BOX_TOP - K.STILE); K._line(v, (cx + w / 2 - 8, K.BOX_TOP - 4), (cx + w / 2 + 8, K.BOX_TOP - 4), K.OUTLINE)
        elif kind == 'uc': K.single_door_cab(v, cx, w, K.TOE, K.BOX_TOP, hinge='R')          # panel-ready door, hinged at the right as drawn (south on the east wall)
        elif kind == 'mw':
            K._rect(v, cx, K.TOE, cx + w, K.BOX_TOP, K.OUTLINE); K.frame_opening(v, cx + K.STILE, K.BOX_TOP - 18, cx + w - K.STILE, K.BOX_TOP - K.STILE)
            K._rect(v, cx + K.STILE + 1, K.BOX_TOP - 17, cx + w - K.STILE - 1, K.BOX_TOP - 3, K.FINE, MID); K.frame_opening(v, cx + K.STILE, K.TOE + K.STILE, cx + w - K.STILE, K.BOX_TOP - 20)
            K._line(v, (cx + w / 2 - 6, K.BOX_TOP - 20 - 6), (cx + w / 2 + 6, K.BOX_TOP - 20 - 6), K.OUTLINE)
        elif kind in ('pullout', 'tray'): K.single_door_cab(v, cx, w, K.TOE, K.BOX_TOP)      # one tall front, one pull
        elif kind in ('filler', 'scribe'): K._rect(v, cx, K.TOE, cx + w, K.BOX_TOP, K.OUTLINE)
        if tagname: tag(v, cx + w / 2 + (w / 4 if kind == 'sink' else 0), 12 if kind != 'mw' else 24, tagname, 5.5, INK, box=True)
        cx += w
    xs.append(cx)
    return xs

def upper_bays(v, x0, bays):
    """Uppers 4'-6\" to 9'-3\": one tall lit glass door per bay (study 4, owner 11.02.26); the open bays (shelving, wine rack) stop at 7'-0\" with the glass transom row over them. Returns the lines."""
    cx = x0; xs = []
    for w, n in bays:
        xs.append(cx)
        if n == 0: K._rect(v, cx, UP_B, cx + w, TOP, K.OUTLINE)                           # scribe
        elif n == 'wine': wine_rack(v, cx, w, UP_B, UP_T); K.door_pair_cab(v, cx, w, UP_T, TOP, glass=True)
        elif n == 'shelf': shelving(v, cx, cx + w, UP_B, UP_T, (63.0, 73.0)); K.door_pair_cab(v, cx, w / 2, UP_T, TOP, glass=True); K.door_pair_cab(v, cx + w / 2, w / 2, UP_T, TOP, glass=True)
        elif n in (1, 'R'):
            hg = 'R' if n == 'R' else 'L'
            K.single_door_cab(v, cx, w, UP_B, TOP, hinge=hg, glass=True); glass_inside(v, cx, w, UP_B, TOP, 1, TALL_SHELVES)
        else: K.door_pair_cab(v, cx, w, UP_B, TOP, glass=True); glass_inside(v, cx, w, UP_B, TOP, 2, TALL_SHELVES)
        cx += w
    xs.append(cx)
    K.light_rail(v, x0, cx, UP_B)
    return xs

TALL_SHELVES = (10.0, 21.0, 32.0, 43.0)   # glass shelves above the bottom of a tall upper (54): 64, 75, 86, 97

def shelving(v, x0, x1, y0, y1, shelves):
    """A painted open niche between cabinet sides: back panel, 1-1/4 in. shelves with an LED channel at the front edge, no doors."""
    C._rect(v, x0, y0, x1, y1, C.OUTLINE)
    C._rect(v, x0 + 0.75, y0 + 0.75, x1 - 0.75, y1 - 0.75, C.FINE, MID)
    for y in shelves:
        K.floating_shelf(v, x0 + 0.75, x1 - x0 - 1.5, y, 1.25)
        C._line(v, (x0 + 2, y - 0.4), (x1 - 2, y - 0.4), C.FINE, LIGHT, '[1.5 1.5] 0')

def glass_inside(v, x, w, y0, y1, n, shelves=(10.0, 20.0)):
    """Glass shelves and the top LED, drawn light inside each door's glass."""
    dw = (w - 3 * K.STILE) / 2 if n == 2 else w - 2 * K.STILE
    for i in range(n):
        dx = x + K.STILE + i * (dw + K.STILE); g0, g1 = dx + K.STILE + 0.8, dx + dw - K.STILE - 0.8
        for dy in shelves: C._line(v, (g0, y0 + dy), (g1, y0 + dy), C.FINE, LIGHT)
        C._line(v, (g0, y1 - 2 * K.STILE - 0.6), (g1, y1 - 2 * K.STILE - 0.6), C.FINE, LIGHT, '[1.5 1.5] 0')

def glass_upper(v, x, w, y0=None, y1=None):
    y0 = UP_B if y0 is None else y0; y1 = UP_T if y1 is None else y1
    K.door_pair_cab(v, x, w, y0, y1, glass=True); glass_inside(v, x, w, y0, y1, 2)

def cut_run(v, x_wall, d):
    """A perpendicular run cut by the view at the wall x_wall, extending in direction d (+1 right, -1 left): base, slab, splash, uppers to the ceiling, grey."""
    def R(a, b, y0, y1): C._rect(v, min(x_wall + d * a, x_wall + d * b), y0, max(x_wall + d * a, x_wall + d * b), y1, C.OUTLINE, fill=SEC)
    R(0, BASE_D - 3, 0, K.TOE); R(0, BASE_D, K.TOE, K.BOX_TOP); R(0, END_D, K.BOX_TOP, K.COUNTER); R(0, 0.75, K.COUNTER, UP_B); R(0, UP_D, UP_B, TOP)

def slab_clear(v, x0, x1, y0, y1, keep=()):
    """Stone splash panel: outline and light veining, one vein per clear stretch, none through the tags in keep (x ranges)."""
    K._rect(v, x0, y0, x1, y1, K.MED)
    edges = [x0] + [e for a, b in sorted(keep) for e in (a, b)] + [x1]
    for a, b in zip(edges[::2], edges[1::2]):
        w = b - a
        if w < 12: continue
        K._line(v, (a + w * 0.25, y1 - 3), (a + w * 0.6, y0 + 4), K.FINE, K.PALE)

def pantry_south(v):
    """Looking south inside the pantry, west at the right: the south run between the two end runs, which the view cuts. View x = PAN_W - plan x."""
    L = PAN_W
    def X(px): return L - px
    shell(v, L, crown=[(0, L)])
    xs = lower_bays(v, X(S_RUN[1]), tuple(reversed(S_BAYS)))                            # from the east end at the left
    K.counter(v, 0, L)
    niche = (X(S_UP[0] + 15.0 + 24.0 + 69.0), X(S_UP[0] + 15.0 + 24.0))                # the open niche, over A11, A9 and the trash
    cx = (niche[0] + niche[1]) / 2
    slab_clear(v, 0, L, K.COUNTER, UP_B, keep=[(cx - 18, cx + 18)])
    ux = upper_bays(v, X(S_UP[1]), ((15.0, 1), (S_BAYS[5][1], 2), (69.0, 'shelf'), (24.0, 2), (15.0, 'R')))   # corner doors hinge at the corners
    cut_run(v, 0.0, +1); cut_run(v, L, -1)
    tag(v, cx, 46, 'COFFEE STATION', 5.0, MID, box=True); tag(v, cx, 58, 'OPEN SHELVES 5\'-9", LIT', 5.0, INK, box=True)
    for ox in P_OUT_S: K.outlet_splash(v, X(ox))
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points(xs + [0, L]))
    v.dim_h(0, L, v.Y(0) + 27, E.snap_points(ux + [0, L]))
    v.dim_h(0, L, v.Y(0) + 40, [0, X(S_RUN[1]), X(S_RUN[0]), L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.COUNTER, 42, UP_B, 63, 73, UP_T, TOP, H]))
    return ('PANTRY, SOUTH WALL, LOOKING SOUTH, WEST AT THE RIGHT. FOR REV 1\'S LAYOUT: THE COUNTER WRAPS THE WEST END, THIS WALL AND THE EAST END, 25" DEEP '
            f'(FOR\'S 2\'-1"), THE NORTH WALL BARE BUT THE OPENING. THE END RUNS ARE CUT BY THE VIEW (GREY), 24" BASES WITH THE SLAB 1" PROUD, 13" UPPERS TO 9\'-3". '
            f'BETWEEN THE END BASES {ft(S_RUN[1] - S_RUN[0])} OF PAINTED INSET LOWERS FROM THE WEST: 4" FILLER UNDER THE END COUNTER\'S OVERHANG, '
            f'24" DRAWERS, 24" PANEL-READY DISHWASHER A11 ({ft(S_RUN[0] + 28.0 - END_D)} OFF THE WEST COUNTER EDGE, NKBA 21"), 30" MICROWAVE DRAWER A9 IN THE TOP OF ITS BASE WITH A '
            f'DRAWER BELOW, 15" TRASH PULL-OUT (ONE FRONT, ONE PULL), {inch(S_BAYS[5][1])} DRAWERS, 4" FILLER. THE OWNER\'S BAYS ARE KEPT, NOT FOR\'S: FOR\'S ONE 24" '
            f'"DW AND MW" BAY ({ft(FOR_DWMW[0])} TO {ft(FOR_DWMW[1])}) CANNOT HOLD THE OWNER\'S DISHWASHER AND 30" MICROWAVE DRAWER, AND THE DISHWASHER BELONGS NEAR '
            f'THE SINK (FOR\'S BAY IS {ft(FOR_DWMW[0] - END_D)} FROM THE COUNTER EDGE), FOR\'S UNDERCOUNTER REFRIGERATOR ({ft(FOR_UCF[0])} TO {ft(FOR_UCF[1])}) STAYS ON THE EAST END RUN '
            'WITH THE WINE RACK. BOTH CORNERS DEAD, 24" x 24" BOXES CLOSED BY THE FILLERS (OWNER TO SAY IF A LAZY SUSAN IS WANTED). THE PANTRY '
            'OPENING HAS NO DOOR (THE SWING DOORS ARE ON THE KITCHEN SIDE, ID-743), SO THE DISHWASHER DOOR OPENS CLEAR. APPLIANCE GRILLES AT THE TOE UNDER A10 AND '
            'A11, NO KICK PANEL THERE. COUNTER 3\'-0" ST-03 1-1/4" SLAB RUNNING AROUND THE THREE WALLS WITH MITERED CORNERS (TWO SEAMS), 3/4" SLAB SPLASH TO THE '
            'UPPERS AT 4\'-6". UPPERS TO THE CEILING, ONE TALL DOOR PER BAY (NO STACKED ROW): 13" DEEP INSET GLASS DOORS 4\'-6" TO 9\'-3" (57" TALL) WITH FOUR '
            '3/8" GLASS SHELVES AT 5\'-4", 6\'-3", 7\'-2" AND 8\'-1", LED IN THE TOP RAIL, A LIGHT RAIL BELOW, A 1" SCRIBE AND THE 8" CM-01 CROWN TO THE 10\'-0" '
            f'CEILING ON THE CABINETS. THE SOUTH UPPERS RUN BETWEEN THE END UPPERS\' FACES, {ft(S_UP[1] - S_UP[0])}, WITH A 13" DEAD BOX BEHIND EACH END UPPER: 15" '
            'SINGLE HINGED AT THE CORNER, 24" PAIR, THEN THE CENTER 5\'-9" (OVER A11, A9 AND THE TRASH) AS A PAINTED OPEN NICHE 4\'-6" TO 7\'-0" WITH A '
            'BACK PANEL AND TWO 1-1/4" SHELVES AT 5\'-3" AND 6\'-1" (LED IN THE FRONT EDGES) UNDER TWO 34-1/2" GLASS TRANSOM PAIRS 7\'-0" TO 9\'-3" (STUDY 4 A), '
            f'THEN A {inch(S_BAYS[5][1])} PAIR AND A 15" SINGLE HINGED AT THE CORNER (CORNER DOORS HINGE AT THE CORNER, PULLS AWAY FROM IT). FOUR GFCI OUTLETS CL '
            f'3\'-6" AT {", ".join(ft(x) for x in P_OUT_S)} FROM THE WEST WALL, WITHIN 24" OF THE CORNERS (NEC 210.52(C)(1)), THE COFFEE STATION UNDER THE NICHE, OVER A11, A9 AND THE TRASH (OWNER TO CONFIRM, IT WAS OVER THE DRAWERS). '
            f'WALKWAY {ft(WALKWAY)} FROM THE COUNTER EDGE TO THE NORTH WALL (FOR\'S 2\'-10", A WALKWAY, NOT A 42" WORK AISLE), {ft(PAN_W - 2 * END_D)} LONG BETWEEN '
            'THE END COUNTERS. SLAB: 1-1/4" ST-03, EASED EDGE, MITERED AT THE TWO INSIDE CORNERS (SEAMS ON THE KEY PLAN), SPLASH ON THE THREE CABINET WALLS ONLY, '
            'NO RETURN ON THE NORTH WALL. CEILING 10\'-0" ASSUMED. TWO DISHWASHERS IN THE HOUSE (A5 ISLAND, A11 HERE), OWNER TO CONFIRM. FINISHES TO BE PICKED '
            '(THE OWNER\'S REFERENCE: WARM GREIGE, POLISHED NICKEL).')

def wine_rack(v, x, w, y0, y1):
    """Lattice wine rack: a face frame and 45 degree slats on a 4-1/2 in. diamond, open to the painted wall behind."""
    import math
    C._rect(v, x, y0, x + w, y1, C.OUTLINE, fill=(1, 1, 1)); C._rect(v, x + K.STILE, y0 + K.STILE, x + w - K.STILE, y1 - K.STILE, C.MED)
    W, Hh = w - 2 * K.STILE, y1 - y0 - 2 * K.STILE
    X0, Y0 = x + K.STILE, y0 + K.STILE
    step = 4.5 * math.sqrt(2)
    c = -Hh + step / 2
    while c < W:                                              # y = x + c
        xa, xb = max(0.0, -c), min(W, Hh - c)
        if xb > xa: C._line(v, (X0 + xa, Y0 + xa + c), (X0 + xb, Y0 + xb + c), C.FINE, MID)
        c += step
    c = step / 2
    while c < W + Hh:                                         # y = -x + c
        xa, xb = max(0.0, c - Hh), min(W, c)
        if xb > xa: C._line(v, (X0 + xa, Y0 + c - xa), (X0 + xb, Y0 + c - xb), C.FINE, MID)
        c += step

def pantry_end(v, which):
    """End walls, 5'-2-1/4": the end run facing the viewer, the south run cut by the view at the south side. West: south at the left. East: south at the right."""
    L = PAN_D
    shell(v, L, crown=[(0, L)])
    K.counter(v, 0, L); K.splash_slab(v, 0, L, K.COUNTER, UP_B)                         # the end run's slab and splash wall to wall (the corner part is behind the cut)
    if which == 'W':                                                                     # north at the right: the bays in view order, from the cut
        xs = lower_bays(v, BASE_D, tuple(reversed(W_BAYS)))
        ux = upper_bays(v, UP_D, tuple(reversed(W_UP_BAYS)))
        sx = L - PSINK_CL                                                                # the sink CL in view inches
        C.faucet_wall(v, sx, K.COUNTER + 10.0)                                           # FOR's wall-mounted faucet, spout CL 10 in. over the counter
        for oy in P_OUT_W: K.outlet_splash(v, L - oy)
        cut_run(v, 0.0, +1)
    else:                                                                                # north at the left
        xs = lower_bays(v, 0.0, E_BAYS); ux = upper_bays(v, 0.0, E_UP_BAYS)
        for oy in P_OUT_E: K.outlet_splash(v, oy)
        cut_run(v, L, -1)
    v.dim_h(0, L, v.Y(0) + 18, E.snap_points(xs + [0, L], tol=1.5))                       # the lowers and the cut run (scribes under 1-1/2 in. ride with their bay)
    v.dim_h(0, L, v.Y(0) + 31, E.snap_points(ux + [0, L], tol=1.5))                       # the uppers
    v.dim_h(0, L, v.Y(0) + 44, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.COUNTER, 42, UP_B] + ([UP_T] if which == 'E' else []) + [TOP, H]))
    if which == 'W':
        return ('PANTRY, WEST END WALL, LOOKING WEST, THE SOUTH RUN CUT AT THE LEFT, THE OPENING ON THE NORTH WALL AT THE RIGHT. THE SINK WALL, PER FOR REV 1: '
                f'FROM THE NORTH WALL A {inch(W_BAYS[0][1])} SCRIBE, 33" SINK CABINET WITH A 30" x 18" SINGLE-BOWL UNDERMOUNT SINK A12 (CL {ft(PSINK_CL)} FROM THE NORTH '
                'WALL, FOR\'S 1\'-5", CUT-OUT PER THE SINK TEMPLATE), TIP-OUT FRONT, AND FOR\'S WALL-MOUNTED FAUCET (BRIDGE, LEVERS EACH SIDE, SPOUT CL 3\'-10", '
                'VALVE IN THE WALL, REACH TO THE BOWL CENTER, SO NOTHING STANDS ON THE DECK UNDER THE UPPERS), THEN A '
                f'{inch(W_BAYS[2][1])} FILLER TO THE SOUTH RUN\'S FACE LINE AND THE DEAD CORNER BEHIND IT (24" x 24", HIDDEN BY THE CUT). FOR\'S {ft(PAN_D)} DEPTH '
                'TAKES THE OWNER\'S 36" SINK CABINET DOWN TO 33". COUNTER ST-03 MITERED INTO THE SOUTH RUN\'S SLAB, 3/4" SLAB SPLASH TO 4\'-6". UPPERS TO THE CEILING '
                f'OVER THE SINK: 33" PAIR OF TALL LIT GLASS DOORS 4\'-6" TO 9\'-3" (FOUR GLASS SHELVES), A {inch(W_UP_BAYS[2][0])} TALL SINGLE HINGED AT THE CORNER '
                f'BESIDE THEM, STOPPING AT THE SOUTH UPPERS\' FACE 13" OFF THE SOUTH WALL. TWO GFCI CL 3\'-6", {ft(P_OUT_W[0])} AND {ft(P_OUT_W[1])} FROM THE NORTH WALL (NORTH OF THE FAUCET AND IN THE CORNER, NEC 210.52(C)(1)). THE OPENING\'S WEST JAMB (DRYWALL '
                f'RETURN, NO CASING) IS {inch(P_OPEN[0] - END_D)} EAST OF THE COUNTER EDGE. 1" SCRIBE AND CM-01 CROWN ON THE CABINETS, NO BASE.')
    return ('PANTRY, EAST END WALL, LOOKING EAST, THE SOUTH RUN CUT AT THE RIGHT. THE BEVERAGE WALL: FROM THE NORTH WALL A 1-1/4" SCRIBE, 24" PANEL-READY '
            'UNDERCOUNTER REFRIGERATOR A10 (DOOR HINGED SOUTH, PULL AT THE NORTH EDGE, THE SCRIBE GIVES THE HAND CLEARANCE), '
            f'{inch(E_BAYS[2][1])} VERTICAL TRAY AND BOARD PULL-OUT (ONE FRONT, ONE PULL), A 1" FILLER TO THE SOUTH '
            'RUN\'S FACE LINE AND THE DEAD CORNER BEHIND IT (24" x 24", HIDDEN BY THE CUT). COUNTER ST-03 MITERED INTO THE SOUTH RUN\'S SLAB, 3/4" SLAB SPLASH TO '
            '4\'-6". ABOVE: A 36" x 30" x 13" LATTICE WINE RACK (4-1/2" DIAMONDS, ABOUT 30 BOTTLES, OPEN TO THE PAINTED WALL) WITH A GLASS TRANSOM PAIR OVER IT TO '
            f'9\'-3" (THE OPEN BAYS CARRY THE TRANSOM ROW, THE DOOR BAYS ARE ONE TALL DOOR), A {inch(E_UP_BAYS[2][0])} TALL LIT GLASS SINGLE HINGED AT THE CORNER '
            f'BESIDE IT, STOPPING AT THE SOUTH UPPERS\' FACE. TWO GFCI CL 3\'-6", {ft(P_OUT_E[0])} AND {ft(P_OUT_E[1])} FROM THE NORTH WALL (NEC 210.52(C)(1)). 1" SCRIBE AND CM-01 CROWN ON THE CABINETS, NO BASE.')

def pantry_north(v):
    """Looking north inside the pantry, west at the left: the kitchen wall with the opening (no door: the swing doors are on the kitchen side),
    the end runs cut by the view at both ends."""
    L = PAN_W; OH = 97.0                                                 # FOR's opening 3'-2" x 8'-1"
    shell(v, L, crown=[(0, L)], base=[(P_OPEN[1], L - END_D)])
    cut_run(v, 0.0, +1); cut_run(v, L, -1)
    C._rect(v, P_OPEN[0], 0, P_OPEN[1], OH, C.OUTLINE)                  # drywall-wrapped opening, no casing
    C._line(v, (P_OPEN[0] + 1.0, 0), (P_OPEN[0] + 1.0, OH - 1.0), C.FINE, LIGHT); C._line(v, (P_OPEN[1] - 1.0, 0), (P_OPEN[1] - 1.0, OH - 1.0), C.FINE, LIGHT)
    C._line(v, (P_OPEN[0] + 1.0, OH - 1.0), (P_OPEN[1] - 1.0, OH - 1.0), C.FINE, LIGHT)
    for gx in (VEST[0] + LEAF_W,):                                      # beyond: the meeting stiles of the closed swing doors, 2'-0" past the wall
        C._line(v, (gx, 0.5), (gx, OH - 1.0), C.FINE, MID, '[2 1.5] 0')
    # swing marks of the doors beyond, solid: they swing toward this view (the set's rule), clipped to the opening
    mid = 0.5 + LEAF_H / 2; top = 0.5 + LEAF_H; gx = VEST[0] + LINING + GAP + LEAF_W
    xa, xb, yt = P_OPEN[0] + 1.0, P_OPEN[1] - 1.0, OH - 1.0
    def seg(p0, p1):
        (x0, y0), (x1, y1) = p0, p1; t0, t1 = 0.0, 1.0
        for pa, pb, lo, hi in ((x0, x1, xa, xb), (y0, y1, 0.0, yt)):
            d = pb - pa
            if abs(d) < 1e-9: continue
            ta, tb = sorted(((lo - pa) / d, (hi - pa) / d)); t0, t1 = max(t0, ta), min(t1, tb)
        if t1 > t0: C._line(v, (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1), C.FINE, MID)
    for hinge in (VEST[0] + LINING, VEST[1]):
        seg((gx, 0.5), (hinge, mid)); seg((gx, top), (hinge, mid))
    for y_, t_, tx_ in ((30, 'DOORS BEYOND', gx), (23, 'OPENING 3\'-2"', P_OPEN[1] - 1.0)):      # east of the opening, clear of the stiles and swings, with a leader
        w_ = FREG.text_length(t_, fontsize=5.0) / v.k
        tag(v, P_OPEN[1] + 6 + w_ / 2, y_, t_, 5.0, MID)
        C._line(v, (P_OPEN[1] + 5, y_ + 1.2), (tx_, y_ + 1.2), C.FINE, MID)
    C.switch(v, P_OPEN[1] + 4, 48, 'S')
    C.robe_hook(v, MIDS[1] + 8, 68) if hasattr(C, 'robe_hook') else None                 # east of the kitchen shelving's rods (72 to 132)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, END_D, P_OPEN[0], P_OPEN[1], L - END_D, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.COUNTER, UP_B, OH, TOP, H]))
    return ('PANTRY, NORTH WALL (THE KITCHEN WALL), LOOKING NORTH, WEST AT THE LEFT. FOR\'S 3\'-2" x 8\'-1" OPENING, '
            f'{ft(P_OPEN[0])} FROM THE WEST WALL (CENTER {ft(sum(P_OPEN) / 2)}), DRYWALL RETURNS INTO THE JAMBS AND HEAD, NO CASING AND NO DOOR (OWNER 11.03.26, IN '
            'PLACE OF FOR\'S HIDDEN MILLWORK DOOR 17): THE PANTRY IS CLOSED BY THE PAIR OF SWING DOORS FACED AS CABINETRY ON THE KITCHEN SIDE, 2\'-0" BEYOND THE '
            f'{inch(WALL_K)} WALL (MEETING STILES DASHED, ID-743 VIEW 3), WHICH SWING INTO THE VESTIBULE AND NOT INTO THE PANTRY. PANTRY SWITCH CL 4\'-0" 4" EAST '
            f'OF THE OPENING, A ROBE HOOK TOP AT 5\'-8" AT {ft(MIDS[1] + 8)} FROM THE WEST WALL, EAST OF THE KITCHEN SHELF RODS IN THIS WALL. THE REST OF THE WALL '
            f'STAYS BARE PT-02 WITH 8-1/2" BASE AND CROWN TO KEEP THE {ft(WALKWAY)} WALKWAY. THE END RUNS ARE CUT BY THE VIEW AT BOTH ENDS (GREY): 24" BASES, SLAB, '
            f'13" UPPERS TO 9\'-3". THE WEST RUN\'S COUNTER EDGE IS {inch(P_OPEN[0] - END_D)} WEST OF THE OPENING.')

# ================================================================== range wall and island: build_kitchen's drawings on the patched constants, notes rewritten
def west_wall(v):
    """Range wall, study 3 B (build_kitchen.west_wall, drawn here so the review fixes stay local): 26 in. columns, 48 in. range, 60 in. plaster
    breast, slab splash in three pieces (the veins stop at the breast), two lit shelves each side, outlets off the seams."""
    L = KD; tall_x = L - TALL_D; s0 = S_TALL
    rx = RC - RANGE_W / 2; bx = RC - BREAST_W / 2; bx1 = bx + BREAST_W; hx = RC - B.HOOD_W / 2
    shell(v, L, crown=[(0, L)], base=[(0, s0), (tall_x, L)])
    base_run(v, s0, rx, [(W_STACKS_S[0], 'drawers'), (W_STACKS_S[1], 'drawers')])
    base_run(v, rx + RANGE_W, tall_x, [(W_STACKS_N[0], 'drawers'), (W_STACKS_N[1], 'drawers')])
    K.counter(v, s0, rx); K.counter(v, rx + RANGE_W, tall_x)
    K.pro_range(v, rx, RANGE_W, B.RANGE_H); tag(v, RC, 14, 'A1', 5.5, INK, box=True)
    for x in (s0, tall_x): C._line(v, (x, 0), (x, H - CR), C.OUTLINE)
    for x in (0.0, tall_x): tag(v, x + TALL_D / 2, 66, 'DRYWALL', 5.0, INK, box=True); tag(v, x + TALL_D / 2, 60, 'COLUMN', 5.0, INK, box=True)
    K.splash_slab(v, s0, bx, K.COUNTER, TOP); K.splash_slab(v, bx, bx1, K.COUNTER, B.HOOD_B); K.splash_slab(v, bx1, tall_x, K.COUNTER, TOP)   # seams at the breast
    K.hood_breast(v, bx, BREAST_W, B.HOOD_B, H, style='plaster', crown_drop=CR + 1.0)
    C._rect(v, hx, B.HOOD_B, hx + B.HOOD_W, B.HOOD_B + 12, C.FINE, LIGHT, dashes='[2 2] 0')
    C._line(v, (s0, TOP), (tall_x, TOP), C.OUTLINE)
    sh_s = (s0 + B.SHELF_GAP, bx - B.SHELF_GAP); sh_n = (bx1 + B.SHELF_GAP, tall_x - B.SHELF_GAP)
    for y in B.SHELF_Y:
        for a, b in (sh_s, sh_n):
            K.floating_shelf(v, a, b - a, y, B.SHELF_T)
            C._line(v, (a + 2, y - 0.4), (b - 2, y - 0.4), C.FINE, LIGHT, '[1.5 1.5] 0')
    K.pot_filler(v, RC, 58); tag(v, RC + 21, 67, 'A8', 5.0, INK, box=True); C._line(v, (RC + 20, 65.4), (RC + 16.4, 59.6), C.FINE, MID)   # leader to the spout
    for ox in W_OUTLETS: K.outlet_splash(v, ox)
    tag(v, RC, 100, 'A2 54" LINER', 5.0, MID, box=True); tag(v, RC, 89, '60" PLASTER BREAST', 5.0, MID, box=True)
    tag(v, (sh_s[0] + sh_s[1]) / 2, 63, 'LIT SHELVES', 5.0, MID, box=True); tag(v, (sh_n[0] + sh_n[1]) / 2, 63, 'LIT SHELVES', 5.0, MID, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, s0, s0 + W_STACKS_S[0], rx, RC, rx + RANGE_W, rx + RANGE_W + W_STACKS_N[0], tall_x, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.COUNTER, 42, B.SHELF_Y[0], B.HOOD_B, TOP, H]))
    n_w = W_STACKS_N[0]
    rx = RC - RANGE_W / 2; bx = RC - BREAST_W / 2; s0 = S_TALL; L = KD
    sh_l = bx - B.SHELF_GAP - (s0 + B.SHELF_GAP)
    return (f'WEST WALL, LOOKING WEST, SOUTH AT THE LEFT, {ft(L)} (FOR REV 1). RANGE WALL STUDY 3, OPTION B (OWNER 11.02.26), COLUMNS 11.03.26. SYMMETRICAL '
            'ABOUT THE RANGE: A 26" x 26" DRYWALL COLUMN AT EACH END ON FOR\'S 2\'-1" CORNER BAYS, FLOOR TO CEILING, PT-02 WITH BASE AND CROWN, 1" PROUD OF THE '
            'COUNTER EDGE, THE NORTH ONE AT THE REFRIGERATOR RUN (ID-742 VIEW 2), THE SOUTH ONE AT THE SWING DOORS (ID-743 VIEW 3), THE COUNTERS AND THE SLAB DYING '
            f'INTO THEIR SIDES. 48" DUAL-FUEL RANGE A1 WITH ITS OVENS BELOW ON FOR\'S RANGE AXIS, {ft(RC)} FROM THE SOUTH CORNER AND {ft(KD - RC)} FROM THE NORTH (THE WALL\'S 1/16" ON THE NORTH SIDE), '
            f'{ft(bx - s0)} OF OPEN STONE WALL EACH SIDE OF THE BREAST. FOR DRAWS A 26" RANGE AND A 32" HOOD: THE 48" RANGE AND THE BREAST ARE THE OWNER\'S AND ARE '
            'LISTED FOR FOR ON ID-741. 54" HOOD LINER A2 IN A VENETIAN PLASTER BREAST 60" WIDE AND 27" DEEP (VERIFY AGAINST THE LINER\'S ENCLOSURE DRAWING), 6\'-0" '
            'TO THE CROWN. STONE SLAB SPLASH ST-03 COUNTER TO SCRIBE LINE, SEAMS AT THE BREAST ONLY. TWO 2" ST-03 FLOATING SHELVES EACH SIDE ON STEEL RODS, '
            f'{ft(sh_l)} LONG, UNDERSIDES AT 4\'-6" AND 6\'-0" (THE HOOD BOTTOM LINE), 4" CLEAR OF THE COLUMNS AND THE BREAST, EACH WITH A MILLED LED CHANNEL AT THE '
            'BACK EDGE (2700K, 90 CRI, FROSTED DIFFUSER, DIMMED WITH THE HOOD LIGHTS), FED THROUGH ONE HOLLOW ROD AND A 3/4" HOLE IN THE SLAB TO DRIVERS IN THE END '
            'BASE CABINETS (BEHIND THE BOTTOM DRAWERS, ACCESS PANEL). NO UPPER CABINETS, NO SCONCES, NO WINDOWS: FOR REV 1 STILL SHOWS TWO WEST WINDOWS, BOTH '
            'DELETED (OWNER, EXTERIOR CHANGE FOR FOR AND THE PERMIT SET). POT FILLER A8 CL 4\'-10" ON THE AXIS. INSET DRAWER STACKS '
            f'{inch(W_STACKS_S[0]).rstrip(chr(34))} AND {inch(W_STACKS_S[1]).rstrip(chr(34))} SOUTH, {inch(W_STACKS_N[0]).rstrip(chr(34))} AND {inch(W_STACKS_N[1]).rstrip(chr(34))} NORTH, 24" DEEP, 4-1/2" TOE, COUNTER '
            '3\'-0" WITH A 1-1/4" SLAB, 25" TO THE EDGE (FOR\'S 2\'-1"). SIX DUPLEX OUTLETS HORIZONTAL IN THE SPLASH CL 3\'-6", THE TWO BESIDE THE RANGE 3" OUTBOARD OF THE SLAB SEAMS (NEC 210.52(C), NONE BEHIND THE RANGE). '
            'CROWN CM-01 OVER A 1" SCRIBE.')

def island_work(v):
    """West face, looking east from the aisle, north at the left: waterfall, drawers, the sink cabinet on the range axis, dishwasher, trash, waterfall."""
    L = ISL_L; floor_line(v, 0, L)
    cx = WF; xs = []
    for w in ISL_BAYS: xs.append(cx); cx += w
    base_run(v, WF, WF + ISL_CAB, list(zip(ISL_BAYS, ('drawers', 'sink', 'dw', 'blank'))))
    K.single_door_cab(v, xs[3], ISL_BAYS[3], K.TOE, K.BOX_TOP)                           # trash front: one door, one pull
    K.counter(v, 0, L, edge=2.0); K.waterfall(v, 0, L, side='L', thick=WF); K.waterfall(v, L, L, side='R', thick=WF)
    K.miter_corner(v, 0, side='L', thick=WF); K.miter_corner(v, L, side='R', thick=WF)
    K.sink_undermount_front(v, xs[1], SINK_CAB)
    tag(v, xs[1] + SINK_CAB / 4 + 1, 18, 'A6 SINK', 5.5, INK, box=True); tag(v, xs[2] + DW_W / 2, 20, 'A5 DW', 5.5, INK, box=True); tag(v, xs[3] + ISL_BAYS[3] / 2, 12, 'TRASH', 5.0, INK, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, WF, xs[1], SINK_CL, xs[2], xs[3], WF + ISL_CAB, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, 60, v.X(L) + 14, E.snap_points([0, K.COUNTER - 2, K.COUNTER]))
    return (f'ISLAND, WORKING FACE (WEST), LOOKING EAST FROM THE AISLE, NORTH AT THE LEFT. FOR REV 1\'S ISLAND (OWNER 11.06.26): TOP {ft(ISL_L)} x {ft(ISL_TOP)} '
            f'OVERALL, ITS WEST EDGE {ft(ISL_X - 1)} FROM THE WEST WALL AND ITS NORTH END {ft(AISLE_N)} OFF THE NORTH RUN (FOR), ITS CENTER {f32(RANGE_Y - ISL_N - ISL_L / 2)} NORTH OF THE RANGE AXIS (ID-742). ST-03 3 CM (1-1/4") SLAB '
            'WITH A 2" MITERED EDGE (A 2" APRON STRIP FROM THE SAME SLAB MITERED 45 DEGREES TO THE TOP, NO JOINT ON THE FACE) ALL ROUND, AND 2" WATERFALL ENDS THE '
            f'FULL {ft(ISL_TOP)} DEPTH MITERED 45 DEGREES TO THE TOP (DIAGONAL AT EACH CORNER), CABINET {ft(ISL_CAB)} x {ft(ISL_W)} BETWEEN THE WATERFALLS, 1" BACK '
            f'FROM THE TOP\'S WORKING EDGE. FROM THE NORTH END: {inch(ISL_BAYS[0])} INSET DRAWER STACK, 36" SINK CABINET WITH A 33" SINGLE-BOWL UNDERMOUNT SINK A6 '
            f'(CL {ft(SINK_CL)} FROM THE NORTH WATERFALL FACE, {f32(RANGE_Y - ISL_N - SINK_CL)} NORTH OF THE RANGE AXIS, PULL-DOWN FAUCET), 24" PANEL-READY DISHWASHER '
            f'A5 SOUTH OF THE SINK (THE COOK STANDS BETWEEN THE RANGE AND THE SINK), {inch(ISL_BAYS[3])} TRASH PULL-OUT (ONE 35 QT BIN) AT THE SOUTH END. LANDING '
            f'{ft(WF + ISL_BAYS[0])} NORTH OF THE SINK CABINET, 24" DISHWASHER PANEL SOUTH (NKBA 24 AND 18). AISLE FROM THE RANGE FRONT TO THE ISLAND TOP EDGE '
            f'{ft(AISLE_RANGE)} (NKBA 42", THE ISLAND {inch(ISL_SHIFT)} EAST OF FOR\'S POSITION, SEE ID-741), FROM THE WEST RUN COUNTER EDGE {ft(AISLE_W)}. ONE '
            'POP-UP OUTLET IN THE TOP AT THE NORTH END, CENTERED 2\'-6" FROM THE WORKING EDGE AND 8" FROM THE NORTH WATERFALL FACE, OVER THE CLOSED ZONE BEHIND THE '
            'DRAWERS (CLEAR OF THE DRAWER BOXES). NO OUTLETS IN THE WATERFALLS. UNDER-TOE LED OPTIONAL. PENDANTS ON THE RCP.')

def island_seat(v):
    """East face, looking west from the dining, south at the left: continuous paneled front between the waterfalls under a 15 in. overhang."""
    L = ISL_L; floor_line(v, 0, L)
    K._rect(v, WF, 0, WF + ISL_CAB, K.BOX_TOP, K.OUTLINE); K.toe(v, WF, WF + ISL_CAB)
    pw = (ISL_CAB - 4 * K.STILE) / 3
    pts = [0, WF]
    for i in range(3):
        px = WF + K.STILE + i * (pw + K.STILE)
        K._rect(v, px, K.TOE + K.STILE, px + pw, K.BOX_TOP - K.STILE, K.MED); K._rect(v, px + 1.5, K.TOE + K.STILE + 1.5, px + pw - 1.5, K.BOX_TOP - K.STILE - 1.5, K.FINE, K.MID)
        pts += [px, px + pw]
    pts += [WF + ISL_CAB, L]
    K.counter(v, 0, L, edge=2.0); K.waterfall(v, 0, L, side='L', thick=WF); K.waterfall(v, L, L, side='R', thick=WF)
    K.miter_corner(v, 0, side='L', thick=WF); K.miter_corner(v, L, side='R', thick=WF)
    tag(v, L / 2, 20, 'SEATING FOR THREE, STOOLS N.I.C.', 5.0, MID, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points(pts))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, 60, v.X(L) + 14, E.snap_points([0, K.COUNTER - 2, K.COUNTER]))
    return (f'ISLAND, SEATING FACE (EAST), LOOKING WEST FROM THE DINING, SOUTH AT THE LEFT. THREE FLAT RECESSED PANELS {ft(pw)} EACH IN A 2" FACE FRAME BETWEEN '
            'THE WATERFALLS, SAME STILE AS THE DOORS, SET 15" BACK FROM THE TOP\'S EDGE. THE WATERFALLS RUN THE FULL DEPTH, SO THE KNEE RECESS IS CLOSED BY STONE AT '
            'BOTH ENDS AND THE TOP DOES NOT READ AS A CANTILEVER: THE 2" MITERED EDGE RUNS ALONG THE SEATING SIDE AND MEETS EACH WATERFALL AT A 45 DEGREE MITER. '
            'SUPPORT OF THE 15" RECESS (DESIGN INTENT, FABRICATOR AND CABINETMAKER TO CONFIRM): SIX 1/4" x 2" STEEL FLAT BARS AT 16" O.C. LET FLUSH INTO A 3/4" '
            'PLYWOOD SUB-TOP, FROM 2" SHORT OF THE SEATING EDGE BACK 30" OVER THE CABINET, SCREWED TO THE BOX, THE CABINET\'S SEATING FACE A 3/4" STRUCTURAL PANEL. '
            f'THE INSIDE FACES OF THE WATERFALLS IN THE RECESS ARE FINISHED STONE. 3\'-0" COUNTER, 15" KNEE SPACE (NKBA), THREE SEATS AT ABOUT {ft(ISL_CAB / 3)} EACH '
            f'({ft(ISL_CAB)} BETWEEN THE WATERFALLS). THE {inch(ISL_W - 24)} BEHIND THE WORKING BAYS IS CLOSED BY THE PANELS (DOORS INSTEAD GIVE IT STORAGE, OWNER '
            f'TO SAY). NO OUTLETS ON THIS FACE. THE SEATING EDGE IS {ft(ISL_X - 1 + ISL_TOP)} FROM THE WEST WALL, {ft(ROOM_W - (ISL_X - 1 + ISL_TOP))} CLEAR TO THE '
            f'EAST WALL: WITH A 42" TABLE AND 36" OF CHAIR ROOM AT THE SLIDER, {ft(DIN_CLEAR)} FROM THE TOP\'S EDGE TO THE TABLE (NKBA 44" BEHIND THE STOOLS). FOR DRAWS NO TABLE AND NO DINING WALL.')

def island_end(v, which='N'):
    """Island end: the waterfall seen face-on, the full depth of the top, mitered to it. The cabinet and the 15 in. knee recess behind it, dashed."""
    L = ISL_TOP
    knee = (0.0, OV) if which == 'N' else (L - OV, L)
    floor_line(v, 0, L)
    K._rect(v, 0, 0, L, K.COUNTER, K.OUTLINE, fill=(1, 1, 1))
    for i in range(3): K._line(v, (18 + i * 10, 20), (26 + i * 10, 4), K.FINE, K.PALE)      # veins, clear of the tags and the knee
    K._line(v, (0, K.COUNTER - 2), (L, K.COUNTER - 2), K.FINE, MID, '[1.5 1.5] 0')
    cx = knee[1] if which == 'N' else knee[0]
    tx = cx + (3 if which == 'N' else -3)
    K._line(v, (cx, K.TOE), (cx, K.COUNTER - 2), K.FINE, MID, '[2 2] 0'); K._line(v, (cx, K.TOE), (tx, K.TOE), K.FINE, MID, '[2 2] 0'); K._line(v, (tx, 0), (tx, K.TOE), K.FINE, MID, '[2 2] 0')
    wx = L - 1 if which == 'N' else 1.0; wt = wx - 3 if which == 'N' else wx + 3                # the working face, 1 in. back, its toe 3 in. further back
    K._line(v, (wx, K.TOE), (wx, K.COUNTER - 2), K.FINE, MID, '[2 2] 0'); K._line(v, (wx, K.TOE), (wt, K.TOE), K.FINE, MID, '[2 2] 0'); K._line(v, (wt, 0), (wt, K.TOE), K.FINE, MID, '[2 2] 0')
    tag(v, L / 2, 26, f'WATERFALL {ft(L)}, FULL DEPTH, MITERED', 5.0, MID, box=True)
    tag(v, (knee[0] + knee[1]) / 2, 12, 'KNEE', 5.0, MID, box=True)
    if which == 'N':
        px = L - 30
        C._rect(v, px - 2, K.COUNTER - 6, px + 2, K.COUNTER, C.FINE, MID, dashes='[1.5 1.5] 0'); tag(v, px - 14, 46, 'POP-UP', 5.0, MID, box=True); C._line(v, (px - 9, 44.5), (px - 1, K.COUNTER + 0.3), C.FINE, MID)
    v.dim_h(0, L, v.Y(0) + 22, E.snap_points([0, OV, L - 1, L] if which == 'N' else [0, 1, L - OV, L]))
    v.dim_h(0, L, v.Y(0) + 35, [0, L])
    v.dim_v(0, 60, v.X(L) + 14, E.snap_points([0, K.COUNTER - 2, K.COUNTER]))
    side = 'NORTH END, LOOKING SOUTH, EAST (THE SEATING SIDE) AT THE LEFT' if which == 'N' else 'SOUTH END, LOOKING NORTH, EAST (THE SEATING SIDE) AT THE RIGHT'
    outlet = ('THE POP-UP OUTLET (DASHED) IS IN THE TOP, CL 2\'-6" FROM THE WORKING EDGE AND 8" FROM THIS WATERFALL\'S OUTER FACE, OVER THE CLOSED ZONE BEHIND THE DRAWERS, FED THROUGH THE CABINET.' if which == 'N' else 'NO OUTLET AT THIS END.')
    return (f'ISLAND {side}. ST-03 WATERFALL THE FULL {ft(L)} DEPTH OF THE TOP, FLOOR TO TOP, ONE PIECE: A 3 CM SLAB WITH 2" MITERED RETURNS ON BOTH VERTICAL '
            'EDGES SO IT READS 2", MITERED 45 DEGREES TO THE TOP ALONG THE WHOLE END, VEIN CONTINUOUS OVER THE MITER FROM THE TOP (VEIN-MATCHED, NOT A MIRRORED '
            f'BOOKMATCH). THE TOP IS ONE PIECE, NO SEAM: {ft(ISL_L)} x {ft(L)} PLUS ITS APRON STRIPS NEEDS A JUMBO SLAB, ABOUT 121" x 72" MINIMUM, THE TWO WATERFALLS '
            'FROM A SECOND SEQUENTIAL SLAB, LAID OUT ON A DIGITAL TEMPLATE WITH THE OWNER. THE WATERFALL SITS ON THE FINISHED FLOOR WITH A 1/8" SILICONE JOINT, NO '
            f'BASE. BEHIND IT (DASHED): THE {ft(ISL_W)} CABINET, 1" BACK FROM THE WORKING EDGE, ITS TOE 3" FURTHER BACK, AND THE 15" KNEE RECESS AT THE SEATING SIDE, '
            'CLOSED BY THIS STONE. 2\'-10" CLEAR UNDER THE TOP AT THE KNEES. ' + outlet)

# ================================================================== key plan (3/8"): the whole room and the pantry

# ---- 11 x 17 review draft (11.07.26): short build notes, a short schedule, a short change list
from idd_sheet import ps as _ps
PN = 6.0; PN_LH = _ps(PN) + 2.4                      # note size and line height as printed
VIEW_NOTES = {
    1: '48" RANGE A1, 54" HOOD LINER A2 IN A 60" x 27" PLASTER BREAST. ST-03 SLAB SPLASH, TWO 2" ST-03 SHELVES EACH SIDE ON STEEL RODS, LED AT THE BACK EDGE. '
       '26" x 26" DRYWALL COLUMNS PT-02. POT FILLER A8 CL 4\'-10". OUTLETS GFCI CL 3\'-6".',
    2: 'RIFT WHITE OAK VENEER, FLUSH INSET. REFRIGERATOR A3 AND FREEZER A4, 36" EACH, PANTRY CABINETS EACH END. GLASS UPPERS 7\'-0" TO 9\'-3" OVER A3 AND A4. '
       'DOOR 05 3\'-0" x 8\'-0" FULL LITE, 5" CASING.',
    3: 'PAINTED INSET TALL CABINETS AND SHELVING, ST-03 COUNTER, SLAB TO 7\'-0", 2" x 12" ST-03 SHELVES AT 4\'-10" AND 6\'-0" WITH LED. '
       'PANTRY: PAIR OF CABINET-FACED SWING DOORS ON PIVOTS, HEADER 9\'-3". ARCHED CASING ON THE 4\'-10" OPENING.',
    4: 'SLIDER 04 BY FOR. 4" x 4" DRAPERY POCKET IN THE CEILING, 8" OFF THE WALL, 14" PAST EACH JAMB. PT-02, 8-1/2" BASE, CM-01 CROWN.',
    5: 'ST-03 TOP WITH A 2" MITERED EDGE AND MITERED WATERFALL ENDS. SINK A6, DISHWASHER A5, TRASH PULL-OUT. POP-UP OUTLET AT THE NORTH END.',
    6: 'THREE RECESSED PANELS, 15" KNEE SPACE, THREE STOOLS. STEEL FLAT BARS IN THE SUB-TOP OVER THE KNEE SPACE, BY THE FABRICATOR.',
    7: 'ST-03 WATERFALL, 2" MITERED EDGES, VEIN CONTINUOUS FROM THE TOP. 1/8" SILICONE JOINT AT THE FLOOR. CABINET AND TOE DASHED BEHIND.',
    8: 'ST-03 WATERFALL, 2" MITERED EDGES, VEIN CONTINUOUS FROM THE TOP. 1/8" SILICONE JOINT AT THE FLOOR. CABINET AND TOE DASHED BEHIND.',
    9: 'PAINTED INSET LOWERS: DISHWASHER A11, MICROWAVE DRAWER A9, TRASH PULL-OUT. GLASS UPPERS 4\'-6" TO 9\'-3" WITH LED. OPEN NICHE 4\'-6" TO 7\'-0", '
       'TWO 1-1/4" SHELVES. ST-03 COUNTER, 3/4" SPLASH. FOUR GFCI CL 3\'-6".',
    10: 'FOR\'S 3\'-2" x 8\'-1" OPENING, NO DOOR, DRYWALL RETURNS. SWITCH CL 4\'-0". ROBE HOOK, TOP AT 5\'-8". PT-02, 8-1/2" BASE, CM-01 CROWN.',
    11: 'SINK A12 30" x 18" UNDERMOUNT IN A 33" CABINET, WALL-MOUNTED FAUCET, VALVE IN THE WALL. GLASS UPPERS 4\'-6" TO 9\'-3". TWO GFCI CL 3\'-6".',
    12: 'UNDERCOUNTER REFRIGERATOR A10, HINGED SOUTH. TRAY PULL-OUT. LATTICE WINE RACK 36" x 30", GLASS TRANSOM ABOVE. TWO GFCI CL 3\'-6".',
}

def draw_views_p(sh, cells, views, scale='1/2', ceiling=H, block=False, heights=None):
    """draw_views with the review-draft notes: two short lines, right-aligned under the title bar.
    block=True: the notes sit just above the view and the two are centered in the cell together (heights: the drawn height per view, in.)."""
    k = E.SCALES[scale]
    for i, (cell, (n, title, L, fn, extra)) in enumerate(zip(cells, views)):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" TO 1\'-0"' % scale)
        hv = heights[i] if heights else ceiling
        spec = {'room': 'KITCHEN', 'view': title, 'length': L + extra, 'ceiling': hv}
        width = min(cell[2] - cell[0] - 16, 700)
        lines_ = wrap(VIEW_NOTES[n], PN, width)
        assert len(lines_) <= 2, (n, lines_)
        top = 26 + len(lines_) * PN_LH + 10
        origin = E.fit_origin(cell, spec, k, top=top)
        ny = cell[1] + 28
        if block:                                            # notes, 18 pt gap, the view, 44 pt for the dimension strings: centered under the title bar
            nh = len(lines_) * PN_LH; bh = nh + 18 + hv * k + 44
            b0 = cell[1] + 16 + (cell[3] - cell[1] - 16 - bh) / 2
            ny = b0 + PN_LH * 0.8; origin = (origin[0], b0 + nh + 18 + hv * k)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        fn(v)
        v.text(v.X(0) - 6, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        for ln in lines_: sh.text(cell[2] - 8, ny, ln, PN, MID, align='r'); ny += PN_LH

def draw_schedule_p(sh, x0, y0, x1, size=6.0, pitch=None):
    """APPLIANCES: tag, item, size. pitch: a ruled table at that row height (pt)."""
    sh.text(x0, y0, 'APPLIANCES', size + 2.0, INK, bold=True)
    cols = [('TAG', 44), ('ITEM', x1 - x0 - 44 - 190), ('SIZE (IN.)', 190)]
    ty = y0 + size + 12; cx = x0
    for h, w in cols: sh.text(cx, ty, h, size, MID); cx += w
    sh.line((x0, ty + 4), (x1, ty + 4), 0.4); ty += 14
    for row in B.APPLIANCES:
        if row[0] == 'A7': continue                                   # not used
        vals = (row[0], row[1], row[3])
        cx = x0
        for (h, w), val in zip(cols, vals):
            assert FREG.text_length(val, fontsize=size) <= w - 8, ('schedule cell too long', val)
            sh.text(cx, ty + (pitch * 0.62 - size * 0.3 if pitch else 0), val, size, INK); cx += w
        if pitch: ty += pitch; sh.line((x0, ty + 4), (x1, ty + 4), 0.3, LIGHT)
        else: ty += size + 6.0
    return ty

def key_plan(sh, marks):
    import compose_plans as CP
    src = fitz.open(CP.BASE_KEY.replace('Base-clean', 'Base-furn')); sp = src[0]
    clip_disp = fitz.Rect(80, 130, 442, 552)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    sp.add_redact_annot(u); sp.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    k = 2.0                                                     # 3/16 -> 3/8
    tw, th = clip_disp.width * k, clip_disp.height * k
    ax0, ay0, ay1 = FR.x0 + 6, HDR_Y + 8, FR.y1 - 6
    COL_W_ = 560.0; GAP_ = 80.0                                 # the schedule and notes column to the right of the plan
    tx = ax0 + (TB_X - 10 - ax0 - (tw + GAP_ + COL_W_)) / 2; ty = ay0 + (ay1 - ay0 - th - 74) / 2   # plan, column and scale bar centered on the sheet
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    sh.p.show_pdf_page(target, src, 0, clip=u, rotate=90)
    xref = sh.p.get_contents()[0]; st = sh.p.parent.xref_stream(xref).decode('latin1')
    parts = st.split('q ')
    for i in range(1, len(parts)):
        if 'Do' in parts[i]: parts[i] = f'{target.x0:.2f} {sh.p.rect.height - target.y1:.2f} {target.width:.2f} {target.height:.2f} re W n ' + parts[i]
    sh.p.parent.update_stream(xref, 'q '.join(parts).encode('latin1'))
    sys.path.insert(0, '/home/claude/flrwork/rev1'); import keyclip as KC
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(1, ['KITCHEN AND DINING', 'PANTRY'], pad=10.0)), 'key plan clip'
    def P(xd, yd): return (target.x0 + (xd - clip_disp.x0) * k, target.y0 + (yd - clip_disp.y0) * k)
    def D(x, y): return (W_FACE + x / PT, N_FACE + y / PT)
    pl = Plan(sh, P)
    # blank the room (alcove zone and the stepped part), the pantry wall band and the pantry
    pl.rect(-0.5, -0.5, ROOM_W + 0.5, KD + 0.5, 0, None, fill=WHITE)
    pl.rect(N_RUN_E - 0.5, -STEP - 0.5, ROOM_W + 0.5, 0.5, 0, None, fill=WHITE)
    pl.rect(-0.5, KD - 0.6, ROOM_W, PANTRY_WALL_Y + 0.8, 0, None, fill=WHITE)
    pl.rect(-0.5, PANTRY_WALL_Y, PAN_W + 0.5, PANTRY_WALL_Y + PAN_D + 0.5, 0, None, fill=WHITE)
    # the kitchen's south wall redrawn: solid except the pantry door opening and the arch
    for a, b in ((-0.5, P_OPEN[0]), (P_OPEN[1], ARCH[0]), (ARCH[1], ROOM_W)):
        pl.rect(a, KD, b, PANTRY_WALL_Y, 0, None, fill=WALL); pl.line(a, KD, b, KD, 0.5); pl.line(a, PANTRY_WALL_Y, b, PANTRY_WALL_Y, 0.5)
    pl.line(ARCH[0], KD + 1, ARCH[1], KD + 1, 0.4, MID, '[2 2] 0'); pl.line(ARCH[0], PANTRY_WALL_Y - 1, ARCH[1], PANTRY_WALL_Y - 1, 0.4, MID, '[2 2] 0')
    pl.text((ARCH[0] + ARCH[1]) / 2, KD - 6, 'ARCHED OPENING 4\'-10"', 5.0, MID)
    # FOR's two west windows, deleted (owner): the wall drawn solid over them
    for a, b in ((fy(249.5), fy(305.0)), (fy(408.4), fy(463.9))): pl.rect(-(F_W - 343.6) / F_PT, a, -0.05, b, 0, None, fill=(90 / 255, 90 / 255, 90 / 255))   # the base wall tone
    # north run on the main north face, 25 deep, to the jog
    pl.rect(0, 0, DW_COL, DW_COL, 0.8, fill=WALL)                                     # NW drywall column
    pl.rect(DW_COL, 0, N_RUN_E, N_RUN_D, 0.8)
    pantry_w = (N_RUN_E - DW_COL - 2 * COL_W - 4.5) / 2; x = DW_COL
    for w in (pantry_w, 1.5, COL_W, 1.5, COL_W, 1.5): x += w; pl.line(x, 0, x, N_RUN_D, 0.4)
    pl.text(DW_COL + pantry_w + 1.5 + COL_W / 2, 16, 'A3', 6.5); pl.text(DW_COL + pantry_w + 3 + COL_W * 1.5, 16, 'A4', 6.5)
    pl.text(DW_COL + pantry_w / 2, 14, 'PANTRY CAB.', 5.0, MID); pl.text(N_RUN_E - pantry_w / 2, 14, 'PANTRY CAB.', 5.0, MID)
    pl.text((N_LEAF_X + N_LEAF / 2), -STEP + 10, 'DOOR 05', 5.0, MID); pl.text((N_RUN_E + N_LEAF_X) / 2, -STEP + 10, '24" RECESS', 5.0, MID)
    # west run, range, breast, shelves, south tall cabinet
    pl.rect(0, TALL_D, BASE_D, KD - S_TALL, 0.8); pl.line(BASE_D + 1, TALL_D, BASE_D + 1, RANGE_Y - RANGE_W / 2, 0.4); pl.line(BASE_D + 1, RANGE_Y + RANGE_W / 2, BASE_D + 1, KD - S_TALL, 0.4)   # counter edge 1 in. proud
    for y in (RANGE_Y - RANGE_W / 2 - W_STACKS_N[1], RANGE_Y - RANGE_W / 2, RANGE_Y + RANGE_W / 2, RANGE_Y + RANGE_W / 2 + W_STACKS_S[1]): pl.line(0, y, BASE_D, y, 0.4)   # as ID-742
    pl.rect(0, RANGE_Y - RANGE_W / 2, RANGE_D, RANGE_Y + RANGE_W / 2, 0.8, fill=WHITE); pl.text(RANGE_D / 2, RANGE_Y + 2, 'A1', 6.5)
    pl.rect(0, RANGE_Y - BREAST_W / 2, BREAST_D, RANGE_Y + BREAST_W / 2, 0.4, dashes='[2 2] 0')
    for a, b in ((S_TALL + 4, RANGE_Y - BREAST_W / 2 - 4), (RANGE_Y + BREAST_W / 2 + 4, KD - S_TALL - 4)): pl.rect(0, a, 12, b, 0.4, MID, dashes='[2 2] 0')
    pl.rect(0, KD - DW_COL, DW_COL, KD, 0.8, fill=WALL)                               # SW drywall column
    pl.text(RANGE_D + 6, RANGE_Y - 36, 'A2 HOOD ABOVE', 5.0, MID, align='l'); pl.line(RANGE_D + 5, RANGE_Y - 37, BREAST_D, RANGE_Y - BREAST_W / 2 + 2, 0.3, MID)
    pl.text(RANGE_D / 2 - 1, RANGE_Y + 13, 'A8 POT', 5.0, MID); pl.text(RANGE_D / 2 - 1, RANGE_Y + 17.5, 'FILLER', 5.0, MID)   # on the wall above the range, clear of the dashed breast
    # south wall: the vestibule with its swing doors, the drywall return, the shelving section, two tall cabinets, the west pier
    pl.rect(RET[0], KD - BASE_D, RET[1], KD, 0.8, fill=WALL)                              # drywall return
    for hx, d in ((VEST[0], 1), (VEST[1], -1)):                                          # leaves open 90 degrees into the vestibule, swings dashed
        pl.rect(hx + (0.2 if d > 0 else -1.6), KD - BASE_D, hx + (1.6 if d > 0 else -0.2), KD - BASE_D + LEAF_W, 0.6, fill=WHITE)   # the leaf, open, 1-3/8 in. thick
        sh.p.draw_sector(fitz.Point(pl.pt(hx, KD - BASE_D)), fitz.Point(pl.pt(hx + d * LEAF_W, KD - BASE_D)), -90 * d, color=MID, width=0.4, dashes='[2 2] 0', fullSector=False)
    pl.line(VEST[0], KD - BASE_D, VEST[1], KD - BASE_D, 0.3, MID, '[1 1.5] 0')            # the cabinet face line the doors close on
    pl.text((VEST[0] + VEST[1]) / 2, KD - 30, f'SWING DOORS, PAIR {ft(VEST[1] - VEST[0])}', 5.0, MID); pl.text((VEST[0] + VEST[1]) / 2, KD - 37, 'PANTRY ENTRY', 5.0, MID)
    pl.rect(MIDS[0], KD - BASE_D, MIDS[1], KD, 0.8); pl.line(MIDS[0] + 30, KD - BASE_D, MIDS[0] + 30, KD, 0.4)
    pl.line(MIDS[0], KD - BASE_D - 1, MIDS[1], KD - BASE_D - 1, 0.4)                      # counter edge
    pl.line(MIDS[0], KD - 12, MIDS[1], KD - 12, 0.4, MID, '[2 2] 0'); pl.text(MIDS[0] + 15, KD - 15, '12" SHELVES', 5.0, MID)
    pl.rect(TALLS[0], KD - BASE_D, TALLS[1], KD, 0.8); pl.line(TALLS[0] + TALL_W, KD - BASE_D, TALLS[0] + TALL_W, KD, 0.4)
    for a in (TALLS[0], TALLS[0] + TALL_W): pl.line(a, KD - BASE_D, a + TALL_W, KD, 0.3, MID); pl.line(a, KD, a + TALL_W, KD - BASE_D, 0.3, MID)
    pl.text((TALLS[0] + TALLS[1]) / 2, KD - 30, 'TALL CABINETS', 5.0, MID)
    pl.text(P_OPEN[1] + 3, PANTRY_WALL_Y + 10, 'OPENING 3\'-2" x 8\'-1"', 5.0, MID, align='l'); pl.text(P_OPEN[1] + 3, PANTRY_WALL_Y + 14.5, 'NO DOOR', 5.0, MID, align='l')
    pl.line(P_OPEN[1] + 2, PANTRY_WALL_Y + 8, (P_OPEN[0] + P_OPEN[1]) / 2 + 4, (KD + PANTRY_WALL_Y) / 2, 0.3, MID)      # leader to the opening
    # island
    ix0, iy0 = ISL_X, ISL_N
    pl.rect(ix0 - 1, iy0, ix0 + ISL_W + OV, iy0 + ISL_L, 0.9)   # the top: 1 in. proud on the working side, 15 in. on the seating side
    pl.line(ix0 + ISL_W, iy0 + WF, ix0 + ISL_W, iy0 + ISL_L - WF, 0.4, MID, '[2 2] 0')
    pl.line(ix0 - 1, iy0 + WF, ix0 + ISL_W + OV, iy0 + WF, 0.6); pl.line(ix0 - 1, iy0 + ISL_L - WF, ix0 + ISL_W + OV, iy0 + ISL_L - WF, 0.6)   # waterfalls, full depth
    yy = iy0 + WF
    for w in ISL_BAYS[:-1]: yy += w; pl.line(ix0, yy, ix0 + 24, yy, 0.4, MID, '[2 2] 0')
    sy = iy0 + SINK_CL
    pl.rect(ix0 + 3, sy - SINK_W / 2, ix0 + 22, sy + SINK_W / 2, 0.6); pl.text(ix0 + 12.5, sy + 2, 'A6', 6.0)
    sh.p.draw_circle(fitz.Point(pl.pt(ix0 + 25, sy)), 2.0, color=INK, width=0.5)
    dy0 = iy0 + WF + ISL_BAYS[0] + SINK_CAB
    pl.rect(ix0, dy0, ix0 + 24, dy0 + DW_W, 0.4, MID, dashes='[2 2] 0'); pl.text(ix0 + 12, dy0 + 14, 'A5', 6.0)
    pl.text(ix0 + 12, dy0 + DW_W + 8, 'TRASH', 5.0, MID)
    pl.rect(ix0 - 1 + 28, iy0 + 6, ix0 - 1 + 32, iy0 + 10, 0.5); pl.text(ix0 - 1 + 30, iy0 + 19, 'POP-UP', 5.0, MID)   # CL 30 from the working edge, 8 from the north face
    pl.text(ix0 + ISL_W + OV / 2, iy0 + ISL_L / 2, '15"', 5.0, MID); pl.text(ix0 + ISL_W + OV / 2, iy0 + ISL_L / 2 + 7, 'KNEE', 5.0, MID)
    pl.text(ix0 + 34, iy0 + 40, 'ISLAND', 6.5, MID)
    # pantry: the counter wraps W, S, E (FOR's layout)
    py0 = PANTRY_WALL_Y
    ps = py0 + PAN_D                                                                   # the south wall face
    pl.rect(0, ps - BASE_D, PAN_W, ps, 0.8)                                            # south bases
    pl.rect(0, py0, BASE_D, ps, 0.8); pl.rect(PAN_W - BASE_D, py0, PAN_W, ps, 0.8)      # end bases
    xx = S_RUN[0]
    for tagname, w, kind in S_BAYS[:-1]: xx += w; pl.line(xx, ps - BASE_D, xx, ps, 0.4)
    pl.line(END_D, ps - BASE_D, END_D, ps, 0.4); pl.line(PAN_W - END_D, ps - BASE_D, PAN_W - END_D, ps, 0.4)
    xx = S_RUN[0]
    for tagname, w, kind in S_BAYS:
        if tagname: pl.text(xx + w / 2, ps - 10, tagname, 5.5)
        xx += w
    yy = 0.0
    for tagname, w, kind in W_BAYS:
        if tagname: pl.text(7, py0 + yy + w / 2 + 2, tagname, 5.5)
        yy += w; pl.line(0, py0 + yy, BASE_D, py0 + yy, 0.4)
    pl.rect(3, py0 + PSINK_CL - 15, 21, py0 + PSINK_CL + 15, 0.5)                        # the sink on the west wall
    yy = 0.0
    for tagname, w, kind in E_BAYS:
        if tagname: pl.text(PAN_W - 6.5, py0 + yy + w / 2 + 2, tagname, 5.5)
        yy += w; pl.line(PAN_W - BASE_D, py0 + yy, PAN_W, py0 + yy, 0.4)
    # counter edges (1 in. proud) and the uppers dashed at 13 in.
    pl.line(END_D, ps - END_D, PAN_W - END_D, ps - END_D, 0.5); pl.line(END_D, py0, END_D, ps - END_D, 0.5); pl.line(PAN_W - END_D, py0, PAN_W - END_D, ps - END_D, 0.5)
    pl.line(UP_D, ps - UP_D, PAN_W - UP_D, ps - UP_D, 0.4, MID, '[2 2] 0')
    pl.line(0, ps, END_D, ps - END_D, 0.4); pl.line(PAN_W, ps, PAN_W - END_D, ps - END_D, 0.4)      # the slab miters
    pl.line(UP_D, py0, UP_D, ps - UP_D, 0.4, MID, '[2 2] 0'); pl.line(PAN_W - UP_D, py0, PAN_W - UP_D, ps - UP_D, 0.4, MID, '[2 2] 0')
    pl.text(66, py0 + 30, 'PANTRY', 6.5, MID)
    pl.dim(32, py0, 32, py0 + WALKWAY, '', 1); pl.text(34.5, py0 + 9, ft(WALKWAY), 6.0, INK, align='l')   # the walkway, at the west end clear of the marker
    # clearances
    pl.dim(RANGE_D, RANGE_Y - 10, ISL_X - 1, RANGE_Y - 10, ft(AISLE_RANGE), 1)
    pl.dim(BASE_D + 1, RANGE_Y + 48, ISL_X - 1, RANGE_Y + 48, ft(AISLE_W), 1)
    pl.dim(ISL_X + 22, N_RUN_D, ISL_X + 22, ISL_N, ft(AISLE_N), 1)
    pl.dim(ISL_X + 10, ISL_N + ISL_L, ISL_X + 10, KD - S_RUN_D, ft(AISLE_S), 1)
    pl.text(ISL_X + ISL_W + OV + 30, 40, 'KITCHEN', 11.0, INK, align='l'); pl.text(ISL_X + ISL_W + OV + 30, 170, 'DINING', 11.0, INK, align='l')
    pl.text(ISL_X + ISL_W + OV + 30, 52, f'{ft(ROOM_W)} x {ft(KD)}', 6.0, MID, align='l')
    pl.text(ROOM_W + 14, 120, 'SLIDER', 6.0, MID, align='l'); pl.text(ROOM_W + 14, 128, ft(SLIDER[1] - SLIDER[0]), 6.0, MID, align='l')
    for n, sheet, d, x, y in marks:
        cx, cy = P(x, y)
        _t = sh.text                                                      # radius 24 (owner 11.07.26: tags legible on 11 x 17), number 11 pt, sheet 9.5 pt
        sh.text = lambda x_, y_, s_, size, *a_, **k_: _t(x_, y_ + (-0.4 if size > 16 else -5.0), s_, 11.0 if size > 16 else 9.5, *a_, **k_)
        try: sh.elev_marker(cx, cy, n, sheet, d, r=MK_R)
        finally: del sh.text
    # the pantry's four views in one marker in the walkway, east of the opening note
    lab_w = FREG.text_length('OPENING 3\'-2" x 8\'-1"', fontsize=5.0)
    qr = 22.0; ppi = k / PT
    lo = (P_OPEN[1] + 3) + lab_w / ppi; hi = PAN_W - END_D                  # the opening note's end and the A10 run's face
    qx = (lo + hi) / 2
    assert qx - (qr + 7 + 10) / ppi > lo and qx + (qr + 7 + 10) / ppi < hi, ('pantry marker crowded', lo, hi)
    quad_marker_k(sh, *P(*D(qx, PANTRY_WALL_Y + WALKWAY / 2)), 'ID-745', {'S': 9, 'N': 10, 'W': 11, 'E': 12}, r=qr)
    return target

MK_R = 24.0
KP_TOP, KP_BOT = 60.0, 18.0          # the key plan's drawn top (the north wall) and foot, from the placed clip's edges (pt): the column aligns to them
def quad_marker_k(sh, cx, cy, sheet, views, r=MK_R):
    """Four views on one sheet: the sheet number in the center, each view number toward its wall, an arrow outside."""
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.6, fill=(1, 1, 1)); s_.commit()
    sh.text(cx, cy + 3.0, sheet.replace('ID-', ''), 8.0, INK, align='c', raw=True)
    for d, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d]
        tip = (cx + dx * (r + 7), cy + dy * (r + 7))
        b1 = (cx + dx * r - dy * 4.5, cy + dy * r + dx * 4.5); b2 = (cx + dx * r + dy * 4.5, cy + dy * r - dx * 4.5)
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
        sh.text(cx + dx * r * 0.72, cy + dy * r * 0.72 + 3.2, str(n), 9.0, INK, align='c', raw=True)

def draw_views_scale(sh, cells, views, scale, ceiling=H):
    draw_views(sh, cells, views, scale=scale, ceiling=ceiling)


def _dim_h_p(self, x0i, x1i, y_pt, pts_i, offset_lines=True):
    """E.ElevationView.dim_h for the print draft. Labels that fit sit in their segment; a label wider than its segment sits beside it
    above the string with a leader, on whichever side is clear of the labels already placed, stepping outward until it is clear."""
    xs = [self.X(v) for v in pts_i]
    E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
    self.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
    for v, x in zip(pts_i, xs):
        self.line((x, y_pt - 3), (x, y_pt + 3), 0.4); self.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)
    placed = []; narrow = []; flip = False
    def clear(x0, x1): return all(x1 + 2.5 < a or x0 - 2.5 > b for a, b in placed)
    for i, (a, b) in enumerate(zip(pts_i, pts_i[1:])):
        if b - a < 0.5: continue
        lab = E.ftin(b - a); cx = (self.X(a) + self.X(b)) / 2; seg = (b - a) * self.k
        if seg < FREG.text_length(lab, fontsize=5.0) + 6: narrow.append((i, a, b, lab, cx)); continue
        short = seg < 30; sz = 5.5 if not short else 5.0; tw = FREG.text_length(lab, fontsize=sz)
        if short and flip: self.text(cx, y_pt + 9.5, lab, sz, align='c')
        else: self.text(cx, y_pt - 2.5, lab, sz, align='c'); placed.append((cx - tw / 2, cx + tw / 2))
        flip = not flip if short else False
    for i, a, b, lab, cx in narrow:
        tw = FREG.text_length(lab, fontsize=5.0)
        prev = a - pts_i[i - 1] if i > 0 else 0; nxt = pts_i[i + 2] - b if i + 2 < len(pts_i) else 0
        sides = (1, -1) if nxt >= prev else (-1, 1)
        for step in (0, 6, 12, 18, 24):
            done = False
            for sd in sides:
                edge = self.X(b) if sd > 0 else self.X(a)
                x0 = edge + sd * (5.5 + step); lo, hi = (x0, x0 + tw) if sd > 0 else (x0 - tw, x0)
                if clear(lo, hi):
                    self.line((cx, y_pt - 3.6), (x0 - sd * 1.0, y_pt - 6.5), 0.3)
                    self.text(x0, y_pt - 5.0, lab, 5.0, align='l' if sd > 0 else 'r'); placed.append((lo, hi)); done = True; break
            if done: break
        else: raise AssertionError(('no room for a narrow dimension label', lab))

def build():
    keep = list(idd_sheet.EXTRA_REVS); idd_sheet.EXTRA_REVS[:] = REVS        # runtime only, the module is untouched
    dh = E.ElevationView.dim_h; E.ElevationView.dim_h = _dim_h_p
    try: _build()
    finally: idd_sheet.EXTRA_REVS[:] = keep; E.ElevationView.dim_h = dh

def _build():
    idd_std.PROJECT['date'] = '11.03.26'
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    doc = fitz.open()
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    I0 = '11.02.26'
    rev = (('0', I0, 'ISSUED FOR REVIEW'), ('1', I0, 'RANGE WALL PER STUDY 3 B'), ('2', I0, 'FULL ROOM, YL WALLS, PANTRY'), ('3', I0, 'PANTRY PER FOR PLAN'), ('4', I0, 'ISLAND 5\'-3", WATERFALLS'), ('5', '11.03.26', 'OWNER COMMENTS'))
    # ---- ID-741 key plan, schedule, notes
    sh = Sheet(doc); sh.frame('KITCHEN, DINING AND PANTRY ELEVATIONS', 'KEY PLAN, SCALE: 3/8" TO 1\'-0"', ['KITCHEN AND PANTRY', 'ELEVATIONS KEY PLAN'], 'ID-741', revisions=rev, legend_rule=False)
    def D(x, y): return (W_FACE + x / PT, N_FACE + y / PT)
    cy_isl = ISL_N + ISL_L / 2
    marks = [(1, 'ID-742', 'W', *D(50, 44)), (2, 'ID-742', 'N', *D(148, 56)), (3, 'ID-743', 'S', *D(180, KD - 56)), (4, 'ID-743', 'E', *D(ROOM_W - 40, 150)),
             (5, 'ID-744', 'E', *D(ISL_X - 14, cy_isl + 22)), (6, 'ID-744', 'W', *D(ISL_X + ISL_W + OV + 18, cy_isl)),
             (7, 'ID-744', 'S', *D(ISL_X + 10, ISL_N - 18)), (8, 'ID-744', 'N', *D(ISL_X + 52, ISL_N + ISL_L + 18))]
    target = key_plan(sh, marks)
    # scale bar and north arrow under the plan (review 11.07.26: label 9 pt, a north arrow)
    sh.text(target.x0 + 10, target.y1 - KP_BOT + 26, 'FLOOR 1 KEY PLAN', 11.0, INK, serif=True, spacing=1.0, raw=True)   # caption under the plan (review 11.07.26)
    bx, by = target.x0 + 10, target.y1 + 50; ft_ = 27.0
    for i in range(10): sh.rect((bx + i * ft_, by - 4, bx + (i + 1) * ft_, by), 0.4, INK, INK if i % 2 == 0 else WHITE)
    for i in (0, 5, 10): sh.text(bx + i * ft_, by + 12, "%d'" % i, 7.5, MID, align='c', raw=True)
    sh.text(bx + 10 * ft_ + 14, by + 0.5, '3/8" TO 1\'-0"', 9.0, INK, raw=True)
    na = (bx + 10 * ft_ + 14 + FREG.f.text_length('3/8" TO 1\'-0"', fontsize=9.0) + 70, by - 4)
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(*na), 16); s_.finish(color=INK, width=0.6, fill=WHITE); s_.commit()
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(na[0], na[1] - 16), fitz.Point(na[0] + 7, na[1] + 10), fitz.Point(na[0], na[1] + 4), fitz.Point(na[0] - 7, na[1] + 10), fitz.Point(na[0], na[1] - 16)])
    s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
    sh.text(na[0] + 24, na[1] + 4, 'N', 11.0, INK, raw=True)
    assert by + 14 < FR.y1 - 20, ('scale bar too close to the frame', by)
    sx = target.x1 + 80; W = 560.0; NS = 10.0; NLH_ = NS + 5.5      # the column: appliances at the top of the plan, changes and materials ending at its foot (10 pt)
    paras = [
        (True, 'CHANGES FROM FOR\'S PLAN'),
        '1. 48" RANGE IN A 60" x 27" PLASTER HOOD BREAST.',
        '2. FOR\'S 3\'-0" BUILT-IN OVEN ON THE SOUTH RUN DELETED.',
        '3. FOR\'S TWO WEST WINDOWS DELETED.',
        '4. 26" x 26" DRYWALL COLUMNS AT THE NW AND SW CORNERS.',
        '5. TALL CABINETS AND SHELVING IN PLACE OF FOR\'S 6\'-5" BAR.',
        '6. HIDDEN DOOR 17 OMITTED: PAIR OF SWING DOORS ON THE KITCHEN SIDE.',
        f'7. ISLAND MOVED {inch(ISL_SHIFT)} EAST FOR A 42" RANGE AISLE.',
        '8. PANTRY: DISHWASHER A11, MICROWAVE A9 AND REFRIGERATOR A10 RELOCATED.', '',
        (True, 'MATERIALS'),
        'ST-03 STONE: COUNTERS, SPLASH, SHELVES, HONED, SLAB T.B.C.',
        'PT-02 AND CM-01 PER THE FINISH SCHEDULE.']
    lines = sum(0.5 if (p_ if isinstance(p_, str) else p_[1]) == '' else len(wrap(p_ if isinstance(p_, str) else p_[1], NS, W)) for p_ in paras)
    global NOTES_END
    ny0 = target.y1 - KP_BOT - lines * NLH_ + NS                                     # last baseline on the plan's south wall line
    rows = len([r_ for r_ in B.APPLIANCES if r_[0] != 'A7'])
    pitch = (ny0 - NS - 70 - (target.y0 + KP_TOP) - (NS + 26)) / rows               # a ruled schedule that runs down to 70 pt above the notes (review: no empty band)
    pitch = max(NS + 6, min(pitch, 36.0))
    ty = draw_schedule_p(sh, sx, target.y0 + KP_TOP, sx + W, size=NS, pitch=pitch)
    assert ny0 > ty + 40, ('key plan column overlaps', ty, ny0)
    NOTES_END = para_block(sh, sx, ny0, paras, W, size=NS, lh=NLH_, head_color=INK)
    # ---- ID-742 west and north
    sh = Sheet(doc); sh.frame('KITCHEN ELEVATIONS', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'KITCHEN'], 'ID-742', revisions=rev, legend_rule=False)
    cells = E.layout_cells(frame, 1, 2)
    draw_views_p(sh, cells, [(1, 'WEST ELEVATION - RANGE WALL', KD, west_wall, 0), (2, 'NORTH ELEVATION - REFRIGERATOR WALL', ROOM_W, north_wall, 0)])
    # ---- ID-743 south and east
    sh = Sheet(doc); sh.frame('KITCHEN ELEVATIONS', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'KITCHEN AND DINING'], 'ID-743', revisions=rev, legend_rule=False)
    cells = E.layout_cells(frame, 1, 2)
    draw_views_p(sh, cells, [(3, 'SOUTH ELEVATION', ROOM_W, south_wall, 0), (4, 'EAST ELEVATION - SLIDER', E_LEN, east_wall, 0)])
    # ---- ID-744 island
    sh = Sheet(doc); sh.frame('KITCHEN ELEVATIONS', 'SCALE: 1" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'KITCHEN ISLAND'], 'ID-744', revisions=rev, legend_rule=False)
    cells = E.layout_cells(frame, 2, 2)
    draw_views_p(sh, cells, [(5, 'ISLAND - WORKING SIDE', ISL_L, island_work, 0), (6, 'ISLAND - SEATING SIDE', ISL_L, island_seat, 0),
                           (7, 'ISLAND - NORTH END', ISL_TOP, lambda v: island_end(v, 'N'), 0), (8, 'ISLAND - SOUTH END', ISL_TOP, lambda v: island_end(v, 'S'), 0)], scale='1', ceiling=60.0, block=True, heights=[60.0, 60.0, 50.0, 50.0])   # 1" (11.07.26: the 17 x 11 sheet has the room)
    # ---- ID-745 pantry
    sh = Sheet(doc); sh.frame('PANTRY ELEVATIONS', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'PANTRY'], 'ID-745', revisions=rev, legend_rule=False)
    cells = E.layout_cells(frame, 2, 2)                      # reading order (review 11.07.26): 9 south, 10 north on the top row, 11 west, 12 east below
    draw_views_p(sh, cells, [(9, 'PANTRY - SOUTH WALL', PAN_W, pantry_south, 0), (10, 'PANTRY - NORTH WALL', PAN_W, pantry_north, 0),
                           (11, 'PANTRY - WEST WALL', PAN_D, lambda v: pantry_end(v, 'W'), 0), (12, 'PANTRY - EAST WALL', PAN_D, lambda v: pantry_end(v, 'E'), 0)])
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, 'notes end', round(NOTES_END, 1), 'frame bottom', FR.y1)

if __name__ == '__main__':
    build()
