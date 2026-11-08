"""Exposure calibration for rendered elevations: a plain wall of linear albedo 0.5 is rendered with the production light
and the exposure is set so its lit face comes out at 0.5. Run after any change to the light (SUN_E, WORLD_E, angle):
    python3 render/calibrate.py
Writes render/calibration.json; render_view.py reads it."""
import json, math, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
PY = '/home/claude/rendervenv/bin/python'   # the Blender (bpy) venv; this script runs with python3
tmp = tempfile.mkdtemp()
view = [{'k': 3.0, 'room': '__cal__', 'view': 'CAL', 'length': 96.0, 'ceiling': 96.0, 'prims': [], 'openings': [], 'labels': []}]
json.dump(view, open(os.path.join(tmp, 'v.json'), 'w'))
rf = os.path.join(HERE, 'room_finishes.json'); R = json.load(open(rf))
R['__cal__'] = {'roles': {'wall': 'CAL-GRAY', 'floor': 'CAL-GRAY'}, 'views': {}}; json.dump(R, open(rf, 'w'), indent=1)
cal = os.path.join(HERE, 'calibration.json')
if os.path.exists(cal): os.remove(cal)
try:
    subprocess.run([PY, os.path.join(HERE, 'render_view.py'), os.path.join(tmp, 'v.json'), '0', os.path.join(tmp, 'c.png'), '--samples', '64', '--ppi', '2'], check=True, capture_output=True)
finally:
    R.pop('__cal__'); json.dump(R, open(rf, 'w'), indent=1)
import numpy as np
from PIL import Image
a = np.asarray(Image.open(os.path.join(tmp, 'c.png')).convert('RGB')).astype(float) / 255
c = a[40:150, 40:150].reshape(-1, 3).mean(0)
linv = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).mean()
exp = -math.log2(linv / 0.5)
json.dump({'exposure': round(exp, 4), 'measured_linear_before': round(float(linv), 4), 'target': 0.5}, open(cal, 'w'))
print('measured', linv, 'exposure', exp)
