"""Simplified base plans from FOR Architecture's REV 1 floor plans (A-201, A-202, 10.23.26), drawn in the same display space as the YL base
they replace (rotated 22 x 17 page, 3/16 in. = 1 ft, 1.125 pt per inch), so every consumer that clips the old base by display coordinates
(the room key plans) lands on the same building.

Kept: walls (solid grey, closed between their faces from FOR's wall layers), doors, windows, bath and kitchen fixtures, millwork, equipment,
stairs, planters, porch, railings, the open-to-above X, room names in FOR's words. Dropped: dimensions, tags, keynotes, clouds, grids,
section and elevation marks, notes, hatches, title block.
Outputs: 261105.3350THOMAS.Base-clean.pdf and 261105.3350THOMAS.Base-furn.pdf (identical, the furniture variant has no furniture now),
pages 0, 1 = floors 1, 2. Also base_rev1.json: wall polygons and the FOR-to-display transform per floor."""
import json, sys
import numpy as np, cv2, pymupdf as fitz
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import replay as R, walls as Wm
from idd_sheet import REG_BUF

OUT = '/home/claude/flrwork/261105.3350THOMAS.Base-clean.pdf'
OUT_FURN = '/home/claude/flrwork/261105.3350THOMAS.Base-furn.pdf'
OUT_KEY = '/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'      # no text: key plans at 1/4 to 3/4 in. write their own labels
GEO = '/home/claude/flrwork/rev1/base_rev1.json'
WALL = (0.353, 0.353, 0.353)            # the YL base's wall grey
LINE = (0.25, 0.25, 0.25)
TEXT = (0.251, 0.251, 0.251)
ZY = 16 / 3                              # YL display px per pt in the alignment (6 px per inch, same as the FOR mask)

def transform(floor):
    """FOR sheet point -> display point on the old YL base (scale 0.75, translation from the phase correlation of the two wall masks)."""
    dx, dy = np.load(f'/home/claude/flrwork/rev1/shift_{floor}.npy')
    a = 1.0 / ZY
    return lambda x, y: (Wm.Z * a * (x - R.PLAN.x0) + dx * a, Wm.Z * a * (y - R.PLAN.y0) + dy * a)

LINE_LAYERS = {   # layer suffix -> width (display pt)
    'A-DOOR': 0.35, 'A-WINDOW': 0.3, 'A-EQPM-BATH': 0.3, 'A-EQPM-KIT': 0.3, 'A-NEW-MILLWORK': 0.3, 'P-NEW-EQUIPMENT': 0.3,
    'P-NEW-STAIR': 0.3, 'A-SITE-PLANTER': 0.3, 'A-SITE-PORCH': 0.3, 'A-GLASS RAILING': 0.3, 'P-RAILING': 0.25, 'P-WALL': 0.3}

LABELS = {   # FOR's room names at FOR's label positions (FOR sheet pt), size, lines
    1: [('KITCHEN', 560, 250, 9.4), ('DINING', 684, 356, 9.4), ('PANTRY', 493, 576, 9.4), ('GUEST\nBEDROOM', 487, 728, 9.4),
        ('LIVING ROOM', 905, 600, 9.4), ('CLOSET', 1012, 920, 7.0), ('GUEST\nBATHROOM', 435, 828, 5.0), ('W.I.C.', 570, 872, 7.0),
        ('STORAGE', 385, 1118, 7.0), ('ENTRY', 791, 1182, 9.4), ('OFFICE', 973, 1353, 9.4), ('COVERED\nPARKING', 512, 1210, 9.4),
        ('POWDER\nROOM', 981, 1172, 7.0), ('STORAGE', 551, 145, 7.0), ('STORAGE', 427, 145, 7.0), ('LAUNDRY', 680, 884, 7.0),
        ('UTILITY\nROOM', 418, 987, 9.4), ('CLOSET', 671, 1093, 7.0),
        ('FRIDGE', 485, 193, 5.0), ('FREEZER', 537, 193, 5.0), ('BUILT-IN\nOVEN', 486, 522, 5.0), ('BAR', 580, 514, 5.0), ('AHU', 607, 1089, 5.0),
        ('W/D', 630, 881, 5.0), ('DW &\nMW', 474, 612.5, 5.0), ('UC\nFRIDGE', 516, 612.5, 5.0), ('CHUTE', 640, 924, 5.0)],
    2: [('TERRACE', 545, 1389, 9.4), ('TERRACE', 972, 1358, 9.4), ('MASTER\nBEDROOM', 841, 1085, 9.4), ('MASTER\nBATH', 567, 1150, 9.4),
        ('WATER\nCLOSET', 662, 1219, 5.0), ('OPEN TO\nBELOW', 905, 701, 9.4), ('DEN /\nPLAYROOM', 661, 743, 9.4), ('BEDROOM\n2', 592, 560, 9.4),
        ('BATH\n2', 523, 360, 6.4), ('BATH\n3', 523, 228, 6.4), ('BEDROOM\n3', 720, 272, 9.4), ('W.I.C.', 568, 900, 9.4),
        ('LINEN CLOSET', 898, 956, 5.0), ('W/D', 832, 945, 5.0), ('CLOSET', 1015, 1108, 6.4), ('CLOSET', 485, 671, 6.4), ('AHU', 482, 799, 5.0),
        ('PLANTER BED', 791, 1270, 6.4)]}

OPEN_X = {1: (764.0, 555.4, 1046.2, 845.0), 2: (766.0, 555.4, 1046.2, 844.0)}   # the double-height volume, the extent of FOR's dashed P-ABOVE diagonals
EXTRA = {1: [('P-ABOVE', (454, 600, 536, 641)),          # the clouded pantry counter: DW & MW and UC fridge, dashed under the top
             ('A-WALL-HEAD', (618, 903, 690, 948))],     # the laundry chute, dashed
         2: []}

def wall_polys(floor):
    m = Wm.line_mask(floor, lambda n: Wm.is_wall(n) and not n.endswith('P-WALL'))
    k = int(16 * 1.5 * Wm.Z) | 1
    cx = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, k)))
    cy = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)))
    w = cx | cy
    w = cv2.morphologyEx(w, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    cs, hier = cv2.findContours(w, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for i, c in enumerate(cs):
        if hier[0][i][3] >= 0: continue                         # holes are collected with their parent
        if cv2.contourArea(c) < 30: continue
        rings = [c]
        ch = hier[0][i][2]
        while ch >= 0:
            if cv2.contourArea(cs[ch]) > 3000: rings.append(cs[ch])  # keep real holes, drop slivers between hatch strokes
            ch = hier[0][ch][0]
        out.append([[(float(x) / Wm.Z + R.PLAN.x0, float(y) / Wm.Z + R.PLAN.y0) for x, y in cv2.approxPolyDP(r, 0.8, True).reshape(-1, 2)] for r in rings])
    return out

def fill_only(sh, dr, T):
    for it in dr['items']:
        k = it[0]
        if k == 'l': sh.draw_line(T(it[1]), T(it[2]))
        elif k == 'c': sh.draw_bezier(T(it[1]), T(it[2]), T(it[3]), T(it[4]))
        elif k == 're': r = it[1]; q = [T(r.tl), T(r.tr), T(r.br), T(r.bl)]; sh.draw_polyline(q + [q[0]])
        elif k == 'qu': q = it[1]; pts = [T(q.ul), T(q.ur), T(q.lr), T(q.ll)]; sh.draw_polyline(pts + [pts[0]])

def draw_floor(page, floor, labels=True):
    T = transform(floor); D = page.derotation_matrix
    P = lambda x, y: fitz.Point(*T(x, y)) * D
    polys = wall_polys(floor)
    sh = page.new_shape()
    for rings in polys:
        for r in rings: sh.draw_polyline([P(*q) for q in r] + [P(*r[0])])
    sh.finish(color=None, fill=WALL, even_odd=True, width=0); sh.commit()
    TP = lambda p: P(p.x, p.y)
    for dr in R.drawings(floor):
        n = R.lname(dr)
        if not n.startswith('PROPOSED FLOOR PLANS|') or not R.inplan(dr): continue
        suf = n.split('|', 1)[1]
        r = dr['rect']
        for lay, (ex0, ey0, ex1, ey1) in EXTRA[floor]:
            if suf == lay and r.x0 >= ex0 and r.y0 >= ey0 and r.x1 <= ex1 and r.y1 <= ey1:
                sh = page.new_shape(); R.replay(sh, dr, T=TP, color=LINE, width=0.3, dashes=dr.get('dashes')); sh.commit()
        if suf in LINE_LAYERS:
            if dr.get('fill') is not None and dr['type'] in ('f', 'fs'):
                # FOR's fixture masks: white fills built from many internal segments, so fill them and never stroke them
                fc = (1, 1, 1) if sum(dr['fill']) > 2.4 else LINE
                sh = page.new_shape(); fill_only(sh, dr, TP); sh.finish(color=None, fill=fc, width=0, closePath=True); sh.commit()
                continue
            if dr.get('color') is not None and sum(dr['color']) > 2.4: continue      # FOR's white strokes are masks, never linework
            sh = page.new_shape(); R.replay(sh, dr, T=TP, color=LINE, width=LINE_LAYERS[suf], dashes=dr.get('dashes')); sh.commit()
    x0, y0, x1, y1 = OPEN_X[floor]                                 # the open-to-above / below X, corner to corner of the volume
    for a, b in (((x0, y0), (x1, y1)), ((x1, y0), (x0, y1))):
        page.draw_line(P(*a), P(*b), color=LINE, width=0.3, dashes='[4 3] 0')
    if not labels: return {'walls': polys}
    page.insert_font(fontname='cg', fontbuffer=REG_BUF)
    font = fitz.Font(fontbuffer=REG_BUF)
    for txt, x, y, size in LABELS[floor]:
        lines = txt.split('\n'); lh = size * 1.08
        X, Y = T(x, y); y0 = Y - (len(lines) - 1) * lh / 2 + size * 0.36
        wmax = max(font.text_length(ln, fontsize=size) for ln in lines)
        mk = fitz.Rect(X - wmax / 2 - 1.2, y0 - size * 0.78, X + wmax / 2 + 1.2, y0 + (len(lines) - 1) * lh + size * 0.25)
        q = mk * D; q.normalize(); page.draw_rect(q, color=None, fill=(1, 1, 1), width=0)
        for i, ln in enumerate(lines):
            w = font.text_length(ln, fontsize=size)
            page.insert_text(fitz.Point(X - w / 2, y0 + i * lh) * D, ln, fontsize=size, fontname='cg', color=TEXT, rotate=270)
    return {'walls': polys}

def build():
    doc = fitz.open(); geo = {}
    for fl in (1, 2):
        pg = doc.new_page(width=1224, height=1584); pg.set_rotation(270)
        g = draw_floor(pg, fl)
        dx, dy = np.load(f'/home/claude/flrwork/rev1/shift_{fl}.npy')
        geo[fl] = {'walls': g['walls'], 'scale': Wm.Z / ZY, 'shift_px': [float(dx), float(dy)], 'plan_origin': [R.PLAN.x0, R.PLAN.y0]}
    doc.set_metadata({'title': 'Casa Grove base plans from FOR REV 1 (10.23.26)', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); doc.save(OUT_FURN, garbage=3, deflate=True)
    kd = fitz.open()
    for fl in (1, 2):
        pg = kd.new_page(width=1224, height=1584); pg.set_rotation(270); draw_floor(pg, fl, labels=False)
    kd.save(OUT_KEY, garbage=3, deflate=True)
    json.dump(geo, open(GEO, 'w'))
    print('saved', OUT)

if __name__ == '__main__':
    build()
