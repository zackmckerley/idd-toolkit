"""Automated QA checks for interior design drawing sheets (run before every delivery; all must pass).
Usage: python3 idd_qa.py survival ORIGINAL.pdf REVISED.pdf PAGE [PAGE ...]
       python3 idd_qa.py sheets FINAL.pdf            (two-way codes, overlaps, soft hyphens, em dashes, glyph boxes)
       python3 idd_qa.py cross FP.pdf WF.pdf ...      (room names and codes consistent across sheets)
"""
import re, sys, collections
import pymupdf as fitz

CODE = r'\b(?:WD|TL|ST|SL|PT|CM|WC|WP|WT|WS|BS|CP|CL|MT|GL|FB|MR|L)-\d\d\b'
PLAN_X1, LEG_X0, LEG_X1 = 780, 790, 1300

def survival(orig_pdf, rev_pdf, pages, dpi=110, out_prefix='survive'):
    """Red = dark in the original, gone in the revision. Every red cluster must be an intended removal."""
    import numpy as np
    from PIL import Image
    o, d = fitz.open(orig_pdf), fitz.open(rev_pdf); report = {}
    for pno in pages:
        po, pd = o[pno].get_pixmap(dpi=dpi, colorspace='gray'), d[pno].get_pixmap(dpi=dpi, colorspace='gray')
        a = np.frombuffer(po.samples, np.uint8).reshape(po.h, po.w).astype(int)
        b = np.frombuffer(pd.samples, np.uint8).reshape(pd.h, pd.w).astype(int)
        h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1]); a, b = a[:h, :w], b[:h, :w]
        lost = (a < 110) & (b > 200); gained = (a > 200) & (b < 110)
        rgb = np.stack([b, b, b], -1).astype(np.uint8); rgb[lost] = [220, 0, 0]; rgb[gained] = [0, 90, 220]
        Image.fromarray(rgb).save(f'{out_prefix}_p{pno}.png')
        # cluster the lost pixels on a coarse grid so each cluster can be accounted for
        g = 24; cl = collections.Counter()
        ys, xs = np.nonzero(lost)
        for y, x in zip(ys, xs): cl[(x // g, y // g)] += 1
        clusters = sorted(((k[0] * g * 72 / dpi, k[1] * g * 72 / dpi, n) for k, n in cl.items() if n > 12), key=lambda t: -t[2])
        report[pno] = {'lost_px': int(lost.sum()), 'gained_px': int(gained.sum()), 'lost_clusters_pt': [(round(x), round(y), n) for x, y, n in clusters[:40]]}
    return report

def two_way_codes(page):
    words = page.get_text('words')
    tags = [(w[4].replace('\xad', '-'), w[0], w[1]) for w in words if re.fullmatch(CODE, w[4].replace('\xad', '-'))]
    plan = collections.Counter(t for t, x, y in tags if x < PLAN_X1)
    legend = set(t for t, x, y in tags if LEG_X0 <= x < LEG_X1)
    return {'plan': dict(plan), 'legend': sorted(legend), 'on_plan_not_in_legend': sorted(set(plan) - legend),
            'in_legend_not_on_plan': sorted(legend - set(plan))}

def code_category_clash(pages):
    """The same code must name one material across every schedule: compare the legend-row title that follows each
    bold code in the legend column (x in the legend range, title text on the same line)."""
    seen = {}; clashes = []
    for pg in pages:
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                spans = [s for s in l['spans'] if s['text'].strip()]
                if not spans or not (LEG_X0 <= spans[0]['bbox'][0] < LEG_X0 + 120): continue
                code = spans[0]['text'].strip().replace('\xad', '-')
                if re.fullmatch(CODE, code) and len(spans) > 1:
                    title = ' '.join(s['text'].strip() for s in spans[1:])[:24]
                    if code in seen and seen[code] != title: clashes.append((code, seen[code], title))
                    seen.setdefault(code, title)
    return clashes

def overlaps(page, min_area=4.0):
    """Text spans whose boxes intersect other text spans (labels on labels, tags on dimensions)."""
    spans = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                if s['text'].strip(): spans.append((fitz.Rect(s['bbox']), s['text'].strip()))
    out = []
    for i in range(len(spans)):
        for j in range(i + 1, len(spans)):
            r = spans[i][0] & spans[j][0]
            if not r.is_empty and r.height > 2.0 and r.width > 2.0 and r.get_area() > min_area and spans[i][1] != spans[j][1]:
                out.append((spans[i][1], spans[j][1], [round(v) for v in r]))
    return out

def text_hygiene(page):
    t = page.get_text()
    return {'soft_hyphens': t.count('\xad'), 'em_dashes': t.count('\u2014'), 'double_hyphens': t.count('--'),
            'replacement_glyphs': t.count('�') + t.count('▯')}

def room_names(page):
    names = set()
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                t = s['text'].strip()
                if t.isupper() and 3 <= len(t) <= 18 and s['size'] > 8.5 and s['bbox'][0] < PLAN_X1 and not re.search(r'\d', t): names.add(t)
    return names

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'survival':
        rep = survival(sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4:]])
        for k, v in rep.items(): print('page', k, v)
    elif cmd == 'sheets':
        d = fitz.open(sys.argv[2])
        for i, p in enumerate(d):
            print(f'--- sheet {i + 1}')
            print('codes', two_way_codes(p)); print('hygiene', text_hygiene(p)); ov = overlaps(p); print('overlaps', len(ov), ov[:12])
        print('code clashes', code_category_clash(list(d)))
    elif cmd == 'cross':
        docs = [fitz.open(f) for f in sys.argv[2:]]
        per_floor = collections.defaultdict(list)
        for f, d in zip(sys.argv[2:], docs):
            for i, p in enumerate(d): per_floor[i].append((f, room_names(p)))
        for fl, items in per_floor.items():
            allnames = set().union(*[n for _, n in items])
            for f, n in items:
                missing = allnames - n
                print(f'floor sheet {fl + 1}: {f}: missing room names vs other sheets: {sorted(missing)}')
