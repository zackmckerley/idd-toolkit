"""Design study sheet: master bathroom north (vanity) wall, three compositions for the owner to choose from.
Drawn with the component library (idd_components), not the generator defaults. Output: 261102.HD102.MasterBathStudy.pdf"""
import pymupdf as fitz
import idd_elevations as E, idd_components as C
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT, HEIGHTS

OUT = '/home/claude/flrwork/261102.HD102.MasterBathStudy.pdf'
L, H = 160.0, 120.0                       # north wall of the master bathroom, ceiling assumed 10'-0" (VERIFY)
OPEN_X, OPEN_W, HEAD = 61.8, 36.4, 96.0   # cased opening to the W.I.C.
VAN_L, VAN_R = (0.0, 54.4), (105.4, 54.6)  # vanities from the plan

def frame_wall(v, crown_on=True, base_on=True):
    """Walls, floor, ceiling, trims; the parts every option shares."""
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    if base_on:
        for a, b in ((0, OPEN_X), (OPEN_X + OPEN_W, L)): C.base(v, a, b)
    if crown_on: C.crown(v, 0, L, H)
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    for x, dx in ((X0, -4), (X1, 4)): v.rect(x, Y0, x + dx, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    C.cased_opening(v, OPEN_X, OPEN_W, HEAD, beyond=C.wardrobe_beyond)

def option_a(v):
    """Furniture vanities on turned legs, framed mirrors, cylinder sconces, painted walls."""
    frame_wall(v)
    for x, w in (VAN_L, VAN_R):
        C.vanity_furniture(v, x + 1.5, w - 3, h=34, legs=True, drawers=3)
        mx = x + w / 2; mw, my, mh = 32, 44, 44
        C.mirror_framed(v, mx - mw / 2, mw, my, mh)
        for sx in (mx - mw / 2 - 7, mx + mw / 2 + 7): C.sconce(v, sx, 66, 'cylinder')
    return ['A  FURNITURE VANITIES: 51" PAINTED VANITIES ON TURNED LEGS, STONE TOPS WITH 3/4" OVERHANG,',
            'FRAMED MIRRORS 32" x 44" AT 3\'-8" AFF, CYLINDER SCONCES CL 5\'-6" AFF 7" OFF THE MIRROR, WALLS PT-02,',
            'CROWN CM-01, BASE RETURNS AT THE OPENING. WAINSCOT NONE: TILE WT-02 AT THE SHOWER AND TUB ALCOVE ONLY.']

def option_b(v):
    """Built-in wall-to-wall vanities on a plinth, tile wainscot WT-02 to 42", frameless mirror panels to the crown, sconces on the mirror."""
    cs = 3.5
    show = [(0, VAN_L[1], 34, 42), (VAN_L[1], OPEN_X - cs, 0, 42), (OPEN_X + OPEN_W + cs, VAN_R[0], 0, 42), (VAN_R[0], L, 34, 42)]
    frame_wall(v, base_on=False)
    C.tile_grid(v, 0, L, 0, 42, (24, 12), 0.125, 'center', show=show)
    for a, b in ((0, OPEN_X), (OPEN_X + OPEN_W, L)): C._line(v, (a, 42), (b, 42), C.OUTLINE)   # tile cap line
    for x, w in (VAN_L, VAN_R):
        C.vanity_furniture(v, x, w, h=34, legs=False, drawers=3)
        C.mirror_panel(v, x, w, 44, H - 5.5 - 44)
        mx = x + w / 2
        for sx in (mx - 15, mx + 15): C.sconce(v, sx, 66, 'cylinder')
    return ['B  BUILT-IN VANITIES: WALL-TO-WALL PAINTED CABINETS ON A 4" PLINTH, STONE TOPS, WALL TILE WT-02 WAINSCOT TO 3\'-6" AFF',
            'ON THE WHOLE WALL (12x24 STACKED, CENTERED SET-OUT), FRAMELESS MIRROR PANELS FROM 3\'-8" TO THE CROWN,',
            'SCONCES MOUNTED THROUGH THE MIRROR CL 5\'-6" AFF, 30" APART. WALLS ABOVE THE TILE PT-02, CROWN CM-01.']

def option_c(v):
    """Floating vanities with LED, stone slab backsplash to 48", framed mirrors, shaded sconces."""
    frame_wall(v)
    for x, w in (VAN_L, VAN_R):
        C.stone_slab(v, x, x + w, 35.25, 48, seams=())
        C.vanity_floating(v, x, w, h=34, box_h=14, drawers=2)
        mx = x + w / 2; mw, my, mh = 30, 50, 40
        C.mirror_framed(v, mx - mw / 2, mw, my, mh, frame=1.25, bevel=False)
        for sx in (mx - mw / 2 - 7, mx + mw / 2 + 7): C.sconce(v, sx, 68, 'shade')
    return ['C  FLOATING VANITIES: 14" DEEP DRAWER CABINETS HUNG AT 1\'-8" AFF WITH LED BELOW, STONE SLAB TOP AND BACKSPLASH TO 4\'-0" AFF',
            '(WS, MATCH THE TOP), THIN-FRAME MIRRORS 30" x 40" AT 4\'-2" AFF, SHADED SCONCES CL 5\'-8" AFF, WALLS PT-02, CROWN CM-01,',
            'BASE CONTINUOUS BEHIND THE VANITIES. TOE SPACE AND FLOOR TILE RUN UNDER THE CABINETS.']

HEIGHTS_BY_OPTION = {1: [0, 34, 44, 66, 88, HEAD, H - 5.5, H],          # counter, mirror, sconce CL, mirror top, head, crown
                     2: [0, 34, 42, 44, 66, HEAD, H - 5.5, H],          # counter, tile cap, mirror panel, sconce CL, head, crown
                     3: [0, 20, 34, 48, 50, 68, 90, HEAD, H - 5.5, H]}  # cabinet bottom, counter, slab, mirror, sconce CL, mirror top, head, crown
def dims(v, n):
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, VAN_L[1], OPEN_X, OPEN_X + OPEN_W, VAN_R[0], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points(HEIGHTS_BY_OPTION[n]))

def build():
    doc = fitz.open(); sh = Sheet(doc)
    sh.frame('DESIGN STUDY - MASTER BATHROOM NORTH WALL', 'SCALE: 1/2" TO 1\'-0"', ['DESIGN STUDY', 'MASTER BATH VANITY WALL'], 'ID-730 S1', legend_rule=False)
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    cells = E.layout_cells(frame, 2, 2)
    spec = {'room': 'MASTER BATHROOM', 'view': 'NORTH', 'length': L, 'ceiling': H}
    k = E.SCALES['1/2']
    for cell, (title, fn), n in zip(cells, (('OPTION A - FURNITURE VANITIES', option_a), ('OPTION B - BUILT-IN WITH TILE WAINSCOT', option_b), ('OPTION C - FLOATING WITH STONE SPLASH', option_c)), (1, 2, 3)):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, f'NORTH ELEVATION - MASTER BATHROOM, {title}', 'SCALE: 1/2" TO 1\'-0"')
        origin = E.fit_origin(cell, spec, k)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        notes = fn(v); dims(v, n)
        v.text(v.X(0) - 6, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 28
        for ln in notes: sh.text(cell[2] - 8, ny, ln, 5.6, MID, align='r'); ny += 8
    # fourth cell: what is common, what the choice decides, and the questions
    cell = cells[3]; E.title_bar(sh.p, sh.font, sh.fontname, cell, 4, 'WHAT THE CHOICE DECIDES', '')
    x, y = cell[0] + 20, cell[1] + 40
    lines = ['COMMON TO ALL THREE: TWO 54" VANITIES EITHER SIDE OF THE 3\'-0" CASED OPENING TO THE W.I.C. (WARDROBES SEEN BEYOND),',
             'COUNTER 2\'-10" AFF, SCONCE CENTERLINES 5\'-6" TO 5\'-8" AFF, CEILING 10\'-0" (VERIFY), CROWN CM-01, WALL PT-02.',
             '',
             'THE CHOICE SETS: THE VANITY TYPE (MILLWORK PRICE AND THE LOOK OF THE WHOLE BATH, THE SAME TYPE REPEATS IN THE',
             'GUEST BATH AND BATHS 2 AND 3), WHETHER TILE WT-02 LEAVES THE WET ZONES AND BECOMES A WAINSCOT (ADDS ABOUT 55 SF),',
             'WHETHER THE MIRRORS ARE FRAMED PIECES OR A MIRROR WALL, AND HOW THE SCONCES MOUNT (WALL OR THROUGH THE MIRROR).',
             '',
             'ONCE PICKED, THE SAME LANGUAGE CARRIES TO THE OTHER THREE WALLS OF THIS ROOM (SHOWER WALL WEST, TUB ALCOVE SOUTH,',
             'ENTRY AND WATER CLOSET EAST) AND THEN TO THE OTHER BATHS, AND THE SET IS REGENERATED WITH THESE COMPONENTS.',
             '',
             'QUESTIONS TO SETTLE WITH THE PICK: SINGLE OR DOUBLE SINK PER VANITY (PLAN SHOWS SINGLE), MEDICINE CABINETS',
             'RECESSED BEHIND THE MIRRORS, A TOWER OR LINEN CABINET AT EITHER END, OUTLET LOCATIONS (IN THE SPLASH OR INSIDE A DRAWER).']
    for ln in lines: sh.text(x, y, ln, 6.6, INK if ln.startswith(('COMMON', 'THE CHOICE', 'ONCE', 'QUESTIONS')) else MID); y += 11
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
