"""2191 SW 23rd St (HD103): FP-2, the owner's first floor with proposed fixes marked in red (not yet drawn into the plan).
    python3 hd103/build_first_floor_markup.py LAYDIR OUT.pdf"""
import sys, os, math
sys.path.insert(0, '/home/claude/flrwork')
src = open('/home/claude/flrwork/hd103/build_first_floor.py').read()
exec(src[:src.index("FOR_PNG = ")].replace("('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')", "('1', DATE, 'FIRST FLOOR, SIDE BY SIDE'), ('2', DATE, 'PROPOSED FIXES MARKED'), ('3', DATE, 'SYMMETRICAL CANOPY AND WALLS')"))
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

# 1 one canopy on the court axis, wing to wing, over the terrace and the sun shelf; a counter at each end wall
zone(39.05, 47.6, 68.57, 55.6)
zone(39.3, 47.65, 45.3, 49.6, fill=130, dashed=False); zone(62.3, 47.65, 68.3, 49.6, fill=130, dashed=False)
note(42.3, 50.6, 'GRILL', 19); note(65.3, 50.6, 'BAR', 19)
note(43.9, 53.4, "DINING\n9'-9\" x 8'-0\"", 19); note(63.7, 53.4, "LOUNGE\n9'-9\" x 8'-0\"", 19)
note(53.8, 49.2, "CANOPY 29'-7\" x 8'-0\", NO COLUMNS", 21); disc(1, 50.7, 53.9)
dash((48.8, 50.6), (48.8, 69.4)); dash((58.8, 50.6), (58.8, 69.4)); note(53.8, 66.6, "POOL 10'-0\" WIDE", 20)
dash((53.8, 43.6), (53.8, 48.4), w=3, on=40, off=12); dash((53.8, 69.7), (53.8, 71.4), w=3, on=40, off=12); note(55.3, 70.6, 'AXIS', 18)
# 9 both outer walls to the setback lines, 2'-2" each
zone(20.08, 17.78, 22.27, 67.03); disc(9, 21.2, 44.0); note(21.2, 41.2, "2'-2\"", 18)
zone(85.38, 39.25, 87.54, 67.03); disc(9, 86.45, 55.0); note(86.45, 52.2, "2'-2\"", 18)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); im.save(os.path.join(LAY, 'g_FINAL_mk3.png'))

sh = S(doc); sh.frame2(['FIRST FLOOR', 'SYMMETRY'], 'FP-3', 'NOT TO SCALE')
sh.text(X, TOP, 'FIRST FLOOR: ITEMS 1 AND 9 REDONE TO KEEP THE SYMMETRY', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Red is proposed and not yet drawn into the plan. Sizes are scaled from FOR Architecture\'s presentation plan and are for FOR to confirm.', 1100, 9.6)
R = (17.6, 15.6, 95.4, 71.6); LW = 410
K = (RIGHT - X - LW - 24) / (R[2] - R[0]); ph = (R[3] - R[1]) * K; py = y + 22
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('g_FINAL_mk3.png', 1115, R, K, X, py, 'OWNER\'S LAYOUT, 11.25.26, ITEMS 1 AND 9 IN RED')
px = X + pw - 26
sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
C = RED
yy = sh.items(X + pw + 24, py + 10, [
    '#SYMMETRICAL ABOUT THE COURT AXIS',
    (1, C, 'One flat canopy on the axis, spanning wing to wing (29\'-7") and 8\'-0" deep, over the terrace at the court doors and the sun shelf. No columns: it bears on the two wings. Under it, a 9\'-9" x 8\'-0" covered place each side of the pool: dining with a grill counter on the living room side, lounge with a bar counter on the guest side. The two counters match. The decks beside the pool stay open and 9\'-9" wide.'),
    (9, C, 'Both outer walls move 2\'-2" to the setback lines: west wall to the 20\'-0" line, guest wing and stair to the 7\'-6" line where the garage already stands. One straight wall each side, and the two wings stay the same width (18\'-11" outside). About 170 SF more on the first floor (estimate): 108 SF in the living, dining and kitchen wing, 61 SF in the guest wing and stair. Kitchen and living room each gain 2\'-2" of width.'),
    '#FOR FOR TO CONFIRM',
    'Lot coverage and both setbacks with the wider footprint. Canopy structure and whether it counts toward coverage. Second floor follows the same lines.',
    '#ACCEPTED BY OWNER, NOT SHOWN HERE',
    'Items 2, 3, 4, 5 and 8 on FP-2.',
], LW - 10, 9.4)
assert yy < FR.y1 - 10, yy
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
