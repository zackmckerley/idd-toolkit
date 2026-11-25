"""2191 SW 23rd St (HD103): kitchen planned to the NKBA guidelines (hd103/layouts.py, ground_new guest=FOR scullery=K).
    python3 hd103/build_kitchen_plan3.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST'), ('5', DATE, 'GUEST SUITE ALTERNATES'), ('6', DATE, 'OWNER KITCHEN MARKUP'), ('7', DATE, 'KITCHEN TO NKBA GUIDELINES'), ('8', DATE, 'FRIDGE AND FREEZER ON RANGE WALL')]
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


sh = S(doc); sh.frame2(['KITCHEN PLAN', 'CHECKED TO NKBA GUIDELINES'], 'KP-3', 'AS NOTED')
sh.text(X, TOP, 'KITCHEN: FRIDGE AND FREEZER TOGETHER ON THE RANGE WALL', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Your markup of 11.25.26 (powder room at the foyer, U-shaped scullery, west run to the kitchen line), re-planned against the NKBA Kitchen Planning Guidelines. The left plan is at 3/8 inch to the foot; the right plan is not to scale. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 900, 9.6) + 10
sh.legend(X + 1000, TOP - 2, [(GUEST, 'Guests'), (SERV, 'Family and groceries'), (SERVE, 'Serving')])
py = y + 16
pw, ph = sh.panel('g_K3.png', 1115, (21.5, 17.0, 47.0, 47.0), 27.0, X, py, 'KITCHEN, POWDER ROOM, SCULLERY AND DINING', 'PROPOSED')
x2 = X + pw + 30
pw2, ph2 = sh.panel('g_K3_r.png', 1115, (20.5, 13.0, 88.5, 68.5), 11.0, x2, py, 'GROUND FLOOR ROUTES')
yy = py + ph2 + 20; cw = (pw2 - 30) / 2
sh.items(x2, yy, ['#Checked against the guidelines',
    'Work triangle (12\' to 26\', each leg 4\' to 9\'): sink to range 5\'-5", sink to fridge 7\'-0", range to fridge 7\'-4". Total 19\'-9". No walkway crosses it.',
    'Work aisles (42" min): 45" at the range, 43" at the fridge, 43" at the street counter.',
    'Walk-past behind seating (44" min from the counter edge): 57". The scullery, wine column and bar open onto this aisle.',
    'Seating (24" wide, 15" knee space each): four stools at 29", 23" of overhang.',
    'Landings: 15" north and 6\'-6" south of the range (12" and 15" needed). For the fridge, the island prep top is 43" across (15" within 48" needed).',
    'Sink: dishwasher beside it (within 36"), trash pull-out on the other side, 3\'-6" of clear prep top next to it (36" needed).',
    'Counter frontage (158" min): about 390".',
    'Range and hood on solid wall, away from the walkway. No tall unit stands in front of glass: the west window is shortened to clear the fridge.'], cw)
sh.items(x2 + cw + 30, yy, ['#What changed from KP-2',
    'Freezer (30") and fridge (36") stand together at the north end of the range wall, the fridge at the dining end. A guest reaches it from the table without passing the range.',
    'The long west window starts 2\'-4" further north, about 9\'-8" long in place of 12\'-0". This is a west elevation change for FOR.',
    'The recess in the powder block now holds the wine column and a bar cabinet, 30" each. Nothing cold or heavy is behind the stools.',
    'Unchanged: range on the solid pier, island in work order with four stools, powder room 5\'-0" x 5\'-3", U-shaped scullery 7\'-1" x 11\'-5", breakfast counter with the microwave drawer.',
    '#Still open',
    'The range is 15" from the freezer and is not centred between the two west windows. Centring it would need the short west window to move.',
    'The dishwasher door opens across the range aisle. A second dishwasher is in the scullery.',
    'Sill heights at the street window and the short west window.',
    'The powder room door faces the dining table, 2\'-3" from the nearest chairs: a concealed door in the paneled wall.',
    'Groceries reach the scullery through the kitchen, about 50\' from the garage door; the fridge is about 42\'.'], cw)
sh.text(X, FR.y1 - 40, 'OWNER:   APPROVED  /  REVISE          DATE ________', 12, INK, bold=True, raw=True)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
