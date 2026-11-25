"""2191 SW 23rd St (HD103): kitchen planned to the NKBA guidelines (hd103/layouts.py, ground_new guest=FOR scullery=K).
    python3 hd103/build_first_floor.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', DATE, 'FIRST FLOOR, SIDE BY SIDE')]
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


FOR_PNG = '/home/claude/deck/img_p3_11.png'
import shutil; shutil.copy(FOR_PNG, os.path.join(LAY, 'for_ground.png'))
for fn_ in ('for_ground.png', 'g_FINAL.png'):                                     # FOR's setback dimension is cut by the crop: leave it off both
    im_ = Image.open(os.path.join(LAY, fn_)).convert('RGB'); from PIL import ImageDraw
    ImageDraw.Draw(im_).rectangle((int(1115 + 77.5 * P), int(Y0 - 71.2 * P), int(1115 + 81.5 * P), int(Y0 - 67.6 * P)), fill=(255, 255, 255))
    im_.save(os.path.join(LAY, fn_.replace('.png', '_s.png')))
sh = S(doc); sh.frame2(['FIRST FLOOR', 'ARCHITECT AND OWNER'], 'FP-1', 'NOT TO SCALE')
sh.text(X, TOP, 'FIRST FLOOR PLAN: ARCHITECT\'S DRAWING AND OWNER\'S LAYOUT', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Both plans are drawn at the same size, north up, SW 23rd St at the bottom. The owner\'s layout is drawn on FOR Architecture\'s plan for FOR to redraw; sizes are scaled from the presentation plan.', 1300, 9.6)
R = (20.6, 15.6, 88.6, 70.9); GAP = 30
K = (RIGHT - X - GAP) / 2 / (R[2] - R[0]); ph = (R[3] - R[1]) * K
py = y + 24 + max(0, (FR.y1 - 30 - (y + 24) - ph) / 2)
assert py + ph < FR.y1 - 10, (py, ph, FR.y1)
pw, _ = sh.panel('for_ground_s.png', 1115, R, K, X, py, 'FOR ARCHITECTURE, PRESENTATION 11.24.26')
sh.panel('g_FINAL_s.png', 1115, R, K, X + pw + GAP, py, 'OWNER\'S LAYOUT, 11.25.26', 'PROPOSED')
for px in (X + pw - 26, X + 2 * pw + GAP - 26):                                   # north arrow in each panel
    sh.p.draw_line(fitz.Point(px, py + 44), fitz.Point(px, py + 16), color=INK, width=1.2)
    sh.p.draw_polyline([fitz.Point(px - 5, py + 24), fitz.Point(px, py + 12), fitz.Point(px + 5, py + 24)], color=INK, fill=INK, width=0.8, closePath=True)
    sh.text(px, py + 56, 'N', 9, INK, bold=True, align='c', raw=True)
print('K pt/ft', K, 'page', sh.p.rect, 'FR', FR)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
