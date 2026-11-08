"""Floor plan from a concept: a plan spec (JSON, inches) becomes a vector base plan PDF on the layers the rest of the
pipeline reads, and the room model (model_f{n}.json) the generators use, exactly, with no extraction step.

    python3 idd_planspec.py spec.json OUT_PREFIX        -> OUT_PREFIX.Base.pdf (one page per floor), model_f{n}.json

Use it when there is no architect's CAD: a hand sketch, a photo of a napkin, a verbal brief, or a plan to be
redesigned. Read the concept, write the spec (rooms as rectangles or orthogonal polygons of their clear interior,
placed with real wall gaps between them), run this, look at the PDF against the concept, then run the pipeline as for
an architect's plan. When an architect's plan arrives later, ingest it (idd_ingest / build_model) and the set re-bases.

Spec (all dimensions in inches; x east, y north; origin anywhere):
{
 "project": {"name": "...", "number": "HD1xx", "address": "..."},
 "scale": "3/16",                       # plotting scale of the base (pt per ft from idd_std / PT_PER_FT)
 "wall": {"exterior": 8.0, "interior": 4.5},
 "floors": [{
   "n": 1, "ceiling": 120,
   "rooms": [{"name": "LIVING ROOM", "kind": "living", "poly": [[0,0],[240,0],[240,192],[0,192]], "ceiling": 132}],
   "openings": [{"room": "LIVING ROOM", "side": "N", "at": 60, "w": 72, "type": "window", "sill": 24, "head": 96},
                {"room": "LIVING ROOM", "side": "W", "at": 30, "w": 36, "type": "door", "hinge": "L", "swing": "in", "head": 96}],
   "fixtures": [{"room": "BATH", "kind": "vanity", "side": "N", "x": 6, "w": 60, "d": 22}]
 }]
}
Opening `at` and fixture `x` run from the left end of the wall as seen from inside the room (the elevation's x), so a
spec reads the same way as the elevations it will produce. Types: door, pair, pocket, slider, opening, window, jib.
Kinds (room): living, dining, kitchen, bath, powder, bedroom, closet, laundry, hall, entry, office, stair, room.
"""
import json, math, sys
import pymupdf as fitz
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

PT_PER_FT = {'1/8': 9.0, '3/16': 13.5, '1/4': 18.0, '3/8': 27.0, '1/2': 36.0}
SIDES = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}


def room_edges(poly):
    """Edges of an orthogonal room polygon (inches) with the side each faces (outward normal), as walls seen from inside:
    a = the viewer's left end, b = the right end, so x along the wall runs left to right in the elevation."""
    pg = Polygon(poly)
    if not pg.exterior.is_ccw: pg = Polygon(list(pg.exterior.coords)[::-1])
    pts = list(pg.exterior.coords)[:-1]; out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        if abs(dx) > 1e-6 and abs(dy) > 1e-6: raise ValueError('room walls must be orthogonal: %s %s' % (a, b))
        n = (dy, -dx); L_ = math.hypot(dx, dy); n = (round(n[0] / L_), round(n[1] / L_))   # CCW ring: outward normal is (dy, -dx)
        side = {v: k for k, v in SIDES.items()}[n]
        # standing inside facing outward along n, the viewer's left is b for a CCW ring
        out.append({'side': side, 'a': b, 'b': a, 'len': L_})
    return out


def build(spec):
    ppf = PT_PER_FT[spec.get('scale', '3/16')]; k = ppf / 12.0
    t_ext = spec.get('wall', {}).get('exterior', 8.0); t_int = spec.get('wall', {}).get('interior', 4.5)
    doc = fitz.open(); models = []
    oc = {n: doc.add_ocg(n, on=True) for n in ('a-bro hatch', 'A-WALL', 'A-DOOR', 'A-WALL-HEAD', 'A-WINDOW', 'A-FLOR-IDEN', 'P-FIXT')}
    for fl in spec['floors']:
        rooms = fl['rooms']; ceil = fl.get('ceiling', 120)
        polys = {r['name']: Polygon(r['poly']) for r in rooms}
        inside = unary_union(list(polys.values()))
        envelope = inside.buffer(t_int / 2 + 0.01, join_style=2).buffer(-(t_int / 2), join_style=2)   # rooms plus the interior wall gaps
        walls = envelope.buffer(t_ext, join_style=2).difference(inside)
        # openings: cut through the wall between the room face and the next space
        cuts = []; heads = []; windows = []; doors = []
        for o in fl.get('openings', []):
            r = next(x for x in rooms if x['name'] == o['room'])
            e = next(x for x in room_edges(r['poly']) if x['side'] == o['side'] and _on_edge(x, o))
            (ax, ay), (bx, by) = e['a'], e['b']; ux, uy = (bx - ax) / e['len'], (by - ay) / e['len']
            nx, ny = SIDES[o['side']]
            p0 = (ax + ux * o['at'], ay + uy * o['at']); p1 = (ax + ux * (o['at'] + o['w']), ay + uy * (o['at'] + o['w']))
            depth = t_ext + 1 if not _neighbour(polys, r['name'], p0, p1, nx, ny, t_int) else t_int + 1
            q = Polygon([p0, p1, (p1[0] + nx * depth, p1[1] + ny * depth), (p0[0] + nx * depth, p0[1] + ny * depth)])
            cuts.append(q)
            if o['type'] == 'window': windows.append((p0, p1, nx, ny, depth - 1))
            else:
                heads.append((p0, p1, nx, ny, depth - 1))
                if o['type'] in ('door', 'pair', 'pocket', 'slider', 'jib'): doors.append((o, p0, p1, nx, ny, depth - 1))
        walls = walls.difference(unary_union(cuts)) if cuts else walls
        minx, miny, maxx, maxy = walls.bounds
        W_, H_ = (maxx - minx) * k + 144, (maxy - miny) * k + 144
        page = doc.new_page(width=max(W_, 792), height=max(H_, 612))
        ox, oy = 72 - minx * k, 72 + maxy * k
        P = lambda x, y: fitz.Point(ox + x * k, oy - y * k)
        def poly_path(sh, g):
            for pg in (g.geoms if hasattr(g, 'geoms') else [g]):
                for ring in [pg.exterior] + list(pg.interiors):
                    cs = [P(*c) for c in ring.coords]; sh.draw_polyline(cs)
        sh = page.new_shape(); poly_path(sh, walls); sh.finish(color=None, fill=(0.0, 0.0, 0.0), even_odd=True, oc=oc['a-bro hatch']); sh.commit()
        sh = page.new_shape(); poly_path(sh, walls); sh.finish(color=(0, 0, 0), width=0.5, oc=oc['A-WALL']); sh.commit()
        for p0, p1, nx, ny, d in heads:
            sh = page.new_shape()
            for off in (0.0, d):
                sh.draw_line(P(p0[0] + nx * off, p0[1] + ny * off), P(p1[0] + nx * off, p1[1] + ny * off))
            sh.finish(color=(0, 0, 0), width=0.3, dashes='[3 2] 0', oc=oc['A-WALL-HEAD']); sh.commit()
        for p0, p1, nx, ny, d in windows:
            sh = page.new_shape()
            for f in (0.0, 0.5, 1.0):
                sh.draw_line(P(p0[0] + nx * d * f, p0[1] + ny * d * f), P(p1[0] + nx * d * f, p1[1] + ny * d * f))
            sh.finish(color=(0, 0, 0), width=0.35, oc=oc['A-WINDOW']); sh.commit()
        for o, p0, p1, nx, ny, d in doors:
            sh = page.new_shape(); w = o['w']
            ux, uy = (p1[0] - p0[0]) / w, (p1[1] - p0[1]) / w
            inward = o.get('swing', 'in') == 'in'; sx, sy = (-nx, -ny) if inward else (nx, ny)
            base_off = 0.0 if inward else d
            if o['type'] in ('pocket', 'slider'):
                sh.draw_rect(fitz.Rect(P(p0[0] + nx * d * 0.4, p0[1] + ny * d * 0.4), P(p1[0] + nx * d * 0.6, p1[1] + ny * d * 0.6)))
            else:
                leaves = [(p0, 1, w / 2), (p1, -1, w / 2)] if o['type'] == 'pair' else ([(p0, 1, w)] if o.get('hinge', 'L') == 'L' else [(p1, -1, w)])
                for (hx, hy), s_, lw in leaves:
                    hx += nx * base_off; hy += ny * base_off
                    tip = (hx + sx * lw, hy + sy * lw); sh.draw_line(P(hx, hy), P(*tip))
                    pts = [P(hx + (ux * s_ * math.cos(a) + sx * math.sin(a)) * lw, hy + (uy * s_ * math.cos(a) + sy * math.sin(a)) * lw) for a in [i * math.pi / 36 for i in range(19)]]
                    sh.draw_polyline(pts)
            sh.finish(color=(0, 0, 0), width=0.35, oc=oc['A-DOOR']); sh.commit()
        for r in rooms:
            c = polys[r['name']].representative_point()
            for i, line in enumerate(r['name'].split('\n')):
                page.insert_text(P(c.x, c.y) + (-len(line) * 2.2, 4 + i * 8), line, fontsize=6.5, oc=oc['A-FLOR-IDEN'])
        for f in fl.get('fixtures', []):
            r = next(x for x in rooms if x['name'] == f['room'])
            e = next(x for x in room_edges(r['poly']) if x['side'] == f['side'])
            (ax, ay), (bx, by) = e['a'], e['b']; ux, uy = (bx - ax) / e['len'], (by - ay) / e['len']; nx, ny = SIDES[f['side']]
            q0 = (ax + ux * f['x'], ay + uy * f['x']); q1 = (ax + ux * (f['x'] + f['w']), ay + uy * (f['x'] + f['w']))
            d = f.get('d', 22)
            g = Polygon([q0, q1, (q1[0] - nx * d, q1[1] - ny * d), (q0[0] - nx * d, q0[1] - ny * d)])
            sh = page.new_shape(); poly_path(sh, g); sh.finish(color=(0, 0, 0), width=0.35, oc=oc['P-FIXT']); sh.commit()
        # the room model, exactly from the spec (display points like an ingested plan, inches for lengths)
        mrooms = []
        for r in rooms:
            ws = []; cnt = {}
            for e in room_edges(r['poly']):
                cnt[e['side']] = cnt.get(e['side'], 0) + 1
                ops = [{'x': o['at'], 'w': o['w'], 'type': {'pair': 'door', 'pocket': 'slider'}.get(o['type'], o['type'])}
                       for o in fl.get('openings', []) if o['room'] == r['name'] and o['side'] == e['side'] and _on_edge(e, o)]
                ws.append({'id': e['side'] + (str(cnt[e['side']]) if sum(1 for x in room_edges(r['poly']) if x['side'] == e['side']) > 1 else ''),
                           'side': e['side'], 'a': [round(P(*e['a']).x, 2), round(P(*e['a']).y, 2)], 'b': [round(P(*e['b']).x, 2), round(P(*e['b']).y, 2)],
                           'length_in': round(e['len'], 2), 'openings': ops})
            fx = [{'kind': f['kind'], 'wall': f['side'], 'x': f['x'], 'w': f['w'], 'd': f.get('d', 22)} for f in fl.get('fixtures', []) if f['room'] == r['name']]
            pg = polys[r['name']]; b = pg.bounds
            mrooms.append({'name': r['name'], 'kind': r.get('kind', 'room'), 'ceiling_in': float(r.get('ceiling', ceil)),
                           'bounds_pt': [round(P(b[0], b[3]).x, 2), round(P(b[0], b[3]).y, 2), round(P(b[2], b[1]).x, 2), round(P(b[2], b[1]).y, 2)],
                           'poly_pt': [[round(P(*c).x, 2), round(P(*c).y, 2)] for c in pg.exterior.coords], 'walls': ws, 'fixtures': fx,
                           'labels': r['name'].split()})
        models.append({'floor': fl['n'], 'source': 'planspec', 'page': len(doc) - 1, 'offset': [0, 0], 'pt_per_ft': ppf, 'rooms': mrooms})
    return doc, models


def _on_edge(e, o):
    return o['at'] >= -0.01 and o['at'] + o['w'] <= e['len'] + 0.01


def _neighbour(polys, name, p0, p1, nx, ny, t_int):
    mid = ((p0[0] + p1[0]) / 2 + nx * (t_int / 2 + 0.5), (p0[1] + p1[1]) / 2 + ny * (t_int / 2 + 0.5))
    probe = box(mid[0] - 0.5, mid[1] - 0.5, mid[0] + 0.5, mid[1] + 0.5).buffer(t_int / 2 + 1)
    return any(n != name and pg.intersects(probe) for n, pg in polys.items())


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); pre = sys.argv[2]
    doc, models = build(spec)
    doc.save(pre + '.Base.pdf', garbage=3, deflate=True)
    for m in models: json.dump(m, open('%s.model_f%d.json' % (pre, m['floor']), 'w'), indent=1)
    print('saved', pre + '.Base.pdf', [len(m['rooms']) for m in models], 'rooms per floor')
