"""Board-by-board wood floors for the renders (owner 11.11.26: "hard to visualize the herringbone pattern... make it more
detailed"). Run with system python (shapely); writes render/floors/<key>.json, which stages.board_floor() builds in Blender.

Every board is its own polygon, clipped to the room's field, with its own grain offset and tone (two random numbers), and
a 1/32 in. joint all round (the dark underlay shows through). The WD-02 border is one board wide along every wall, mitred
at the corners. Herringbone (ID-102: WD-01 herringbone in the master bedroom and bath, one grid on the bedroom's center
line): boards W x L at 45 degrees, spines running north-south, a spine on the given center line.

Frame: the room's render frame, inches (X east, Y north). Board size T.B.C. on ID-102: 3-1/2 x 21 in. here (VERIFY)."""
import json, math, os, random, sys
from shapely.geometry import Polygon, box as sbox
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
JOINT = 1.0 / 32.0


def herringbone(field, W=3.5, L=21.0, spine_x=0.0, seed=7):
    """Boards covering `field` (a shapely polygon). Built in a frame where the boards are axis-aligned and a spine runs along
    u = v, then turned 45 degrees so the spines run along Y, then moved so one spine sits on X = spine_x."""
    rnd = random.Random(seed)
    minx, miny, maxx, maxy = field.bounds
    span = max(maxx - minx, maxy - miny) * 1.6 + 4 * L
    n_k = int(span / W) + 4; n_s = int(span / L) + 4
    out = []
    for s in range(-n_s, n_s + 1):                       # strips: translation (L, -L) in the board frame
        for k in range(-n_k, n_k + 1):
            ox, oy = s * L, -s * L
            for kind, (u0, v0, u1, v1) in (('h', (k * W, k * W, k * W + L, k * W + W)),
                                           ('v', (k * W - W, k * W, k * W, k * W + L))):
                b = sbox(u0 + ox + JOINT, v0 + oy + JOINT, u1 + ox - JOINT, v1 + oy - JOINT)
                b = affinity.rotate(b, 45, origin=(0, 0))
                b = affinity.translate(b, spine_x, (minx + maxy) * 0 + (miny + maxy) / 2)
                if not b.intersects(field): continue
                c = b.intersection(field)
                if c.is_empty or c.area < 0.5: continue
                ang = 45.0 if kind == 'h' else 135.0      # the board's long axis, degrees from +X
                r1, r2 = rnd.random(), rnd.random()
                for g in getattr(c, 'geoms', [c]):
                    if g.geom_type != 'Polygon' or g.area < 0.5: continue
                    out.append({'pts': [[round(x, 3), round(y, 3)] for x, y in list(g.exterior.coords)[:-1]], 'ang': ang,
                                'r': [round(r1, 4), round(r2, 4)]})
    return out


def border(outline, width=6.0, seed=11):
    """One board along every edge of `outline` (counter-clockwise points), mitred at the corners, joints at the mitres."""
    rnd = random.Random(seed)
    P = Polygon(outline)
    if not P.exterior.is_ccw: outline = outline[::-1]
    inner = Polygon(outline).buffer(-width, join_style=2)
    ip = list(inner.exterior.coords)[:-1]
    # match each outer vertex to its inset vertex (the nearest along the bisector)
    def near(p):
        return min(ip, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
    out = []; n = len(outline)
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]; ia, ib = near(a), near(b)
        poly = Polygon([a, b, ib, ia]).buffer(-JOINT, join_style=2)
        if poly.is_empty: continue
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        out.append({'pts': [[round(x, 3), round(y, 3)] for x, y in list(poly.exterior.coords)[:-1]], 'ang': ang,
                    'r': [round(rnd.random(), 4), round(rnd.random(), 4)]})
    return out, inner


ROOMS = {
    # master bedroom (build_mbr_shell.py frame): the bedroom and the reading nook, one floor, a 6 in. border all round;
    # spine on the bedroom's center line X 91.69
    'mbr': {'outline': [(0, 0), (132.2, 0), (132.2, -49.9), (231.8, -49.9), (231.8, 44.0), (183.375, 44.0), (183.375, 161.4), (0, 161.4)],
            'border': 6.0, 'spine_x': 183.375 / 2},
}

def bath():
    """Master bath (build_bath_shell.py frame): WD-01 herringbone with a 6 in. WD-02 border round the main room (across the
    alcove openings as a threshold), the herringbone run on into the tub alcove and the W.C. (ID-102: W.C. herringbone, no
    border); the shower is TL-03 mosaic, not boards. Spine on X 81, the alcove's center line."""
    from shapely.ops import unary_union
    main = [(0, 0), (162, 0), (162, 79.125), (0, 79.125)]
    bd, field = border(main, 6.0)
    extra = unary_union([sbox(48.625, -63.0, 113.375, 0.0), sbox(118.375, -63.0, 162.0, -6.0), sbox(124.0, -6.0, 154.0, 0.0)])
    hb = herringbone(unary_union([field, extra]), spine_x=81.0, seed=9)
    return {'field': hb, 'border': bd, 'outline': main}


if __name__ == '__main__':
    if 'bath' in sys.argv[1:]:
        os.makedirs(os.path.join(HERE, 'floors'), exist_ok=True)
        json.dump(bath(), open(os.path.join(HERE, 'floors', 'bath.json'), 'w')); print('bath written'); sys.exit(0)
    os.makedirs(os.path.join(HERE, 'floors'), exist_ok=True)
    for key in (sys.argv[1:] or ROOMS):
        R = ROOMS[key]
        bd, field = border(R['outline'], R['border']) if R.get('border') else ([], Polygon(R['outline']))
        hb = herringbone(field, spine_x=R['spine_x'])
        json.dump({'field': hb, 'border': bd, 'outline': R['outline']}, open(os.path.join(HERE, 'floors', key + '.json'), 'w'))
        print(key, len(hb), 'boards', len(bd), 'border boards', round(sum(Polygon(b['pts']).area for b in hb) / field.area, 3), 'coverage')
