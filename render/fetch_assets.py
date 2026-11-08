"""Download the CC0 render assets (Poly Haven) into render/assets: textures at 2k (Diffuse, nor_gl, Rough) and the HDRIs.
    python3 render/fetch_assets.py
Poly Haven blocks Python's default user agent, so curl does the fetching."""
import json, os, subprocess
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); os.makedirs(HERE, exist_ok=True)
def get(u, out=None):
    r = subprocess.run(['curl', '-sSfL', '--max-time', '180', '-A', 'IDD-render/1.0'] + (['-o', out] if out else []) + [u], capture_output=True, check=True)
    return r.stdout
TEX = ['oak_veneer_01', 'wood_floor', 'marble_01', 'painted_plaster_wall', 'rough_linen']
HDRI = ['white_home_studio', 'modern_bathroom']
for a in TEX:
    d = json.loads(get('https://api.polyhaven.com/files/' + a)); os.makedirs(os.path.join(HERE, a), exist_ok=True)
    for m in ('Diffuse', 'nor_gl', 'Rough'):
        out = os.path.join(HERE, a, m + '.jpg')
        if m in d and not os.path.exists(out): get(d[m]['2k']['jpg']['url'], out)
for h in HDRI:
    out = os.path.join(HERE, h + '_2k.hdr')
    if not os.path.exists(out): get(json.loads(get('https://api.polyhaven.com/files/' + h))['hdri']['2k']['hdr']['url'], out)
print('assets in', HERE)
