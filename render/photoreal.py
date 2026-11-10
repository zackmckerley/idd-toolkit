"""Photoreal rendered elevation of one captured view (Blender 4.2, Cycles CPU, the bpy venv):
    /home/claude/rendervenv/bin/python render/photoreal.py views.json INDEX out.png [--samples 256] [--ppi auto] [--preview]

What makes it read as a photograph and not a coloured drawing:
- Real objects, not extruded linework. Every component call the generator made (render/idd_capture.py records it with
  its arguments) is rebuilt in 3-D by a builder below: trim is a swept profile with mitred corners, doors have stiles,
  rails, recessed panels and sticking, a vanity has a carcass, inset drawers with reveals, a stone top, pulls and a
  wall faucet, a mirror is real silvered glass in a moulded frame, a sconce is a lit glass cylinder. Components with no
  builder fall back to the captured primitives, extruded (and the run lists them, so the gap is visible).
- Softened edges everywhere (Cycles bevel shader), so nothing has the knife edge of a CG box.
- Measured materials: paint at its maker's colour with a faint drywall texture, CC0 scanned textures from Poly Haven for
  wood and stone (render/assets, real-world size), metals from measured reflectance with their edge tint.
- A room, not a wall: side walls, floor, ceiling and the facing wall exist (the orthographic camera sees them edge on),
  so light bounces, corners darken, and the mirrors reflect the room. Daylight comes from a window behind the viewer,
  the sconces are on (2700 K), and an interior HDRI gives reflections something real to show.
- Colour: Khronos PBR Neutral (keeps base colours faithful between 8 and 80 percent linear and rolls highlights off like
  film). A preview pass of the bare wall sets the exposure so the lit wall reads at its paint colour.
- No linework. The drawing stays the drawing; this is the picture."""
import bpy, bmesh, json, math, os, sys, fnmatch
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from idd_std import trim_for

IN = 0.0254
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
views_path, idx, out = args[0], int(args[1]), args[2]
SAMPLES = int(args[args.index('--samples') + 1]) if '--samples' in args else 256
PREVIEW = '--preview' in args
# perspective: --persp X,Y,Z,TX,TY,TZ in room plan inches (X east from the west wall face, Y north from the south wall face,
# Z up from the floor), --lens mm, --res W,H, --clip inches (hide what is nearer than this, e.g. a wall behind the camera),
# --stage bath|none (dress the room for the picture)
PERSP = [float(v) for v in args[args.index('--persp') + 1].split(',')] if '--persp' in args else None
LENS = float(args[args.index('--lens') + 1]) if '--lens' in args else 24.0
RES = [int(v) for v in args[args.index('--res') + 1].split(',')] if '--res' in args else [1600, 1200]
CLIP = float(args[args.index('--clip') + 1]) if '--clip' in args else 2.0
STAGE = args[args.index('--stage') + 1] if '--stage' in args else 'none'
# components left out of this picture: an elevation flattens an alcove onto its wall plane (the tub drawn on the south
# wall stands in the tub alcove, not in the room), so a perspective inside the room leaves those pieces out
SKIP = set(args[args.index('--skip') + 1].split(',')) if '--skip' in args else set()
LIGHTS_ON = '--lights' in args
# room assembly by hand (11.09.26): --walls N=i,E=j,S=k,W=l picks the captured view for each side; --shift EAST=-24 slides a
# wall along itself (a wall longer than the room, its extra length beyond the first corner); --dims WID,DEP the room size;
# --open WEST leaves a side open; every other side without a view gets a plain wall
_FULL = {'N': 'NORTH', 'E': 'EAST', 'S': 'SOUTH', 'W': 'WEST'}
WALLMAP = {_FULL.get(k, k): int(v) for k, v in (kv.split('=') for kv in args[args.index('--walls') + 1].split(','))} if '--walls' in args else None
SHIFT = {_FULL.get(k, k): float(v) for k, v in (kv.split('=') for kv in args[args.index('--shift') + 1].split(','))} if '--shift' in args else {}
DIMS = [float(v) for v in args[args.index('--dims') + 1].split(',')] if '--dims' in args else None
OPEN = set(_FULL.get(k, k) for k in args[args.index('--open') + 1].split(',')) if '--open' in args else set()
# the lighting plan (render/export_lights.py): recessed downlights and pendants at their drawn positions, room inches; --dusk: an
# evening photograph, daylight down, every fixture of the plan on (the way the lighting design reads)
LIGHTPLAN = json.load(open(args[args.index('--lightplan') + 1])) if '--lightplan' in args else None
DUSK = '--dusk' in args
# --sun ELEV,AZ: the sun's altitude and its azimuth in plan degrees (clockwise from plan north), from the site's true north,
# latitude, date and hour. Default 32, 250: a late-afternoon sun from the plan west-southwest.
SUN = [float(v) for v in args[args.index('--sun') + 1].split(',')] if '--sun' in args else None
V = json.load(open(views_path))[idx]
_ppi = args[args.index('--ppi') + 1] if '--ppi' in args else 'auto'
PPI = float(V['k']) * 17.0 / 1892.0 * 300.0 if _ppi == 'auto' else float(_ppi)
MATS = json.load(open(os.path.join(HERE, 'materials.json')))
ROOMS = json.load(open(os.path.join(HERE, 'room_finishes.json')))
ASSETS = os.path.join(HERE, 'assets')
L, H = float(V['length']), float(V['ceiling'])
T = trim_for(H)
DEPTH = 150.0          # room depth to the facing wall, inches (lighting and reflections only; never seen directly)

room = ROOMS.get(V['room'] or '', {'roles': {}, 'views': {}})
roles = dict(room['roles'])
for pat, ov in room.get('views', {}).items():
    if fnmatch.fnmatch((V['view'] or '').upper(), pat): roles.update(ov)
R = lambda role, dflt: roles.get(role, dflt)


# ------------------------------------------------------------------ materials
def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    h = h.lstrip('#'); return [lin(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]


def _img(nt, path, colorspace, size_m, coord):
    """Image texture box-projected in object space at its real-world size."""
    mp = nt.nodes.new('ShaderNodeMapping'); s = 1.0 / size_m
    mp.inputs['Scale'].default_value = (s, s, s)
    nt.links.new(coord, mp.inputs['Vector'])
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True)
    t.image.colorspace_settings.name = colorspace; t.projection = 'BOX'; t.projection_blend = 0.25
    nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
    return t


_LIB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'material_library.json'))) if os.path.exists(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'material_library.json')) else {}
_ACG = {'Diffuse.jpg': 'Color', 'nor_gl.jpg': 'NormalGL', 'Rough.jpg': 'Roughness'}


def _map(folder, name):
    """A texture map path. Poly Haven folders hold Diffuse/nor_gl/Rough.jpg; ambientCG folders ('acg/<id>') hold
    <id>_2K-JPG_Color/NormalGL/Roughness.jpg."""
    if folder.startswith('acg/'):
        aid = folder[4:]; return os.path.join(ASSETS, 'acg', aid, '%s_2K-JPG_%s.jpg' % (aid, _ACG[name]))
    return os.path.join(ASSETS, folder, name)


def _tex_size(spec, folder, default):
    """Real-world width of one repeat of the map, in metres: the code's size_in, then ambientCG's stated width, then the default."""
    if spec.get('size_in'): return spec['size_in'] * IN
    if folder.startswith('acg/'):
        aid = folder[4:]; cat = next((k for k, v in _LIB.items() if not k.startswith('_') and aid in v), '')
        return _LIB.get('_size_cm', {}).get(aid, {'tile': 100, 'soft': 50, 'metal': 100}.get(cat, 200)) / 100.0
    return default


def _bevel_normal(nt, b, radius_in, normal_from=None):
    bv = nt.nodes.new('ShaderNodeBevel'); bv.samples = 8; bv.inputs['Radius'].default_value = radius_in * IN
    if normal_from is not None: nt.links.new(normal_from, bv.inputs['Normal'])
    nt.links.new(bv.outputs['Normal'], b.inputs['Normal'])


def material(code, variant=''):
    key = code + variant
    m = bpy.data.materials.get(key)
    if m: return m
    spec = MATS.get(code, {'hex': '#FF00FF', 'rough': 0.5, 'kind': 'paint'})
    kind = spec.get('kind', 'paint')
    m = bpy.data.materials.new(key); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); obj = tc.outputs['Object']
    rgb = list(spec['lin']) if 'lin' in spec else hex_lin(spec.get('hex', '#FF00FF'))
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = spec.get('rough', 0.5)
    bevel_r = 0.06
    if kind == 'paint':
        # painted drywall or millwork: the maker's colour, a faint texture in the roughness and normal so light breaks up
        nm = _img(nt, os.path.join(ASSETS, 'painted_plaster_wall', 'nor_gl.jpg'), 'Non-Color', 2.0, obj)
        nmap = nt.nodes.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value = 0.04 if variant != '-trim' else 0.015
        nt.links.new(nm.outputs['Color'], nmap.inputs['Color'])
        rr = _img(nt, os.path.join(ASSETS, 'painted_plaster_wall', 'Rough.jpg'), 'Non-Color', 2.0, obj)
        mr = nt.nodes.new('ShaderNodeMapRange'); base_r = spec.get('rough', 0.5)
        mr.inputs['To Min'].default_value = max(0.05, base_r - 0.06); mr.inputs['To Max'].default_value = base_r + 0.06
        nt.links.new(rr.outputs['Color'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
        _bevel_normal(nt, b, 0.06 if variant else 0.02, nmap.outputs['Normal'])
        return m
    if kind == 'fabric':
        # terry or linen: the colour from the spec, the weave from a scan's normal and roughness, a soft sheen at the edges
        folder = spec.get('texture', 'terry_cloth'); size = _tex_size(spec, folder, {'terry_cloth': 0.367, 'rough_linen': 0.5}.get(folder, 0.4))
        n = _img(nt, _map(folder, 'nor_gl.jpg'), 'Non-Color', size, obj)
        nmap = nt.nodes.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value = 0.8; nt.links.new(n.outputs['Color'], nmap.inputs['Color'])
        nt.links.new(nmap.outputs['Normal'], b.inputs['Normal'])
        b.inputs['Roughness'].default_value = 0.95; b.inputs['Sheen Weight'].default_value = 0.6; b.inputs['Sheen Roughness'].default_value = 0.5
        return m
    if kind == 'checker':
        # a checkered floor: two colours on the module the spec gives, laid square to the room
        ck = nt.nodes.new('ShaderNodeTexChecker'); mp = nt.nodes.new('ShaderNodeMapping')
        s_ = 1.0 / (2 * spec.get('module', 12.0) * IN); mp.inputs['Scale'].default_value = (s_, s_, s_)
        nt.links.new(obj, mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], ck.inputs['Vector']); ck.inputs['Scale'].default_value = 1.0
        ck.inputs['Color1'].default_value = (*rgb, 1); ck.inputs['Color2'].default_value = (*hex_lin(spec.get('hex2', '#333333')), 1)
        nt.links.new(ck.outputs['Color'], b.inputs['Base Color']); _bevel_normal(nt, b, 0.02)
        return m
    if kind == 'marble':
        # polished or honed white marble, procedural: soft grey veins that wander and branch (calacatta / carrara look);
        # spec 'veins' sets how strong. Scanned marble at Poly Haven is beige rock, not a quarried white slab.
        base = rgb; vein = hex_lin(spec.get('vein', '#8E8E8C')); strength = spec.get('veins', 0.85)
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.6, 1.6, 1.6); nt.links.new(obj, mp.inputs['Vector'])
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.4; nz.inputs['Detail'].default_value = 6.0; nz.inputs['Distortion'].default_value = 0.4
        nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
        wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'DIAGONAL'; wv.inputs['Scale'].default_value = 0.9
        wv.inputs['Distortion'].default_value = 9.0; wv.inputs['Detail'].default_value = 8.0; wv.inputs['Detail Scale'].default_value = 1.5
        nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
        mx0 = nt.nodes.new('ShaderNodeMix'); mx0.data_type = 'FLOAT'; mx0.inputs[0].default_value = 0.35
        nt.links.new(wv.outputs['Fac'], mx0.inputs[2]); nt.links.new(nz.outputs['Fac'], mx0.inputs[3])
        cr = nt.nodes.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements
        # thin cores, soft halos: a vein is a grey line with a haze either side, never a crack
        core = tuple(b_ * (1 - 0.75 * strength) + v_ * 0.75 * strength for b_, v_ in zip(base, vein))
        halo = tuple(b_ * (1 - 0.22 * strength) + v_ * 0.22 * strength for b_, v_ in zip(base, vein))
        e[0].position = 0.0; e[0].color = (*core, 1); e[1].position = 0.07; e[1].color = (*base, 1)
        e2 = cr.color_ramp.elements.new(0.008); e2.color = (*halo, 1)
        # fold the field so veins appear where it crosses mid-grey
        ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'SUBTRACT'; ab.inputs[1].default_value = 0.5; nt.links.new(mx0.outputs[0], ab.inputs[0])
        ab2 = nt.nodes.new('ShaderNodeMath'); ab2.operation = 'ABSOLUTE'; nt.links.new(ab.outputs[0], ab2.inputs[0])
        nt.links.new(ab2.outputs[0], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
        if spec.get('vein2'):
            # a second vein colour (Calacatta Monet: violet-grey veins that turn gold and sage in places): a twin ramp in the
            # second colour, blended in by a broad, slow noise so a vein changes colour along its length
            v2 = hex_lin(spec['vein2'])
            cr2 = nt.nodes.new('ShaderNodeValToRGB'); e2_ = cr2.color_ramp.elements
            core2 = tuple(b_ * (1 - 0.7 * strength) + v_ * 0.7 * strength for b_, v_ in zip(base, v2))
            halo2 = tuple(b_ * (1 - 0.25 * strength) + v_ * 0.25 * strength for b_, v_ in zip(base, v2))
            e2_[0].position = 0.0; e2_[0].color = (*core2, 1); e2_[1].position = 0.09; e2_[1].color = (*base, 1)
            e3_ = cr2.color_ramp.elements.new(0.01); e3_.color = (*halo2, 1)
            nt.links.new(ab2.outputs[0], cr2.inputs['Fac'])
            nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 0.6; nz2.inputs['Detail'].default_value = 2.0
            nt.links.new(mp.outputs['Vector'], nz2.inputs['Vector'])
            mr2 = nt.nodes.new('ShaderNodeMapRange'); mr2.inputs['From Min'].default_value = 0.48; mr2.inputs['From Max'].default_value = 0.56
            nt.links.new(nz2.outputs['Fac'], mr2.inputs['Value'])
            mxc = nt.nodes.new('ShaderNodeMix'); mxc.data_type = 'RGBA'
            nt.links.new(mr2.outputs['Result'], mxc.inputs['Factor']); nt.links.new(cr.outputs['Color'], mxc.inputs[6]); nt.links.new(cr2.outputs['Color'], mxc.inputs[7])
            nt.links.new(mxc.outputs[2], b.inputs['Base Color'])
        b.inputs['Coat Weight'].default_value = 0.0 if spec.get('honed') else 0.25; b.inputs['Coat Roughness'].default_value = 0.05
        _bevel_normal(nt, b, 0.12)
        return m
    if kind in ('wood', 'stone'):
        folder = spec.get('texture') or ('wood_floor' if kind == 'wood' else 'marble_01')
        size = _tex_size(spec, folder, {'wood_floor': 1.7, 'marble_01': 1.5, 'oak_veneer_01': 1.0, 'plank_flooring_02': 1.98, 'laminate_floor_02': 1.7, 'terry_cloth': 0.367}.get(folder, 1.5))
        d = _img(nt, _map(folder, 'Diffuse.jpg'), 'sRGB', size, obj)
        if spec.get('tint'):
            # pull the scan toward the specified colour without losing its grain: multiply by tint / mean
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
            nt.links.new(d.outputs['Color'], mx.inputs[6]); mx.inputs[7].default_value = (*spec['tint'], 1)
            nt.links.new(mx.outputs[2], b.inputs['Base Color'])
        else:
            nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
        r = _img(nt, _map(folder, 'Rough.jpg'), 'Non-Color', size, obj)
        mr = nt.nodes.new('ShaderNodeMapRange'); base_r = spec.get('rough', 0.4)
        mr.inputs['To Min'].default_value = max(0.02, base_r - 0.15); mr.inputs['To Max'].default_value = base_r + 0.15
        nt.links.new(r.outputs['Color'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
        n = _img(nt, _map(folder, 'nor_gl.jpg'), 'Non-Color', size, obj)
        nmap = nt.nodes.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value = 0.5
        nt.links.new(n.outputs['Color'], nmap.inputs['Color'])
        _bevel_normal(nt, b, 0.12 if kind == 'stone' else 0.04, nmap.outputs['Normal'])
        return m
    if kind == 'metal':
        b.inputs['Metallic'].default_value = 1.0
        if 'f82' in spec: b.inputs['Specular Tint'].default_value = (*spec['f82'], 1)
        if spec.get('brushed'):
            b.inputs['Anisotropic'].default_value = 0.6
        bevel_r = 0.03
    elif kind == 'mirror':
        b.inputs['Base Color'].default_value = (0.92, 0.94, 0.93, 1); b.inputs['Metallic'].default_value = 1.0
        b.inputs['Roughness'].default_value = 0.0; bevel_r = 0.0
    elif kind == 'glass':
        # thin architectural glass: transparent (so daylight and sun pass straight through, as they do through a pane)
        # plus a Fresnel reflection. Refractive glass would block shadow rays with caustics off and leave the room dark.
        out_n = nt.nodes['Material Output']; tr = nt.nodes.new('ShaderNodeBsdfTransparent'); gl = nt.nodes.new('ShaderNodeBsdfGlossy')
        gl.inputs['Roughness'].default_value = 0.0; fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.52
        mx = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(fr.outputs['Fac'], mx.inputs['Fac'])
        nt.links.new(tr.outputs['BSDF'], mx.inputs[1]); nt.links.new(gl.outputs['BSDF'], mx.inputs[2]); nt.links.new(mx.outputs['Shader'], out_n.inputs['Surface'])
        return m
    elif kind == 'lamp':
        # opal glass or linen shade lit from inside: translucent body plus a warm glow
        b.inputs['Base Color'].default_value = (0.95, 0.93, 0.88, 1); b.inputs['Roughness'].default_value = 0.4
        b.inputs['Subsurface Weight'].default_value = 0.0
        bb = nt.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = 3000
        nt.links.new(bb.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = spec.get('emit', 2.5)
        bevel_r = 0.05
    elif kind in ('ceramic', 'tile'):
        b.inputs['Coat Weight'].default_value = 0.6; b.inputs['Coat Roughness'].default_value = 0.03
    elif kind == 'gap':
        b.inputs['Base Color'].default_value = (0.012, 0.011, 0.010, 1); b.inputs['Roughness'].default_value = 0.9; bevel_r = 0.0
    if bevel_r: _bevel_normal(nt, b, bevel_r)
    return m


MATS.setdefault('GAP', {'kind': 'gap'})
MATS.setdefault('LAMP', {'kind': 'lamp', 'emit': 2.5})
MATS.setdefault('MIRROR-SILVER', {'kind': 'mirror'})
MATS.setdefault('PLATE-WHITE', {'hex': '#F1F0EC', 'rough': 0.32, 'kind': 'plastic'})


# ------------------------------------------------------------------ geometry (wall inches: x along the wall, y up, d out from the wall face)
COUNT = {'objects': 0}


def obj_from(verts, faces, mat, name, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x * IN, -d * IN, y * IN) for x, y, d in verts], [], faces); me.update()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat); COUNT['objects'] += 1
    return o


def box(x0, x1, y0, y1, d0, d1, mat, name='box'):
    if x1 - x0 < 0.01 or y1 - y0 < 0.01 or d1 - d0 < 0.005: return None
    v = [(x0, y0, d1), (x1, y0, d1), (x1, y0, d0), (x0, y0, d0), (x0, y1, d1), (x1, y1, d1), (x1, y1, d0), (x0, y1, d0)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return obj_from(v, f, mat, name)


def cyl(cx, cy, cd, r, length, axis, mat, name='cyl', n=40, cap=True):
    """Cylinder centred at (cx, cy, cd); axis 'd' (toward the viewer), 'y' (vertical) or 'x' (along the wall)."""
    verts = []; faces = []
    for k in (0, 1):
        t = -length / 2 + k * length
        for i in range(n):
            a = 2 * math.pi * i / n; u, w = r * math.cos(a), r * math.sin(a)
            if axis == 'd': verts.append((cx + u, cy + w, cd + t))
            elif axis == 'y': verts.append((cx + u, cy + t, cd + w))
            else: verts.append((cx + t, cy + u, cd + w))
    for i in range(n):
        j = (i + 1) % n; faces.append((i, j, n + j, n + i))
    if cap: faces.append(tuple(range(n - 1, -1, -1))); faces.append(tuple(range(n, 2 * n)))
    o = obj_from(verts, faces, mat, name, smooth=True)
    return o


def sweep(path, profile, mat, name='sweep', closed=False):
    """Sweep a profile along a polyline in the wall plane, with mitred corners.
    path: [(x, y)]; profile: [(q, d)] where q runs along the in-plane normal (the direction is rotated 90 deg CCW)
    and d is the distance out from the wall. The profile is a closed outline (first and last points on the wall)."""
    n = len(path); m = len(profile)
    def dirv(i):
        a, b = Vector(path[i]), Vector(path[(i + 1) % n]); return (b - a).normalized()
    verts = []
    for i in range(n):
        if closed or 0 < i < n - 1:
            d0 = dirv(i - 1 if i > 0 else n - 1); d1 = dirv(i if i < n - 1 or closed else i - 1)
            n0 = Vector((-d0.y, d0.x)); n1 = Vector((-d1.y, d1.x))
            mv = (n0 + n1); mv = mv.normalized() if mv.length > 1e-6 else n0
            sc = 1.0 / max(0.2, mv.dot(n1))
        else:
            dd = dirv(0) if i == 0 else dirv(n - 2); mv = Vector((-dd.y, dd.x)); sc = 1.0
        for q, d in profile:
            p = Vector(path[i]) + mv * q * sc
            verts.append((p.x, p.y, d))
    faces = []
    segs = n if closed else n - 1
    for i in range(segs):
        a, b = i * m, ((i + 1) % n) * m
        for j in range(m):
            k = (j + 1) % m; faces.append((a + j, a + k, b + k, b + j))
    if not closed:
        faces.append(tuple(range(m - 1, -1, -1))); faces.append(tuple(range((n - 1) * m, n * m)))
    o = obj_from(verts, faces, mat, name)
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    return o


def arc(cq, cd, r, a0, a1, n=8):
    return [(cq + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cd + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ------------------------------------------------------------------ trim profiles (q across the face, d projection), inches
def base_profile(h):
    """Board with an ogee cap and a quarter-round shoe: 7/8 board, cap projecting 1-1/8."""
    cap0 = h - 1.25
    pts = [(0, 0)] + [(0, 0.875 + 0.75)] + arc(0.75, 0.875 + 0.75, 0.75, 180, 270)[1:] + [(0.75, 0.875), (cap0, 0.875)]
    pts += [(cap0, 1.0)] + arc(cap0 + 0.45, 1.0, 0.45, 180, 90)[1:] + arc(cap0 + 0.45 + 0.4, 1.45, 0.4, 270, 360)[1:]
    pts += [(h - 0.1, 1.05), (h, 0.6), (h, 0)]
    return pts


def crown_profile(drop, proj):
    """Built-up crown: frieze board with a bead, bed mould, then a cyma recta to the ceiling (q from the ceiling down)."""
    fr = drop * 0.42           # frieze board from the bottom
    pts = [(0, 0), (0, proj)]
    # cyma recta, ceiling to the bed mould
    c_end = drop - fr - 0.9
    for i in range(1, 15):
        t = i / 14.0
        q = c_end * t; dd = proj - (proj - 2.0) * (0.5 - 0.5 * math.cos(math.pi * t)) - 0.35 * math.sin(2 * math.pi * t)
        pts.append((q, dd))
    pts += [(c_end + 0.15, 1.75)] + arc(c_end + 0.55, 1.75, 0.4, 90, -90)[1:]   # bed mould bead
    pts += [(drop - fr, 1.0), (drop - fr, 0.875), (drop - 0.9, 0.875)] + arc(drop - 0.5, 0.875, 0.4, 90, -90)[1:]
    pts += [(drop, 0.75), (drop, 0)]
    return pts


def casing_profile(cs):
    """5 in. casing: bead at the reveal, flat face, raised backband."""
    bb = 1.25
    pts = [(0, 0), (0, 0.55)] + arc(0.3, 0.55, 0.3, 180, 90)[1:] + [(0.6, 0.75), (cs - bb - 0.1, 0.8), (cs - bb, 0.95)]
    pts += arc(cs - bb + 0.45, 0.95, 0.45, 180, 90)[1:] + [(cs - 0.3, 1.35)] + arc(cs - 0.3, 1.05, 0.3, 90, 0)[1:] + [(cs, 0)]
    return pts


def sticking_profile(w=0.75, depth=0.5):
    """Ovolo sticking around a recessed panel (q from the frame edge into the panel)."""
    return [(0, 0), (0, depth)] + arc(0.0, depth - w * 0.6, w * 0.6, 90, 0)[1:] + [(w, 0)]


# ------------------------------------------------------------------ builders: one per component the generators call
BUILT, MISSING = set(), set()
trim_mat = lambda: material(R('trim', 'PT-01-SATIN'), '-trim')
wall_mat = lambda: material(R('wall', 'PT-02'))


def b_base(a, ctx):
    h = a.get('h') or T['base']
    sweep([(a['x0'], 0.0), (a['x1'], 0.0)], base_profile(h), trim_mat(), 'base')


def b_crown(a, ctx):
    drop = a.get('drop') or T['crown']; Hh = a['H']
    sweep([(a['x1'], Hh), (a['x0'], Hh)], crown_profile(drop, T['crown_proj']), material(R('crown', R('trim', 'PT-01-SATIN')), '-trim'), 'crown')


def b_casing(a, ctx):
    cs = a.get('cs') or T['casing']; x, w, head, sill = a['x'], a['w'], a['head'], a.get('sill', 0) or 0
    sweep([(x, sill), (x, head), (x + w, head), (x + w, sill)], casing_profile(cs), trim_mat(), 'casing')


def _panel(x0, y0, x1, y1, face_d, mat, raised=False):
    """A recessed panel in a stile-and-rail frame: ovolo sticking, panel 1/2 in. back."""
    sweep([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], [(q, d + face_d - 0.5) for q, d in sticking_profile()], mat, 'sticking', closed=True)
    box(x0, x1, y0, y1, face_d - 0.75, face_d - 0.5, mat, 'panel')


def b_door_leaf(a, ctx, face_d=-0.25):
    x, w, head, panels = a['x'], a['w'], a['head'], a.get('panels', 2)
    m = material(R('door', 'PT-01-SATIN'), '-trim')
    st, rb, rt, mid = 4.5, 9.0, 4.5, 4.5
    gap = 0.0625
    x0, x1 = x + gap, x + w - gap
    back = face_d - 1.75
    box(x0, x0 + st, 0.5, head - gap, back, face_d, m, 'stile'); box(x1 - st, x1, 0.5, head - gap, back, face_d, m, 'stile')
    box(x0 + st, x1 - st, 0.5, rb, back, face_d, m, 'rail'); box(x0 + st, x1 - st, head - rt, head - gap, back, face_d, m, 'rail')
    if panels == 2:
        split = rb + (head - rt - rb) * 0.62
        box(x0 + st, x1 - st, split - mid / 2, split + mid / 2, back, face_d, m, 'rail')
        _panel(x0 + st, rb, x1 - st, split - mid / 2, face_d, m); _panel(x0 + st, split + mid / 2, x1 - st, head - rt, face_d, m)
    elif panels == 'glass':
        box(x0 + st, x1 - st, rb, head - rt, back + 0.6, back + 0.85, material('GLASS-CLEAR'), 'glass')
    else:
        _panel(x0 + st, rb, x1 - st, head - rt, face_d, m)
    if panels != 'glass': box(x, x + w, 0.0, head, back - 0.05, back, material('GAP'), 'doorback')   # a glass door must let light through
    if a.get('swing') is None:
        px = x + w - 3.5 if a.get('pull', 'R') == 'R' else x + 2.3
        box(px, px + 1.2, 36, 40, face_d - 0.2, face_d + 0.01, material('GAP'), 'flushpull'); return
    hinge_left = a.get('swing', 'L') == 'L'
    lx = x + w - 3 if hinge_left else x + 3
    metal = material(R('metal', 'METAL-NICKEL'))
    cyl(lx, 38, face_d + 0.2, 1.1, 0.4, 'd', metal, 'rose')
    cyl(lx, 38, face_d + 1.2, 0.3, 1.8, 'd', metal, 'neck')
    dirn = -1 if hinge_left else 1
    cyl(lx + dirn * 2.0, 38, face_d + 2.1, 0.32, 4.2, 'x', metal, 'lever')


def b_door_pair(a, ctx):
    x, w, head = a['x'], a['w'], a['head']
    # jamb lining in the wall thickness, the leaves set in the jamb
    jm = material(R('door', 'PT-01-SATIN'), '-trim')
    box(x - 0.01, x + 0.75, 0, head, -5.5, 0.0, jm, 'jamb'); box(x + w - 0.75, x + w + 0.01, 0, head, -5.5, 0.0, jm, 'jamb')
    box(x, x + w, head - 0.01, head + 0.75, -5.5, 0.0, jm, 'jamb')


def b_vanity_furniture(a, ctx):
    x, w, h, ctr = a['x'], a['w'], a['h'], a['counter']
    paint = material(R('vanity', 'VAN-01'), '-trim'); stone = material(R('counter', 'STONE-TOP'))
    metal = material(R('metal', 'METAL-NICKEL')); gap = material('GAP')
    D = 21.0                                          # carcass front, inches from the wall
    leg_h = 5.0 if a.get('legs', True) else 0.0
    # stone top with eased edge, 3/4 overhang
    box(x - 0.75, x + w + 0.75, h, h + ctr, 0.0, D + 0.75, stone, 'top')
    # carcass: sides, back, face frame
    box(x, x + w, leg_h, h, 0.5, D - 0.875, paint, 'carcass')
    if leg_h:
        for lx in (x, x + w - 2.25):
            box(lx, lx + 2.25, 0.0, leg_h, D - 2.25, D, paint, 'leg')
            box(lx, lx + 2.25, 0.0, 0.4, D - 2.25, D + 0.02, material(R('metal', 'METAL-NICKEL')), 'sabot')
    else:
        box(x + 2, x + w - 2, 0, 4, D - 3, D - 2.5, gap, 'toe')
    ff = 1.5                                          # face frame stiles and rails
    box(x, x + ff, leg_h + 1.5, h - 1.5, D - 0.875, D, paint, 'ff'); box(x + w - ff, x + w, leg_h + 1.5, h - 1.5, D - 0.875, D, paint, 'ff')
    box(x, x + w, leg_h, leg_h + 1.5, D - 0.875, D, paint, 'ff_bottom'); box(x, x + w, h - 1.5, h, D - 0.875, D, paint, 'ff_top')
    sc = a['sink_center'] if a.get('sink_center') is not None else x + w / 2
    dw = 24 if w >= 48 else 18
    y_b, y_t = leg_h + 1.5, h - 1.5
    # doors at the sink: inset shaker, 1/8 reveal
    rv = 0.125
    box(sc - dw / 2 - ff, sc - dw / 2, y_b, y_t, D - 0.875, D, paint, 'ff_mid'); box(sc + dw / 2, sc + dw / 2 + ff, y_b, y_t, D - 0.875, D, paint, 'ff_mid')
    box(sc - dw / 2, sc + dw / 2, y_b, y_t, D - 1.0, D - 0.95, gap, 'reveal_back')
    for dx0, dx1 in ((sc - dw / 2 + rv, sc - rv / 2), (sc + rv / 2, sc + dw / 2 - rv)):
        fy0, fy1 = y_b + rv, y_t - rv; fw = 2.25
        box(dx0, dx0 + fw, fy0, fy1, D - 0.75, D - 0.02, paint, 'dstile'); box(dx1 - fw, dx1, fy0, fy1, D - 0.75, D - 0.02, paint, 'dstile')
        box(dx0 + fw, dx1 - fw, fy0, fy0 + fw, D - 0.75, D - 0.02, paint, 'drail'); box(dx0 + fw, dx1 - fw, fy1 - fw, fy1, D - 0.75, D - 0.02, paint, 'drail')
        box(dx0 + fw, dx1 - fw, fy0 + fw, fy1 - fw, D - 0.75, D - 0.4, paint, 'dpanel')
    for px in (sc - 1.6, sc + 1.6):                   # vertical bar pulls
        cyl(px, y_t - 9, D + 1.1, 0.22, 5.0, 'y', metal, 'pull'); cyl(px, y_t - 6.8, D + 0.55, 0.16, 1.1, 'd', metal, 'post'); cyl(px, y_t - 11.2, D + 0.55, 0.16, 1.1, 'd', metal, 'post')
    # drawer stacks: inset slab fronts with a reveal, centred bar pulls
    n = a.get('drawers', 3)
    for a0, a1 in ((x + ff, sc - dw / 2 - ff), (sc + dw / 2 + ff, x + w - ff)):
        if a1 - a0 < 6: continue
        dh = (y_t - y_b) / n
        box(a0, a1, y_b, y_t, D - 1.0, D - 0.95, gap, 'reveal_back')
        for i in range(n):
            y0 = y_b + i * dh
            if i: box(a0, a1, y0 - 0.375, y0 + 0.375, D - 0.875, D, paint, 'ff_rail')
            fy0, fy1 = y0 + (0.375 if i else 0) + rv, y0 + dh - (0.375 if i < n - 1 else 0) - rv
            box(a0 + rv, a1 - rv, fy0, fy1, D - 0.75, D - 0.02, paint, 'drawer')
            cy_ = (fy0 + fy1) / 2; cx_ = (a0 + a1) / 2
            cyl(cx_, cy_, D + 1.1, 0.2, 5.0, 'x', metal, 'dpull'); cyl(cx_ - 2.3, cy_, D + 0.55, 0.15, 1.1, 'd', metal, 'post'); cyl(cx_ + 2.3, cy_, D + 0.55, 0.15, 1.1, 'd', metal, 'post')


def b_faucet_wall(a, ctx):
    cx, y, sp = a['cx'], a['y'], a.get('spread', 8.0)
    m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y, 0.25, 1.5, 0.5, 'd', m, 'esc'); cyl(cx, y, 3.6, 0.45, 6.4, 'd', m, 'spout')
    cyl(cx, y - 1.3, 6.8, 0.45, 2.6, 'y', m, 'spout_down'); cyl(cx, y, 6.8, 0.52, 1.1, 'x', m, 'elbow')
    cyl(cx, y - 2.7, 6.8, 0.5, 0.35, 'y', material('GAP'), 'aerator')
    for hx, dd in ((cx - sp, -1), (cx + sp, 1)):
        cyl(hx, y, 0.25, 1.25, 0.5, 'd', m, 'hesc'); cyl(hx, y, 1.2, 0.35, 1.6, 'd', m, 'stem')
        cyl(hx + dd * 1.6, y, 1.9, 0.25, 3.2, 'x', m, 'lever')


def b_faucet(a, ctx):
    cx, y, hh = a['cx'], a['y'], a.get('h', 7)
    m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y + (hh - 2) / 2, 12.0, 0.55, hh - 2, 'y', m, 'body'); cyl(cx + 1.6, y + hh, 12.0, 0.4, 3.4, 'x', m, 'spout')
    for hx in (cx - 4, cx + 4): cyl(hx, y + 0.8, 12.0, 0.7, 1.6, 'y', m, 'handle')


def b_mirror_framed(a, ctx):
    x, w, y, h, fr = a['x'], a['w'], a['y'], a['h'], a.get('frame', 2.0)
    m = material(R('mirror_frame', 'METAL-NICKEL'))
    prof = [(0, 0), (0, 0.9)] + arc(0.45, 0.9, 0.45, 180, 90)[1:] + [(fr * 0.55, 1.2), (fr - 0.25, 0.95), (fr, 0.75), (fr, 0)]
    sweep([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], prof, m, 'frame', closed=True)
    box(x + fr - 0.2, x + w - fr + 0.2, y + fr - 0.2, y + h - fr + 0.2, 0.3, 0.55, material('MIRROR-SILVER'), 'glass')


def b_mirror_panel(a, ctx):
    x, w, y, h = a['x'], a['w'], a['y'], a['h']
    box(x, x + w, y, y + h, 0.0, 0.25, material('MIRROR-SILVER'), 'mirror')


def b_sconce(a, ctx):
    cx, cy = a['cx'], a['cy']
    m = material(R('metal', 'METAL-NICKEL'))
    if a.get('style', 'cylinder') == 'cylinder':
        cyl(cx, cy, 0.3, 2.25, 0.6, 'd', m, 'plate'); cyl(cx, cy, 2.0, 0.3, 2.8, 'd', m, 'arm')
        sh_ = cyl(cx, cy, 4.0, 1.5, 9.0, 'y', material('LAMP'), 'shade'); sh_.visible_shadow = False   # the lamp inside lights the room through it
        sh_.visible_diffuse = False   # the glowing shade is for the eye; the lamp inside does the lighting (a lit mesh at the exposure gain swamped the wall in orange)
        cyl(cx, cy + 4.65, 4.0, 1.58, 0.3, 'y', m, 'cap'); cyl(cx, cy - 4.65, 4.0, 1.58, 0.3, 'y', m, 'cap')
        lamp(cx, cy, 4.0)
    else:
        cyl(cx, cy, 0.3, 2.0, 0.6, 'd', m, 'plate'); cyl(cx, cy + 2.75, 2.5, 0.25, 1.5, 'y', m, 'stem')
        sh_ = cyl(cx, cy + 7.0, 3.0, 3.25, 7.0, 'y', material('LAMP'), 'shade'); sh_.visible_shadow = False; sh_.visible_diffuse = False; lamp(cx, cy + 6.0, 3.0)


def lamp(cx, cy, cd, watts=0.25, radius=0.9):
    """A warm 3000 K point light inside a shade. 1.2 W radiant is about a 350 lm sconce lamp (Blender manual: 800 lm = 2.1 W)."""
    ld = bpy.data.lights.new('lamp', 'POINT'); ld.energy = watts; ld.shadow_soft_size = radius * IN
    ld.use_nodes = True; nt = ld.node_tree; bb = nt.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = 3000
    nt.links.new(bb.outputs['Color'], nt.nodes['Emission'].inputs['Color'])
    o = bpy.data.objects.new('lamp', ld); o.location = (cx * IN, -cd * IN, cy * IN); bpy.context.collection.objects.link(o); o.visible_glossy = False


def b_outlet(a, ctx):
    cx, cy = a['cx'], a.get('cy') or 18.0
    pm = material('PLATE-WHITE'); gap = material('GAP')
    hz = a.get('horizontal')
    pw, ph = (4.5, 2.75) if hz else (2.75, 4.5)
    box(cx - pw / 2, cx + pw / 2, cy - ph / 2, cy + ph / 2, 0.0, 0.2, pm, 'plate')
    if a.get('label') == 'GFCI':
        box(cx - 0.65, cx + 0.65, cy - 1.3, cy + 1.3, 0.2, 0.32, pm, 'decora')
        for yy in (cy + 0.7, cy - 0.7):
            box(cx - 0.18, cx - 0.1, yy - 0.22, yy + 0.22, 0.31, 0.33, gap, 'slot'); box(cx + 0.1, cx + 0.2, yy - 0.22, yy + 0.22, 0.31, 0.33, gap, 'slot')
        box(cx - 0.35, cx + 0.35, cy - 0.12, cy + 0.12, 0.32, 0.36, pm, 'btn')
    else:
        # a horizontal duplex has its two receptacles side by side (both were built at the centre, one inside the other: the audit's DUPLICATE)
        for (xx, yy) in (((cx, cy + 1.1), (cx, cy - 1.1)) if not hz else ((cx - 1.1, cy), (cx + 1.1, cy))):
            cyl(xx, yy, 0.27, 0.62, 0.14, 'd', pm, 'face')
            box(xx - 0.2, xx - 0.12, yy - 0.18, yy + 0.18, 0.33, 0.35, gap, 'slot'); box(xx + 0.12, xx + 0.2, yy - 0.18, yy + 0.18, 0.33, 0.35, gap, 'slot')


def b_switch(a, ctx):
    cx, cy = a['cx'], a.get('cy', 48)
    pm = material('PLATE-WHITE')
    box(cx - 1.375, cx + 1.375, cy - 2.25, cy + 2.25, 0.0, 0.2, pm, 'plate'); box(cx - 0.65, cx + 0.65, cy - 1.3, cy + 1.3, 0.2, 0.36, pm, 'rocker')


def _vanity_front_at(x, y):
    for c in V.get('calls', []):   # V is the wall being built
        if c['comp'] in ('vanity_furniture', 'vanity_floating') and c['depth'] == 0:
            a = c['args']
            if a['x'] - 1 <= x <= a['x'] + a['w'] + 1 and y < a['h']: return 21.0
    return 0.0


def b_towel_bar(a, ctx):
    cx, y, w = a['cx'], a.get('y', 48), a.get('w', 24)
    m = material(R('metal', 'METAL-NICKEL')); base_d = _vanity_front_at(cx, y)
    for px in (cx - w / 2, cx + w / 2):
        cyl(px, y, base_d + 0.2, 1.0, 0.4, 'd', m, 'rose'); cyl(px, y, base_d + 1.6, 0.3, 2.6, 'd', m, 'post')
    cyl(cx, y, base_d + 2.6, 0.38, w + 0.6, 'x', m, 'bar')


def b_towel_ring(a, ctx):
    cx, y = a['cx'], a.get('y', 52); m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y, 0.2, 1.0, 0.4, 'd', m, 'rose'); cyl(cx, y, 1.3, 0.25, 2.0, 'd', m, 'post')
    bpy.ops.mesh.primitive_torus_add(major_radius=3.0 * IN, minor_radius=0.22 * IN, location=(cx * IN, -2.4 * IN, (y - 3.2) * IN), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()


def b_robe_hook(a, ctx):
    cx, y = a['cx'], a.get('y', 66); m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y, 0.2, 0.9, 0.4, 'd', m, 'rose'); cyl(cx, y, 1.4, 0.28, 2.4, 'd', m, 'hook'); cyl(cx, y + 0.5, 2.6, 0.3, 1.2, 'y', m, 'tip')


def b_paper_holder(a, ctx):
    cx, y = a['cx'], a.get('y', 26); m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx - 3.0, y, 0.2, 1.0, 0.4, 'd', m, 'rose'); cyl(cx - 3.0, y, 1.6, 0.25, 2.8, 'd', m, 'arm'); cyl(cx, y, 3.0, 0.25, 6.0, 'x', m, 'rod')


def b_valve(a, ctx):
    cx, y = a['cx'], a.get('y', 48); m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y, 0.2, 3.5, 0.4, 'd', m, 'trim'); cyl(cx, y, 1.1, 0.5, 1.6, 'd', m, 'stem'); cyl(cx + 1.5, y, 1.9, 0.3, 3.4, 'x', m, 'lever')


def loft(rings, mat, name, cap_bottom=True, smooth=True):
    """Join closed rings of (x, y, d) points (same count) into a surface."""
    n = len(rings[0]); verts = [p for r in rings for p in r]; faces = []
    for k in range(len(rings) - 1):
        a, b = k * n, (k + 1) * n
        for i in range(n): j = (i + 1) % n; faces.append((a + i, a + j, b + j, b + i))
    if cap_bottom: faces.append(tuple(range(n - 1, -1, -1)))
    o = obj_from(verts, faces, mat, name, smooth=smooth)
    me = o.data; bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return o


def superellipse(cx, cd, a, b, y, n=64, e=2.6):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; c, s_ = math.cos(t), math.sin(t)
        pts.append((cx + a * math.copysign(abs(c) ** (2 / e), c), y, cd + b * math.copysign(abs(s_) ** (2 / e), s_)))
    return pts


def b_freestanding_tub(a, ctx):
    """Freestanding soaking tub: a soft oval shell, sides tapering to a smaller foot, a rolled rim and an inner basin."""
    x, w, h = a['x'], a['w'], a.get('h', 22)
    cx, cd, A, B = x + w / 2, 18.0, w / 2, 15.0
    m = material('PORCELAIN')
    rings = []
    for t in (0.0, 0.08, 0.25, 0.5, 0.75, 0.92, 1.0):
        sc_ = 0.80 + 0.20 * math.sin(t * math.pi / 2) ** 0.7
        rings.append(superellipse(cx, cd, A * sc_, B * sc_, h * t))
    rim_in = 1.5
    rings.append(superellipse(cx, cd, A - 0.4, B - 0.4, h + 0.6))
    rings.append(superellipse(cx, cd, A - rim_in, B - rim_in, h + 0.4))
    for t in (0.15, 0.5, 1.0):
        sc_ = 1.0 - 0.18 * t
        rings.append(superellipse(cx, cd, (A - rim_in) * sc_, (B - rim_in) * (1.0 - 0.25 * t), h - 15.0 * t))
    loft(rings, m, 'tub')


def b_tub_filler_wall(a, ctx):
    cx, y, sp = a['cx'], a.get('y', 30), a.get('spread', 8.0)
    m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y, 0.25, 1.5, 0.5, 'd', m, 'esc'); cyl(cx, y, 4.0, 0.55, 7.5, 'd', m, 'spout'); cyl(cx, y - 0.9, 7.8, 0.55, 1.6, 'y', m, 'spout_tip')
    for hx, dd in ((cx - sp, -1), (cx + sp, 1)):
        cyl(hx, y + 4, 0.25, 1.25, 0.5, 'd', m, 'hesc'); cyl(hx, y + 4, 1.2, 0.35, 1.6, 'd', m, 'stem'); cyl(hx + dd * 1.6, y + 4, 1.9, 0.25, 3.2, 'x', m, 'lever')


def b_window(a, ctx):
    """Window in the wall: jamb return (cased, or tiled when trim=False), a painted frame and muntins, real glass."""
    x, w, sill, head, lites = a['x'], a['w'], a['sill'], a['head'], a.get('lites', 2)
    jm = material(R('trim', 'PT-01-SATIN'), '-trim') if a.get('trim', True) else wall_mat()
    box(x - 0.01, x + 0.01, sill, head, -5.5, 0.0, jm, 'jamb'); box(x + w - 0.01, x + w + 0.01, sill, head, -5.5, 0.0, jm, 'jamb')
    box(x, x + w, head - 0.01, head + 0.01, -5.5, 0.0, jm, 'head'); box(x, x + w, sill - 0.01, sill + 0.01, -5.5, 0.0, jm, 'sill')
    fr = material('PT-01-SATIN', '-trim'); gl = material('GLASS-CLEAR')
    box(x, x + 1.75, sill, head, -4.5, -2.5, fr, 'frame'); box(x + w - 1.75, x + w, sill, head, -4.5, -2.5, fr, 'frame')
    box(x, x + w, sill, sill + 2.25, -4.5, -2.5, fr, 'frame'); box(x, x + w, head - 1.75, head, -4.5, -2.5, fr, 'frame')
    for i in range(1, lites):
        mx = x + w * i / lites; box(mx - 1.0, mx + 1.0, sill, head, -4.5, -2.5, fr, 'mullion')
    box(x + 1.0, x + w - 1.0, sill + 1.0, head - 1.0, -3.6, -3.4, gl, 'glass')
    if a.get('trim', True):
        b_casing({'x': x, 'w': w, 'head': head, 'sill': sill}, ctx)
        box(x - 5.5, x + w + 6.5, sill - 1.5, sill, -0.01, 1.5, jm, 'stool')
    PORTALS.append((x + 1, x + w - 1, sill + 1, head - 1, -5.0))


def b_niche(a, ctx):
    x, w, y, h = a['x'], a['w'], a['y'], a['h']
    m = material(R('tile', R('wall', 'PT-02')))
    box(x, x + w, y, y + h, -4.5, -4.0, m, 'niche_back')
    box(x, x + 0.01, y, y + h, -4.0, 0.0, m, 'niche_side'); box(x + w - 0.01, x + w, y, y + h, -4.0, 0.0, m, 'niche_side')
    box(x, x + w, y + h - 0.01, y + h, -4.0, 0.0, m, 'niche_top'); box(x, x + w, y - 0.6, y, -4.0, 0.25, material(R('counter', 'STONE-TOP')), 'niche_sill')


def b_vanity_end(a, ctx):
    """The side of a vanity seen on an end wall. In a room build the vanity already exists from its own wall: skip."""
    if ROOM_MODE: return
    x, dp, h, ctr = a['x'], a['depth'], a['h'], a['counter']
    x0, x1 = (x, x + dp) if a.get('open_to', 'R') == 'R' else (x - dp, x)
    box(x0, x1, 5.0, h, 0.0, 24.0, material(R('vanity', 'VAN-01'), '-trim'), 'vanity_side')
    box(x0, x1 + 0.75, h, h + ctr, 0.0, 24.75, material(R('counter', 'STONE-TOP')), 'top')


def b_tile_grid(a, ctx):
    """Tile or slab on the wall: each piece a 3/8 in. body with eased edges, set out exactly as the drawing sets it out,
    grout behind; only inside the `show` windows when the drawing limits them (cabinets and mirrors in front)."""
    x0, x1, y0, y1 = a['x0'], a['x1'], a['y0'], a['y1']; tw, th = a.get('module') or (24, 12); g = a.get('grout', 0.125) or 0.125
    m = material(R('tile', 'WT-02')); grout = material('GROUT')
    fd = float(a.get('face_d') or 0.0)    # a column return seen face-on: the tile sits on that face, not on the wall
    box(x0, x1, y0, y1, fd - 0.01, fd + 0.2, grout, 'grout')
    Lx = x1 - x0; n = int(Lx / tw); rem = Lx - n * tw
    off = rem / 2 if a.get('setout', 'center') == 'center' else 0
    if a.get('setout', 'center') == 'center' and rem / 2 < tw * 0.25: off = rem / 2 + tw / 2
    cols = [x0]
    if n:
        xx = x0 + off
        while xx > x0 + 0.1: xx -= tw
        xx += tw
        while xx < x1 - 0.1: cols.append(xx); xx += tw
    cols.append(x1)
    rows = []; yy = y0
    while yy < y1 - 0.1: rows.append(yy); yy += th
    rows.append(y1)
    count = 0
    for ri in range(len(rows) - 1):
        cs_ = cols
        if a.get('stagger') and ri % 2 and n:
            cs_ = sorted(set([x0, x1] + [min(x1, max(x0, c + tw / 2)) for c in cols[1:-1]]))
        for ci in range(len(cs_) - 1):
            bx0, bx1, by0, by1 = cs_[ci] + (g / 2 if ci else 0), cs_[ci + 1] - (g / 2 if ci < len(cs_) - 2 else 0), rows[ri] + (g / 2 if ri else 0), rows[ri + 1] - (g / 2 if ri < len(rows) - 2 else 0)
            if bx1 - bx0 > 0.2 and by1 - by0 > 0.2:
                box(bx0, bx1, by0, by1, fd, fd + 0.375, m, 'tile'); count += 1
            if count > 2500: return


def b_stone_slab(a, ctx):
    x0, x1, y0, y1 = a['x0'], a['x1'], a['y0'], a['y1']; m = material(R('tile', 'WT-02'))
    edges = [x0] + sorted(a.get('seams') or []) + [x1]
    for i in range(len(edges) - 1):
        box(edges[i] + (0.0625 if i else 0), edges[i + 1] - (0.0625 if i < len(edges) - 2 else 0), y0, y1, 0.0, 0.75, m, 'slab')


def b_pilaster(a, ctx):
    x, w, Hh = a['x'], a['w'], a['H']
    box(x, x + w, 0, Hh, 0.0, 6.0, material(R('tile', R('wall', 'PT-02'))), 'pilaster')


def b_glass_edge(a, ctx):
    x, h = a['x'], a.get('h', 84)
    box(x - 0.1875, x + 0.1875, 0.0, h, 0.0, 34.0, material('GLASS-CLEAR'), 'glass_panel')
    box(x - 0.5, x + 0.5, h, h + 1.0, 0.0, 34.0, material(R('metal', 'METAL-NICKEL')), 'channel')


def b_shower_door_centered(a, ctx):
    x, w, h, dw = a['x'], a['w'], a.get('h', 96), a.get('door_w', 28)
    fix = (w - dw) / 2; gl = material('GLASS-CLEAR'); mt = material(R('metal', 'METAL-NICKEL'))
    box(x, x + fix - 0.25, 0.25, h - 0.5, 0.0, 0.375, gl, 'fixed'); box(x + w - fix + 0.25, x + w, 0.25, h - 0.5, 0.0, 0.375, gl, 'fixed')
    box(x + fix + 0.25, x + fix + dw - 0.25, 0.5, h - 1.0, 0.0, 0.375, gl, 'door')
    box(x, x + w, h - 0.5, h + 0.75, -0.25, 0.75, mt, 'header')
    hx = x + fix if a.get('hinge', 'L') == 'L' else x + fix + dw
    for hy in (12, h / 2, h - 12): box(hx - 1.2, hx + 1.2, hy - 1.5, hy + 1.5, -0.2, 0.6, mt, 'hinge')
    lx = x + fix + dw - 2.8 if a.get('hinge', 'L') == 'L' else x + fix + 2.8
    cyl(lx, 42, 1.4, 0.4, 12.0, 'y', mt, 'pull'); cyl(lx, 37, 0.7, 0.25, 1.4, 'd', mt, 'post'); cyl(lx, 47, 0.7, 0.25, 1.4, 'd', mt, 'post')


def b_shower_glass(a, ctx):
    x, w, h = a['x'], a['w'], a.get('h', 84)
    box(x, x + w, 0.25, h, 0.0, 0.375, material('GLASS-CLEAR'), 'glass'); box(x, x + w, h, h + 0.75, -0.2, 0.6, material(R('metal', 'METAL-NICKEL')), 'channel')


def b_shower_head(a, ctx):
    cx, y, w = a['cx'], a.get('y', 80), a.get('w', 8); m = material(R('metal', 'METAL-NICKEL'))
    cyl(cx, y, 0.2, 1.5, 0.4, 'd', m, 'esc'); cyl(cx, y, 6.0, 0.4, 12.0, 'd', m, 'arm')
    cyl(cx, y - 1.5, 11.5, 0.4, 3.0, 'y', m, 'drop'); cyl(cx, y - 3.4, 11.5, w / 2, 0.6, 'y', m, 'head')


def _toilet(cx, cd, rot, Lf=28.7, seat=17.0, tank_h=31.0):
    """A one-piece skirted toilet: tank against the wall, oval bowl, seat and lid. Built facing +d, then turned by rot (deg)."""
    m = material('PORCELAIN'); objs = []
    rings = []
    for y_, sc_ in ((0.0, 0.78), (6.0, 0.80), (12.0, 0.88), (15.0, 0.98), (15.8, 1.0)):
        rings.append(superellipse(0.0, 17.0, 7.3 * sc_, 10.3 * sc_, y_, n=48, e=2.2))
    objs.append(loft(rings, m, 'bowl'))
    seat_r = [superellipse(0.0, 17.2, 7.4, 10.4, seat - 1.2, n=48, e=2.2), superellipse(0.0, 17.2, 7.4, 10.4, seat, n=48, e=2.2)]
    objs.append(loft(seat_r, m, 'seat'))
    objs.append(box(-7.6, 7.6, seat - 1.0, tank_h, 1.0, 9.0, m, 'tank')); objs.append(box(-7.9, 7.9, tank_h, tank_h + 1.4, 0.75, 9.4, m, 'lid'))
    objs.append(box(-6.0, 6.0, 0.0, seat - 1.0, 4.0, 12.0, m, 'skirt'))
    cyl(-6.2, tank_h - 3.0, 9.3, 0.45, 0.6, 'd', material(R('metal', 'METAL-NICKEL')), 'lever')
    return objs


def b_toilet(a, ctx):
    x, w = a['x'], a.get('w', 15)
    before = set(bpy.data.objects); _toilet(0, 0, 0)
    for o in set(bpy.data.objects) - before: o.location.x += (x + w / 2) * IN


def b_toilet_profile(a, ctx):
    """The toilet seen from the side. In a room build it already exists from the wall it stands against: skip."""
    if ROOM_MODE: return
    x, facing = a['x'], a.get('facing', 'L')
    before = set(bpy.data.objects); _toilet(0, 0, 0)
    for o in set(bpy.data.objects) - before:
        # stand it on the wall at x, bowl toward `facing`, 21 in. out from this wall (the middle of a compartment)
        o.matrix_world = Matrix.Translation((x * IN, -21.0 * IN, 0)) @ Matrix.Rotation(math.radians(90 if facing == 'L' else -90), 4, 'Z') @ o.matrix_world


def b_cut_wall(a, ctx):
    pass   # a partition seen end-on: the room build has the partition itself


def b_mirror_led(a, ctx):
    x, w, y, h = a['x'], a['w'], a['y'], a['h']
    box(x, x + w, y, y + h, 1.0, 1.25, material('MIRROR-SILVER'), 'mirror'); box(x + 0.5, x + w - 0.5, y + 0.5, y + h - 0.5, 0.0, 1.0, material('GAP'), 'back')


exec(open(os.path.join(HERE, 'extra_builders.py')).read())
BUILDERS = {'base': b_base, 'crown': b_crown, 'casing': b_casing, 'door_leaf': b_door_leaf, 'door_pair': b_door_pair,
            'vanity_furniture': b_vanity_furniture, 'faucet_wall': b_faucet_wall, 'faucet': b_faucet, 'mirror_framed': b_mirror_framed,
            'mirror_panel': b_mirror_panel, 'sconce': b_sconce, 'outlet': b_outlet, 'switch': b_switch, 'towel_bar': b_towel_bar,
            'towel_ring': b_towel_ring, 'robe_hook': b_robe_hook, 'paper_holder': b_paper_holder, 'valve': b_valve,
            'freestanding_tub': b_freestanding_tub, 'tub_filler_wall': b_tub_filler_wall, 'window': b_window, 'niche': b_niche,
            'vanity_end': b_vanity_end, 'tile_grid': b_tile_grid, 'stone_slab': b_stone_slab, 'pilaster': b_pilaster,
            'glass_edge': b_glass_edge, 'shower_door_centered': b_shower_door_centered, 'shower_glass': b_shower_glass,
            'shower_head': b_shower_head, 'toilet': b_toilet, 'toilet_profile': b_toilet_profile, 'cut_wall': b_cut_wall,
            'mirror_led': b_mirror_led,
            # drawn only for the line drawing, no object: the shadow line, the hidden basin
            'shadow': None, 'basin_hidden': None}
BUILDERS.update(EXTRA_BUILDERS)
MATS.setdefault('GLASS-CLEAR', {'kind': 'glass'})
MATS.setdefault('GROUT', {'hex': '#CFCBC3', 'rough': 0.8, 'kind': 'plastic'})


def area(name, size_x, size_y, energy, loc_in, aim_in, color=(1.0, 0.985, 0.96), glossy=False):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = size_x * IN; ld.size_y = size_y * IN
    ld.energy = energy; ld.color = color
    o = bpy.data.objects.new(name, ld); bpy.context.collection.objects.link(o)
    o.location = (loc_in[0] * IN, -loc_in[2] * IN, loc_in[1] * IN)
    aim = Vector((aim_in[0] * IN, -aim_in[2] * IN, aim_in[1] * IN)) - o.location
    o.rotation_euler = aim.normalized().to_track_quat('-Z', 'Y').to_euler()
    o.visible_glossy = glossy
    return o


# ------------------------------------------------------------------ the room: every wall of the room built in place
def subtract(rect, hs):
    outr = [rect]
    for h_ in hs:
        nxt = []
        for (a0, a1, b0, b1) in outr:
            hx0, hx1, hy0, hy1 = max(a0, h_[0]), min(a1, h_[1]), max(b0, h_[2]), min(b1, h_[3])
            if hx0 >= hx1 or hy0 >= hy1: nxt.append((a0, a1, b0, b1)); continue
            if b0 < hy0: nxt.append((a0, a1, b0, hy0))
            if hy1 < b1: nxt.append((a0, a1, hy1, b1))
            if a0 < hx0: nxt.append((a0, hx0, hy0, hy1))
            if hx1 < a1: nxt.append((hx1, a1, hy0, hy1))
        outr = nxt
    return outr


from mathutils import Matrix
ALL = json.load(open(views_path))
DIRS = ('NORTH', 'EAST', 'SOUTH', 'WEST')
def _group_of(v):
    t = (v['view'] or '').upper()
    for d_ in DIRS:
        if t.startswith(d_ + ' ELEVATION - '): return t[len(d_ + ' ELEVATION - '):], d_
        if t.endswith(' - ' + d_ + ' WALL'): return t[:-len(' - ' + d_ + ' WALL')], d_
    return None, None


def room_walls():
    """The walls of this view's room or compartment, keyed by direction, when they close into a rectangle (a three-sided
    compartment counts: its open side faces the room)."""
    if WALLMAP: return dict(WALLMAP)
    g0, _ = _group_of(V)
    if not g0: return None
    got = {}
    for i, v in enumerate(ALL):
        g, d_ = _group_of(v)
        if g == g0 and v['room'] == V['room']: got[d_] = i
    ln = {d_: ALL[i]['length'] for d_, i in got.items()}
    def same(a_, b_): return a_ not in ln or b_ not in ln or abs(ln[a_] - ln[b_]) < 1
    if len(got) >= 3 and same('NORTH', 'SOUTH') and same('EAST', 'WEST') and ('NORTH' in ln or 'SOUTH' in ln) and ('EAST' in ln or 'WEST' in ln):
        return got
    return None


WALLS = room_walls()
ROOM_MODE = WALLS is not None and idx in WALLS.values()
if ROOM_MODE and DIMS:
    WID, DEP = DIMS
elif ROOM_MODE:
    WID = ALL[WALLS.get('NORTH', WALLS.get('SOUTH'))]['length']; DEP = ALL[WALLS.get('EAST', WALLS.get('WEST'))]['length']
else:
    WID, DEP = L, DEPTH


def wall_matrix(direction):
    """Wall-local metres (x along the wall, -y out from the face, z up) to world (X east, Y north, Z up)."""
    rot = {'NORTH': 0, 'EAST': -90, 'SOUTH': 180, 'WEST': 90}[direction]
    tr = {'NORTH': (0, DEP), 'EAST': (WID, DEP), 'SOUTH': (WID, 0), 'WEST': (0, 0)}[direction]
    return Matrix.Translation((tr[0] * IN, tr[1] * IN, 0)) @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Translation((SHIFT.get(direction, 0.0) * IN, 0, 0))


# builders that build their children themselves; a child call under one of these is not built again (a parent missing from this set, such
# as door_pair (jamb only) or vanity_furniture (no faucet), relies on its children being built)
OWNS_CHILDREN = {'filler_panel', 'sink_cab', 'window', 'outlet_splash', 'undercounter_appliance', 'door_pair_cab', 'single_door_cab',
                 'drawer_stack', 'veneer_door'}
PORTALS = []
# ---- joint audit (owner 11.09.26 night: "joints between cabinets and walls flush with no differences in width / height that are not
# intentionally supposed to be there"). Every box that forms a face of the millwork is listed per wall in wall inches before the
# wall transform; neighbours that touch along the wall are compared: a face-plane step, a top or bottom step, or a sliver gap is
# written to OUT.joints.txt. Intentional steps (a counter edge 1 in. proud, the toe) are other groups and are not compared.
JOINT_AUDIT = []
AUDIT_NAMES = {'carcass': 'body', 'filler_panel': 'body', 'column_panel': 'body', 'wall_column': 'body', 'ff': 'body',
               'wall_soffit': 'soffit', 'toe': 'toe'}
def _local_bbox(o):
    xs = [v.co.x / IN for v in o.data.vertices]; ys = [v.co.z / IN for v in o.data.vertices]; ds = [-v.co.y / IN for v in o.data.vertices]
    return (min(xs), max(xs), min(ys), max(ys), min(ds), max(ds))

def joint_report(path):
    lines = []; n = 0
    for view, items in JOINT_AUDIT:
        for grp in ('body', 'soffit', 'toe'):
            its = sorted([it for it in items if AUDIT_NAMES[it[0]] == grp], key=lambda t: t[1])
            for i, a in enumerate(its):
                covered = []
                for b in its[i + 1:]:
                    if b[1] > a[2] + 1.0: break
                    if min(a[4], b[4]) - max(a[3], b[3]) < 1.0: continue          # not side by side
                    lo_, hi_ = max(a[3], b[3]), min(a[4], b[4])
                    if any(c0 <= lo_ + 0.5 and hi_ - 0.5 <= c1 for c0, c1 in covered): continue   # a nearer piece already meets a here
                    if b[1] < a[2] - 0.5: continue                                   # overlapping along the wall, not a joint
                    gap = b[1] - a[2]
                    if -0.02 <= gap <= 1.0:
                        # intentional by the drawing: a 1/8 in. reveal between leaves, and a base under a counter beside a column whose face
                        # is flush with the counter edge (the range wall, owner 11.09.26 PM)
                        under_ctr = {a[0], b[0]} & {'wall_column', 'column_panel'} and min(a[4], b[4]) <= 35.0 and abs(a[6] - b[6]) <= 1.01
                        if abs(a[6] - b[6]) > 0.06 and not under_ctr:
                            lines.append(f'{view}: {grp} FACE STEP {abs(a[6] - b[6]):.2f} in. at x {a[2]:.2f} ({a[0]} face {a[6]:.2f} / {b[0]} face {b[6]:.2f})'); n += 1
                        if 0.14 < gap <= 1.0:
                            lines.append(f'{view}: {grp} GAP {gap:.2f} in. between {a[0]} and {b[0]} at x {a[2]:.2f}, y {max(a[3], b[3]):.1f} to {min(a[4], b[4]):.1f}'); n += 1
                        if grp == 'body' and abs(a[4] - b[4]) > 0.06 and abs(a[4] - b[4]) < 3.0:
                            lines.append(f'{view}: body TOP STEP {abs(a[4] - b[4]):.2f} in. at x {a[2]:.2f} ({a[0]} top {a[4]:.2f} / {b[0]} top {b[4]:.2f})'); n += 1
                        covered.append((max(a[3], b[3]), min(a[4], b[4])))           # the nearest neighbour only, per height band
    # any two meshes occupying exactly the same box are a duplicate build: they render as black (shared faces with the bevel shader)
    from mathutils import Vector as _V2
    seen_ = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render: continue
        bb = [o.matrix_world @ _V2(c) for c in o.bound_box]
        key = tuple(round(f(getattr(p_, ax) for p_ in bb) / IN * 20) for ax in 'xyz' for f in (min, max))
        if key in seen_ and (key[1] - key[0]) * (key[3] - key[2]) * (key[5] - key[4]) > 0:
            lines.append(f'DUPLICATE {o.name} and {seen_[key]} occupy the same box (inches {[k / 20 for k in key]})'); n += 1
        else: seen_[key] = o.name
    open(path, 'w').write('\n'.join(lines) + ('\n' if lines else 'no unintended steps or gaps\n'))
    print('joint audit:', n, 'findings ->', path)

def build_wall(vi, M, front_room_depth):
    global V, roles
    V = ALL[vi]
    roles = dict(room['roles'])
    for pat, ov in room.get('views', {}).items():
        if fnmatch.fnmatch((V['view'] or '').upper(), pat): roles.update(ov)
    before = set(bpy.data.objects)
    Lw = float(V['length'])
    hs = [(o['x0'], o['x1'], o['y0'], o['y1']) for o in V['openings'] if 'x0' in o and o.get('ctx', [''])[0] == o['kind']]
    if not any(o.get('kind') == 'door' for o in V['openings']):   # an arched pair drawn by component: its wall hole up to the apex
        hs += [(c['args']['x'], c['args']['x'] + c['args']['w'], 0.0, c['args']['spring'] + c['args']['w'] / 2)
               for c in V.get('calls', []) if c['comp'] == 'arched_door_pair' and c['depth'] == 0]
    for i, r in enumerate(subtract((-6.0, Lw + 6.0, 0.0, H), hs)):
        box(r[0], r[1], r[2], r[3], -6.0, 0.0, wall_mat(), 'wall')
    PORTALS.clear()
    glass_doors = [c['args'] for c in V.get('calls', []) if c['comp'] == 'door_leaf' and c.get('args', {}).get('panels') == 'glass']
    for o in V['openings']:
        if 'x0' in o and o.get('ctx', [''])[0] == o['kind'] and o['kind'] not in ('niche', 'window'):
            ext = any(g['x'] - 1 <= o['x0'] and o['x1'] <= g['x'] + g['w'] + 1 for g in glass_doors)
            if ext:   # a full-lite door is a terrace door (the generators draw interior doors paneled): outside is beyond it
                PORTALS.append((o['x0'] + 2, o['x1'] - 2, 9.0, o['y1'] - 5, -3.0))
                continue
            box(o['x0'] - 24, o['x1'] + 24, 0, H, -60, -59, wall_mat(), 'beyond')
            box(o['x0'] - 24, o['x1'] + 24, -2, 0, -60, 0, material(R('floor', 'WD-01')), 'beyond_floor')
    for c in V.get('calls', []):
        fn = BUILDERS.get(c['comp'], 'missing')
        if c['comp'] in SKIP: continue
        if c.get('parent') in OWNS_CHILDREN: continue   # that parent's builder builds its own children: building them again stacked a second
                                                         # toe under every filler (black slots, 11.09.26), a second sink door pair, outlet, casing
        if fn == 'missing':
            if c['depth'] == 0: MISSING.add(c['comp'])
            continue
        if fn is None: continue
        if 'error' in c: MISSING.add(c['comp'] + ' (args not captured)'); continue
        fn(c['args'], c); BUILT.add(c['comp'])
    for (x0, x1, y0, y1, d) in list(PORTALS):    # daylight through the windows: a light portal in each opening
        ld = bpy.data.lights.new('portal', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = (x1 - x0) * IN; ld.size_y = (y1 - y0) * IN
        ld.cycles.is_portal = True
        po = bpy.data.objects.new('portal', ld); bpy.context.collection.objects.link(po)
        po.location = ((x0 + x1) / 2 * IN, -d * IN, (y0 + y1) / 2 * IN); po.rotation_euler = (math.radians(-90), 0, 0)
        WINDOWS.append(((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, M))
    JOINT_AUDIT.append((V['view'], [(o.name.split('.')[0], *_local_bbox(o)) for o in set(bpy.data.objects) - before
                                    if o.type == 'MESH' and o.name.split('.')[0] in AUDIT_NAMES and not o.hide_render]))
    for o in set(bpy.data.objects) - before:
        o.matrix_world = M @ o.matrix_world; o['wall_view'] = vi


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
WINDOWS = []
if ROOM_MODE:
    for d_ in DIRS:
        if d_ in WALLS: build_wall(WALLS[d_], wall_matrix(d_), DEP if d_ in ('NORTH', 'SOUTH') else WID)
    # a corner column seen in two elevations is drawn in both: build it once. Two copies in the same place overlap face for face
    # and render as a black slot (the kitchen's NW corner, 11.09.26).
    from mathutils import Vector as _V
    _cols = {}
    for o in bpy.data.objects:
        if o.get('col_id') is not None and o.type == 'MESH' and (o.name.startswith('column_panel') or o.name.startswith('wall_column')):
            bb = [o.matrix_world @ _V(c) for c in o.bound_box]
            _cols[o['col_id']] = tuple(round(f(getattr(p_, ax) for p_ in bb) / IN) for ax in 'xyz' for f in (min, max))
    _seen = []; _drop = set()
    for cid in sorted(_cols):
        if any(all(abs(a_ - b_) <= 2 for a_, b_ in zip(_cols[cid], k_)) for k_ in _seen): _drop.add(cid)
        else: _seen.append(_cols[cid])
    for o in bpy.data.objects:
        if o.get('col_id') in _drop: o.hide_render = True   # hidden, not removed: removing segfaulted later passes
    if _drop: print('duplicate corner columns built once:', sorted(_drop))
    joint_report(out + '.joints.txt')
    if os.environ.get('PR_DUMP'):   # debugging: list the objects inside a world box (inches) and stop before rendering
        bx_ = [float(t) for t in os.environ['PR_DUMP'].split(',')]
        for o in bpy.data.objects:
            if o.type != 'MESH': continue
            bb = [o.matrix_world @ _V(c) for c in o.bound_box]
            lo_ = [min(getattr(p_, a_) for p_ in bb) / IN for a_ in 'xyz']; hi_ = [max(getattr(p_, a_) for p_ in bb) / IN for a_ in 'xyz']
            if all(lo_[i] < bx_[2 * i + 1] and hi_[i] > bx_[2 * i] for i in range(3)):
                print('DUMP', o.name, o.hide_render, [round(v, 2) for v in lo_], [round(v, 2) for v in hi_], o.active_material.name if o.active_material else '')
        sys.exit(0)
    OPEN_SIDES = [d_ for d_ in DIRS if d_ not in WALLS and (not WALLMAP or d_ in OPEN)]
    PLAIN_SIDES = [d_ for d_ in DIRS if WALLMAP and d_ not in WALLS and d_ not in OPEN]
    V = ALL[idx]; roles = dict(room['roles'])
    for pat, ov in room.get('views', {}).items():
        if fnmatch.fnmatch((V['view'] or '').upper(), pat): roles.update(ov)
    cam_dir = next(d_ for d_ in DIRS if WALLS[d_] == idx)
    M_cam = wall_matrix(cam_dir); depth_here = DEP if cam_dir in ('NORTH', 'SOUTH') else WID
    floor_rect = (0, WID, 0, DEP)
else:
    OPEN_SIDES = []
    cam_dir = None; M_cam = Matrix.Identity(4); depth_here = DEPTH
    build_wall(idx, Matrix.Identity(4), DEPTH)
    b_ = box(-12, -0.001, 0, H, 0, DEPTH, wall_mat(), 'return_l'); b_ = box(L + 0.001, L + 12, 0, H, 0, DEPTH, wall_mat(), 'return_r')
    box(-12, L + 12, 0, H, DEPTH, DEPTH + 6, wall_mat(), 'front_wall')
    floor_rect = None

# floor and ceiling (world coordinates: X east, Y north)
def world_box(x0, x1, y0, y1, z0, z1, mat, name):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    me = bpy.data.meshes.new(name); me.from_pydata([(a_ * IN, b_ * IN, c_ * IN) for a_, b_, c_ in v], [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o
if floor_rect:
    for d_ in (PLAIN_SIDES if ROOM_MODE else []):
        r_ = {'NORTH': (-6, WID + 6, DEP, DEP + 6), 'SOUTH': (-6, WID + 6, -6, 0), 'EAST': (WID, WID + 6, -6, DEP + 6), 'WEST': (-6, 0, -6, DEP + 6)}[d_]
        world_box(r_[0], r_[1], r_[2], r_[3], 0, H, wall_mat(), 'wall_plain')
    world_box(-12, WID + 12, -12, DEP + 12, -2, 0, material(R('floor', 'WD-01')), 'floor')
    world_box(-12, WID + 12, -12, DEP + 12, H, H + 4, material(R('ceiling', 'PT-01')), 'ceiling')
else:
    box(-12, L + 12, -2, 0, -6, DEPTH + 6, material(R('floor', 'WD-01')), 'floor')
    box(-12, L + 12, H, H + 4, -6, DEPTH + 6, material(R('ceiling', 'PT-01')), 'ceiling')

# ------------------------------------------------------------------ light
# daylight: a clear Miami sky outside the windows (Nishita, sun disc off: the sun is its own lamp), light portals in the
# window openings; an afternoon sun through them; recessed 3000 K downlights 20 in. off each long wall wash the walls in
# soft scallops, the sconces are on.
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
# outside the windows: a neutral daylight environment (a white studio HDRI). A Nishita sky was tried: its saturated blue
# through one window lit the wall in cyan patches beside the warm downlights, and no white balance fixes two colors at once
env = w.node_tree.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(ASSETS, 'white_home_studio_2k.hdr'))
w.node_tree.links.new(env.outputs['Color'], w.node_tree.nodes['Background'].inputs['Color'])
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 12.0
if WINDOWS:
    sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 10.0; sun_d.angle = math.radians(0.6); sun_d.color = (1.0, 0.96, 0.9)
    sun_o = bpy.data.objects.new('sun', sun_d); bpy.context.collection.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(90 - 48), 0, math.radians(-25))   # afternoon sun from the south-west, heading north-east
else:
    # no window on this room's walls: the soft key of a window behind the viewer
    pass
DOWN = []
def downlight(X, Y, watts=1.5, cone=70):
    ld = bpy.data.lights.new('downlight', 'SPOT'); ld.energy = watts; ld.spot_size = math.radians(cone); ld.spot_blend = 0.55
    ld.shadow_soft_size = 1.25 * IN; ld.use_nodes = True
    bb = ld.node_tree.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = 3500
    ld.node_tree.links.new(bb.outputs['Color'], ld.node_tree.nodes['Emission'].inputs['Color'])
    o = bpy.data.objects.new('downlight', ld); bpy.context.collection.objects.link(o); o.location = (X * IN, Y * IN, (H - 0.5) * IN)
    o.visible_glossy = False; DOWN.append(o)
    world_box(X - 2.0, X + 2.0, Y - 2.0, Y + 2.0, H - 0.05, H, material('TRIM-RING'), 'trim_ring')
    if LIGHTPLAN:   # the lit lens is seen, as in a photograph of the room with the lights on (owner 11.09.26 PM: "you see all lights")
        world_box(X - 1.6, X + 1.6, Y - 1.6, Y + 1.6, H - 0.08, H - 0.04, material('LENS'), 'downlight_lens')
MATS.setdefault('TRIM-RING', {'hex': '#F4F3EF', 'rough': 0.3, 'kind': 'plastic'})
MATS.setdefault('LENS', {'kind': 'lamp', 'emit': 6.0})
if floor_rect and LIGHTPLAN:
    for l_ in LIGHTPLAN:
        if l_['type'] == 'recess': downlight(l_['X'], l_['Y'], watts=4.0, cone=75)    # soft pools, nothing overpowering
elif floor_rect:
    n_ = max(1, int(round(WID / 48)))
    rows_ = (DEP - 20, 20) if DEP >= 60 else (DEP / 2,)
    for i in range(n_):
        for Y in rows_: downlight(WID * (i + 0.5) / n_, Y)
    # an open side (a compartment off the room) is lit by the room beyond it
    for d_ in OPEN_SIDES:
        span = WID if d_ in ('NORTH', 'SOUTH') else DEP
        ld = bpy.data.lights.new('room_beyond', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = span * IN; ld.size_y = H * 0.8 * IN; ld.energy = 40.0
        ld.color = (1.0, 0.97, 0.93); o = bpy.data.objects.new('room_beyond', ld); bpy.context.collection.objects.link(o); o.visible_glossy = False
        pos = {'NORTH': (WID / 2, DEP + 30), 'SOUTH': (WID / 2, -30), 'EAST': (WID + 30, DEP / 2), 'WEST': (-30, DEP / 2)}[d_]
        o.location = (pos[0] * IN, pos[1] * IN, H * 0.5 * IN)
        o.rotation_euler = (Vector((WID / 2, DEP / 2, H * 0.45)) * IN - o.location).normalized().to_track_quat('-Z', 'Y').to_euler()
else:
    for i in range(max(2, int(round(L / 48)))):
        X = L * (i + 0.5) / max(2, int(round(L / 48))); downlight(X, -20)   # single-wall mode: local coords are X along, -Y out
        DOWN[-1].location = (X * IN, -20 * IN, (H - 0.5) * IN)
    area('fill_window', 72, 54, 60.0, (L * 0.5, H * 0.55, DEPTH - 2.0), (L * 0.5, H * 0.45, 0.0))

ONLY = os.environ.get('PR_ONLY')     # debugging: render with one light only (sun, downlight, lamp, world)
if ONLY:
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT' and not o.name.startswith(ONLY) and o.data.type != 'AREA' or (o.type == 'LIGHT' and o.data.type == 'AREA' and not o.data.cycles.is_portal and not o.name.startswith(ONLY)): o.hide_render = True
    if ONLY != 'world': w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
    for m_ in bpy.data.materials:
        if m_.name == 'LAMP' and ONLY != 'lamp': m_.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.0

# ------------------------------------------------------------------ staging: what makes a room look lived in for the picture
def import_model(name, height_in, X, Y, Z, rot_deg=0.0):
    """A CC0 Poly Haven model (render/assets/models), scaled to a height in inches, its base centred on (X, Y, Z) plan inches."""
    try: bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
    except Exception: pass
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, 'models', name, name + '.gltf'))
    new = [o for o in set(bpy.data.objects) - before]
    meshes = [o for o in new if o.type == 'MESH']
    if not meshes: return
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
    cx_, cy_ = (min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    k = height_in * IN / max(zmax - zmin, 1e-6)
    roots = [o for o in new if o.parent is None]
    for o in roots:
        o.matrix_world = (Matrix.Translation((X * IN, Y * IN, Z * IN)) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z') @ Matrix.Scale(k, 4)
                          @ Matrix.Translation((-cx_, -cy_, -zmin)) @ o.matrix_world)
    STAGED.append(name)


def soft_box(x0, x1, y0, y1, z0, z1, mat, radius_in, name):
    """A soft-edged object (a folded towel, a cushion) in plan inches: a box with a real rounded bevel."""
    o = world_box(x0, x1, y0, y1, z0, z1, mat, name)
    bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = radius_in * IN; bv.segments = 4; bv.limit_method = 'NONE'
    for pg in o.data.polygons: pg.use_smooth = True
    return o


STAGED = []
def stage_bath():
    """Master bath dressing (placeholder styling, captioned as such): folded towels and a vase on the vanity tops, hand
    towels on the vanity bars, a small plant. Positions come from the north wall's own vanity and towel bar calls."""
    vn = ALL[WALLS['NORTH']]
    vans = [c['args'] for c in vn['calls'] if c['comp'] == 'vanity_furniture' and c['depth'] == 0]
    bars = [c['args'] for c in vn['calls'] if c['comp'] == 'towel_bar' and c['depth'] == 0]
    tw = material('TOWEL')
    for i, a in enumerate(vans):
        top = a['h'] + a['counter']; Yf = DEP - 21.0          # the vanity front, plan Y
        if i == 0:
            x0 = a['x'] + 3
            for k in range(3):
                soft_box(x0, x0 + 11, Yf - 1 - 8, Yf - 1, top + k * 1.5, top + (k + 1) * 1.5 - 0.1, tw, 0.45, 'towel_stack')
            import_model('ceramic_vase_01', 9.0, a['x'] + a['w'] - 7, DEP - 6, top, 20)
        else:
            import_model('potted_plant_04', 11.0, a['x'] + a['w'] - 7, DEP - 7, top, 0)
            import_model('wooden_bowl_01', 2.2, a['x'] + 9, DEP - 8, top, 0)
    for a in bars:
        cx_, y_, w_ = a['cx'], a.get('y', 30), a.get('w', 24)
        Yb = DEP - 21.0 - 2.6                                    # bar centre, in front of the vanity face
        hw = min(16.0, w_ - 4)
        cyl_w = bpy.data.objects
        soft_box(cx_ - hw / 2, cx_ + hw / 2, Yb - 1.0, Yb - 0.45, y_ - 15, y_ + 0.6, tw, 0.2, 'hand_towel_front')
        soft_box(cx_ - hw / 2, cx_ + hw / 2, Yb + 0.45, Yb + 1.0, y_ - 9, y_ + 0.6, tw, 0.2, 'hand_towel_back')
        soft_box(cx_ - hw / 2, cx_ + hw / 2, Yb - 1.0, Yb + 1.0, y_ + 0.2, y_ + 1.1, tw, 0.45, 'hand_towel_fold')


exec(open(os.path.join(HERE, 'stages.py')).read())
if PERSP:
    if STAGE == 'bath' and ROOM_MODE: stage_bath()
    elif STAGE in STAGES: STAGES[STAGE]()
    if ROOM_MODE: joint_report(out + '.joints.txt')   # again with the staging (island, built-ins) in, so its duplicates are caught too
    if os.environ.get('PR_STAGECHECK'): print('stage built, objects', len(bpy.data.objects)); sys.exit(0)   # build-only check
    cam_d = bpy.data.cameras.new('cam'); cam_d.type = 'PERSP'; cam_d.lens = LENS; cam_d.sensor_width = 36.0; cam_d.sensor_fit = 'HORIZONTAL'
    cam_d.clip_start = max(0.01, CLIP * IN); cam_d.clip_end = 60.0
    cam = bpy.data.objects.new('cam', cam_d); bpy.context.collection.objects.link(cam)
    loc = Vector((PERSP[0] * IN, PERSP[1] * IN, PERSP[2] * IN)); tgt_ = Vector((PERSP[3] * IN, PERSP[4] * IN, PERSP[5] * IN))
    # verticals stay vertical: the camera is levelled and the target height is reached with lens shift, never by tilting
    d_ = tgt_ - loc; flat = Vector((d_.x, d_.y, 0.0))
    cam.rotation_euler = flat.normalized().to_track_quat('-Z', 'Y').to_euler()
    W_r, H_r = RES; hfov = 2 * math.atan(18.0 / LENS)
    big_fov = 2 * math.atan(18.0 / LENS * max(W_r, H_r) / W_r)   # Blender shifts in units of the larger image side (portrait: the height)
    rise = d_.z / max(flat.length, 1e-6)                       # tangent of the angle to the target above the horizon
    cam_d.shift_y = rise / (2 * math.tan(big_fov / 2))
    cam.location = loc; sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = W_r, H_r
    # the garden outside the windows: an outdoor HDRI in place of the studio one, so the glass shows planting and sky
    env.image = bpy.data.images.load(os.path.join(ASSETS, 'green_sanctuary_2k.hdr'))
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5 if DUSK else 7.0
    # late-afternoon sun, low from the west-southwest, through the windows and glass doors: long patches on the floor and
    # the lower walls, the contrast every interior photograph is built on
    if not LIGHTS_ON:   # a daytime photograph: downlights off, sconces on low
        for o in DOWN: o.hide_render = True
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o.data.type == 'SUN':
            o.data.energy = 0.0 if DUSK else 22.0; o.data.angle = math.radians(1.2)
            el_, az_ = SUN if SUN else (32.0, 250.0)
            o.rotation_euler = (math.radians(90 - el_), 0, math.radians(180 - az_))
    for o in bpy.data.objects:                                   # walls for the exposure mask
        if o.type == 'MESH' and o.name.startswith('wall'): o.pass_index = 1
else:
    cam_d = bpy.data.cameras.new('cam'); cam_d.type = 'ORTHO'; cam_d.sensor_fit = 'HORIZONTAL'; cam_d.ortho_scale = L * IN
    # the camera sees only the 36 in. in front of this wall (deeper than anything mounted on it); the rest of the room is
    # clipped from view but still lights, shades and shows in the mirrors
    cam_d.clip_start = max(0.01, (depth_here - 4 - 36) * IN); cam_d.clip_end = (depth_here + 12) * IN
    cam = bpy.data.objects.new('cam', cam_d); bpy.context.collection.objects.link(cam)
    cam.matrix_world = M_cam @ (Matrix.Translation((L / 2 * IN, -(depth_here - 4) * IN, H / 2 * IN)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    sc.camera = cam
    if ROOM_MODE:
        # the side walls' crown, base and trim would show end-on at the frame edges as dark profiles: hidden from the camera only
        for o in bpy.data.objects:
            if o.type == 'MESH' and o.get('wall_view') is not None and o['wall_view'] != idx: o.visible_camera = False


sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01
try: sc.cycles.sampling_pattern = 'BLUE_NOISE'
except Exception: pass
sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'; sc.cycles.denoising_prefilter = 'ACCURATE'
sc.cycles.max_bounces = 8; sc.cycles.diffuse_bounces = 4; sc.cycles.glossy_bounces = 4; sc.cycles.sample_clamp_indirect = 8.0
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
sc.view_settings.view_transform = 'Khronos PBR Neutral'; sc.view_settings.look = 'None'
if PERSP:
    # a photograph, not a chip: AgX rolls the sun patches and the window off like film; the grey card still sets the wall
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.view_layers[0].use_pass_object_index = True
else:
    sc.render.resolution_x, sc.render.resolution_y = int(round(L * PPI)), int(round(H * PPI))
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'


WALL_MASK = None
def wall_mask(W_, H_):
    """Bare-wall pixels: the view minus every captured primitive's footprint (grown 3 in.), the crown and base bands."""
    from math import floor
    k = W_ / L; grid = [[True] * W_ for _ in range(H_)]
    def off(x0, y0, x1, y1):
        for yy in range(max(0, int(floor((H - y1) * k))), min(H_, int((H - y0) * k) + 1)):
            row = grid[yy]
            for xx in range(max(0, int(floor(x0 * k))), min(W_, int(x1 * k) + 1)): row[xx] = False
    for p_ in V['prims']:
        if p_.get('dash') or 'view.rect' in p_['ctx']: continue
        if p_['t'] == 'rect': (x0, y0), (x1, y1) = p_['pts']
        elif p_['t'] == 'ellipse': (cx_, cy_), (rx, ry) = p_['pts']; x0, y0, x1, y1 = cx_ - rx, cy_ - ry, cx_ + rx, cy_ + ry
        else: xs = [q[0] for q in p_['pts']]; ys = [q[1] for q in p_['pts']]; x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        off(x0 - 3, y0 - 3, x1 + 3, y1 + 3)
    for o in V['openings']:
        if 'x0' in o: off(o['x0'] - 7, o['y0'] - 1, o['x1'] + 7, o['y1'] + 7)
    off(-1, H - T['crown'] - 3, L + 1, H + 1); off(-1, -1, L + 1, T['base'] + 3); off(-1, -1, 2, H + 1); off(L - 2, -1, L + 1, H + 1)
    return grid


def measure_wall(path):
    """Median linear RGB of the bare-wall pixels (ortho: the mask from the captured primitives; perspective: the walls'
    object index pass written beside the calibration render)."""
    img = bpy.data.images.load(path); px = list(img.pixels); W_, H_ = img.size
    if PERSP:
        mi = bpy.data.images.load(MASK_PATH, check_existing=False); mp_ = list(mi.pixels)
        mask = [[mp_[((H_ - 1 - yy) * W_ + xx) * 4] > 0.5 for xx in range(W_)] for yy in range(H_)]
    else:
        mask = wall_mask(W_, H_)
    vals = []
    for yy in range(H_):
        row = H_ - 1 - yy
        for xx in range(0, W_, 2):
            if mask[yy][xx]:
                i = (row * W_ + xx) * 4; vals.append((lin(px[i]), lin(px[i + 1]), lin(px[i + 2])))
    print('wall pixels measured', len(vals))
    if not vals: return (0.5, 0.5, 0.5)
    return tuple(sorted(v[c] for v in vals)[len(vals) // 2] for c in range(3))


WALL_EXPOSURE = 0.74   # the median bare wall is set to 74 % of its paint value: a lit wall photographs a little under its chip,
                       # which leaves trim whites and lit shades their highlight range instead of clipping

# exposure and white balance, the way a photographer uses a grey card: a quick pass, then the bare wall under the crown
# is brought to its paint colour (per-channel gain in scene-linear, before the view transform). Floor bounce and warm
# lamps no longer tint the paint; everything else keeps its colour relative to the wall.
tgt = [WALL_EXPOSURE * v for v in (MATS.get(R('wall', 'PT-02'), {}).get('lin') or hex_lin(MATS.get(R('wall', 'PT-02'), {}).get('hex', '#BCBCBC')))]
sc.view_settings.exposure = 0.0
sc.use_nodes = True; ntc = sc.node_tree
for nd in list(ntc.nodes): ntc.nodes.remove(nd)
rl = ntc.nodes.new('CompositorNodeRLayers'); cb = ntc.nodes.new('CompositorNodeColorBalance'); co = ntc.nodes.new('CompositorNodeComposite')
cb.correction_method = 'OFFSET_POWER_SLOPE'; cb.slope = (1.0, 1.0, 1.0)
ntc.links.new(rl.outputs['Image'], cb.inputs['Image']); ntc.links.new(cb.outputs['Image'], co.inputs['Image'])
MASK_PATH = None
if PERSP:
    idm = ntc.nodes.new('CompositorNodeIDMask'); idm.index = 1; idm.use_antialiasing = False
    fo = ntc.nodes.new('CompositorNodeOutputFile'); fo.base_path = out + '_mask'; fo.file_slots[0].path = 'mask'
    fo.format.file_format = 'PNG'; fo.format.color_mode = 'RGB'
    ntc.links.new(rl.outputs['IndexOB'], idm.inputs['ID value']); ntc.links.new(idm.outputs['Alpha'], fo.inputs[0])
    MASK_PATH = os.path.join(out + '_mask', 'mask%04d.png' % sc.frame_current)
    WALL_EXPOSURE = 0.82     # a bright interior photograph; the sun patches roll off in AgX
    tgt = [WALL_EXPOSURE * v for v in (MATS.get(R('wall', 'PT-02'), {}).get('lin') or hex_lin(MATS.get(R('wall', 'PT-02'), {}).get('hex', '#BCBCBC')))]
sc.render.resolution_percentage = 25; sc.cycles.samples = 24; sc.render.filepath = out + '.cal.png'
gain = [1.0, 1.0, 1.0]
for it in range(4):   # measured after the view transform, so iterate: highlight roll-off makes one step undershoot
    bpy.ops.render.render(write_still=True)
    got = measure_wall(out + '.cal.png')
    err = max(abs(got[c] / tgt[c] - 1) for c in range(3))
    print('cal pass', it, 'wall', [round(v, 4) for v in got], 'paint', [round(v, 4) for v in tgt], 'err', round(err, 4))
    if err < 0.015: break
    gain = [gain[c] * tgt[c] / max(got[c], 1e-4) for c in range(3)]
    g_mid = sorted(gain)[1]
    lim = 1.6 if PERSP else 2.2          # a perspective keeps some of the light's own warmth, as a photograph does
    if max(gain) / min(gain) > lim:      # more than a strong white-balance correction: the light is wrong, not the camera
        print('WARNING white balance outside a plausible range', [round(g, 3) for g in gain], '- clamped')
        gain = [min(max(g, g_mid / lim ** 0.5), g_mid * lim ** 0.5) for g in gain]
    cb.slope = gain
print('gain', [round(v, 3) for v in gain])
if PERSP and MASK_PATH:
    for nd in list(ntc.nodes):
        if nd.bl_idname in ('CompositorNodeOutputFile', 'CompositorNodeIDMask'): ntc.nodes.remove(nd)
if not PREVIEW:
    sc.render.resolution_percentage = 100; sc.cycles.samples = SAMPLES
else:
    sc.render.resolution_percentage = 50; sc.cycles.samples = 48
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('rendered', out, sc.render.resolution_x * sc.render.resolution_percentage // 100, 'built', sorted(BUILT), 'MISSING', sorted(MISSING), 'staged', STAGED)
