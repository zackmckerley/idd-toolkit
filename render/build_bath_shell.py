"""Master bath shell for the photoreal renders (11.11.26; owner: "the toilet compartment and the shower... that is all one room").

Room frame (the photoreal room frame): X east from the west wall face, Y north from the alcove line's room face; the room
162 x 79.125, ceiling 118. The alcove line (ID-321 view 3) is the south wall: from the east, the W.C. front (door 30 in. at
8 to 38), the tub alcove open full height (48.625 to 113.375, no header, the crown stops at its jambs), the shower's painted
front with its cased 30 in. opening and one-panel hammered glass door (125 to 155). The line is 6 in. thick here (FOR's
plan shows about 4-1/2 in.: VERIFY); the compartments behind it are 57 in. deep (ID-322, ID-323): shower X 0 to 43.625,
tub alcove X 48.625 to 113.375, W.C. X 118.375 to 162, 5 in. partitions.

Views out: 0 N, 1 E, 2 S (the alcove line, rebuilt), 3 W, then the compartments' walls, built by stage_bath at their places:
4 shower W, 5 shower S, 6 shower E, 7 shower N (inside of the front), 8 tub W, 9 tub S, 10 tub E, 11 W.C. N, 12 W.C. E,
13 W.C. S, 14 W.C. W."""
import json, copy, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(HERE, 'bath_views.json')))
D = 57.0


def view(base, name, length, calls, openings):
    v = copy.deepcopy(base); v['view'] = name; v['length'] = length; v['calls'] = copy.deepcopy(calls); v['openings'] = openings
    return v


def cut(x0, x1, y1=130.0, note=''):
    return {'kind': 'opening', 'x0': x0, 'x1': x1, 'y0': 0.0, 'y1': y1, 'ctx': ['opening'], 'beyond': False, 'note': note}


def no(calls, *comps):
    return [c for c in calls if c['comp'] not in comps]


S = src[2]
s_calls = no(S['calls'], 'window', 'glazing', 'muntins', 'freestanding_tub', 'rev_cloud')
s_open = [dict(o, beyond=False) for o in S['openings'] if o['kind'] == 'door_leaf'] + [   # the W.C. is modelled behind its door
    cut(48.625, 113.375, note='the tub alcove, open full height'),
    cut(125.0, 155.0, 96.0, note="the shower's cased opening; the hammered glass door stands in it")]
tile = next(c for c in src[4]['calls'] if c['comp'] == 'tile_grid')
def piece(x0, x1, y0, y1):
    t = copy.deepcopy(tile); t['args'].update({'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}); return [t]
def tiled(L, extra=()):
    t = copy.deepcopy(tile); t['args']['x1'] = L; return [t] + list(extra)

out = [
    src[0], src[1], view(S, 'SOUTH ELEVATION - MASTER BATH', 162.0, s_calls, s_open), src[3],
    # shower
    view(src[4], 'SHOWER - WEST WALL', D, src[4]['calls'], src[4]['openings']),
    view(src[5], 'SHOWER - SOUTH WALL', 43.625, src[5]['calls'], src[5]['openings']),
    view(src[6], 'SHOWER - EAST WALL', D, tiled(D, src[6]['calls']), []),
    view(src[6], 'SHOWER - NORTH WALL', 43.625, piece(0, 7.0, 0, 118.0) + piece(37.0, 43.625, 0, 118.0) + piece(7.0, 37.0, 96.0, 118.0),
         [cut(7.0, 37.0, 96.0, 'the door opening')]),   # tile_grid fills its whole rectangle: three pieces round the door
    # tub alcove
    view(src[7], 'TUB ALCOVE - WEST WALL', D, no(src[7]['calls'], 'freestanding_tub'), []),
    view(src[8], 'TUB ALCOVE - SOUTH WALL', 64.75, src[8]['calls'], src[8]['openings']),   # the tub built once, from here
    view(src[9], 'TUB ALCOVE - EAST WALL', D, no(src[9]['calls'], 'freestanding_tub'), []),
    # W.C.: its north wall is the back of the alcove line (the room wall is the solid): only its trim, no second leaf
    view(src[10], 'WATER CLOSET - NORTH WALL', 43.625, no(src[10]['calls'], 'door_leaf'), [cut(-12.0, 60.0, note='the solid is the room wall')]),
    view(src[11], 'WATER CLOSET - EAST WALL', D, src[11]['calls'], []),
    view(src[12], 'WATER CLOSET - SOUTH WALL', 43.625, src[12]['calls'], []),
    view(src[13], 'WATER CLOSET - WEST WALL', D, src[13]['calls'], []),
]
for v in out: v['room'] = 'MASTER BATH'
for v in out:   # the 5 in. partitions: two 2-1/2 in. backers back to back (a 6 in. solid stood 1 in. proud into the next compartment)
    if v['view'] in ('SHOWER - EAST WALL', 'TUB ALCOVE - WEST WALL', 'TUB ALCOVE - EAST WALL', 'WATER CLOSET - WEST WALL'): v['thick'] = 2.5
json.dump(out, open(os.path.join(HERE, 'bath_shell_views.json'), 'w'), indent=1)
for i, v in enumerate(out):
    print(i, v['view'], v['length'], [c['comp'] for c in v['calls'] if c['comp'] not in ('rev_cloud', 'shadow')],
          [(o['kind'], o['x0'], o['x1']) for o in v['openings']])
