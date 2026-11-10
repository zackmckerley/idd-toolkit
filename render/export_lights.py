"""The lighting plan (ID-121, build_rcp) for one room, in the renderer's room coordinates, so a rendering lights the room the way
the drawings do: recessed downlights and pendants at their plan positions. python3 render/export_lights.py kitchen render/kitchen_lights.json"""
import sys, json
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
import build_rcp as RC
from shapely.geometry import Point
room, out = sys.argv[1], sys.argv[2]
if room == 'kitchen':
    F_W, F_N, KD, PT = 356.22, 173.04, 244.9375, 1.5                    # build_kitchen_rev1: FOR plan pt to kitchen inches, Y north from the south face
    R = RC.FN.RR.rooms(1); g = R['KITCHEN AND DINING'].buffer(-2)
    W = lambda x, y: ((x - F_W) / PT, KD - (y - F_N) / PT)
    lights = []
    for k, d, c, r in RC.for_items(1):
        if k == 'recess' and 10 < r.width < 14 and g.contains(Point(c)):
            X, Y = W(*c)
            if 0 < Y < KD: lights.append({'type': 'recess', 'X': round(X, 2), 'Y': round(Y, 2), 'tag': 'L1'})
    for p in RC.P1_FOR:
        X, Y = W(p[0] + RC.ISL_SHIFT_PT, p[1]); lights.append({'type': 'pendant', 'X': round(X, 2), 'Y': round(Y, 2), 'tag': 'P1'})
json.dump(lights, open(out, 'w'), indent=0); print(len(lights), [(l['tag'], l['X'], l['Y']) for l in lights])
