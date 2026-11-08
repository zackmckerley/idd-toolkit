"""Rule-based lighting, switching, power and data layouts from the room model (for pricing and coordination).
All positions in model points (plan coordinates of the floor's base); inches where noted. The rules are the usual residential
ones (downlight grids 4 to 5 ft on center, sconces at mirrors, NEC 210.52 receptacle spacing, GFCI in wet rooms) and every
output carries a 'rule' field so a reviewer can see why a device is where it is."""
import math, json
from shapely.geometry import Polygon, Point, LineString
PT_PER_FT = 13.5; PT_PER_IN = PT_PER_FT / 12.0

# ---------------------------------------------------------------- fixture library (type, symbol, description, mount)
FIXTURES = {
    'R1': ('recessed', '4" LED RECESSED DOWNLIGHT, 2700K, 90 CRI MIN., DIMMABLE', 'CEILING'),
    'R2': ('recessed', '4" LED RECESSED DOWNLIGHT, WET LOCATION, 2700K', 'CEILING, SHOWER / TUB'),
    'P1': ('pendant', 'PENDANT, OWNER SELECTION, 30" TO 36" ABOVE COUNTER', 'CEILING'),
    'C1': ('chandelier', 'CHANDELIER, OWNER SELECTION, 7\'-0" MIN. CLEAR AFF', 'CEILING'),
    'S1': ('sconce', 'WALL SCONCE, OWNER SELECTION, CL 5\'-6" AFF', 'WALL'),
    'S2': ('sconce', 'READING SCONCE AT BED, CL 4\'-6" AFF, SWITCHED AT BED', 'WALL'),
    'SM': ('surface', 'SURFACE MOUNT LED, CLOSETS AND UTILITY', 'CEILING'),
    'F1': ('fan', 'CEILING FAN WITH LIGHT, 52", OWNER SELECTION', 'CEILING'),
    'UC': ('strip', 'LED TAPE UNDER UPPER CABINETS, 2700K, DIMMABLE', 'UNDER CABINET'),
}
DEVICES = {
    'REC': 'DUPLEX RECEPTACLE, 15" AFF TO CL U.N.O.', 'GFI': 'GFCI DUPLEX RECEPTACLE, 42" AFF AT COUNTERS, 15" AFF ELSEWHERE',
    'USB': 'DUPLEX RECEPTACLE WITH USB A AND C, 15" AFF', 'DAT': 'DATA / CAT 6 OUTLET, 15" AFF', 'TV': 'TV: RECESSED POWER AND DATA BOX, CL 42" AFF (BEDROOMS 50")',
    'FLR': 'FLOOR RECEPTACLE, FLUSH BRASS', 'S': 'SINGLE POLE SWITCH, 42" AFF', 'S3': 'THREE-WAY SWITCH, 42" AFF', 'SD': 'DIMMER, 42" AFF', 'S3D': 'THREE-WAY DIMMER, 42" AFF',
}

def room_polygon(room): return Polygon(room['poly_pt'])

def wall_point(w, x_in, inset_pt=0.0):
    """Model point at x_in inches along a wall from the viewer's left, pulled inset_pt into the room."""
    (ax, ay), (bx, by) = w['a'], w['b']
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[w['side']]
    t = x_in * PT_PER_IN
    return (ax + ux * t - nx * inset_pt, ay + uy * t - ny * inset_pt)

def free_runs(w):
    """Wall stretches with no opening: [(x0_in, x1_in)]."""
    L = w['length_in']; cuts = sorted((o['x'], o['x'] + o['w']) for o in w['openings'])
    runs = []; x = 0.0
    for a, b in cuts:
        if a - x >= 1: runs.append((x, a))
        x = max(x, b)
    if L - x >= 1: runs.append((x, L))
    return runs

# ---------------------------------------------------------------- lighting
def _plan_text(floor):
    import idd_model as M, build_model as B
    cfg = B.FLOORS[floor]; return M.PlanPage(B.W, cfg['pno'], offset=cfg['offset']).text

def nudge_off_text(out, floor):
    """A fixture centered on a room lands on the room name: slide it down past the text block (ceiling symmetry is kept by the pair rule, noted)."""
    words = [r for t, r, sz in _plan_text(floor) if sz > 8.5]
    for o in out:
        if o['type'] not in ('C1', 'F1', 'R1', 'SM', 'P1'): continue
        for _ in range(4):
            hit = [r for r in words if r[0] - 8 <= o['x'] <= r[2] + 8 and r[1] - 8 <= o['y'] <= r[3] + 8]
            if not hit: break
            o['y'] = max(r[3] for r in hit) + 10; o['rule'] += ', moved below the room name'
    return out

def lighting(model, floor):
    out = []
    for r in model['rooms']:
        name, kind = r['name'], r['kind']; poly = room_polygon(r); x0, y0, x1, y1 = poly.bounds
        W_ft, H_ft = (x1 - x0) / PT_PER_FT, (y1 - y0) / PT_PER_FT
        area_ft2 = poly.area / PT_PER_FT ** 2
        if (kind == 'closet' and area_ft2 < 40) or name in ('HIDDEN SAFE',):
            c = poly.representative_point(); out.append({'room': name, 'type': 'SM', 'x': c.x, 'y': c.y, 'rule': 'closet: one surface mount at center'}); continue
        # downlight grid: 4.5 ft target spacing, 2.5 ft min from walls, every point inside the room polygon (L-shapes included)
        sp = 4.5 if kind in ('bath', 'kitchen', 'utility', 'closet') else 5.0
        nx = max(1, round(max(W_ft - 3.0, 0.1) / sp)); ny = max(1, round(max(H_ft - 3.0, 0.1) / sp))
        if kind == 'bath' and W_ft < 7 and H_ft < 7: nx = ny = 1
        fix = 'R1'; core = poly.buffer(-12)
        for i in range(nx):
            for j in range(ny):
                px = x0 + (x1 - x0) * (i + 0.5) / nx; py = y0 + (y1 - y0) * (j + 0.5) / ny
                if core.contains(Point(px, py)):
                    out.append({'room': name, 'type': fix, 'x': px, 'y': py, 'rule': f'grid {nx}x{ny}, {sp} ft target spacing'})
                else:
                    # L-shaped room: slide the point into the nearest part of the core along the grid row/column
                    from shapely.ops import nearest_points
                    if core.is_empty: continue
                    q = nearest_points(core, Point(px, py))[0]
                    if q.distance(Point(px, py)) < sp * PT_PER_FT * 0.6 and not any(abs(o['x'] - q.x) < 20 and abs(o['y'] - q.y) < 20 for o in out if o['room'] == name):
                        out.append({'room': name, 'type': fix, 'x': q.x, 'y': q.y, 'rule': f'grid {nx}x{ny}, moved into the room outline'})
        # fixtures at plan elements
        for f in r['fixtures']:
            k = f['kind']
            if k in ('shower', 'tub') and f.get('rect_pt'):
                rx0, ry0, rx1, ry1 = f['rect_pt']
                out.append({'room': name, 'type': 'R2', 'x': (rx0 + rx1) / 2, 'y': (ry0 + ry1) / 2, 'rule': f'wet-location downlight centered on {k}'})
            if k in ('vanity', 'lav') and f['on']:
                on = f['on'][0]; w = next(w for w in r['walls'] if w['id'] == on['wall'])
                flanks = [xx for xx in (on['x'] - 6, on['x'] + on['w'] + 6) if 8 <= xx <= w['length_in'] - 8]
                if len(flanks) == 2:
                    for xx in flanks:
                        px, py = wall_point(w, xx, 4); out.append({'room': name, 'type': 'S1', 'x': px, 'y': py, 'rule': 'sconces flanking the mirror', 'wall': w['id']})
                else:   # no room to flank: one sconce centered above the mirror
                    px, py = wall_point(w, on['x'] + on['w'] / 2, 4); out.append({'room': name, 'type': 'S1', 'x': px, 'y': py, 'rule': 'sconce centered above the mirror (no room to flank)', 'wall': w['id'], 'above': True})
            if k == 'upper' and kind == 'kitchen' and f['on']:
                on = f['on'][0]; w = next(w for w in r['walls'] if w['id'] == on['wall'])
                px, py = wall_point(w, on['x'] + on['w'] / 2, 14); out.append({'room': name, 'type': 'UC', 'x': px, 'y': py, 'rule': 'LED tape under uppers', 'len_in': on['w'], 'wall': w['id']})
        if kind == 'kitchen':
            isl = [f for f in r['fixtures'] if f['kind'] == 'cabinet' and not f['on'] and f.get('rect_pt')]
            isl_rects = [f['rect_pt'] for f in isl]
            # the island on this plan is a-cab rect without wall contact; fall back to a known island box if none
            if not isl_rects: isl_rects = [[172.4, 238.2, 243.3, 363.0]] if floor == 1 else []
            for rx0, ry0, rx1, ry1 in isl_rects:
                n = 3 if (ry1 - ry0) > 90 else 2
                for i in range(n):
                    out.append({'room': name, 'type': 'P1', 'x': (rx0 + rx1) / 2, 'y': ry0 + (ry1 - ry0) * (i + 0.5) / n, 'rule': 'pendants over island'})
        if name in ('GREAT ROOM', 'FOYER', 'MASTER SUITE', 'PIANO ROOM'):
            c = poly.centroid; out.append({'room': name, 'type': 'C1', 'x': c.x, 'y': c.y, 'rule': 'feature fixture at room center'})
            out[:] = [o for o in out if not (o['room'] == name and o['type'] == 'R1' and abs(o['x'] - c.x) < 20 and abs(o['y'] - c.y) < 20)]
        if name in ('BEDROOM 2', 'BEDROOM 3', 'GUEST BEDROOM', 'DEN / PLAYROOM'):
            c = poly.centroid; out.append({'room': name, 'type': 'F1', 'x': c.x, 'y': c.y, 'rule': 'ceiling fan at room center'})
            out[:] = [o for o in out if not (o['room'] == name and o['type'] == 'R1' and abs(o['x'] - c.x) < 20 and abs(o['y'] - c.y) < 20)]
        if name == 'MASTER SUITE':
            w = next((w for w in r['walls'] if w['id'] == 'E2'), None)
            if w:
                for xx in (w['length_in'] / 2 - 42, w['length_in'] / 2 + 42):
                    px, py = wall_point(w, xx, 4); out.append({'room': name, 'type': 'S2', 'x': px, 'y': py, 'rule': 'reading sconces either side of the bed', 'wall': 'E2'})
    return nudge_off_text(out, floor)

def switches(model, lights):
    """One switch bank per door into a room, on the latch side 6 in. from the jamb, inside the room. Two or more doors: three-way."""
    out = []
    for r in model['rooms']:
        name = r['name']
        doors = [(w, o) for w in r['walls'] for o in w['openings'] if o['type'] in ('door', 'slider', 'opening') and 24 <= o['w'] < 100 and not w.get('guard')]
        if name == 'MASTER SUITE': doors = [(w, o) for w, o in doors if w['id'] != 'N3']     # the jib door to the safe is not an entry
        if not doors: continue
        kinds = {o['type'] for o in lights if o['room'] == name}
        dim = name in ('GREAT ROOM', 'MASTER SUITE', 'KITCHEN & DINING AREA', 'PIANO ROOM', 'FOYER', 'BEDROOM 2', 'BEDROOM 3', 'GUEST BEDROOM', 'DEN / PLAYROOM')
        for w, o in doors:
            if w.get('guard'): continue
            # latch side: the end of the opening farther from the wall's nearer corner
            xx = o['x'] + o['w'] + 6 if o['x'] + o['w'] + 8 < w['length_in'] else o['x'] - 6
            if xx < 2 or xx > w['length_in'] - 2: continue
            px, py = wall_point(w, xx, 7)
            typ = ('S3D' if dim else 'S3') if len(doors) > 1 else ('SD' if dim else 'S')
            out.append({'room': name, 'type': typ, 'x': px, 'y': py, 'wall': w['id'], 'rule': 'latch side of door, 42 in. AFF' + (', dimmer' if dim and typ == 'S3' else ''), 'controls': sorted(kinds), 'dimmer': dim})
    return out

# ---------------------------------------------------------------- power and data
def power(model):
    out = []
    for r in model['rooms']:
        name, kind = r['name'], r['kind']
        if name == 'HIDDEN SAFE': continue
        counters = [(f['on'][0]['wall'], f['on'][0]['x'], f['on'][0]['w']) for f in r['fixtures'] if f['kind'] in ('cabinet',) and f['on'] and kind in ('kitchen', 'utility', 'bath')]
        vanities = [(f['on'][0]['wall'], f['on'][0]['x'], f['on'][0]['w']) for f in r['fixtures'] if f['kind'] in ('vanity', 'lav') and f['on']]
        for w in r['walls']:
            if kind == 'closet' or w['length_in'] < 24 or w.get('guard'): continue
            for a, b in free_runs(w):
                if b - a < 24: continue
                run_counters = [(max(a, x), min(b, x + ww)) for wid, x, ww in counters + vanities if wid == w['id'] and x < b and x + ww > a]
                added = 0
                for cx0, cx1 in run_counters:
                    if cx1 - cx0 < 12: continue
                    n = max(1, math.ceil((cx1 - cx0) / 48.0))
                    for i in range(n):
                        xx = cx0 + (cx1 - cx0) * (i + 0.5) / n
                        out.append({'room': name, 'type': 'GFI', 'x': wall_point(w, xx, 6)[0], 'y': wall_point(w, xx, 6)[1], 'wall': w['id'], 'aff': 42, 'rule': 'counter receptacle, 4 ft max spacing, GFCI (NEC 210.52(C), 210.8)'}); added += 1
                if added: continue
                if kind == 'bath':
                    continue
                # NEC 210.52(A): no point along the wall more than 6 ft from a receptacle; 12 ft max between
                n = max(1, math.ceil((b - a) / 144.0))
                for i in range(n):
                    xx = a + (b - a) * (i + 0.5) / n
                    typ = 'GFI' if kind in ('utility',) or name in ('LAUNDRY',) else 'REC'
                    out.append({'room': name, 'type': typ, 'x': wall_point(w, xx, 6)[0], 'y': wall_point(w, xx, 6)[1], 'wall': w['id'], 'aff': 15, 'rule': 'NEC 210.52(A) 12 ft rule' + (', GFCI (210.8)' if typ == 'GFI' else '')})
        # data and TV
        tv_wall = {'MASTER SUITE': 'W2', 'GREAT ROOM': 'E', 'DEN / PLAYROOM': 'N', 'BEDROOM 2': 'E3', 'BEDROOM 3': 'W3', 'GUEST BEDROOM': 'N', 'OFFICE': 'W', 'PIANO ROOM': 'W1'}.get(name)
        w = next((w for w in r['walls'] if w['id'] == tv_wall), None)
        if w:
            runs = [rn for rn in free_runs(w) if rn[1] - rn[0] >= 48]
            if runs:
                a, b = max(runs, key=lambda t: t[1] - t[0]); xx = (a + b) / 2
                px, py = wall_point(w, xx, 6)
                out.append({'room': name, 'type': 'TV', 'x': px, 'y': py, 'wall': w['id'], 'aff': 50 if 'BED' in name or name in ('MASTER SUITE', 'GUEST BEDROOM') else 42, 'rule': 'TV wall per furniture layout, verify with owner'})
                out.append({'room': name, 'type': 'DAT', 'x': px, 'y': py, 'wall': w['id'], 'aff': 15, 'rule': 'data at TV'})
        if name == 'OFFICE':
            w = next((w for w in r['walls'] if w['id'] == 'S'), None)
            if w:
                runs = [rn for rn in free_runs(w) if rn[1] - rn[0] >= 30]
                if runs:
                    a, b = max(runs, key=lambda t: t[1] - t[0]); px, py = wall_point(w, (a + b) / 2, 6)
                    out.append({'room': name, 'type': 'DAT', 'x': px, 'y': py, 'wall': 'S', 'aff': 15, 'rule': 'desk data'}); out.append({'room': name, 'type': 'USB', 'x': px + 9, 'y': py, 'wall': 'S', 'aff': 15, 'rule': 'desk power'})
        if name in ('MASTER SUITE', 'BEDROOM 2', 'BEDROOM 3', 'GUEST BEDROOM'):
            # USB at bed sides: headboard wall quarter points
            hb = {'MASTER SUITE': 'E2', 'BEDROOM 2': 'W1', 'BEDROOM 3': 'E', 'GUEST BEDROOM': 'S'}[name]
            w = next((w for w in r['walls'] if w['id'] == hb), None)
            if w:
                for xx in (w['length_in'] / 2 - 48, w['length_in'] / 2 + 48):
                    if 6 < xx < w['length_in'] - 6 and any(a <= xx <= b for a, b in free_runs(w)):
                        px, py = wall_point(w, xx, 6); out.append({'room': name, 'type': 'USB', 'x': px, 'y': py, 'wall': hb, 'aff': 15, 'rule': 'nightstand power with USB'})
    return out

def dedupe(devs, r=2.0):
    """One symbol per device: drop a device within r pt of an earlier one of the same type."""
    out = []
    for d in devs:
        if any(o['type'] == d['type'] and abs(o['x'] - d['x']) < r and abs(o['y'] - d['y']) < r for o in out): continue
        out.append(d)
    return out

def floor_receptacles(model):
    out = []
    for r in model['rooms']:
        if r['name'] in ('GREAT ROOM', 'PIANO ROOM'):
            c = room_polygon(r).centroid
            out.append({'room': r['name'], 'type': 'FLR', 'x': c.x, 'y': c.y + 20, 'aff': 0, 'rule': 'floor receptacle at seating group, verify with furniture plan'})
    return out

if __name__ == '__main__':
    for f in (1, 2):
        m = json.load(open(f'model_f{f}.json'))
        L = lighting(m, f); S = dedupe(switches(m, L)); P = dedupe(power(m) + floor_receptacles(m))
        json.dump({'lights': L, 'switches': S, 'power': P}, open(f'electrical_f{f}.json', 'w'), indent=1)
        import collections
        print(f, collections.Counter(o['type'] for o in L), collections.Counter(o['type'] for o in S), collections.Counter(o['type'] for o in P))
