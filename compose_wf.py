"""Compose the Helios Development wall finish plan sheets (WF-1, WF-2) from the edited wall sheets."""
import pymupdf as fitz

SRC = '/home/claude/flrwork/261101.3350THOMAS.WallFinish-base.pdf'
OUT = '/home/claude/flrwork/261101.HD102.WallFinishPlans.pdf'
W, H = 1584.0, 1224.0            # 22 x 17 in (ANSI C), landscape
FT = 13.5                        # 3/16" = 1'-0"
INK = (0.20, 0.20, 0.20)
MID = (0.45, 0.45, 0.45)
LIGHT = (0.70, 0.70, 0.70)
RULE = 0.5

src = fitz.open(SRC)
REG_BUF = fitz.open('/mnt/user-data/uploads/3807f371-Flooring_Plans.pdf').extract_font(807)[3]
FREG = fitz.Font(fontbuffer=REG_BUF)
out = fitz.open()

# swatch images from the designer's legend (page 1), keyed by code
_imgs = {round((fitz.Rect(i['bbox']) * src[1].rotation_matrix).y0): i['xref'] for i in src[1].get_image_info(xrefs=True)}
IMG = {'PT-01': _imgs[92], 'PT-02': _imgs[173], 'PT-03': _imgs[335], 'WS-01': _imgs[416]}


class Sheet:
    def __init__(self):
        self.p = out.new_page(width=W, height=H)
        self.p.insert_font(fontname='cg', fontbuffer=REG_BUF)

    def text(self, x, y, s, size, color=INK, bold=False, align='l', spacing=0.0):
        missing = [c for c in s if not FREG.has_glyph(ord(c))]
        assert not missing, (s, missing)
        if spacing:
            w = sum(FREG.text_length(c, fontsize=size) for c in s) + spacing * (len(s) - 1)
        else:
            w = FREG.text_length(s, fontsize=size)
        if align == 'c': x -= w / 2
        if align == 'r': x -= w
        kw = dict(render_mode=2, border_width=size * 0.0042) if bold else {}
        if spacing:
            cx = x
            for c in s:
                self.p.insert_text((cx, y), c, fontsize=size, fontname='cg', color=color, **kw)
                cx += FREG.text_length(c, fontsize=size) + spacing
        else:
            self.p.insert_text((x, y), s, fontsize=size, fontname='cg', color=color, **kw)
        return w

    def line(self, a, b, width=RULE, color=INK):
        self.p.draw_line(fitz.Point(a), fitz.Point(b), color=color, width=width)

    def rect(self, r, width=RULE, color=INK, fill=None):
        self.p.draw_rect(fitz.Rect(r), color=color, fill=fill, width=width)

    def swatch(self, r, code):
        r = fitz.Rect(r)
        if code in IMG:
            self.p.insert_image(r, stream=src.extract_image(IMG[code])['image'])
        elif code.startswith('WT'):
            tone = {'WT-01': (0.93, 0.93, 0.92), 'WT-02': (0.91, 0.90, 0.88)}[code]
            self.rect(r, width=0, color=None, fill=tone)
            n = 4
            for k in range(1, n):
                self.line((r.x0 + r.width * k / n, r.y0), (r.x0 + r.width * k / n, r.y1), 0.4, (1, 1, 1))
                self.line((r.x0, r.y0 + r.height * k / n), (r.x1, r.y0 + r.height * k / n), 0.4, (1, 1, 1))
        elif code.startswith('WP'):
            tone = (0.96, 0.95, 0.93) if code == 'WP-01' else (0.90, 0.89, 0.86)
            self.rect(r, width=0, color=None, fill=tone)
            # painted panel: stile and rail outline with a raised field
            self.rect((r.x0 + 6, r.y0 + 6, r.x1 - 6, r.y1 - 6), 0.5, MID)
            self.rect((r.x0 + 10, r.y0 + 10, r.x1 - 10, r.y1 - 10), 0.3, MID)
        elif code == 'CM-01':
            self.rect(r, width=0, color=None, fill=(0.97, 0.97, 0.96))
            # crown profile section: wall at right, ceiling at top
            pts = [(r.x0 + 30, r.y0 + 4), (r.x0 + 12, r.y0 + 4), (r.x0 + 14, r.y0 + 9), (r.x0 + 20, r.y0 + 14),
                   (r.x0 + 22, r.y0 + 20), (r.x0 + 27, r.y0 + 26), (r.x0 + 30, r.y0 + 34)]
            for a, b in zip(pts, pts[1:]):
                self.line(a, b, 0.7, INK)
            self.line((r.x0 + 30, r.y0 + 4), (r.x0 + 30, r.y1 - 4), 0.7, INK)
            self.line((r.x0 + 4, r.y0 + 4), (r.x0 + 30, r.y0 + 4), 0.7, INK)
        self.rect(r, width=0.3, color=LIGHT)


# ------------------------------------------------------------------ layout constants
M = 36.0                       # sheet margin
FR = fitz.Rect(M, M, W - M, H - M)
TB_X = 1330.0                  # title block left edge
LG_X0, LG_X1 = 790.0, 1300.0   # legend column
PLAN_X1 = 740.0
HDR_Y = 70.0                   # header strip bottom


def frame(sh, floor, sheet_no, title_lines):
    p = sh
    p.rect(FR, width=1.2)
    p.line((TB_X, FR.y0), (TB_X, FR.y1), 1.0)
    p.line((PLAN_X1 + 22, HDR_Y), (PLAN_X1 + 22, FR.y1), RULE, LIGHT)
    # header strip
    p.line((FR.x0, HDR_Y), (TB_X, HDR_Y), RULE)
    p.text(FR.x0 + 14, 58, f'WALL FINISH PLAN - FLOOR {floor}', 14, bold=True, spacing=1.2)
    p.text(PLAN_X1, 58, 'SCALE: 3/16" TO 1\'-0"', 10, MID, align='r')
    p.text(LG_X0, 58, 'WALL FINISH SCHEDULE', 11, bold=True, spacing=1.0)

    # ---------------- title block ----------------
    x0, x1 = TB_X, FR.x1
    cx = (x0 + x1) / 2
    y = 92
    p.text(cx, y, 'HELIOS', 30, bold=True, align='c', spacing=5.0)
    p.text(cx, y + 20, 'DEVELOPMENT', 10.5, align='c', spacing=4.2)
    p.line((x0 + 22, y + 36), (x1 - 22, y + 36), 0.6)
    p.text(cx, y + 54, 'DEVELOPER, DESIGNER & GENERAL CONTRACTOR', 6.3, MID, align='c', spacing=0.6)
    p.line((x0, y + 70), (x1, y + 70), RULE)

    def block(top, label, lines, bottom, big=False):
        p.text(x0 + 14, top + 14, label, 6.8, MID, spacing=0.9)
        yy = top + 32
        for i, (t, sz, b) in enumerate(lines):
            p.text(x0 + 14, yy, t, sz, bold=b)
            yy += sz + 4
        p.line((x0, bottom), (x1, bottom), RULE)

    block(162, 'PROJECT', [('CASA GROVE', 14, True), ('3350 THOMAS AVE', 9.5, False), ('COCONUT GROVE, FL 33133', 9.5, False)], 240)
    # key-value rows
    rows = [('PROJECT NO.', 'HD102'), ('DATE', '11.01.26'), ('SCALE', '3/16" TO 1\'-0"'), ('SHEET SIZE', '22" x 17" (ANSI C)'),
            ('DRAWN', 'ZM'), ('CHECKED', 'ZM')]
    yy = 262
    for k, v in rows:
        p.text(x0 + 14, yy, k, 6.8, MID, spacing=0.9)
        p.text(x0 + 100, yy, v, 9.5)
        yy += 19
    p.line((x0, yy - 6), (x1, yy - 6), RULE)
    block(yy - 6, 'ISSUE', [('FOR PRICING & COORDINATION', 9, True), ('NOT FOR PERMIT', 9, False)], yy + 56)
    block(yy + 56, 'BASE PLAN', [('FOR ARCHITECTURE CO.', 9, False), ('ARCHITECTURAL SET, REF. FOR ALL', 7.5, False),
                                 ('DIMENSIONS, DOORS & WINDOWS', 7.5, False)], yy + 124)
    # revisions
    ry = yy + 124
    p.text(x0 + 14, ry + 14, 'REVISIONS', 6.8, MID, spacing=0.9)
    cols = [x0, x0 + 30, x0 + 86, x1]
    hy = ry + 24
    p.line((x0, hy), (x1, hy), RULE)
    for cx_, t in zip(cols, ['NO.', 'DATE', 'DESCRIPTION']):
        p.text(cx_ + 6, hy + 11, t, 6.8, MID)
    p.line((x0, hy + 16), (x1, hy + 16), RULE)
    nrows = 8
    for i in range(nrows + 1):
        p.line((x0, hy + 16 + 17 * i), (x1, hy + 16 + 17 * i), 0.3, LIGHT)
    for c in cols[1:3]:
        p.line((c, hy), (c, hy + 16 + 17 * nrows), 0.3, LIGHT)
    p.text(cols[0] + 6, hy + 28, '0', 7.5)
    p.text(cols[1] + 6, hy + 28, '11.01.26', 7.5)
    p.text(cols[2] + 6, hy + 28, 'ISSUED FOR REVIEW', 7.5)
    rb = hy + 16 + 17 * nrows
    p.line((x0, rb), (x1, rb), RULE)
    # sheet title + number
    st = rb
    p.text(x0 + 14, st + 14, 'SHEET TITLE', 6.8, MID, spacing=0.9)
    p.text(x0 + 14, st + 40, title_lines[0], 13, bold=True)
    p.text(x0 + 14, st + 58, title_lines[1], 13, bold=True)
    p.line((x0, FR.y1 - 96), (x1, FR.y1 - 96), RULE)
    p.text(x0 + 14, FR.y1 - 82, 'SHEET NO.', 6.8, MID, spacing=0.9)
    p.text(cx, FR.y1 - 28, sheet_no, 38, bold=True, align='c', spacing=2.0)
    p.text(cx, FR.y1 - 10, 'HELIOS DEVELOPMENT  .  HD102  .  CASA GROVE', 5.5, LIGHT, align='c')


def legend(sh, rows, notes):
    p = sh
    y = HDR_Y + 20
    sw = 44.0
    for code, title, lines in rows:
        p.swatch((LG_X0, y, LG_X0 + sw, y + sw), code)
        tx = LG_X0 + sw + 12
        w = p.text(tx, y + 11, code, 9.5, bold=True)
        p.text(tx + w + 5, y + 11, title, 8.5)
        yy = y + 24
        for t in lines:
            p.text(tx, yy, t, 7.6, MID)
            yy += 10.5
        y += max(sw + 14, yy - y + 6)
    y += 10
    p.line((LG_X0, y), (LG_X1, y), RULE, LIGHT)
    y += 24
    p.text(LG_X0, y, 'GENERAL NOTES', 11, bold=True, spacing=1.0)
    y += 18
    for i, n in enumerate(notes, 1):
        p.text(LG_X0, y, f'{i}.', 7.6)
        for t in n:
            p.text(LG_X0 + 14, y, t, 7.6)
            y += 10.5
        y += 4
    return y


def scale_bar(sh, x, y):
    p = sh
    segs = [0, 2, 4, 8, 12, 16]
    h = 6
    for a, b in zip(segs, segs[1:]):
        fill = INK if (segs.index(a) % 2 == 0) else (1, 1, 1)
        p.rect((x + a * FT, y, x + b * FT, y + h), width=0.5, color=INK, fill=fill)
    for v in segs:
        p.text(x + v * FT, y + h + 9, str(v), 6.5, align='c')
    p.text(x + segs[-1] * FT + 14, y + h + 0.5, 'FEET', 6.5)
    p.text(x, y - 4, 'GRAPHIC SCALE  3/16" TO 1\'-0"', 6.5, MID)


SHIFT = {1: (2.6, 22.7), 2: (0.0, 0.0)}   # the designer's Floor 1 wall sheet sits offset from her flooring sheet; align to FP-1
def place_plan(sh, pno):
    sp = src[pno]
    dx, dy = SHIFT[pno]
    clip_disp = fitz.Rect(20 + dx, 72 + dy, 715 + dx, 1160 + dy)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    target = fitz.Rect(20 + 20, 72 + 4, 715 + 20, 1160 + 4)
    sh.p.show_pdf_page(target, src, pno, clip=u, rotate=90)
    # show_pdf_page's clip is not honored with rotate: add a hard clip around the form XObject
    xref = sh.p.get_contents()[0]
    st = out.xref_stream(xref).decode('latin1')
    assert 'Do' in st and st.count('Do') == 1, st
    t = target
    clipop = f'{t.x0:.2f} {H - t.y1:.2f} {t.width:.2f} {t.height:.2f} re W n '
    st = st.replace('q ', 'q ' + clipop, 1)
    out.update_stream(xref, st.encode('latin1'))
    return target


def _ranges():
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'elev_index.json')
    out = {1: 'ID-7XX', 2: 'ID-7XX'}
    if os.path.exists(path):
        ix = json.load(open(path))
        for f in (1, 2):
            nos = sorted({v['sheet'] for v in ix if v['floor'] == f})
            if nos: out[f] = f'{nos[0]} TO {nos[-1]}' if len(nos) > 1 else nos[0]
    return out
_RANGE = _ranges()
def _sheets_of(*rooms, wall=None):
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'elev_index.json')
    if not os.path.exists(path): return 'ID-7XX'
    nos = sorted({v['sheet'] for v in json.load(open(path)) if v['room'] in rooms and (wall is None or v['wall'] == wall)})
    return ', '.join(n if i == 0 else n[3:] for i, n in enumerate(nos)) or 'ID-7XX'

NOTES_COMMON = [
    ['ALL WALLS PT-02 EGGSHELL, ALL CEILINGS PT-01 FLAT, ALL CROWN (CM-01) PAINTED PT-02 WITH UPPER', 'MEMBER PT-01, ALL CASING, BASE AND INTERIOR DOORS PT-01 SATIN, UNLESS NOTED OTHERWISE.', 'CLOSETS AND MECHANICAL SPACES PT-02, NO CROWN.'],
    ['PAINT: ONE COAT PRIMER AND TWO FINISH COATS MINIMUM. GRILLES, ACCESS PANELS AND', 'ELECTRICAL COVERS ON PAINTED WALLS TO BE PAINTED TO MATCH THE WALL.'],
    ['HEAVY DASHED LINES SHOW THE RUN OF EACH SPECIAL WALL FINISH IN PLAN. FINISHES RUN', 'FULL HEIGHT, FLOOR TO CEILING, UNLESS NOTED. HEIGHTS, SET-OUTS AND PANEL MODULES PER', 'INTERIOR ELEVATIONS.'],
    ['INTERIOR ELEVATIONS: CIRCLE MARKERS REFER TO HELIOS SHEETS ' + _RANGE[1] + ' (FLOOR 1) AND', _RANGE[2] + ' (FLOOR 2). DIAMOND MARKERS REFER TO YL DESIGNS SET YLD.068 (id 04 TO id 12).'],
    ['WALL TILE AND STONE: MITER OUTSIDE CORNERS, LEVEL SET-OUT FROM FINISHED FLOOR, MOVEMENT', 'JOINTS PER TCNA EJ171, WATERPROOFING AT ALL WET WALLS. SHOP DRAWINGS FOR ALL STONE WALLS.'],
    ['WOOD PANELING: SHOP DRAWINGS FOR APPROVAL. PANEL MODULE CENTERED ON THE WALL UNLESS', 'NOTED. FINISH SAMPLE APPROVED BEFORE FABRICATION.'],
    ['DRAW-DOWNS OF ALL PAINT COLORS AND SAMPLES OF ALL FINISHES TO BE APPROVED BY OWNER', 'BEFORE ORDERING.'],
    ['NO DIMENSIONS ON THIS SHEET. REFER TO THE ARCHITECTURAL SET FOR ALL DIMENSIONS AND', 'CONSTRUCTION AND TO ID-101 AND ID-102 FOR FLOOR FINISHES.'],
]

ROWS_F1 = [
    ('PT-01', 'PAINT - SW 7005 PURE WHITE', ['CEILINGS (FLAT), UPPER CROWN, CASING, BASE & INTERIOR DOORS (SATIN)', 'FOYER WALLS (EGGSHELL), PANELING WP-01 (SATIN)']),
    ('PT-02', 'PAINT - SW 5971 SOLSTICE (OPTION 1)', ['WALLS & CROWN MOLDING THROUGHOUT U.N.O., EGGSHELL', 'OPTION 2: SW 9583 SANCTUARY. OWNER TO CONFIRM FROM DRAW-DOWNS']),
    ('PT-03', 'PAINT - BM 2041-10 HUNTER GREEN', ['POWDER ROOM WALLS, EGGSHELL']),
    ('CM-01', 'CROWN MOLDING', ['PROFILE T.B.C., PAINTED PT-02, UPPER MEMBER PT-01', 'ALL ROOMS OTHER THAN CLOSETS & MECHANICAL']),
    ('WS-01', 'STONE - GREAT ROOM FIREPLACE', ['NATURAL LIGHT MARBLE, HONED, SLAB T.B.C.', 'FULL HEIGHT, ELEVATIONS ' + _sheets_of('GREAT ROOM', wall='E') + ' (YLD id 04)']),
    ('WP-01', 'PAINTED WOOD PANELING - GREAT ROOM', ['FLANKING FIREPLACE, FULL HEIGHT, PAINTED PT-01 SATIN', 'ELEVATIONS ' + _sheets_of('GREAT ROOM', wall='E') + ' (YLD id 04)']),
    ('WT-01', 'WALL TILE - GUEST BATH, BATHS 2 & 3', ['TUB/SHOWER ALCOVES, THREE WALLS TO CEILING', 'FINISH & SIZE T.B.C., GROUT TO MATCH, ELEVATIONS ' + _sheets_of('GUEST BATH', 'BATH 2', 'BATH 3')]),
]
ROWS_F2 = [
    ('PT-01', 'PAINT - SW 7005 PURE WHITE', ['CEILINGS (FLAT), UPPER CROWN, CASING, BASE & INTERIOR DOORS (SATIN)']),
    ('PT-02', 'PAINT - SW 5971 SOLSTICE (OPTION 1)', ['WALLS & CROWN MOLDING THROUGHOUT U.N.O., EGGSHELL', 'OPTION 2: SW 9583 SANCTUARY. OWNER TO CONFIRM FROM DRAW-DOWNS']),
    ('CM-01', 'CROWN MOLDING', ['PROFILE T.B.C., PAINTED PT-02, UPPER MEMBER PT-01', 'ALL ROOMS OTHER THAN CLOSETS & MECHANICAL']),
    ('WP-02', 'PAINTED WOOD PANELING - MASTER SUITE', ['HEADBOARD WALL, CORNER TO CORNER, FULL HEIGHT', 'PAINTED PT-02 SATIN, ELEVATIONS ' + _sheets_of('MASTER SUITE', wall='E2')]),
    ('WT-01', 'WALL TILE - GUEST BATH, BATHS 2 & 3', ['TUB/SHOWER ALCOVES, THREE WALLS TO CEILING', 'FINISH & SIZE T.B.C., GROUT TO MATCH']),
    ('WT-02', 'WALL TILE - MASTER BATH', ['SHOWER, THREE WALLS, AND TUB ALCOVE, THREE WALLS, TO CEILING', 'FINISH & SIZE T.B.C., GROUT TO MATCH, ELEVATIONS ' + _sheets_of('MASTER BATHROOM') + ' (YLD id 11)']),
]


def marker(p, cx, cy, number, sheet, direction, r=7.0):
    g = INK
    p.p.draw_circle(fitz.Point(cx, cy), r, color=g, width=0.6, fill=(1, 1, 1))
    p.line((cx - r, cy), (cx + r, cy), 0.5, g)
    p.text(cx, cy - 1.4, str(number), 5.2, g, align='c')
    p.text(cx, cy + 5.6, sheet.replace('ID-', ''), 4.4, g, align='c')
    dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[direction]
    tip = fitz.Point(cx + dx * (r + 5), cy + dy * (r + 5))
    b1 = fitz.Point(cx + dx * r - dy * 3, cy + dy * r + dx * 3); b2 = fitz.Point(cx + dx * r + dy * 3, cy + dy * r - dx * 3)
    p.p.draw_polyline([b1, tip, b2, b1], color=g, width=0.4, fill=g)


def markers(sh, floor):
    """Helios elevation markers from elev_index.json: at each wall's midpoint, pulled 18 pt into the room, arrow toward the wall."""
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'elev_index.json')
    if not os.path.exists(path): return
    placed = []
    words = [fitz.Rect(w[:4]) for w in sh.p.get_text('words')]
    def clear(cx, cy):
        r = fitz.Rect(cx - 9, cy - 9, cx + 9, cy + 9)
        return not any(r.intersects(wr) for wr in words) and not any(abs(cx - px) < 18 and abs(cy - py) < 18 for px, py in placed)
    for v in json.load(open(path)):
        if v['floor'] != floor: continue
        (ax, ay), (bx, by) = v['a'], v['b']
        mx, my = (ax + bx) / 2 + 20, (ay + by) / 2 + 4          # model -> sheet
        nx, ny = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[v['side']]
        cx, cy = mx - nx * 18, my - ny * 18
        # nudge along the wall if another marker sits within 16 pt
        ux, uy = (bx - ax), (by - ay); L = max(1e-6, (ux * ux + uy * uy) ** 0.5); ux, uy = ux / L, uy / L
        # slide along the wall (both directions, then deeper into the room) until the marker sits clear of text and other markers
        best = (cx, cy)
        found = clear(cx, cy)
        if not found:
            for depth in (18, 30):
                for step in (0, 18, -18, 36, -36, 54, -54, 72, -72):
                    tx, ty = mx - nx * depth + ux * step, my - ny * depth + uy * step
                    if clear(tx, ty): best = (tx, ty); found = True; break
                if found: break
        cx, cy = best
        marker(sh, cx, cy, v['number'], v['sheet'], v['side'])
        placed.append((cx, cy))


def symbols(sh, y):
    """Small symbol key under the general notes."""
    p = sh
    p.text(LG_X0, y, 'SYMBOLS', 11, bold=True, spacing=1.0)
    y += 20
    # stacked wall tag
    bw, bh = 24, 7.4
    for k, c in enumerate(['PT-02', 'CM-01']):
        yy = y + k * (bh + 0.9)
        p.rect((LG_X0, yy, LG_X0 + bw, yy + bh), 0.48, INK)
        p.text(LG_X0 + bw / 2, yy + 5.5, c, 5.87, INK, align='c')
    p.text(LG_X0 + 36, y + 6, 'WALL TAG: WALL PAINT OVER CROWN / TRIM OR PANEL MATERIAL.', 7.6, MID)
    p.text(LG_X0 + 36, y + 16.5, 'FREE-STANDING TAG APPLIES TO EVERY WALL OF THE ROOM.', 7.6, MID)
    y += 30
    p.p.draw_line(fitz.Point(LG_X0, y + 3), fitz.Point(LG_X0 + 24, y + 3), color=INK, width=1.0, dashes='[6 3] 0')
    for x in (LG_X0, LG_X0 + 24):
        p.line((x, y + 1), (x, y + 5), 0.6, INK)
    p.text(LG_X0 + 36, y + 6, 'RUN OF A SPECIAL WALL FINISH, TICKS AT START AND STOP. CONTINUOUS OVER OPENINGS.', 7.6, MID)
    y += 20
    cx, cy = LG_X0 + 12, y + 6
    r = 9
    p.p.draw_polyline([fitz.Point(cx, cy - r), fitz.Point(cx + r, cy), fitz.Point(cx, cy + r), fitz.Point(cx - r, cy), fitz.Point(cx, cy - r)], color=INK, width=0.5)
    p.p.draw_circle(fitz.Point(cx, cy), r * 0.62, color=INK, width=0.4)
    p.text(LG_X0 + 36, y + 6, 'INTERIOR ELEVATION MARKER, YL DESIGNS SET: VIEW NUMBERS AROUND, SHEET BELOW.', 7.6, MID)
    y += 24
    marker(p, LG_X0 + 12, y + 6, '1', 'ID-701', 'N')
    p.text(LG_X0 + 36, y + 6, 'INTERIOR ELEVATION MARKER, HELIOS: VIEW NUMBER OVER SHEET NUMBER, ARROW TOWARD THE WALL.', 7.6, MID)
    y += 24
    p.text(LG_X0, y + 6, 'CODES: PT PAINT, CM CROWN & TRIM, WS WALL STONE, WP WOOD PANELING, WT WALL TILE.', 7.6, MID)
    p.text(LG_X0, y + 16.5, 'FLOOR FINISHES ARE ON ID-101 AND ID-102. WALL CODES NEVER REUSE A FLOOR CODE.', 7.6, MID)
    return y + 20


for floor, pno, rows, sheet_no in [(1, 1, ROWS_F1, 'ID-201'), (2, 2, ROWS_F2, 'ID-202')]:
    sh = Sheet()
    target = place_plan(sh, pno)
    markers(sh, floor)
    frame(sh, floor, sheet_no, ['WALL FINISH PLAN', f'FLOOR {floor}'])
    y = legend(sh, rows, NOTES_COMMON)
    symbols(sh, y + 14)
    scale_bar(sh, FR.x0 + 24, FR.y1 - 22)

out.set_metadata({'title': 'Casa Grove - Wall Finish Plans', 'author': 'Helios Development', 'subject': 'HD102 Wall Finish Plans - Floors 1 and 2',
                  'creator': 'Helios Development', 'producer': 'Helios Development'})
# the embedded Century Gothic subsets map the hyphen glyph to U+00AD (soft hyphen); fix ToUnicode so "WD-01" is searchable
def fix_soft_hyphen(doc):
    done = set()
    for pg in doc:
        for fo in pg.get_fonts(full=True):
            tu = doc.xref_get_key(fo[0], 'ToUnicode')
            if tu[0] != 'xref': continue
            tx = int(tu[1].split()[0])
            if tx in done: continue
            done.add(tx)
            st = doc.xref_stream(tx).decode('latin1')
            st2 = st.replace('<00ad>', '<002d>').replace('<00AD>', '<002D>')
            if st2 != st: doc.update_stream(tx, st2.encode('latin1'))
fix_soft_hyphen(out)
out.save(OUT, garbage=3, deflate=True)
print('saved', OUT)
