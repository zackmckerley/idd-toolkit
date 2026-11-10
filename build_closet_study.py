"""Master closet (FOR's W.I.C., floor 2): ten design options (owner 11.09.26: "design the master closet now. The north wall (the wall you
see from the bathroom) has a showcase for purses ... cabinet or drawers below. On the west side a really nice vanity for my wife to do her
makeup, wide enough for two people to sit next to each other. Utilize the center island for drawers. There is a chute on the right side
that you'll need to accommodate. Dream up the most amazing / luxurious closets. Give me 10 different options.")
Room measured on FOR's A-202 REV 1 (same as our base): inside faces x 446.1 to 690.0, y 832.0 to 1064.2 FOR pt at 1/4" (1.5 pt/in):
13'-6-5/8" east-west by 12'-10-3/4" north-south. Ceiling 9'-6" (A-206 REV 1, CLG tag in the W.I.C.; FOR's RCP: closet lighting L14 at the
built-ins, L13 on the west, a fixture centered on the space). Door 19 (pair) centered on the south wall from the master bath.
FOR's LAUNDRY CHUTE (owner confirmed laundry, 11.09.26): a shaft about 18-1/2" square in the east run, 4'-11" to 6'-6" from the
north wall.
Output: 261109.HD102.MasterClosetOptions.pdf, ID-330 (key plan, brief, how to choose) and ID-331 to ID-335 (two options each)."""
import sys, math, random
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_std
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen, _FR, _FB
from idd_std import INK, MID, LIGHT

OUT = '/home/claude/flrwork/261109.HD102.MasterClosetOptions.pdf'
PALE = (0.86, 0.86, 0.86); GLOW = (0.93, 0.93, 0.9); WHITE = (1, 1, 1); STONE = (0.9, 0.9, 0.88); DARK = (0.35, 0.35, 0.35)
HEAVY, OUTLINE, MED, FINE = C.HEAVY, C.OUTLINE, C.MED, C.FINE

# ---------------------------------------------------------------- the room (inches, origin at the NW inside corner, x east, y south)
W = 162.6            # (690.0 - 446.1) / 1.5
D = 154.8            # (1064.2 - 832.0) / 1.5
H = 114.0            # 9'-6" (A-206)
DOOR_C, DOOR_W = 81.3, 36.0                      # door 19, pair of 1'-6" leaves, centered
CH_Y0, CH_Y1, CH_D = 59.1, 77.7, 23.3            # the chute shaft in the east run (from the north wall; depth from the east wall)
DE = 24.0            # east run: hanging and the chute
DF = 24.0            # west run flanks (towers)
DV = 22.0            # vanity depth
AISLE = 36.0
CROWN = 4.5

def L(v, a, b, w=MED, c=None, d=None): C._line(v, a, b, w, c, d)
def R(v, x0, y0, x1, y1, w=MED, c=None, fill=None, d=None): C._rect(v, x0, y0, x1, y1, w, c, fill, d)
def P(v, pts, w=MED, c=None, fill=None, close=True): C._poly(v, pts, w, c, fill, close)

# ---------------------------------------------------------------- pieces drawn in elevation (inches, y up)
def crown_band(v, x0, x1):
    """Cabinets run to the ceiling: a 4-1/2" crown on a flush soffit line, continuous across the wall (ID-501 rule)."""
    C.crown(v, x0, x1, H, drop=CROWN)

def toe(v, x0, x1, h=4.0, recess=True):
    R(v, x0, 0, x1, h, OUTLINE, fill=PALE if recess else None)

def bag(v, cx, y0, w, h, kind=0, c=None):
    """A handbag on its shelf, for size: tapered body, flap or zip line, top handle."""
    c = MID if c is None else c
    tw = w * (0.78 if kind % 3 else 0.9)
    P(v, [(cx - w / 2, y0), (cx + w / 2, y0), (cx + tw / 2, y0 + h), (cx - tw / 2, y0 + h)], FINE, c, fill=WHITE)
    if kind % 2: L(v, (cx - tw / 2, y0 + h * 0.62), (cx + tw / 2, y0 + h * 0.62), FINE, c); C._ellipse(v, cx, y0 + h * 0.5, 0.6, 0.6, FINE, c)
    else: L(v, (cx - tw / 2 + 0.6, y0 + h - 1.2), (cx + tw / 2 - 0.6, y0 + h - 1.2), FINE, c)
    C._arc(v, cx, y0 + h, tw * 0.28, 0, 180, FINE, c)

def drawers(v, x0, x1, y0, y1, n=3, pull='bar', leather=False):
    """A bank of inset drawers between y0 and y1 (top drawer shallower)."""
    R(v, x0, y0, x1, y1, OUTLINE)
    hs = [1.0] if n == 1 else [0.8] + [1.1] * (n - 1); s = sum(hs); y = y1; g = 0.75
    for h_ in hs:
        hh = (y1 - y0) * h_ / s
        R(v, x0 + g, y - hh + g / 2, x1 - g, y - g / 2, FINE)
        cy = y - hh / 2; cx = (x0 + x1) / 2
        if leather: L(v, (x0 + 1.6, y - hh + 1.6), (x1 - 1.6, y - hh + 1.6), FINE, LIGHT, '[1 1] 0')
        if pull == 'bar': L(v, (cx - min(5, (x1 - x0) * 0.2), cy), (cx + min(5, (x1 - x0) * 0.2), cy), OUTLINE)
        elif pull == 'knob': C._ellipse(v, cx, cy, 0.7, 0.7, MED)
        elif pull == 'edge': L(v, (x0 + 1.5, y - g / 2 - 0.3), (x1 - 1.5, y - g / 2 - 0.3), MED)
        y -= hh

def door(v, x0, x1, y0, y1, kind='slab', hinge='L', glass=False, knob=True):
    """One cabinet door: slab, shaker (frame and panel), fluted, mirror, glass; a pull at the latch side."""
    R(v, x0, y0, x1, y1, OUTLINE)
    if kind == 'shaker': R(v, x0 + 2.5, y0 + 2.5, x1 - 2.5, y1 - 2.5, MED)
    if kind == 'fluted':
        x = x0 + 1.25
        while x < x1 - 0.6: L(v, (x, y0 + 0.6), (x, y1 - 0.6), FINE, LIGHT); x += 1.25
    if kind == 'mirror':
        R(v, x0 + 1.5, y0 + 1.5, x1 - 1.5, y1 - 1.5, FINE, fill=PALE)
        rnd = random.Random(int(x0 * 7 + y0));
        for _ in range(int((x1 - x0) * (y1 - y0) / 40)):
            px = rnd.uniform(x0 + 2, x1 - 2); py = rnd.uniform(y0 + 2, y1 - 2); C._ellipse(v, px, py, 0.25, 0.25, FINE, MID)
    if glass:
        R(v, x0 + 1.75, y0 + 1.75, x1 - 1.75, y1 - 1.75, FINE, LIGHT)
    if knob:
        px = x1 - 1.6 if hinge == 'L' else x0 + 1.6
        L(v, (px, (y0 + y1) / 2 - 3), (px, (y0 + y1) / 2 + 3), OUTLINE)

def cubbies(v, x0, x1, y0, y1, cols, rows, seed=1, back=None, rail=1.25, arch=False, bags=True, led=True, frame=OUTLINE):
    """Lit display cubbies for handbags: uprights and shelves, a bag on most shelves, an LED line under each shelf."""
    rnd = random.Random(seed)
    R(v, x0, y0, x1, y1, frame, fill=back)
    cw = (x1 - x0) / cols; rh = (y1 - y0) / rows
    for i in range(1, cols): L(v, (x0 + i * cw, y0), (x0 + i * cw, y1), MED)
    for j in range(1, rows):
        y = y0 + j * rh; R(v, x0, y - rail / 2, x1, y + rail / 2, FINE, fill=WHITE)
        if led: L(v, (x0 + 0.8, y - rail / 2 - 0.4), (x1 - 0.8, y - rail / 2 - 0.4), FINE, LIGHT, '[1.5 1] 0')
    if bags:
        for i in range(cols):
            for j in range(rows):
                bw = min(cw - 4, rnd.uniform(9, 13)); bh = min(rh - 4.5, rnd.uniform(7.5, 10.5))
                bag(v, x0 + (i + 0.5) * cw + rnd.uniform(-1, 1), y0 + j * rh + rail / 2 + 0.2, bw, bh, rnd.randint(0, 5))

def glass_door_grid(v, x0, x1, y0, y1, n, frame=2.0, bronze=True):
    """Framed glass doors over a display (bronze or wood frames), hinged in pairs, small pulls."""
    w = (x1 - x0) / n
    for i in range(n):
        a = x0 + i * w; b = a + w
        R(v, a, y0, b, y1, OUTLINE); R(v, a + frame, y0 + frame, b - frame, y1 - frame, MED)
        px = b - frame - 0.9 if i % 2 == 0 else a + frame + 0.9
        L(v, (px, (y0 + y1) / 2 - 4), (px, (y0 + y1) / 2 + 4), OUTLINE)
        L(v, (a + frame + 2, y1 - frame - 3), (a + w * 0.4, y1 - (y1 - y0) * 0.3), FINE, PALE)

def stone_top(v, x0, x1, y, t=1.5, edge=0.5):
    R(v, x0 - edge, y, x1 + edge, y + t, OUTLINE, fill=STONE)

def end_profile(v, x0, x1, top=H, label=None):
    """A side run seen end-on at the corner of the wall: its cabinet side, toe and crown, light grey."""
    R(v, x0, 0, x1, top, OUTLINE, fill=GLOW)
    R(v, x0, 0, x1, 4, FINE, fill=PALE)
    if label: v.text(v.X((x0 + x1) / 2), v.Y(top / 2), label, 4.5, MID, align='c', rotate=90)

def stool(v, cx, seat=18.0, w=16.0, kind='drum'):
    """A vanity stool in front of the knee space (furniture, N.I.C.)."""
    d = '[2 1.5] 0'
    if kind == 'drum':
        R(v, cx - w / 2, 0, cx + w / 2, seat, MED, d=d); L(v, (cx - w / 2, seat - 3), (cx + w / 2, seat - 3), FINE, LIGHT, d)
    else:
        R(v, cx - w / 2, seat - 3, cx + w / 2, seat, MED, d=d)
        for x in (cx - w / 2 + 1.5, cx + w / 2 - 1.5): L(v, (x, 0), (x, seat - 3), MED, None, d)

def sconce(v, cx, cy, style='cylinder'): C.sconce(v, cx, cy, style)

def mirror_arched(v, x0, x1, y0, y1, frame=2.0):
    """Arched-top framed mirror: straight sides, a half-round head."""
    w = x1 - x0; r = w / 2; cx = (x0 + x1) / 2; ys = y1 - r
    for off, lw in ((0, OUTLINE), (frame, MED)):
        pts = [(x0 + off, y0 + off), (x0 + off, ys)] + [(cx + (r - off) * math.cos(math.radians(180 - a)), ys + (r - off) * math.sin(math.radians(180 - a))) for a in range(0, 181, 6)] + [(x1 - off, ys), (x1 - off, y0 + off)]
        P(v, pts, lw)
    L(v, (x0 + frame + 3, ys), (cx, y0 + frame + 4), FINE, PALE)

def mirror_round(v, cx, cy, r, frame=1.5):
    C._ellipse(v, cx, cy, r, r, OUTLINE); C._ellipse(v, cx, cy, r - frame, r - frame, MED)
    L(v, (cx - r * 0.45, cy + r * 0.2), (cx + r * 0.05, cy - r * 0.45), FINE, PALE)

def mirror_rect(v, x0, x1, y0, y1, frame=2.0, lit=False):
    C.mirror_framed(v, x0, x1 - x0, y0, y1 - y0, frame=frame)
    if lit: R(v, x0 - 0.8, y0 - 0.8, x1 + 0.8, y1 + 0.8, FINE, LIGHT, d='[1.5 1] 0')

def bulbs(v, x0, x1, y0, y1, pitch=6.0):
    """Exposed globe lamps around a mirror (a dressing-room border)."""
    n = max(2, int((x1 - x0) / pitch));
    for i in range(n + 1): C._ellipse(v, x0 + (x1 - x0) * i / n, y1 + 2, 1.3, 1.3, MED)
    m = max(2, int((y1 - y0) / pitch))
    for j in range(m + 1):
        for x in (x0 - 2, x1 + 2): C._ellipse(v, x, y0 + (y1 - y0) * j / m, 1.3, 1.3, MED)

def chandelier(v, cx, drop=30.0, w=28.0, kind='tiered'):
    """Decorative fixture over the island, dashed (FOR's RCP: centered on the space)."""
    d = '[2 1.5] 0'
    L(v, (cx, H), (cx, H - drop + 12), MED, None, d)
    if kind == 'tiered':
        for k, f in ((0, 1.0), (1, 0.72), (2, 0.45)):
            y = H - drop + 12 - k * 4
            R(v, cx - w * f / 2, y - 4, cx + w * f / 2, y, FINE, None, d=d)
    elif kind == 'drum':
        R(v, cx - w / 2, H - drop, cx + w / 2, H - drop + 9, MED, d=d)
    else:   # sputnik / globe
        C._ellipse(v, cx, H - drop + 6, w / 2, 6, MED, dashes=d)
        for a in range(0, 180, 30):
            L(v, (cx, H - drop + 6), (cx + w / 2 * math.cos(math.radians(a)), H - drop + 6 + 6 * math.sin(math.radians(a))), FINE, None, d)

def hanging(v, x0, x1, y_rod, y_bot, n=None, seed=3, c=LIGHT):
    """Hanging clothes beyond, for size: a rod and garment silhouettes."""
    rnd = random.Random(seed)
    L(v, (x0, y_rod), (x1, y_rod), MED)
    x = x0 + 1.5
    while x < x1 - 2:
        w_ = rnd.uniform(1.5, 3.0); bot = y_bot + rnd.uniform(0, 10)
        P(v, [(x, y_rod - 1), (x + w_, y_rod - 1), (x + w_ + 0.6, bot), (x - 0.4, bot)], FINE, c)
        x += w_ + 0.4

# ---------------------------------------------------------------- the ten
SPECS = [
    dict(n=1, shoe_front='glass', name='THE GALLERY', rec=True, cost='$$$', dN=18.0, north='vitrine', west='arched_towers', vw=48.0, island='glass_drawers', shape='rect', chand='tiered',
         text='A LIT VITRINE: BRONZE-FRAMED GLASS DOORS OVER 16 HANDBAG CUBBIES, LED UNDER EVERY SHELF, CLOSED TALL CABINETS EACH SIDE, LEATHER-LINED DRAWERS AND A STONE TOP BELOW. A 4 FT VANITY FOR TWO WITH TWO ARCHED MIRRORS AND A SCONCE BETWEEN, LIT GLASS JEWELRY TOWERS EACH SIDE. ISLAND OF DRAWERS WITH A GLASS-TOP JEWELRY ROW, STONE TOP, A TIERED CHANDELIER. SHOES: 36 PAIRS IN A LIT TOWER BEHIND BRONZE-FRAMED GLASS AT THE SOUTH END OF THE EAST RUN.'),
    dict(n=2, shoe_front='open', name='BACKLIT ONYX', cost='$$$$', dN=18.0, north='onyx', west='mirror_wall', vw=48.0, island='waterfall', shape='rect', chand='drum',
         text='FOUR NICHES WITH BACKLIT HONEY ONYX BACKS, 16 BAGS ON FLOATING SHELVES, LACQUER DOORS EACH SIDE AND A ROW OF DRAWERS BELOW. A 4 FT FLOATING VANITY UNDER A LIT MIRROR, FULL-HEIGHT MIRROR DOORS EACH SIDE. AN ONYX-TOPPED ISLAND WITH MITERED WATERFALL ENDS. THE MOST DRAMATIC AT NIGHT; ONYX IS SOFT AND COSTLY. SHOES: 36 PAIRS ON OPEN LIT SHELVES WITH A BRASS HEEL RAIL, EAST RUN.'),
    dict(n=3, shoe_front='glass', name='PARISIAN SALON', cost='$$', dN=18.0, north='paneled', west='skirted_triptych', vw=48.0, island='legs', shape='rect', chand='tiered',
         text='PAINTED PICTURE-FRAME DOORS TO MATCH THE BEDROOM PANELING, A GLASS VITRINE IN THE CENTER FOR 16 BAGS. A 4 FT SKIRTED VANITY WITH A TRIPTYCH MIRROR AND TWO SLIPPER STOOLS, PAINTED TALL CABINETS EACH SIDE. A FURNITURE ISLAND ON TURNED LEGS WITH A MARBLE TOP. CLASSIC, CALM, THE LEAST COST HERE. SHOES: 36 PAIRS BEHIND PAINTED GLASS DOORS, EAST RUN.'),
    dict(n=4, shoe_front='open', name='FLUTED WALNUT', cost='$$$', dN=18.0, north='fluted', west='round_fluted', vw=48.0, island='fluted_round', shape='racetrack', chand='globe',
         text='FLUTED WALNUT DOORS FRAME A LIT SHOWCASE FOR 16 BAGS WITH BRASS-EDGED SHELVES. A 4 FT FLOATING FLUTED VANITY WITH TWO ROUND BACKLIT MIRRORS, FLUTED TALL CABINETS EACH SIDE. A RACETRACK ISLAND, FLUTED ALL AROUND, PUSH-LATCH DRAWERS, A ROUNDED STONE TOP. WARM AND SCULPTURAL. SHOES: 36 PAIRS ON OPEN WALNUT SHELVES, LIT, EAST RUN.'),
    dict(n=5, shoe_front='open', name='BRASS BOUTIQUE', cost='$$$', dN=16.0, north='brass_open', west='hollywood', vw=48.0, island='brass_glass', shape='rect', chand='globe',
         text='OPEN SHOWCASE LIKE A BOUTIQUE: A SLIM BRASS GRID WITH GLASS SHELVES FOR 16 BAGS, NO DOORS, LIT FROM ABOVE; LEATHER-WRAPPED DOORS EACH SIDE AND DRAWERS BELOW. A 4 FT DRESSING-ROOM VANITY: TWO MIRRORS RINGED WITH GLOBE LAMPS, TALL CABINETS EACH SIDE. A BRASS-TRIMMED ISLAND WITH A GLASS DISPLAY TOP. OPEN SHELVES NEED DUSTING. SHOES: 36 PAIRS ON OPEN GLASS SHELVES WITH BRASS HEEL RAILS, EAST RUN.'),
    dict(n=6, shoe_front='glass', name='MIRRORED MAISON', cost='$$$', dN=18.0, north='mirror', west='mirror_sconces', vw=48.0, island='lacquer_plinth', shape='rect', chand='tiered',
         text='ANTIQUED MIRROR DOORS; THE FOUR CENTER DOORS HAVE CLEAR LITES SHOWING 16 BAGS, THE OUTER TWO ARE CLOSED. A MIRRORED WALL BEHIND THE 4 FT VANITY WITH A SCONCE ON THE GLASS, MIRROR DOORS EACH SIDE SO THE WHOLE WALL REFLECTS. A HIGH-GLOSS LACQUER ISLAND ON A MIRRORED PLINTH. GLAMOROUS; FINGERPRINTS SHOW. SHOES: 36 PAIRS BEHIND GLASS, EAST RUN.'),
    dict(n=7, shoe_front='open', name='ARCHED NICHES', cost='$$', dN=18.0, north='arches', west='arched_alcove', vw=48.0, island='curved', shape='racetrack', chand='drum',
         text='FOUR ARCHED, LIT NICHES IN PLASTER, FOUR BAGS HIGH (16), CABINETS BELOW. THE 4 FT VANITY SITS IN AN ARCHED ALCOVE WITH ONE ARCHED MIRROR AND TWO SCONCES, LIT JEWELRY TOWERS EITHER SIDE. AN ISLAND WITH CURVED ENDS AND A HONED STONE TOP. ECHOES THE HOUSE\'S ARCHES. SHOES: 36 PAIRS ON OPEN LIT SHELVES, EAST RUN.'),
    dict(n=8, shoe_front='glass', name='GLASS AND LACQUER', cost='$$$$', dN=16.0, north='lacquer', west='backlit_strip', vw=48.0, island='glass_top', shape='rect', chand='globe',
         text='FRAMELESS GLASS DOORS OVER 16 HIGH-GLOSS CUBBIES, VERTICAL LED IN EVERY UPRIGHT, PLAIN LACQUER DOORS EACH SIDE AND DRAWERS BELOW. A 4 FT LACQUER VANITY UNDER A MIRROR WITH A BACKLIT EDGE, LACQUER TALL CABINETS EACH SIDE. A FRAMELESS ISLAND WITH A GLASS TOP OVER VELVET JEWELRY TRAYS. THE MOST MODERN; THE MOST UPKEEP. SHOES: 36 PAIRS BEHIND FRAMELESS GLASS, EAST RUN.'),
    dict(n=9, shoe_front='glass', name='JEWEL BOX', cost='$$$', dN=18.0, north='velvet', west='towers_full', vw=48.0, island='bench_end', shape='rect', chand='tiered',
         text='16 CUBBIES, EACH WITH ITS OWN LIT GLASS DOOR, A BRASS KNOB AND A VELVET BACK; PAINTED DOORS EACH SIDE. THE 4 FT VANITY IS FLANKED BY FULL-HEIGHT JEWELRY TOWERS WITH PULL-OUT TRAYS. THE ISLAND ENDS IN AN UPHOLSTERED BENCH FOR PUTTING ON SHOES. RICH, COLLECTED, LIKE A JEWELER\'S CASE. SHOES: 36 PAIRS BEHIND LIT GLASS DOORS, EAST RUN.'),
    dict(n=10, shoe_front='open', name='SHOWROOM', cost='$$$$', dN=18.0, north='showroom', west='threeway_bench', vw=48.0, island='oval_glass', shape='oval', chand='tiered',
         text='16 BAGS ON INDIVIDUAL LIT PLINTHS BEHIND GLASS, STEPPED LIKE A STORE, A FULL-HEIGHT LIT MIRROR IN THE CENTER. A THREE-WAY MIRROR OVER THE 4 FT VANITY, ONE UPHOLSTERED BENCH FOR TWO, FULL-HEIGHT MIRROR DOORS EACH SIDE. AN OVAL ISLAND WITH A GLASS DISPLAY TOP. THE MOST THEATRICAL. SHOES: 36 PAIRS ON OPEN LIT SHELVES LIKE A STORE, EAST RUN.'),
]

def island_box(s):
    """Island footprint (x0, y0, x1, y1): 36" aisles to the runs, 33" to the south wall for the door leaves."""
    x0, x1 = DF + AISLE, W - DE - AISLE
    cx = (x0 + x1) / 2; w = 42.0
    y0 = s['dN'] + AISLE; y1 = D - 33.0
    return cx - w / 2, y0, cx + w / 2, y1

def vanity_span(s):
    """West run: vanity centered on the island, towers or hanging either side to the north run and the south wall."""
    yc = (s['dN'] + D) / 2                     # centered on the open west wall, equal towers each side
    return yc - s['vw'] / 2, yc + s['vw'] / 2

# ---------------------------------------------------------------- north wall (seen from the bath): x 0 (west) to W (east)
def north_wall(v, s):
    a, b = DF, W - DE
    end_profile(v, 0, a, label='WEST RUN'); end_profile(v, b, W, label='EAST RUN')
    st = s['north']; rnd = random.Random(s['n'])
    BASE_T = 34.0
    crown_band(v, a, b)
    BW = (b - a) / 6                          # six equal bays; the 16 bags (owner 11.09.26) take the middle four, closed storage either side
    c0, c1 = a + BW, b - BW
    def side_doors(y0, y1, kind='shaker', knob=True):
        for x0_, hg in ((a, 'R'), (c1, 'L')): door(v, x0_, x0_ + BW, y0, y1, kind, hg, knob=knob)
    if st == 'vitrine':
        toe(v, a, b); w = (b - a) / 4
        for i in range(4): drawers(v, a + i * w, a + (i + 1) * w, 4, BASE_T, 3, 'bar', leather=True)
        stone_top(v, a, b, BASE_T)
        side_doors(BASE_T + 1.5, H - CROWN)
        cubbies(v, c0 + 1, c1 - 1, BASE_T + 1.5, 94, 4, 4, s['n'], back=GLOW)
        glass_door_grid(v, c0, c1, BASE_T + 1.5, 94, 4)
        for i in range(4): door(v, c0 + i * BW, c0 + (i + 1) * BW, 94, H - CROWN, 'shaker', 'L' if i % 2 == 0 else 'R')
    elif st == 'onyx':
        toe(v, a, b)
        for i in range(6): drawers(v, a + i * BW, a + (i + 1) * BW, 4, 30, 2, 'edge')
        side_doors(30, H - CROWN, 'slab')
        R(v, c0, 30, c1, H - CROWN, OUTLINE)
        for i in range(4):
            x0, x1 = c0 + i * BW + 1.5, c0 + (i + 1) * BW - 1.5
            R(v, x0, 32, x1, H - CROWN - 2, MED, fill=GLOW)
            rr = random.Random(i + 7)
            for _ in range(4):
                y = rr.uniform(36, H - 12); L(v, (x0, y), (x1, y + rr.uniform(-6, 6)), FINE, LIGHT)
            pitch = (H - CROWN - 2 - 32) / 4
            for j in range(4):
                y = 32 + j * pitch
                if j: R(v, x0, y - 0.6, x1, y + 0.6, FINE, fill=WHITE)
                bag(v, (x0 + x1) / 2 + rr.uniform(-1, 1), y + 0.6, min(x1 - x0 - 4, rr.uniform(10, 12.5)), min(pitch - 4, rr.uniform(8.5, 10.5)), i + j)
    elif st == 'paneled':
        toe(v, a, b)
        for i in range(6): door(v, a + i * BW, a + (i + 1) * BW, 4, 32, 'shaker', 'L' if i % 2 == 0 else 'R')
        stone_top(v, a, b, 32)
        for x0_, hg in ((a, 'R'), (c1, 'L')):
            door(v, x0_, x0_ + BW, 33.5, H - CROWN, 'shaker', hg)
            R(v, x0_ + 5, 40, x0_ + BW - 5, 60, FINE); R(v, x0_ + 5, 66, x0_ + BW - 5, H - CROWN - 7, FINE)
        cubbies(v, c0 + 1, c1 - 1, 33.5, H - CROWN - 1, 4, 4, s['n'], back=GLOW)
        glass_door_grid(v, c0, c1, 33.5, H - CROWN, 4, frame=3.0)
    elif st == 'fluted':
        toe(v, a, b); w = (b - a) / 6
        for i in range(6): drawers(v, a + i * w, a + (i + 1) * w, 4, 32, 3, 'edge')
        stone_top(v, a, b, 32)
        for i in (0, 5): door(v, a + i * w, a + (i + 1) * w, 33.5, H - CROWN, 'fluted', 'L' if i == 0 else 'R')
        cubbies(v, a + w, a + 5 * w, 33.5, H - CROWN, 4, 4, s['n'], back=GLOW, rail=1.5)
    elif st == 'brass_open':
        toe(v, a, b); w = (b - a) / 4
        for i in range(4): drawers(v, a + i * w, a + (i + 1) * w, 4, 30, 2, 'bar', leather=True)
        stone_top(v, a, b, 30)
        side_doors(31.5, H - CROWN, 'slab')
        cubbies(v, c0, c1, 31.5, H - CROWN, 4, 4, s['n'], back=None, rail=0.5, frame=MED)
        for i in range(5):
            x = c0 + i * BW; R(v, x - 0.4, 31.5, x + 0.4, H - CROWN, FINE, fill=STONE)
    elif st == 'mirror':
        toe(v, a, b)
        for i in range(6): drawers(v, a + i * BW, a + (i + 1) * BW, 4, 30, 2, 'knob')
        stone_top(v, a, b, 30)
        for i in range(6):
            x0, x1 = a + i * BW, a + (i + 1) * BW
            door(v, x0, x1, 31.5, H - CROWN, 'mirror', 'L' if i % 2 == 0 else 'R')
            if i in (0, 5): continue                                          # closed: full antiqued mirror
            R(v, x0 + 3, 36, x1 - 3, H - CROWN - 5, MED, fill=WHITE)            # clear center lite, the bags show through
            pitch = (H - CROWN - 5 - 36) / 4
            for j in range(4):
                y = 36 + j * pitch
                if j: L(v, (x0 + 3, y), (x1 - 3, y), FINE, MID)
                bag(v, (x0 + x1) / 2, y + 0.3, min(BW - 9, 10), min(pitch - 4, 9.5), i + j)
    elif st == 'arches':
        R(v, a, 0, b, H - CROWN, OUTLINE, fill=GLOW)
        toe(v, a, b); n = 4; w = (b - a) / n
        for i in range(n): door(v, a + i * w + 0.5, a + (i + 1) * w - 0.5, 4, 32, 'shaker', 'L' if i % 2 == 0 else 'R')
        stone_top(v, a, b, 32)
        for i in range(n):
            x0, x1 = a + i * w + 4, a + (i + 1) * w - 4; r = (x1 - x0) / 2; ys = H - CROWN - 6 - r
            pts = [(x0, 36), (x0, ys)] + [((x0 + x1) / 2 + r * math.cos(math.radians(180 - t)), ys + r * math.sin(math.radians(180 - t))) for t in range(0, 181, 6)] + [(x1, ys), (x1, 36)]
            P(v, pts, OUTLINE, fill=WHITE)
            pitch = 16.2
            for j in range(4):
                y = 36 + j * pitch
                if j: R(v, x0, y - 0.6, x1, y + 0.6, FINE, fill=WHITE)
                bag(v, (x0 + x1) / 2, y + 0.6, min(x1 - x0 - 6, 12), 9.5, i + j)
    elif st == 'lacquer':
        toe(v, a, b)
        for i in range(6): drawers(v, a + i * BW, a + (i + 1) * BW, 4, 30, 2, 'edge')
        side_doors(30, H - CROWN, 'slab', knob=False)
        cubbies(v, c0 + 0.5, c1 - 0.5, 30.5, H - CROWN - 0.5, 4, 4, s['n'], back=None, rail=0.75)
        for i in range(4):
            x0 = c0 + i * BW; R(v, x0, 30, x0 + BW, H - CROWN, OUTLINE)
            L(v, (x0 + 0.6, 33), (x0 + 0.6, H - CROWN - 3), FINE, LIGHT, '[1.5 1] 0')
            L(v, (x0 + 2, H - CROWN - 6), (x0 + BW * 0.45, H - 50), FINE, PALE)
    elif st == 'velvet':
        toe(v, a, b)
        for i in range(6): drawers(v, a + i * BW, a + (i + 1) * BW, 4, 30, 2, 'knob')
        stone_top(v, a, b, 30)
        side_doors(31.5, H - CROWN)
        cubbies(v, c0, c1, 31.5, H - CROWN, 4, 4, s['n'], back=PALE, rail=1.5)
        rh = (H - CROWN - 31.5) / 4
        for i in range(4):
            for j in range(4):
                x0, y0 = c0 + i * BW, 31.5 + j * rh
                R(v, x0 + 0.6, y0 + 0.6, x0 + BW - 0.6, y0 + rh - 0.6, FINE)
                C._ellipse(v, x0 + BW - 2.2, y0 + rh / 2, 0.6, 0.6, MED)
    elif st == 'showroom':
        toe(v, a, b); w = (b - a) / 6
        for i in range(6): drawers(v, a + i * w, a + (i + 1) * w, 4, 26, 2, 'edge')
        cx = (a + b) / 2
        mirror_rect(v, cx - 15, cx + 15, 26, H - CROWN - 2, frame=1.5, lit=True)
        for side in (-1, 1):
            x0, x1 = (a, cx - 17) if side < 0 else (cx + 17, b)
            R(v, x0, 26, x1, H - CROWN, OUTLINE)
            n = 2; cw = (x1 - x0) / n
            for i in range(n):
                xa = x0 + i * cw; k_ = i if side < 0 else n - 1 - i
                for j in range(4):
                    base = 29 + j * 19 + k_ * 3
                    R(v, xa + 3, base, xa + cw - 3, base + 4, FINE, fill=GLOW)
                    bag(v, xa + cw / 2, base + 4, min(cw - 7, 12), 10, i + j + side)
            L(v, (x0 + 2, H - CROWN - 4), (x0 + (x1 - x0) * 0.4, 40), FINE, PALE)
    # the purse showcase label
    v.text(v.X((a + b) / 2), v.Y(H) - 3, 'PURSE SHOWCASE', 5.0, INK, align='c')

# ---------------------------------------------------------------- west wall (seen from the island): x 0 (south) to D (north)
def west_wall(v, s):
    y0v, y1v = vanity_span(s)
    xa, xb = D - y1v, D - y0v                 # vanity in elevation x
    nN = D - s['dN']                          # the north run's face
    R(v, -6, 0, 0, H, HEAVY, fill=(0.3, 0.3, 0.3))     # the south wall, cut (the door wall)
    end_profile(v, nN, D, label='NORTH RUN')
    crown_band(v, 0, nN)
    st = s['west']; TOP = 30.0; cx = (xa + xb) / 2
    # vanity body (owner 11.09.26: 4'-0" wide, two seated side by side): one continuous 48" knee space, two 24" seats,
    # a pair of shallow apron drawers under the top
    if st == 'skirted_triptych':
        R(v, xa, 0, xb, TOP, OUTLINE)
        x = xa + 1.5
        while x < xb - 1: L(v, (x, 1), (x + 0.6, TOP - 3), FINE, LIGHT); x += 2.4
        L(v, (xa, TOP - 3), (xb, TOP - 3), MED)
    else:
        for x0_, x1_ in ((xa, cx), (cx, xb)): drawers(v, x0_, x1_, TOP - 5.5, TOP - 1.5, 1, 'edge' if st in ('mirror_wall', 'backlit_strip') else 'bar')
        R(v, xa, 0, xb, TOP - 5.5, FINE, LIGHT, d='[2 1.5] 0')                      # the knee space, clear
        if st in ('mirror_wall', 'backlit_strip', 'round_fluted'): L(v, (xa + 1, TOP - 6.1), (xb - 1, TOP - 6.1), FINE, LIGHT, '[1.5 1] 0')   # LED under the apron
        if st == 'round_fluted':
            x = xa + 1.25
            while x < xb - 0.6: L(v, (x, TOP - 5.0), (x, TOP - 2.0), FINE, LIGHT); x += 1.25
    stone_top(v, xa, xb, TOP - 1.5)
    kc = [xa + 12, xb - 12]                                                      # seat centers, 24" each
    if st == 'threeway_bench':
        R(v, xa + 2, 0, xb - 2, 18, MED, d='[2 1.5] 0'); L(v, (xa + 2, 14), (xb - 2, 14), FINE, LIGHT, '[2 1.5] 0')
        v.text(v.X(cx), v.Y(8), 'BENCH FOR TWO', 4.0, MID, align='c')
    else:
        for c_ in kc: stool(v, c_, w=15.0, kind='drum' if st != 'skirted_triptych' else 'slipper')
    MY0 = TOP + 8; MY1 = 84.0
    # mirrors and lights, sized to the 4'-0" top
    if st == 'arched_towers':
        for c_ in kc: mirror_arched(v, c_ - 9.5, c_ + 9.5, MY0, MY1 + 6)
        sconce(v, cx, 62)
    elif st == 'mirror_wall':
        mirror_rect(v, xa, xb, TOP + 2, H - CROWN - 6, frame=0.6, lit=True)
    elif st == 'skirted_triptych':
        mirror_arched(v, cx - 10, cx + 10, MY0, MY1 + 4)
        mirror_rect(v, cx - 22.5, cx - 11, MY0 + 6, MY1 - 6, frame=1.5); mirror_rect(v, cx + 11, cx + 22.5, MY0 + 6, MY1 - 6, frame=1.5)
    elif st == 'round_fluted':
        for c_ in kc: mirror_round(v, c_, 60, 10.5); C._ellipse(v, c_, 60, 11.5, 11.5, FINE, LIGHT, dashes='[1.5 1] 0')
    elif st == 'hollywood':
        for c_ in kc: mirror_rect(v, c_ - 8.5, c_ + 8.5, MY0, MY1, frame=1.5)
        m_ = 7
        for x_ in (kc[0] - 10.5, cx, kc[1] + 10.5):                     # one shared column of globes between the two mirrors
            for j in range(m_ + 1): C._ellipse(v, x_, MY0 + (MY1 - MY0) * j / m_, 1.3, 1.3, MED)
        for c_ in kc:
            for i in range(4): C._ellipse(v, c_ - 7.5 + 5 * i, MY1 + 2.2, 1.3, 1.3, MED)
    elif st == 'mirror_sconces':
        R(v, xa, TOP + 1, xb, H - CROWN - 1, OUTLINE, fill=PALE)
        rnd = random.Random(9)
        for _ in range(60): C._ellipse(v, rnd.uniform(xa + 1, xb - 1), rnd.uniform(TOP + 2, H - CROWN - 2), 0.25, 0.25, FINE, MID)
        for c_ in kc: mirror_rect(v, c_ - 9, c_ + 9, MY0 + 4, MY1 - 4, frame=2.0)
        sconce(v, cx, 64)
    elif st == 'arched_alcove':
        r = (xb - xa) / 2; ys = H - CROWN - 6 - r
        pts = [(xa - 4, 0), (xa - 4, ys)] + [(cx + (r + 4) * math.cos(math.radians(180 - t)), ys + (r + 4) * math.sin(math.radians(180 - t))) for t in range(0, 181, 6)] + [(xb + 4, ys), (xb + 4, 0)]
        P(v, pts, HEAVY, close=False)
        mirror_arched(v, cx - 14, cx + 14, MY0, min(MY1 + 10, ys + r - 4))
        for x in (cx - 19, cx + 19): sconce(v, x, 64)
    elif st == 'backlit_strip':
        mirror_rect(v, xa + 2, xb - 2, MY0, MY1, frame=0.5, lit=True)
        L(v, (xa + 2, MY1 + 3), (xb - 2, MY1 + 3), FINE, LIGHT, '[1.5 1] 0')
    elif st == 'towers_full':
        for c_ in kc: mirror_rect(v, c_ - 9, c_ + 9, MY0, MY1, frame=2.5)
        sconce(v, cx, 64, 'shaded')
    elif st == 'threeway_bench':
        mirror_rect(v, cx - 11, cx + 11, MY0, MY1 + 4, frame=2.0, lit=True)
        mirror_rect(v, cx - 22.5, cx - 12, MY0 + 4, MY1, frame=1.5); mirror_rect(v, cx + 12, cx + 22.5, MY0 + 4, MY1, frame=1.5)
    # upper above the vanity (where the mirror does not run to the ceiling)
    if st in ('arched_towers', 'hollywood', 'towers_full', 'backlit_strip', 'round_fluted', 'threeway_bench', 'skirted_triptych'):
        for i in range(2): door(v, xa + i * (xb - xa) / 2, xa + (i + 1) * (xb - xa) / 2, 92, H - CROWN, 'fluted' if st == 'round_fluted' else 'shaker', 'L' if i % 2 == 0 else 'R')
    # the freed wall each side: jewelry towers, or tall storage (drawers under full-height doors), or full-height mirror doors
    for f0, f1 in ((0, xa - (4 if st == 'arched_alcove' else 0)), (xb + (4 if st == 'arched_alcove' else 0), nN)):
        if f1 - f0 < 6: continue
        nb = max(1, round((f1 - f0) / 22)); bw = (f1 - f0) / nb
        if st in ('arched_towers', 'towers_full', 'arched_alcove'):
            toe(v, f0, f1)
            for i in range(nb):
                g0, g1 = f0 + i * bw, f0 + (i + 1) * bw
                drawers(v, g0, g1, 4, 30, 3, 'bar')
                cubbies(v, g0 + 1, g1 - 1, 31, H - CROWN - 1, 1, 6, s['n'] + int(g0), back=GLOW, bags=False)
                for j in range(1, 6):
                    y = 31 + j * (H - CROWN - 32) / 6
                    R(v, g0 + 3, y + 0.8, g1 - 3, y + 2.0, FINE, LIGHT)            # jewelry trays
            glass_door_grid(v, f0, f1, 31, H - CROWN, nb)
        else:
            kind = {'round_fluted': 'fluted', 'mirror_wall': 'mirror', 'backlit_strip': 'slab', 'mirror_sconces': 'mirror', 'threeway_bench': 'mirror'}.get(st, 'shaker')
            toe(v, f0, f1)
            for i in range(nb):
                g0, g1 = f0 + i * bw, f0 + (i + 1) * bw
                drawers(v, g0, g1, 4, 30, 2, 'edge' if kind == 'slab' else 'bar')
                door(v, g0, g1, 30, H - CROWN, kind, 'L' if i % 2 == 0 else 'R')
    v.text(v.X((xa + xb) / 2), v.Y(H) - 3, 'MAKEUP VANITY FOR TWO', 5.0, INK, align='c')

# ---------------------------------------------------------------- east wall (owner 11.09.26: "a place for our shoes ... like 32 pairs")
# Seen from the island: x 0 (north wall, at the left) to D (south wall). The east run: double hang to the chute, the chute in its own
# closed bay with an access door, long hang, then a full-height shoe tower at the south end, four pairs a shelf.
SHOE_W = 9.0                                         # shelf width per pair
SHOE_PITCH = [(14.0, 'boot'), (14.0, 'boot'), (11.0, 'heel'), (11.0, 'heel'), (11.0, 'heel'), (7.5, 'flat'), (7.5, 'flat'), (7.5, 'flat'), (7.5, 'flat')]
def east_bays(s):
    bw = (D - CH_Y1) / 2
    return {'dbl': (s['dN'], CH_Y0), 'chute': (CH_Y0, CH_Y1), 'long': (CH_Y1, CH_Y1 + bw), 'shoes': (CH_Y1 + bw, D)}

def shoe(v, cx, y, kind, c=MID):
    """One pair seen from the front, for size: two shoes."""
    for dx in (-2.1, 2.1):
        x = cx + dx
        if kind == 'boot': R(v, x - 1.6, y, x + 1.6, y + 12.0, FINE, c, fill=WHITE); L(v, (x - 1.6, y + 2.5), (x + 1.6, y + 2.5), FINE, c)
        elif kind == 'heel': P(v, [(x - 1.7, y + 1.2), (x + 1.7, y + 1.2), (x + 1.3, y + 6.5), (x - 1.3, y + 6.5)], FINE, c, fill=WHITE); L(v, (x, y), (x, y + 1.2), MED, c)
        else: C._ellipse(v, x, y + 1.4, 1.8, 1.4, FINE, c)

def shoe_tower(v, x0, x1, front, door_kind='shaker'):
    """Full-height lit shoe tower, pitched shelves with a heel rail; returns the number of pairs."""
    toe(v, x0, x1)
    R(v, x0, 4, x1, H - CROWN, OUTLINE, fill=GLOW if front != 'closed' else None)
    per = int((x1 - x0 - 2) // SHOE_W); y = 4.0; pairs = 0
    for pitch, kind in SHOE_PITCH:
        R(v, x0 + 0.75, y, x1 - 0.75, y + 0.75, FINE, fill=WHITE)                       # shelf edge
        L(v, (x0 + 1.2, y + 1.6), (x1 - 1.2, y + 1.6), FINE, MID)                         # heel rail
        L(v, (x0 + 1.0, y + pitch + 0.2), (x1 - 1.0, y + pitch + 0.2), FINE, LIGHT, '[1.5 1] 0')   # LED under the shelf above
        w = (x1 - x0) / per
        for i in range(per): shoe(v, x0 + (i + 0.5) * w, y + 0.75, kind)
        pairs += per; y += pitch + 0.75
    if front == 'glass': glass_door_grid(v, x0, x1, 4, H - CROWN, 2)
    return pairs

def east_wall(v, s):
    b = east_bays(s); nN = s['dN']
    R(v, D, 0, D + 6, H, HEAVY, fill=(0.3, 0.3, 0.3))                                 # the south wall, cut
    end_profile(v, 0, nN, label='NORTH RUN')
    crown_band(v, nN, D)
    a0, a1 = b['dbl']; R(v, a0, 0, a1, H - CROWN, OUTLINE); hanging(v, a0 + 1, a1 - 1, 80, 46, seed=s['n']); hanging(v, a0 + 1, a1 - 1, 40, 6, seed=s['n'] + 1)
    R(v, a0, 82, a1, 83.5, FINE, fill=WHITE); toe(v, a0, a1)
    c0, c1 = b['chute']                                                                # the chute: a closed bay, one access door at the intake
    door(v, c0, c1, 4, H - CROWN, s.get('east_door', 'shaker'), 'L', knob=False); toe(v, c0, c1)
    R(v, c0 + 2.3, 30, c1 - 2.3, 46, MED); L(v, (c1 - 4, 38), (c1 - 4, 41), OUTLINE)
    v.text(v.X((c0 + c1) / 2), v.Y(52), 'LAUNDRY CHUTE', 4.5, INK, align='c', bold=True)
    l0, l1 = b['long']; R(v, l0, 0, l1, H - CROWN, OUTLINE); hanging(v, l0 + 1, l1 - 1, 72, 8, seed=s['n'] + 2)
    R(v, l0, 74, l1, 75.5, FINE, fill=WHITE); R(v, l0, 90, l1, 91.25, FINE, fill=WHITE); toe(v, l0, l1)
    s0, s1 = b['shoes']
    n = shoe_tower(v, s0, s1, s.get('shoe_front', 'open'))
    v.text(v.X((s0 + s1) / 2), v.Y(H) - 3, 'SHOES, %d PAIRS' % n, 5.0, INK, align='c')
    v.text(v.X((a0 + l1) / 2), v.Y(H) - 3, 'HANGING AND THE CHUTE', 5.0, INK, align='c')
    return n

# ---------------------------------------------------------------- island, seen from the west aisle: x 0 (south end) to Li (north end)
def island_elev(v, s, Li):
    st = s['island']; TOP = 36.0; T = 1.5
    if st in ('fluted_round', 'curved'):
        R(v, 0, 0, Li, TOP - T, OUTLINE)
        for x in (5, Li - 5): L(v, (x, 0), (x, TOP - T), FINE, MID)
    if st == 'glass_drawers':
        toe(v, 0, Li); w = Li / 3
        for i in range(3): drawers(v, i * w, (i + 1) * w, 4, TOP - T - 6, 3, 'bar', leather=True)
        R(v, 0, TOP - T - 6, Li, TOP - T, OUTLINE, fill=GLOW); v.text(v.X(Li / 2), v.Y(TOP - T - 3) + 2, 'GLASS-TOP JEWELRY DRAWERS', 4.0, MID, align='c')
    elif st == 'waterfall':
        R(v, 0, 0, 2, TOP, OUTLINE, fill=STONE); R(v, Li - 2, 0, Li, TOP, OUTLINE, fill=STONE)
        R(v, 2, 0, Li - 2, 3, FINE, fill=PALE); w = (Li - 4) / 3
        for i in range(3): drawers(v, 2 + i * w, 2 + (i + 1) * w, 3, TOP - T, 4, 'edge')
    elif st == 'legs':
        for x in (2, Li - 4): R(v, x, 0, x + 2.2, 28, OUTLINE); C._ellipse(v, x + 1.1, 9, 1.4, 1.8, FINE)
        R(v, 0, 28, Li, TOP - T, OUTLINE); w = Li / 3
        for i in range(3): drawers(v, i * w + 1, (i + 1) * w - 1, 28.5, TOP - T - 0.5, 1, 'knob')
        R(v, 4.5, 8, Li - 4.5, 9.25, FINE, fill=WHITE); v.text(v.X(Li / 2), v.Y(4), 'OPEN SHELF FOR BOOTS', 4.0, MID, align='c')
    elif st == 'fluted_round':
        x = 5.6
        while x < Li - 5.4: L(v, (x, 4), (x, TOP - T - 0.5), FINE, LIGHT); x += 1.25
        R(v, 0, 0, Li, 4, FINE, fill=PALE)
        for y in (13, 22, 29): L(v, (5.5, y), (Li - 5.5, y), FINE, MID, '[2 1.5] 0')
        v.text(v.X(Li / 2), v.Y(17.5), 'PUSH-LATCH DRAWERS', 4.0, MID, align='c')
    elif st == 'brass_glass':
        toe(v, 0, Li); w = Li / 3
        for i in range(3): drawers(v, i * w, (i + 1) * w, 4, TOP - T - 7, 3, 'bar', leather=True)
        R(v, 0, TOP - T - 7, Li, TOP - T, OUTLINE, fill=GLOW); R(v, -0.5, TOP - T - 7.5, Li + 0.5, TOP - T - 7, FINE, fill=STONE)
        v.text(v.X(Li / 2), v.Y(TOP - T - 4) + 2, 'GLASS DISPLAY TOP, BRASS FRAME', 4.0, MID, align='c')
    elif st == 'lacquer_plinth':
        R(v, 3, 0, Li - 3, 4, FINE, fill=PALE); w = Li / 3
        for i in range(3): drawers(v, i * w, (i + 1) * w, 4, TOP - T, 4, 'edge')
        v.text(v.X(Li / 2), v.Y(1.5), 'MIRRORED PLINTH', 4.0, MID, align='c')
    elif st == 'curved':
        R(v, 5, 0, Li - 5, 4, FINE, fill=PALE); w = (Li - 10) / 3
        for i in range(3): drawers(v, 5 + i * w, 5 + (i + 1) * w, 4, TOP - T, 3, 'bar')
    elif st == 'glass_top':
        R(v, 0, 0, Li, 3, FINE, fill=PALE); w = Li / 3
        for i in range(3): drawers(v, i * w, (i + 1) * w, 3, TOP - T - 5, 3, 'edge')
        R(v, 0, TOP - T - 5, Li, TOP - T, OUTLINE, fill=GLOW); v.text(v.X(Li / 2), v.Y(TOP - T - 2.5) + 2, 'VELVET TRAYS UNDER GLASS', 4.0, MID, align='c')
    elif st == 'bench_end':
        bl = 20.0
        toe(v, bl, Li); w = (Li - bl) / 2
        for i in range(2): drawers(v, bl + i * w, bl + (i + 1) * w, 4, TOP - T, 4, 'knob')
        R(v, 0, 0, bl, 18, OUTLINE); R(v, 0.5, 14, bl - 0.5, 18, MED, fill=PALE); v.text(v.X(bl / 2), v.Y(8), 'BENCH', 4.0, MID, align='c')
    elif st == 'oval_glass':
        R(v, 6, 0, Li - 6, 3, FINE, fill=PALE); w = (Li - 12) / 3
        for i in range(3): drawers(v, 6 + i * w, 6 + (i + 1) * w, 3, TOP - T - 5, 3, 'edge')
        R(v, 6, TOP - T - 5, Li - 6, TOP - T, OUTLINE, fill=GLOW)
        for x in (0, Li - 6): R(v, x, 0, x + 6, TOP - T, FINE, LIGHT)
    top_x0 = 0 if st != 'bench_end' else 20.0
    stone_top(v, top_x0, Li, TOP - T, T, 0.75 if st != 'waterfall' else 0)
    chand_kind = s['chand']
    v.text(v.X(Li / 2), v.Y(TOP + T) - 3, 'ISLAND OF DRAWERS', 5.0, INK, align='c')

# ---------------------------------------------------------------- plan (page points; inches x east, y south)
class PV:
    def __init__(self, page, ox, oy, k): self.p, self.ox, self.oy, self.k = page, ox, oy, k
    def P(self, x, y): return fitz.Point(self.ox + x * self.k, self.oy + y * self.k)
    def rect(self, x0, y0, x1, y1, w=0.5, c=INK, fill=None, d=None):
        sh = self.p.new_shape(); sh.draw_rect(fitz.Rect(self.P(x0, y0), self.P(x1, y1))); sh.finish(color=c, width=w, fill=fill, dashes=d); sh.commit()
    def line(self, a, b, w=0.5, c=INK, d=None):
        sh = self.p.new_shape(); sh.draw_line(self.P(*a), self.P(*b)); sh.finish(color=c, width=w, dashes=d); sh.commit()
    def poly(self, pts, w=0.5, c=INK, fill=None, d=None, close=True):
        sh = self.p.new_shape(); sh.draw_polyline([self.P(*q) for q in pts]); sh.finish(color=c, width=w, fill=fill, dashes=d, closePath=close); sh.commit()
    def circle(self, cx, cy, r, w=0.5, c=INK, fill=None, d=None):
        sh = self.p.new_shape(); sh.draw_circle(self.P(cx, cy), r * self.k); sh.finish(color=c, width=w, fill=fill, dashes=d); sh.commit()
    def arc(self, cx, cy, r, a0, a1, w=0.4, c=INK, d=None):
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
        self.poly(pts, w, c, None, d, close=False)

def shape_pts(shape, x0, y0, x1, y1):
    if shape == 'rect': return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    w = x1 - x0; r = w / 2; cx = (x0 + x1) / 2
    if shape == 'racetrack':
        top = [(cx + r * math.cos(math.radians(180 + t)), y0 + r + r * math.sin(math.radians(180 + t))) for t in range(0, 181, 10)]
        bot = [(cx + r * math.cos(math.radians(t)), y1 - r + r * math.sin(math.radians(t))) for t in range(0, 181, 10)]
        return top + bot
    cy = (y0 + y1) / 2; ry = (y1 - y0) / 2
    return [(cx + r * math.cos(math.radians(t)), cy + ry * math.sin(math.radians(t))) for t in range(0, 360, 10)]

WALL_T = 5.0
def plan(page, ox, oy, k, s, labels=True):
    """The closet in plan: walls, door 19, the chute, the three runs, the island, the stools, the fixture over the island."""
    pv = PV(page, ox, oy, k); G = (0.32, 0.32, 0.32)
    for r in ((-WALL_T, -WALL_T, W + WALL_T, 0), (-WALL_T, 0, 0, D), (W, 0, W + WALL_T, D),
              (-WALL_T, D, DOOR_C - DOOR_W / 2, D + WALL_T), (DOOR_C + DOOR_W / 2, D, W + WALL_T, D + WALL_T)):
        pv.rect(*r, w=0.6, c=INK, fill=G)
    for sx, a0 in ((DOOR_C - DOOR_W / 2, 270), (DOOR_C + DOOR_W / 2, 180)):          # door 19: leaves swing into the closet
        hx = sx; leaf = DOOR_W / 2; tip = (hx + (leaf if a0 == 270 else -leaf), D)
        pv.line((hx, D), (hx, D - leaf), 0.6); pv.arc(hx, D, leaf, 270 if a0 == 270 else 270, 360 if a0 == 270 else 180, 0.35, MID)
    # runs
    dN = s['dN']; yv0, yv1 = vanity_span(s)
    pv.rect(0, 0, W, dN, 0.5, INK, fill=(0.96, 0.96, 0.96))                       # north: purse showcase
    pv.rect(W - DE, dN, W, D, 0.5, INK, fill=(0.96, 0.96, 0.96))                  # east: hanging, chute
    pv.rect(0, dN, DF, yv0, 0.5, INK, fill=(0.96, 0.96, 0.96)); pv.rect(0, yv1, DF, D, 0.5, INK, fill=(0.96, 0.96, 0.96))
    if s['west'] == 'arched_alcove': pv.rect(-3, yv0, DV - 3, yv1, 0.5, INK, fill=WHITE)
    else: pv.rect(0, yv0, DV, yv1, 0.5, INK, fill=WHITE)
    eb = east_bays(s); x = W - DE / 2
    pv.line((x, dN + 2), (x, CH_Y0 - 2), 0.35, MID, '[2 1.5] 0'); pv.line((x, eb['long'][0] + 2), (x, eb['long'][1] - 2), 0.35, MID, '[2 1.5] 0')   # rods
    s0_, s1_ = eb['shoes']; pv.line((W - DE, s0_), (W, s0_), 0.5)
    for f in (0.25, 0.5, 0.75): pv.line((W - DE + 2, s0_ + (s1_ - s0_) * f), (W - 2, s0_ + (s1_ - s0_) * f), 0.3, MID)   # shoe shelves
    pv.p.insert_text(pv.P(W - DE + 3, (s0_ + s1_) / 2 + 9.0), 'SHOES', fontsize=4.2, fontname='helv', rotate=90, color=INK)
    pv.line((W - DE, CH_Y0), (W, CH_Y0), 0.5); pv.line((W - DE, CH_Y1), (W, CH_Y1), 0.5)
    # chute shaft
    cx0 = W - CH_D; pv.rect(cx0, CH_Y0, W - 4.5, CH_Y1, 0.7, INK, fill=WHITE); pv.line((cx0, CH_Y0), (W - 4.5, CH_Y1), 0.35); pv.line((cx0, CH_Y1), (W - 4.5, CH_Y0), 0.35)
    # two 24" seats at the 4'-0" vanity, or one bench
    if s['west'] == 'threeway_bench': pv.rect(DV + 2, yv0 + 2, DV + 18, yv1 - 2, 0.4, MID, d='[2 1.5] 0')
    else:
        for c_ in (yv0 + 12, yv1 - 12): pv.circle(DV + 9, c_, 7.5, 0.4, MID, d='[2 1.5] 0')
    # island
    x0, y0, x1, y1 = island_box(s)
    pv.poly(shape_pts(s['shape'], x0, y0, x1, y1), 0.7, INK, fill=WHITE)
    if s['island'] == 'bench_end': pv.line((x0, y1 - 20), (x1, y1 - 20), 0.4, MID)
    pv.circle((x0 + x1) / 2, (y0 + y1) / 2, 14, 0.4, MID, d='[2 1.5] 0')
    return pv, (x0, y0, x1, y1)

# ---------------------------------------------------------------- one option band
NS = 6.6; NLH = 10.5
def wrap(t, size, width):
    out = []; cur = ''
    for w in t.split():
        if _FR.text_length((cur + ' ' + w).strip(), fontsize=size) > width and cur: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    return out + ([cur] if cur else [])

def flag(sh, x, y, t):
    w = _FB.text_length(t, fontsize=8.0) + 12
    sh.p.draw_rect(fitz.Rect(x, y - 10, x + w, y + 4), color=None, fill=INK, width=0)
    sh.p.insert_text((x + 6, y), t, fontsize=8.0, fontname='cgb', color=(1, 1, 1))

def band(sh, cell, s):
    x0, y0, x1, y1 = cell
    E.title_bar(sh.p, sh.font, sh.fontname, cell, s['n'], 'OPTION %d: %s' % (s['n'], s['name']), 'SCALE: 3/8" TO 1\'-0"')
    kE = E.SCALES['3/8']; kP = 1.3
    # the text, across the top of the band
    tx = x0 + 14; tw = x1 - x0 - 28; ty = y0 + 32
    if s.get('rec'): flag(sh, tx, ty, 'RECOMMENDED'); ty += 18
    for t in wrap(s['text'], 7.4, tw): sh.text(tx, ty, t, 7.4, INK, raw=True); ty += 11.5
    ty += 5
    ib = island_box(s); Li = ib[3] - ib[1]
    stats = 'SHOES: %d PAIRS     16 HANDBAGS     VANITY %s WIDE, TWO SEATS     ISLAND %s x %s, AISLES 3\'-0" MIN.' % (
        len(SHOE_PITCH) * int((east_bays(s)['shoes'][1] - east_bays(s)['shoes'][0] - 2) // SHOE_W), E.ftin(s['vw']), E.ftin(ib[2] - ib[0]), E.ftin(Li))
    sh.text(tx, ty, 'COST  %s' % s['cost'], 8.0, INK, bold=True, raw=True); sh.text(tx + 80, ty, stats, 7.4, INK, bold=True, raw=True)
    ty += 8
    floor = max(ty + 340, (ty + 340 + y1 - 46) / 2)
    assert floor <= y1 - 44, ('band too short', s['n'])
    # left column: the plan over the island elevation
    cw_ = max(W * kP, Li * kE + 30) + 52 + W * kE + 50 + 2 * (D * kE + 50) + 10
    lx = x0 + max(22, (x1 - x0 - cw_) / 2)                                   # the views centered across the band
    pl_oy = floor - 95 - 22 - D * kP
    pv, ib = plan(sh.p, lx, pl_oy, kP, s)
    sh.text(lx - 4, pl_oy + D * kP + 17, 'PLAN', 6.0, INK, raw=True)
    spec = {'room': 'MASTER CLOSET', 'view': 'ISLAND', 'length': Li, 'ceiling': 36.0}
    vI = E.ElevationView(sh.p, sh.font, sh.fontname, (lx + 4, floor), kE, spec)
    island_elev(vI, s, Li)
    L(vI, (-4, 0), (Li + 4, 0), HEAVY); vI.dim_h(0, Li, floor + 12, E.snap_points([0, Li]))
    vI.dim_v(0, 36.0, vI.X(Li) + 14, E.snap_points([0, 36.0]))
    sh.text(lx + 4, floor + 34, 'ISLAND, FROM THE VANITY', 6.0, INK, raw=True)
    # north, west, east walls
    ox = lx + max(W * kP, Li * kE + 30) + 52
    vN = E.ElevationView(sh.p, sh.font, sh.fontname, (ox, floor), kE, {'room': 'MASTER CLOSET', 'view': 'NORTH', 'length': W, 'ceiling': H})
    north_wall(vN, s)
    L(vN, (0, 0), (W, 0), HEAVY); vN.dim_h(0, W, floor + 12, E.snap_points([0, DF, W - DE, W]))
    vN.dim_v(0, H, vN.X(W) + 14, E.snap_points([0, H]))
    sh.text(ox, floor + 34, 'NORTH WALL, FROM THE BATH', 6.0, INK, raw=True)
    ox2 = ox + W * kE + 50
    vW = E.ElevationView(sh.p, sh.font, sh.fontname, (ox2, floor), kE, {'room': 'MASTER CLOSET', 'view': 'WEST', 'length': D, 'ceiling': H})
    west_wall(vW, s)
    L(vW, (0, 0), (D, 0), HEAVY)
    yv0, yv1 = vanity_span(s)
    vW.dim_h(0, D, floor + 12, E.snap_points([0, D - yv1, D - yv0, D - s['dN'], D]))
    vW.dim_v(0, H, vW.X(D) + 14, E.snap_points([0, 30.0, H]))
    sh.text(ox2, floor + 34, 'WEST WALL, THE VANITY', 6.0, INK, raw=True)
    ox3 = ox2 + D * kE + 50
    vE = E.ElevationView(sh.p, sh.font, sh.fontname, (ox3, floor), kE, {'room': 'MASTER CLOSET', 'view': 'EAST', 'length': D, 'ceiling': H})
    n_ = east_wall(vE, s)
    L(vE, (0, 0), (D, 0), HEAVY)
    eb = east_bays(s)
    vE.dim_h(0, D, floor + 12, E.snap_points([0, s['dN'], CH_Y0, CH_Y1, eb['long'][1], D]))
    vE.dim_v(0, H, vE.X(D) + 22, E.snap_points([0, H]))
    sh.text(ox3, floor + 34, 'EAST WALL, SHOES AND THE CHUTE', 6.0, INK, raw=True)
    assert n_ >= 32, ('fewer than 32 pairs', s['n'], n_)
    assert vE.X(D) + 40 < x1, ('east view runs off the band', s['n'], vE.X(D), x1)
    assert pl_oy - 8 > ty, ('plan runs into the text', s['n'])

# ---------------------------------------------------------------- ID-330, the key plan and the brief
BRIEF = [
    ('THE BRIEF (OWNER 11.09.26)', [
        'NORTH WALL, SEEN FROM THE BATH THROUGH DOOR 19: A SHOWCASE FOR HANDBAGS, CABINETS OR DRAWERS BELOW.',
        'NORTH SHOWCASE HOLDS 16 HANDBAGS (OWNER: "WE REALISTICALLY ONLY HAVE 16"); THE REST OF THE WALL IS CLOSED STORAGE.',
        'WEST WALL: A MAKEUP VANITY 4\'-0" WIDE (OWNER), TWO PEOPLE SEATED SIDE BY SIDE; THE REST OF THE WALL STORAGE, TOWERS OR MIRROR.',
        'CENTER ISLAND: DRAWERS.',
        'EAST WALL: HANGING, AND THE LAUNDRY CHUTE, KEPT CLEAR WITH ITS OWN DOOR IN THE RUN.',
        'SHOES (OWNER: "LIKE 32 PAIRS"): A FULL-HEIGHT LIT SHOE TOWER AT THE SOUTH END OF THE EAST RUN, 36 PAIRS.']),
    ('THE ROOM, FROM FOR\'S A-202 AND A-206 (REV 1)', [
        '13\'-6-5/8" x 12\'-10-3/4" INSIDE, CEILING 9\'-6" (A-206).',
        'DOOR 19, A PAIR FROM THE MASTER BATH, CENTERED ON THE SOUTH WALL. NO WINDOW.',
        'CHUTE: A SHAFT ABOUT 18-1/2" SQUARE IN THE EAST RUN, 4\'-11" TO 6\'-6" FROM THE NORTH WALL. LAUNDRY CHUTE (OWNER CONFIRMED 11.09.26), DOOR KEPT CLEAR.',
        'FOR\'S RCP: CLOSET LIGHTING AT THE BUILT-INS, A FIXTURE CENTERED OVER THE ISLAND.']),
    ('WHAT EVERY OPTION KEEPS', [
        'CABINETS TO THE 9\'-6" CEILING, A 4-1/2" CROWN CONTINUOUS ACROSS THE RUNS (AS 1/ID-501).',
        'AISLES 3\'-0" MINIMUM AROUND THE ISLAND, 2\'-9" TO THE SOUTH WALL FOR THE DOOR LEAVES.',
        'EXACTLY 16 HANDBAG POSITIONS, ABOUT 16" TO 19" WIDE AND 14" TO 19" HIGH, 14" TO 16" DEEP; LED UNDER EVERY SHELF.',
        'VANITY 4\'-0" WIDE, TOP AT 30", ONE CONTINUOUS 48" KNEE SPACE: TWO 24" SEATS OR ONE BENCH. 24" A SEAT IS SNUG (30" IS COMFORTABLE).',
        'LIGHT AT THE FACE: SCONCES OR A LIT MIRROR, SIZED TO THE 4 FT TOP.',
        'ISLAND 3\'-0" HIGH, 3\'-6" WIDE, DRAWERS BOTH SIDES.',
        'EAST RUN, NORTH TO SOUTH: DOUBLE HANG, THE CHUTE IN ITS OWN CLOSED BAY WITH AN ACCESS DOOR AT THE INTAKE, LONG HANG, THE SHOE TOWER.',
        'SHOE TOWER 3\'-2" WIDE, NINE PITCHED LIT SHELVES WITH A HEEL RAIL, FOUR PAIRS EACH (9" A PAIR): 2 FOR BOOTS AT 14", 3 FOR HEELS AT 11", 4 FOR FLATS AT 7-1/2". THE TOP SHELVES TAKE A STEP STOOL.']),
    ('HOW TO CHOOSE', [
        'PICK THE NORTH WALL FIRST: IT IS WHAT YOU SEE FROM THE BATH, AND IT SETS THE STYLE.',
        'THEN THE VANITY: MIRRORS AND LIGHT DECIDE HOW MAKEUP LOOKS. A LIT MIRROR OR SCONCES EACH SIDE OF THE FACE IS BEST.',
        'PARTS MIX: ANY NORTH WALL CAN TAKE ANY VANITY OR ISLAND. MARK THE ONE YOU WANT, OR THE PIECES FROM SEVERAL.',
        'OPTION 1 IS RECOMMENDED: THE 16 BAGS BEHIND LIT GLASS, JEWELRY TOWERS EITHER SIDE OF THE VANITY, AND IT MATCHES THE HOUSE.'])]

def key_sheet(doc):
    import compose_plans as CP, keyclip as KC, base_rev1 as BR
    sh = Sheet(doc); sh.frame('MASTER CLOSET', 'SCALE: 3/4" TO 1\'-0"', ['MASTER CLOSET', 'KEY PLAN AND BRIEF'], 'ID-330', legend_rule=False)
    src = fitz.open(CP.BASE_KEY); sp = src[1]
    T = BR.transform(2)
    a = T(446.1 - 9, 832.0 - 9); b = T(690.0 + 9, 1064.2 + 40)
    clip_disp = fitz.Rect(a[0], a[1], b[0], b[1])
    u = clip_disp * sp.derotation_matrix; u.normalize()
    k = 4.0                                                      # 3/16 base -> 3/4"
    tw, th = clip_disp.width * k, clip_disp.height * k
    ax0, ay0, ax1, ay1 = FR.x0 + 6, FR.y0 + 24, TB_X - 10, FR.y1 - 6
    colx = ax1 - 640
    tx = max(ax0 + 90, ax0 + (colx - 40 - ax0 - tw) / 2); ty = ay0 + (ay1 - ay0 - th) / 2
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    sh.p.show_pdf_page(target, src, 1, clip=u, rotate=90)
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(2, ['W.I.C.'])), 'key plan clip'
    def O(xf, yf):                                                # FOR point -> sheet point
        d_ = T(xf, yf); return (target.x0 + (d_[0] - clip_disp.x0) * k, target.y0 + (d_[1] - clip_disp.y0) * k)
    def I(xi, yi): return O(446.1 + xi * 1.5, 832.0 + yi * 1.5)  # closet inches -> sheet point
    # zones
    def zone(x0, y0, x1, y1, t, rot=0):
        p0, p1 = I(x0, y0), I(x1, y1); r = fitz.Rect(p0, p1); r.normalize()
        sh.p.draw_rect(r, color=INK, width=0.9, dashes='[4 2] 0')
        sh.text(r.x0 + r.width / 2 - _FR.text_length(t, fontsize=8.5) / 2, r.y0 + r.height / 2 + 3, t, 8.5, INK, raw=True)
    s1 = SPECS[0]; yv0, yv1 = vanity_span(s1); ib = island_box(s1)
    zone(1, 1, W - 1, s1['dN'], 'PURSE SHOWCASE')
    zone(ib[0], ib[1], ib[2], ib[3], 'ISLAND')
    zone(1, yv0, DV, yv1, 'VANITY', rot=1)
    eb = east_bays(s1)
    zone(W - DE, s1['dN'] + 1, W - 1, CH_Y0 - 1, 'HANG', rot=1)
    zone(W - DE, eb['long'][0] + 1, W - 1, eb['long'][1] - 1, 'HANG', rot=1)
    zone(W - DE, eb['shoes'][0] + 1, W - 1, D - 1, 'SHOES', rot=1)
    p = I(W - CH_D - 2, (CH_Y0 + CH_Y1) / 2); sh.text(p[0] - _FR.text_length('CHUTE', fontsize=8.5) - 4, p[1] + 3, 'CHUTE', 8.5, INK, bold=True, raw=True)
    # dimensions: overall
    pa, pb = I(0, -14), I(W, -14)
    sh.line(pa, pb, 0.5, INK)
    for q in (pa, pb): sh.line((q[0], q[1] - 4), (q[0], q[1] + 4), 0.5); sh.line((q[0] - 2.5, q[1] + 2.5), (q[0] + 2.5, q[1] - 2.5), 0.8)
    lab = '13\'-6-5/8"'; sh.text((pa[0] + pb[0]) / 2 - _FR.text_length(lab, fontsize=9) / 2, pa[1] - 4, lab, 9, INK, raw=True)
    pa, pb = I(-14, 0), I(-14, D)
    sh.line(pa, pb, 0.5, INK)
    for q in (pa, pb): sh.line((q[0] - 4, q[1]), (q[0] + 4, q[1]), 0.5); sh.line((q[0] - 2.5, q[1] + 2.5), (q[0] + 2.5, q[1] - 2.5), 0.8)
    lab = '12\'-10-3/4"'; lw_ = 1.45 * _FR.text_length(lab, fontsize=9); cy_ = (pa[1] + pb[1]) / 2
    sh.p.draw_rect(fitz.Rect(pa[0] - lw_ / 2 - 3, cy_ - 9, pa[0] + lw_ / 2 + 3, cy_ + 6), color=None, fill=WHITE, width=0)
    sh.text(pa[0] - lw_ / 2, cy_ + 3, lab, 9, INK, raw=True)
    # brief column
    x = colx + 10; y = ay0 + 30; tw_ = ax1 - x - 10
    sh.text(x, y, 'MASTER CLOSET, TEN OPTIONS ON ID-331 TO ID-335', 14, serif=True, raw=True); y += 30
    for head, lines in BRIEF:
        sh.text(x, y, head, 9.5, INK, bold=True, raw=True); y += 16
        for t in lines:
            for i, ln in enumerate(wrap(t, 9.0, tw_ - 14)):
                if i == 0: sh.text(x, y, '-', 9.0, INK, raw=True)
                sh.text(x + 12, y, ln, 9.0, INK, raw=True); y += 13
        y += 12
    y += 4; sh.text(x, y, 'THE TEN', 9.5, INK, bold=True, raw=True); y += 16
    for s in SPECS:
        sh.text(x, y, '%d' % s['n'], 9.0, INK, raw=True); sh.text(x + 20, y, s['name'], 9.0, INK, bold=True, raw=True)
        sh.text(x + 160, y, s['cost'], 9.0, INK, raw=True); sh.text(x + 210, y, 'ID-%d' % (331 + (s['n'] - 1) // 2), 9.0, INK, raw=True); y += 13.5
    y += 18
    sh.line((x, y), (ax1 - 10, y), 0.5, INK); y += 24
    sh.text(x, y, 'OWNER PICK:', 14, serif=True, raw=True); sh.text(x + 160, y, 'OPTION ____     DATE ________', 14, serif=True, raw=True)
    assert y < ay1 - 10, ('ID-330 column runs off the sheet', y)
    # north arrow
    nx, ny = target.x1 - 24, target.y0 - 34
    sh.p.draw_circle(fitz.Point(nx, ny + 14), 9, color=INK, width=0.6)
    sh.p.draw_polyline([fitz.Point(nx, ny + 4), fitz.Point(nx + 5, ny + 20), fitz.Point(nx, ny + 16), fitz.Point(nx - 5, ny + 20), fitz.Point(nx, ny + 4)], color=INK, fill=INK, width=0.5)
    sh.text(nx - 3, ny - 1, 'N', 8, INK, bold=True, raw=True)
    return sh

def build():
    doc = fitz.open()
    key_sheet(doc)
    fx0, fy0, fx1, fy1 = FR.x0 + 6, FR.y0 + 6, TB_X - 6, FR.y1 - 6
    hh = (fy1 - fy0) / 2
    for i in range(5):
        sh = Sheet(doc)
        a, b = SPECS[2 * i], SPECS[2 * i + 1]
        sh.frame('MASTER CLOSET OPTIONS', 'SCALE: 3/8" TO 1\'-0"', ['MASTER CLOSET', 'OPTIONS %d AND %d' % (a['n'], b['n'])], 'ID-%d' % (331 + i), legend_rule=False)
        band(sh, (fx0, fy0, fx1, fy0 + hh), a)
        band(sh, (fx0, fy0 + hh, fx1, fy1), b)
    import idd_sheet as I_
    if hasattr(I_, 'finish_scales'): I_.finish_scales(doc)
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, len(doc), 'sheets')

if __name__ == '__main__':
    build()
