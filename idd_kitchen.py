"""Kitchen components for designed elevations (luxury inset cabinetry, panel-ready appliances), drawn with the idd_components primitives.
All sizes in inches, y up from the finished floor. Cabinet conventions: 36 in. counter (34-3/4 box plus 1-1/4 slab), 4-1/2 in. toe kick,
inset doors and drawer fronts with 2 in. face frame stiles and rails drawn as a reveal line, 7/8 in. fronts, full-height end panels."""
import math
import idd_components as C
from idd_components import _rect, _line, _poly, _ellipse, shadow, HEAVY, OUTLINE, MED, FINE, SHADOW, INK, MID, LIGHT, PALE

COUNTER = 36.0; SLAB = 1.25; TOE = 4.5; BOX_TOP = COUNTER - SLAB
STILE = 2.0          # face frame stile and rail
REVEAL = 0.125       # inset reveal, drawn as the inner line offset

def counter(v, x0, x1, top=COUNTER, slab=SLAB, edge=None, overhang=0.0):
    """Stone counter seen face-on: the slab edge (thick edge when `edge` is given), shadow line under the overhang."""
    e = edge if edge else slab
    _rect(v, x0 - overhang, top - e, x1 + overhang, top, OUTLINE, fill=(1, 1, 1)); shadow(v, x0 - overhang, x1 + overhang, top - e)
    # a mitered edge shows no joint on its face: the apron meets the slab at the arris (45 degrees), so no line is drawn in the band

def toe(v, x0, x1):
    _rect(v, x0, 0, x1, TOE, MED); _line(v, (x0, TOE), (x1, TOE), FINE, MID)

def frame_opening(v, x0, y0, x1, y1):
    """One inset opening in the face frame: the opening line and the front 1/8 in. inside it."""
    _rect(v, x0, y0, x1, y1, MED); _rect(v, x0 + REVEAL, y0 + REVEAL, x1 - REVEAL, y1 - REVEAL, FINE, MID)

def drawer_stack(v, x, w, n=3, top=BOX_TOP, pull='bar', bottom=TOE, depth=24.0):
    """Inset drawer stack: the face frame as a rect with the openings laid out top to bottom (top drawer shallower)."""
    _rect(v, x, bottom, x + w, top, OUTLINE)
    inner = top - bottom - STILE * (n + 1)
    hs = [inner * 0.22] + [inner * (0.78 / (n - 1))] * (n - 1) if n > 1 else [inner]
    y = top - STILE
    for h in hs:
        frame_opening(v, x + STILE, y - h, x + w - STILE, y)
        cy = y - h / 2
        if pull == 'bar': _line(v, (x + w / 2 - min(6, w * 0.2), cy), (x + w / 2 + min(6, w * 0.2), cy), OUTLINE)
        elif pull == 'cup': _poly(v, [(x + w / 2 - 2.5, cy + 0.6), (x + w / 2 + 2.5, cy + 0.6), (x + w / 2 + 1.8, cy - 1.0), (x + w / 2 - 1.8, cy - 1.0)], MED)
        y -= h + STILE

def door_pair_cab(v, x, w, y0, y1, glass=False, pulls=True, muntins=0, depth=24.0):
    """Inset pair of doors between y0 and y1 (a base sink cabinet, an upper, a tall cabinet). `depth` is the box depth from the wall
    (not drawn in elevation; recorded for the plan and the 3-D render, 24 in. unless the cabinet is a true 13 in. upper)."""
    _rect(v, x, y0, x + w, y1, OUTLINE)
    dw = (w - 3 * STILE) / 2
    for i in range(2):
        dx = x + STILE + i * (dw + STILE)
        frame_opening(v, dx, y0 + STILE, dx + dw, y1 - STILE)
        if glass:
            _rect(v, dx + 2.5, y0 + STILE + 2.5, dx + dw - 2.5, y1 - STILE - 2.5, FINE, MID)
            _line(v, (dx + 4, y1 - STILE - 5), (dx + dw * 0.45, y0 + STILE + 4), FINE, PALE)
            for m in range(1, muntins + 1):
                my = y0 + STILE + 2.5 + (y1 - y0 - 2 * STILE - 5) * m / (muntins + 1); _line(v, (dx + 2.5, my), (dx + dw - 2.5, my), FINE, MID)
        if pulls:
            px = dx + dw - 2.2 if i == 0 else dx + 2.2
            py = (y0 + y1) / 2 if (y1 - y0) < 40 else (y0 + 36 if y1 > 60 else y0 + (y1 - y0) * 0.5)
            _line(v, (px, py - 3), (px, py + 3), OUTLINE)

def single_door_cab(v, x, w, y0, y1, hinge='L', glass=False, depth=24.0):
    _rect(v, x, y0, x + w, y1, OUTLINE); frame_opening(v, x + STILE, y0 + STILE, x + w - STILE, y1 - STILE)
    if glass: _rect(v, x + STILE + 2.5, y0 + STILE + 2.5, x + w - STILE - 2.5, y1 - STILE - 2.5, FINE, MID)
    px = x + w - STILE - 2.2 if hinge == 'L' else x + STILE + 2.2
    py = (y0 + y1) / 2 if (y1 - y0) < 40 else y0 + 36
    _line(v, (px, py - 3), (px, py + 3), OUTLINE)

def end_panel(v, x, w, y0, y1):
    _rect(v, x, y0, x + w, y1, OUTLINE); _rect(v, x + 1.5, y0 + 1.5, x + w - 1.5, y1 - 1.5, FINE, MID)

def light_rail(v, x0, x1, y, h=1.5):
    _rect(v, x0, y - h, x1, y, MED); _line(v, (x0 + 1, y - h - 0.3), (x1 - 1, y - h - 0.3), FINE, LIGHT, '[1.5 1.5] 0')   # LED tape

def upper_run(v, x, widths, y0, y1, glass=False, stack=None, muntins=0):
    """Row of upper cabinets of the given widths from x, bottom y0 to top y1; optional stacked row above to `stack` (y)."""
    cx = x
    for w in widths:
        if w >= 24: door_pair_cab(v, cx, w, y0, y1, glass=glass, muntins=muntins)
        else: single_door_cab(v, cx, w, y0, y1, glass=glass)
        if stack:
            if w >= 24: door_pair_cab(v, cx, w, y1, stack, glass=True, muntins=0)
            else: single_door_cab(v, cx, w, y1, stack, glass=True)
        cx += w
    light_rail(v, x, cx, y0)
    return cx

def tall_cab(v, x, w, top, glass_top=None, doors=2, split=None):
    """Tall pantry cabinet from the toe to `top`: lower pair of doors to `split` (default 60), upper pair above, optional glass stack."""
    split = split or 60.0
    _rect(v, x, 0, x + w, top, OUTLINE); toe(v, x, x + w)
    if doors == 2: door_pair_cab(v, x, w, TOE, split); door_pair_cab(v, x, w, split, glass_top or top, glass=False)
    else: single_door_cab(v, x, w, TOE, split); single_door_cab(v, x, w, split, glass_top or top)
    if glass_top: door_pair_cab(v, x, w, glass_top, top, glass=True) if doors == 2 else single_door_cab(v, x, w, glass_top, top, glass=True)

def column(v, x, w, h=84.0, top=None, kind='R', hinge='L'):
    """Panel-ready refrigerator or freezer column (Sub-Zero IC-36R, IC-36FI): one full-height panel door to h, a cabinet above to `top`.
    Integrated columns are single-door units with interior drawers. No door-over-drawer configuration exists at 36 in."""
    _rect(v, x, 0, x + w, h, OUTLINE); toe(v, x, x + w)
    frame_opening(v, x + STILE, TOE + STILE, x + w - STILE, h - STILE)
    px = x + w - STILE - 2.2 if hinge == 'L' else x + STILE + 2.2; _line(v, (px, 40), (px, 52), OUTLINE)
    if top: door_pair_cab(v, x, w, h, top, glass=False) if w >= 24 else single_door_cab(v, x, w, h, top)

def pro_range(v, x, w=48.0, h=36.0, burners=6, griddle=True):
    """48 in. dual-fuel pro range seen from the front: oven doors, knob rail, cooktop rim with the burner grates in plan-ish projection."""
    _rect(v, x, 0, x + w, h, OUTLINE, fill=(1, 1, 1))
    _rect(v, x + 1, 1.5, x + w - 1, 4.5, MED)                                                  # kick/base
    rail_y = h - 5.5
    _rect(v, x + 1, rail_y, x + w - 1, rail_y + 2.6, MED)                                      # control panel
    for i in range(8): _ellipse(v, x + 5 + (w - 10) * i / 7, rail_y + 1.3, 0.9, 0.9, FINE)     # knobs
    if w >= 48:
        _rect(v, x + 1.5, 5, x + w * 0.62 - 1, rail_y - 1, MED); _rect(v, x + w * 0.62 + 1, 5, x + w - 1.5, rail_y - 1, MED)   # two oven doors
        for dx0, dx1 in ((x + 1.5, x + w * 0.62 - 1), (x + w * 0.62 + 1, x + w - 1.5)):
            _rect(v, dx0 + 2, rail_y - 6, dx1 - 2, rail_y - 4.6, OUTLINE); _rect(v, dx0 + 3, 9, dx1 - 3, rail_y - 9, FINE, MID)   # handles, glass
    else:
        _rect(v, x + 1.5, 5, x + w - 1.5, rail_y - 1, MED); _rect(v, x + 3.5, rail_y - 6, x + w - 3.5, rail_y - 4.6, OUTLINE); _rect(v, x + 2.5, 9, x + w - 2.5, rail_y - 9, FINE, MID)
    _rect(v, x - 0.5, h - 0.75, x + w + 0.5, h + 0.75, OUTLINE, fill=(1, 1, 1))                 # cooktop rim
    _line(v, (x, h + 0.75), (x + w, h + 0.75), FINE, MID)

def hood_breast(v, x, w, y0, H, style='plaster', crown_drop=8.0, depth=27.0):
    """Concealed hood in a chimney breast from the hood bottom y0 to the crown: a flat plastered or stone breast, 2 in. proud of the splash."""
    _rect(v, x, y0, x + w, H - crown_drop, OUTLINE)
    _rect(v, x + 0.75, y0 + 0.75, x + w - 0.75, H - crown_drop - 0.75, FINE, LIGHT)
    _line(v, (x, y0), (x + w, y0), HEAVY); shadow(v, x, x + w, y0)
    if style == 'stone':
        _line(v, (x, y0 + (H - crown_drop - y0) / 2), (x + w, y0 + (H - crown_drop - y0) / 2), FINE, MID)   # slab seam

def hood_canopy(v, x, w, y0, H, crown_drop=8.0, mantle=True):
    """Paneled canopy hood: tapered lower body, flat upper chimney, mantle shelf with corbel brackets."""
    taper = 6.0; body = 12.0
    _poly(v, [(x + taper, y0), (x + w - taper, y0), (x + w, y0 + body), (x, y0 + body)], OUTLINE, fill=(1, 1, 1))
    _rect(v, x, y0 + body, x + w, H - crown_drop, OUTLINE)
    _rect(v, x + 3, y0 + body + 3, x + w - 3, H - crown_drop - 4, MED); _rect(v, x + 4.5, y0 + body + 4.5, x + w - 4.5, H - crown_drop - 5.5, FINE, MID)
    if mantle:
        _rect(v, x - 2, y0 + body, x + w + 2, y0 + body + 2.5, OUTLINE, fill=(1, 1, 1)); shadow(v, x - 2, x + w + 2, y0 + body)
        for bx in (x + 2, x + w - 6): _poly(v, [(bx, y0 + body), (bx + 4, y0 + body), (bx + 4, y0 + body - 6), (bx, y0 + body - 1.5)], MED)

def veneer_grain(v, x0, y0, x1, y1):
    """Veneer: three light wavy grain lines across a door."""
    n = 3; h = y1 - y0
    for i in range(n):
        yy = y0 + h * (i + 1) / (n + 1)
        pts = [(x0 + 1.5 + (x1 - x0 - 3) * t / 12, yy + 0.6 * math.sin(t * 1.3 + i)) for t in range(13)]
        _poly(v, pts, FINE, PALE, close=False)

def veneer_door(v, x, w, y0, y1, glass=False, pull='bar', hinge='L', depth=24.0):
    """One inset veneer door in its face frame; glass=True for a glass door with lit shelves behind (recorded for the 3-D render)."""
    _rect(v, x, y0, x + w, y1, OUTLINE); frame_opening(v, x + STILE, y0 + STILE, x + w - STILE, y1 - STILE)
    if glass: _rect(v, x + STILE + 2.5, y0 + STILE + 2.5, x + w - STILE - 2.5, y1 - STILE - 2.5, FINE, MID); _line(v, (x + 4, y1 - 6), (x + w * 0.45, y0 + 5), FINE, PALE)
    else: veneer_grain(v, x + STILE, y0 + STILE, x + w - STILE, y1 - STILE)
    px = x + w - STILE - 2.2 if hinge == 'L' else x + STILE + 2.2
    if pull == 'bar': _line(v, (px, (y0 + y1) / 2 - 3), (px, (y0 + y1) / 2 + 3), OUTLINE)
    elif pull == 'long': _line(v, (px, 30), (px, 66), OUTLINE); _line(v, (px - 0.6, 30), (px - 0.6, 66), FINE, MID)

def drywall_column(v, x, w, H, crown_drop=8.0, depth=26.0):
    """A drywall column or pilaster seen face-on, floor to the crown, `depth` deep off the wall (recorded for the plan and the 3-D render)."""
    _rect(v, x, 0, x + w, H - crown_drop, OUTLINE)

def counter_stool(v, cx, seat=26.0, w=17.0):
    """Counter stool, N.I.C., dashed: seat, four legs, foot ring."""
    _rect(v, cx - w / 2, seat - 2.0, cx + w / 2, seat, FINE, LIGHT, dashes='[2 1.5] 0')
    for lx in (cx - w / 2 + 1.0, cx + w / 2 - 1.0): _line(v, (lx, 0), (lx, seat - 2.0), FINE, LIGHT, '[2 1.5] 0')
    _line(v, (cx - w / 2 + 1.0, 9.0), (cx + w / 2 - 1.0, 9.0), FINE, LIGHT, '[2 1.5] 0')

def floating_shelf(v, x, w, y, thick=2.0):
    _rect(v, x, y, x + w, y + thick, OUTLINE, fill=(1, 1, 1)); shadow(v, x, x + w, y)

def splash_slab(v, x0, x1, y0, y1, seams=()):
    """Stone splash panel: outline, light veining, seam lines."""
    _rect(v, x0, y0, x1, y1, MED)
    for i in range(3):
        _line(v, (x0 + (x1 - x0) * (0.1 + 0.25 * i), y1 - 3), (x0 + (x1 - x0) * (0.3 + 0.25 * i), y0 + 4), FINE, PALE)
    for sx in seams: _line(v, (sx, y0), (sx, y1), FINE, MID)

def pot_filler(v, cx, y):
    _ellipse(v, cx, y, 1.6, 1.6, OUTLINE, fill=(1, 1, 1)); _line(v, (cx, y), (cx + 9, y - 1), MED); _line(v, (cx + 9, y - 1), (cx + 16, y + 1), MED)
    _ellipse(v, cx + 9, y - 1, 0.9, 0.9, FINE); _line(v, (cx + 16, y + 1), (cx + 16, y - 2), MED)

def sink_undermount_front(v, x, w, top=COUNTER):
    """What shows of an undermount sink from the front: the faucet and the cabinet below; the bowl is hidden. Draw the faucet only."""
    cx = x + w / 2
    _rect(v, cx - 0.9, top, cx + 0.9, top + 9, OUTLINE, fill=(1, 1, 1)); _arc_bridge(v, cx, top + 9)
def _arc_bridge(v, cx, y, reach=5.0):
    """Gooseneck: rises from the stem top at (cx, y), arcs east over the bowl and drops to the spout."""
    import math
    arc = [(cx + reach + reach * math.cos(math.radians(a)), y + reach * math.sin(math.radians(a))) for a in range(180, -1, -15)]
    _poly(v, arc + [(cx + 2 * reach, y - 4)], MED, close=False)
    _line(v, (cx + 2 * reach, y - 4), (cx + 2 * reach + 1.5, y - 4), MED)

def sink_cab(v, x, w, bottom=TOE, top=BOX_TOP, front=7.0):
    """Sink base: a pair of doors under a false front (tip-out) the depth of the sink rim."""
    door_pair_cab(v, x, w, bottom, top - front)
    _rect(v, x, top - front, x + w, top, OUTLINE); frame_opening(v, x + STILE, top - front + STILE / 2, x + w - STILE, top - STILE / 2)

def outlet_splash(v, cx, cy=42.0):
    C.outlet(v, cx, cy, horizontal=True)

def island_face(v, L, seating=False, overhang=15.0, top=COUNTER, panels=3):
    """Island long face: seating side = continuous paneled front under the overhang; working side is drawn by the caller with cabinets."""
    if seating:
        _rect(v, 0, 0, L, top - SLAB, OUTLINE); toe(v, 0, L)
        pw = (L - STILE * (panels + 1)) / panels
        for i in range(panels):
            px = STILE + i * (pw + STILE); _rect(v, px, TOE + STILE, px + pw, top - SLAB - STILE, MED); _rect(v, px + 1.5, TOE + STILE + 1.5, px + pw - 1.5, top - SLAB - STILE - 1.5, FINE, MID)

def miter_corner(v, x, top=COUNTER, side='L', thick=2.0):
    """The 45 degree miter where a waterfall meets the top, seen in a long elevation: white-out the butt lines in the corner square,
    redraw the outer arris and the diagonal from the outer corner to the inner corner."""
    x0, x1 = (x, x + thick) if side == 'L' else (x - thick, x)
    wx0, wx1 = (x0 + 0.1, x1 + 0.15) if side == 'L' else (x0 - 0.15, x1 - 0.1)       # cover the butt lines: the waterfall's inner edge and the band's bottom edge inside the corner
    _rect(v, wx0, top - thick - 0.12, wx1, top - 0.1, 0, fill=(1, 1, 1))
    ox = x0 if side == 'L' else x1; ix = x1 if side == 'L' else x0
    _line(v, (ox, top - thick - 0.3), (ox, top), OUTLINE); _line(v, (x0, top), (x1, top), OUTLINE)
    _line(v, (ox, top), (ix, top - thick), FINE)

def waterfall(v, x, w, top=COUNTER, side='L', thick=SLAB):
    """Stone waterfall end seen face-on: the slab leg at the end of the island."""
    x0, x1 = (x, x + thick) if side == 'L' else (x - thick, x)
    _rect(v, x0, 0, x1, top, OUTLINE, fill=(1, 1, 1))

def stool_clear(v, L, top=COUNTER, knee=15.0):
    _line(v, (0, top - SLAB - knee), (L, top - SLAB - knee), FINE, LIGHT, '[2 2] 0')
