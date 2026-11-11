"""The house model registry (owner 11.11.26: "just add to some sort of database that will eventually be completed whenever I fully
render the house"). One plan grid for the whole house; every room on it with its outline and its status; every rendered room adds its
saved model (render/rooms/KEY.blend, written by PR_SAVEROOM=KEY with its own render command) and its renders. When every room is
rendered, the registry is the assembly list for the walk-through model.

Grid: inches, X east, Y north, origin at the living room's west wall face on the south gallery line (the living room render's own
origin, so it sits at offset 0, 0). FOR REV 1 sheet points convert as X = (x_pt - 626.2) / 1.5, Y = (844.5 - y_pt) / 1.5; A-201 and
A-202 share one frame (the stair lines up). Floor 1 finish floor 0; floor 2 at 12'-10" (154 in.).

Writes render/house_model.json (merging what is already there: statuses and renders are kept) and a grid sheet PDF."""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'rev1'))
OUT = os.path.join(HERE, 'house_model.json')
FF = {1: 0.0, 2: 154.0}
X = lambda x: (x - 626.2) / 1.5
Y = lambda y: (844.5 - y) / 1.5

# what exists today (11.11.26); later renders update the file through register()
DESIGNED = {(1, 'KITCHEN AND DINING'), (1, 'LIVING ROOM'), (1, 'POWDER ROOM'), (2, 'MASTER BATH'), (2, 'MASTER SHOWER'), (2, 'WATER CLOSET'),
            (2, 'MASTER BEDROOM'), (2, 'W.I.C.')}   # the shower and water closet are drawn with the master bath (ID-32x)
RENDERED = {
    (1, 'LIVING ROOM'): {'key': 'living', 'blend': None, 'stage': 'living',
                         'renders': ['261110.HD102.Living-Render-Fireplace-R2.jpg', '261110.HD102.Living-Render-WindowWall-R2.jpg',
                                     '261110.HD102.Living-Render-SouthEnd-OpenStair.jpg', '261110.HD102.Living-Render-SouthEnd-Piano.jpg'],
                         'note': 'includes the south end, the opened stair and the entry foyer seen through the arch'},
    (1, 'KITCHEN AND DINING'): {'key': 'kitchen', 'blend': 'render/rooms/kitchen.blend', 'stage': 'kitchen',
                                'renders': ['261109.HD102.Kitchen-Render.jpg']},
    (2, 'W.I.C.'): {'key': 'closet', 'blend': None, 'stage': 'closet', 'renders': ['261109.HD102.MasterCloset-Render.jpg']},
    (2, 'MASTER BATH'): {'key': 'mbath', 'blend': None, 'stage': None,
                         'renders': ['261108.HD102.MasterBathNorth-Render.jpg', '261108.HD102.MasterBath-Perspective-Pilot.jpg'],
                         'note': 'rendered before the 11.10 palette and render rules; re-render queued'},
}


def rooms():
    import rooms_rev1 as RR
    out = {}
    for f in (1, 2):
        for k, g in RR.rooms(f).items():
            p = g if g.geom_type == 'Polygon' else max(g.geoms, key=lambda q: q.area)
            x0, y0, x1, y1 = g.bounds
            out[(f, k)] = {'floor': f, 'name': k, 'ff_in': FF[f], 'bounds_in': [round(X(x0), 1), round(Y(y1), 1), round(X(x1), 1), round(Y(y0), 1)],
                           'area_sf': round(g.area / 1.5 ** 2 / 144.0, 1), 'outline_in': [[round(X(a), 1), round(Y(b), 1)] for a, b in p.exterior.coords]}
    return out


def build():
    old = json.load(open(OUT)) if os.path.exists(OUT) else {'rooms': {}}
    R = rooms(); rec = {}
    for (f, k), r in R.items():
        rid = 'F%d %s' % (f, k)
        prev = old['rooms'].get(rid, {})
        st = 'rendered' if (f, k) in RENDERED else 'designed' if (f, k) in DESIGNED else 'plan only'
        r['status'] = prev.get('status') if prev.get('status') == 'rendered' else st
        r.update({kk: vv for kk, vv in RENDERED.get((f, k), {}).items()})
        for kk in ('key', 'blend', 'stage', 'renders', 'note', 'cmds'):
            if kk in prev and kk not in r: r[kk] = prev[kk]
        rec[rid] = r
    doc = {'_doc': __doc__.split('\n\n')[0] + ' ' + __doc__.split('\n\n')[1],
           'grid': {'units': 'inches', 'x': 'east', 'y': 'north', 'origin': "living room west wall face on the south gallery line",
                    'from_FOR_pt': 'X = (x_pt - 626.2) / 1.5, Y = (844.5 - y_pt) / 1.5', 'floors_ff_in': {'1': 0.0, '2': 154.0}},
           'status_values': {'plan only': 'outline from FOR REV 1, no elevations yet: a painted shell in the walk-through',
                             'designed': 'elevations drawn, not rendered yet', 'rendered': 'rendered; its saved model joins the house model'},
           'updated': datetime.date.today().isoformat(), 'rooms': rec}
    json.dump(doc, open(OUT, 'w'), indent=1)
    return doc


def register(floor, name, key, blend=None, render=None, cmd=None):
    """Called after a final render: mark the room rendered, add its saved model and the render file."""
    d = json.load(open(OUT)); r = d['rooms']['F%d %s' % (floor, name)]
    r['status'] = 'rendered'; r['key'] = key
    if blend: r['blend'] = blend
    if render: r.setdefault('renders', []); render in r['renders'] or r['renders'].append(render)
    if cmd: r.setdefault('cmds', []); cmd in r['cmds'] or r['cmds'].append(cmd)
    d['updated'] = datetime.date.today().isoformat(); json.dump(d, open(OUT, 'w'), indent=1)


def sheet(doc, path):
    """Two pages, one per floor: the grid every 5 ft, each room outlined and shaded by status, a legend and the tally."""
    import pymupdf as fitz
    COL = {'rendered': (0.55, 0.75, 0.55), 'designed': (0.95, 0.82, 0.5), 'plan only': (0.9, 0.9, 0.9)}
    pdf = fitz.open()
    allx = [p[0] for r in doc['rooms'].values() for p in r['outline_in']]; ally = [p[1] for r in doc['rooms'].values() for p in r['outline_in']]
    gx0, gx1, gy0, gy1 = min(allx) - 30, max(allx) + 30, min(ally) - 30, max(ally) + 30
    W_, H_ = 1224, 792; s = min((W_ - 300) / (gx1 - gx0), (H_ - 120) / (gy1 - gy0)); ox, oy = 60, 70
    P = lambda x, y: fitz.Point(ox + (x - gx0) * s, oy + (gy1 - y) * s)
    for f in (1, 2):
        pg = pdf.new_page(width=W_, height=H_)
        pg.insert_text((60, 40), 'CASA GROVE (HD102): HOUSE MODEL REGISTRY, FLOOR %d (FF %s)' % (f, "0'-0\"" if f == 1 else "12'-10\""), fontsize=14, fontname='helv')
        pg.insert_text((60, 56), 'Grid in inches from the living room west wall face on the south gallery line; lines every 5\'-0". Updated %s.' % doc['updated'], fontsize=8, fontname='helv', color=(0.3, 0.3, 0.3))
        g = (gx0 // 60) * 60
        while g <= gx1:
            pg.draw_line(P(g, gy0), P(g, gy1), color=(0.85, 0.85, 0.85), width=0.4); pg.insert_text(P(g, gy0) + (2, 10), '%d' % g, fontsize=5.5, color=(0.5, 0.5, 0.5)); g += 60
        g = (gy0 // 60) * 60
        while g <= gy1:
            pg.draw_line(P(gx0, g), P(gx1, g), color=(0.85, 0.85, 0.85), width=0.4); pg.insert_text(P(gx0, g) + (-26, 2), '%d' % g, fontsize=5.5, color=(0.5, 0.5, 0.5)); g += 60
        pg.draw_circle(P(0, 0), 3, color=(0.8, 0.1, 0.1), fill=(0.8, 0.1, 0.1)); pg.insert_text(P(0, 0) + (5, 10), 'ORIGIN 0,0', fontsize=6, color=(0.8, 0.1, 0.1))
        tally = {}
        for rid, r in sorted(doc['rooms'].items()):
            if r['floor'] != f: continue
            tally[r['status']] = tally.get(r['status'], 0) + 1
            pg.draw_polyline([P(*p) for p in r['outline_in']], color=(0.2, 0.2, 0.2), fill=COL[r['status']], width=0.7, closePath=True)
            b = r['bounds_in']; c = P((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            fs = 6.5 if r['area_sf'] > 40 else 5
            tw = fitz.get_text_length(r['name'], fontsize=fs); pg.insert_text(c + (-tw / 2, 0), r['name'], fontsize=fs, fontname='helv')
            t2 = '%s SF, %s' % (r['area_sf'], r['status'].upper()); tw = fitz.get_text_length(t2, fontsize=4.5)
            pg.insert_text(c + (-tw / 2, 7), t2, fontsize=4.5, color=(0.3, 0.3, 0.3))
        lx, ly = W_ - 220, 90
        pg.insert_text((lx, ly), 'STATUS', fontsize=9, fontname='helv'); ly += 14
        for k_ in ('rendered', 'designed', 'plan only'):
            pg.draw_rect(fitz.Rect(lx, ly - 8, lx + 14, ly + 2), color=(0.2, 0.2, 0.2), fill=COL[k_], width=0.5)
            pg.insert_text((lx + 20, ly), '%s (%d)' % (k_.upper(), tally.get(k_, 0)), fontsize=8); ly += 15
        ly += 10
        for ln in ('Each finished render saves its room', 'model and is registered here; the', 'walk-through is assembled from the', 'rendered rooms, the rest as shells.'):
            pg.insert_text((lx, ly), ln, fontsize=7, color=(0.3, 0.3, 0.3)); ly += 10
        ly += 8
        for rid, r in sorted(doc['rooms'].items()):
            if r['floor'] == f and r.get('renders'):
                pg.insert_text((lx, ly), r['name'], fontsize=7, fontname='helv'); ly += 9
                for fn in r['renders']: pg.insert_text((lx + 6, ly), fn, fontsize=5.5, color=(0.3, 0.3, 0.3)); ly += 8
                ly += 3
    pdf.set_metadata({'title': 'Casa Grove house model registry', 'author': 'Helios Development'}); pdf.save(path)


if __name__ == '__main__':
    d = build()
    sheet(d, sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'house_model.pdf'))
    n = {}
    for r in d['rooms'].values(): n[r['status']] = n.get(r['status'], 0) + 1
    print(len(d['rooms']), 'rooms', n)
