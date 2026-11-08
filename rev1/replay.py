"""Replay FOR's vector paths by layer into a new page (for layer filtering and restyling)."""
import pymupdf as fitz
SRC = {1: '/mnt/user-data/uploads/95f5b900-A-201_Proposed_First_Floor_Plan_REV_1.pdf',
       2: '/mnt/user-data/uploads/ff33b53b-A-202_Proposed_Second_Floor_Plan_REV_1.pdf'}
PLAN = fitz.Rect(40, 40, 1340, 1700)     # the plan viewport on FOR's 36 x 24 sheet (pt); key plan and notes lie outside

_cache = {}
def drawings(floor):
    if floor not in _cache:
        d = fitz.open(SRC[floor]); _cache[floor] = d[0].get_drawings()
    return _cache[floor]

def lname(dr): return (dr.get('layer') or '')

def replay(shape, dr, T=lambda p: p, color=None, width=None, fill=None, dashes=None):
    for it in dr['items']:
        k = it[0]
        if k == 'l': shape.draw_line(T(it[1]), T(it[2]))
        elif k == 'c': shape.draw_bezier(T(it[1]), T(it[2]), T(it[3]), T(it[4]))
        elif k == 're':
            r = it[1]; q = [T(r.tl), T(r.tr), T(r.br), T(r.bl)]; shape.draw_polyline(q + [q[0]])
        elif k == 'qu':
            q = it[1]; pts = [T(q.ul), T(q.ur), T(q.lr), T(q.ll)]; shape.draw_polyline(pts + [pts[0]])
    c = dr.get('color') if color is None else color
    w = dr.get('width') or 0.5 if width is None else width
    shape.finish(color=c, fill=fill if fill is not None else None, width=w, closePath=False, dashes=dashes if dashes is not None else dr.get('dashes'))

def inplan(dr, R=PLAN):
    r = dr['rect']
    return r.x0 < R.x1 and r.x1 > R.x0 and r.y0 < R.y1 and r.y1 > R.y0
