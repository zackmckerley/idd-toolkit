"""2191 SW 23rd St (HD103): layout sheets drawn around movement routes (hd103/layouts.py).
    python3 hd103/build_layout_set.py LAYDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

LAY = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE')]
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
        self.p.draw_rect(fitz.Rect(px, py, px + pw, py + ph), color=RED if tag == 'PROPOSED' else (0.55, 0.55, 0.55), width=1.4 if tag == 'PROPOSED' else 0.5)
        return pw, ph
    def legend(self, x, y, rows):
        for col, t in rows:
            self.p.draw_line(fitz.Point(x, y - 3), fitz.Point(x + 26, y - 3), color=col, width=3.2); self.text(x + 34, y, t, 9.6, INK, raw=True); y += 15
        return y

doc = fitz.open(); X = FR.x0 + 20; TOP = FR.y0 + 44; RIGHT = TB_X - 20

# ---------------------------------------------------------------- LA-1 ground floor routes
sh = S(doc); sh.frame2(['LAYOUT BY ROUTE', 'GROUND FLOOR'], 'LA-1', 'NOT TO SCALE')
sh.text(X, TOP, 'GROUND FLOOR: HOW YOU MOVE THROUGH IT', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Both plans are FOR\'s plan as revised 11.24.26, north up, SW 23rd St at the bottom. Every route is drawn door to door. The numbers on the plans match the notes under them.', 900, 9.6) + 10
sh.legend(X + 1000, TOP - 2, [(GUEST, 'Guests'), (SERV, 'Family and groceries'), (SERVE, 'Serving')])
R = (20.5, 13.0, 88.5, 68.5); K = 11.0; py = y + 16
pw, ph = sh.panel('g_old_r.png', 1115, R, K, X, py, 'AS REVISED 11.24.26: KITCHEN IN THE MIDDLE', 'CURRENTLY DRAWN')
x2 = X + pw + 34
sh.panel('g_new_r.png', 1115, R, K, x2, py, 'PROPOSED: KITCHEN SOUTH, THROUGH SCULLERY, POWDER ROOM BY THE STAIR', 'PROPOSED')
yy = py + ph + 20
ya = sh.items(X, yy, [
    (1, GUEST, 'Front door. The island and the cooktop are the first thing on your left.'),
    (2, GUEST, 'To reach the living room a guest walks past the island stools and the cook.'),
    (3, GUEST, 'The powder room door opens off the dining room, next to the scullery opening.'),
    (4, SERV, 'Groceries: garage, across the foyer, to the fridge at the far end of the kitchen. About 44\'. The mudroom is an open alcove on the foyer, and the garage door opens beside it, not into it.'),
    (5, SERVE, 'The scullery is around a corner behind the dining table, about 12\' from the island. It works as a pantry, not as a second kitchen.')], pw)
yb = sh.items(x2, yy, [
    (1, GUEST, 'Front door. The court and pool are ahead, the dining table and the long west window are to the left. The scullery block hides the kitchen from the door.'),
    (2, GUEST, 'Foyer to living room: a clear walk past the end of the table, 3\'-4" at its tightest.'),
    (3, GUEST, 'Powder room off a small vestibule by the stair, out of sight of the kitchen, dining and living rooms.'),
    (4, SERV, 'The garage opens into a closed mudroom. Its door faces down the south wall of the foyer.'),
    (5, SERV, 'Groceries enter the scullery by its own door, about 33\' from the garage door. Cold goods go on through to the kitchen fridge, about 17\' more, north of the island and clear of the cook.'),
    (6, SERVE, 'Island to table is 4\'-2". Table to the court doors is about 15\'.')], pw)
y3 = max(ya, yb) + 12; cw = (RIGHT - X - 60) / 3
sh.items(X, y3, ['#What the routes showed',
    'The kitchen sat on the path between the front door and the living room.',
    'The powder room and the scullery shared one corner of the dining room.',
    'Moving the kitchen south only works if the scullery becomes a through room. If it does not, groceries cross the dining room.'], cw)
sh.items(X + cw + 30, y3, ['#What it costs',
    'The service route passes the front door inside the foyer. FOR\'s plan has the garage east and the kitchen west of the entry, so any layout does this.',
    'The island is about 28\' from the court doors. Today it is about 20\'.',
    'The guest closet drops from 9\'-0" to 3\'-8" deep.'], cw)
sh.items(X + 2 * (cw + 30), y3, ['#Not changed',
    'Exterior walls, windows, stair, pool court, living room, garage, second floor stack.'], cw)

# ---------------------------------------------------------------- LA-2 enlarged ground plans
sh = S(doc); sh.frame2(['LAYOUT BY ROUTE', 'KITCHEN AND SCULLERY'], 'LA-2', 'AS NOTED')
sh.text(X, TOP, 'KITCHEN, SCULLERY, DINING, POWDER ROOM AND MUDROOM', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'The proposed ground floor, enlarged. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 1250, 9.6) + 10
py = y + 16
pw, ph = sh.panel('g_new.png', 1115, (21.5, 17.0, 47.0, 48.5), 27.0, X, py, 'KITCHEN, SCULLERY AND DINING, 3/8" TO 1\'-0"', 'PROPOSED')
x2 = X + pw + 30
pw2, ph2 = sh.panel('g_new.png', 1115, (60.0, 33.5, 84.0, 58.0), 18.0, x2, py, 'POWDER ROOM, GUEST DOOR, MUDROOM, 1/4" TO 1\'-0"', 'PROPOSED')
lx = x2 + pw2 + 26; lw = RIGHT - lx
sh.items(lx, py + 4, ['#Powder room and guest suite',
    'Powder room 5\'-1" x 4\'-11" in the south end of the guest closet, with a 2\'-6" pocket door. You see the vanity from the door, not the toilet. It backs onto the guest bath, so the plumbing is next door.',
    'The guest bedroom door moves 3\'-0" north. The guest closet becomes 5\'-1" x 3\'-8".',
    '#Mudroom',
    'Two new partitions close it. The garage door now opens into the mudroom, and the bench and lockers are no longer on view from the foyer.',
    '#For FOR to confirm',
    'Hood duct through the west pier. Plumbing for the relocated powder room. Island sink waste and vent in the slab. The paneled wall and its concealed door. Guest closet size.'], lw)
ny = py + ph2 + 26; cw = (RIGHT - x2 - 30) / 2
sh.items(x2, ny, ['#Kitchen, 14\'-8" x 15\'-5"',
    'Range and fridge stand on the only solid stretch of the west wall, so the hood ducts straight out and no window is lost.',
    'The main sink and dishwasher are in the island, facing the range. Sink, range and fridge are within 7\' of each other, and nobody walks through that triangle.',
    'Island 3\'-6" x 8\'-0" with three stools. Aisles: 3\'-7" at the range, 3\'-7" at the street counter, 5\'-6" behind the stools.',
    'The fridge is at the dining end of the run, so a guest can reach it without entering the work zone.',
    'The street window gets a 12\'-7" coffee and breakfast counter.',
    '#Dining',
    'FOR\'s table for ten turns to run east and west beside the long west window, with his bar on that wall. The table sits 4\'-2" north of the island.'], cw)
sh.items(x2 + cw + 30, ny, ['#Scullery, 7\'-1" x 15\'-2"',
    'It takes the old powder room and becomes a through room: a 3\'-6" opening to the kitchen and a 2\'-10" pocket door to the foyer. Aisle 3\'-4".',
    'FOR\'s sink and dishwasher stay where they are. Added: second ovens and coffee, a freezer, and 11\'-8" of tall pantry.',
    'The wall facing the dining room is 7\'-6" wide with the scullery door in it. Finish it as one paneled wall with a concealed door. The art wall there goes away; the two beside the court doors stay.'], cw)

# ---------------------------------------------------------------- LA-3 master suite
sh = S(doc); sh.frame2(['LAYOUT BY ROUTE', 'MASTER SUITE'], 'LA-3', '3/8" TO 1\'-0"')
sh.text(X, TOP, 'MASTER SUITE: BEDROOM, BATH AND DRESSING ROOM AS A LOOP', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Second floor, FOR\'s plan as revised 11.24.26, north up. No exterior wall or window changes. The bedroom is untouched.', 1250, 9.6) + 10
py = y + 16; R = (24.0, 21.0, 50.0, 48.0)
pw, ph = sh.panel('m_old_r.png', 1126, R, 27.0, X, py, 'AS REVISED 11.24.26', 'CURRENTLY DRAWN')
x2 = X + pw + 30
sh.panel('m_new_r.png', 1126, R, 27.0, x2, py, 'PROPOSED: LOOP SUITE', 'PROPOSED')
yy = py + ph + 20
ya = sh.items(X, yy, [
    (1, SERV, 'One way in and out: a 3\'-9" passage between the two closets.'),
    (2, SERV, 'The bath is a 6\'-2" deep strip. The water closet is at the far end, about 21\' from the bed.'),
    (3, GUEST, 'Both closets open off the passage, so anyone dressing stands in the only route to the bath. Each closet is 8\'-9" x 5\'-7".')], pw)
yb = sh.items(x2, yy, [
    (1, SERV, 'A pocket door on FOR\'s axis leads from the bedroom to the bath. Bed to water closet is about 15\'.'),
    (2, SERV, 'Bath 12\'-6" x 12\'-1". Freestanding tub at the west window. Vanity 7\'-7" with the south window between the two mirrors, and a linen tower. Shower 5\'-5" x 4\'-0". Water closet 3\'-5" x 4\'-11" with its own door.'),
    (3, SERV, 'A second pocket door leads from the bath straight to the dressing room. Shower, dress and leave without crossing the bedroom.'),
    (4, SERV, 'Dressing room 9\'-2" x 12\'-1" with its own opening to the bedroom. 17\'-7" of wall for double hanging (about 35\' of rod), a dresser under the window, and shoes.')], pw)
y3 = max(ya, yb) + 10; cw = (RIGHT - X - 90) / 4
sh.items(X, y3, ['#Why a loop',
    'Two people can use the suite at once. One sleeps while the other goes bath, dressing room, out.',
    'Every room has two ways out, so nobody stands in the only route.'], cw)
sh.items(X + cw + 30, y3, ['#What I removed',
    'The passage between the closets, and the split into his and her closets. One room works harder than two 5\'-7" rooms with a door each.'], cw)
sh.items(X + 2 * (cw + 30), y3, ['#What it costs',
    'The water closet and the shower back onto the bedroom wall. That wall needs sound insulation.',
    'Three door openings in place of one.'], cw)
sh.items(X + 3 * (cw + 30), y3, ['#For FOR to confirm',
    'Tub and shower drains over the dining room and kitchen below. Pocket door framing in the bedroom wall.'], cw)

fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
