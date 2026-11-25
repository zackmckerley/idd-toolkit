"""2191 SW 23rd St (HD103): kitchen planned to the NKBA guidelines (hd103/layouts.py, ground_new guest=FOR scullery=K).
    python3 hd103/build_mudroom4.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST'), ('5', DATE, 'GUEST SUITE ALTERNATES'), ('6', DATE, 'OWNER KITCHEN MARKUP'), ('7', DATE, 'KITCHEN TO NKBA GUIDELINES'), ('8', DATE, 'FRIDGE AND FREEZER ON RANGE WALL'), ('9', DATE, 'MUDROOM AND GARAGE'), ('10', DATE, 'GARAGE, MUDROOM, MECHANICAL'), ('11', DATE, 'OWNER MARKUP: MUDROOM SOUTH'), ('12', DATE, 'DOOR TO HALL, FULL STAIR')]
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


sh = S(doc); sh.frame2(['GARAGE AND MUDROOM', 'DOOR TO THE HALL'], 'GM-4', 'AS NOTED')
sh.text(X, TOP, 'GARAGE OPENS TO THE HALL, MUDROOM BESIDE IT, FULL STAIR, AIR HANDLER CLOSET', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Ground floor, southeast corner, north up, on the KP-3 plan. The left plan is at 3/8 inch to the foot; the right plan is enlarged. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 900, 9.6) + 10
sh.legend(X + 1000, TOP - 2, [(GUEST, 'Stair'), (SERV, 'Family'), (SERVE, 'Garage and service')])
py = y + 16
pw, ph = sh.panel('gm5_r.png', 1115, (58.0, 16.0, 89.0, 49.0), 27.0, X, py, 'GARAGE, MUDROOM, STAIR AND MECHANICAL CLOSET', 'PROPOSED')
lx = X + pw + 34; lw = RIGHT - lx
pw2, ph2 = sh.panel('g_M5.png', 1115, (68.3, 37.75, 88.3, 48.0), lw / 20.0, lx, py, 'STAIR AND AIR HANDLER CLOSET, ENLARGED')
sh.items(lx, py + ph2 + 22, [
    (1, SERV, 'The house door is at the north end of the garage wall, in front of the cars, 2\'-7" wide. It swings out onto a 3\'-0" x 2\'-7" landing and opens into a 4\'-11" x 2\'-10" recess off the stair hall. The cars park as FOR drew them.'),
    (2, SERV, 'Mudroom 4\'-11" x 10\'-3", directly on your left through a 3\'-6" cased opening, no door: bench and hooks 8\'-0", four lockers on the end wall.'),
    (3, SERV, 'From the recess: 5\' to the stair, 10\' to the guest suite, west down the foyer to the kitchen.'),
    (4, SERVE, 'Garage storage bay 4\'-10" x 6\'-5", open to the garage through a 4\'-10" opening.'),
    (5, GUEST, 'The stair is drawn in full, both flights, taken from FOR\'s second floor plan: up along the south side to the landing at the east window, then back west along the north side. The closet is gone, so the upper flight stands open over the hall.'),
    (6, SERVE, 'Air handler closet 4\'-6" x 3\'-6", opening to the garage through a pair of doors. The air handler (AHU, 2\'-2" x 2\'-1") stands at the back with its 30" service space shown dashed in front. The water heater (WH) hangs on the east wall.'),
    '#What it costs',
    'The garage door is on view from the far end of the foyer. Finish it as a flush panel in the wall.',
    'The mudroom is beside the route, not on it.',
    'The landing clears the left car by about 8".',
    'FOR\'s bedroom 3 closet above the old storage room overhangs or shrinks. The air handler is about 45\' from the living room end.',
    '#For FOR to confirm',
    'The stair itself: FOR\'s ground floor plan cuts it at the break line, so the upper flight here is his second floor drawing laid over the ground floor. Tread count, guard and what is open below are his to design.',
    'Fire rating of the garage door and the storage bay. Header over the bay opening. Louvers or a return path for the air handler closet.'], lw)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
