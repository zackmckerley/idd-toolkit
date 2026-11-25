"""2191 SW 23rd St (HD103): kitchen planned to the NKBA guidelines (hd103/layouts.py, ground_new guest=FOR scullery=K).
    python3 hd103/build_mudroom3.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST'), ('5', DATE, 'GUEST SUITE ALTERNATES'), ('6', DATE, 'OWNER KITCHEN MARKUP'), ('7', DATE, 'KITCHEN TO NKBA GUIDELINES'), ('8', DATE, 'FRIDGE AND FREEZER ON RANGE WALL'), ('9', DATE, 'MUDROOM AND GARAGE'), ('10', DATE, 'GARAGE, MUDROOM, MECHANICAL'), ('11', DATE, 'OWNER MARKUP: MUDROOM SOUTH')]
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


sh = S(doc); sh.frame2(['GARAGE AND MUDROOM', 'OWNER MARKUP DRAWN'], 'GM-3', '3/8" TO 1\'-0"')
sh.text(X, TOP, 'GARAGE AND MUDROOM AS MARKED UP: MUDROOM SOUTH, OPEN STAIR, SMALL MECHANICAL ROOM', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Ground floor, southeast corner, north up, on the KP-3 plan, from the owner\'s markup of 11.25.26. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 900, 9.6) + 10
sh.legend(X + 1000, TOP - 2, [(GUEST, 'Guests'), (SERV, 'Family'), (SERVE, 'Garage and service')])
py = y + 16
pw, ph = sh.panel('gm4_r.png', 1115, (58.0, 16.0, 89.0, 49.0), 27.0, X, py, 'MUDROOM BEHIND THE FOYER WALL LINE, OPEN STAIR, MINIMUM MECHANICAL ROOM', 'PROPOSED')
lx = X + pw + 34; lw = RIGHT - lx
sh.items(lx, py + 4, [
    (1, SERV, 'The garage wall is solid at the north end. The door to the house is now 3\'-0" wide beside the left car, reached by a 2\'-7" strip between the car and the wall.'),
    (2, SERV, 'Mudroom 4\'-11" x 10\'-3", shifted 3\'-2" south. You enter facing the bench and hooks (8\'-0"), with four lockers on the end wall. The garage door folds back flat against the wall.'),
    (3, SERV, 'A 2\'-6" pocket door in the north wall opens to the stair hall. The mudroom\'s north wall now continues the foyer\'s south wall in one line, and the hall by the stair gains 4\'-11" x 2\'-10".'),
    (4, SERVE, 'Garage storage bay 4\'-10" x 6\'-5", open to the garage through a 4\'-10" opening, with 6\'-5" of shelves. It was 9\'-7" long before the mudroom moved.'),
    (5, GUEST, 'The closet by the stair is removed. The stair stands open on its north side for FOR to design as the feature stair. The air handler that was here moves to the mechanical room.'),
    (6, SERVE, 'Mechanical room 4\'-6" x 3\'-6", the least that gives the air handler its 30" service space and room for a wall-hung water heater. Entered from the garage.'),
    '#What the smaller mechanical room gives you',
    'About 20 SF less building, and the stair\'s east wall becomes an outside wall. A window there (drawn 2\'-6" wide) lights the open stair from the landing side.',
    '#What it costs',
    'Cars: to make the 2\'-7" strip, both cars shift east. That leaves about 19" between them and about 10" on the far side of the right car, mirror to wall. The garage is 19\'-0" wide and cannot grow.',
    'FOR has the bedroom 3 closet above the old storage room. With the room cut back 3\'-6", that closet overhangs or shrinks. His call.',
    'The air handler is still about 45\' from the living room end. The mechanical engineer has to confirm one unit can serve the floor from there.',
    'The storage bay opening and the new garage door opening are both in a wall that carries the second floor: two headers.',
    '#For FOR to confirm',
    'Fire rating at the garage door and around the storage bay. Garage slab level at the house door. The open stair design and its guard. The stair window size and height.'], lw)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
