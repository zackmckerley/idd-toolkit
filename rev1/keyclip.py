"""Clip a key plan's base to the rooms it is about plus their walls, so nothing outside reads as a cut fragment."""
import sys; sys.path.insert(0, '/home/claude/flrwork/rev1')
from shapely.ops import unary_union
from shapely.geometry import Polygon
import rooms_rev1 as RR, base_rev1 as BR, replay as RP
from shapely.geometry import box

_cache = {}
def room_poly(floor, names, pad=12.0, doors=True):
    """Display-space polygon: the named REV 1 rooms, grown by pad (display pt, about the exterior wall) with square corners."""
    if floor not in _cache: _cache[floor] = RR.rooms(floor)
    T = BR.transform(floor)
    gs = []
    for n in names:
        g = _cache[floor][n]
        for p in (g.geoms if hasattr(g, 'geoms') else [g]):
            gs.append(Polygon([T(x, y) for x, y in p.exterior.coords]))
    return area_poly(floor, gs, pad, doors)


def for_rect(floor, x0, y0, x1, y1):
    """A rectangle given in FOR sheet points, as a display-space polygon (for designed areas that are part of a room:
    the double-height living room inside the open plan)."""
    T = BR.transform(floor)
    return Polygon([T(x0, y0), T(x1, y0), T(x1, y1), T(x0, y1)])


def area_poly(floor, display_polys, pad=12.0, doors=True):
    """The designed area of a key plan: the union of the given display-space polygons grown by pad (square corners), plus
    every door in its walls shown whole. RULE (owner 11.07.26): a key plan shows only the area its section designs; doors
    and openings into the adjacent rooms are shown, nothing of those rooms beyond them."""
    T = BR.transform(floor)
    u = unary_union(display_polys).buffer(pad, join_style=2, mitre_limit=10)
    if doors:      # every door in the room's walls is shown whole, swing and all, even where it swings out of the room
        add = []
        for dr in RP.drawings(floor):
            n = RP.lname(dr)
            if not n.endswith('A-DOOR') or not RP.inplan(dr): continue
            r = dr['rect']; a_, b_ = T(r.x0, r.y0), T(r.x1, r.y1)
            bx = box(min(a_[0], b_[0]) - 1, min(a_[1], b_[1]) - 1, max(a_[0], b_[0]) + 1, max(a_[1], b_[1]) + 1)
            if bx.intersects(u): add.append(bx)
        if add:
            grp = unary_union(add)                      # a door is its leaf, swing and frame drawings together
            for g in (grp.geoms if hasattr(grp, 'geoms') else [grp]):
                if g.intersects(u): u = unary_union([u, g.envelope])
    u = u.buffer(-2, join_style=2).buffer(2, join_style=2)
    return max(u.geoms, key=lambda q: q.area) if hasattr(u, 'geoms') else u

def apply(page, target, clip_disp, k, poly):
    """Add the polygon as a clip in front of the placed base (the last form XObject drawn into target)."""
    H = page.rect.height
    pts = [(target.x0 + (x - clip_disp.x0) * k, target.y0 + (y - clip_disp.y0) * k) for x, y in poly.exterior.coords]
    path = ' '.join(f'{x:.2f} {H - y:.2f} {"m" if i == 0 else "l"}' for i, (x, y) in enumerate(pts)) + ' h W n '
    for xref in reversed(page.get_contents()):
        st = page.parent.xref_stream(xref).decode('latin1')
        i = st.rfind(' Do')
        if i < 0: continue
        q = max(st.rfind('q\n', 0, i), st.rfind('q ', 0, i))
        if q < 0: continue
        j = q + 2; st = st[:j] + path + '\n' + st[j:]
        page.parent.update_stream(xref, st.encode('latin1')); return True
    return False
