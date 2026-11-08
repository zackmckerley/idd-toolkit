"""Wall finish plans: edit the designer's wall covering sheets (id 01, id 07) into clean Helios base pages.
Run with IDD_SRC pointing at the wall covering PDF."""
import os, re
os.environ['IDD_SRC'] = '/mnt/user-data/uploads/f4877d18-Pages_from_Casa_Grove_ID_Set_-_Wall_Coverings.pdf'
import wf_helpers as H
from wf_helpers import doc, fitz, Draw, FREG, strip_oc, strip_text_in, strip_paths_in, edit_text, find, neutralize
OUT = '/home/claude/flrwork/261101.3350THOMAS.WallFinish-base.pdf'
DARK = (0.251, 0.251, 0.251)
EXT_W = 1.0          # extent line weight
EXT_OFF = 2.0        # offset inside the wall face
TICK = 4.0

class WDraw(Draw):
    def dline(self, pts, width, color, dashes=None):
        sh = self.p.new_shape()
        sh.draw_polyline([self.P(*q) for q in pts])
        sh.finish(color=color, width=width, closePath=False, lineCap=0, dashes=dashes)
        sh.commit()
    def tag(self, cx, cy, code, lead=11.0, flip=False, sides='lr'):
        """Boxed code, white fill, dog-leg leaders."""
        g = DARK; size = 5.8748
        w = FREG.text_length(code, fontsize=size); bw, bh = w + 1.0, 7.4
        x0, x1 = cx - bw / 2, cx + bw / 2; y0, y1 = cy - bh / 2, cy + bh / 2
        self.rect((x0, y0, x1, y1), width=0.48, color=g, fill=(1, 1, 1))
        self.text(cx, cy + 2.1, code, size, g, align='c')
        d = lead * 0.87; sgn = -1 if flip else 1
        if 'l' in sides: self.line([(x0, cy), (x0 - 4.7, cy), (x0 - 4.7 - d * 1.15, cy - sgn * d)], 0.3, g)
        if 'r' in sides: self.line([(x1, cy), (x1 + 4.7, cy), (x1 + 4.7 + d * 1.15, cy + sgn * d)], 0.3, g)
    def tag_stack(self, cx, cy, codes, lead=11.0, sides='lr', flip=False):
        g = DARK; size = 5.8748; bh = 7.4; pitch = bh + 0.9
        w = max(FREG.text_length(c, fontsize=size) for c in codes) + 1.0
        x0, x1 = cx - w / 2, cx + w / 2
        tops = [cy - pitch / 2 - bh / 2, cy + pitch / 2 - bh / 2]
        for c, y0 in zip(codes, tops):
            self.rect((x0, y0, x1, y0 + bh), width=0.48, color=g, fill=(1, 1, 1))
            self.text(cx, y0 + bh / 2 + 2.1, c, size, g, align='c')
        d = lead * 0.87; sgn = -1 if flip else 1
        if 'l' in sides:
            yl = tops[0] + bh / 2
            self.line([(x0, yl), (x0 - 4.7, yl), (x0 - 4.7 - d * 1.15, yl - sgn * d)], 0.3, g)
        if 'r' in sides:
            yr = tops[1] + bh / 2
            self.line([(x1, yr), (x1 + 4.7, yr), (x1 + 4.7 + d * 1.15, yr + sgn * d)], 0.3, g)
    def extent(self, a, b):
        """Heavy dashed wall-finish extent line from a to b (already offset inside the wall face) with end ticks."""
        (x0, y0), (x1, y1) = a, b
        self.dline([a, b], EXT_W, DARK, dashes='[6 3] 0')
        if abs(x1 - x0) < 1e-6:      # vertical run: ticks horizontal
            for y in (y0, y1): self.line([(x0 - TICK / 2, y), (x0 + TICK / 2, y)], 0.6, DARK)
        else:
            for x in (x0, x1): self.line([(x, y0 - TICK / 2), (x, y0 + TICK / 2)], 0.6, DARK)
    def note(self, x, y, lines, size=5.9, align='l'):
        for i, t in enumerate(lines):
            self.text(x, y + i * (size + 1.2), t, size, DARK, align=align)

# =====================================================================
# FLOOR 1 (page index 1, designer sheet id 01)
# =====================================================================
p1 = doc[1]
print('gray fills removed', strip_oc(p1, 'a-bro hatch 2'))
print('a-fin flr removed', strip_oc(p1, 'a-fin flr'))
print('dimension chains removed', strip_oc(p1, 'a-dim'))   # dimensions belong on the architectural set, not the wall finish plan
print('stray dimensions on layer 0 removed', strip_paths_in(p1, (180, 455, 560, 940), '0'))   # foyer chain and pantry ticks drawn on layer 0
# wall codes that clash with floor codes: WD-01 (wood) -> WP-01, ST-01 (stone) -> WS-01
wd = find(p1, 'WD-01'); st = [o for o in find(p1, 'ST-01') if o[0] < 760]   # the legend copy stays with the legend
assert len(wd) == 2 and len(st) == 1, (wd, st)
edit_text(p1, [('WD-01', wd[0], 'WP-01'), ('WD-01', wd[1], 'WP-01'), ('ST-01', st[0], 'WS-01'),
               ('Coconut Grove, FL 33143', None, 'Coconut Grove, FL 33133')] + [('CARTPORT', o, 'CARPORT') for o in find(p1, 'CARTPORT')])
# room-size subtitles off too (they stay on FP-1)
for t in ('22\'-8" x 22\'-5"', '15\'-6" x 16\'-2"', '15\'-9" x 15\'-2"'):
    for o in find(p1, t):
        if o[0] < 760: edit_text(p1, [(t, o, None)])
d1 = WDraw(p1)
d1.text(353.1, 641.7, 'GUEST RM', 9.4, DARK, align='c'); d1.text(353.1, 651.7, 'FOYER', 9.4, DARK, align='c')   # named on FP-1, unnamed on the designer's wall sheet
# rooms the designer left gray: default wall finish, tagged
for cx, cy in [(200.0, 625.0),    # guest bedroom
               (115.0, 685.0),    # guest bath
               (358.0, 764.0),    # laundry
               (266.0, 828.0),    # service area
               (148.0, 820.0),    # pet area
               (561.0, 1097.0),   # office
               (262.0, 470.0),    # pantry (no designer tag), clear of the dimension strings
               (330.0, 330.0)]:   # kitchen, free-standing (the designer's kitchen tags sit on the pantry wall line)
    d1.tag_stack(cx, cy, ['PT-02', 'CM-01'], sides='')
# guest bath: tub/shower alcove walls, three sides, full height
GB = (175.4, 667.1, 215.9, 734.6)
d1.extent((GB[2] - EXT_OFF, GB[1] + EXT_OFF), (GB[2] - EXT_OFF, GB[3] - EXT_OFF))
d1.extent((GB[0], GB[1] + EXT_OFF), (GB[2] - EXT_OFF, GB[1] + EXT_OFF))
d1.extent((GB[0], GB[3] - EXT_OFF), (GB[2] - EXT_OFF, GB[3] - EXT_OFF))
d1.tag(195.5, 700.0, 'WT-01', sides='')
# great room east wall: stone at the fireplace, painted paneled cabinetry at the flanks (designer's tags, renamed)
d1.extent((596.9 - EXT_OFF, 541.0), (596.9 - EXT_OFF, 622.0))             # WS-01 fireplace face
d1.extent((601.4 - EXT_OFF, 472.2), (601.4 - EXT_OFF, 541.0))             # WP-01 north flank
d1.extent((601.4 - EXT_OFF, 622.0), (601.4 - EXT_OFF, 690.6))             # WP-01 south flank
# title text that compose does not show is left alone; sheet is clipped to the plan column

# =====================================================================
# FLOOR 2 (page index 2, designer sheet id 07)
# =====================================================================
p2 = doc[2]
print('gray fills removed', strip_oc(p2, 'a-bro hatch 2'))
print('floor hatches removed', strip_oc(p2, 'a-fin flr'))
print('furniture removed', strip_oc(p2, 'a-furniture'))
print('rugs removed', strip_oc(p2, 'a-rug'))
# paint legend images in the schedule column (outside the clip, but keep the page clean)
for xref in p2.get_contents():
    s_ = doc.xref_stream(xref).decode('latin1')
    if re.search(r'/Xop[234] Do', s_):
        doc.update_stream(xref, neutralize(s_).encode('latin1'))
print('legend text removed', strip_text_in(p2, (730, 45, 1390, 340)))
edits = []
for txt in ('W.I.C.', 'MASTER', 'BATHRM'):
    for o in find(p2, txt, 0xff8c1a):
        edits.append((txt, o, None))
for txt in ('MASTER', 'BEDROOM'):
    for o in find(p2, txt, 0x404040, 10.1825):
        if 350 < o[0] < 450 and 830 < o[1] < 880:
            edits.append((txt, o, None))
for o in find(p2, 'TERRACE', 0x404040, 11.7491):
    if o[0] > 450:
        edits.append(('TERRACE', o, None))
dims = sorted(find(p2, '15\'-6" x 16\'-2"'), key=lambda o: o[1]); assert len(dims) == 2, dims
wic_dim, mb_dim = dims
edits += [('15\'-6" x 16\'-2"', wic_dim, None), ('15\'-6" x 16\'-2"', mb_dim, None),
          ('Coconut Grove, FL 33143', None, 'Coconut Grove, FL 33133')]
ms_dim = find(p2, '15\' x 17\'-6"'); assert len(ms_dim) == 1, ms_dim
edits.append(('15\' x 17\'-6"', ms_dim[0], None))
print('page2 edits', len(edits)); edit_text(p2, edits)
d2 = WDraw(p2)
d2.text(316.0, 566.0, 'HALL', 9.4, DARK, align='c')      # unnamed on the designer's sheet
OLDW = FREG.text_length('15\'-6" x 16\'-2"', fontsize=10.1825)
# room sizes stay on the flooring sheets; the wall finish plan carries finishes only
# room tags (default finish) free-standing under each room name
for cx, cy in [(280.0, 248.0),   # bedroom 3, clear of the room number
               (174.0, 203.0),   # bath 3
               (174.0, 335.0),   # bath 2
               (209.0, 506.0),   # bedroom 2, clear of the room number
               (209.0, 625.0),   # den / playroom
               (338.0, 470.0),   # hall
               (452.0, 880.0),   # master suite, clear of the id.10 marker
               (215.0, 746.0),   # W.I.C., inside the island above the label
               (265.0, 928.0)]:  # master bath
    d2.tag_stack(cx, cy, ['PT-02', 'CM-01'], sides='')
# baths 2 and 3: tub alcove walls, three sides, full height
for tub, tagy in [((123.8, 149.3, 191.3, 183.0), 190.0), ((123.8, 281.4, 191.3, 315.2), 322.0)]:
    x0, y0, x1, y1 = tub
    d2.extent((x0 + EXT_OFF, y0 + EXT_OFF), (x0 + EXT_OFF, y1))
    d2.extent((x1 - EXT_OFF, y0 + EXT_OFF), (x1 - EXT_OFF, y1))
    d2.extent((x0 + EXT_OFF, y0 + EXT_OFF), (x1 - EXT_OFF, y0 + EXT_OFF))
    d2.tag(150.0, tagy, 'WT-01', lead=20.0 / 0.87, sides='r', flip=True)
# master bath: shower (three walls) and tub alcove (three walls)
SH = (123.8, 950.6, 173.3, 1014.7)
d2.extent((SH[0] + EXT_OFF, SH[1]), (SH[0] + EXT_OFF, SH[3] - EXT_OFF))
d2.extent((SH[2] - EXT_OFF, SH[1]), (SH[2] - EXT_OFF, SH[3] - EXT_OFF))
d2.extent((SH[0] + EXT_OFF, SH[3] - EXT_OFF), (SH[2] - EXT_OFF, SH[3] - EXT_OFF))
d2.tag(150.0, 982.0, 'WT-02', sides='')
TUB = (178.0, 945.0, 250.0, 1014.7)
d2.extent((TUB[0] + EXT_OFF, TUB[1] + 5), (TUB[0] + EXT_OFF, TUB[3] - EXT_OFF))
d2.extent((TUB[2] - EXT_OFF, TUB[1] + 5), (TUB[2] - EXT_OFF, TUB[3] - EXT_OFF))
d2.extent((TUB[0] + EXT_OFF, TUB[3] - EXT_OFF), (TUB[2] - EXT_OFF, TUB[3] - EXT_OFF))
d2.tag(214.0, 962.0, 'WT-02', lead=15.0 / 0.87, sides='lr', flip=True)
# master suite headboard wall: painted wood paneling, full height, corner to corner
d2.extent((515.9 - EXT_OFF, 768.1), (515.9 - EXT_OFF, 909.0))
d2.tag_stack(488.0, 836.0, ['PT-02', 'WP-02'], lead=6.3 / 0.87, sides='r')
# hidden safe: jib door finished to match the wall
d2.note(556.0, 930.0, ['JIB DOOR', 'FINISH TO MATCH WALL,', 'NO CASING'], align='c')
d2.line([(545.0, 922.0), (541.0, 911.0)], 0.3, DARK)

doc.save(OUT, garbage=3, deflate=True)
print('saved', OUT)
