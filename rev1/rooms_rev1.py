"""Room polygons from FOR REV 1: free space between the wall mask, windows and door heads, split at the open-plan cut lines, named from seed
points. FOR sheet coordinates (pt)."""
import numpy as np, cv2, json
import replay as R, walls as Wm
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

Z = Wm.Z
CUTS = {1: [(652, 548, 738, 548),        # kitchen to hall opening, on the wall line
            (770, 205, 770, 545),        # kitchen east glass (sliders are doors in FOR's layers)
            (806, 548, 1004, 548),       # living room north slider
            (665, 952, 715, 952),        # laundry door (no head line)
            (978, 928, 978, 980),        # under-stair closet door 27
            (980, 976.5, 1046, 976.5)],  # under-stair closet / the visible upper flight
        2: [(695, 640, 695, 830)]}       # den / playroom, open to the hall: on the line of the bedroom 2 and W.I.C. east walls            # (x0, y0, x1, y1) segments, FOR pt
SEEDS = {1: {'KITCHEN AND DINING': (560, 300), 'PANTRY': (493, 600), 'GUEST BEDROOM': (487, 700), 'GUEST BATHROOM': (400, 860),
             'W.I.C.': (570, 850), 'LIVING ROOM': (905, 700), 'STAIR CLOSET': (1012, 940), 'LAUNDRY AND BACK HALL': (650, 990), 'LAUNDRY': (660, 880),
             'UTILITY ROOM': (418, 980), 'STORAGE': (400, 1095), 'AHU': (607, 1089), 'CLOSET': (671, 1090), 'ENTRY': (820, 1200),
             'POWDER ROOM': (1000, 1190), 'OFFICE': (970, 1350)},
         2: {'BATH 3': (495, 220), 'BATH 2': (495, 380), 'BEDROOM 3': (700, 250), 'BEDROOM 2': (560, 520), 'DEN / PLAYROOM': (600, 720),
             'DEN CLOSET': (485, 660), 'AHU': (482, 800), 'HALL': (730, 600), 'W.I.C.': (568, 950), 'MASTER BATH': (560, 1150),
             'MASTER SHOWER': (480, 1250), 'WATER CLOSET': (655, 1250), 'MASTER BEDROOM': (840, 1050), 'LINEN CLOSET': (860, 940),
             'SAFE CLOSET': (1012, 1110)}}
STAIRS = {1: {'treads': [(878, 1073, 983, 1137), (983, 977, 1046, 1072)], 'landing': [(983, 1072, 1046, 1137)]},
          2: {'treads': [(930, 840, 983, 912), (983, 912, 1046, 1075)], 'landing': [(983, 840, 1046, 912)]}}

def barrier(floor):
    w = Wm.line_mask(floor, lambda n: Wm.is_wall(n))
    k = int(16 * 1.5 * Z) | 1
    cx = cv2.morphologyEx(w, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, k)))
    cy = cv2.morphologyEx(w, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)))
    walls = cx | cy
    extra = Wm.line_mask(floor, lambda n: n.endswith('A-WINDOW') or n.endswith('A-WALL-HEAD'), lw=1.2)
    # FOR draws heads as real dashes: close the gaps along each line direction (up to 8 pt)
    g = int(8 * Z) | 1
    extra = cv2.morphologyEx(extra, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (g, 1))) | \
            cv2.morphologyEx(extra, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, g)))
    b = walls | cv2.dilate(extra, np.ones((3, 3), np.uint8))
    for x0, y0, x1, y1 in CUTS[floor]:
        cv2.line(b, (int((x0 - R.PLAN.x0) * Z), int((y0 - R.PLAN.y0) * Z)), (int((x1 - R.PLAN.x0) * Z), int((y1 - R.PLAN.y0) * Z)), 1, 3)
    return walls, b

def components(floor):
    walls, b = barrier(floor)
    n, lab = cv2.connectedComponents((1 - b).astype(np.uint8), connectivity=4)
    return walls, b, n, lab

def rooms(floor, min_in2=400):
    walls, b, n, lab = components(floor)
    out = {}
    for name, (x, y) in SEEDS[floor].items():
        v = lab[int((y - R.PLAN.y0) * Z), int((x - R.PLAN.x0) * Z)]
        if v == 0: raise ValueError(('seed on a barrier', floor, name))
        m = (lab == v).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))          # swallow the barrier lines inside a room
        cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        polys = []
        for i, c in enumerate(cs):
            if hier[0][i][3] >= 0 or cv2.contourArea(c) < 50: continue
            ext = [(float(px) / Z + R.PLAN.x0, float(py) / Z + R.PLAN.y0) for px, py in cv2.approxPolyDP(c, 1.0, True).reshape(-1, 2)]
            holes = []; ch = hier[0][i][2]
            while ch >= 0:
                if cv2.contourArea(cs[ch]) > 600:
                    holes.append([(float(px) / Z + R.PLAN.x0, float(py) / Z + R.PLAN.y0) for px, py in cv2.approxPolyDP(cs[ch], 1.0, True).reshape(-1, 2)])
                ch = hier[0][ch][0]
            if len(ext) >= 3: polys.append(Polygon(ext, holes).buffer(0))
        g = unary_union(polys)
        out.setdefault(name, []).append(g)
    return {k: unary_union(v) for k, v in out.items()}

def preview(floor, path):
    walls, b, n, lab = components(floor)
    rng = np.random.default_rng(3); col = rng.integers(60, 255, (n, 3)).astype(np.uint8); col[0] = 0
    img = col[lab]; img[b > 0] = 0
    sizes = np.bincount(lab.ravel())
    for v in range(1, n):
        if sizes[v] < 2000: continue
        ys, xs = np.nonzero(lab == v)
        cv2.putText(img, str(v), (int(xs.mean()), int(ys.mean())), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 4)
    cv2.imwrite(path, cv2.resize(img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_NEAREST))
    return n, lab

def _poly_from_mask(m):
    cs, hier = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < 20: continue
        pts = [(float(px) / Z + R.PLAN.x0, float(py) / Z + R.PLAN.y0) for px, py in cv2.approxPolyDP(c, 1.0, True).reshape(-1, 2)]
        if len(pts) >= 3: out.append(Polygon(pts).buffer(0))
    return unary_union(out) if out else Polygon()

def thresholds(floor, max_sf=25.0, reach=14):
    """Door and cased-opening thresholds: the strips between two door heads that belong to no room. Each strip is split between the
    rooms it joins at its centerline (transition centered under the door), returned as {room: geometry} in FOR pt."""
    walls, b, n, lab = components(floor)
    seeded = {}
    for name, (x, y) in SEEDS[floor].items():
        seeded[int(lab[int((y - R.PLAN.y0) * Z), int((x - R.PLAN.x0) * Z)])] = name
    sizes = np.bincount(lab.ravel()); lim = max_sf * 324 * Z * Z
    out = {}
    ker = np.ones((2 * reach + 1, 2 * reach + 1), np.uint8)
    cutm = np.zeros_like(b)
    for x0_, y0_, x1_, y1_ in CUTS[floor]:
        cv2.line(cutm, (int((x0_ - R.PLAN.x0) * Z), int((y0_ - R.PLAN.y0) * Z)), (int((x1_ - R.PLAN.x0) * Z), int((y1_ - R.PLAN.y0) * Z)), 1, 3)
    for v in range(1, n):
        if v in seeded or sizes[v] > lim or sizes[v] < 30 * Z * Z: continue
        m = (lab == v).astype(np.uint8)
        ys, xs = np.nonzero(m); y0, y1, x0, x1 = max(ys.min() - 3 * reach, 0), ys.max() + 3 * reach, max(xs.min() - 3 * reach, 0), xs.max() + 3 * reach
        sub = lab[y0:y1, x0:x1]; ms = m[y0:y1, x0:x1]
        ring = cv2.dilate(ms, ker) & (1 - ms)
        near = [int(u) for u in np.unique(sub[ring > 0]) if int(u) in seeded]
        if len(near) == 1 and (cv2.dilate(ms, np.ones((7, 7), np.uint8)) & cutm[y0:y1, x0:x1]).any():
            out.setdefault(seeded[near[0]], []).append(_poly_from_mask(cv2.dilate(m, np.ones((3, 3), np.uint8)))); continue   # half an opening, split by a cut
        if len(near) < 2: continue
        dist = np.stack([cv2.distanceTransform((sub != u).astype(np.uint8), cv2.DIST_L2, 3) for u in near])
        own = np.argmin(dist, axis=0)
        for i, u in enumerate(near):
            part = np.zeros_like(m); part[y0:y1, x0:x1] = ms & (own == i)
            if part.sum() < 4: continue
            g = _poly_from_mask(cv2.dilate(part, np.ones((3, 3), np.uint8)))
            out.setdefault(seeded[u], []).append(g)
    # door heads drawn close together leave the whole opening as barrier: the head pixels (barrier, not wall) joining two rooms
    hm = (b > 0) & (walls == 0)
    nh, hl = cv2.connectedComponents(hm.astype(np.uint8), connectivity=8)
    hs = np.bincount(hl.ravel())
    for v in range(1, nh):
        if hs[v] < 4 * Z * Z or hs[v] > lim: continue
        m = (hl == v).astype(np.uint8)
        ys, xs = np.nonzero(m); y0, y1, x0, x1 = max(ys.min() - 3 * reach, 0), ys.max() + 3 * reach, max(xs.min() - 3 * reach, 0), xs.max() + 3 * reach
        sub = lab[y0:y1, x0:x1]; ms = m[y0:y1, x0:x1]
        ring = cv2.dilate(ms, np.ones((7, 7), np.uint8)) & (1 - ms)
        near = [int(u) for u in np.unique(sub[ring > 0]) if int(u) in seeded]
        if len(near) < 2: continue
        dist = np.stack([cv2.distanceTransform((sub != u).astype(np.uint8), cv2.DIST_L2, 3) for u in near])
        own = np.argmin(dist, axis=0)
        for i, u in enumerate(near):
            part = np.zeros_like(m); part[y0:y1, x0:x1] = ms & (own == i)
            if part.sum() < 4: continue
            out.setdefault(seeded[u], []).append(_poly_from_mask(cv2.dilate(part, np.ones((3, 3), np.uint8))))
    return {k: unary_union(v) for k, v in out.items()}
