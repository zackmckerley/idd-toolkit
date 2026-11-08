"""Compose the Helios Development flooring plan sheets from the edited plan pages."""
import pymupdf as fitz

SRC = '/home/claude/flrwork/261101.3350THOMAS.FlooringPlans-Rev1.pdf'
OUT = '/home/claude/flrwork/261101.HD102.FlooringPlans.pdf'
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
IMG = {'TL-01': _imgs[92], 'ST-01': _imgs[173], 'ST-02': _imgs[254], 'SL-01': _imgs[335], 'WD-01': _imgs[416], 'WD-02': _imgs[497]}


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
        else:
            tone = {'TL-02': (0.92, 0.92, 0.91), 'TL-03': (0.90, 0.89, 0.87), 'TL-04': (0.80, 0.78, 0.75)}[code]
            self.rect(r, width=0, color=None, fill=tone)
            n = 4
            for k in range(1, n):
                self.line((r.x0 + r.width * k / n, r.y0), (r.x0 + r.width * k / n, r.y1), 0.4, (1, 1, 1))
                self.line((r.x0, r.y0 + r.height * k / n), (r.x1, r.y0 + r.height * k / n), 0.4, (1, 1, 1))
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
    p.text(FR.x0 + 14, 58, f'FLOORING PLAN - FLOOR {floor}', 14, bold=True, spacing=1.2)
    p.text(PLAN_X1, 58, 'SCALE: 3/16" TO 1\'-0"', 10, MID, align='r')
    p.text(LG_X0, 58, 'FLOOR FINISH SCHEDULE', 11, bold=True, spacing=1.0)

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


def place_plan(sh, pno):
    sp = src[pno]
    clip_disp = fitz.Rect(20, 72, 715, 1160)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    target = fitz.Rect(clip_disp.x0 + 20, clip_disp.y0 + 4, clip_disp.x1 + 20, clip_disp.y1 + 4)
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


NOTES_COMMON = [
    ['ALL FLOOR FINISHES TO FINISH FLUSH WITH EACH OTHER. BUILD UP SUBFLOOR OR USE LEVELING', 'UNDERLAYMENT AT TILE AREAS AS REQUIRED. NO RAISED THRESHOLDS.'],
    ['TRANSITIONS CENTERED UNDER DOORS IN THE CLOSED POSITION. FLUSH METAL TRANSITION PROFILE', 'AT ALL WOOD-TO-TILE JOINTS, FINISH TO MATCH SL-01 ON FLOOR 1 AND ADJACENT WOOD ON FLOOR 2.'],
    ['WOOD FLOORING: GLUE-DOWN INSTALLATION WITH MOISTURE MITIGATION PER MANUFACTURER.', 'ACCLIMATE ON SITE 7 DAYS MIN. RUN FIELD BOARDS IN THE DIRECTION SHOWN.'],
    ['WD-02 BORDER: SINGLE BOARD, MITERED CORNERS, RUNS CONTINUOUS ACROSS DOOR OPENINGS.', 'FIELD BOARDS STOP AT BORDER.'],
    ['TILE: DCOF 0.42 MIN. (ANSI A326.3) AT ALL WET AREAS. MOSAIC OR 2x2 AT SHOWER FLOORS.', 'RECTIFIED EDGES, 1/16" JOINTS, GROUT TO MATCH TILE.'],
    ['SUBMIT SAMPLES AND LAYOUT SHOP DRAWINGS FOR ALL BORDERS AND PATTERNED AREAS FOR', 'OWNER APPROVAL BEFORE INSTALLATION.'],
    ['VERIFY ALL DIMENSIONS IN FIELD. ROOM DIMENSIONS SHOWN ARE NOMINAL. REFER TO', 'ARCHITECTURAL SET FOR ALL CONSTRUCTION.'],
]

ROWS_F1 = [
    ('WD-01', 'WOOD FLOORS - FIELD', ['FINISH & SIZE T.B.C.', 'ALSO STAIR TREADS & RISERS, TO MATCH FIELD']),
    ('WD-02', 'WOOD FLOORS - BORDER', ['SINGLE 6" BOARD, FINISH TO MATCH WD-01', 'MITERED CORNERS, CONTINUOUS ACROSS DOORS']),
    ('SL-01', 'SCHLUTER BORDER STRIP', ['SOLID BRASS, FLUSH WITH WOOD', 'FLOOR 1 ONLY']),
    ('TL-01', 'PORCELAIN TILE - FOYER & PANTRY', ['DARK/MEDIUM GRAY & WHITE', 'CHECKERED PATTERN, SET ON THE DIAGONAL']),
    ('TL-02', 'PORCELAIN TILE - GUEST BATH, BATHS 2 & 3', ['FINISH & SIZE T.B.C.', 'DCOF 0.42 MIN., MOSAIC AT SHOWER FLOORS']),
    ('TL-04', 'PORCELAIN TILE - LAUNDRY, SERVICE AREA,', ['PET AREA, AHU & STORAGE CLOSETS', 'WARM GRAY, 24x24 MATTE, DCOF 0.42 MIN.']),
    ('ST-02', 'MARBLE - POWDER ROOM', ['EMERALD GREEN MARBLE (OPTION)', 'HONED FINISH, T.B.C.']),
    ('ST-01', 'MARBLE - STAIR LANDING AT FLOOR 1', ['HONED FINISH, T.B.C.']),
]
ROWS_F2 = [
    ('WD-01', 'WOOD FLOORS - FIELD', ['FINISH & SIZE T.B.C.', 'HERRINGBONE IN MASTER SUITE ONLY, CENTERED ON ROOM', 'STAIR TREADS & RISERS TO MATCH FIELD']),
    ('WD-02', 'WOOD FLOORS - BORDER', ['SINGLE BOARD, FINISH TO MATCH WD-01', '6" AT MASTER SUITE, 4-1/2" AT HALL & LANDING', 'NO SCHLUTER STRIP ON FLOOR 2']),
    ('TL-02', 'PORCELAIN TILE - GUEST BATH, BATHS 2 & 3', ['FINISH & SIZE T.B.C.', 'DCOF 0.42 MIN., MOSAIC AT SHOWER FLOORS']),
    ('TL-03', 'PORCELAIN TILE - MASTER BATH', ['FINISH & SIZE T.B.C.', 'DCOF 0.42 MIN., MOSAIC AT SHOWER FLOOR']),
    ('ST-01', 'MARBLE - STAIR LANDING AT FLOOR 2', ['HONED FINISH, T.B.C.']),
]

for floor, pno, rows, sheet_no in [(1, 1, ROWS_F1, 'ID-101'), (2, 2, ROWS_F2, 'ID-102')]:
    sh = Sheet()
    target = place_plan(sh, pno)
    frame(sh, floor, sheet_no, ['FLOORING PLAN', f'FLOOR {floor}'])
    legend(sh, rows, NOTES_COMMON)
    scale_bar(sh, FR.x0 + 24, FR.y1 - 22)

out.set_metadata({'title': 'Casa Grove - Flooring Plans', 'author': 'Helios Development', 'subject': 'HD102 Flooring Plans - Floors 1 and 2',
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
