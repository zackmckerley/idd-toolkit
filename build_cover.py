"""Cover sheet ID-000 (index, abbreviations, symbol legend, general notes, base plan control, coordination log) and
schedules sheet ID-001 (material schedule, room finish schedule, lighting schedule, device counts) for Casa Grove.
Everything is generated from the set itself: the index from the sheet list, the schedules from the room model and the
finish codes used on ID-101/102 and ID-201/202, the fixture counts from the electrical layouts."""
import json, collections, pymupdf as fitz
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen, FREG
from idd_std import TXT, INK, MID, LIGHT, KEYNOTES, PROJECT, SERIES
import ast
def rows_from(path, name):
    """Read a module-level list literal (ROWS_F1 etc.) from a composer script without running it."""
    tree = ast.parse(open(path).read())
    ix = json.load(open('elev_index.json'))
    def _sheets_of(*rooms, wall=None):
        nos = sorted({v['sheet'] for v in ix if v['room'] in rooms and (wall is None or v['wall'] == wall)})
        return ', '.join(n if i == 0 else n[3:] for i, n in enumerate(nos)) or 'ID-7XX'
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == name for t in node.targets):
            return eval(compile(ast.Expression(node.value), path, 'eval'), {'_sheets_of': _sheets_of})
    raise KeyError(name)

# ---------------------------------------------------------------- the set
def sheet_list():
    ix = json.load(open('elev_index.json'))
    sheets = [('ID-000', 'COVER SHEET, INDEX, SYMBOLS & NOTES'), ('ID-001', 'FINISH, LIGHTING & DEVICE SCHEDULES'),
              ('ID-101', 'FLOORING PLAN - FLOOR 1'), ('ID-102', 'FLOORING PLAN - FLOOR 2'),
              ('ID-201', 'WALL FINISH PLAN - FLOOR 1'), ('ID-202', 'WALL FINISH PLAN - FLOOR 2'),
              ('ID-301', 'REFLECTED CEILING PLAN - FLOOR 1'), ('ID-302', 'REFLECTED CEILING PLAN - FLOOR 2'),
              ('ID-401', 'LIGHTING & SWITCHING PLAN - FLOOR 1'), ('ID-402', 'LIGHTING & SWITCHING PLAN - FLOOR 2'),
              ('ID-501', 'POWER & DATA PLAN - FLOOR 1'), ('ID-502', 'POWER & DATA PLAN - FLOOR 2'),
              ('ID-601', 'FURNITURE PLAN - FLOOR 1'), ('ID-602', 'FURNITURE PLAN - FLOOR 2')]
    by_sheet = collections.OrderedDict()
    for v in ix:
        by_sheet.setdefault(v['sheet'], []).append(v)
    for no, views in by_sheet.items():
        rooms = []
        for v in views:
            if v['room'] not in rooms: rooms.append(v['room'])
        sheets.append((no, f"INTERIOR ELEVATIONS - FLOOR {views[0]['floor']}: " + ', '.join(rooms)))
    sheets.append(('ID-801', 'TYPICAL DETAILS - TRIM, MILLWORK, TILE & FLOORS'))
    return sheets

ABBREV = [('AFF', 'ABOVE FINISHED FLOOR'), ('CL', 'CENTERLINE'), ('CLG', 'CEILING'), ('CM', 'CROWN MOLDING'), ('DCOF', 'DYNAMIC COEFFICIENT OF FRICTION'),
          ('EQ', 'EQUAL'), ('FIN. FLR.', 'FINISHED FLOOR'), ('GFCI', 'GROUND FAULT CIRCUIT INTERRUPTER'), ('LF', 'LINEAR FEET'), ('MIN.', 'MINIMUM'),
          ('N.I.C.', 'NOT IN CONTRACT'), ('O.C.', 'ON CENTER'), ('PT', 'PAINT'), ('SF', 'SQUARE FEET'), ('SL', 'SCHLUTER STRIP'), ('ST', 'STONE (FLOOR)'),
          ('T.B.C.', 'TO BE CONFIRMED'), ('TL', 'TILE (FLOOR)'), ('TYP.', 'TYPICAL'), ('U.N.O.', 'UNLESS NOTED OTHERWISE'), ('VIF', 'VERIFY IN FIELD'),
          ('WD', 'WOOD (FLOOR)'), ('WP', 'WOOD PANELING (WALL)'), ('WS', 'STONE (WALL)'), ('WT', 'TILE (WALL)')]

GENERAL_NOTES = [
    ['THIS INTERIOR DESIGN SET IS ISSUED FOR PRICING AND COORDINATION ONLY. IT IS NOT FOR PERMIT AND NOT FOR', 'CONSTRUCTION. THE ARCHITECTURAL SET BY FOR ARCHITECTURE CO. GOVERNS ALL DIMENSIONS, STRUCTURE, OPENINGS,', 'EGRESS AND LIFE SAFETY. WHERE THIS SET AND THE ARCHITECTURAL SET DISAGREE, NOTIFY HELIOS BEFORE PROCEEDING.'],
    ['BASE PLANS ARE THE YL DESIGNS INTERIOR SET YLD.068 (09.25.26), REDRAWN AND CORRECTED BY HELIOS. ROOM', 'NAMES ARE AS ON THE ARCHITECTURAL SET. NO DIMENSIONS ARE SHOWN ON PLAN SHEETS. ELEVATIONS CARRY', 'FINISH SET-OUT DIMENSIONS ONLY, FROM FINISHED FLOOR AND ROOM CENTERLINES.'],
    ['FINISH CODES ARE UNIQUE ACROSS THE SET: FLOOR CODES (WD, TL, ST, SL) NEVER REPEAT A WALL CODE (PT, CM, WS, WP, WT).', 'ONE CODE MEANS ONE MATERIAL EVERYWHERE IT APPEARS. SEE THE MATERIAL SCHEDULE ON ID-001.'],
    ['SUBMIT SAMPLES OF ALL FINISHES AND DRAW-DOWNS OF ALL PAINT COLORS FOR OWNER APPROVAL BEFORE ORDERING.', 'SUBMIT SHOP DRAWINGS FOR ALL MILLWORK, STONE, PANELING AND TILE SET-OUTS BEFORE FABRICATION.'],
    ['VERIFY ALL CONDITIONS IN THE FIELD. REPORT ANY CONFLICT BETWEEN FINISH EXTENTS AND BUILT CONDITIONS', 'BEFORE INSTALLATION. FINISHES RUN FULL HEIGHT, FLOOR TO CEILING, UNLESS NOTED.'],
    ['CEILING HEIGHTS, DOOR AND WINDOW HEADS ON THIS SET ARE TAKEN FROM THE YL DESIGNS ELEVATIONS OR ASSUMED', '(10\'-0" CEILINGS, 8\'-0" HEADS) AND ARE MARKED VERIFY. CONFIRM AGAINST THE ARCHITECTURAL SET BEFORE PRICING.'],
    ['LIGHTING, SWITCHING, POWER AND DATA SHEETS SHOW DESIGN INTENT. CIRCUITING, LOADS, AFCI / GFCI PROTECTION', 'AND CODE COMPLIANCE ARE BY THE ELECTRICAL ENGINEER OF RECORD.'],
    ['FLOORING: DCOF 0.42 MINIMUM FOR ALL TILE IN WET AREAS. TEMPERED GLAZING WITHIN 60" OF TUB AND SHOWER', 'FLOORS PER CODE. BLOCKING FOR FUTURE GRAB BARS AT ALL TUB AND SHOWER WALLS, 33" TO 36" AFF.'],
    ['KEYNOTES FOLLOW CSI MASTERFORMAT:'] + [', '.join(f'{k} {v}' for k, v in list(KEYNOTES.items())[i:i + 3]) for i in range(0, len(KEYNOTES), 3)],
]

def cover_sheet(doc):
    sh = Sheet(doc)
    sh.frame('COVER SHEET', '', ['COVER SHEET, INDEX,', 'SYMBOLS & NOTES'], 'ID-000', legend_rule=False)
    # project title block, big
    x, y = FR.x0 + 24, HDR_Y + 60
    sh.text(x, y, 'CASA GROVE', 34, bold=True, spacing=3.0); y += 26
    sh.text(x, y, '3350 THOMAS AVE, COCONUT GROVE, FL 33133', 12, MID, spacing=1.2); y += 22
    sh.text(x, y, 'INTERIOR DESIGN SET  .  HELIOS DEVELOPMENT  .  PROJECT HD102  .  ISSUED 11.01.26 FOR PRICING & COORDINATION', 9, MID); y += 30
    # index
    sh.text(x, y, 'SHEET INDEX', TXT['header'], bold=True, spacing=1.0); y += 16
    sheets = sheet_list()
    col_x = [x, x + 60]
    yy = y
    for i, (no, title) in enumerate(sheets):
        if i == 22: yy = y; col_x = [x + 410, x + 470]
        sh.text(col_x[0], yy, no, 7.5, bold=True); sh.text(col_x[1], yy, title[:92], 7.2, INK if not title.startswith('INTERIOR') else MID); yy += 11
    y_index_end = y + 11 * min(22, len(sheets)) + 10
    # abbreviations
    y = y_index_end + 12
    sh.text(x, y, 'ABBREVIATIONS', TXT['header'], bold=True, spacing=1.0); y += 16
    for i, (a, b) in enumerate(ABBREV):
        cx = x + (i % 3) * 270; cy = y + (i // 3) * 11
        sh.text(cx, cy, a, 7.2, bold=True); sh.text(cx + 48, cy, b, 7.2, MID)
    y += 11 * ((len(ABBREV) + 2) // 3) + 14
    # symbols
    sh.text(x, y, 'SYMBOLS', TXT['header'], bold=True, spacing=1.0); y += 18
    sh.tag_stack(x + 14, y + 4, ['PT-02', 'CM-01'], lead=0, sides=''); sh.text(x + 40, y + 2, 'FINISH TAG: CODE PER THE MATERIAL SCHEDULE. STACKED TAGS READ TOP TO BOTTOM (WALL OVER TRIM).', 7.2, MID); y += 24
    sh.p.draw_line(fitz.Point(x, y + 3), fitz.Point(x + 28, y + 3), color=INK, width=1.0, dashes='[6 3] 0')
    sh.text(x + 40, y + 6, 'EXTENT OF A SPECIAL WALL FINISH IN PLAN, TICKS AT START AND STOP.', 7.2, MID); y += 18
    sh.elev_marker(x + 14, y + 4, '1', 'ID-701', 'N'); sh.text(x + 40, y + 6, 'INTERIOR ELEVATION: VIEW NUMBER OVER SHEET NUMBER, ARROW TOWARD THE WALL VIEWED.', 7.2, MID); y += 24
    sh.p.draw_line(fitz.Point(x, y + 3), fitz.Point(x + 28, y + 3), color=INK, width=0.7, dashes='[4 2] 0')
    sh.text(x + 40, y + 6, 'CROWN MOLDING IN PLAN (RCP). HIDDEN OR ABOVE-PLANE WORK IS DASHED THROUGHOUT.', 7.2, MID); y += 18
    cloud(sh, (x, y - 2, x + 28, y + 10), '1'); sh.text(x + 40, y + 6, 'REVISION CLOUD WITH DELTA. CLOUDS ARE REMOVED AT THE NEXT ISSUE. THE REVISION TABLE IS THE RECORD.', 7.2, MID); y += 34
    # key plans: both floors from the clean base, small
    sh.text(x, y, 'KEY PLANS', TXT['header'], bold=True, spacing=1.0); y += 10
    import compose_plans as CP
    src = fitz.open(CP.BASE_CLEAN)
    # size the key plans to the space that is left above the frame (label line included); never to a fixed width
    clip_w, clip_h = 560.0, 1050.0
    avail_h = FR.y1 - 34 - (y + 6)
    kw = min(250.0, avail_h * clip_w / clip_h); kh = kw * clip_h / clip_w
    assert kh + y + 6 + 20 <= FR.y1, ('key plans do not fit above the frame', kh, y)
    targets = []
    for floor in (1, 2):
        sp = src[floor - 1]; dx, dy = CP.SHIFT[floor]
        clip_disp = fitz.Rect(80 + dx, 110 + dy, 640 + dx, 1160 + dy); u = clip_disp * sp.derotation_matrix; u.normalize()
        kx = x + (floor - 1) * (kw + 50); target = fitz.Rect(kx, y + 6, kx + kw, y + 6 + kh); targets.append(target)
        sh.p.show_pdf_page(target, src, floor - 1, clip=u, rotate=90)
        sh.text(kx + kw / 2, target.y1 + 12, f'FLOOR {floor}', 7.5, MID, align='c')
    # hard clips for the two key plans (show_pdf_page ignores clip with rotate)
    xref = sh.p.get_contents()[0]; st = doc.xref_stream(xref).decode('latin1')
    parts = st.split('q ')
    k = 0
    for i in range(1, len(parts)):
        if 'Do' in parts[i]:
            t = targets[k]; k += 1
            parts[i] = f'{t.x0:.2f} {sh.p.rect.height - t.y1:.2f} {t.width:.2f} {t.height:.2f} re W n ' + parts[i]
    doc.update_stream(xref, 'q '.join(parts).encode('latin1'))
    # general notes, right column
    gx, gy = x + 760, HDR_Y + 60
    sh.text(gx, gy, 'GENERAL NOTES', TXT['header'], bold=True, spacing=1.0); gy += 16
    for i, lines in enumerate(GENERAL_NOTES, 1):
        sh.text(gx, gy, f'{i}.', 7.2, MID)
        for ln in lines:
            sh.text(gx + 14, gy, ln, 7.0, MID); gy += 10
        gy += 3
    gy += 10
    sh.text(gx, gy, 'BASE PLAN CONTROL', TXT['header'], bold=True, spacing=1.0); gy += 16
    for ln in [f"ARCHITECT: {PROJECT['base']}, {PROJECT['base_date']}", f"DESIGNER: {PROJECT['designer_set']}",
               'HELIOS BASE: WALL COVERING SHEETS id 01 / id 07 OF THE DESIGNER SET, LAYERS STRIPPED TO WALLS, DOORS, WINDOWS,',
               'FIXTURES, CABINETS AND ROOM NAMES. FLOOR 1 BASE OFFSET (2.6, 22.7) PT RELATIVE TO THE FLOORING SHEET, CORRECTED.',
               'ANY NEW ARCHITECTURAL ISSUE REPLACES THE BASE ON EVERY SHEET. CHANGED ROOMS ARE CLOUDED AT THE NEXT ISSUE.']:
        sh.text(gx, gy, ln, 7.0, MID); gy += 10
    gy += 12
    sh.text(gx, gy, 'COORDINATION LOG', TXT['header'], bold=True, spacing=1.0); gy += 16
    for ln in ['11.01.26  FLOOR 1 WALL SHEET OFFSET VS FLOORING SHEET FOUND AND CORRECTED (2.6, 22.7 PT).',
               '11.01.26  WALL CODES WD-01 / ST-01 ON THE DESIGNER WALL SHEET RENAMED WP-01 / WS-01 (CLASH WITH FLOOR CODES).',
               '11.01.26  FLOOR 1 STAIR RESTORED ON THE FLOORING PLAN. NO BORDER AT THE MASTER TV UNIT.',
               '11.01.26  CEILING HEIGHTS, DOOR HEADS AND WINDOW SILLS ASSUMED, MARKED VERIFY ON ELEVATIONS.',
               '11.01.26  FLOOR 1 FURNITURE: NONE IN THE DESIGNER SET. ID-601 CARRIES FIXED ELEMENTS ONLY.']:
        sh.text(gx, gy, ln, 7.0, MID); gy += 10
    return sh

def cloud(sh, rect, delta, r=4.0):
    """Revision cloud around a rect with a numbered delta at the top-right."""
    x0, y0, x1, y1 = rect
    import math
    pts = []
    per = 2 * (x1 - x0) + 2 * (y1 - y0); n = max(8, int(per / (r * 1.6)))
    def at(t):
        d = t * per
        if d < (x1 - x0): return (x0 + d, y0)
        d -= (x1 - x0)
        if d < (y1 - y0): return (x1, y0 + d)
        d -= (y1 - y0)
        if d < (x1 - x0): return (x1 - d, y1)
        d -= (x1 - x0); return (x0, y1 - d)
    prev = at(0)
    for i in range(1, n + 1):
        cur = at(i / n)
        mx, my = (prev[0] + cur[0]) / 2, (prev[1] + cur[1]) / 2
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vx, vy = mx - cx, my - cy; L = math.hypot(vx, vy) or 1
        ctrl = fitz.Point(mx + vx / L * r * 1.4, my + vy / L * r * 1.4)
        sh.p.draw_bezier(fitz.Point(prev), ctrl, ctrl, fitz.Point(cur), color=INK, width=0.5)
        prev = cur
    tx, ty = x1 + 2, y0 - 2
    sh.p.draw_polyline([fitz.Point(tx, ty + 7), fitz.Point(tx + 8, ty + 7), fitz.Point(tx + 4, ty)], color=INK, width=0.5, fill=(1, 1, 1), closePath=True)
    sh.text(tx + 4, ty + 6.2, str(delta), 4.6, INK, align='c')

# ---------------------------------------------------------------- schedules
def schedules_sheet(doc):
    import build_elev as BE
    from idd_electrical import FIXTURES, DEVICES
    class C: ROWS_F1 = rows_from('compose.py', 'ROWS_F1'); ROWS_F2 = rows_from('compose.py', 'ROWS_F2')
    class CW: ROWS_F1 = rows_from('compose_wf.py', 'ROWS_F1'); ROWS_F2 = rows_from('compose_wf.py', 'ROWS_F2')
    sh = Sheet(doc)
    sh.frame('SCHEDULES', '', ['FINISH, LIGHTING &', 'DEVICE SCHEDULES'], 'ID-001', legend_rule=False)
    x, y = FR.x0 + 20, HDR_Y + 30
    # material schedule: floor codes then wall codes, merged across floors
    mats = collections.OrderedDict()
    for rows in (C.ROWS_F1, C.ROWS_F2, CW.ROWS_F1, CW.ROWS_F2):
        for code, title, lines in rows:
            if code not in mats: mats[code] = (title, list(lines))
            else:
                t0, l0 = mats[code]
                for ln in lines:
                    if not any(ln.startswith(x) or x.startswith(ln) for x in l0): l0.append(ln)
                if title != t0 and 'STAIR LANDING' in title: mats[code] = ('MARBLE - STAIR LANDINGS, FLOORS 1 & 2', l0)
    mats = collections.OrderedDict(sorted(mats.items(), key=lambda kv: (['WD', 'SL', 'TL', 'ST', 'PT', 'CM', 'WS', 'WP', 'WT'].index(kv[0][:2]), kv[0])))
    sh.text(x, y, 'MATERIAL SCHEDULE', TXT['header'], bold=True, spacing=1.0); y += 8
    cols = [x, x + 50, x + 290, x + 600, x + 680]
    hdr = ['CODE', 'MATERIAL', 'DESCRIPTION / LOCATION', 'CSI', 'SHEETS']
    y += 12; sh.line((x, y - 9), (x + 740, y - 9), 0.5)
    for cx, h in zip(cols, hdr): sh.text(cx, y, h, 6.8, MID, spacing=0.8)
    y += 4; sh.line((x, y), (x + 740, y), 0.5); y += 11
    csi = {'WD': '09 64 00', 'TL': '09 30 00', 'ST': '09 30 00', 'SL': '09 30 00', 'PT': '09 91 23', 'CM': '06 46 00', 'WS': '09 75 00', 'WP': '09 72 00', 'WT': '09 30 00'}
    ix = json.load(open('elev_index.json'))
    def sheets_of(*rooms, wall=None):
        nos = sorted({v['sheet'] for v in ix if v['room'] in rooms and (wall is None or v['wall'] == wall)})
        return ', '.join(n if i == 0 else n[3:] for i, n in enumerate(nos))
    where = {'WD-01': 'ID-101, 102', 'WD-02': 'ID-101, 102', 'SL-01': 'ID-101', 'TL-01': 'ID-101', 'TL-02': 'ID-101, 102', 'TL-03': 'ID-102', 'TL-04': 'ID-101', 'ST-01': 'ID-101, 102', 'ST-02': 'ID-101',
             'PT-01': 'ID-201, 202, 3XX, 7XX', 'PT-02': 'ID-201, 202, 7XX', 'PT-03': 'ID-201, ' + sheets_of('POWDER ROOM')[3:], 'CM-01': 'ID-201, 202, 301, 302, 7XX',
             'WS-01': 'ID-201, ' + sheets_of('GREAT ROOM', wall='E')[3:], 'WP-01': 'ID-201, ' + sheets_of('GREAT ROOM', wall='E')[3:], 'WP-02': 'ID-202, ' + sheets_of('MASTER SUITE', wall='E2')[3:],
             'WT-01': 'ID-201, 202, ' + sheets_of('GUEST BATH', 'BATH 2', 'BATH 3')[3:], 'WT-02': 'ID-202, ' + sheets_of('MASTER BATHROOM')[3:]}
    for code, (title, lines) in mats.items():
        sh.text(cols[0], y, code, 7.5, bold=True); sh.text(cols[1], y, title, 7.2)
        sh.text(cols[2], y, lines[0], 6.8, MID); sh.text(cols[3], y, csi[code[:2]], 6.8, MID); sh.text(cols[4], y, where.get(code, ''), 6.8, MID)
        for ln in lines[1:]:
            y += 9; sh.text(cols[2], y, ln, 6.8, MID)
        y += 12; sh.line((x, y - 8), (x + 740, y - 8), 0.3, LIGHT)
    # room finish schedule
    y += 14
    sh.text(x, y, 'ROOM FINISH SCHEDULE', TXT['header'], bold=True, spacing=1.0); y += 20
    cols = [x, x + 150, x + 262, x + 322, x + 382, x + 442, x + 502, x + 562, x + 600, x + 640]
    hdr = ['ROOM', 'FLOOR', 'BASE', 'N', 'E', 'S', 'W', 'CLG', 'CROWN', 'REMARKS']
    for cx, h in zip(cols, hdr): sh.text(cx, y, h, 6.8, MID, spacing=0.8)
    y += 4; sh.line((x, y), (x + 740, y), 0.5); y += 11
    FLOOR_FIN = {'KITCHEN & DINING AREA': 'WD-01 / WD-02 / SL-01', 'PANTRY': 'TL-01', 'GREAT ROOM': 'WD-01 / WD-02 / SL-01', 'PIANO ROOM': 'WD-01 / WD-02 / SL-01', 'FOYER': 'TL-01', 'POWDER ROOM': 'ST-02',
                 'GUEST BEDROOM': 'WD-01', 'GUEST BATH': 'TL-02', 'GUEST CLOSET': 'WD-01', 'LAUNDRY': 'TL-04', 'SERVICE AREA': 'TL-04', 'PET AREA': 'TL-04', 'OFFICE': 'WD-01',
                 'BEDROOM 3': 'WD-01', 'BATH 3': 'TL-02', 'BATH 2': 'TL-02', 'BEDROOM 2': 'WD-01', 'DEN / PLAYROOM': 'WD-01', 'W.I.C.': 'WD-01', 'MASTER BATHROOM': 'TL-03',
                 'MASTER SUITE': 'WD-01 / WD-02', 'HALL': 'WD-01 / WD-02', 'LINEN CLOSET': 'WD-01', 'HIDDEN SAFE': 'WD-01'}
    for floor in (1, 2):
        model = json.load(open(f'model_f{floor}.json'))
        sh.text(x, y, f'FLOOR {floor}', 7.2, bold=True); y += 11
        for r in model['rooms']:
            name = r['name']; kind = r['kind']
            paint = BE.ROOM_PAINT.get(name, BE.DEFAULT_PAINT[floor])
            sides = {}
            for w in r['walls']:
                side = w['side']
                spec = BE.wall_spec(floor, r, w, r['fixtures'])
                codes = [f['code'] for f in spec['finishes'] if f['code'] != 'CM-01']
                sides.setdefault(side, set()).update(codes or [paint])
            crown = 'NONE' if (kind in BE.NO_CROWN and name != 'W.I.C.') else 'CM-01'
            remarks = {'GREAT ROOM': 'DOUBLE HEIGHT, STONE & PANELING AT FIREPLACE WALL', 'MASTER SUITE': 'WP-02 HEADBOARD WALL', 'POWDER ROOM': 'PT-03 WALLS, ST-02 FLOOR',
                       'FOYER': 'PT-01 WALLS', 'HIDDEN SAFE': 'JIB DOOR, NO CASING', 'MASTER BATHROOM': 'WT-02 SHOWER & TUB ALCOVE', 'GUEST BATH': 'WT-01 TUB ALCOVE',
                       'BATH 2': 'WT-01 TUB ALCOVE', 'BATH 3': 'WT-01 TUB ALCOVE'}.get(name, '')
            vals = [name, FLOOR_FIN.get(name, 'T.B.C.'), 'WD BASE PT-01', ' / '.join(sorted(sides.get('N', {paint}))), ' / '.join(sorted(sides.get('E', {paint}))),
                    ' / '.join(sorted(sides.get('S', {paint}))), ' / '.join(sorted(sides.get('W', {paint}))), 'PT-01', crown, remarks]
            for cx, v in zip(cols, vals): sh.text(cx, y, v, 6.4 if cx != x else 6.8, INK if cx == x else MID)
            y += 10
        if floor == 1:
            extra = [('GUEST RM FOYER', 'WD-01', 'PT-02', 'CM-01', 'WEST ALCOVE OF THE GREAT ROOM'), ('AHU', 'TL-04', 'PT-02', 'NONE', 'MECHANICAL, NO CROWN'),
                     ('CLOSETS AT SERVICE AREA (2)', 'TL-04', 'PT-02', 'NONE', 'UNNAMED ON THE PLANS, BIFOLD DOORS')]
        else:
            extra = [('CLOSETS AT BEDROOMS 2 & 3', 'WD-01', 'PT-02', 'NONE', 'UNNAMED ON THE PLANS, NO CROWN'), ('AHU', 'WD-01', 'PT-02', 'NONE', 'MECHANICAL, NO CROWN'), ('WATER CLOSET AT MASTER BATHRM', 'TL-03', 'PT-02', 'CM-01', 'UNNAMED ON THE PLANS')]
        for nm, fl, pt, cr, rem in extra:
            vals = [nm, fl, 'WD BASE PT-01', pt, pt, pt, pt, 'PT-01', cr, rem]
            for cx, v in enumerate(vals): sh.text(cols[cx], y, v, 6.4 if cx else 6.8, MID if cx else INK)
            y += 10
        y += 4
    # lighting schedule and device counts, right column
    rx, ry = x + 770, HDR_Y + 30
    sh.text(rx, ry, 'LIGHTING SCHEDULE', TXT['header'], bold=True, spacing=1.0); ry += 20
    counts = {f: collections.Counter(o['type'] for o in json.load(open(f'electrical_f{f}.json'))['lights']) for f in (1, 2)}
    cols = [rx, rx + 36, rx + 300, rx + 384, rx + 420, rx + 456]
    for cx, h in zip(cols, ['TYPE', 'DESCRIPTION', 'MOUNT', 'FL 1', 'FL 2', 'TOTAL']): sh.text(cx, ry, h, 6.8, MID, spacing=0.8)
    ry += 4; sh.line((rx, ry), (rx + 520, ry), 0.5); ry += 11
    for code, (fam, desc, mount) in FIXTURES.items():
        n1, n2 = counts[1][code], counts[2][code]
        if code == 'UC':
            n1 = sum(round(o.get('len_in', 0) / 12) for o in json.load(open('electrical_f1.json'))['lights'] if o['type'] == 'UC'); n2 = 0; desc += ' (LF)'
        sh.text(cols[0], ry, code, 7.2, bold=True); sh.text(cols[1], ry, desc[:62], 6.2, MID); sh.text(cols[2], ry, mount[:24], 5.6, MID)
        sh.text(cols[3], ry, str(n1), 6.8); sh.text(cols[4], ry, str(n2), 6.8); sh.text(cols[5], ry, str(n1 + n2), 6.8, bold=True); ry += 11
    ry += 14
    sh.text(rx, ry, 'DEVICE COUNTS (POWER & DATA)', TXT['header'], bold=True, spacing=1.0); ry += 20
    pc = {f: collections.Counter(o['type'] for o in json.load(open(f'electrical_f{f}.json'))['power']) for f in (1, 2)}
    sc = {f: collections.Counter(o['type'] for o in json.load(open(f'electrical_f{f}.json'))['switches']) for f in (1, 2)}
    for cx, h in zip(cols, ['TYPE', 'DESCRIPTION', '', 'FL 1', 'FL 2', 'TOTAL']): sh.text(cx, ry, h, 6.8, MID, spacing=0.8)
    ry += 4; sh.line((rx, ry), (rx + 520, ry), 0.5); ry += 11
    for code, desc in DEVICES.items():
        n1 = pc[1][code] + sc[1][code]; n2 = pc[2][code] + sc[2][code]
        sh.text(cols[0], ry, code, 7.2, bold=True); sh.text(cols[1], ry, desc, 6.6, MID)
        sh.text(cols[3], ry, str(n1), 6.8); sh.text(cols[4], ry, str(n2), 6.8); sh.text(cols[5], ry, str(n1 + n2), 6.8, bold=True); ry += 11
    ry += 14
    for ln in ['COUNTS ARE FROM THE RULE-BASED LAYOUTS ON ID-30X, 40X AND 50X AND ARE FOR PRICING. THE ELECTRICAL',
               'ENGINEER OF RECORD SETS FINAL COUNTS. ALLOWANCES FOR OWNER-SELECTED FIXTURES (P1, C1, S1, S2, F1) TO BE',
               'CARRIED IN THE BID AS LINE ITEMS. SEE THE TAKEOFF WORKBOOK FOR AREAS AND LENGTHS BY FINISH.']:
        sh.text(rx, ry, ln, 6.8, MID); ry += 10
    return sh

def build():
    doc = fitz.open()
    cover_sheet(doc); schedules_sheet(doc)
    doc.set_metadata({'title': 'Casa Grove - Cover and Schedules', 'author': 'Helios Development', 'subject': 'HD102 Cover Sheet and Schedules', 'creator': 'Helios Development', 'producer': 'Helios Development'})
    fix_soft_hyphen(doc); path = '/home/claude/flrwork/261101.HD102.CoverSchedules.pdf'; doc.save(path, garbage=3, deflate=True); print('saved', path)

if __name__ == '__main__':
    build()
