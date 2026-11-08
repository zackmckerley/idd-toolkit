"""Room model extraction from an AutoCAD PDF plot (interior-design-drawings skill).

Builds, per floor, a JSON model of rooms: interior wall faces, openings (door, window, cased opening) located
along each face in inches, fixtures, cabinets and stairs, from the CAD layers that survive in the PDF as optional
content groups. Rooms are seeded by name and a point; rectangular rooms are measured with rays against the wall
union; irregular rooms take an explicit polygon.

Display coordinates are sheet points (y down). PT_PER_FT converts to inches: in = pt * 12 / PT_PER_FT.
"""
import re, json, math, collections
import pymupdf as fitz
from shapely.geometry import Polygon, box, Point, LineString, MultiPolygon
from shapely.ops import unary_union

PT_PER_FT = 13.5
IN_PER_PT = 12.0 / PT_PER_FT

def polys_from(x, M):
    pts = []; out = []
    for it in x['items']:
        if it[0] == 'l':
            a, b = it[1] * M, it[2] * M
            if pts and (abs(pts[-1][0] - a.x) > 1e-3 or abs(pts[-1][1] - a.y) > 1e-3):
                out.append(pts); pts = []
            if not pts: pts.append((a.x, a.y))
            pts.append((b.x, b.y))
        elif it[0] == 're':
            r = it[1] * M; out.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
        elif it[0] == 'qu':
            q = it[1] * M; out.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)])
    if pts: out.append(pts)
    res = []
    for o in out:
        if len(o) >= 3:
            pg = Polygon(o).buffer(0)
            if pg.area > 1e-4: res.append(pg)
    return res

class PlanPage:
    """One plan page: layer geometry in display coordinates, shifted by `offset` so several bases of one floor align."""
    def __init__(self, pdf, pno, offset=(0.0, 0.0), wall_layers=('a-bro hatch', 'a-bro'), wall_fill_max=0.5):
        self.doc = fitz.open(pdf); self.page = self.doc[pno]; self.R = self.page.rotation_matrix
        self.dx, self.dy = offset
        self.items = collections.defaultdict(list)     # layer -> list of dict(rect, type, fill, paths[polys], segs)
        walls = []
        for x in self.page.get_drawings():
            lyr = x.get('layer') or ''
            r = fitz.Rect(x['rect']) * self.R; r.normalize()
            rect = (r.x0 - self.dx, r.y0 - self.dy, r.x1 - self.dx, r.y1 - self.dy)
            segs = []
            for it in x['items']:
                if it[0] == 'l':
                    a, b = it[1] * self.R, it[2] * self.R
                    segs.append(((a.x - self.dx, a.y - self.dy), (b.x - self.dx, b.y - self.dy)))
            rec = {'rect': rect, 'type': x['type'], 'fill': x.get('fill'), 'segs': segs, 'raw': x}
            self.items[lyr].append(rec)
            f = x.get('fill')
            if lyr in wall_layers and f is not None and f[0] < wall_fill_max:
                walls += [shift(pg, -self.dx, -self.dy) for pg in polys_from(x, self.R)]
        # architect wall line layers (xref) become thin bands so Floor 1 (no poché on the exterior) still closes
        wall_lines = []
        for lyr, recs in self.items.items():
            tail = lyr.split('|')[-1].upper()
            if tail.startswith('A-WALL') and tail not in ('A-WALL-HEAD', 'A-WALL-HATCH-NEW'):
                for rec in recs:
                    for a, b in rec['segs']:
                        if a != b: wall_lines.append(LineString([a, b]).buffer(0.9))
        self.wall_lines = unary_union(wall_lines) if wall_lines else Polygon()
        self.walls = unary_union(walls + [self.wall_lines])
        closers = [box(*r['rect']).buffer(0.6) for r in self.layer('A-WINDOW')] + [box(*r['rect']).buffer(1.2) for r in self.layer('A-WALL-HEAD')]
        # sliders, pocket and folding doors are drawn as thin rects along the wall line (no dashed head): close them too
        for r in self.layer('A-DOOR'):
            x0, y0, x1, y1 = r['rect']; w, h = x1 - x0, y1 - y0
            if min(w, h) < 4.0 and max(w, h) > 12.0:
                closers.append(box(x0, y0, x1, y1).buffer(1.0))
        self.closers = closers
        self.boundary = unary_union([self.walls] + closers)
        self.text = []
        for b in self.page.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    t = s['text'].strip()
                    if not t: continue
                    rr = fitz.Rect(s['bbox']) * self.R; rr.normalize()
                    self.text.append((t, (rr.x0 - self.dx, rr.y0 - self.dy, rr.x1 - self.dx, rr.y1 - self.dy), s['size']))
    def layer(self, suffix):
        return [rec for lyr, recs in self.items.items() if lyr.endswith(suffix) for rec in recs]
    def rays(self, x, y, far=600):
        P = Point(x, y); res = {}
        for name, (dx, dy) in dict(W=(-1, 0), E=(1, 0), N=(0, -1), S=(0, 1)).items():
            ln = LineString([(x, y), (x + dx * far, y + dy * far)])
            it = ln.intersection(self.boundary)
            res[name] = P.distance(it) if not it.is_empty else None
        return res

def shift(pg, dx, dy):
    from shapely.affinity import translate
    return translate(pg, dx, dy)

def cluster_rects(rects, gap=1.5):
    """Merge overlapping or near rects (fixture symbols come as many small paths and zero-width lines) into clusters."""
    polys = [box(r[0], r[1], r[2], r[3]).buffer(gap, join_style=2) for r in rects]
    if not polys: return []
    u = unary_union(polys)
    gs = list(u.geoms) if u.geom_type == 'MultiPolygon' else [u]
    out = []
    for g in gs:
        x0, y0, x1, y1 = g.bounds
        out.append((round(x0 + gap, 2), round(y0 + gap, 2), round(x1 - gap, 2), round(y1 - gap, 2)))
    return out

def classify_fixture(rect, layer):
    """Name a fixture cluster by its size in inches and the layer it came from."""
    w, h = (rect[2] - rect[0]) * IN_PER_PT, (rect[3] - rect[1]) * IN_PER_PT
    lo, hi = sorted((w, h))
    if layer.endswith('A-EQPM-BATH'):
        if 54 <= hi <= 76 and 28 <= lo <= 37: return 'tub'
        if lo >= 38 and hi >= 34: return 'shower'
        if 25 <= hi <= 31 and 13 <= lo <= 17: return 'toilet'
        if hi >= 24 and 16 <= lo <= 24: return 'vanity'
        if 12 <= hi <= 24 and 10 <= lo <= 24: return 'lav'
        return 'bath_fixture'
    if layer.endswith('A-EQPM-KIT'):
        if hi >= 30 and lo >= 24: return 'range' if hi < 40 else 'fridge'
        if 20 <= hi <= 40 and 16 <= lo <= 26: return 'sink'
        return 'appliance'
    if layer.endswith('a-cab') or layer.endswith('a-millwrk'):
        return 'cabinet'
    return 'item'

class Room:
    def __init__(self, plan, name, seed=None, poly=None, kind='room', ceiling_in=120.0):
        self.plan, self.name, self.kind, self.ceiling = plan, name, kind, ceiling_in
        if poly is not None:
            self.poly = poly if isinstance(poly, Polygon) else Polygon(poly)
        else:
            r = plan.rays(*seed)
            assert all(v is not None for v in r.values()), (name, r)
            x, y = seed
            self.poly = box(x - r['W'], y - r['N'], x + r['E'], y + r['S'])
        self.x0, self.y0, self.x1, self.y1 = self.poly.bounds
    def faces(self):
        """Wall faces as (side, start_pt, end_pt) running clockwise as seen on the plan; the viewer faces the side."""
        return {'N': ((self.x0, self.y0), (self.x1, self.y0)),     # north wall, viewer faces north: left is west
                'E': ((self.x1, self.y0), (self.x1, self.y1)),     # east wall: left is north
                'S': ((self.x1, self.y1), (self.x0, self.y1)),     # south wall: left is east
                'W': ((self.x0, self.y1), (self.x0, self.y0))}     # west wall: left is south
    def _along(self, side, rect, face=None):
        """(a, b) positions of a rect along a face in pt from the viewer's left end, plus its distance from the face line."""
        (ax, ay), (bx, by) = face or self.faces()[side]
        x0, y0, x1, y1 = rect
        if side == 'N': a, b, dist = x0 - ax, x1 - ax, abs((y0 + y1) / 2 - ay)
        elif side == 'S': a, b, dist = ax - x1, ax - x0, abs((y0 + y1) / 2 - ay)
        elif side == 'E': a, b, dist = y0 - ay, y1 - ay, abs((x0 + x1) / 2 - ax)
        else: a, b, dist = ay - y1, ay - y0, abs((x0 + x1) / 2 - ax)
        return a, b, dist
    def openings(self, side, probe=2.0, step=0.5, min_len=8.0, near=8.0, face=None):
        """Openings on one face from the drawing records: dashed door heads (A-WALL-HEAD), window rects (A-WINDOW) and
        thin door panels in the wall plane (sliders, pockets). Runs with no wall fill and no record become 'opening' (cased).
        Returns [{'x': in from the viewer's left, 'w': in, 'type': door|window|slider|opening}]."""
        (ax, ay), (bx, by) = face or self.faces()[side]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[side]
        horiz = side in ('N', 'S')
        recs = []
        for kind, layer in (('door', 'A-WALL-HEAD'), ('window', 'A-WINDOW'), ('slider', 'A-DOOR'), ('window', 'A-DOOR')):
            for r in self.plan.layer(layer):
                x0, y0, x1, y1 = r['rect']; w, h = x1 - x0, y1 - y0
                if kind == 'slider' and not (min(w, h) < 4.0 and max(w, h) > 12.0): continue
                if kind == 'slider':
                    # a thin panel is a slider / pocket / jib door only when it lies in the wall plane; a thin rect on the room side of the
                    # face is an open door leaf belonging to the adjacent wall (and must not become a phantom door here)
                    cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
                    inward = {'N': cy_ - ay, 'S': ay - cy_, 'E': ax - cx_, 'W': cx_ - ax}[side]
                    if inward > 1.5: continue
                if kind == 'window' and layer == 'A-DOOR':
                    if not (6 <= min(w, h) and max(w, h) <= 20): continue        # glazed panel units drawn as small rects in the wall plane
                    a, b, dist = self._along(side, r['rect'], face)
                    if dist > near or b < 0 or a > L: continue
                    recs.append((max(0.0, a), min(L, b), kind)); continue
                if (horiz and w < h) or (not horiz and h < w): continue          # must run along the face
                a, b, dist = self._along(side, r['rect'], face)
                if dist > near or b < 0 or a > L: continue
                recs.append((max(0.0, a), min(L, b), kind))
        # merge records of one kind that touch (window mullion pieces, head segments)
        recs.sort(); merged = []
        for a, b, kind in recs:
            if merged and merged[-1][2] == kind and a <= merged[-1][1] + 2.0:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b), kind)
            else: merged.append((a, b, kind))
        # a dashed head over a window reads as a door head: the window wins
        wins = [(a, b) for a, b, k in merged if k == 'window']
        merged = [(a, b, k) for a, b, k in merged if not (k == 'door' and any(min(b, wb) - max(a, wa) > 0.5 * (b - a) for wa, wb in wins))]
        # cased openings: runs with no wall fill not covered by a record
        runs = []; d = 0.0; cur = None
        while d <= L:
            px, py = ax + ux * d + nx * probe, ay + uy * d + ny * probe
            inwall = self.plan.walls.contains(Point(px, py))
            if not self.poly.buffer(0.8).contains(Point(px - nx * 2 * probe, py - ny * 2 * probe)): inwall = True
            if not inwall and cur is None: cur = d
            if inwall and cur is not None: runs.append((cur, d)); cur = None
            d += step
        if cur is not None: runs.append((cur, L))
        # a slider / pocket panel is drawn partly in its pocket: the real opening is the gap in the wall fill, so where a free run
        # overlaps a slider record the run's extent replaces the record's
        fixed = []
        for a, b, kind in merged:
            if kind == 'slider':
                hits = [(ra, rb) for ra, rb in runs if min(b, rb) - max(a, ra) > 0.25 * (b - a)]
                if hits:
                    ra, rb = max(hits, key=lambda t: t[1] - t[0]); fixed.append((max(0.0, ra), min(L, rb), 'slider')); continue
            fixed.append((a, b, kind))
        merged = fixed
        leaves = [box(*r['rect']) for r in self.plan.layer('A-DOOR') if min(r['rect'][2] - r['rect'][0], r['rect'][3] - r['rect'][1]) >= 12]
        for a, b in runs:
            if b - a < min_len: continue
            covered = sum(max(0.0, min(b, mb) - max(a, ma)) for ma, mb, k in merged)
            if covered < 0.25 * (b - a):
                # a swing leaf drawn either side of the gap makes it a door, otherwise a cased opening
                pa = (ax + ux * a, ay + uy * a); pb = (ax + ux * b, ay + uy * b)
                probe_box = box(min(pa[0], pb[0]) - abs(nx) * 50, min(pa[1], pb[1]) - abs(ny) * 50, max(pa[0], pb[0]) + abs(nx) * 50, max(pa[1], pb[1]) + abs(ny) * 50)
                kind = 'door' if any(lf.intersects(probe_box) and lf.intersection(probe_box).area > 0.5 * lf.area for lf in leaves) else 'opening'
                merged.append((a, b, kind))
        merged.sort()
        out = [{'x': round(a * IN_PER_PT, 1), 'w': round((b - a) * IN_PER_PT, 1), 'type': kind} for a, b, kind in merged if b - a >= min_len and not (kind == 'slider' and (b - a) * IN_PER_PT < 18)]
        return out
    def contents(self, layer_suffix, min_size=6.0, gap=1.5):
        rs = [r['rect'] for r in self.plan.layer(layer_suffix) if self.poly.buffer(1.0).intersects(box(*r['rect']))]
        cl = cluster_rects(rs, gap)
        return [c for c in cl if (c[2] - c[0]) >= min_size and (c[3] - c[1]) >= min_size]
    def cabinet_runs(self, min_run_in=12.0):
        """Cabinet runs per wall from the counter front lines: a-cab segments parallel to a wall 18 to 30 in. off it are base
        cabinets (counter front), a-cab oh segments 9 to 16 in. off it are uppers. An L-shaped run is two runs, one per wall."""
        out = []
        def segs_of(suffix):
            res = []
            for r in self.plan.layer(suffix):
                if not self.poly.buffer(1.0).intersects(box(*r['rect'])): continue
                x0, y0, x1, y1 = r['rect']
                if (x1 - x0) > 3 and (y1 - y0) > 3:
                    # a real rect (counter outline): the front edge is the edge farthest from the wall it touches; emit only that edge, tagged with its depth
                    res.append((((x0, y0), (x1, y0)), 'rect', r['rect'])); res.append((((x1, y1), (x0, y1)), 'rect', r['rect']))
                    res.append((((x1, y0), (x1, y1)), 'rect', r['rect'])); res.append((((x0, y1), (x0, y0)), 'rect', r['rect']))
                else:
                    for (ax, ay), (bx, by) in r['segs']:
                        res.append((((ax, ay), (bx, by)), 'line', None))
            return res
        base_segs, upper_segs = segs_of('a-cab'), segs_of('a-cab oh')
        for w in self.walls():
            face = (tuple(w['a']), tuple(w['b'])); Lpt = w['length_in'] / IN_PER_PT
            horiz = w['side'] in ('N', 'S')
            # the opposite wall's distance: a counter line can only belong to this wall if it is nearer to it than to the far wall
            x0b, y0b, x1b, y1b = self.poly.bounds
            depth_room = (y1b - y0b if horiz else x1b - x0b) * IN_PER_PT
            for kind, segs, lo, hi in (('cabinet', base_segs, 16.0, 40.0), ('upper', upper_segs, 9.0, 15.9)):
                ivs = []
                for ((ax, ay), (bx, by)), src, rc in segs:
                    if horiz and abs(ay - by) > 0.5: continue
                    if not horiz and abs(ax - bx) > 0.5: continue
                    off = {'N': ay - w['a'][1], 'S': w['a'][1] - ay, 'E': w['a'][0] - ax, 'W': ax - w['a'][0]}[w['side']] * IN_PER_PT
                    if not (lo <= off <= hi): continue
                    if src == 'rect':
                        # the rect must touch this wall with its near edge (within 4 pt) and this edge must be its far edge
                        rx0, ry0, rx1, ry1 = rc
                        near_edge = {'N': ry0 - w['a'][1], 'S': w['a'][1] - ry1, 'E': w['a'][0] - rx1, 'W': rx0 - w['a'][0]}[w['side']]
                        if not (-3.0 <= near_edge <= 4.0): continue
                    elif off > depth_room / 2: continue
                    rc = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
                    a, b, _ = self._along(w['side'], rc, face)
                    a, b = max(a, 0.0), min(b, Lpt)
                    if b - a > 2.0: ivs.append((a, b, off))
                ivs.sort(); runs = []; gap = 3.0 if kind == 'cabinet' else 7.0
                for a, b, d in ivs:
                    if runs and a <= runs[-1][1] + gap: runs[-1] = (runs[-1][0], max(runs[-1][1], b), max(runs[-1][2], d))
                    else: runs.append((a, b, d))
                for a, b, d in runs:
                    if (b - a) * IN_PER_PT >= min_run_in:
                        out.append({'kind': kind, 'layer': 'a-cab', 'rect_pt': None, 'size_in': [round((b - a) * IN_PER_PT, 1), round(d, 1)],
                                    'on': [{'wall': w['id'], 'x': round(a * IN_PER_PT, 1), 'w': round((b - a) * IN_PER_PT, 1)}]})
        return out
    def fixtures(self):
        """Fixture clusters with a name, size in inches and the wall(s) they sit against, plus cabinet runs per wall."""
        out = self.cabinet_runs()
        for suffix in ('A-EQPM-BATH', 'A-EQPM-KIT'):
            for c in self.contents(suffix, gap=2.5 if suffix == 'A-EQPM-BATH' else 1.5):
                kind = classify_fixture(c, suffix)
                walls = []
                for w in self.walls():
                    a, b, dist = self._along(w['side'], c, (tuple(w['a']), tuple(w['b'])))
                    # against this wall if the cluster's near edge is within 4 pt of the face and it overlaps the face run
                    x0, y0, x1, y1 = c
                    near = {'N': y0 - w['a'][1], 'S': w['a'][1] - y1, 'E': w['a'][0] - x1, 'W': x0 - w['a'][0]}[w['side']]
                    along_pt = min(b, w['length_in'] / IN_PER_PT) - max(a, 0)
                    depth_pt = (y1 - y0) if w['side'] in ('N', 'S') else (x1 - x0)
                    ok = -3.0 <= near <= 4.0 and along_pt > 4
                    if kind in ('vanity', 'lav', 'cabinet', 'sink', 'fridge', 'range', 'appliance', 'item'): ok = ok and along_pt >= 0.9 * depth_pt
                    if kind == 'toilet': ok = ok and along_pt <= depth_pt
                    if ok:
                        walls.append({'wall': w['id'], 'x': round(max(a, 0) * IN_PER_PT, 1), 'w': round((min(b, w['length_in'] / IN_PER_PT) - max(a, 0)) * IN_PER_PT, 1)})
                out.append({'kind': kind, 'layer': suffix, 'rect_pt': [round(v, 2) for v in c],
                            'size_in': [round((c[2] - c[0]) * IN_PER_PT, 1), round((c[3] - c[1]) * IN_PER_PT, 1)], 'on': walls})
        return out
    def labels(self):
        return [t for t, r, s in self.plan.text if self.poly.contains(Point((r[0] + r[2]) / 2, (r[1] + r[3]) / 2))]
    def along(self, side, rect):
        """Position of a rect along a face, in inches from the face's left end as the viewer sees it, plus its width and depth off the wall."""
        (ax, ay), (bx, by) = self.faces()[side]
        x0, y0, x1, y1 = rect
        if side in ('N', 'S'):
            lo, hi = (x0, x1) if side == 'N' else (bx + (bx - x1) * 0 and 0, 0)
        if side == 'N': a, b = x0 - ax, x1 - ax; depth = y1 - self.y0
        elif side == 'S': a, b = ax - x1, ax - x0; depth = self.y1 - y0
        elif side == 'E': a, b = y0 - ay, y1 - ay; depth = self.x1 - x0
        else: a, b = ay - y1, ay - y0; depth = x1 - self.x0
        return round(a * IN_PER_PT, 1), round((b - a) * IN_PER_PT, 1), round(depth * IN_PER_PT, 1)
    def length_in(self, side):
        (ax, ay), (bx, by) = self.faces()[side]
        return round(math.hypot(bx - ax, by - ay) * IN_PER_PT, 1)
    def wall_runs(self, side, tol=14.0, min_len=27.0, step=0.5):
        """Wall faces on one side from the polygon envelope: runs of constant depth, ordered left to right as the viewer sees them.
        Handles L-shapes and notches (a headboard wall in front of a safe, a shower alcove) that a bounding box hides."""
        x0, y0, x1, y1 = self.poly.bounds
        horiz = side in ('N', 'S')
        lo, hi = (x0, x1) if horiz else (y0, y1)
        samples = []
        t = lo
        while t <= hi:
            ln = LineString([(t, y0 - 1), (t, y1 + 1)]) if horiz else LineString([(x0 - 1, t), (x1 + 1, t)])
            it = ln.intersection(self.poly)
            if not it.is_empty:
                cs = [c for g in (it.geoms if hasattr(it, 'geoms') else [it]) for c in g.coords]
                vals = [c[1] for c in cs] if horiz else [c[0] for c in cs]
                v = {'N': min, 'S': max, 'W': min, 'E': max}[side](vals)
                samples.append((t, v))
            t += step
        runs = []
        for t, v in samples:
            if runs and (abs(v - runs[-1]['v']) <= tol or abs(v - runs[-1]['vs'][-1]) <= 4.0) and t - runs[-1]['t1'] <= step * 1.5:
                runs[-1]['t1'] = t; runs[-1]['vs'].append(v)
            else:
                runs.append({'t0': t, 't1': t, 'v': v, 'vs': [v]})
        merged_runs = []
        for r in runs:
            if merged_runs and abs(r['v'] - merged_runs[-1]['v']) <= tol and r['t0'] - merged_runs[-1]['t1'] <= 3 * step:
                merged_runs[-1]['t1'] = r['t1']; merged_runs[-1]['vs'] += r['vs']
            else: merged_runs.append(r)
        out = []
        for r in merged_runs:
            if r['t1'] - r['t0'] < min_len: continue
            v = sorted(r['vs'])[len(r['vs']) // 2]
            if side == 'N': a, b = (r['t0'], v), (r['t1'], v)
            elif side == 'S': a, b = (r['t1'], v), (r['t0'], v)
            elif side == 'E': a, b = (v, r['t0']), (v, r['t1'])
            else: a, b = (v, r['t1']), (v, r['t0'])
            out.append({'side': side, 'a': a, 'b': b, 'len_pt': r['t1'] - r['t0']})
        if side in ('S', 'W'): out = out[::-1]
        return out
    def walls(self):
        res = []
        for side in 'NESW':
            runs = self.wall_runs(side)
            for i, w in enumerate(runs, 1):
                face = (w['a'], w['b'])
                res.append({'id': f"{side}{i}" if len(runs) > 1 else side, 'side': side, 'a': [round(v, 2) for v in w['a']], 'b': [round(v, 2) for v in w['b']],
                            'length_in': round(w['len_pt'] * IN_PER_PT, 1), 'openings': self.openings(side, face=face)})
        return res
    def to_dict(self):
        d = {'name': self.name, 'kind': self.kind, 'ceiling_in': self.ceiling, 'bounds_pt': [round(v, 2) for v in self.poly.bounds],
             'poly_pt': [[round(x, 2), round(y, 2)] for x, y in self.poly.exterior.coords[:-1]], 'walls': self.walls()}
        d['fixtures'] = self.fixtures()
        d['labels'] = self.labels()
        return d

# ----------------------------------------------------------------------------- automatic room polygons
def room_polygons(plan, extent, cuts=(), head_buffer=2.5, min_area=400.0):
    """Rooms = connected regions of the plan extent not covered by walls, windows, door heads and explicit cut lines
    (for cased openings between rooms). Returns [(polygon, labels)]."""
    closers = list(plan.closers)
    closers += [box(*r['rect']).buffer(head_buffer) for r in plan.layer('A-WALL-HEAD')]
    near_band = plan.walls.buffer(4.0)
    for r in plan.layer('A-DOOR'):
        bx = box(*r['rect']); w, h = bx.bounds[2] - bx.bounds[0], bx.bounds[3] - bx.bounds[1]
        # door and window panels drawn in the wall plane (sliders, folding doors, bay windows) close the opening; swing leaves never do,
        # because carving a leaf out of the room polygon puts a phantom door on the wall the leaf rests against
        if max(w, h) <= 20 and min(w, h) >= 6 and bx.intersects(near_band):
            closers.append(bx.buffer(2.0))
    closers += [LineString(c).buffer(1.0) for c in cuts]
    boundary = unary_union([plan.walls] + closers)
    space = box(*extent).difference(boundary)
    rooms = []
    geoms = list(space.geoms) if space.geom_type == 'MultiPolygon' else [space]
    for g in geoms:
        if g.area < min_area: continue
        g = Polygon(g.exterior, [i for i in g.interiors if Polygon(i).area > 150]).simplify(0.8)     # drop interior slivers (door leaves etc.), keep real islands (wall blobs, columns)
        labels = [t for t, r, s in plan.text if g.contains(Point((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)) and s > 8.5 and t.isupper()]
        rooms.append((g, labels))
    return rooms

def rectilinear_edges(poly, min_len=6.0):
    """Edges of a rectilinear polygon with the side the viewer faces (N/E/S/W) decided by which side the interior lies on."""
    coords = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:          # shapely y-up convention; our y is down so flip to get a consistent walk
        coords = coords[::-1]
    edges = []
    for (ax, ay), (bx, by) in zip(coords, coords[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L < min_len: continue
        mx, my = (ax + bx) / 2, (ay + by) / 2
        if abs(by - ay) < 0.5:   # horizontal edge: interior above or below?
            inside_below = poly.contains(Point(mx, my + 1.5))
            side = 'N' if inside_below else 'S'
        elif abs(bx - ax) < 0.5:
            inside_right = poly.contains(Point(mx + 1.5, my))
            side = 'W' if inside_right else 'E'
        else:
            continue   # non-rectilinear edge (rare); skip
        edges.append({'side': side, 'a': (ax, ay), 'b': (bx, by), 'len_pt': L})
    return edges

def split_necks(poly, k=40.0, min_area=400.0):
    """Split one open-plan polygon at necks narrower than 2k (cased openings, door openings without heads).
    Erode by k, take the components, grow each back and claim the original area nearest to it."""
    from shapely.ops import nearest_points
    core = poly.buffer(-k)
    parts = list(core.geoms) if core.geom_type == 'MultiPolygon' else ([core] if not core.is_empty else [])
    if len(parts) <= 1: return [poly]
    grown = [p.buffer(k + 0.6).intersection(poly) for p in parts]
    claimed = unary_union(grown)
    rest = poly.difference(claimed)
    rest_parts = list(rest.geoms) if rest.geom_type == 'MultiPolygon' else ([rest] if not rest.is_empty else [])
    for rp in rest_parts:
        i = min(range(len(grown)), key=lambda j: grown[j].distance(rp))
        grown[i] = unary_union([grown[i], rp])
    out = []
    for g in grown:
        gs = list(g.geoms) if g.geom_type == 'MultiPolygon' else [g]
        for p in gs:
            if p.area >= min_area: out.append(Polygon(p.exterior).simplify(0.8))
    return out

def label_rooms(plan, polys, min_size=8.5):
    res = []
    for g in polys:
        labels = [t for t, r, s in plan.text if g.contains(Point((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)) and s > min_size and t.isupper()]
        res.append((g, labels))
    return res
