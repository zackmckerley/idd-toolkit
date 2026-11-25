"""2191 SW 23rd St (HD103): SF-1, the second floor after the first floor moves, west wall held and west wall following.
    python3 hd103/build_second_floor.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', DATE, 'SECOND FLOOR, TWO WAYS')]
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



sh = S(doc); sh.frame2(['SECOND FLOOR', 'TWO WAYS'], 'SF-1', 'NOT TO SCALE')
sh.text(X, TOP, 'SECOND FLOOR AFTER THE FIRST FLOOR MOVES: WEST WALL HELD, OR FOLLOWING THE FLOOR BELOW', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Both plans: stair and junior master wing 3\'-0" east with the floor below, one straight east wall on the 7\'-6" setback line, terrace trimmed to the living room below. Drawn on FOR Architecture\'s plan for FOR to redraw; sizes and areas are scaled from the presentation plan (estimates).', 1300, 9.6)
R = (18.6, 15.6, 89.3, 68.9); GAP = 30
K = (RIGHT - X - GAP) / 2 / (R[2] - R[0]); ph = (R[3] - R[1]) * K
py = y + 26; assert py + ph + 150 < FR.y1, (py, ph)
pw, _ = sh.panel('s_hold.png', 1126, R, K, X, py, 'A. WEST WALL HELD')
sh.panel('s_follow.png', 1126, R, K, X + pw + GAP, py, 'B. WEST WALL FOLLOWS, 2\'-2" WEST')
for px in (X + pw - 26, X + 2 * pw + GAP - 26):
    sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
    sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
    sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
ya = sh.items(X, py + ph + 22, [
    '#A. About 1,975 SF under air. House about 3,975 SF.',
    'Master suite as it was. The planter ledge on the west grows from 3\'-0" to 5\'-2" over the wider first floor.',
    'Junior master: closet 2\'-2" wider, bath moves to the east wall. The W.I.C. by the stair goes; bedroom 3 keeps its reach-in closet. Landing at the top of the stair 3\'-0" wider.',
], pw, 9.6)
yb = sh.items(X + pw + GAP, py + ph + 22, [
    '#B. About 2,030 SF under air. House about 4,030 SF.',
    'Master bedroom, bath and terrace 2\'-2" wider (bedroom about 24\'-4" wide). Planter ledge stays 3\'-0". About 56 SF more than A, all in the master suite.',
    'East side as A.',
], pw, 9.6)
assert max(ya, yb) < FR.y1 - 10
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF)
