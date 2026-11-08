"""Interior elevation sheets (ID-7xx) for Casa Grove from the room models (model_f1.json, model_f2.json).
Every elevation is generated from the model: wall length and openings from the base plan, fixtures from the plan symbols,
finishes from the wall finish plans, heights from idd_std.HEIGHTS (flagged VERIFY where the architectural set governs).
Output: 261101.HD102.InteriorElevations.pdf plus elev_index.json (room, wall, view number, sheet) for the plan markers."""
import json, pymupdf as fitz
import idd_elevations as E
from idd_sheet import Sheet, FR, TB_X, HDR_Y, fix_soft_hyphen
from idd_std import HEIGHTS, TXT, INK, MID, LIGHT, sheet_no, trim_for
import build_model as B

OUT = '/home/claude/flrwork/261101.HD102.InteriorElevations.pdf'
VIEW = {'N': 'NORTH', 'E': 'EAST', 'S': 'SOUTH', 'W': 'WEST'}
SKIP_ROOMS = {'HIDDEN SAFE', 'LINEN CLOSET', 'GUEST CLOSET', 'HALL', 'LAUNDRY', 'SERVICE AREA', 'PET AREA'}
SKIP_REASON = {'HALL': 'PAINTED WALLS PT-02 / CM-01 THROUGHOUT, STAIR AND GUARD PER ARCHITECTURAL SET',
               'LAUNDRY': 'PAINTED WALLS PT-02 / CM-01, CABINETS PER MILLWORK SHOP DRAWINGS', 'SERVICE AREA': 'PAINTED WALLS PT-02 / CM-01',
               'PET AREA': 'PAINTED WALLS PT-02 / CM-01', 'GUEST CLOSET': 'CLOSET, PT-02, NO CROWN', 'LINEN CLOSET': 'CLOSET, PT-02, NO CROWN',
               'HIDDEN SAFE': 'JIB DOOR AND WALL PER WALL FINISH PLAN, NO CROWN'}
MIN_WALL_IN = 36.0

# ---------------------------------------------------------------- finish rules (must agree with the wall finish plans WF-1 / WF-2)
DEFAULT_PAINT = {1: 'PT-02', 2: 'PT-02'}
ROOM_PAINT = {'POWDER ROOM': 'PT-03', 'FOYER': 'PT-01'}
NO_CROWN = {'closet', 'utility_closet'}
SILL = {'bath': 48.0, 'kitchen': 42.0, 'utility': 42.0, 'room': 24.0, 'hall': 24.0, 'closet': 24.0}
TILE_BY_FLOOR = {1: 'WT-01', 2: 'WT-01'}          # tub alcoves in guest bath, baths 2 and 3
MASTER_TILE = 'WT-02'

def view_title(room, side): return f"{VIEW[side]} ELEVATION - {room}"

def wall_spec(floor, room, w, fixtures):
    """Build the ElevationView wall dict for one wall of one room."""
    name, kind = room['name'], room['kind']
    L, H = w['length_in'], room['ceiling_in']
    paint = ROOM_PAINT.get(name, DEFAULT_PAINT[floor])
    T = trim_for(H); CS = T['casing']                   # trim block sized from this room's ceiling (skill: Trim and paneling proportions)
    crown = None if (kind in NO_CROWN and name != 'W.I.C.') else T['crown']     # the W.I.C. is a dressing room with crown per ID-202
    spec = {'room': name, 'view': VIEW[w['side']], 'length': L, 'ceiling': H, 'base': T['base'], 'crown': crown, 'chair_rail': None,
            'openings': [], 'items': [], 'finishes': [], 'notes': [], 'breaks': ('wall', 'wall')}
    # openings
    for o in w['openings']:
        x, ow, t = o['x'], o['w'], o['type']
        if t == 'window':
            spec['openings'].append({'type': 'window', 'x': x, 'w': ow, 'head': HEIGHTS['window_head'], 'sill': SILL.get(kind, 24.0), 'casing': CS, 'lites': max(1, int(round(ow / 30.0)))})
        elif t == 'slider' and name == 'MASTER SUITE' and w['id'] == 'N3':
            spec['openings'].append({'type': 'jib', 'x': x, 'w': ow, 'head': HEIGHTS['door_head'], 'sill': 0, 'casing': 0})
            spec['notes'].append('JIB DOOR TO HIDDEN SAFE: FLUSH, NO CASING, FINISHED PT-02 TO MATCH THE WALL, CONCEALED HINGES')
        elif t in ('door', 'slider'):
            if ow > 44: spec['openings'].append({'type': 'door', 'x': x, 'w': ow, 'head': HEIGHTS['door_head'], 'sill': 0, 'casing': CS, 'pair': True})   # pair of leaves
            else: spec['openings'].append({'type': 'door', 'x': x, 'w': ow, 'head': HEIGHTS['door_head'], 'sill': 0, 'casing': CS, 'swing': 'L' if x < L / 2 else 'R'})
        elif ow >= 90:
            spec['openings'].append({'type': 'opening', 'x': x, 'w': ow, 'head': min(H, 120.0), 'sill': 0, 'casing': 0, 'open': True})
            spec['notes'].append(f'OPEN TO ADJACENT ROOM, NO CASING, HEAD AT {E.ftin(min(H, 120.0))}')
        else:
            spec['openings'].append({'type': 'opening', 'x': x, 'w': ow, 'head': HEIGHTS['door_head'], 'sill': 0, 'casing': CS})
    # fixtures against this wall
    tiles = []
    for f in fixtures:
        for on in f['on']:
            if on['wall'] != w['id']: continue
            x, fw = on['x'], on['w']; k = f['kind']
            if k == 'tub':
                spec['items'].append({'kind': 'tub', 'x': x, 'w': fw, 'h': 22})
                tiles.append((x, x + fw))      # back wall: the tub length; end walls: back corner to the tub's front edge
            elif k == 'shower':
                tiles.append((x, x + fw))
                if fw >= 40: spec['items'].append({'kind': 'shower_glass', 'x': x, 'w': fw, 'h': 84})
                spec['notes'].append('SHOWER: FRAMELESS GLASS ENCLOSURE, VALVE 4\'-0" AFF, HEAD 6\'-8" AFF, NICHE PER OWNER')
            elif k == 'toilet':
                spec['items'].append({'kind': 'toilet', 'x': x, 'w': fw, 'h': 30})
            elif k in ('vanity', 'lav'):
                spec['items'].append({'kind': 'vanity', 'x': x, 'w': fw, 'h': HEIGHTS['bath_counter'] - 1.25, 'counter': 1.25})
                spec['items'].append({'kind': 'mirror', 'x': x + 3, 'w': max(18, fw - 6), 'y': HEIGHTS['mirror_bottom'], 'h': 40})
                flanks = [sx for sx in (x - 6, x + fw + 6) if 8 <= sx <= L - 8]   # sconces just outside the mirror, never within 8 in. of a corner
                if len(flanks) == 2:
                    for sx in flanks: spec['items'].append({'kind': 'sconce', 'x': sx, 'y': HEIGHTS['sconce']})
                else:
                    spec['items'].append({'kind': 'sconce', 'x': x + fw / 2, 'y': HEIGHTS['mirror_bottom'] + 44}); spec['notes'].append('SCONCE CENTERED ABOVE THE MIRROR (NO ROOM TO FLANK)')
            elif k == 'upper':
                if kind == 'kitchen':
                    # uppers stop at windows: split the run around any window opening on this wall
                    runs = [(x, x + fw)]
                    for o in w['openings']:
                        if o['type'] == 'window':
                            runs = [seg for a, b in runs for seg in ((a, min(b, o['x'] - 1)), (max(a, o['x'] + o['w'] + 1), b)) if seg[1] - seg[0] >= 12]
                    for a, b in runs:
                        spec['items'].append({'kind': 'upper_cab', 'x': a, 'w': b - a, 'y': HEIGHTS['upper_cab_bottom'], 'h': (H - T['crown'] - 6 - HEIGHTS['upper_cab_bottom']) if H <= 126 else 42, 'doors': max(1, int(round((b - a) / 18.0)))})
                elif kind == 'closet':
                    spec['items'].append({'kind': 'shelves', 'x': x, 'w': fw, 'y': 84, 'h': min(H - 6, 108) - 84, 'n': 2})
                else:
                    spec['items'].append({'kind': 'upper_cab', 'x': x, 'w': fw, 'y': HEIGHTS['upper_cab_bottom'], 'h': 30, 'doors': max(1, int(round(fw / 18.0)))})
            elif k == 'cabinet':
                if kind == 'closet':
                    spec['items'].append({'kind': 'tall_cab', 'x': x, 'w': fw, 'h': 84, 'doors': max(1, int(round(fw / 24.0)))})
                    spec['notes'].append('WARDROBE UNITS PER MILLWORK SHOP DRAWINGS, SHEET ID-801')
                elif kind == 'bath':
                    spec['items'].append({'kind': 'vanity', 'x': x, 'w': fw, 'h': HEIGHTS['bath_counter'] - 1.25, 'counter': 1.25})
                else:
                    doors = max(1, int(round(fw / 18.0)))
                    spec['items'].append({'kind': 'base_cab', 'x': x, 'w': fw, 'h': HEIGHTS['counter'] - 1.5, 'counter': 1.5, 'doors': doors})
            elif k == 'fridge':
                spec['items'].append({'kind': 'box', 'x': x, 'w': fw, 'y': 0, 'h': 84, 'lw': 0.6}); spec['notes'].append('REFRIGERATOR / FREEZER PER APPLIANCE SCHEDULE, PANEL-READY')
            elif k == 'range':
                spec['items'].append({'kind': 'box', 'x': x, 'w': fw, 'y': 0, 'h': 36, 'lw': 0.6}); spec['notes'].append('APPLIANCE PER APPLIANCE SCHEDULE (SEE PLAN LABEL), PANEL-READY WHERE SHOWN')
            elif k == 'sink' and kind in ('kitchen', 'utility'):
                if not any(i['kind'] == 'base_cab' and i['x'] <= x + 2 and i['x'] + i['w'] >= x + fw - 2 for i in spec['items']):
                    spec['items'].append({'kind': 'base_cab', 'x': max(0, x - 6), 'w': min(L, x + fw + 6) - max(0, x - 6), 'h': HEIGHTS['counter'] - 1.5, 'counter': 1.5, 'doors': 2})
                spec['items'].append({'kind': 'box', 'x': x + 2, 'w': max(12, fw - 4), 'y': HEIGHTS['counter'] - 1, 'h': 1, 'lw': 0.4})
                if name.startswith('KITCHEN') and w['side'] == 'W':
                    spec['items'].append({'kind': 'box', 'x': x - 3, 'w': fw + 6, 'y': 66, 'h': 18, 'lw': 0.6}); spec['notes'].append('COOKTOP AND HOOD ON THIS WALL PER PLAN: HOOD BOTTOM 2\'-6" ABOVE THE COOKTOP, VENT PER MECHANICAL')
                else:
                    spec['notes'].append('SINK PER PLUMBING SCHEDULE, CENTERED ON THE BASE CABINET')
    spec['items'] = [i for i in spec['items'] if i]
    # finishes: paint everywhere, tile over wet walls, special walls
    special = SPECIAL.get((floor, name, w['id']))
    if special:
        spec['finishes'] += special(L, H, spec)
    for (a, b) in tiles:
        code = MASTER_TILE if name == 'MASTER BATHROOM' else TILE_BY_FLOOR[floor]
        spec['finishes'].append({'code': code, 'x0': max(0, a), 'x1': min(L, b), 'y0': 0, 'y1': H, 'hatch': 'tile', 'module': (12, 24), 'setout': 'center', 'tag_at': ((a + b) / 2, H * 0.72)})
    tile_cov = sum(min(L, b) - max(0, a) for a, b in tiles)
    covered = sum(min(L, f['x1']) - max(0, f['x0']) for f in spec['finishes'] if f['code'].startswith(('WP', 'WS')) and f['y1'] >= H - 0.1) + tile_cov
    if tile_cov >= 0.98 * L: crown = None; spec['crown'] = None        # tiled to the ceiling: no crown, no paint
    if covered < 0.98 * L:
        spec['finishes'].append({'code': paint, 'x0': 0, 'x1': L, 'y0': 0, 'y1': H, 'hatch': None, 'tag_at': (L * 0.5 if not tiles else (L * 0.12 if tiles[0][0] > L * 0.3 else L * 0.88), H * 0.86)})
    if crown: spec['finishes'].append({'code': 'CM-01', 'x0': 0, 'x1': L, 'y0': H - crown, 'y1': H, 'hatch': None, 'tag_at': (L * 0.2, H - crown - 9)})
    # notes
    spec['notes'] += [f'CEILING {E.ftin(H)} AFF PER ARCH. SET, VERIFY', 'DOOR & WINDOW HEADS 8\'-0" AFF U.N.O., VERIFY WITH ARCH. SET']
    if tiles: spec['notes'] += ['TILE TO CEILING, LEVEL SET-OUT FROM FIN. FLR., CENTERED ON WALL', 'WATERPROOF MEMBRANE AT ALL WET WALLS', 'BLOCKING 33" TO 36" AFF FOR FUTURE GRAB BARS']
    if tiles and any(o['type'] == 'window' for o in spec['openings']): spec['notes'].append('TEMPERED GLAZING: WINDOW WITHIN 60" OF THE TUB / SHOWER FLOOR, PER CODE')
    if kind == 'kitchen' and w['side'] == 'N': spec['notes'].append('BAY WINDOW UNITS ABOVE THIS WALL PER ARCH. SET: VERIFY HEAD AND SILL, UPPERS TO CLEAR')
    if kind == 'kitchen': spec['notes'] += ['CABINETS PER MILLWORK SHOP DRAWINGS, SHEET ID-801', 'COUNTER 3\'-0" AFF, UPPERS 4\'-6" AFF U.N.O.']
    spec['notes'].append('BASE & CASING PER TYPICAL DETAILS, SHEET ID-801')
    return spec

# special wall finishes keyed by (floor, room, wall id)
def great_room_east(L, H, spec):
    # fireplace from the cabinet cluster placed on this wall (the stone zone), paneling either side
    fp = [i for i in spec['items'] if i['kind'] == 'base_cab' and i['w'] >= 48]
    spec['items'] = [i for i in spec['items'] if i not in fp]
    out = []
    if fp:
        x, w = fp[0]['x'], fp[0]['w']
        spec['items'].append({'kind': 'fireplace', 'x': x, 'w': w, 'h': H, 'opening': (48, 36), 'hearth': 0})
        out.append({'code': 'WS-01', 'x0': x, 'x1': x + w, 'y0': 0, 'y1': H, 'hatch': 'stone', 'tag_at': (x + w / 2, H * 0.78)})
        out.append({'code': 'WP-01', 'x0': 0, 'x1': x, 'y0': 0, 'y1': H, 'hatch': 'panels', 'module': 36.0, 'tag_at': (x / 2, H * 0.6)})
        out.append({'code': 'WP-01', 'x0': x + w, 'x1': L, 'y0': 0, 'y1': H, 'hatch': 'panels', 'module': 36.0, 'tag_at': (x + w + (L - x - w) / 2, H * 0.6)})
        spec['notes'] += ['WS-01 STONE: FULL HEIGHT, BOOK-MATCHED SLABS, SHOP DRAWINGS REQ\'D', 'WP-01 PANELS: MODULE CENTERED EACH SIDE, PAINTED PT-01 SATIN', 'FIREPLACE OPENING & UNIT PER MANUFACTURER, VERIFY CLEARANCES']
    else:   # no fireplace found on the base: center a 6 ft stone zone and flag it
        x, w = L / 2 - 36, 72
        spec['items'].append({'kind': 'fireplace', 'x': x, 'w': w, 'h': H, 'opening': (48, 36), 'hearth': 0})
        out.append({'code': 'WS-01', 'x0': x, 'x1': x + w, 'y0': 0, 'y1': H, 'hatch': 'stone', 'tag_at': (x + w / 2, H * 0.78)})
        out.append({'code': 'WP-01', 'x0': 0, 'x1': x, 'y0': 0, 'y1': H, 'hatch': 'panels', 'module': 36.0, 'tag_at': (x / 2, H * 0.6)})
        out.append({'code': 'WP-01', 'x0': x + w, 'x1': L, 'y0': 0, 'y1': H, 'hatch': 'panels', 'module': 36.0, 'tag_at': (x + w + (L - x - w) / 2, H * 0.6)})
        spec['notes'].append('FIREPLACE NOT ON THE BASE PLAN: STONE ZONE ASSUMED 6\'-0" CENTERED, VERIFY WITH ARCH.')
    return out
def master_headboard(L, H, spec):
    spec['notes'] += ['WP-02 PANELING CORNER TO CORNER, FULL HEIGHT, PAINTED PT-02 SATIN', 'PANEL MODULE CENTERED ON WALL, SHOP DRAWINGS REQ\'D', 'BED CENTERED ON WALL, READING SCONCES S2 CL 4\'-6" AFF, 3\'-6" EACH SIDE OF CENTER']
    for sx in (L / 2 - 42, L / 2 + 42): spec['items'].append({'kind': 'sconce', 'x': sx, 'y': 54})
    return [{'code': 'WP-02', 'x0': 0, 'x1': L, 'y0': 0, 'y1': H, 'hatch': 'panels', 'module': 30.0, 'tag_at': (L * 0.15, H * 0.6)}]
SPECIAL = {(1, 'GREAT ROOM', 'E'): great_room_east, (2, 'MASTER SUITE', 'E2'): master_headboard}

# ---------------------------------------------------------------- sheets
def build():
    doc = fitz.open()
    index = []          # dicts: floor, room, wall, side, number, sheet
    cells_frame = (FR.x0 + 6, HDR_Y + 8, TB_X - 10, FR.y1 - 6)
    cells = E.layout_cells(cells_frame, 2, 2)
    state = {'sheet': None, 'cell': 4, 'n': 0, 'floor': None, 'count': {1: 0, 2: 0}}
    series = {1: 700, 2: 720}      # Floor 1 elevations ID-701.., Floor 2 ID-721..

    def new_sheet(floor):
        state['count'][floor] += 1
        no = f"ID-{series[floor] + state['count'][floor]}"
        sh = Sheet(doc)
        sh.frame(f'INTERIOR ELEVATIONS - FLOOR {floor}', 'SCALE: AS NOTED', ['INTERIOR ELEVATIONS', f'FLOOR {floor}'], no, legend_rule=False)
        state.update(sheet=sh, cell=0, n=0, no=no, floor=floor)
        return sh

    for floor in (1, 2):
        model = json.load(open(f'model_f{floor}.json'))
        for room in model['rooms']:
            if room['name'] in SKIP_ROOMS: continue
            walls = [w for w in room['walls'] if w['length_in'] >= MIN_WALL_IN
                     and sum(o['w'] for o in w['openings'] if o['type'] == 'opening') < 0.85 * w['length_in']]   # a wall that is all opening is not a wall
            multi = {s: sum(1 for w in walls if w['side'] == s) for s in 'NESW'}
            if state['sheet'] is None or state['floor'] != floor or (len(walls) <= 4 and state['cell'] + len(walls) > 4): new_sheet(floor)
            for w in walls:
                if state['cell'] >= 4: new_sheet(floor)
                sh = state['sheet']; cell = cells[state['cell']]; state['cell'] += 1; state['n'] += 1
                spec = wall_spec(floor, room, w, room['fixtures'])
                prefer = ('1/2', '3/8', '1/4') if room['kind'] in ('bath', 'kitchen') else ('3/8', '1/4')
                scale_name, k = E.best_scale(cell, spec, prefer=prefer)
                origin = E.fit_origin(cell, spec, k)
                title = view_title(room['name'], w['side']) + (f"  (WALL {w['id']})" if multi[w['side']] > 1 else '')
                E.title_bar(sh.p, sh.font, sh.fontname, cell, state['n'], title, f'SCALE: {scale_name}" = 1\'-0"')
                view = E.ElevationView(sh.p, sh.font, sh.fontname, origin, k, spec)
                view.draw(tag_fn=lambda x, y, code, sh=sh: sh.tag(x, y, code, lead=8, sides='l'), number=state['n'], cell=cell)
                index.append({'floor': floor, 'room': room['name'], 'wall': w['id'], 'side': w['side'], 'number': state['n'], 'sheet': state['no'],
                              'a': w['a'], 'b': w['b'], 'length_in': w['length_in'], 'scale': scale_name})
    doc.set_metadata({'title': 'Casa Grove - Interior Elevations', 'author': 'Helios Development', 'subject': 'HD102 Interior Elevations - Floors 1 and 2',
                      'creator': 'Helios Development', 'producer': 'Helios Development'})
    fix_soft_hyphen(doc)
    doc.save(OUT, garbage=3, deflate=True)
    json.dump(index, open('elev_index.json', 'w'), indent=1)
    json.dump(SKIP_REASON, open('elev_skipped.json', 'w'), indent=1)
    print('saved', OUT, 'pages', len(doc), 'views', len(index))

if __name__ == '__main__':
    build()
