"""2191 SW 23rd St (HD103): owner options drawn on the revised FOR plans (hd103/revise_plans.py).
Kitchen on the south side (two ways) and a reworked master bath (two ways). Every option reuses FOR's own symbols.

    python3 hd103/options.py OUTDIR
"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/hd103')
from PIL import Image
from idd_revise import Plan, BLACK, THIN, FURN, WHITE
import revise_plans as RP

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/rev/opt'
os.makedirs(OUT, exist_ok=True)


def grab(p, x0, y0, x1, y1): return p.im.crop(p.box(x0, y0, x1, y1))
def put(p, img, x, y, rotate=0, flip=None):
    if flip == 'v': img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if flip == 'h': img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate: img = img.rotate(rotate, expand=True, fillcolor=WHITE)
    p.im.paste(img, (p.X(x), p.Y(y) - img.height)); p._redraw()


# ------------------------------------------------------------------ kitchen on the south side
def kitchen_south(p, variant):
    """Kitchen moves to the street end beside the scullery; dining takes the middle, beside the foyer and the court.
    The west wall's windows and solid piers stay where FOR drew them: the sink sits under the small south window and the
    tall units stand on the solid pier (y 24.8 to 33.6)."""
    isl = grab(p, 29.9, 34.3, 36.0, 44.8); tbl = grab(p, 28.3, 19.2, 34.6, 30.4); bar = grab(p, 23.08, 18.95, 25.3, 27.18)
    frg = grab(p, 23.08, 45.72, 25.45, 48.9); snk = grab(p, 23.08, 38.42, 25.3, 40.85); dw = grab(p, 23.08, 40.85, 25.3, 43.0)
    ovn = grab(p, 23.08, 30.25, 25.45, 33.3)
    p.white(23.08, 18.56, 25.5, 49.0); p.white(29.9, 34.3, 36.0, 44.8); p.white(30.8, 45.4, 34.0, 46.6); p.white(28.3, 19.2, 34.6, 30.4)
    # kitchen run on the west wall
    p.rect(23.08, 18.56, 25.2, 27.2, 2, BLACK)
    put(p, snk, 23.08, 21.8); put(p, dw, 23.08, 24.3); put(p, frg, 23.08, 27.2); put(p, ovn, 23.08, 30.3)
    # dining in the middle, FOR's table and dry bar
    put(p, tbl, 29.2, 35.6); put(p, bar, 23.08, 35.8)
    if variant == 'B':        # FOR's island, cooktop and four stools, moved as drawn
        put(p, isl, 28.9, 21.9)
        p.label(31.5, 20.3, 'KITCHEN')
    else:                     # range wall on the scullery wall, prep island
        p.rect(35.7, 20.5, 37.78, 26.9, 2, BLACK)             # range run stops short of the street window
        p.rect(35.7, 21.6, 37.78, 25.6, 2, BLACK)
        for bx in (36.25, 37.2):
            for by in (22.3, 23.6, 24.9): p.ellipse(bx - 0.33, by - 0.33, bx + 0.33, by + 0.33, 2, BLACK)
        p.label(34.9, 23.6, '48" RANGE + HOOD', px=17, rotate=90)
        p.rect(29.1, 22.2, 32.1, 29.2, 2, BLACK); p.label(30.6, 25.7, 'ISLAND', px=18)
        p.label(30.6, 20.3, 'KITCHEN')
    return p


# ------------------------------------------------------------------ master bath
def master_a(p):
    """Inside FOR's walls: the bath takes the west 12'-6" at full depth, one dressing room takes the east 9'-3"."""
    toilet = grab(p, 45.55, 22.72, 46.95, 25.15); sink = grab(p, 35.72, 22.76, 37.25, 24.3); valve = grab(p, 31.35, 22.56, 32.15, 23.25)
    p.white(25.98, 22.56, 48.05, 35.03)
    p.partition(25.98, 34.65, 48.1, 35.0)                       # bedroom wall, whole, then the two openings
    p.white(35.3, 34.6, 38.0, 35.05); p.pocket((35.3, 34.82), (38.0, 34.82))
    p.white(41.9, 34.6, 44.9, 35.05); p.line([(41.9, 34.82), (44.9, 34.82)], 1, FURN, dash=(8, 6))
    p.partition(38.5, 22.55, 38.85, 34.65)                      # bath / dressing room
    # bath: tub free on the west window, water closet in the northwest corner, shower beside it, vanity on the east wall
    p.rrect(26.25, 22.95, 28.85, 28.35, r=0.9, w=2, color=BLACK); p.ellipse(26.6, 23.45, 28.5, 27.85, 1, FURN); p.ellipse(27.4, 23.6, 27.7, 23.9, 2, BLACK)
    p.partition(29.3, 30.15, 29.55, 34.65)                      # water closet east wall
    p.partition(25.98, 30.15, 26.4, 30.4); p.partition(28.9, 30.15, 29.55, 30.4)
    p.pocket((26.4, 30.27), (28.9, 30.27))                      # pocket door: a swing would land on the tub
    put(p, toilet, 26.95, 31.95, flip='v'); p.label(27.65, 31.0, 'WC', px=17)
    p.rect(36.4, 22.56, 38.5, 31.6, 2, BLACK)
    put(p, sink, 36.75, 23.7, rotate=90); put(p, sink, 36.75, 28.1, rotate=90)
    p.rect(29.55, 30.3, 32.3, 30.5, 2, BLACK, fill=WHITE); p.line([(32.3, 30.4), (34.9, 30.4)], 1, FURN, dash=(8, 6))
    p.rect(34.9, 30.3, 35.1, 34.65, 2, BLACK, fill=WHITE)
    p.line([(29.6, 30.55), (34.85, 34.6)], 1, FURN); p.line([(29.6, 34.6), (34.85, 30.55)], 1, FURN)
    p.rect(31.8, 32.15, 32.65, 33.0, 1, THIN, dash=(8, 5)); put(p, valve, 30.6, 33.95, flip='v')
    p.rect(29.6, 22.56, 33.2, 24.2, 2, BLACK); p.label(31.4, 23.38, 'LINEN', px=16)
    p.label(32.6, 27.4, 'MASTER\nBATH')
    # dressing room
    for a, b in ((38.87, 40.85), (46.1, 48.05)):
        p.rect(a, 22.58, b, 34.62, 2, THIN); p.line([((a + b) / 2, 22.6), ((a + b) / 2, 34.6)], 1, FURN, dash=(14, 8))
    p.rect(42.0, 22.75, 45.0, 24.25, 2, THIN); p.label(43.5, 23.5, 'BENCH', px=15)
    p.label(43.5, 29.3, 'DRESSING\nROOM')
    return p


def master_b(p):
    """Bath extended 4'-0" south to the ground floor wall line (over the dining room); FOR's closets and water closet stay."""
    sink = grab(p, 35.72, 22.76, 37.25, 24.3); valve = grab(p, 31.35, 22.56, 32.15, 23.25)
    p.white(22.2, 17.2, 46.7, 21.79)                            # south planter
    p.white(25.98, 21.7, 45.28, 22.58); p.white(25.98, 18.52, 44.18, 28.66); p.white(44.18, 18.52, 45.3, 22.5)
    p.wall(25.29, 17.81, 25.96, 21.95); p.wall(25.29, 17.81, 45.99, 18.5); p.wall(45.3, 18.5, 45.99, 22.51); p.wall(44.2, 21.82, 45.35, 22.51)
    p.line([(22.3, 21.8), (25.29, 21.8)], 2, THIN)
    p.wall(25.29, 21.6, 25.96, 22.65)
    p.window(34.6, 17.81, 39.6, 18.5)
    p.rrect(34.4, 19.0, 39.8, 21.7, r=0.9, w=2, color=BLACK); p.ellipse(34.9, 19.35, 39.3, 21.35, 1, FURN); p.ellipse(35.3, 20.2, 35.6, 20.5, 2, BLACK)
    p.rect(27.6, 26.6, 35.2, 28.66, 2, BLACK); put(p, sink, 28.9, 26.8, flip='v'); put(p, sink, 32.3, 26.8, flip='v')
    p.rect(25.98, 23.0, 29.0, 23.2, 2, BLACK, fill=WHITE); p.line([(29.0, 23.1), (31.5, 23.1)], 1, FURN, dash=(8, 6))
    p.rect(31.5, 18.52, 31.7, 23.2, 2, BLACK, fill=WHITE)
    p.line([(26.05, 18.6), (31.45, 22.95)], 1, FURN); p.line([(26.05, 22.95), (31.45, 18.6)], 1, FURN)
    p.rect(28.35, 20.35, 29.2, 21.2, 1, THIN, dash=(8, 5)); put(p, valve, 27.0, 18.56)
    p.rect(40.8, 18.56, 45.25, 20.2, 2, BLACK); p.label(43.0, 19.4, 'LINEN', px=16)
    p.label(37.1, 24.4, 'MASTER\nBATH')
    return p


if __name__ == '__main__':
    g = RP.ground(); g.save(os.path.join(OUT, 'k_current.png'))
    kitchen_south(RP.ground(), 'A').save(os.path.join(OUT, 'k_A.png'))
    kitchen_south(RP.ground(), 'B').save(os.path.join(OUT, 'k_B.png'))
    RP.second(g).save(os.path.join(OUT, 'm_current.png'))
    master_a(RP.second(g)).save(os.path.join(OUT, 'm_A.png'))
    master_b(RP.second(g)).save(os.path.join(OUT, 'm_B.png'))
    print('options done')
