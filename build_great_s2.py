"""Great room fireplace wall, ten variations (owner 11.03.26: "my wife likes the floor to ceiling bookshelf look, I'm worried about it looking
too busy, give me 10 different variations, my preference is simple"). ID-751 S2 puts all ten side by side at 1/8" ordered from quietest to
busiest; ID-751 S3 to S5 draw them at 1/4" with notes, plus what makes shelving calm and what the pick decides.
Same room, same breast, same fireplace, same TV height as ID-751 to ID-755 (build_great.py). Books are drawn for scale only.
Output: 261105.HD102.LivingRoomStudy2.pdf"""
import math, random
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT
from build_kitchen import tag, para_block
import build_great as G
from build_great import (RD, H, B0, B1, CX, BELT0, BELT1, FF2, BOX_TOP, CAB_H, TOP_T, CRG, ART_B, ART_W, ART_H, WHITE, ISSUE, FRAME, FB_W, LEG)

OUT = '/home/claude/flrwork/261105.HD102.LivingRoomStudy2.pdf'
E.SCALES['1/8'] = 9.0 / 12
BOOK = (0.55, 0.55, 0.55); BACK = (0.86, 0.86, 0.86)
CASE_TOP = G.CL_HEAD                       # full-height cases stop at the window head line (20'-10"), a plain frieze and the crown above
SIDE = 1.5                                 # case side and upright
SURF = [0.0]                               # inches of book-bearing surface drawn in the current view (openings x clear width)

def books(v, a, b, y, h, density, seed):
    """Books and a few objects on one shelf, for scale: density is the share of the shelf filled with spines."""
    rnd = random.Random(seed); x = a + 1.0
    while x < b - 4:
        if rnd.random() < density:
            run = rnd.uniform(6, 14)
            if rnd.random() < 0.18 and h > 6:   # a short horizontal stack
                sw = min(run, 10, b - 1 - x)
                for i in range(3):
                    C._rect(v, x, y + i * 1.4, x + sw, y + (i + 1) * 1.4, C.FINE, BOOK)
                x += sw + rnd.uniform(1, 3); continue
            end = min(b - 1, x + run)
            while x < end - 0.8:
                bw = rnd.uniform(0.8, 1.7); bh = min(h - 1.2, rnd.uniform(7.5, 11.5))
                C._rect(v, x, y, x + bw, y + bh, C.FINE, BOOK); x += bw
            x += rnd.uniform(1.5, 4)
        else:
            gap = rnd.uniform(5, 14)
            if rnd.random() < 0.35 and h > 9 and x + 6 < b - 1:   # an object: a vase or a box
                if rnd.random() < 0.5: C._ellipse(v, x + 3, y + 3.5, 2.6, 3.5, C.FINE, BOOK); C._rect(v, x + 2.2, y + 7, x + 3.8, y + 8.5, C.FINE, BOOK)
                else: C._rect(v, x + 0.5, y, x + 6, y + 4, C.FINE, BOOK)
            x += gap

def bay_shelves(v, a, b, y0, y1, pitch, thick, density, seed, back=False):
    """Open shelving between y0 and y1 at about `pitch`, shelf `thick`, the back toned or not, books on each shelf. Returns the shelf count."""
    if back: C._rect(v, a, y0, b, y1, 0.3, BACK, fill=BACK)
    n = max(1, int(round((y1 - y0) / pitch)))
    p = (y1 - y0) / n; SURF[0] += n * (b - a)
    for i in range(n):
        yb = y0 + i * p + (thick if i else 0)
        if i: C._rect(v, a, y0 + i * p, b, y0 + i * p + thick, C.MED, fill=WHITE); C.shadow(v, a, b, y0 + i * p)
        if density: books(v, a, b, yb, p - (thick if i else 0), density, seed + i)
    return n - 1

def case(v, a, b, y0, y1, bays, pitch, thick, density, seed, back=False):
    """A bookcase between a and b: sides and uprights, open bays, shelves, books. Returns the shelf count."""
    C._rect(v, a, y0, b, y1, C.OUTLINE)
    inner = (a + SIDE, b - SIDE); w = (inner[1] - inner[0] - SIDE * (bays - 1)) / bays; n = 0
    for i in range(bays):
        x0 = inner[0] + i * (w + SIDE)
        n += bay_shelves(v, x0, x0 + w, y0, y1, pitch, thick, density, seed + 10 * i, back)
        C._line(v, (x0, y0), (x0, y1), C.MED)
        if i: C._rect(v, x0 - SIDE, y0, x0, y1, C.MED, fill=WHITE)
    C._line(v, (b - SIDE, y0), (b - SIDE, y1), C.MED)
    return n

def stacked_case(v, a, b, bays, pitch, thick, density, seed, back=False, lower=True):
    """Full-height shelving in three stories so the belt course and the gallery cap run through it: cabinet top to the belt, belt to the cap
    (the fascia band), the cap to the case top. Returns the shelf count."""
    n = 0
    if lower: n += case(v, a, b, CAB_H + TOP_T, BELT0, bays, pitch, thick, density, seed, back)
    n += case(v, a, b, BELT1, FF2 - 1.5, bays, pitch, thick, density * 0.8, seed + 3, back)
    n += case(v, a, b, FF2, CASE_TOP, bays, pitch, thick, density, seed + 5, back)
    return n

def base_cab(v, a, b):
    K.toe(v, a, b); K.door_pair_cab(v, a, b - a, K.TOE, CAB_H)
    C._rect(v, a, CAB_H, b, CAB_H + TOP_T, C.OUTLINE, fill=WHITE); C.shadow(v, a, b, CAB_H)

def glass_doors(v, a, b, y0, y1, mid, pulls=True):
    """Inset glass inside the case sides, two leaves wide and two tiers high, the tiers meeting on the shelf at `mid` (doors when pulls=True,
    removable panes held by stop beads otherwise): 3 in. stiles and rails, a 4 in. bottom rail, opaque in front of the books, glass edge, glint."""
    dw = (b - a) / 2; ST = 3.0; units = []
    for j in range(2):
        dx0, dx1 = a + j * dw + 0.125, a + (j + 1) * dw - 0.125
        for t, (ya, yb) in enumerate(((y0, mid - 0.125), (mid + 0.125, y1))):
            br = 4.0 if t == 0 else ST
            for r in ((dx0, ya, dx0 + ST, yb), (dx1 - ST, ya, dx1, yb), (dx0, ya, dx1, ya + br), (dx0, yb - ST, dx1, yb)):
                C._rect(v, *r, C.MED, fill=WHITE)
            C._rect(v, dx0, ya, dx1, yb, C.MED); C._rect(v, dx0 + ST, ya + br, dx1 - ST, yb - ST, C.FINE, MID)
            C._line(v, (dx0 + ST + 3, yb - ST - 6), (dx0 + (dx1 - dx0) * 0.55, ya + (yb - ya) * 0.45), C.FINE, C.PALE)
            if pulls:
                px = dx1 - 1.5 if j == 0 else dx0 + 1.5; py = ya + 6 if t == 1 else yb - 8
                C._line(v, (px, py - 3), (px, py + 3), C.OUTLINE)
            units.append((dx1 - dx0, yb - ya))
    return units

def mid_shelf(y0, y1, pitch):
    """The shelf line nearest the middle of a case section (where the mid rail goes)."""
    n = max(1, int(round((y1 - y0) / pitch))); p = (y1 - y0) / n
    return min((y0 + i * p + 0.75 for i in range(1, n)), key=lambda y: abs(y - (y0 + y1) / 2))

def _rungs(rail_y, shelf_pitch=None, shelf_thick=2.0):
    """Rung heights, evenly spaced at about 12", placed so no rung lands on a shelf or the cabinet top (review 11.09.26)."""
    bands = []
    if shelf_pitch:
        y0, y1 = CAB_H + TOP_T, BELT0; n = max(1, int(round((y1 - y0) / shelf_pitch))); p = (y1 - y0) / n
        bands = [(CAB_H, CAB_H + TOP_T)] + [(y0 + i * p, y0 + i * p + shelf_thick) for i in range(1, n)]
    best = None
    for q10 in range(110, 131):
        q = q10 / 10.0
        for s10 in range(80, 141, 2):
            st = s10 / 10.0; ys = []; y = st
            while y < rail_y - 6.0: ys.append(y); y += q
            clr = min((min(abs(y - a), abs(y - b)) if not (a - 0.7 <= y <= b + 0.7) else -1.0 for y in ys for a, b in bands), default=9.0)
            key = (clr, -abs(q - 12.0))
            if best is None or key > best[0]: best = (key, ys)
    return best[1]

def ladder(v, rail_y=123.5, shelf_pitch=None, shelf_thick=2.0):
    """A brass rail on the belt course of each flank, one rolling ladder (it lifts off to cross the breast), parked at the north wall."""
    for a, b in ((0.5, B0 - 0.5), (B1 + 0.5, RD - 0.5)): C._rect(v, a, rail_y, b, rail_y + 1.25, C.MED, fill=WHITE)
    x0, x1 = 3.0, 21.0
    for y in _rungs(rail_y, shelf_pitch, shelf_thick): C._rect(v, x0 + 1.5, y - 0.625, x1, y + 0.625, C.MED, fill=WHITE)   # rungs masked
    for x in (x0, x1): C._rect(v, x, 0.5, x + 1.75, rail_y + 3, C.OUTLINE, fill=WHITE)   # stiles masked, drawn over the rung ends
    C._rect(v, x0 - 0.5, rail_y + 1.25, x1 + 2.25, rail_y + 3.0, C.MED, fill=WHITE)      # hook over the rail

def arched_niche(v, a, b, seed):
    """One arched book niche over the cabinet: 6 in. margins, springing at 7'-6", three shelves."""
    w = b - a - 12; x = a + 6; spring = 90.0; y0 = CAB_H + TOP_T + 4
    r = w / 2; cx = x + r
    arc = [(cx - r * math.cos(math.pi * i / 30), spring + r * math.sin(math.pi * i / 30)) for i in range(31)]
    C._poly(v, [(x, y0), (x, spring)] + arc + [(x + w, spring), (x + w, y0)], C.OUTLINE, close=True)
    for i, y in enumerate((y0, 56.0, 74.0)):
        if i: C._rect(v, x, y, x + w, y + 1.25, C.MED, fill=WHITE); C.shadow(v, x, x + w, y)
        books(v, x, x + w, y + (1.25 if i else 0), 16, 0.4, seed + i); SURF[0] += w

def wall(v, spec):
    """The east wall per a variation spec: flank style, breast finish, art, ladder. Returns the note text; records shelf counts in spec."""
    L = RD; f = spec['flank']; marble = spec.get('breast') == 'marble'
    G.floor_line(v, 0, L); shelves = 0; SURF[0] = 0.0
    if marble:
        C.stone_slab(v, B0, B1, 0, H - CRG, seams=(CX,))
        for y in (BELT0, FF2): C._line(v, (B0, y), (B1, y), C.FINE, C.MID)   # six slabs in three rows, seams on the belt and cap lines
    else:
        if f == 'library': shelves += stacked_case(v, B0, B1, 2, spec['pitch'], 1.5, spec['density'], 90, spec.get('back', False), lower=False)
        if spec.get('shaft') != 'plain': G.belt(v, B0, B1); G.cap(v, B0, B1)   # the owner's pick: the breast one plane, nothing across it
        C.base(v, B0, CX - FB_W / 2 - LEG); C.base(v, CX + FB_W / 2 + LEG, B1)
    for x in (B0, B1): C._line(v, (x, 0), (x, H - CRG), C.OUTLINE)
    C._line(v, (B1 - 0.75, 0), (B1 - 0.75, H - CRG), C.FINE, LIGHT)
    G.mantel(v, CX, 'C' if marble else 'B'); G.tv_niche(v, CX)
    if spec.get('art'): C.art(v, CX, ART_B + ART_H / 2, ART_W, ART_H)
    for side, (a, b) in enumerate(((0, B0), (B1, L))):
        sd = 7 * side + 3
        if f == 'panel':
            G.flank(v, a, b, 'B')
        elif f == 'arch':
            base_cab(v, a, b); arched_niche(v, a, b, 40 + sd); shelves += 2; G.box(v, a + 4, b - 4, FF2 + 4, BOX_TOP)
        elif f == 'belt':
            base_cab(v, a, b); shelves += case(v, a, b, CAB_H + TOP_T, BELT0, 1, 17.75, 1.5, 0.5, 60 + sd); G.box(v, a + 4, b - 4, FF2 + 4, BOX_TOP)
        elif f == 'lowopen':
            base_cab(v, a, b); shelves += case(v, a, b, CAB_H + TOP_T, BELT0, 1, 17.75, 1.5, 0.5, 70 + sd)
            G.box(v, a + 4, b - 4, BELT1 + 4, FF2 - 5.5)
            w2 = (b - a - 12) / 2; h2 = (BOX_TOP - FF2 - 12) / 2   # a 2 x 2 grid of picture-frame boxes, the case behind closed
            for i in range(2):
                for j in range(2): G.box(v, a + 4 + i * (w2 + 4), a + 4 + i * (w2 + 4) + w2, FF2 + 4 + j * (h2 + 4), FF2 + 4 + j * (h2 + 4) + h2)
        elif f == 'full' and spec.get('mid') == 'panel':     # owner pick 11.09.26: option 7 with option 8's panel in the band (the wainscot break)
            base_cab(v, a, b)
            shelves += case(v, a, b, CAB_H + TOP_T, BELT0, spec['bays'], spec['pitch'], spec['thick'], spec['density'], 20 + sd, spec.get('back', False))
            G.box(v, a + 4, b - 4, BELT1 + 4, FF2 - 5.5)
            shelves += case(v, a, b, FF2, CASE_TOP, spec['bays'], spec['pitch'], spec['thick'], spec['density'], 25 + sd, spec.get('back', False))
        elif f in ('full', 'library'):
            base_cab(v, a, b); shelves += stacked_case(v, a, b, spec['bays'], spec['pitch'], spec['thick'], spec['density'], 20 + sd, spec.get('back', False))
        elif f == 'glass':
            base_cab(v, a, b)
            shelves += case(v, a, b, CAB_H + TOP_T, BELT0, 1, 17.75, 1.5, 0.45, 80 + sd)
            glass_doors(v, a + SIDE, b - SIDE, CAB_H + TOP_T + 0.25, BELT0 - 0.25, mid_shelf(CAB_H + TOP_T, BELT0, 17.75))
            G.box(v, a + 4, b - 4, BELT1 + 4, FF2 - 5.5)
            shelves += case(v, a, b, FF2, CASE_TOP, 1, 19.2, 1.5, 0.45, 85 + sd)
            glass_doors(v, a + SIDE, b - SIDE, FF2 + 0.25, CASE_TOP - 0.25, mid_shelf(FF2, CASE_TOP, 19.2), pulls=False)
        G.belt(v, a, b); G.cap(v, a, b)
    if spec.get('ladder'): ladder(v, shelf_pitch=spec['pitch'] if spec.get('mid') == 'panel' else None, shelf_thick=spec.get('thick', 2.0))
    C.crown(v, 0, L, H, drop=CRG); G.ceiling(v, 0, L)
    G.poche(v, -4, 0, 0, H); G.poche(v, L, L + 4, 0, G.SOFFIT); G.poche(v, L, L + 4, G.SOFFIT, FF2); G.section(v, L, L + 4.0, FF2, G.GT + 2.0)
    spec['shelves'] = shelves; spec['feet'] = SURF[0] / 12
    return spec['note']

RULE = 'STYLING SHOWN FOR SCALE ONLY.'
BOOKS_NOTE = ' BOOKS AND OBJECTS SHOWN FOR SCALE.'
V = [
    dict(n=1, title='PANELED, NOTHING ABOVE THE TV', flank='panel', art=False,
         note='PANELED FLANKS OVER CLOSED BASE CABINETS, A PLAIN PLASTER BREAST WITH ONLY THE FIRE AND THE TV ON IT. THE SIMPLEST WALL. NO BOOKS.'),
    dict(n=2, title='PANELED, ART ABOVE THE TV', flank='panel', art=True,
         note='AS 1 WITH ONE ARTWORK IN THE UPPER STORY (S1 OPTION B, THE PILOT SHEETS ID-751 TO ID-755). NO BOOKS.'),
    dict(n=3, title='MARBLE BREAST, PANELED FLANKS', flank='panel', breast='marble', art=False,
         note='THE BREAST CLAD IN WS-01 TO THE CROWN, THE STONE IS THE DECORATION, PANELED FLANKS (S1 OPTION C, A SECOND SEAM). NO BOOKS.'),
    dict(n=4, title='ARCHED BOOK NICHES TO THE BELT', flank='arch', art=True,
         note='ONE ARCHED BOOK NICHE EACH SIDE OVER THE CABINETS WITH TWO SHELVES, A PANEL BOX ABOVE THE CAP, ART. THE BOOKS IN TWO FRAMED OPENINGS.'),
    dict(n=5, title='BOOKSHELVES TO THE BELT', flank='belt', art=True,
         note='OPEN SHELVES FROM THE CABINET TOP TO THE BELT, A PANEL BOX ABOVE THE CAP, ART (S1 OPTION A). HALF THE BOOKCASE LOOK.'),
    dict(n=6, title='OPEN BELOW, PANELED FRONTS ABOVE', flank='lowopen', art=True,
         note='OPEN SHELVES TO THE BELT, A STEP STOOL REACHES THEM ALL, PANELING IN FOUR BOXES ABOVE THE CAP, ART. BOOKS BELOW THE BELT ONLY.'),
    dict(n=7, title='FLOOR TO CEILING, TONAL (OWNER PICK)', short='FLOOR TO CEILING, TONAL', flank='full', bays=1, pitch=18.0, thick=2.0, density=0.35, back=False, art=False,
         mid='panel', shaft='plain', ladder=True,
         note='OWNER PICK 11.09.26. FLOOR TO CEILING SHELVES EACH SIDE: ONE WIDE BAY, 2" SHELVES ABOUT 18" ON CENTER, PAINTED THE WALL COLOR, A PANEL IN THE 10 FT BAND, A ROLLING LADDER, THE BREAST ONE PLANE, NO ART.'),
    dict(n=8, title='FLOOR TO CEILING BEHIND GLASS', flank='glass', art=False,
         note='FLOOR TO CEILING CASES BEHIND INSET GLASS, DOORS BELOW THE BELT, REMOVABLE PANES ABOVE THE CAP. THE BOOKS READ THROUGH GLASS, THE FRAMES KEEP THE WALL ORDERED. NO ART.'),
    dict(n=9, title='FLOOR TO CEILING LIBRARY, LADDER (YL)', flank='full', bays=2, pitch=13.0, thick=1.25, density=0.7, back=True, art=True, ladder=True,
         note='YL\'S LOOK: TWO BAYS EACH SIDE, 13" SHELF SPACING, TONED BACKS, FULLY STOCKED, A ROLLING LADDER, ART OVER THE TV.'),
    dict(n=10, title='THE LIBRARY WALL', flank='library', bays=2, pitch=13.0, thick=1.25, density=0.7, back=True, art=False, ladder=True,
         note='SHELVES ON THE FLANKS AND ACROSS THE BREAST ABOVE THE BELT, THE WHOLE WALL BOOKS. THE BUSIEST, SHOWN SO YOU CAN SEE THE ENDPOINT.'),
]
STOCKED = dict(n=11, title='7 FULLY STOCKED, FOR COMPARISON', flank='full', bays=1, pitch=18.0, thick=2.0, density=0.7, back=False, art=False, note='',
               mid='panel', shaft='plain', ladder=True)

DETAIL = {
    1: 'WP-01 PICTURE-FRAME PANELING OVER 30" CLOSED BASE CABINETS WITH A WS-01 TOP, ONE BOX BELOW THE BELT AND ONE ABOVE THE CAP. THE BREAST IS PLASTER WITH ONLY THE FIREPLACE AND THE TV ON IT: '
       '13\'-10-1/4" OF PLASTER ABOVE THE TV NICHE, CROSSED ONLY BY THE BELT AND THE CAP. NO BOOKS, THE LEAST MILLWORK OF THE TEN. THE RISK: THE UPPER BREAST CAN READ EMPTY IN A 22\'-10" ROOM. '
       'WASH IT WITH LIGHT FROM THE CEILING, OR GO TO 2 OR 3.',
    2: 'AS 1 WITH ONE ARTWORK 4\'-8" x 5\'-10" ON THE BREAST IN THE UPPER STORY, ITS TOP AT 20\'-6", CENTER 17\'-7" (ABOUT THE GALLERY\'S EYE LEVEL). THE BELT COURSE AND THE CAP KEEP THE ART AND THE TV '
       'FROM STACKING. THIS IS S1 OPTION B, AND THE PILOT SHEETS ID-751 TO ID-755 ARE DRAWN WITH IT. NO BOOKS.',
    3: 'THE BREAST CLAD IN WS-01 FROM THE FLOOR TO THE CROWN, SIX SLABS BOOK-MATCHED IN PAIRS, SEAMS ON THE CENTERLINE AND ON THE BELT AND CAP LINES (10\'-0" AND 12\'-10"), THE LONGEST SLAB 10\'-0" (A JUMBO SLAB, VERIFY THE SIZE WITH THE YARD), ABOUT 150 SF. A SLIM MITERED FRAME AT THE FIREBOX AND A 2" '
       'LEDGE IN PLACE OF THE MANTEL, THE TV IN THE STONE, NO ART. PANELED FLANKS AS 1. THIS IS S1 OPTION C WITH A SECOND SEAM (S1\'S UPPER SLABS WERE 11\'-10" LONG). RANKED AFTER 2: THE VEINING RUNS THE FULL 22\'-10", ONE ARTWORK IS ONE OBJECT ON PLASTER. THE BIGGEST STONE ORDER. NO BOOKS.',
    4: 'ONE ARCHED NICHE EACH SIDE ABOVE THE CABINETS, 3\'-6-7/8" WIDE WITH 6" MARGINS, SPRINGING AT 7\'-6", THE ARCH TOP AT 9\'-3-7/16" UNDER THE BELT, TWO SHELVES AND THE NICHE BOTTOM '
       '(ABOUT 21 FT OF SHELF IN ALL), EVERY BOOK WITHIN REACH FROM THE FLOOR. A PANEL BOX ABOVE THE CAP, ART ON THE BREAST. THE BOOKS SIT IN TWO FRAMED OPENINGS AND THE REST OF THE WALL STAYS PAINTED.' + BOOKS_NOTE,
    5: 'S1 OPTION A WITH THE BOOKS DRAWN. OPEN SHELVES FROM THE CABINET TOP (2\'-7-1/4") TO THE BELT (10\'-0"), FOUR 1-1/2" SHELVES ABOUT 17-3/4" ON CENTER, EACH WITH A STEEL FLAT IN THE FRONT EDGE '
       'FOR THE 4\'-3-7/8" SPAN, ABOUT 43 FT OF SHELF COUNTING THE CABINET TOP (S1\'S 35 FT LEFT IT OUT), THE TOP SHELF SURFACE AT 8\'-7-3/4" (A STEP STOOL REACHES IT). A PANEL BOX ABOVE THE CAP, ART ON THE BREAST. '
       'HALF THE BOOKCASE LOOK, ALL OF IT USABLE.' + BOOKS_NOTE,
    6: 'OPEN SHELVES TO THE BELT AS 5 (ABOUT 43 FT, A STEP STOOL REACHES ALL OF THEM), A PANEL BOX IN THE BAND, THEN WP-01 PICTURE-FRAME PANELING IN FOUR BOXES EACH SIDE ABOVE THE CAP, ON THE CASE\'S '
       'FRONT PLANE SO THE BUILT-IN READS AS ONE PIECE OF FURNITURE FLOOR TO CEILING. THE CASE BEHIND THE PANELING IS CLOSED: NOTHING ABOVE 12\'-10" IS REACHABLE WITHOUT A LIFT, SO NOTHING IS STORED THERE. ART ON THE BREAST. '
       'EVERY BOOK IS WITHIN REACH AND NOTHING NEEDS A LIFT. THE UPPER STORY STAYS QUIET.' + BOOKS_NOTE,
    7: 'RECOMMENDED. FLOOR TO CEILING SHELVES BOTH SIDES, DRAWN TO BE CALM: ONE WIDE BAY EACH SIDE WITH NO UPRIGHTS, 2" SHELVES ABOUT 18" ON CENTER (8 A SIDE, EACH WITH A STEEL FLAT IN THE FRONT '
       'EDGE FOR THE 4\'-3-7/8" SPAN), CASES AND BACKS PAINTED THE WALL COLOR, STYLED ABOUT A THIRD FULL, CLOSED CABINETS BELOW, NO ART ON THE BREAST. THE BELT COURSE AND THE GALLERY CAP RUN THROUGH '
       'THE SHELVES SO THE ROOM STILL READS AS TWO STORIES. ABOUT 95 FT OF SHELF. CASE TOP AT THE CLERESTORY HEAD (20\'-10"), A PLAIN FRIEZE TO THE CROWN. THE UPKEEP: ABOUT 43 OF THE 95 FT ARE BELOW THE BELT, WITHIN A STEP STOOL. THE OTHER 52 FT, FROM THE BAND TO 20\'-10", ARE '
       'DISPLAY, STYLED ONCE AND DUSTED FROM A LIFT. STOCKED FULL IT LOOKS LIKE VIEW 11 ON ID-751 S5.' + BOOKS_NOTE,
    8: 'FLOOR TO CEILING CASES BEHIND INSET GLASS. BELOW THE BELT FOUR GLASS DOORS EACH SIDE, TWO WIDE AND TWO TIERS HIGH MEETING ON A SHELF LINE (ABOUT 2\'-1-3/4" WIDE, 2\'-11-7/8" AND 4\'-4-1/8" TALL, 3" STILES, '
       '2 HINGES ON THE SHORT LEAVES AND 3 ON THE TALL), 8 DOORS IN ALL. ABOVE THE CAP 8 PANES IN THE SAME PATTERN, HELD BY STOP BEADS AND TAKEN OUT FOR DUSTING FROM A LIFT. LOW-IRON TEMPERED GLASS. A PANEL BOX IN THE BAND BETWEEN. 1-1/2" SHELVES WITH STEEL FLATS, ABOUT 86 FT. THE BOOKS READ THROUGH THE GLASS, THE FRAMES KEEP THE '
       'WALL ORDERED AND THE DUST OUT. NO ART. THE COST: DOORS, HINGES, LOW-IRON GLASS, AND REFLECTIONS FROM THE WINDOWS.' + BOOKS_NOTE,
    9: 'YL\'S LOOK: FLOOR TO CEILING, TWO BAYS EACH SIDE WITH A CENTER UPRIGHT, 1-1/4" SHELVES ABOUT 13" ON CENTER (26 A SIDE, 2\'-1-3/16" SPANS), TONED BACKS THAT SET OFF EVERY OBJECT, FULLY '
       'STOCKED, ART ON THE BREAST. A BRASS RAIL ON THE BELT COURSE OF EACH FLANK AND ONE ROLLING LADDER, SHOWN PARKED AT THE NORTH WALL, THAT SLIDES CLEAR OF A CABINET DOOR IN USE AND LIFTS OFF TO CROSS THE BREAST. ABOUT 134 FT OF SHELF. THE CLASSIC '
       'LIBRARY, AND THE BUSIEST WALL THAT KEEPS THE BREAST FREE OF SHELVES.' + BOOKS_NOTE,
    10: 'SHELVES ON BOTH FLANKS AS 9 AND ACROSS THE BREAST ABOVE THE BELT (TWO BAYS, 3\'-3-3/4" SPANS IN 1-1/2" SHELVES), THE FIRE AND THE TV IN THE ONLY PLASTER LEFT, NO ART, THE LADDER AS 9 ON THE FLANKS (THE BREAST SHELVES BY LIFT). ABOUT '
        '194 FT OF SHELF. THE BREAST SHELVES SIT IN FRONT OF THE FLUE CHASE: VERIFY THE VENT ROUTE AND ITS CLEARANCES. THE ENDPOINT OF THE BOOKSHELF LOOK, SHOWN SO THE OTHER NINE CAN BE JUDGED '
        'AGAINST IT. NOT RECOMMENDED FOR A SIMPLE ROOM.' + BOOKS_NOTE,
    11: 'VIEW 7 FULLY STOCKED: THE SAME CASES, ONE BAY, 8 SHELVES A SIDE, TONAL BACKS AS 7, FILLED TO THE SAME DENSITY AS 9 AND 10. THIS IS HOW 7 LOOKS IF EVERY SHELF IS USED. AGAINST 9 WHAT IS LEFT '
        'IS THE GRID (NO CENTER UPRIGHT, 8 SHELF LINES A SIDE AGAINST 13), 2" SHELVES AGAINST 1-1/4", THE BACK COLOR, NO ART AND NO LADDER. IF THE SHELVES WILL BE FILLED, PICK 8 (GLASS) OR 6 (BOOKS BELOW THE BELT ONLY).' + BOOKS_NOTE,
}

def shelf_points(s):
    """Shelf spacing for the north flank's dimension string: case bottom, each board, case top (lower story, and the upper story for full height)."""
    def sect(y0, y1, pitch):
        n = max(1, int(round((y1 - y0) / pitch))); p = (y1 - y0) / n
        return [y0 + i * p for i in range(n + 1)]
    f = s['flank']
    if f == 'arch': return [CAB_H + TOP_T + 4, 56.0, 74.0, 90.0, 90.0 + (B0 - 12) / 2]
    if f in ('belt', 'lowopen'): return sect(CAB_H + TOP_T, BELT0, 17.75)
    if f == 'glass': return sect(CAB_H + TOP_T, BELT0, 17.75)
    if f == 'full' and s['bays'] == 1: return sect(CAB_H + TOP_T, BELT0, s['pitch'])
    return []

def draw(sh, cells, specs, scale, detail):
    """Views with one fixed top per sheet so every elevation in a row sits on the same floor line; 1/4 in. views carry dimensions."""
    k = E.SCALES[scale]
    texts = [(DETAIL[s['n']] if detail else s['note']) for s in specs]
    widths = [min(c[2] - c[0] - 16, 660) for c in cells]
    lines = [G.wrap(t, G.NOTE, w) for t, w in zip(texts, widths)]
    top = 26 + max(len(l) for l in lines) * G.NOTE_LH + 14
    for cell, s, ln_ in zip(cells, specs, lines):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, s['n'], s['title'] if detail else s.get('short', s['title']), 'SCALE: %s" TO 1\'-0"' % scale)
        spec = {'room': 'LIVING ROOM', 'view': s['title'], 'length': RD, 'ceiling': H}
        origin = E.fit_origin(cell, spec, k, top=top, margin_b=58)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        wall(v, s)
        v.text(v.X(0) - 8, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        if detail:
            v.dim_h(0, RD, v.Y(0) + 16, E.snap_points([0, B0, B1, RD]))
            pts = [0, CAB_H + TOP_T, BELT0, BELT1, FF2, H] + [CASE_TOP if s['flank'] in ('full', 'glass', 'library') else BOX_TOP]
            sp = shelf_points(s)
            if sp: v.dim_v(sp[0], sp[-1], v.X(0) - 22, E.snap_points(sp), side='l')
            v.dim_v(0, H, v.X(RD) + 30, E.snap_points(sorted(set(pts))))
        ny = cell[1] + 26
        for t in ln_: sh.text(cell[2] - 8, ny, t, G.NOTE, MID, align='r'); ny += G.NOTE_LH

REACH = {1: '-', 2: '-', 3: '-', 4: 'ALL FROM THE FLOOR', 5: 'A STEP STOOL', 6: 'A STEP STOOL, NOTHING ABOVE', 7: 'STEP STOOL BELOW THE BELT, LIFT FROM THE BAND UP',
         8: 'STEP STOOL BELOW THE BELT, LIFT ABOVE THE CAP', 9: 'LADDER TO THE BAND, LIFT ABOVE THE CAP', 10: 'LADDER ON THE FLANKS TO THE BAND, LIFT FOR THE REST'}
GLASS = {8: '8 DOORS, 8 PANES'}

def table(sh, x0, y, x1):
    """The ten side by side in numbers, counted from the drawn views."""
    cols = [('NO.', 0), ('OPTION', 22), ('SHELVES', 205), ('FT OF SHELF', 250), ('GLASS', 305), ('ART', 375), ('REACH', 405)]
    sh.text(x0, y, 'THE TEN IN NUMBERS, COUNTED FROM THE DRAWINGS, BOTH SIDES', 6.0, INK); y += 11
    for name, dx in cols: sh.text(x0 + dx, y, name, 5.2, MID)
    y += 3; sh.p.draw_line((x0, y), (x1, y), color=MID, width=0.4); y += 8
    for s in V:
        row = [str(s['n']), s['title'], str(s['shelves']) if s['shelves'] else '-', '%d' % round(s['feet']) if s['feet'] else '-', GLASS.get(s['n'], '-'),
               'YES' if s.get('art') else 'NO', REACH[s['n']]]
        for (name, dx), t in zip(cols, row): sh.text(x0 + dx, y, t, 5.2, INK if s['n'] == 7 else MID)
        y += 8.5
    y += 2
    sh.text(x0, y, 'THE SHELVES COLUMN COUNTS SHELF BOARDS, NOT CASE BOTTOMS. FT OF SHELF COUNTS EVERY SURFACE BOOKS STAND ON, THE CABINET TOP INCLUDED.', 5.2, MID)
    return y + 8

NOTES = [
    (True, 'WHAT MAKES FLOOR TO CEILING SHELVES CALM'), '',
    'THE BOOKSHELF LOOK AND A SIMPLE ROOM ARE NOT OPPOSITES. A BOOKCASE LOOKS BUSY FOR FIVE REASONS, AND EACH ONE CAN BE TURNED DOWN WITHOUT LOSING THE LOOK:',
    '1. COLOR. SHELVES PAINTED THE WALL COLOR (TONAL) RECEDE. A CONTRASTING OR DARK BACK MAKES EVERY OBJECT A SILHOUETTE (9, 10). TONAL IN 7.',
    '2. GRID. EVERY UPRIGHT AND EVERY SHELF IS A LINE: 8 SHELF LINES A SIDE IN ONE WIDE BAY (7) AGAINST 13 LINES AND A CENTER UPRIGHT (9).',
    '3. SPACING. 2" SHELVES ABOUT 18" ON CENTER READ AS ARCHITECTURE. THIN SHELVES 13" ON CENTER READ AS STORAGE. FEWER, THICKER, FURTHER APART.',
    '4. FILL. STOCKED FULL, ANY BOOKCASE IS A WALL OF SPINES (VIEW 11 IS 7 STOCKED FULL). STYLED AT ABOUT A THIRD (BOOKS IN GROUPS, A FEW OBJECTS, AIR BETWEEN) IT STAYS QUIET. THAT IS A HABIT THE DRAWING CANNOT PROMISE.',
    '5. COMPETITION. SHELVES, ART AND A TV ARE THREE THINGS TALKING. WITH FULL-HEIGHT SHELVES LEAVE THE BREAST PLAIN ABOVE THE TV (7, 8) AND LET THE SHELVES BE THE DECORATION.', '',
    'GLASS (8) CONTAINS THE FILL AND THE DUST: A FULL CASE STILL SHOWS ITS SPINES, BUT BEHIND A FRAME THAT KEEPS THE WALL ORDERED. THE COST IS DOORS, HARDWARE AND REFLECTIONS FROM THE WINDOWS.', '',
    'REACH: A STEP STOOL REACHES THE TOP SHELF BELOW THE BELT (ITS SURFACE AT 8\'-7-3/4" TO 8\'-8-1/4"). A ROLLING LADDER ON A RAIL AT THE BELT COURSE REACHES THE BAND ABOVE IT. ABOVE THE GALLERY CAP (12\'-10") THE SHELVES ARE DISPLAY ONLY, STOCKED AND '
    'DUSTED FROM A LIFT. KEEP THE BOOKS YOU READ BELOW THE BELT AND THE ONES YOU KEEP ABOVE THE CAP, OR USE 6 (BOOKS BELOW THE BELT ONLY).', '', '',
    (True, 'WHAT THE PICK DECIDES'), '',
    (True, 'RECOMMENDED: 7, THE QUIETEST WAY TO GET FLOOR TO CEILING BOOKSHELVES: ONE BAY EACH SIDE, TONAL, 2" SHELVES ABOUT 18" ON CENTER, CLOSED CABINETS BELOW, NO ART, THE BELT '
           'COURSE AND THE GALLERY CAP RUNNING THROUGH THE SHELVES SO THE ROOM STILL READS AS TWO STORIES. TWO HONEST COSTS: IT STAYS SIMPLE ONLY IF IT IS STYLED, NOT FILLED (VIEW 11), '
           'AND ONLY 43 OF ITS 95 FT ARE WITHIN A STEP STOOL. THE REST IS DISPLAY, DUSTED FROM A LIFT. IF THE SHELVES WILL BE FILLED, PICK 8 (GLASS) OR 6 (BOOKS BELOW THE BELT ONLY). IF A LIFT IS UNWANTED, 6 OR 5. '
           'GLASS CANNOT BE ADDED TO 7 LATER WITHOUT REBUILDING THE CASES (SHELF SETBACK, HINGE BLOCKING, THE BAND DETAIL).'), '',
    'THE SAME IN ALL TEN: THE BREAST 7\'-0" x 2\'-0" ON THE ROOM\'S CENTERLINE, THE GAS FIREPLACE, THE WS-01 MANTEL (A FRAME AND LEDGE IN 3), THE 75" ART-MODE TV AT 6\'-2-7/8", THE 14" DEEP BUILT-INS '
    '(BOOKS NEED 10" TO 12"), 30" CLOSED CABINETS BELOW (AV AND STORAGE), THE BELT COURSE AT 10\'-0" TO 10\'-8", THE CAP AT 12\'-10" AND THE 12" CROWN. NOTHING ON THE OTHER THREE WALLS CHANGES.', '',
    'WHAT CHANGES: THE MILLWORK (SHELF COUNTS AND GLASS IN THE TABLE BELOW), THE SHELF STRUCTURE (THE ONE-BAY SHELVES IN 5 TO 8 SPAN 4\'-3-7/8" AND GET A STEEL FLAT IN THE FRONT EDGE, 2" IN 7, 1-1/2" IN 5, 6 '
    'AND 8. THE NICHE SHELVES IN 4 SPAN 3\'-6-7/8" IN 1-1/4" WOOD. THE TWO-BAY SHELVES IN 9 AND 10 SPAN 2\'-1-3/16" IN 1-1/4" WOOD, THE BREAST SHELVES IN 10 SPAN 3\'-3-3/4" IN 1-1/2"), LIGHTING (LED IN THE SHELF FRONTS, A LIGHT AT THE CASE TOP, OR NONE), '
    'THE LADDER AND RAILS (9, 10), AND WHETHER ART HANGS ABOVE THE TV.', '',
    '4 TO 9 ALSO WORK WITH THE MARBLE BREAST OF 3. THE SHELVES START 21" FROM THE FIREBOX OPENING: VERIFY AGAINST THE UNIT\'S LISTED CLEARANCES TO COMBUSTIBLES. THIS STUDY SUPERSEDES ID-751 S1. '
    'ID-751 TO ID-755 SHOW 2 TODAY AND ARE REDRAWN WITH THE PICK.']

def build():
    doc = fitz.open()
    rev = (('0', ISSUE, 'ISSUED FOR REVIEW'),)
    sh = Sheet(doc); sh.frame('LIVING ROOM DESIGN STUDY - TEN FIREPLACE WALLS', 'SCALE: 1/8" TO 1\'-0"', ['DESIGN STUDY', 'FIREPLACE WALL, 10 OPTIONS'], 'ID-751 S2', revisions=rev, legend_rule=False)
    fx0, fy0, fx1, fy1 = FRAME
    sh.text(fx0 + 6, fy0 + 14, 'NUMBERED FROM QUIETEST (1) TO BUSIEST (10). THE SAME BREAST SIZE AND PLACE, FIREPLACE AND TV IN EVERY ONE (TV CENTER 6\'-2-7/8"). WHAT CHANGES IS WHAT HAPPENS EITHER SIDE '
            'OF THE BREAST AND ABOVE THE TV. ' + RULE + ' DETAIL AT 1/4" ON ID-751 S3 TO S5. THIS STUDY SUPERSEDES ID-751 S1.', 6.5, INK)
    sh.text(fx0 + 6, fy0 + 26, 'FOR A FLOOR TO CEILING BOOKSHELF LOOK THAT STAYS SIMPLE, SEE 7 (TONAL, ONE WIDE BAY, RECOMMENDED) AND 8 (BEHIND GLASS). 6 KEEPS THE BOOKS BELOW THE BELT. 9 AND 10 ARE THE FULL LIBRARY.', 6.5, INK)
    draw(sh, E.layout_cells((fx0, fy0 + 40, fx1, fy1), 5, 2), V, '1/8', False)
    for k, specs in enumerate((V[0:4], V[4:8], V[8:10] + [STOCKED])):
        sh = Sheet(doc); sh.frame('LIVING ROOM DESIGN STUDY - FIREPLACE WALL OPTIONS', 'SCALE: 1/4" TO 1\'-0"', ['DESIGN STUDY', 'FIREPLACE WALL, 10 OPTIONS'], 'ID-751 S%d' % (k + 3), revisions=rev, legend_rule=False)
        cells = E.layout_cells(FRAME, 2, 2)
        draw(sh, cells[:len(specs)], specs, '1/4', True)
        if len(specs) == 3:
            x0, y0, x1, y1 = cells[3]
            E.title_bar(sh.p, sh.font, sh.fontname, cells[3], 12, 'CALM SHELVES, AND WHAT THE PICK DECIDES', 'OWNER: SIMPLE, WITH FLOOR TO CEILING BOOKS')
            yend = para_block(sh, x0 + 8, y0 + 30, NOTES, x1 - x0 - 16)
            yend = table(sh, x0 + 8, yend + 14, x1 - 8)
            assert yend < y1 - 6, ('notes overrun', yend, y1)
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    idd_std.PROJECT['date'] = ISSUE
    build()


# ---------------------------------------------------------------- review set (owner 11.07.26): the ten options as ID-235 and ID-236 so Megan can pick
from idd_sheet import FREG, _FR, _FS, _FB
OUT_REVIEW = '/home/claude/flrwork/261107.HD102.FireplaceWallOptions.pdf'
E.SCALES['3/16'] = 13.5 / 12
# FOR REV 1: the wall is 16'-2" with 4'-7" flanks either side of the 7'-0" breast, as on ID-230 and ID-231 (the study was drawn on YL's 16'-1-3/4")
RD = 194.0; B0 = (RD - G.BW) / 2; B1 = B0 + G.BW; CX = RD / 2
G.RD, G.B0, G.B1, G.CX = RD, B0, B1, CX
NS, NLH = 6.0, 10.0                         # option text: prints 7.8 pt full size
TS, TLH = 10.0, 14.5                         # ID-236 reading text, raw full-size points

class RV(E.ElevationView):
    """Elevation view with plain words for a non-architect reader."""
    def text(self, x, y, s, *a, **k):
        return super().text(x, y, s.replace('ART, N.I.C.', 'ART BY OWNER'), *a, **k)

SHORT = {
    1: 'PAINTED PANELS EITHER SIDE OVER CLOSED CABINETS. THE CHIMNEY BREAST IS PLAIN PLASTER WITH ONLY THE FIRE AND THE TV. NO BOOKS, NO ART. THE SIMPLEST AND THE LEAST COST.',
    2: 'AS 1, WITH ONE LARGE ARTWORK HIGH ABOVE THE TV. NO BOOKS.',
    3: 'AS 1, BUT THE CHIMNEY BREAST IS MARBLE FROM THE FLOOR TO THE CEILING, SO THE STONE IS THE DECORATION. NO ART, NO BOOKS. HIGHER COST.',
    4: 'ONE ARCHED BOOK NICHE EACH SIDE OVER THE CABINETS, PANELS ABOVE, ART. ABOUT 22 FEET OF SHELF, ALL WITHIN REACH FROM THE FLOOR.',
    5: 'OPEN SHELVES UP TO 10 FT, THEN PLAIN PAINTED WALL WITH ONE PANEL, ART. EVERY SHELF IS REACHED FROM A STEP STOOL. THE LEAST MILLWORK OF THE BOOK OPTIONS.',
    6: 'THE SAME SHELVES AS 5, BUT THE CABINETRY CONTINUES TO THE CEILING AS PAINTED PANELS, SO IT LOOKS LIKE FLOOR TO CEILING BUILT-INS. MORE MILLWORK, MORE COST. ART.',
    7: 'AS PICKED: FLOOR TO CEILING SHELVES, ONE WIDE OPENING EACH SIDE, 2" SHELVES 18" APART, A PANEL IN THE 10 FT BAND (AS C ON ID-236), A SMALL ROLLING LADDER ON A RAIL, THE BREAST ONE PLANE. DRAWN ON ID-231.',
    8: 'FLOOR TO CEILING SHELVES BEHIND GLASS DOORS, NO ART. KEEPS THE BOOKS TIDY AND THE DUST OUT. COSTS MORE, AND THE GLASS REFLECTS THE WINDOWS.',
    9: 'YL\'S LIBRARY: TWO OPENINGS EACH SIDE, SHELVES 13" APART, DARK BACKS, FULL OF BOOKS, A ROLLING LADDER, ART. ABOUT 135 FEET OF SHELF.',
    10: 'SHELVES BOTH SIDES AND ACROSS THE CHIMNEY BREAST ABOVE 10 FT, THE WHOLE WALL BOOKS, A LADDER, NO ART. THE BUSIEST, NOT RECOMMENDED.'}
MARK = {7: 'OWNER PICK 11.09.26'}
TITLE_R = {1: 'PANELED, NOTHING ABOVE THE TV', 2: 'PANELED, ART ABOVE THE TV', 3: 'MARBLE CHIMNEY BREAST', 4: 'ARCHED BOOK NICHES',
           5: 'SHELVES TO 10 FT, PLAIN WALL ABOVE', 6: 'SHELVES TO 10 FT, PANELS TO CEILING', 7: 'FLOOR TO CEILING, WALL COLOR', 8: 'FLOOR TO CEILING BEHIND GLASS',
           9: 'FULL LIBRARY WITH A LADDER (YL)', 10: 'THE WHOLE WALL BOOKS'}
COST = {1: '$', 2: '$', 3: '$$$', 4: '$$', 5: '$$', 6: '$$$', 7: '$$$', 8: '$$$$', 9: '$$$$', 10: '$$$$'}
UPKEEP = {1: 'NOTHING TO STYLE OR DUST', 2: 'NOTHING TO STYLE OR DUST', 3: 'NOTHING TO STYLE OR DUST', 4: 'DUST FROM THE FLOOR',
          5: 'DUST FROM A STEP STOOL', 6: 'DUST FROM A STEP STOOL', 7: 'ROLLING LADDER BELOW 10 FT, A SCAFFOLD ABOVE', 8: 'CLEAN THE GLASS, A SCAFFOLD FOR THE TOP PANES',
          9: 'LADDER TO 12 FT, A SCAFFOLD ABOVE', 10: 'LADDER AND A SCAFFOLD'}

def mark(sh, x, y, t):
    """A dark flag with white text: RECOMMENDED, CURRENTLY DRAWN."""
    w = _FB.text_length(t, fontsize=8.0) + 12
    sh.p.draw_rect(fitz.Rect(x, y - 10, x + w, y + 4), color=None, fill=INK if t.startswith(('RECOMMENDED', 'OWNER PICK')) else MID, width=0)
    sh.p.insert_text((x + 6, y), t, fontsize=8.0, fontname='cgb', color=(1, 1, 1))

def wrap_raw(t, size, width, font=None):
    f = font or _FR; out = []; cur = ''
    for w in t.split():
        if f.text_length((cur + ' ' + w).strip(), fontsize=size) > width and cur: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    return out + ([cur] if cur else [])

def _cloud_inside(page, r, tag='1'):
    """Revision cloud with its delta inside the rect's top-right corner (the shared one puts it outside, on the panel divider)."""
    import idd_sheet as _I
    tmp = fitz.open(); tp = tmp.new_page(width=page.rect.width, height=page.rect.height)
    _I.rev_cloud_pt(tp, r, tag)                                            # draw on a scratch page, then copy only the scallops
    for dr in tp.get_drawings():
        if dr.get('fill') is not None: continue                            # skip the delta (the only filled path)
        sh_ = page.new_shape()
        for it in dr['items']:
            if it[0] == 'c': sh_.draw_bezier(*it[1:5])
            elif it[0] == 'l': sh_.draw_line(it[1], it[2])
        sh_.finish(color=dr.get('color'), width=dr.get('width') or 0.9, closePath=False); sh_.commit()
    cx, cy = r.x1 - 12, r.y0 + 12; s_ = 7.5
    tri = [fitz.Point(cx, cy - s_), fitz.Point(cx + s_ * 0.9, cy + s_ * 0.6), fitz.Point(cx - s_ * 0.9, cy + s_ * 0.6)]
    sh_ = page.new_shape(); sh_.draw_polyline(tri + [tri[0]]); sh_.finish(color=(0, 0, 0), width=0.7, fill=(1, 1, 1), closePath=True); sh_.commit()
    page.insert_text(fitz.Point(cx - 2.0, cy + 3.2), tag, fontsize=6.5, fontname='helv', color=(0, 0, 0))

def labels(v, k):
    """Option 1 names the parts once, in plain words, on its plaster breast."""
    v.text(v.X(CX), v.Y(H - 40), 'CHIMNEY BREAST', 5.0, INK, align='c')
    v.text(v.X(CX), v.Y(G.BELT1) - 3, '10 FT TRIM LINE', 5.0, INK, align='c')
    v.text(v.X(CX), v.Y(G.FF2) - 3, 'GALLERY FLOOR LINE', 5.0, INK, align='c')

def overview(sh, cells, specs):
    """ID-235: all ten at one scale, each with its number, name, a short description and the flags."""
    w0 = cells[0][2] - cells[0][0] - 16
    for scale in ('1/4', '3/16', '1/8'):
        k = E.SCALES[scale]; Hpt = H * k
        need = max(32 + (18 if s['n'] in MARK else 0) + len(G.wrap(SHORT[s['n']], NS, w0)) * NLH + 8 for s in specs)
        if (RD + 8) * k + 14 <= cells[0][2] - cells[0][0] and Hpt + need + 26 <= cells[0][3] - cells[0][1]: break
    for cell, s in zip(cells, specs):
        x0, y0, x1, y1 = cell
        E.title_bar(sh.p, sh.font, sh.fontname, cell, s['n'], TITLE_R[s['n']], '%s" TO 1\'-0"' % scale)
        if s['n'] == 7:
            sh.p.draw_rect(fitz.Rect(x0 + 1.2, y0 + 1.2, x1 - 1.2, y1 - 1.2), color=INK, width=1.6)
            _cloud_inside(sh.p, fitz.Rect(x0 + 3, y0 + 19, x1 - 3, y1 - 4))   # rev 1: the owner's pick, delta inside the panel (review 11.09.26)
        y = y0 + 32
        if s['n'] in MARK: mark(sh, x0 + 8, y, MARK[s['n']]); y += 18
        for ln in G.wrap(SHORT[s['n']], NS, w0): sh.text(x0 + 8, y, ln, NS, MID); y += NLH
        spec = {'room': 'LIVING ROOM', 'view': s['title'], 'length': RD, 'ceiling': H}
        oy = y1 - 22 - max(0, (y1 - 22 - H * k - y - 8) / 2)          # the view centered in the space under its text
        v = RV(sh.p, sh.font, sh.fontname, ((x0 + x1) / 2 - RD * k / 2, oy), k, spec)
        assert oy - H * k > y + 4, ('option text runs into the view', s['n'], scale)
        wall(v, s)
        if s['n'] == 1: labels(v, k)
    return scale

def glance(sh, x0, y, x1):
    """The ten at a glance: books, feet of shelf, art, cost direction, then upkeep on a second line."""
    sh.text(x0, y, 'THE TEN AT A GLANCE', 11, serif=True, spacing=0.8, raw=True); y += 22
    W_ = x1 - x0; cols = [('NO.', 0.0), ('OPTION', 0.07), ('FEET OF SHELF', 0.60), ('ART', 0.80), ('COST', 0.90)]
    for name, f in cols: sh.text(x0 + f * W_, y, name, 7.5, MID, spacing=0.3, raw=True)
    y += 5; sh.line((x0, y), (x1, y), 0.5, INK); y += 14
    for s in V:
        c = INK if s['n'] == 7 else MID
        row = [str(s['n']), TITLE_R[s['n']], '%d' % round(s['feet']) if s['feet'] else 'NONE', 'YES' if s.get('art') else 'NO', COST[s['n']]]
        for (name, f), t in zip(cols, row):
            nxt = [g for _, g in cols if g > f]; w_ = ((nxt[0] if nxt else 1.0) - f) * W_ - 6; sz = 8.5
            while _FR.text_length(t, fontsize=sz) > w_ and sz > 7.0: sz -= 0.25
            sh.text(x0 + f * W_, y, t, sz, c, bold=(s['n'] == 7), raw=True)
        y += 12; sh.text(x0 + 0.07 * W_, y, UPKEEP[s['n']], 7.5, MID, raw=True)
        y += 6; sh.line((x0, y), (x1, y), 0.3, LIGHT); y += 14
    for ln in wrap_raw('COST IS DIRECTION ONLY, FROM THE AMOUNT OF MILLWORK, GLASS AND STONE: $ LEAST, $$$$ MOST. THE MILLWORKER PRICES THE PICK.', 7.5, W_):
        sh.text(x0, y, ln, 7.5, MID, raw=True); y += 11
    return y

READ = [
    ('h', 'HOW TO CHOOSE'),
    ('p', 'THE QUESTION IS HOW MANY BOOKS THIS WALL SHOULD HOLD, AND WHETHER THEY WILL BE STYLED OR FILLED.'),
    ('b', '1 TO 3: NO BOOKS ON THIS WALL. NOTHING TO STYLE OR DUST. 3 MAKES THE CHIMNEY BREAST MARBLE.'),
    ('b', '4 TO 6: BOOKS ONLY AS HIGH AS A STEP STOOL REACHES. 5 HAS A PLAIN WALL ABOVE THE SHELVES. 6 CARRIES PAINTED PANELS TO THE CEILING, SO IT LOOKS LIKE FLOOR TO CEILING BUILT-INS, FOR MORE COST.'),
    ('b', '7: THE FLOOR TO CEILING BOOKSHELF LOOK, KEPT CALM: FEW THICK SHELVES, ONE OPENING EACH SIDE, PAINTED THE WALL COLOR. IT STAYS SIMPLE ONLY IF THE SHELVES ARE LIGHTLY STYLED (VIEW A). FILLED, IT LOOKS LIKE VIEW B. THE TOP HALF IS FOR DISPLAY, REACHED ONLY FROM A ROLLING SCAFFOLD.'),
    ('b', '8: LIKE 7, BEHIND GLASS DOORS (VIEW C). FILLED SHELVES STILL LOOK ORDERLY AND STAY CLEAN. COSTS MORE.'),
    ('b', '9 AND 10: A FULL LIBRARY WITH A ROLLING LADDER. THE BUSIEST LOOK.'),
    ('h', 'OWNER PICK, 11.09.26'),
    ('p', '7, WITH THREE CHANGES: A SMALL ROLLING LADDER ON A BRASS RAIL ON THE BELT COURSE, MOVED FROM ONE SIDE TO THE OTHER; THE PANEL IN THE 10 FT BAND FROM 8 (VIEW C) IN PLACE OF THE BAND SHELVES; THE CHIMNEY BREAST ONE PLASTER PLANE, NO BELT OR CAP ACROSS IT.'),
    ('p', 'VIEWS A AND B ARE DRAWN AS PICKED. ID-231 IS REDRAWN WITH THE PICK.'),
    ('h', 'THE SAME IN ALL TEN'),
    ('p', 'THE GAS FIREPLACE, THE 75" TV AT THE SAME HEIGHT, CLOSED CABINETS 30" HIGH AT THE BOTTOM, AND THE OTHER THREE WALLS. ID-231 AND ID-234 ARE DRAWN WITH THE PICK.')]

def reading(sh, x0, y, x1):
    for kind, t in READ:
        if kind == 'h':
            y += 10; sh.text(x0, y, t, 11, serif=True, spacing=0.8, raw=True); y += 20; continue
        ind = 12 if kind == 'b' else 0
        if kind == 'b': sh.p.draw_circle(fitz.Point(x0 + 3, y - 3.4), 1.7, color=INK, fill=INK)
        for ln in wrap_raw(t, TS, x1 - x0 - ind): sh.text(x0 + ind, y, ln, TS, INK, raw=True); y += TLH
        y += 6
    return y

DETAIL_R = {'A': 'OPTION 7 AS PICKED: LIGHTLY STYLED, PAINTED THE WALL COLOR, CLOSED CABINETS BELOW, A PANEL IN THE 10 FT BAND, A ROLLING LADDER, THE BREAST ONE PLANE. ABOUT {feet} FEET OF SHELF.',
            'B': 'THE SAME SHELVES FILLED WITH BOOKS. THIS IS HOW 7 LOOKS IF EVERY SHELF IS USED. IF THAT IS THE PLAN, CHOOSE 8 (GLASS) OR 6.',
            'C': 'OPTION 8: FLOOR TO CEILING SHELVES BEHIND GLASS DOORS. FULL SHELVES STAY ORDERLY AND CLEAN. THE CHOICE IF THE SHELVES WILL BE FULL OF BOOKS.'}

def big_view(sh, cell, s, label, title, scale):
    """One option drawn larger with its main dimensions, the text above it, the block centered in the cell."""
    k = E.SCALES[scale]; x0, y0, x1, y1 = cell
    E.title_bar(sh.p, sh.font, sh.fontname, cell, label, title, 'SCALE: %s" TO 1\'-0"' % scale)
    ln_ = wrap_raw(DETAIL_R[label].replace('{feet}', '%d' % round(s.get('feet') or 0)), TS, x1 - x0 - 20)
    block = len(ln_) * TLH + 24 + H * k + 50                         # text, gap, view, dimension strings
    ty = y0 + 16 + max(16, (y1 - y0 - 16 - block) / 2)
    for t in ln_: sh.text(x0 + 10, ty + 10, t, TS, INK, raw=True); ty += TLH
    oy = ty + 24 + H * k
    spec = {'room': 'LIVING ROOM', 'view': title, 'length': RD, 'ceiling': H}
    v = RV(sh.p, sh.font, sh.fontname, ((x0 + x1) / 2 - RD * k / 2 + 8, oy), k, spec)
    wall(v, s)
    v.dim_h(0, RD, v.Y(0) + 16, E.snap_points([0, B0, B1, RD]))
    pts = [0, CAB_H + TOP_T, BELT0, BELT1, FF2, H] + [CASE_TOP if s['flank'] in ('full', 'glass', 'library') else BOX_TOP]
    v.dim_v(0, H, v.X(RD) + 30, E.snap_points(sorted(set(pts))))
    assert oy + 44 < y1, ('view runs off the cell', label)

def build_review():
    doc = fitz.open()
    fx0, fy0, fx1, fy1 = FRAME
    # ID-235: the ten
    sh = Sheet(doc); sh.frame('FIREPLACE WALL OPTIONS', 'SCALE: 1/4" TO 1\'-0"', ['FIREPLACE WALL OPTIONS', '1 TO 10'], 'ID-235', legend_rule=False)
    top = ['LIVING ROOM FIREPLACE WALL, 16\'-2" WIDE AND 22\'-10" TALL, NUMBERED FROM THE SIMPLEST (1) TO THE BUSIEST (10). EVERY OPTION KEEPS THE SAME GAS FIREPLACE AND TV',
           'ON THE 7\'-0" CHIMNEY BREAST IN THE CENTER. WHAT CHANGES IS EITHER SIDE OF THE BREAST AND ABOVE THE TV, EXCEPT 3, WHICH CLADS THE BREAST IN MARBLE, AND 10, WHICH RUNS SHELVES',
           'ACROSS IT ABOVE 10 FT. OPTION 1 NAMES THE PARTS. BOOKS AND OBJECTS ARE SHOWN FOR SIZE ONLY. HOW TO CHOOSE, AND THE TEN SIDE BY SIDE: ID-236.']
    for i, t in enumerate(top): sh.text(fx0 + 6, fy0 + 14 + 13 * i, t, 9.0, INK, raw=True)
    sc = overview(sh, E.layout_cells((fx0, fy0 + 50, fx1, fy1), 5, 2), V)
    # ID-236: how to choose, the ten at a glance, option 7 styled and filled, the pick
    sh = Sheet(doc); sh.frame('FIREPLACE WALL OPTIONS', '', ['FIREPLACE WALL OPTIONS,', 'COMPARISON'], 'ID-236', legend_rule=False)
    xb = fx1 - 400; cw = (xb - fx0) / 3; yv = fy0 + 566
    s7 = next(s for s in V if s['n'] == 7); s8 = next(s for s in V if s['n'] == 8)
    for i, (sp, lab, ttl) in enumerate(((s7, 'A', 'OPTION 7 AS PICKED, LIGHTLY STYLED'), (STOCKED, 'B', 'OPTION 7, SHELVES FILLED'), (s8, 'C', 'OPTION 8, BEHIND GLASS'))):
        big_view(sh, (fx0 + i * cw, fy0, fx0 + (i + 1) * cw, yv), sp, lab, ttl, '1/4')
    sh.p.draw_rect(fitz.Rect(fx0, yv, xb, fy1), color=LIGHT, width=0.4)
    yg = glance_wide(sh, fx0 + 14, yv + 30, xb - 14, fy1 - 10)
    sh.p.draw_rect(fitz.Rect(xb, fy0, fx1, fy1), color=LIGHT, width=0.4)
    y = reading(sh, xb + 14, fy0 + 24, fx1 - 14)
    y = max(y + 40, fy1 - 80); sh.line((xb, y - 26), (fx1, y - 26), 0.5, INK)
    sh.text(xb + 14, y, 'OWNER PICK:', 14, serif=True, raw=True); sh.text(xb + 14, y + 34, 'OPTION 7     DATE 11.09.26', 14, serif=True, raw=True)
    import idd_sheet as _I
    _I.rev_cloud_pt(sh.p, fitz.Rect(xb + 8, y - 18, fx1 - 10, y + 42))
    _I.rev_cloud_pt(sh.p, fitz.Rect(fx0 + 4, fy0 + 19, fx0 + 2 * cw - 6, yv - 6))     # views A and B redrawn as picked
    assert y + 34 < fy1 - 6, ('ID-236 right column runs off the sheet', y)
    if hasattr(idd_sheet_mod(), 'finish_scales'): idd_sheet_mod().finish_scales(doc)
    fix_soft_hyphen(doc); doc.save(OUT_REVIEW, garbage=3, deflate=True); print('saved', OUT_REVIEW, 'overview scale', sc, 'reading ends', round(y, 1), 'glance ends', round(yg, 1))

def glance_wide(sh, x0, y, x1, ybot):
    """The ten at a glance, one line each across the width under the views, rows spaced to fill the space."""
    sh.text(x0, y, 'THE TEN AT A GLANCE', 12, serif=True, spacing=0.8, raw=True); y += 24
    W_ = x1 - x0; cols = [('NO.', 0.0), ('OPTION', 0.04), ('FEET OF SHELF', 0.36), ('ART', 0.46), ('COST', 0.52), ('UPKEEP AND REACH', 0.60)]
    for name, f in cols: sh.text(x0 + f * W_, y, name, 8.0, MID, spacing=0.3, raw=True)
    y += 6; sh.line((x0, y), (x1, y), 0.5, INK)
    pitch = min(40.0, (ybot - y - 40) / 10); y += pitch * 0.62
    for s in V:
        c = INK if s['n'] == 7 else MID
        row = [str(s['n']), TITLE_R[s['n']], '%d' % round(s['feet']) if s['feet'] else 'NONE', 'YES' if s.get('art') else 'NO', COST[s['n']], UPKEEP[s['n']]]
        for (name, f), t in zip(cols, row):
            nxt = [g for _, g in cols if g > f]; w_ = ((nxt[0] if nxt else 1.0) - f) * W_ - 8; sz = 10.0
            while _FR.text_length(t, fontsize=sz) > w_ and sz > 7.5: sz -= 0.25
            sh.text(x0 + f * W_, y, t, sz, c, bold=(s['n'] == 7), raw=True)
        sh.line((x0, y + pitch * 0.38), (x1, y + pitch * 0.38), 0.3, LIGHT); y += pitch
    y += 4
    sh.text(x0, y, 'COST IS DIRECTION ONLY, FROM THE AMOUNT OF MILLWORK, GLASS AND STONE: $ LEAST, $$$$ MOST. THE MILLWORKER PRICES THE PICK.', 8.0, MID, raw=True)
    assert y < ybot, ('table runs off', y)
    return y

def idd_sheet_mod():
    import idd_sheet; return idd_sheet
