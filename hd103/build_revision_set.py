"""2191 SW 23rd St (HD103): review set for the plan revisions made on FOR's drawings (hd103/revise_plans.py).
    python3 hd103/build_revision_set.py REVDIR OUT.pdf
SK-0 what changed and the areas, FOR's plans beside the revised ones. SK-1 ground floor, SK-2 second floor, changes tinted and numbered."""
import sys, os, json
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, W, H, fix_soft_hyphen

REV = sys.argv[1]; OUTPDF = sys.argv[2]; DATE = '11.24.26'
idd_std.PROJECT.update({'name': 'VILLA SHENANDOAH', 'address1': '2191 SW 23RD STREET', 'address2': 'MIAMI, FL 33145', 'no': 'HD103', 'date': DATE})
idd_sheet.PRINT_DATE = DATE; idd_sheet.REVS = [('0', DATE, 'OWNER SCHEMATIC (VOID)'), ('1', DATE, 'EDITS ON FOR PLANS')]
idd_sheet.remap = lambda s: s
INK = (0, 0, 0); P = 37.40; Y0 = 3020
C1 = json.load(open(os.path.join(REV, 'f1_changes.json'))); C2 = json.load(open(os.path.join(REV, 'f2_changes.json')))
CROP = (-5.0, -5.0, 96.5, 80.0)            # ft: the lot with its streets

def crop(path, x0px, scale=0.62, q=88):
    im = Image.open(path).convert('RGB')
    box = (int(x0px + CROP[0] * P), int(Y0 - CROP[3] * P), int(x0px + CROP[2] * P), int(Y0 - CROP[1] * P))
    c = im.crop(box); c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
    out = path.replace('.png', '_c%d.jpg' % int(scale * 100)) if path.startswith(REV) else os.path.join(REV, os.path.basename(path).replace('.png', '_c%d.jpg' % int(scale * 100)))
    c.save(out, quality=q); return out, c.width / c.height

def wrap(s, width, size):
    out = []; cur = ''
    for w_ in s.split():
        t = (cur + ' ' + w_).strip()
        if idd_sheet._FR.text_length(t, fontsize=size) > width and cur: out.append(cur); cur = w_
        else: cur = t
    out.append(cur); return out

class S(Sheet):
    def frame2(self, titles, no, scale):
        self.frame(None, scale, titles, no, legend_rule=False)
        for r in self.p.search_for('A-201 AND A-202, REV 1, 10.23.26'):
            self.p.add_redact_annot(r + (-1, -1, 1, 1), fill=(1, 1, 1)); self.p.apply_redactions(images=0, graphics=0)
            self.text(r.x0, r.y1 - 2.2, 'PRESENTATION, 11.24.26', 9, INK, raw=True)
    def para(self, x, y, s, width, size=9.0, lead=None, bold=False):
        lead = lead or size * 1.42
        for ln in wrap(s, width, size): self.text(x, y, ln, size, INK, bold=bold, raw=True); y += lead
        return y
    def bubble(self, x, y, n, r=9.5):
        sh = self.p.new_shape(); sh.draw_circle(fitz.Point(x, y), r); sh.finish(color=None, fill=(0.78, 0.12, 0.18)); sh.commit()
        self.p.insert_text((x - idd_sheet._FB.text_length(str(n), fontsize=10) / 2, y + 3.6), str(n), fontsize=10, fontname='cgb', color=(1, 1, 1))

def plan_sheet(doc, img, x0px, changes, title, no, lead_note):
    sh = S(doc); sh.frame2(['FOR PLAN WITH OWNER', title], no, '3/16" TO 1\'-0"')
    path, ar = crop(img, x0px)
    ph = (CROP[3] - CROP[1]) * 13.5; pw = ph * ar; x = FR.x0 + 8; y = FR.y0 + (FR.height - ph) / 2
    sh.p.insert_image(fitz.Rect(x, y, x + pw, y + ph), filename=path)
    cx = x + pw + 26; cw = TB_X - cx - 22; yy = FR.y0 + 46
    sh.text(cx, yy, 'CHANGES ON THIS FLOOR', 11, INK, bold=True, raw=True); yy += 18
    yy = sh.para(cx, yy, lead_note, cw, 8.6) + 8
    for c in sorted(changes, key=lambda c: c['n']):
        sh.bubble(cx + 9.5, yy + 1, c['n']); y2 = sh.para(cx + 28, yy + 4, c['text'], cw - 28, 9.2); yy = max(y2, yy + 24) + 7
    yy += 6
    sh.para(cx, yy, 'Everything not tinted is FOR Architecture Co.\'s drawing, unchanged. The tinted areas are the owner\'s edits, drawn on FOR\'s plan for FOR to verify and redraw.', cw, 8.6)
    return sh

def summary(doc):
    sh = S(doc); sh.frame2(['WHAT CHANGED', 'AND THE AREAS'], 'SK-0', 'NOT TO SCALE')
    x = FR.x0 + 26; y = FR.y0 + 46
    sh.text(x, y, 'VILLA SHENANDOAH: OWNER\'S CHANGES ON FOR\'S PLANS', 16, INK, serif=True, raw=True); y += 20
    y = sh.para(x, y, 'FOR\'s design is kept: the U shape around the pool court, the entry court, the great room bar, the stair, the guest wing, the den and every bedroom. The house gets wider in two places only. The west bar moves 3\'-0" toward SW 22nd Ave on both floors, and the garage side of the east wing moves 5\'-2" to FOR\'s own 7\'-6" setback line. The front goes from 57\'-0" to about 65\'-2".', 980, 10) + 10
    tw = 505.0; gap = 14.0; th = 0
    panels = [('FOR, GROUND FLOOR', '/home/claude/deck/img_p3_11.png', 1115), ('REVISED, GROUND FLOOR', os.path.join(REV, 'f1_marked.png'), 1115),
              ('FOR, SECOND FLOOR', '/home/claude/deck/img_p4_22.png', 1126), ('REVISED, SECOND FLOOR', os.path.join(REV, 'f2_marked.png'), 1126)]
    for i, (t, pth, x0px) in enumerate(panels):
        path, ar = crop(pth, x0px, scale=0.42, q=86); th = tw / ar
        px = x + (i % 2) * (tw + gap); ty = y + 14 + (i // 2) * (th + 26)
        sh.text(px, ty - 5, t, 9, INK, bold=True, raw=True)
        sh.p.insert_image(fitz.Rect(px, ty, px + tw, ty + th), filename=path)
        sh.p.draw_rect(fitz.Rect(px, ty, px + tw, ty + th), color=(0.6, 0.6, 0.6), width=0.4)
    c = x + 2 * tw + gap + 26; cw = TB_X - c - 20; yy = FR.y0 + 100
    sh.text(c, yy, 'AREAS (SF, ESTIMATED)', 10, INK, bold=True, raw=True); yy += 17
    rows = [('', 'FOR 11.24', 'REVISED'), ('Ground floor, under air', '1,735', '1,858'), ('Second floor, under air', '1,706', '1,914'), ('Total under air', '3,441', '3,772'),
            ('Garage, clear', "12'-6\" x 20'", "19'-0\" x 20'"), ('Pool', "about 7' x 12'", "12' x 18'"), ('Bedrooms / baths', '5 + den / 5.5', '5 + den / 5.5'),
            ('Second story coverage', '24.1%', '27.0%')]
    for a, b, c_ in rows:
        sh.text(c, yy, a, 8.8, INK, raw=True); sh.text(c + cw - 78, yy, b, 8.8, INK, align='r', raw=True); sh.text(c + cw, yy, c_, 8.8, INK, align='r', bold=bool(a == 'Total under air'), raw=True); yy += 14
    yy = sh.para(c, yy + 3, 'FOR\'s figures are as printed on its plans. The revised figures add the widened strips (to the exterior face) and are estimates until FOR redraws. Coverage is on the 7,077 SF county lot area. The cap is 30% if the lot is T3-R or T3-L. At $1,000/SF the revised house is about $3.77MM.', cw, 8.4) + 12
    sh.text(c, yy, 'WHAT THE OWNER ASKED FOR', 10, INK, bold=True, raw=True); yy += 16
    for t in ['Two-car garage: change 4.', 'Scullery: change 2.', 'Larger pool: change 6.', 'Mudroom downstairs: change 3.', 'Laundry upstairs: change 10.', 'Better master bath and closets: changes 7, 8 and 9.']:
        yy = sh.para(c, yy, t, cw, 8.8) + 2
    yy += 10; sh.text(c, yy, 'KEPT AS FOR DREW IT', 10, INK, bold=True, raw=True); yy += 16
    yy = sh.para(c, yy, 'Entry court and covered entry, foyer, powder room, stair, guest suite, junior master, Bedroom 4, Bath 4, den, master water closet. The kitchen run, island, living and dining furniture, Bath 3, Bedroom 3, the terrace and the planters keep FOR\'s layout and move or lengthen with their walls.', cw, 8.8) + 12
    sh.text(c, yy, 'FOR THE ARCHITECT TO CONFIRM', 10, INK, bold=True, raw=True); yy += 16
    for t in ['A. Elevations and renders: the front is about 8\'-2" wider and the garage door is 16\'-0". FOR to restudy the front with the wider garage.',
              'B. The east wing steps back 5\'-2" at the guest suite, behind the stair. Running the wall straight instead adds about 208 SF to the guest suite and junior master.',
              'C. Pool: 12\' x 18\' is about the most FOR\'s court holds, with 3\'-0" of deck at the foyer doors and the coping 5\'-0" off the north line. A 25\' pool needs the court rebuilt. Pool barrier per the Florida pool safety act.',
              'D. Setbacks: FOR draws 7\'-6" north and east. Miami 21 lists a 20\' rear setback for T3. Confirm the frontage reading, the transect and the survey before redrawing.',
              'E. Mudroom is 4\'-11" wide so the garage can be 19\'-0". A 5\'-5" mudroom leaves an 18\'-6" garage.',
              'F. Master bath: extending it 4\'-0" south over the dining room would add a linen wall and a larger wet room, at the cost of the southwest planter on the front.',
              'G. Structure and roof over the widened bays. The dashed roof and setback lines on these plans are FOR\'s and are not updated.']:
        yy = sh.para(c, yy, t, cw, 8.4) + 4
    return sh

doc = fitz.open()
summary(doc)
plan_sheet(doc, os.path.join(REV, 'f1_marked.png'), 1115, C1, 'CHANGES, GROUND FLOOR', 'SK-1', 'The west wall and the garage side of the east wing move out. The pool grows inside FOR\'s court.')
plan_sheet(doc, os.path.join(REV, 'f2_marked.png'), 1126, C2, 'CHANGES, SECOND FLOOR', 'SK-2', 'The second floor follows the ground floor walls. The planter ledges move with them.')
fix_soft_hyphen(doc)
doc.save(OUTPDF, garbage=3, deflate=True); print('saved', OUTPDF, len(doc), os.path.getsize(OUTPDF))
