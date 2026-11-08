"""Rebuild render/paint/official/*_official.json from the makers' own downloads.
Sources (fetch again when a maker reissues its palette):
  Sherwin-Williams ColorSnap ASE by number   sw-colors-number-csp-ase.ase          (1,526 colors)
  Sherwin-Williams Emerald Designer Edition  sw-xcl-sherwin-williams-ede.zip       (200 colors with LRV, the SW 9xxx series)
  Benjamin Moore collection ASEs             bm_<collection>.ase, nine collections (about 4,056 colors, full names)
Run: python3 -I render/paint/build_official.py"""
import struct, glob, json, re, os, zipfile, io
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'official')

def ase(path):
    b = open(path, 'rb').read(); assert b[:4] == b'ASEF'
    n = struct.unpack('>I', b[8:12])[0]; i = 12; out = []
    for _ in range(n):
        t, l = struct.unpack('>HI', b[i:i+6]); body = b[i+6:i+6+l]; i += 6 + l
        if t != 1: continue
        nl = struct.unpack('>H', body[:2])[0]; name = body[2:2+nl*2].decode('utf-16-be').rstrip('\x00'); j = 2 + nl*2
        if body[j:j+4] == b'RGB ':
            r, g, bb = struct.unpack('>fff', body[j+4:j+16])
            out.append((name, '#%02X%02X%02X' % tuple(round(v*255) for v in (r, g, bb))))
    return out

sw = []
for nm, h in ase(os.path.join(D, 'sw-colors-number-csp-ase.ase')):
    m = re.match(r'(.*) \((SW \d{4})\)$', nm)
    if m: sw.append({'brand': 'SW', 'label': m.group(2), 'name': m.group(1).strip(), 'hex': h, 'source': 'sherwin-williams.com ColorSnap ASE (official download)'})
json.dump(sw, open(os.path.join(D, 'sw_official.json'), 'w'), indent=0)

import openpyxl
z = zipfile.ZipFile(os.path.join(D, 'sw-xcl-sherwin-williams-ede.zip'))
x = [n for n in z.namelist() if n.endswith('.xlsx')][0]
rows = list(openpyxl.load_workbook(io.BytesIO(z.read(x)), read_only=True, data_only=True).active.iter_rows(values_only=True))
ede = []
for r in rows[1:]:
    if not r or not r[4] or r[8] is None: continue
    cid = str(r[4]).replace(' ', '')
    ede.append({'brand': 'SW', 'label': 'SW ' + cid[2:], 'name': r[3], 'hex': '#%02X%02X%02X' % (r[8], r[9], r[10]),
                'lrv': round(float(r[6]), 1) if r[6] else None, 'source': 'sherwin-williams.com Emerald Designer Edition data (official download)'})
json.dump(ede, open(os.path.join(D, 'sw_ede_official.json'), 'w'), indent=0)

bm = {}
for f in sorted(glob.glob(os.path.join(D, 'bm_*.ase'))):
    coll = os.path.basename(f)[3:-4]
    for nm, h in ase(f):
        m = re.match(r'(\S+)\s+(.*)$', nm)
        if not m: continue
        lab = 'BM ' + m.group(1)
        bm.setdefault(lab, {'brand': 'BM', 'label': lab, 'name': re.sub(r'[®™]', '', m.group(2)).strip(), 'hex': h,
                            'source': 'benjaminmoore.com %s ASE (official download)' % coll})
json.dump(list(bm.values()), open(os.path.join(D, 'bm_official.json'), 'w'), indent=0)
print('SW', len(sw), 'SW EDE', len(ede), 'BM', len(bm))
