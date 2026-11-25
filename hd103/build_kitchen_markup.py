"""2191 SW 23rd St (HD103): owner kitchen markup drawn (hd103/layouts.py, ground_new guest=FOR scullery=U).
    python3 hd103/build_kitchen_markup.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST'), ('5', DATE, 'GUEST SUITE ALTERNATES'), ('6', DATE, 'OWNER KITCHEN MARKUP')]
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


sh = S(doc); sh.frame2(['OWNER MARKUP DRAWN', 'KITCHEN, POWDER, SCULLERY'], 'KP-1', 'AS NOTED')
sh.text(X, TOP, 'KITCHEN AS MARKED UP: POWDER ROOM AT THE FOYER, U-SHAPED SCULLERY', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Drawn from the owner\'s markup of 11.25.26 on FOR\'s plan as revised. The left plan is at 3/8 inch to the foot; the right plan is not to scale. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 900, 9.6) + 10
sh.legend(X + 1000, TOP - 2, [(GUEST, 'Guests'), (SERV, 'Family and groceries'), (SERVE, 'Serving')])
py = y + 16
pw, ph = sh.panel('g_U.png', 1115, (21.5, 17.0, 47.0, 47.0), 27.0, X, py, 'KITCHEN, POWDER ROOM, SCULLERY AND DINING', 'PROPOSED')
x2 = X + pw + 30
pw2, ph2 = sh.panel('g_U_r.png', 1115, (20.5, 13.0, 88.5, 68.5), 11.0, x2, py, 'GROUND FLOOR ROUTES')
yy = py + ph2 + 20; cw = (pw2 - 30) / 2
sh.items(x2, yy, [
    (1, GUEST, 'Front door: the court and pool ahead, dining to the left. Unchanged.'),
    (2, GUEST, 'Foyer to living room past the end of the table, 4\'-0" at its tightest.'),
    (3, GUEST, 'Powder room door at the foyer end of the paneled wall, about 10\' from the front door.'),
    (4, SERV, 'Garage into the closed mudroom, then along the foyer\'s south wall.'),
    (5, SERV, 'Groceries reach the scullery through the kitchen, behind the stools: about 50\' from the garage door. With its own foyer door it was 27\'.'),
    (6, SERV, 'Garage to the kitchen fridge: about 43\'.'),
    (7, SERVE, 'Island to the dining chairs 4\'-1". Table to the court doors about 14\'.')], cw)
sh.items(x2 + cw + 30, yy, ['#What you get',
    'The guest wing goes back to FOR\'s drawing: his 5\'-4" x 9\'-0" walk-in closet, his guest door, no air handler move, no east wall move, no added area.',
    'Powder room 7\'-1" x 4\'-0" with a 2\'-6" door. Vanity opposite the door, toilet at the far end, out of the line of sight. It backs onto the scullery, not the dining room.',
    'Scullery 7\'-1" x 12\'-8" with counters on three sides and an 18" pantry: about 26\' of run. A 4\'-0" opening to the kitchen\'s south aisle. Aisle 3\'-6".',
    'Kitchen 14\'-8" x 17\'-4". The west run now reaches the kitchen line: 2\'-7" of counter north of the fridge.',
    '#What it costs',
    'The powder room door faces the dining table, 2\'-3" from the nearest chairs. It is in the paneled wall, so finish it as a concealed door.',
    'The scullery is no longer a through room. Groceries pass between the stools and the scullery wall, 3\'-4" wide.',
    'The new counter north of the fridge runs in front of the first 2\'-7" of the long west window. Sill height to confirm.'], cw)
sh.text(X, FR.y1 - 40, 'OWNER:   APPROVED  /  REVISE          DATE ________', 12, INK, bold=True, raw=True)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
