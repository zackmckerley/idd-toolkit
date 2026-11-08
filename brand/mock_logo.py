import pymupdf as fitz, idd_sheet as S
LOGO = fitz.open('brand/HELIOS.Logo.pdf'); LB = fitz.Rect(434.29, 413.25, 867.72, 486.77)   # logo ink bounds
CAP = 485.6 - 414.44                                                                          # H cap height in logo units
SANS = S.FREG; SERIF = fitz.Font(fontfile='/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')

def lockup(page, font, fname, ffile, W=150.0, top=58.0, track=None):
    x0, x1 = S.TB_X, S.FR.x1; cx = (x0 + x1) / 2; k = W / LB.width
    page.draw_rect(fitz.Rect(x0 + 1, S.FR.y0 + 1, x1 - 1, 126.5), color=None, fill=(1, 1, 1), overlay=True)
    r = fitz.Rect(cx - W / 2, top, cx + W / 2, top + LB.height * k)
    page.show_pdf_page(r, LOGO, 0, clip=LB)
    cap = 0.4 * CAP * k                                   # 60% smaller: cap height 40% of the logo's
    size = cap / (font.ascender * 0.0 + 0.0 + (0.66 if font is SANS else 0.662))
    s = 'DEVELOPMENT'; n = len(s)
    w0 = sum(font.text_length(c, fontsize=size) for c in s)
    sp = (W - w0) / (n - 1) if track is None else track    # tracked to the logo's width
    base = r.y1 + 9.0 + cap
    page.insert_font(fontname=fname, fontbuffer=font.buffer)
    x = cx - (w0 + sp * (n - 1)) / 2
    for c in s:
        page.insert_text((x, base), c, fontsize=size, fontname=fname, color=(0, 0, 0)); x += font.text_length(c, fontsize=size) + sp
    return size, sp

src = fitz.open('261106.HD102.PrintSet.pdf'); i = 5   # ID-730
clip = fitz.Rect(S.TB_X - 6, S.FR.y0 - 6, S.FR.x1 + 6, 240)
out = []
for tag, font, fn in (('CURRENT', None, None), ('A', SANS, 'cgx'), ('B', SERIF, 'lsx')):
    d = fitz.open(); d.insert_pdf(src, from_page=i, to_page=i); p = d[0]
    if font: print(tag, lockup(p, font, fn, None))
    out.append(p.get_pixmap(dpi=300, clip=clip))
# side by side with labels
W = sum(o.width for o in out) + 80 * 2; H = out[0].height + 90
doc = fitz.open(); pg = doc.new_page(width=W * 72 / 300, height=H * 72 / 300)
x = 0
for o, t in zip(out, ('CURRENT', 'A  SHEET FONT', 'B  SERIF TO MATCH THE LOGO')):
    rr = fitz.Rect(x, 20, x + o.width * 72 / 300, 20 + o.height * 72 / 300); pg.insert_image(rr, pixmap=o)
    pg.insert_text((x + 4, 14), t, fontsize=9); x = rr.x1 + 80 * 72 / 300
doc[0].get_pixmap(dpi=300).save('brand/261107.HD102.LogoMockup.png')
