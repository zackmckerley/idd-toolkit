"""Exterior CC0 assets from Poly Haven for the whole-property model (owner 11.11.26): lawn, asphalt, stucco, sidewalk concrete,
mulch, a pure-sky HDRI for daylight, and planting models (trees and shrubs) for FOR's / the landscape architect's plant list."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
def get(u, out=None):
    r = subprocess.run(['curl', '-sSfL', '--max-time', '300', '-A', 'IDD-render/1.0'] + (['-o', out] if out else []) + [u], capture_output=True, check=True)
    return r.stdout
TEX = ['leafy_grass', 'aerial_grass_rock', 'asphalt_02', 'white_stucco', 'concrete_floor', 'brushed_concrete', 'forrest_ground_01', 'gravel_floor']
HDRI = ['kloofendal_48d_partly_cloudy_puresky', 'qwantani_mid_morning_puresky']
MODELS = ['island_tree_01', 'island_tree_02', 'island_tree_03', 'jacaranda_tree', 'tree_small_02', 'shrub_01', 'shrub_02', 'shrub_04',
          'grass_medium_01', 'potted_plant_04', 'outdoor_table_chair_set_01', 'fire_hydrant', 'planter_box_01']
def tex(a):
    try:
        d = json.loads(get('https://api.polyhaven.com/files/' + a)); os.makedirs(os.path.join(HERE, a), exist_ok=True)
        for m in ('Diffuse', 'nor_gl', 'Rough'):
            out = os.path.join(HERE, a, m + '.jpg')
            if m in d and not os.path.exists(out): get(d[m]['2k']['jpg']['url'], out)
        return a, 'ok'
    except Exception as e: return a, 'fail %s' % e
def hdr(h):
    out = os.path.join(HERE, h + '_2k.hdr')
    if not os.path.exists(out): get(json.loads(get('https://api.polyhaven.com/files/' + h))['hdri']['2k']['hdr']['url'], out)
    return h, 'ok'
def model(m):
    try:
        dest = os.path.join(HERE, 'models', m)
        if os.path.exists(os.path.join(dest, m + '.gltf')): return m, 'have'
        g = json.loads(get('https://api.polyhaven.com/files/' + m))['gltf']['1k']['gltf']; os.makedirs(dest, exist_ok=True)
        get(g['url'], os.path.join(dest, m + '.gltf'))
        for rel, inc in g.get('include', {}).items():
            p_ = os.path.join(dest, rel); os.makedirs(os.path.dirname(p_), exist_ok=True); get(inc['url'], p_)
        return m, 'ok'
    except Exception as e: return m, 'fail %s' % e
with ThreadPoolExecutor(6) as ex:
    for r in list(ex.map(tex, TEX)) + list(ex.map(hdr, HDRI)) + list(ex.map(model, MODELS)): print(*r)
