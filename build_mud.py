"""Mudroom (back of house, floor 1), designed elevations on FOR REV 1 (A-201 REV 1, 10.23.26). Owner 11.05.26: option A of ID-761 S1
(three open lockers, doors may be added later), two shoe drawers per locker, three large dogs (60 lb and over) shut in the mudroom, so
everything is durable, cleanable and out of their reach or behind a closed front; FOR's utility room becomes the dog room (beds, FRP).
Sheets: ID-761 key plan, ID-762 back hall, ID-763 laundry, ID-764 dog room. Output: 261105.HD102.MudroomPilot.pdf

Measured from FOR's vectors (rev1/rooms_rev1.py and the A-DOOR / wall layers), FOR sheet pt, 1.5 pt per inch:
  back hall   x 488.2 (dog room wall face) to 753.2 (living room wall face); north: recess back 914.5 (x 488.2 to 606.0), laundry wall 956.8;
              laundry wall end (pier) 606.0 to 613.8 down to 963.0; south face 1049.2 to 1050.0
  north wall  pocket wall 613.4 to 664.4, laundry opening 664.4 to 715.4 (pocket door 28, 2'-10" leaf, pocket west), wall 715.4 to 753.2
  south wall  door 07 opening 491.2 to 552.0 (3'-0" leaf, arc r 54, exterior, swings out), wall 552.0 to 580.2, AHU door 14 opening
              580.2 to 632.8 (2'-6" leaf, arc r 45, hinged west, swings into the hall), wall 632.8 to 651.2, closet 13 opening 651.2 to
              745.8 (two bifold pairs), wall 745.8 to 753.2
  east wall   956.8 to 978.0 wall, door 12 opening 978.0 to 1029.0 (2'-10" leaf, hinged north, swings into the hall), wall to 1049.2
  west wall   1050.0 to 962.0 wall, door 15 opening 962.0 to 1011.0 (FOR's pocket door, pocket north to 914.5), locker end 950.5 to 914.5
  laundry     x 613.8 to 753.2, y 857.2 to 949.4; FOR's W/D 613.9 to 655.4 x 857.5 to 904.6 (front south, turned per the owner); counter
              716.3 to 753.2 the full depth; sink bowl 720.5 to 745.4 x 864.4 to 908.7; FOR's chute 618 to 690 x 903 to 948 (dashed, A-WALL-HEAD)
Laundry per the owner 11.05.26: stacked W/D on the west wall at the north end facing east, the chute counter south of it with the chute
dropping into the upper over it, the sink counter on the east wall with a hanging rod and no uppers, the north wall open. Doors 15 and 28 stay
FOR's pocket doors; the drop zone moves off the pocket wall.
  dog room    x 356.5 to 480.5, y 914.5 to 1058.8; door 02 (exterior) 959.2 to 1014.8 on the west wall; chase 432.2 to 441.5 x 914.5
              to 921.5 on the north wall; south jog 463.8 to 480.5 at 1050.0 to 1058.8
Heights assumed (VERIFY): ceiling 10'-0", door heads 8'-0"."""
import sys
sys.path.insert(0, '/home/claude/flrwork/rev1')
import pymupdf as fitz
import idd_elevations as E, idd_components as C, idd_kitchen as K, idd_std
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import INK, MID, LIGHT, TRIM
from build_kitchen import H, CR, TOP, shell, tag, draw_views, para_block, NOTE, NOTE_LH, wrap
import base_rev1 as BR, keyclip as KC

def _dim_h(self, x0i, x1i, y_pt, pts_i, offset_lines=True):
    """E.ElevationView.dim_h with the stacking test on the label width: a label wider than its segment goes above the string, alternating height."""
    xs = [self.X(v) for v in pts_i]
    E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
    self.line((xs[0], y_pt), (xs[-1], y_pt), 0.4)
    for v, x in zip(pts_i, xs):
        self.line((x, y_pt - 3), (x, y_pt + 3), 0.4); self.line((x - 1.8, y_pt + 1.8), (x + 1.8, y_pt - 1.8), 0.6)
    flip = False; up = False
    for a, b in zip(pts_i, pts_i[1:]):
        if b - a < 0.5: continue
        lab = E.ftin(b - a); seg = (b - a) * self.k; tw = self.F.text_length(lab, fontsize=5.0 if seg < 26 else 5.5)          # the printed width
        if seg < tw + 8:
            yy = y_pt - 6.3 if not up else y_pt + 9.0
            if b == pts_i[-1]: self.text(self.X(b) - 0.5, yy, lab, 5.0, align='r')          # ends: kept inside the string, clear of the cut wall and the vertical string
            elif a == pts_i[0]: self.text(self.X(a) + 0.5, yy, lab, 5.0, align='l')
            else: self.text((self.X(a) + self.X(b)) / 2, yy, lab, 5.0, align='c')
            up = not up; continue
        up = False
        short = seg < 26
        y_text = y_pt - 2.5 if not (short and flip) else y_pt + 6.5
        self.text((self.X(a) + self.X(b)) / 2, y_text, lab, 5.5 if not short else 5.0, align='c')
        flip = not flip if short else False
E.ElevationView.dim_h = _dim_h
def _dim_v(self, y0i, y1i, x_pt, pts_i, side='r'):
    """E.ElevationView.dim_v with the fit test on the printed label length: a label longer than its segment goes beside the string, alternating sides."""
    ys = [self.Y(v) for v in pts_i]
    E.check_string(pts_i, self.w.get('room'), self.w.get('view'))
    self.line((x_pt, ys[0]), (x_pt, ys[-1]), 0.4)
    for v, y in zip(pts_i, ys):
        self.line((x_pt - 3, y), (x_pt + 3, y), 0.4); self.line((x_pt - 1.8, y + 1.8), (x_pt + 1.8, y - 1.8), 0.6)
    out = side == 'r'; flip = False
    for a, b in zip(pts_i, pts_i[1:]):
        if b - a < 0.5: continue
        cy = (self.Y(a) + self.Y(b)) / 2; lab = E.ftin(b - a); seg = (b - a) * self.k
        tw = self.F.text_length(lab, fontsize=5.0)
        if seg < tw + 6:
            xx = (x_pt + 11.5) if out else (x_pt - 5.0)
            if side != 'r': xx = (x_pt - 5.0) if out else (x_pt + 11.5)
            self.text(xx, cy, lab, 5.0, align='c', rotate=90)
            lx = xx - 6.9 if xx > x_pt else xx + 0.6                                  # leader from the string to the label
            self.line((x_pt, cy), (lx, cy), 0.3) if xx > x_pt else self.line((x_pt, cy), (xx + 0.6, cy), 0.3)
            out = not out; continue
        out = side == 'r'
        short = seg < 26
        sz = 5.5 if not short else 5.0
        x_text = x_pt - 2.5 if side == 'r' else x_pt + 7.5
        if short and flip: x_text = x_pt + 7.5 if side == 'r' else x_pt - 2.5
        self.text(x_text, cy, lab, sz, align='c', rotate=90)
        flip = not flip if short else False
E.ElevationView.dim_v = _dim_v
def elev_marker(sh, cx, cy, number, sheet, direction, r=24.0):
    """Key plan marker (owner 11.07.26: tags on plans larger): r 24, the text and arrow grow with r (view number 10.5 pt, sheet 9.75 pt)."""
    f = r / 16.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.7, fill=(1, 1, 1)); s_.commit()
    sh.line((cx - r, cy), (cx + r, cy), 0.6, INK)
    sh.text(cx, cy - 3.6 * f, str(number), 7.0 * f, INK, align='c', raw=True)
    sh.text(cx, cy + 9.6 * f, sheet.replace('ID-', ''), 6.5 * f, INK, align='c', raw=True)
    dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[direction]
    tip = (cx + dx * (r + 6 * f), cy + dy * (r + 6 * f))
    b1 = (cx + dx * r - dy * 3.5 * f, cy + dy * r + dx * 3.5 * f); b2 = (cx + dx * r + dy * 3.5 * f, cy + dy * r - dx * 3.5 * f)
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
def quad_marker(sh, cx, cy, sheet, views, r=24.0):
    """build_baths.quad_marker at the key plan size (r 24): sheet number in the center, a view number toward each wall, an arrow outside."""
    f = r / 18.0
    s_ = sh.p.new_shape(); s_.draw_circle(fitz.Point(cx, cy), r); s_.finish(color=INK, width=0.7, fill=(1, 1, 1)); s_.commit()
    sh.text(cx, cy + 2.4 * f, sheet.replace('ID-', ''), 6.5 * f, INK, align='c', raw=True)
    for d, n in views.items():
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[d]
        tip = (cx + dx * (r + 6 * f), cy + dy * (r + 6 * f))
        b1 = (cx + dx * r - dy * 3.5 * f, cy + dy * r + dx * 3.5 * f); b2 = (cx + dx * r + dy * 3.5 * f, cy + dy * r - dx * 3.5 * f)
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(b1), fitz.Point(tip), fitz.Point(b2), fitz.Point(b1)]); s_.finish(color=INK, width=0.4, fill=INK); s_.commit()
        sh.text(cx + dx * r * 0.68, cy + dy * r * 0.68 + 2.4 * f, str(n), 7.0 * f, INK, align='c', raw=True)

# --- review draft (11.07.26): notes print at ps(size), so the line height follows the printed size
from idd_sheet import ps as _ps
NLH = _ps(NOTE) * 1.32
def draw_views(sh, cells, views, scale='1/2', ceiling=H):
    """build_kitchen.draw_views with the line height of the printed note size."""
    k = E.SCALES[scale]
    for cell, (n, title, L, fn, extra) in zip(cells, views):
        E.title_bar(sh.p, sh.font, sh.fontname, cell, n, title, 'SCALE: %s" TO 1\'-0"' % scale)
        spec = {'room': 'MUDROOM', 'view': title, 'length': L + extra, 'ceiling': ceiling}
        probe = E.ElevationView(Sheet(fitz.open()).p, sh.font, sh.fontname, (0, 0), k, spec)
        text = fn(probe)
        width = min(cell[2] - cell[0] - 16, 660)
        lines_ = wrap(text, NOTE, width) if text else []
        top = 30 + len(lines_) * NLH + 8
        origin = E.fit_origin(cell, spec, k, top=top)
        v = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
        fn(v)
        v.text(v.X(0) - 6, v.Y(0) - 2.5, 'FIN. FLR.', 5.0, MID, align='r')
        ny = cell[1] + 30
        for ln in lines_: sh.text(cell[2] - 8, ny, ln, NOTE, MID, align='r'); ny += NLH
def para_block(sh, x, y, paras, width, size=NOTE, lh=None, head_color=INK):
    lh = lh or _ps(size) * 1.32
    for p in paras:
        head = isinstance(p, tuple); text = p[1] if head else p
        if text == '': y += lh / 2; continue
        for ln in wrap(text, size, width): sh.text(x, y, ln, size, head_color if head else MID, bold=head); y += lh
    return y

def prop_cells(frame, views, scale):
    """2 x 2 cells, column widths in proportion to the longest wall each column holds plus its margins, the slack shared evenly.
    3/4" does not fit: two rows of 10'-0" walls at 3/4" need 608 pt a row, the sheet has 552, so the elevations stay at 1/2"."""
    k = E.SCALES[scale]; x0, y0, x1, y1 = frame
    need = [max(views[c][2], views[c + 2][2]) * k + 46 + 60 for c in (0, 1)]
    extra = (x1 - x0 - sum(need)) / 2; w0 = need[0] + extra; ym = (y0 + y1) / 2
    return [(x0, y0, x0 + w0, ym), (x0 + w0, y0, x1, ym), (x0, ym, x0 + w0, y1), (x0 + w0, ym, x1, y1)]

OUT = '/home/claude/flrwork/261105.HD102.MudroomPilot.pdf'
ISSUE = '11.05.26'
IN = 1.5                                   # FOR pt per inch
HEAD = 96.0; CS = TRIM['casing']
TB = 6.0                                   # porcelain tile base TL-04, 6" (cleanable, takes claws and a mop)
PALE = (0.72, 0.72, 0.72)
PLATE = 34.0                               # brushed brass scratch plates on the dog side of every door, 34" high
# lockers (option A, revised for the dogs)
L_REC = (606.44 - 488.03) / IN               # 78.5 recess
SCRIBE = 1.0; PART = 0.75
BENCH = 20.0; BENCH_T = 1.25               # quartz bench top at 1'-8", two shoe drawers under it
HOOK = 66.0                                # hooks at 5'-6": the dogs' standing reach (owner: 60 lb and over)
HAT = 72.0                                 # hat shelf 6'-0", 9" cubby above it
LTOP = 81.0; UP0 = 83.0                    # locker top 6'-9", uppers 6'-11" to the 9'-3" scribe line
BAY = (L_REC - 2 * SCRIBE - 2 * PART) / 3  # 25 clear

def F(x):
    """Feet and inches to the nearest 1/8", the way the dimension strings snap."""
    return E.ftin(round(x * 8) / 8)
def r8(x): return round(x * 8) / 8
def x_of(a, b, flip=False, n=None):
    """FOR pt span -> elevation inches from the viewer's left. flip: the view runs against the FOR axis (n = the FOR coordinate at x 0)."""
    return ((n - b) / IN, (n - a) / IN) if flip else ((a - n) / IN, (b - n) / IN)

# ------------------------------------------------------------------ components
def tile_base(v, x0, x1):
    C._rect(v, x0, 0, x1, TB, C.OUTLINE)
    x = x0 + 12
    while x < x1 - 1: C._line(v, (x, 0), (x, TB), C.FINE, PALE); x += 12
def bases(v, spans):
    for a, b in spans: tile_base(v, a, b)
def scratch_plate(v, x, w):
    C._rect(v, x + 1.0, 1.0, x + w - 1.0, PLATE, C.FINE, MID)
TAG_Y = HEAD + CS + 5.5                    # door tags on the wall between the head casing and the crown, clear of the leaf
def door_leaf(v, x, w, head, panels=2, swing='L', knob=False, toward=False):
    """C.door_leaf with the set's swing-mark rule: solid lines when the door swings toward the viewer, dashed when it swings away."""
    C._rect(v, x, 0, x + w, head, C.OUTLINE)                                            # leaf and panels, as C.door_leaf
    st, rail_b, rail_t, mid = 4.5, 9, 4.5, 4.5
    if panels == 2:
        split = rail_b + (head - rail_t - rail_b) * 0.62
        for y0, y1 in ((rail_b, split - mid / 2), (split + mid / 2, head - rail_t)):
            C._rect(v, x + st, y0, x + w - st, y1, C.MED); C._rect(v, x + st + 0.75, y0 + 0.75, x + w - st - 0.75, y1 - 0.75, C.FINE, MID)
    else:
        C._rect(v, x + st, rail_b, x + w - st, head - rail_t, C.MED); C._rect(v, x + st + 0.75, rail_b + 0.75, x + w - st - 0.75, head - rail_t - 0.75, C.FINE, MID)
    hinge, far = (x, x + w) if swing == 'L' else (x + w, x)
    d = None if toward else '[2 1.5] 0'
    C._line(v, (far, 0), (hinge, head / 2), C.FINE, MID, d); C._line(v, (far, head), (hinge, head / 2), C.FINE, MID, d)
    lever = far - 3 if far > hinge else far + 3
    if knob: C._ellipse(v, lever, 38, 1.4, 1.4, C.MED); C._ellipse(v, lever, 38, 0.6, 0.6, C.FINE); return
    C._ellipse(v, lever, 38, 0.9, 0.9, C.FINE); C._line(v, (lever, 38), (lever + (-3.5 if far > hinge else 3.5), 38), C.MED)
def door(v, x, w, swing, panels=2, plate=True, label=None, casing=True, toward=False):
    """A door seen from the room: casing, leaf, swing marks meeting at the hinge side, a round knob at the latch, scratch plate on the dog side."""
    if casing: C.casing(v, x, w, HEAD)
    door_leaf(v, x, w, HEAD, panels=panels, swing=swing, knob=True, toward=toward)
    if plate: scratch_plate(v, x, w)
    if label: tag(v, x + w / 2, TAG_Y, label, 5.0, MID)
def pocket_door(v, x, w, pocket, leaf=None, label=None, casing=True, plate=True, ghost=None):
    """A pocket door seen from one side: casing on the w opening, the leaf closed against the pocket jamb, the latch jamb built out where the
    leaf (sized to the pocket) is shorter than the opening, a flush pull at the leading edge, a flush scratch plate, the pocket dashed (ghost)."""
    lf = w if leaf is None else leaf
    if casing: C.casing(v, x, w, HEAD)
    lx = x if pocket == 'L' else x + w - lf
    if lf < w - 0.01:
        jx = x + lf if pocket == 'L' else x
        C._rect(v, jx, 0, jx + (w - lf), HEAD, C.MED)                                    # latch jamb built out
    C.door_leaf(v, lx, lf, HEAD, panels=2, swing=None, pull='L' if pocket == 'R' else 'R')
    if plate: scratch_plate(v, lx, lf)
    if ghost:
        C._rect(v, ghost[0], 0.75, ghost[1], HEAD - 0.75, C.FINE, MID, dashes='[2 1.5] 0'); tag(v, (ghost[0] + ghost[1]) / 2, HEAD / 2, 'POCKET', 5.0, MID, box=True)
    if label: tag(v, x + w / 2, TAG_Y, label, 5.0, MID)
def fr_wall(v, x0, x1, y0=TB, y1=H, module=48.0, cap=True):
    """FRP panels, 48" wide, PVC division bars at the seams, top cap at the ceiling."""
    x = x0 + module
    while x < x1 - 6: C._line(v, (x, y0), (x, y1), C.MED, MID); x += module
    if cap: C._line(v, (x0, y1 - 1.0), (x1, y1 - 1.0), C.FINE, MID)
RAIL = 0.75                                # drawer rails in the shoe base
def drawers2(v, x, w, bottom, top):
    """Two equal shoe drawers on 3/4" rails, push-to-open (touch latch), no pull: nothing a dog can grip."""
    C._rect(v, x, bottom, x + w, top, C.OUTLINE)
    h = (top - bottom - 3 * RAIL) / 2; y = bottom + RAIL
    for i in range(2):
        K.frame_opening(v, x + RAIL, y, x + w - RAIL, y + h)
        y += h + RAIL
def uppers(v, x, w, y0, y1, single=None, pulls='bottom'):
    """Inset upper doors; pulls at the bottom rail, or routed finger pulls (no hardware) where the dogs can reach."""
    C._rect(v, x, y0, x + w, y1, C.OUTLINE)
    if single:
        K.frame_opening(v, x + K.STILE, y0 + K.STILE, x + w - K.STILE, y1 - K.STILE)
        px = [x + K.STILE + 2.2] if single == 'R' else [x + w - K.STILE - 2.2]
    else:
        dw = (w - 3 * K.STILE) / 2
        for i in range(2):
            dx = x + K.STILE + i * (dw + K.STILE); K.frame_opening(v, dx, y0 + K.STILE, dx + dw, y1 - K.STILE)
        px = [x + K.STILE + dw - 2.2, x + 2 * K.STILE + dw + 2.2]
    for p in px:
        if pulls == 'bottom': C._line(v, (p, y0 + 4.0), (p, y0 + 10.0), C.OUTLINE)
        else: C._line(v, (p, y1 - 3.5), (p, y1 - 7.5), C.MED)
TOE_L = 3.0                                # locker toe 3": the shoe drawers get 6-3/4" fronts
def locker(v, x, w):
    K.toe(v, x, x + w) if TOE_L == K.TOE else C._rect(v, x + 0.5, 0, x + w - 0.5, TOE_L, C.MED, MID)
    drawers2(v, x, w, TOE_L, BENCH - BENCH_T)
    C._rect(v, x - 0.4, BENCH - BENCH_T, x + w + 0.4, BENCH, C.OUTLINE)                       # quartz bench top
    C._rect(v, x, BENCH, x + w, LTOP, C.OUTLINE)
    gx = x + 3.5
    while gx < x + w - 1.0:
        for a, b in ((BENCH + 0.5, HOOK - 5.0), (HOOK + 2.0, HAT - 0.5), (HAT + 0.5, LTOP - 0.5)): C._line(v, (gx, a), (gx, b), C.FINE, PALE)
        gx += 3.5
    C._rect(v, x, HAT - 1.0, x + w, HAT, C.MED)
    for cx in (x + w * 0.3, x + w * 0.7): C.robe_hook(v, cx, HOOK)
    C._rect(v, x, LTOP, x + w, UP0, C.MED)
    uppers(v, x, w, UP0, TOP)
def lockers(v, x0):
    xs = []; x = x0 + SCRIBE
    for i in range(3):
        locker(v, x, BAY); xs.append((x, BAY)); x += BAY + PART
    C._line(v, (x0, TOP), (x0 + L_REC, TOP), C.OUTLINE)
    return xs
def counter_run(v, x0, x1, bays, top=K.COUNTER):
    K.toe(v, x0, x1); cx = x0
    for w, kind in bays:
        if kind == 'sink': K.door_pair_cab(v, cx, w, K.TOE, K.BOX_TOP)
        elif kind == 'drawers': K.drawer_stack(v, cx, w, 3)
        elif kind == 'hamper': K.single_door_cab(v, cx, w, K.TOE, K.BOX_TOP, hinge='R')
        elif kind == 'pullout': K.drawer_stack(v, cx, w, 1)
        cx += w
    K.counter(v, x0, x1)
DZ_W = 16.0; DZ0, DZ1 = 60.0, 84.0         # drop zone 16" x 12", 5'-0" to 7'-0", on the 1'-8-1/4" wall east of door 28
def drop_zone(v, x, w):
    """Closed drop zone, 12" deep: a charging drawer at 5'-0" to 5'-6" (routed finger pull), a door above (key hooks, mail shelf inside)."""
    C._rect(v, x, DZ0, x + w, DZ1, C.OUTLINE)
    K.frame_opening(v, x + RAIL, DZ0 + RAIL, x + w - RAIL, DZ0 + 6.0)
    C._line(v, (x + w / 2 - 4, DZ0 + 5.0), (x + w / 2 + 4, DZ0 + 5.0), C.MED)
    K.frame_opening(v, x + RAIL, DZ0 + 6.0 + RAIL, x + w - RAIL, DZ1 - RAIL)                  # one door, hinged right
    C._line(v, (x + RAIL + 2.2, DZ0 + 9.0), (x + RAIL + 2.2, DZ0 + 14.0), C.OUTLINE)
    tag(v, x + w / 2, DZ1 + 4.0, 'DROP ZONE', 5.0, MID)

def cut_end(v, x, w, top):
    """A run seen end-on (cut): the end panel."""
    K.end_panel(v, x, w, 0, top)
def locker_profile(v, x, d):
    """The locker run seen from its end on the hall west wall: the fronts at the left (south, x), the recess back wall at x + d.
    Bench nose, drawer front edge, hat shelf, locker top, the 12" uppers flush with the fronts."""
    C._rect(v, x, 0, x + d, TOP, C.OUTLINE)
    C._rect(v, x, TOE_L, x + 0.75, BENCH - BENCH_T, C.MED)                                    # drawer fronts edge
    C._rect(v, x - 0.4, BENCH - BENCH_T, x + d, BENCH, C.OUTLINE)                             # bench nose
    C._line(v, (x, HAT - 1.0), (x + d, HAT - 1.0), C.FINE, MID); C._line(v, (x, HAT), (x + d, HAT), C.FINE, MID)
    C._rect(v, x, LTOP, x + d, UP0, C.MED)
    C._rect(v, x, UP0, x + 12.0, TOP, C.MED)                                                  # uppers 12" deep, flush with the fronts
    tag(v, x + d / 2, 46.0, 'LOCKERS', 5.0, MID); tag(v, x + d / 2, 40.0, 'IN PROFILE', 5.0, MID)

# ------------------------------------------------------------------ the back hall, ID-762
BH_W, BH_E, BH_N, BH_S = 488.03, 753.72, 914.5, 1050.62     # FOR's finished faces (drywall lines, audit 11.06.26)
# the back hall and the laundry share their north/south wall: one set of rounded numbers for both faces
HL = r8((BH_E - BH_W) / IN)                    # 176-5/8 hall north wall
LL = r8((753.72 - 613.44) / IN)                  # 92-7/8 laundry
E28 = r8((753.72 - 715.44) / IN)                 # 2'-1-1/4" east of door 28
W28 = 34.0                                     # FOR's 2'-10" pocket leaf and opening
P28 = W28                                      # FOR's pocket frame takes the full 2'-10" leaf (pocket wall 2'-10")
def hall_north(v):
    L = HL
    pier = (r8((606.44 - BH_W) / IN), HL - LL); op = (L - E28 - W28, L - E28)
    shell(v, L, crown=[(0, L)])
    lockers(v, 0.0)
    C._line(v, (pier[0], 0), (pier[0], H - CR), C.OUTLINE); C._line(v, (pier[1], 0), (pier[1], H - CR), C.OUTLINE)   # the pier face, 4" proud of the laundry wall
    bases(v, [(pier[0], pier[1]), (pier[1], op[0] - CS), (op[1] + CS, L)])
    pocket_door(v, op[0], W28, 'L', leaf=P28, label='28', ghost=(op[0] - P28, op[0]))
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, SCRIBE + BAY + PART / 2, SCRIBE + 2 * BAY + 1.5 * PART, L_REC, pier[1], op[0], op[1], L], tol=0.5))
    v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TOE_L, BENCH, HOOK, HAT, LTOP, UP0, TOP, H]))
    v.dim_v(0, H, v.X(L) + 30, [0, HEAD, H])
    return ('LOCKERS: PAINTED INSET, 3 OPEN BAYS, 2 PUSH-TO-OPEN SHOE DRAWERS EACH, 1-1/4" QUARTZ BENCH AT 1\'-8", HOOKS AT 5\'-6", SHELF AT 6\'-0", '
            'UPPERS TO 9\'-3". DOOR 28: %s SOLID-CORE POCKET, FLUSH PULLS, EDGE LATCH. PT-02, TL-04 TILE BASE.' % F(P28))
def hall_east(v):
    L = (BH_S - 956.5) / IN                                                  # 62.1
    a, b = x_of(978.06, 1029.06, n=956.5)
    shell(v, L, crown=[(0, L)])
    bases(v, [(0, a - CS), (b + CS, L)])
    door(v, a, b - a, 'L', label='12', toward=True)
    C.switch(v, b + CS + 3.0, 48.0, 'S')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, a, b, L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, PLATE, HEAD, HEAD + CS, H - CR, H]))
    return ('DOOR 12: 2\'-10" x 8\'-0" TWO-PANEL, ROUND KNOB, SCRATCH PLATE, DOOR STOP. SWITCH CL 4\'-0". PT-02, TL-04 TILE BASE, CM-01 CROWN.')
def hall_south(v):
    n = BH_E; L = (BH_E - BH_W) / IN
    c13 = x_of(652.14, 745.2, True, n); c13 = (r8(c13[0]), r8(c13[0]) + 62.0); d14 = x_of(580.2, 632.8, True, n); d07 = x_of(491.2, 552.0, True, n)
    w14 = 30.0; x14 = d14[1] - w14 - 2.5                                       # hinged west (right in this view), in FOR's 2'-11" opening
    w07 = 36.0; x07 = (n - 548.46) / IN                                        # FOR's leaf 494.46 to 548.46, hinged east (left), 4-1/4" off the west corner
    shell(v, L, crown=[(0, L)])
    bases(v, [(0, c13[0] - CS), (c13[1] + CS, x14 - CS), (x14 + w14 + CS, x07 - CS)])
    half = 30.0; jb = (c13[1] - c13[0] - 2 * half) / 2                          # a pair of 2'-6" leaves in FOR's 5'-2" opening, 1" jambs
    C.casing(v, c13[0], c13[1] - c13[0], HEAD)                                 # one casing around the whole pair of leaves
    door(v, c13[0] + jb, half, 'L', casing=False, label='13 COAT CLOSET', toward=True)           # west leaf hinged west, swings into the hall
    door(v, c13[0] + jb + half, half, 'R', casing=False, toward=True)                            # east leaf hinged east, swings into the hall
    door(v, x14, w14, 'R', label='14 AHU', toward=True)
    door(v, x07, w07, 'L', label='07')
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, c13[0], c13[1], x14, x14 + w14, x07, x07 + w07, L], tol=0.5)); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, PLATE, HEAD, HEAD + CS, H - CR, H]))
    return ('CLOSET 13: PAIR OF %s TWO-PANEL SWING DOORS, LATCH AT THE MEETING STILES. INSIDE: ROD AND SHELF AT 5\'-6", DROP ZONE WITH A CHARGING SHELF AND OUTLET AT 5\'-6". '
            'DOOR 14: KEYED KNOB, NO LOUVER. DOOR 07: EXTERIOR, DEADBOLT. PT-02, TL-04 TILE BASE.' % F(half))
W15 = r8((1011.06 - 963.06) / IN)              # FOR's 2'-8" door 15 leaf
P15 = W15                                      # FOR's pocket frame takes the full leaf
PW15 = r8((963.06 - BH_N) / IN)                # pocket wall from door 15 to the locker recess
def hall_west(v):
    n = 1050.48; L = r8((1050.48 - 914.22) / IN)                               # FOR's drywall line on this face runs 914.22 to 1050.48 (7'-6-7/8")
    d15 = (L - PW15 - W15, L - PW15); le = (L - r8((950.5 - BH_N) / IN), L)
    shell(v, L, crown=[(0, le[0])])
    bases(v, [(0, d15[0] - CS), (d15[1] + CS, le[0])])
    pocket_door(v, d15[0], W15, 'R', leaf=P15, label='15')
    C._rect(v, d15[1], 0.75, d15[1] + P15, HEAD - 0.75, C.FINE, MID, dashes='[2 1.5] 0')
    tag(v, (le[0] + le[1]) / 2, 64.0, 'POCKET BEHIND', 5.0, MID, box=True)
    locker_profile(v, le[0], le[1] - le[0]); C.crown(v, le[0], le[1], H)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d15[0], d15[1], le[0], L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, PLATE, HEAD, HEAD + CS, H - CR, H]))
    return ('DOOR 15: %s x 8\'-0" SOLID-CORE POCKET DOOR, HEAVY-DUTY FRAME, FLUSH PULLS, EDGE LATCH, SCRATCH PLATES BOTH FACES. LOCKER END SCRIBED TO THE '
            'POCKET WALL, NO FASTENERS INTO IT. PT-02, TL-04 TILE BASE.' % F(P15))
# ------------------------------------------------------------------ the laundry, ID-763
LA_W, LA_E, LA_N, LA_S = 613.44, 753.72, 857.04, 949.4
WD_W, WD_D, WD_H = 27.0, 27.5, 77.0           # FOR's stacked W/D: 27" wide x 27-1/2" deep with the door (P-NEW-EQUIPMENT), 6'-5" tall (VERIFY)
WD_GAP = 1.5                                                                    # behind the W/D: a recessed washer box and dryer vent box
WD_ALC = 30.0                                                                   # the W/D alcove at the north end of the west wall
WD_N0 = (WD_ALC - WD_W) / 2                                                     # the W/D centered in it
CNT_D = 24.0                                                                    # the chute counter
SK_D = 20.0                                                                     # the sink counter, narrowed from FOR's 2'-0-5/8" (sink 16-1/2" front to back)
CH_D = 18.0                                                                     # chute cabinet and the cabinet over the W/D, 18" deep
CHUTE = 14.0                                                                    # chute 14" square (VERIFY with FOR)
UPL0 = 60.0                                                                     # chute cabinet 5'-0" to 9'-3"
ROD = 78.0; ROD_OFF = 12.0                                                      # hanging rod 6'-6", 12" off the east wall
FAU = K.COUNTER + 10.0                                                          # wall faucet 3'-10"
ROD0 = 32.0                                                                     # the rod starts south of the faucet levers (from the north wall)
def wd_front(v, x, w):
    C._rect(v, x, 0, x + w, WD_H, C.OUTLINE)
    C._line(v, (x, WD_H / 2), (x + w, WD_H / 2), C.MED)
    for y in (WD_H * 0.25, WD_H * 0.75): C._ellipse(v, x + w / 2, y, w * 0.32, w * 0.32, C.MED)
    C._rect(v, x + 2, WD_H / 2 - 4.5, x + w - 2, WD_H / 2 - 1.5, C.FINE, MID); C._rect(v, x + 2, WD_H - 4.5, x + w - 2, WD_H - 1.5, C.FINE, MID)
def wd_side(v, x, d):
    C._rect(v, x, 0, x + d, WD_H, C.OUTLINE); C._line(v, (x, WD_H / 2), (x + d, WD_H / 2), C.MED)
def end_masked(v, x, w, y0, y1):
    """A cabinet or counter end nearer the viewer: masks what is behind it."""
    C._rect(v, x, y0, x + w, y1, 0, (1, 1, 1), fill=(1, 1, 1)); K.end_panel(v, x, w, y0, y1)
def chute_shaft(v, x):
    """The chute coming down through the ceiling, the crown and the scribe into the top of the chute cabinet (dashed)."""
    C._rect(v, x, TOP, x + CHUTE, H, C.FINE, MID, dashes='[2 1.5] 0')
def laundry_north(v):
    L = LL; wf = WD_GAP + WD_D; ce = L - SK_D
    shell(v, L, crown=[(0, L)])
    wd_side(v, WD_GAP, WD_D); C._rect(v, 0, WD_H + 4, CH_D, TOP, C.OUTLINE)                   # the W/D stack in profile, its cabinet over it
    tag(v, 9.0, 49.0, 'W/D', 5.0, MID, box=True)
    end_masked(v, 0, CNT_D, 0, K.COUNTER); end_masked(v, 0, CH_D, UPL0, TOP)                  # nearer: the chute counter and the chute cabinet, end on
    chute_shaft(v, (CH_D - CHUTE) / 2)
    tag(v, CH_D / 2, 88.0, 'CHUTE', 5.0, MID); tag(v, CH_D / 2, 82.0, 'CABINET', 5.0, MID)
    bases(v, [(wf, ce)])
    end_masked(v, ce, SK_D, 0, K.COUNTER)                                                     # the sink counter, end on
    C._line(v, (L, ROD + 2.0), (L - ROD_OFF, ROD + 2.0), C.MED); C._ellipse(v, L - ROD_OFF, ROD, 0.8, 0.8, C.OUTLINE, fill=(1, 1, 1))
    tag(v, L - ROD_OFF, ROD + 6.0, 'ROD', 5.0, MID)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, CNT_D, wf, ce, L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.COUNTER, UPL0, WD_H, TOP, H]))
    return ('W/D IN PROFILE AT THE LEFT, CHUTE COUNTER AND CABINET END ON (ID-763 4). SINK COUNTER END ON WITH THE HANGING ROD (ID-763 2). %s CLEAR IN FRONT OF THE W/D. '
            'PT-02, TL-04 TILE BASE, CM-01 CROWN.' % F(ce - wf))
def laundry_east(v):
    L = r8((LA_S - LA_N) / IN)                                                # 61.5
    sink_c = r8(((864.4 + 908.7) / 2 - LA_N) / IN)                             # FOR's sink, from the north wall
    shell(v, L, crown=[(0, L)])
    sw = 36.0; s0 = sink_c - sw / 2; hw = L - 0.5 - (s0 + sw)
    C._rect(v, 0.5, K.TOE, s0, K.BOX_TOP, C.MED)                                               # filler to the corner
    counter_run(v, s0, L - 0.5, [(sw, 'sink'), (hw, 'pullout')])
    K.counter(v, 0.5, s0); K.toe(v, 0.5, s0)
    C._rect(v, 0.5, K.COUNTER, L - 0.5, UPL0, C.FINE, MID)                      # porcelain slab splash to 5'-0"
    C.faucet_wall(v, sink_c, FAU)
    C.outlet(v, sink_c + 20.0, K.COUNTER + 6.0, 'GFCI')
    C._line(v, (ROD0, ROD), (L - 1.0, ROD), C.HEAVY)
    for bx in (ROD0 + 1.0, L - 2.0): C._rect(v, bx - 1.0, ROD - 0.75, bx + 1.0, ROD + 3.0, C.MED, fill=(1, 1, 1))
    tag(v, (ROD0 + L) / 2, ROD + 5.5, 'HANGING ROD', 5.0, MID)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, s0, s0 + sw, L])); v.dim_h(0, L, v.Y(0) + 27, E.snap_points([0, ROD0, L]))
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.TOE, K.COUNTER, FAU, UPL0, ROD, H]))
    return ('COUNTER 20" DEEP, 1-1/4" QUARTZ, SLAB SPLASH TO 5\'-0". 36" SINK CABINET, 29-1/2" x 16-1/2" STAINLESS SINK %s OFF THE NORTH WALL, WALL FAUCET AT 3\'-10", '
            'HAMPER PULL-OUT, GFCI. STAINLESS ROD AT 6\'-6", 12" OFF THE WALL. NO UPPERS.' % F(sink_c))
def laundry_south(v):
    L = LL; op = (E28, E28 + W28)
    shell(v, L, crown=[(0, L)])
    C.casing(v, op[0], W28, HEAD)
    end_masked(v, 0.0, SK_D, 0, K.COUNTER)                                                    # the sink counter end, the rod end over it
    C._line(v, (0, ROD + 2.0), (ROD_OFF, ROD + 2.0), C.MED); C._ellipse(v, ROD_OFF, ROD, 0.8, 0.8, C.OUTLINE, fill=(1, 1, 1))
    C.switch(v, SK_D / 2, 48.0, 'S')
    C._rect(v, op[1] + 0.5, 0.75, op[1] + P28, HEAD - 0.75, C.FINE, MID, dashes='[2 1.5] 0')      # the leaf in its pocket, behind the chute counter
    pocket_door(v, op[0], W28, 'R', leaf=P28, casing=False, plate=False)
    end_masked(v, L - CNT_D, CNT_D, 0, K.COUNTER); end_masked(v, L - CH_D, CH_D, UPL0, TOP)   # the chute counter and the chute cabinet, end on
    chute_shaft(v, L - CH_D + (CH_D - CHUTE) / 2)
    bases(v, [(op[1] + CS, L - CNT_D)])
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, SK_D, op[0], op[1], L - CNT_D, L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, K.COUNTER, 48.0, UPL0, HEAD, HEAD + CS, TOP, H]))
    return ('DOOR 28: %s POCKET LEAF (DASHED IN ITS POCKET), FLUSH PULL, EDGE LATCH. SWITCH CL 4\'-0". CHUTE COUNTER AND CABINET END ON, SCRIBED TO THE POCKET WALL, '
            'NO FASTENERS INTO IT.' % F(P28))
def laundry_west(v):
    L = r8((LA_S - LA_N) / IN)
    cc = L - WD_ALC                                                             # the chute counter, from the south wall to the W/D alcove
    wd0 = L - (WD_N0 + WD_W)
    shell(v, L, crown=[(0, L)])
    counter_run(v, 0.5, cc, [(cc - 0.5, 'drawers')])
    C._rect(v, 0.5, K.COUNTER, cc, UPL0, C.FINE, MID)                            # porcelain slab splash
    C.outlet(v, 7.0, K.COUNTER + 6.0, 'GFCI')
    uppers(v, 0.5, cc - 0.5, UPL0, TOP)                                          # the chute cabinet
    chute_shaft(v, cc / 2 - CHUTE / 2)
    dw = (cc - 0.5 - 3 * K.STILE) / 2; tx = 0.5 + K.STILE + dw / 2
    tag(v, tx, 92.0, 'CHUTE', 5.0, MID); tag(v, tx, 86.0, 'CABINET', 5.0, MID)
    wd_front(v, wd0, WD_W); tag(v, wd0 + WD_W / 2, WD_H / 2 + 2.5, 'W/D', 5.0, MID, box=True)
    uppers(v, cc, L - 0.5 - cc, WD_H + 4, TOP)                                   # the cabinet over the W/D
    C._line(v, (0.5, TOP), (L - 0.5, TOP), C.OUTLINE)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, cc, L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, K.TOE, K.COUNTER, UPL0, WD_H, WD_H + 4, TOP, H]))
    return ('STACKED W/D %s x %s IN A %s ALCOVE, RECESSED WASHER AND DRYER VENT BOXES, DRIP PAN WITH DRAIN, 18" CABINET OVER. CHUTE COUNTER %s x %s, 3 DRAWERS, '
            'QUARTZ, SLAB SPLASH, GFCI. CHUTE CABINET 5\'-0" TO 9\'-3", 18" DEEP, MELAMINE LINED.' % (F(WD_W), F(WD_D), F(WD_ALC), F(cc), F(CNT_D)))
# ------------------------------------------------------------------ the dog room, ID-764
DR_W, DR_E, DR_N, DR_S = 356.22, 481.08, 914.22, 1059.30   # FOR's drywall faces
JOG_N = 1050.48; JOG_W = 464.22                                          # FOR's jog at the southeast corner
def dog_wall(v, L, openings=(), note_side=None):
    shell(v, L)
    bases(v, [(a, b) for a, b in openings])
def dog_north(v):
    L = (DR_E - DR_W) / IN; ch = x_of(432.2, 441.5, n=DR_W)
    shell(v, L); tile_base(v, 0, L)
    C._rect(v, ch[0], TB, ch[1], H, C.OUTLINE); C._line(v, (ch[1], 105.0), (ch[1] + 4.0, 105.0), C.FINE, MID); tag(v, ch[1] + 11.0, 103.5, 'CHASE', 5.0, MID)
    fr_wall(v, 0, ch[0]); fr_wall(v, ch[1], L)
    C._rect(v, 1.5, 0.5, 35.5, 10.0, C.MED, MID, dashes='[2 1.5] 0'); tag(v, 18.5, 13.5, 'BED', 5.0, MID)
    C._rect(v, L / 2 - 6, H - 14, L / 2 + 6, H - 6, C.MED); tag(v, L / 2, H - 19, 'FAN', 5.0, MID, box=True)
    C.outlet(v, 16.0, 72.0, 'GFCI')
    tag(v, L * 0.3, 52, 'FR-01', 6.0, INK, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, ch[0], ch[1], L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, 72.0, H]))
    return ('FR-01 FRP FULL HEIGHT, WHITE PEBBLED, PVC TRIMS, OVER MOISTURE-RESISTANT BOARD. TL-04 COVE BASE. CHASE BOXED IN FR-01. EXHAUST FAN ON A HUMIDITY AND TIMER CONTROL. '
            'GFCI AT 6\'-0" WITH A WHILE-IN-USE COVER.')
def dog_east(v):
    n = DR_N; L = r8((DR_S - DR_N) / IN); d15 = (PW15, PW15 + W15)
    shell(v, L); tile_base(v, 0, d15[0] - 1.5); tile_base(v, d15[1] + 1.5, r8((JOG_N - DR_N) / IN))
    fr_wall(v, 0, d15[0], cap=False); fr_wall(v, d15[1], L, cap=False); C._line(v, (0, H - 1.0), (L, H - 1.0), C.FINE, MID)
    C._rect(v, d15[0] - 1.5, 0, d15[1] + 1.5, HEAD + 1.5, C.OUTLINE)        # PVC J-trim at the opening, no wood casing
    pocket_door(v, d15[0], W15, 'L', leaf=P15, casing=False, label='15', ghost=(0.5, d15[0]))
    C.switch(v, d15[1] + 4.0, 48.0, 'S'); tag(v, (0.5 + d15[0]) / 2, 74.0, 'FR-01', 6.0, INK, box=True)
    jx = r8((JOG_N - DR_N) / IN); C._line(v, (jx, 0), (jx, H), C.OUTLINE); tag(v, (jx + L) / 2, 104, 'JOG', 5.0, MID, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, d15[0], d15[1], jx, L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, PLATE, 48.0, HEAD, H]))
    return ('DOOR 15: %s POCKET LEAF, FLUSH PULL, SCRATCH PLATE, PVC J-TRIM, NO WOOD CASING. FR-01 OVER THE POCKET BONDED, NOT SCREWED. SWITCH CL 4\'-0". '
            'FR-01 FRP FULL HEIGHT, TL-04 COVE BASE.' % F(P15))
def dog_south(v):
    n = DR_E; L = (DR_E - DR_W) / IN; jg = x_of(JOG_W, DR_E, True, n)
    shell(v, L); tile_base(v, 0, L); fr_wall(v, 0, L); tag(v, L * 0.55, 60.0, 'FR-01', 6.0, INK, box=True)
    C._line(v, (jg[1], 0), (jg[1], H), C.OUTLINE); tag(v, (jg[0] + jg[1]) / 2, 104, 'JOG', 5.0, MID, box=True)
    for bx in (jg[1] + 1.0, jg[1] + 36.0): C._rect(v, bx, 0.5, bx + 34.0, 10.0, C.MED, MID, dashes='[2 1.5] 0'); tag(v, bx + 17.0, 13.5, 'BED', 5.0, MID)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, jg[1], L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, H]))
    return ('FR-01 FRP FULL HEIGHT, TL-04 COVE BASE. %s JOG WRAPPED IN FR-01 WITH PVC OUTSIDE CORNERS. NOTHING MOUNTED BELOW 6\'-0".' % F(jg[1] - jg[0]))
def dog_west(v):
    n = DR_S; L = (DR_S - DR_N) / IN; d02 = x_of(959.76, 1013.76, True, n)
    shell(v, L); tile_base(v, 0, (d02[0] + d02[1]) / 2 - 17.5); tile_base(v, (d02[0] + d02[1]) / 2 + 17.5, L)
    fr_wall(v, 0, d02[0], cap=False); fr_wall(v, d02[1], L, cap=False); C._line(v, (0, H - 1.0), (L, H - 1.0), C.FINE, MID)
    w02 = 32.0; x02 = (d02[0] + d02[1]) / 2 - w02 / 2
    C._rect(v, x02 - 1.5, 0, x02 + w02 + 1.5, HEAD + 1.5, C.OUTLINE)
    door(v, x02, w02, 'R', casing=False, label='02'); tag(v, (x02 + w02 + 1.5 + L) / 2, 60.0, 'FR-01', 6.0, INK, box=True)
    v.dim_h(0, L, v.Y(0) + 14, E.snap_points([0, x02, x02 + w02, L])); v.dim_h(0, L, v.Y(0) + 27, [0, L])
    v.dim_v(0, H, v.X(L) + 14, E.snap_points([0, TB, PLATE, HEAD, H]))
    return ('DOOR 02: 2\'-8" x 8\'-0" EXTERIOR, SWINGS OUT, ROUND KNOB, DEADBOLT, SCRATCH PLATE, PVC J-TRIM. FR-01 FRP FULL HEIGHT.')
# ------------------------------------------------------------------ key plan, ID-761
def key_plan(sh):
    src = fitz.open('/home/claude/flrwork/261105.3350THOMAS.Base-key.pdf'); sp = src[0]
    T = BR.transform(1); a, b = T(345, 848), T(762, 1132)
    clip_disp = fitz.Rect(a[0], a[1], b[0], b[1]); k = 4.0                      # 3/16 -> 3/4 (11.07.26: the plan fills the 17:11 sheet)
    u = clip_disp * sp.derotation_matrix; u.normalize()
    ax0, ax1 = FR.x0 + 14, TB_X - 14
    tw, th = clip_disp.width * k, clip_disp.height * k
    ay0 = HDR_Y + 24 + max(0.0, (FR.y1 - 190 - HDR_Y - 24 - th) / 2)       # centered in the band above the scale bar and the notes
    target = fitz.Rect(ax0 + (ax1 - ax0 - tw) / 2, ay0, ax0 + (ax1 - ax0 - tw) / 2 + tw, ay0 + th)
    sh.p.show_pdf_page(target, src, 0, clip=u, rotate=90)
    assert KC.apply(sh.p, target, clip_disp, k, KC.room_poly(1, ['LAUNDRY AND BACK HALL', 'LAUNDRY', 'CLOSET', 'UTILITY ROOM'], pad=9.0, doors=False)), 'key plan clip'
    def P(x, y): d = T(x, y); return (target.x0 + (d[0] - clip_disp.x0) * k, target.y0 + (d[1] - clip_disp.y0) * k)
    def R(x0, y0, x1, y1, **kw): p, q = P(x0, y0), P(x1, y1); sh.rect((p[0], p[1], q[0], q[1]), **kw)
    # the clip's pad picks up the guest bath and storage room linework past the dog room's north and south walls: masked
    R(340.0, 894.0, 481.0, 905.0, width=0, color=(1, 1, 1), fill=(1, 1, 1)); R(488.0, 894.0, 606.0, 905.0, width=0, color=(1, 1, 1), fill=(1, 1, 1)); R(340.0, 1066.0, 481.0, 1078.0, width=0, color=(1, 1, 1), fill=(1, 1, 1))
    # the lockers and the laundry millwork, drawn over FOR's base
    R(488.6, 914.9, 605.6, 950.5, width=0.9, color=INK, fill=(1, 1, 1))
    for i in (1, 2):
        x = 488.03 + (SCRIBE + i * BAY + (i - 0.5) * PART) * IN; p, q = P(x, 914.9), P(x, 950.5); sh.line(p, q, 0.6, INK)
    R(488.6, 940.0, 605.6, 950.5, width=0.4, color=MID, dashes='[2 1.5] 0')                 # bench line
    # the laundry per the owner: FOR's W/D, chute and their labels covered, the turned W/D, the chute counter and cabinet, the rod
    R(614.4, 857.8, 752.9, 948.8, width=0, color=(1, 1, 1), fill=(1, 1, 1))
    R(LA_E - SK_D * IN, LA_N, LA_E, LA_S, width=0.6, color=INK, fill=(1, 1, 1))                # the 20" sink counter
    sc = LA_N + ((864.4 + 908.7) / 2 - LA_N); bw, bd = 29.5 * IN, 16.5 * IN
    p, q = P(LA_E - SK_D * IN + 1.75 * IN, sc - bw / 2), P(LA_E - 1.75 * IN, sc + bw / 2); sh.rect((p[0], p[1], q[0], q[1]), width=0.5, color=INK)
    R(LA_W + WD_GAP * IN, LA_N + WD_N0 * IN, LA_W + (WD_GAP + WD_D) * IN, LA_N + (WD_N0 + WD_W) * IN, width=0.8, color=INK, fill=(1, 1, 1))
    R(LA_W, LA_N + WD_ALC * IN, LA_W + CNT_D * IN, LA_S, width=0.6, color=INK, fill=(1, 1, 1))
    p, q = P(LA_W + CH_D * IN, LA_N + WD_ALC * IN), P(LA_W + CH_D * IN, LA_S); sh.line(p, q, 0.4, MID, dashes='[2 1.5] 0')
    cy_ = LA_N + (WD_ALC + (LA_S - LA_N) / IN) / 2 * IN
    cx_ = LA_W + CH_D / 2 * IN
    R(cx_ - CHUTE / 2 * IN, cy_ - CHUTE / 2 * IN, cx_ + CHUTE / 2 * IN, cy_ + CHUTE / 2 * IN, width=0.4, color=MID, dashes='[1 1] 0')
    p, q = P(LA_E - ROD_OFF * IN, LA_N + ROD0 * IN), P(LA_E - ROD_OFF * IN, LA_S - 1.5); sh.line(p, q, 0.8, MID, dashes='[3 1.5] 0')
    def swing(hx, hy, r, a0, a1, open_at):
        import math
        pts = [P(hx + r * math.cos(math.radians(a)), hy + r * math.sin(math.radians(a))) for a in range(int(a0), int(a1) + 1, 3)]
        s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(*q) for q in pts]); s_.finish(color=INK, width=0.4, closePath=False); s_.commit()
        o = P(hx + r * math.cos(math.radians(open_at)), hy + r * math.sin(math.radians(open_at))); h = P(hx, hy); sh.line(h, o, 0.8, INK)
    swing(548.46, 1065.48, 54.0, 90, 180, 90)      # 07, FOR's hinge at the exterior face, swings out (south)
    R(653.8, 1037.6, 743.5, 1056.8, width=0, color=(1, 1, 1), fill=(1, 1, 1))                  # FOR's bifold symbols out of the opening
    WG = (0.353, 0.353, 0.353)
    R(754.6, 849.0, 761.9, 854.0, width=0, color=WG, fill=WG)                                   # FOR's porch mark in the laundry corner wall
    # FOR draws pocket leaves 28 and 15 half open: drawn closed against the pocket jamb, sized to the pocket
    R(664.6, 949.6, 715.2, 956.6, width=0, color=(1, 1, 1), fill=(1, 1, 1)); R(630.9, 950.6, 664.44, 955.4, width=0, color=WG, fill=WG)
    R(664.44, 951.4, 664.44 + P28 * IN, 954.6, width=0.6, color=INK, fill=(1, 1, 1))
    R(482.9, 962.2, 486.3, 1010.8, width=0, color=(1, 1, 1), fill=(1, 1, 1)); R(482.6, 936.0, 486.6, 963.06, width=0, color=WG, fill=WG)
    R(483.0, 963.06, 486.2, 963.06 + P15 * IN, width=0.6, color=INK, fill=(1, 1, 1))
    R(664.44 - P28 * IN, 951.4, 664.44, 954.6, width=0.4, color=(1, 1, 1), dashes='[2 1.5] 0')
    R(483.0, 963.06 - P15 * IN, 486.2, 963.06, width=0.4, color=(1, 1, 1), dashes='[2 1.5] 0')
    swing(652.14, 1050.0, 47.25, 270, 360, 270)     # 13 west leaf, hinged west, swings north into the hall
    swing(745.2, 1050.0, 47.25, 180, 270, 270)     # 13 east leaf, hinged east, swings north into the hall
    R(753.25 - 12.0 * IN, 1060.0, 753.25, 1060.0 + DZ_W * IN, width=0.6, color=INK, fill=(1, 1, 1))   # drop zone inside the coat closet, east wall
    swing(349.0, 959.2, 48.0, 90, 180, 180)         # 02, hinged north, swings out (west)
    for x0_, y0_ in ((358.0, 1009.5), (411.0, 1009.5), (358.0, 915.0)): R(x0_, y0_, x0_ + 51.0, y0_ + 40.5, width=0.5, color=MID, dashes='[2 1.5] 0')
    # labels
    for txt, x, y, s in (('BACK HALL', 668, 990, 9.0), ('LAUNDRY', 690.5, 880, 7.0), ('DOG ROOM', 440, 950, 9.0),
                         ('COAT CLOSET', 698, 1092, 7.0), ('LOCKERS', 547, 933, 7.0)):
        p = P(x, y); sh.text(p[0], p[1], txt, s * 1.25, INK, align='c')
    for txt, x, y in (('BED', 383.5, 1032), ('BED', 436.5, 1032), ('BED', 383.5, 937), ('FR-01 FRP WALLS', 445, 1000), ('W/D', 639.6, 882), ('CHUTE', 627.3, 927.5), ('DROP', 744.25, 1067.5), ('ZONE', 744.25, 1073.5)):
        p = P(x, y); sh.text(p[0], p[1], txt, 6.0, MID, align='c')
    for n_, (x, y) in {'02': (368, 987), '07': (520, 1040), '12': (739, 995), '13': (698.5, 1066), '14': (606, 1040), '15': (494, 1000), '28': (690, 966)}.items():
        q = P(x, y); s_ = sh.p.new_shape(); s_.draw_oval(fitz.Rect(q[0] - 14, q[1] - 9.5, q[0] + 14, q[1] + 9.5)); s_.finish(color=INK, width=0.5, fill=(1, 1, 1)); s_.commit()
        sh.text(q[0], q[1] + 3.4, n_, 9.5, INK, align='c', raw=True)
    marks = [(1, 'ID-762', 'N', 548, 972), (2, 'ID-762', 'E', 566, 990), (3, 'ID-762', 'S', 548, 1008), (4, 'ID-762', 'W', 530, 990),
             (1, 'ID-764', 'N', 410, 967.5), (2, 'ID-764', 'E', 428, 982.5), (3, 'ID-764', 'S', 410, 997.5), (4, 'ID-764', 'W', 392, 982.5)]   # centered between the beds, arrows 15 pt clear of the bed outlines
    q = P(684, 920); quad_marker(sh, q[0], q[1], 'ID-763', {'N': 1, 'E': 2, 'S': 3, 'W': 4}, r=28.0)   # five numbers inside: a size up
    for n_, s_, d, x, y in marks:
        q = P(x, y); elev_marker(sh, q[0], q[1], n_, s_, d)
    nx, ny = target.x0 + 30, target.y0 + 30
    sh.text(target.x0 + 14, target.y1 + 26, 'FLOOR 1 KEY PLAN', 11, serif=True, spacing=0.8, raw=True)
    bx, by = target.x1 - 54.0 * 10 - 110, target.y1 + 56          # under the plan's right half: 50 pt clear of the coat closet wall, door 07's swing and the notes (review 11.07.26)
    for i in range(10): sh.rect((bx + i * 54.0, by - 5, bx + (i + 1) * 54.0, by), 0.4, INK, INK if i % 2 == 0 else (1, 1, 1))
    for i in (0, 5, 10): sh.text(bx + i * 54.0, by + 13, "%d'" % i, 9.0, MID, align='c', raw=True)
    sh.text(bx + 540 + 12, by + 0.5, '3/4" TO 1\'-0"', 9.5, MID, raw=True)
    s_ = sh.p.new_shape(); s_.draw_polyline([fitz.Point(nx, ny - 18), fitz.Point(nx + 8, ny + 8), fitz.Point(nx, ny + 2), fitz.Point(nx - 8, ny + 8), fitz.Point(nx, ny - 18)]); s_.finish(color=INK, fill=INK, width=0.4); s_.commit()
    sh.text(nx, ny + 24, 'N', 10.0, INK, align='c', raw=True)
    return target

def notes(sh, y0):
    x0, x1 = FR.x0 + 14, TB_X - 14
    items = [(True, 'CHANGES FROM FOR\'S PLAN'),
             '1. DOG ROOM: FR-01 FRP WALLS, TILE COVE BASE.',
             '2. COAT CLOSET 13: PAIR OF SWING DOORS. DROP ZONE INSIDE, ON THE EAST WALL.',
             '3. LAUNDRY: STACKED W/D FACING EAST AT THE NORTH END, CHUTE COUNTER SOUTH OF IT, SINK COUNTER 20" DEEP.',
             '4. LOCKERS 2\'-0" DEEP.',
             '5. TL-04 TILE BASE IN THE BACK HALL AND LAUNDRY.',
             '6. DOORS 02, 07, 12, 13, 14: ROUND KNOBS, BRASS SCRATCH PLATES 2\'-10" HIGH ON THE DOG SIDE. DEADBOLTS ON 02 AND 07.',
             '7. DOOR 12 AND THE EAST LEAF OF 13 DO NOT OPEN TOGETHER.']
    y_end = para_block(sh, x0, y0, items, x1 - x0)
    assert y_end < FR.y1 - 8, ('notes run off the sheet', y_end)

def build():
    import idd_sheet; idd_sheet.EXTRA_REVS[:] = []
    idd_std.PROJECT['date'] = '11.06.26'
    idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
    doc = fitz.open()
    rev = (('0', ISSUE, 'ISSUED FOR REVIEW'), ('1', '11.06.26', 'REV 1 CHECK, FOR FACES'))
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)       # HDR_Y + 8 is 24 pt clear of the top frame
    sh = Sheet(doc); sh.frame('MUDROOM ELEVATIONS', 'KEY PLAN, SCALE: 3/4" TO 1\'-0"', ['MUDROOM', 'ELEVATIONS KEY PLAN'], 'ID-761', revisions=rev, legend_rule=False)
    t = key_plan(sh); notes(sh, t.y1 + 100)
    sheets = [('ID-762', 'MUDROOM ELEVATIONS - BACK HALL', ['INTERIOR ELEVATIONS', 'MUDROOM BACK HALL'],
               [(1, 'NORTH ELEVATION - LOCKERS AND LAUNDRY WALL', (BH_E - BH_W) / IN, hall_north, 0), (2, 'EAST ELEVATION - DOOR 12', (BH_S - 956.5) / IN, hall_east, 0),
                (3, 'SOUTH ELEVATION - COAT CLOSET, AHU, DOOR 07', (BH_E - BH_W) / IN, hall_south, 0), (4, 'WEST ELEVATION - DOOR 15 TO THE DOG ROOM', (BH_S - BH_N) / IN, hall_west, 0)]),
              ('ID-763', 'MUDROOM ELEVATIONS - LAUNDRY', ['INTERIOR ELEVATIONS', 'MUDROOM LAUNDRY'],
               [(1, 'NORTH ELEVATION - OPEN WALL', (LA_E - LA_W) / IN, laundry_north, 0), (2, 'EAST ELEVATION - SINK AND HANGING ROD', (LA_S - LA_N) / IN, laundry_east, 0),
                (3, 'SOUTH ELEVATION - DOOR 28', (LA_E - LA_W) / IN, laundry_south, 0), (4, 'WEST ELEVATION - W/D AND CHUTE', (LA_S - LA_N) / IN, laundry_west, 0)]),
              ('ID-764', 'MUDROOM ELEVATIONS - DOG ROOM', ['INTERIOR ELEVATIONS', 'MUDROOM DOG ROOM'],
               [(1, 'NORTH ELEVATION', (DR_E - DR_W) / IN, dog_north, 0), (2, 'EAST ELEVATION - DOOR 15', (DR_S - DR_N) / IN, dog_east, 0),
                (3, 'SOUTH ELEVATION', (DR_E - DR_W) / IN, dog_south, 0), (4, 'WEST ELEVATION - DOOR 02', (DR_S - DR_N) / IN, dog_west, 0)])]
    for sid, title, tl, views in sheets:
        s = Sheet(doc); s.frame(title, 'SCALE: 1/2" TO 1\'-0"', tl, sid, revisions=rev, legend_rule=False)
        draw_views(s, prop_cells(frame, views, '1/2'), views, scale='1/2')
    fix_soft_hyphen(doc); doc.set_metadata({'title': 'Casa Grove mudroom ID-761 to ID-764', 'author': 'Helios Development'})
    doc.save(OUT, garbage=3, deflate=True); print('saved', OUT)

if __name__ == '__main__':
    build()
