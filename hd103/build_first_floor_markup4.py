"""2191 SW 23rd St (HD103): FP-2, the owner's first floor with proposed fixes marked in red (not yet drawn into the plan).
    python3 hd103/build_first_floor_markup.py LAYDIR OUT.pdf"""
import sys, os, math
sys.path.insert(0, '/home/claude/flrwork')
src = open('/home/claude/flrwork/hd103/build_first_floor.py').read()
exec(src[:src.index("FOR_PNG = ")].replace("('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')", "('1', DATE, 'FIRST FLOOR, SIDE BY SIDE'), ('2', DATE, 'PROPOSED FIXES MARKED'), ('3', DATE, 'SYMMETRICAL CANOPY AND WALLS'), ('4', DATE, 'AREA CUT, OPTION A')"))
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

# A: wings back to 16'-9", court 4'-5" wider; outer walls stay on the setback lines
zone(36.83, 47.6, 39.02, 67.03, fill=70); zone(68.6, 47.6, 70.79, 67.03, fill=70)
solid((36.83, 47.6), (36.83, 67.03), 11); solid((70.79, 47.6), (70.79, 67.03), 11)
note(37.9, 58.5, "2'-2\"\nOUT", 18); note(69.7, 58.5, "2'-2\"\nOUT", 18)
disc('A', 37.9, 62.0); disc('A', 69.7, 62.0)
note(28.5, 50.3, "LIVING ROOM 16'-9\" OUTSIDE\n(AS APPROVED BEFORE)", 19); note(79.2, 61.8, "GUEST WING 16'-9\" OUTSIDE", 19)
note(42.8, 60.5, "DECK\n12'-0\"", 20); note(64.8, 60.5, "DECK\n12'-0\"", 20)
dash((36.83, 55.6), (70.79, 55.6)); note(53.8, 56.5, "CANOPY SPAN 33'-11\" (WAS 29'-7\")", 19)
dash((53.8, 43.6), (53.8, 48.4), w=3, on=40, off=12); dash((53.8, 69.7), (53.8, 71.4), w=3, on=40, off=12); note(55.3, 70.6, 'AXIS', 18)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); im.save(os.path.join(LAY, 'g_FINAL_mk4.png'))

sh = S(doc); sh.frame2(['FIRST FLOOR', 'AREA CUT'], 'FP-4', 'NOT TO SCALE')
sh.text(X, TOP, 'FIRST FLOOR: OPTION A, 85 SF OUT BY WIDENING THE COURT', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Red is proposed and not yet drawn into the plan. Sizes are scaled from FOR Architecture\'s presentation plan and are for FOR to confirm.', 1100, 9.6)
R = (17.6, 15.6, 95.4, 71.6); LW = 410
K = (RIGHT - X - LW - 24) / (R[2] - R[0]); ph = (R[3] - R[1]) * K; py = y + 22
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('g_FINAL_mk4.png', 1115, R, K, X, py, 'OWNER\'S LAYOUT, 11.25.26, OPTION A IN RED')
px = X + pw - 26
sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
C = RED
yy = sh.items(X + pw + 24, py + 10, [
    '#OPTION A',
    ('A', C, 'The living room\'s court wall moves 2\'-2" west and the guest wing\'s court wall moves 2\'-2" east. The red strips come out of the house and become pool deck. Both outer walls stay on the setback lines.'),
    '#RESULT (ESTIMATES)',
    'First floor under air: about 1,915 SF (now about 2,000 SF). About 43 SF out of each wing.',
    'Living room and guest wing: 16\'-9" outside, the width approved before the outer walls moved. Kitchen and dining wing keeps its extra 2\'-2".',
    'Court: about 33\'-11" between the wings (now 29\'-7"). Deck each side of the pool about 12\'-0" (now 9\'-9").',
    'Symmetry about the court axis is kept.',
    '#WHAT MOVES WITH IT',
    'Canopy spans 33\'-11". Grill and bar counters, art wall recesses and the outdoor shower slide with the walls. Guest bedroom door, closet and bath shift 2\'-2" east inside the wing, or the closet gives the width back.',
    'Second floor: junior master wing narrows the same 2\'-2" (about 43 SF more out); terrace over the living room narrows 2\'-2".',
], LW - 10, 9.4)
assert yy < FR.y1 - 10, yy
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
