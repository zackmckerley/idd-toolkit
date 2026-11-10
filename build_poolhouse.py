"""Pool house (FOR's ANCILLARY STRUCTURE, A-204 Rev 1). Redone 11.09.26 in the guest suite's language (owner: "the pool house design is too
complex. just do these rooms like the guest bedroom"): painted walls, 8-1/2" base, 5" casing, single-panel doors, the guest bedroom's dado and
WC-01 in the office, the guest bath in the bath; bar, window seat, peg rail, lit towel shelves and office built-in removed.
Elevations at 1/2". Sheets: ID-400 key plan, ID-401 floor and wall finish plan, ID-402 storage, ID-403 office, ID-404 bath, ID-405 vestibule.
Output: 261109.HD102.PoolHouse.pdf

PLAN, measured from FOR's A-204 Rev 1 vectors (display pt of the rotated sheet, 1/4" = 1'-0", 1.5 pt per inch), checked against FOR's
dimension strings (finish to finish, A-204 general note 9). Origin here: the interior northwest corner (FOR 407.0, 388.2); x east, y south.
  shell       B2 walls 10" (8" CMU, 1-1/2" channel, 1/2" GWB; FOR 373.7 / 388.2 north, 559.7 / 574.5 south); 30'-0" x 11'-2" outside
  interior    x 0 to 340 (FOR 407.0 to 917.0), y 0 to 114.3 (FOR 388.2 to 559.7)
  storage     x 0 to 120.9 (FOR 10'-1"); window M north, x 11.3 to 107.3 (FOR 424.0 to 568.0); mini split 1 south wall x 49.7 to 77.0
  core        west wall x 120.9 to 127.4 (FOR 588.3 to 597.6), east wall x 207.1 to 213.4 (FOR 717.6 to 727.0), drawn 6-1/2"
              FOR's SHELVES: x 120.9 to 142.7, y 0 to 30.4, open to the storage room (no wall on the storage face)
              shower x 147.0 to 207.1 (FOR 627.5 to 717.6, 5'-0"), y 0 to 34.5 (FOR 440.0), center drain, valve on the east wall y 17
              vanity x 127.4 to 147.4 (20"), y 34.5 to 70.6 (36"); toilet on the east wall, CL y 52.0 (FOR 466.2)
              bath south wall y 70.6 to 76.8 (FOR 494.1 to 503.4); bath door 11 x 151.2 to 183.6 (2'-8"), hinged west, swings out
  vestibule   x 120.9 to 213.4, y 76.8 to 114.3 (3'-1-1/2" deep); door 05 x 149.3 to 185.3 (3'-0"), hinged west, swings out
              doors 11 to storage and office in the core wall lines, y 80.0 to 113.0, hinged at the south jamb, swing into each room
  office      x 213.4 to 340 (FOR 10'-6"); window M south, x 229.0 to 324.3 (FOR 750.4 to 893.4); mini split 2 on the core face y 14.8 to 51.6
Heights (A-207, A-600): storage and office CLG 8'-11" with an 8'-7" band 10" wide at the walls (FOR's cove lighting L12 at the step);
bath and vestibule CLG 8'-11"; doors 05 and 11 8'-0" leaves; window M 8'-0" x 5'-6", 2 panels, head 8'-0", sill 2'-6".
Owner decisions carried (coordination brief 11.09.26): FOR's sizes govern, divided lites (30% reduced grid), wall-hung smart toilet,
outlets CL 1'-6", no clouds. Crown: none in the pool house (8'-0" heads and a 5" casing leave 2" under the 8'-7" band); FOR's LED cove stays at the step."""
import sys, math
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG, ps
from idd_std import INK, MID, LIGHT, TRIM

OUT = '/home/claude/flrwork/261109.HD102.PoolHouse.pdf'
WHITE = (1, 1, 1); GREY = (0.55, 0.55, 0.55); POCHE = (0.35, 0.35, 0.35)
NOTE = 6.0; NLH = ps(NOTE) * 1.32

# ------------------------------------------------------------------ PLAN (inches, origin interior NW corner)
W_EXT = 10.0
IX, IY = 340.0, 114.3                    # interior
ST_E = 120.9                             # storage east face (core west face)
CW0, CW1 = 120.9, 127.4                  # core west wall
CE0, CE1 = 207.1, 213.4                  # core east wall
SH_X = (147.0, 207.1); SH_Y = (0.0, 34.5)                  # shower
NI_X = (120.9, 142.7); NI_Y = (0.0, 30.4)                  # FOR's shelves, open to the storage room
VAN_X = (127.4, 147.4); VAN_Y = (34.6, 70.6)               # bath vanity, 36" (review 11.09.26: one width)
TOI_Y = 52.0                                               # toilet CL
BS_Y = (70.6, 76.8)                                        # bath south wall
BD_X = (150.5, 178.5)                                      # bath door 11: 2'-4" INSWING hinged at the east jamb (review 11.09.26: FOR's 2'-8" outswing blocked the 3'-1" vestibule)
D05_X = (149.3, 185.3)                                     # door 05 (3'-0")
D11_Y = (80.0, 113.0)                                      # doors 11 in the core lines
MS_WIN = (11.3, 107.3); OF_WIN = (229.0, 324.3)            # windows M
MS1 = (49.7, 77.0); MS2 = (14.8, 51.6)                     # mini splits
VALVE_Y = 17.0
H_BAND = 103.0; H_CTR = 107.0                              # 8'-7" band at the walls, 8'-11" center
H_WET = 107.0                                              # bath and vestibule 8'-11"
HEAD = 96.0; CS = TRIM['casing']                           # 8'-0" heads; 5" casing as the guest bedroom (owner 11.09.26: "do these rooms like the guest bedroom")
CS_EXT = 1.25                                              # casing leg at the core doors' south jambs: the openings sit 1-1/4" off the exterior wall
CS_VN = 3.0                                                # vestibule face of the core doors, north leg: 3-1/4" to the bath wall corner
CS_BW = 2.0                                                # bath door 11, west leg: 3-1/8" to the vanity end, whose top overhangs 3/4"
BASE = TRIM['base']; CAP = TRIM['dado']                    # 8-1/2" base; dado cap top 3'-4" (guest bedroom)
SILL = 30.0                                                # window M sill 2'-6"
OUT_CL = 18.0; SW = 48.0; TV_CL = 60.0; UW_CL = 11.0       # guest bedroom: outlets CL 1'-6", switches CL 4'-0", TV-ready CL 5'-0", duplex under a window CL 11"
MS_TOP = 97.0; MS_H = 11.0                                 # mini splits: top 6" under the 8'-7" band, 11" unit, 6" clear below (confirm with the manufacturer)
SHELF_YS = (12.0, 30.0, 48.0, 66.0, 84.0)                  # FOR's shelves: five painted shelves to 7'-0" in the opening
# bath, as the guest bath (ID-262)
VAN_H = 34.0; VAN_D = VAN_X[1] - VAN_X[0]                  # furniture vanity, FOR's 20" depth, stone top 2'-11-1/4"
MIR_W = 24.0; MIR_B = 48.0; MIR_H = 48.0                   # frameless backlit LED mirror 24" x 48", 4'-0" to 8'-0" (guest bath)
GFCI_CL = 42.0; RING_CL = 52.0; PH_CL = 26.0; HOOK_CL = 66.0
TILE = (24, 12)                                            # WT-01 12 x 24, set horizontal (guest bath)
HDR = 4.0                                                  # painted header wall over the glass front
NICHE = (24.0, 12.0, 56.0)                                 # WT-01 niche 24" x 12", bottom 4'-8"
BEYOND = (0.55, 0.55, 0.55)

def r8(x): return round(x * 8) / 8

def wrap(text, size, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if FREG.text_length(t, fontsize=size) > width and cur: out.append(cur); cur = w
        else: cur = t
    return out + ([cur] if cur else [])

# ------------------------------------------------------------------ elevation view with the house's dimension handling
class View(E.ElevationView):
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
            if self.F.text_length(s_, fontsize=5.0) + 4 > seg:
                xo = (x_pt + 9 + 8 * out) if side == 'r' else (x_pt - 9 - 8 * out)
                self.text(xo, cy, s_, 5.0, align='c', rotate=90); out = 1 - out; continue
            out = 0
            self.text(x_pt - 2.5 if side == 'r' else x_pt + 7.5, cy, s_, 5.0, align='c', rotate=90)

    def dim_h(self, x0i, x1i, y_pt, pts_i, offset_lines=True):
        y_pt += 4.0
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
            if w + 3 > seg:
                cx = max(mid, last + 5 + w / 2)
                self.text(cx, y_pt - 10.5, s_, 5.0, align='c'); last = cx + w / 2
                self.line((cx, y_pt - 9.0), (mid, y_pt - 1.2), 0.3, MID); continue
            self.text(mid, y_pt - 2.5, s_, 5.0, align='c')

def H(v): return v.w['ceiling']

def tag(v, x, y, s, size=5.0, c=MID, box=False):
    if box:
        w = FREG.text_length(s, fontsize=size)
        v.rect(v.X(x) - w / 2 - 1.5, v.Y(y) - size * 0.9, v.X(x) + w / 2 + 1.5, v.Y(y) + size * 0.4, 0, color=WHITE, fill=WHITE)
    v.text(v.X(x), v.Y(y), s, size, c, align='c')

def shell(v, L, base=(), cut_left=True, cut_right=True):
    """Floor, ceiling (the 8'-7" band in the storage room and office), cut walls each end, the 8-1/2" PT-01 base (guest bedroom)."""
    h = H(v); X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(h)
    for a, b in base:
        if b - a > 0.5: C.base(v, a, b)
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    if cut_left: v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=POCHE)
    if cut_right: v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=POCHE)

def overall(v, L, xpt=None):
    """Overall floor-to-ceiling dimension, outboard of the chain string."""
    v.dim_v(0, H(v), (v.X(L) + 30) if xpt is None else xpt, [0, H(v)])

def casing2(v, x, w, csl=CS, csr=CS):
    """5" casing (guest bedroom), each leg its own width: a full leg miters into the 5" head, a narrowed leg butts it."""
    C._rect(v, x - csl, 0, x, HEAD + CS, C.OUTLINE); C._rect(v, x + w, 0, x + w + csr, HEAD + CS, C.OUTLINE)
    C._rect(v, x - csl, HEAD, x + w + csr, HEAD + CS, C.OUTLINE)
    C._line(v, (x - csl, HEAD + CS) if csl == CS else (x - csl, HEAD), (x, HEAD), C.FINE, MID)
    C._line(v, (x + w + csr, HEAD + CS) if csr == CS else (x + w + csr, HEAD), (x + w, HEAD), C.FINE, MID)
    C._rect(v, x - 0.25, 0, x + w + 0.25, HEAD + 0.25, C.FINE, MID)

def door1(v, x, w, hinge, label=None, csl=CS, csr=CS, toward=True):
    """Single-panel 8'-0" door with its casing, as the guest bedroom. The swing marks meet at the hinge side: solid when the door swings
    toward the viewer, dashed away."""
    casing2(v, x, w, csl, csr)
    st, rb, rt = 4.5, 9, 4.5
    C._rect(v, x, 0, x + w, HEAD, C.OUTLINE)
    C._rect(v, x + st, rb, x + w - st, HEAD - rt, C.MED); C._rect(v, x + st + 0.75, rb + 0.75, x + w - st - 0.75, HEAD - rt - 0.75, C.FINE, MID)
    h_, far = (x, x + w) if hinge == 'L' else (x + w, x)
    dash = None if toward else '[5 3.5] 0'
    C._line(v, (far, 0), (h_, HEAD / 2), C.FINE, MID, dash); C._line(v, (far, HEAD), (h_, HEAD / 2), C.FINE, MID, dash)
    lever = far - 3 if far > h_ else far + 3
    C._ellipse(v, lever, 38, 0.9, 0.9, C.FINE); C._line(v, (lever, 38), (lever + (-3.5 if far > h_ else 3.5), 38), C.MED)
    if label: tag(v, x + w / 2, HEAD + 2.6, label, 5.0, INK, box=True)

def ghost(v, x0, x1, y1, label=None, y0=0.0, lx=None, ly=None):
    v.rect(v.X(x0), v.Y(y0), v.X(x1), v.Y(y1), 0.4, color=MID, dashes='[3 2] 0')
    if label:
        lx = (x0 + x1) / 2 if lx is None else lx; ly = (y0 + y1) / 2 if ly is None else ly
        for i, ln in enumerate(label.split('|')): v.text(v.X(lx), v.Y(ly) - 4 + 8 * i, ln, 5.0, MID, align='c')

def window_m(v, x, w):
    """FOR's window M: 8'-0" x 5'-6" fixed, two panels on a vertical mullion, head 8'-0", sill 2'-6"; divided lites (owner rule);
    5" casing, stool and apron as the guest bedroom."""
    C.window(v, x, w, SILL, HEAD, lites=2, cs=CS)

def drapery_pocket(v, L):
    """FOR's C-1 pocket in the 8'-7" band, full width, drapery hung from it (guest bedroom: drapery pocket 4" full width, dashed).
    Drawn above the band line: the casing heads leave 2" under the band."""
    h = H(v); C._rect(v, 0, h, L, h + 4.0, C.FINE, MID, dashes='[2 1.5] 0')

def mini_split(v, x0, x1, top=MS_TOP):
    C._rect(v, x0, top - MS_H, x1, top, C.OUTLINE, fill=WHITE); C._line(v, (x0 + 1, top - 8.5), (x1 - 1, top - 8.5), C.FINE, MID)
    for i in range(1, 6): C._line(v, (x0 + (x1 - x0) * i / 6, top - 10.2), (x0 + (x1 - x0) * i / 6, top - 9.0), C.FINE, LIGHT)
    tag(v, (x0 + x1) / 2, top - 5.0, 'MINI SPLIT (FOR)', 4.5, MID)

def dado(v, L, cuts, centered=None):
    """The guest bedroom's dado wainscot: picture-frame boxes, cap top 3'-4", PT-01 satin; WC-01 above."""
    return C.panel_wall(v, 0, L, H(v), openings=cuts, centered=centered, dado=True, target=24.0, upper=False)

def outer_outlets(v, boxes):
    """Guest bedroom: duplexes CL 1'-6" centered in the first and last dado boxes."""
    if not boxes: return []
    xs = sorted({(boxes[0][0] + boxes[0][1]) / 2, (boxes[-1][0] + boxes[-1][1]) / 2})
    for x in xs: C.outlet(v, x, OUT_CL)
    return xs

def paper(v, x, y=72.0):
    tag(v, x, y, 'WC-01', 6.0, INK, box=True)

# ================================================================== ID-402 STORAGE
def shelves(v, x0, x1):
    """FOR's SHELVES, open to the storage room as FOR draws them: the opening to 8'-0" with a drywall return, five painted shelves."""
    C._rect(v, x0, 0, x1, HEAD, C.OUTLINE)
    for y in SHELF_YS: C._rect(v, x0 + 0.5, y - 1.0, x1 - 0.5, y, C.MED, fill=WHITE)
    tag(v, (x0 + x1) / 2, 90.0, 'SHELVES (FOR)', 4.5, MID)

def st_north(v):
    L = ST_E; h = H(v); w0, w1 = MS_WIN
    shell(v, L, base=[(0, L)])
    window_m(v, w0, w1 - w0)
    drapery_pocket(v, L)
    C.outlet(v, (w0 + w1) / 2, UW_CL, horizontal=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, w0, (w0 + w1) / 2, w1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, UW_CL, SILL, HEAD, h]))
    overall(v, L)
    return ['WINDOW M (FOR): 8\'-0" x 5\'-6", FIXED, TWO PANELS, DIVIDED LITES, SILL 2\'-6", HEAD 8\'-0"; 5" CASING, STOOL AND APRON AS THE GUEST BEDROOM. '
            'DUPLEX UNDER THE WINDOW CL 11". DRAPERY IN FOR\'S C-1 POCKET, FULL WIDTH (DASHED, IN THE BAND). WALLS PT-02; BASE 8-1/2", CASING AND STOOL PT-01. '
            'NO CROWN: THE CASING TOPS AT 8\'-5", 2" UNDER THE 8\'-7" BAND; FOR\'S LED COVE STAYS AT THE BAND STEP, 8\'-11" CENTER.']

def st_east(v):
    L = IY; h = H(v); s1 = NI_Y[1]; d0, d1 = D11_Y
    shell(v, L, base=[(s1, d0 - CS)])
    shelves(v, 0, s1)
    door1(v, d0, d1 - d0, 'R', '11', csl=CS, csr=CS_EXT, toward=True)
    C.switch(v, d0 - CS - 2.5, SW, 'S')
    oc = (s1 + d0 - CS) / 2; C.outlet(v, oc, OUT_CL)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, s1, oc, d0, d1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, OUT_CL, SW, 84.0, HEAD, h]))
    overall(v, L)
    return ['FOR\'S SHELVES OPEN TO THIS ROOM AS FOR DRAWS THEM: 1\'-9" DEEP, DRYWALL RETURN TO 8\'-0", FIVE PAINTED SHELVES (PT-01) TO 7\'-0". '
            'DOOR 11 2\'-8" x 8\'-0" (FOR D11), SINGLE PANEL, SWINGS IN; 5" CASING, 1-1/4" LEG AT THE SOUTH JAMB (1-1/4" TO THE EXTERIOR WALL). '
            'SWITCH AT THE LATCH CL 4\'-0". DUPLEX CL 1\'-6".']

def st_south(v):
    L = ST_E; h = H(v); dw = D11_Y[1] - D11_Y[0]
    shell(v, L, base=[(0, L)])
    ghost(v, 0, dw, HEAD, 'DOOR 11,|OPEN')
    ms = (L - MS1[1], L - MS1[0]); mini_split(v, ms[0], ms[1])
    oc = (dw + L) / 2; C.outlet(v, oc, OUT_CL)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, dw, ms[0], ms[1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, OUT_CL, MS_TOP - MS_H, MS_TOP, h]))
    overall(v, L)
    return ['A PLAIN WALL: PT-02, BASE 8-1/2". DOOR 11 OPENS FLAT AGAINST IT (DASHED). FOR\'S MINI SPLIT 1, 6" CLEAR ABOVE AND BELOW (CONFIRM WITH THE MANUFACTURER). '
            'DUPLEX CL 1\'-6" CENTERED ON THE WALL PAST THE DOOR.']

def st_west(v):
    L = IY; h = H(v)
    shell(v, L, base=[(0, L)])
    C.outlet(v, L / 2, OUT_CL)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, L / 2, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, OUT_CL, h]))
    overall(v, L)
    return ['A PLAIN WALL: PT-02, BASE 8-1/2", DUPLEX CL 1\'-6" CENTERED.']

# ================================================================== ID-403 OFFICE
OF_L = IX - CE1                                          # 126.6
def of_north(v):
    L = OF_L; h = H(v)
    shell(v, L, base=[(0, L)])
    boxes = dado(v, L, [])
    xs = outer_outlets(v, boxes)
    paper(v, L / 2)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0] + xs + [L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, h]))
    overall(v, L)
    return ['DADO WAINSCOT AS THE GUEST BEDROOM, CAP AT 3\'-4", PT-01 SATIN; WC-01 ABOVE TO THE 8\'-7" BAND. DUPLEXES CL 1\'-6" CENTERED IN THE END BOXES. '
            'FURNITURE BY OWNER (FOR\'S DESK AND CHAIRS, FREESTANDING).']

def of_east(v):
    L = IY; h = H(v); c = L / 2
    shell(v, L, base=[(0, L)])
    boxes = dado(v, L, [], centered=c)
    xs = outer_outlets(v, boxes)
    C.outlet(v, c - 6, TV_CL); C.data_jack(v, c + 6, TV_CL)
    C._rect(v, c - 24, TV_CL - 12, c + 24, TV_CL + 12, C.FINE, MID, dashes='[3 2] 0')
    tag(v, c, TV_CL + 15, 'TV-READY, BLOCKING (DASHED)')
    paper(v, c, 84.0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, xs[0], c, xs[-1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, TV_CL, h]))
    overall(v, L)
    return ['TV WALL AS THE GUEST BEDROOM: TV-READY POWER AND DATA (2 CAT6, 1 COAX) CL 5\'-0", CENTERED, 2x10 BLOCKING; TV BY OWNER. '
            'DADO CAP AT 3\'-4", WC-01 ABOVE. DUPLEXES CL 1\'-6" IN THE END BOXES.']

def of_south(v):
    L = OF_L; h = H(v)
    w0, w1 = IX - OF_WIN[1], IX - OF_WIN[0]               # 15.7, 111.0 from the east wall
    shell(v, L, base=[(0, L)])
    window_m(v, w0, w1 - w0)
    drapery_pocket(v, L)
    C.outlet(v, (w0 + w1) / 2, UW_CL, horizontal=True)
    C.switch(v, L - 4.0, SW, 'D')                                           # at the latch of door 11 (hinged north), 4" off the core corner
    paper(v, w0 + (w1 - w0) * 0.25, 18.0)                                   # under the window, clear of the casing and the outlet (review 11.09.26)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, w0, (w0 + w1) / 2, w1, L - 4.0, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, UW_CL, SILL, SW, HEAD, h]))
    overall(v, L)
    return ['WINDOW WALL AS THE GUEST BEDROOM: NO DADO, WC-01 FULL HEIGHT. WINDOW M (FOR): 8\'-0" x 5\'-6", FIXED, TWO PANELS, DIVIDED LITES, SILL 2\'-6", HEAD 8\'-0", '
            '5" CASING, STOOL AND APRON. DUPLEX UNDER THE WINDOW CL 11". DRAPERY IN FOR\'S C-1 POCKET, FULL WIDTH (DASHED). DIMMER D (FOR\'S CHANDELIER AND L12 COVE) CL 4\'-0", '
            '4" OFF THE CORE CORNER, AT THE LATCH OF DOOR 11.']

def of_west(v):
    L = IY; h = H(v)
    d0, d1 = L - D11_Y[1], L - D11_Y[0]                   # 1.3, 34.3
    m0, m1 = L - MS2[1], L - MS2[0]                       # 62.7, 99.5
    shell(v, L, base=[(d1 + CS, L)])
    door1(v, d0, d1 - d0, 'R', '11', csl=CS_EXT, csr=CS, toward=True)
    boxes = dado(v, L, [(0, d1 + CS)])
    xs = outer_outlets(v, boxes)
    mini_split(v, m0, m1)
    paper(v, (d1 + CS + L) / 2, 72.0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d0, d1, m0, m1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, OUT_CL, CAP, MS_TOP - MS_H, MS_TOP, h]))
    overall(v, L)
    return ['DOOR 11 2\'-8" x 8\'-0" (FOR D11), SINGLE PANEL, SWINGS IN, HINGED AT THE NORTH JAMB (CLEAR OF WINDOW M); 1-1/4" CASING LEG AT THE SOUTH JAMB. '
            'THE DIMMER IS AT THE LATCH, ON THE SOUTH WALL (VIEW 3). DADO AND WC-01. FOR\'S MINI SPLIT 2, 6" CLEAR ABOVE AND BELOW (CONFIRM WITH THE MANUFACTURER).']

# ================================================================== ID-404 BATH (as the guest bath, ID-262)
BW = CE0 - CW1                                           # 79.7
BD = BS_Y[0]                                             # 70.6
FLUSH_CL = 44.0; SEAT_GFCI = 14.0; SEAT_OFF = 8.0
PH_X = 15.0                                              # paper holder on the bath south wall, 1'-3" off the east wall (south view, x from the east)
def wall_toilet(v, cx, w=14.5):
    """Wall-hung smart toilet on an in-wall carrier (owner 11.09.26), front view: bowl off the floor, flush plate CL 3'-8", seat GFCI 8" off
    the bowl CL at CL 1'-2", dashed behind the bowl (5/ID-502)."""
    C._poly(v, [(cx - w / 2, 15.5), (cx - w / 2 + 2.2, 7.0), (cx + w / 2 - 2.2, 7.0), (cx + w / 2, 15.5)], C.OUTLINE, fill=WHITE)
    C._ellipse(v, cx, 15.5, w / 2, 1.2, C.OUTLINE, fill=WHITE)
    C._rect(v, cx - w / 2, 15.5, cx + w / 2, 16.5, C.OUTLINE, fill=WHITE); C._rect(v, cx - w / 2 + 0.5, 16.5, cx + w / 2 - 0.5, 17.2, C.MED, fill=WHITE)   # seat and lid on the rim
    C._rect(v, cx - 4.5, FLUSH_CL - 3.0, cx + 4.5, FLUSH_CL + 3.0, C.OUTLINE, fill=WHITE); C._rect(v, cx - 1.6, FLUSH_CL - 1.6, cx + 1.6, FLUSH_CL + 1.6, C.FINE)
    gx = cx + SEAT_OFF
    C._rect(v, gx - 1.4, SEAT_GFCI - 2.25, gx + 1.4, SEAT_GFCI + 2.25, C.FINE, MID, dashes='[1.5 1.0] 0')

def wall_toilet_profile(v, x, facing='L'):
    """Wall-hung bowl seen from the side: 21" projection, rim 16-1/2", off the floor."""
    s = -1 if facing == 'L' else 1
    pts = [(x, 9.0), (x + s * 16.0, 9.0), (x + s * 21.0, 14.0), (x + s * 21.0, 16.5), (x, 16.5)]
    C._poly(v, pts, C.OUTLINE, fill=WHITE); C._rect(v, min(x, x + s * 20.0), 16.5, max(x, x + s * 20.0), 17.4, C.MED, fill=WHITE)   # seat on the rim

def tile(v, x0, x1, y0=0.0, y1=None):
    y1 = H_WET if y1 is None else y1
    C.tile_grid(v, x0, x1, y0, y1, TILE, show=[(x0, x1, y0, y1)])

def beyond(fn):
    keep = (C.INK, C.MID); C.INK = BEYOND; C.MID = BEYOND
    try: fn()
    finally: C.INK, C.MID = keep

def header_cut(v, x):
    """The painted header wall over the glass front, cut (guest bath)."""
    v.rect(v.X(x - HDR / 2), v.Y(HEAD), v.X(x + HDR / 2), v.Y(H(v)), 0.6, fill=POCHE)

def mtag(v, x, y, s, size=4.5, c=MID):
    """A label on tile or glass: a white box behind it so no joint runs through the letters."""
    tag(v, x, y, s, size, c, box=True)

def glass_front(v, x, w, h=96.0, door_w=24.0, door_at='L'):
    """Frameless glass front at the shower: the 24" door at one end, hinged off the fixed panel (a wall hinge at the vanity end would
    swing the door into the vanity), the fixed panel with a 24" towel bar (guest bath); swing marks solid (toward the viewer)."""
    dx = x if door_at == 'L' else x + w - door_w
    fx0, fx1 = (x + door_w, x + w) if door_at == 'L' else (x, x + w - door_w)
    C._rect(v, x, 0, x + w, h, C.OUTLINE); C._line(v, (x, h), (x + w, h), C.MED)
    C._rect(v, fx0 + 0.4, 0.6, fx1 - 0.6, h - 0.6, C.FINE, LIGHT)
    C._rect(v, dx, 0.5, dx + door_w, h - 1.0, C.OUTLINE); C._rect(v, dx + 0.6, 1.1, dx + door_w - 0.6, h - 1.6, C.FINE, LIGHT)
    hx, lx = (dx + door_w, dx) if door_at == 'L' else (dx, dx + door_w)
    for y in (0.5, h - 1.0): C._line(v, (lx, y), (hx, h / 2), C.FINE, MID)
    for hy in (12, h - 12): C._rect(v, hx - 1.2, hy - 1.5, hx + 1.2, hy + 1.5, C.MED, fill=WHITE)
    px = lx + 2.2 if door_at == 'L' else lx - 3.4
    C._rect(v, px, 36, px + 1.2, 48, C.OUTLINE)
    C.towel_bar(v, (fx0 + fx1) / 2, 48, 24)
    for i in range(2): C._line(v, (fx1 - 14 + i * 2.5, h - 6), (fx1 - 14 + i * 2.5 + 8, h - 16), C.FINE, C.PALE)

def ba_north(v):
    L = BW; h = H(v)
    sx = SH_X[0] - CW1                                   # 19.6: the shower front's west end
    shell(v, L)
    beyond(lambda: (tile(v, sx, L), C.shower_head(v, L - 4, 80)))
    v.rect(v.X(sx), v.Y(HEAD), v.X(L), v.Y(h), 0, color=WHITE, fill=WHITE)      # the painted header in the glass plane, in front of the tile
    v.line((v.X(sx), v.Y(h)), (v.X(L), v.Y(h)), 0.9)
    glass_front(v, sx, L - sx, HEAD, 24.0, 'L')
    C.vanity_end(v, 0, VAN_D, VAN_H, open_to='R')
    tag(v, (sx + L) / 2, 100.5, 'PAINTED HEADER')
    mtag(v, sx + 12, 62, 'GLASS DOOR')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, VAN_D, sx + 24.0, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, VAN_H, 48, HEAD, h]))
    overall(v, L)
    return ['SHOWER FRONT AS THE GUEST BATH: 1/2" TEMPERED GLASS, 24" DOOR AT THE VANITY END (22" CLEAR), HINGED OFF THE FIXED PANEL SO IT SWINGS CLEAR OF THE VANITY; '
            'FIXED PANEL WITH A 24" TOWEL BAR CL 4\'-0". PAINTED HEADER OVER THE GLASS. BEYOND: WT-01 TO THE CEILING, HEAD ON THE EAST WALL.']

def ba_east(v):
    L = BD; h = H(v); g = SH_Y[1]
    shell(v, L, base=[(g + HDR / 2, L)])
    tile(v, 0, g); C.schluter(v, g, 0, h)
    header_cut(v, g)
    C.valve(v, VALVE_Y, 48); C.shower_head(v, VALVE_Y, 80)
    nw, nh, nb = NICHE; C.niche(v, VALVE_Y - nw / 2, nw, nb, nh)
    C.glass_edge(v, g, HEAD)
    wall_toilet(v, TOI_Y)
    mtag(v, VALVE_Y, 100.5, 'WT-01')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, VALVE_Y, g, TOI_Y, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, SEAT_GFCI, FLUSH_CL, 48, nb, nb + nh, 80, HEAD, h]))
    overall(v, L)
    return ['WT-01 12 x 24 SET HORIZONTAL, FLOOR TO CEILING, SCHLUTER EDGE. VALVE CL 4\'-0" ON FOR\'S LOCATION, HEAD CL 6\'-8", NICHE 24" x 12" OVER THE VALVE. '
            'WALL-HUNG SMART TOILET ON A CARRIER IN THE CORE WALL (CONFIRM DEPTH), FLUSH PLATE CL 3\'-8", SEAT GFCI 8" OFF THE BOWL CL, CL 1\'-2" (DASHED), SEE 5/ID-502. '
            'PAPER HOLDER ON THE SOUTH WALL (VIEW 3). WALLS PT-02.']

def ba_south(v):
    L = BW; h = H(v)
    d0, d1 = CE0 - BD_X[1], CE0 - BD_X[0]                 # 28.6, 56.6 from the east wall
    vx = L - VAN_D                                        # vanity end, 59.7
    shell(v, L, base=[(0, d0 - CS)])
    wall_toilet_profile(v, 0, facing='R')
    C.vanity_end(v, L, VAN_D, VAN_H, open_to='L')
    door1(v, d0, d1 - d0, 'L', '11', csl=CS, csr=CS_BW, toward=True)
    C.robe_hook(v, (d0 + d1) / 2, HOOK_CL)
    C.switch(v, d1 + CS_BW + 2.5, SW, 'S2')
    C.paper_holder(v, PH_X, PH_CL)
    C.towel_ring(v, vx + VAN_D / 2 + 1.5, RING_CL)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, PH_X, d0, d1, vx, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, PH_CL, VAN_H, SW, HOOK_CL, HEAD, h]))
    overall(v, L)
    return ['DOOR 11 2\'-4" x 8\'-0" (FOR D11 IS 2\'-8"), SINGLE PANEL, SWINGS INTO THE BATH FROM THE EAST JAMB, CLEAR OF THE TOILET; ROBE HOOK ON THE DOOR CL 5\'-6". '
            '5" CASING, 2" LEG AT THE VANITY. S2 (MIRROR AND FOR\'S EF) AT THE LATCH CL 4\'-0". PAPER HOLDER CL 2\'-2", 1\'-3" OFF THE EAST WALL; TOWEL RING CL 4\'-4" OVER THE VANITY END.']

def ba_west(v):
    L = BD; h = H(v)
    v1 = L - VAN_Y[0]                                     # 36.0: the glass line
    shell(v, L, base=[(0, v1)])
    beyond(lambda: tile(v, v1, L))
    header_cut(v, v1)
    C.glass_edge(v, v1, HEAD)
    C.vanity_furniture(v, 0.75, v1 - 1.5, VAN_H, legs=True, drawers=3, faucet_style='deck')   # top scribed wall to glass
    cx = v1 / 2
    C.mirror_led(v, cx - MIR_W / 2, MIR_W, MIR_B, MIR_H)
    C.outlet(v, 3.5, GFCI_CL)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, cx, v1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, VAN_H, GFCI_CL, MIR_B, MIR_B + MIR_H, h]))
    overall(v, L)
    return ['VANITY AS THE GUEST BATH: PAINTED FURNITURE VANITY ON TURNED LEGS, 36" x 20" (FOR), STONE TOP SCRIBED WALL TO GLASS, UNDERMOUNT SINK, DECK FAUCET. '
            'FRAMELESS BACKLIT LED MIRROR 24" x 48", 4\'-0" TO 8\'-0", NO SEPARATE LIGHT. GFCI CL 3\'-6" AT THE CORNER. WALL PT-02. BEYOND THE GLASS: THE SHOWER WEST WALL, WT-01.']

# ================================================================== ID-405 VESTIBULE
VW = CE1 - CW0                                           # 92.5
VD = IY - BS_Y[1]                                        # 37.5
def ve_north(v):
    L = VW; h = H(v)
    d0, d1 = BD_X[0] - CW0, BD_X[1] - CW0                 # 29.6, 57.6
    shell(v, L, base=[(CW1 - CW0, d0 - CS), (d1 + CS, CE0 - CW0)])
    for a, b in ((0, CW1 - CW0), (CE0 - CW0, L)): v.rect(v.X(a), v.Y(0), v.X(b), v.Y(h), 0.6, fill=POCHE)
    door1(v, d0, d1 - d0, 'R', '11', toward=False)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, CW1 - CW0, d0, d1, CE0 - CW0, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, HEAD, HEAD + CS, h]))
    overall(v, L)
    return ['BATH DOOR 11 2\'-4", SINGLE PANEL, SWINGS INTO THE BATH (AWAY), 5" CASING. A PLAIN ROOM: PT-02, BASE 8-1/2", TL-02 FLOOR. CORE WALL ENDS CUT EACH SIDE: DOORS 11 TO STORAGE AND OFFICE IN THEM.']

def ve_south(v):
    L = VW; h = H(v)
    d0, d1 = CE1 - D05_X[1], CE1 - D05_X[0]               # 28.1, 64.1 from the east
    shell(v, L, base=[(0, d0 - CS), (d1 + CS, L)])
    casing2(v, d0, d1 - d0)
    C.door_leaf(v, d0, d1 - d0, HEAD, panels='glass', swing='R')
    tag(v, (d0 + d1) / 2, HEAD + 2.6, '05', 5.0, INK, box=True)
    C.switch(v, d0 - CS - 2.5, SW, 'S')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d0, d1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, SW, HEAD, HEAD + CS, h]))
    overall(v, L)
    return ['DOOR 05 (FOR D05): 3\'-0" x 8\'-0" METAL, FULL LITE, IMPACT, SWINGS OUT; DIVIDED LITES (OWNER RULE, CONFIRM WITH FOR\'S NOA); 5" CASING. SWITCH AT THE LATCH, CL 4\'-0".']

def ve_side(v, which):
    L = VD; h = H(v)
    if which == 'W': d0, d1, csl, csr = IY - D11_Y[1], IY - D11_Y[0], CS_EXT, CS_VN      # looking west, left = south: hinge at the south jamb
    else: d0, d1, csl, csr = D11_Y[0] - BS_Y[1], D11_Y[1] - BS_Y[1], CS_VN, CS_EXT       # looking east, left = north: office door hinged at the north jamb
    shell(v, L)
    door1(v, d0, d1 - d0, 'L', '11', csl=csl, csr=csr, toward=False)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d0, d1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, h, v.X(L) + 14, E.snap_points([0, HEAD, HEAD + CS, h]))
    overall(v, L)
    room = 'STORAGE' if which == 'W' else 'OFFICE'
    return ['DOOR 11 TO THE %s, 2\'-8" x 8\'-0", SINGLE PANEL, SWINGS AWAY. 5" HEAD; LEGS 1-1/4" AT THE SOUTH JAMB (1-1/4" TO THE EXTERIOR WALL) AND 3" AT THE NORTH JAMB (3-1/4" TO THE BATH WALL).' % room]
def ve_west(v): return ve_side(v, 'W')
def ve_east(v): return ve_side(v, 'E')

# ================================================================== views on a sheet
def draw_views(sh, cells, views, scale):
    k = E.SCALES[scale]
    for cell, (n, title, L, fn, ceiling, room) in zip(cells, views):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" TO 1\'-0"' % scale)
        spec = {'room': room, 'view': title, 'length': L, 'ceiling': ceiling}
        probe = View(Sheet(fitz.open()).p, sh.font, sh.fontname, (0, 0), k, spec)
        text = ' '.join(fn(probe))
        width = min(cell[2] - cell[0] - 16, 720)
        lines_ = wrap(text, NOTE, width)
        top = 30 + len(lines_) * NLH + 8
        origin = E.fit_origin(cell, spec, k, top=top, margin_b=48)
        v = View(sh.p, sh.font, sh.fontname, origin, k, spec)
        fn(v)
        v.text(v.X(0) - 6, v.Y(0) - 2.5, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 30
        for ln in lines_: sh.text(cell[2] - 8, ny, ln, NOTE, MID, align='r'); ny += NLH

def cells_2x2(frame, views, scale):
    k = E.SCALES[scale]; x0, y0, x1, y1 = frame
    need = [max(views[c][2], views[c + 2][2]) * k + 46 + 60 + 30 for c in (0, 1)]
    extra = (x1 - x0 - sum(need)) / 2; w0 = need[0] + extra; ym = (y0 + y1) / 2
    return [(x0, y0, x0 + w0, ym), (x0 + w0, y0, x1, ym), (x0, ym, x0 + w0, y1), (x0 + w0, ym, x1, y1)]

# ================================================================== plans (drawn clean from the PLAN block, FOR's A-204 Rev 1 geometry)
class Plan:
    def __init__(self, sh, x0, y0, k):
        self.sh, self.x0, self.y0, self.k = sh, x0, y0, k
    def P(self, x, y): return (self.x0 + (x + W_EXT) * self.k, self.y0 + (y + W_EXT) * self.k)
    def rect(self, x0, y0, x1, y1, w=0.6, color=INK, fill=None, dashes=None):
        a, b = self.P(x0, y0), self.P(x1, y1)
        self.sh.rect((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), width=w, color=color, fill=fill, dashes=dashes)
    def line(self, a, b, w=0.6, color=INK, dashes=None): self.sh.line(self.P(*a), self.P(*b), w, color, dashes=dashes)
    def text(self, x, y, s, size, color=INK, align='c', bold=False):
        p = self.P(x, y); self.sh.text(p[0], p[1], s, size, color, align=align, bold=bold, raw=True)
    def arc(self, hx, hy, r, a0, a1, w=0.4):
        pts = [self.P(hx + r * math.cos(math.radians(a)), hy + r * math.sin(math.radians(a))) for a in range(int(a0), int(a1) + 1, 3)]
        s_ = self.sh.p.new_shape(); s_.draw_polyline([fitz.Point(*q) for q in pts]); s_.finish(color=INK, width=w, closePath=False); s_.commit()
    def door(self, hx, hy, r, a_closed, a_open, w=0.4):
        """Swing arc from the closed to the open position, leaf drawn open."""
        a0, a1 = sorted((a_closed, a_open)); self.arc(hx, hy, r, a0, a1, w)
        o = (hx + r * math.cos(math.radians(a_open)), hy + r * math.sin(math.radians(a_open)))
        self.line((hx, hy), o, 1.0)

def draw_plan(pl, fixtures=True, millwork=True):
    """Walls (poche), openings, windows, the core, fixtures and the millwork of the design."""
    # exterior walls with openings
    segs_n = [(-W_EXT, MS_WIN[0]), (MS_WIN[1], IX + W_EXT)]
    segs_s = [(-W_EXT, D05_X[0]), (D05_X[1], OF_WIN[0]), (OF_WIN[1], IX + W_EXT)]
    for a, b in segs_n: pl.rect(a, -W_EXT, b, 0, 0.8, INK, POCHE)
    for a, b in segs_s: pl.rect(a, IY, b, IY + W_EXT, 0.8, INK, POCHE)
    pl.rect(-W_EXT, 0, 0, IY, 0.8, INK, POCHE); pl.rect(IX, 0, IX + W_EXT, IY, 0.8, INK, POCHE)
    for a, b, y0, y1 in ((MS_WIN[0], MS_WIN[1], -W_EXT, 0), (OF_WIN[0], OF_WIN[1], IY, IY + W_EXT)):   # window M: frame, glass, mullion
        pl.rect(a, y0, b, y1, 0.6, INK, WHITE)
        for f in (0.35, 0.65): pl.line((a, y0 + (y1 - y0) * f), (b, y0 + (y1 - y0) * f), 0.4)
        pl.line(((a + b) / 2, y0), ((a + b) / 2, y1), 0.6)
    pl.rect(D05_X[0] - 1.0, IY, D05_X[0], IY + W_EXT, 0.6, INK, WHITE); pl.rect(D05_X[1], IY, D05_X[1] + 1.0, IY + W_EXT, 0.6, INK, WHITE)
    # core
    pl.rect(CW0, NI_Y[1], CW1, D11_Y[0], 0.7, INK, POCHE)                       # core west wall below FOR's shelves
    pl.rect(CE0, 0, CE1, D11_Y[0], 0.7, INK, POCHE)                             # core east wall
    pl.rect(NI_X[1], 0, SH_X[0], SH_Y[1], 0.7, INK, POCHE)                      # shelves / shower wall
    pl.rect(CW1, NI_Y[1], NI_X[1], SH_Y[1], 0.7, INK, POCHE)                    # shelves' south wall
    pl.rect(CW1, BS_Y[0], BD_X[0], BS_Y[1], 0.7, INK, POCHE); pl.rect(BD_X[1], BS_Y[0], CE0, BS_Y[1], 0.7, INK, POCHE)
    for x0_, x1_ in ((CW0, CW1), (CE0, CE1)):
        pl.rect(x0_, D11_Y[1], x1_, IY, 0.7, INK, POCHE)                          # jamb stub at the south wall
    # doors
    pl.door(D05_X[0], IY + W_EXT, D05_X[1] - D05_X[0], 0, 90, 0.5)                  # 05: hinged west, swings out (south)
    pl.door(CW0, D11_Y[1], D11_Y[1] - D11_Y[0], 270, 180)                       # 11 storage: hinged at the south jamb, swings west
    pl.door(CE1, D11_Y[0], D11_Y[1] - D11_Y[0], 90, 0)                          # 11 office: hinged at the north jamb, swings east, clear of window M
    pl.door(BD_X[1], BS_Y[0], BD_X[1] - BD_X[0], 180, 270)                      # 11 bath: 2'-4", hinged at the east jamb, swings into the bath
    if fixtures:
        pl.rect(SH_X[0], SH_Y[1] - 0.5, SH_X[1], SH_Y[1] + 0.5, 0.6, INK, WHITE)          # glass front
        pl.door(SH_X[0] + 24.0, SH_Y[1], 24.0, 180, 90, 0.4)                               # glass door hinged off the fixed panel, swings out
        c = pl.P((SH_X[0] + SH_X[1]) / 2, SH_Y[1] / 2); s_ = pl.sh.p.new_shape(); s_.draw_circle(fitz.Point(*c), 1.6 * pl.k); s_.finish(color=INK, width=0.4); s_.commit()
        pl.rect(VAN_X[0], VAN_Y[0] + 0.5, VAN_X[1], VAN_Y[1] - 0.5, 0.6, INK, WHITE)      # furniture vanity, 36" x 20"
        cc = pl.P((VAN_X[0] + VAN_X[1]) / 2, (VAN_Y[0] + VAN_Y[1]) / 2)
        s_ = pl.sh.p.new_shape(); s_.draw_oval(fitz.Rect(cc[0] - 6 * pl.k, cc[1] - 8 * pl.k, cc[0] + 6 * pl.k, cc[1] + 8 * pl.k)); s_.finish(color=INK, width=0.4); s_.commit()
        # wall-hung toilet: carrier dashed in the core east wall, bowl 21" off it
        pl.rect(CE0 - 0.0, TOI_Y - 9, CE1, TOI_Y + 9, 0.4, MID, None, dashes='[2 1.5] 0')
        a = pl.P(CE0 - 21, TOI_Y - 7.25); b = pl.P(CE0 - 1.0, TOI_Y + 7.25)
        s_ = pl.sh.p.new_shape(); s_.draw_oval(fitz.Rect(a[0], a[1], b[0], b[1])); s_.finish(color=INK, width=0.6, fill=WHITE); s_.commit()
        pl.rect(CE0 - 2.0, TOI_Y - 7.5, CE0, TOI_Y + 7.5, 0.6, INK, WHITE)
    if millwork:
        pl.rect(NI_X[0], NI_Y[0], NI_X[1], NI_Y[1], 0.4, MID, None, dashes='[2 1.5] 0')  # FOR's shelves, open to the storage room

def plan_labels(pl, size=1.0):
    for txt, x, y, s in (('STORAGE', 60.0, 58.0, 9.0), ('OFFICE', 272.0, 60.0, 9.0),
                         ('BATH', 186.0, 67.0, 7.5), ('VESTIBULE', 167.0, 98.0, 6.5)):
        pl.text(x, y, txt, s * size)
    for txt, x, y in (('SHELVES', NI_X[0] + 11, 16.0), ('SHOWER', 164.0, 10.0)):
        pl.text(x, y, txt, 6.0, MID)

def door_tag(pl, n, x, y):
    q = pl.P(x, y); s_ = pl.sh.p.new_shape(); s_.draw_oval(fitz.Rect(q[0] - 12, q[1] - 8, q[0] + 12, q[1] + 8)); s_.finish(color=INK, width=0.5, fill=WHITE); s_.commit()
    pl.sh.text(q[0], q[1] + 3.2, n, 8.5, INK, align='c', raw=True)

def win_tag(pl, n, x, y):
    q = pl.P(x, y); s_ = pl.sh.p.new_shape()
    s_.draw_polyline([fitz.Point(q[0] - 12, q[1]), fitz.Point(q[0] - 6, q[1] - 7), fitz.Point(q[0] + 6, q[1] - 7), fitz.Point(q[0] + 12, q[1]),
                      fitz.Point(q[0] + 6, q[1] + 7), fitz.Point(q[0] - 6, q[1] + 7), fitz.Point(q[0] - 12, q[1])]); s_.finish(color=INK, width=0.5, fill=WHITE); s_.commit()
    pl.sh.text(q[0], q[1] + 3.2, n, 8.5, INK, align='c', raw=True)

def quad_marker(sh, cx, cy, sheet, views, r=22.0):
    f = r / 16.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.8, fill=WHITE); s_.commit()
    sh.text(cx, cy + 2.4 * f, sheet.replace('ID-', ''), 7.0 * f, INK, align='c', raw=True)
    for d, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d]
        a = 3.5 * f; tip = (cx + dx * (r + 6 * f), cy + dy * (r + 6 * f))
        b1 = (cx + dx * r - dy * a, cy + dy * r + dx * a); b2 = (cx + dx * r + dy * a, cy + dy * r - dx * a)
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
        off = 0.74 * r if dx else 0.62 * r
        sh.text(cx + dx * off, cy + dy * off + 2.4 * f, str(n), 7.0 * f, INK, align='c', raw=True)

def scale_bar(sh, x, y, k):
    ft = 12 * k
    for i in range(10): sh.rect((x + i * ft, y - 5, x + (i + 1) * ft, y), 0.4, INK, INK if i % 2 == 0 else WHITE)
    for i in (0, 5, 10): sh.text(x + i * ft, y + 13, "%d'" % i, 9.0, MID, align='c', raw=True)
    sh.text(x + 10 * ft + 12, y + 0.5, '1/2" TO 1\'-0"', 9.5, MID, raw=True)

def north(sh, nx, ny):
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(nx, ny - 18), fitz.Point(nx + 8, ny + 8), fitz.Point(nx, ny + 2), fitz.Point(nx - 8, ny + 8), fitz.Point(nx, ny - 18)]); s_.finish(color=INK, fill=INK, width=0.4); s_.commit()
    sh.text(nx, ny + 24, 'N', 10.0, INK, align='c', raw=True)

def para_block(sh, x, y, items, width, size=NOTE):
    lh = ps(size) * 1.32
    for it in items:
        head = isinstance(it, tuple); text = it[1] if head else it
        if text == '': y += lh / 2; continue
        for ln in wrap(text, size, width): sh.text(x, y, ln, size, INK if head else MID, bold=head); y += lh
    return y

K_PLAN = 3.0                                             # 1/2" = 1'-0", 3 pt per inch
def plan_origin():
    w = (IX + 2 * W_EXT) * K_PLAN; x0 = FR.x0 + 14 + (TB_X - 14 - FR.x0 - 14 - w) / 2
    return x0, HDR_Y + 70

def key_plan_sheet(sh):
    x0, y0 = plan_origin(); pl = Plan(sh, x0, y0, K_PLAN)
    # outside, for orientation only (owner rule: only the area designed, plus its doors): the exterior shower and the pool side
    draw_plan(pl)
    plan_labels(pl)
    for n, x, y in (('05', 167.3, IY + 22.0), ('11', CW0 - 12, 96.5), ('11', CE1 + 12, 96.5), ('11', 164.5, 86.0)): door_tag(pl, n, x, y)
    for x, y in ((59.3, -W_EXT - 10), (276.6, IY + W_EXT + 10)): win_tag(pl, 'M', x, y)
    # markers
    for sheet, x, y in (('ID-402', 80.0, 77.0), ('ID-403', 292.0, 86.0)):
        q = pl.P(x, y); quad_marker(sh, q[0], q[1], sheet, {'N': 1, 'E': 2, 'S': 3, 'W': 4})
    q = pl.P(192.0, 21.0); quad_marker(sh, q[0], q[1], 'ID-404', {'N': 1, 'E': 2, 'S': 3, 'W': 4}, r=15.0)
    q = pl.P(197.0, 98.0); quad_marker(sh, q[0], q[1], 'ID-405', {'N': 1, 'E': 4, 'S': 2, 'W': 3}, r=16.0)
    a = pl.P(-W_EXT, -W_EXT); b = pl.P(IX + W_EXT, IY + W_EXT)
    sh.text(a[0], b[1] + 64, 'POOL HOUSE KEY PLAN', 11, serif=True, spacing=0.8, raw=True)
    sh.text(a[0], b[1] + 78, 'FOR\'S ANCILLARY STRUCTURE, A-204 REV 1. 335 SF UNDER A/C. FINISH FLOOR 0\'-0" = 11.70 NGVD.', 7.0, MID, raw=True)
    scale_bar(sh, b[0] - 12 * K_PLAN * 10 - 110, b[1] + 66, K_PLAN)
    north(sh, a[0] - 34, a[1] + 20)
    return b[1] + 128

def key_notes(sh, y0):
    x0, x1 = FR.x0 + 14, TB_X - 14; col = (x1 - x0 - 40) / 3
    c1 = [(True, 'THE DESIGN'),
          'THE POOL HOUSE IN THE GUEST SUITE\'S LANGUAGE (OWNER 11.09.26: "DO THESE ROOMS LIKE THE GUEST BEDROOM"): PAINTED WALLS, 8-1/2" BASE, 5" CASING, '
          'SINGLE-PANEL 8\'-0" DOORS, DIVIDED LITES, OUTLETS CL 1\'-6", NO SCONCES. NO CROWN: THE CASING TOPS AT 8\'-5", 2" UNDER THE 8\'-7" BAND, SO FOR\'S LED COVE '
          'AT THE BAND STEP IS THE CEILING DETAIL.',
          'STORAGE: A PLAIN ROOM. PT-02 WALLS, FOR\'S SHELVES AS FOR DRAWS THEM (FIVE PAINTED SHELVES), DRAPERY AT WINDOW M.',
          'OFFICE: AS THE GUEST BEDROOM. DADO WAINSCOT (CAP 3\'-4", PT-01) WITH WC-01 ABOVE, NO DADO ON THE WINDOW WALL, TV-READY EAST WALL, '
          'DRAPERY IN FOR\'S C-1 POCKET. FURNITURE BY OWNER.',
          'BATH: AS THE GUEST BATH. PAINTED FURNITURE VANITY, BACKLIT LED MIRROR, WT-01 IN THE SHOWER TO THE CEILING, TL-02 FLOOR WITH A MOSAIC SHOWER FLOOR, '
          'WALL-HUNG SMART TOILET, GLASS FRONT WITH A 24" DOOR, PAINTED HEADER.',
          'VESTIBULE: PLAIN. PT-02, TL-02.']
    c2 = [(True, 'CHANGES FROM FOR\'S PLAN'),
          '1. TOILET WALL-HUNG ON AN IN-WALL CARRIER (OWNER 11.09.26): THE CORE EAST WALL BECOMES A 6" STUD CHASE AT THE TOILET, SEAT GFCI. CONFIRM WITH FOR.',
          '2. BATH DOOR 11 2\'-4" (FOR 2\'-8"), SWINGS INTO THE BATH FROM THE EAST JAMB: FOR\'S OUTSWING BLOCKED THE 3\'-1" VESTIBULE. OFFICE DOOR 11 REHUNG AT THE NORTH JAMB, CLEAR OF WINDOW M.',
          '3. SHOWER GLASS FRONT, 24" DOOR HINGED OFF THE FIXED PANEL; FOR\'S VALVE AND CENTER DRAIN KEPT.',
          '4. OFFICE TV-READY POWER AND DATA ON THE EAST WALL: FOR\'S SET HAS NO DATA, LOW VOLTAGE TO BE ADDED.',
          '5. DIVIDED LITES ON WINDOW M AND DOOR 05 (OWNER RULE): CONFIRM WITH THE IMPACT NOAs.',
          '6. OUTLETS CL 1\'-6" (FOR SHOWS 24"); DUPLEX UNDER WINDOW M CL 11".',
          '7. CASING LEGS NARROWED WHERE AN OPENING SITS AT A WALL: 1-1/4" AT THE CORE DOORS\' SOUTH JAMBS, 3" ON THEIR VESTIBULE NORTH JAMBS, 2" AT THE BATH DOOR\'S WEST JAMB.',
          (True, 'CHANGES FROM THE PREVIOUS DESIGN (11.09.26)'),
          'A. BAR DELETED (THE OWNER DID NOT ASK FOR ONE): A15 BEVERAGE REFRIGERATOR, BAR SINK, STONE TOP, TILE SPLASH, TEAK SHELVES, ITS WATER, DRAIN, VENT AND CIRCUIT.',
          'B. REMOVED: WINDOW SEAT AND BANQUETTE, TEAK PEG RAIL, POOL STORAGE CABINETS, LIT TOWEL SHELVES, OFFICE BUILT-IN, V-GROOVE WAINSCOT, ROMAN SHADES, '
          'ROUND MIRROR AND BRASS LIGHT, FLOATING TEAK VANITY, HAND SHOWER, LIMESTONE FLOOR AND BASE, LIMEWASH.',
          'C. CODES RETIRED: ST-05, TL-06, TL-07, PT-05, PT-06, WP-03, WD-03. THE GUEST SUITE\'S CODES APPLY.']
    c3 = [(True, 'COORDINATED WITH FOR REV 1 (11.09.26)'),
          'CEILINGS (A-207): STORAGE AND OFFICE 8\'-11" WITH AN 8\'-7" BAND 10" WIDE AT THE WALLS, FOR\'S LED COVE (L12) AT THE STEP (FOR TO CONFIRM THE 8\'-11" CENTER AND THE BAND); '
          'BATH AND VESTIBULE 8\'-11".',
          'OPENINGS (A-600): DOOR 05 3\'-0" x 8\'-0" METAL, GLAZED, IMPACT, SWINGS OUT; DOORS 11 2\'-8" x 8\'-0"; WINDOW M 8\'-0" x 5\'-6", TWO PANELS, HEAD 8\'-0", SILL 2\'-6".',
          'MECHANICAL: MINI SPLITS 1 AND 2 AS FOR, TOP 8\'-1", 6" CLEAR ABOVE AND BELOW (CONFIRM WITH THE MANUFACTURER); EF IN THE BATH. LIGHTING: FOR\'S CHANDELIER BOXES, L1 DOWNLIGHTS, '
          'L12 COVE, C-1 POCKETS AT BOTH M WINDOWS; THE VANITY FIXTURE BECOMES THE BACKLIT MIRROR (J-BOX BEHIND IT).',
          'PLUMBING: FOR\'S LAV, WC AND SHOWER LOCATIONS KEPT; ADD THE CARRIER. NO OTHER FIXTURES.',
          'ROOF: FOR\'S EXTERIOR STAIR TO THE ROOF DECK (A-204, A-303) RUNS OUTSIDE THE EAST WALL; NO INTERIOR WALL CHANGES.',
          (True, 'OPEN'),
          'A. OFFICE FLOOR: WD-01 AS THE GUEST BEDROOM, OR TL-02 THROUGHOUT NEXT TO THE POOL (OWNER). B. CARRIER DEPTH IN THE CORE WALL. C. WC-01 PATTERN (AS THE GUEST BEDROOM).']
    ys = [para_block(sh, x0 + i * (col + 20), y0, c, col) for i, c in enumerate((c1, c2, c3))]
    assert max(ys) < FR.y1 - 8, ('key notes run off the sheet', max(ys))

# ------------------------------------------------------------------ ID-401 finish plan
FLOOR_ROWS = [('WD-01', 'WOOD FLOORS - FIELD (AS THE HOUSE)', 'OFFICE, AS THE GUEST BEDROOM. GLUE-DOWN WITH MOISTURE MITIGATION ON THE SLAB. OPEN: WOOD NEXT TO THE POOL, OR TL-02 (OWNER).'),
              ('TL-02', 'PORCELAIN TILE - AS THE GUEST BATHROOM', 'STORAGE, VESTIBULE AND BATH; MOSAIC AT THE SHOWER FLOOR. DCOF 0.42 MIN., FINISH AND SIZE T.B.C.')]
WALL_ROWS = [('PT-01', 'PAINT - SW 7005 PURE WHITE', 'CEILINGS (FLAT); BASE 8-1/2", CASING 5", DOORS, SHELVES AND THE OFFICE DADO WAINSCOT (SATIN).'),
             ('PT-02', 'PAINT - SW 5971 SOLSTICE (OPTION 1)', 'WALLS IN THE STORAGE ROOM, BATH AND VESTIBULE, EGGSHELL; THE BATH ON MOISTURE-RESISTANT BOARD (FOR).'),
             ('WC-01', 'WALLCOVERING - AS THE GUEST BEDROOM', 'OFFICE: ABOVE THE DADO (CAP 3\'-4", PT-01 SATIN) TO THE 8\'-7" BAND; FULL HEIGHT ON THE WINDOW WALL, NO DADO THERE.'),
             ('WT-01', 'WALL TILE - AS THE GUEST BATHROOM', 'SHOWER, THREE WALLS TO THE CEILING, 12 x 24 SET HORIZONTAL, SCHLUTER EDGE, NICHE 24" x 12".')]

def swatch(sh, x, y, code):
    sh.rect((x, y, x + 30, y + 20), 0.5, INK, WHITE)
    if code == 'WD-01':
        for j in range(1, 5): sh.line((x, y + j * 4), (x + 30, y + j * 4), 0.25, MID)
        for j in range(5):
            jx = x + (8 if j % 2 else 19); sh.line((jx, y + j * 4), (jx, y + j * 4 + 4), 0.25, MID)
    elif code == 'TL-02':
        for i in range(1, 5): sh.line((x + i * 6, y), (x + i * 6, y + 20), 0.2, MID)
        for j in range(1, 4): sh.line((x, y + j * 5), (x + 30, y + j * 5), 0.2, MID)
    elif code == 'WT-01':
        for j in range(1, 4): sh.line((x, y + j * 5), (x + 30, y + j * 5), 0.2, MID)
        for i in range(1, 3): sh.line((x + i * 10, y), (x + i * 10, y + 20), 0.2, MID)
    elif code == 'WC-01':
        for j in range(4):
            for i in range(6): sh.rect((x + 2.5 + i * 5 + (2.5 if j % 2 else 0) - 0.6, y + 2.5 + j * 5 - 0.6, x + 2.5 + i * 5 + (2.5 if j % 2 else 0) + 0.6, y + 2.5 + j * 5 + 0.6), 0, MID, MID)
    elif code == 'PT-02':
        sh.rect((x + 1, y + 1, x + 29, y + 19), 0, (0.80, 0.84, 0.82), (0.80, 0.84, 0.82))

def legend(sh, x, y, title, rows, width):
    if title: sh.text(x, y, title, 8.0, INK, bold=True, raw=True)
    y += 14
    for code, name, use in rows:
        swatch(sh, x, y, code)
        sh.text(x + 38, y + 7, code, 7.0, INK, bold=True, raw=True); sh.text(x + 76, y + 7, name, 6.5, INK, raw=True)
        ly = y + 16
        for ln in wrap(use, 6.0, width - 40): sh.text(x + 38, ly, ln, 6.0, MID); ly += NLH
        y = max(y + 28, ly + 6)
    return y

def finish_plan_sheet(sh):
    x0, y0 = plan_origin(); y0 -= 20; pl = Plan(sh, x0, y0, K_PLAN)
    # floor hatch: TL-02 12 x 12 from door 05's center line in the storage room, vestibule and bath; mosaic in the shower; WD-01 boards in the office
    cx0 = (D05_X[0] + D05_X[1]) / 2
    for a, b, c, d in [(0, 0, ST_E, IY), (CW0, BS_Y[1], CE1, IY), (CW1, SH_Y[1], CE0, BS_Y[0])]:
        x = cx0 - 6 - 12 * math.ceil((cx0 - 6 - a) / 12.0)
        while x <= c:
            if x > a: pl.line((x, b), (x, d), 0.25, LIGHT)
            x += 12
        y = IY - 12
        while y > b:
            if y < d: pl.line((a, y), (c, y), 0.25, LIGHT)
            y -= 12
    for i in range(1, 30):
        x = SH_X[0] + i * 2.0
        if x < SH_X[1]: pl.line((x, 0), (x, SH_Y[1]), 0.15, LIGHT)
    for j in range(1, 18): pl.line((SH_X[0], j * 2.0), (SH_X[1], j * 2.0), 0.15, LIGHT)
    y = 6.0; k = 0
    while y < IY:                                                                      # WD-01 boards east-west, 6", end joints staggered
        pl.line((CE1, y), (IX, y), 0.25, LIGHT)
        for jx in ((CE1 + 30 + 41 * (k % 3)), (CE1 + 30 + 41 * (k % 3) + 62)):
            if jx < IX: pl.line((jx, y - 6), (jx, y), 0.25, LIGHT)
        y += 6.0; k += 1
    draw_plan(pl)
    # wall finishes: WT-01 extents (heavy dashed 1" inside the face), dado and WC-01 walls light dashed
    def ext(a, b, w=1.6): pl.line(a, b, w, INK, dashes='[5 2.5] 0')
    ext((SH_X[0] + 0.7, 0.7), (SH_X[1] - 0.7, 0.7)); ext((SH_X[1] - 0.7, 0.7), (SH_X[1] - 0.7, SH_Y[1])); ext((SH_X[0] + 0.7, 0.7), (SH_X[0] + 0.7, SH_Y[1]))
    for a, b in (((CE1 + 1.0, 1.0), (IX - 1.0, 1.0)), ((IX - 1.0, 1.0), (IX - 1.0, IY - 1.0)), ((CE1 + 1.0, 1.0), (CE1 + 1.0, D11_Y[0]))):
        pl.line(a, b, 0.6, MID, dashes='[2 2] 0')
    # tags
    def ftag(code, x, y, s=7.0):
        q = pl.P(x, y); w = FREG.text_length(code, fontsize=s) + 8
        sh.rect((q[0] - w / 2, q[1] - 7, q[0] + w / 2, q[1] + 5), 0.5, INK, WHITE); sh.text(q[0], q[1] + 2.2, code, s, INK, align='c', raw=True)
    for code, x, y in (('TL-02', 60.0, 72.0), ('WD-01', 285.0, 74.0), ('TL-02', 163.0, 40.0), ('TL-02', 140.0, 106.0), ('TL-02 MOSAIC', 177.0, 20.0)): ftag(code, x, y)
    for code, x, y in (('PT-02', 6.0, 30.0), ('DADO / WC-01', 296.0, 7.0), ('WC-01', 300.0, IY - 6.0), ('WT-01', SH_X[1] - 10, 8.0), ('PT-02', 198.0, 40.5), ('PT-02', 196.0, 109.0)):
        q = pl.P(x, y); sh.text(q[0], q[1], code, 6.0, INK, align='l' if x < 10 else 'c', bold=True, raw=True)
    plan_labels(pl, 0.85)
    a = pl.P(-W_EXT, -W_EXT); b = pl.P(IX + W_EXT, IY + W_EXT)
    sh.text(a[0], b[1] + 40, 'POOL HOUSE FLOOR AND WALL FINISH PLAN', 11, serif=True, spacing=0.8, raw=True)
    scale_bar(sh, b[0] - 12 * K_PLAN * 10 - 110, b[1] + 42, K_PLAN)
    north(sh, a[0] - 34, a[1] + 20)
    # legends and the room finish schedule
    lx0, lx1 = FR.x0 + 14, TB_X - 14; col = (lx1 - lx0 - 40) / 3; ly = b[1] + 128
    y1 = legend(sh, lx0, ly, 'FLOOR FINISH SCHEDULE', FLOOR_ROWS, col)
    y1 = para_block(sh, lx0, y1 + 6, ['FLOOR NOTES: 1. TL-02 SET OUT FROM DOOR 05\'S CENTER LINE, FULL TILE AT THE ENTRY, 1/16" JOINTS. 2. FLOORS FLUSH, NO SADDLES; '
                                      'FLUSH METAL PROFILE AT WD-01 TO TL-02, CENTERED UNDER THE OFFICE DOOR CLOSED. 3. THE SHOWER CURBLESS ONLY IF FOR RECESSES THE SLAB, '
                                      'OTHERWISE A 2" TL-02 CURB. 4. SLAB ON GRADE: MOISTURE TEST BEFORE SETTING.'], col)
    y2 = legend(sh, lx0 + col + 20, ly, 'WALL FINISH SCHEDULE', WALL_ROWS[:2], col)
    y2 = legend(sh, lx0 + col + 20, y2 - 14, '', WALL_ROWS[2:], col)
    y3 = para_block(sh, lx0 + 2 * (col + 20), ly, [(True, 'ROOM FINISH SCHEDULE'),
        'STORAGE: TL-02 FLOOR, PT-01 BASE, PT-02 WALLS, PT-01 CEILING 8\'-11" (8\'-7" BAND, FOR\'S LED COVE).',
        'OFFICE: WD-01, PT-01 BASE, PT-01 DADO WITH WC-01 ABOVE (WC-01 FULL HEIGHT ON THE WINDOW WALL), PT-01 CEILING 8\'-11" (8\'-7" BAND, LED COVE).',
        'BATH: TL-02 (MOSAIC AT THE SHOWER), PT-02 WALLS, WT-01 IN THE SHOWER TO THE CEILING, PT-01 CEILING 8\'-11".',
        'VESTIBULE: TL-02, PT-02, PT-01 8\'-11".',
        'WALL NOTES: HEAVY DASHED LINE 1" INSIDE THE FACE = WT-01, FULL HEIGHT. LIGHT DASHED = DADO WAINSCOT WITH WC-01 ABOVE. '
        'NO CROWN IN THE POOL HOUSE: THE 5" CASING TOPS AT 8\'-5", 2" UNDER THE 8\'-7" BAND.'], col)
    assert max(y1, y2, y3) < FR.y1 - 8, ('finish legends run off the sheet', max(y1, y2, y3))

# ================================================================== build
def build():
    doc = fitz.open()
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    sh = Sheet(doc); sh.frame('POOL HOUSE', 'KEY PLAN, SCALE: 1/2" TO 1\'-0"', ['POOL HOUSE', 'KEY PLAN'], 'ID-400', legend_rule=False)
    y = key_plan_sheet(sh); key_notes(sh, y + 10)
    sh = Sheet(doc); sh.frame('POOL HOUSE', 'SCALE: 1/2" TO 1\'-0"', ['POOL HOUSE', 'FLOOR AND WALL FINISH PLAN'], 'ID-401', legend_rule=False)
    finish_plan_sheet(sh)
    RM_S, RM_O, RM_B, RM_V = 'POOL HOUSE STORAGE', 'POOL HOUSE OFFICE', 'POOL HOUSE BATH', 'POOL HOUSE VESTIBULE'
    sheets = [('ID-402', ['INTERIOR ELEVATIONS', 'POOL HOUSE STORAGE'], '1/2',
               [(1, 'NORTH ELEVATION - WINDOW M', ST_E, st_north, H_BAND, RM_S), (2, 'EAST ELEVATION - FOR\'S SHELVES, DOOR 11', IY, st_east, H_BAND, RM_S),
                (3, 'SOUTH ELEVATION - MINI SPLIT', ST_E, st_south, H_BAND, RM_S), (4, 'WEST ELEVATION', IY, st_west, H_BAND, RM_S)]),
              ('ID-403', ['INTERIOR ELEVATIONS', 'POOL HOUSE OFFICE'], '1/2',
               [(1, 'NORTH ELEVATION', OF_L, of_north, H_BAND, RM_O), (2, 'EAST ELEVATION - TV WALL', IY, of_east, H_BAND, RM_O),
                (3, 'SOUTH ELEVATION - WINDOW M', OF_L, of_south, H_BAND, RM_O), (4, 'WEST ELEVATION - DOOR 11, MINI SPLIT', IY, of_west, H_BAND, RM_O)]),
              ('ID-404', ['INTERIOR ELEVATIONS', 'POOL HOUSE BATH'], '1/2',
               [(1, 'NORTH ELEVATION - SHOWER FRONT', BW, ba_north, H_WET, RM_B), (2, 'EAST ELEVATION - SHOWER, TOILET', BD, ba_east, H_WET, RM_B),
                (3, 'SOUTH ELEVATION - DOOR 11', BW, ba_south, H_WET, RM_B), (4, 'WEST ELEVATION - VANITY', BD, ba_west, H_WET, RM_B)]),
              ('ID-405', ['INTERIOR ELEVATIONS', 'POOL HOUSE VESTIBULE'], '1/2',
               [(1, 'NORTH ELEVATION - BATH DOOR', VW, ve_north, H_WET, RM_V), (2, 'SOUTH ELEVATION - DOOR 05', VW, ve_south, H_WET, RM_V),
                (3, 'WEST ELEVATION - DOOR 11 TO STORAGE', VD, ve_west, H_WET, RM_V), (4, 'EAST ELEVATION - DOOR 11 TO OFFICE', VD, ve_east, H_WET, RM_V)])]
    for sid, tl, scale, views in sheets:
        s = Sheet(doc); s.frame('POOL HOUSE', 'SCALE: %s" TO 1\'-0"' % scale, tl, sid, legend_rule=False)
        draw_views(s, cells_2x2(frame, views, scale), views, scale)
    fix_soft_hyphen(doc); doc.set_metadata({'title': 'Casa Grove pool house ID-400 to ID-405', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, len(doc), 'sheets')

if __name__ == '__main__':
    build()
