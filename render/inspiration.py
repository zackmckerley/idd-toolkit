"""Inspiration image read: palette, paint candidates, and the record the design read fills in.
    python3 render/inspiration.py IMAGE OUT_PREFIX [--neutral x,y,w,h [--neutral-is HEX]] [--k 8] [--source "URL or publication"]

What it does (method from the research notes in the skill):
1. White balance. With --neutral (a patch of white trim, ceiling or porcelain in the photo, in image pixels) the image is
   scaled in linear RGB so that patch reads neutral. Without it, the brightest near-neutral pixels are used and the
   correction is flagged AUTO (weaker). The read always says which.
2. Resize with nearest-neighbour (smooth resampling invents colors), convert to CIELAB, drop the darkest and brightest
   7% of lightness (shadows and highlights are not the paint).
3. k-means in CIELAB with lightness weighted x2, 10 restarts, k clusters; clusters closer than dE00 3 are merged.
   Each color gets its share of the image and a spread (median dE00 of its pixels to the center): the confidence.
4. Paint candidates: the top 3 Sherwin-Williams and top 3 Benjamin Moore colors by CIEDE2000 (colour-science), from
   render/paint/*.json plus the sourced supplement. LRV is the maker's where known, else estimated from luminance
   and marked EST. Never one "match": a photo is not a paint chip.
Outputs OUT_PREFIX.json (everything above plus empty fields for the design read: style, materials, trim and panel
language, metals, lighting color temperature, which the analyst fills in from looking at the image) and OUT_PREFIX.png
(a swatch strip with the candidates) for the options deck. The image itself is reference only: it goes in the
client-only options deck with its source caption, never in the drawing set."""
import json, os, sys
import numpy as np
from PIL import Image
import colour

HERE = os.path.dirname(os.path.abspath(__file__))


def srgb_to_lab(rgb01):
    xyz = colour.sRGB_to_XYZ(rgb01)
    return colour.XYZ_to_Lab(xyz)


def hex_to_rgb01(h):
    h = h.strip().lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


def lab_to_hex(lab):
    rgb = np.clip(colour.XYZ_to_sRGB(colour.Lab_to_XYZ(lab)), 0, 1)
    return '#%02X%02X%02X' % tuple(int(round(c * 255)) for c in rgb)


def load_paints():
    out = []
    for fn, brand in (('sherwin-williams.json', 'SW'), ('benjamin-moore.json', 'BM')):
        for c in json.load(open(os.path.join(HERE, 'paint', fn))):
            lab = srgb_to_lab(hex_to_rgb01(c['hex']))
            label = ('SW %04d' % c['label']) if brand == 'SW' and isinstance(c['label'], int) else str(c['label'])
            if brand == 'BM': label = 'BM ' + label
            out.append({'brand': brand, 'label': label, 'name': c['name'], 'hex': c['hex'].strip().upper(), 'lab': lab, 'lrv': None, 'source': 'colornerd 2.4.11 (2022)' + ('; BM names in this dataset are cut to one word: confirm the full name' if brand == 'BM' else '')})
    seen = set(); uniq = []
    for p in out:
        if (p['brand'], p['label']) not in seen: seen.add((p['brand'], p['label'])); uniq.append(p)
    out = uniq
    sup = json.load(open(os.path.join(HERE, 'paint', 'supplement.json')))['colors']
    keys = {(p['brand'], p['label']) for p in out}
    for c in sup:
        rec = dict(c)
        if c['brand'] == 'BM' and not c['label'].startswith('BM '): rec['label'] = c['label'] = 'BM ' + c['label']
        rec['lab'] = srgb_to_lab(hex_to_rgb01(c['hex']))
        if (c['brand'], c['label']) in keys:
            for p in out:
                if (p['brand'], p['label']) == (c['brand'], c['label']): p.update({k: v for k, v in rec.items() if v is not None})
        else: out.append(rec)
    return out


def est_lrv(hexv):
    """LRV estimated as the CIE Y of the sRGB color (0-100). The maker's published LRV governs; this only flags a gross mismatch."""
    return float(colour.sRGB_to_XYZ(hex_to_rgb01(hexv))[1] * 100)


def white_balance(img, neutral=None, ref_hex=None):
    a = np.asarray(img).astype(np.float64) / 255.0
    lin = colour.cctf_decoding(a, function='sRGB')
    if neutral:
        x, y, w, h = neutral; ref = np.median(lin[y:y + h, x:x + w].reshape(-1, 3), axis=0); mode = 'PATCH'
        if ref_hex:   # the patch is a known color (the trim white is SW 7005): balance to it, not to grey
            tgt = colour.cctf_decoding(hex_to_rgb01(ref_hex), function='sRGB')
            gain = (tgt / tgt.mean()) / np.maximum(ref / ref.mean(), 1e-4)
            return colour.cctf_encoding(np.clip(lin * gain, 0, 1), function='sRGB'), 'PATCH = ' + ref_hex
    else:
        flat = lin.reshape(-1, 3); lum = flat.mean(1); chroma = flat.max(1) - flat.min(1)
        cand = flat[(lum > np.percentile(lum, 90)) & (chroma < 0.08)]
        if len(cand) < 50: return a, 'NONE (no neutral found)'
        ref = np.median(cand, axis=0); mode = 'AUTO (brightest near-neutral pixels)'
    gain = ref.mean() / np.maximum(ref, 1e-4)
    lin2 = np.clip(lin * gain, 0, 1)
    return colour.cctf_encoding(lin2, function='sRGB'), mode


def palette(rgb01, k=8, seed=0):
    """k-means on every pixel (the brightest color is often the trim, so nothing is cut before clustering); inside each
    cluster the darkest and brightest 10% of lightness are dropped (shadow and highlight) and the median taken.
    Clusters under dE00 3 are merged. Clusters that differ mostly in lightness (dE00 with kL=2 under 3) are NOT merged,
    because a white trim against a light grey wall differs in exactly that way; they are flagged as possibly one surface
    in light and shade, for the analyst to settle by looking at the image."""
    from sklearn.cluster import KMeans
    lab = srgb_to_lab(rgb01.reshape(-1, 3))
    feat = lab * np.array([2.0, 1.0, 1.0])                # lightness weighted x2
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(feat)
    groups = [lab[km.labels_ == i] for i in range(k) if (km.labels_ == i).any()]
    def center(m):
        L = m[:, 0]; keep = m[(L >= np.percentile(L, 10)) & (L <= np.percentile(L, 90))]
        return np.median(keep if len(keep) else m, axis=0)
    groups.sort(key=lambda m: -len(m)); merged = []
    for m in groups:
        c = center(m)
        hit = next((g for g in merged if colour.delta_E(center(g), c, method='CIE 2000') < 3.0), None)
        if hit is not None:
            i = next(j for j, g in enumerate(merged) if g is hit); merged[i] = np.vstack([hit, m])
        else: merged.append(m)
    out = []
    for m in merged:
        c = center(m)
        spread = float(np.median(colour.delta_E(m, c, method='CIE 2000', textiles=True)))
        L = m[:, 0]; lit = m[L >= np.median(L)]
        out.append({'lab': c, 'lab_lit': np.median(lit, axis=0), 'share': len(m) / len(lab), 'spread': spread})
    for i, a in enumerate(out):
        a['maybe_same_surface_as'] = [j for j, b in enumerate(out) if j != i and colour.delta_E(a['lab'], b['lab'], method='CIE 2000', textiles=True) < 3.0]
    return out


def candidates(lab, paints, n=3, textiles=False):
    labs = np.array([p['lab'] for p in paints]); d = colour.delta_E(labs, lab, method='CIE 2000', textiles=textiles)
    out = {}
    for brand in ('SW', 'BM'):
        idx = [i for i in np.argsort(d) if paints[i]['brand'] == brand][:n]
        out[brand] = [{'label': paints[i]['label'], 'name': paints[i]['name'], 'hex': paints[i]['hex'], 'dE00': round(float(d[i]), 2),
                       'lrv': paints[i]['lrv'] if paints[i].get('lrv') else round(est_lrv(paints[i]['hex']), 1),
                       'lrv_kind': 'MAKER' if paints[i].get('lrv') else 'EST', 'source': paints[i].get('source')} for i in idx]
    return out


def confidence(spread, best_de):
    if spread <= 3 and best_de <= 2: return 'GOOD: sample the top candidates'
    if spread <= 5 and best_de <= 3.5: return 'FAIR: candidates are a starting point, sample before choosing'
    return 'INDICATIVE ONLY: the photo color is unreliable (lighting, shade or texture); choose from samples'


def main():
    a = sys.argv[1:]
    img_path, prefix = a[0], a[1]
    k = int(a[a.index('--k') + 1]) if '--k' in a else 8
    neutral = tuple(int(v) for v in a[a.index('--neutral') + 1].split(',')) if '--neutral' in a else None
    src = a[a.index('--source') + 1] if '--source' in a else 'NOT GIVEN'
    ref_hex = a[a.index('--neutral-is') + 1] if '--neutral-is' in a else None
    im = Image.open(img_path).convert('RGB')
    s = 320 / max(im.size)
    if s < 1: im = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.NEAREST)
    if neutral and s < 1: neutral = tuple(int(v * s) for v in neutral)
    rgb, wb = white_balance(im, neutral, ref_hex)
    pal = palette(rgb, k)
    paints = load_paints()
    rows = []
    for c in pal:
        cand = candidates(c['lab'], paints)
        fam = candidates(c['lab_lit'], paints, textiles=True)   # same hue and chroma, lightness weighted half: the photo's exposure is unknown
        best = min(cand['SW'][0]['dE00'], cand['BM'][0]['dE00'])
        rows.append({'photo_hex': lab_to_hex(c['lab']), 'lab': [round(float(v), 2) for v in c['lab']], 'share': round(c['share'], 3),
                     'spread_dE00': round(c['spread'], 2), 'est_lrv': round(est_lrv(lab_to_hex(c['lab'])), 1),
                     'confidence': confidence(c['spread'], best), 'maybe_same_surface_as': c['maybe_same_surface_as'],
                     'candidates': cand, 'family_candidates': fam})
    read = {'image': os.path.basename(img_path), 'source': src, 'white_balance': wb, 'k': k, 'palette': rows,
            'candidates_note': 'candidates = closest at the photo lightness (dE00); family_candidates = closest in hue and chroma with lightness weighted half (dE00 kL=2), because a photo cannot fix how light a wall is',
            'proportions_note': 'shares are of the whole photo (walls, floor, furniture and props), not a 60-30-10 spec',
            'design_read': {'style': '', 'era': '', 'palette_roles': {'dominant': '', 'secondary': '', 'accent': ''}, 'undertones': '',
                            'sheens': '', 'materials': {'wood': '', 'stone': '', 'tile': '', 'metal': '', 'fabric': ''},
                            'trim': {'base_ratio_of_ceiling': None, 'crown': '', 'casing': '', 'chair_rail_or_cap_ratio': None},
                            'paneling': {'type': '', 'layout': '', 'stile_to_panel': None}, 'millwork': '', 'hardware': '', 'lighting_cct_K': None,
                            'pattern_scale': '', 'what_not_to_copy': ''}}
    json.dump(read, open(prefix + '.json', 'w'), indent=1)
    # swatch strip
    W, rowh = 1400, 120
    strip = Image.new('RGB', (W, rowh * len(rows) + 10), 'white')
    from PIL import ImageDraw
    dr = ImageDraw.Draw(strip)
    for i, r in enumerate(rows):
        y = 5 + i * rowh
        dr.rectangle([10, y, 150, y + rowh - 10], fill=r['photo_hex']); dr.text((14, y + rowh - 26), 'PHOTO %s %d%%' % (r['photo_hex'], round(r['share'] * 100)), fill='black')
        x = 170
        for brand in ('SW', 'BM'):
            for c in r['candidates'][brand]:
                dr.rectangle([x, y, x + 130, y + 70], fill=c['hex']); dr.text((x, y + 74), '%s %s' % (c['label'], c['name'][:16]), fill='black')
                dr.text((x, y + 88), 'dE %.1f  LRV %s%s' % (c['dE00'], c['lrv'], '' if c['lrv_kind'] == 'MAKER' else ' est'), fill='black'); x += 140
            x += 20
    strip.save(prefix + '.png')
    print('palette', len(rows), 'white balance', wb, '->', prefix + '.json')


if __name__ == '__main__':
    main()
