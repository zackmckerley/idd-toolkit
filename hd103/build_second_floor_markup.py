"""2191 SW 23rd St (HD103): FP-2, the owner's first floor with proposed fixes marked in red (not yet drawn into the plan).
    python3 hd103/build_first_floor_markup.py LAYDIR OUT.pdf"""
import sys, os, math
sys.path.insert(0, '/home/claude/flrwork')
src = open('/home/claude/flrwork/hd103/build_first_floor.py').read()
exec(src[:src.index("FOR_PNG = ")].replace("('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')", "('1', DATE, 'FIRST FLOOR, SIDE BY SIDE'), ('2', DATE, 'PROPOSED FIXES MARKED'), ('3', DATE, 'SYMMETRICAL CANOPY AND WALLS'), ('4', DATE, 'AREA CUT, OPTION A'), ('5', DATE, 'NICHES OUT, FOYER OPTION'), ('6', DATE, 'PATH TO 1,700 SF'), ('7', DATE, 'SECOND FLOOR B, AREA CUT')"))
from PIL import ImageDraw, ImageFont
from idd_revise import SANS, SANS_B
RD = (200, 30, 45)
im = Image.open(os.path.join(LAY, 's_follow.png')).convert('RGB')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
Xp = lambda x: int(1126 + x * P); Yp = lambda y: int(Y0 - y * P)
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

# S: south wall 2'-0" north, full length; V: option, open to the foyer below
zone(23.10, 21.79, 87.54, 23.79, fill=70); solid((23.10, 23.79), (87.54, 23.79), 11)
disc('S', 40.5, 22.8); disc('S', 78.0, 22.8)
note(56.0, 24.9, "SOUTH WALL 2'-0\" NORTH. FRONT LEDGE 6'-0\" (NOW 4'-0\")", 19)
zone(48.4, 36.4, 59.2, 43.2); disc('V', 53.8, 41.6); note(53.8, 38.6, "OPTION: OPEN TO\nFOYER BELOW", 19)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); im.save(os.path.join(LAY, 's_follow_mk.png'))

sh = S(doc); sh.frame2(['SECOND FLOOR', 'OPTION B, AREA CUT'], 'SF-2', 'NOT TO SCALE')
sh.text(X, TOP, 'SECOND FLOOR, OPTION B: TAKING AREA OUT WITHOUT OVERHANGS', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Red is proposed and not drawn in. Sizes are scaled from FOR Architecture\'s presentation plan and are for FOR to confirm.', 1100, 9.6)
R = (17.6, 14.6, 91.0, 69.0); LW = 410
K = (RIGHT - X - LW - 24) / (R[2] - R[0]); ph = (R[3] - R[1]) * K; py = y + 22
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('s_follow_mk.png', 1126, R, K, X, py, 'SECOND FLOOR, OPTION B (WEST WALL FOLLOWS), PROPOSED CUT IN RED')
px = X + pw - 26
sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
C = RED
yy = sh.items(X + pw + 24, py + 10, [
    '#RECOMMENDED',
    ('S', C, 'South wall 2\'-0" north along the whole front. About 129 SF out: second floor about 1,860 SF under air (now about 1,990 SF). House about 3,730 SF.'),
    'No overhang: the wall still sits over the first floor, and the front planter ledge goes from 4\'-0" to 6\'-0". One wall moves; every room keeps its place.',
    'Rooms get 2\'-0" shallower: master bath about 10\'-1" deep, bedrooms 3 and 4 about 11\'-6", baths 3 and 4 and the laundry about 7\'-6" long. All workable; the master bath and the two baths need replanning.',
    '#OPTION',
    ('V', C, 'Open the floor over the foyer, about 10\'-10" x 6\'-10": a two-storey entry with the stair hall as a gallery. About 74 SF more out (about 1,785 SF). Bedroom 4\'s two closets move into the bedroom.'),
    '#THE ONE OVERHANG TO SETTLE',
    'Since the art wall recesses came out, the second floor\'s north wall stands 2\'-6" proud of the court wall below. The canopy starts at that line, so it reads as the canopy\'s edge and not as an overhang. FOR to confirm the beam.',
    '#NOT RECOMMENDED',
    'Pulling the east end back off the garage (bedroom 3 narrows and the east wall jogs), or cutting the rooms that bridge the entry court (changes FOR\'s front elevation).',
], LW - 10, 9.4)
assert yy < FR.y1 - 10, yy
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
