"""Master bedroom shell for the photoreal renders (11.11.26), from the captured elevations in mbr_views.json and the key plan
ID-310 (measured at 2.5 px/in, origin the west wall face and the window wall face).

Room frame, inches: X east from the west wall face, Y north from the window wall face. The bedroom is 183.375 x 161.4; the
bed wall (east) runs 117.4 from the north wall to the safe closet line Y 44.0; the window wall runs 132.2 from the west wall
to the nook. The reading nook is open to the room: X 132.2 to 231.8, Y -49.9 to 0, and its north strip X 183.375 to 231.8,
Y 0 to 44.0. Terrace doors in the nook's south wall, the arched bookcase on its west wall, jib door 21 in its north wall.

Views out: 0 N (ID-311 view 1), 1 E (ID-312 view 2, the bed wall), 2 S (ID-311 view 3, the window wall, built with
--shift SOUTH=51.2), 3..6 the nook's N, E, S, W walls, built by stage_mbr at their own positions.
The captured views 2 and 4 each hold two drawings (view 2 also has the west elevation, view 4 the nook south wall): split here."""
import json, copy, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(HERE, 'mbr_views.json')))
DEP, NOOK_N, NOOK_S = 161.4, 44.0, -49.9


def view(base, name, length, calls, openings):
    v = copy.deepcopy(base); v['view'] = name; v['length'] = length; v['calls'] = copy.deepcopy(calls); v['openings'] = openings
    return v


def cut(x0, x1, note):
    return {'kind': 'opening', 'x0': x0, 'x1': x1, 'y0': 0.0, 'y1': 130.0, 'ctx': ['opening'], 'beyond': False, 'note': note}


def split(calls):
    """A captured view that holds two drawings: the second starts where a 'base' call restarts at x0 = 0."""
    for i in range(1, len(calls)):
        if calls[i]['comp'] == 'base' and calls[i]['args'].get('x0') == 0 and any(c['comp'] == 'base' for c in calls[:i]):
            return calls[:i], calls[i:]
    return calls, []


def stretch(calls, lo=None, hi=None, d=0.75):
    """Outside corners: base and crown run past the wall end by their own depth so the two returns meet."""
    for c in calls:
        if c['comp'] in ('base', 'crown'):
            if lo is not None and abs(c['args']['x0'] - lo) < 0.3: c['args']['x0'] = lo - d
            if hi is not None and abs(c['args']['x1'] - hi) < 0.3: c['args']['x1'] = hi + d
    return calls


N, E2, NE4, NW5, S6 = src[1], src[2], src[4], src[5], src[6]
e_calls, _west = split(E2['calls'])
ne_calls, ns_calls = split(NE4['calls'])
ns_calls = [c for c in ns_calls if not (c['comp'] in ('base', 'crown') and c['args'].get('x0', 0) > 87)]   # a third drawing's stubs
nw_calls = [c for c in NW5['calls'] if c['comp'] not in ('base', 'crown', 'switch', 'outlet') or
            min(c['args'].get('x0', c['args'].get('cx', 0)), 99) < 49.9]
for c in nw_calls:
    if c['comp'] == 'crown' and c['args']['x1'] > 49.9: c['args']['x1'] = 49.95
    if c['comp'] == 'cabinet_lower': c['args']['depth'] = 12.0          # the bookcase is 12 in. deep (ID-310), not a 24 in. base cabinet

# ---- the wainscot as drawn (ID-311, ID-312, ID-313 in 261110 ReviewSet-FullSize): panels are an outer rectangle with an inner
# one inset by the moulding width; chair rails are the 3 in. rectangles at 37 to 40 in.
import fitz
FS = fitz.open(os.path.join(os.path.dirname(HERE), '261110.HD102.ReviewSet-FullSize.pdf'))
def drawn(page, ox, oy, L, k, xlim=(-1, 1e9), skip=()):
    rs = []
    for dr in FS[page].get_drawings():
        r = dr['rect']; its = dr['items']
        if dr.get('fill') or not ((len(its) == 1 and its[0][0] == 're') or (len(its) in (4, 5) and all(i[0] == 'l' for i in its))): continue
        x0, x1, y0, y1 = (r.x0 - ox) / k, (r.x1 - ox) / k, (oy - r.y1) / k, (oy - r.y0) / k
        if x0 < -1 or x1 > L + 1 or y0 < -0.5 or y1 > 117 or x0 < xlim[0] or x1 > xlim[1]: continue
        if any(s0 <= x0 and x1 <= s1 for s0, s1 in skip): continue
        rs.append((round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3), round(dr.get('width') or 0, 2)))
    rs = sorted(set(rs)); panels = []; rails = []
    for o in rs:
        if abs(o[4] - 0.65) < 0.03:
            for i in rs:
                if abs(i[4] - 0.5) < 0.03:
                    m = i[0] - o[0]
                    if 0.5 <= m <= 2.6 and all(abs(v) < 0.08 for v in (i[1] - o[1] - m, o[2] - i[2] - m, o[3] - i[3] - m)):
                        panels.append([o[0], o[1], o[2], o[3], round(m, 3)]); break
        if abs(o[1] - 37.0) < 0.3 and abs(o[3] - 40.0) < 0.3: rails.append([o[0], o[2], o[1], o[3]])
    return {'comp': 'panel_drawn', 'args': {'panels': panels, 'rails': rails}, 'depth': 0, 'parent': None}


def wainscot(calls, call):
    calls = [c for c in calls if c['comp'] not in ('panel_wall', 'chair_rail')] + [call]
    for c in calls:
        if c['comp'] == 'nightstand': c['args']['lamp'] = False        # the swing-arm sconces are the bedside light
    return calls


out = [
    view(N, 'NORTH ELEVATION - MASTER BEDROOM', 183.375, N['calls'], N['openings']),
    view(E2, 'EAST ELEVATION - MASTER BEDROOM', DEP, stretch(e_calls, hi=117.25, d=0.9),
         [cut(DEP - NOOK_N - 0.05, DEP + 12, 'open south of the safe closet line to the nook strip; the wall ends 0.05 in. inside the nook north wall')]),
    view(S6, 'SOUTH ELEVATION - MASTER BEDROOM', 132.2, stretch(copy.deepcopy(S6['calls']), lo=0.0),
         [o for o in S6['openings']] + [cut(-12.0, 0.0, 'the wall ends at the nook west wall face, X 132.2')]),
    view(src[3], 'READING NOOK - NORTH WALL', 99.6, stretch(copy.deepcopy(src[3]['calls']), lo=51.375),
         [cut(-12.0, 51.2, 'open to the bedroom west of the bed wall face; the end 0.025 in. inside the bed wall')]),          # jib door 21 drawn by stage_mbr: no hole
    view(NE4, 'READING NOOK - EAST WALL', 93.9, ne_calls, []),
    view(NE4, 'READING NOOK - SOUTH WALL', 99.6, ns_calls, [o for o in NE4['openings'] if o['kind'] == 'door_pair' or 'door_pair' in o['ctx']]),
    view(NW5, 'READING NOOK - WEST WALL, BOOKCASE', 93.9, stretch(nw_calls, hi=49.95),
         [cut(49.85, 120.0, 'open to the bedroom north of the window wall face')]),
]
DRAWN = [(33, 85.7, 625.0, 183.375, 4.5, (-1, 1e9), ((4.0, 51.0),)), (34, 85.98, 625.0, 117.25, 4.5, (-1, 1e9), ()),
         (33, 994.3, 611.0, 132.0, 4.5, (-1, 1e9), ()), (35, 290.5, 471.0, 100.0, 3.0, (-1, 1e9), ()),
         (35, 1092.575, 471.0, 93.95, 3.0, (-1, 1e9), ()), (35, 290.5, 1020.5, 100.0, 3.0, (-1, 1e9), ((17.0, 83.0),)),
         (35, 1092.575, 1026.25, 93.95, 3.0, (-1, 49.9), ((3.0, 47.0),))]
for v, (pg, ox, oy, L, k, xl, sk) in zip(out, DRAWN):
    dcall = drawn(pg, ox, oy, L, k, xl, sk); v['calls'] = wainscot(v['calls'], dcall)
    print(v['view'], len(dcall['args']['panels']), 'panels', len(dcall['args']['rails']), 'rails')
for v in out: v['room'] = 'MASTER BEDROOM'
json.dump(out, open(os.path.join(HERE, 'mbr_shell_views.json'), 'w'), indent=1)
for i, v in enumerate(out):
    print(i, v['view'], v['length'], [c['comp'] for c in v['calls']], [(o['kind'], round(o['x0'], 2), round(o['x1'], 2)) for o in v['openings']])
