import sys
"""Master bathroom pilot set, Option A language (furniture vanities, framed mirrors, cylinder sconces, painted walls,
WT-02 tile in the shower and tub alcove only). Drawn with idd_components.
Sheets: ID-730 key plan with the elevation markers; ID-731 room elevations 1-4; ID-732 shower and tub alcove; ID-733 water closet.
Geometry measured off FOR's floor 2 plan (YL id 07 base, 3/16" scale): PLAN below, inches from the room's west wall face (x)
and north wall face (y). Output: 261105.HD102.MasterBathPilot.pdf"""
import pymupdf as fitz
import idd_elevations as E, idd_components as C
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT, TRIM

OUT = '/home/claude/flrwork/261105.HD102.MasterBathPilot.pdf'
H = 120.0                 # ceiling, VERIFY
HEAD, SILL = 96.0, 48.0   # door and window heads, bath window sills, VERIFY
CS = TRIM['casing']
CTR, FAUCET, MIR_B, MIR_T, SCONCE = 34.0, 40.0, 44.0, HEAD + CS, 66.0   # mirror top on the top of the head casing
TILE = (48, 96)           # WT-02 large-format porcelain slab, 48 x 96 panels set vertical, seams as drawn
WHITE = (1, 1, 1); BEYOND = (0.55, 0.55, 0.55)

# ---- plan, inches (measured on the base plan; the room is 160 wide x 139.7 deep)
ROOM_W, ROOM_D = 160.0, 139.7
WIC_X, WIC_W = 61.8, 36.4                 # cased opening in the north wall
VAN_W = 51.0                              # furniture vanities, centered on each wall segment between the corner and the opening casing
VAN_GAP = (WIC_X - CS - VAN_W) / 2        # 2.9 in. each side with the 5 in. casing
VAN_L, VAN_R = (VAN_GAP, VAN_W), (ROOM_W - VAN_GAP - VAN_W, VAN_W)
PD_Y0, PD_Y1 = 31.4, 67.1                 # pocket door in the east wall (from the north face)
FRONT_Y0, FRONT_Y1 = 78.2, 83.0           # alcove line: the water closet front wall and the piers
ALC_D = ROOM_D - FRONT_Y1                 # alcove depth, 56.7
WC_DOOR = 31.4                            # water closet door opening
WC_JAMB_E = (160.0 - 117.4 - WC_DOOR) / 2   # 5.6: door centered on the water closet wall (FOR's plan has it 3.5 from the east wall, see note)
PIER_WC = (112.6, 160.0 - 5.6 - 31.4)      # pier between the tub alcove and the water closet door (plan x): partition plus the 5-5/8 in. jamb wall
PIER_SH = (38.6, 48.7)                    # pier between the shower opening and the tub alcove (plan x)
STUB_SH = (0.0, 3.9)                      # stub at the west wall where the shower glass lands
TUB_WALL = (48.7, 111.4)                  # tub alcove back wall (plan x), window centered with 1.3 in. each side
SH_IN = (0.0, 43.1)                       # shower interior (plan x)
WC_IN = (117.4, 160.0)                    # water closet interior (plan x)
TER_Y0, TER_Y1 = 21.4, 77.1               # terrace door opening in the west wall (from the north face)
SWIN_Y0, SWIN_Y1 = 93.0, 129.8            # shower window in the west wall (from the north face)
TOILET_X = (130.6, 145.3)                 # toilet, plan x, tank against the south wall
SH_DOOR = 28.0                            # frameless glass shower door, centered in the opening between equal fixed panels
VALVE_IN = 32.3                           # valve and head, in from the alcove line on the shower's east partition

def sx(plan_x): return ROOM_W - plan_x    # looking south: view x runs east to west
def wx(plan_y): return ROOM_D - plan_y    # looking west: view x runs south to north

def shell(v, L, crown=(), base=(), cut_left=True, cut_right=True):
    """Floor, ceiling, cut end walls, crown and base runs (lists of (x0, x1))."""
    X0, X1, Y0, Y1 = v.X(0), v.X(L), v.Y(0), v.Y(H)
    for a, b in base: C.base(v, a, b)
    for a, b in crown: C.crown(v, a, b, H)
    v.line((X0 - 8, Y0), (X1 + 8, Y0), 1.2); v.line((X0, Y1), (X1, Y1), 0.9)
    if cut_left: v.rect(X0 - 4, Y0, X0, Y1, 0.6, fill=(0.3, 0.3, 0.3))
    if cut_right: v.rect(X1, Y0, X1 + 4, Y1, 0.6, fill=(0.3, 0.3, 0.3))

def towel_ring(v, cx, cy):
    C._ellipse(v, cx, cy - 4, 3.0, 3.0, C.OUTLINE); C._ellipse(v, cx, cy, 1.1, 1.1, C.FINE, MID)
def robe_hook(v, cx, cy):
    C._rect(v, cx - 1.0, cy - 1.0, cx + 1.0, cy + 1.0, C.FINE); C._line(v, (cx, cy - 1.0), (cx, cy - 3.0), C.OUTLINE); C._ellipse(v, cx, cy - 3.3, 0.6, 0.6, C.FINE)
def tile_cap(v, x0, x1, y=HEAD): C._line(v, (x0, y), (x1, y), C.OUTLINE)
def finish_tag(v, x, y, s): v.text(v.X(x), v.Y(y), s, 5.2, MID, align='c')

# ================================================================== room elevations (ID-731)
def north(v):
    L = ROOM_W
    shell(v, L, crown=[(0, L)], base=[(0, WIC_X), (WIC_X + WIC_W, L)])
    C.door_pair(v, WIC_X, WIC_W, HEAD, panels=1)
    for x, w in (VAN_L, VAN_R):
        C.vanity_furniture(v, x, w, h=CTR, legs=True, drawers=3, faucet_style='wall')
        mx = x + w / 2; mw = 32
        C.mirror_framed(v, mx - mw / 2, mw, MIR_B, MIR_T - MIR_B)
        for s in (mx - mw / 2 - 7, mx + mw / 2 + 7): C.sconce(v, s, SCONCE, 'cylinder')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, VAN_L[0], VAN_L[0] + VAN_W / 2, VAN_L[0] + VAN_W, WIC_X - CS, WIC_X + WIC_W + CS, VAN_R[0], VAN_R[0] + VAN_W / 2, VAN_R[0] + VAN_W, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TRIM['base'], CTR, FAUCET, MIR_B, SCONCE, HEAD, MIR_T, H - TRIM['crown'], H]))
    return ['51" PAINTED FURNITURE VANITIES ON TURNED LEGS, STONE TOPS, WALL-MOUNTED FAUCETS CL 3\'-4" AFF. SINK, MIRROR AND SCONCES',
            'CENTERED ON EACH VANITY. EACH VANITY CENTERED BETWEEN THE CORNER AND THE 5" DOOR CASING, 2-7/8" CLEAR EACH SIDE.',
            'FRAMED MIRRORS 32" x 57", 3\'-8" AFF TO THE TOP OF THE HEAD CASING (8\'-5"). CYLINDER SCONCES CL 5\'-6" AFF. BASE 8-1/2", CROWN 8" BUILT UP, CASING 5" PER THE TRIM BLOCK.',
            'W.I.C.: PAIR OF 1\'-6" SINGLE-PANEL PAINTED DOORS, CASED, SWING INTO THE CLOSET, BALL CATCH, 8\'-0" HEAD. WALLS PT-02, CROWN CM-01,',
            'BASE RETURNS AT THE DOOR. HAND TOWEL RINGS ON THE SIDE WALLS, SEE 2 AND 4.']

def east(v):
    L = FRONT_Y0
    shell(v, L, crown=[(0, L)], base=[(0, PD_Y0 - CS), (PD_Y1 + CS, L)])
    C.casing(v, PD_Y0, PD_Y1 - PD_Y0, HEAD); C.door_leaf(v, PD_Y0, PD_Y1 - PD_Y0, HEAD, panels=1, swing=None)
    C.vanity_end(v, 0, depth=20.1, h=CTR, open_to='R')
    towel_ring(v, 10, 52)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, 20.1, PD_Y0, PD_Y1, L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, CTR, 52, HEAD, H - TRIM['crown'], H]))
    return ['NORTH CORNER TO THE WATER CLOSET WALL (6\'-6"). THE WATER CLOSET IS DRAWN ON ID-733.',
            'POCKET DOOR TO THE MASTER BEDROOM 2\'-11-3/4" x 8\'-0", SINGLE-PANEL PAINTED LEAF, CASED. HAND TOWEL RING OVER THE VANITY END, CL 4\'-4" AFF.',
            'WALLS PT-02, CROWN CM-01 AND BASE CONTINUOUS, BASE RETURNS AT THE DOOR.']

def south(v):
    """The front plane at the alcove line as the room sees it: one painted wall with the water closet door, the open tub alcove
    and the glass-fronted shower. What is inside the alcoves is drawn lightly, as beyond; their own elevations are on ID-732 and ID-733."""
    L = ROOM_W
    wc_door = (sx(ROOM_W - WC_JAMB_E), sx(ROOM_W - WC_JAMB_E - WC_DOOR))   # 5.6 in. jamb takes the 5 in. casing with 5/8 in. to the corner
    pier_wc = (sx(PIER_WC[1]), sx(PIER_WC[0]))
    tub = (sx(TUB_WALL[1]), sx(TUB_WALL[0]))
    pier_sh = (sx(PIER_SH[1]), sx(PIER_SH[0]))
    sh_open = (sx(PIER_SH[0]), sx(STUB_SH[1]))
    stub = (sx(STUB_SH[1]), L)
    shell(v, L, crown=[(0, pier_wc[1]), (pier_sh[0], L)], base=[(0, wc_door[0]), (wc_door[1], pier_wc[1]), pier_sh, stub])
    # beyond, lightly: tub alcove back wall (tile line, window, tub) and the shower back wall (niche)
    keep = (C.INK, C.MID); C.INK = BEYOND; C.MID = BEYOND
    win = (tub[0] + 1.3, tub[1] - 1.3)
    C.window(v, win[0], win[1] - win[0], SILL, HEAD, lites=3, trim=False)
    C.tub_filler_wall(v, (tub[0] + tub[1]) / 2, 30); C.freestanding_tub(v, (tub[0] + tub[1]) / 2 - 30.05, 60.1, 22, filler=None)
    shc = (sx(SH_IN[1]) + sx(SH_IN[0])) / 2; C.niche(v, shc - 12, 24, 58, 12, shelves=0)
    C.INK, C.MID = keep
    # header wall over the shower glass, same as over the water closet door: masks what is beyond above 8'-0"
    C._rect(v, sh_open[0], HEAD, sh_open[1], H, C.FINE, WHITE, fill=WHITE); C.crown(v, sh_open[0], sh_open[1], H)
    C._line(v, (sh_open[0], HEAD), (sh_open[1], HEAD), C.OUTLINE)
    # the alcove openings: heavy jamb lines with a shadow on the recess side
    for (a, b), top in ((tub, H), (sh_open, HEAD)):
        C._line(v, (a, 0), (a, top), C.HEAVY); C._line(v, (b, 0), (b, top), C.HEAVY)
        C._line(v, (a + 0.6, 0), (a + 0.6, top), C.FINE, LIGHT); C._line(v, (b - 0.6, 0), (b - 0.6, top), C.FINE, LIGHT)
    # shower glass: frameless front with a 28 in. door centered between equal fixed panels, hinged at the pier like the water closet door
    fin = (sh_open[1] - sh_open[0] - SH_DOOR) / 2
    C.shower_door_centered(v, sh_open[0], sh_open[1] - sh_open[0], HEAD, SH_DOOR, hinge='L')
    # water closet door in the front wall, hinged at the east jamb; robe hook on the pier
    C.casing(v, wc_door[0], WC_DOOR, HEAD); C.door_leaf(v, wc_door[0], WC_DOOR, HEAD, panels=2, swing='L')
    robe_hook(v, (pier_wc[0] + pier_wc[1]) / 2, 68)
    finish_tag(v, (tub[0] + tub[1]) / 2, 108, 'TUB ALCOVE BEYOND, SEE ID-732')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, wc_door[0], wc_door[1], pier_wc[1], tub[1], sh_open[0], sh_open[0] + fin, sh_open[1] - fin, sh_open[1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 36, 48, HEAD, H - TRIM['crown'], H]))
    return ['LOOKING SOUTH, EAST AT THE LEFT: THE WALL AT THE ALCOVE LINE, PT-02 WITH CROWN AND BASE, 10-3/8" AND 10" PIERS BETWEEN THE OPENINGS.',
            'WATER CLOSET: 2\'-8" TWO-PANEL DOOR CENTERED ON ITS WALL (5-5/8" EACH SIDE), HINGED AT THE EAST JAMB. FOR\'S PLAN HAS IT 3-1/2" FROM THE EAST WALL:',
            'SHIFT 2-1/8" WEST, FOR TO CONFIRM. WALL ABOVE TO THE CEILING. TUB ALCOVE: OPEN TO THE CEILING, 4\'-8-3/4" DEEP, WT-02 SLAB FLOOR TO CEILING ON ALL THREE WALLS, SEE ID-732.',
            'SHOWER: FRAMELESS 1/2" GLASS FRONT, 8\'-0" HIGH TO MATCH THE DOOR HEADS, 28" SWING DOOR CENTERED BETWEEN TWO 3-3/8" FIXED PANELS, HINGED AT',
            'THE PIER, OPENS OUT, 12" PULL, HEADER CHANNEL AT 8\'-0". PAINTED HEADER WALL ABOVE THE GLASS TO THE CEILING, SAME AS OVER THE WATER CLOSET',
            'DOOR, CROWN CONTINUOUS ACROSS IT. SHOWER FINISHES ON ID-732. DOUBLE ROBE HOOK ON THE WATER CLOSET PIER CL 5\'-8" AFF.']

def west(v):
    """West wall from the shower stub to the north corner; the shower side wall is drawn with the shower on ID-732."""
    L = FRONT_Y0
    stub = (0.0, FRONT_Y1 - FRONT_Y0)                    # 0 to 4.8, 3.9 in. proud
    door = (FRONT_Y0 - TER_Y1, FRONT_Y0 - TER_Y0)        # 1.1 to 56.8
    shell(v, L, crown=[(0, L)], base=[(door[1] + CS, L)])
    C.door_pair(v, door[0], door[1] - door[0], HEAD, panels='glass')
    C.pilaster(v, stub[0], stub[1], H, shadow_side='R'); C.crown(v, stub[0], stub[1], H); C.base(v, stub[0], stub[1])
    C.glass_edge(v, 0, HEAD)
    C.vanity_end(v, L, depth=20.1, h=CTR, open_to='L')
    towel_ring(v, L - 10, 52)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, door[0], door[1], L]))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, CTR, 52, HEAD, H - TRIM['crown'], H]))
    return ['LOOKING WEST, SOUTH AT THE LEFT: THE SHOWER STUB TO THE NORTH CORNER (6\'-6"). THE SHOWER SIDE WALL IS DRAWN ON ID-732.',
            'TERRACE DOORS: PAIR OF 2\'-4" FULL-LITE EXTERIOR DOORS IN A 4\'-7-3/4" OPENING, 8\'-0" HEAD (TYPE PER FOR DOOR SCHEDULE, VERIFY).',
            'COORDINATE: 1-1/8" FROM THE SOUTH JAMB TO THE STUB, NO ROOM FOR THE 5" CASING THERE (WRAP THE JAMB). THE VANITY SITS 3-5/8" OFF',
            'THIS WALL, SO THE NORTH CASING CLEARS IT.',
            'HAND TOWEL RING OVER THE VANITY END CL 4\'-4". WALLS PT-02, CROWN CM-01, BASE RETURNS AT THE DOOR.']

# ================================================================== shower (ID-732), all faces WT-02 floor to ceiling
def shower_west(v):
    """Shower side wall with the window, looking west: back wall at the left, glass line at the right."""
    L = ALC_D
    win = (wx(SWIN_Y1), wx(SWIN_Y0))
    shell(v, L, cut_right=False)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.window(v, win[0], win[1] - win[0], SILL, HEAD, lites=2, trim=False)
    C.pilaster(v, L - (FRONT_Y1 - FRONT_Y0), FRONT_Y1 - FRONT_Y0, H, shadow_side='L'); C.tile_grid(v, L - 4.8, L, 0, H, TILE, show=[(L - 4.8, L, 0, H)])
    C.glass_edge(v, L, HEAD)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, win[0], win[1], L - 4.8, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, SILL, HEAD, H]))
    return ['SHOWER WEST WALL. WT-02 PORCELAIN SLAB 48" x 96" x 1/4", HONED, SET VERTICAL, FLOOR TO CEILING, SEAMS AS DRAWN.',
            'WINDOW 3\'-1" x 4\'-0" AT A 4\'-0" SILL (VERIFY), TEMPERED, SLAB RETURNS INTO THE JAMB, SLOPED SLAB SILL. THE 4" STUB CARRIES THE FIXED GLASS.']

def shower_south(v):
    L = SH_IN[1] - SH_IN[0]
    shell(v, L)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.niche(v, L / 2 - 12, 24, 58, 12, shelves=0)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, L / 2 - 12, L / 2 + 12, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 58, 70, H]))
    return ['SHOWER BACK WALL, LOOKING SOUTH. WT-02 SLAB FLOOR TO CEILING, ONE PANEL WIDE, SEAM AT 8\'-0". NICHE 24" x 12" x 3-1/2" DEEP, 4\'-10" TO THE SILL,',
            'CENTERED, MITERED SLAB RETURNS AT THE NICHE, SLAB SILL SLOPED. LINEAR DRAIN AT THIS WALL, SHOWER FLOOR 2x2 MOSAIC CUT FROM THE SLAB.']

def shower_east(v):
    """The partition to the tub alcove, looking east: glass line at the left, back wall at the right."""
    L = ALC_D
    shell(v, L, cut_left=False)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.pilaster(v, 0, FRONT_Y1 - FRONT_Y0, H, shadow_side='R'); C.tile_grid(v, 0, 4.8, 0, H, TILE, show=[(0, 4.8, 0, H)])
    C.valve(v, VALVE_IN, 48); C.shower_head(v, VALVE_IN, 80)
    C.glass_edge(v, 0, HEAD)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, VALVE_IN, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 48, 80, HEAD, H]))
    return ['SHOWER EAST WALL (THE PARTITION TO THE TUB ALCOVE), LOOKING EAST. VALVE CL 4\'-0", RAIN HEAD ARM 6\'-8", BOTH 2\'-8" IN FROM',
            'THE ALCOVE LINE PER PLAN. WT-02 SLAB FLOOR TO CEILING, SEAM AT 8\'-0". GLASS FRONT SEEN EDGE-ON AT THE LEFT, DOOR HINGED ON THIS SIDE.']

# ================================================================== tub alcove (ID-732), WT-02 to 8'-0", PT-02 and crown above
def tub_south(v):
    L = TUB_WALL[1] - TUB_WALL[0]
    shell(v, L)
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    C.window(v, 1.3, L - 2.6, SILL, HEAD, lites=3, trim=False)
    C.tub_filler_wall(v, L / 2, 30); C.freestanding_tub(v, L / 2 - 30.05, 60.1, 22, filler=None)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, 1.3, L - 1.3, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 22, 30, SILL, HEAD, H]))
    return ['TUB ALCOVE BACK WALL, LOOKING SOUTH. WT-02 SLAB FLOOR TO CEILING, SEAMS AS DRAWN, NO CROWN IN THE ALCOVE. WINDOW 5\'-0" x 4\'-0"',
            'AT A 4\'-0" SILL, TEMPERED, TILE RETURNS INTO THE JAMB. 60" x 33" FREESTANDING TUB, WALL-MOUNTED FILLER CL 2\'-6" WITH HAND SHOWER.']

def tub_side(v, which):
    """Alcove side walls. West: back wall at the left. East: back wall at the right. 24 in. towel bar at the room end."""
    L = ALC_D
    shell(v, L, cut_right=(which == 'E'), cut_left=(which == 'W'))
    C.tile_grid(v, 0, L, 0, H, TILE, show=[(0, L, 0, H)])
    if which == 'W':
        C.freestanding_tub(v, 0.5, 32.9, 22, filler=None); C.towel_bar(v, L - 22, 48, 24)
        pts = [0, 32.9, L - 34, L - 10, L]
    else:
        C.freestanding_tub(v, L - 33.4, 32.9, 22, filler=None); C.towel_bar(v, 22, 48, 24)
        pts = [0, 10, 34, L - 32.9, L]
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points(pts))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 22, 48, H]))
    side = 'WEST' if which == 'W' else 'EAST'
    return [f'TUB ALCOVE {side} WALL. WT-02 SLAB FLOOR TO CEILING, SEAMS AS DRAWN. 24" TOWEL BAR CL 4\'-0" AFF AT THE ROOM END,',
            'REACHED FROM THE TUB' + (' AND FROM THE SHOWER ENTRY (THE OTHER SIDE OF THIS PARTITION).' if which == 'W' else ' AND FROM THE ROOM.')]

# ================================================================== water closet (ID-733), PT-02, crown, base
def wc_south(v):
    L = WC_IN[1] - WC_IN[0]
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    tx = sx(TOILET_X[1]); C.toilet(v, tx, TOILET_X[1] - TOILET_X[0])
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, tx + (TOILET_X[1] - TOILET_X[0]) / 2, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 31.5, H - TRIM['crown'], H]))
    return ['WATER CLOSET SOUTH WALL. ONE-PIECE TOILET PER PLAN, CENTERED ON THE ROOM (PLAN SHOWS IT 1-1/4" EAST OF CENTER).',
            'PT-02, CROWN CM-01, BASE. NO WINDOW. EXHAUST FAN ON THE RCP.']

def wc_east(v):
    """Looking east inside the water closet: door wall at the left, toilet in profile at the right."""
    L = ALC_D
    shell(v, L, crown=[(0, L)], base=[(0, L)], cut_left=True)
    C.toilet_profile(v, L, facing='L', length=28.7)
    C.paper_holder(v, L - 28.7 - 8, 26)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, L - 28.7 - 8, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, 26, H - TRIM['crown'], H]))
    return ['WATER CLOSET EAST WALL. PAPER HOLDER CL 2\'-2" AFF, 8" AHEAD OF THE BOWL. PT-02, CROWN CM-01, BASE.',
            'THE DOOR WALL IS AT THE LEFT, SEE 1.']

def wc_north(v):
    """Inside the water closet looking north: the door wall, hinge at the east jamb (right)."""
    L = WC_IN[1] - WC_IN[0]
    door_x = L - WC_JAMB_E - WC_DOOR
    shell(v, L, crown=[(0, L)], base=[(0, door_x - CS)])
    C.casing(v, door_x, WC_DOOR, HEAD); C.door_leaf(v, door_x, WC_DOOR, HEAD, panels=2, swing='R')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, door_x, door_x + WC_DOOR, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, HEAD, H - TRIM['crown'], H]))
    return ['WATER CLOSET NORTH WALL FROM INSIDE. 2\'-8" TWO-PANEL DOOR CENTERED ON THE WALL, PRIVACY SET, HINGED AT THE EAST JAMB, SWINGS IN.',
            'PT-02, CROWN CM-01, BASE RETURNS AT THE DOOR.']

def wc_west(v):
    """Inside the water closet looking west: the partition to the tub alcove, door wall at the right."""
    L = ALC_D
    shell(v, L, crown=[(0, L)], base=[(0, L)])
    C.toilet_profile(v, 0, facing='R', length=28.7)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, 28.7, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, H - TRIM['crown'], H]))
    return ['WATER CLOSET WEST WALL. PT-02, CROWN CM-01, BASE. NO HARDWARE ON THIS WALL.']

# ================================================================== key plan (ID-730)
def key_plan(sh):
    """Base plan clip of the master bathroom at 3/4 in. scale, centered, with every elevation marker and the towel hardware."""
    import compose_plans as CP
    src = fitz.open(CP.BASE_KEY); sp = src[1]
    clip_disp = fitz.Rect(72, 828, 318, 1030)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    k = 4.0                                                      # 3/16 -> 3/4
    tw, th = clip_disp.width * k, clip_disp.height * k
    ax0, ay0, ax1, ay1 = FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6
    tx = ax0 + (ax1 - ax0 - tw) / 2; ty = ay0 + (ay1 - ay0 - th) / 2 - 10
    target = fitz.Rect(tx, ty, tx + tw, ty + th)
    sh.p.show_pdf_page(target, src, 1, clip=u, rotate=90)
    xref = sh.p.get_contents()[0]; st = sh.p.parent.xref_stream(xref).decode('latin1')
    parts = st.split('q ')
    for i in range(1, len(parts)):
        if 'Do' in parts[i]: parts[i] = f'{target.x0:.2f} {sh.p.rect.height - target.y1:.2f} {target.width:.2f} {target.height:.2f} re W n ' + parts[i]
    sh.p.parent.update_stream(xref, 'q '.join(parts).encode('latin1'))
    sys.path.insert(0, '/home/claude/flrwork/rev1'); import keyclip as KC
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(2, ['MASTER BATH', 'MASTER SHOWER', 'WATER CLOSET'])), 'key plan clip'
    PT_IN = 180 / 160 * k
    def P(x_in, y_in): return (target.x0 + (124.74 - clip_disp.x0) * k + x_in * PT_IN, target.y0 + (857.45 - clip_disp.y0) * k + y_in * PT_IN)
    # cover the base plan's room label and write our own
    a, b = P(40, 30), P(120, 54); sh.rect((a[0], a[1], b[0], b[1]), width=0, color=WHITE, fill=WHITE)
    lx, ly = P(80, 44); sh.text(lx, ly, 'MASTER BATH', 13.0, INK, align='c')
    # markers: (number, sheet, direction, plan x, plan y)
    marks = [(1, 'ID-731', 'N', 80, 58), (2, 'ID-731', 'E', 94, 70), (3, 'ID-731', 'S', 80, 82), (4, 'ID-731', 'W', 66, 70),
             (1, 'ID-732', 'W', 14, 110), (2, 'ID-732', 'S', 21.5, 120), (3, 'ID-732', 'E', 29, 110),
             (4, 'ID-732', 'W', 66, 100), (5, 'ID-732', 'S', 80, 112), (6, 'ID-732', 'E', 94, 100),
             (1, 'ID-733', 'N', 138.7, 94), (2, 'ID-733', 'E', 153, 118), (3, 'ID-733', 'S', 124, 134), (4, 'ID-733', 'W', 124, 118)]
    for n, sheet, d, x, y in marks:
        cx, cy = P(x, y); sh.elev_marker(cx, cy, n, sheet, d, r=11.0)
    g = INK
    def bar(x0, y0, x1, y1, label):
        a, b = P(x0, y0), P(x1, y1); sh.line(a, b, 2.0, g); sh.text(b[0] + 5, (a[1] + b[1]) / 2 + 2, label, 6.0, g)
    bar(49.5, FRONT_Y1 + 10, 49.5, FRONT_Y1 + 34, 'TB 24"')
    bar(110.6, FRONT_Y1 + 10, 110.6, FRONT_Y1 + 34, 'TB 24"')
    for x, y, lab in ((158.0, 10, 'TR'), (2.0, 10, 'TR'), ((PIER_WC[0] + PIER_WC[1]) / 2, FRONT_Y0 - 1.5, 'RH')):
        px, py = P(x, y); sh.rect((px - 3, py - 3, px + 3, py + 3), width=0.6, color=g, fill=WHITE)
        if x > 100: sh.text(px - 6, py + 2.5, lab, 6.0, g, align='r')       # the east wall: label to the room side
        else: sh.text(px + 6, py + 2.5, lab, 6.0, g)
    y = target.y1 + 18; x = target.x0
    for ln in ('KEY PLAN AT 3/4" TO 1\'-0". MARKERS: VIEW NUMBER OVER SHEET NUMBER, ARROW IN THE DIRECTION OF VIEW. ID-731 ROOM, ID-732 SHOWER AND TUB ALCOVE, ID-733 WATER CLOSET.',
               'TB TOWEL BAR, TR HAND TOWEL RING, RH DOUBLE ROBE HOOK. ROOM 13\'-4" x 11\'-7-3/4" TO THE ALCOVE BACKS, PARTITIONS 5", PIERS 10-3/8" AND 10" AT THE ALCOVE LINE.',
               'BASE PLAN IS FOR\'S. THE WATER CLOSET DOOR IS TO BE CENTERED ON ITS WALL (2-1/8" WEST OF WHERE THE PLAN SHOWS IT) AND THE SHOWER DOOR IS CENTERED IN ITS GLASS FRONT, SEE ID-731. THE VANITIES ARE 51" FURNITURE PIECES CENTERED ON THEIR WALLS, NOT THE TWO 4\'-7-1/2" BUILT-IN VANITIES FOR REV 1 SHOWS. THE W.I.C. OPENING GETS A PAIR OF 1\'-6" DOORS.',
               'WT-02 IS LARGE-FORMAT PORCELAIN SLAB (48" x 96" x 1/4", HONED) IN THE SHOWER AND TUB ALCOVE, MITERED OUTSIDE CORNERS, SEAMS AS DRAWN ON ID-732.'):
        from idd_sheet import FREG
        words, cur = ln.split(), ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if FREG.text_length(t, fontsize=6.4) > TB_X - 16 - x and cur: sh.text(x, y, cur, 6.4, MID); y += 9; cur = w
            else: cur = t
        if cur: sh.text(x, y, cur, 6.4, MID); y += 9

ROOM = ((1, 'NORTH ELEVATION - MASTER BATH', ROOM_W, north), (2, 'EAST ELEVATION - MASTER BATH', FRONT_Y0, east),
        (3, 'SOUTH ELEVATION - MASTER BATH', ROOM_W, south), (4, 'WEST ELEVATION - MASTER BATH', FRONT_Y0, west))
ALCOVES = ((1, 'SHOWER - WEST WALL', ALC_D, shower_west), (2, 'SHOWER - SOUTH WALL', SH_IN[1], shower_south), (3, 'SHOWER - EAST WALL', ALC_D, shower_east),
           (4, 'TUB ALCOVE - WEST WALL', ALC_D, lambda v: tub_side(v, 'W')), (5, 'TUB ALCOVE - SOUTH WALL', TUB_WALL[1] - TUB_WALL[0], tub_south),
           (6, 'TUB ALCOVE - EAST WALL', ALC_D, lambda v: tub_side(v, 'E')))
WC = ((1, 'WATER CLOSET - NORTH WALL', WC_IN[1] - WC_IN[0], wc_north), (2, 'WATER CLOSET - EAST WALL', ALC_D, wc_east),
      (3, 'WATER CLOSET - SOUTH WALL', WC_IN[1] - WC_IN[0], wc_south), (4, 'WATER CLOSET - WEST WALL', ALC_D, wc_west))

def draw_views(sh, cells, views, note_size=5.4):
    k = E.SCALES['1/2']
    for cell, (n, title, L, fn) in zip(cells, views):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: 1/2" TO 1\'-0"')
        spec = {'room': 'MASTER BATH', 'view': title, 'length': L, 'ceiling': H}
        origin = E.fit_origin(cell, spec, k)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        notes = fn(v)
        v.text(v.X(0) - 6, v.Y(0) + 7, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 28
        for ln in notes: sh.text(cell[2] - 8, ny, ln, note_size, MID, align='r'); ny += 8

def build():
    doc = fitz.open()
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    s0 = Sheet(doc); s0.frame('MASTER BATH ELEVATIONS', 'KEY PLAN, SCALE: 3/4" TO 1\'-0"', ['MASTER BATH', 'ELEVATIONS KEY PLAN'], 'ID-730', legend_rule=False)
    key_plan(s0)
    s1 = Sheet(doc); s1.frame('MASTER BATH ELEVATIONS', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'MASTER BATH'], 'ID-731', legend_rule=False)
    draw_views(s1, E.layout_cells(frame, 2, 2), ROOM)
    s2 = Sheet(doc); s2.frame('MASTER BATH ELEVATIONS - SHOWER & TUB ALCOVE', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'MASTER BATH SHOWER & TUB'], 'ID-732', legend_rule=False)
    draw_views(s2, E.layout_cells(frame, 3, 2), ALCOVES, note_size=5.0)
    s3 = Sheet(doc); s3.frame('MASTER BATH ELEVATIONS - WATER CLOSET', 'SCALE: 1/2" TO 1\'-0"', ['INTERIOR ELEVATIONS', 'MASTER BATH WATER CLOSET'], 'ID-733', legend_rule=False)
    draw_views(s3, E.layout_cells(frame, 2, 2), WC)
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
