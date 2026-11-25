"""2191 SW 23rd St (HD103): FP-2, the owner's first floor with proposed fixes marked in red (not yet drawn into the plan).
    python3 hd103/build_first_floor_markup.py LAYDIR OUT.pdf"""
import sys, os, math
sys.path.insert(0, '/home/claude/flrwork')
src = open('/home/claude/flrwork/hd103/build_first_floor.py').read()
exec(src[:src.index("FOR_PNG = ")].replace("('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')", "('1', DATE, 'FIRST FLOOR, SIDE BY SIDE'), ('2', DATE, 'PROPOSED FIXES MARKED')"))
from PIL import ImageDraw, ImageFont
from idd_revise import SANS, SANS_B
RD = (200, 30, 45)
im = Image.open(os.path.join(LAY, 'g_FINAL.png')).convert('RGB')
ImageDraw.Draw(im).rectangle((int(1115 + 77.5 * P), int(Y0 - 71.2 * P), int(1115 + 81.5 * P), int(Y0 - 67.6 * P)), fill=(255, 255, 255))
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
Xp = lambda x: int(1115 + x * P); Yp = lambda y: int(Y0 - y * P)
def box(x0, y0, x1, y1): return (Xp(x0), Yp(y1), Xp(x1), Yp(y0))
def dash(a, b, w=5, on=26, off=14):
    ax, ay, bx, by = Xp(a[0]), Yp(a[1]), Xp(b[0]), Yp(b[1]); L = math.hypot(bx - ax, by - ay); n = 0
    while n < L:
        m = min(n + on, L); d.line([(ax + (bx - ax) * n / L, ay + (by - ay) * n / L), (ax + (bx - ax) * m / L, ay + (by - ay) * m / L)], fill=RD + (255,), width=w); n += on + off
def zone(x0, y0, x1, y1, fill=38, dashed=True):
    d.rectangle(box(x0, y0, x1, y1), fill=RD + (fill,))
    if dashed:
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))): dash(a, b)
    else: d.rectangle(box(x0, y0, x1, y1), outline=RD + (255,), width=5)
def solid(a, b, w=9): d.line([(Xp(a[0]), Yp(a[1])), (Xp(b[0]), Yp(b[1]))], fill=RD + (255,), width=w)
def disc(n, x, y):
    r = 30; cx, cy = Xp(x), Yp(y); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255), outline=RD + (255,), width=5)
    d.text((cx, cy), str(n), font=ImageFont.truetype(SANS_B, 34), fill=RD + (255,), anchor='mm')
def note(x, y, s, px=22, anchor='mm'):
    f = ImageFont.truetype(SANS_B, px)
    for i, ln in enumerate(s.split('\n')):
        yy = Yp(y) + i * int(px * 1.15); l, t, r, b = d.textbbox((Xp(x), yy), ln, font=f, anchor=anchor)
        d.rectangle((l - 4, t - 3, r + 4, b + 3), fill=(255, 255, 255, 235)); d.text((Xp(x), yy), ln, font=f, fill=RD + (255,), anchor=anchor)

# 1 covered loggia and summer kitchen on the living room's court side; matching trellis on the guest side
zone(39.05, 49.0, 47.3, 65.5); zone(40.0, 63.4, 46.6, 65.4, fill=120, dashed=False)
for cy in (49.3, 65.2): d.ellipse((Xp(47.0) - 9, Yp(cy) - 9, Xp(47.0) + 9, Yp(cy) + 9), fill=RD + (255,))
note(43.2, 57.6, "COVERED LOGGIA\n8'-3\" x 16'-6\""); note(43.3, 62.6, 'SUMMER KITCHEN', 19); disc(1, 43.2, 54.2)
for a, b in (((60.3, 49.0), (68.5, 49.0)), ((60.3, 49.0), (60.3, 65.5)), ((60.3, 65.5), (68.5, 65.5))): dash(a, b)
note(64.4, 57.6, 'MATCHING\nTRELLIS', 20)
# 2 pool to the program width
dash((48.8, 50.6), (48.8, 69.4)); dash((58.8, 50.6), (58.8, 69.4)); note(53.8, 66.6, "POOL 10'-0\" WIDE", 20); disc(2, 53.8, 64.4)
# 3 outdoor shower
zone(66.3, 62.6, 68.5, 65.4, fill=120, dashed=False); note(64.3, 61.6, 'OUTDOOR\nSHOWER', 19); disc(3, 64.3, 64.0)
# 4 garage: no projecting step, cars 6" east
zone(67.88, 32.6, 69.4, 36.2, fill=90, dashed=False); d.line([box(67.88, 32.6, 69.4, 36.2)[:2], box(67.88, 32.6, 69.4, 36.2)[2:]], fill=RD + (255,), width=5)
disc(4, 71.2, 37.0)
# 5 storage: coat closet and buffet in the two art wall recesses; service yard on the east side
zone(62.43, 45.05, 66.46, 46.88, fill=110, dashed=False); note(64.45, 44.2, 'COATS', 19); disc(5, 67.6, 45.6)
zone(41.17, 45.05, 45.2, 46.88, fill=110, dashed=False); note(43.2, 44.2, 'BUFFET', 19); disc(5, 40.0, 45.6)
zone(88.6, 42.0, 93.8, 58.0); note(91.2, 50.6, 'SERVICE\nYARD', 20); disc(5, 91.2, 55.0)
# 6 second air handler over the powder room and scullery
zone(40.4, 28.2, 45.2, 35.5); disc(6, 44.2, 33.0)
# 7 two paneled millwork walls, powder door flush in the panelling
solid((25.55, 25.05), (25.55, 35.88)); disc(7, 26.9, 31.8)
solid((37.68, 30.3), (37.68, 36.0)); solid((37.68, 36.0), (45.3, 36.0)); disc(7, 39.2, 37.3)
# 8 scullery: small pantry out
x0, y0, x1, y1 = box(38.17, 25.3, 39.67, 27.95); d.line([(x0, y0), (x1, y1)], fill=RD + (255,), width=7); d.line([(x0, y1), (x1, y0)], fill=RD + (255,), width=7); disc(8, 40.7, 26.6)
# 9 option: one straight east wall
zone(85.38, 39.25, 87.54, 67.03); disc(9, 86.45, 60.0); note(86.45, 57.4, 'OPTION', 18)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); im.save(os.path.join(LAY, 'g_FINAL_mk.png'))

sh = S(doc); sh.frame2(['FIRST FLOOR', 'PROPOSED FIXES'], 'FP-2', 'NOT TO SCALE')
sh.text(X, TOP, 'FIRST FLOOR: PROPOSED FIXES MARKED ON THE OWNER\'S LAYOUT', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Red is proposed and not yet drawn into the plan. Sizes are scaled from FOR Architecture\'s presentation plan and are for FOR to confirm.', 1100, 9.6)
R = (20.6, 15.6, 95.4, 71.0); LW = 410
K = (RIGHT - X - LW - 24) / (R[2] - R[0]); ph = (R[3] - R[1]) * K; py = y + 22
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('g_FINAL_mk.png', 1115, R, K, X, py, 'OWNER\'S LAYOUT, 11.25.26, WITH PROPOSED FIXES')
px = X + pw - 26
sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
C = RED
yy = sh.items(X + pw + 24, py + 10, [
    '#MISSING OR WEAK',
    (1, C, 'Covered loggia on the living room\'s court side, 8\'-3" x 16\'-6", open on three sides so the walk around the pool stays free. Summer kitchen counter (grill, sink, fridge drawers) at the north end. A matching open trellis on the guest side holds the symmetry.'),
    (2, C, 'Pool to the program width, 10\'-0" (drawn 12\'-0"). Deck each side goes from about 8\'-6" to about 9\'-9". Length stays 18\'-0": the court allows about 21\'-0", not the 25\'-0" in the program.'),
    (3, C, 'Outdoor shower on the guest wing\'s court wall, so swimmers rinse outside. The powder room stays where it is.'),
    (4, C, 'Garage stays 19\'-0" x 20\'-0": the east wall is on the 7\'-6" setback line and the west wall is the mudroom. Take out the projecting step (sill step at the door) and park both cars 6" east: about 2\'-7" beside the left car, about 13" between cars.'),
    (5, C, 'Storage. Coat closet in the east art wall recess by the stair, buffet storage in the west one, both behind flush panels. Pool equipment, condensers and bins in a screened service yard on the east side.'),
    (6, C, 'Second air handler: horizontal unit above the powder room and scullery ceiling, serving the west wing. The southeast unit serves the foyer, guest wing and stair. Mechanical engineer to confirm.'),
    '#SIMPLER',
    (7, C, 'Two millwork walls only: fridge, freezer and range as one paneled elevation; bar, wine and powder room door as the other. The powder door becomes a flush door in the panelling, so the dining room sees a wall and not a door.'),
    (8, C, 'Scullery: take out the small pantry. Tall pantry, ovens and coffee, sink and dishwasher stay.'),
    (9, C, 'Option: one straight east wall. Guest wing and stair go 2\'-2" east to the garage line, about 60 SF more under air (estimate). Removes a jog in structure and roof; the guest wing becomes wider than the living wing.'),
], LW - 10, 9.4)
assert yy < FR.y1 - 10, yy
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
