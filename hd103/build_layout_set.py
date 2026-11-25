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
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS'), ('3', DATE, 'LAYOUTS BY ROUTE'), ('4', DATE, 'KITCHEN NORTH, GUEST EAST')]
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
sh.panel('g_new_r.png', 1115, R, K, x2, py, 'PROPOSED: KITCHEN TO THE FOYER LINE, THROUGH SCULLERY, GUEST WING WIDENED', 'PROPOSED')
yy = py + ph + 20
ya = sh.items(X, yy, [
    (1, GUEST, 'Front door. The island and the cooktop are the first thing on your left.'),
    (2, GUEST, 'To reach the living room a guest walks past the island stools and the cook.'),
    (3, GUEST, 'The powder room door opens off the dining room, next to the scullery opening.'),
    (4, SERV, 'Groceries: garage, across the foyer, to the fridge at the far end of the kitchen. About 45\'. The mudroom is an open alcove on the foyer, and the garage door opens beside it, not into it.'),
    (5, SERVE, 'The scullery is around a corner behind the dining table, about 23\' from the kitchen sink. It works as a pantry, not as a second kitchen.')], pw)
yb = sh.items(x2, yy, [
    (1, GUEST, 'Front door. The court and pool are ahead, the dining table and the long west window are to the left. The scullery block screens the range and the working side of the island; from the middle of the foyer you see the island\'s north end.'),
    (2, GUEST, 'Foyer to living room: an open walk past the end of the table, 4\'-0" at its tightest.'),
    (3, GUEST, 'Powder room off a small vestibule by the stair, out of sight of the kitchen, dining and living rooms.'),
    (4, SERV, 'The garage opens into a closed mudroom. Its door faces down the south wall of the foyer.'),
    (5, SERV, 'Dry goods go straight into the scullery by its own door, about 27\' from the garage door.'),
    (6, SERV, 'Cold goods go to the kitchen fridge along the south edge of the dining area, about 43\' from the garage door. Today it is about 45\'.'),
    (7, SERVE, 'Scullery to kitchen through the south aisle, 13\'. Island to the dining chairs, 4\'-1". Table to the court doors, about 14\'.')], pw)
y3 = max(ya, yb) + 12; cw = (RIGHT - X - 60) / 3
sh.items(X, y3, ['#What the routes showed',
    'The kitchen sat on the path between the front door and the living room.',
    'The powder room and the scullery shared one corner of the dining room.',
    'Moving the kitchen south only works if the scullery becomes a through room. If it does not, groceries cross the dining room.'], cw)
sh.items(X + cw + 30, y3, ['#What it costs',
    'The service route passes the front door inside the foyer. FOR\'s plan has the garage east and the kitchen west of the entry, so any layout does this.',
    'The island is about 28\' from the court doors. Today it is about 20\'.',
    'FOR\'s dry bar leaves the west wall. The bar moves to the street counter.',
    'The guest wing\'s east wall moves out 5\'-3" to the garage wall line, about 105 SF (estimate). The exterior shape changes on the east side only.',
    'The powder room shares a 3\' x 3\' vestibule with the guest bedroom door.'], cw)
sh.items(X + 2 * (cw + 30), y3, ['#Not changed',
    'West, south and north exterior walls, windows, stair, pool court, living room, garage, second floor.'], cw)

# ---------------------------------------------------------------- LA-2 enlarged ground plans
sh = S(doc); sh.frame2(['LAYOUT BY ROUTE', 'KITCHEN AND SCULLERY'], 'LA-2', 'AS NOTED')
sh.text(X, TOP, 'KITCHEN, SCULLERY, DINING, POWDER ROOM AND MUDROOM', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'The proposed ground floor, enlarged: the kitchen plan is at 3/8 inch to the foot and the powder room plan at 1/4 inch. Dimensions are scaled from FOR\'s presentation plan and are good to about 2".', 1250, 9.6) + 10
py = y + 16
pw, ph = sh.panel('g_new.png', 1115, (21.5, 17.0, 47.0, 47.0), 27.0, X, py, 'KITCHEN, SCULLERY AND DINING', 'PROPOSED')
x2 = X + pw + 30
pw2, ph2 = sh.panel('g_new.png', 1115, (60.0, 33.5, 89.0, 68.5), 18.0, x2, py, 'GUEST SUITE, POWDER ROOM, MUDROOM', 'PROPOSED')
lx = x2 + pw2 + 26; lw = RIGHT - lx
sh.items(lx, py + 4, ['#Guest suite',
    'The east wall moves out 5\'-3" to the line of the garage and storage wall, so the house has one straight east wall. About 105 SF added (estimate).',
    'Walk-in closet 4\'-6" x 9\'-8" off the bedroom, with 9\'-8" of double hanging. The old closet, 5\'-4" x 3\'-7", stays for linen and luggage.',
    'The bath opens into the new bay: a freestanding tub at a new east window, and a linen cabinet. Vanity, toilet and shower stay where FOR has them.',
    '#Powder room',
    '5\'-4" x 5\'-1" with a 2\'-4" pocket door. The toilet is in the far corner, facing away from the hall. The guest bedroom door moves 2\'-8" north.',
    '#Mudroom',
    'Two new partitions close it, so the garage opens into the mudroom. Its door parks on the foyer\'s south wall, 3\'-5" clear of the front door.',
    '#For FOR to confirm',
    'East side setback and lot coverage with the wider guest wing. Beam over the 5\'-10" opening in the old east wall, which carries the second floor. Roof over the new bay, or carry the junior master out over it (about 105 SF more).',
    'Sill heights at the street window and the short west window. Hood duct through the west pier. Island sink waste in the slab. Powder room plumbing. The paneled wall and its concealed door.'], lw)
ny = py + ph2 + 26; cw = (lx - 26 - x2 - 30) / 2
sh.items(x2, ny, ['#Kitchen, 14\'-8" x 17\'-4"',
    'The kitchen and scullery now run north to the line of the foyer\'s south wall, 1\'-9" more than before. No exterior wall moves for this.',
    'Range and fridge on the solid west pier with 15" of counter between them. Sink and dishwasher in the island, facing the range. All three within 6\'.',
    'Island 4\'-0" x 9\'-8" with four stools. Aisles: 3\'-9" at the range, 3\'-7" at the fridge and the street counter, 3\'-4" behind the stools.',
    '#Dining',
    'FOR\'s table for ten, turned east and west. Clear space: 4\'-1" to the island, 3\'-4" to the west window, 8\'-0" to the foyer. The dining zone is 11\'-0" deep, down from 12\'-9".'], cw)
sh.items(x2 + cw + 30, ny, ['#Scullery, 7\'-1" x 17\'-0"',
    'A through room: a 3\'-4" opening to the kitchen\'s south aisle and a 2\'-6" concealed door to the foyer, swinging in. Aisle 4\'-0".',
    'FOR\'s sink and dishwasher stay. Added: ovens and coffee, a freezer and tall pantry on the south wall (5\'-0"), and 10\'-7" of 12" pantry shelves.',
    'The wall facing the dining room is 7\'-6" wide, flush with the foyer wall. Finish both as one paneled wall with the door concealed in it.'], cw)

# ---------------------------------------------------------------- LA-3 master suite
sh = S(doc); sh.frame2(['LAYOUT BY ROUTE', 'MASTER SUITE'], 'LA-3', '3/8" TO 1\'-0"')
sh.text(X, TOP, 'MASTER SUITE: BEDROOM, BATH AND DRESSING ROOM AS A LOOP', 15, INK, serif=True, raw=True)
y = sh.para(X, TOP + 18, 'Second floor, FOR\'s plan as revised 11.24.26, north up. No exterior wall or window changes. The bedroom keeps its size and furniture; its south wall gets two doors in place of one opening.', 1250, 9.6) + 10
py = y + 16; R = (24.9, 21.0, 50.0, 48.0)
pw, ph = sh.panel('m_old_r.png', 1126, R, 27.0, X, py, 'AS REVISED 11.24.26', 'CURRENTLY DRAWN')
x2 = X + pw + 30
sh.panel('m_new_r.png', 1126, R, 27.0, x2, py, 'PROPOSED: LOOP SUITE', 'PROPOSED')
yy = py + ph + 20
ya = sh.items(X, yy, [
    (1, SERV, 'One way in and out: a 3\'-9" passage between the two closets.'),
    (2, SERV, 'The bath is a 6\'-2" deep strip. The water closet is at the far end, about 22\' from the bed.'),
    (3, GUEST, 'Both closets open off the passage, so anyone dressing stands in the only route to the bath. Each closet is 8\'-9" x 5\'-7".')], pw)
yb = sh.items(x2, yy, [
    (1, SERV, 'A door at the foot of the bed leads to the bath. Bed to water closet is about 16\'. The water closet is in the far corner, 9\' from the pillows.'),
    (2, SERV, 'Bath 12\'-4" x 12\'-1". Freestanding tub at the west window, 12" off the wall. Vanity 7\'-5" with the south window between the two mirrors. Shower 5\'-2" x 3\'-7". Water closet 3\'-5" x 4\'-11" with its own door.'),
    (3, SERV, 'A pocket door leads from the bath straight to the dressing room. Shower and dress without walking back past the bed.'),
    (4, SERV, 'Dressing room 9\'-2" x 12\'-1" with its own pocket door to the bedroom, on the side nearest the suite door. About 16\' of wall for double hanging, a dresser under the window, and linen.')], pw)
y3 = max(ya, yb) + 10; cw = (RIGHT - X - 90) / 4
sh.items(X, y3, ['#Why a loop',
    'Two people can use the suite at once. One sleeps while the other goes bath, dressing room, out.',
    'Bath and dressing room each have two ways out, so nobody stands in the only route.'], cw)
sh.items(X + cw + 30, y3, ['#What I removed',
    'The passage between the closets, and the split into his and her closets. One room works harder than two 5\'-7" rooms with a door each.'], cw)
sh.items(X + 2 * (cw + 30), y3, ['#What it costs',
    'The shower and the water closet back onto the bedroom wall. Build it as a double wall with insulation, and keep the shower valve on the east partition.',
    'Three doors in place of one opening.'], cw)
sh.items(X + 3 * (cw + 30), y3, ['#For FOR to confirm',
    'Toilet, tub and shower wastes over the dining room and kitchen ceiling below. Pocket door framing. Tub filler location.'], cw)

fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
