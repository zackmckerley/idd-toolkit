"""2191 SW 23rd St (HD103): FP-2, the owner's first floor with proposed fixes marked in red (not yet drawn into the plan).
    python3 hd103/build_first_floor_markup.py LAYDIR OUT.pdf"""
import sys, os, math
sys.path.insert(0, '/home/claude/flrwork')
src = open('/home/claude/flrwork/hd103/build_first_floor.py').read()
exec(src[:src.index("FOR_PNG = ")].replace("('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')", "('1', DATE, 'FIRST FLOOR, SIDE BY SIDE'), ('2', DATE, 'PROPOSED FIXES MARKED'), ('3', DATE, 'SYMMETRICAL CANOPY AND WALLS'), ('4', DATE, 'AREA CUT, OPTION A'), ('5', DATE, 'NICHES OUT, FOYER OPTION'), ('6', DATE, 'PATH TO 1,700 SF')"))
from PIL import ImageDraw, ImageFont
from idd_revise import SANS, SANS_B
RD = (200, 30, 45)
im = Image.open(os.path.join(LAY, 'g_FINAL.png')).convert('RGB')
ImageDraw.Draw(im).rectangle((int(1115 + 77.5 * P), int(Y0 - 72.5 * P), int(1115 + 81.5 * P), int(Y0 - 67.6 * P)), fill=(255, 255, 255))
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

# N: both wings 5'-0" shorter at the north end
for x0, x1 in ((20.08, 36.83), (70.79, 87.54)):
    zone(x0, 62.03, x1, 67.03, fill=70); solid((x0, 62.03), (x1, 62.03), 11)
disc('N', 28.4, 64.5); disc('N', 79.2, 64.5)
note(28.4, 62.9, "NORTH WALL 5'-0\" SOUTH", 19); note(79.2, 62.9, "NORTH WALL 5'-0\" SOUTH", 19)
note(28.4, 47.0, "LIVING 15'-1\" x 16'-4\"", 19)
note(65.0, 59.2, "GUEST SUITE REPLANNED:\nREACH-IN CLOSET,\nNO WALK-IN", 18)
note(53.8, 67.6, "POOL RUNS 7'-0\" PAST THE WINGS", 19)
# F: foyer option kept for reference
zone(46.05, 35.9, 61.55, 37.38, fill=40); disc('F', 53.8, 36.65)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); im.save(os.path.join(LAY, 'g_FINAL_mk6.png'))

sh = S(doc); sh.frame2(['FIRST FLOOR', 'PATH TO 1,700 SF'], 'FP-6', 'NOT TO SCALE')
sh.text(X, TOP, 'FIRST FLOOR: GETTING TO ABOUT 1,700 SF UNDER AIR', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Red is proposed and not drawn in. Sizes are scaled from FOR Architecture\'s presentation plan and are for FOR to confirm.', 1100, 9.6)
R = (17.6, 15.6, 95.4, 71.6); LW = 410
K = (RIGHT - X - LW - 24) / (R[2] - R[0]); ph = (R[3] - R[1]) * K; py = y + 22
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('g_FINAL_mk6.png', 1115, R, K, X, py, 'OWNER\'S LAYOUT, 11.25.26, PROPOSED CUT IN RED')
px = X + pw - 26
sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
C = RED
yy = sh.items(X + pw + 24, py + 10, [
    '#RECOMMENDED',
    ('N', C, 'Both wings 5\'-0" shorter at the north end. About 168 SF out: first floor about 1,700 SF under air (now about 1,870 SF). Symmetry, the straight outer walls and the wide court all stay.'),
    'Living room: 15\'-1" x 16\'-4" (FOR drew 15\'-1" x 18\'-8"). It still opens to dining and to the court on two sides.',
    'Guest suite: the wing is about 17\'-0" long. Bedroom and bath stay; the walk-in becomes a reach-in closet. Needs replanning.',
    'Pool: unchanged, and runs 7\'-0" past the wings into the rear yard, as the program asked.',
    'Second floor: the junior master wing shortens with it, about 84 SF more out. Terrace over the living room 5\'-0" shorter.',
    '#SMALLER MOVES, IF 5\'-0" IS TOO MUCH',
    ('F', C, 'Front door wall 1\'-6" north: about 23 SF. With the wings 4\'-0" shorter (134 SF) this lands at about 1,713 SF.'),
    'Outer walls back off the setback lines: about 85 SF with the court walls following, but the kitchen returns to 14\'-8" and the east jog at the garage comes back.',
    '#NOT RECOMMENDED',
    'Cutting the mudroom, mechanical room or stair hall (each already at its working minimum), or shortening the kitchen from the street side (breaks the front elevation, and the garage cannot follow).',
], LW - 10, 9.4)
assert yy < FR.y1 - 10, yy
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
