"""Download the CC0 render assets (Poly Haven) into render/assets: textures at 2k (Diffuse, nor_gl, Rough) and the HDRIs.
    python3 render/fetch_assets.py
Poly Haven blocks Python's default user agent, so curl does the fetching."""
import json, os, subprocess, sys, zipfile, tempfile
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.abspath(__file__))
HERE = sys.argv[sys.argv.index('--dest') + 1] if '--dest' in sys.argv else os.path.join(ROOT, 'assets'); os.makedirs(HERE, exist_ok=True)
def get(u, out=None):
    r = subprocess.run(['curl', '-sSfL', '--max-time', '180', '-A', 'IDD-render/1.0'] + (['-o', out] if out else []) + [u], capture_output=True, check=True)
    return r.stdout
TEX = ['oak_veneer_01', 'wood_floor', 'marble_01', 'painted_plaster_wall', 'rough_linen', 'laminate_floor_02', 'plank_flooring_02', 'terry_cloth', 'concrete_pavement_02']
HDRI = ['white_home_studio', 'modern_bathroom', 'green_sanctuary', 'garden_nook']
MODELS = ['potted_plant_01', 'potted_plant_04', 'ceramic_vase_01', 'ceramic_vase_03', 'wooden_bowl_01', 'wicker_basket_02', 'wooden_stool_02', 'potted_plant_02', 'modern_arm_chair_01']
for a in TEX:
    d = json.loads(get('https://api.polyhaven.com/files/' + a)); os.makedirs(os.path.join(HERE, a), exist_ok=True)
    for m in ('Diffuse', 'nor_gl', 'Rough'):
        out = os.path.join(HERE, a, m + '.jpg')
        if m in d and not os.path.exists(out): get(d[m]['2k']['jpg']['url'], out)
for h in HDRI:
    out = os.path.join(HERE, h + '_2k.hdr')
    if not os.path.exists(out): get(json.loads(get('https://api.polyhaven.com/files/' + h))['hdri']['2k']['hdr']['url'], out)
for m in MODELS:
    dest = os.path.join(HERE, 'models', m)
    if os.path.exists(os.path.join(dest, m + '.gltf')): continue
    g = json.loads(get('https://api.polyhaven.com/files/' + m))['gltf']['1k']['gltf']; os.makedirs(dest, exist_ok=True)
    get(g['url'], os.path.join(dest, m + '.gltf'))
    for rel, inc in g.get('include', {}).items():
        p_ = os.path.join(dest, rel); os.makedirs(os.path.dirname(p_), exist_ok=True); get(inc['url'], p_)
# ambientCG curated library (render/material_library.json), 2K JPG, about 20 MB a material before trimming
KEEP = ('_Color.jpg', '_NormalGL.jpg', '_Roughness.jpg', '_Metalness.jpg', '_Displacement.jpg')
def acg(aid):
    dest = os.path.join(HERE, 'acg', aid)
    if os.path.exists(os.path.join(dest, aid + '_2K-JPG_Color.jpg')): return aid, 'have'
    os.makedirs(dest, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        z = os.path.join(t, aid + '.zip'); get('https://ambientcg.com/get?file=%s_2K-JPG.zip' % aid, z)
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.endswith(KEEP): zf.extract(n, dest)
    return aid, 'got'
lib = json.load(open(os.path.join(ROOT, 'material_library.json')))
ids = [a for k, v in lib.items() if not k.startswith('_') for a in v]
for aid, st in ThreadPoolExecutor(4).map(acg, ids): print(aid, st)
print('assets in', HERE)
