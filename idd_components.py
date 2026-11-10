"""Drawn component library for interior elevations: real profiles instead of boxes, with a line weight hierarchy.
Every function draws in inches on an ElevationView-like canvas `v` (v.X(), v.Y(), v.k pt per inch, v.p the page).
Weights: HEAVY 0.9 (cut walls, floor), OUTLINE 0.6 (object silhouettes), MED 0.4 (panels, rails, frames), FINE 0.25 (detail, hatch, joints), SHADOW 1.1 (shade lines under projections)."""
import math, pymupdf as fitz
from idd_std import TRIM
INK = (0.15, 0.15, 0.15); MID = (0.4, 0.4, 0.4); LIGHT = (0.68, 0.68, 0.68); PALE = (0.82, 0.82, 0.82); TILE = (0.55, 0.55, 0.55)
HEAVY, OUTLINE, MED, FINE, SHADOW = 0.9, 0.6, 0.4, 0.25, 1.1

def _line(v, a, b, w=MED, c=None, dashes=None):
    c = INK if c is None else c   # resolved at call time so beyond() can grey a whole component
    sh = v.p.new_shape(); sh.draw_line(fitz.Point(v.X(a[0]), v.Y(a[1])), fitz.Point(v.X(b[0]), v.Y(b[1]))); sh.finish(color=c, width=w, dashes=dashes); sh.commit()
def _rect(v, x0, y0, x1, y1, w=MED, c=None, fill=None, dashes=None):
    c = INK if c is None else c
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)   # normalize so mirrored (right-to-left) rects still draw
    sh = v.p.new_shape(); sh.draw_rect(fitz.Rect(v.X(x0), v.Y(y1), v.X(x1), v.Y(y0))); sh.finish(color=c, width=w, fill=fill, dashes=dashes); sh.commit()
def _poly(v, pts, w=MED, c=None, fill=None, close=True):
    c = INK if c is None else c
    sh = v.p.new_shape(); sh.draw_polyline([fitz.Point(v.X(x), v.Y(y)) for x, y in pts]); sh.finish(color=c, width=w, fill=fill, closePath=close); sh.commit()
def _arc(v, cx, cy, r, a0, a1, w=MED, c=None):
    c = INK if c is None else c
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    _poly(v, pts, w, c, close=False)
def _ellipse(v, cx, cy, rx, ry, w=MED, c=INK, fill=None, dashes=None):
    pts = [(cx + rx * math.cos(math.radians(t)), cy + ry * math.sin(math.radians(t))) for t in range(0, 360, 10)]
    sh = v.p.new_shape(); sh.draw_polyline([fitz.Point(v.X(x), v.Y(y)) for x, y in pts]); sh.finish(color=c, width=w, fill=fill, closePath=True, dashes=dashes); sh.commit()
def shadow(v, x0, x1, y):
    """Shade line under a projecting edge (counter, shelf, cap): reads as depth."""
    _line(v, (x0, y - 0.4), (x1, y - 0.4), SHADOW)

# ---------------------------------------------------------------- trim
def base(v, x0, x1, h=None, cap=0.75):
    """Base from the TRIM block (8-1/2 at 10 ft): board, cap, shoe line."""
    h = TRIM['base'] if h is None else h
    _rect(v, x0, 0, x1, h, OUTLINE); _line(v, (x0, h - cap), (x1, h - cap), FINE, MID); _line(v, (x0, h - cap * 2.2), (x1, h - cap * 2.2), FINE, LIGHT)
    _line(v, (x0, 0.75), (x1, 0.75), FINE, LIGHT)   # shoe
def crown(v, x0, x1, H, drop=None):
    """Crown from the TRIM block (8 in. drop at 10 ft, built up: frieze, bed mould, crown)."""
    drop = TRIM['crown'] if drop is None else drop
    _rect(v, x0, H - drop, x1, H, OUTLINE)
    if TRIM['crown_built_up'] and drop > 7:
        for f, w, c in ((0.3, FINE, MID), (0.42, FINE, LIGHT), (0.62, MED, INK), (0.8, FINE, LIGHT)): _line(v, (x0, H - drop * f), (x1, H - drop * f), w, c)
    else:
        for f, w, c in ((0.3, FINE, MID), (0.55, FINE, LIGHT), (0.8, FINE, MID)): _line(v, (x0, H - drop * f), (x1, H - drop * f), w, c)
def casing(v, x, w, head, cs=None, sill=0):
    """Door or opening casing from the TRIM block (5 in. face at 10 ft): head casing over leg casings, mitered, backband line, 1/4 in. reveal to the jamb."""
    cs = TRIM['casing'] if cs is None else cs
    _rect(v, x - cs, sill, x, head + cs, OUTLINE); _rect(v, x + w, sill, x + w + cs, head + cs, OUTLINE); _rect(v, x - cs, head, x + w + cs, head + cs, OUTLINE)
    _line(v, (x - cs, head + cs), (x, head), FINE, MID); _line(v, (x + w + cs, head + cs), (x + w, head), FINE, MID)
    _rect(v, x - 0.25, sill, x + w + 0.25, head + 0.25, FINE, MID)
    _line(v, (x - cs + 1.0, sill), (x - cs + 1.0, head + cs - 1.0), FINE, LIGHT); _line(v, (x + w + cs - 1.0, sill), (x + w + cs - 1.0, head + cs - 1.0), FINE, LIGHT); _line(v, (x - cs + 1.0, head + cs - 1.0), (x + w + cs - 1.0, head + cs - 1.0), FINE, LIGHT)   # backband
def chair_rail(v, x0, x1, y, h=None):
    h = TRIM['cap'] if h is None else h
    _rect(v, x0, y, x1, y + h, OUTLINE); _line(v, (x0, y + h * 0.45), (x1, y + h * 0.45), FINE, MID); shadow(v, x0, x1, y)

# ---------------------------------------------------------------- openings
def door_leaf(v, x, w, head, panels=2, swing='L', knob=False, pull='R', glass='clear', lites=None):
    """panels: 2 (two-panel), 1, 'glass' (full lite, divided per the set rule), 'lite_over_panel' (glass over one raised panel,
    the front door the owner picked 11.09.26: 2 x 2 lites per leaf over a bottom panel). glass: 'clear' or 'hammered'."""
    _rect(v, x, 0, x + w, head, OUTLINE)
    st = 4.5; rail_b = 9; rail_t = 4.5; mid = 4.5
    inner = [(x + st, rail_b), (x + w - st, head - rail_t)]
    if panels == 'glass':   # full-lite door: one glass panel in a stile-and-rail frame
        _rect(v, x + st, rail_b, x + w - st, head - rail_t, MED); _rect(v, x + st + 0.75, rail_b + 0.75, x + w - st - 0.75, head - rail_t - 0.75, FINE, LIGHT)
        cr = lites if lites else (None, None)
        glazing(v, x + st + 0.75, rail_b + 0.75, x + w - st - 0.75, head - rail_t - 0.75, glass=glass, cols=cr[0], rows=cr[1])
    elif panels == 'lite_over_panel':
        rail_b = 9.0; lock = 36.0; mid = 5.0          # bottom rail, lock rail top at 36", the glass above it
        _rect(v, x + st, rail_b, x + w - st, lock - mid, MED); _rect(v, x + st + 1.5, rail_b + 1.5, x + w - st - 1.5, lock - mid - 1.5, FINE, MID)
        _rect(v, x + st, lock, x + w - st, head - rail_t, MED); _rect(v, x + st + 0.75, lock + 0.75, x + w - st - 0.75, head - rail_t - 0.75, FINE, LIGHT)
        cr = lites if lites else (2, 2)
        glazing(v, x + st + 0.75, lock + 0.75, x + w - st - 0.75, head - rail_t - 0.75, glass=glass, cols=cr[0], rows=cr[1])
    elif panels == 2:
        split = rail_b + (head - rail_t - rail_b) * 0.62
        _rect(v, x + st, rail_b, x + w - st, split - mid / 2, MED); _rect(v, x + st + 0.75, rail_b + 0.75, x + w - st - 0.75, split - mid / 2 - 0.75, FINE, MID)
        _rect(v, x + st, split + mid / 2, x + w - st, head - rail_t, MED); _rect(v, x + st + 0.75, split + mid / 2 + 0.75, x + w - st - 0.75, head - rail_t - 0.75, FINE, MID)
    else:
        _rect(v, x + st, rail_b, x + w - st, head - rail_t, MED); _rect(v, x + st + 0.75, rail_b + 0.75, x + w - st - 0.75, head - rail_t - 0.75, FINE, MID)
    if swing is None:   # pocket or sliding leaf: recessed pull at the leading edge (pull='L' or 'R'), no swing marks
        px = x + w - 3.5 if pull == 'R' else x + 2.3
        _rect(v, px, 36, px + 1.2, 40, OUTLINE); return
    hinge, far = (x, x + w) if swing == 'L' else (x + w, x)
    _line(v, (far, 0), (hinge, head / 2), FINE, MID, '[2 1.5] 0'); _line(v, (far, head), (hinge, head / 2), FINE, MID, '[2 1.5] 0')   # the lines meet at the hinge side
    lever = far - 3 if far > hinge else far + 3
    hy = 33.5 if panels == 'lite_over_panel' else 38      # on the lock rail
    if knob: _ellipse(v, lever, hy, 1.4, 1.4, MED); _ellipse(v, lever, hy, 0.6, 0.6, FINE); return
    _ellipse(v, lever, hy, 0.9, 0.9, FINE); _line(v, (lever, hy), (lever + (-3.5 if far > hinge else 3.5), hy), MED)
def cased_opening(v, x, w, head, beyond=None):
    """Cased opening; `beyond` draws what is seen through it (callable drawing in the opening at a lighter weight)."""
    casing(v, x, w, head)
    if beyond: beyond(v, x, w, head)
# ---------------------------------------------------------------- divided lites (owner 11.09.26: "many window panes. all glass doors and
# windows in house to match"). The pattern follows FOR's front elevation: true divided lites, panes about 10" wide and taller than wide.
DIVIDED = True
PANE_W = 10.5          # target pane width, in.
PANE_ASPECT = 1.55     # pane height / width
PANE_REDUCE = 0.7      # owner 11.09.26 evening: about 30% fewer panes than the first pass
def lite_grid(gw, gh, pane_w=None, aspect=None):
    """(cols, rows) for a glass panel gw x gh in.: the first-pass grid (panes about PANE_W wide, PANE_ASPECT tall) with the pane
    count cut to PANE_REDUCE, keeping two columns on narrow leaves so the pattern still reads as divided."""
    pane_w = PANE_W if pane_w is None else pane_w; aspect = PANE_ASPECT if aspect is None else aspect
    cols = max(1, round(gw / pane_w)); rows = max(1, round(gh / (gw / cols * aspect)))
    n = cols * rows * PANE_REDUCE
    c2 = cols if cols <= 2 else max(2, round(cols * 0.85))
    r2 = max(min(2, rows), round(n / c2))
    return c2, r2
def muntins(v, x0, y0, x1, y1, cols=None, rows=None, bar=0.875):
    """Muntin grid in a glass panel (x0..x1, y0..y1 in.): every bar a pair of lines at one weight, verticals run through,
    horizontals stop at them (review 11.09.26: no mix of single and double lines)."""
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
    c_, r_ = lite_grid(x1 - x0, y1 - y0)
    cols = c_ if cols is None else cols; rows = r_ if rows is None else rows
    W_ = (1, 1, 1)
    xs = [x0 + (x1 - x0) * i / cols for i in range(1, cols)]; ys = [y0 + (y1 - y0) * j / rows for j in range(1, rows)]
    for my in ys: _rect(v, x0, my - bar / 2, x1, my + bar / 2, 0.01, W_, fill=W_)
    for mx in xs: _rect(v, mx - bar / 2, y0, mx + bar / 2, y1, 0.01, W_, fill=W_)
    for mx in xs:
        for e in (-bar / 2, bar / 2): _line(v, (mx + e, y0), (mx + e, y1), FINE)
    stops = [x0] + [e for mx in xs for e in (mx - bar / 2, mx + bar / 2)] + [x1]
    for my in ys:
        for e in (-bar / 2, bar / 2):
            for a_, b_ in zip(stops[0::2], stops[1::2]): _line(v, (a_, my + e), (b_, my + e), FINE)
def hammered(v, x0, y0, x1, y1, pitch=2.2):
    """Hammered (obscure) glass: a regular field of short pale arcs, so it reads as textured, not clear (owner 11.09.26)."""
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
    j = 0; y = y0 + pitch * 0.6
    while y < y1 - pitch * 0.3:
        x = x0 + pitch * (0.5 if j % 2 else 1.0)
        while x < x1 - pitch * 0.4:
            _arc(v, x, y, pitch * 0.28, 200, 340, FINE, PALE); x += pitch
        y += pitch * 0.85; j += 1
def glazing(v, x0, y0, x1, y1, divided=None, glass='clear', cols=None, rows=None):
    """One glass panel: clear (glare lines) or hammered, with divided lites when the set rule is on."""
    divided = DIVIDED if divided is None else divided
    if glass == 'hammered': hammered(v, x0, y0, x1, y1)
    if divided: muntins(v, x0, y0, x1, y1, cols, rows)
    elif glass != 'hammered':
        w_ = x1 - x0; h_ = y1 - y0
        _line(v, (x0 + 2, y1 - 3), (x0 + w_ * 0.45, y0 + h_ * 0.45), FINE, PALE); _line(v, (x0 + 4, y1 - 3), (x0 + w_ * 0.6, y0 + h_ * 0.45), FINE, PALE)
def rev_cloud(v, x0, y0, x1, y1, tag='1', pad=3.0, tag_at='tr'):
    """Revision cloud around an elevation region (in., view coordinates), padded `pad` in."""
    import idd_sheet
    xa, xb = sorted((v.X(x0 - pad), v.X(x1 + pad))); ya, yb = sorted((v.Y(y0 - pad), v.Y(y1 + pad)))
    idd_sheet.rev_cloud_pt(v.p, fitz.Rect(xa, ya, xb, yb), tag, tag_at=tag_at)

def window(v, x, w, sill, head, lites=2, cs=None, trim=True, glass='clear'):
    cs = TRIM['casing'] if cs is None else cs
    if trim: casing(v, x, w, head, cs, sill); _rect(v, x - cs, sill - 1.5, x + w + cs + 1, sill, OUTLINE); _rect(v, x - cs + 0.5, sill - 1.5 - TRIM['cap'], x + w + cs - 0.5, sill - 1.5, OUTLINE)   # stool and apron
    else: _rect(v, x - 1, sill - 1, x + w + 1, head + 1, OUTLINE)   # tile return into the jamb, no casing
    _rect(v, x, sill, x + w, head, OUTLINE); lw = w / lites
    for i in range(lites):
        gx = x + i * lw; _rect(v, gx + 1.25, sill + 1.25, gx + lw - 1.25, head - 1.25, MED)
        glazing(v, gx + 1.25, sill + 1.25, gx + lw - 1.25, head - 1.25, glass=glass)

# ---------------------------------------------------------------- bath
def vanity_furniture(v, x, w, h=34, counter=1.25, legs=True, drawers=3, sink_center=None, doors_center=True, faucet_style='deck'):
    """Furniture-style vanity: stone top with a shadow line, apron, door pair at the sink, drawer stacks either side, turned legs or plinth."""
    top = h; _rect(v, x - 0.75, top, x + w + 0.75, top + counter, OUTLINE); shadow(v, x - 0.75, x + w + 0.75, top)
    leg_h = 5 if legs else 0; box_b = leg_h
    _rect(v, x, box_b, x + w, top, OUTLINE)
    if legs:
        for lx in (x + 1.0, x + w - 3.0): _rect(v, lx, 0, lx + 2.0, leg_h, MED); _line(v, (lx + 0.3, 1.2), (lx + 1.7, 1.2), FINE, MID)
    else:
        _rect(v, x + 2, 0, x + w - 2, 4, MED)
    sc = sink_center if sink_center is not None else x + w / 2
    dw = 24 if w >= 48 else 18
    # doors under the sink
    _rect(v, sc - dw / 2, box_b + 1, sc + dw / 2, top - 1.5, MED)
    _line(v, (sc, box_b + 1), (sc, top - 1.5), MED)
    for dx in (sc - dw / 2 + 1, sc + 1): _rect(v, dx, box_b + 2, dx + dw / 2 - 2, top - 2.5, FINE, MID)
    for px in (sc - 1.6, sc + 1.6): _line(v, (px, top - 11), (px, top - 7), OUTLINE)
    # drawer stacks either side
    for a, b in ((x + 1, sc - dw / 2 - 1), (sc + dw / 2 + 1, x + w - 1)):
        if b - a < 8: continue
        n = drawers; dh = (top - 1.5 - (box_b + 1)) / n
        for i in range(n):
            y0 = box_b + 1 + i * dh; _rect(v, a, y0 + 0.5, b, y0 + dh - 0.5, MED); _rect(v, a + 1, y0 + 1.5, b - 1, y0 + dh - 1.5, FINE, MID)
            _line(v, ((a + b) / 2 - 2.5, y0 + dh / 2), ((a + b) / 2 + 2.5, y0 + dh / 2), OUTLINE)
    if faucet_style == 'deck': faucet(v, sc, top + counter)
    elif faucet_style == 'wall': faucet_wall(v, sc, top + counter + 5.0)
    basin_hidden(v, sc, top, 17, 6)
def vanity_floating(v, x, w, h=34, counter=1.25, box_h=14, drawers=2, sink_center=None):
    top = h; _rect(v, x, top, x + w, top + counter, OUTLINE); shadow(v, x, x + w, top)
    _rect(v, x, top - box_h, x + w, top, OUTLINE)
    sc = sink_center if sink_center is not None else x + w / 2
    n = drawers; dh = box_h / n
    for i in range(n):
        y0 = top - box_h + i * dh; _rect(v, x + 0.5, y0 + 0.5, x + w - 0.5, y0 + dh - 0.5, MED)
        _line(v, (x + w / 2 - 4, y0 + dh - 1.2), (x + w / 2 + 4, y0 + dh - 1.2), OUTLINE)   # finger pull
    _line(v, (x + 1, top - box_h - 0.6), (x + w - 1, top - box_h - 0.6), FINE, LIGHT, '[1.5 1.5] 0')   # LED under the box
    faucet(v, sc, top + counter); basin_hidden(v, sc, top, 17, 6)
def faucet(v, cx, y, h=7):
    _rect(v, cx - 0.6, y, cx + 0.6, y + h - 2, MED); _arc(v, cx + 1.0, y + h - 2, 2.2, 90, 180, MED); _line(v, (cx + 1.0, y + h + 0.2), (cx + 3.2, y + h + 0.2), MED)
    _line(v, (cx + 3.2, y + h + 0.2), (cx + 3.2, y + h - 1.5), MED)
    for hx in (cx - 4, cx + 4): _rect(v, hx - 0.7, y, hx + 0.7, y + 1.6, FINE); _line(v, (hx - 1.2, y + 1.6), (hx + 1.2, y + 1.6), FINE)
def faucet_wall(v, cx, y, spread=8.0):
    """Wall-mounted faucet seen from the front: round spout escutcheon with the spout coming toward the viewer and turning down, lever handles either side."""
    _ellipse(v, cx, y, 1.5, 1.5, OUTLINE, fill=(1, 1, 1)); _ellipse(v, cx, y, 0.9, 0.9, FINE, MID)
    _poly(v, [(cx - 0.9, y - 0.4), (cx + 0.9, y - 0.4), (cx + 0.9, y - 3.2), (cx - 0.9, y - 3.2)], OUTLINE, fill=(1, 1, 1))   # spout nose, foreshortened
    _ellipse(v, cx, y - 3.2, 0.9, 0.35, MED)
    for hx, d in ((cx - spread, -1), (cx + spread, 1)):
        _ellipse(v, hx, y, 1.25, 1.25, OUTLINE, fill=(1, 1, 1)); _ellipse(v, hx, y, 0.5, 0.5, FINE, MID)
        _line(v, (hx, y), (hx + d * 3.0, y), OUTLINE)   # lever, pointing outward
def basin_hidden(v, cx, top, w, d):
    _ellipse(v, cx, top - d / 2 - 0.5, w / 2, d / 2, FINE, MID, dashes='[1.5 1.5] 0')   # under-mount basin, hidden: dashed
def vanity_end(v, x, depth=20.1, h=34, counter=1.25, legs=True, open_to='R'):
    """Furniture vanity seen end-on (the return wall elevation): side panel with a recessed panel, counter edge with overhang, legs."""
    x0, x1 = (x, x + depth) if open_to == 'R' else (x - depth, x)
    leg_h = 5 if legs else 0
    _rect(v, x0, leg_h, x1, h, OUTLINE); _rect(v, x0 + 2, leg_h + 2, x1 - 2, h - 2.5, MED); _rect(v, x0 + 3, leg_h + 3, x1 - 3, h - 3.5, FINE, MID)
    ov0, ov1 = (x0, x1 + 0.75) if open_to == 'R' else (x0 - 0.75, x1)
    _rect(v, ov0, h, ov1, h + counter, OUTLINE); shadow(v, ov0, ov1, h)
    if legs:
        for lx in (x0 + 1.0, x1 - 3.0): _rect(v, lx, 0, lx + 2.0, leg_h, MED)
    else: _rect(v, x0 + 2, 0, x1 - 2, 4, MED)
def toilet_profile(v, x, facing='L', length=28.7, seat_h=17, tank_h=31):
    """Toilet seen from the side: tank against the wall at x, bowl projecting toward `facing`. Filled white so it masks the base behind it."""
    d = -1 if facing == 'L' else 1
    bx = x + d * 8; fx = x + d * length
    _poly(v, [(x, seat_h + 1), (fx, seat_h + 1), (fx, seat_h), (fx - d * 1.5, seat_h - 6), (fx - d * 7, seat_h - 12), (x + d * 16, seat_h - 14),
              (x + d * 16, 0), (x + d * 4, 0), (x + d * 4, seat_h - 10), (x + d * 2, seat_h - 8)], OUTLINE, fill=(1, 1, 1))
    _rect(v, x, seat_h + 1, bx, tank_h, OUTLINE, fill=(1, 1, 1)); _rect(v, x + d * 0.5, tank_h, x + d * 8.5, tank_h + 1.5, OUTLINE, fill=(1, 1, 1))   # tank and lid
    _line(v, (bx, seat_h - 1.5), (fx - d * 2, seat_h - 1.5), FINE, MID)   # seat
def paper_holder(v, cx, y=26):
    _rect(v, cx - 2.75, y - 0.5, cx + 2.75, y + 0.5, OUTLINE); _ellipse(v, cx, y, 2.4, 2.4, FINE, MID); _rect(v, cx - 0.6, y - 1.5, cx + 0.6, y + 1.5, FINE)
def tub_filler_wall(v, cx, y=30, spread=8.0):
    _ellipse(v, cx, y, 1.6, 1.6, OUTLINE, fill=(1, 1, 1)); _poly(v, [(cx - 1.1, y - 0.4), (cx + 1.1, y - 0.4), (cx + 1.1, y - 4.0), (cx - 1.1, y - 4.0)], OUTLINE, fill=(1, 1, 1)); _ellipse(v, cx, y - 4.0, 1.1, 0.4, MED)
    for hx, d in ((cx - spread, -1), (cx + spread, 1)):
        _ellipse(v, hx, y, 1.25, 1.25, OUTLINE, fill=(1, 1, 1)); _line(v, (hx, y), (hx + d * 3.0, y), OUTLINE)
    _ellipse(v, cx, y + 6, 1.25, 1.25, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - 0.5, y + 6, cx + 0.5, y + 9, MED)   # hand shower holder
def glass_edge(v, x, h=84):
    """Frameless glass seen edge-on: a heavy vertical line with the header channel stub."""
    _line(v, (x, 0), (x, h), OUTLINE); _line(v, (x - 0.5, h), (x + 0.5, h), MED)
def door_pair(v, x, w, head, panels=2, glass='clear', lites=None, cased=True):
    """Pair of swinging doors in a cased opening, each leaf hinged at its jamb."""
    if cased: casing(v, x, w, head)
    door_leaf(v, x, w / 2, head, panels, swing='L', glass=glass, lites=lites); door_leaf(v, x + w / 2, w / 2, head, panels, swing='R', glass=glass, lites=lites)
def arched_door_pair(v, x, w, spring, panels=1, cased=True, cs=None, hw='lever'):
    """Pair of swinging leaves under a semicircular arched head (apex = spring + w/2): arched casing, leaves cut to the arch,
    one raised panel per leaf following the arch (panels=1) or a lower panel under an arched upper panel (panels=2)."""
    r = w / 2.0; cx = x + r; apex = spring + r
    cs = TRIM['casing'] if cs is None else cs
    def top(px, rad=r): return spring + math.sqrt(max(0.0, rad * rad - (px - cx) ** 2))
    def arc_pts(x0, x1, rad, n=24):            # sampled by angle so the head stays concentric with the casing right down to the spring line
        a0 = math.acos(max(-1.0, min(1.0, (x0 - cx) / rad))); a1 = math.acos(max(-1.0, min(1.0, (x1 - cx) / rad)))
        return [(cx + rad * math.cos(a0 + (a1 - a0) * i / n), spring + rad * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    if cased:
        _poly(v, [(x - cs, 0), (x - cs, spring)] + [(cx + (r + cs) * math.cos(math.radians(180 - 180 * i / 36)), spring + (r + cs) * math.sin(math.radians(180 - 180 * i / 36))) for i in range(37)]
              + [(x + w + cs, spring), (x + w + cs, 0)], OUTLINE, close=False)
        _line(v, (x, 0), (x, spring), OUTLINE); _line(v, (x + w, 0), (x + w, spring), OUTLINE); _arc(v, cx, spring, r, 0, 180, OUTLINE)
        _line(v, (x - cs, spring), (x, spring), FINE, MID); _line(v, (x + w, spring), (x + w + cs, spring), FINE, MID)   # leg to arch joint
        _line(v, (x - cs + 1.0, 0), (x - cs + 1.0, spring), FINE, LIGHT); _line(v, (x + w + cs - 1.0, 0), (x + w + cs - 1.0, spring), FINE, LIGHT)
        _arc(v, cx, spring, r + cs - 1.0, 0, 180, FINE, LIGHT)                                      # backband
        _arc(v, cx, spring, r + 0.25, 0, 180, FINE, MID)                                            # reveal to the jamb
    st, rail_b, rail_t, mid = 4.5, 9.0, 4.5, 4.5
    for (x0, x1, swing) in ((x, cx, 'L'), (cx, x + w, 'R')):
        _poly(v, [(x0, 0), (x1, 0)] + arc_pts(x1, x0, r), OUTLINE)
        px0, px1 = x0 + st, x1 - st; rp = r - rail_t
        lo = rail_b
        if panels == 2:
            split = rail_b + (spring - rail_b) * 0.62
            _rect(v, px0, rail_b, px1, split - mid / 2, MED); _rect(v, px0 + 0.75, rail_b + 0.75, px1 - 0.75, split - mid / 2 - 0.75, FINE, MID)
            lo = split + mid / 2
        _poly(v, [(px0, lo), (px1, lo)] + arc_pts(px1, px0, rp), MED)
        _poly(v, [(px0 + 0.75, lo + 0.75), (px1 - 0.75, lo + 0.75)] + arc_pts(px1 - 0.75, px0 + 0.75, rp - 0.75), FINE, MID)
        hinge, far = (x0, x1) if swing == 'L' else (x1, x0)
        _line(v, (far, 0), (hinge, apex / 2), FINE, MID, '[2 1.5] 0'); _line(v, (far, top(far)), (hinge, apex / 2), FINE, MID, '[2 1.5] 0')
        lever = far - 3 if far > hinge else far + 3
        if hw == 'pull': _rect(v, lever - 0.35, 34, lever + 0.35, 46, MED, fill=(1, 1, 1))     # vertical pull, ball catch at the head
        else: _ellipse(v, lever, 38, 0.9, 0.9, FINE); _line(v, (lever, 38), (lever + (-3.5 if far > hinge else 3.5), 38), MED)
    return apex
def cut_wall(v, x, w, H, fill=(0.3, 0.3, 0.3)):
    """A partition seen end-on inside the view (alcove walls): solid poche to the ceiling."""
    _rect(v, x, 0, x + w, H, OUTLINE, fill=fill)
def pilaster(v, x, w, H, shadow_side='R'):
    """A short wall stub projecting toward the viewer: filled white (masks trim behind it) with a shadow at its edge."""
    _rect(v, x, 0, x + w, H, OUTLINE, fill=(1, 1, 1))
    sx = x + w - 0.5 if shadow_side == 'R' else x + 0.5
    _line(v, (sx, 0), (sx, H), SHADOW, INK)
def mirror_framed(v, x, w, y, h, frame=2.0, bevel=True):
    _rect(v, x, y, x + w, y + h, OUTLINE); _rect(v, x + frame, y + frame, x + w - frame, y + h - frame, MED)
    if bevel: _rect(v, x + frame + 1, y + frame + 1, x + w - frame - 1, y + h - frame - 1, FINE, LIGHT)
    _line(v, (x + frame + 3, y + h - frame - 3), (x + w * 0.45, y + frame + 3), FINE, PALE)
    _line(v, (x + frame + 6, y + h - frame - 3), (x + w * 0.55, y + frame + 3), FINE, PALE)
def mirror_panel(v, x, w, y, h):
    """Frameless mirror panel to the ceiling or trim, polished edge."""
    _rect(v, x, y, x + w, y + h, OUTLINE); _rect(v, x + 0.5, y + 0.5, x + w - 0.5, y + h - 0.5, FINE, LIGHT)
    _line(v, (x + 4, y + h - 6), (x + w * 0.4, y + 6), FINE, PALE); _line(v, (x + 8, y + h - 6), (x + w * 0.5, y + 6), FINE, PALE)
def sconce(v, cx, cy, style='cylinder'):
    """Backplate, arm and shade; centerline tick."""
    if style == 'cylinder':   # 4-1/2 in. round backplate, 3 in. cylinder centered on it (CL = box center)
        _ellipse(v, cx, cy, 2.25, 2.25, MED)
        _rect(v, cx - 1.5, cy - 4.5, cx + 1.5, cy + 4.5, OUTLINE, fill=(1, 1, 1))
        _line(v, (cx - 1.5, cy + 3.9), (cx + 1.5, cy + 3.9), FINE, MID); _line(v, (cx - 1.5, cy - 3.9), (cx + 1.5, cy - 3.9), FINE, MID)
    else:   # shaded: backplate at the CL, short arm, tapered fabric shade above
        _ellipse(v, cx, cy, 2.0, 2.0, MED); _ellipse(v, cx, cy, 0.8, 0.8, FINE, MID)
        _line(v, (cx, cy + 2.0), (cx, cy + 3.5), MED)
        _poly(v, [(cx - 3.75, cy + 3.5), (cx + 3.75, cy + 3.5), (cx + 2.75, cy + 10.5), (cx - 2.75, cy + 10.5)], OUTLINE)
        _line(v, (cx - 3.4, cy + 6), (cx + 3.4, cy + 6), FINE, LIGHT)
def toilet(v, x, w=15, tank=True):
    """Toilet seen from the front, filled white so the base behind it is masked."""
    cx = x + w / 2
    _poly(v, [(cx - w / 2, 15), (cx - w / 2 + 2, 2), (cx + w / 2 - 2, 2), (cx + w / 2, 15)], OUTLINE, fill=(1, 1, 1))
    _ellipse(v, cx, 15, w / 2, 1.2, OUTLINE, fill=(1, 1, 1))
    _line(v, (cx - w / 2, 17), (cx + w / 2, 17), OUTLINE); _line(v, (cx - w / 2 + 1, 18.5), (cx + w / 2 - 1, 18.5), MED)
    if tank: _rect(v, cx - w / 2 + 0.5, 17, cx + w / 2 - 0.5, 30, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - w / 2 - 0.5, 30, cx + w / 2 + 0.5, 31.5, OUTLINE, fill=(1, 1, 1))
def freestanding_tub(v, x, w=60, h=22, filler='deck'):
    """Freestanding tub seen from the side: soft body curving in to a plinth, flat rim band."""
    cx = x + w / 2
    body = [(x, h), (x + 0.4, h - 6), (x + 1.4, h - 12), (x + 3.2, 5), (x + 5.5, 1.8), (x + 9, 0.8), (x + w - 9, 0.8), (x + w - 5.5, 1.8), (x + w - 3.2, 5), (x + w - 1.4, h - 12), (x + w - 0.4, h - 6), (x + w, h)]
    _poly(v, body, OUTLINE, close=False)
    _line(v, (x - 0.6, h), (x + w + 0.6, h), OUTLINE); _line(v, (x + 0.6, h - 1.5), (x + w - 0.6, h - 1.5), FINE, MID)   # rim band
    _line(v, (x + 10, 2.4), (x + w - 10, 2.4), FINE, LIGHT)   # plinth shade
    if filler == 'deck': _rect(v, cx - 0.5, h, cx + 0.5, h + 7, MED); _arc(v, cx + 1.5, h + 7, 2, 90, 180, MED); _line(v, (cx + 1.5, h + 9), (cx + 4, h + 9), MED)   # tub filler
def shower_glass(v, x, w, h=84, door_w=28, door_at='R'):
    _rect(v, x, 0, x + w, h, OUTLINE); _rect(v, x + 0.75, 0.75, x + w - 0.75, h - 0.75, FINE, LIGHT)
    if door_w > 0:
        dx = x + w - door_w if door_at == 'R' else x
        _line(v, (dx, 0), (dx, h), MED)
        px = dx + door_w - 3.2 if door_at == 'L' else dx + 2
        _rect(v, px, 40, px + 1.2, 50, OUTLINE)   # pull at the latch side
    if w >= 20:
        for i in range(3): _line(v, (x + 3 + i * 2.5, h - 4), (x + 3 + i * 2.5 + 10, h - 16), FINE, PALE)
    _line(v, (x, h), (x + w, h), MED)   # header channel
def shower_door_centered(v, x, w, h=96, door_w=28, hinge='L'):
    """Frameless glass front filling an opening: a swing door centered between two equal fixed panels, drawn like any other door
    (leaf outline, swing marks from the hinge side, pull at the latch side), header channel across the top."""
    fix = (w - door_w) / 2
    _rect(v, x, 0, x + w, h, OUTLINE); _line(v, (x, h), (x + w, h), MED)   # glass extents and header channel
    for px in (x + 0.75, x + w - fix - 0.75 + 0.0):
        pass
    _rect(v, x + 0.6, 0.6, x + fix - 0.4, h - 0.6, FINE, LIGHT); _rect(v, x + w - fix + 0.4, 0.6, x + w - 0.6, h - 0.6, FINE, LIGHT)   # fixed panels
    dx = x + fix
    _rect(v, dx, 0.5, dx + door_w, h - 1.0, OUTLINE); _rect(v, dx + 0.6, 1.1, dx + door_w - 0.6, h - 1.6, FINE, LIGHT)   # door leaf, 1/2 in. clear all round
    hx, lx = (dx, dx + door_w) if hinge == 'L' else (dx + door_w, dx)
    _line(v, (hx, 0.5), (lx, h / 2), FINE, MID, '[2 1.5] 0'); _line(v, (hx, h - 1.0), (lx, h / 2), FINE, MID, '[2 1.5] 0')
    for hy in (12, h / 2, h - 12): _rect(v, hx - 1.2, hy - 1.5, hx + 1.2, hy + 1.5, MED, fill=(1, 1, 1))   # hinges on the fixed-panel side
    px = lx - 3.4 if hinge == 'L' else lx + 2.2
    _rect(v, px, 36, px + 1.2, 48, OUTLINE)   # 12 in. pull at the latch side
    for i in range(2): _line(v, (dx + 4 + i * 2.5, h - 6), (dx + 4 + i * 2.5 + 8, h - 16), FINE, PALE)
def shower_head(v, cx, y=80, w=8):
    """Wall-mounted rain head seen from the front: arm escutcheon at y, arm dropping toward the viewer, flat head below it."""
    _ellipse(v, cx, y, 1.5, 1.5, OUTLINE, fill=(1, 1, 1)); _ellipse(v, cx, y, 0.6, 0.6, FINE, MID)
    _rect(v, cx - 0.5, y - 3.0, cx + 0.5, y - 0.4, OUTLINE, fill=(1, 1, 1))
    _ellipse(v, cx, y - 3.6, w / 2, 0.7, OUTLINE, fill=(1, 1, 1)); _line(v, (cx - w / 2 + 1, y - 4.3), (cx + w / 2 - 1, y - 4.3), FINE, MID)
def valve(v, cx, y=48):
    _ellipse(v, cx, y, 3, 3, OUTLINE); _ellipse(v, cx, y, 1.2, 1.2, FINE); _line(v, (cx, y), (cx + 2.2, y + 1.5), MED)
def niche(v, x, w, y, h, shelves=1):
    _rect(v, x, y, x + w, y + h, OUTLINE); _rect(v, x + 0.75, y + 0.75, x + w - 0.75, y + h - 0.75, FINE, MID)
    for i in range(1, shelves + 1): yy = y + h * i / (shelves + 1); _line(v, (x, yy), (x + w, yy), MED); shadow(v, x, x + w, yy)
def towel_bar(v, cx, y=48, w=24):
    _line(v, (cx - w / 2, y), (cx + w / 2, y), OUTLINE)
    for px in (cx - w / 2 + 1, cx + w / 2 - 1): _rect(v, px - 0.6, y - 1.2, px + 0.6, y + 1.2, FINE)
def tile_grid(v, x0, x1, y0, y1, module=(24, 12), grout=0.125, setout='center', stagger=False, show=None, face_d=0.0, side=None):
    """side=(x_face, facing) tiles the side of a return that this view sees edge-on (owner 11.10.26: the bar tile wraps the return's
    side like the range wall's column returns): x0..x1 are then depths off the wall, the plane is at x_face, facing -1 or +1 along x.
    Nothing is drawn on the sheet (the view sees it edge-on); the 3-D render builds it.
    Tile hatch: horizontal joints as fine lines, vertical joints set out from the center (or a centered joint), full course at the floor.
    module = (tile width, tile height). `show` = list of (x0, x1, y0, y1) windows; joints are drawn only inside them (set-out stays on the full extent),
    so cabinets, mirrors and openings in front of the tile are not hatched through. face_d: the tiled face's distance off the wall when it
    is not the wall itself (a column return seen face-on, 11.09.26 night), recorded for the 3-D render."""
    if side is not None: return
    tw, th = module
    def seg(a, b):
        if not show: _line(v, a, b, FINE, TILE); return
        for wx0, wx1, wy0, wy1 in show:
            if a[1] == b[1]:   # horizontal
                lo, hi = max(a[0], wx0), min(b[0], wx1)
                if wy0 - 0.01 <= a[1] <= wy1 + 0.01 and hi > lo: _line(v, (lo, a[1]), (hi, a[1]), FINE, TILE)
            else:              # vertical
                lo, hi = max(a[1], wy0), min(b[1], wy1)
                if wx0 - 0.01 <= a[0] <= wx1 + 0.01 and hi > lo: _line(v, (a[0], lo), (a[0], hi), FINE, TILE)
    y = y0
    while y < y1 - 0.1:
        seg((x0, y), (x1, y)); y += th
    L = x1 - x0; n = int(L / tw); rem = L - n * tw
    if n == 0: return   # narrower than one tile or panel: no vertical joints
    off = rem / 2 if setout == 'center' else 0
    if setout == 'center' and (rem / 2) < tw * 0.25: off = rem / 2 + tw / 2   # avoid slivers: shift half a tile
    row = 0; y = y0
    while y < y1 - 0.1:
        x = x0 + off + (tw / 2 if stagger and row % 2 else 0)
        while x > x0 + 0.1: x -= tw
        x += tw
        while x < x1 - 0.1:
            seg((x, y), (x, min(y1, y + th))); x += tw
        y += th; row += 1
def stone_slab(v, x0, x1, y0, y1, seams=()):
    _rect(v, x0, y0, x1, y1, OUTLINE)
    for s in seams: _line(v, (s, y0), (s, y1), FINE, MID)
    import random; rnd = random.Random(7)
    for i in range(6):
        ax = rnd.uniform(x0, x1); ay = rnd.uniform(y0, y1); bx = min(x1, max(x0, ax + rnd.uniform(-18, 18))); by = min(y1, max(y0, ay + rnd.uniform(-6, 6)))
        _line(v, (ax, ay), (bx, by), FINE, PALE)
def paneling(v, x0, x1, y0, y1, module=30, stile=3.5, rail=3.5):
    _rect(v, x0, y0, x1, y1, OUTLINE)
    L = x1 - x0; n = max(1, round((L - stile) / (module + stile))); pw = (L - stile * (n + 1)) / n
    for i in range(n):
        px = x0 + stile + i * (pw + stile)
        _rect(v, px, y0 + rail, px + pw, y1 - rail, MED); _rect(v, px + 1.0, y0 + rail + 1.0, px + pw - 1.0, y1 - rail - 1.0, FINE, MID)
def wardrobe_beyond(v, x, w, head):
    """What shows through the W.I.C. opening: wardrobe doors and a top rail, lightly."""
    _line(v, (x, 84), (x + w, 84), FINE, MID); _line(v, (x + w / 2, 4), (x + w / 2, 84), FINE, MID)
    for dx in (x + w * 0.25, x + w * 0.75): _line(v, (dx - 1, 40), (dx + 1, 40), FINE, MID)
    _line(v, (x, 4), (x + w, 4), FINE, MID); _line(v, (x, 0), (x + w, 0), MED)


# ---------------------------------------------------------------- bedroom and living (added for the master bedroom pilot)
def panel_wall(v, x0, x1, H, openings=(), single=(), centered=None, mold=None, margin=None, cap_top=None, dado=True, target=32.0, upper_openings=(), end_margin=None, upper=True):
    """Picture-frame paneling on drywall per the skill's Trim and paneling proportions (rule 6):
    base from the TRIM block, one margin (4 in.) above the base cap, horizontal dado boxes, a 3 in. cap with its top at one third of the
    ceiling, a margin below and above the cap, vertical upper boxes to a margin below the crown. Boxes are equal within a wall segment,
    stiles (margins) of the upper and dado tiers align, no box narrower than half the typical box: a remainder goes into the end margins.
    `openings` are (a, b) extents left clear (casing included), the cap and margins stop at them. `single` lists (a, b) extents that
    must be exactly one upper box (a TV, a bed, a piece of art); the dado below a single bay is laid out normally. `centered` = x of a
    feature the layout is set out from (odd box count on that segment)."""
    mold = TRIM['panel_mold'] if mold is None else mold; m = TRIM['margin'] if margin is None else margin
    base_h = TRIM['base']; cap = TRIM['cap']; cap_top = TRIM['dado'] if cap_top is None else cap_top; crown_b = H - TRIM['crown']
    lo = (base_h + m, cap_top - cap - m); hi = (cap_top + m, crown_b - m)
    em = m if end_margin is None else end_margin                 # wider end margins take a device beside a corner
    single = [tuple(sb) for sb in single]
    def segments(cutlist):
        out = []; cur = x0
        for a, b in sorted(cutlist):
            if a - cur > 0.5: out.append((cur, a))
            cur = max(cur, b)
        if x1 - cur > 0.5: out.append((cur, x1))
        return out
    sing_cuts = [(sb[0], sb[0]) for sb in single] + [(sb[1], sb[1]) for sb in single]
    segs = segments(list(openings) + list(upper_openings) + sing_cuts)          # upper tier
    segs_lo = segments(list(openings) + sing_cuts)                              # dado tier runs under windows that sit on the cap line
    # the cap runs across every segment that is not an opening (it passes behind a single bay at the dado level)
    for a, b in segments(list(openings) + list(upper_openings)):
        _rect(v, a, cap_top - cap, b, cap_top, OUTLINE); _line(v, (a, cap_top - cap * 0.45), (b, cap_top - cap * 0.45), FINE, MID); shadow(v, a, b, cap_top - cap)
    def box(a, b, y0, y1):
        if b - a < 6 or y1 - y0 < 6: return
        _rect(v, a, y0, b, y1, MED); _rect(v, a + mold, y0 + mold, b - mold, y1 - mold, FINE, MID)
    def layout(a, b, odd):
        ma = em if abs(a - x0) < 0.1 else m; mb = em if abs(b - x1) < 0.1 else m
        inner = b - a - ma - mb
        if inner < target * 0.5: return []
        n = max(1, int(round((inner + m) / (target + m))))
        if odd and n % 2 == 0:   # odd count on a centered wall: whichever neighbor count lands nearer the target width
            wu, wd = (inner + m) / (n + 1) - m, (inner + m) / (n - 1) - m if n > 1 else 1e9
            n += 1 if abs(wu - target) <= abs(wd - target) else -1
        n = max(1, n); w = (inner - m * (n - 1)) / n
        return [(a + ma + i * (w + m), a + ma + i * (w + m) + w) for i in range(n)]
    for a, b in (segs if upper else []):
        sb = next((sb for sb in single if abs(a - sb[0]) < 0.1 and abs(b - sb[1]) < 0.1), None)
        odd = centered is not None and a <= centered <= b
        if sb is not None:
            top = sb[2] if len(sb) > 2 else hi[1]
            box(a, b, hi[0], top)                        # the forced upper bay: the feature's edges are its edges, margins already outside
            if top < hi[1] - 6: box(a, b, top + m, hi[1])   # transom box above a bay sized to its feature
            continue
        for ba, bb in layout(a, b, odd): box(ba, bb, hi[0], hi[1])
    dado_boxes = []
    if dado:
        for a, b in segs_lo:
            sb = next((sb for sb in single if abs(a - sb[0]) < 0.1 and abs(b - sb[1]) < 0.1), None)
            odd = centered is not None and a <= centered <= b
            bays = layout(a - m, b + m, odd) if sb is not None else layout(a, b, odd)   # dado under a forced bay: outer edges on the bay edges
            for ba, bb in bays: box(ba, bb, lo[0], lo[1]); dado_boxes.append((ba, bb))
    return dado_boxes   # so devices in the base can be centered under a box
def bed_king(v, cx, hb_w=80, hb_h=54, w=76, top=25):
    """King bed seen from the foot or the side wall: headboard with a frame and panel, mattress and bedding, two pillows."""
    _rect(v, cx - hb_w / 2, 0, cx + hb_w / 2, hb_h, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - hb_w / 2 + 2.5, 2.5, cx + hb_w / 2 - 2.5, hb_h - 2.5, MED)
    _line(v, (cx - hb_w / 2 + 2.5, hb_h - 2.5), (cx + hb_w / 2 - 2.5, hb_h - 2.5), FINE, MID)
    _rect(v, cx - w / 2, 10, cx + w / 2, top, OUTLINE, fill=(1, 1, 1)); _line(v, (cx - w / 2, 17), (cx + w / 2, 17), FINE, MID)   # box and mattress
    _rect(v, cx - w / 2 + 2, 0, cx - w / 2 + 4, 10, MED); _rect(v, cx + w / 2 - 4, 0, cx + w / 2 - 2, 10, MED)   # feet
    for px in (cx - 19, cx + 19): _ellipse(v, px, top + 5, 16, 5, OUTLINE, fill=(1, 1, 1))   # pillows
def nightstand(v, x, w=22, h=28, drawers=2):
    _rect(v, x, 0, x + w, h, OUTLINE, fill=(1, 1, 1)); _rect(v, x - 0.5, h - 1.25, x + w + 0.5, h, OUTLINE); shadow(v, x - 0.5, x + w + 0.5, h - 1.25)
    dh = (h - 1.25 - 3) / drawers
    for i in range(drawers):
        y0 = 3 + i * dh; _rect(v, x + 1, y0 + 0.5, x + w - 1, y0 + dh - 0.5, MED); _line(v, (x + w / 2 - 2, y0 + dh / 2), (x + w / 2 + 2, y0 + dh / 2), OUTLINE)
    for lx in (x + 1, x + w - 3): _rect(v, lx, 0, lx + 2, 3, MED)
def tv(v, cx, cy, diag=55):
    w = diag * 0.872; h = diag * 0.49
    _rect(v, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - w / 2 + 0.6, cy - h / 2 + 0.6, cx + w / 2 - 0.6, cy + h / 2 - 0.6, FINE, MID)
    _line(v, (cx - w * 0.35, cy + h * 0.3), (cx - w * 0.05, cy - h * 0.1), FINE, PALE)
def arched_opening(v, x, w, spring, r=None, lw=OUTLINE):
    """Arched niche outline: jambs to the spring line, then a semicircular (or segmental when r > w/2) head."""
    r = r or w / 2; cx = x + w / 2; cy = spring + (0 if r == w / 2 else -(r ** 2 - (w / 2) ** 2) ** 0.5)
    import math
    a0 = math.degrees(math.atan2(spring - cy, -w / 2)); a1 = math.degrees(math.atan2(spring - cy, w / 2))
    if a0 < a1: a0 += 360
    pts = [(cx + r * math.cos(math.radians(a0 - (a0 - a1) * i / 30)), cy + r * math.sin(math.radians(a0 - (a0 - a1) * i / 30))) for i in range(31)]
    _poly(v, [(x, 0), (x, spring)] + pts + [(x + w, spring), (x + w, 0)], lw, close=False)
    return cy
def cabinet_lower(v, x, w, h=30, doors=2, toe=3, pulls=True):
    _rect(v, x, toe, x + w, h, OUTLINE, fill=(1, 1, 1)); _rect(v, x + 2, 0, x + w - 2, toe, MED)
    _rect(v, x - 0.5, h, x + w + 0.5, h + 1.25, OUTLINE); shadow(v, x - 0.5, x + w + 0.5, h)
    dw = (w - 2) / doors
    for i in range(doors):
        dx = x + 1 + i * dw; _rect(v, dx + 0.5, toe + 1, dx + dw - 0.5, h - 1, MED); _rect(v, dx + 1.5, toe + 2, dx + dw - 1.5, h - 2, FINE, MID)
        px = dx + dw - 3 if i == 0 else dx + 3
        if pulls: _line(v, (px, h / 2 - 2), (px, h / 2 + 2), OUTLINE)
def shelves(v, x, w, y0, y1, n=3, thick=1.0):
    for i in range(1, n + 1):
        y = y0 + (y1 - y0) * i / (n + 1); _rect(v, x, y, x + w, y + thick, MED); shadow(v, x, x + w, y)
def drapery(v, x0, x1, H, stack=14, pocket=4):
    """Ceiling pocket (dashed slot at the ceiling line) with pleated drapery panels stacked at both ends, hem 1/2 in. off the floor."""
    import math
    _rect(v, x0, H - pocket, x1, H, FINE, MID, dashes='[2 1.5] 0')
    for a in (x0, x1 - stack):
        top = H - pocket - 0.5; n = 5; pw = stack / n
        pts = [(a, 0.5)]
        for i in range(n):   # pinch-pleat header: a small arc per pleat
            pts += [(a + pw * i + pw * t / 6, top - 1.2 * math.sin(math.pi * t / 6)) for t in range(7)]
        pts += [(a + stack, 0.5)]
        hem = [(a + stack - pw * i - pw * t / 6, 0.5 + 0.6 * math.sin(math.pi * t / 6)) for i in range(n) for t in range(7)]
        _poly(v, pts + hem, OUTLINE, fill=(1, 1, 1))
        for i in range(1, n):
            px = a + pw * i; _line(v, (px, top - 1.2), (px + 0.8, 1.2), FINE, LIGHT)
def pendant(v, cx, H, drop=36, dia=24, body=10):
    """Decorative fixture over the bed, dashed (it is on the RCP; shown here for height only)."""
    d = '[2 1.5] 0'
    _rect(v, cx - 2.5, H - 1.5, cx + 2.5, H, MED, dashes=d); _line(v, (cx, H - 1.5), (cx, H - drop + body), MED, dashes=d)
    _ellipse(v, cx, H - drop + body / 2, dia / 2, body / 2, OUTLINE, dashes=d)
def bifold(v, x, w, head, cs=None):
    casing(v, x, w, head, cs)
    half = w / 2
    for i in range(2):
        a = x + i * half; _rect(v, a, 0.5, a + half, head - 0.5, OUTLINE); _line(v, (a + half / 2, 0.5), (a + half / 2, head - 0.5), MED)
        for q in (a + half / 4, a + 3 * half / 4): _rect(v, q - half / 4 + 2.5, 8, q + half / 4 - 2.5, head - 6, FINE, MID)
        hinge, far = (a, a + half) if i == 0 else (a + half, a)
        _line(v, (hinge, 0.5), ((hinge + far) / 2, head / 2), FINE, MID, '[2 1.5] 0'); _line(v, (hinge, head - 0.5), ((hinge + far) / 2, head / 2), FINE, MID, '[2 1.5] 0')
def jib_door(v, x, w, head):
    _rect(v, x, 0, x + w, head, MED, dashes='[3 2] 0')
    _line(v, (x + w, 0), (x, head / 2), FINE, MID, '[2 1.5] 0'); _line(v, (x + w, head), (x, head / 2), FINE, MID, '[2 1.5] 0')
def sofa(v, x, w=66, h=32, seat=18, arm=6):
    _rect(v, x, 2, x + w, seat, OUTLINE, fill=(1, 1, 1)); _rect(v, x, seat, x + w, h, OUTLINE, fill=(1, 1, 1))
    _rect(v, x, seat - 2, x + arm, h - 4, OUTLINE, fill=(1, 1, 1)); _rect(v, x + w - arm, seat - 2, x + w, h - 4, OUTLINE, fill=(1, 1, 1))
    for i in range(1, 3): _line(v, (x + arm + (w - 2 * arm) * i / 3, seat + 1), (x + arm + (w - 2 * arm) * i / 3, h - 1), FINE, MID)
    for lx in (x + 2, x + w - 4): _rect(v, lx, 0, lx + 2, 2, MED)

def outlet(v, cx, cy=None, label=None, horizontal=False):
    """Duplex receptacle in elevation. In a paneled room it sits vertical, low and centered in the dado box (owner's call 11.02.26:
    not in the base, not in the margin), CL 18 in. AFF so the 4-1/2 in. plate clears the box moulding by over an inch."""
    cy = 18.0 if cy is None else cy
    if horizontal:
        _rect(v, cx - 2.25, cy - 1.4, cx + 2.25, cy + 1.4, OUTLINE, fill=(1, 1, 1)); _ellipse(v, cx - 1.1, cy, 0.45, 0.45, FINE); _ellipse(v, cx + 1.1, cy, 0.45, 0.45, FINE)
    else:
        _rect(v, cx - 1.4, cy - 2.25, cx + 1.4, cy + 2.25, OUTLINE, fill=(1, 1, 1)); _ellipse(v, cx, cy + 1.1, 0.45, 0.45, FINE); _ellipse(v, cx, cy - 1.1, 0.45, 0.45, FINE)
    if label: v.text(v.X(cx), v.Y(cy - (1.4 if horizontal else 2.25)) + 6.2, label, 5.0, (0.4, 0.4, 0.4), align='c')   # clear of the plate
def switch(v, cx, cy=48, label='S'):
    _rect(v, cx - 1.4, cy - 2.25, cx + 1.4, cy + 2.25, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - 0.5, cy - 1.0, cx + 0.5, cy + 1.0, FINE)
    if label: v.text(v.X(cx), v.Y(cy + 2.25) - 1.8, label, 5.0, (0.4, 0.4, 0.4), align='c')   # clear of the plate
def data_jack(v, cx, cy=None):
    cy = 18.0 if cy is None else cy
    _rect(v, cx - 1.4, cy - 2.25, cx + 1.4, cy + 2.25, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - 0.7, cy - 0.6, cx + 0.7, cy + 0.6, FINE)
    _line(v, (cx - 0.7, cy + 0.6), (cx + 0.7, cy - 0.6), FINE)
def picture_light(v, cx, cy, w=24):
    _rect(v, cx - w / 2, cy, cx + w / 2, cy + 1.6, OUTLINE, fill=(1, 1, 1)); _line(v, (cx - 1, cy), (cx - 1, cy - 2.5), MED); _line(v, (cx + 1, cy), (cx + 1, cy - 2.5), MED)
    _ellipse(v, cx, cy - 3.2, 1.6, 0.8, MED)
def art(v, cx, cy, w, h, mat=2.5):
    _rect(v, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, OUTLINE); _rect(v, cx - w / 2 + mat, cy - h / 2 + mat, cx + w / 2 - mat, cy + h / 2 - mat, FINE, MID)
    v.text(v.X(cx), v.Y(cy), 'ART, N.I.C.', 5.0, (0.4, 0.4, 0.4), align='c')

# ---------------------------------------------------------------- secondary bath additions (11.02.26)
def alcove_tub_front(v, x, w, rim=20.0, apron=True):
    """Alcove (apron-front) tub seen from the room: apron panel to the floor, rim band, the inside of the far rim above it."""
    _rect(v, x, 0, x + w, rim, OUTLINE, fill=(1, 1, 1)); _line(v, (x, rim - 2.5), (x + w, rim - 2.5), FINE, MID)   # apron and rim roll
    _rect(v, x + 1.5, 1.0, x + w - 1.5, rim - 3.5, FINE, LIGHT)                                                   # apron panel line
    _line(v, (x + 4, rim - 1.2), (x + w - 4, rim - 1.2), FINE, LIGHT)
def alcove_tub_end(v, x, depth=30.0, rim=20.0, open_to='R'):
    """Alcove tub seen end-on from the room side wall: the rim profile, apron at the room side, tub body."""
    x0, x1 = (x, x + depth) if open_to == 'R' else (x - depth, x)
    _rect(v, x0, 0, x1, rim, OUTLINE, fill=(1, 1, 1))
    _line(v, (x0, rim - 2.5), (x1, rim - 2.5), FINE, MID)
    inner = [(x0 + 2, rim - 2.5), (x0 + 3.5, 6), (x0 + 7, 3.5), (x1 - 7, 3.5), (x1 - 3.5, 6), (x1 - 2, rim - 2.5)]
    _poly(v, inner, FINE, MID, close=False)
def tub_spout(v, cx, y, length=6.0):
    _ellipse(v, cx, y, 1.4, 1.4, OUTLINE, fill=(1, 1, 1)); _rect(v, cx - 1.0, y - length, cx + 1.0, y - 1.0, OUTLINE, fill=(1, 1, 1)); _ellipse(v, cx, y - length, 1.0, 0.4, MED)
def bar_light(v, cx, cy, w=24.0, lamps=3):
    """Linear bath light over a mirror: backplate bar with round shades, CL at cy."""
    _rect(v, cx - w / 2, cy - 1.0, cx + w / 2, cy + 1.0, OUTLINE, fill=(1, 1, 1))
    for i in range(lamps):
        lx = cx - w / 2 + w * (i + 0.5) / lamps
        _ellipse(v, lx, cy - 3.0, 2.2, 2.2, OUTLINE, fill=(1, 1, 1)); _line(v, (lx, cy - 1.0), (lx, cy - 0.8), MED)
def glass_screen_face(v, x, w, y0, h):
    """Fixed frameless glass panel seen face-on (a tub screen): outline, glass tint lines, wall channel at x."""
    _rect(v, x, y0, x + w, y0 + h, OUTLINE); _rect(v, x + 0.6, y0 + 0.6, x + w - 0.6, y0 + h - 0.6, FINE, LIGHT)
    for i in range(2): _line(v, (x + 3 + i * 2.5, y0 + h - 4), (x + 3 + i * 2.5 + 8, y0 + h - 14), FINE, PALE)
def towel_ring(v, cx, y=52):
    _rect(v, cx - 1.2, y + 1.5, cx + 1.2, y + 3.5, FINE); _ellipse(v, cx, y - 1.5, 3.0, 3.0, OUTLINE); _ellipse(v, cx, y - 1.5, 2.3, 2.3, FINE, MID)
def robe_hook(v, cx, y=66):
    _ellipse(v, cx, y, 1.3, 1.3, OUTLINE); _rect(v, cx - 0.5, y - 3.5, cx + 0.5, y - 1.3, OUTLINE); _ellipse(v, cx, y - 3.8, 1.0, 0.5, MED)
def schluter(v, x, y0, y1):
    """Tile edge trim seen face-on at a tile to paint transition."""
    _line(v, (x, y0), (x, y1), MED); _line(v, (x + 0.5, y0), (x + 0.5, y1), FINE, MID)

def mirror_led(v, x, w, y, h):
    """Frameless backlit LED mirror: polished edge, a light halo line 1-1/2 in. inside the edge, no frame."""
    _rect(v, x, y, x + w, y + h, OUTLINE); _rect(v, x + 1.5, y + 1.5, x + w - 1.5, y + h - 1.5, FINE, LIGHT, dashes='[1.5 1.5] 0')
    _line(v, (x + 4, y + h - 6), (x + w * 0.4, y + 6), FINE, PALE); _line(v, (x + 8, y + h - 6), (x + w * 0.5, y + 6), FINE, PALE)

def shower_door_end(v, x, w, h=96, door_w=26, door_at='L'):
    """Frameless glass front with the swing door at one end (hinged on the wall at that end) and one fixed panel, drawn like any door."""
    dx = x if door_at == 'L' else x + w - door_w
    fx0, fx1 = (x + door_w, x + w) if door_at == 'L' else (x, x + w - door_w)
    _rect(v, x, 0, x + w, h, OUTLINE); _line(v, (x, h), (x + w, h), MED)
    _rect(v, fx0 + 0.4, 0.6, fx1 - 0.6, h - 0.6, FINE, LIGHT)
    _rect(v, dx, 0.5, dx + door_w, h - 1.0, OUTLINE); _rect(v, dx + 0.6, 1.1, dx + door_w - 0.6, h - 1.6, FINE, LIGHT)
    hx, lx = (dx, dx + door_w) if door_at == 'L' else (dx + door_w, dx)
    _line(v, (hx, 0.5), (lx, h / 2), FINE, MID, '[2 1.5] 0'); _line(v, (hx, h - 1.0), (lx, h / 2), FINE, MID, '[2 1.5] 0')
    for hy in (12, h / 2, h - 12): _rect(v, hx - 1.2, hy - 1.5, hx + 1.2, hy + 1.5, MED, fill=(1, 1, 1))
    px = lx - 3.4 if door_at == 'L' else lx + 2.2
    _rect(v, px, 36, px + 1.2, 48, OUTLINE)
    for i in range(2): _line(v, (fx0 + 4 + i * 2.5, h - 6), (fx0 + 4 + i * 2.5 + 8, h - 16), FINE, PALE)


def arched_cased_opening(v, x, w, spring, r, cs=5.0):
    """Cased opening with a segmental arched head: leg casings to the spring line, inner and outer arcs sharing one center. A component,
    so the capture records it as an opening up to the apex and the renderer cuts the wall, builds the spandrels and the casing, and a
    render with --context sees the next room through it (owner 11.10.26)."""
    import math
    cx = x + w / 2; cy = spring - math.sqrt(r ** 2 - (w / 2) ** 2)
    def arc(rr, xa, xb):
        a0 = math.atan2(math.sqrt(rr ** 2 - (xa - cx) ** 2), xa - cx); a1 = math.atan2(math.sqrt(rr ** 2 - (xb - cx) ** 2), xb - cx)
        return [(cx + rr * math.cos(a0 + (a1 - a0) * i / 30), cy + rr * math.sin(a0 + (a1 - a0) * i / 30)) for i in range(31)]
    inner = arc(r, x, x + w); outer = arc(r + cs, x - cs, x + w + cs)
    sp_out = cy + math.sqrt((r + cs) ** 2 - (w / 2 + cs) ** 2)
    _rect(v, x - cs, 0, x, sp_out, OUTLINE); _rect(v, x + w, 0, x + w + cs, sp_out, OUTLINE)
    _poly(v, [(x, 0), (x, spring)] + inner + [(x + w, spring), (x + w, 0)], OUTLINE, close=False)
    _poly(v, outer, OUTLINE, close=False)
    _poly(v, arc(r + cs - 1.0, x - cs + 1.0, x + w + cs - 1.0), FINE, LIGHT, close=False)   # backband line
    _line(v, (x - cs + 1.0, 0), (x - cs + 1.0, sp_out), FINE, LIGHT); _line(v, (x + w + cs - 1.0, 0), (x + w + cs - 1.0, sp_out), FINE, LIGHT)
