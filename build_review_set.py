"""Casa Grove review draft (owner 11.07.26): cover with the front elevation and the sheet index, every sheet in walk-the-house order,
printed on 11 x 17. Sheets are drawn 17:11 so they print edge to edge. Output: 261109.HD102.ReviewSet.pdf (11 x 17) and 261109.HD102.ReviewSet-FullSize.pdf."""
import re, sys
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
import idd_std, idd_sheet
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, _FR, _FS
from idd_std import INK, MID, LIGHT
from elev_front import draw_front

D = '/home/claude/flrwork/'
SOURCES = ['261109.HD102.DoorSchedule.pdf', '261105.HD102.FinishPlans.pdf', '261109.HD102.RCP-Lighting.pdf', '261105.HD102.EntryPowderPilot.pdf', '261105.HD102.LivingRoomPilot.pdf', '261105.HD102.KitchenPilot.pdf',
           '261105.HD102.MudroomPilot.pdf', '261105.HD102.MasterBedroomPilot.pdf', '261105.HD102.MasterBathPilot.pdf', '261109.HD102.MasterCloset.pdf', '261109.HD102.PoolHouse.pdf',
           '261106.HD102.Bedrooms.pdf', '261105.HD102.SecondaryBaths.pdf', '261109.HD102.Details.pdf']
# Owner 11.07.26: plans in the 100s, floor 1 rooms in the 200s, floor 2 rooms in the 300s, a block of ten per room (x0 = key plan).
# The index lists every sheet the set will have; sheets not drawn yet are marked TBD.
SECTIONS = [('GENERAL', [('0', None)]), ('PLANS', [('1', None)]),
            ('FLOOR 1', [('21', 'ENTRY AND POWDER ROOM'), ('22', 'OFFICE'), ('23', 'LIVING ROOM'), ('24', 'KITCHEN, DINING AND PANTRY'),
                         ('25', 'MUDROOM, LAUNDRY AND DOG ROOM'), ('26', 'GUEST BEDROOM AND GUEST BATH'), ('27', 'STAIR AND HALLS')]),
            ('FLOOR 2', [('31', 'MASTER BEDROOM'), ('32', 'MASTER BATH'), ('33', 'MASTER CLOSET'), ('34', 'BEDROOM 2 AND BATH 2'),
                         ('35', 'BEDROOM 3 AND BATH 3'), ('36', 'DEN / PLAYROOM'), ('37', 'UPPER HALL AND LINEN CLOSET')]),
            ('POOL HOUSE', [('40', None)]),                          # review 11.09.26: no repeated heading on the cover
            ('DETAILS', [('5', None)])]
TBD = [('ID-001', 'SCHEDULES'),
       ('ID-141', 'POWER AND DATA PLAN FLOOR 1'), ('ID-142', 'POWER AND DATA PLAN FLOOR 2'),
       ('ID-151', 'FURNITURE PLAN FLOOR 1'), ('ID-152', 'FURNITURE PLAN FLOOR 2'),
       ('ID-220', 'OFFICE ELEVATIONS'), ('ID-270', 'STAIR AND HALLS ELEVATIONS'),
       ('ID-360', 'DEN / PLAYROOM ELEVATIONS'), ('ID-370', 'UPPER HALL AND LINEN CLOSET (WASHER AND DRYER)'),
       # renderings sit at x8 and x9 of each room block (owner 11.07.26: prepared, not rendered yet)
       ('ID-218', 'RENDERINGS: ENTRY AND POWDER ROOM'), ('ID-238', 'RENDERINGS: LIVING ROOM'), ('ID-248', 'RENDERINGS: KITCHEN AND PANTRY'),
       ('ID-258', 'RENDERINGS: MUDROOM'), ('ID-268', 'RENDERINGS: GUEST BEDROOM AND BATH'), ('ID-318', 'RENDERINGS: MASTER BEDROOM'),
       ('ID-328', 'RENDERINGS: MASTER BATH'), ('ID-348', 'RENDERINGS: BEDROOM 2 AND BATH 2'), ('ID-358', 'RENDERINGS: BEDROOM 3 AND BATH 3')]
NEW_SHEETS = ()          # owner comments 11.09.26: new sheets, clouded in the index
COORD = ['FOR ARCHITECTURE CO., PERMIT SET OF 07.01.26,', 'REVISION 1 OF 10.23.26 (RESPONSE TO BUILDING COMMENTS):',
         'A-201 PROPOSED FIRST FLOOR PLAN', 'A-202 PROPOSED SECOND FLOOR PLAN']
NOTES = [['FOR\'S DRAWINGS GOVERN CONSTRUCTION. WHERE THESE SHEETS CHANGE FOR\'S PLAN,', 'THE CHANGE IS LISTED ON THAT ROOM\'S KEY PLAN.'],
         ['DIMENSIONS ARE TO FINISHED FACES.'],
         ['CEILINGS 10\'-0" AND DOOR HEADS 8\'-0" ARE ASSUMED. VERIFY WITH FOR.'],
         ['OUTLETS AND SWITCHES SHOW DESIGN INTENT. THE ELECTRICIAN FINALIZES PER CODE.'],
         ['DOOR NUMBERS ARE FOR\'S. FOR NUMBERS DOORS BY TYPE, SO A NUMBER CAN REPEAT.'],
         ['SHEET NUMBERS: 100s PLANS, 200s FLOOR 1 ROOMS, 300s FLOOR 2 ROOMS. EACH ROOM HAS', 'A BLOCK OF TEN: x0 KEY PLAN, x1 TO x7 DRAWINGS, RENDERINGS FROM x8. TBD SHEETS ARE TO COME.'],
         ['PRINTED ON 11 x 17 AT 65% OF FULL SIZE: NOTED SCALES ARE FULL SIZE. DO NOT SCALE', 'THE PRINT. USE THE DIMENSIONS OR THE GRAPHIC SCALES.']]


def place(num):
    """(section, room) of a sheet number, for the index and the bookmarks."""
    n = num.replace('ID-', '')
    for sec, rooms in SECTIONS:
        for pre, room in rooms:
            if n.startswith(pre): return sec, room
    raise ValueError(num)


def sheet_info(page):
    """Sheet number and title as printed in the title block."""
    num, lab_t, lab_n, title = None, None, None, []
    spans = [s for b in page.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans'] if s['bbox'][0] > TB_X and s['text'].strip()]
    for s in spans:
        t = s['text'].strip()
        if t == 'SHEET TITLE': lab_t = s['bbox'][3]
        if t == 'SHEET NO.': lab_n = s['bbox'][1]
        if re.fullmatch(r'ID-\d{3}', t) and s['size'] > 30: num = t
    for s in spans:
        if lab_t and lab_n and lab_t < s['bbox'][1] < lab_n and s['size'] > 9: title.append(s['text'].strip())
    return num, ' '.join(title)


def cover(doc, rows):
    """rows: (number, title, drawn) for every sheet in the index, drawn sheets and TBD alike, in number order."""
    sh = Sheet(doc)
    sh.frame('CASA GROVE', '', ['COVER AND', 'SHEET INDEX'], 'ID-000', revisions=(), legend_rule=False)
    # front elevation (owner 11.09.26: coordinated-with and general notes removed from the cover; the elevation and the
    # project block take the column, the coordination lives in the title block of every sheet)
    er = draw_front(sh.p, fitz.Rect(70, 110, 850, 700))
    sh.text(er.x0, er.y1 + 24, 'FRONT ELEVATION', 11, serif=True, spacing=1.2, raw=True)
    sh.text(er.x0, er.y1 + 38, 'AFTER FOR ARCHITECTURE CO.', 8, MID, raw=True)
    # project
    y = FR.y1 - 190                                    # bottom-aligned with the index column
    sh.text(70, y, 'CASA GROVE', 54, serif=True, spacing=3.0, raw=True)
    sh.text(72, y + 34, '3350 THOMAS AVE, COCONUT GROVE, FLORIDA 33133', 14, raw=True)
    sh.line((72, y + 56), (850, y + 56), 0.6, INK)
    sh.text(72, y + 84, 'INTERIOR DESIGN DRAWINGS', 16, serif=True, spacing=1.5, raw=True)
    sh.text(72, y + 106, 'REVIEW DRAFT, REVISION 2, COORDINATED WITH FOR REV 1, NOVEMBER 9, 2026', 12, raw=True)
    sh.text(72, y + 122, 'NOT FOR CONSTRUCTION', 10, MID, raw=True)
    assert y + 122 < FR.y1 - 8, ('cover project block runs off the sheet', y)
    # sheet index: two columns, grouped by floor and room, TBD sheets in grey
    X0 = 900.0; GAP = 34.0; CW = (TB_X - 24 - X0 - GAP) / 2
    sh.line((X0 - 24, 90), (X0 - 24, FR.y1 - 20), 0.4, LIGHT)
    sh.text(X0, 112, 'SHEET INDEX', 16, serif=True, spacing=1.5, raw=True)
    items = []; last = (None, None)
    for num, title, drawn in rows:
        sec, room = place(num)
        if sec != last[0]: items.append(('sec', sec)); last = (sec, None)
        if room and room != last[1]: items.append(('room', room)); last = (sec, room)
        items.append(('row', (num, title, drawn)))
    H_ = {'sec': 34.0, 'room': 24.0, 'row': 18.5}
    total = sum(H_[k] for k, _ in items); top = 142.0; bottom = FR.y1 - 16
    # break the columns before a section or a room, at the first one past the middle
    acc = 0.0; brk = len(items)
    for i, (k, _) in enumerate(items):
        if k in ('sec', 'room') and acc > total / 2 - 20: brk = i; break
        acc += H_[k]
    for col, part in ((0, items[:brk]), (1, items[brk:])):
        x0 = X0 + col * (CW + GAP); x1 = x0 + CW; y = top
        for k, v in part:
            if k == 'sec':
                y += 14; sh.text(x0, y, v, 10.5, bold=True, spacing=0.8, raw=True); y += 5
                sh.line((x0, y), (x1, y), 0.5, INK); y += 15
            elif k == 'room':
                y += 7; sh.text(x0, y, v, 9, MID, spacing=0.6, raw=True); y += 17
            else:
                num, title, drawn = v; c = INK if drawn else MID
                sh.text(x0, y, num, 10.5, c, serif=True, raw=True)
                room_w = x1 - x0 - 58 - (26 if not drawn else 0); sz = 9.5
                while _FR.text_length(title, fontsize=sz) > room_w and sz > 6.5: sz -= 0.25
                sh.text(x0 + 58, y, title, sz, c, raw=True)
                if not drawn: sh.text(x1, y, 'TBD', 8.5, MID, bold=True, align='r', raw=True)
                if num in NEW_SHEETS: idd_sheet.rev_cloud_pt(sh.p, fitz.Rect(x0 - 4, y - 9.5, x0 + 58 + _FR.text_length(title, fontsize=sz) + 6, y + 3.5), '1', bump=4.5, tag_at='br')
                y += 18.5
        assert y < bottom, ('index column runs off the sheet', col, y)
    return sh


def build():
    pages = []
    for fn in SOURCES:
        d = fitz.open(D + fn)
        for p in d:
            n, t = sheet_info(p); assert n, ('no sheet number', fn, p.number)
            pages.append((n, t, d, p.number))
    nums = [r[0] for r in pages]; assert len(set(nums)) == len(nums), ('duplicate sheet numbers', sorted(nums))
    tbd = [r for r in TBD if r[0] not in nums]
    pages.sort(key=lambda r: r[0])
    rows = sorted([('ID-000', 'COVER AND SHEET INDEX', True)] + [(n, t, True) for n, t, _, _ in pages] + [(n, t, False) for n, t in tbd])
    full = fitz.open()
    cover(full, rows)
    for n, t, d, pno in pages: full.insert_pdf(d, from_page=pno, to_page=pno)
    fix_soft_hyphen(full)
    idd_sheet.print_ink(full)                               # black ink, heavier lines for the 11 x 17 print
    toc = [[1, 'ID-000 COVER AND SHEET INDEX', 1]]; last = (None, None)
    for i, (n, t, _, _) in enumerate(pages, start=2):
        sec, room = place(n)
        label = 'FLOOR 1 ROOMS' if sec == 'FLOOR 1' else 'FLOOR 2 ROOMS' if sec == 'FLOOR 2' else sec
        if sec != last[0]: toc.append([1, label, i]); last = (sec, None)
        if room and room != last[1]: toc.append([2, room, i]); last = (sec, room)
        toc.append([3 if room else 2, '%s  %s' % (n, t), i])
    full.set_toc(toc)
    meta = {'title': 'Casa Grove, Interior Design Drawings, Review Draft 11.07.26', 'author': 'Helios Development', 'subject': 'HD102, 3350 Thomas Ave'}
    full.set_metadata(meta); full.subset_fonts(); full.save(D + '261109.HD102.ReviewSet-FullSize.pdf', garbage=4, deflate=True, deflate_fonts=True, use_objstms=1)
    # 11 x 17: each 17:11 sheet scaled to the page, edge to edge
    small = fitz.open(); W, H = 1224.0, 792.0
    for p in full:
        r = p.rect; k = min(W / r.width, H / r.height)
        pg = small.new_page(width=W, height=H)
        tw, th = r.width * k, r.height * k
        pg.show_pdf_page(fitz.Rect((W - tw) / 2, (H - th) / 2, (W + tw) / 2, (H + th) / 2), full, p.number)
    small.set_toc(toc); small.set_metadata(meta)
    small.subset_fonts()                                   # fonts embedded once, subset: the set is small enough to email
    small.save(D + '261109.HD102.ReviewSet.pdf', garbage=4, deflate=True, deflate_fonts=True, clean=True, use_objstms=1)
    print('saved', len(full), 'sheets,', len(tbd), 'TBD rows')


if __name__ == '__main__':
    build()
