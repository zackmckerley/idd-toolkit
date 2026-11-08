"""Print set for review: a cover (ID-000) with the sheet index read from each sheet's title block and the open items, then the finish plans
and every designed room on FOR REV 1, bookmarked. Output: 261106.HD102.PrintSet.pdf"""
import re, sys
sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_std
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID
from build_kitchen import para_block, NOTE, NOTE_LH

OUT = '/home/claude/flrwork/261106.HD102.PrintSet.pdf'
ISSUE = '11.06.26'
GROUPS = [('FINISH PLANS', '261105.HD102.FinishPlans.pdf'), ('MASTER BATH', '261105.HD102.MasterBathPilot.pdf'),
          ('MASTER BEDROOM', '261105.HD102.MasterBedroomPilot.pdf'), ('BEDROOMS', '261106.HD102.Bedrooms.pdf'),
          ('SECONDARY BATHS', '261105.HD102.SecondaryBaths.pdf'), ('KITCHEN, DINING AND PANTRY', '261105.HD102.KitchenPilot.pdf'),
          ('LIVING ROOM', '261105.HD102.LivingRoomPilot.pdf'), ('MUDROOM', '261105.HD102.MudroomPilot.pdf'),
          ('ENTRY AND POWDER ROOM', '261105.HD102.EntryPowderPilot.pdf')]
OPEN = [
    (True, 'OPEN ITEMS FOR THE OWNER'),
    '1. POWDER ROOM WALLCOVERING WC-02: SAMPLES ON THE WALL BEFORE ORDERING. THE TRIM AND CEILING IN PT-03 LACQUER IS A HELIOS PROPOSAL. THE VANITY FINISH, '
    'STONE, FAUCET AND BAR LIGHT.',
    '2. ENTRY MIRROR: A SOURCED VINTAGE FRAMED MIRROR UP TO 3\'-6" WIDE, TOP AT 8\'-5", ON THE WALL THE OWNER CALLED EAST (EAST BY FOR\'S NORTH ARROW, WEST IN THIS SET).',
    '3. MUDROOM: THE LOCKERS STAY OPEN FOR NOW, SO THE DOGS STAY BEHIND DOOR 15 WHEN NOBODY IS HOME. DOOR 12 AND THE EAST LEAF OF CLOSET 13 CANNOT STAND OPEN '
    'TOGETHER. MILLWORK COLOR, BENCH QUARTZ, A PET DOOR IN 02, A FLOOR DRAIN AND WATER BOWLS IN THE DOG ROOM, THE W/D MODEL.',
    '4. MASTER BATH: A 58" TUB (DRAWN, FOR HAS 60"), THE TUB FILLER, FLOOR-MOUNTED (FOR\'S NOTE) OR WALL-MOUNTED (DRAWN), THE HAND TOWELS ON 18" BARS ON THE VANITY FRONTS (THE WALL BESIDE THE EAST VANITY IS DOOR 19\'S POCKET). GUEST BATH: THE SHOWER VALVE AT THE ENTRY END, THE SWITCHES IN THE GUEST BEDROOM, A HAND SHOWER.',
    '5. LIVING ROOM: THE FIREPLACE WALL PICK FROM THE STUDY (ISSUED SEPARATELY), THE FIREPLACE UNIT, TV SIZE, THE STEEL GUARD COLOR. MASTER BEDROOM: ONE PICTURE LIGHT OVER THE TV IN PLACE OF SCONCES (DOOR 19\'S POCKET).',
    '6. KITCHEN AND PANTRY: FOR\'S ISLAND KEPT, MOVED 4-5/8" EAST FOR A 42" RANGE AISLE, THE OVENS STAY UNDER THE 48" RANGE, THE PANTRY DISHWASHER A11 SWAPPED WITH THE 24" DRAWERS TO CLEAR THE SINK CORNER, SO THE COFFEE STATION SITS OVER THE DISHWASHER. COLORS, VENEER, STONE, HARDWARE, RANGE AND HOOD.', '',
    (True, 'OPEN ITEMS FOR FOR ARCHITECTURE'),
    'EVERY KEY PLAN LISTS ITS CHANGES FROM FOR\'S PLAN. THE LARGEST: THE GALLERY GUARD IN PAINTED STEEL IN PLACE OF FOR\'S GLASS RAILING, FOR\'S SEPARATE BUILT-IN '
    'OVEN DROPPED (OVENS UNDER THE RANGE), THE POWDER ROOM EAST WALL FURRED OUT ON 2x4 FOR THE WALL FAUCET AND DRAIN, THE OFFICE DOOR 11 CENTERED ON ITS WALL, '
    'THE MASTER BATH WATER CLOSET DOOR CENTERED, THE MASTER CLOSET PAIR OF SWING DOORS IN PLACE OF THE POCKET, THE COAT CLOSET 13 PAIR OF SWING DOORS. '
    'QUESTIONS: THE STAIR HEADROOM AT THE LIVING ROOM LANDING (A 10\'-10" CEILING OR THE CLOSET HEADER MOVED), THE 18" INSET RECTANGLE OVER THE LIVING ROOM '
    'SOUTH END (TRAY OR SOFFIT), THE UNLABELLED BOXED X SYMBOLS, THE CHASE SYMBOL IN THE DOG ROOM, THE MASTER BEDROOM NICHE HEIGHTS, THE KITCHEN ISLAND MOVE AND THE PENDANTS RECENTERED OVER IT. FOR\'S NORTH ARROW '
    'READS NORTH DOWN THE SHEET: THE SET NAMES WALLS WITH PLAN NORTH UP. HEIGHTS ASSUMED EVERYWHERE (VERIFY): CEILINGS 10\'-0", DOOR HEADS 8\'-0".', '',
    (True, 'NOT IN THIS SET'),
    'THE RCP, LIGHTING, POWER AND FURNITURE PLANS AND THE TAKEOFF ARE STILL ON THE DESIGNER\'S BASE AND ARE NOT REISSUED ON FOR REV 1. THE DESIGN STUDIES '
    '(OPTION SHEETS) ARE ISSUED SEPARATELY. THE SET IS FOR PRICING AND COORDINATION, NOT FOR PERMIT.']

def sheet_info(page):
    num, title, hdr, dates = None, '', [], []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                t = sp['text'].strip()
                if sp['bbox'][0] > TB_X and re.fullmatch(r'\d\d\.\d\d\.\d\d', t): dates.append(t)
                if re.fullmatch(r'ID-\d{3}[A-Z]?', t) and sp['size'] > 20: num = t
                if sp['bbox'][1] < HDR_Y and sp['bbox'][0] < TB_X - 400 and sp['size'] >= 9: hdr.append((sp['bbox'][0], t))
    title = ' '.join(t for _, t in sorted(hdr)) if hdr else ''
    title = re.sub(r'(,)? ?(SCALE:.*|AS NOTED.*)$', '', title).strip()
    title = re.sub(r' (FLOOR|WALL) FINISH SCHEDULE$', '', title).strip().rstrip(',')
    last = max(dates, key=lambda d: (d[6:8], d[0:2], d[3:5])) if dates else ''      # the latest revision row in the title block
    return num, title, last

def build():
    idd_std.PROJECT['date'] = ISSUE
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    srcs = [(g, fitz.open('/home/claude/flrwork/' + fn), fn) for g, fn in GROUPS]
    rows = []
    for g, d, fn in srcs:
        for p in d:
            n, t, iss = sheet_info(p); rows.append((n or '?', t, g, iss))
    doc = fitz.open()
    sh = Sheet(doc); sh.frame('SHEET INDEX AND OPEN ITEMS', 'PRINT SET FOR REVIEW', ['SHEET INDEX', 'OPEN ITEMS'], 'ID-000', revisions=(('0', ISSUE, 'PRINT SET FOR REVIEW'),), legend_rule=False)
    x0, y = FR.x0 + 20, HDR_Y + 34
    sh.text(x0, y, 'SHEET', 7.0, INK); sh.text(x0 + 60, y, 'TITLE', 7.0, INK); sh.text(x0 + 420, y, 'LAST REVISED', 7.0, INK); y += 4
    sh.line((x0, y), (x0 + 470, y), 0.5, INK); y += 11
    last = None
    for n, t, g, iss in rows:
        if g != last:
            y += 3; sh.text(x0, y, g, 6.5, INK); y += 10; last = g
        sh.text(x0, y, n, 6.0, MID); sh.text(x0 + 60, y, t[:80], 6.0, MID); sh.text(x0 + 420, y, iss, 6.0, MID); y += 9
    assert y < FR.y1 - 10, ('index runs off the sheet', y)
    para_block(sh, x0 + 520, HDR_Y + 34, OPEN, TB_X - 20 - (x0 + 520))
    fix_soft_hyphen(doc)
    toc = [[1, 'ID-000 SHEET INDEX AND OPEN ITEMS', 1]]
    for g, d, fn in srcs:
        start = len(doc) + 1; doc.insert_pdf(d); toc.append([1, g, start])
        for i in range(len(d)):
            n, t, _ = sheet_info(doc[start - 1 + i]); toc.append([2, '%s %s' % (n, t), start + i])
    doc.set_toc(toc)
    doc.set_metadata({'title': 'Casa Grove interior design print set for review, 11.06.26', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, len(doc), 'pages')
    for r in rows: print(r)

if __name__ == '__main__':
    build()
