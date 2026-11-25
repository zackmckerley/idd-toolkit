"""2191 SW 23rd St (HD103): FP-2, the owner's first floor with proposed fixes marked in red (not yet drawn into the plan).
    python3 hd103/build_first_floor_markup.py LAYDIR OUT.pdf"""
import sys, os, math
sys.path.insert(0, '/home/claude/flrwork')
src = open('/home/claude/flrwork/hd103/build_first_floor.py').read()
exec(src[:src.index("FOR_PNG = ")].replace("('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')", "('1', DATE, 'FIRST FLOOR, SIDE BY SIDE'), ('2', DATE, 'PROPOSED FIXES MARKED'), ('3', DATE, 'SYMMETRICAL CANOPY AND WALLS'), ('4', DATE, 'AREA CUT, OPTION A'), ('5', DATE, 'NICHES OUT, FOYER OPTION')"))
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

# foyer option: front door wall 1'-6" north
zone(46.05, 35.9, 61.55, 37.38, fill=70); solid((46.05, 37.38), (61.55, 37.38), 11)
disc('F', 53.8, 36.65); note(53.8, 38.4, "FRONT DOOR WALL 1'-6\" NORTH (OPTION)", 19)
note(53.8, 41.6, "FOYER 7'-1\" DEEP\n(NOW 8'-7\")", 19)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); im.save(os.path.join(LAY, 'g_FINAL_mk5.png'))

sh = S(doc); sh.frame2(['FIRST FLOOR', 'COURT WALL, FOYER'], 'FP-5', 'NOT TO SCALE')
sh.text(X, TOP, 'FIRST FLOOR: ART WALL RECESSES OUT, AND THE FOYER OPTION', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'The court wall change is drawn in. Red is an option and not drawn in. Sizes are scaled from FOR Architecture\'s presentation plan and are for FOR to confirm.', 1100, 9.6)
R = (17.6, 15.6, 95.4, 71.6); LW = 410
K = (RIGHT - X - LW - 24) / (R[2] - R[0]); ph = (R[3] - R[1]) * K; py = y + 22
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('g_FINAL_mk5.png', 1115, R, K, X, py, 'OWNER\'S LAYOUT, 11.25.26, FOYER OPTION IN RED')
px = X + pw - 26
sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
C = RED
yy = sh.items(X + pw + 24, py + 10, [
    '#DRAWN IN: RECESSES OUT',
    'The buffet and coats recesses are gone and the court\'s south wall drops 2\'-6" to the court door line: one straight wall, wing to wing, with the court doors in it.',
    'Covered terrace is 10\'-6" deep under the canopy (was 8\'-0"). Grill and bar counters sit on the new wall.',
    'About 46 SF out of the house (estimate). First floor about 1,870 SF under air.',
    'Costs: the second floor wall above no longer has a wall under it at these two stretches and needs a beam (FOR). The coat closet needs a new home; the hall by the guest bedroom door is 3\'-1" wide.',
    '#OPTION, NOT DRAWN',
    ('F', C, 'Front door wall 1\'-6" north. Foyer 7\'-1" deep (now 8\'-7"), covered entry 1\'-6" deeper. About 23 SF out: first floor about 1,845 SF.'),
    'More than 1\'-6" is too much: under about 7\'-0" the foyer reads as a corridor, and the pivot door and the walk from dining to the stair share the same floor.',
    'It also breaks the line the front door wall shares with the powder room block and the garage vestibule, and the foyer opening shifts 9" off the dining table.',
], LW - 10, 9.4)
assert yy < FR.y1 - 10, yy
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
