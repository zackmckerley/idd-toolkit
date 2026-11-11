"""Helios Development sheet, proportioned 17 x 11 so it prints edge to edge on 11 x 17 (26.28 x 17 at full size, printed at 64.7%): border, header strip, title block, revision table, sheet number.
Reused by every sheet type so the set is one hand. Fonts: the Century Gothic subset embedded in the designer's plot."""
import pymupdf as fitz
from idd_std import LW, TXT, INK, MID, LIGHT, PROJECT

W, H = 1892.0, 1224.0          # 17:11, the 11 x 17 page (owner 11.07.26: the drawings span the whole printed page)
M = 36.0
FR = fitz.Rect(M, M, W - M, H - M)
TB_X = W - 254.0       # title block left edge (218 pt wide, as before)
HDR_Y = 52.0           # no header strip (owner 11.07.26: the title is in the title block only); content starts at HDR_Y + 8, 24 pt below the frame
RULE = 0.5
EXTRA_REVS = []
PRINT_DATE = '11.09.26'          # owner comments 11.09.26 reissue (review draft was 11.07.26)
REVS = [('0', '11.07.26', 'REVIEW DRAFT'), ('1', '11.09.26', 'OWNER COMMENTS'), ('2', '11.09.26', 'COORDINATED WITH FOR REV 1')]          # the review draft printed on 11 x 17                 # e.g. [('1', '11.05.26', 'BASE PLAN TO FOR REV 1')], set by a reissue driver
# Fonts (owner pick 11.07.26, option F): Inter for all drawing text, a serif for titles and sheet numbers to match the HELIOS lockup.
INTER_R = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'      # Medium, not Regular: the 11 x 17 print read too light (owner 11.07.26)
INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
REG_BUF = open(INTER_R, 'rb').read(); BOLD_BUF = open(INTER_B, 'rb').read(); SERIF_BUF = open(SERIF, 'rb').read()
_FR, _FB, _FS = fitz.Font(fontbuffer=REG_BUF), fitz.Font(fontbuffer=BOLD_BUF), fitz.Font(fontbuffer=SERIF_BUF)
LOGO_PDF = '/home/claude/flrwork/brand/HELIOS.Logo.pdf'
LOGO_BOUNDS = fitz.Rect(434.29, 413.25, 867.72, 486.77); LOGO_CAP = 485.6 - 414.44

NOTE_INK = (0.0, 0.0, 0.0)       # notes print black (owner 11.07.26: no grey)

def ps(size):
    """Print size: the set is read on 11 x 17 (64.7% of the full-size sheet), so small text grows 30%, capped at 9 pt,
    and nothing prints under 4.5 pt (7 pt full size; review 11.07.26)."""
    return max(size, min(max(size * 1.3, 7.0), 9.0))

# Sheet numbers (owner 11.07.26 evening): plans in the 100s, floor 1 rooms in the 200s, floor 2 rooms in the 300s.
# Each room has a block of ten; the x0 sheet is its key plan; gaps are left so adding a sheet never renumbers another.
# The generators still name sheets by their old 7xx numbers: every printed reference goes through remap().
SHEET_MAP = {'771': '210', '772': '211', '773': '212',                                   # entry and powder room
             '751': '230', '752': '231', '753': '232', '754': '233', '755': '234', '756': '235',   # living room (235: the stair opened, 11.10.26)
             '741': '240', '742': '241', '743': '242', '744': '243', '745': '244',       # kitchen, dining and pantry
             '761': '250', '762': '251', '763': '252', '764': '253',                     # mudroom, laundry and dog room
             '738A': '261', '740': '262',                                                # guest bedroom and guest bath (key plan ID-260)
             '734': '310', '735': '311', '736': '312', '737': '313',                     # master bedroom
             '730': '320', '731': '321', '732': '322', '733': '323',                     # master bath
             '738B': '341', '739': '342',                                                # bedroom 2 and bath 2 (key plan ID-340)
             '738C': '351', '739A': '352'}                                               # bedroom 3 and bath 3 (key plan ID-350)
PLAN_MAP = {'201': '111', '202': '112'}                                                   # wall finish plans join the plans in the 100s
import re as _re
_RX_ID = _re.compile(r'(?<![0-9A-Z\'.-])(7[3-7]\d[A-C]?)(?![0-9A-Z"\'])')
def remap(s):
    """Every reference to an elevation sheet, written ID-7xx or bare in a marker, follows the new numbering."""
    if s in SHEET_MAP: return SHEET_MAP[s]
    s = _re.sub(r'ID-(7[3-7]\d[A-C]?)(?![0-9A-Z])', lambda m: 'ID-' + SHEET_MAP.get(m.group(1), m.group(1)), s)
    s = _re.sub(r'ID-(20[12])(?![0-9A-Z])', lambda m: 'ID-' + PLAN_MAP[m.group(1)], s)
    return _RX_ID.sub(lambda m: SHEET_MAP.get(m.group(1), m.group(1)), s)

# Scales print in the title block only (owner 11.07.26). Any scale written on the sheet (a view title bar, a key plan caption,
# a scale bar label) is taken out of the text where it is drawn and recorded for the title block, which lists it when the doc is finished.
_SC_RX = _re.compile(r'(\d+(?:-\d+/\d+|/\d+)?)"\s*(?:TO|=)\s*1\'-0"')
SCALES_SEEN = {}          # (id(doc), page number) -> [(context, scale)]
TB_SCALE_AT = {}          # (id(doc), page number) -> (x, y, x1, frame label)
def _key(page): return (id(page.parent), page.number)
def take_scale(page, s, ctx):
    """Remove scale callouts from s, record them for the page's title block. Returns what is left to print ('' if nothing)."""
    found = _SC_RX.findall(s)
    if not found: return s
    c = 'PLAN' if 'PLAN' in s else ctx
    for f_ in found: SCALES_SEEN.setdefault(_key(page), []).append((c, f_ + '" TO 1\'-0"'))
    t = _SC_RX.sub('', s)
    t = _re.sub(r'SCALE IN FEET|SCALE:?', '', t)
    t = _re.sub(r'\(\s*\)', '', t)
    t = _re.sub(r'\s{2,}', ' ', t).strip(' ,:-')
    return t if _re.search(r'[A-Z0-9]', t) else ''

def _ranges(ns):
    """1, 2, 3, 5 -> 1-3, 5 (numbers as printed; letters kept as they are)."""
    try: v = sorted(set(int(x) for x in ns))
    except ValueError: return ', '.join(dict.fromkeys(ns))
    out = []; a = b = v[0]
    for x in v[1:]:
        if x == b + 1: b = x
        else: out.append(str(a) if a == b else '%d-%d' % (a, b)); a = b = x
    out.append(str(a) if a == b else '%d-%d' % (a, b))
    return ', '.join(out)

def finish_scales(doc):
    """Write each page's scales into its title block: one line when the sheet has one scale, else plan and view groups."""
    for pg in doc:
        k = _key(pg)
        if k not in TB_SCALE_AT: continue
        x, y, x1, flab = TB_SCALE_AT.pop(k)
        seen = SCALES_SEEN.pop(k, [])
        m = _SC_RX.search(flab or '')
        if m and not any(c == 'PLAN' for c, _ in seen) and 'PLAN' in (flab or ''): seen.append(('PLAN', m.group(1) + '" TO 1\'-0"'))
        if not seen and m: seen.append(('SHEET', m.group(1) + '" TO 1\'-0"'))
        if any(c.startswith('VIEW') for c, _ in seen): seen = [('PLAN' if c == 'SHEET' else c, sc) for c, sc in seen]   # a scale bar beside views is the key plan's
        uniq = list(dict.fromkeys(sc for _, sc in seen))
        if not uniq: lines = [flab if flab else 'NOT TO SCALE']
        elif len(uniq) == 1: lines = [uniq[0]]
        else:
            lines = []
            plans = list(dict.fromkeys(sc for c, sc in seen if c == 'PLAN'))
            for sc in plans: lines.append('PLAN ' + sc)
            views = {}
            for c, sc in seen:
                if c.startswith('VIEW'): views.setdefault(sc, []).append(c[5:])
            for sc, ns in views.items(): lines.append(('VIEWS ' if len(set(ns)) > 1 else 'VIEW ') + _ranges(ns) + ': ' + sc)
            other = [sc for c, sc in seen if c == 'SHEET' and sc not in plans and sc not in views]
            for sc in dict.fromkeys(other): lines.append(sc)
        if 'srf' not in [f[4] for f in pg.get_fonts()]: pass
        if 'cg' not in [f[4] for f in pg.get_fonts()]: pg.insert_font(fontname='cg', fontbuffer=REG_BUF)
        sz = 10.0 if len(lines) == 1 else 8.5
        for i, t in enumerate(lines[:4]):
            z = sz
            while _FR.text_length(t, fontsize=z) > x1 - x - 10 and z > 6.5: z -= 0.25
            pg.insert_text((x, y + i * (z + 3.5)), t, fontsize=z, fontname='cg', color=INK)

class _PrintFont:
    """Width calculations everywhere in the generators go through this, so they match the size actually printed."""
    def __init__(self, f): self.f = f
    def text_length(self, s, fontsize=11): return self.f.text_length(remap(s), fontsize=ps(fontsize))
    def has_glyph(self, c): return self.f.has_glyph(c)
    def __getattr__(self, k): return getattr(self.f, k)
FREG = _PrintFont(_FR)


class Sheet:
    def __init__(self, doc):
        self.p = doc.new_page(width=W, height=H)
        self.p.insert_font(fontname='cg', fontbuffer=REG_BUF); self.p.insert_font(fontname='cgb', fontbuffer=BOLD_BUF)
        self.p.insert_font(fontname='srf', fontbuffer=SERIF_BUF)
        self.font, self.fontname = FREG, 'cg'

    # ---- primitives
    def _glyph_x(self, x, y, size, color, bold):
        """The embedded subset has no 'X': draw one as two strokes the width of a 'K'."""
        w = FREG.text_length('K', fontsize=size); h = size * 0.72
        lw = size * (0.09 if bold else 0.07)
        self.p.draw_line(fitz.Point(x + w * 0.08, y), fitz.Point(x + w * 0.92, y - h), color=color, width=lw)
        self.p.draw_line(fitz.Point(x + w * 0.08, y - h), fitz.Point(x + w * 0.92, y), color=color, width=lw)
        return w
    def text(self, x, y, s, size, color=INK, bold=False, align='l', spacing=0.0, serif=False, raw=False):
        s = take_scale(self.p, remap(s), 'SHEET')
        if not s: return 0.0
        if not raw: size = ps(size)
        if color == MID: color = NOTE_INK
        f, fn = (_FS, 'srf') if serif else ((_FB, 'cgb') if bold else (_FR, 'cg'))
        missing = [c for c in s if not f.has_glyph(ord(c))]
        assert not missing, (s, missing)
        w = (sum(f.text_length(c, fontsize=size) for c in s) + spacing * (len(s) - 1)) if spacing else f.text_length(s, fontsize=size)
        if align == 'c': x -= w / 2
        if align == 'r': x -= w
        if spacing:
            cx = x
            for c in s:
                self.p.insert_text((cx, y), c, fontsize=size, fontname=fn, color=color)
                cx += f.text_length(c, fontsize=size) + spacing
        else:
            self.p.insert_text((x, y), s, fontsize=size, fontname=fn, color=color)
        return w

    def line(self, a, b, width=RULE, color=INK, dashes=None):
        self.p.draw_line(fitz.Point(a), fitz.Point(b), color=color, width=width, dashes=dashes)

    def rect(self, r, width=RULE, color=INK, fill=None, dashes=None):
        self.p.draw_rect(fitz.Rect(r), color=color, fill=fill, width=width, dashes=dashes)

    def polyline(self, pts, width=RULE, color=INK, dashes=None, close=True):
        sh = self.p.new_shape(); sh.draw_polyline([fitz.Point(q) for q in pts]); sh.finish(color=color, width=width, dashes=dashes, closePath=close); sh.commit()

    # ---- the frame: border, header, title block
    def frame(self, header, scale_label, title_lines, sheet_no, revisions=(('0', PROJECT['date'], 'ISSUED FOR REVIEW'),), legend_rule=True, legend_header=None, plan_x1=740.0):
        p = self
        revisions = tuple(revisions)                                # a reissue appends its row, numbered after the sheet's last one
        for i, (_, d_, t_) in enumerate(EXTRA_REVS):
            revisions += ((str(int(revisions[-1][0]) + 1) if revisions else str(i), d_, t_),)
        p.rect(FR, width=LW['border'])
        p.line((TB_X, FR.y0), (TB_X, FR.y1), 1.0)
        if legend_rule:
            p.line((plan_x1 + 22, HDR_Y), (plan_x1 + 22, FR.y1), RULE, LIGHT)
        # no header strip: the sheet title lives in the title block only (owner 11.07.26)
        # the scale is not in the header (owner 11.07.26: it sat squeezed against the title): it lives in the title block, the view title bars and the scale bars
        if legend_header:
            p.text(790.0, 59, legend_header, 10, bold=True, spacing=0.8, raw=True)
        x0, x1 = TB_X, FR.x1
        cx = (x0 + x1) / 2
        # HELIOS lockup (owner 11.07.26): the logo, DEVELOPMENT under it in the serif, cap height 40% of the logo's, centered in the top block
        top_b, bot_b = FR.y0, 162.0; lw = 156.0; k = lw / LOGO_BOUNDS.width
        cap = 0.4 * LOGO_CAP * k; gap = 8.0; hl = LOGO_BOUNDS.height * k; tot = hl + gap + cap
        ly = (top_b + bot_b) / 2 - tot / 2
        p.p.show_pdf_page(fitz.Rect(cx - lw / 2, ly, cx + lw / 2, ly + hl), fitz.open(LOGO_PDF), 0, clip=LOGO_BOUNDS)
        dsz = cap / 0.662; dw = sum(_FS.text_length(c, fontsize=dsz) for c in 'DEVELOPMENT')
        p.text(cx - lw / 2, ly + hl + gap + cap, 'DEVELOPMENT', dsz, (0, 0, 0), serif=True, spacing=(lw - dw) / 10, raw=True)
        p.line((x0, bot_b), (x1, bot_b), RULE)

        def lab(y, t): p.text(x0 + 14, y, t, 7.0, MID, spacing=0.9, raw=True)
        lab(184, 'PROJECT')
        p.text(x0 + 14, 210, PROJECT['name'], 18, serif=True, spacing=0.6, raw=True)
        p.text(x0 + 14, 228, PROJECT['address1'], 10, raw=True); p.text(x0 + 14, 242, PROJECT['address2'], 10, raw=True)
        p.line((x0, 256), (x1, 256), RULE)
        yy = 276
        for k_, v_ in (('PROJECT NO.', PROJECT['no']), ('DATE', PRINT_DATE)):
            lab(yy, k_); p.text(x0 + 96, yy + 0.5, v_, 10, raw=True); yy += 20
        p.line((x0, yy - 6), (x1, yy - 6), RULE)
        lab(yy + 14, 'SCALE')                                      # filled in when the doc is finished, from every scale drawn on the sheet
        TB_SCALE_AT[_key(self.p)] = (x0 + 14, yy + 31, x1, remap(scale_label or '').replace(' = ', ' TO '))
        yy += 74; p.line((x0, yy - 6), (x1, yy - 6), RULE)
        lab(yy + 14, 'ISSUE')
        p.text(x0 + 14, yy + 32, 'REVIEW DRAFT', 10.5, bold=True, raw=True)
        p.text(x0 + 14, yy + 46, 'NOT FOR CONSTRUCTION', 10, raw=True)
        p.text(x0 + 14, yy + 60, '11 x 17 PRINT IS 65% OF FULL SIZE:', 8.0, MID, raw=True)
        p.text(x0 + 14, yy + 72, 'NOTED SCALES ARE FULL SIZE. DO NOT SCALE.', 8.0, MID, raw=True)
        yy += 86; p.line((x0, yy), (x1, yy), RULE)
        lab(yy + 20, 'COORDINATED WITH')
        p.text(x0 + 14, yy + 38, 'FOR ARCHITECTURE CO.', 10, raw=True)
        p.text(x0 + 14, yy + 52, 'A-201 AND A-202, REV 1, 10.23.26', 9, raw=True)
        ry = yy + 66; p.line((x0, ry), (x1, ry), RULE)
        lab(ry + 20, 'REVISIONS')
        cols = [x0, x0 + 30, x0 + 92, x1]; hy = ry + 30; pitch = 18
        revs = list(REVS)          # review draft rows on every sheet (the history lives in the project record)
        nrows = len(revs)
        for i in range(nrows + 1): p.line((x0, hy + pitch * i), (x1, hy + pitch * i), 0.3, LIGHT)
        for c in cols[1:3]: p.line((c, hy), (c, hy + pitch * nrows), 0.3, LIGHT)
        for i, (no, date, desc) in enumerate(revs[-nrows:]):
            yb = hy + pitch * i + 12.5
            p.text(cols[0] + 8, yb, no, 8, raw=True); p.text(cols[1] + 6, yb, date, 8, raw=True)
            sz = 8.0
            while _FR.text_length(desc, fontsize=sz) > cols[3] - cols[2] - 10 and sz > 5.6: sz -= 0.2
            p.text(cols[2] + 6, yb, desc, sz, raw=True)
        rb = hy + pitch * nrows; p.line((x0, rb), (x1, rb), RULE)
        lab(rb + 20, 'SHEET TITLE')
        tl = [remap(t).replace(' & ', ' AND ') for t in title_lines[:2]]
        wmax = x1 - x0 - 28; sz = 15.0
        words = ' '.join(tl).split()
        if max(_FS.text_length(t, fontsize=13) for t in tl) > wmax:          # too long for two lines at 13: rewrap onto up to three
            tl = []; cur = ''
            for w_ in words:
                t_ = (cur + ' ' + w_).strip()
                if _FS.text_length(t_, fontsize=13) > wmax and cur: tl.append(cur); cur = w_
                else: cur = t_
            tl.append(cur); sz = 13.0
        while max(_FS.text_length(t, fontsize=sz) for t in tl) > wmax and sz > 10: sz -= 0.5
        for i, t in enumerate(tl[:3]): p.text(x0 + 14, rb + 44 + (sz + 5) * i, t, sz, serif=True, raw=True)
        p.line((x0, FR.y1 - 96), (x1, FR.y1 - 96), RULE)
        lab(FR.y1 - 78, 'SHEET NO.')
        p.text(cx, FR.y1 - 24, sheet_no, 44, serif=True, align='c', spacing=1.0, raw=True)

    # ---- finish tag (designer style boxed code with dog-leg leader)
    def tag(self, cx, cy, code, lead=11.0, flip=False, sides='lr'):
        g = (0.251, 0.251, 0.251); size = TXT['tag']
        w = FREG.text_length(code, fontsize=size); bw, bh = w + 3.0, ps(size) + 2.6
        x0, x1 = cx - bw / 2, cx + bw / 2; y0, y1 = cy - bh / 2, cy + bh / 2
        self.rect((x0, y0, x1, y1), width=0.48, color=g, fill=(1, 1, 1))
        self.text(cx, cy + ps(size) * 0.36, code, size, g, align='c')
        d = lead * 0.87; sgn = -1 if flip else 1
        if 'l' in sides: self.polyline([(x0, cy), (x0 - 4.7, cy), (x0 - 4.7 - d * 1.15, cy - sgn * d)], 0.3, g, close=False)
        if 'r' in sides: self.polyline([(x1, cy), (x1 + 4.7, cy), (x1 + 4.7 + d * 1.15, cy + sgn * d)], 0.3, g, close=False)

    def tag_stack(self, cx, cy, codes, lead=11.0, sides='lr', flip=False):
        g = (0.251, 0.251, 0.251); size = TXT['tag']; bh = ps(size) + 2.6; pitch = bh + 0.9
        w = max(FREG.text_length(c, fontsize=size) for c in codes) + 3.0
        x0, x1 = cx - w / 2, cx + w / 2
        n = len(codes); tops = [cy - (n - 1) * pitch / 2 + i * pitch - bh / 2 for i in range(n)]
        for c, y0 in zip(codes, tops):
            self.rect((x0, y0, x1, y0 + bh), width=0.48, color=g, fill=(1, 1, 1))
            self.text(cx, y0 + bh / 2 + ps(size) * 0.36, c, size, g, align='c')
        d = lead * 0.87; sgn = -1 if flip else 1
        if 'l' in sides:
            yl = tops[0] + bh / 2; self.polyline([(x0, yl), (x0 - 4.7, yl), (x0 - 4.7 - d * 1.15, yl - sgn * d)], 0.3, g, close=False)
        if 'r' in sides:
            yr = tops[-1] + bh / 2; self.polyline([(x1, yr), (x1 + 4.7, yr), (x1 + 4.7 + d * 1.15, yr + sgn * d)], 0.3, g, close=False)

    # ---- elevation marker (circle with view number over sheet number, arrow toward the wall)
    def elev_marker(self, cx, cy, number, sheet, direction, r=8.0):
        """direction: the way the viewer looks (N/E/S/W). Circle split by a horizontal bar: view number top, sheet bottom."""
        g = INK
        sh = self.p.new_shape(); sh.draw_circle(fitz.Point(cx, cy), r); sh.finish(color=g, width=0.6, fill=(1, 1, 1)); sh.commit()
        self.line((cx - r, cy), (cx + r, cy), 0.5, g)
        f = r / 8.0
        self.text(cx, cy - 1.6 * f, str(number), 6.2 * f, g, align='c', raw=True)
        self.text(cx, cy + 6.0 * f, sheet.replace('ID-', ''), 5.0 * f, g, align='c', raw=True)
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[direction]
        tip = (cx + dx * (r + 6), cy + dy * (r + 6))
        base1 = (cx + dx * r - dy * 3.5, cy + dy * r + dx * 3.5); base2 = (cx + dx * r + dy * 3.5, cy + dy * r - dx * 3.5)
        sh = self.p.new_shape(); sh.draw_polyline([fitz.Point(base1), fitz.Point(tip), fitz.Point(base2), fitz.Point(base1)]); sh.finish(color=g, width=0.4, fill=g); sh.commit()

    def scale_bar(self, x, y, ft_per_unit=1.0, pt_per_ft=13.5, label='3/16" TO 1\'-0"'):
        p = self
        units = 10
        for i in range(units):
            fill = INK if i % 2 == 0 else (1, 1, 1)
            p.rect((x + i * pt_per_ft, y - 4, x + (i + 1) * pt_per_ft, y), 0.4, INK, fill)
        for i in (0, 5, 10):
            p.text(x + i * pt_per_ft, y + 8, f"{i}'", 5.5, MID, align='c')
        p.text(x + units * pt_per_ft + 10, y - 0.5, label, 6, MID)


def fix_soft_hyphen(doc):
    """Every generator calls this last: the title block scales are written, then the ToUnicode fix
    (the embedded Century Gothic subset maps the hyphen glyph to U+00AD; rewrite ToUnicode so 'WD-01' is searchable)."""
    finish_scales(doc)
    done = set()
    for pg in doc:
        for fo in pg.get_fonts(full=True):
            tu = doc.xref_get_key(fo[0], 'ToUnicode')
            if tu[0] != 'xref': continue
            x = int(tu[1].split()[0])
            if x in done: continue
            s = doc.xref_stream(x)
            if s and (b'00AD' in s or b'00ad' in s):
                doc.update_stream(x, s.replace(b'00AD', b'002D').replace(b'00ad', b'002d')); done.add(x)


def print_ink(doc):
    """Print pass (owner 11.07.26: 'very dark black, no gray'). On every page and every form it draws (the FOR base, the logo):
    every grey line (stroke) becomes black; grey fills at or under 0.6 become black, lighter fills darken by 0.25, near-whites stay;
    every line gets 0.25 pt heavier, none under 0.45 pt. Colours that are not neutral grey (swatches, the orange view numbers) are untouched."""
    import re as re_
    num = r'(-?\d*\.?\d+)'
    def g(v):
        v = float(v)
        return 0.0 if v <= 0.6 else (round(v - 0.25, 3) if v < 0.9 else v)
    def rgb(m):
        r, gg, b = (float(m.group(i)) for i in (1, 2, 3))
        if max(r, gg, b) - min(r, gg, b) > 0.03: return m.group(0)
        v0 = (r + gg + b) / 3
        v = (0.0 if v0 < 0.95 else v0) if m.group(4) == 'RG' else g(v0)      # every grey line prints black; light grey fills only darken
        return '%g %g %g %s' % (v, v, v, m.group(4))
    def gray(m):
        if m.group(2) == 'G': return '%g G' % (0.0 if float(m.group(1)) < 0.95 else float(m.group(1)))
        return '%g %s' % (g(m.group(1)), m.group(2))
    def width(m): return '%g w' % max(float(m.group(1)) + 0.25, 0.45)
    rx_rgb = re_.compile(num + r'\s+' + num + r'\s+' + num + r'\s+(RG|rg)\b')
    rx_g = re_.compile(r'(?<![\d.])' + num + r'\s+(G|g)\b')
    rx_w = re_.compile(r'(?<![\d.])' + num + r'\s+w\b')
    rx_d = re_.compile(r'\[([\d.\s]*)\]\s+(-?\d*\.?\d+)\s+d\b')
    def dash(m):                                         # short dashes print solid at 65%: lengthen them so hidden lines read as hidden
        v = [float(x) for x in m.group(1).split()]
        if not v or max(v) >= 5: return m.group(0)
        return '[%s] %s d' % (' '.join('%g' % (x * 1.8) for x in v), m.group(2))
    seen = set()
    def fix(xref):
        if xref in seen: return
        seen.add(xref)
        try: st = doc.xref_stream(xref)
        except Exception: return
        if st is None: return
        t = st.decode('latin1')
        t2 = rx_d.sub(dash, rx_w.sub(width, rx_g.sub(gray, rx_rgb.sub(rgb, t))))
        if t2 != t: doc.update_stream(xref, t2.encode('latin1'))
    for pg in doc:
        for x in pg.get_contents(): fix(x)
        for xo in pg.get_xobjects():                     # forms placed with show_pdf_page: the base plans, the logo, other sheets
            if doc.xref_get_key(xo[0], 'Subtype')[1] == '/Form': fix(xo[0])
        # forms nested inside forms
        stack = [xo[0] for xo in pg.get_xobjects()]
        while stack:
            x = stack.pop()
            res = doc.xref_get_key(x, 'Resources/XObject')
            for ref in re_.findall(r'(\d+) 0 R', res[1] if res[0] in ('dict', 'xref') else ''):
                r_ = int(ref)
                if doc.xref_get_key(r_, 'Subtype')[1] == '/Form' and r_ not in seen: fix(r_); stack.append(r_)


CLOUDS = False      # owner 11.09.26: no revision clouds unless he asks (these sheets are not going to the city)
def rev_cloud_pt(page, r, tag='1', bump=7.0, color=(0.0, 0.0, 0.0), width=0.9, tag_at='tr'):
    if not CLOUDS: return
    """Revision cloud around page rect r (points), scalloped outward, with a delta tag at a corner (owner comments 11.09.26:
    every change on the reissue is clouded so the review starts at the clouds)."""
    import math
    r = fitz.Rect(r); pts = []
    def edge(a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, round(L / bump)); return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    corners = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
    sh = page.new_shape()
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]; seg = edge(a, b) + [b]
        for j in range(len(seg) - 1):
            p0, p1 = seg[j], seg[j + 1]; mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
            nx, ny = dy / L, -dx / L              # outward normal for a clockwise loop in page space (y down)
            ctrl = (mx + nx * L * 0.55, my + ny * L * 0.55)
            sh.draw_bezier(fitz.Point(*p0), fitz.Point(p0[0] + (ctrl[0] - p0[0]) * 0.9, p0[1] + (ctrl[1] - p0[1]) * 0.9),
                           fitz.Point(p1[0] + (ctrl[0] - p1[0]) * 0.9, p1[1] + (ctrl[1] - p1[1]) * 0.9), fitz.Point(*p1))
    sh.finish(color=color, width=width, closePath=False); sh.commit()
    cx, cy = {'tr': (r.x1 + 4, r.y0 - 4), 'tl': (r.x0 - 4, r.y0 - 4), 'br': (r.x1 + 4, r.y1 + 4), 'bl': (r.x0 - 4, r.y1 + 4)}[tag_at]
    s_ = 7.5; tri = [fitz.Point(cx, cy - s_), fitz.Point(cx + s_ * 0.9, cy + s_ * 0.6), fitz.Point(cx - s_ * 0.9, cy + s_ * 0.6)]
    sh = page.new_shape(); sh.draw_polyline(tri + [tri[0]]); sh.finish(color=color, width=0.7, fill=(1, 1, 1), closePath=True); sh.commit()
    page.insert_text(fitz.Point(cx - 2.0, cy + 3.2), tag, fontsize=6.5, fontname='helv', color=color)
