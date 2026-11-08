"""Build the room model JSON for each floor of Casa Grove from the YL Designs wall covering bases.
Usage: python3 build_model.py  -> model_f1.json, model_f2.json"""
import json, idd_model as M
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
W = '/mnt/user-data/uploads/f4877d18-Pages_from_Casa_Grove_ID_Set_-_Wall_Coverings.pdf'
EXTENT = (80, 110, 640, 1160)
FLOORS = {
 1: dict(pno=1, offset=(2.6, 22.7), cuts=[((297,441),(410,441)), ((298,670),(600,670)), ((400,889),(500,889))], ceiling=120.0,
         rooms={'KITCHEN & DINING AREA': [(250,300)], 'PANTRY': [(190,470)], 'GREAT ROOM': [(450,550)], 'PIANO ROOM': [(480,780)],
                'FOYER': [(460,940)], 'POWDER ROOM': [(580,930)], 'GUEST BEDROOM': [(190,580)], 'GUEST BATH': [(150,680)],
                'GUEST CLOSET': [(255,680)], 'LAUNDRY': [(350,700),(350,790),(350,850)],
                'SERVICE AREA': [(250,770)], 'PET AREA': [(150,770),(130,855)], 'OFFICE': [(560,1050)]},
         kinds={'GUEST BATH': 'bath', 'POWDER ROOM': 'bath', 'KITCHEN & DINING AREA': 'kitchen', 'LAUNDRY': 'utility', 'PANTRY': 'utility',
                'SERVICE AREA': 'utility', 'PET AREA': 'utility', 'GUEST CLOSET': 'closet'},
         ceilings={'GREAT ROOM': 250.0}),
 2: dict(pno=2, offset=(0, 0), cuts=[((520,909),(575,909))], ceiling=120.0,
         rooms={'BEDROOM 3': [(280,250)], 'BATH 3': [(150,200)], 'BATH 2': [(150,340)], 'BEDROOM 2': [(210,450)], 'DEN / PLAYROOM': [(210,610)],
                'W.I.C.': [(215,760)], 'MASTER BATHROOM': [(215,930),(150,985),(280,985)], 'MASTER SUITE': [(450,880)], 'HALL': [(330,600)],
                'LINEN CLOSET': [(450,755)], 'HIDDEN SAFE': [(545,880)]},
         kinds={'BATH 3': 'bath', 'BATH 2': 'bath', 'MASTER BATHROOM': 'bath', 'W.I.C.': 'closet', 'LINEN CLOSET': 'closet', 'HIDDEN SAFE': 'closet', 'HALL': 'hall'},
         ceilings={}, guard={'HALL': ['N3', 'E1', 'E2', 'S1', 'S2', 'S3', 'S4']}),      # the hall's long 'east wall' is the guard at the open-to-below void, not a wall
}
def build(floor):
    cfg = FLOORS[floor]
    plan = M.PlanPage(W, cfg['pno'], offset=cfg['offset'])
    polys = []
    for poly, labels in M.room_polygons(plan, EXTENT, cuts=cfg['cuts']): polys += M.split_necks(poly, k=30)
    model = {'floor': floor, 'source': W.split('/')[-1], 'page': cfg['pno'], 'offset': cfg['offset'], 'pt_per_ft': M.PT_PER_FT, 'rooms': []}
    claimed = set()
    for name, seeds in cfg['rooms'].items():
        parts = [p for p in polys if any(p.distance(Point(*s)) < 3.0 for s in seeds) and id(p) not in claimed]
        assert parts, ('no polygon for', name)
        claimed |= {id(p) for p in parts}          # a polygon part belongs to one room only
        poly = unary_union(parts).buffer(2.5).buffer(-2.5).simplify(0.8)
        if poly.geom_type == 'MultiPolygon':
            print('  note', name, 'parts not joined; keeping the largest', [round(g.area) for g in poly.geoms])
            poly = max(poly.geoms, key=lambda g: g.area)
        poly = Polygon(poly.exterior)
        room = M.Room(plan, name, poly=poly, kind=cfg['kinds'].get(name, 'room'), ceiling_in=cfg['ceilings'].get(name, cfg['ceiling']))
        d = room.to_dict()
        for w in d['walls']:
            if w['id'] in cfg.get('guard', {}).get(name, []): w['guard'] = True
        model['rooms'].append(d)
    return model
if __name__ == '__main__':
    for f in (1, 2):
        m = build(f); json.dump(m, open(f'model_f{f}.json', 'w'), indent=1)
        for r in m['rooms']:
            print(f, r['name'], [round(v) for v in r['bounds_pt']], [(w['id'], w['length_in'], len(w['openings'])) for w in r['walls']], [(f['kind'], f['size_in'], [(o['wall'], o['x']) for o in f['on']]) for f in r['fixtures']])
