"""RCP (ID-301/302), lighting and switching (ID-401/402), power and data (ID-501/502) and furniture (ID-601/602) sheets
for Casa Grove, drawn over the neutral base plans from the room model and the rule-based electrical layouts.
Each sheet shows only its own content (sheet purity): the base carries walls, doors, windows, fixtures and room names; nothing else."""
import json, math, pymupdf as fitz
from idd_sheet import Sheet, FR, TB_X, HDR_Y, W, H, fix_soft_hyphen, FREG
from idd_std import LW, TXT, INK, MID, LIGHT, HEIGHTS
from idd_electrical import FIXTURES, DEVICES
import idd_electrical as EL

BASE_CLEAN = '/home/claude/flrwork/261101.3350THOMAS.Base-clean.pdf'
BASE_KEY = '/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'   # FOR REV 1 (10.23.26) base, same display space; room key plans and ID-101/102/201/202 use it
BASE_FURN = '/home/claude/flrwork/261101.3350THOMAS.Base-furn.pdf'
SHIFT = {1: (2.6, 22.7), 2: (0.0, 0.0)}
LG_X0, LG_X1 = 790.0, 1300.0
PLAN_X1 = 740.0
OFF = (20.0, 4.0)       # model -> sheet
DARK = (0.251, 0.251, 0.251)

def S(x, y): return x + OFF[0], y + OFF[1]

def place_base(sh, doc_out, base, floor):
    src = fitz.open(base); pno = floor - 1; sp = src[pno]
    dx, dy = SHIFT[floor]
    clip_disp = fitz.Rect(20 + dx, 72 + dy, 715 + dx, 1160 + dy)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    target = fitz.Rect(20 + 20, 72 + 4, 715 + 20, 1160 + 4)
    sh.p.show_pdf_page(target, src, pno, clip=u, rotate=90)
    xref = sh.p.get_contents()[0]
    st = doc_out.xref_stream(xref).decode('latin1')
    assert 'Do' in st and st.count('Do') == 1, st
    t = target
    clipop = f'{t.x0:.2f} {H - t.y1:.2f} {t.width:.2f} {t.height:.2f} re W n '
    st = st.replace('q ', 'q ' + clipop, 1)
    doc_out.update_stream(xref, st.encode('latin1'))
    return target

# ---------------------------------------------------------------- symbols (all in sheet coordinates)
def sym_recessed(sh, x, y, wet=False, r=4.2):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.6, fill=(1, 1, 1))
    if wet: sh.p.draw_circle(fitz.Point(x, y), r * 0.55, color=INK, width=0.5)
def sym_pendant(sh, x, y, r=4.2):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.6, fill=(1, 1, 1))
    sh.p.draw_circle(fitz.Point(x, y), r * 0.35, color=INK, width=0.5, fill=INK)
def sym_chandelier(sh, x, y, r=6.5):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.7, fill=(1, 1, 1))
    for a in range(0, 360, 45):
        t = math.radians(a); sh.line((x + r * 0.45 * math.cos(t), y + r * 0.45 * math.sin(t)), (x + r * math.cos(t), y + r * math.sin(t)), 0.4, INK)
def sym_sconce(sh, x, y, r=3.2):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.6, fill=(1, 1, 1)); sh.line((x - r, y), (x + r, y), 0.6, INK)
def sym_surface(sh, x, y, r=4.2):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.6, fill=(1, 1, 1))
    sh.line((x - r * 0.7, y - r * 0.7), (x + r * 0.7, y + r * 0.7), 0.5, INK); sh.line((x - r * 0.7, y + r * 0.7), (x + r * 0.7, y - r * 0.7), 0.5, INK)
def sym_fan(sh, x, y, r=7.0):
    sh.p.draw_circle(fitz.Point(x, y), r * 0.3, color=INK, width=0.6, fill=(1, 1, 1))
    for a in (0, 90, 180, 270):
        t = math.radians(a)
        sh.p.draw_rect(fitz.Rect(-r, -1.6, -r * 0.3, 1.6) * fitz.Matrix(math.cos(t), math.sin(t), -math.sin(t), math.cos(t), x, y) if False else fitz.Rect(0, 0, 0, 0), width=0)
        sh.line((x + r * 0.3 * math.cos(t), y + r * 0.3 * math.sin(t)), (x + r * math.cos(t), y + r * math.sin(t)), 2.2, INK)
def sym_strip(sh, x, y, len_pt, horiz):
    if horiz: sh.p.draw_line(fitz.Point(x - len_pt / 2, y), fitz.Point(x + len_pt / 2, y), color=INK, width=1.2, dashes='[2 1.5] 0')
    else: sh.p.draw_line(fitz.Point(x, y - len_pt / 2), fitz.Point(x, y + len_pt / 2), color=INK, width=1.2, dashes='[2 1.5] 0')
def sym_switch(sh, x, y, label):
    sh.text(x, y + 2.6, 'S', 7.5, INK, align='c', bold=True)
    sh.line((x, y - 4.6), (x, y + 4.0), 0.5, INK)
    if label: sh.text(x + 4.2, y + 4.2, label, 4.6, INK)
def sym_receptacle(sh, x, y, kind, r=3.4):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.6, fill=(1, 1, 1))
    sh.line((x - r - 2.5, y), (x + r + 2.5, y), 0.6, INK)
    if kind == 'GFI': sh.text(x, y - r - 1.2, 'GFI', 3.8, INK, align='c')
    if kind == 'USB': sh.text(x, y - r - 1.2, 'USB', 3.8, INK, align='c')
def sym_data(sh, x, y, r=3.6):
    sh.p.draw_polyline([fitz.Point(x - r, y + r * 0.8), fitz.Point(x + r, y + r * 0.8), fitz.Point(x, y - r), fitz.Point(x - r, y + r * 0.8)], color=INK, width=0.6, fill=(1, 1, 1))
def sym_tv(sh, x, y):
    sh.rect((x - 6, y - 4, x + 6, y + 4), 0.6, INK, fill=(1, 1, 1)); sh.text(x, y + 2, 'TV', 4.6, INK, align='c')
def sym_floor_rec(sh, x, y, r=4.0):
    sh.p.draw_circle(fitz.Point(x, y), r, color=INK, width=0.6, fill=(1, 1, 1)); sh.text(x, y + 1.8, 'F', 4.6, INK, align='c')

def nudge(sh, x, y, side, words, r=6):
    """Slide a wall-mounted symbol along its wall until it clears the base text."""
    ux, uy = (1, 0) if side in ('N', 'S') else (0, 1)
    for step in (0, 10, -10, 20, -20, 30, -30):
        tx, ty = x + ux * step, y + uy * step
        if not any(fitz.Rect(tx - r, ty - r, tx + r, ty + r).intersects(w) for w in words): return tx, ty
    return x, y

def draw_light(sh, o, wall_dir=None):
    x, y = S(o['x'], o['y']); t = o['type']
    if t == 'R1': sym_recessed(sh, x, y)
    elif t == 'R2': sym_recessed(sh, x, y, wet=True)
    elif t == 'P1': sym_pendant(sh, x, y)
    elif t == 'C1': sym_chandelier(sh, x, y)
    elif t in ('S1', 'S2'): sym_sconce(sh, x, y)
    elif t == 'SM': sym_surface(sh, x, y)
    elif t == 'F1': sym_fan(sh, x, y)
    elif t == 'UC': sym_strip(sh, x, y, o.get('len_in', 36) * 1.125, horiz=wall_dir in ('N', 'S'))

# ---------------------------------------------------------------- legends
def legend_block(sh, y, title, rows, sym_fn):
    sh.text(LG_X0, y, title, TXT['header'], bold=True, spacing=1.0); y += 18
    for code, desc in rows:
        sym_fn(sh, LG_X0 + 10, y - 3, code)
        sh.text(LG_X0 + 30, y, code, 8.5, bold=True); sh.text(LG_X0 + 62, y, desc, 7.6, MID); y += 14
    return y + 6

def notes_block(sh, y, title, notes):
    sh.text(LG_X0, y, title, TXT['header'], bold=True, spacing=1.0); y += 18
    for i, lines in enumerate(notes, 1):
        sh.text(LG_X0, y, f'{i}.', 7.6, MID)
        for ln in lines:
            sh.text(LG_X0 + 14, y, ln, 7.6, MID); y += 10.5
        y += 3
    return y

_PLANS = {}
def plan_text(floor):
    if floor not in _PLANS:
        import idd_model as M, build_model as B
        cfg = B.FLOORS[floor]; _PLANS[floor] = M.PlanPage(B.W, cfg['pno'], offset=cfg['offset']).text
    return _PLANS[floor]

LABEL_AT = {(2, 'HALL'): (316.0, 566.0)}     # rooms named by Helios on the base, not by the designer

def room_label_point(room, floor=None):
    if (floor, room['name']) in LABEL_AT: return S(*LABEL_AT[(floor, room['name'])])
    """Point under the room's name text (so added labels never sit on the name); falls back to the polygon's representative point."""
    from shapely.geometry import Polygon, Point
    poly = Polygon(room['poly_pt'])
    if floor is not None:
        boxes = [r for t, r, sz in plan_text(floor) if sz > 8.5 and (t.isupper() or t.isdigit() or t in ('/',)) and poly.contains(Point((r[0] + r[2]) / 2, (r[1] + r[3]) / 2))]
        if boxes:
            cx = sum((r[0] + r[2]) / 2 for r in boxes) / len(boxes); by = max(r[3] for r in boxes)
            return S(cx, by)
    p = poly.representative_point(); return S(p.x, p.y)

# ---------------------------------------------------------------- the sheets
def rcp_sheet(doc, floor, model, elec):
    sh = Sheet(doc); place_base(sh, doc, BASE_CLEAN, floor)
    # ceiling heights, ceiling finish and crown per room
    for r in model['rooms']:
        if r['name'] == 'HIDDEN SAFE': continue
        x, y = room_label_point(r, floor)
        words = [fitz.Rect(w[:4]) for w in sh.p.get_text('words')]
        for _ in range(6):   # drop the label until it clears every word on the base
            box_ = fitz.Rect(x - 30, y + 4, x + 30, y + 34)
            if not any(box_.intersects(w) for w in words): break
            y += 8
        h = r['ceiling_in']; txt = f"CLG {int(h // 12)}'-{int(h % 12)}\""
        if r['name'] == 'GREAT ROOM': txt = 'OPEN TO ABOVE, CLG 20\'-10"'
        sh.text(x, y + 13, txt, 6.8, DARK, align='c')
        crowned = not (r['kind'] == 'closet' and r['name'] != 'W.I.C.') and r['name'] != 'HIDDEN SAFE'
        sh.tag_stack(x, y + 27, ['PT-01'] + (['CM-01'] if crowned else []), lead=0, sides='')
        # crown: dashed line 6 pt inside the room outline
        if crowned:
            from shapely.geometry import Polygon
            inner = Polygon(r['poly_pt']).simplify(6.0).buffer(-5.0, join_style=2).simplify(1.0)
            if not inner.is_empty and inner.geom_type == 'Polygon':
                pts = [S(px, py) for px, py in inner.exterior.coords]
                sh.polyline(pts, 0.7, DARK, dashes='[4 2] 0')
    for o in elec['lights']:
        if o['type'] in ('S1', 'S2'): continue          # wall fixtures belong to the lighting plan, not the ceiling
        draw_light(sh, o, o.get('wall'))
    sh.frame(f'REFLECTED CEILING PLAN - FLOOR {floor}', 'SCALE: 3/16" TO 1\'-0"', ['REFLECTED CEILING PLAN', f'FLOOR {floor}'], f'ID-30{floor}', legend_header='CEILING LEGEND')
    y = HDR_Y + 24
    def symf(sh, x, y, code):
        {'R1': lambda: sym_recessed(sh, x, y), 'R2': lambda: sym_recessed(sh, x, y, True), 'P1': lambda: sym_pendant(sh, x, y), 'C1': lambda: sym_chandelier(sh, x, y, 5),
         'SM': lambda: sym_surface(sh, x, y), 'F1': lambda: sym_fan(sh, x, y, 5.5), 'UC': lambda: sym_strip(sh, x, y, 16, True)}[code]()
    rows = [(c, FIXTURES[c][1]) for c in ('R1', 'R2', 'P1', 'C1', 'SM', 'F1', 'UC')]
    y = legend_block(sh, y, 'CEILING FIXTURES (SEE LIGHTING SCHEDULE, ID-001)', rows, symf)
    sh.tag_stack(LG_X0 + 10, y + 4, ['PT-01', 'CM-01'], lead=0, sides=''); sh.text(LG_X0 + 30, y + 2, 'CEILING FINISH OVER CROWN. PT-01 FLAT ON ALL CEILINGS. CM-01 WHERE SHOWN DASHED.', 7.6, MID)
    y += 22
    sh.p.draw_line(fitz.Point(LG_X0, y + 3), fitz.Point(LG_X0 + 24, y + 3), color=DARK, width=0.7, dashes='[4 2] 0')
    sh.text(LG_X0 + 30, y + 6, 'CROWN MOLDING CM-01, CONTINUOUS AROUND THE ROOM. NONE IN CLOSETS AND MECHANICAL.', 7.6, MID); y += 24
    notes = [['CEILING HEIGHTS ARE TAKEN FROM THE YL DESIGNS ELEVATIONS (FLOOR 1) AND ASSUMED FOR FLOOR 2.', 'VERIFY EVERY HEIGHT AGAINST THE ARCHITECTURAL SET BEFORE PRICING CROWN AND PANELING.'],
             ['GREAT ROOM IS OPEN TO ABOVE (DOUBLE HEIGHT). NO SOFFITS OR TRAYS ARE SHOWN ON THE ARCHITECTURAL', 'BASE. ANY SOFFIT, BEAM OR TRAY IS BY THE ARCHITECT AND IS TO BE ADDED HERE WHEN ISSUED.'],
             ['FIXTURE LOCATIONS ARE SET BY RULE (GRIDS 4\'-6" TO 5\'-0" O.C., 2\'-6" MIN. OFF WALLS, CENTERED ON TUBS', 'AND SHOWERS, PENDANTS CENTERED ON THE ISLAND). FINAL LOCATIONS TO BE COORDINATED WITH FRAMING,', 'HVAC AND SPRINKLERS. CENTER FIXTURES ON ROOM AXES AND ALIGN ROWS ROOM TO ROOM.'],
             ['CROWN CM-01 PROFILE PER TYPICAL DETAILS, SHEET ID-801. CROWN RUNS CONTINUOUS OVER DOOR HEADS', 'AND RETURNS INTO CLOSETS ONLY WHERE SHOWN.'],
             ['WALL SCONCES ARE ON THE LIGHTING PLAN (ID-40X), NOT ON THIS SHEET.'],
             ['NO DIMENSIONS ON THIS SHEET. SET-OUT POINTS: ROOM CENTERLINES. REFER TO THE ARCHITECTURAL SET.']]
    y = notes_block(sh, y + 6, 'GENERAL NOTES', notes)
    sh.scale_bar(FR.x0 + 24, FR.y1 - 22)
    return sh

def lighting_sheet(doc, floor, model, elec):
    sh = Sheet(doc); place_base(sh, doc, BASE_CLEAN, floor)
    for o in elec['lights']: draw_light(sh, o, o.get('wall'))
    # switches and a dashed switch leg to the nearest controlled fixture of the room
    words = [fitz.Rect(w[:4]) for w in sh.p.get_text('words')]
    for s in elec['switches']:
        x, y = S(s['x'], s['y']); x, y = nudge(sh, x, y, s.get('wall', 'N')[0], words)
        lab = {'S': '', 'S3': '3', 'SD': 'D', 'S3D': '3D'}[s['type']]
        sym_switch(sh, x, y, lab)
        cands = [o for o in elec['lights'] if o['room'] == s['room'] and o['type'] not in ('UC',)]
        if cands:
            o = min(cands, key=lambda o: (o['x'] - s['x']) ** 2 + (o['y'] - s['y']) ** 2)
            ox, oy = S(o['x'], o['y'])
            mx, my = (x + ox) / 2 + (oy - y) * 0.15, (y + oy) / 2 - (ox - x) * 0.15
            sh.p.draw_bezier(fitz.Point(x, y), fitz.Point(mx, my), fitz.Point(mx, my), fitz.Point(ox, oy), color=MID, width=0.4, dashes='[3 2] 0')
    sh.frame(f'LIGHTING & SWITCHING PLAN - FLOOR {floor}', 'SCALE: 3/16" TO 1\'-0"', ['LIGHTING & SWITCHING', f'PLAN - FLOOR {floor}'], f'ID-40{floor}', legend_header='LIGHTING LEGEND')
    y = HDR_Y + 24
    def symf(sh, x, y, code):
        {'R1': lambda: sym_recessed(sh, x, y), 'R2': lambda: sym_recessed(sh, x, y, True), 'P1': lambda: sym_pendant(sh, x, y), 'C1': lambda: sym_chandelier(sh, x, y, 5),
         'S1': lambda: sym_sconce(sh, x, y), 'S2': lambda: sym_sconce(sh, x, y), 'SM': lambda: sym_surface(sh, x, y), 'F1': lambda: sym_fan(sh, x, y, 5.5), 'UC': lambda: sym_strip(sh, x, y, 16, True),
         'S': lambda: sym_switch(sh, x, y, ''), 'S3': lambda: sym_switch(sh, x, y, '3'), 'SD': lambda: sym_switch(sh, x, y, 'D'), 'S3D': lambda: sym_switch(sh, x, y, '3D')}[code]()
    rows = [(c, FIXTURES[c][1]) for c in ('R1', 'R2', 'P1', 'C1', 'S1', 'S2', 'SM', 'F1', 'UC')]
    y = legend_block(sh, y, 'FIXTURES (SEE LIGHTING SCHEDULE, ID-001)', rows, symf)
    rows = [(c, DEVICES[c]) for c in ('S', 'S3', 'SD', 'S3D')]
    y = legend_block(sh, y, 'SWITCHES', rows, symf)
    sh.p.draw_line(fitz.Point(LG_X0, y + 3), fitz.Point(LG_X0 + 24, y + 3), color=MID, width=0.4, dashes='[3 2] 0')
    sh.text(LG_X0 + 30, y + 6, 'SWITCH LEG: SWITCH TO THE FIXTURE GROUP IT CONTROLS (DIAGRAMMATIC).', 7.6, MID); y += 24
    notes = [['SWITCHES AT THE LATCH SIDE OF EACH DOOR, 6" FROM THE CASING, CL 3\'-6" AFF. ROOMS WITH TWO OR MORE', 'ENTRIES GET THREE-WAY SWITCHING. DIMMERS IN ALL LIVING AND SLEEPING ROOMS.'],
             ['ALL LAMPS 2700K, 90 CRI MIN., DIMMABLE LED. ONE DIMMER SYSTEM THROUGHOUT (OWNER TO CONFIRM).'],
             ['FIXTURES: OWNER SELECTION FOR PENDANTS, CHANDELIERS AND SCONCES. ALLOWANCES PER THE', 'LIGHTING SCHEDULE ON ID-001. RECESSED TRIMS WHITE, FLANGELESS WHERE THE BUDGET ALLOWS.'],
             ['SCONCE MOUNTING HEIGHTS PER INTERIOR ELEVATIONS (ID-7XX). CENTER SCONCES ON MIRRORS AND BEDS.'],
             ['COORDINATE ALL LOCATIONS WITH THE ELECTRICAL ENGINEER OF RECORD. THIS SHEET SHOWS DESIGN INTENT', 'FOR PRICING. CIRCUITING, LOADS AND CODE COMPLIANCE ARE BY THE ENGINEER.'],
             ['NO DIMENSIONS ON THIS SHEET. SET-OUT FROM ROOM CENTERLINES AND DOOR CASINGS.']]
    y = notes_block(sh, y + 6, 'GENERAL NOTES', notes)
    sh.scale_bar(FR.x0 + 24, FR.y1 - 22)
    return sh

def power_sheet(doc, floor, model, elec):
    sh = Sheet(doc); place_base(sh, doc, BASE_CLEAN, floor)
    words = [fitz.Rect(w[:4]) for w in sh.p.get_text('words')]
    for o in elec['power']:
        x, y = S(o['x'], o['y']); t = o['type']
        if o.get('wall'): x, y = nudge(sh, x, y, o['wall'][0], words, 8)
        if t in ('REC', 'GFI', 'USB'): sym_receptacle(sh, x, y, t)
        elif t == 'DAT': sym_data(sh, x + 7, y)
        elif t == 'TV': sym_tv(sh, x, y - 8)
        elif t == 'FLR': sym_floor_rec(sh, x, y)
    sh.frame(f'POWER & DATA PLAN - FLOOR {floor}', 'SCALE: 3/16" TO 1\'-0"', ['POWER & DATA PLAN', f'FLOOR {floor}'], f'ID-50{floor}', legend_header='POWER & DATA LEGEND')
    y = HDR_Y + 24
    def symf(sh, x, y, code):
        {'REC': lambda: sym_receptacle(sh, x, y, 'REC'), 'GFI': lambda: sym_receptacle(sh, x, y, 'GFI'), 'USB': lambda: sym_receptacle(sh, x, y, 'USB'),
         'DAT': lambda: sym_data(sh, x, y), 'TV': lambda: sym_tv(sh, x, y), 'FLR': lambda: sym_floor_rec(sh, x, y)}[code]()
    rows = [(c, DEVICES[c]) for c in ('REC', 'GFI', 'USB', 'DAT', 'TV', 'FLR')]
    y = legend_block(sh, y, 'DEVICES', rows, symf)
    notes = [['RECEPTACLE SPACING PER NEC 210.52(A): NO POINT ALONG A WALL 2\'-0" OR LONGER IS MORE THAN 6\'-0"', 'FROM A RECEPTACLE. COUNTERS PER 210.52(C): NO POINT MORE THAN 2\'-0" FROM A RECEPTACLE.'],
             ['GFCI PROTECTION PER NEC 210.8 AT BATHROOMS, KITCHEN COUNTERS, LAUNDRY, GARAGE / CARPORT AND', 'WITHIN 6\'-0" OF ANY SINK. AFCI PER NEC 210.12 FOR ALL HABITABLE ROOMS (BY THE ENGINEER).'],
             ['MOUNTING: CL 15" AFF U.N.O. COUNTERS CL 3\'-6" AFF, HORIZONTAL IN BACKSPLASH TILE JOINTS WHERE', 'POSSIBLE. TV BOXES CL 3\'-6" AFF (LIVING) AND 4\'-2" AFF (BEDROOMS), VERIFY WITH FURNITURE.'],
             ['DEVICES AND PLATES: OWNER SELECTION. ON PAINTED WALLS PAINT PLATES TO MATCH. ON TILE AND STONE', 'USE SCREWLESS PLATES CENTERED ON THE TILE MODULE. NO DEVICES IN WOOD PANELING WP-01 / WP-02', 'EXCEPT WHERE SHOWN. LOCATE IN THE PANEL FIELD, NEVER ACROSS A STILE OR RAIL.'],
             ['KITCHEN: DEDICATED CIRCUITS FOR REFRIGERATOR, RANGE, DISHWASHER, DISPOSAL AND MICROWAVE PER', 'APPLIANCE SCHEDULE. ISLAND RECEPTACLES PER NEC 210.52(C)(2), BELOW COUNTER OR POP-UP, OWNER TO CONFIRM.'],
             ['DATA: CAT 6 HOME RUNS TO THE NETWORK PANEL (LOCATION BY OWNER). WIFI ACCESS POINTS ON THE CEILING,', 'ONE PER FLOOR MINIMUM, LOCATIONS BY THE LOW-VOLTAGE CONTRACTOR.'],
             ['THIS SHEET SHOWS DESIGN INTENT FOR PRICING AND COORDINATION. CIRCUITING AND CODE COMPLIANCE', 'ARE BY THE ELECTRICAL ENGINEER OF RECORD. NO DIMENSIONS ON THIS SHEET.']]
    y = notes_block(sh, y + 6, 'GENERAL NOTES', notes)
    sh.scale_bar(FR.x0 + 24, FR.y1 - 22)
    return sh

def furniture_sheet(doc, floor, model):
    sh = Sheet(doc); place_base(sh, doc, BASE_FURN, floor)
    sh.frame(f'FURNITURE PLAN - FLOOR {floor}', 'SCALE: 3/16" TO 1\'-0"', ['FURNITURE PLAN', f'FLOOR {floor}'], f'ID-60{floor}', legend_header='FURNITURE NOTES')
    y = HDR_Y + 24
    if floor == 1:
        notes = [['THE YL DESIGNS SET (YLD.068) CARRIES NO FURNITURE LAYOUT FOR FLOOR 1. THIS SHEET SHOWS THE FIXED', 'ELEMENTS ONLY (KITCHEN ISLAND, COUNTERS, FIREPLACE, STAIR). THE FLOOR 1 FURNITURE LAYOUT IS TO BE', 'DEVELOPED WITH THE OWNER AND ISSUED AS A REVISION TO THIS SHEET.'],
                 ['FLOOR RECEPTACLES AND TV LOCATIONS ON ID-501 ASSUME: SEATING GROUP CENTERED ON THE GREAT ROOM', 'FIREPLACE, DINING TABLE AT THE SOUTH SIDE OF THE KITCHEN, PIANO IN THE PIANO ROOM. CONFIRM BEFORE ROUGH-IN.'],
                 ['CLEARANCES TO HOLD: 36" MIN. CIRCULATION, 42" AT THE ISLAND ON ALL SIDES, 48" IN FRONT OF THE', 'REFRIGERATOR AND RANGE, 18" FROM SOFA TO COFFEE TABLE, 36" BEHIND DINING CHAIRS.']]
    else:
        notes = [['FURNITURE AND RUGS AS LAID OUT BY YL DESIGNS (SET YLD.068, SHEET id 07): MASTER SUITE AND TERRACES ONLY.', 'BEDROOMS 2 AND 3, THE DEN AND THE HALL HAVE NO LAYOUT YET AND ARE TO BE LAID OUT WITH THE OWNER.', 'PIECES SHOWN ARE FOR COORDINATION OF POWER, DATA AND LIGHTING. SPECIFICATIONS BY THE DESIGNER / OWNER.'],
                 ['BED CENTERED ON THE HEADBOARD WALL (WP-02 IN THE MASTER SUITE). NIGHTSTAND POWER PER ID-502.'],
                 ['CLEARANCES TO HOLD: 36" MIN. CIRCULATION, 30" EACH SIDE OF BEDS, 36" IN FRONT OF WARDROBES.'],
                 ['RUG SIZES: FRONT LEGS OF ALL SEATING ON THE RUG. BEDROOM RUGS EXTEND 24" MIN. BEYOND THE BED SIDES.']]
    y = notes_block(sh, y, 'NOTES', notes)
    sh.scale_bar(FR.x0 + 24, FR.y1 - 22)
    return sh

def build():
    out = {}
    for name, fn, base_needed in (('RCP', rcp_sheet, True), ('Lighting', lighting_sheet, True), ('PowerData', power_sheet, True), ('Furniture', furniture_sheet, False)):
        doc = fitz.open()
        for floor in (1, 2):
            model = json.load(open(f'model_f{floor}.json'))
            if base_needed:
                elec = json.load(open(f'electrical_f{floor}.json')); fn(doc, floor, model, elec)
            else:
                fn(doc, floor, model)
        path = f'/home/claude/flrwork/261101.HD102.{name}Plans.pdf'
        doc.set_metadata({'title': f'Casa Grove - {name} Plans', 'author': 'Helios Development', 'subject': f'HD102 {name} Plans - Floors 1 and 2', 'creator': 'Helios Development', 'producer': 'Helios Development'})
        fix_soft_hyphen(doc); doc.save(path, garbage=3, deflate=True); out[name] = path; print('saved', path)
    return out

if __name__ == '__main__':
    build()
