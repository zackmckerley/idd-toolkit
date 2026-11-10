"""Living room on FOR REV 1, revision 2 (11.05.26): a copy of build_great.py with ID-752 view 2 (west, the gallery) and ID-754 (south)
redrawn from FOR A-201 / A-202 REV 1 (the piano room gone, the south end and the west end open under floor 2, the stair and closet 27,
the den open to the hall, FOR's side-mounted glass guard), the ID-751 key plans and notes reworked, the guard ends on ID-752 view 1 and
ID-753 changed to glass. Revision 3 (11.06.26): the guard is painted steel (owner), the west end 7'-8", the south end tray noted. The fireplace wall (option 2) and the trim block are unchanged. The REV 1 numbers are in the PLAN block.
Output: 261105.HD102.LivingRoomPilot.pdf (the previous issue kept as 261105.HD102.LivingRoomPilot.prev.pdf)."""
import sys; sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import idd_std as _std, idd_sheet as _ish
_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
_ish.EXTRA_REVS[:] = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1'), ('2', '11.05.26', 'GALLERY AND STAIR, REV 1'), ('3', '11.06.26', 'METAL GUARD, REV 1 CHECK')]

import math
from contextlib import contextmanager
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG
from idd_std import INK, MID, LIGHT
from build_kitchen import tag as _tag, wrap, para_block

def tag(v, x, y, s, size=5.0, c=MID, box=False):
    """Label; box=True masks a white field the full height of the printed text (review 11.09.26: the shared tag's mask was
    sized to the nominal size, so linework crossed the top of the letters)."""
    if box:
        sz = _ish.ps(size); w = FREG.text_length(s, fontsize=size)
        v.rect(v.X(x) - w / 2 - 2.0, v.Y(y) - sz * 0.95, v.X(x) + w / 2 + 2.0, v.Y(y) + 2.2, 0, fill=WHITE)
    v.text(v.X(x), v.Y(y), s, size, c, align='c')

OUT_STUDY = '/home/claude/flrwork/261105.HD102.LivingRoomStudy.pdf'
OUT = '/home/claude/flrwork/261105.HD102.LivingRoomPilot.pdf'
ISSUE = '11.03.26'
BASE_CLEAN = '/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'   # FOR REV 1 base
PT = 0.8889                                  # inches per display point on the base plans
NOTE = 6.0; NOTE_LH = 10.0                 # print size: 6 pt grows to 7.8 pt (idd_sheet.ps)
WHITE = (1, 1, 1); POCHE = (0.3, 0.3, 0.3); SEC = (0.88, 0.88, 0.88); GREY = (0.58, 0.58, 0.58)

def q(v): return round(v * 8) / 8           # to 1/8 in.
def inch(a, b): return q((b - a) * PT)

# ---- floor 1 (Base-clean page 0, display points)
GF_W = 302.32                                # guest room foyer west wall face (under the gallery)
V_W, V_E = 405.6, 617.08                     # the double-height volume: west edge (gallery line), east wall face
V_N, V_S = 472.44, 690.48                    # north wall face, south edge (gallery line, the stair wall face)
GF_N = 466.32                                # guest foyer north wall face, 5.4 in. north of the great room's
SL_F1 = (429.64, 577.48)                     # FOR's four-panel slider, jamb to jamb
STAIR_W = 569.8                              # west end of the stair enclosure wall (the pier east of the piano room opening)
GF_DOOR = (615.2, 655.2)                     # guest bedroom door opening in the guest foyer west wall (plan y)
ARCH_F1 = (321.2, 386.5)                     # the kitchen's arched opening in the guest foyer north wall (build_kitchen2 ARCH)
# ---- floor 2 (page 1), registered: f1 = f2 + (43.24, 9.24) on the east face 573.84 / 617.08 and the north face 463.2 / 472.44
F2D = (43.24, 9.24)
F2_HALL_W = 312.96                           # hall west wall face (floor 2)
F2_BED_DOOR = (558.36, 598.44); F2_AHU = (624.84, 662.76)   # openings in the hall west wall (plan y, floor 2)
F2_LINEN = (393.6, 476.4); F2_LINEN_WALL = (356.52, 521.16); F2_STAIR_TOP = 483.84   # floor 2 x
HALL_DOOR_N = (52.625, 89.875)               # the door across the hall 4'-1" north of the north wall line (north view x)
MASTER_DOOR = (193.25, 227.375)              # the master suite door at the hall's south end (south view x)
STAIR_TOP = (80.0, 69.0, 58.0, 47.0)        # floor 2 nosings from the east wall (527.1, 539.4, 551.8, 564.2 registered), the corner landing east of 47
RISER = 7.375; LOW_FLIGHT = 107.625          # the lower flight starts 8'-11-5/8" from the east wall (FOR)
F2_CLR = (405.48, 553.32)                    # FOR's clerestory, floor 2 x (1'-4-7/8" east of the slider: aligned here, listed)

RW = 188.0                                   # 15'-8" E-W: FOR A-201 floor 1 wall corner x764.2 to the east face x1046.2 (the floor 2 glass sits 1" inside)
RD = 194.0                                   # 16'-2" N-S: FOR REV 1 floor 1 string (vectors 16'-1-1/2")
GFW = 92.0                                   # the west end under floor 2, 7'-8": FOR 626.2 to 764.2 pt, 1'-5" | 4'-10" | 1'-5"
NL = GFW + RW                                # 280.0, 23'-4": x626.2 to x1046.2
H = 272.0                                    # 22'-8", FOR A-403 section 6 / A-301-302 TOP OF CEILING 2ND FLOOR (coordination 11.09.26)
BAND = 268.0; BAND_W = 12.0                  # FOR: the 22'-4" perimeter band at the window wall (embedded lights, 5" curtain pocket); width VERIFY
SLOPE0 = 108.0; SLOPE_RUN = 20.0              # FOR A-411 sec 04: the south end's ceiling 9'-0" at the walls rising to 10'-8" (run INFERRED)
HALL_C = 154.0 + 114.0                       # FOR A-206 / A-411: floor 2 hall ceiling 9'-6" above floor 2 (22'-4")
COVE = 4.0                                   # owner 11.09.26: crown held 4" below the ceiling with an LED strip on its top (FOR's L14 cove)
SOFFIT = 128.0; FF2 = 154.0                  # YL id 04: gallery soffit 10'-8" (the ceilings under it), finished floor 2 12'-10" (VERIFY with FOR)
BELT0, BELT1 = 117.0, 124.0                  # belt course: FOR's slider D03 head 9'-9" to clerestory G sill 10'-4" (the HSS beam in the band)
GUARD = 42.0; GT = FF2 + GUARD               # 3'-6" guard (FBC R312 minimum 36 in.)
CRG = 12.0; CR10 = 8.0; BASE = 8.5           # great room crown (built up, low end of the 14 ft row), the 10 ft rooms' crown, house base
CROWN_B = H - COVE - CRG                     # the great room crown's bottom: its top 4" under the ceiling, the LED cove above it
SL_X0 = 28.0; SL_W = 132.0                   # FOR A-201 slider jambs x806.2 and x1004.5: 2'-4" | 11'-0" | 2'-4", centered
ARCH = (17.0, 58.0)                          # FOR's kitchen arch in the west end's north wall: 1'-5" pier, 4'-10"
R2_HALL_N = (48.25, 53.0)                    # floor 2 hall west wall face 698.5, bedroom 3 door leaf 705.7 to 756.7 (2'-10"), from the west end's west wall (626.2)
SL_HEAD = 117.0; CL_SILL = BELT1; CL_HEAD = 250.0  # FOR A-600: slider D03 11'-0" x 9'-9", clerestory G 11'-0" x 10'-6", 10'-4" to 20'-10"
BW = 84.0; BD = 24.0                         # breast 7'-0" x 2'-0" (FOR 6'-0" x 1'-6"): a 75 in. TV with 8-7/8 in. each side, a listed DV unit
B0 = (RD - BW) / 2; B1 = B0 + BW; CX = RD / 2   # 54.875, 138.875, 96.875 from the north wall face
BI_D = 14.0; CAB_H = 30.0; TOP_T = 1.25      # built-ins 14 in. deep (FOR: the slider is centered on the wall to their face)
FB_W = 42.0; FB_B = 6.0; FB_T = 36.0         # firebox opening 42 x 30, 6 in. above the flush hearth (unit to confirm)
LEG = 9.0; SHELF_B = 45.5; SHELF_T = 48.0; SHELF_OV = 1.0; SHELF_D = 6.0   # WS-01 surround: 9 in. legs, frieze, 2-1/2 in. shelf at 4'-0"
HEARTH_D = 20.0; HEARTH_S = 12.0             # hearth extension in front and each side (NFPA 211 for an opening over 6 sf)
TV_W = 66.25; TV_H = 37.75; TV_D = 1.125     # Samsung The Frame 75 (66.2 x 37.8 x 1.1)
NM = 2.0; NICHE_D = 4.0                      # niche 2 in. larger each way, 4 in. deep
TV_B = 56.0; TV_T = TV_B + TV_H              # 8 in. above the shelf top, center 74.875 (6'-2-7/8")
N_B = TV_B - NM; N_T = TV_T + NM             # niche 54 to 95.75
TV_C = TV_B + TV_H / 2
EYE = 42.0; EYE_X = 18.0                     # seated eye 3'-6", 1'-6" in front of a sofa whose back is on the gallery line
SEAT = RW - BD - EYE_X                        # 146: eye to the breast face (the TV face is 1/2 in. behind it), 12'-2"
ANGLE = math.degrees(math.atan((TV_C - EYE) / SEAT))
ART_W = 56.0; ART_H = 70.0
BOX_TOP = CL_HEAD - 4.0
ART_B = BOX_TOP - ART_H                      # two thirds of the breast, its top on the upper boxes' top line (20'-6"), center 17'-7" (the gallery's eye level is 17'-10")
ANGLE_UP = math.degrees(math.atan((TV_B + 2.5 + TV_H / 2 - EYE) / (RW - BD - 18.0)))   # the TV raised 2-1/2 in. with the shelf
BOX_TOP = CL_HEAD - 4.0                      # upper paneling boxes stop at the window head line, plain frieze to the crown
SL_C = SL_X0 + SL_W / 2                      # slider centerline from the gallery line
pass  # print(f'RW {RW} RD {RD} GFW {GFW} NL {NL} pier {SL_X0} slider {SL_W} NE wall {RW - SL_X0 - SL_W} angle {ANGLE:.1f}')

@contextmanager
def beyond():
    keep = (C.INK, C.MID, C.LIGHT, C.PALE)
    C.INK = GREY; C.MID = (0.68, 0.68, 0.68); C.LIGHT = (0.8, 0.8, 0.8); C.PALE = (0.88, 0.88, 0.88)
    try: yield
    finally: C.INK, C.MID, C.LIGHT, C.PALE = keep

def up(v, dy=FF2):
    """The same view with its floor line raised to finished floor 2, so floor 2 components draw with y from their own floor."""
    return E.ElevationView(v.p, v.F, v.fn, (v.ox, v.oy - dy * v.k), v.k, v.w)

def poche(v, x0, x1, y0, y1): C._rect(v, x0, y0, x1, y1, C.OUTLINE, INK, fill=POCHE)
def section(v, x0, x1, y0, y1): C._rect(v, x0, y0, x1, y1, C.OUTLINE, INK, fill=SEC)
def floor_line(v, x0, x1): v.line((v.X(x0) - 8, v.Y(0)), (v.X(x1) + 8, v.Y(0)), 1.2)
def ceiling(v, x0, x1, y=H): C._line(v, (x0, y), (x1, y), C.HEAVY)

def crown_cove(v, x0, x1, ceil=H):
    """CM-02 crown held COVE below the ceiling with a concealed LED strip on its top washing the ceiling (owner 11.09.26, FOR's L14 cove)."""
    C.crown(v, x0, x1, ceil - COVE, drop=CRG)
    C._rect(v, x0 + 0.5, ceil - COVE, x1 - 0.5, ceil - COVE + 0.6, C.FINE, C.MID)                     # the LED channel on the crown top
    C._line(v, (x0, ceil - COVE + 2.6), (x1, ceil - COVE + 2.6), C.FINE, C.LIGHT, '[1.5 1.5] 0')    # the light line, ceiling wash

def band_end(v, x0, x1):
    """FOR's 22'-4" perimeter band at the window wall, seen in section at the end of a side wall (4" drop, width VERIFY)."""
    C._rect(v, x0, BAND, x1, H, C.OUTLINE, INK, fill=SEC)

def belt(v, x0, x1):
    """Belt course, 10'-0" to 10'-8": the band between the slider head and the clerestory sill carried around the solid walls and across
    the breast; its top is the gallery soffit line (the 10'-8" ceilings under the gallery, the opening heads)."""
    C._rect(v, x0, BELT0, x1, BELT1, C.OUTLINE, fill=WHITE)
    C._line(v, (x0, BELT0 + 1.25), (x1, BELT0 + 1.25), C.FINE, C.MID); C._line(v, (x0, BELT1 - 1.75), (x1, BELT1 - 1.75), C.FINE, C.MID)
    C.shadow(v, x0, x1, BELT0)

def cap(v, x0, x1):
    """The gallery floor line (12'-10") carried on the solid walls: a 1-1/2 in. cap moulding, the same as the top of the fascia."""
    C._rect(v, x0, FF2 - 1.5, x1, FF2, C.OUTLINE, fill=WHITE); C.shadow(v, x0, x1, FF2 - 1.5)

def fascia(v, x0, x1):
    """The gallery beam face, 10'-8" to 12'-10": painted, a bed moulding at the soffit, the cap at the floor line."""
    C._rect(v, x0, SOFFIT, x1, FF2, C.OUTLINE, fill=WHITE)
    C._rect(v, x0, SOFFIT, x1, SOFFIT + 2.0, C.MED); C._line(v, (x0, SOFFIT + 1.0), (x1, SOFFIT + 1.0), C.FINE, C.MID)
    C._rect(v, x0, FF2 - 1.5, x1, FF2, C.OUTLINE); C.shadow(v, x0, x1, SOFFIT)

def guard(v, x0, x1, posts=None):
    """Painted balustrade on the fascia: 1-3/4 in. square balusters at 5-1/4 in. o.c. (3-1/2 in. clear, under the 4 in. sphere),
    shoe rail, 2-1/2 in. cap matching the stair handrail, 4 in. posts at the ends and the given positions. Balusters are filled so
    what is beyond reads behind them."""
    posts = sorted(set([x0, x1 - 4.0] + list(posts or ())))
    C._rect(v, x0, FF2, x1, FF2 + 3.0, C.MED, fill=WHITE)
    C._rect(v, x0, GT - 3.0, x1, GT, C.OUTLINE, fill=WHITE); C._line(v, (x0, GT - 1.2), (x1, GT - 1.2), C.FINE, C.MID)
    spans = []; cur = x0
    for p in posts:
        if p - cur > 1: spans.append((cur, p))
        cur = p + 4.0
    if x1 - cur > 1: spans.append((cur, x1))
    for a, b in spans:
        n = max(1, int(round((b - a - 1.75) / 5.25)))
        pitch = (b - a - 1.75) / n
        for i in range(n + 1):
            bx = a + i * pitch
            if a < bx < b - 1.75: C._rect(v, bx, FF2 + 3.0, bx + 1.75, GT - 3.0, C.FINE, fill=WHITE)
    for p in posts:
        C._rect(v, p, FF2, p + 4.0, GT + 2.0, C.OUTLINE, fill=WHITE); C._rect(v, p - 0.5, GT + 0.5, p + 4.5, GT + 2.0, C.MED)

def glazed_unit(v, x0, w, y0, y1, n, operable=False):
    """Glass in a drywall return, no casing (the kitchen slider's detail): n equal lites or panels with frames."""
    C._rect(v, x0 - 1, y0 - (0 if y0 == 0 else 1), x0 + w + 1, y1 + 1, C.OUTLINE)
    pw = w / n
    for i in range(n):
        px = x0 + i * pw
        C._rect(v, px, y0 + 0.5, px + pw, y1, C.OUTLINE); C._rect(v, px + 2.5, y0 + 3, px + pw - 2.5, y1 - 2.5, C.MED)
        C.glazing(v, px + 2.5, y0 + 3, px + pw - 2.5, y1 - 2.5)          # owner 11.09.26: divided lites, every window and glass door in the house
    if operable:   # three panels on three tracks: pulls on the two sliding panels' leading stiles
        for px in (x0 + pw - 3.0, x0 + 2 * pw - 3.0): C._rect(v, px, 38, px + 1.2, 46, C.MED)

def box(v, a, b, y0, y1, mold=2.0):
    if b - a < 6 or y1 - y0 < 6: return
    C._rect(v, a, y0, b, y1, C.MED); C._rect(v, a + mold, y0 + mold, b - mold, y1 - mold, C.FINE, C.MID)

def arched_cased_opening(v, x, w, spring, r):
    """The kitchen's arched opening seen from the guest foyer: same casing both sides (build_kitchen2)."""
    cs = 5.0; cx = x + w / 2; cy = spring - math.sqrt(r ** 2 - (w / 2) ** 2)
    def arc(rr, xa, xb):
        a0 = math.atan2(math.sqrt(rr ** 2 - (xa - cx) ** 2), xa - cx); a1 = math.atan2(math.sqrt(rr ** 2 - (xb - cx) ** 2), xb - cx)
        return [(cx + rr * math.cos(a0 + (a1 - a0) * i / 30), cy + rr * math.sin(a0 + (a1 - a0) * i / 30)) for i in range(31)]
    inner = arc(r, x, x + w); outer = arc(r + cs, x - cs, x + w + cs)
    sp_out = cy + math.sqrt((r + cs) ** 2 - (w / 2 + cs) ** 2)
    C._rect(v, x - cs, 0, x, sp_out, C.OUTLINE); C._rect(v, x + w, 0, x + w + cs, sp_out, C.OUTLINE)
    C._poly(v, [(x, 0), (x, spring)] + inner + [(x + w, spring), (x + w, 0)], C.OUTLINE, close=False)
    C._poly(v, outer, C.OUTLINE, close=False)
    C._poly(v, arc(r + cs - 1.0, x - cs + 1.0, x + w + cs - 1.0), C.FINE, LIGHT, close=False)
    return cy + r

# ================================================================== the fireplace stack (shared by the study, view 1 and view 5)
def mantel(v, cx, opt='B'):
    """Gas firebox in a WS-01 marble surround: 9 in. legs, frieze, 2-1/2 in. shelf at 4'-0" projecting 6 in. (the TV's heat deflector).
    Option C: the breast is the slab, so the surround is a 1-1/2 in. mitered frame and the shelf a 2 in. ledge the width of the breast."""
    h = FB_W / 2
    if opt == 'C':
        C._rect(v, cx - h - 1.5, FB_B - 1.5, cx + h + 1.5, FB_T + 1.5, C.OUTLINE)
        C._rect(v, B0, SHELF_T - 2.0, B1, SHELF_T, C.OUTLINE, fill=WHITE); C.shadow(v, B0, B1, SHELF_T - 2.0)
    else:
        C._rect(v, cx - h - LEG, 0, cx - h, SHELF_B, C.OUTLINE, fill=WHITE); C._rect(v, cx + h, 0, cx + h + LEG, SHELF_B, C.OUTLINE, fill=WHITE)
        C._rect(v, cx - h - LEG, FB_T, cx + h + LEG, SHELF_B, C.OUTLINE, fill=WHITE)
        C._poly(v, [(cx - h - 1.5, 0), (cx - h - 1.5, FB_T + 1.5), (cx + h + 1.5, FB_T + 1.5), (cx + h + 1.5, 0)], C.MED, close=False)   # bolection bead
        C._line(v, (cx - h - LEG, 4.0), (cx - h, 4.0), C.FINE, C.MID); C._line(v, (cx + h, 4.0), (cx + h + LEG, 4.0), C.FINE, C.MID)   # plinths
        C._rect(v, cx - h - LEG - SHELF_OV, SHELF_B, cx + h + LEG + SHELF_OV, SHELF_T, C.OUTLINE, fill=WHITE)
        C._line(v, (cx - h - LEG - SHELF_OV, SHELF_B + 1.0), (cx + h + LEG + SHELF_OV, SHELF_B + 1.0), C.FINE, C.MID); C.shadow(v, cx - h - LEG - SHELF_OV, cx + h + LEG + SHELF_OV, SHELF_B)
    C._rect(v, cx - h, FB_B, cx + h, FB_T, C.OUTLINE, fill=(0.25, 0.25, 0.25))   # the unit's glass front, black
    C._rect(v, cx - h + 3, FB_B + 3, cx + h - 3, FB_T - 3, C.FINE, (0.55, 0.55, 0.55))
    for i in range(3):
        lx = cx - 12 + i * 12; C._poly(v, [(lx - 5, FB_B + 6), (lx, FB_B + 14 + 3 * (i % 2)), (lx + 5, FB_B + 6)], C.FINE, (0.7, 0.7, 0.7), close=False)
    C._line(v, (cx - h, FB_B), (cx + h, FB_B), C.MED)

def tv_niche(v, cx):
    """The art-mode TV nearly flush in a 4 in. niche 2 in. larger than the set each way (the next size fits a 1 in. wider set)."""
    a, b = cx - TV_W / 2 - NM, cx + TV_W / 2 + NM
    C._rect(v, a, N_B, b, N_T, C.MED, fill=(0.93, 0.93, 0.93)); C._line(v, (a + 0.8, N_T - 0.8), (b - 0.8, N_T - 0.8), C.FINE, C.MID)
    C._rect(v, cx - TV_W / 2, TV_B, cx + TV_W / 2, TV_T, C.OUTLINE, fill=WHITE)
    C._rect(v, cx - TV_W / 2 + 1.0, TV_B + 1.0, cx + TV_W / 2 - 1.0, TV_T - 1.0, C.FINE, C.MID)
    C._line(v, (cx - TV_W * 0.38, TV_T - 5), (cx - TV_W * 0.12, TV_B + 6), C.FINE, C.PALE); C._line(v, (cx - TV_W * 0.32, TV_T - 5), (cx - TV_W * 0.06, TV_B + 6), C.FINE, C.PALE)

def flank(v, a, b, opt='B'):
    """A built-in between the breast and a corner: 30 in. inset base cabinet (pair of doors, 4-1/2 in. toe) with a WS-01 top and a lamp
    receptacle in the margin above it, then paneling WP-01 (B, C) or lit open shelves (A) to the belt course, a plain frieze to the gallery
    cap, and one paneled box above the cap to 4 in. under the clerestory head line."""
    w = b - a
    K.toe(v, a, b); K.door_pair_cab(v, a, w, K.TOE, CAB_H)
    C._rect(v, a, CAB_H, b, CAB_H + TOP_T, C.OUTLINE, fill=WHITE); C.shadow(v, a, b, CAB_H)
    if opt == 'A':
        C._line(v, (a + 1.5, CAB_H + TOP_T), (a + 1.5, BELT0), C.MED); C._line(v, (b - 1.5, CAB_H + TOP_T), (b - 1.5, BELT0), C.MED)
        C._rect(v, a, CAB_H + TOP_T, b, BELT0, C.OUTLINE)
        n = 4; pitch = (BELT0 - CAB_H - TOP_T) / (n + 1)
        for i in range(1, n + 1):
            y = CAB_H + TOP_T + i * pitch; C._rect(v, a + 1.5, y, b - 1.5, y + 1.5, C.MED, fill=WHITE); C.shadow(v, a + 1.5, b - 1.5, y)
    else:
        box(v, a + 4, b - 4, CAB_H + TOP_T + 4, BELT0 - 4)
        C.outlet(v, (a + b) / 2, CAB_H + TOP_T + 4 + 5.0)
    box(v, a + 4, b - 4, FF2 + 4, BOX_TOP)

def east_wall(v, opt='B', study=False):
    L = RD
    floor_line(v, 0, L)
    if opt == 'C':
        C.stone_slab(v, B0, B1, 0, CROWN_B, seams=(CX,)); C._line(v, (B0, BELT0), (B1, BELT0), C.FINE, C.MID)   # four slabs, book-matched in pairs, seam at 10'-0"
        belt(v, 0, B0); belt(v, B1, L); cap(v, 0, B0); cap(v, B1, L)
    else:
        belt(v, 0, L); cap(v, 0, L)
        C.base(v, B0, CX - FB_W / 2 - LEG); C.base(v, CX + FB_W / 2 + LEG, B1)
    crown_cove(v, 0, L); ceiling(v, 0, L)
    for x in (B0, B1): C._line(v, (x, 0), (x, CROWN_B), C.OUTLINE)
    C._line(v, (B1 - 0.75, 0), (B1 - 0.75, CROWN_B), C.FINE, LIGHT)     # shade line on the breast's south return
    flank(v, 0, B0, opt); flank(v, B1, L, opt)
    mantel(v, CX, opt); tv_niche(v, CX)
    if opt in ('A', 'B'): C.art(v, CX, ART_B + ART_H / 2, ART_W, ART_H)
    poche(v, -4, 0, 0, H)                                                # the north wall, cut
    poche(v, L, L + 4, 0, SOFFIT)                                        # the stair wall, cut
    poche(v, L, L + 4, SOFFIT, FF2)                                      # the gallery fascia, closed in front of the stair top, cut
    guard_end(v, L - POST / 2)                                           # the south steel guard, end on at the east wall
    if study:
        return
    tag(v, CX, FB_B + 22, 'GAS FIREPLACE', 5.0, WHITE)
    tag(v, CX, SHELF_T + 2.5, 'WS-01 MANTEL', 5.0, MID, box=True)
    tag(v, CX, TV_C - 1, '75 IN. ART-MODE TV IN A 4 IN. NICHE', 5.0, MID, box=True)
    tag(v, CX, 108, 'PLASTER BREAST, PT-02', 5.0, MID)
    tag(v, B0 / 4, 8.5, 'BUILT-IN', 5.0, MID, box=True); tag(v, B1 + (L - B1) * 0.75, 8.5, 'BUILT-IN', 5.0, MID, box=True)
    tag(v, B0 / 2, 75, 'WP-01', 5.0, MID); tag(v, (B1 + L) / 2, 75, 'WP-01', 5.0, MID)
    tag(v, B0 / 2, 200, 'WP-01', 5.0, MID); tag(v, (B1 + L) / 2, 200, 'WP-01', 5.0, MID)
    tag(v, B0 / 2, BELT0 + 2.4, 'BELT COURSE', 5.0, MID); tag(v, B0 / 2, FF2 + 1.0, 'GALLERY CAP AT FLOOR 2', 5.0, MID)
    tag(v, L / 2, CROWN_B + CRG / 2 - 2, 'CM-02 CROWN', 5.0, MID, box=True)
    y1 = v.Y(0) + 16; y2 = y1 + 27
    dim_h(v, 0, L, y1, E.snap_points([0, B0, CX - FB_W / 2 - LEG, CX - FB_W / 2, CX + FB_W / 2, CX + FB_W / 2 + LEG, B1, L]))
    dim_h(v, 0, L, y2, E.snap_points([0, B0, B1, L]))
    dim_h(v, 0, L, y2 + 27, [0, L], total=' OVERALL, NORTH WALL TO GALLERY LINE')
    dim_v(v, 0, H, v.X(L) + 30, E.snap_points([0, FB_B, FB_T, SHELF_T, N_B, TV_B, TV_T, N_T, BELT0, BELT1, FF2, ART_B, ART_B + ART_H, CROWN_B, H]))
    dim_v(v, 0, H, v.X(L) + 74, E.snap_points([0, CAB_H + TOP_T, BELT0, BELT1, FF2, BOX_TOP, H]))
    return ('PLASTER BREAST PT-02, 7\'-0" x 2\'-0", FLOOR TO CEILING. LISTED DIRECT-VENT GAS FIREPLACE, 42" OPENING, FLUSH ST-01 HEARTH. WS-01 SURROUND, 6" SHELF AT 4\'-0". '
            '75" TV FLUSH IN A 4" NICHE, POWER AND DATA IN THE NICHE. BUILT-INS PT-01 WITH WS-01 TOPS, WP-01 PANELING, CM-02 CROWN.')

PICK_PITCH = 18.0; PICK_THICK = 2.0                  # option 7: 2 in. shelves about 18 in. on center, one bay each side
def east_wall_pick(v):
    """Owner pick 11.09.26 (ID-235 option 7 with his changes): floor to ceiling open shelves each side, one bay, painted; the closed band
    from the belt to the gallery cap carries one panel each side (the wainscot break of option 8, ID-236 view C); a brass rail on the belt
    course with a small rolling ladder that moves along it and lifts off to the other side; the chimney breast one plaster plane from the
    floor to the crown, nothing crossing it."""
    import build_great_s2 as S
    L = RD; CT = S.CASE_TOP
    floor_line(v, 0, L)
    C.base(v, B0, CX - FB_W / 2 - LEG); C.base(v, CX + FB_W / 2 + LEG, B1)
    crown_cove(v, 0, L); ceiling(v, 0, L)
    for x in (B0, B1): C._line(v, (x, 0), (x, CROWN_B), C.OUTLINE)
    C._line(v, (B1 - 0.75, 0), (B1 - 0.75, CROWN_B), C.FINE, LIGHT)     # shade line on the breast's south return
    for i, (a, b) in enumerate(((0, B0), (B1, L))):
        S.base_cab(v, a, b)
        S.case(v, a, b, CAB_H + TOP_T, BELT0, 1, PICK_PITCH, PICK_THICK, 0.35, 23 + 7 * i)
        belt(v, a, b)
        box(v, a + 4, b - 4, BELT1 + 4, FF2 - 5.5)                     # the wainscot break: one painted panel in the band
        cap(v, a, b)
        S.case(v, a, b, FF2, CT, 1, PICK_PITCH, PICK_THICK, 0.35, 28 + 7 * i)
    mantel(v, CX, 'B'); tv_niche(v, CX)
    S.ladder(v, rail_y=(BELT0 + BELT1) / 2 - 0.625, shelf_pitch=PICK_PITCH, shelf_thick=PICK_THICK)   # the rail centered on the 9'-9" to 10'-4" belt
    band_end(v, 0, BAND_W)                                                 # FOR's 22'-4" band at the window wall, cut
    poche(v, -4, 0, 0, H); poche(v, L, L + 4, 0, SOFFIT); poche(v, L, L + 4, SOFFIT, FF2)
    guard_end(v, L - POST / 2)
    tag(v, CX, FB_B + 22, 'GAS FIREPLACE', 5.0, WHITE)
    tag(v, CX, SHELF_T + 2.5, 'WS-01 MANTEL', 5.0, MID, box=True)
    tag(v, CX, TV_C - 1, '75 IN. ART-MODE TV IN A 4 IN. NICHE', 5.0, MID, box=True)
    tag(v, CX, 150, 'PLASTER BREAST, PT-02,', 5.0, MID); tag(v, CX, 142, 'ONE PLANE FLOOR TO CEILING', 5.0, MID)
    tag(v, B0 * 0.62, 8.5, 'BUILT-IN', 5.0, MID, box=True); tag(v, B1 + (L - B1) * 0.75, 8.5, 'BUILT-IN', 5.0, MID, box=True)
    tag(v, (B1 + L) / 2, BELT0 + 2.0, 'BELT COURSE, BRASS RAIL', 5.0, MID, box=True)
    tag(v, B0 / 2, (BELT1 + FF2) / 2 - 1.5, 'PANEL', 5.0, MID); tag(v, (B1 + L) / 2, (BELT1 + FF2) / 2 - 1.5, 'PANEL', 5.0, MID)
    tag(v, (B1 + L) / 2, S.CASE_TOP + 4.0, 'OPEN SHELVES PT-01', 5.0, MID)
    tag(v, 38.0, 92.5, 'ROLLING LADDER', 5.0, MID, box=True)
    tag(v, L / 2, CROWN_B + CRG / 2 - 2, 'CM-02 CROWN, LED COVE ABOVE', 5.0, MID, box=True)
    C.rev_cloud(v, 0, 0.5, L, H, pad=1.0)                               # rev 1: the wall redrawn as the owner's pick
    y1 = v.Y(0) + 16; y2 = y1 + 27
    dim_h(v, 0, L, y1, E.snap_points([0, B0, CX - FB_W / 2 - LEG, CX - FB_W / 2, CX + FB_W / 2, CX + FB_W / 2 + LEG, B1, L]))
    dim_h(v, 0, L, y2, E.snap_points([0, B0, B1, L]))
    dim_h(v, 0, L, y2 + 27, [0, L], total=' OVERALL, NORTH WALL TO GALLERY LINE')
    dim_v(v, 0, H, v.X(L) + 30, E.snap_points([0, FB_B, FB_T, SHELF_T, N_B, TV_B, TV_T, N_T, BELT0, BELT1, FF2, CROWN_B, H - COVE, H]))
    dim_v(v, 0, H, v.X(L) + 74, E.snap_points([0, CAB_H + TOP_T, BELT0, BELT1, FF2, CT, H]))
    return ('PLASTER BREAST PT-02, 7\'-0" x 2\'-0", ONE PLANE FLOOR TO CEILING, NO BELT OR CAP ACROSS IT. LISTED DIRECT-VENT GAS FIREPLACE, 42" OPENING, FLUSH ST-01 HEARTH. '
            'WS-01 SURROUND, 6" SHELF AT 4\'-0". 75" TV FLUSH IN A 4" NICHE, POWER AND DATA IN THE NICHE. BUILT-INS PT-01: 30" CABINETS, WS-01 TOPS, OPEN SHELVES ONE BAY EACH SIDE, 2" SHELVES ABOUT 18" O.C. '
            'WITH STEEL FLATS, A PAINTED PANEL IN THE %s TO 12\'-10" BAND, SHELVES TO %s. BRASS RAIL ON THE BELT COURSE, ROLLING LADDER 18" WIDE, MOVES ALONG THE SHELVES AND LIFTS OFF '
            'TO THE OTHER SIDE. CEILING 22\'-8" (FOR), 22\'-4" BAND AT THE WINDOW WALL. CM-02 CROWN 4" BELOW THE CEILING WITH AN LED COVE ON ITS TOP, SEE 4/ID-502.' % (E.ftin(BELT1), E.ftin(CT)))

# ================================================================== FOR REV 1 PLAN block (11.05.26): FOR A-201 / A-202 REV 1 sheet points, 1.5 pt per inch.
# Floor 1 and floor 2 register on FOR's sheets (east wall face 1045.8 and north wall face 555.8 on both).
FIN = 1.5
R1_E = 1046.2                 # east wall face (the fireplace wall), A-201 drywall
R1_N = 555.8                  # north wall face (the window wall)
R1_GL = 764.2                 # gallery line on the west: floor 2 slab edge (A-202 hall outline); FOR's glass at 767.5 / 767.9
R1_GS = 844.5                 # gallery line on the south: floor 2 slab edge; FOR's glass at 842.5 / 842.8 (A-GLASS RAILING)
R1_GLASS_W = 767.5; R1_GLASS_S = 842.8
R1_WZ_W = 626.2               # the living room's west end (REV 1): its west wall face
R1_WZ_S = 846.0               # its south face (the laundry's north wall); closet 27's north wall face is on the same line
R1_D16 = (742.7, 796.7)       # door 16 to the guest bedroom in the west wall, A-DOOR jambs (3'-0" opening)
R1_SZ_W = 764.5               # the south end's west wall face (the back hall wall, door 12 at 978.8 to 1028.0 on it)
R1_CW = (972.2, 981.2)        # closet 27's west wall (door 27 at 933.4 to 976.6 on it, hinged south, swings west)
R1_KW = (875.0, 980.0, 1066.5, 1074.0)   # the 5" wall on the north side of the lower flight: x0, x1, y0, y1
R1_LF = (880.1, 979.1)        # lower flight: bottom riser, top riser at the southeast landing (7 risers, 16.5 pt = 11" treads)
R1_S = 1139.5                 # the living room's south face (the entry wall)
R1_ENT = (780.7, 859.1)       # the cased opening to the entry in it (A-WALL-HEAD 1140.2 to 1152.5)
R2_HW = 698.5                 # floor 2: the hall's west wall face
R2_HW_B = 688.5               # its back face (the W.I.C. side)
R2_DEN = (644.8, 824.2)       # the den, open to the hall in REV 1 (no wall, returns at 695.8)
R2_HS = 912.2                 # the hall's south wall face (hall side)
R2_D18 = (713.3, 765.5)       # door 18 to the master bedroom (A-DOOR jambs), hinged west, swings south
R2_D22 = (862.6, 911.8)       # door 22 to the linen closet, hinged east, swings north into the hall
R2_TF = (930.7, 980.2)        # top flight: top riser at floor 2, bottom riser at the northeast landing (4 risers)
R2_STW = 980.0                # the stairwell's west edge on floor 2 (the hall outline)
R_RISER = 7.3125              # FOR A-411: 21 risers at 7-5/16" (lower 7, east flight 10, top 4) to floor 2 at 12'-10" (FOR's total is 7/16" short)
LAND_SE = 7 * R_RISER         # 4'-3-5/16" (FOR LOWER LANDING)
LAND_NE = 17 * R_RISER        # 10'-4-5/16" (FOR UPPER LANDING 10'-4-11/16" as printed)
STRUCT = 12.0                 # landing and flight structure under the nosing line (VERIFY)
GUARD_NOTE = ('STEEL GUARD TO RESIST 200 LB AT THE TOP RAIL AND 50 LB ON 1 SQ FT AT THE INFILL (FBC R301.5), POSTS AND THEIR CONNECTION TO THE GALLERY FRAMING '
              'DESIGNED AND SEALED BY THE ENGINEER, PAINTED PT-01 OR AS SELECTED')
PICKET = 0.75; PICK_CLR = 3.75                # 3/4" square pickets, 3-3/4" clear (under the 4" sphere)
TRAIL = 2.5; BRAIL0, BRAIL1 = FF2 + 2.0, FF2 + 3.5   # top rail 1-1/2" x 2-1/2" (its 2-1/2" face seen), bottom rail 1-1/2" held 2" above floor 2
HR_OFF = 2.25 * 1.5                           # handrail CL 2-1/4" off the wall face in FOR pt: 1-1/2" clear to a 1-1/2" rail (FBC R311.7.8)
POST = 2.0; POST_MAX = 72.0                   # 2" square posts at the ends, the corner and 6'-0" o.c. max
def rq(a, b): return q((b - a) / FIN)

def _pack(items, gap=3.0):
    """1D label packing: items (want, half_len) in order; returns centers with no two labels closer than gap."""
    out = []
    for want, h in items:
        c = want if not out else max(want, out[-1][0] + out[-1][1] + gap + h)
        out.append((c, h))
    for i in range(len(out) - 2, -1, -1):                     # pull back toward the wanted positions where there is room
        c, h = out[i]; nc, nh = out[i + 1]
        out[i] = (min(c, nc - nh - gap - h), h)
    return [c for c, _ in out]

def _ticks_v(v, x_pt, ys):
    v.line((x_pt, ys[0]), (x_pt, ys[-1]), 0.4)
    for y in ys:
        v.line((x_pt - 3, y), (x_pt + 3, y), 0.4); v.line((x_pt - 1.8, y + 1.8), (x_pt + 1.8, y - 1.8), 0.6)

def dim_v(v, y0i, y1i, x_pt, pts_i, side='r'):
    """Vertical string: a label that fits sits beside the line between its ticks, one that does not goes out on a leader to a packed column."""
    E.check_string(pts_i, v.w.get('room'), v.w.get('view'))
    _ticks_v(v, x_pt, [v.Y(t) for t in pts_i])
    out = []
    for a, b in zip(pts_i, pts_i[1:]):
        if b - a < 0.5: continue
        lab = E.ftin(b - a); w = FREG.text_length(lab, fontsize=5.5); cy = (v.Y(a) + v.Y(b)) / 2
        if abs(v.Y(a) - v.Y(b)) >= w + 7: v.text(x_pt - 2.5, cy, lab, 5.5, align='c', rotate=90)
        else: out.append((cy, w / 2, lab))
    out.sort()
    for (cy, h, lab), c in zip(out, _pack([(cy, h) for cy, h, _ in out])):
        v.line((x_pt + 3.5, cy), (x_pt + 6.0, cy), 0.3); v.line((x_pt + 6.0, cy), (x_pt + 9.0, c), 0.3)
        v.text(x_pt + 16.0, c, lab, 5.5, align='c', rotate=90)
    if len(pts_i) > 2 and pts_i[-1] - pts_i[0] >= 90:      # review 11.09.26: overall floor-to-ceiling string outside the chain
        xo = x_pt + 26.0; _ticks_v(v, xo, [v.Y(pts_i[0]), v.Y(pts_i[-1])])
        v.text(xo - 2.5, (v.Y(pts_i[0]) + v.Y(pts_i[-1])) / 2, E.ftin(pts_i[-1] - pts_i[0]), 5.5, align='c', rotate=90)

def dim_h(v, x0i, x1i, y_pt, pts_i, total=None):
    """Horizontal string: labels that fit above the line, the rest below it on leaders, packed so none touches a tick or another label."""
    E.check_string(pts_i, v.w.get('room'), v.w.get('view'))
    xs = [v.X(t) for t in pts_i]
    v.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
    for x in xs:
        v.line((x, y_pt - 3), (x, y_pt + 3), 0.4); v.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)
    out = []
    for a, b in zip(pts_i, pts_i[1:]):
        if b - a < 0.5: continue
        lab = E.ftin(b - a) + (total or ''); w = FREG.text_length(lab, fontsize=5.5); cx = (v.X(a) + v.X(b)) / 2
        if v.X(b) - v.X(a) >= w + 6: v.text(cx, y_pt - 2.5, lab, 5.5, align='c')
        else: out.append((cx, w / 2, lab))
    keep = []
    for cx, h, lab in out:
        if abs(cx - (xs[0] + xs[1]) / 2) < 0.01: v.text(xs[0] - 4.0, y_pt + 2.0, lab, 5.5, align='r')
        elif abs(cx - (xs[-2] + xs[-1]) / 2) < 0.01: v.text(xs[-1] + 4.0, y_pt + 2.0, lab, 5.5, align='l')
        else: keep.append((cx, h, lab))
    out = sorted(keep)
    for (cx, h, lab), c in zip(out, _pack([(cx, h) for cx, h, _ in out], 4.0)):
        v.line((cx, y_pt + 3.5), (c, y_pt + 6.0), 0.3)
        v.text(c, y_pt + 13.0, lab, 5.5, align='c')

def hid(v, a, b, w=None, c=None, d='[2 1.5] 0'):
    """A dashed (hidden) line drawn open, so the dash pattern is not overdrawn by a closing stroke."""
    sh_ = v.p.new_shape(); sh_.draw_line(fitz.Point(v.X(a[0]), v.Y(a[1])), fitz.Point(v.X(b[0]), v.Y(b[1])))
    sh_.finish(color=MID if c is None else c, width=C.MED if w is None else w, dashes=d, closePath=False); sh_.commit()

def fascia_flat(v, x0, x1):
    """The gallery beam face: painted, a bed moulding at the soffit, a 1-1/4" cap at floor 2 that the steel guard stands on."""
    C._rect(v, x0, SOFFIT, x1, FF2, C.OUTLINE, fill=WHITE)
    C._rect(v, x0, SOFFIT, x1, SOFFIT + 2.0, C.MED); C._line(v, (x0, SOFFIT + 1.0), (x1, SOFFIT + 1.0), C.FINE, C.MID)
    C._rect(v, x0, FF2 - 1.25, x1, FF2, C.MED)
    C.shadow(v, x0, x1, SOFFIT)
def guard_posts(x0, x1):
    """Post centers: the two ends and equal bays no wider than POST_MAX."""
    n = max(1, math.ceil((x1 - x0 - POST) / POST_MAX))
    return [x0 + POST / 2 + i * (x1 - x0 - POST) / n for i in range(n + 1)]
def metal_guard(v, x0, x1):
    """The painted steel guard seen face-on, standing on the fascia cap: 2" posts (ends, corner, 6'-0" o.c. max), a 1-1/2" x 2-1/2" top rail
    with an eased cap at 3'-6" above floor 2, a 1-1/2" bottom rail 2" above the floor, 3/4" square pickets at 3-3/4" clear between. Open, so what is beyond reads through."""
    posts = guard_posts(x0, x1)
    C._rect(v, x0, GT - TRAIL, x1, GT, C.OUTLINE, fill=WHITE)
    C._line(v, (x0, GT - 0.6), (x1, GT - 0.6), C.FINE, C.MID)                      # the eased cap
    C._rect(v, x0, BRAIL0, x1, BRAIL1, C.MED, fill=WHITE)
    for a, b in zip(posts, posts[1:]):
        lo, hi = a + POST / 2, b - POST / 2
        n = max(1, math.ceil((hi - lo - PICK_CLR) / (PICKET + PICK_CLR) - 1e-6))      # clear never over 3-3/4", every view
        clr = (hi - lo - n * PICKET) / (n + 1)
        x = lo + clr
        for _ in range(n):
            C._rect(v, x, BRAIL1, x + PICKET, GT - TRAIL, C.FINE, INK); x += PICKET + clr
    for c in posts:
        C._rect(v, c - POST / 2, FF2, c + POST / 2, GT + 0.75, C.OUTLINE, fill=WHITE)
    return (posts[1] - posts[0]) if len(posts) > 1 else 0
def guard_end(v, x):
    """The guard seen end on at a wall or a corner: its post with the rails behind."""
    C._rect(v, x - POST / 2, FF2, x + POST / 2, GT + 0.75, C.OUTLINE, fill=WHITE)

# ================================================================== west: the gallery over the west end of the living room (FOR REV 1)
def west_wall(v):
    WS, WN = 846.54, 556.14                                  # FOR A-201 drywall: the west end's south face and the north wall face on the west wall line
    L = q((WS - WN) / FIN)                                   # 16'-1-5/8" on this wall (FOR's vectors)
    def Y(y): return (WS - y) / FIN                          # plan y to view x (south at the left)
    lx = q((WS - 796.68) / FIN)                              # FOR's door 16 leaf 742.68 to 796.68: 2'-9-1/4" south of it, 10'-4-3/8" north
    global ART_WX; ART_WX = q((lx + 36 + L) / 2)             # the art centered on the open wall north of the door
    n1 = q(L - (R2_DEN[0] - R1_N) / FIN); n0 = n1 - 120.0     # the den opening on floor 2, FOR 10'-0"
    g0 = q(Y(R1_GLASS_S))                                     # the glass corner
    floor_line(v, 0, L)
    with beyond():   # floor 1: the west end's west wall 7'-8-5/8" behind the gallery line, its 10'-8" ceiling and CM-01
        C.base(v, 0, L)                                       # owner 11.09.26: door 16 a recessed hidden door, base and crown run across it
        C.crown(v, 0, L, SOFFIT, drop=CR10)
        C.jib_door(v, lx, 36.0, 96.0)
        C.art(v, ART_WX, 62.0, 60.0, 42.0)                    # owner 11.09.26: one piece of art on this wall
        C.outlet(v, L - 54.0, 18.0)                               # 4'-6" from the north corner: 5'-11" to the arch jamb around the 1'-5" pier (NEC 210.52(A))
        # floor 2: the hall's west wall 3'-8-5/8" behind the gallery line, the den open to the hall between its returns
        C._line(v, (0, FF2), (L, FF2), C.MED)
        u = up(v)
        for x in (n0, n1): C._line(v, (x, FF2), (x, HALL_C), C.MED)
        C._line(v, (0, HALL_C), (L, HALL_C), C.MED)                        # the floor 2 hall ceiling beyond, 9'-6" (FOR)
        C.crown(v, n1, L, HALL_C, drop=CR10)
        C._line(v, (n0 + 18.0, FF2), (n1 - 18.0, FF2), C.FINE)                  # the den floor beyond
    ceiling(v, 0, L)
    band_end(v, L - BAND_W, L)                                               # FOR's 22'-4" band at the window wall, cut
    fascia_flat(v, 0, L)
    bay = metal_guard(v, g0, L)                                              # the corner post at g0 carries the south run, end on
    poche(v, -5, 0, 0, SOFFIT); poche(v, -4, 0, SOFFIT, FF2)                 # the laundry wall and the south gallery fascia, cut (4", as view 1)
    poche(v, L, L + 5, 0, H)                                                 # the north wall, cut
    tag(v, lx + 18, 106, 'HIDDEN DOOR 16', 5.0, GREY); tag(v, ART_WX, 104, 'WEST END OF THE LIVING ROOM BEYOND, PT-02, CM-01', 5.0, GREY, box=True)
    C.rev_cloud(v, lx - 4, 1.5, L - 6, 112, pad=1.0)                                        # rev 1: hidden door, art
    tag(v, (n0 + n1) / 2, FF2 + 70, 'DEN BEYOND, OPEN TO THE HALL', 5.0, GREY, box=True)
    tag(v, (n1 + L) / 2, FF2 + 100, 'HALL WALL', 5.0, GREY)
    tag(v, (n0 + n1) / 2, GT + 5, 'STEEL PICKET GUARD 3\'-6"', 5.0, MID, box=True)
    tag(v, L / 2, SOFFIT + 5, 'GALLERY FASCIA', 5.0, MID)
    y1 = v.Y(0) + 16; y2 = y1 + 27
    dim_h(v, 0, L, y1, E.snap_points([0, lx, lx + 36, ART_WX, L]))
    dim_h(v, 0, L, y2, E.snap_points([0, n0, n1, L]))
    dim_h(v, 0, L, y2 + 27, [0, L], total=' OVERALL, LAUNDRY WALL TO NORTH WALL (FOR)')
    dim_v(v, 0, H, v.X(L) + 30, E.snap_points([0, 96, SOFFIT, FF2, GT, HALL_C, H]))
    return ('GALLERY FASCIA PT-01. PAINTED STEEL GUARD 3\'-6" ABOVE FLOOR 2: 3/4" PICKETS, 3-3/4" CLEAR (4" SPHERE MAX), 2" POSTS AT %s O.C. MAX. '
            'GUARD TO RESIST 200 LB AT THE TOP RAIL AND 50 LB AT THE INFILL, POSTS AND CONNECTION BY THE ENGINEER. BEYOND: DOOR 16 A RECESSED HIDDEN DOOR (FLUSH LEAF, CONCEALED HINGES, TOUCH LATCH, NO CASING, BASE AND CROWN ACROSS), '
            'ONE ARTWORK 5\'-0" x 3\'-6" CENTERED ON THE OPEN WALL AT 5\'-2", THE DEN OPEN TO THE HALL. CEILINGS (FOR): LIVING 22\'-8" WITH A 22\'-4" BAND AT THE WINDOW WALL, WEST END 10\'-8", FLOOR 2 HALL 9\'-6".' % E.ftin(q(bay)))

def north_wall(v):
    L = NL
    GX = GFW                                   # the gallery line in this view
    S0, S1 = GX + SL_X0, GX + SL_X0 + SL_W     # slider jambs (FOR REV 1)
    BIF = L - BI_D                             # the east built-in face
    HALL_W = R2_HALL_N[0]                      # floor 2: the hall's west wall face
    ax0, aw = ARCH                             # FOR: 1'-5" | 4'-10" | 1'-5"
    floor_line(v, 0, L)
    # the west end under floor 2: its north wall flush with the living room's, the kitchen's arched opening, ceiling 10'-8" (YL), CM-01
    crown_y = arched_cased_opening(v, ax0, aw, 86.0, aw * 0.62)
    C.base(v, 0, ax0 - 5); C.base(v, ax0 + aw + 5, S0 - 1); C.outlet(v, (ax0 + aw + 5 + S0) / 2, 18.0)
    C.crown(v, 0, GX, SOFFIT, drop=CR10)
    with beyond(): tag(v, ax0 + aw / 2, 50, 'KITCHEN BEYOND', 5.0, GREY)
    poche(v, 0, GX, SOFFIT, FF2)                                       # the floor 2 slab over the west end, cut
    poche(v, HALL_W - 4.875, HALL_W, FF2, H)                           # floor 2: the hall's west wall, cut
    with beyond():   # floor 2: the hall going north 5'-6" to the bedroom 3 door
        u = up(v)
        hd0 = R2_HALL_N[1]
        C.base(u, HALL_W, hd0 - 5); C.base(u, hd0 + 34 + 5, GX)
        C.casing(u, hd0, 34.0, 96.0); C.door_leaf(u, hd0, 34.0, 96.0, panels=2, swing='R')
        C.crown(v, HALL_W, GX, HALL_C, drop=CR10)                        # the floor 2 hall, 9'-6" (FOR)
        tag(v, hd0 + 17, FF2 + 30, 'BEDROOM 3 DOOR', 5.0, GREY, box=True)
    guard_end(v, GX + POST / 2)                                         # the west steel guard, end on at the north wall
    # the double-height window wall: FOR's three-panel slider, the belt as the band between, FOR's three-lite clerestory over it
    C.base(v, S1 + 1, BIF)
    glazed_unit(v, S0, SL_W, 0, SL_HEAD, 3, operable=True)
    glazed_unit(v, S0, SL_W, CL_SILL, CL_HEAD, 3)
    C.rev_cloud(v, S0 + 1, 1.5, S1 - 1, CL_HEAD, pad=1.5)                                    # rev 1: divided lites
    C.rev_cloud(v, GX + 12, BELT0 - 3, S0 - 4, FF2 + 3, pad=1.0, tag_at='tl')                 # rev 1: belt and cap removed either side
    C.rev_cloud(v, S1 + 4, BELT0 - 3, BIF - 2, FF2 + 3, pad=1.0, tag_at='tr')                                  # rev 1: divided lites, belt and cap removed either side
    belt(v, S0 - 1, S1 + 1)                    # owner 11.09.26: the band only between the slider and the clerestory, no belt or cap on the wall either side
    PK0, PK1 = S0 - 15, S1 + 15                 # FOR's 5" drapery pocket, 14" past each jamb
    for a_, b_ in ((GX, PK0), (PK1, L)):        # CM-02 held 4" under the band with the LED cove (as ID-231), stopping at the pocket ends so the drape drops clear
        crown_cove(v, a_, b_, ceil=BAND)
    for x_ in (PK0, PK1): C._line(v, (x_, BAND - COVE - CRG), (x_, BAND - COVE), C.MED)   # crown returns into the band at the pocket
    ceiling(v, HALL_W, GX, y=HALL_C); C._line(v, (GX, HALL_C), (GX, H), C.HEAVY); ceiling(v, GX, L)
    C._rect(v, GX, BAND, L, H, C.MED, fill=WHITE)                           # FOR's 22'-4" band at the window wall, its face seen
    C._rect(v, S0 - 14 - 1, BAND - 0.5, S1 + 14 + 1, H - 0.25, C.FINE, MID, dashes='[2 1.5] 0')   # 5" drapery pocket up into the band (FOR C-1)
    section(v, BIF, L, 0, CAB_H + TOP_T); C._line(v, (BIF, CAB_H), (L, CAB_H), C.FINE, INK)
    C._line(v, (L - 1.0, CAB_H + TOP_T), (L - 1.0, BELT0), C.FINE, INK); C._line(v, (L - 1.0, FF2), (L - 1.0, CROWN_B), C.FINE, INK)
    poche(v, -5, 0, 0, SOFFIT); poche(v, L, L + 5, 0, H)
    tag(v, ax0 + aw / 2, 64, 'ARCHED OPENING', 5.0, MID)
    tag(v, (S0 + S1) / 2, 24, 'FOR SLIDER, 3 PANELS', 5.0, MID, box=True)
    tag(v, (S0 + S1) / 2, CL_SILL + 22, 'FOR CLERESTORY, 3 LITES', 5.0, MID, box=True)
    tag(v, (S0 + S1) / 2, H + 6, '22\'-4" BAND, 5" DRAPERY POCKET (FOR)', 5.0, MID)
    tag(v, GX / 2, SOFFIT - CR10 / 2 - 2, 'CM-01', 5.0, MID, box=True)
    tag(v, (GX + S0) / 2, 60, 'PT-02', 5.0, MID)
    y1 = v.Y(0) + 16; y2 = y1 + 27
    C._line(v, (GX + POST, GT - 4.0), (GX + 6.0, GT + 6.0), C.FINE, MID); v.rect(v.X(GX + 5.5), v.Y(GT + 10.0) - _ish.ps(5.0) * 0.95, v.X(GX + 5.5) + FREG.text_length('END POST', fontsize=5.0) + 3.0, v.Y(GT + 10.0) + 2.2, 0, fill=WHITE); v.text(v.X(GX + 6.5), v.Y(GT + 10.0), 'END POST', 5.0, MID, align='l')   # the end post, tagged in the clear bay beside it
    dim_h(v, 0, L, y1, E.snap_points([0, ax0, ax0 + aw, GX, S0, S1, BIF, L]))
    dim_h(v, 0, L, y2, E.snap_points([0, GX, L]))
    dim_v(v, 0, H, v.X(L) + 30, E.snap_points([0, SL_HEAD, CL_SILL, FF2, CL_HEAD, BAND - COVE - CRG, BAND - COVE, BAND, H]))
    return ('FOR\'S 3-PANEL SLIDER D03 %s x 9\'-9", FIXED CLERESTORY G ABOVE, 11\'-0" x 10\'-6" FROM 10\'-4" TO 20\'-10", DIVIDED LITES, DRYWALL RETURNS, NO CASING. 9\'-9" TO 10\'-4" BAND (FOR\'S HSS BEAM) BETWEEN THE SLIDER AND THE CLERESTORY ONLY, NO BELT OR CAP ON THE WALL EITHER SIDE. '
            'CEILING 22\'-8" WITH FOR\'S 22\'-4" BAND AT THIS WALL: 5" DRAPERY POCKET IN THE BAND WITH POWER. CM-02 CROWN 4" BELOW THE BAND WITH AN LED COVE ON ITS TOP, SEE 4/ID-502, STOPPING AT THE POCKET ENDS SO THE DRAPERY DROPS CLEAR. FLOOR 2 HALL 9\'-6". ARCHED OPENING TO THE KITCHEN AT THE LEFT.' % E.ftin(SL_W))

def south_wall(v):
    L = NL                                                    # 23'-3-1/2", the east wall face to the west end's west wall
    def X(x): return q((R1_E - x) / FIN)                      # plan x to view x (east at the left)
    PX = 49.0                                                 # FOR 4'-1": closet 27's west wall, the end of the closet wall
    GX = RW                                                   # 15'-7", the gallery line (the south end's west wall below it)
    HALL_W, HALL_B = X(R2_HW), X(R2_HW_B)                     # floor 2: the hall's west wall, cut
    T0, T1 = 44.0, 77.0                                       # FOR 3'-8" landing, 2'-9" top flight, 9'-2" to the gallery line
    K0, K1 = X(R1_CW[0]), X(R1_KW[0])                         # the lower flight's half wall, seen from the closet wall to its west end
    LF0, LF1 = (R1_E - R1_LF[1]) / FIN, (R1_E - R1_LF[0]) / FIN   # the lower flight's top and bottom risers
    E0, E1 = X(R1_ENT[1]), X(R1_ENT[0])                       # the cased opening to the entry beyond
    D22 = (X(R2_D22[1]), X(R2_D22[0])); D18 = (X(R2_D18[1]), X(R2_D18[0]))
    l22 = q((D22[0] + D22[1]) / 2 - 17.0); l18 = q((D18[0] + D18[1]) / 2 - 18.0)   # FOR leaves: door 22 2'-10", door 18 3'-0"
    def nose_tf(x): return LAND_NE + R_RISER + (x - T0) * R_RISER / 11.0         # the top flight's nosing line
    def nose_lf(x): return R_RISER + (LF1 - x) * (LAND_SE - R_RISER) / (LF1 - LF0)   # the lower flight's nosing line
    FUR = q(nose_tf(PX) - STRUCT)                             # the flight's underside at the closet wall, 10'-4-3/8"
    FUR_X = q(T0 + (SOFFIT + STRUCT - LAND_NE - R_RISER) * 11.0 / R_RISER)          # where the underside meets the 10'-8" head
    floor_line(v, 0, L)
    # floor 1 at the gallery line: the built-in end cut, closet 27's north wall, the open south end, the laundry wall under the west end
    C.base(v, BI_D, PX); C.outlet(v, (BI_D + PX) / 2, 18.0)
    C._line(v, (PX, 0), (PX, FUR), C.OUTLINE); C._line(v, (GX, 0), (GX, SOFFIT), C.OUTLINE)
    C._rect(v, PX, FUR, FUR_X, SOFFIT, C.OUTLINE, fill=WHITE)                 # the top flight's underside, furred down past the closet wall
    C.base(v, GX, L); C.crown(v, GX, L, SOFFIT, drop=CR10); C.outlet(v, L - 36.0, 18.0)   # 3'-0" from the west corner: 5'-9-1/4" to door 16 around it
    C.art(v, (GX + L) / 2, 60.0, 54.0, 40.0)                                               # owner 11.09.26: artwork on this wall
    C.rev_cloud(v, GX + 4, 34, L - 4, 86, pad=3.0)
    with beyond():   # the south end beyond: FOR's sloped ceiling (A-411 sec 04: 9'-0" at the walls up to a 10'-8" flat center), no crown
        C._line(v, (K1, SLOPE0), (GX, SLOPE0), C.MED)                         # the entry wall's top, 9'-0"
        C._line(v, (GX, SLOPE0), (GX - SLOPE_RUN, SOFFIT), C.FINE)          # the hip at the southwest corner, rising to the flat center
        C._line(v, (K1, SLOPE0), (K1 + SLOPE_RUN, SOFFIT), C.FINE)           # and at the half wall end
        kt0, kt1 = nose_lf(K0) + 42.0, nose_lf(K1) + 42.0
        C._poly(v, [(K0, 0), (K0, kt0), (K1, kt1), (K1, 0)], C.MED, fill=WHITE)
        C._poly(v, [(K0, kt0), (K0, kt0 + 1.5), (K1, kt1 + 1.5), (K1, kt1)], C.MED, fill=WHITE)   # cap
        C._line(v, (K0, 0), (K1, 0), C.MED)
        hid(v, (K0, nose_lf(K0) + 36.0), (LF1, nose_lf(LF1) + 36.0), C.MED, GREY)          # the handrail, 1-1/2" round, on the stair side (hidden)
        hid(v, (K0, nose_lf(K0) + 34.5), (LF1, nose_lf(LF1) + 34.5), C.FINE, GREY)
        xm_ = (K0 + K1) / 2
        C._line(v, (xm_, nose_lf(xm_) + 17.0), (xm_, nose_lf(xm_) + 35.5), C.FINE, GREY)
        tag(v, xm_, nose_lf(xm_) + 13.5, 'HANDRAIL (HIDDEN)', 5.0, GREY)
        C.base(v, K1, E0 - 5.0); C.base(v, E1 + 5.0, GX)
        ew = E1 - E0; er = ew * 0.62                          # owner 11.09.26: arched, the same arch as the kitchen opening (top at 8'-4-3/4")
        arched_cased_opening(v, E0, ew, 100.75 - er + math.sqrt(er ** 2 - (ew / 2) ** 2), er)
        tag(v, (E0 + E1) / 2, 50, 'ARCHED OPENING, ENTRY BEYOND', 5.0, GREY)
        C.rev_cloud(v, E0 - 6, 1.5, E1 + 6, 104, pad=1.0)
        tag(v, (K0 + K1) / 2, 24, 'STAIR UP BEHIND THE HALF WALL', 5.0, GREY)
        # floor 2 beyond the glass: the hall's south wall with the linen closet door 22 and the master bedroom door 18, the stairwell over the landing
        C._line(v, (T1, FF2), (GX, FF2), C.MED)
        u = up(v)
        C.casing(u, l22, 34.0, 96.0); C.door_leaf(u, l22, 34.0, 96.0, panels=2, swing=None, pull='R')
        C.casing(u, l18, 36.0, 96.0); C.door_leaf(u, l18, 36.0, 96.0, panels=2, swing=None, pull='L')
        C._line(v, (X(R2_STW), GT + 0.75), (X(R2_STW), H), C.MED)              # the stairwell's west edge, above the guard
        C.crown(v, X(R2_STW), HALL_W, HALL_C, drop=CR10)                    # the floor 2 hall's south wall, 9'-6" (FOR)
        tag(v, l22 + 17.0, FF2 + 102, 'LINEN CLOSET', 5.0, GREY); tag(v, l18 + 18.0, FF2 + 102, 'MASTER BEDROOM', 5.0, GREY)
        tag(v, T0 / 2, FF2 + 70, 'STAIR DN', 5.0, GREY)
    poche(v, GX, L, SOFFIT, FF2)                                              # the floor 2 slab over the west end, cut
    poche(v, HALL_W, HALL_B, FF2, H)                                          # floor 2: the hall's west wall, cut
    fascia_flat(v, 0, GX)                                                     # the fascia, carried across in front of the stair as a closed panel
    # the stair top behind the panel (hidden): the northeast landing at 10'-6", three treads up to floor 2, its underside 12" below the nosings
    d = '[2 1.5] 0'
    pts = [(0, LAND_NE), (T0, LAND_NE)]
    for i in range(4):
        x = T0 + 11.0 * i; y = LAND_NE + R_RISER * (i + 1); pts += [(x, y), (min(x + 11.0, T1), y)]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]): hid(v, (xa, ya), (xb, yb))
    hid(v, (0, LAND_NE - STRUCT), (T0, LAND_NE - STRUCT))
    hid(v, (T0, LAND_NE - STRUCT), (T0, nose_tf(T0) - STRUCT))
    hid(v, (FUR_X, SOFFIT), (T1, nose_tf(T1) - STRUCT))
    metal_guard(v, 0, GX)
    ceiling(v, 0, GX); C._line(v, (GX, H), (GX, HALL_C), C.HEAVY); ceiling(v, GX, HALL_W, y=HALL_C)   # the void at 22'-8", the hall over the west end at 9'-6"
    section(v, 0, BI_D, 0, CAB_H + TOP_T); C._line(v, (1.0, CAB_H + TOP_T), (1.0, BELT0), C.FINE, INK); C._line(v, (1.0, FF2), (1.0, CROWN_B), C.FINE, INK)
    poche(v, -5, 0, 0, H); poche(v, L, L + 5, 0, SOFFIT)
    tag(v, (E0 + GX) / 2 - 6.0, SOFFIT - 9, 'OPEN TO THE SOUTH END', 5.0, MID, box=True)   # kept between the slope lines (review 11.09.26)
    tag(v, (E0 + GX) / 2 - 6.0, SOFFIT - 17, 'SLOPED CEILING 9\'-0" TO 10\'-8" (FOR)', 5.0, GREY, box=True)
    tag(v, PX / 2 + 8, 70, 'CLOSET 27 WALL', 5.0, MID)
    tag(v, (GX + L) / 2, 100, 'PT-02', 5.0, MID); tag(v, (GX + L) / 2, SOFFIT - CR10 / 2 - 2, 'CM-01', 5.0, MID, box=True)
    tag(v, (GX + l22 + 40.0) / 2, GT + 5, 'STEEL PICKET GUARD 3\'-6", LEVEL', 5.0, MID, box=True)
    tag(v, GX / 2 + 40, SOFFIT + 5, 'GALLERY FASCIA, CARRIED ACROSS THE STAIR', 5.0, MID)
    y1 = v.Y(0) + 16; y2 = y1 + 27
    dim_h(v, 0, L, y1, E.snap_points([0, BI_D, PX, GX, L]))
    dim_h(v, 0, L, y2, E.snap_points([0, T0, T1, GX, L]))
    dim_v(v, 0, H, v.X(L) + 30, E.snap_points([0, 96, SOFFIT, FF2, GT, HALL_C, H]))
    return ('CLOSET 27 WALL, THEN OPEN TO THE SOUTH END UNDER THE GALLERY BEAM (HEAD 10\'-8", DRYWALL RETURNS). ARCHED CASED OPENING TO THE ENTRY, AS THE KITCHEN ARCH. ART ON THE WEST END WALL. FASCIA CARRIED ACROSS THE STAIR TOP, STEEL PICKET GUARD ON IT, LEVEL AT 3\'-6". '
            'HANDRAILS 1-1/2" ROUND, 3\'-0" ABOVE THE NOSINGS, EVERY FLIGHT. TOP FLIGHT UNDERSIDE FURRED DOWN TO %s. STAIR PER FOR A-411: 21 RISERS AT 7-5/16". '
            'SOUTH END CEILING SLOPES FROM 9\'-0" AT THE WALLS TO 10\'-8" (FOR A-411), NO CROWN; THE ARCH CASING STOPS 2-1/4" UNDER THE 9\'-0" LINE.' % E.ftin(FUR))

OFF5 = B0 - 6.0

def stack_elev(v):
    L = BW + 12.0
    sv = E.ElevationView(v.p, v.F, v.fn, (v.ox - OFF5 * v.k, v.oy), v.k, v.w)
    floor_line(v, 0, L)
    C.base(sv, B0, CX - FB_W / 2 - LEG); C.base(sv, CX + FB_W / 2 + LEG, B1)
    for x in (B0, B1): C._line(sv, (x, 0), (x, BELT1), C.OUTLINE)
    with beyond():   # the built-ins each side, 4 in. behind the breast face
        for a, b in ((OFF5, B0), (B1, B1 + 6)):
            C._rect(sv, a, 0, b, CAB_H + TOP_T, C.MED)
            n = max(1, int(round((BELT0 - CAB_H - TOP_T) / PICK_PITCH)))
            for j in range(1, n): yy = CAB_H + TOP_T + j * (BELT0 - CAB_H - TOP_T) / n; C._rect(sv, a, yy, b, yy + PICK_THICK, C.FINE)   # the open shelves (owner pick)
    mantel(sv, CX, 'B'); tv_niche(sv, CX)
    belt(sv, OFF5, B0); belt(sv, B1, B1 + 6)                            # owner 11.09.26: the belt stops at the breast, the breast is one plane
    C.rev_cloud(sv, B0 + 2, BELT0 - 4, B1 - 2, BELT1 - 1.5, pad=1.0)
    C._rect(sv, CX - 4, N_B + 6, CX + 4, N_B + 14, C.FINE, MID, dashes='[2 1.5] 0'); tag(sv, CX, N_B + 16, 'POWER, DATA, CONDUIT BEHIND', 5.0, MID)
    C._rect(sv, CX - FB_W / 2 - HEARTH_S, -0.01, CX + FB_W / 2 + HEARTH_S, 0.01, C.HEAVY)
    tag(sv, CX, FB_B + 22, 'GAS FIREPLACE', 5.0, WHITE)
    tag(sv, CX, SHELF_T + 2.5, 'WS-01', 5.0, MID, box=True)
    tag(sv, CX, TV_C - 1, '75 IN. ART-MODE TV', 5.2, MID, box=True)
    tag(sv, CX, 106, 'PLASTER BREAST, PT-02', 5.0, MID)
    y1 = v.Y(0) + 16; y2 = y1 + 27
    dim_h(sv, B0, B1, y1, E.snap_points([B0, CX - FB_W / 2 - LEG - SHELF_OV, CX - FB_W / 2 - LEG, CX - FB_W / 2 - 1.5, CX - FB_W / 2, CX + FB_W / 2, CX + FB_W / 2 + 1.5, CX + FB_W / 2 + LEG, CX + FB_W / 2 + LEG + SHELF_OV, B1]))
    dim_h(sv, B0, B1, y2, E.snap_points([B0, CX - TV_W / 2 - NM, CX - TV_W / 2, CX + TV_W / 2, CX + TV_W / 2 + NM, B1]))
    dim_v(v, 0, BELT1, v.X(L) + 18, E.snap_points([0, FB_B, FB_T, SHELF_B, SHELF_T, N_B, TV_B, TV_T, N_T, BELT0, BELT1]))
    return ('WS-01 SURROUND, HONED: 9" LEGS, 9-1/2" FRIEZE, 2-1/2" SHELF 5\'-2" LONG AT 4\'-0", 6" DEEP. GLASS 6" ABOVE A FLUSH ST-01 HEARTH 1\'-8" DEEP. '
            'TV NICHE 70-1/4" x 41-3/4" x 4" DEEP, BOTTOM 6" ABOVE THE SHELF. UNIT LISTED FOR A TV ABOVE.')

def stack_section(v):
    """Section through the breast on the room's centerline, looking north: the room at the left, the east wall at the right."""
    RF = 30.0                                  # breast face, from the view's left edge
    EW = RF + BD                               # east wall inside face
    L = EW + 10.5
    floor_line(v, 0, L)
    poche(v, EW, EW + 10.5, 0, BELT1)          # the east (exterior) wall, cut
    C._rect(v, RF, 0, EW, BELT1, C.OUTLINE)    # the breast: framed chase
    C._rect(v, RF + 2.0, 0, EW - 0.5, 40.0, C.OUTLINE, fill=WHITE)     # the unit (22 in. deep class), cut
    tag(v, (RF + EW) / 2 + 1, 22, 'DIRECT-VENT GAS UNIT', 5.0, MID)
    C._line(v, ((RF + EW) / 2 + 2, 40), ((RF + EW) / 2 + 2, BELT1 - 1), C.MED, MID, '[3 2] 0'); C._line(v, ((RF + EW) / 2 + 5, 40), ((RF + EW) / 2 + 5, BELT1 - 1), C.MED, MID, '[3 2] 0')
    v.text(v.X((RF + EW) / 2 + 4.15), v.Y(70), 'VENT', 5.0, MID, align='c', rotate=90)
    C._rect(v, RF - 1.5, 0, RF, SHELF_B, C.OUTLINE, fill=SEC)       # WS-01 surround
    C._rect(v, RF - SHELF_D, SHELF_B, RF, SHELF_T, C.OUTLINE, fill=SEC)
    C._rect(v, RF, FB_B, RF + 2.0, FB_T, C.OUTLINE, fill=(0.25, 0.25, 0.25))
    C._rect(v, RF, N_B, RF + NICHE_D, N_T, C.OUTLINE, fill=WHITE)    # the niche
    C._rect(v, RF + 0.5, TV_B, RF + 0.5 + TV_D, TV_T, C.OUTLINE, fill=(0.5, 0.5, 0.5))   # the TV, face 1/2 in. behind the breast face
    C._rect(v, RF + 2.4, TV_B + 10, RF + NICHE_D, TV_B + 20, C.FINE)
    C._line(v, (RF + 3.0, N_B), (RF + 3.0, 44.0), C.FINE, MID, '[2 1.5] 0'); v.text(v.X(1), v.Y(62), '2 IN. CONDUIT', 5.0, MID); C._line(v, (17.0, 61.0), (RF + 3.0, 50.0), C.FINE, MID); v.text(v.X(1), v.Y(57.5), 'DOWN THE CHASE', 5.0, MID); v.text(v.X(1), v.Y(53), 'BESIDE THE UNIT', 5.0, MID)
    C.rev_cloud(v, RF - 5, BELT0 - 5, RF + 5, BELT1 - 1.5, pad=1.0)        # rev 1: no belt course on the breast face (owner 11.09.26)
    C._rect(v, RF - HEARTH_D, -1.5, RF, 0, C.OUTLINE, fill=SEC); tag(v, RF - HEARTH_D / 2, 2.5, 'ST-01 HEARTH', 5.0, MID)
    y0s = TV_C - (TV_C - EYE) * RF / SEAT                              # the sight line's last 2'-6", from the eye
    y1 = v.Y(0) + 24; y2 = y1 + 27
    dim_h(v, 0, L, y1, E.snap_points([RF - HEARTH_D, RF - SHELF_D, RF, RF + NICHE_D]))
    dim_h(v, 0, L, y2, E.snap_points([RF - HEARTH_D, RF, EW, L]))
    dim_v(v, 0, BELT1, v.X(L) + 18, E.snap_points([0, FB_B, FB_T, SHELF_T, N_B, N_T, BELT0, BELT1]))
    return ('FRAMED CHASE 2\'-0" DEEP. VENT UP THE CHASE TO THE ROOF. GAS AND 120V TO THE UNIT. NONCOMBUSTIBLE BOARD BEHIND THE SURROUND. '
            'BLOCKING FOR THE TV MOUNT. 2" CONDUIT IN THE SLAB TO THE SOUTH BUILT-IN, SET BEFORE THE POUR.')

def marker(sh, cx, cy, n, sheet, d, r=24.0):
    """Sheet.elev_marker at r=24 (owner 11.07.26: tags on plans bigger), text scaled with the circle: number 11.5 pt, sheet 9.5 pt."""
    calls = []; orig = sh.text; f = r / 24.0
    def t(x, y, s_, size, color=INK, **kw):
        calls.append(1); kw['raw'] = True
        if len(calls) == 1: return orig(x, cy - 5.0 * f, s_, 11.5 * f, color, **kw)
        return orig(x, cy + 15.5 * f, s_, 9.5 * f, color, **kw)
    sh.text = t
    try: sh.elev_marker(cx, cy, n, sheet, d, r=r)
    finally: sh.text = orig

def place_base(sh, pno, clip_disp, k, tx, ty):
    src = fitz.open(BASE_CLEAN); sp = src[pno]
    u = clip_disp * sp.derotation_matrix; u.normalize()
    target = fitz.Rect(tx, ty, tx + clip_disp.width * k, ty + clip_disp.height * k)
    sh.p.show_pdf_page(target, src, pno, clip=u, rotate=90)
    xref = sh.p.get_contents()[0]; st = sh.p.parent.xref_stream(xref).decode('latin1')
    parts = st.split('q ')
    for i in range(1, len(parts)):
        if 'Do' in parts[i] and ' re W n ' not in parts[i]:
            parts[i] = f'{target.x0:.2f} {sh.p.rect.height - target.y1:.2f} {target.width:.2f} {target.height:.2f} re W n ' + parts[i]
    sh.p.parent.update_stream(xref, 'q '.join(parts).encode('latin1'))
    def P(xd, yd): return (target.x0 + (xd - clip_disp.x0) * k, target.y0 + (yd - clip_disp.y0) * k)
    return target, P

def scale_bar_n(sh, x, y, ppf, label):
    """Scale bar with its label at 9 pt and a north arrow beyond it (plan north up, the views are titled by compass direction)."""
    sh.scale_bar(x, y, pt_per_ft=ppf, label='')
    lx = x + 10 * ppf + 12; sh.text(lx, y + 1.0, label, 9.0, INK, raw=True)
    nx = lx + FREG.f.text_length(label, fontsize=9.0) + 46; ny = y - 4
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(nx, ny - 18), fitz.Point(nx + 8, ny + 8), fitz.Point(nx, ny + 2), fitz.Point(nx - 8, ny + 8), fitz.Point(nx, ny - 18)]); s_.finish(color=INK, fill=INK, width=0.4); s_.commit()
    sh.text(nx, ny + 22, 'N', 10.0, INK, align='c', raw=True)

def wall_inset(sh, x, ytop, ybot, which):
    """Floor 1 key plan at 1/4" beside a single-view sheet, centered in the space between the notes and the view's last dimension line:
    the wall drawn heavy, its marker, the caption under the plan (one caption form set-wide: FLOOR n KEY PLAN, scale)."""
    import base_rev1 as BR
    T1 = BR.transform(1); c = fitz.Rect(252, 452, 634, 915); k = 4.0 / 3.0          # 3/16 -> 1/4
    h = c.height * k + 26
    y = ytop + max(0.0, (ybot - ytop - h) / 2)
    import keyclip as KC
    LR1 = KC.area_poly(1, [KC.for_rect(1, R1_E - NL * FIN - 14.0, R1_N - 14.0, R1_E + 14.0, R1_N + RD * FIN)], pad=0.5, doors=True)
    b_ = LR1.bounds; c = fitz.Rect(b_[0] - 6, b_[1] - 6, b_[2] + 6, b_[3] + 6)
    h = c.height * k + 26; y = ytop + max(0.0, (ybot - ytop - h) / 2)
    t, P = place_base(sh, 0, c, k, x, y)
    assert KC.apply(sh.p, t, c, k, LR1), 'key plan clip, inset'
    sh.text(t.x0, t.y1 + 20, 'FLOOR 1 KEY PLAN, 1/4" TO 1\'-0"', 9.0, INK, raw=True)
    def D(xi, yi): return P(*T1(R1_E - (RW - xi) * FIN, R1_N + yi * FIN))
    yw = 0 if which == 'N' else RD
    a, b = D(RW - NL, yw), D(RW, yw); sh.line(a, b, 4.0, (0.85, 0.35, 0.1))
    n = 3 if which == 'N' else 4; cx, cy = D(RW / 2 - 20, 40 if which == 'N' else RD - 36)
    sh.p.draw_circle(fitz.Point(cx, cy), 23.0, color=None, fill=WHITE, width=0); marker(sh, cx, cy, n, 'ID-753' if which == 'N' else 'ID-754', which, r=18.0)
    return t.y1 + 20

def key_plans(sh):
    """ID-751 on FOR REV 1: floor 1 at 3/8" with the south end and the stair (view 4 looks into it), floor 2 at 3/16"."""
    import base_rev1 as BR
    T1 = BR.transform(1); T2 = BR.transform(2)
    # RULE 11.07.26 (owner): a key plan shows only the area the section designs, the double-height living room here, with
    # the openings to the rooms around it; the west end, the south end, the stair and the baths are not shown
    import keyclip as KC
    # the clip takes the full wall on the walled sides (north, east) and stops at the line on the open sides (west, south)
    WALL_T = 14.0                                                      # FOR pt, the exterior wall and its finish
    LR1 = KC.area_poly(1, [KC.for_rect(1, R1_E - NL * FIN - WALL_T, R1_N - WALL_T, R1_E + WALL_T, R1_N + RD * FIN)], pad=0.5, doors=True)
    LR2 = KC.area_poly(2, [KC.for_rect(2, R1_GLASS_W, R1_N - WALL_T, R1_E + WALL_T, R1_GLASS_S)], pad=0.5, doors=False)
    def _r(poly, m=4.0): b = poly.bounds; return fitz.Rect(b[0] - m, b[1] - m, b[2] + m, b[3] + m)
    c1 = _r(LR1); c2 = _r(LR2); GAP = 90.0
    # the largest standard scale at which both clipped plans fit side by side (3/16 base: k = scale / (3/16))
    for k1, SC_LBL in ((8.0 / 3.0, '1/2"'), (2.0, '3/8"'), (4.0 / 3.0, '1/4"')):
        if (c1.width + c2.width) * k1 + GAP <= TB_X - FR.x0 - 80: break
    k2 = k1; PPF = 13.5 * k1
    wtot = c1.width * k1 + GAP + c2.width * k2
    ax0 = FR.x0 + 14 + (TB_X - 14 - FR.x0 - 14 - wtot) / 2
    ay0 = FR.y0 + max(60.0, (FR.y1 - FR.y0 - (max(c1.height * k1, c2.height * k2) + 250.0)) / 2)   # plans, captions and notes centered top to bottom          # the plans, captions and scale bars centered top to bottom
    t1, P = place_base(sh, 0, c1, k1, ax0, ay0)
    assert KC.apply(sh.p, t1, c1, k1, LR1), 'key plan clip, floor 1'
    def F(xf, yf): return P(*T1(xf, yf))                               # FOR REV 1 sheet points, floor 1
    def D(x, y): return F(R1_E - (RW - x) * FIN, R1_N + y * FIN)       # inches: x east of the gallery line, y south of the north wall face (FOR's walls)
    def mask(x, y, s_, size, align):                                   # a white ground under a label so the linework stops at it
        w = FREG.text_length(s_, fontsize=size); x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
        sh.rect((x0 - 3.5, y - size * 1.1, x0 + w + 3.5, y + size * 0.55), width=0, fill=WHITE)   # padded so no line grazes the letters
    def rect(x0, y0, x1, y1, w=0.6, color=INK, fill=None, dashes=None):
        a, b = D(x0, y0), D(x1, y1); sh.rect((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), width=w, color=color, fill=fill, dashes=dashes)
    def line(x0, y0, x1, y1, w=0.5, color=INK, dashes=None): sh.line(D(x0, y0), D(x1, y1), w, color, dashes)
    def text(x, y, s, size=6.0, color=INK, align='c', bg=False):
        a = D(x, y)
        if bg: mask(a[0], a[1], s, size, align)
        sh.text(a[0], a[1], s, size, color, align=align)
    def ftext(xf, yf, s, size=6.0, color=INK, align='c', bg=False):
        a = F(xf, yf)
        if bg: mask(a[0], a[1], s, size, align)
        sh.text(a[0], a[1], s, size, color, align=align)
    # this design's fireplace wall over FOR's 8'-1" x 1'-8" millwork
    rect(RW - 26, 1.0, RW - 0.3, RD - 0.5, 0, None, fill=WHITE)
    rect(RW - BI_D, 0, RW, B0, 0.7); rect(RW - BI_D, B1, RW, RD, 0.7)
    for y in (B0 / 2, B1 + (RD - B1) / 2): line(RW - BI_D, y, RW, y, 0.3, MID)
    rect(RW - BD, B0, RW, B1, 0.9, fill=WHITE)
    rect(RW - BD + 2, CX - FB_W / 2, RW - 2, CX + FB_W / 2, 0.4, MID, dashes='[2 2] 0')
    rect(RW - BD - HEARTH_D, CX - FB_W / 2 - HEARTH_S, RW - BD, CX + FB_W / 2 + HEARTH_S, 0.5, MID, fill=(0.92, 0.92, 0.92))
    rect(RW - BD - SHELF_D, CX - FB_W / 2 - LEG - SHELF_OV, RW - BD, CX + FB_W / 2 + LEG + SHELF_OV, 0.6, INK, dashes='[2 1.5] 0')
    text(RW - BD - 12, CX - 22, 'HEARTH', 5.0, MID)
    text(RW - BI_D / 2, B0 / 2 + 2, 'BI', 5.0, MID); text(RW - BI_D / 2, B1 + (RD - B1) / 2 + 2, 'BI', 5.0, MID)
    text(RW - BD / 2 + 1, CX - 30, 'GAS FP,', 5.0, MID, bg=True); text(RW - BD / 2 + 1, CX - 24, 'TV OVER', 5.0, MID, bg=True)
    # the gallery line, the volume and the parts of the room under floor 2
    line(0, 0, 0, RD, 0.5, MID, '[4 2] 0'); line(0, RD, RW, RD, 0.5, MID, '[4 2] 0')
    text(RW / 2 - 6, RD / 2 - 22, 'LIVING ROOM', 9.0, INK, bg=True)          # below marker 3 (r=24), on a white ground over FOR's X
    text(RW / 2 - 6, RD / 2 - 13, 'OPEN TO ABOVE, 22\'-8"', 5.5, MID, bg=True)
    # the west end is in the section (views 3 and 4 run 23'-4" across it); the south end, the stair and the baths are not
    ftext(696, 700, 'WEST END', 6.0, MID); ftext(696, 709, 'FLOOR 2 ABOVE', 5.5, MID)
    text(RW / 2 + 30, RD - 6, 'OPEN TO THE SOUTH END', 5.5, MID, bg=True)
    # FOR's door 16 (3'-0", hinged at the south jamb, swings west into the guest bedroom): leaf and swing.
    # Owner 11.09.26: a recessed hidden jib door, so FOR's jamb stops come out and the wall runs flush to the leaf.
    hx, hy, r_ = 619.2, 796.7, 54.0
    sh.line(F(hx, hy), F(hx - r_, hy), 0.7, INK)
    pts = [F(hx - r_ * math.sin(math.radians(a)), hy - r_ * math.cos(math.radians(a))) for a in range(0, 91, 5)]
    for a_, b_ in zip(pts, pts[1:]): sh.line(a_, b_, 0.3, INK)
    # FOR's head line over the arched opening to the kitchen in the west end's north wall
    for yh in (540.4, 555.6): sh.line(F(651.7, yh), F(738.7, yh), 0.4, INK, '[3 2] 0')
    ftext(604, 764, 'HIDDEN JIB', 5.0, INK, align='r'); ftext(604, 771, 'DOOR 16,', 5.0, INK, align='r'); ftext(604, 778, 'SEE ID-231', 5.0, INK, align='r')
    for _a, _b in ((739.0, 744.0), (795.4, 801.8)):                     # FOR's stop and jamb blocks, inside the opening only
        _p0, _p1 = F(618.85, _a), F(626.8, _b)
        sh.p.draw_rect(fitz.Rect(min(_p0[0], _p1[0]), min(_p0[1], _p1[1]), max(_p0[0], _p1[0]), max(_p0[1], _p1[1])), color=None, fill=WHITE, width=0)
    _c0, _c1 = F(560.0, 735.0), F(632.0, 805.0)
    _ish.rev_cloud_pt(sh.p, fitz.Rect(min(_c0[0], _c1[0]), min(_c0[1], _c1[1]), max(_c0[0], _c1[0]), max(_c0[1], _c1[1])), '1', tag_at='tl')   # owner 11.09.26: hidden jib door 16
    # dimensions
    def dim(x0, y0, x1, y1, label, side=1, at=0.5):
        a, b = D(x0, y0), D(x1, y1); sh.line(a, b, 0.4, INK)
        horiz = abs(y1 - y0) < abs(x1 - x0)
        for p in (a, b):
            if horiz: sh.line((p[0], p[1] - 3), (p[0], p[1] + 3), 0.4)
            else: sh.line((p[0] - 3, p[1]), (p[0] + 3, p[1]), 0.4)
            sh.line((p[0] - 1.8, p[1] + 1.8), (p[0] + 1.8, p[1] - 1.8), 0.6)
        mx, my = a[0] + (b[0] - a[0]) * at, a[1] + (b[1] - a[1]) * at
        if horiz: tx, ty, al = mx, (my - 3 if side > 0 else my + 8), 'c'
        else: tx, ty, al = (mx + 5 if side > 0 else mx - 5), my + 2, ('l' if side > 0 else 'r')
        mask(tx, ty, label, 6.0, al); sh.text(tx, ty, label, 6.0, INK, align=al)
    dim(RW - BD + 3, B0, RW - BD + 3, B1, '7\'-0"', 1, at=0.82)
    dim(20, 0, 20, RD, E.ftin(RD), 1)
    a_, b_ = D(39, CX + 51), D(39, CX + 57); wq = FREG.text_length('FLOOR OUTLET,', fontsize=5.0)
    sh.rect((a_[0] - 4.0, min(a_[1], b_[1]) - 7.0, a_[0] + wq + 4.0, max(a_[1], b_[1]) + 3.5), width=0, fill=WHITE)   # one ground under both lines
    rect(30, CX + 49, 36, CX + 55, 0.6); text(39, CX + 51, 'FLOOR OUTLET,', 5.0, MID, align='l'); text(39, CX + 57, 'POWER, DATA', 5.0, MID, align='l')
    for n, sheet, d, x, y in ((1, 'ID-752', 'E', RW - 60, CX + 30), (2, 'ID-752', 'W', 46, CX + 30), (3, 'ID-753', 'N', RW / 2 - 20, 40), (4, 'ID-754', 'S', RW / 2 - 20, RD - 24)):
        cx, cy = D(x, y); sh.p.draw_circle(fitz.Point(cx, cy), 30.0, color=None, fill=WHITE, width=0); marker(sh, cx, cy, n, sheet, d)   # white ground: FOR's dashed open-to-above line stops at the marker
    cx, cy = D(RW - 60, CX - 34); sh.p.draw_circle(fitz.Point(cx, cy), 30.0, color=None, fill=WHITE, width=0); marker(sh, cx, cy, 5, 'ID-755', 'E')
    line(RW - BD - HEARTH_D - 3, CX, RW + 6, CX, 0.8, INK, '[6 2 1 2] 0'); cx, cy = D(RW - BD - HEARTH_D - 14, CX); marker(sh, cx, cy, 6, 'ID-755', 'N')   # clear of the hearth
    sh.text(t1.x0, t1.y1 + 22, 'FLOOR 1 KEY PLAN, %s TO 1\'-0"' % SC_LBL, 9.0, INK, raw=True)       # caption under the plan, scale bar under it
    scale_bar_n(sh, t1.x0, t1.y1 + 58, PPF, '%s TO 1\'-0"' % SC_LBL)
    # floor 2: the gallery, the steel guard (FOR: glass), the stair top, the den open to the hall
    t2, P2 = place_base(sh, 1, c2, k2, t1.x1 + GAP, ay0)
    assert KC.apply(sh.p, t2, c2, k2, LR2), 'key plan clip, floor 2'
    def F2(xf, yf): return P2(*T2(xf, yf))
    for (xa, ya), (xb, yb) in (((R1_GLASS_W, R1_N), (R1_GLASS_W, R1_GLASS_S)), ((R1_GLASS_W, R1_GLASS_S), (R1_E, R1_GLASS_S))):
        sh.line(F2(xa, ya), F2(xb, yb), 2.0, INK)
    g_ = F2(R1_GLASS_W, 694); a = F2(R1_GLASS_W + 26, 700)
    _w = FREG.text_length('STEEL PICKET GUARD 3\'-6"', fontsize=5.5); sh.rect((a[0] - 3, a[1] - 7.5, a[0] + _w + 3, a[1] + 3), width=0, fill=WHITE)
    sh.line(g_, (a[0] - 3.0, a[1] - 2.5), 0.35, INK); sh.p.draw_circle(fitz.Point(*g_), 1.0, color=INK, fill=INK, width=0)
    sh.text(a[0], a[1], 'STEEL PICKET GUARD 3\'-6"', 5.5, INK, align='l')
    a = F2(905, 568); sh.text(a[0], a[1], 'CLERESTORY, 3 LITES OVER THE SLIDER', 5.5, INK, align='c')
    sh.text(t2.x0, t2.y1 + 22, 'FLOOR 2 KEY PLAN, OPEN TO ABOVE, %s TO 1\'-0"' % SC_LBL, 9.0, INK, raw=True)
    sh.text(t2.x0, t2.y1 + 36, 'NO MARKERS ON FLOOR 2: THE GALLERY SHOWS IN THE FULL-HEIGHT VIEWS 2 (ID-752) AND 4 (ID-754).', 7.0, INK)
    scale_bar_n(sh, t2.x0, t2.y1 + 70, PPF, '%s TO 1\'-0"' % SC_LBL)
    return t1, t2

# ================================================================== layout
def _fits(cell, spec, k, top, margin_b=58):
    try: E.fit_origin(cell, spec, k, top=top, margin_b=margin_b); return True
    except AssertionError: return False

def draw_views(sh, cells, views, scale='auto', side=0.0, inset=None):
    """scale='auto' (11.07.26): the largest standard scale at which every view of the sheet fits its cell, one scale per sheet.
    side > 0: the notes take a column that wide at the right of the cell and the view is centered in the rest (single-view sheets)."""
    def plan(cell, view, k):
        n, title, L, H_, fn = view
        spec = {'room': 'LIVING ROOM', 'view': title, 'length': L, 'ceiling': H_}
        probe = E.ElevationView(Sheet(fitz.open()).p, sh.font, sh.fontname, (0, 0), k, spec)
        text = fn(probe) or ''
        if side:                                                    # the view and its notes column centered together as one group
            lines_ = wrap(text, SIDE_NOTE, side); top = 40
            wv = L * k + 46 + 60; gx0 = cell[0] + max(8.0, (cell[2] - cell[0] - wv - 40 - side) / 2)
            vcell = (gx0, cell[1], min(gx0 + wv, cell[2] - side - 40), cell[3])
        else:
            lines_ = wrap(text, NOTE, min(cell[2] - cell[0] - 16, 660)); top = 26 + len(lines_) * NOTE_LH + 14; vcell = cell
        return spec, lines_, top, vcell
    if scale == 'auto':
        for scale in ('1', '3/4', '1/2', '3/8', '1/4'):
            k = E.SCALES[scale]
            if all(_fits(plan(c, vw, k)[3], plan(c, vw, k)[0], k, plan(c, vw, k)[2]) for c, vw in zip(cells, views)): break
    k = E.SCALES[scale]
    for cell, view in zip(cells, views):
        n, title, L, H_, fn = view
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" TO 1\'-0"' % scale)
        spec, lines_, top, vcell = plan(cell, view, k)
        origin = E.fit_origin(vcell, spec, k, top=top, margin_b=58)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        fn(v)
        v.text(v.X(0) - 8, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 26
        if side:
            nx = vcell[2] + 40; ny = v.Y(H_) + 8
            for ln in lines_: sh.text(nx, ny, ln, SIDE_NOTE, INK, align='l', raw=True); ny += SIDE_NOTE * 1.45
            if inset:
                yb = inset(sh, nx, ny + 30, origin[1] + 52)            # down to the view's overall dimension line
                assert yb < cell[3] - 24, ('key plan inset runs off the sheet', yb)
        else:
            for ln in lines_: sh.text(cell[2] - 8, ny, ln, NOTE, MID, align='r'); ny += NOTE_LH
    return scale

SIDE_NOTE = 9.5                              # the notes beside a single view, read at 9.5 pt full size (owner: notes legible)
FRAME = (FR.x0 + 6, FR.y0 + 24, TB_X - 10, FR.y1 - 6)          # 24 pt clear of the top frame (no header strip)

def build_study():
    doc = fitz.open()
    sh = Sheet(doc); sh.frame('LIVING ROOM DESIGN STUDY - THE FIREPLACE WALL', 'SCALE: 1/4" TO 1\'-0"', ['DESIGN STUDY', 'LIVING ROOM FIREPLACE WALL'], 'ID-751 S1',
                              revisions=(('0', ISSUE, 'ISSUED FOR REVIEW'),), legend_rule=False)
    cells = E.layout_cells(FRAME, 2, 2)
    notes = {'A': 'OPTION A - THE LIBRARY: TV AT THE MANTEL, ART ABOVE THE BELT, LIT OPEN SHELVES IN THE FLANKS TO THE BELT COURSE (FOUR 1-1/2" SHELVES WITH A STEEL FLAT IN THE FRONT EDGE, SPANNING 4\'-4", '
                  'OVER THE BASE CABINETS), PANELING ABOVE. THE FULLEST WALL: THE SHELVES HOLD ABOUT 35 FEET OF OBJECTS THAT HAVE TO BE STYLED AND KEPT, LIT FROM THE SHELVES.',
             'B': 'OPTION B (RECOMMENDED) - TV AT THE MANTEL, ONE ARTWORK ABOVE THE BELT COURSE, PAINTED PANELING IN THE FLANKS OVER CLOSED BASE CABINETS. THE BELT '
                  'COURSE SEPARATES THE TWO STORIES, SO THE TV AND THE ART READ AS TWO COMPOSITIONS, NOT A STACK. THE TV IN ART MODE AND THE ART ABOVE ARE TWO PICTURES '
                  'ON ONE AXIS, 6\'-10-1/4" APART WITH THE BELT COURSE AND THE GALLERY CAP BETWEEN THEM.',
             'C': 'OPTION C - THE SLAB BREAST: THE BREAST CLAD IN WS-01 MARBLE TO THE CROWN (FOUR SLABS BOOK-MATCHED IN PAIRS, SEAMS ON THE CENTERLINE AND AT 10\'-0", THE LOWER SLABS 10 FT LONG), '
                  'THE TV IN THE STONE, A SLIM MITERED FRAME AT THE FIREBOX AND A 2" LEDGE IN PLACE OF THE MANTEL, NO ART. THE STONE IS THE ART: THE QUIETEST WALL, '
                  'ABOUT 150 SF OF SLAB, THE BIGGEST STONE ORDER.'}
    views = [(1, 'OPTION A - TV, ART ABOVE, OPEN SHELVES', RD, H, lambda v: (east_wall(v, 'A', True), notes['A'])[1]),
             (2, 'OPTION B - TV, ART ABOVE, PANELED FLANKS (RECOMMENDED)', RD, H, lambda v: (east_wall(v, 'B', True), notes['B'])[1]),
             (3, 'OPTION C - TV IN A MARBLE BREAST, NO ART', RD, H, lambda v: (east_wall(v, 'C', True), notes['C'])[1])]
    draw_views(sh, cells[:3], views, scale='1/4')
    x0, y0, x1, y1 = cells[3]
    E.title_bar(sh.p, sh.font, sh.fontname, cells[3], 4, 'WHAT THE PICK DECIDES', 'THE OWNER: SIMPLE AND ELEGANT')
    para_block(sh, x0 + 8, y0 + 30, [
        'THE SAME ON ALL THREE: THE BREAST 7\'-0" WIDE AND 2\'-0" DEEP FLOOR TO CEILING ON THE ROOM\'S CENTERLINE (FOR DRAWS 6\'-0" x 1\'-6"), A LISTED DIRECT-VENT GAS '
        'FIREPLACE WITH A 42" TRADITIONAL OPENING AND A FLUSH ST-01 HEARTH, THE 75" ART-MODE TV (THE FRAME OR EQUAL) IN A NICHE WITH ITS CENTER AT 6\'-2-7/8" (12.7 '
        'DEGREES FROM THE SOFA AT THE GALLERY LINE, UNDER THE 15 DEGREE LIMIT), BUILT-INS 14" DEEP EACH SIDE (FOR\'S DEPTH: THE SLIDER ON THE NORTH WALL IS CENTERED '
        'TO THEIR FACE) WITH 30" CLOSED BASE CABINETS, THE BELT COURSE (10\'-0" TO 10\'-8"), THE GALLERY CAP AT 12\'-10" AND THE 12" CROWN AT 22\'-10" (FLOOR 2 AND CEILING FROM YL, VERIFY).', '',
        (True, 'THE OWNER\'S QUESTION, ART ABOVE THE TV OR NOT: IN A 22\'-10" ROOM THE BREAST ABOVE THE TV NICHE IS 13\'-10" OF PLASTER UNDER THE CROWN. WITHOUT ART (C) IT NEEDS A MATERIAL TO '
               'CARRY IT. WITH ART (A, B) THE ART SITS IN THE UPPER STORY AT THE GALLERY\'S EYE LEVEL, SEEN FROM THE ROOM AND FROM THE HALL ABOVE, AND THE BELT COURSE '
               'KEEPS IT FROM STACKING ON THE TV. WHAT MAKES THIS WALL BUSY IS OPEN SHELVING (A), NOT THE ART.'), '',
        (True, 'RECOMMENDED: B. ONE AXIS, FOUR THINGS ON IT (FIRE, MANTEL, TV, ART), EVERYTHING ELSE PAINTED PANELING IN ONE COLOR. IF THE ART READS BUSY ONCE IT IS '
               'HUNG, IT COMES DOWN AND THE WALL IS C WITHOUT THE STONE.'), '',
        (True, 'THE PICK SETTLES: (1) FLANKS: PANELING (B, C) OR OPEN SHELVES (A), (2) THE BREAST: PLASTER (A, B) OR WS-01 SLAB (C, ABOUT 150 SF), (3) THE MANTEL: A '
               'MARBLE SURROUND WITH A 6" SHELF (A, B) OR A FRAME AND LEDGE (C), (4) ART ABOVE OR NOT. NOT AFFECTED: THE FIREPLACE UNIT, THE TV, ITS HEIGHT, THE BUILT-IN '
               'DEPTH, THE OTHER THREE ELEVATIONS (ID-752 TO ID-754 ARE DRAWN WITH B).'), '',
        (True, 'ALSO FOR THE OWNER: THE FIREPLACE UNIT AND ITS VENT ROUTE (ROOF OR EAST WALL), THE TV SIZE (85" NEEDS AN 8\'-0" BREAST), THE BREAST FINISH (VENETIAN '
               'PLASTER TO MATCH PT-02 OR PAINT), THE WS-01 SLAB, THE ART (OWNER\'S, ABOUT 4\'-8" x 5\'-10"), THE BUILT-IN COLOR AND HARDWARE.')], x1 - x0 - 16)
    fix_soft_hyphen(doc); doc.save(OUT_STUDY, garbage=3, deflate=True); print('saved', OUT_STUDY)

def build():
    doc = fitz.open()
    rev = (('0', ISSUE, 'ISSUED FOR REVIEW'),)
    # ---- ID-751 key plans and notes
    sh = Sheet(doc); sh.frame('LIVING ROOM ELEVATIONS', 'KEY PLANS, AS NOTED', ['LIVING ROOM', 'ELEVATIONS KEY PLAN'], 'ID-751', revisions=rev, legend_rule=False)
    t1, t2 = key_plans(sh)
    cw_ = (TB_X - 14 - t2.x0 - 20) / 2
    cols = [(t2.x0, t2.y1 + 118, cw_ + 60), (t2.x0 + cw_ + 80, t2.y1 + 118, cw_ - 60)]          # under floor 2's scale bar, 30 pt clear
    FUR = q(LAND_NE + R_RISER + 5.0 * R_RISER / 11.0 - STRUCT); FUR_X = q(44.0 + (SOFFIT + STRUCT - LAND_NE - R_RISER) * 11.0 / R_RISER)   # as on ID-754
    paras = [
        [(True, 'CHANGES FROM FOR\'S PLAN'),
         '1. FIREPLACE BREAST 7\'-0" x 2\'-0", FLOOR TO CEILING, CENTERED, ONE PLANE (OWNER PICK, OPTION 7).',
         '2. FLUSH ST-01 HEARTH 5\'-6" x 1\'-8" IN THE FLOOR.',
         '3. GALLERY GUARD PAINTED STEEL PICKETS, 3\'-6" ABOVE FLOOR 2.',
         '4. FASCIA AND GUARD CARRIED LEVEL ACROSS THE STAIR TOP.',
         '5. TOP FLIGHT UNDERSIDE FURRED DOWN TO %s FOR %s WEST OF CLOSET 27.' % (E.ftin(FUR), E.ftin(FUR_X - 49.0)),
         '6. CEILING OVER THE SOUTHEAST LANDING %s MIN. (6\'-8" HEADROOM).' % E.ftin(q(LAND_SE + 80.0)),
         '7. 5" WALL AT THE LOWER FLIGHT A HALF WALL, CAP 3\'-6" ABOVE THE NOSINGS.'],
        [(True, 'LEGEND'),
         'BI  BUILT-IN, 14" DEEP, 30" CLOSED BASE CABINETS WITH WS-01 TOPS, OPEN SHELVES TO %s, EACH SIDE OF THE FIREPLACE BREAST.' % E.ftin(CL_HEAD), '',
         (True, 'COORDINATED WITH FOR REV 1 (11.09.26)'),
         'CEILINGS: LIVING 22\'-8" WITH A 22\'-4" BAND AT THE WINDOW WALL; WEST END 10\'-8"; SOUTH END SLOPED 9\'-0" TO 10\'-8"; FLOOR 2 HALL 9\'-6".',
         'SLIDER D03 11\'-0" x 9\'-9", CLERESTORY G 10\'-4" TO 20\'-10". STAIR 21 RISERS AT 7-5/16".',
         'CM-02 CROWN HELD 4" BELOW THE CEILING, LED COVE ON ITS TOP (FOR L14), SEE 4/ID-502.']]
    for (cx, cy, cw), pp in zip(cols, paras):
        yend = para_block(sh, cx, cy, pp, cw, lh=NOTE_LH)
        assert yend < FR.y1 - 8, ('key plan notes run off the sheet', yend)
    _hdr = 'REDRAWN ON FOR REV 1 (REVISION 2): THE WEST END AND THE SOUTH END OF THE LIVING ROOM, THE STAIR, THE DEN OPEN TO THE HALL. REVISION 3: THE GALLERY GUARD IN PAINTED STEEL, REV 1 CHECK.'
    # ---- ID-752 east and west (11.07.26: views at the largest scale the sheet takes)
    def sheet_views(no, titles, cells, views, side=0.0, inset=None):
        probe = fitz.open(); ps_ = Sheet(probe)
        sc = draw_views(ps_, cells, views, side=side)                  # dry run picks the scale, so the title block states it
        sh = Sheet(doc); sh.frame('LIVING ROOM ELEVATIONS', 'SCALE: %s" TO 1\'-0"' % sc, titles, no, revisions=rev, legend_rule=False)
        draw_views(sh, cells, views, scale=sc, side=side, inset=inset)
    sheet_views('ID-752', ['INTERIOR ELEVATIONS', 'LIVING ROOM'], E.layout_cells(FRAME, 2, 1),
                [(1, 'EAST ELEVATION - FIREPLACE WALL', RD, H, east_wall_pick), (2, 'WEST ELEVATION - THE GALLERY', RD, H, west_wall)])
    # ---- ID-753 north, ID-754 south: one tall view each, notes in a column at the right
    sheet_views('ID-753', ['INTERIOR ELEVATIONS', 'LIVING ROOM'], [FRAME], [(3, 'NORTH ELEVATION - THE WINDOW WALL', NL, H, north_wall)], side=520.0,
                inset=lambda sh_, x, y, w: wall_inset(sh_, x, y, w, 'N'))
    sheet_views('ID-754', ['INTERIOR ELEVATIONS', 'LIVING ROOM'], [FRAME], [(4, 'SOUTH ELEVATION - THE STAIR SIDE AND THE GALLERY', NL, H, south_wall)], side=520.0,
                inset=lambda sh_, x, y, w: wall_inset(sh_, x, y, w, 'S'))
    # ---- ID-755 the fireplace stack
    sheet_views('ID-755', ['LIVING ROOM', 'FIREPLACE AND TV'], E.layout_cells(FRAME, 2, 1),
                [(5, 'FIREPLACE STACK - ENLARGED ELEVATION', BW + 12.0, BELT1, stack_elev), (6, 'SECTION THROUGH THE BREAST', 30.0 + BD + 10.5, BELT1, stack_section)])
    fix_soft_hyphen(doc); doc.set_metadata({'title': 'Casa Grove living room ID-751 to ID-755, FOR REV 1', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    import shutil, os
    prev = OUT.replace('.pdf', '.prev.pdf')
    if not os.path.exists(prev): shutil.copy2(OUT, prev)
    idd_std.PROJECT['date'] = ISSUE
    build()
