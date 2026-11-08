"""Ingest paths other than the AutoCAD PDF plot: DXF/DWG (via ezdxf; DWG converted to DXF first with ODA File Converter or
LibreCAD) and raster images (scanned or photographed plans). Both produce a PlanPage-compatible object so idd_model.room_polygons,
Room and the generators run unchanged. Scale: DXF drawing units are inches unless told otherwise; images need two known points.

Usage:
    plan = from_dxf('plan.dxf', units='in', wall_layers=('A-WALL',), door_layers=('A-DOOR',), window_layers=('A-GLAZ',))
    plan = from_image('plan.png', scale_pt_per_px=..., or calibrate=((x1,y1),(x2,y2), inches))
    rooms = idd_model.room_polygons(plan, plan.extent)
Coordinates are converted to the set's plan points (13.5 pt per foot, y down) so every downstream tool is shared."""
import math, collections
from shapely.geometry import Polygon, LineString, box, Point
from shapely.ops import unary_union
PT_PER_FT = 13.5; PT_PER_IN = PT_PER_FT / 12.0

class IngestedPlan:
    """Duck-typed PlanPage: items[layer] records with 'rect', 'type', 'fill', 'segs'; walls (polygon union); boundary; text list."""
    def __init__(self):
        self.items = collections.defaultdict(list); self.text = []; self.dx = self.dy = 0.0
        self.walls = Polygon(); self.wall_lines = Polygon(); self.closers = []; self.boundary = Polygon(); self.extent = (0, 0, 0, 0)
    def layer(self, suffix):
        return [rec for lyr, recs in self.items.items() if lyr.upper().endswith(suffix.upper()) for rec in recs]
    def finish(self, wall_layers, door_layers, window_layers, wall_width_pt=0.9):
        lines = []
        for lyr, recs in self.items.items():
            if any(lyr.upper().endswith(w.upper()) for w in wall_layers):
                for rec in recs:
                    for a, b in rec['segs']:
                        if a != b: lines.append(LineString([a, b]).buffer(wall_width_pt))
                    if rec.get('poly') is not None: lines.append(rec['poly'])
        self.wall_lines = unary_union(lines) if lines else Polygon()
        self.walls = self.wall_lines
        closers = []
        for lyr, recs in self.items.items():
            if any(lyr.upper().endswith(w.upper()) for w in window_layers):
                closers += [box(*r['rect']).buffer(0.6) for r in recs]
            if any(lyr.upper().endswith(d.upper()) for d in door_layers):
                for r in recs:
                    x0, y0, x1, y1 = r['rect']; w, h = x1 - x0, y1 - y0
                    closers.append(box(x0, y0, x1, y1).buffer(1.0))
        self.closers = closers
        self.boundary = unary_union([self.walls] + closers)
        xs = [v for recs in self.items.values() for r in recs for v in (r['rect'][0], r['rect'][2])]
        ys = [v for recs in self.items.values() for r in recs for v in (r['rect'][1], r['rect'][3])]
        self.extent = (min(xs) - 5, min(ys) - 5, max(xs) + 5, max(ys) + 5) if xs else (0, 0, 0, 0)
        # door-layer rects double as A-DOOR records and A-WALL-HEAD closers for the opening detector
        for lyr in list(self.items):
            if any(lyr.upper().endswith(d.upper()) for d in door_layers) and not lyr.upper().endswith('A-DOOR'):
                self.items['A-DOOR'] += self.items[lyr]
            if any(lyr.upper().endswith(w.upper()) for w in window_layers) and not lyr.upper().endswith('A-WINDOW'):
                self.items['A-WINDOW'] += self.items[lyr]
        return self

def _rec(segs, extra=None):
    xs = [p[0] for s in segs for p in s]; ys = [p[1] for s in segs for p in s]
    rec = {'rect': (min(xs), min(ys), max(xs), max(ys)), 'type': 's', 'fill': None, 'segs': segs, 'raw': None}
    if extra: rec.update(extra)
    return rec

# ---------------------------------------------------------------- DXF
def from_dxf(path, units='in', wall_layers=('A-WALL', 'WALL', 'WALLS', 'A-WALL-PART', 'A-WALL-DRYWALL'), door_layers=('A-DOOR', 'DOOR', 'DOORS'), window_layers=('A-GLAZ', 'A-WINDOW', 'WINDOW', 'WINDOWS'), text_layers=None, flip_y=True):
    """Model-space lines, polylines, arcs (as chords), inserts (exploded one level), text and mtext -> IngestedPlan in plan points."""
    import ezdxf
    from ezdxf.math import Vec3
    doc = ezdxf.readfile(path); msp = doc.modelspace()
    k = {'in': PT_PER_IN, 'ft': PT_PER_FT, 'mm': PT_PER_IN / 25.4, 'm': PT_PER_FT / 0.3048}[units]
    plan = IngestedPlan()
    ys_all = []
    def P(v): return (v[0] * k, -v[1] * k if flip_y else v[1] * k)
    def add(entity, layer):
        t = entity.dxftype()
        if t == 'LINE':
            plan.items[layer].append(_rec([(P(entity.dxf.start), P(entity.dxf.end))]))
        elif t in ('LWPOLYLINE', 'POLYLINE'):
            pts = [P(p) for p in (entity.get_points('xy') if t == 'LWPOLYLINE' else [v.dxf.location for v in entity.vertices])]
            if len(pts) >= 2:
                segs = list(zip(pts, pts[1:])) + ([(pts[-1], pts[0])] if entity.closed and len(pts) > 2 else [])
                extra = {'poly': Polygon(pts)} if entity.closed and len(pts) > 2 and Polygon(pts).is_valid else None
                plan.items[layer].append(_rec(segs, extra))
        elif t in ('ARC', 'CIRCLE'):
            c = entity.dxf.center; r = entity.dxf.radius
            a0, a1 = (entity.dxf.start_angle, entity.dxf.end_angle) if t == 'ARC' else (0, 360)
            if a1 < a0: a1 += 360
            n = max(4, int((a1 - a0) / 15)); pts = [P((c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))) for i in range(n + 1)]
            plan.items[layer].append(_rec(list(zip(pts, pts[1:]))))
        elif t in ('TEXT', 'MTEXT'):
            s = entity.dxf.text if t == 'TEXT' else entity.text
            ins = entity.dxf.insert; h = (entity.dxf.height if t == 'TEXT' else entity.dxf.char_height) * k
            x, y = P(ins); w = len(s) * h * 0.6
            plan.text.append((s.strip(), (x, y - h, x + w, y), h))
        elif t == 'INSERT':
            try:
                for e in entity.virtual_entities(): add(e, e.dxf.layer if e.dxf.layer != '0' else layer)
            except Exception: pass
    for e in msp: add(e, e.dxf.layer)
    return plan.finish(wall_layers, door_layers, window_layers)

# ---------------------------------------------------------------- raster image
def from_image(path, scale_pt_per_px=None, calibrate=None, dark=120, wall_min_px=4, ocr=True):
    """Scanned / photographed plan -> walls as polygons from the dark linework (morphological close), text via tesseract.
    calibrate = ((x1, y1), (x2, y2), inches): two pixel points a known distance apart sets the scale."""
    import cv2, numpy as np
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE); assert img is not None, path
    if calibrate:
        (x1, y1), (x2, y2), inches = calibrate; scale_pt_per_px = inches * PT_PER_IN / math.hypot(x2 - x1, y2 - y1)
    assert scale_pt_per_px, 'give scale_pt_per_px or calibrate'
    ink = (img < dark).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    walls = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, k, iterations=1)
    # keep thick strokes only (walls), drop thin lines (dimensions, furniture): open with a wall_min_px kernel
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (wall_min_px, wall_min_px))
    thick = cv2.morphologyEx(walls, cv2.MORPH_OPEN, k2)
    contours, hier = cv2.findContours(thick, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    plan = IngestedPlan(); polys = []
    hier = hier[0] if hier is not None else []
    def ring(c): return [(float(p[0][0]) * scale_pt_per_px, float(p[0][1]) * scale_pt_per_px) for p in c]
    for i, c in enumerate(contours):
        if len(c) < 3 or hier[i][3] != -1: continue             # outer contours only; children become holes (room interiors)
        holes = []; j = hier[i][2]
        while j != -1:
            if len(contours[j]) >= 3: holes.append(ring(contours[j]))
            j = hier[j][0]
        pts = ring(c); pg = Polygon(pts, holes).buffer(0)
        if pg.is_empty or pg.area < 4: continue
        polys.append(pg)
        segs = list(zip(pts, pts[1:] + pts[:1]))
        plan.items['A-WALL-RASTER'].append(_rec(segs, {'poly': pg, 'fill': (0.3, 0.3, 0.3)}))
    plan.walls = unary_union(polys) if polys else Polygon(); plan.wall_lines = plan.walls
    plan.boundary = plan.walls; plan.closers = []
    h, w = img.shape; plan.extent = (0, 0, w * scale_pt_per_px, h * scale_pt_per_px)
    if ocr:
        try:
            import pytesseract
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 11')
            for i, t in enumerate(data['text']):
                t = t.strip()
                if len(t) < 2 or int(float(data['conf'][i])) < 50: continue
                x, y, ww, hh = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                plan.text.append((t, (x * scale_pt_per_px, y * scale_pt_per_px, (x + ww) * scale_pt_per_px, (y + hh) * scale_pt_per_px), hh * scale_pt_per_px))
        except Exception as e:
            print('ocr skipped', e)
    return plan

# ---------------------------------------------------------------- round trip test helpers
def model_to_dxf(model_json, out_path):
    """Write a floor's room polygons (as closed A-WALL polylines offset outward) plus door/window rects and labels to a DXF, in inches."""
    import ezdxf, json
    m = json.load(open(model_json)); doc = ezdxf.new('R2010'); msp = doc.modelspace()
    for lyr in ('A-WALL', 'A-DOOR', 'A-GLAZ', 'A-ANNO-TEXT'): doc.layers.add(lyr)
    for r in m['rooms']:
        pts = [(x / PT_PER_IN, -y / PT_PER_IN) for x, y in r['poly_pt']]
        for a, b in zip(pts, pts[1:] + pts[:1]): msp.add_line(a, b, dxfattribs={'layer': 'A-WALL'})    # wall faces as lines (a wall layer holds faces, not room fills)
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        msp.add_text(r['name'], dxfattribs={'layer': 'A-ANNO-TEXT', 'height': 9 / PT_PER_IN}).set_placement((cx, cy))
        for w in r['walls']:
            for o in w['openings']:
                (ax, ay), (bx, by) = w['a'], w['b']; L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
                x0 = ax + ux * o['x'] * PT_PER_IN; y0 = ay + uy * o['x'] * PT_PER_IN; x1 = ax + ux * (o['x'] + o['w']) * PT_PER_IN; y1 = ay + uy * (o['x'] + o['w']) * PT_PER_IN
                lyr = 'A-GLAZ' if o['type'] == 'window' else 'A-DOOR'
                nx, ny = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[w['side']]
                rect = [(x0, y0), (x1, y1), (x1 + nx * 3, y1 + ny * 3), (x0 + nx * 3, y0 + ny * 3)]
                msp.add_lwpolyline([(x / PT_PER_IN, -y / PT_PER_IN) for x, y in rect], close=True, dxfattribs={'layer': lyr})
    doc.saveas(out_path); return out_path

if __name__ == '__main__':
    import json, idd_model as M
    # DXF round trip: model -> DXF -> ingest -> rooms
    p = model_to_dxf('model_f2.json', 'test_f2.dxf')
    plan = from_dxf(p)
    rooms = M.room_polygons(plan, plan.extent)
    print('dxf rooms', len(rooms), [(labels[:2], round(poly.area / PT_PER_FT ** 2)) for poly, labels in sorted(rooms, key=lambda t: -t[0].area)[:6]])
    # image path: render the clean base of floor 2 to PNG and ingest it
    import pymupdf as fitz
    pg = fitz.open('261101.3350THOMAS.Base-clean.pdf')[1]
    pix = pg.get_pixmap(dpi=144, clip=fitz.Rect(80, 110, 640, 1100)); pix.save('test_f2.png')
    plan2 = from_image('test_f2.png', scale_pt_per_px=72 / 144, wall_min_px=5)
    rooms2 = []
    for poly, labels in M.room_polygons(plan2, plan2.extent, min_area=400): rooms2 += M.label_rooms(plan2, M.split_necks(poly, k=40))   # no door symbols on a raster: split at door and window necks
    print('image rooms', len(rooms2), [(labels[:2], round(poly.area / PT_PER_FT ** 2)) for poly, labels in sorted(rooms2, key=lambda t: -t[0].area)[:8]])
