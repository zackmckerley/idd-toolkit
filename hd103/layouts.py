"""2191 SW 23rd St (HD103): layouts replanned around how people move, drawn on the revised FOR plans (hd103/revise_plans.py).

Ground floor: kitchen at the street end on the solid stretch of the west wall, a through scullery in place of the powder room
(a second door to the foyer so groceries never cross the dining room), dining in the middle, the powder room moved off the
kitchen to a vestibule by the stair, and the mudroom closed so the garage opens into it.
Second floor: the master bath and one dressing room form a loop with the bedroom (bedroom, bath, dressing, bedroom).

    python3 hd103/layouts.py OUTDIR
"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/hd103')
from PIL import Image
from idd_revise import Plan, BLACK, THIN, FURN, WHITE
import revise_plans as RP

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/rev/lay'
os.makedirs(OUT, exist_ok=True)
KN = 35.88                                                # kitchen and scullery north limit: the foyer's south wall line
GUEST = (25, 95, 200); SERV = (225, 120, 0); SERVE = (20, 140, 70)


def grab(p, x0, y0, x1, y1): return p.im.crop(p.box(x0, y0, x1, y1))
def put(p, img, x, y, rotate=0, flip=None):
    if flip == 'v': img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if flip == 'h': img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate: img = img.rotate(rotate, expand=True, fillcolor=WHITE)
    p.im.paste(img, (p.X(x), p.Y(y) - img.height)); p._redraw()
def stool(p, cx, cy, r=0.68): p.ellipse(cx - r, cy - r, cx + r, cy + r, 2, FURN)


def ground_new(p, guest='R4', scullery='THRU', mud='M1'):
    tbl = grab(p, 28.3, 19.2, 34.6, 30.4); snk = grab(p, 23.2, 38.42, 25.3, 40.85)
    sce = grab(p, 43.22, 20.15, 45.26, 27.08)                                    # FOR's scullery sink and dishwasher run
    ptoilet = grab(p, 42.6, 31.05, 44.1, 33.62); psink = grab(p, 42.62, 27.42, 44.12, 28.92)
    # ---- clear what moves (the wall face line at x 23.1 stays)
    p.white(23.2, 18.56, 25.5, 49.0); p.white(29.9, 34.3, 36.0, 44.8); p.white(30.8, 45.4, 34.0, 46.6); p.white(28.3, 19.2, 34.6, 30.4)
    p.white(37.7, 18.56, 45.28, 35.05)
    # ---- scullery: the whole block, a through room (kitchen's south aisle on the west, foyer on the north)
    p.partition(37.8, 18.56, 38.15, KN); p.partition(37.8, KN - 0.3, 45.3, KN)
    p.white(37.74, 21.0, 38.21, 24.3); p.line([(37.97, 21.0), (37.97, 24.3)], 1, FURN, dash=(8, 6))
    p.white(40.3, KN - 0.36, 42.8, KN + 0.06); p.door((42.8, KN - 0.15), 2.5, 'W', 'S')              # concealed (jib) door, swings in
    put(p, sce, 43.22, 20.15); p.rect(43.22, 18.6, 45.26, 20.15, 2, BLACK); p.rect(43.22, 27.08, 45.26, 32.9, 2, BLACK)
    p.label(44.24, 30.0, 'OVENS + COFFEE', px=15, rotate=90)
    p.rect(38.17, 18.6, 43.22, 20.65, 2, BLACK); p.label(40.7, 19.62, 'FREEZER + TALL PANTRY', px=14)
    p.rect(38.17, 25.0, 39.17, KN - 0.32, 2, BLACK); p.label(38.67, 30.2, 'PANTRY SHELVES', px=13, rotate=90)
    p.label(41.2, 28.2, 'SCULLERY', px=17, rotate=90)
    # ---- kitchen at the street end: range and fridge on the solid pier, sink in the island facing them
    p.rect(23.14, 18.56, 25.2, 33.3, 2, BLACK)
    p.rect(23.14, 25.05, 25.2, 29.05, 2, BLACK)
    for bx in (23.72, 24.65):
        for by in (25.75, 27.05, 28.35): p.ellipse(bx - 0.33, by - 0.33, bx + 0.33, by + 0.33, 2, BLACK)
    p.label(26.1, 27.05, '48" RANGE + HOOD', px=15, rotate=90)
    p.rect(23.14, 30.3, 25.43, 33.3, 2, BLACK, fill=WHITE); p.label(24.28, 31.8, 'FRIDGE', px=15, rotate=90)
    p.rect(25.2, 18.56, 37.78, 20.7, 2, BLACK); p.label(31.5, 19.63, 'BAR + BREAKFAST COUNTER', px=15)
    p.rect(29.0, 24.3, 33.0, 34.0, 2, BLACK)
    put(p, snk, 29.1, 26.85, flip='h'); p.rect(29.05, 24.6, 31.15, 26.6, 1, THIN, dash=(8, 5)); p.label(30.1, 25.6, 'DW', px=15)
    p.label(31.0, 32.2, 'ISLAND', px=16); p.label(30.2, 29.75, 'SINK', px=13)
    for cy in (25.7, 28.0, 30.3, 32.6): stool(p, 33.75, cy)
    p.label(31.2, 22.5, 'KITCHEN')
    if scullery == 'U':
        # ---- owner markup 11.25.26: powder room at the north end of the block, U-shaped scullery entered from the kitchen only
        p.white(38.16, 18.58, 45.27, KN + 0.08); p.white(37.74, 20.9, 38.21, 27.1)
        p.partition(37.8, 18.56, 38.15, KN); p.partition(37.8, KN - 0.3, 45.3, KN); p.partition(38.15, 31.3, 45.28, 31.6)
        p.white(37.74, 21.0, 38.21, 25.0); p.line([(37.97, 21.0), (37.97, 25.0)], 1, FURN, dash=(8, 6))
        put(p, sce, 43.22, 20.15); p.rect(43.22, 18.6, 45.26, 20.15, 2, BLACK); p.rect(43.22, 27.08, 45.26, 31.28, 2, BLACK)
        p.rect(38.17, 18.6, 43.22, 20.65, 2, BLACK); p.label(40.7, 19.62, 'FREEZER + TALL PANTRY', px=14)
        p.rect(38.17, 29.25, 43.22, 31.28, 2, BLACK); p.label(40.7, 30.27, 'OVENS + COFFEE', px=14)
        p.rect(38.17, 25.3, 39.67, 29.25, 2, BLACK); p.label(38.92, 27.3, 'PANTRY', px=13, rotate=90)
        p.label(41.45, 24.6, 'SCULLERY', px=17, rotate=90)
        p.white(42.5, KN - 0.36, 45.0, KN + 0.06); p.door((45.0, KN - 0.15), 2.5, 'W', 'S')
        put(p, ptoilet, 38.25, 32.85, rotate=90); p.rect(41.4, 31.62, 44.4, 33.2, 2, BLACK); put(p, psink, 42.15, 31.68)
        p.label(40.6, 34.6, 'POWDER', px=14)
        p.rect(23.14, 33.3, 25.2, KN, 2, BLACK)                                    # west run carried north to the kitchen line
    if scullery in ('K', 'K3'):
        # ---- kitchen planned to the NKBA guidelines (11.25.26): tall freezer and wine columns recessed into the powder block,
        #      a through aisle behind the stools, sink / range / fridge triangle on the west side, U-shaped scullery
        p.white(38.16, 18.58, 45.27, KN + 0.08); p.white(37.74, 18.58, 38.21, KN + 0.08)
        p.white(28.9, 24.2, 34.6, 34.1); p.white(23.2, 33.32, 25.5, KN + 0.05)
        p.partition(37.8, 18.56, 38.15, 30.3); p.partition(37.8, 30.0, 45.28, 30.3)            # scullery west and north walls
        p.partition(40.0, 30.3, 40.3, KN); p.partition(37.8, KN - 0.3, 45.3, KN)               # back of the tall units, block north wall
        p.white(37.74, 21.0, 38.21, 25.0); p.line([(37.97, 21.0), (37.97, 25.0)], 1, FURN, dash=(8, 6))
        # scullery
        put(p, sce, 43.22, 20.15); p.rect(43.22, 18.6, 45.26, 20.15, 2, BLACK); p.rect(43.22, 27.08, 45.26, 29.98, 2, BLACK)
        p.rect(38.17, 18.6, 43.22, 20.65, 2, BLACK); p.label(40.7, 19.62, 'TALL PANTRY', px=14)
        p.rect(38.17, 27.95, 43.22, 29.98, 2, BLACK); p.label(40.7, 28.97, 'OVENS + COFFEE', px=14)
        p.rect(38.17, 25.3, 39.67, 27.95, 2, BLACK); p.label(38.92, 26.6, 'PANTRY', px=12, rotate=90)
        p.label(41.45, 24.0, 'SCULLERY', px=17, rotate=90)
        # tall columns facing the kitchen, flush with the scullery wall
        p.rect(37.8, 30.6, 39.98, 33.1, 2, BLACK, fill=WHITE); p.rect(37.8, 33.1, 39.98, 35.56, 2, BLACK, fill=WHITE)
        p.label(38.9, 31.85, 'FREEZER', px=13, rotate=90); p.label(38.9, 34.33, 'WINE', px=13, rotate=90)
        # powder room, 5'-0" x 5'-3"
        p.white(42.5, KN - 0.36, 45.0, KN + 0.06); p.door((45.0, KN - 0.15), 2.5, 'W', 'S')
        put(p, ptoilet, 40.85, 30.35, flip='v'); p.rect(43.0, 30.32, 45.24, 31.9, 2, BLACK); put(p, psink, 43.37, 30.38)
        p.label(41.9, 34.3, 'POWDER', px=13)
        # west run to the kitchen line, serving counter north of the fridge
        p.rect(23.14, 33.3, 25.2, KN, 2, BLACK); p.label(24.17, 34.6, 'SERVE', px=12, rotate=90)
        # island: trash, sink, dishwasher in work order from the fridge; prep top; four stools on the walk-past side
        p.rect(29.0, 24.3, 33.0, 34.0, 2, BLACK)
        put(p, snk, 29.1, 28.0, flip='h')
        p.rect(29.05, 25.9, 31.15, 27.9, 1, THIN, dash=(8, 5)); p.label(30.1, 26.9, 'DW', px=15)
        p.rect(29.05, 30.55, 31.15, 32.05, 1, THIN, dash=(8, 5)); p.label(30.1, 31.3, 'TRASH', px=12)
        p.label(31.0, 33.1, 'PREP', px=14); p.label(31.0, 25.0, 'ISLAND', px=14)
        for cy in (25.7, 28.0, 30.3, 32.6): stool(p, 33.75, cy)
        p.white(26.5, 19.2, 36.5, 20.1); p.label(31.5, 19.63, 'BREAKFAST COUNTER + MICROWAVE DRAWER', px=14)
    if scullery == 'K3':
        # ---- fridge and freezer together at the dining end of the range wall; the long west window starts 2'-7" further north
        p.white(23.2, 29.1, 25.5, KN + 0.05)
        p.wall(22.28, 33.4, 22.98, KN + 0.02)
        p.rect(23.14, 29.05, 25.2, 30.38, 2, BLACK)
        p.rect(23.14, 30.38, 25.43, 32.88, 2, BLACK, fill=WHITE); p.label(24.28, 31.63, 'FREEZER', px=13, rotate=90)
        p.rect(23.14, 32.88, 25.43, KN, 2, BLACK, fill=WHITE); p.label(24.28, 34.38, 'FRIDGE', px=14, rotate=90)
        p.white(37.85, 30.65, 39.95, 35.5)
        p.rect(37.8, 30.6, 39.98, 33.1, 2, BLACK, fill=WHITE); p.rect(37.8, 33.1, 39.98, 35.56, 2, BLACK, fill=WHITE)
        p.label(38.9, 31.85, 'WINE', px=13, rotate=90); p.label(38.9, 34.33, 'BAR', px=13, rotate=90)
    # ---- dining in the middle, clear of the walk from the foyer to the living room; the long west window is left free
    put(p, tbl, 26.1, 37.95, rotate=90); p.white(31.1, 39.6, 32.3, 42.6); p.label(31.7, 41.1, 'DINING', bg=True)
    if mud in ('M5', 'M6'):
        # ---- owner direction 11.25.26: garage opens into the hall recess, mudroom off it through a cased opening,
        #      the stair drawn in full (from FOR's second floor plan), the air handler in its own small closet
        global _S2
        try: _S2
        except NameError: _S2 = RP.second(RP.ground())
        p.white(62.36, 18.6, 67.17, 38.72); p.white(67.9, 35.05, 69.45, 38.5)
        p.wall(67.17, 35.0, 67.84, KN)                                                  # wall solid up to the foyer wall line
        p.rect(67.9, KN, 70.9, 38.5, 2, THIN); p.door((67.9, KN + 0.05), 2.6, 'N', 'E')   # house door swings out onto a landing
        p.partition(62.3, KN - 0.3, 67.2, KN)
        if mud == 'M6':                                                               # sliding (pocket) door to the mudroom
            p.white(64.8, KN - 0.36, 67.1, KN + 0.06); p.pocket((64.8, KN - 0.15), (67.1, KN - 0.15))
        else:
            p.white(63.4, KN - 0.36, 66.9, KN + 0.06); p.line([(63.4, KN - 0.15), (66.9, KN - 0.15)], 1, FURN, dash=(8, 6))
        p.partition(62.3, 25.0, 67.2, 25.3)
        p.rect(62.36, 25.3, 67.15, 27.3, 2, BLACK)
        for lx in (63.56, 64.76, 65.96): p.line([(lx, 25.3), (lx, 27.3)], 1, THIN)
        p.label(64.76, 26.3, 'LOCKERS', px=14, bg=True)
        p.rect(62.36, 27.3, 63.86, KN - 0.32, 2, BLACK); p.label(63.11, 31.4, 'BENCH + HOOKS', px=14, rotate=90)
        p.label(65.6, 30.6, 'MUD\nROOM', px=16)
        p.white(67.13, 19.6, 67.88, 24.4); p.line([(67.5, 19.6), (67.5, 24.4)], 1, FURN, dash=(8, 6))
        p.rect(62.36, 18.62, 63.86, 24.98, 2, THIN); p.label(63.11, 21.8, 'SHELVES', px=13, rotate=90)
        p.label(65.6, 20.4, 'GARAGE\nSTORAGE', px=13)
        # stair in full: closet removed, the upper flight copied from FOR's second floor plan
        p.white(68.6, 43.25, 74.45, 46.42)
        st = _S2.im.crop(_S2.box(69.22, 43.08, 77.2, 46.72)); p.im.paste(st, (p.X(69.22), p.Y(46.72))); p._redraw()
        p.white(69.3, 43.9, 70.5, 45.7); p.line([(71.45, 45.4), (70.75, 44.9), (71.45, 44.4)], 4, BLACK)
        # mechanical closet 4'-6" x 3'-6": air handler with its 30 in. service space, wall-hung water heater, doors to the garage
        p.white(82.36, 39.25, 87.58, 46.92); p.wall(86.82, 38.5, 87.54, 43.4); p.wall(82.33, 42.7, 87.54, 43.4)
        if mud == 'M6':                                                               # one 2'-8" door, hinged on the garage face
            p.wall(82.33, 38.5, 83.2, 39.2); p.wall(85.87, 38.5, 86.9, 39.2); p.white(83.2, 38.46, 85.87, 39.24)
            p.door((83.2, 38.53), 2.67, 'E', 'S')
        else:
            p.door((82.95, 39.2), 1.3, 'E', 'S'); p.door((85.6, 39.2), 1.3, 'W', 'S')
        p.rect(82.6, 40.5, 84.8, 42.6, 3, BLACK); p.line([(82.6, 40.5), (84.8, 42.6)], 1, THIN); p.line([(82.6, 42.6), (84.8, 40.5)], 1, THIN)
        p.label(83.7, 41.55, 'AHU', px=14, bg=True)
        p.rect(82.6, 39.3, 84.8, 40.5, 1, FURN, dash=(6, 5))
        p.rect(86.15, 40.2, 86.78, 42.0, 2, BLACK); p.label(85.75, 41.1, 'WH', px=11)
        p.window(81.63, 43.6, 82.33, 46.1)
    elif mud == 'M4':
        # ---- owner markup 11.25.26: mudroom shifted south behind the foyer wall line, garage wall closed at the north end,
        #      coat closet removed for an open stair, mechanical room at its minimum
        car1 = grab(p, 69.3, 19.0, 76.55, 34.9); car2 = grab(p, 78.3, 19.0, 85.55, 34.9)
        p.white(62.36, 18.6, 67.17, 38.72); p.white(67.9, 35.05, 69.45, 38.5); p.white(69.3, 19.0, 76.55, 34.9); p.white(78.3, 19.0, 85.55, 34.9)
        put(p, car1, 70.3, 19.0); put(p, car2, 78.85, 19.0)
        p.wall(67.17, 35.0, 67.84, 38.6)                                                # garage wall closed at the north end
        p.partition(62.3, KN - 0.3, 67.2, KN)                                           # mudroom north wall on the foyer wall line
        p.white(64.4, KN - 0.36, 66.9, KN + 0.06); p.pocket((64.4, KN - 0.15), (66.9, KN - 0.15))
        p.white(67.13, 31.9, 67.88, 34.9); p.door((67.2, 31.9), 3.0, 'N', 'W')          # garage door, beside the left car
        p.partition(62.3, 25.0, 67.2, 25.3)
        p.rect(62.36, 25.3, 67.15, 27.3, 2, BLACK)
        for lx in (63.56, 64.76, 65.96): p.line([(lx, 25.3), (lx, 27.3)], 1, THIN)
        p.label(64.76, 26.3, 'LOCKERS', px=14, bg=True)
        p.rect(62.36, 27.3, 63.86, KN - 0.32, 2, BLACK); p.label(63.11, 31.4, 'BENCH + HOOKS', px=14, rotate=90)
        p.label(65.6, 29.6, 'MUD\nROOM', px=16)
        p.white(67.13, 19.6, 67.88, 24.4); p.line([(67.5, 19.6), (67.5, 24.4)], 1, FURN, dash=(8, 6))
        p.rect(62.36, 18.62, 63.86, 24.98, 2, THIN); p.label(63.11, 21.8, 'SHELVES', px=13, rotate=90)
        p.label(65.6, 20.4, 'GARAGE\nSTORAGE', px=13)
        # stair: closet removed
        p.white(68.6, 43.25, 74.45, 46.42)
        p.label(72.2, 44.9, 'OPEN STAIR\nBY FOR', px=13)
        # mechanical room cut to 4'-6" x 3'-6"; the stair's east wall becomes an outside wall and takes a window
        p.white(82.36, 39.25, 87.58, 46.92); p.wall(86.82, 38.5, 87.54, 43.4); p.wall(82.33, 42.7, 87.54, 43.4)
        p.door((83.0, 39.2), 2.6, 'E', 'N')
        p.rect(84.9, 40.6, 86.75, 42.6, 2, THIN); p.line([(84.9, 40.6), (86.75, 42.6)], 1, FURN); p.line([(84.9, 42.6), (86.75, 40.6)], 1, FURN)
        p.label(83.5, 42.2, 'MECH.', px=11)
        p.window(81.63, 43.6, 82.33, 46.1)
    elif mud == 'M1':
        # ---- mudroom closed: the garage door now opens into it, and its own door faces down the foyer's south wall
        p.partition(62.3, 38.75, 67.3, 39.05); p.partition(62.0, 35.8, 62.3, 39.05)
        p.white(61.95, 36.05, 62.35, 38.75); p.door((62.15, 36.05), 2.7, 'N', 'W')
    else:
        # ---- mudroom re-planned 11.25.26: a 10 ft room at the garage door, no door swings inside it, exit north to the stair hall;
        #      the south half of the strip becomes a storage bay open to the garage
        p.white(62.36, 18.6, 67.17, 38.72); p.white(67.95, 35.05, 69.45, 38.5)
        p.partition(62.3, 38.75, 67.3, 39.05); p.partition(62.0, 35.8, 62.3, 39.05)
        p.white(64.5, 38.7, 67.0, 39.1); p.pocket((64.5, 38.9), (67.0, 38.9))
        p.rect(67.92, 35.2, 70.9, 38.5, 2, THIN); p.door((67.92, 35.3), 3.1, 'N', 'E')          # garage door swings out onto a landing
        p.partition(62.3, 28.2, 67.2, 28.5)
        p.rect(62.36, 28.5, 67.17, 30.5, 2, BLACK)
        for lx in (63.56, 64.76, 65.96): p.line([(lx, 28.5), (lx, 30.5)], 1, THIN)
        p.label(64.76, 29.5, 'LOCKERS', px=14, bg=True)
        p.rect(62.36, 30.5, 63.86, 38.4, 2, BLACK); p.label(63.11, 34.4, 'BENCH + HOOKS', px=14, rotate=90)
        p.label(65.6, 33.3, 'MUD\nROOM', px=16)
        p.white(67.15, 20.5, 67.95, 27.0); p.line([(67.55, 20.5), (67.55, 27.0)], 1, FURN, dash=(8, 6))
        p.rect(62.36, 18.62, 63.86, 28.18, 2, THIN); p.label(63.11, 23.4, 'SHELVES', px=13, rotate=90)
        p.label(65.6, 21.4, 'GARAGE\nSTORAGE', px=14)
        if mud == 'M3':
            # ---- the old storage room behind the stair becomes the mechanical room; the air handler closet becomes a coat closet
            p.white(82.9, 42.4, 85.4, 43.25); p.label(84.0, 42.78, 'MECH.', px=13)
            p.rect(83.0, 43.3, 85.3, 45.6, 2, THIN); p.line([(83.0, 43.3), (85.3, 45.6)], 1, FURN); p.line([(83.0, 45.6), (85.3, 43.3)], 1, FURN)
            p.label(84.15, 44.45, 'AHU', px=13, bg=True)
            p.ellipse(85.5, 41.6, 86.6, 42.7, 2, THIN); p.label(86.05, 42.15, 'WH', px=11)
            p.white(70.75, 43.55, 74.25, 46.25); p.line([(70.8, 45.3), (74.2, 45.3)], 1, FURN, dash=(14, 8))
            p.label(72.5, 44.4, 'COATS', px=14)
    if guest == 'FOR': return p
    if guest == 'R4':
        # ---- powder room: out of the kitchen, into the south end of the guest closet, off a vestibule by the stair
        p.white(70.56, 47.18, 75.8, 52.5); p.partition(70.5, 52.2, 75.86, 52.5)
        p.white(70.03, 47.2, 70.56, 49.5); p.pocket((70.33, 49.5), (70.33, 47.2))
        p.rect(72.3, 47.15, 75.82, 48.75, 2, BLACK); put(p, psink, 73.3, 47.2)
        put(p, ptoilet, 73.25, 50.15, rotate=-90)                                    # tank on the east wall, bowl to the west
        p.label(71.6, 51.2, 'POWDER', px=14); p.white(71.6, 54.0, 74.8, 55.0); p.label(73.2, 54.4, 'LINEN +\nLUGGAGE', px=14, bg=True)
        p.white(66.38, 46.55, 69.95, 50.45)
        p.partition(66.3, 49.5, 66.95, 49.8); p.partition(69.95, 49.5, 70.2, 49.8); p.door((69.95, 49.65), 3.0, 'W', 'N')
        # ---- guest wing: east wall out 5'-3" to the line of the garage and storage wall (one straight east wall)
        p.white(82.36, 46.9, 86.8, 66.28)
        p.wall(86.82, 46.2, 87.54, 67.02); p.wall(82.3, 66.3, 87.54, 67.02)
        p.white(81.6, 50.45, 82.36, 56.3)                                            # bath opens into the new bay (beam over)
        p.wall(81.63, 50.2, 82.33, 50.51)
        p.white(81.3, 50.6, 81.62, 56.0)
        p.partition(82.33, 56.3, 86.82, 56.6)                                        # bath / closet
        p.rrect(83.2, 50.7, 86.0, 55.9, r=0.9, w=2, color=BLACK); p.ellipse(83.55, 51.2, 85.65, 55.4, 1, FURN); p.ellipse(84.45, 51.35, 84.75, 51.65, 2, BLACK)
        p.window(86.82, 51.3, 87.54, 55.3)
        p.rect(82.4, 46.92, 86.8, 48.6, 2, BLACK); p.label(84.6, 47.76, 'LINEN', px=15)
        p.white(81.6, 57.3, 82.36, 60.0); p.pocket((81.98, 60.0), (81.98, 57.3))     # bedroom to walk-in closet
        p.rect(84.8, 56.62, 86.8, 66.28, 2, THIN); p.line([(85.8, 56.65), (85.8, 66.25)], 1, FURN, dash=(14, 8))
        p.rect(82.36, 64.6, 84.8, 66.28, 2, THIN)
        p.label(83.6, 61.0, 'WALK-IN CLOSET', px=15, rotate=90)
    elif guest == 'A':
        # ---- A: east wall out 5'-3"; the bedroom widens, one walk-in closet in the southeast bay, FOR's bath untouched
        # ---- powder room: out of the kitchen, into the south end of the guest closet, off a vestibule by the stair
        p.white(70.56, 47.18, 75.8, 52.5); p.partition(70.5, 52.2, 75.86, 52.5)
        p.white(70.03, 47.2, 70.56, 49.5); p.pocket((70.33, 49.5), (70.33, 47.2))
        p.rect(72.3, 47.15, 75.82, 48.75, 2, BLACK); put(p, psink, 73.3, 47.2)
        put(p, ptoilet, 73.25, 50.15, rotate=-90)                                    # tank on the east wall, bowl to the west
        p.label(71.6, 51.2, 'POWDER', px=14); p.white(71.6, 54.0, 74.8, 55.0); p.label(73.2, 54.4, 'LINEN +\nLUGGAGE', px=14, bg=True)
        p.white(66.38, 46.55, 69.95, 50.45)
        p.partition(66.3, 49.5, 66.95, 49.8); p.partition(69.95, 49.5, 70.2, 49.8); p.door((69.95, 49.65), 3.0, 'W', 'N')
        p.white(70.03, 52.55, 70.58, 56.2); p.white(70.56, 52.55, 75.8, 56.12)       # old closet opens up as an entry alcove
        p.rect(70.7, 54.7, 75.75, 56.1, 2, THIN); p.label(73.2, 55.4, 'BENCH + HOOKS', px=14)
        p.white(82.36, 46.9, 86.8, 66.28)
        p.wall(86.82, 46.2, 87.54, 67.02); p.wall(82.3, 66.3, 87.54, 67.02)
        p.white(81.6, 56.62, 82.36, 66.28)                                          # bedroom east wall out (beam over)
        p.white(81.3, 56.66, 81.62, 66.25)
        p.wall(81.63, 50.4, 82.33, 52.75)                                           # bath window closed
        p.partition(81.63, 56.3, 86.82, 56.6)
        p.white(84.45, 56.25, 86.75, 56.65); p.pocket((84.45, 56.45), (86.75, 56.45))
        p.rect(82.36, 46.95, 84.36, 56.28, 2, THIN); p.line([(83.36, 46.98), (83.36, 56.25)], 1, FURN, dash=(14, 8))
        p.rect(84.36, 46.95, 86.8, 48.4, 2, THIN)
        p.label(85.6, 52.0, 'WALK-IN CLOSET', px=15, rotate=90)
        p.window(83.2, 66.3, 86.2, 67.02); p.label(84.3, 61.5, 'SITTING', px=15)
    elif guest == 'B':
        # ---- B: no exterior change; FOR's guest suite stays, the powder room takes the AHU closet by the stair
        p.white(68.6, 43.25, 74.5, 46.5); p.white(70.3, 46.4, 74.5, 47.3); p.white(70.56, 47.2, 75.8, 48.95)
        p.partition(70.0, 43.15, 70.3, 47.2); p.partition(74.5, 46.4, 74.8, 48.9); p.partition(70.2, 48.6, 75.9, 48.9)
        p.white(69.95, 43.5, 70.35, 46.0); p.pocket((70.15, 46.0), (70.15, 43.5))
        put(p, ptoilet, 71.6, 46.0); p.rect(72.9, 43.3, 74.48, 45.7, 2, BLACK); put(p, psink, 72.95, 43.75, rotate=90)
        p.label(71.4, 44.7, 'POWDER', px=13); p.label(75.35, 47.85, 'CHASE', px=10, rotate=90)
        p.rect(83.3, 43.6, 85.6, 45.9, 2, THIN); p.line([(83.3, 43.6), (85.6, 45.9)], 1, FURN); p.line([(83.3, 45.9), (85.6, 43.6)], 1, FURN)
        p.label(84.45, 44.75, 'AHU', px=13, bg=True)
    return p


def master_new(p):
    """Loop suite inside FOR's walls: bedroom to bath, bath to dressing room, dressing room to bedroom."""
    toilet = grab(p, 45.55, 22.72, 46.95, 25.15); sink = grab(p, 35.72, 22.76, 37.25, 24.3)
    p.white(26.2, 22.56, 47.98, 35.03)
    p.partition(26.15, 34.65, 48.0, 35.0)
    p.white(32.05, 34.6, 34.75, 35.05); p.door((32.05, 34.82), 2.7, 'E', 'S')               # bedroom to bath, parks on the shower wall
    p.white(41.95, 34.6, 44.95, 35.05); p.pocket((41.95, 34.82), (44.95, 34.82))             # bedroom to dressing, pocket in dry wall
    p.partition(38.5, 22.55, 38.85, 34.65)
    p.white(38.45, 25.6, 38.9, 28.3); p.pocket((38.67, 28.3), (38.67, 25.6))                 # bath to dressing
    # tub at the west window, 12 in. off the wall
    p.rrect(27.0, 23.5, 29.7, 29.0, r=0.9, w=2, color=BLACK); p.ellipse(27.35, 24.0, 29.35, 28.5, 1, FURN); p.ellipse(28.2, 24.15, 28.5, 24.45, 2, BLACK)
    # vanity on the south wall, the window between the two mirrors
    p.rect(31.1, 22.56, 38.5, 24.65, 2, BLACK); put(p, sink, 31.75, 22.76); put(p, sink, 35.85, 22.76)
    # shower in the northwest corner, door hinged on its east wall
    p.rect(26.2, 30.95, 28.9, 31.15, 2, BLACK, fill=WHITE); p.door((31.4, 31.05), 2.5, 'W', 'S')
    p.partition(31.4, 30.95, 31.75, 34.65)
    p.line([(26.25, 31.2), (31.35, 34.6)], 1, FURN); p.line([(26.25, 34.6), (31.35, 31.2)], 1, FURN)
    p.rect(28.4, 32.5, 29.2, 33.3, 1, THIN, dash=(8, 5))
    # water closet in the northeast corner, away from the bed, door on its south side swinging out
    p.partition(34.85, 29.5, 35.1, 34.65); p.partition(34.85, 29.5, 35.5, 29.75); p.partition(38.0, 29.5, 38.5, 29.75)
    p.door((35.5, 29.62), 2.5, 'E', 'S'); put(p, toilet, 36.1, 32.2, flip='v'); p.label(36.8, 31.0, 'WC', px=16)
    p.label(33.6, 27.1, 'MASTER\nBATH')
    # dressing room
    p.rect(46.05, 22.58, 47.98, 34.62, 2, THIN); p.line([(47.02, 22.6), (47.02, 34.6)], 1, FURN, dash=(14, 8))
    p.rect(38.87, 29.0, 40.85, 34.62, 2, THIN); p.line([(39.86, 29.0), (39.86, 34.6)], 1, FURN, dash=(14, 8))
    p.rect(38.87, 22.58, 40.3, 25.1, 2, THIN); p.label(39.6, 23.85, 'LINEN', px=13, rotate=90)
    p.rect(41.2, 22.6, 45.2, 24.2, 2, THIN); p.label(43.2, 23.4, 'DRESSER', px=15)
    p.label(44.45, 30.2, 'DRESSING\nROOM', px=17)
    return p


def put_dark(p, img, x, y):
    """Paste keeping whatever is already drawn underneath (darker of the two), so white paper in the piece erases nothing."""
    from PIL import ImageChops
    box = (p.X(x), p.Y(y) - img.height, p.X(x) + img.width, p.Y(y))
    p.im.paste(ImageChops.darker(p.im.crop(box).convert('RGB'), img.convert('RGB')), box[:2]); p._redraw()


def sink_sym(p, x0, y0, x1, y1, faucet='E'):
    """A plain sink: bowl outline, inner bowl, faucet dot on the given side."""
    p.rect(x0, y0, x1, y1, 2, BLACK, fill=WHITE); p.rrect(x0 + 0.18, y0 + 0.18, x1 - 0.18, y1 - 0.18, r=0.15, w=1, color=THIN)
    fx, fy = {'E': (x1 + 0.22, (y0 + y1) / 2), 'W': (x0 - 0.22, (y0 + y1) / 2), 'N': ((x0 + x1) / 2, y1 + 0.22), 'S': ((x0 + x1) / 2, y0 - 0.22)}[faucet]
    p.ellipse(fx - 0.12, fy - 0.12, fx + 0.12, fy + 0.12, 2, BLACK)


def ground_final():
    """The owner's ground floor, 11.25.26: KP-3 kitchen; court door wall 1'-2" north; living room back to FOR's width with its
    east wall 3'-0" further west; guest wing and stair 3'-0" further east (court 6'-0" wider, plan symmetrical about the
    court); mechanical and electrical room in the garage bay; the room north of the garage removed."""
    p = ground_new(RP.ground(), 'FOR', 'K3', 'M6')
    FOR = Image.open('/home/claude/deck/img_p3_11.png').convert('RGB')
    DASH = (22, 12)
    # ---- repairs before anything moves
    p.wall(81.63, 43.5, 82.33, 46.2)                                           # the earlier stair window comes out
    p.line([(70.0, 46.75), (75.0, 46.75)], 3, BLACK); p.line([(70.0, 46.9), (75.0, 46.9)], 2, BLACK)   # wall where the closet met it
    # ---- court door wall 1'-2" north
    D = 1.17
    plant = grab(p, 46.3, 23.4, 49.75, 26.15)
    frame = grab(p, 46.03, 43.27, 61.57, 43.95); leaves = grab(p, 50.2, 43.95, 56.9, 45.98)
    p.white(45.1, 42.9, 62.5, 43.22)
    p.white(46.03, 43.1, 61.57, 46.86)
    for x0, x1 in ((45.3, 46.06), (61.54, 62.31)): p.white(x0, 43.1, x1, 44.34)
    p.wall(45.33, 43.16 + D, 46.02, 46.02); p.wall(61.58, 43.16 + D, 62.28, 46.02)
    put_dark(p, frame, 46.03, 43.27 + D); put_dark(p, leaves, 50.2, 43.95 + D)
    p.line([(45.19, 44.24), (62.42, 44.24)], 1, THIN, dash=DASH)
    for vx in (45.19, 62.42): p.line([(vx, 42.9), (vx, 44.24)], 1, THIN, dash=DASH)
    sm = plant.resize((int(plant.width * 0.5), int(plant.height * 0.5)))
    for x in (47.3, 58.5): put_dark(p, sm, x, 45.25)
    # ---- living room: FOR's own room, 3'-0" further west than he drew it (east wall 3'-0" west of where it was)
    blk = FOR.crop(p.box(25.0, 47.02, 42.6, 67.8))
    p.white(21.95, 47.02, 42.62, 67.8); p.im.paste(blk, (p.X(22.0), p.Y(67.8))); p._redraw()
    p.white(23.2, 47.0, 25.7, 49.2)                                            # FOR's fridge, which stood at this pier
    p.wall(38.7, 46.9, 45.4, 47.55)
    p.line([(39.5, 67.06), (42.7, 67.06)], 1, THIN, dash=DASH)
    # ---- guest wing and stair 3'-0" east; the room north of the garage goes
    Rw = grab(p, 65.5, 47.02, 66.35, 67.8); R = grab(p, 66.35, 39.25, 82.45, 67.8)
    p.white(65.5, 47.02, 82.47, 67.8); p.white(66.35, 39.25, 82.47, 47.02); p.white(82.34, 39.22, 87.62, 46.96)
    put(p, Rw, 68.5, 47.02); put(p, R, 69.35, 39.25)
    p.wall(62.28, 46.9, 69.3, 47.55)
    p.wall(82.3, 38.5, 87.54, 39.2)
    p.line([(65.5, 67.06), (68.6, 67.06)], 1, THIN, dash=DASH)
    p.window(84.63, 41.2, 85.33, 45.2)                                         # stair landing window, east wall
    # ---- mechanical and electrical room in the garage bay
    p.white(62.4, 18.62, 67.12, 24.98); p.wall(67.17, 19.4, 67.84, 24.6)
    p.white(67.13, 20.3, 67.88, 23.1); p.door((67.2, 23.1), 2.8, 'S', 'W')
    p.white(62.42, 22.6, 67.14, 24.93)
    p.rect(62.45, 22.9, 64.25, 24.9, 3, BLACK); p.line([(62.45, 22.9), (64.25, 24.9)], 1, THIN); p.line([(62.45, 24.9), (64.25, 22.9)], 1, THIN)
    p.label(63.35, 23.9, 'AHU', px=14, bg=True)
    p.rect(62.42, 18.7, 63.05, 20.3, 2, BLACK); p.label(63.55, 19.5, 'WH', px=13)
    p.rect(64.6, 18.64, 67.0, 19.0, 2, BLACK); p.label(65.8, 19.45, 'PANEL', px=13)
    p.label(65.75, 21.6, 'MECH. +\nELEC.', px=15)
    # ---- the room north of the garage is gone: its door and the wall end go with it
    p.white(82.9, 35.5, 86.2, 38.47); p.white(85.36, 39.22, 87.62, 46.96)
    p.wall(67.17, 38.5, 70.0, 39.2)
    # ---- windows touched by the changes
    p.wall(22.28, 33.0, 22.98, KN); p.line([(22.28, KN + 0.03), (22.98, KN + 0.03)], 3, BLACK)      # west window stops at the fridge with a jamb
    p.white(25.3, 18.57, 37.74, 18.72)
    p.window(27.15, 17.83, 37.74, 18.5); p.line([(32.45, 17.83), (32.45, 18.5)], 2, BLACK)         # street window: one centre mullion, both jambs
    p.rect(25.2, 18.56, 37.78, 20.7, 2, BLACK)
    # ---- sinks redrawn clean
    p.white(29.04, 27.92, 31.4, 30.52); sink_sym(p, 29.35, 28.15, 30.95, 30.3, 'E'); p.label(31.75, 29.2, 'SINK', px=12, rotate=90)
    p.white(43.25, 20.18, 45.23, 27.05); p.rect(43.22, 20.15, 45.26, 27.08, 2, BLACK)
    sink_sym(p, 43.5, 21.0, 44.75, 23.4, 'E'); p.rect(43.25, 24.3, 45.23, 26.3, 1, THIN, dash=(8, 5)); p.label(44.24, 25.3, 'DW', px=15)
    p.rect(37.8, 30.32, 39.98, 33.1, 2, BLACK, fill=WHITE); p.label(38.9, 31.75, 'WINE', px=13, rotate=90)
    # ---- court walls drawn once, clean, with both art walls against them
    p.wall(38.32, 46.88, 46.02, 47.58); p.wall(61.58, 46.88, 69.36, 47.58)
    p.white(69.38, 45.0, 69.58, 46.68)
    for a, b in ((41.17, 45.2), (62.43, 66.46)):
        p.white(a - 0.08, 44.98, b + 0.08, 46.87); p.rect(a, 45.05, b, 46.88, 2, THIN); p.label((a + b) / 2, 45.95, 'ART WALL', px=15)
    p.white(48.1, 46.7, 48.95, 47.3); p.white(59.65, 46.7, 60.5, 47.3)                        # ticks left over the plants
    # ---- guest wing north-east window: the survey tick copied with the wing comes out
    p.white(82.15, 67.04, 83.27, 68.8); p.white(82.45, 65.5, 83.0, 66.28)
    p.window(79.82, 66.3, 83.27, 67.02)
    p.line([(82.2, 67.10), (83.2, 67.10)], 2, BLACK, dash=DASH)
    # ---- garage entry as FOR drew it (owner, 11.25.26): door in the garage wall just south of the foyer line, swinging into a
    #      vestibule open to the stair hall, step on the garage side; mudroom behind a pocket door; mech room shortened
    p.white(62.36, 18.54, 67.16, 35.86); p.white(62.36, 35.4, 67.16, 36.15); p.white(67.88, 35.75, 71.05, 38.47)
    p.wall(67.17, 18.5, 67.86, 38.5); p.wall(61.58, 18.5, 62.34, 35.88)
    def opening(y0, y1):
        p.white(67.15, y0, 67.88, y1)
        for x in (67.19, 67.84): p.line([(x, y0), (x, y1)], 1, THIN, dash=(8, 6))
        for y in (y0, y1): p.line([(67.17, y), (67.86, y)], 2, BLACK)
    opening(32.95, 35.88); p.door((67.17, 32.95), 2.93, 'N', 'W')
    p.rect(67.88, 32.6, 69.4, 36.2, 2, THIN)                                              # step down to the garage slab
    p.rect(62.33, 32.42, 67.17, 32.72, 2, BLACK, fill=WHITE)                              # mudroom partition, pocket door at the west end
    p.white(62.5, 32.38, 64.95, 32.76); p.line([(62.5, 32.42), (62.5, 32.72)], 2, BLACK); p.line([(64.95, 32.42), (64.95, 32.72)], 2, BLACK)
    p.pocket((64.95, 32.57), (62.5, 32.57))
    M = (40, 40, 40)
    p.rect(62.4, 23.95, 67.12, 26.1, 2, M)                                                # lockers: tall millwork, four doors
    for x in (63.58, 64.76, 65.94): p.line([(x, 23.95), (x, 26.1)], 2, M)
    p.label(64.76, 25.0, 'LOCKERS', px=18, bg=True)
    p.rect(65.5, 26.5, 67.12, 32.0, 2, M); p.line([(66.45, 26.5), (66.45, 32.0)], 2, M, dash=DASH)   # bench, hook rail and shelf over (dashed)
    p.label(65.95, 29.25, 'BENCH', px=18, rotate=90)
    p.label(63.9, 29.3, 'MUD\nROOM')
    p.rect(62.33, 23.6, 67.17, 23.9, 2, BLACK, fill=WHITE)                                # mech room north partition
    p.rect(62.45, 21.5, 64.25, 23.5, 3, BLACK); p.line([(62.45, 21.5), (64.25, 23.5)], 1, THIN); p.line([(62.45, 23.5), (64.25, 21.5)], 1, THIN)
    p.label(63.35, 22.5, 'AHU', px=14, bg=True)
    p.rect(62.45, 18.7, 63.2, 20.6, 2, BLACK); p.label(63.75, 19.6, 'WH', px=13)
    p.rect(64.5, 18.66, 66.9, 19.0, 2, BLACK); p.label(65.7, 19.4, 'PANEL', px=12, bg=True)
    opening(19.3, 21.97); p.door((67.17, 21.97), 2.67, 'S', 'W')
    p.label(65.75, 22.8, 'MECH. +\nELEC.', px=13)
    # ---- kitchen, scullery and bar millwork redrawn in FOR's hand (owner, 11.25.26): one thin line at the counter front,
    #      long dashes for what is overhead or under the counter, tall units as plain boxes, FOR's own stool
    p.white(23.17, 18.6, 37.74, 35.84)
    p.rect(23.14, 18.56, 25.2, 30.38, 2, M); p.rect(25.2, 18.56, 37.78, 20.7, 2, M)
    p.rect(23.14, 25.05, 25.2, 29.05, 2, M, dash=DASH)                                    # hood over
    p.rrect(23.3, 25.25, 25.05, 28.85, 0.12, 2, M)
    for bx in (23.75, 24.6):
        for by in (25.9, 27.05, 28.2): p.ellipse(bx - 0.3, by - 0.3, bx + 0.3, by + 0.3, 2, M)
    p.label(26.0, 27.05, '48" RANGE', px=20, rotate=90)
    p.rect(33.6, 18.64, 35.6, 20.62, 2, M, dash=DASH); p.label(34.6, 19.63, 'MW', px=20)
    p.label(29.4, 19.63, 'BREAKFAST COUNTER', px=20)
    p.rect(23.14, 30.38, 25.43, 32.88, 2, M, fill=WHITE); p.label(24.28, 31.63, 'FREEZER', px=17, rotate=90)
    p.rect(23.14, 32.88, 25.43, KN, 2, M, fill=WHITE); p.label(24.28, 34.38, 'FRIDGE', px=19, rotate=90)
    p.rect(29.0, 24.3, 33.0, 34.0, 2, M); p.line([(31.81, 24.3), (31.81, 34.0)], 2, M, dash=DASH)
    sink_sym(p, 29.35, 28.15, 30.95, 30.3, 'E')
    p.rect(29.05, 25.9, 31.15, 27.9, 2, M, dash=DASH); p.label(30.1, 26.9, 'DW', px=20)
    p.rect(29.05, 30.55, 31.15, 32.05, 2, M, dash=DASH); p.label(30.1, 31.3, 'TRASH', px=15)
    st = FOR.crop(p.box(35.42, 42.15, 37.3, 43.9))
    for cy in (25.7, 28.0, 30.3, 32.6): put(p, st, 32.03, cy - 0.875)
    p.label(31.0, 22.4, 'KITCHEN')
    p.rect(37.8, 30.32, 39.98, 33.1, 2, M, fill=WHITE); p.rect(37.8, 33.1, 39.98, 35.56, 2, M, fill=WHITE)
    p.label(38.9, 31.7, 'WINE', px=19, rotate=90); p.label(38.9, 34.33, 'BAR', px=19, rotate=90)
    p.white(38.19, 18.6, 45.27, 29.97)
    p.rect(38.17, 18.6, 43.22, 20.65, 2, M); p.label(40.7, 19.62, 'TALL PANTRY', px=19)
    p.rect(38.17, 27.95, 43.22, 29.98, 2, M); p.label(40.7, 28.97, 'OVENS + COFFEE', px=19)
    p.rect(38.17, 25.3, 39.67, 27.95, 2, M); p.label(38.92, 26.62, 'PANTRY', px=17, rotate=90)
    p.rect(43.22, 18.6, 45.26, 29.98, 2, M); p.line([(44.2, 18.6), (44.2, 29.98)], 2, M, dash=DASH)
    sink_sym(p, 43.5, 21.0, 44.75, 23.4, 'E')
    p.rect(43.25, 24.3, 45.23, 26.3, 2, M, dash=DASH); p.label(44.24, 25.3, 'DW', px=20, bg=True)
    p.label(41.45, 24.0, 'SCULLERY', rotate=90)
    p.white(41.1, 34.0, 42.7, 34.6); p.label(41.6, 34.3, 'POWDER', px=17)
    # ==== owner approvals 11.25.26 (FP-2 items 2, 3, 4, 5, 8; FP-3 items 1 and 9)
    def smear(xs, x0, x1, y0, y1):                                   # carry what crosses column xs straight across x0..x1
        c = p.im.crop((p.X(xs), p.Y(y1), p.X(xs) + 1, p.Y(y0))); w = p.X(x1) - p.X(x0)
        p.im.paste(c.resize((w, c.height), Image.NEAREST), (p.X(x0), p.Y(y1))); p._redraw()
    W = 2.19
    # ---- 8 scullery: small pantry out
    p.white(38.2, 25.25, 39.72, 27.92)
    # ---- 9 west wall 2'-2" west to the 20'-0" setback line; the range wall goes with it, the island follows 1'-6"
    band = grab(p, 22.2, 17.4, 23.22, 67.3); cnt = grab(p, 23.22, 18.58, 25.6, 35.86); isl = grab(p, 28.9, 24.2, 34.65, 34.1)
    smear(23.3, 22.2 - W + 1.02, 23.3, 35.86, 67.3); smear(23.3, 22.2 - W + 1.02, 23.3, 17.4, 18.58)
    p.white(22.2 - W + 1.02, 18.58, 25.62, 35.86)
    put(p, cnt, 23.22 - W, 18.58); put(p, band, 22.2 - W, 17.4)
    p.white(23.05, 18.6, 25.66, 20.67)
    p.line([(23.01, 20.7), (25.66, 20.7)], 2, M); p.line([(23.01, 18.56), (25.66, 18.56)], 2, M); p.line([(23.01, 18.56), (23.01, 20.7)], 2, M)
    p.white(25.66, 25.4, 26.5, 28.7); p.label(23.85, 27.05, '48" RANGE', px=20, rotate=90)
    p.white(28.9, 24.2, 34.65, 34.1); put(p, isl, 27.4, 24.2)
    p.white(29.5, 22.0, 32.5, 22.8); p.label(30.0, 22.4, 'KITCHEN')
    p.white(23.27, 35.8, 25.6, 35.96)
    # ---- 9 guest wing and stair east wall 2'-2" east to the garage line; the bath moves with it, the closet takes the width
    eband = grab(p, 84.46, 39.25, 85.45, 67.3); bath = grab(p, 78.85, 46.68, 84.46, 56.62)
    smear(84.4, 84.4, 84.46 + W + 0.05, 56.62, 67.3); smear(84.4, 84.4, 84.46 + W + 0.05, 39.25, 46.68)
    smear(78.7, 78.7, 78.85 + W + 0.05, 46.68, 56.62)
    put(p, bath, 78.85 + W, 46.68); put(p, eband, 84.46 + W, 39.25)
    # ---- 2 pool 10'-0" wide on the axis
    p.white(47.2, 50.35, 60.45, 69.6)
    p.rect(48.3, 50.5, 59.3, 69.5, 3, BLACK); p.rect(48.8, 51.0, 58.8, 69.0, 3, BLACK)
    p.line([(48.8, 55.95), (58.8, 55.95)], 2, M, dash=DASH)
    p.label(53.8, 62.2, 'POOL\n10\'-0" x 18\'-0"', px=18); p.label(53.8, 53.4, 'SUN SHELF', px=15)
    # ---- 1 canopy on the axis, wing to wing, with a counter at each end wall
    p.rect(39.05, 47.6, 68.57, 55.6, 2, M, dash=DASH)
    p.rect(39.05, 47.6, 45.3, 49.6, 2, M); p.label(42.2, 48.6, 'GRILL', px=18)
    p.rect(62.3, 47.6, 68.57, 49.6, 2, M); p.label(65.4, 48.6, 'BAR', px=18)
    p.label(43.9, 52.6, 'COVERED\nDINING', px=18); p.label(63.7, 52.6, 'COVERED\nLOUNGE', px=18)
    p.label(53.8, 49.3, 'CANOPY OVER', px=15, bg=True)
    # ---- 3 outdoor shower on the guest wing's court wall
    p.rect(66.5, 62.8, 68.57, 65.2, 2, M); p.ellipse(67.3, 63.75, 67.8, 64.25, 2, M); p.label(64.5, 64.0, 'OUTDOOR\nSHOWER', px=15)
    # ---- 4 garage: no projecting step, both cars 6" east
    cars = grab(p, 69.5, 19.0, 86.3, 36.4); p.white(67.9, 32.5, 69.5, 36.3); p.white(69.2, 19.0, 86.6, 36.4); put(p, cars, 70.0, 19.0)
    # ---- 5 coats and buffet behind flush panels in the two recesses; service yard on the east side
    for a_, b_, t_ in ((41.17, 45.2, 'BUFFET'), (62.43, 66.46, 'COATS')):
        p.rect(a_, 45.05, b_, 46.88, 2, M, fill=WHITE)
        for f_ in (0.25, 0.5, 0.75): p.line([(a_ + (b_ - a_) * f_, 45.05), (a_ + (b_ - a_) * f_, 45.3)], 2, M)
        p.label((a_ + b_) / 2, 46.05, t_, px=15)
    p.rect(88.6, 42.0, 93.8, 58.0, 2, M, dash=DASH); p.label(91.2, 50.0, 'SERVICE\nYARD', px=18)
    # ==== area cut, option A (owner, 11.25.26): both court walls 2'-2" out, wings back to 16'-9", outer walls stay
    lv = grab(p, 23.25, 47.62, 39.1, 67.3)
    p.white(21.06, 47.62, 39.12, 67.3); put(p, lv, 23.25 - W, 47.62)
    p.wall(36.13, 46.88, 38.4, 47.58)
    p.line([(36.95, 67.10), (39.1, 67.10)], 2, BLACK, dash=DASH)
    p.rect(36.86, 47.6, 45.3, 49.6, 2, M, fill=WHITE); p.label(41.1, 48.6, 'GRILL', px=18)
    p.line([(36.86, 55.6), (39.15, 55.6)], 2, M, dash=DASH)
    # guest wing: court wall, door and closet 2'-2" east (the closet gives its extra width back); bed moves with them; stair too
    shw = grab(p, 63.2, 62.6, 68.5, 65.4)
    g1 = grab(p, 68.5, 46.68, 78.7, 56.62); g2 = grab(p, 68.5, 56.62, 84.4, 67.3); stq = grab(p, 71.4, 39.25, 84.4, 46.68)
    p.white(63.2, 62.6, 68.5, 65.4); p.white(68.5, 46.68, 70.7, 67.3); p.white(71.4, 39.25, 73.6, 46.68)
    put(p, g1, 68.5 + W, 46.68); put(p, g2, 68.5 + W, 56.62); put(p, stq, 71.4 + W, 39.25); put(p, shw, 63.2 + W, 62.6)
    p.wall(68.4, 46.88, 70.75, 47.58)
    p.line([(68.5, 67.10), (70.7, 67.10)], 2, BLACK, dash=DASH)
    p.rect(62.3, 47.6, 70.76, 49.6, 2, M, fill=WHITE); p.label(66.5, 48.6, 'BAR', px=18)
    p.line([(68.45, 55.6), (70.76, 55.6)], 2, M, dash=DASH)
    # ==== owner 11.25.26: art wall recesses (buffet, coats) out; the court's south wall drops to the court door line, one straight wall
    p.white(36.84, 44.9, 45.34, 49.66); p.white(45.3, 45.08, 46.05, 47.7); p.white(62.26, 44.9, 70.78, 49.66); p.white(61.55, 45.08, 62.3, 47.7)
    p.white(46.0, 47.42, 61.6, 47.75)
    p.wall(36.13, 44.37, 46.02, 45.07); p.wall(36.13, 44.37, 36.83, 47.62)
    p.wall(61.58, 44.37, 71.49, 45.07); p.wall(70.79, 44.37, 71.49, 47.62)
    p.rect(36.86, 45.07, 45.3, 47.07, 2, M, fill=WHITE); p.label(41.1, 46.07, 'GRILL', px=18)
    p.rect(62.3, 45.07, 70.76, 47.07, 2, M, fill=WHITE); p.label(66.5, 46.07, 'BAR', px=18)
    p.line([(36.86, 47.1), (36.86, 55.6)], 2, M, dash=DASH); p.line([(70.76, 47.1), (70.76, 55.6)], 2, M, dash=DASH)
    return p


G_OLD = dict(routes=[(GUEST, [(53.7, 13.5), (53.7, 41.3), (38.5, 41.3), (38.5, 50.5), (34, 53)]),
                     (GUEST, [(38.5, 41.3), (39.7, 30.6), (41.0, 30.6)]),
                     (SERV, [(67.5, 36.9), (65.2, 37.2), (64.6, 42.6), (40, 43.4), (27.5, 46.8)]),
                     (SERVE, [(25.6, 39.5), (28.3, 32.0), (37.0, 30.5), (39.6, 28.5), (39.6, 25.5)])],
             stops=[(1, 55.6, 38.3, GUEST), (2, 37.4, 46.2, GUEST), (3, 39.3, 33.0, GUEST), (4, 58, 44.6, SERV), (5, 33.5, 31.6, SERVE)])
G_NEW = dict(routes=[(GUEST, [(53.7, 13.5), (53.7, 41.3), (53.7, 45.6)]),
                     (GUEST, [(53.7, 41.3), (43.2, 42.6), (39.6, 46.2), (37.5, 50.5), (34, 53)]),
                     (GUEST, [(53.7, 41.3), (63.5, 42.6), (68.4, 45.6), (68.4, 48.4), (71.6, 48.4)]),
                     (SERV, [(67.5, 36.9), (60.5, 36.9), (46.5, 36.9), (41.55, 36.9), (41.55, 29.0)]),
                     (SERV, [(41.55, 36.9), (36.0, 36.9), (34.6, 35.0), (27.2, 35.0), (26.4, 33.0)]),
                     (SERVE, [(41.5, 29.0), (41.5, 22.6), (35.0, 22.6)]), (SERVE, [(31.0, 34.3), (31.0, 37.8)]), (SERVE, [(38.6, 41.1), (48, 43.6), (51.2, 46.2)])],
             stops=[(1, 55.6, 38.9, GUEST), (2, 45.3, 43.9, GUEST), (3, 66.0, 47.2, GUEST), (4, 57.6, 38.4, SERV), (5, 43.3, 31.6, SERV), (6, 29.0, 36.0, SERV), (7, 46.3, 42.2, SERVE)])
G_U = dict(routes=[(GUEST, [(53.7, 13.5), (53.7, 41.3), (53.7, 45.6)]),
                   (GUEST, [(53.7, 41.3), (43.2, 42.6), (39.6, 46.2), (37.5, 50.5), (34, 53)]),
                   (GUEST, [(53.7, 38.0), (46.5, 37.2), (43.75, 37.2), (43.75, 34.6)]),
                   (SERV, [(67.5, 36.9), (60.5, 37.6), (46.5, 37.6), (37.0, 36.9), (35.9, 34.5), (35.9, 23.0), (41.0, 23.0)]),
                   (SERV, [(37.0, 36.9), (34.6, 35.2), (27.2, 35.2), (26.4, 33.0)]),
                   (SERVE, [(31.0, 34.3), (31.0, 37.8)]), (SERVE, [(38.6, 41.1), (48, 43.6), (51.2, 46.2)])],
           stops=[(1, 55.6, 39.4, GUEST), (2, 45.3, 44.1, GUEST), (3, 46.6, 35.0, GUEST), (4, 57.6, 39.2, SERV), (5, 36.9, 28.0, SERV), (6, 29.0, 36.2, SERV), (7, 46.3, 42.2, SERVE)])
GM_OLD = dict(routes=[(SERV, [(73.0, 36.6), (67.5, 36.9), (64.6, 37.2), (62.15, 37.4), (57.5, 37.6), (48.0, 37.6)]),
                      (SERV, [(57.5, 37.6), (66.0, 41.0), (70.5, 41.0)]), (SERV, [(66.0, 41.0), (68.4, 44.0), (68.4, 47.8)]),
                      (SERVE, [(64.8, 36.0), (64.8, 27.0)])],
              stops=[(1, 65.6, 35.6, SERV), (2, 60.4, 39.0, SERV), (3, 65.9, 30.0, SERVE)])
GM_NEW = dict(routes=[(SERV, [(73.0, 36.6), (69.4, 36.9), (65.8, 36.9), (65.8, 40.6)]),
                      (SERV, [(65.8, 40.6), (57.0, 39.6), (48.0, 37.8)]), (SERV, [(65.8, 40.6), (68.2, 41.0), (70.5, 41.0)]),
                      (SERV, [(65.8, 40.6), (68.4, 44.0), (68.4, 47.8)]), (SERVE, [(71.5, 24.6), (66.4, 24.6)])],
              stops=[(1, 71.8, 38.0, SERV), (2, 65.3, 31.6, SERV), (3, 63.6, 41.8, SERV), (4, 65.5, 26.4, SERVE)])
GM3 = dict(routes=GM_NEW['routes'] + [(GUEST, [(54.0, 40.5), (62.5, 42.0), (68.6, 44.9)]), (SERVE, [(80.0, 36.5), (84.3, 37.4), (84.3, 40.0)])],
           stops=GM_NEW['stops'] + [(5, 67.6, 43.2, GUEST), (6, 82.0, 35.4, SERVE)])
GM4 = dict(routes=[(SERV, [(72.5, 36.6), (69.2, 36.3), (68.9, 33.4), (65.6, 33.4), (65.6, 39.6)]),
                   (SERV, [(65.6, 39.6), (57.0, 38.8), (48.0, 37.8)]), (SERV, [(65.6, 39.6), (68.2, 41.0), (70.5, 41.0)]),
                   (SERV, [(65.6, 39.6), (68.4, 44.0), (68.4, 47.8)]), (SERVE, [(69.6, 23.2), (66.2, 23.2)]),
                   (SERVE, [(80.0, 36.5), (84.3, 37.4), (84.3, 40.0)])],
           stops=[(1, 69.9, 37.6, SERV), (2, 65.4, 31.2, SERV), (3, 63.4, 40.6, SERV), (4, 68.9, 21.6, SERVE), (5, 71.2, 46.0, GUEST), (6, 86.0, 37.4, SERVE)])
GM5 = dict(routes=[(SERV, [(73.0, 37.3), (69.4, 37.2), (65.6, 37.2), (65.6, 39.8)]), (SERV, [(65.6, 37.2), (65.3, 33.2)]),
                   (SERV, [(65.6, 39.8), (57.0, 38.9), (48.0, 37.8)]), (SERV, [(65.6, 39.8), (68.0, 41.0), (70.5, 41.0)]),
                   (SERV, [(65.6, 39.8), (68.2, 46.0), (68.4, 47.8)]), (SERVE, [(69.6, 23.2), (66.2, 23.2)]),
                   (SERVE, [(80.0, 36.5), (84.3, 36.6), (84.3, 38.2)])],
           stops=[(1, 71.9, 38.0, SERV), (2, 65.4, 29.2, SERV), (3, 63.3, 40.8, SERV), (4, 68.9, 21.6, SERVE), (5, 72.3, 45.9, GUEST), (6, 86.0, 37.2, SERVE)])
G_K3 = dict(routes=[r if i != 4 else (SERV, [(37.0, 36.9), (30.0, 36.6), (27.2, 35.6), (26.3, 34.4)]) for i, r in enumerate(G_U['routes'])], stops=G_U['stops'])
M_OLD = dict(routes=[(SERV, [(33.5, 36.4), (37.1, 36.2), (37.1, 27.4), (44.6, 27.4), (46.2, 26.2)]),
                     (SERV, [(37.1, 27.4), (33.5, 26.6), (30.5, 26.0)]), (GUEST, [(37.1, 32.2), (35.2, 32.2), (33, 32.2)]), (GUEST, [(37.1, 32.2), (40.5, 32.2)])],
             stops=[(1, 37.1, 34.0, SERV), (2, 41, 27.4, SERV), (3, 38.6, 31.0, GUEST)])
M_NEW = dict(routes=[(SERV, [(30.5, 36.4), (33.4, 36.3), (33.4, 28.6), (36.75, 28.6), (36.75, 30.2)]),
                     (SERV, [(36.75, 27.0), (40.2, 27.0), (42.6, 28.0), (42.6, 36.5), (45.2, 40.0), (45.4, 43.6), (48.6, 44.8)])],
             stops=[(1, 33.4, 33.0, SERV), (2, 31.2, 26.2, SERV), (3, 40.0, 27.0, SERV), (4, 42.6, 33.3, SERV)])

def second_final(follow):
    """The owner's second floor after the first floor moves of 11.25.26: stair and junior master wing 3'-0" east and their east
    wall 2'-2" further (one straight east wall, the W.I.C. by the stair goes); terrace trimmed to the living room below;
    west wall either held (planter ledge 5'-2") or carried 2'-2" west with the floor below (follow)."""
    p = master_new(RP.second(RP.ground())); W = 2.19; S = 3.0
    def smear(xs, x0, x1, y0, y1):
        c = p.im.crop((p.X(xs), p.Y(y1), p.X(xs) + 1, p.Y(y0))); w = p.X(x1) - p.X(x0)
        p.im.paste(c.resize((w, c.height), Image.NEAREST), (p.X(x0), p.Y(y1))); p._redraw()
    # ---- wing 2'-2" wider: bath 2 moves with the east wall, the closet takes the width
    eb = grab(p, 81.45, 46.87, 82.45, 67.3); b2 = grab(p, 75.4, 46.87, 81.45, 56.62); es = grab(p, 81.45, 39.3, 82.45, 46.87)
    smear(75.4, 75.4, 75.4 + W + 0.05, 46.87, 56.62); smear(81.2, 81.2, 81.45 + W + 0.05, 56.62, 67.3); smear(81.2, 81.2, 81.45 + W + 0.05, 39.3, 46.87)
    put(p, b2, 75.4 + W, 46.87); put(p, eb, 81.45 + W, 46.87); put(p, es, 81.45 + W, 39.3)
    # ---- stair and wing 3'-0" east
    st = grab(p, 69.6, 39.3, 84.7, 46.87); wg = grab(p, 65.5, 46.87, 84.7, 67.3)
    p.white(69.6, 39.3, 86.8, 46.87); p.white(65.5, 46.87, 86.8, 67.3)
    put(p, st, 69.6 + S, 39.3); put(p, wg, 65.5 + S, 46.87)
    p.wall(65.5, 46.87, 68.62, 57 - 9.43)
    p.window(86.83, 41.2, 87.56, 45.2)
    p.white(85.4, 37.75, 85.8, 39.2); p.white(87.58, 38.8, 88.0, 47.8)
    p.white(84.55, 39.03, 85.45, 39.33); p.white(85.4, 67.06, 86.2, 68.6)
    # ---- terrace and north planter end at the living room's east wall, 3'-0" further west
    tb = grab(p, 41.3, 47.62, 42.3, 67.7); p.white(38.25, 47.62, 42.35, 67.7); put(p, tb, 41.3 - S, 47.62)
    # ---- area cut, option A: the wing's court wall 2'-2" east (closet gives the width back), stair with it; terrace 2'-2" narrower
    j1 = grab(p, 68.5, 46.87, 78.4, 56.62); j2 = grab(p, 68.5, 56.62, 84.2, 67.3); js = grab(p, 72.6, 39.3, 84.2, 46.87)
    p.white(68.5, 46.87, 70.7, 67.3); p.white(72.6, 39.3, 74.8, 46.87)
    put(p, j1, 68.5 + W, 46.87); put(p, j2, 68.5 + W, 56.62); put(p, js, 72.6 + W, 39.3)
    p.wall(68.5, 46.87, 70.82, 47.57)
    fx = grab(p, 27.6, 48.6, 38.22, 62.8)
    tb2 = grab(p, 38.25, 47.62, 39.35, 67.7); p.white(36.0, 47.62, 39.4, 67.7); put(p, tb2, 38.25 - W, 47.62)
    p.white(27.6, 48.6, 36.0, 62.8); put_dark(p, fx, 27.6 - 2.25, 48.6)          # terrace furniture back onto the narrower terrace
    # ---- west side
    if follow:
        p.slide(21.9, 21.6, 31.6, 47.62, dx=-W, fill='smear'); p.slide(21.9, 47.62, 26.0, 63.55, dx=-W, fill='smear')
        p.slide(21.9, 63.55, 25.9, 67.8, dx=-W, fill='tile'); p.slide(21.9, 16.8, 25.0, 21.6, dx=-W, fill='tile')
    else:
        p.slide(21.9, 16.8, 23.0, 67.8, dx=-W, fill='tile')
        put(p, grab(p, 21.3, 30.0, 22.15, 33.8), 21.3, 40.0)                   # the tile carried a second PLANTER label
    return p


def length(pts): return sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 for a, b in zip(pts, pts[1:]))

if __name__ == '__main__':
    g = RP.ground(); g.save(os.path.join(OUT, 'g_old.png')); g.routes(**G_OLD).save(os.path.join(OUT, 'g_old_r.png'))
    n = ground_new(RP.ground()); n.save(os.path.join(OUT, 'g_new.png')); n.routes(**G_NEW).save(os.path.join(OUT, 'g_new_r.png'))
    s = RP.second(g); s.save(os.path.join(OUT, 'm_old.png')); s.routes(**M_OLD).save(os.path.join(OUT, 'm_old_r.png'))
    m = master_new(RP.second(g)); m.save(os.path.join(OUT, 'm_new.png')); m.routes(**M_NEW).save(os.path.join(OUT, 'm_new_r.png'))
    for name, R in (('G_OLD', G_OLD), ('G_NEW', G_NEW), ('M_OLD', M_OLD), ('M_NEW', M_NEW)):
        print(name, [round(length(pts), 1) for _, pts in R['routes']])
    for v in 'AB': ground_new(RP.ground(), v).save(os.path.join(OUT, 'g_%s.png' % v))
    u = ground_new(RP.ground(), 'FOR', 'U'); u.save(os.path.join(OUT, 'g_U.png')); u.routes(**G_U).save(os.path.join(OUT, 'g_U_r.png'))
    print('G_U', [round(length(pts), 1) for _, pts in G_U['routes']])
    k = ground_new(RP.ground(), 'FOR', 'K'); k.save(os.path.join(OUT, 'g_K.png')); k.routes(**G_U).save(os.path.join(OUT, 'g_K_r.png'))
    k = ground_new(RP.ground(), 'FOR', 'K3'); k.save(os.path.join(OUT, 'g_K3.png')); k.routes(**G_K3).save(os.path.join(OUT, 'g_K3_r.png'))
    k.routes(**GM_OLD).save(os.path.join(OUT, 'gm_old_r.png'))
    m2 = ground_new(RP.ground(), 'FOR', 'K3', 'M2'); m2.save(os.path.join(OUT, 'g_M2.png')); m2.routes(**GM_NEW).save(os.path.join(OUT, 'gm_new_r.png'))
    m3 = ground_new(RP.ground(), 'FOR', 'K3', 'M3'); m3.save(os.path.join(OUT, 'g_M3.png')); m3.routes(**GM3).save(os.path.join(OUT, 'gm3_r.png'))
    m4 = ground_new(RP.ground(), 'FOR', 'K3', 'M4'); m4.save(os.path.join(OUT, 'g_M4.png')); m4.routes(**GM4).save(os.path.join(OUT, 'gm4_r.png'))
    m5 = ground_new(RP.ground(), 'FOR', 'K3', 'M5'); m5.save(os.path.join(OUT, 'g_M5.png')); m5.routes(**GM5).save(os.path.join(OUT, 'gm5_r.png'))
    ground_new(RP.ground(), 'FOR', 'K3', 'M6').save(os.path.join(OUT, 'g_M6.png'))
    ground_final().save(os.path.join(OUT, 'g_FINAL.png'))
    print('layouts done')
