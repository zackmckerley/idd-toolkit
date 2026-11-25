"""2191 SW 23rd St (HD103): kitchen planned to the NKBA guidelines (hd103/layouts.py, ground_new guest=FOR scullery=K).
    python3 hd103/build_mudroom.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST'), ('5', DATE, 'GUEST SUITE ALTERNATES'), ('6', DATE, 'OWNER KITCHEN MARKUP'), ('7', DATE, 'KITCHEN TO NKBA GUIDELINES'), ('8', DATE, 'FRIDGE AND FREEZER ON RANGE WALL'), ('9', DATE, 'MUDROOM AND GARAGE')]
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


sh = S(doc); sh.frame2(['GARAGE AND MUDROOM', 'ROUTES, BEFORE AND AFTER'], 'GM-1', '1/4" TO 1\'-0"')
sh.text(X, TOP, 'GARAGE AND MUDROOM: HOW THEY TIE TOGETHER', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Ground floor, southeast corner, north up, on the KP-3 plan. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 1250, 9.6) + 10
R = (58.0, 16.0, 89.0, 49.0); K = 18.0; py = y + 16
pw, ph = sh.panel('gm_old_r.png', 1115, R, K, X, py, 'AS DRAWN ON KP-3', 'CURRENTLY DRAWN')
x2 = X + pw + 30
sh.panel('gm_new_r.png', 1115, R, K, x2, py, 'RECOMMENDED', 'PROPOSED')
yy = py + ph + 20
sh.items(X, yy, [
    (1, SERV, 'The garage door and the foyer door are both at the north end, 4\'-11" apart, and both swing in or beside the room. An open garage door spans the whole width.'),
    (2, SERV, 'You cross one corner of the mudroom and leave. The route never passes the bench.'),
    (3, SERVE, 'The rest is a dead-end passage 4\'-11" wide and about 17\' long, 3\'-5" clear beside the bench.')], pw)
sh.items(x2, yy, [
    (1, SERV, 'The garage door swings out onto a 3\'-0" x 3\'-4" landing in front of the cars. No door swings inside the mudroom.'),
    (2, SERV, 'Mudroom 4\'-11" x 10\'-3". You step in facing the bench and hooks (7\'-11"), with four lockers on the end wall. Everything is within two steps of the door.'),
    (3, SERV, 'A 2\'-6" pocket door leads north to the stair hall: 6\' to the stair, 9\' to the guest suite, and west down the foyer to the kitchen. The mudroom no longer opens onto the foyer by the front door.'),
    (4, SERVE, 'The south half of the strip opens to the garage through a 6\'-6" opening: a 4\'-10" x 9\'-7" bay for bins, bikes and shelves. The garage had no storage.')], pw)
lx = x2 + pw + 30; lw = RIGHT - lx
sh.items(lx, py + 4, ['#Why it felt cramped',
    'The room is only 4\'-11" wide and that cannot grow: the garage is at its 19\'-0" minimum, the east wall is on the setback line, and the entry court is on the other side.',
    'A narrow room works when it is short and nothing swings in it. This one was 20\' long with two door swings at one end.',
    'The door from the garage has to stay in front of the cars, so the route will always enter at the north end. The fix is to put the working part of the mudroom there and give the rest away.',
    '#What it costs',
    'A landing in the garage in front of the left car, 3\'-0" deep. As drawn it clears the car by about 8", so the left car has to stop short of it.',
    'A 6\'-6" opening in the wall between the garage and the strip. It carries the second floor, so it needs a header.',
    'Bench drops from about 11\' to 7\'-11", with lockers added.',
    '#For FOR to confirm',
    'Garage slab level and the step at the landing. Fire rating of the garage door and of the wall and ceiling around the storage bay. Header size.',
    '#Option',
    'A door from the storage bay to the driveway, beside the garage door, so bins roll straight out. It changes the front elevation.'], lw)
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
