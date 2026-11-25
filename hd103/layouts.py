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
GUEST = (25, 95, 200); SERV = (225, 120, 0); SERVE = (20, 140, 70)


def grab(p, x0, y0, x1, y1): return p.im.crop(p.box(x0, y0, x1, y1))
def put(p, img, x, y, rotate=0, flip=None):
    if flip == 'v': img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if flip == 'h': img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate: img = img.rotate(rotate, expand=True, fillcolor=WHITE)
    p.im.paste(img, (p.X(x), p.Y(y) - img.height)); p._redraw()
def stool(p, cx, cy, r=0.68): p.ellipse(cx - r, cy - r, cx + r, cy + r, 2, FURN)


def ground_new(p):
    tbl = grab(p, 28.3, 19.2, 34.6, 30.4); bar = grab(p, 23.08, 18.95, 25.3, 27.18); snk = grab(p, 23.08, 38.42, 25.3, 40.85)
    sce = grab(p, 43.22, 20.15, 45.26, 27.08)                                    # FOR's scullery sink and dishwasher run
    ptoilet = grab(p, 42.6, 31.05, 44.1, 33.62); psink = grab(p, 42.62, 27.42, 44.12, 28.92)
    # ---- clear what moves
    p.white(23.08, 18.56, 25.5, 49.0); p.white(29.9, 34.3, 36.0, 44.8); p.white(30.8, 45.4, 34.0, 46.6); p.white(28.3, 19.2, 34.6, 30.4)
    p.white(37.7, 18.56, 45.28, 35.05)
    # ---- scullery: the whole block, a through room (kitchen on the west, foyer on the north)
    p.partition(37.8, 18.56, 38.15, 34.1); p.partition(37.8, 33.8, 45.3, 34.1)
    p.white(37.74, 27.0, 38.21, 30.5); p.line([(37.97, 27.0), (37.97, 30.5)], 1, FURN, dash=(8, 6))
    p.white(40.1, 33.74, 42.9, 34.16); p.pocket((40.1, 33.95), (42.9, 33.95))
    put(p, sce, 43.22, 20.15); p.rect(43.22, 18.6, 45.26, 20.15, 2, BLACK); p.rect(43.22, 27.08, 45.26, 33.78, 2, BLACK)
    p.label(44.24, 30.4, 'OVENS + COFFEE', px=15, rotate=90)
    p.rect(38.17, 18.6, 43.22, 20.0, 2, BLACK); p.label(40.7, 19.3, 'TALL PANTRY', px=15)
    p.rect(38.17, 20.0, 39.9, 26.6, 2, BLACK); p.label(39.03, 23.3, 'PANTRY', px=15, rotate=90)
    p.rect(38.17, 30.9, 40.0, 33.78, 2, BLACK); p.label(39.08, 32.34, 'FREEZER', px=12)
    p.label(41.55, 25.2, 'SCULLERY', px=17, rotate=90)
    # ---- kitchen at the street end: range and fridge on the solid pier, sink in the island facing them (a 17' triangle)
    p.rect(23.08, 18.56, 25.2, 33.3, 2, BLACK)
    p.rect(23.08, 25.6, 25.2, 29.6, 2, BLACK)
    for bx in (23.7, 24.65):
        for by in (26.3, 27.6, 28.9): p.ellipse(bx - 0.33, by - 0.33, bx + 0.33, by + 0.33, 2, BLACK)
    p.label(26.05, 27.6, '48" RANGE + HOOD', px=15, rotate=90)
    p.rect(23.08, 30.25, 25.4, 33.3, 2, BLACK, fill=WHITE); p.label(24.24, 31.78, 'FRIDGE', px=15, rotate=90)
    p.rect(25.2, 18.56, 37.78, 20.7, 2, BLACK); p.label(31.5, 19.63, 'COFFEE + BREAKFAST BAR', px=15)
    p.rect(28.8, 24.3, 32.3, 32.3, 2, BLACK)
    put(p, snk, 29.45, 26.3, flip='h'); p.rect(28.85, 28.95, 30.95, 30.95, 1, THIN, dash=(8, 5)); p.label(29.9, 29.95, 'DW', px=15)
    p.label(30.55, 31.65, 'ISLAND', px=15); p.label(30.55, 25.2, 'SINK', px=13)
    for cy in (26.2, 28.2, 30.2): stool(p, 33.15, cy)
    p.label(31.2, 22.5, 'KITCHEN')
    # ---- dining in the middle, clear of the walk from the foyer to the living room; FOR's bar under the long west window
    put(p, tbl, 27.6, 36.45, rotate=90); p.white(32.6, 38.1, 33.8, 41.1); p.label(33.2, 39.6, 'DINING', bg=True)
    put(p, bar, 23.08, 35.8)
    # ---- powder room: out of the kitchen, into the south end of the guest closet, off a vestibule by the stair
    p.white(70.56, 47.3, 75.62, 52.5); p.partition(70.5, 52.2, 75.7, 52.5)
    p.white(70.1, 47.35, 70.56, 49.85); p.pocket((70.33, 49.85), (70.33, 47.35))
    put(p, ptoilet, 71.3, 49.55); p.rect(73.9, 47.35, 75.62, 50.6, 2, BLACK); put(p, psink, 74.02, 48.2, rotate=90)
    p.label(72.6, 48.4, 'POWDER', px=14); p.label(73.1, 54.5, 'CLOSET', px=16, bg=True)
    p.white(66.38, 46.55, 69.95, 50.45)
    p.partition(66.3, 49.85, 66.95, 50.15); p.partition(69.95, 49.85, 70.2, 50.15); p.door((69.95, 50.0), 3.0, 'W', 'N')
    # ---- mudroom closed: the garage door now opens into it, and its own door faces down the foyer's south wall
    p.partition(62.3, 38.75, 67.3, 39.05); p.partition(62.0, 35.8, 62.3, 39.05)
    p.white(61.95, 36.05, 62.35, 38.75); p.door((62.15, 36.05), 2.7, 'N', 'W')
    return p


def master_new(p):
    """Loop suite inside FOR's walls: bedroom to bath, bath to dressing room, dressing room to bedroom."""
    toilet = grab(p, 45.55, 22.72, 46.95, 25.15); sink = grab(p, 35.72, 22.76, 37.25, 24.3); valve = grab(p, 31.35, 22.56, 32.15, 23.25)
    p.white(25.98, 22.56, 48.05, 35.03)
    p.partition(25.98, 34.65, 48.1, 35.0)
    p.white(35.6, 34.6, 38.3, 35.05); p.pocket((35.6, 34.82), (38.3, 34.82))                 # bedroom to bath
    p.white(41.95, 34.6, 44.95, 35.05); p.line([(41.95, 34.82), (44.95, 34.82)], 1, FURN, dash=(8, 6))   # bedroom to dressing
    p.partition(38.5, 22.55, 38.85, 34.65)
    p.white(38.45, 25.6, 38.9, 28.3); p.pocket((38.67, 28.3), (38.67, 25.6))                 # bath to dressing
    # tub at the west window
    p.rrect(26.3, 22.95, 29.0, 28.65, r=0.9, w=2, color=BLACK); p.ellipse(26.65, 23.45, 28.65, 28.15, 1, FURN); p.ellipse(27.5, 23.6, 27.8, 23.9, 2, BLACK)
    # vanity on the south wall, the window between the two mirrors
    p.rect(30.9, 22.56, 38.5, 24.65, 2, BLACK); put(p, sink, 31.75, 22.76); put(p, sink, 35.95, 22.76)
    p.rect(29.5, 22.56, 30.9, 24.65, 2, BLACK); p.label(30.2, 23.6, 'LINEN', px=13, rotate=90)
    # shower in the northwest corner
    p.rect(26.0, 30.45, 28.6, 30.65, 2, BLACK, fill=WHITE); p.line([(28.6, 30.55), (31.3, 30.55)], 1, FURN, dash=(8, 6))
    p.partition(31.4, 30.45, 31.75, 34.65)
    p.line([(26.05, 30.7), (31.35, 34.6)], 1, FURN); p.line([(26.05, 34.6), (31.35, 30.7)], 1, FURN)
    p.rect(28.3, 32.25, 29.15, 33.1, 1, THIN, dash=(8, 5)); put(p, valve, 27.0, 33.95, flip='v')
    # water closet beside it, door on its south side
    p.partition(35.15, 29.5, 35.4, 34.65); p.partition(31.4, 29.5, 32.1, 29.75); p.partition(34.6, 29.5, 35.4, 29.75); p.partition(31.4, 29.5, 31.75, 30.6)
    p.pocket((32.1, 29.62), (34.6, 29.62)); put(p, toilet, 32.75, 32.2, flip='v'); p.label(33.45, 30.9, 'WC', px=16)
    p.label(33.6, 27.1, 'MASTER\nBATH')
    # dressing room
    p.rect(46.05, 22.58, 48.05, 34.62, 2, THIN); p.line([(47.05, 22.6), (47.05, 34.6)], 1, FURN, dash=(14, 8))
    p.rect(38.87, 29.0, 40.85, 34.62, 2, THIN); p.line([(39.86, 29.0), (39.86, 34.6)], 1, FURN, dash=(14, 8))
    p.rect(38.87, 22.58, 40.3, 25.1, 2, THIN); p.label(39.6, 23.85, 'SHOES', px=13, rotate=90)
    p.rect(41.2, 22.6, 45.6, 24.2, 2, THIN); p.label(43.4, 23.4, 'DRESSER', px=15)
    p.label(44.45, 30.2, 'DRESSING\nROOM', px=17)
    return p


G_OLD = dict(routes=[(GUEST, [(53.7, 13), (53.7, 41.3), (38.5, 41.3), (38.5, 50.5), (34, 53)]),
                     (GUEST, [(38.5, 41.3), (39.7, 30.6), (41.0, 30.6)]),
                     (SERV, [(69.5, 36.9), (65.2, 37.2), (64.6, 42.6), (40, 43.4), (27.5, 46.8)]),
                     (SERVE, [(28.3, 39.5), (28.3, 32.0), (37.0, 30.5), (39.6, 28.5), (39.6, 25.5)])],
             stops=[(1, 53.7, 38.3, GUEST), (2, 37.4, 46.2, GUEST), (3, 39.3, 33.0, GUEST), (4, 58, 44.6, SERV), (5, 33.5, 31.6, SERVE)])
G_NEW = dict(routes=[(GUEST, [(53.7, 13), (53.7, 41.3), (53.7, 45.6)]),
                     (GUEST, [(53.7, 41.3), (43.2, 42.3), (40.2, 45.3), (37.5, 50.5), (34, 53)]),
                     (GUEST, [(53.7, 41.3), (63.5, 42.6), (68.4, 45.6), (68.4, 48.6), (71.6, 48.6)]),
                     (SERV, [(69.5, 36.9), (60.5, 36.9), (46.5, 36.9), (41.5, 35.4), (41.5, 28.8), (36.6, 28.8), (35.3, 33.3), (26.6, 33.3)]),
                     (SERVE, [(34.6, 31.6), (34.6, 36.0)]), (SERVE, [(39.6, 39.6), (48, 43.2), (51.2, 46.2)])],
             stops=[(1, 53.7, 38.9, GUEST), (2, 45.3, 43.9, GUEST), (3, 66.0, 45.6, GUEST), (4, 57, 38.3, SERV), (5, 43.2, 30.5, SERV), (6, 46.0, 40.6, SERVE)])
M_OLD = dict(routes=[(SERV, [(35.5, 40.5), (37.1, 36.2), (37.1, 27.4), (44.6, 27.4), (46.2, 26.2)]),
                     (SERV, [(37.1, 27.4), (33.5, 26.6), (30.5, 26.0)]), (GUEST, [(37.1, 32.2), (35.2, 32.2), (33, 32.2)]), (GUEST, [(37.1, 32.2), (40.5, 32.2)])],
             stops=[(1, 37.1, 34.0, SERV), (2, 41, 27.4, SERV), (3, 38.6, 31.0, GUEST)])
M_NEW = dict(routes=[(SERV, [(35.5, 40.5), (36.95, 36.3), (36.95, 28.6), (34.6, 28.6), (33.4, 29.4)]),
                     (SERV, [(36.95, 27.0), (40.2, 27.0), (42.6, 28.0), (42.6, 36.5), (47.0, 41.5), (48.6, 44.6)])],
             stops=[(1, 36.95, 33.0, SERV), (2, 31.0, 26.0, SERV), (3, 40.0, 27.0, SERV), (4, 42.6, 33.3, SERV)])

if __name__ == '__main__':
    g = RP.ground(); g.save(os.path.join(OUT, 'g_old.png')); g.routes(**G_OLD).save(os.path.join(OUT, 'g_old_r.png'))
    n = ground_new(RP.ground()); n.save(os.path.join(OUT, 'g_new.png')); n.routes(**G_NEW).save(os.path.join(OUT, 'g_new_r.png'))
    s = RP.second(g); s.save(os.path.join(OUT, 'm_old.png')); s.routes(**M_OLD).save(os.path.join(OUT, 'm_old_r.png'))
    m = master_new(RP.second(g)); m.save(os.path.join(OUT, 'm_new.png')); m.routes(**M_NEW).save(os.path.join(OUT, 'm_new_r.png'))
    print('layouts done')
