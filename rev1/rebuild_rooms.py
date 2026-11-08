"""Reissue the designed-room sheets on the FOR REV 1 base (11.05.26): key plans re-based, FOR's room names, revision row 1."""
import sys; sys.path.insert(0, '/home/claude/flrwork')
import idd_std, idd_sheet
idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
idd_sheet.EXTRA_REVS[:] = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1')]
BASE_REVS = list(idd_sheet.EXTRA_REVS)
import build_great_rev1b                                   # sets its own revision rows at import, captured here
LIV_REVS = list(idd_sheet.EXTRA_REVS); idd_sheet.EXTRA_REVS[:] = BASE_REVS
# every designed room on its FOR REV 1 generator (11.06.26); the pre-REV 1 generators are not called, so a rerun cannot overwrite the redrawn sheets
import build_mbath_rev1, build_mbr_rev1, build_baths_rev1 as build_baths, build_kitchen_rev1, build_beds_rev1, build_great_s2
import json, pymupdf as fitz
from idd_sheet import Sheet
# record every key plan placement and every elevation marker drawn over it, back in base display space, for ID-201/202
_KP = {}; MARKS = []
_show = fitz.Page.show_pdf_page
def show(page, rect, src, pno=0, **kw):
    clip = kw.get('clip')
    if clip is not None and 'Base' in (src.name or ''):
        sp = src[pno]; cd = fitz.Rect(clip) * sp.rotation_matrix; cd.normalize()
        _KP[id(page)] = (fitz.Rect(rect), cd, pno + 1)
    return _show(page, rect, src, pno, **kw)
fitz.Page.show_pdf_page = show
_em = Sheet.elev_marker
def em(self, cx, cy, n, sheet, d, *a, **kw):
    kp = _KP.get(id(self.p))
    if kp:
        t, cd, fl = kp; k = t.width / cd.width
        if t.contains(fitz.Point(cx, cy)): MARKS.append({'floor': fl, 'x': cd.x0 + (cx - t.x0) / k, 'y': cd.y0 + (cy - t.y0) / k, 'n': n, 'sheet': sheet, 'dir': d})
    return _em(self, cx, cy, n, sheet, d, *a, **kw)
Sheet.elev_marker = em
only = sys.argv[1:]
def living():
    idd_sheet.EXTRA_REVS[:] = LIV_REVS; idd_std.PROJECT['date'] = build_great_rev1b.ISSUE; build_great_rev1b.build()
JOBS = (('bath', build_mbath_rev1.build), ('mbr', build_mbr_rev1.build), ('baths', build_baths.build), ('kitchen', build_kitchen_rev1.build),
        ('beds', build_beds_rev1.build), ('living', living), ('study2', build_great_s2.build))
P0 = dict(idd_std.PROJECT)
for name, fn in JOBS:
    if only and name not in only: continue
    # each generator sets its own revision rows and dates: reset both so one job cannot leak into the next
    idd_std.PROJECT.clear(); idd_std.PROJECT.update(P0); idd_sheet.EXTRA_REVS = list(BASE_REVS); idd_sheet.EXTRA_REVS[:] = BASE_REVS
    fn()

if not only:
    json.dump(MARKS, open('/home/claude/flrwork/rev1/markers_display.json', 'w'), indent=0)
    print(len(MARKS), 'markers recorded')
