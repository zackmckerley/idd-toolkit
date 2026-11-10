"""Dramatic marble slabs for the renderer, generated (owner 11.09.26 night: "make sure you have dramatic marbles with beautiful veins").

    python3 render/make_slab.py CODE [CODE ...]      writes render/assets/slabs/CODE/{Diffuse,Rough,nor_gl}.jpg

Why generated: the CC0 marble scans on hand are mild, small-repeat tiles, and the procedural shader drew veins as sub-pixel
hairlines that the lit counter washed out. A slab here is one full 126 x 63 in. slab at 32 px/in. (4032 x 2016): broad cloudy
movement, two or three bold primary veins that swell, split and fade (cores dark, halos soft), secondary veins branching off
them, hairline crazing, all domain-warped so nothing repeats in a pattern. Colors per code from SLABS below, from the owner's
picks and inspiration image. The renderer maps one slab at its true size (materials.json: kind stone, texture slabs/CODE,
size_in 126), so a counter shows the veining at the scale the fabricator would lay out.
These are stand-ins for the look of the stone. The selected slab's own photograph replaces it when the owner picks one."""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 4032, 2016

SLABS = {   # base (ground), cloud (soft movement), core (vein core), halo (vein haze), accent (gold/sage turn), seed, drama 0..1
    'CAL-MONET':   dict(base='#F3EEE6', cloud='#E3DBD0', core='#4E3F4C', halo='#9C8C98', accent='#A88752', seed=11, drama=0.9),
    'CAL-VIOLA':   dict(base='#F2EDE8', cloud='#DCCFCB', core='#4A2232', halo='#8E5A6C', accent='#6E4A55', seed=23, drama=1.0),
    'ST-03-INSPO': dict(base='#EFE6D8', cloud='#DCCDB8', core='#6B5543', halo='#A99078', accent='#B08E62', seed=37, drama=0.75),
}


def hexrgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def fbm(shape, rng, octaves=6, base=4.0, persistence=0.5):
    """Fractal value noise by bilinear-upsampled random grids (fast, tileable enough for one slab)."""
    h, w = shape; out = np.zeros(shape, np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        n = int(base * (2 ** o))
        g = rng.random((n + 1, int(n * w / h) + 1)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(im, np.float32) / 255.0); tot += amp; amp *= persistence
    return out / tot


def make(code):
    p = SLABS[code]; rng = np.random.default_rng(p['seed'])
    hs, ws = H // 2, W // 2                                   # built at half size, upsampled at the end (smooth veins)
    yy, xx = np.mgrid[0:hs, 0:ws].astype(np.float32); yy /= hs; xx /= hs
    base = hexrgb(p['base']); cloud = hexrgb(p['cloud']); core = hexrgb(p['core']); halo = hexrgb(p['halo']); acc = hexrgb(p['accent'])
    dr = p['drama']
    img = np.ones((hs, ws, 3), np.float32) * base
    cl = np.clip((fbm((hs, ws), rng, 5, 1.2) - 0.42) * 2.0, 0, 1)[..., None]   # soft cloudy movement in the ground
    img = img * (1 - 0.45 * cl) + cloud * (0.45 * cl)
    vein = np.zeros((hs, ws), np.float32); haze = np.zeros((hs, ws), np.float32); wash = np.zeros((hs, ws), np.float32)

    def family(angle, levels, warp, width, strength, seg=None, wash_k=0.0, wobble=0.05, rough=0.010, band=0.0):
        """Veins as flowing lines: isolines of a smooth warped gradient field (warp kept under the field's own slope, so no loops),
        swelling and thinning along their length, feathered rough edges, and for primaries a brecciated band of fragments
        between two close isolines. seg breaks a family into runs that start and stop."""
        nonlocal vein, haze, wash
        a = np.radians(angle)
        F = (xx * np.cos(a) + yy * np.sin(a) + warp * (fbm((hs, ws), rng, 3, 0.8) - 0.5)
             + wobble * (fbm((hs, ws), rng, 4, 2.2) - 0.5))
        edge = rough * (fbm((hs, ws), rng, 4, 24.0) - 0.5)                    # feathered, crystalline vein edges
        swell = 0.2 + 1.6 * np.clip(fbm((hs, ws), rng, 3, 1.4) - 0.3, 0, 1)
        runs = 1.0 if seg is None else np.clip((fbm((hs, ws), rng, 3, 1.3) - seg) * 6.0, 0, 1)
        for L in levels:
            d = np.abs(F + edge - L); w = width * swell
            c = np.clip(1.15 - d / np.maximum(w, 1e-5), 0, 1) ** 0.8 * strength * runs
            h = np.exp(-d / np.maximum(w * 6.0, 1e-5)) * strength * 0.65 * runs
            vein = np.maximum(vein, c); haze = np.maximum(haze, h)
            if wash_k: wash = np.maximum(wash, np.exp(-d / 0.12) * wash_k * runs)
            if band:                                                          # breccia: dark fragments between L and L + band
                inside = np.clip(1 - np.abs(F + edge - (L + band / 2)) / (band / 2), 0, 1)
                frag = np.clip((fbm((hs, ws), rng, 4, 10.0) - 0.52) * 7.0, 0, 1)
                vein = np.maximum(vein, inside * frag * strength * 0.9 * runs)

    span = (ws / hs) * 0.6 + 0.6
    prim = sorted(rng.uniform(0.2, span - 0.1, 3 if dr > 0.8 else 2))
    family(34, prim, 0.30, 0.032 * (0.6 + 0.8 * dr), 0.95, None, 0.6 * dr, band=0.09 * dr, rough=0.016)   # bold primaries: wide, smoky wash, breccia band
    family(36, [prim[0] + 0.06], 0.30, 0.012, 0.7, 0.45, 0.25 * dr, rough=0.01)                          # a companion vein riding the main one
    family(48, sorted(rng.uniform(0.0, span, 6)), 0.30, 0.0060, 0.8, 0.48, rough=0.006)       # secondaries in runs, branching off
    family(22, sorted(rng.uniform(0.0, span, 12)), 0.25, 0.0022, 0.5, 0.55, wobble=0.07, rough=0.004)   # hairlines and crazing
    img = img * (1 - wash[..., None] * 0.5) + halo * (wash[..., None] * 0.5)
    acc_w = np.clip((fbm((hs, ws), rng, 3, 1.0) - 0.5) * 3.0, 0, 1)[..., None]       # where a vein turns gold or sage along its length
    vcol = core * (1 - 0.55 * acc_w) + acc * (0.55 * acc_w)
    img = img * (1 - haze[..., None] * 0.55) + halo * (haze[..., None] * 0.55)
    vm = np.clip(vein, 0, 1)[..., None]
    img = img * (1 - vm) + vcol * vm
    grain = (fbm((hs, ws), rng, 2, 160.0) - 0.5) * 0.025                    # crystalline sparkle in the ground
    img = np.clip(img + grain[..., None], 0, 1)
    out = os.path.join(HERE, 'assets', 'slabs', code); os.makedirs(out, exist_ok=True)
    Image.fromarray((img * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).save(os.path.join(out, 'Diffuse.jpg'), quality=93)
    rough = np.clip(0.5 + 0.25 * vein - 0.1 * cl[..., 0], 0, 1)             # veins a touch duller than the polished ground
    Image.fromarray((rough * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).save(os.path.join(out, 'Rough.jpg'), quality=90)
    nrm = np.zeros((hs, ws, 3), np.float32); nrm[..., 0] = 0.5; nrm[..., 1] = 0.5; nrm[..., 2] = 1.0   # flat: polished stone
    Image.fromarray((nrm * 255).astype(np.uint8)).resize((W, H)).save(os.path.join(out, 'nor_gl.jpg'), quality=90)
    print('wrote', out)


if __name__ == '__main__':
    for c in sys.argv[1:] or SLABS: make(c)
