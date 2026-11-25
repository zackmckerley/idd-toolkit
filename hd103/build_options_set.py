"""2191 SW 23rd St (HD103): owner decision sheets for the kitchen position and the master bath (hd103/options.py).
    python3 hd103/build_options_set.py OPTDIR OUT.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen

OPT = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.25.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('1', '11.24.26', 'EDITS ON FOR PLANS'), ('2', DATE, 'OWNER OPTIONS')]
idd_sheet.remap = lambda s: s
INK = (0, 0, 0); RED = (0.78, 0.12, 0.18); P = 37.40; Y0 = 3020; K = 18.0     # 1/4" = 1'-0"

def wrap(s, width, size):
    out = []; cur = ''
    for w_ in s.split():
        t = (cur + ' ' + w_).strip()
        if idd_sheet._FR.text_length(t, fontsize=size) > width and cur: out.append(cur); cur = w_
        else: cur = t
    out.append(cur); return out

class S(Sheet):
    def frame2(self, titles, no):
        self.frame(None, '1/4" TO 1\'-0"', titles, no, legend_rule=False)
        for r in self.p.search_for('A-201 AND A-202, REV 1, 10.23.26'):
            self.p.add_redact_annot(r + (-1, -1, 1, 1), fill=(1, 1, 1)); self.p.apply_redactions(images=0, graphics=0)
            self.text(r.x0, r.y1 - 2.2, 'PRESENTATION, 11.24.26', 9, INK, raw=True)
    def para(self, x, y, s, width, size=9.0, bold=False, color=INK):
        for ln in wrap(s, width, size): self.text(x, y, ln, size, color, bold=bold, raw=True); y += size * 1.42
        return y

def sheet(doc, no, titles, heading, intro, x0px, rect, panels, both, pick):
    sh = S(doc); sh.frame2(titles, no)
    x0, y0, x1, y1 = rect; pw = (x1 - x0) * K; ph = (y1 - y0) * K; gap = (TB_X - FR.x0 - 40 - 3 * pw) / 2
    x = FR.x0 + 20; y = FR.y0 + 44
    sh.text(x, y, heading, 15, INK, serif=True, raw=True); y = sh.para(x, y + 18, intro, 1200, 9.5) + 8
    ty = y + 18; ymax = 0
    for i, (fn, name, tag, lines) in enumerate(panels):
        px = x + i * (pw + gap)
        im = Image.open(os.path.join(OPT, fn)).convert('RGB').crop((int(x0px + x0 * P), int(Y0 - y1 * P), int(x0px + x1 * P), int(Y0 - y0 * P)))
        jp = os.path.join(OPT, fn.replace('.png', '_p.jpg')); im.save(jp, quality=88)
        sh.text(px, ty - 6, name, 10.5, INK, bold=True, raw=True)
        if tag: sh.text(px + pw, ty - 6, tag, 9, RED, bold=True, align='r', raw=True)
        sh.p.insert_image(fitz.Rect(px, ty, px + pw, ty + ph), filename=jp)
        sh.p.draw_rect(fitz.Rect(px, ty, px + pw, ty + ph), color=RED if tag == 'RECOMMENDED' else (0.55, 0.55, 0.55), width=1.4 if tag == 'RECOMMENDED' else 0.5)
        yy = ty + ph + 18
        for ln in lines: yy = sh.para(px, yy, ln, pw, 9.6) + 4
        ymax = max(ymax, yy)
    yb = sh.para(x, ymax + 22, both, 1250, 10.0) + 26
    sh.text(x, yb, pick, 12, INK, bold=True, raw=True)
    return sh

doc = fitz.open()
sheet(doc, 'OP-1', ['OWNER OPTIONS', 'KITCHEN POSITION'], 'KITCHEN: WHERE IT SITS IN THE GREAT ROOM',
      'Ground floor, west bar, drawn on FOR\'s plan as revised 11.24.26. North is up: the living room and pool court are above, SW 23rd St is below. The walls, windows, scullery and powder room are the same in all three.',
      1115, (22.0, 17.2, 47.0, 50.0),
      [('k_current.png', 'AS DRAWN: KITCHEN IN THE MIDDLE', 'CURRENTLY DRAWN',
        ['FOR\'s layout. The kitchen sits beside the foyer and the pool court, and the dining room has the street window.',
         'Shortest walk from the kitchen to the pool, the living room and the garage.',
         'The scullery is behind the dining room, about 10\' from the island.']),
       ('k_A.png', 'OPTION A: KITCHEN SOUTH, RANGE WALL', '',
        ['A 48" range with a wall hood on the scullery wall. The sink is under the west window, and the fridge and wall oven stand on the solid stretch of wall.',
         'Prep island 3\'-0" x 7\'-0". Aisles 3\'-11" at the sink, 3\'-7" at the range and 3\'-8" at the street window.',
         'A wall hood vents better than a hood over an island. There is no island seating.']),
       ('k_B.png', 'OPTION B: KITCHEN SOUTH, FOR\'S ISLAND', 'RECOMMENDED',
        ['FOR\'s own island, cooktop and four stools, moved south as drawn. The sink is under the west window, and the fridge and wall oven stand on the solid stretch of wall.',
         'Aisles: 4\'-0" at the sink run, 3\'-7" at the street window, 3\'-2" behind the stools.',
         'Keeps FOR\'s kitchen and its seating. The cooktop stays on the island, so it needs an island hood or a downdraft, as it does today.'])],
      'Both south options: the scullery opens beside the kitchen, and the dining table moves to the middle, next to the foyer and the court, with FOR\'s dry bar under the west window. Guests arrive to the dining room, not the kitchen. The kitchen ends up about 15\' farther from the pool and the garage. No window or exterior wall changes.',
      'OWNER PICK:   AS DRAWN  /  A  /  B          DATE ________')
sheet(doc, 'OP-2', ['OWNER OPTIONS', 'MASTER BATH'], 'MASTER BATH AND CLOSETS',
      'Second floor, master suite, drawn on FOR\'s plan as revised 11.24.26. North is up: the bedroom is above, SW 23rd St is below. The bedroom is the same in all three.',
      1126, (22.0, 16.6, 49.0, 48.0),
      [('m_current.png', 'AS DRAWN: WET ROOM', 'CURRENTLY DRAWN',
        ['FOR\'s layout with a tub added. Wet room about 8\'-1" x 6\'-1", 9\'-10" double vanity, FOR\'s water closet.',
         'His and her closets about 8\'-9" x 5\'-7" each.',
         'The smallest change. The bath is still a 6\'-2" deep strip.']),
       ('m_A.png', 'OPTION A: SPA BATH AND ONE DRESSING ROOM', 'RECOMMENDED',
        ['Inside FOR\'s walls, with no exterior change. Bath 12\'-6" x 12\'-1": freestanding tub at the west window with open floor beside it, 5\'-4" x 4\'-2" shower, 9\'-0" double vanity, private water closet with a pocket door, linen cabinet.',
         'One dressing room, 9\'-3" x 12\'-1", with 24\' of wall for double hanging and a bench at the window.',
         'The bath and the dressing room each open off the bedroom.']),
       ('m_B.png', 'OPTION B: BATH EXTENDED 4\'-0" SOUTH', '',
        ['Bath 19\'-4" x 10\'-2" plus FOR\'s water closet: tub on the entry axis under a new street window, 7\'-7" double vanity, 5\'-6" x 4\'-6" shower, linen cabinet.',
         'FOR\'s his and her closets stay as revised.',
         'Adds about 83 SF over the dining room and scullery. It removes the south planter on that side and brings the upper wall flush with the ground floor at the left of the front. The new wall bears over the 10\'-7" street window: header by the engineer.'])],
      'Option A changes no exterior wall or window. Option B changes the front elevation, so FOR should draw that elevation before it is picked. In A the two south windows stay where FOR has them: one lights the vanity aisle and one the dressing room.',
      'OWNER PICK:   AS DRAWN  /  A  /  B          DATE ________')
fix_soft_hyphen(doc); doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, os.path.getsize(OUTPDF))
