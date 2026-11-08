import pymupdf as fitz
G = '/usr/share/texmf/fonts/opentype/public/tex-gyre/'; I = '/usr/share/fonts/opentype/inter/'; B = 'brand/fonts/'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
OPTS = [
 ('A', 'GEOMETRIC, THE CURRENT LOOK', 'TeX Gyre Adventor (Century Gothic / Avant Garde family), complete character set', G+'texgyreadventor-regular.otf', G+'texgyreadventor-bold.otf', None),
 ('B', 'CLASSIC ARCHITECTURAL', 'Helvetica (TeX Gyre Heros), condensed cut for notes', G+'texgyreheros-regular.otf', G+'texgyreheros-bold.otf', G+'texgyreheroscn-regular.otf'),
 ('C', 'MODERN NEUTRAL', 'Inter, drawn for small sizes on screen and paper', I+'Inter-Regular.otf', I+'Inter-SemiBold.otf', None),
 ('D', 'LUXURY GEOMETRIC', 'Jost (Futura family)', B+'jost-400.ttf', B+'jost-600.ttf', None),
 ('E', 'TECHNICAL CONDENSED', 'IBM Plex Sans Condensed, fits the most notes per inch', B+'plexcond-400.ttf', B+'plexcond-600.ttf', None),
 ('F', 'SERIF TITLES, SANS NOTES', 'Serif to match DEVELOPMENT for titles and the sheet number, Inter for everything else', I+'Inter-Regular.otf', SERIF, None),
]
LOGO = fitz.open('brand/HELIOS.Logo.pdf'); LB = fitz.Rect(434.29, 413.25, 867.72, 486.77); CAP = 485.6 - 414.44
FS = fitz.Font(fontfile=SERIF)
INK, MID, LIGHT = (0.15, 0.15, 0.15), (0.35, 0.35, 0.35), (0.55, 0.55, 0.55)
NOTE = ['SHOWER, LOOKING EAST. WT-02 PORCELAIN SLAB 48" x 96" FLOOR TO CEILING, SEAMS AS DRAWN. FRAMELESS 1/2" TEMPERED',
        'GLASS, 28" DOOR ON WALL-MOUNT HINGES AT THE PIER, 7" FIXED PANEL. VALVE AND SLIDE BAR 1\'-3" FROM THE GLASS,',
        'MAX. 4" BOX DEPTH. EXHAUST FAN ON THE WC SWITCH. VERIFY ALL HEIGHTS WITH FOR (CEILING 10\'-0", HEADS 8\'-0").']
doc = fitz.open(); pg = doc.new_page(width=1584, height=1224)
pg.draw_rect(fitz.Rect(36, 36, 1548, 1188), color=INK, width=1.2)
fonts = {}
def F(path):
    if path not in fonts: fonts[path] = (fitz.Font(fontfile=path), 'f%d' % len(fonts)); pg.insert_font(fontname=fonts[path][1], fontfile=path)
    return fonts[path]
def T(x, y, s, path, size, color=INK, align='l', spacing=0.0):
    f, n = F(path); w = sum(f.text_length(c, fontsize=size) for c in s) + spacing * (len(s) - 1)
    if align == 'c': x -= w / 2
    if align == 'r': x -= w
    if spacing:
        for c in s: pg.insert_text((x, y), c, fontsize=size, fontname=n, color=color); x += f.text_length(c, fontsize=size) + spacing
    else: pg.insert_text((x, y), s, fontsize=size, fontname=n, color=color)
    return w
T(60, 70, 'DRAWING FONT OPTIONS', I+'Inter-SemiBold.otf', 14, spacing=1.2)
T(1524, 70, 'PRINT AT 100% ON 22 x 17 TO JUDGE THE SMALL TEXT. SIZES AS USED ON THE SHEETS.', I+'Inter-Regular.otf', 8, MID, align='r')
pw, ph = 488, 540
for i, (key, name, desc, reg, bold, cond) in enumerate(OPTS):
    x0 = 60 + (i % 3) * (pw + 12); y0 = 92 + (i // 3) * (ph + 10)
    pg.draw_rect(fitz.Rect(x0, y0, x0 + pw, y0 + ph), color=LIGHT, width=0.5)
    title_font = bold
    T(x0 + 14, y0 + 26, '%s  %s' % (key, name), I+'Inter-SemiBold.otf', 11, spacing=0.6)
    T(x0 + 14, y0 + 40, desc, I+'Inter-Regular.otf', 6.5, MID)
    # lockup
    k = 110 / LB.width; cx = x0 + pw - 80; r = fitz.Rect(cx - 55, y0 + 14, cx + 55, y0 + 14 + LB.height * k)
    pg.show_pdf_page(r, LOGO, 0, clip=LB)
    cap = 0.4 * CAP * k; sz = cap / 0.662; s = 'DEVELOPMENT'; w0 = sum(FS.text_length(c, fontsize=sz) for c in s)
    T(cx - 55, r.y1 + 6 + cap, s, SERIF, sz, (0, 0, 0), spacing=(110 - w0) / 10)
    pg.draw_line((x0 + 14, y0 + 62), (x0 + pw - 14, y0 + 62), color=LIGHT, width=0.4)
    # sheet header
    T(x0 + 14, y0 + 88, 'MASTER BATH ELEVATIONS', title_font, 13, spacing=1.2)
    T(x0 + pw - 14, y0 + 88, 'SCALE: 1/2" TO 1\'-0"', reg, 10, MID, align='r')
    # view title bar
    y = y0 + 118; pg.draw_line((x0 + 14, y + 4), (x0 + pw - 14, y + 4), color=INK, width=0.4)
    T(x0 + 14, y, '3 - SHOWER, EAST WALL', title_font if key == 'F' else bold, 7.5)
    T(x0 + pw - 14, y, 'SCALE: 1/2" TO 1\'-0"', reg, 7.0, MID, align='r')
    # note
    nf = cond or reg
    for j, ln in enumerate(NOTE): T(x0 + 14, y + 18 + j * 7.4, ln, nf, 5.5 if not cond else 5.9, MID)
    # dimension string
    yd = y0 + 190; xs = [x0 + 30, x0 + 30 + 4.625 * 9, x0 + 30 + 36.625 * 9, x0 + 30 + 46 * 9]
    pg.draw_line((xs[0], yd), (xs[-1], yd), color=INK, width=0.4)
    for xx in xs: pg.draw_line((xx - 1.8, yd + 1.8), (xx + 1.8, yd - 1.8), color=INK, width=0.6); pg.draw_line((xx, yd - 3), (xx, yd + 3), color=INK, width=0.4)
    for (a, b), lab in zip(zip(xs, xs[1:]), ('4-5/8"', '2\'-8"', '9-3/8"')): T((a + b) / 2, yd - 2.5 if lab != '4-5/8"' else yd - 7.5, lab, reg, 5.5 if lab != '4-5/8"' else 5.0, align='c')
    pg.draw_line((xs[0], yd + 13), (xs[-1], yd + 13), color=INK, width=0.4)
    T((xs[0] + xs[-1]) / 2, yd + 10.5, '3\'-10"', reg, 5.5, align='c')
    # tags
    tx = x0 + 30
    for t in ('WT-02', 'PT-02', 'CM-01', 'GFCI', 'TB 24"', 'ID-731'):
        f, n = F(reg); w = f.text_length(t, fontsize=5.5) + 6
        pg.draw_rect(fitz.Rect(tx, yd + 26, tx + w, yd + 35), color=INK, width=0.4); T(tx + 3, yd + 33, t, reg, 5.5); tx += w + 8
    # title block sample
    tb = fitz.Rect(x0 + 14, y0 + 250, x0 + 232, y0 + ph - 14); pg.draw_rect(tb, color=INK, width=0.6)
    yy = tb.y0 + 16
    T(tb.x0 + 12, yy, 'PROJECT', reg, 6.8, MID, spacing=0.9); T(tb.x0 + 12, yy + 18, 'CASA GROVE', bold, 12)
    T(tb.x0 + 12, yy + 32, '3350 THOMAS AVE', reg, 8.5); T(tb.x0 + 12, yy + 44, 'COCONUT GROVE, FL 33133', reg, 8.5)
    for j, (kk, vv) in enumerate((('PROJECT NO.', 'HD102'), ('DATE', '11.07.26'), ('SCALE', 'AS NOTED'), ('DRAWN', 'ZM'))):
        T(tb.x0 + 12, yy + 70 + j * 16, kk, reg, 6.0, MID, spacing=0.6); T(tb.x0 + 100, yy + 70 + j * 16, vv, reg, 8.5)
    T(tb.x0 + 12, yy + 150, 'SHEET TITLE', reg, 6.8, MID, spacing=0.9)
    T(tb.x0 + 12, yy + 168, 'MASTER BATH', title_font, 11); T(tb.x0 + 12, yy + 182, 'ELEVATIONS', title_font, 11)
    T(tb.x0 + 12, yy + 205, 'SHEET NO.', reg, 6.8, MID, spacing=0.9)
    T((tb.x0 + tb.x1) / 2, tb.y1 - 22, 'ID-730', title_font, 30, align='c')
    # plan text sample
    px = x0 + 248
    T(px, y0 + 270, 'ON THE PLANS', reg, 6.8, MID, spacing=0.9)
    T(px, y0 + 292, 'MASTER BATH', reg, 7.5); T(px, y0 + 304, '13\'-6" x 11\'-8-5/8"', reg, 6.0, MID)
    T(px, y0 + 326, 'DN', reg, 6.0); T(px + 30, y0 + 326, 'HR', reg, 6.0); T(px + 60, y0 + 326, 'W.I.C.', reg, 6.0)
    T(px, y0 + 352, 'ALPHABET AT 5.5 PT', reg, 6.8, MID, spacing=0.9)
    T(px, y0 + 366, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', reg, 5.5); T(px, y0 + 375, '0123456789  1/2"  3\'-4"  &  ( ) , . : / %', reg, 5.5)
    T(px, y0 + 400, 'ALPHABET AT 8 PT', reg, 6.8, MID, spacing=0.9)
    T(px, y0 + 414, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', reg, 8); T(px, y0 + 426, '0123456789  1/2"  3\'-4"', reg, 8)
    if cond: T(px, y0 + 450, 'NOTES IN THE CONDENSED CUT', cond, 6.8, MID, spacing=0.6)
doc.save('brand/261107.HD102.FontOptions.pdf')
doc[0].get_pixmap(dpi=110).save('brand/261107.HD102.FontOptions.png')
fitz.open('brand/261107.HD102.FontOptions.pdf')[0].get_pixmap(dpi=300, clip=fitz.Rect(60, 92, 1048, 640)).save('/tmp/fo_top.png')
