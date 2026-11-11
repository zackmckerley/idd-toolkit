"""The whole-house shell from FOR REV 1 (owner 11.11.26: "get the whole property modelled, interior and exterior"): walls,
openings and stairs per floor from A-201 / A-202's layers, on the house grid (house_model.json: inches, X east, Y north, the
living room's west wall face on the south gallery line). Writes render/house_geom.json for stage_house (house_stage.py).

Walls: FOR's wall layers closed between their faces (rev1/walls.py), vectorised. Openings: each window (A-WINDOW) or door head
(A-WALL-HEAD) group is one opening, its rectangle the group's extent across the wall; exterior when it sits on the building's
outline. Heights from A-600: window heads 8'-0" AFF unless the type's schedule head is 10'-0"; the type is read from the
nearest window tag on the sheet, else from the width; door heads 8'-0", the 15'-9" and 11'-0" sliders 9'-9" (the kitchen
slider lowered to 9'-3-1/2", owner 11.11.26), the pivot entry door 9'-0".

    python3 render/house_geom.py            # writes render/house_geom.json and render/house_geom_f{1,2}.png (a check plot)
"""
import os, sys, json, math
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/claude/idd-toolkit/rev1'); sys.path.insert(0, '/home/claude/idd-toolkit')
import replay as R, walls as Wm
import pymupdf as fitz
from shapely.geometry import Polygon, MultiPolygon, box as sbox, Point, LineString
from shapely.ops import unary_union

X = lambda x: (x - 626.2) / 1.5
Y = lambda y: (844.5 - y) / 1.5
Z = Wm.Z

# A-600 window types: (width, height, head AFF) in inches
WTYPES = {'A': (60, 72, 96), 'A-1': (60, 24, 120), 'B': (42, 66, 120), 'C': (36, 54, 96), 'D': (49, 74.25, 96), 'E': (60, 60, 96),
          'F': (42, 72, 96), 'G': (132, 126, 96), 'H': (96, 72, 96), 'I': (26, 37, 96), 'J': (26.5, 52.6, 96), 'K': (37, 26, 96),
          'L': (60, 90, 96), 'M': (96, 66, 96)}


def mask_layers(floor, pred, lw=0.6):
    return Wm.line_mask(floor, pred, lw=lw)


def to_in_poly(pts):
    return [(round(X(x), 2), round(Y(y), 2)) for x, y in pts]


def px2pt(px, py):
    return px / Z + R.PLAN.x0, py / Z + R.PLAN.y0


def wall_polys(floor):
    m, w = Wm.wall_mask(floor)
    cs, hier = cv2.findContours(w, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    outers = {}
    for i, c in enumerate(cs):
        if cv2.contourArea(c) < 30: continue
        a = cv2.approxPolyDP(c, 1.2, True).reshape(-1, 2)
        if len(a) < 3: continue
        pts = [(X(px2pt(x, y)[0]), Y(px2pt(x, y)[1])) for x, y in a]
        if hier[0][i][3] < 0: outers[i] = [pts, []]
        else:
            par = hier[0][i][3]
            if par in outers: outers[par][1].append(pts)
    for k, (ext, holes) in outers.items():
        p = Polygon(ext, holes).buffer(0)
        if p.area > 20: polys.append(p)
    return unary_union(polys), w


def tags(floor):
    """Window tag letters on the sheet (FOR draws the type letter in a hexagon next to each window)."""
    d = fitz.open(R.SRC[floor]); pg = d[0]; out = []
    for b in pg.get_text('words'):
        s = b[4].strip()
        if s in WTYPES or s in ('A-1',):
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            if R.PLAN.contains(fitz.Point(cx, cy)): out.append((s, X(cx), Y(cy)))
    return out


def openings(floor, wall_u):
    win = mask_layers(floor, lambda n: n.endswith('A-WINDOW'))
    head = mask_layers(floor, lambda n: n.endswith('A-WALL-HEAD'))
    door = mask_layers(floor, lambda n: n.endswith('A-DOOR'))
    g = int(10 * Z) | 1
    def grp(mk):
        c = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (g, 1))) | \
            cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, g)))
        c = cv2.dilate(c, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(c, connectivity=8)
        return [(st[i][0], st[i][1], st[i][2], st[i][3]) for i in range(1, n) if max(st[i][2], st[i][3]) > 14 * 1.5 * Z]
    out = []
    for kind, mk in (('window', win), ('door', head)):
        for (x, y, w, h) in grp(mk):
            x0, y0 = px2pt(x, y); x1, y1 = px2pt(x + w, y + h)
            X0, X1, Y0, Y1 = X(x0), X(x1), Y(y1), Y(y0)
            along = 'x' if (X1 - X0) >= (Y1 - Y0) else 'y'
            span = (X1 - X0) if along == 'x' else (Y1 - Y0)
            if span > 240 or span < 16: continue
            out.append({'kind': kind, 'along': along, 'x0': X0, 'x1': X1, 'y0': Y0, 'y1': Y1, 'span': span})
    # the wall each opening sits in: the thickness across it from the wall polygons beside its ends
    res = []
    for o in out:
        cx, cy = (o['x0'] + o['x1']) / 2, (o['y0'] + o['y1']) / 2
        if o['along'] == 'x':
            probe = LineString([(cx, cy - 20), (cx, cy + 20)])
            ends = [Point(o['x0'] - 3, cy), Point(o['x1'] + 3, cy)]
        else:
            probe = LineString([(cx - 20, cy), (cx + 20, cy)])
            ends = [Point(cx, o['y0'] - 3), Point(cx, o['y1'] + 3)]
        # wall band: the walls just beyond each end, their extent across
        across = []
        for e in ends:
            near = wall_u.intersection(e.buffer(4))
            if not near.is_empty:
                b = near.bounds
                across.append((b[1], b[3]) if o['along'] == 'x' else (b[0], b[2]))
        if across:
            lo = float(np.median([a[0] for a in across])); hi = float(np.median([a[1] for a in across]))
        else:
            lo, hi = ((o['y0'], o['y1']) if o['along'] == 'x' else (o['x0'], o['x1']))
        if hi - lo < 3.5: lo, hi = (lo + hi) / 2 - 3, (lo + hi) / 2 + 3
        if o['along'] == 'x': o['y0'], o['y1'] = lo, hi
        else: o['x0'], o['x1'] = lo, hi
        o['thick'] = hi - lo
        res.append(o)
    # windows win over door heads drawn in the same place (a slider has both)
    keep = []
    for o in sorted(res, key=lambda q: q['kind'] != 'window'):
        r = sbox(o['x0'], o['y0'], o['x1'], o['y1'])
        if any(r.intersection(sbox(k['x0'], k['y0'], k['x1'], k['y1'])).area > 0.4 * r.area for k in keep): continue
        keep.append(o)
    return keep


def classify(floor, ops, outline, door_mask_pts):
    T = tags(floor)
    edge = outline.exterior
    for o in ops:
        cx, cy = (o['x0'] + o['x1']) / 2, (o['y0'] + o['y1']) / 2
        d_ = o['thick'] / 2 + 14.0
        sides = [Point(cx, cy - d_), Point(cx, cy + d_)] if o['along'] == 'x' else [Point(cx - d_, cy), Point(cx + d_, cy)]
        o['exterior'] = any(not outline.contains(p_) for p_ in sides)
        if o['kind'] == 'window':
            near = sorted(((math.hypot(tx - cx, ty - cy), t) for t, tx, ty in T if math.hypot(tx - cx, ty - cy) < 60))
            cands = [t for _, t in near if abs(WTYPES[t][0] - o['span']) < 14]
            t = cands[0] if cands else min(WTYPES, key=lambda k: abs(WTYPES[k][0] - o['span']) + (0 if k != 'A-1' else 99))
            w, h, head = WTYPES[t]
            o.update({'type': t, 'head': head, 'sill': max(0.0, head - h)})
            if o['span'] > 100: o.update({'kind': 'slider', 'head': 117.0, 'sill': 0.0})
        else:
            o.update({'head': 96.0, 'sill': 0.0})
            if o['exterior'] and o['span'] > 100: o.update({'kind': 'slider', 'head': 117.0})
            elif o['exterior'] and 54 <= o['span'] <= 66: o.update({'head': 108.0})          # D01 pivot entry, 5'-0" x 9'-0"
    return ops


def stairs(floor):
    import rooms_rev1 as RR
    st = RR.STAIRS.get(floor, {})
    return {k: [[X(a), Y(d), X(c), Y(b)] for a, b, c, d in v] for k, v in st.items()}


def house_rooms():
    h = json.load(open(os.path.join(HERE, 'house_model.json')))['rooms']
    out = {1: {}, 2: {}}
    for k, r in h.items():
        out[r['floor']][r['name']] = Polygon(r['outline_in']).buffer(0)
    return out


def ext_gaps(floor, enclosed, wu, ops):
    """Openings in the outside wall that FOR draws with no window line or head (sliders and doors on A-DOOR, open bays): the
    9 in. band inside the enclosed outline where there is no wall and no opening already found."""
    band = enclosed.difference(enclosed.buffer(-7.0, join_style=2))
    have = unary_union([sbox(o['x0'], o['y0'], o['x1'], o['y1']).buffer(1.5) for o in ops] + [wu.buffer(1.0)])
    gap = band.difference(have)
    win = mask_layers(floor, lambda n: n.endswith('A-WINDOW')); door = mask_layers(floor, lambda n: n.endswith('A-DOOR'))
    def frac(mk, g):
        x0, y0, x1, y1 = g.bounds
        px = lambda xx: int(((xx * 1.5 + 626.2) - R.PLAN.x0) * Z); py = lambda yy: int(((844.5 - yy * 1.5) - R.PLAN.y0) * Z)
        a, b_ = sorted((px(x0), px(x1))); c, d = sorted((py(y0), py(y1)))
        sub = mk[max(c - 6, 0):d + 6, max(a - 6, 0):b_ + 6]
        return float(sub.mean()) if sub.size else 0.0
    out = []
    for g in (gap.geoms if hasattr(gap, 'geoms') else [gap]):
        if g.area < 60: continue
        x0, y0, x1, y1 = g.bounds
        along = 'x' if (x1 - x0) >= (y1 - y0) else 'y'; span = max(x1 - x0, y1 - y0)
        if span < 20 or min(x1 - x0, y1 - y0) < 3.0: continue
        kind = 'window' if frac(win, g) > 0.02 else 'slider' if span > 100 else 'door' if frac(door, g) > 0.01 else 'open'
        o = {'kind': kind, 'along': along, 'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1, 'span': span, 'thick': min(x1 - x0, y1 - y0),
             'exterior': True, 'from': 'gap'}
        o['head'] = 117.0 if kind == 'slider' else 96.0 if kind != 'open' else 0.0
        o['sill'] = 0.0 if kind != 'window' else 24.0
        out.append(o)
    return out


def main():
    out = {'_doc': __doc__.split('\n\n')[0], 'floors': {}}
    RM = house_rooms()
    ENC = {}
    for fl in (1, 2):
        rooms = unary_union(list(RM[fl].values()))
        if fl == 2: rooms = unary_union([rooms, RM[1]['LIVING ROOM']])          # the double-height volume is inside the floor 2 envelope
        e = rooms.buffer(14.0, join_style=2).buffer(-1.0, join_style=2)
        parts = [g for g in (e.geoms if hasattr(e, 'geoms') else [e]) if g.area > 20000]
        ENC[fl] = unary_union([Polygon(g.exterior) for g in parts])
    for fl in (1, 2):
        wu, wmask = wall_polys(fl)
        enclosed = ENC[fl]
        main_ = enclosed if enclosed.geom_type == 'Polygon' else max(enclosed.geoms, key=lambda q: q.area)
        inner = wu.intersection(enclosed.buffer(1.0, join_style=2)); outer = wu.difference(enclosed.buffer(1.0, join_style=2))
        full = [g for g in (inner.geoms if hasattr(inner, 'geoms') else [inner]) if g.geom_type == 'Polygon' and g.area > 10]
        low = [g for g in (outer.geoms if hasattr(outer, 'geoms') else [outer]) if g.geom_type == 'Polygon' and g.area > 10]
        polys = full
        ops = classify(fl, openings(fl, wu), main_.buffer(-1.0), None)
        # gaps in the outside wall: merge into a found opening on the same wall line, else a new one
        tight = unary_union([unary_union(list(RM[fl].values()))] + full).buffer(1.0, join_style=2).buffer(-1.0, join_style=2)
        tight = unary_union([Polygon(g.exterior) for g in (tight.geoms if hasattr(tight, 'geoms') else [tight]) if g.area > 20000])
        for gp in ext_gaps(fl, tight, unary_union(full), ops):
            gb = sbox(gp['x0'], gp['y0'], gp['x1'], gp['y1'])
            if gb.centroid.distance(ENC[fl].boundary) > 24.0: continue          # an edge of the open volume, not the outside wall
            hit = next((o for o in ops if o['along'] == gp['along'] and gb.distance(sbox(o['x0'], o['y0'], o['x1'], o['y1'])) < 3.0), None)
            if hit and hit['kind'] == 'window':
                a0, a1 = (gp['x0'], gp['x1']) if gp['along'] == 'x' else (gp['y0'], gp['y1'])
                h0, h1 = (hit['x0'], hit['x1']) if gp['along'] == 'x' else (hit['y0'], hit['y1'])
                if min(a1, h1) - max(a0, h0) > 0.5 * (a1 - a0): continue           # the same window, seen across its thickness
                hit = None
            if hit:
                if gp['along'] == 'x': hit['x0'], hit['x1'] = min(hit['x0'], gp['x0']), max(hit['x1'], gp['x1'])
                else: hit['y0'], hit['y1'] = min(hit['y0'], gp['y0']), max(hit['y1'], gp['y1'])
                hit['span'] = max(hit['x1'] - hit['x0'], hit['y1'] - hit['y0'])
            else: ops.append(gp)
        for o in ops:
            if o['kind'] == 'open' and o['span'] < 72: o.update({'kind': 'door', 'head': 96.0})   # an exterior door FOR drew without a head
        low_pl = [{'ext': [list(c) for c in p.exterior.coords], 'holes': [[list(c) for c in h.coords] for h in p.interiors],
                   'under_floor2': bool(fl == 1 and p.buffer(2).intersects(ENC[2]))} for p in low]
        out['floors'][str(fl)] = {
            'walls': [{'ext': [list(c) for c in p.exterior.coords], 'holes': [[list(c) for c in h.coords] for h in p.interiors]} for p in full],
            'low_walls': low_pl,
            'enclosed': [[list(c) for c in g.exterior.coords] for g in (enclosed.geoms if hasattr(enclosed, 'geoms') else [enclosed])],
            'rooms': {k: [list(c) for c in (v.exterior.coords if v.geom_type == 'Polygon' else max(v.geoms, key=lambda q: q.area).exterior.coords)] for k, v in RM[fl].items()},
            'openings': ops, 'stairs': stairs(fl)}
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 16))
        for g in (enclosed.geoms if hasattr(enclosed, 'geoms') else [enclosed]): ax.fill(*g.exterior.xy, color='#e8f0e0')
        for p in full:
            ax.fill(*p.exterior.xy, color='#444')
            for h in p.interiors: ax.fill(*h.xy, color='white')
        for p in low: ax.fill(*p.exterior.xy, color='#c84')
        for o in ops:
            c = {'window': 'tab:blue', 'door': 'tab:red', 'slider': 'tab:purple', 'open': 'tab:orange'}[o['kind']]
            ax.add_patch(plt.Rectangle((o['x0'], o['y0']), o['x1'] - o['x0'], o['y1'] - o['y0'], color=c, alpha=0.85 if o['exterior'] else 0.3))
            ax.text((o['x0'] + o['x1']) / 2, (o['y0'] + o['y1']) / 2, o.get('type', o['kind'][0]), fontsize=6)
        ax.set_aspect('equal'); ax.grid(True, lw=0.2); fig.savefig(os.path.join(HERE, 'house_geom_f%d.png' % fl), dpi=70, bbox_inches='tight'); plt.close(fig)
        print('floor', fl, 'walls', len(full), 'low', len(low), 'openings', len(ops), 'exterior', sum(o['exterior'] for o in ops))
    json.dump(out, open(os.path.join(HERE, 'house_geom.json'), 'w'), indent=0)


if __name__ == '__main__':
    main()


# ---------------------------------------------------------------------------------------------------------------- 3D prep
FF = {1: 0.0, 2: 154.0}
TOPS = {1: 154.0, 2: 276.0}           # floor 1 walls run to floor 2; floor 2 walls to the truss heel (top of beam 22'-9" + 3")
CEIL = {1: 130.0, 2: 272.0}           # A-301: top of ceiling 10'-10" and 22'-8"
ROOM_CEIL = {(1, 'KITCHEN AND DINING'): 124.0, (1, 'PANTRY'): 124.0, (1, 'LIVING ROOM'): 272.0}


def railings(floor):
    out = []
    for d in R.drawings(floor):
        n = R.lname(d)
        if not (n.endswith('P-RAILING') and R.inplan(d)): continue
        for it in d['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                L = math.hypot(b.x - a.x, b.y - a.y) / 1.5
                if L > 20: out.append([X(a.x), Y(a.y), X(b.x), Y(b.y)])
    return out


def prep3d(G):
    """Walls as prisms between the opening sills and heads (absolute z), so each band is the wall minus the openings open in it."""
    allops = []
    for fl in (1, 2):
        for o in G['floors'][str(fl)]['openings']:
            if o.get('type') == 'G': o['sill'], o['head'] = -30.0, 96.0          # the living room clerestory: 10'-4" to 20'-10" (living model)
            if fl == 2 and o['kind'] == 'door' and o['head'] == 108.0: o['head'] = 96.0
            if fl == 1 and o['kind'] == 'slider' and o['along'] == 'y' and o['x0'] > 80 and o['y0'] > 200: o['head'] = 111.5   # kitchen slider, owner 11.11.26
            o['z0'] = FF[fl] + o['sill']; o['z1'] = FF[fl] + o['head']; o['floor'] = fl
            allops.append(o)
    prisms = []
    for fl in (1, 2):
        F = G['floors'][str(fl)]
        walls = unary_union([Polygon(w['ext'], w['holes']).buffer(0) for w in F['walls']])
        z0, z1 = FF[fl], TOPS[fl]
        cuts = [(o['z0'], o['z1'], sbox(o['x0'], o['y0'], o['x1'], o['y1']).buffer(1.5, join_style=2)) for o in allops
                if o['z1'] > z0 and o['z0'] < z1 and o['kind'] != 'open']
        cuts += [(z0, z1, sbox(o['x0'], o['y0'], o['x1'], o['y1']).buffer(1.5, join_style=2)) for o in allops if o['kind'] == 'open' and o['floor'] == fl]
        zs = sorted(set([z0, z1] + [max(z0, min(z1, c[0])) for c in cuts] + [max(z0, min(z1, c[1])) for c in cuts]))
        for za, zb in zip(zs[:-1], zs[1:]):
            if zb - za < 0.05: continue
            act = [c[2] for c in cuts if c[0] < zb - 0.01 and c[1] > za + 0.01]
            p = walls.difference(unary_union(act)) if act else walls
            for g in (p.geoms if hasattr(p, 'geoms') else [p]):
                if g.geom_type == 'Polygon' and g.area > 1:
                    prisms.append({'z0': za, 'z1': zb, 'ext': [list(c) for c in g.exterior.coords], 'holes': [[list(c) for c in h.coords] for h in g.interiors], 'floor': fl})
        for w in F['low_walls']:
            top = (FF[2]) if (fl == 1 and w['under_floor2']) else FF[fl] + (30.0 if fl == 2 else 36.0)
            prisms.append({'z0': FF[fl] - (6.0 if fl == 1 else 0.0), 'z1': top, 'ext': w['ext'], 'holes': w['holes'], 'floor': fl, 'low': True})
    G['prisms'] = prisms
    G['openings_all'] = allops
    # roof: the floor 2 envelope (with the double-height living room), FOR A-203: 6:12 hips from the walls to a low-slope
    # field; eaves 18 in.; heel at 23'-0", field at 26'-0-1/2" (A-301: midpoint 24'-4-3/4" between eave 22'-9" and top)
    enc2 = unary_union([Polygon(e) for e in G['floors']['2']['enclosed']])
    walls2 = unary_union([Polygon(w['ext'], w['holes']).buffer(0) for w in G['floors']['2']['walls']])
    outline = unary_union([enc2, walls2]).buffer(2, join_style=2).buffer(-2, join_style=2)
    outline = max(outline.geoms, key=lambda g: g.area) if hasattr(outline, 'geoms') else outline
    outline = Polygon(outline.exterior).simplify(1.5)
    rings = []
    for d in [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 73]:
        r = outline.buffer(-d, join_style=2)
        rings.append({'d': d, 'polys': [[list(c) for c in g.exterior.coords] for g in (r.geoms if hasattr(r, 'geoms') else [r]) if not g.is_empty]})
    G['roof'] = {'outline': [list(c) for c in outline.exterior.coords], 'eave': [list(c) for c in outline.buffer(18, join_style=2).exterior.coords],
                 'rings': rings, 'heel': 276.0, 'slope': 0.5, 'top': 312.5}
    # floor 1 roof decks (floor 1 outside floor 2) and the open bays under floor 2 (carport): slabs at floor 2
    enc1 = unary_union([Polygon(e) for e in G['floors']['1']['enclosed']])
    deck = enc1.difference(enc2.buffer(0.5))
    G['f1_roofs'] = [[list(c) for c in g.exterior.coords] for g in (deck.geoms if hasattr(deck, 'geoms') else [deck]) if g.area > 400]
    G['railings'] = {str(fl): railings(fl) for fl in (1, 2)}
    eave = outline.buffer(18, join_style=2)
    def pj(g): return [{'ext': [list(c) for c in q.exterior.coords], 'holes': [[list(c) for c in h.coords] for h in q.interiors]}
                       for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon' and q.area > 1]
    G['roof']['gutter'] = pj(eave.buffer(5.0, join_style=2).difference(eave))                 # 5 in. box gutter, roof colour
    G['roof']['fascia'] = pj(eave.difference(eave.buffer(-1.0, join_style=2)))
    G['roof']['soffit'] = pj(eave.difference(outline.buffer(-0.5, join_style=2)))
    # floor 2 balconies over the carport and the office (FOR A-202 P-WALL / P-RAILING, A-301 north elevation): slab, planter
    # boxes along the front (decorative planters, E-5), picket railing behind them
    G['balconies'] = pj(unary_union([sbox(-190, -414, 50, -300), sbox(170, -414, 290, -300)]).difference(enc2))
    G['planters2'] = pj(unary_union([sbox(-190, -414, 50, -390), sbox(170, -414, 290, -390), sbox(50, -330, 170, -300)]).difference(enc2))
    G['f1_roofs'] = pj(unary_union([Polygon(p) for p in G['f1_roofs']]).difference(unary_union([Polygon(b['ext']) for b in G['balconies']])))
    G['enc'] = {'1': [list(c) for c in enc1.exterior.coords] if enc1.geom_type == 'Polygon' else [list(c) for c in max(enc1.geoms, key=lambda q: q.area).exterior.coords],
                '2': [list(c) for c in enc2.exterior.coords] if enc2.geom_type == 'Polygon' else [list(c) for c in max(enc2.geoms, key=lambda q: q.area).exterior.coords]}
    belt = unary_union([enc1] + [Polygon(b['ext']) for b in G['balconies']] + [Polygon(f['ext']) for f in G['f1_roofs']]).buffer(0.5, join_style=2)
    belt = max(belt.geoms, key=lambda q: q.area) if hasattr(belt, 'geoms') else belt
    belt = Polygon(belt.exterior)
    G['belt'] = pj(belt.buffer(3.0, join_style=2).difference(belt.buffer(-1.0, join_style=2)))      # the second-floor belt course
    rc = [list(c) for c in outline.exterior.coords][:-1]; dsp = []
    for i in range(len(rc)):                                   # downspouts (E-9) at the outline's inside corners
        a_, b_, c_ = rc[i - 1], rc[i], rc[(i + 1) % len(rc)]
        cross = (b_[0] - a_[0]) * (c_[1] - b_[1]) - (b_[1] - a_[1]) * (c_[0] - b_[0])
        if cross < 0 and math.hypot(b_[0] - a_[0], b_[1] - a_[1]) > 30 and math.hypot(c_[0] - b_[0], c_[1] - b_[1]) > 30: dsp.append(b_)
    G['downspouts'] = dsp
    # interior trim for the shell rooms: an 8-1/2 in. base round each room, broken at its doorways
    bases = []
    for fl in ('1', '2'):
        ops_ = [sbox(o['x0'], o['y0'], o['x1'], o['y1']).buffer(3.0, join_style=2) for o in G['openings_all'] if o['floor'] == int(fl) and o['kind'] in ('door', 'slider', 'open')]
        cut = unary_union(ops_) if ops_ else None
        for name, ring in G['floors'][fl]['rooms'].items():
            if (fl, name) in (('1', 'LIVING ROOM'), ('1', 'KITCHEN AND DINING')): continue
            rp = Polygon(ring).buffer(0)
            band = rp.difference(rp.buffer(-0.75, join_style=2))
            if cut is not None: band = band.difference(cut)
            for q in pj(band): q['floor'] = int(fl); q['room'] = name; bases.append(q)
    G['bases'] = bases
    G['f2_struct'] = pj(enc2.difference(Polygon(G['floors']['1']['rooms']['LIVING ROOM']).buffer(-0.5)))
    G['ceil'] = {'%d|%s' % k: v for k, v in ROOM_CEIL.items()}
    return G


if __name__ == '__main__' and '--prep' in sys.argv:
    G = json.load(open(os.path.join(HERE, 'house_geom.json')))
    G = prep3d(G)
    json.dump(G, open(os.path.join(HERE, 'house_geom.json'), 'w'), indent=0)
    print('prisms', len(G['prisms']), 'roof rings', len(G['roof']['rings']), 'f1 roofs', len(G['f1_roofs']), 'rails', {k: len(v) for k, v in G['railings'].items()})
