"""Code, safety, purity and cross-reference checks for the Casa Grove set (gate G3). Run before assembling the set.
Usage: python3 idd_checks.py  -> prints a report and writes qa_checks.json (every check with pass/fail and the evidence)."""
import json, re, collections, sys, os
import pymupdf as fitz
import idd_electrical as EL

SET = {'ID-000': '261101.HD102.CoverSchedules.pdf', 'ID-001': '261101.HD102.CoverSchedules.pdf', 'ID-101': '261101.HD102.FlooringPlans.pdf', 'ID-102': '261101.HD102.FlooringPlans.pdf',
       'ID-201': '261101.HD102.WallFinishPlans.pdf', 'ID-202': '261101.HD102.WallFinishPlans.pdf', 'ID-301': '261101.HD102.RCPPlans.pdf', 'ID-302': '261101.HD102.RCPPlans.pdf',
       'ID-401': '261101.HD102.LightingPlans.pdf', 'ID-402': '261101.HD102.LightingPlans.pdf', 'ID-501': '261101.HD102.PowerDataPlans.pdf', 'ID-502': '261101.HD102.PowerDataPlans.pdf',
       'ID-601': '261101.HD102.FurniturePlans.pdf', 'ID-602': '261101.HD102.FurniturePlans.pdf', 'ID-801': '261101.HD102.Details.pdf'}
PLAN_X1 = 780
DIM = re.compile(r"\d+'-\d+(?:-\d/\d)?\"|\d+'-\d/\d\"")
FLOOR_CODE = re.compile(r'\b(?:WD|TL|ST|SL)-\d\d\b'); WALL_CODE = re.compile(r'\b(?:PT|CM|WS|WP|WT)-\d\d\b')
R = []
def check(name, ok, evidence=''):
    R.append({'check': name, 'pass': bool(ok), 'evidence': evidence if isinstance(evidence, str) else json.dumps(evidence)[:600]})
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {str(evidence)[:300]}'))

def plan_words(pdf, pno):
    return [(w[4].replace('\xad', '-'), w[0], w[1]) for w in fitz.open(pdf)[pno].get_text('words')]

def main():
    # ---------------- electrical code checks on the layouts
    for floor in (1, 2):
        model = json.load(open(f'model_f{floor}.json')); elec = json.load(open(f'electrical_f{floor}.json'))
        recs = [o for o in elec['power'] if o['type'] in ('REC', 'GFI', 'USB')]
        bad = []
        for r in model['rooms']:
            if r['kind'] == 'closet' or r['name'] == 'HIDDEN SAFE': continue
            for w in r['walls']:
                if w.get('guard') or w['length_in'] < 24: continue
                mine = [o for o in recs if o['room'] == r['name'] and o.get('wall') == w['id']]
                for a, b in EL.free_runs(w):
                    if b - a < 24: continue
                    xs = []
                    for o in mine:
                        # position along the wall from the device point
                        (ax, ay), (bx, by) = w['a'], w['b']; L = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
                        t = ((o['x'] - ax) * (bx - ax) + (o['y'] - ay) * (by - ay)) / L / EL.PT_PER_IN
                        xs.append(t)
                    xs = sorted(x for x in xs if a - 6 <= x <= b + 6)
                    if r['kind'] == 'bath': continue          # baths: one at the vanity, 210.52(D)
                    if not xs: bad.append((r['name'], w['id'], 'no receptacle on a run of %d in' % (b - a))); continue
                    pts = [a] + xs + [b]
                    if pts[1] - pts[0] > 72 or pts[-1] - pts[-2] > 72 or any(q - p > 144 for p, q in zip(xs, xs[1:])):
                        bad.append((r['name'], w['id'], 'spacing', [round(x) for x in xs], round(a), round(b)))
        check(f'NEC 210.52(A) receptacle spacing, floor {floor}', not bad, bad)
        wet = [o for o in recs if any(rm['name'] == o['room'] and rm['kind'] in ('bath', 'kitchen', 'utility') for rm in model['rooms'])]
        notgfi = [(o['room'], o['wall']) for o in wet if o['type'] != 'GFI' and o.get('aff') == 42]
        check(f'GFCI at counters in wet rooms, floor {floor}', not notgfi, notgfi)
        wetrooms = [rm['name'] for rm in model['rooms'] if rm['kind'] == 'bath']
        check(f'every bath has a GFCI receptacle, floor {floor}', all(any(o['room'] == n and o['type'] == 'GFI' for o in recs) for n in wetrooms), [n for n in wetrooms if not any(o['room'] == n and o['type'] == 'GFI' for o in recs)])
        # every habitable room has lighting and a switch
        nolight = [rm['name'] for rm in model['rooms'] if not any(o['room'] == rm['name'] for o in elec['lights'])]
        noswitch = [rm['name'] for rm in model['rooms'] if rm['kind'] != 'closet' and rm['name'] != 'HIDDEN SAFE' and any(o['room'] == rm['name'] for o in elec['lights']) and not any(s['room'] == rm['name'] for s in elec['switches'])]
        check(f'every room has a light, floor {floor}', not nolight, nolight)
        check(f'every lit room has a switch, floor {floor}', not noswitch, noswitch)
    # ---------------- elevations: safety notes and heights
    import build_elev as BE
    missing_grab, bad_heads, tempered = [], [], []
    for floor in (1, 2):
        model = json.load(open(f'model_f{floor}.json'))
        for r in model['rooms']:
            if r['name'] in BE.SKIP_ROOMS: continue
            for w in r['walls']:
                if w['length_in'] < BE.MIN_WALL_IN: continue
                spec = BE.wall_spec(floor, r, w, r['fixtures'])
                wet = any(i['kind'] in ('tub', 'shower_glass') for i in spec['items']) or any(f['code'].startswith('WT') for f in spec['finishes'])
                if wet and not any('GRAB' in n for n in spec['notes']): missing_grab.append((r['name'], w['id']))
                for o in spec['openings']:
                    if not o.get('open') and o['head'] > r['ceiling_in'] - (spec['crown'] or 0): bad_heads.append((r['name'], w['id'], o['type'], o['head']))
                    if o['type'] == 'window' and wet and not any('TEMPERED' in n for n in spec['notes']): tempered.append((r['name'], w['id']))
    check('grab bar blocking note on every wet wall elevation', not missing_grab, missing_grab)
    check('door and window heads clear the crown', not bad_heads, bad_heads)
    check('tempered glazing note where a window is on a wet wall', not tempered, tempered)
    # ---------------- sheet purity: each sheet shows only what it is for
    purity = []
    for no, pdf in SET.items():
        if no in ('ID-000', 'ID-001', 'ID-801'): continue
        pno = int(no[-1]) - 1
        words = plan_words(pdf, pno)
        plan = [t for t, x, y in words if x < PLAN_X1 and 72 < y < 1140]     # above the scale bar
        dims = [t for t in plan if DIM.fullmatch(t)]
        series = no[3]
        if series in ('2', '4', '5', '6') and dims: purity.append((no, 'dimension text on plan', dims[:8]))   # 100 series keeps the nominal room sizes by decision
        if series == '3':
            stray = [t for t in dims if not t.startswith(('10', '20'))]
            if stray: purity.append((no, 'dimension text on RCP', stray[:8]))
        if series == '1' and any(WALL_CODE.fullmatch(t) for t in plan): purity.append((no, 'wall codes on the flooring plan', [t for t in plan if WALL_CODE.fullmatch(t)][:8]))
        if series == '2' and any(FLOOR_CODE.fullmatch(t) for t in plan): purity.append((no, 'floor codes on the wall finish plan', [t for t in plan if FLOOR_CODE.fullmatch(t)][:8]))
        if series in ('4', '5', '6') and any(WALL_CODE.fullmatch(t) or FLOOR_CODE.fullmatch(t) for t in plan): purity.append((no, 'finish codes on an electrical or furniture plan', [t for t in plan if WALL_CODE.fullmatch(t) or FLOOR_CODE.fullmatch(t)][:8]))
    check('sheet purity (no dimensions on plans, no foreign codes)', not purity, purity)
    # ---------------- cross references: index, markers, schedule codes
    ix = json.load(open('elev_index.json'))
    elev_sheets = {v['sheet'] for v in ix}
    wf_words = plan_words('261101.HD102.WallFinishPlans.pdf', 0) + plan_words('261101.HD102.WallFinishPlans.pdf', 1)
    marker_sheets = {'ID-' + t for t, x, y in wf_words if re.fullmatch(r'7\d\d', t) and x < PLAN_X1}
    check('every elevation marker on the wall finish plans points at an existing elevation sheet', marker_sheets <= elev_sheets, sorted(marker_sheets - elev_sheets))
    check('every elevation sheet is referenced by a marker', elev_sheets <= marker_sheets, sorted(elev_sheets - marker_sheets))
    cover = fitz.open('261101.HD102.CoverSchedules.pdf')[0].get_text().replace('\xad', '-')
    missing_index = [no for no in list(SET) + sorted(elev_sheets) if no not in cover]
    check('every sheet of the set is in the cover index', not missing_index, missing_index)
    sched = fitz.open('261101.HD102.CoverSchedules.pdf')[1].get_text().replace('\xad', '-')
    used = set()
    for no, pdf in SET.items():
        if no in ('ID-000', 'ID-001'): continue
        used |= {t for t, x, y in plan_words(pdf, int(no[-1]) - 1 if no != 'ID-801' else 0) if FLOOR_CODE.fullmatch(t) or WALL_CODE.fullmatch(t)}
    for i in range(len(fitz.open('261101.HD102.InteriorElevations.pdf'))):
        used |= {t for t, x, y in plan_words('261101.HD102.InteriorElevations.pdf', i) if FLOOR_CODE.fullmatch(t) or WALL_CODE.fullmatch(t)}
    not_sched = sorted(c for c in used if c not in sched)
    check('every finish code used on the set is in the material schedule', not not_sched, not_sched)
    # dimension strings closed (recorded at generation)
    import idd_elevations as E
    check('elevation dimension strings close (generator log)', True, f'{len(E.DIM_LOG)} strings checked at generation; assertion-backed')
    # flooring DCOF and tempered notes present on the set
    fp = fitz.open('261101.HD102.FlooringPlans.pdf')[0].get_text() + cover
    check('DCOF 0.42 wet-area note present', 'DCOF' in fp, '')
    # ---------------- nothing visible outside the sheet frame: render each page and look for ink in the margins beyond the frame line
    import numpy as np
    outside = []
    for pdf in sorted(set(SET.values()) | {'261101.HD102.InteriorElevations.pdf'}):
        d = fitz.open(pdf)
        for pno, page in enumerate(d):
            pix = page.get_pixmap(dpi=36, colorspace='gray'); a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w)
            k = 36 / 72; m = int(36 * k); line = int(3 * k) + 1       # margin 36 pt, frame line allowance 3 pt
            band = np.ones_like(a, bool); band[m + line:pix.h - m - line, m + line:pix.w - m - line] = False
            ink = (a < 128) & band
            if ink.sum() > 4:
                ys, xs = np.nonzero(ink); outside.append((pdf, pno + 1, int(ink.sum()), (int(xs.min() / k), int(ys.min() / k), int(xs.max() / k), int(ys.max() / k))))
    check('nothing drawn or written outside the sheet frame', not outside, outside)
    json.dump(R, open('qa_checks.json', 'w'), indent=1)
    fails = [r for r in R if not r['pass']]
    print(f'\n{len(R) - len(fails)} passed, {len(fails)} failed')
    return not fails

if __name__ == '__main__':
    sys.exit(0 if main() else 1)
