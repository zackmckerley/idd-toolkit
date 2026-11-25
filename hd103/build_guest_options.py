"""2191 SW 23rd St (HD103): guest suite alternates (hd103/layouts.py, ground_new guest=A/B).
    python3 hd103/build_guest_options.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST'), ('5', DATE, 'GUEST SUITE ALTERNATES')]
idd_sheet.remap = lambda s: s
INK = (0, 0, 0); RED = (0.78, 0.12, 0.18); GREY = (0.35, 0.35, 0.35); P = 37.40; Y0 = 3020
GUEST = (25 / 255, 95 / 255, 200 / 255); SERV = (225 / 255, 120 / 255, 0); SERVE = (20 / 255, 140 / 255, 70 / 255)

def wrap(s, width, size, bold=False):
    out = []; cur = ''
    for w_ in s.split():
        t = (cur + ' ' + w_).strip()
        if idd_sheet._FR.text_length(t, fontsize=size) * (1.06 if bold else 1) > width and cur: out.append(cur); cur = w_
        else: cur = t
    out.append(cur); return out

class S(Sheet):
    def frame2(self, titles, no, scale):
        self.frame(None, scale, titles, no, legend_rule=False)
        for r in self.p.search_for('A-201 AND A-202, REV 1, 10.23.26'):
            self.p.add_redact_annot(r + (-1, -1, 1, 1), fill=(1, 1, 1)); self.p.apply_redactions(images=0, graphics=0)
            self.text(r.x0, r.y1 - 2.2, 'PRESENTATION, 11.24.26', 9, INK, raw=True)
    def para(self, x, y, s, width, size=9.6, bold=False, color=INK):
        for ln in wrap(s, width, size, bold): self.text(x, y, ln, size, color, bold=bold, raw=True); y += size * 1.42
        return y
    def items(self, x, y, items, width, size=9.6):
        for it in items:
            if isinstance(it, tuple):                       # (number, colour, text)
                n, col, t = it
                self.p.draw_circle(fitz.Point(x + 6, y - 3.2), 6.2, color=col, fill=(1, 1, 1), width=1.3)
                self.text(x + 6, y, str(n), 8.2, col, bold=True, align='c', raw=True)
                y = self.para(x + 18, y, t, width - 18, size) + 4
            elif it.startswith('#'): y = self.para(x, y + 6, it[1:], width, size + 0.6, bold=True) + 3
            else: y = self.para(x, y, it, width, size) + 4
        return y
    def panel(self, fn, x0px, rect, K, px, py, name, tag=''):
        x0, y0, x1, y1 = rect; pw = (x1 - x0) * K; ph = (y1 - y0) * K
        im = Image.open(os.path.join(LAY, fn)).convert('RGB').crop((int(x0px + x0 * P), int(Y0 - y1 * P), int(x0px + x1 * P), int(Y0 - y0 * P)))
        jp = os.path.join(LAY, fn.replace('.png', '_%d_p.jpg' % int(x0 * 10 + y0))); im.save(jp, quality=88)
        self.text(px, py - 6, name, 10.5, INK, bold=True, raw=True)
        if tag: self.text(px + pw, py - 6, tag, 9, RED, bold=True, align='r', raw=True)
        self.p.insert_image(fitz.Rect(px, py, px + pw, py + ph), filename=jp)
        self.p.draw_rect(fitz.Rect(px, py, px + pw, py + ph), color=RED if tag in ('PROPOSED', 'RECOMMENDED') else (0.55, 0.55, 0.55), width=1.4 if tag in ('PROPOSED', 'RECOMMENDED') else 0.5)
        return pw, ph
    def legend(self, x, y, rows):
        for col, t in rows:
            self.p.draw_line(fitz.Point(x, y - 3), fitz.Point(x + 26, y - 3), color=col, width=3.2); self.text(x + 34, y, t, 9.6, INK, raw=True); y += 15
        return y

doc = fitz.open(); X = FR.x0 + 20; TOP = FR.y0 + 44; RIGHT = TB_X - 20


sh = S(doc); sh.frame2(['OWNER OPTIONS', 'GUEST SUITE'], 'GS-1', '1/4" TO 1\'-0"')
sh.text(X, TOP, 'GUEST SUITE: TWO ALTERNATE LAYOUTS', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Ground floor, northeast wing, north up. Each option has one closet and FOR\'s bath as he drew it: vanity, toilet, shower. The kitchen side of the house is as rev 4 in both. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 1300, 9.6) + 10
R = (62.0, 38.0, 89.0, 69.0); K = 18.0; py = y + 16
pw, ph = sh.panel('g_old.png', 1115, R, K, X, py, 'FOR\'S SUITE AS REVISED 11.24.26', 'NO POWDER ROOM HERE')
gap = (RIGHT - X - 3 * pw) / 2
xa = X + pw + gap; xb = xa + pw + gap
sh.panel('g_A.png', 1115, R, K, xa, py, 'OPTION A: WIDER WING, BEDROOM WITH SITTING AREA')
sh.panel('g_B.png', 1115, R, K, xb, py, 'OPTION B: INSIDE FOR\'S WALLS', 'RECOMMENDED')
yy = py + ph + 20
sh.items(X, yy, ['#For reference',
    'Bedroom 15\'-4" x 9\'-8". Walk-in closet 5\'-4" x 9\'-0". Bath 5\'-1" x 9\'-3".',
    'The powder room was off the dining room, where the scullery is now. Both options give it a new home on this side of the foyer.'], pw)
sh.items(xa, yy, ['#What changes',
    'The east wall moves out 5\'-3" to the garage wall line, one straight east wall. About 105 SF added (estimate).',
    'The bedroom widens to 20\'-6" x 9\'-8" with a sitting area and a third north window.',
    'One walk-in closet in the new southeast bay, 4\'-6" x 9\'-4", with 9\'-4" of double hanging, entered from the sitting area.',
    'Powder room where rev 4 has it, 5\'-4" x 5\'-1". The rest of FOR\'s closet opens up as an entry alcove with a bench and hooks.',
    '#What it costs',
    'A 9\'-8" beam where the bedroom\'s east wall comes out; it carries the second floor. The bath loses its window. East setback and lot coverage to confirm. The guest door and the powder room still share a 3\' x 3\' vestibule.'], pw)
sh.items(xb, yy, ['#What changes',
    'No exterior wall moves and no area is added. FOR\'s bedroom, bath, bath window, plumbing and guest door all stay.',
    'The powder room takes the air handler closet by the stair plus 1\'-6" of the closet: 4\'-2" x 5\'-4", pocket door, vanity facing the door, toilet out of the line of sight.',
    'One walk-in closet, 5\'-4" x 7\'-4", with FOR\'s door. It gives up 1\'-8" of its 9\'-0".',
    '#What it costs',
    'The air handler moves to the storage room behind the stair, with ducts through the stair wall. FOR and the mechanical engineer must confirm it.',
    'The powder room door faces the east end of the foyer, beside the stair. It is about 35\' from the dining table and not on axis with the front door.'], pw)
sh.text(X, FR.y1 - 40, 'OWNER PICK:   A  /  B          DATE ________', 12, INK, bold=True, raw=True)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
