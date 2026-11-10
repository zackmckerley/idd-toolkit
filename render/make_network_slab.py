"""Photoreal fracture-network marble (Calacatta Viola / Arabescato / Breccia type) for the renderer.

    python3 render/make_network_slab.py CODE [--preview]     writes render/assets/slabs/CODE/{Diffuse,Rough,nor_gl}.jpg

Why (owner 11.10.26, with reference photos: "do you see how the style of stone in these images is really detailed and realistic.
why cant you do that on mine"): the first generator drew a few smooth vein lines on a flat ground. Real stone carries detail at
every scale at once, and this generator builds each scale separately:
  - ground: cream with broad cloudy movement, a mid-scale mottle and a crystalline grain at about 1/10 in., calcite sparkle;
  - clasts: the slab is broken into fragments by a domain-warped Voronoi fracture network at two scales (large clasts 8 to 16 in.,
    and dense fine crackle in clusters, as in a brecciated zone), with some boundaries healed so it never reads as a honeycomb;
  - veins: width swells and pinches along each fracture, a near-black brown core, a greyer halo bleeding into the ground,
    gold-brown iron staining along some runs, hairline crazing inside the clasts;
  - surface maps: veins a little rougher than the polished ground, a faint normal from the grain.
One full 126 x 63 in. slab at 32 px/in. (4032 x 2016), mapped at true size (materials.json: kind stone, texture slabs/CODE,
size_in 126). A stand-in for the look of the stone until the selected slab is photographed: the photograph then replaces it."""
import os, sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
PX_IN = 32.0

SLABS = {   # ground, cloud, core, halo, gold; seed; clast size (in.); crackle share 0..1; vein weight
    # owner 11.10.26: the kitchen inspiration marble, cream with bold black-brown network veins and gold
    'ST-03-INSPO': dict(ground='#EDE6DB', cloud='#E0D5C6', core='#1E1A17', halo='#6E6258', gold='#9C7A45', seed=41,
                        clast=13.0, crackle=0.55, weight=1.0),
}


def hexrgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def fbm(shape, rng, octaves, cells, persistence=0.5):
    """Fractal value noise; `cells` = grid cells across the short side at the first octave."""
    h, w = shape; out = np.zeros(shape, np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        n = max(2, int(cells * (2 ** o)))
        g = rng.random((n + 1, int(n * w / h) + 2)).astype(np.float32)
        im = Image.fromarray(g, mode='F').resize((w, h), Image.BICUBIC)
        out += amp * np.asarray(im, np.float32); tot += amp; amp *= persistence
    return out / tot


def network(shape, rng, cell_px, warp_px, heal, wvar, wob_px=0.0, fallback=True):
    """Distance to the nearest kept Voronoi boundary (pixels) on domain-warped coordinates, and a per-boundary width factor."""
    h, w = shape
    n = int(h * w / cell_px ** 2 * 1.15) + 8
    pts = rng.random((n, 2)) * [h + 2 * cell_px, w + 2 * cell_px] - cell_px
    tree = cKDTree(pts)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    wy = (fbm(shape, rng, 4, h / (cell_px * 2.2)) - 0.5) * 2 * warp_px
    wx = (fbm(shape, rng, 4, h / (cell_px * 2.2)) - 0.5) * 2 * warp_px
    if wob_px:   # a short-wave wobble on top: real fractures wander at every scale, Voronoi edges are straight
        wy = wy + (fbm(shape, rng, 3, h / (cell_px * 0.3)) - 0.5) * 2 * wob_px
        wx = wx + (fbm(shape, rng, 3, h / (cell_px * 0.3)) - 0.5) * 2 * wob_px
    q = np.stack([(yy + wy).ravel(), (xx + wx).ravel()], 1)
    d, i = tree.query(q, k=3, workers=-1)
    d1, d2, d3 = d[:, 0], d[:, 1], d[:, 2]
    i1, i2, i3 = i[:, 0], i[:, 1], i[:, 2]
    lo, hi = np.minimum(i1, i2), np.maximum(i1, i2)
    hsh = np.modf(np.sin(lo * 12.9898 + hi * 78.233) * 43758.5453)[0]
    hsh = np.abs(hsh)
    keep = hsh > heal                                             # healed boundaries: clasts merge, the net stays irregular
    width = 0.35 + wvar * np.abs(np.modf(np.sin(lo * 3.17 + hi * 9.71) * 9631.7)[0])   # each fracture its own weight
    edge = (d2 - d1) * 0.5                                        # distance to the bisector (pixels)
    # where the nearest boundary is healed, fall back to the next one (cell 1 against cell 3)
    lo3, hi3 = np.minimum(i1, i3), np.maximum(i1, i3)
    k3 = np.abs(np.modf(np.sin(lo3 * 12.9898 + hi3 * 78.233) * 43758.5453)[0]) > heal
    edge3 = (d3 - d1) * 0.5
    w3 = 0.35 + wvar * np.abs(np.modf(np.sin(lo3 * 3.17 + hi3 * 9.71) * 9631.7)[0])
    e = np.where(keep, edge, np.where(k3 & fallback, edge3, 1e6)); wf = np.where(keep, width, w3)   # no fallback: a healed edge simply stops
    return e.reshape(shape).astype(np.float32), wf.reshape(shape).astype(np.float32)


def make(code, preview=False):
    p = SLABS[code]; rng = np.random.default_rng(p['seed'])
    W, H = (int(126 * PX_IN), int(63 * PX_IN))
    if preview: W, H = W // 2, H // 2
    s = W / 4032.0                                                # pixel scale against the full slab
    shape = (H, W)
    ground = hexrgb(p['ground']); cloud = hexrgb(p['cloud']); core = hexrgb(p['core']); halo = hexrgb(p['halo']); gold = hexrgb(p['gold'])
    # ---- the ground: broad clouds, a mid mottle, grain and sparkle
    cl = np.clip((fbm(shape, rng, 5, 1.6) - 0.40) * 1.8, 0, 1)
    mot = fbm(shape, rng, 4, 14.0) - 0.5
    grain = gaussian_filter(rng.standard_normal(shape).astype(np.float32), 1.2 * s)
    img = ground[None, None] * (1 - 0.55 * cl[..., None]) + cloud[None, None] * (0.55 * cl[..., None])
    img *= (1 + 0.05 * mot[..., None] + 0.035 * grain[..., None] / (grain.std() + 1e-6) * 0.5)
    # ---- the fracture network at three scales: big clasts, medium breakup in places, dense crackle in clusters
    big_px = p['clast'] * PX_IN * s
    jit = (fbm(shape, rng, 3, 60.0) - 0.5) * 2.2 * s                       # ragged, crystalline vein edges
    e1, w1 = network(shape, rng, big_px, big_px * 0.55, heal=0.22, wvar=2.2)
    e2, w2 = network(shape, rng, big_px * 0.45, big_px * 0.30, heal=0.35, wvar=1.6)
    e3, w3 = network(shape, rng, big_px * 0.16, big_px * 0.10, heal=0.30, wvar=1.0)
    zone2 = np.clip((fbm(shape, rng, 3, 1.1) - 0.45) * 3.0, 0, 1)                                  # medium breakup in about half the slab
    zone3 = np.clip((fbm(shape, rng, 3, 1.4) - (0.66 - 0.2 * p['crackle'])) * 4.0, 0, 1)            # dense crackle in clusters
    swell = 0.25 + 1.6 * fbm(shape, rng, 4, 2.5) ** 2.0                                              # swells and pinches along runs
    vw1 = (PX_IN * s * 0.11) * w1 * swell * p['weight']           # 1/8 in. typical, past 1/2 in. at a swell
    vw2 = (PX_IN * s * 0.08) * w2 * swell * zone2
    vw3 = (PX_IN * s * 0.05) * w3 * (0.5 + swell) * zone3
    def core_of(e, vw, lo):
        e_ = np.abs(e + jit)
        c = np.clip(1.2 - e_ / np.maximum(vw, lo), 0, 1)
        # a second strand beside the main one where the vein is wide: the spidery bundles of a real fracture
        c2 = np.clip(1.0 - np.abs(e_ - 2.6 * vw) / np.maximum(0.35 * vw, lo), 0, 1) * (vw > 2.5 * s)
        return np.clip(np.maximum(c, 0.8 * c2), 0, 1) * (vw > 0.15)
    core1 = core_of(e1, vw1, 0.4); core2 = core_of(e2, vw2, 0.35); core3 = core_of(e3, vw3, 0.3)
    halo1 = np.exp(-np.abs(e1 + jit) / np.maximum(vw1 * 1.6, 0.8)) * (vw1 > 0.3)
    halo2 = np.exp(-np.abs(e2 + jit) / np.maximum(vw2 * 1.4, 0.6)) * (vw2 > 0.2)
    stain = np.clip((fbm(shape, rng, 4, 3.0) - 0.52) * 3.5, 0, 1)
    goldm = np.clip(np.maximum(halo1, halo2) * stain * 1.3, 0, 1)
    # ---- composite: a tight grey halo, gold-brown iron staining, then the cores (broken by grain so they read crystalline)
    hal = np.clip(0.5 * halo1 + 0.35 * halo2, 0, 1)[..., None]
    img = img * (1 - 0.35 * hal) + halo[None, None] * (0.35 * hal)
    img = img * (1 - 0.6 * goldm[..., None]) + gold[None, None] * (0.6 * goldm[..., None])
    brk = np.clip(0.8 + 0.45 * grain / (grain.std() + 1e-6), 0.4, 1.0)
    cor = np.clip(np.maximum.reduce([core1, 0.9 * core2, 0.8 * core3]) * brk, 0, 1)[..., None]
    coretone = core[None, None] * (1 - 0.5 * stain[..., None]) + gold[None, None] * 0.55 * (0.5 * stain[..., None])   # some cores run brown-gold
    img = img * (1 - cor) + coretone * cor
    img = np.clip(img, 0, 1)
    out = os.path.join(HERE, 'assets', 'slabs', code + ('_preview' if preview else '')); os.makedirs(out, exist_ok=True)
    Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(out, 'Diffuse.jpg'), quality=93)
    # rough: polished ground about 0.18, veins and stains a little rougher
    rough = np.clip(0.35 + 0.35 * cor[..., 0] + 0.15 * goldm + 0.05 * grain / (grain.std() + 1e-6), 0, 1)
    Image.fromarray((rough * 255).astype(np.uint8)).save(os.path.join(out, 'Rough.jpg'), quality=90)
    hgt = gaussian_filter(grain, 1.0) * 0.6 - cor[..., 0] * 0.4
    gy, gx = np.gradient(hgt)
    nrm = np.stack([-gx * 0.6, gy * 0.6, np.ones_like(gx)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(out, 'nor_gl.jpg'), quality=90)
    print('wrote', out, img.shape)




# ================================================================== photographed vein network (preferred)
# The generated net above still reads drawn at full size. A real stone photograph carries the jagged, spotted, bleeding vein edges
# no generator gets right, so the preferred slab is built from a CC0 photo scan of a network marble (ambientCG Marble023, a dark
# stone with a white vein net, 4K), inverted so its net is dark on a light ground, cleaned of the speckle that reads as dirt,
# recolored to the picked palette, set at a clast size like the owner's reference (8 to 14 in.), and book-matched across the slab
# (the left half mirrored to the right, as a fabricator lays two consecutive slabs).
PHOTO = {   # scan, the scan's width in inches on the slab, palette
    'ST-03-INSPO': dict(scan='Marble023', scan_in=126.0, ground='#EEE7DC', cloud='#DED3C3', core='#1C1815', mid='#5E544C', gold='#A07C46', seed=41),
}


def make_photo(code, preview=False):
    from scipy import ndimage as ndi
    p = PHOTO[code]; rng = np.random.default_rng(p['seed'])
    W, H = (int(126 * PX_IN), int(63 * PX_IN))
    if preview: W, H = W // 2, H // 2
    s = W / 4032.0
    src = Image.open(os.path.join(HERE, 'assets', 'scans', p['scan'], p['scan'] + '_4K-JPG_Color.jpg')).convert('L')
    tpx = int(p['scan_in'] * PX_IN * s)                                     # the scan's width on the slab, in pixels
    tile = np.asarray(src.resize((tpx, tpx), Image.LANCZOS), np.float32) / 255.0
    half = W if tpx >= W else W // 2
    reps = int(np.ceil(half / tpx)) + 1; rows = int(np.ceil(H / tpx)) + 1
    big = np.tile(tile, (rows, reps))[:H, :half]
    L = 1.0 - big                                                           # inverted: the white net becomes the dark vein net
    L = (L - np.percentile(L, 1)) / (np.percentile(L, 99.5) - np.percentile(L, 1) + 1e-6)
    v = np.clip((0.80 - L) / 0.62, 0, 1)                                   # vein darkness
    # clean the speckle: keep vein bodies that are part of a run, fade isolated dots to a faint fleck
    m = v > 0.42
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, index=np.arange(1, n + 1))
    keep = np.zeros(n + 1, bool); keep[1:] = sizes > (900 * s * s)
    body = ndi.binary_dilation(keep[lab], iterations=max(1, int(2 * s)))
    v = np.where(body, v, v * 0.06)
    v = ndi.gaussian_filter(v, 0.6 * s)
    # bolder primaries: where the net is dense, thicken a little (the reference's veins read at arm's length)
    dens = ndi.gaussian_filter(v, 14 * s)
    v = np.clip(v * (1.0 + 1.1 * np.clip(dens * 3.0 - 0.15, 0, 1)), 0, 1)
    halo = np.clip(ndi.gaussian_filter(v, 4.0 * s) * 1.6, 0, 1)
    shape = v.shape
    ground = hexrgb(p['ground']); cloud = hexrgb(p['cloud']); core = hexrgb(p['core']); mid = hexrgb(p['mid']); gold = hexrgb(p['gold'])
    cl = np.clip((fbm(shape, rng, 5, 1.4) - 0.42) * 1.6, 0, 1)
    gl = np.clip(L, 0, 1)                                                   # the scan's own ground texture, kept faint
    img = ground[None, None] * (1 - 0.5 * cl[..., None]) + cloud[None, None] * (0.5 * cl[..., None])
    img *= (0.965 + 0.045 * gl[..., None])
    stain = np.clip((fbm(shape, rng, 4, 2.2) - 0.40) * 3.0, 0, 1)
    # (the scan's own vein halos and stains are not used: at slab size they read as blotches)
    # the clast structure of the reference: a dense, wandering fracture net at three scales (9 in. clasts, 4 in. breakup over most
    # of the slab, 1-3/4 in. crackle in clusters), thin charcoal veins with a soft brown edge; the scan contributes only its hairlines
    vsc = np.clip(v - 0.55, 0, 1) * 0.6 * (1 - body) + np.where(body, np.clip(v, 0, 1) * 0.0, 0)   # scan blobs dropped (read as ink)
    nets = []
    for cell_in, heal_, zone_t, wmin, wmax, wob in ((9.0, 0.30, None, 0.11, 0.24, 0.10), (4.0, 0.22, 0.34, 0.07, 0.14, 0.12), (1.75, 0.18, 0.58, 0.04, 0.075, 0.14)):
        cp_ = cell_in * PX_IN * s
        e_, w_ = network(shape, rng, cp_, cp_ * 0.55, heal=heal_, wvar=1.0, wob_px=cp_ * wob, fallback=False)
        zone = np.ones(shape, np.float32) if zone_t is None else np.clip((fbm(shape, rng, 3, 1.2) - zone_t) * 3.5, 0, 1)
        sw = 0.6 + 0.8 * fbm(shape, rng, 3, 4.0)
        vw = np.minimum(PX_IN * s * (wmin + (wmax - wmin) * np.clip(w_ - 0.35, 0, 1)) * sw, PX_IN * s * wmax * 1.15) * zone
        c_ = np.clip(0.5 + (vw * 0.5 - np.abs(e_)) / (0.9 * max(s, 0.5)), 0, 1) * (vw > 0.25)   # crisp, antialiased edges: a soft ramp read as a smudge
        h_ = np.exp(-np.abs(e_) / np.maximum(vw * 1.4, 0.6)) * (vw > 0.25)
        nets.append((c_, h_))
    net = np.maximum.reduce([c_ for c_, _ in nets]); nh = np.maximum.reduce([h_ for _, h_ in nets])
    img = img * (1 - 0.14 * nh[..., None]) + mid[None, None] * (0.14 * nh[..., None])
    gm2 = (nh * stain)[..., None]
    img = img * (1 - 0.40 * gm2) + gold[None, None] * (0.40 * gm2)   # gold-brown iron staining along some veins
    v = np.clip(np.maximum(net, vsc), 0, 1)
    vc = np.clip(v, 0, 1)[..., None]
    k_ = np.clip((vc - 0.25) / 0.4, 0, 1)                                    # vein edges warm grey-brown and gold, cores near black
    edge_tone = mid[None, None] * (1 - 0.45 * stain[..., None]) + gold[None, None] * (0.45 * stain[..., None])
    tone = edge_tone * (1 - k_) + core[None, None] * k_
    a_ = np.clip(vc * 1.05, 0, 0.93)                                       # never a flat ink black: the grain shows through
    img = np.clip(img * (1 - a_) + tone * a_, 0, 1)
    full = img if img.shape[1] >= W else np.concatenate([img, img[:, ::-1]], 1)[:, :W]   # one scan across the slab; book-match only when it is narrower
    out = os.path.join(HERE, 'assets', 'slabs', code + ('_preview' if preview else '')); os.makedirs(out, exist_ok=True)
    Image.fromarray((full * 255).astype(np.uint8)).save(os.path.join(out, 'Diffuse.jpg'), quality=93)
    vv = v if v.shape[1] >= W else np.concatenate([v, v[:, ::-1]], 1)[:, :W]
    rough = np.clip(0.30 + 0.30 * vv + 0.05 * rng.standard_normal(vv.shape).astype(np.float32), 0, 1)
    Image.fromarray((rough * 255).astype(np.uint8)).save(os.path.join(out, 'Rough.jpg'), quality=90)
    hgt = ndi.gaussian_filter(-vv * 0.5, 1.0)
    gy, gx = np.gradient(hgt)
    nrm = np.stack([-gx, gy, np.ones_like(gx)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(out, 'nor_gl.jpg'), quality=90)
    print('wrote', out, full.shape)


if __name__ == '__main__':
    pv = '--preview' in sys.argv
    for c in [a for a in sys.argv[1:] if not a.startswith('--')]:
        (make if '--generated' in sys.argv else make_photo)(c, pv)
