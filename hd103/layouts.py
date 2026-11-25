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


def ground_new(p, guest='R4', scullery='THRU'):
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
    # ---- dining in the middle, clear of the walk from the foyer to the living room; the long west window is left free
    put(p, tbl, 26.1, 37.95, rotate=90); p.white(31.1, 39.6, 32.3, 42.6); p.label(31.7, 41.1, 'DINING', bg=True)
    # ---- mudroom closed: the garage door now opens into it, and its own door faces down the foyer's south wall
    p.partition(62.3, 38.75, 67.3, 39.05); p.partition(62.0, 35.8, 62.3, 39.05)
    p.white(61.95, 36.05, 62.35, 38.75); p.door((62.15, 36.05), 2.7, 'N', 'W')
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
M_OLD = dict(routes=[(SERV, [(33.5, 36.4), (37.1, 36.2), (37.1, 27.4), (44.6, 27.4), (46.2, 26.2)]),
                     (SERV, [(37.1, 27.4), (33.5, 26.6), (30.5, 26.0)]), (GUEST, [(37.1, 32.2), (35.2, 32.2), (33, 32.2)]), (GUEST, [(37.1, 32.2), (40.5, 32.2)])],
             stops=[(1, 37.1, 34.0, SERV), (2, 41, 27.4, SERV), (3, 38.6, 31.0, GUEST)])
M_NEW = dict(routes=[(SERV, [(30.5, 36.4), (33.4, 36.3), (33.4, 28.6), (36.75, 28.6), (36.75, 30.2)]),
                     (SERV, [(36.75, 27.0), (40.2, 27.0), (42.6, 28.0), (42.6, 36.5), (45.2, 40.0), (45.4, 43.6), (48.6, 44.8)])],
             stops=[(1, 33.4, 33.0, SERV), (2, 31.2, 26.2, SERV), (3, 40.0, 27.0, SERV), (4, 42.6, 33.3, SERV)])

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
    print('layouts done')
