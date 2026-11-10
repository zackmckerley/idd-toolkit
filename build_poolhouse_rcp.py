"""ID-406 POOL HOUSE RCP AND LIGHTING, coordinated with FOR Rev 1 A-207 (ceilings) and E-300 (pool house lighting and switching).

Drawn on our pool house plan (build_poolhouse.py PLAN block, inches from the storage room's interior NW corner) at 1/2", RCP above, lighting below.
FOR's E-300 positions are taken at 1.5 pt per inch from the storage room's interior NW corner (E-300 display 1320.1, 206.5; the core walls
check to 0.3 pt). Called from build_rcp.py, which writes the sheet into 261109.HD102.RCP-Lighting.pdf after ID-132."""
import sys, math
sys.path[:0] = ['/home/claude/flrwork', '/home/claude/flrwork/rev1']
import pymupdf as fitz
import build_poolhouse as PH
from build_poolhouse import (Plan, draw_plan, door_tag, scale_bar, north, para_block, IX, IY, W_EXT, ST_E, CW1, CE0, CE1, NI_X, NI_Y,
                             VAN_X, VAN_Y, BS_Y, D11_Y, D05_X, MS_WIN, OF_WIN, MS1, MS2, SH_X, SH_Y)
from idd_sheet import Sheet, FR, TB_X, HDR_Y, FREG
from idd_std import INK, MID, LIGHT

K = 3.0                                   # 1/2" = 1'-0"
GREY = (0.62, 0.62, 0.62); DARKG = (0.35, 0.35, 0.35); WHITE = (1, 1, 1)
BAND = 10.0                               # 8'-7" band, 10" wide at the walls (A-207)
STORAGE = (0.0, 0.0, ST_E, IY); OFFICE = (CE1, 0.0, IX, IY)

# FOR's E-300 positions (inches); ours where noted
CH = [(60.2, 57.0), (276.3, 57.8)]                       # chandelier J-boxes, storage and office (FOR), CH1
L1 = [(177.1, 51.9), (167.0, 94.5)]                      # bath, vestibule (FOR)
L2 = [(177.1, 17.0)]                                     # shower (FOR tags it L1 (W); A-207a's wet type is L2)
SD = [(88.2, 67.4), (251.2, 73.8)]                       # smoke (FOR)
SDCO = [(176.4, 98.9)]                                   # smoke / CO combination, vestibule (FOR)
EF = (197.0, 52.0)                                       # bath exhaust over the toilet (FOR)
WP = [(126.1, 132.2), (207.9, 132.2)]                    # exterior wall lights flanking door 05 (FOR)
LM1 = (CW1, (VAN_Y[0] + VAN_Y[1]) / 2, 24.0)              # ours: backlit LED mirror 24" x 48" over the vanity, on the core west wall (4/ID-404), as the guest bath
# switches at our elevation locations (FOR's gangs at E-300): (plan pt of the device, offset into the room, label, elevation)
SW = [((ST_E, 72.5), (-2.6, 0), 'S', 'l'), ((CE1 + 4.0, IY), (0, -2.6), 'D', 'l'),         # storage at the latch of door 11 (2/ID-402); office at the latch, south wall (3/ID-403)
      ((146.0, BS_Y[0]), (0, -2.6), 'S2', 'u'), ((192.8, IY), (0, -2.6), 'S', 'r')]        # bath, two devices: mirror and EF (3/ID-404); vestibule at door 05 (2/ID-405)
FOR_SW = [(116.2, 71.5), (191.5, 65.0), (217.5, 69.0), (190.8, 109.5)]       # where E-300 puts them (for the note)

FIXTURES = [('L1', 'RECESSED DOWNLIGHT, 3-1/2" APERTURE', 'FOR', 'BATH, VESTIBULE (A-207a)'),
            ('L2', 'RECESSED DOWNLIGHT, WET LOCATION', 'FOR', 'SHOWER; E-300 TAGS IT L1 (W), A-207a\'S WET TYPE IS L2'),
            ('L12', 'LED COVE AT THE BAND STEP', 'FOR', 'STORAGE AND OFFICE; NO CROWN IN THE POOL HOUSE, SO FOR\'S COVE STAYS'),
            ('LM1', 'BACKLIT LED MIRROR 24" x 48", HARDWIRED, DIMMABLE', 'ID', 'BATH, 4\'-0" TO 8\'-0" (4/ID-404), AS THE GUEST BATH; J-BOX BEHIND IT; REPLACES FOR\'S VANITY WALL LIGHT'),
            ('CH1', 'CHANDELIER ON A J-BOX (CENTER TO SPACE)', 'ID', 'ON FOR\'S J-BOXES, STORAGE AND OFFICE; 7\'-0" CLEAR UNDER IT'),
            ('WP', 'EXTERIOR WALL LIGHT, WET LOCATION', 'FOR', 'DOOR 05, EACH SIDE (E-300)')]


def tray(pl, r, color, w):
    x0, y0, x1, y1 = r
    pl.rect(x0 + BAND, y0 + BAND, x1 - BAND, y1 - BAND, w, color)

def cove(pl, r, color):
    x0, y0, x1, y1 = r; d = BAND - 1.5
    pl.rect(x0 + d, y0 + d, x1 - d, y1 - d, 0.8, color, None, dashes='[3 1.5] 0')

def pockets(pl, color):
    for a, b, y0, y1 in ((MS_WIN[0] - 4, MS_WIN[1] + 4, 0.0, 5.0), (OF_WIN[0] - 4, OF_WIN[1] + 4, IY - 5.0, IY)):
        pl.rect(a, y0, b, y1, 0.5, color, None)

def mini_splits(pl, color):
    pl.rect(MS1[0], IY - 8.0, MS1[1], IY, 0.5, color, None, dashes='[2 1.5] 0')
    pl.rect(CE1, MS2[0], CE1 + 8.0, MS2[1], 0.5, color, None, dashes='[2 1.5] 0')

def ctag(sh, pl, x, y, lines):
    q = pl.P(x, y); w = max(FREG.f.text_length(t, fontsize=7.0) for t in lines) + 8; h = 8.6 * len(lines) + 4
    r = fitz.Rect(q[0] - w / 2, q[1] - h / 2, q[0] + w / 2, q[1] + h / 2)
    sh.p.draw_rect(r, color=INK, fill=WHITE, width=0.5)
    for i, t in enumerate(lines): sh.text(q[0], r.y0 + 8.6 + 8.6 * i, t, 7.0, INK, align='c', raw=True)

def downlight(sh, q, r=4.5):
    sh.p.draw_circle(fitz.Point(*q), r, color=INK, width=0.6); sh.p.draw_circle(fitz.Point(*q), 1.0, color=INK, fill=INK, width=0.3)

def jbox(sh, q):
    sh.p.draw_circle(fitz.Point(*q), 5.0, color=INK, width=0.6)
    sh.line((q[0] - 8, q[1]), (q[0] + 8, q[1]), 0.5, INK); sh.line((q[0], q[1] - 8), (q[0], q[1] + 8), 0.5, INK)

def detector(sh, q, t):
    sh.p.draw_circle(fitz.Point(*q), 5.0, color=INK, width=0.5); sh.p.draw_circle(fitz.Point(*q), 1.6, color=INK, width=0.4)
    sh.text(q[0] + 7, q[1] + 2.5, t, 7.0, INK, raw=True)

def fan(sh, q):
    r = fitz.Rect(q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7); sh.p.draw_rect(r, color=INK, width=0.5)
    sh.text(q[0], q[1] + 2.5, 'EF', 7.0, INK, align='c', raw=True)

def label(sh, q, t, dx=7, dy=-4, size=7.0, color=INK, align='l'):
    sh.text(q[0] + dx, q[1] + dy, t, size, color, align=align, raw=True)

def ceiling_items(sh, pl, tags=True):
    for c in CH: jbox(sh, pl.P(*c))
    for c in L1 + L2: downlight(sh, pl.P(*c))
    for c in SD: detector(sh, pl.P(*c), 'SD')
    for c in SDCO: detector(sh, pl.P(*c), 'SD/CO')
    fan(sh, pl.P(*EF))
    if tags:
        for c in CH: label(sh, pl.P(*c), 'CH1', 8, -6)
        for c in L1: label(sh, pl.P(*c), 'L1')
        for c in L2: label(sh, pl.P(*c), 'L2')

def lighting_items(sh, pl):
    ceiling_items(sh, pl)
    # LM1: the backlit mirror on the core west wall over the vanity, bath side (heavy bar on the wall face, as on ID-131/132)
    x_, yc, w_ = LM1
    sh.line(pl.P(x_ + 1.0, yc - w_ / 2), pl.P(x_ + 1.0, yc + w_ / 2), 2.4, INK)
    label(sh, pl.P(x_ + 2.0, yc - w_ / 2), 'LM1', 4, -3)
    for c in WP:
        q = pl.P(*c); sh.p.draw_circle(fitz.Point(*q), 4.5, color=DARKG, width=0.5)
        sh.line((q[0] - 4.5, q[1] - 4.5), (q[0] + 4.5, q[1] - 4.5), 0.8, DARKG)
        label(sh, q, 'WP', 6, 9, 7.0, DARKG)
    for (x, y), (ox, oy), t, side in SW:
        q = pl.P(x + ox, y + oy)
        sh.text(q[0], q[1] + 3.5, '$', 10, INK, align='c', raw=True)
        if ox: sh.text(q[0] + (-6 if ox < 0 else 6), q[1] + 11, t, 7.0, INK, align='r' if ox < 0 else 'l', raw=True)
        elif side == 'r': sh.text(q[0] + 6, q[1] + 1, t, 7.0, INK, raw=True)
        elif side == 'u': sh.text(q[0] - 3, q[1] - 6, t, 7.0, INK, align='r', raw=True)
        else: sh.text(q[0] - 6, q[1] + 1, t, 7.0, INK, align='r', raw=True)

def sym_sconce(sh, x, y, nx, ny, r=3.2):
    """Wall light: half disc on the wall face, opening into the room."""
    s = sh.p.new_shape(); a0 = math.degrees(math.atan2(ny, nx)) - 90
    pts = [fitz.Point(x + r * math.cos(math.radians(a0 + t)), y + r * math.sin(math.radians(a0 + t))) for t in range(0, 181, 15)]
    s.draw_polyline(pts + [pts[0]]); s.finish(color=INK, fill=INK, width=0.4, closePath=True); s.commit()

def walls(pl, millwork):
    """RCP: walls and openings only, no door swings. Lighting: the millwork the lights sit in, no plumbing fixtures (the EF is over the toilet)."""
    door = Plan.door
    if not millwork: Plan.door = lambda *a, **k: None
    try: draw_plan(pl, fixtures=False, millwork=millwork)
    finally: Plan.door = door
    if millwork: pl.rect(VAN_X[0], VAN_Y[0] + 0.5, VAN_X[1], VAN_Y[1] - 0.5, 0.5, MID, None)     # the vanity, for the mirror over it

def _row_sym(sh, kind, x, y):
    if kind == 'down': downlight(sh, (x, y))
    elif kind == 'jbox': jbox(sh, (x, y))
    elif kind == 'sd':
        sh.p.draw_circle(fitz.Point(x, y), 5.0, color=INK, width=0.5); sh.p.draw_circle(fitz.Point(x, y), 1.6, color=INK, width=0.4)
    elif kind == 'ef':
        sh.p.draw_rect(fitz.Rect(x - 7, y - 7, x + 7, y + 7), color=INK, width=0.5); sh.text(x, y + 2.5, 'EF', 7.0, INK, align='c', raw=True)
    elif kind == 'lm1': sh.line((x - 12, y), (x + 12, y), 2.4, INK)
    elif kind == 'cove': sh.line((x - 12, y), (x + 12, y), 0.8, INK, dashes='[3 1.5] 0')
    elif kind == 'band': sh.line((x - 12, y), (x + 12, y), 0.7, INK)
    elif kind == 'pocket': sh.p.draw_rect(fitz.Rect(x - 12, y - 3, x + 12, y + 3), color=INK, width=0.5)
    elif kind == 'ms': sh.p.draw_rect(fitz.Rect(x - 12, y - 4, x + 12, y + 4), color=MID, width=0.5, dashes='[2 1.5] 0')
    elif kind == 'sw': sh.text(x, y + 3.5, '$', 10, INK, align='c', raw=True)
    elif kind == 'wp':
        sh.p.draw_circle(fitz.Point(x, y), 4.5, color=DARKG, width=0.5); sh.line((x - 4.5, y - 4.5), (x + 4.5, y - 4.5), 0.8, DARKG)

def legend(sh, x, y, w):
    sh.text(x, y, 'FIXTURE SCHEDULE', 9.0, INK, bold=True, spacing=1.0, raw=True); y += 18
    cols = [x, x + 30, x + 196, x + 222]
    for cx, t in zip(cols, ('TYPE', 'DESCRIPTION', 'BY', 'NOTES')): sh.text(cx, y, t, 7.0, INK, bold=True, raw=True)
    y += 4; sh.line((x, y), (x + w, y), 0.5, INK); y += 10
    for typ, desc, src, note in FIXTURES:
        d_ = PH.wrap(desc, 7.0, 160); n_ = PH.wrap(note, 7.0, w - 226)
        sh.text(cols[0], y, typ, 7.0, INK, bold=True, raw=True); sh.text(cols[2], y, src, 7.0, INK, raw=True)
        for i, t in enumerate(d_): sh.text(cols[1], y + 9 * i, t, 7.0, INK, raw=True)
        for i, t in enumerate(n_): sh.text(cols[3], y + 9 * i, t, 7.0, INK, raw=True)
        y += 9 * max(len(d_), len(n_)) + 4; sh.line((x, y - 8.2), (x + w, y - 8.2), 0.25, LIGHT)
    y += 12
    sh.text(x, y, 'SYMBOLS', 9.0, INK, bold=True, spacing=1.0, raw=True); y += 16
    rows = [('down', 'RECESSED DOWNLIGHT, TYPE TAGGED (L1, L2).'), ('jbox', 'CHANDELIER J-BOX CH1, CENTERED IN THE ROOM (FOR).'),
            ('sd', 'SD SMOKE DETECTOR, SD/CO COMBINATION (FOR).'), ('ef', 'EXHAUST FAN (FOR), OVER THE TOILET.'),
            ('lm1', 'LM1 BACKLIT LED MIRROR ON THE WALL, J-BOX BEHIND IT.'),
            ('cove', 'L12 LED COVE AT THE BAND STEP (FOR).'), ('band', 'BAND EDGE: 8\'-7" BAND STEPS UP TO THE 8\'-11" FIELD.'),
            ('pocket', 'C-1 POCKET, 5", DRAPERY TRACK, FULL WIDTH.'), ('ms', 'MINI SPLIT ON THE WALL (FOR), DASHED.'),
            ('wp', 'EXTERIOR WALL LIGHT WP (FOR).'),
            ('sw', 'SWITCH CL 4\'-0" AT THE LATCH: S SINGLE POLE, D DIMMER, S2 TWO DEVICES.')]
    for kind, t in rows:
        _row_sym(sh, kind, x + 12, y - 3)
        ls = PH.wrap(t, 7.0, w - 40)
        for i, ln in enumerate(ls): sh.text(x + 34, y + 9 * i, ln, 7.0, INK, raw=True)
        y += 9 * len(ls) + 6
    y += 8
    notes = [(True, 'CEILINGS (FOR A-207)'),
             'STORAGE, OFFICE: GYP. PT-01, 8\'-11" CENTER, 8\'-7" BAND 10" WIDE AT THE WALLS, FOR\'S L12 COVE AT THE STEP. '
             'NO CROWN: THE 8\'-0" HEADS LEAVE 3-1/2" UNDER THE BAND (ID-400). BATH AND VESTIBULE: 8\'-11" FLAT; MOISTURE-RESISTANT BOARD IN THE BATH.',
             'C-1: FOR\'S 5" POCKETS AT BOTH M WINDOWS WITH FULL-WIDTH DRAPERY (ID-402, ID-403); MOTORIZED OR MANUAL BY OWNER, FOR\'S MOTOR OUTLETS AT EACH (E-300) IF MOTORIZED. MINI SPLITS TOP 8\'-1", 6" UNDER THE BAND.',
             (True, 'LIGHTING AND SWITCHING (FOR E-300)'),
             'FOR\'S FIXTURES KEPT: CH1 J-BOXES, L1, L2, L12, EF, SD, SD/CO, WP. OURS: THE LM1 BACKLIT MIRROR IN PLACE OF FOR\'S VANITY WALL LIGHT (AS THE GUEST BATH). NO TAPE LIGHTS, NO BAR.',
             'SWITCHES AT THE LATCH, PER OUR ELEVATIONS. STORAGE S (2/ID-402): CH1 AND L12. OFFICE D (3/ID-403, SOUTH WALL 4" OFF THE CORNER): CH1 AND L12. '
             'BATH S2 (3/ID-404): L1, L2 AND LM1 ON ONE, EF ON THE OTHER. VESTIBULE S (2/ID-405): L1. EXTERIOR WP ON FOR\'S CIRCUIT.',
             'FOR\'S E-300 SWITCHES ON THE HINGE SIDE OF DOORS 11 AND EAST OF THE BATH DOOR MOVE AS SHOWN (FOR LIST).',
             'EXTERIOR STAIR LIGHTS (L15) AND PLANTER LIGHTS ON THE EAST SIDE: FOR E-300, OUTSIDE THIS SCOPE.']
    return para_block(sh, x, y, notes, w, 7.0)

def sheet(doc):
    sh = Sheet(doc); sh.frame('POOL HOUSE', 'SCALE: 1/2" TO 1\'-0"', ['POOL HOUSE', 'RCP AND LIGHTING'], 'ID-406', legend_rule=False)
    x0 = FR.x0 + 40; w = (IX + 2 * W_EXT) * K
    lx = x0 + w + 56; lw = TB_X - 14 - lx
    # ---------------- RCP
    pl = Plan(sh, x0, HDR_Y + 58, K)
    walls(pl, False)
    for r in (STORAGE, OFFICE): tray(pl, r, INK, 0.7); cove(pl, r, INK)
    pockets(pl, INK); mini_splits(pl, MID)
    ceiling_items(sh, pl, tags=True)
    ctag(sh, pl, 30.0, 82.0, ['CLG 8\'-11"', '8\'-7" BAND', 'GYP. PT-01', 'L12 COVE'])
    ctag(sh, pl, 300.0, 82.0, ['CLG 8\'-11"', '8\'-7" BAND', 'GYP. PT-01', 'L12 COVE'])
    ctag(sh, pl, 158.0, 22.0, ['CLG 8\'-11"', 'GYP. PT-01 MR'])
    ctag(sh, pl, 148.0, 94.0, ['CLG 8\'-11"', 'GYP. PT-01'])
    for t, x, y in (('C-1 POCKET', 59.3, 4.0), ('C-1 POCKET', 276.6, IY - 1.0), ('MINI SPLIT 1', 63.4, IY - 2.2), ('MINI SPLIT 2', CE1 + 14.0, 33.2)):
        q = pl.P(x, y); sh.text(q[0], q[1], t, 7.0, MID, align='c' if 'SPLIT 2' not in t else 'l', raw=True)
    for t, x, y in (('STORAGE', 60.0, 40.0), ('OFFICE', 276.0, 40.0), ('BATH', 186.0, 64.0), ('VESTIBULE', 190.0, 86.0)):
        pl.text(x, y, t, 7.0, MID)
    a = pl.P(-W_EXT, -W_EXT); b = pl.P(IX + W_EXT, IY + W_EXT)
    sh.text(a[0], b[1] + 30, 'POOL HOUSE REFLECTED CEILING PLAN', 11, serif=True, spacing=0.8, raw=True)
    scale_bar(sh, b[0] - 12 * K * 10 - 110, b[1] + 32, K); north(sh, a[0] - 30, a[1] + 20)
    # ---------------- lighting
    pl = Plan(sh, x0, b[1] + 146, K)
    walls(pl, True)
    for r in (STORAGE, OFFICE): tray(pl, r, GREY, 0.45); cove(pl, r, INK)
    for t, x, y in (('L12', 30.0, BAND + 4.0), ('L12', CE1 + BAND + 2.0, IY - BAND - 4.0)):
        q = pl.P(x, y); sh.text(q[0], q[1], t, 7.0, INK, raw=True)
    lighting_items(sh, pl)
    a = pl.P(-W_EXT, -W_EXT); b = pl.P(IX + W_EXT, IY + W_EXT)
    sh.text(a[0], b[1] + 40, 'POOL HOUSE LIGHTING AND SWITCHING PLAN', 11, serif=True, spacing=0.8, raw=True)
    scale_bar(sh, b[0] - 12 * K * 10 - 110, b[1] + 42, K); north(sh, a[0] - 30, a[1] + 20)
    y = legend(sh, lx, HDR_Y + 60, lw)
    assert y < FR.y1 - 8, ('ID-406 legend runs off', y)
    assert b[1] + 60 < FR.y1 - 8, ('ID-406 plans run off', b[1])
    return sh
