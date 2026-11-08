"""Typical details sheet ID-801: base, casing, crown, wood paneling, cabinet section, tile edge and floor transitions.
Drawn at 3" = 1'-0" (section details) and 1-1/2" = 1'-0" (cabinet section) from parametric profiles; every detail is dimensioned
from the finished floor or the wall face and keyed to the finish codes and CSI sections used on the set."""
import math, pymupdf as fitz
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import LW, TXT, INK, MID, LIGHT, HEIGHTS, TRIM
import idd_elevations as E

K3 = 3.0 / 12 * 72 / 12       # 3" = 1'-0"  -> 18 pt per inch? no: 3 in. of paper per 12 in. = 0.25 in paper per inch = 18 pt per inch
K3 = 18.0
K15 = 9.0                     # 1-1/2" = 1'-0" -> 9 pt per inch
K75 = 4.5                     # 3/4" = 1'-0" -> 4.5 pt per inch
GYP = (0.9, 0.9, 0.9); WOOD = (0.85, 0.8, 0.72); TILE = (0.93, 0.93, 0.92); STONE = (0.9, 0.9, 0.88); CONC = (0.82, 0.82, 0.82)

class Det:
    """Small drawing helper: inches to points inside a cell, y up from a datum."""
    def __init__(self, sh, cell, k, origin_pt=(120.0, 100.0)):
        self.sh, self.k = sh, k
        self.x0, self.y0, self.x1, self.y1 = cell
        self.ox = self.x0 + origin_pt[0]; self.oy = self.y1 - origin_pt[1]
    def X(self, x): return self.ox + x * self.k
    def Y(self, y): return self.oy - y * self.k
    def rect(self, x0, y0, x1, y1, fill=None, w=0.5, color=INK, dashes=None):
        self.sh.rect((self.X(x0), self.Y(y1), self.X(x1), self.Y(y0)), w, color, fill=fill, dashes=dashes)
    def line(self, a, b, w=0.5, color=INK, dashes=None): self.sh.line((self.X(a[0]), self.Y(a[1])), (self.X(b[0]), self.Y(b[1])), w, color, dashes=dashes)
    def poly(self, pts, fill=None, w=0.5, color=INK):
        sh = self.sh.p.new_shape(); sh.draw_polyline([fitz.Point(self.X(x), self.Y(y)) for x, y in pts]); sh.finish(color=color, fill=fill, width=w, closePath=True); sh.commit()
    def hatch(self, x0, y0, x1, y1, pitch=0.35, color=LIGHT, w=0.3):
        from shapely.geometry import LineString, box as sbox
        X0, Y0, X1, Y1 = self.X(x0), self.Y(y1), self.X(x1), self.Y(y0)
        clip = sbox(X0, Y0, X1, Y1); d = pitch * self.k; h = Y1 - Y0
        t = -h
        while t < (X1 - X0):
            seg = LineString([(X0 + t, Y1), (X0 + t + h, Y0)]).intersection(clip)
            if not seg.is_empty and seg.geom_type == 'LineString':
                (ax, ay), (bx, by) = seg.coords[0], seg.coords[-1]
                self.sh.line((ax, ay), (bx, by), w, color)
            t += d
    def dim(self, a, b, off, text=None, vertical=False):
        """Dimension between points a and b (inches), offset off inches from them."""
        if vertical:
            x = self.X(a[0] + off); ya, yb = self.Y(a[1]), self.Y(b[1])
            self.sh.line((x, ya), (x, yb), 0.4);
            for y in (ya, yb):
                self.sh.line((x - 3, y), (x + 3, y), 0.4); self.sh.line((x - 1.8, y + 1.8), (x + 1.8, y - 1.8), 0.6)
                self.sh.line((self.X(a[0]), y), (x + (3 if off > 0 else -3), y), 0.3, LIGHT)
            self.sh.text(x + (4 if off > 0 else -4), (ya + yb) / 2 + 2, text or E.ftin(abs(b[1] - a[1])), 5.5, INK, align='l' if off > 0 else 'r')
        else:
            y = self.Y(a[1] + off); xa, xb = self.X(a[0]), self.X(b[0])
            self.sh.line((xa, y), (xb, y), 0.4)
            for x in (xa, xb):
                self.sh.line((x, y - 3), (x, y + 3), 0.4); self.sh.line((x - 1.8, y + 1.8), (x + 1.8, y - 1.8), 0.6)
                self.sh.line((x, self.Y(a[1])), (x, y + (3 if off < 0 else -3)), 0.3, LIGHT)
            self.sh.text((xa + xb) / 2, y - 2.5, text or E.ftin(abs(b[0] - a[0])), 5.5, INK, align='c')
    def note(self, x, y, lines, lead_to=None, align='l'):
        px, py = self.X(x), self.Y(y)
        if lead_to:
            self.sh.line((self.X(lead_to[0]), self.Y(lead_to[1])), (px - (3 if align == 'l' else -3), py - 2), 0.3, INK)
        for i, ln in enumerate(lines): self.sh.text(px, py + i * 7.5, ln, 5.5, INK if i == 0 else MID, align=align)

def title(sh, cell, number, name, scale):
    E.title_bar(sh.p, sh.font, sh.fontname, cell, number, name, scale)

def wall_stack(d, x_face, y0, y1, thick=4.5):
    """Wall section: 1/2 in. gyp on studs (hatched) with the finished face at x_face; wall extends to the left."""
    d.rect(x_face - thick, y0, x_face - 0.5, y1, fill=None, w=0.4)
    d.hatch(x_face - thick, y0, x_face - 0.5, y1, 0.6)
    d.rect(x_face - 0.5, y0, x_face, y1, fill=GYP, w=0.5)

def floor_stack(d, x0, x1, finish=0.75, finish_fill=WOOD, sub=0.75):
    d.rect(x0, -sub - 4, x1, -sub, fill=CONC, w=0.4); d.hatch(x0, -sub - 4, x1, -sub, 0.8)
    d.rect(x0, -sub, x1, 0, fill=None, w=0.4)
    d.rect(x0, 0, x1, finish, fill=finish_fill, w=0.6)

# ---------------------------------------------------------------- details
def det_base(sh, cell, n):
    T = TRIM; bh, bt = T['base'], 0.875
    title(sh, cell, n, 'BASE AT WOOD FLOOR  .  06 46 00 / 09 64 00', 'SCALE: 3" = 1\'-0"')
    d = Det(sh, cell, K3, (124, 110))
    floor_stack(d, 0, 6)
    wall_stack(d, 0, -5, bh + 4)
    # base 7/8 x 8-1/2 (TRIM block, 7 percent of the 10 ft ceiling): flat board with a 3/4 ogee cap, 3/4 shoe on the finished floor
    d.poly([(0, 0.75), (bt, 0.75), (bt, bh - 0.75), (bt - 0.15, bh - 0.45), (bt - 0.45, bh - 0.25), (bt - 0.7, bh - 0.1), (0, bh)], fill=WOOD, w=0.6)
    d.poly([(bt, 0.75), (bt + 0.75, 0.75), (bt + 0.55, 1.1), (bt + 0.25, 1.4), (bt, 1.5)], fill=WOOD, w=0.5)   # shoe 3/4 quarter round
    d.line((bt, 0.75), (bt, 0.0), 0.3, LIGHT)
    d.dim((0, 0.75), (0, bh), -1.4, text=E.ftin(bh), vertical=True)
    d.dim((0, 0.75), (bt, 0.75), -1.4, text='7/8"')
    d.note(2.6, bh + 2.6, ['WALL PT-02 EGGSHELL (U.N.O.)', 'GYPSUM BOARD, LEVEL 4 FINISH'], lead_to=(-0.3, bh + 2.0))
    d.note(2.6, 6.0, ['BASE: POPLAR 7/8" x ' + E.ftin(bh) + ', FLAT WITH A 3/4" OGEE CAP, PAINTED', 'PT-01 SATIN, CAULK TO WALL. 7/8" STOCK SO THE CASING (1") STANDS', 'PROUD OF IT. SHOE 3/4" QUARTER ROUND, SCRIBED TO THE FLOOR'], lead_to=(0.8, 4.0))
    d.note(6.8, 0.3, ['WOOD FLOOR WD-01, 3/4" OVER UNDERLAYMENT', '1/4" EXPANSION GAP AT WALL, COVERED BY THE SHOE'], lead_to=(5.6, 0.4))
    d.note(-5.5, -3.2, ['SLAB / SUBFLOOR PER ARCH.'], align='l')
    d.sh.text(d.X(-6), d.Y(0) + 8, 'FIN. FLR.', 5.0, MID)

def det_casing(sh, cell, n):
    T = TRIM; cs, ct = T['casing'], T['casing_thick']; bb = 0.75     # backband 3/4 wide on the outside edge, 1/4 proud of the flat casing
    title(sh, cell, n, 'DOOR CASING, PLAN SECTION  .  06 46 00', 'SCALE: 3" = 1\'-0"')
    d = Det(sh, cell, K3, (190, 130))
    # wall in plan: 4-1/2 thick with 1/2 gyp both sides; jamb and casing at the opening on the right
    d.rect(-6.5, 0, 0, 4.5, w=0.4); d.hatch(-6.5, 0, 0, 4.5, 0.6)
    d.rect(-6.5, -0.5, 0, 0, fill=GYP); d.rect(-6.5, 4.5, 0, 5.0, fill=GYP)
    d.rect(0, -0.5, 0.75, 5.0, fill=WOOD, w=0.6)                       # jamb 3/4 x 5-1/2 (wall + gyp)
    d.rect(0.75, 1.6, 2.4, 2.9, fill=WOOD, w=0.6)                      # door leaf 1-3/4 (stop side)
    d.rect(0, 2.9, 0.75, 3.4, fill=WOOD, w=0.4)                       # stop (applied)
    for y in (-0.5, 5.0):                                               # flat casing 1" x (cs - 3/4) with a 1/4 reveal, backband 3/4 x 1-1/4 on the outside edge
        sgn = -1 if y < 0 else 1
        d.rect(-(cs - 0.25 - bb), min(y, y + sgn * ct), 0.5, max(y, y + sgn * ct), fill=WOOD, w=0.6)
        d.poly([(-(cs - 0.25 - bb), y), (-(cs - 0.25), y), (-(cs - 0.25), y + sgn * (ct + 0.25)), (-(cs - 0.25) + 0.3, y + sgn * (ct + 0.25)), (-(cs - 0.25 - bb) + 0.1, y + sgn * (ct + 0.05)), (-(cs - 0.25 - bb), y + sgn * ct)], fill=WOOD, w=0.6)
    d.dim((-(cs - 0.25), -0.5), (0.5, -0.5), -1.9, text=E.ftin(cs))
    d.dim((0.5, -0.5), (0.75, -0.5), -1.0, text='1/4" REVEAL')
    d.dim((-6.5, 5.0), (-6.5, -0.5), -1.2, text='5-1/2" FIN. WALL', vertical=True)
    d.note(3.2, 6.6, ['CASING: POPLAR 1" x ' + E.ftin(cs) + ' OVERALL, FLAT STOCK WITH A', '3/4" x 1-1/4" BACKBAND ON THE OUTSIDE EDGE, 1/4" REVEAL', 'TO THE JAMB, PT-01 SATIN, MITERED AT THE HEAD.', '1/8" PROUD OF THE 7/8" BASE WHERE THEY MEET'], lead_to=(-2.0, 5.9))
    d.note(3.2, 2.3, ['DOOR 1-3/4" SOLID CORE, PT-01 SATIN', 'HARDWARE PER OWNER'], lead_to=(2.4, 2.25))
    d.note(3.2, -1.6, ['JAMB 3/4" POPLAR, FULL WALL DEPTH, SCRIBED', 'TO FINISHED WALL BOTH SIDES'], lead_to=(0.75, -0.2))
    d.note(-6.0, 8.6, ['NOTE: SAME PROFILE AT WINDOWS, WITH STOOL AND APRON (APRON IN THE CAP PROFILE).', 'NO CASING AT THE HIDDEN SAFE JIB DOOR (ID-737).'], align='l')

def det_crown(sh, cell, n):
    T = TRIM; D, P = T['crown'], T['crown_proj']
    title(sh, cell, n, 'CROWN MOLDING CM-01, BUILT UP  .  06 46 00', 'SCALE: 3" = 1\'-0"')
    d = Det(sh, cell, K3, (124, 90))
    # ceiling at y=10 (local), wall face at x=0 extending left
    d.rect(-6, 10, 9, 10.5, fill=GYP, w=0.5); d.rect(-6, 10.5, 9, 12.5, w=0.4); d.hatch(-6, 10.5, 9, 12.5, 0.6)
    wall_stack(d, 0, 1, 10)
    fr_h = 3.5; fr_t = 0.75; y0 = 10 - D                                 # frieze board 1x4 flat on the wall at the bottom of the build-up
    d.rect(0, y0, fr_t, y0 + fr_h, fill=WOOD, w=0.5)
    d.poly([(fr_t, y0), (fr_t + 0.35, y0 + 0.15), (fr_t + 0.5, y0 + 0.5), (fr_t, y0 + 0.5)], fill=WOOD, w=0.4)              # small cove at the frieze bottom edge
    bt = y0 + fr_h + 1.0                                                   # bed mould 1 in. high on top of the frieze, projecting 1 in.
    d.poly([(fr_t, y0 + fr_h), (fr_t + 0.4, y0 + fr_h), (fr_t + 0.85, y0 + fr_h + 0.35), (fr_t + 1.0, y0 + fr_h + 0.8), (fr_t + 1.0, bt), (fr_t, bt)], fill=WOOD, w=0.5)
    cx = fr_t + 1.0                                                        # the crown springs from the bed mould top to the ceiling at P
    d.poly([(fr_t, bt), (fr_t, 10), (P, 10), (cx, bt)], fill=(0.94, 0.92, 0.88), w=0.3, color=MID)                               # continuous backer behind the crown
    rise = 10 - bt; run = P - cx
    prof = [(cx + fx * run, bt + fy * rise) for fx, fy in ((0, 0), (0.05, 0.02), (0.22, 0.06), (0.36, 0.16), (0.45, 0.3), (0.5, 0.42), (0.6, 0.5), (0.74, 0.58), (0.84, 0.7), (0.92, 0.84), (1, 1))]
    d.poly(prof, fill=WOOD, w=0.6)
    d.dim((0, 10 - D), (0, 10), -1.6, text=E.ftin(D) + ' DROP', vertical=True)
    d.dim((0, 10), (P, 10), 1.2, text=E.ftin(P) + ' PROJ.')
    d.note(-5.6, 11.6, ['CEILING PT-01 FLAT'], align='l')
    d.note(8.2, 7.4, ['CROWN CM-01, THREE PIECE: 1x4 FRIEZE FLAT ON THE', 'WALL, BED MOULD, THEN A SPRUNG CROWN TO THE', 'CEILING ON A CONTINUOUS BACKER. DROP ' + E.ftin(D) + ',', 'PROJECTION ' + E.ftin(P) + '. POPLAR, PROFILES CONFIRMED', 'WITH OWNER FROM SAMPLES. ALL MEMBERS PT-01 SATIN'], lead_to=(cx + 0.5 * run, bt + 0.62 * rise))
    d.note(8.2, 3.2, ['WALL PT-02 EGGSHELL. CROWN RUNS CONTINUOUS OVER', 'DOOR HEADS, 11" OF WALL BETWEEN HEAD CASING AND', 'CROWN. COPED INSIDE CORNERS, MITERED OUTSIDE.', 'NONE IN CLOSETS, MECHANICAL SPACES OR INSIDE', 'TILED COMPARTMENTS'], lead_to=(-0.3, 3.8))
    d.sh.text(d.X(-6), d.Y(10) - 4, 'CLG 10\'-0" AFF (VERIFY)', 5.0, MID)

def det_panel(sh, cell, n):
    T = TRIM; H = T['ceiling']; bh, m, cap, dado, pm, D = T['base'], T['margin'], T['cap'], T['dado'], T['panel_mold'], T['crown']
    lo = (bh + m, dado - cap - m); hi = (dado + m, H - D - m)
    title(sh, cell, n, 'WALL PANELING, PICTURE-FRAME MOULDING ON DRYWALL, WALL SECTION  .  06 46 00', 'SCALE: 3/4" = 1\'-0"')
    d = Det(sh, cell, K75, (50, 60))
    wall_stack(d, 0, -2, H)
    floor_stack(d, -6, 14)
    d.rect(-6, H - 2, 14, H, fill=GYP, w=0.4)
    d.rect(0, 0.75, 0.875, bh, fill=WOOD, w=0.6)                                        # base 7/8 x 8-1/2
    for y0, y1 in ((lo[0], lo[0] + pm), (lo[1] - pm, lo[1]), (hi[0], hi[0] + pm), (hi[1] - pm, hi[1])):   # panel mould rails, 2 in. face x 3/4
        d.poly([(0, y0), (0.75, y0 + 0.3), (0.75, y1 - 0.3), (0, y1)], fill=WOOD, w=0.5)
    d.rect(0, dado - cap, 0.75, dado - 0.5, fill=WOOD, w=0.5); d.rect(0, dado - 0.5, 1.25, dado, fill=WOOD, w=0.6)   # cap 3 in. with a 1-1/4 nosing
    d.poly([(0, H - D), (0.75, H - D), (0.75, H - D + 3.5), (2.0, H - D + 4.6), (T['crown_proj'], H), (0, H)], fill=WOOD, w=0.6)   # crown CM-01, built up (detail 5)
    d.dim((1.25, 0.75), (1.25, bh), 1.6, text=E.ftin(bh) + ' BASE', vertical=True)
    d.dim((1.25, bh), (1.25, lo[0]), 1.6, text=E.ftin(m), vertical=True)
    d.dim((1.25, lo[0]), (1.25, lo[1]), 1.6, text=E.ftin(lo[1] - lo[0]) + ' DADO BOX', vertical=True)
    d.dim((1.25, lo[1]), (1.25, dado - cap), 1.6, text=E.ftin(m), vertical=True)
    d.dim((1.25, dado - cap), (1.25, dado), 1.6, text=E.ftin(cap) + ' CAP', vertical=True)
    d.dim((1.25, dado), (1.25, hi[0]), 1.6, text=E.ftin(m), vertical=True)
    d.dim((1.25, hi[0]), (1.25, hi[1]), 1.6, text=E.ftin(hi[1] - hi[0]) + ' UPPER BOX', vertical=True)
    d.dim((1.25, hi[1]), (1.25, H - D), 1.6, text=E.ftin(m), vertical=True)
    d.dim((1.25, H - D), (1.25, H), 1.6, text=E.ftin(D) + ' CROWN', vertical=True)
    d.note(10.5, H - 14, ['PANEL MOULD: POPLAR 3/4" x ' + E.ftin(pm) + ' FACE, APPLIED TO THE DRYWALL', 'AS PICTURE-FRAME BOXES, MITERED. ONE ' + E.ftin(m) + ' MARGIN EVERYWHERE:', 'ABOVE THE BASE, EACH SIDE OF THE CAP, BELOW THE CROWN, AT', 'CORNERS, CASINGS AND BETWEEN BOXES. BOX LAYOUT PER ELEVATIONS,', 'EQUAL BOXES PER WALL, UPPER AND DADO STILES ALIGNED'], lead_to=(0.75, hi[1] - 1))
    d.note(10.5, 62, ['CAP: 3" FACE WITH A 1-1/4" NOSING, TOP AT ' + E.ftin(dado) + ' AFF (ONE THIRD', 'OF THE CEILING). STOOLS AND COUNTERS WITHIN 2" OF THE CAP', 'TAKE THE CAP LINE INSTEAD'], lead_to=(1.25, dado - 1.5))
    d.note(10.5, 34, ['DEVICES: OUTLETS HORIZONTAL IN THE BASE MARGIN, CL ' + E.ftin(bh + m / 2) + ' AFF.', 'SWITCHES IN THE 4" MARGIN BESIDE THE CASING, CL 4\'-0".', 'NOTHING IN A PANEL FIELD. BLOCKING BEHIND ALL SCONCES,', 'ART AND TV MOUNTS'], lead_to=(0, bh + m / 2))
    d.note(10.5, 12, ['BASE DETAIL 1, CROWN DETAIL 5. ALL TRIM PT-01 SATIN,', 'WALL AND PANEL FIELDS PT-02 EGGSHELL (U.N.O.). SHOP', 'DRAWINGS REQUIRED, VERIFY WALL LENGTHS IN FIELD'], lead_to=(0.875, 4))
    d.sh.text(d.X(-6), d.Y(0) + 8, 'FIN. FLR.', 5.0, MID); d.sh.text(d.X(-6), d.Y(H) - 4, 'CLG 10\'-0" (VERIFY)', 5.0, MID)

def det_cabinet(sh, cell, n):
    title(sh, cell, n, 'BASE AND UPPER CABINET SECTION  .  06 41 00', 'SCALE: 3/4" = 1\'-0"')
    d = Det(sh, cell, K75, (50, 60))
    wall_stack(d, 0, -2, 100)
    floor_stack(d, -6, 30, finish_fill=WOOD)
    # base cabinet: 24 deep, 34-1/2 high, 4 toe kick, 1-1/2 counter at 36; uppers 12 deep from 54 to 96 (42 high)
    d.rect(0, 4, 24, 34.5, w=0.6); d.rect(3, 0.75, 24, 4, fill=None, w=0.4)     # box and toe kick
    d.rect(0, 34.5, 25, 36, fill=STONE, w=0.6)                                    # counter 1-1/2 with 1" overhang
    d.rect(0, 36, 0.5, 54, fill=TILE, w=0.5)                                      # backsplash tile to uppers
    d.rect(0, 54, 12, 96, w=0.6); d.rect(0, 93, 12, 96, fill=None, w=0.4)       # upper box, top rail
    d.rect(0, 53.0, 12, 54, fill=None, w=0.4)                                     # light valance / bottom rail
    d.line((1, 54.5), (11, 54.5), 1.0, INK, dashes='[2 1.5] 0')                   # LED tape UC
    d.rect(24, 4, 24.75, 34.5, fill=WOOD, w=0.4); d.rect(12, 54, 12.75, 96, fill=WOOD, w=0.4)   # door fronts 3/4
    d.dim((0, 0.75), (0, 36), -1.5, text='3\'-0" COUNTER', vertical=True)
    d.dim((0, 36), (0, 54), -1.5, text='1\'-6" SPLASH', vertical=True)
    d.dim((0, 54), (0, 96), -1.5, text='3\'-6" UPPERS', vertical=True)
    d.dim((0, 96), (0, 100), -1.5, text='TO CLG', vertical=True)
    d.dim((0, 0.75), (24, 0.75), -1.8, text='2\'-0" DEEP')
    d.dim((0, 98), (12, 98), 1.0, text='1\'-0"')
    d.note(29, 90, ['UPPER CABINETS: 12" DEEP, DOORS TO CEILING OR', 'CROWN PER ELEVATIONS, FLUSH INSET OR FULL', 'OVERLAY PER OWNER. LED TAPE UC BEHIND A 1"', 'VALANCE, 2700K, DIMMABLE'], lead_to=(12.75, 80))
    d.note(29, 50, ['BACKSPLASH: COUNTER MATERIAL OR TILE, FULL', 'HEIGHT TO THE UPPERS. RECEPTACLES HORIZONTAL', 'IN THE SPLASH, CL 3\'-6" AFF (ID-501)'], lead_to=(0.5, 45))
    d.note(29, 20, ['BASE CABINETS: 24" DEEP, 34-1/2" BOX, 1-1/2" STONE', 'COUNTER WITH 1" OVERHANG, 4" x 3" TOE KICK.', 'PANEL-READY APPLIANCES PER THE APPLIANCE', 'SCHEDULE. SHOP DRAWINGS REQUIRED'], lead_to=(24.75, 18))
    d.sh.text(d.X(-6), d.Y(0) + 8, 'FIN. FLR.', 5.0, MID)

def det_tile_edge(sh, cell, n):
    title(sh, cell, n, 'WALL TILE EDGE AND WET WALL  .  09 30 00', 'SCALE: 3" = 1\'-0"')
    d = Det(sh, cell, K3, (124, 90))
    # plan section at a tile-to-paint corner (outside corner mitered) and a tub edge below; here: wall section at a tub deck
    wall_stack(d, 0, -3, 12)
    d.rect(0, -3, 0.5, 12, fill=None, w=0.4, color=MID)                 # cement board / membrane zone
    d.rect(0.5, 1.5, 0.9, 12, fill=TILE, w=0.6)                         # tile 3/8 on thinset
    for y in (3.5, 5.5, 7.5, 9.5, 11.5): d.line((0.5, y), (0.9, y), 0.3, MID)    # tile joints (horizontal, 2" shown for clarity)
    d.rect(0.9, 0, 6, 1.5, fill=None, w=0.6)                            # tub rim / deck
    d.poly([(0.9, 1.5), (6, 1.5), (6, 0.0), (0.9, 0.0)], fill=None, w=0.6)
    d.line((0.9, 1.5), (0.5, 1.5), 0.6)                                 # tile sits on the tub flange with a sealant joint
    d.rect(0.5, 1.5, 0.9, 1.75, fill=MID, w=0)                         # sealant joint
    d.dim((0, 1.5), (0.9, 1.5), -1.0, text='7/8"')
    d.note(2.6, 10.4, ['WALL TILE WT-01 / WT-02, THINSET ON CEMENT BOARD', 'OVER A SHEET OR LIQUID WATERPROOF MEMBRANE,', 'FULL HEIGHT TO CEILING. LEVEL SET-OUT FROM', 'FINISHED FLOOR, CENTERED ON THE WALL'], lead_to=(0.9, 9.0))
    d.note(2.6, 5.8, ['OUTSIDE CORNERS MITERED (NO METAL TRIM).', 'EXPOSED TILE EDGES: SCHLUTER JOLLY, BRUSHED', 'BRASS TO MATCH SL-01 WHERE A CUT EDGE SHOWS'], lead_to=(0.9, 6.0))
    d.note(2.6, 2.6, ['SEALANT JOINT (NOT GROUT) AT TUB FLANGE AND AT', 'ALL CHANGES OF PLANE, COLOR TO MATCH GROUT.', 'MOVEMENT JOINTS PER TCNA EJ171'], lead_to=(0.7, 1.6))
    d.note(-5.5, -2.0, ['BLOCKING 2x10 FLAT, 33" TO 36" AFF, ALL TUB AND', 'SHOWER WALLS FOR FUTURE GRAB BARS'], align='l')

def det_transition(sh, cell, n):
    title(sh, cell, n, 'FLOOR TRANSITIONS: WOOD TO TILE AND WOOD BORDER  .  09 64 00 / 09 30 00', 'SCALE: 3" = 1\'-0"')
    d = Det(sh, cell, K3, (52, 110))
    # left: wood WD-01 3/4; right: tile TL 3/8 on 1/2 underlayment; flush, with the SL-01 brass strip between (floor 1)
    d.rect(-2, -4.75, 14, -0.75, fill=CONC, w=0.4); d.hatch(-2, -4.75, 14, -0.75, 0.8)
    d.rect(-2, -0.75, 6, 0, fill=None, w=0.4)                            # wood underlayment
    d.rect(-2, 0, 5.5, 0.75, fill=WOOD, w=0.6)                           # WD-01 field
    d.rect(5.5, 0, 6.0, 0.75, fill=(0.8, 0.7, 0.4), w=0.6)               # SL-01 brass strip 1/2 x 3/4 (flush)
    d.rect(6.0, -0.75, 14, 0.375, fill=None, w=0.4); d.hatch(6.0, -0.75, 14, 0.375, 0.3, MID, 0.25)   # self-leveler and uncoupling membrane under the tile
    d.rect(6.0, 0.375, 14, 0.75, fill=TILE, w=0.6)                       # tile 3/8
    for x in (8, 10, 12): d.line((x, 0.375), (x, 0.75), 0.3, MID)
    d.line((-2, 0.75), (14, 0.75), 0.9)                                  # finished floor line, flush
    d.dim((5.5, 0.75), (6.0, 0.75), 1.0, text='1/2"')
    d.dim((-2, 0), (-2, 0.75), -1.2, text='3/4"', vertical=True)
    d.dim((14, 0.375), (14, 0.75), 1.2, text='3/8"', vertical=True)
    d.note(-1.5, 4.6, ['WOOD FLOOR WD-01 (FIELD) WITH WD-02 BORDER BOARD', 'AT THE ROOM EDGE PER ID-101 / ID-102. FLUSH WITH TILE'], lead_to=(2.0, 0.75))
    d.note(5.75, 3.2, ['SL-01 SOLID BRASS STRIP 1/2" x 3/4", SET FLUSH IN', 'THINSET BETWEEN WOOD AND TILE (FLOOR 1 ONLY).', 'FLOOR 2: WOOD BUTTS TILE WITH A SEALANT JOINT'], lead_to=(5.75, 0.8))
    d.note(9.0, -2.2, ['TILE TL-01 / TL-02 / TL-03 / TL-04 ON UNCOUPLING MEMBRANE', 'OVER SELF-LEVELER, SET TO FINISH FLUSH WITH WOOD.', 'DCOF 0.42 MIN. IN WET AREAS'], lead_to=(10, 0.3))
    d.note(-1.5, -3.2, ['BUILD-UPS SET SO ALL FINISHED FLOORS ARE FLUSH.', 'DOOR THRESHOLDS: NONE. TRANSITIONS CENTERED', 'UNDER CLOSED DOORS'], align='l')

def build():
    doc = fitz.open(); sh = Sheet(doc)
    sh.frame('TYPICAL DETAILS', 'SCALE: AS NOTED', ['TYPICAL DETAILS', 'TRIM, MILLWORK, TILE & FLOORS'], 'ID-801', legend_rule=False)
    frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    g = E.layout_cells(frame, 3, 3)      # 3 columns x 3 rows; the two tall sections take two rows each
    tall = lambda a, b: (g[a][0], g[a][1], g[b][2], g[b][3])
    plan = [(det_base, g[0]), (det_panel, tall(1, 4)), (det_cabinet, tall(2, 5)), (det_casing, g[3]), (det_crown, g[6]), (det_tile_edge, g[7]), (det_transition, g[8])]
    for n, (fn, cell) in enumerate(plan, 1):
        fn(sh, cell, n)
    doc.set_metadata({'title': 'Casa Grove - Typical Details', 'author': 'Helios Development', 'subject': 'HD102 Typical Details', 'creator': 'Helios Development', 'producer': 'Helios Development'})
    fix_soft_hyphen(doc); path = '/home/claude/flrwork/261101.HD102.Details.pdf'; doc.save(path, garbage=3, deflate=True); print('saved', path)

if __name__ == '__main__':
    build()
