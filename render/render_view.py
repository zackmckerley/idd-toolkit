"""Render one captured elevation view in Blender (run with the bpy venv, Python 3.11):
    /home/claude/rendervenv/bin/python render/render_view.py views.json INDEX out.png [--samples 128] [--ppi auto]

Orthographic rendered elevation: the wall is a plane with its openings cut, every captured primitive is a slab standing
off the wall by its component's depth, materials come from the room's finish roles, one sun rakes from the upper left so
mouldings, panels, counters and trim cast readable shadows. The image is framed exactly to the view (wall length x
ceiling at `ppi` pixels per wall inch), so it lands on the PDF view rect with no rescaling of the drawing.

Settings and why (sources in the skill's rendering notes):
- Light: the classic shade-and-shadow convention. Rays run along the cube diagonal from over the viewer's left shoulder
  (travel direction right, into the wall, down, all equal), so a moulding that projects d inches throws a shadow d inches
  right and d inches down: depth reads off the drawing. Every face that sees the sun gets the same light (cos 54.7 deg).
- Colour: view transform Standard, look None. AgX and Filmic shift and desaturate paint colours; Standard leaves a lit
  face at its paint value once exposure is calibrated (CAL below: a lit face of albedo a renders at a, measured).
- Resolution: --ppi auto = 300 dpi on the printed 11x17 (page points per wall inch x 17/1892 x 300).
- Noise: adaptive sampling 0.01, blue-noise pattern, OpenImageDenoise with albedo and normal, accurate prefilter."""
import bpy, json, math, sys, fnmatch, os
from mathutils import Vector

IN = 0.0254
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
views_path, idx, out = args[0], int(args[1]), args[2]
SAMPLES = int(args[args.index('--samples') + 1]) if '--samples' in args else 128
HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(views_path))[idx]
_ppi = args[args.index('--ppi') + 1] if '--ppi' in args else 'auto'
PPI = float(V['k']) * 17.0 / 1892.0 * 300.0 if _ppi == 'auto' else float(_ppi)
SUN_E, WORLD_E = 2.6, 0.45       # key to fill: shadows at about 35 percent of the lit value, measured on the test wall
CAL = float(json.load(open(os.path.join(HERE, 'calibration.json')))['exposure']) if os.path.exists(os.path.join(HERE, 'calibration.json')) else 0.0
MATS = json.load(open(os.path.join(HERE, 'materials.json')))
ROOMS = json.load(open(os.path.join(HERE, 'room_finishes.json')))
L, H = float(V['length']), float(V['ceiling'])

room = ROOMS.get(V['room'] or '', {'roles': {}, 'views': {}})
roles = dict(room['roles'])
for pat, ov in room.get('views', {}).items():
    if fnmatch.fnmatch((V['view'] or '').upper(), pat): roles.update(ov)

# component -> (front depth in inches from the wall face, role); negative = recessed into the wall
COMP = {
    'base': (0.875, 'trim'), 'crown': (6.0, 'crown'), 'casing': (1.0, 'trim'), 'chair_rail': (1.25, 'trim'),
    'door_leaf': (-2.0, 'door'), 'door_pair': (-2.0, 'door'), 'jib_door': (0.0, 'wall'), 'bifold': (-2.0, 'door'),
    'cased_opening': (1.0, 'trim'), 'arched_opening': (1.0, 'trim'), 'window': (1.0, 'trim'),
    'vanity_furniture': (21.0, 'vanity'), 'vanity_floating': (21.0, 'vanity'), 'vanity_end': (24.0, 'vanity'),
    'mirror_framed': (1.5, 'mirror_frame'), 'mirror_panel': (0.5, 'mirror'), 'mirror_led': (1.0, 'mirror'),
    'sconce': (6.0, 'metal'), 'bar_light': (5.0, 'metal'), 'picture_light': (4.0, 'metal'), 'pendant': (24.0, 'metal'),
    'faucet': (6.0, 'metal'), 'faucet_wall': (7.0, 'metal'), 'tub_filler_wall': (8.0, 'metal'), 'valve': (2.0, 'metal'),
    'shower_head': (8.0, 'metal'), 'towel_bar': (3.0, 'metal'), 'towel_ring': (3.0, 'metal'), 'robe_hook': (2.0, 'metal'),
    'paper_holder': (3.0, 'metal'), 'tub_spout': (6.0, 'metal'),
    'toilet': (28.0, 'porcelain'), 'toilet_profile': (28.0, 'porcelain'), 'freestanding_tub': (32.0, 'porcelain'),
    'alcove_tub_front': (30.0, 'porcelain'), 'alcove_tub_end': (30.0, 'porcelain'),
    'outlet': (0.25, 'plate'), 'switch': (0.25, 'plate'), 'data_jack': (0.25, 'plate'),
    'niche': (-4.0, 'tile'), 'tv': (2.0, 'black'), 'art': (1.5, 'mirror_frame'),
    'panel_wall': (0.6, 'panel'), 'paneling': (0.6, 'panel'), 'nightstand': (20.0, 'vanity'), 'bed_king': (40.0, 'vanity'),
    'cabinet_lower': (20.0, 'cabinet'), 'shelves': (12.0, 'cabinet'), 'pilaster': (0.0, 'wall'),
    'shower_glass': (0.0, None), 'shower_door_centered': (0.0, None), 'shower_door_end': (0.0, None), 'glass_screen_face': (0.0, None),
    'glass_edge': (0.0, None), 'cut_wall': (0.0, None), 'drapery': (0.0, None), 'tile_grid': (0.05, 'tile'), 'stone_slab': (0.05, 'tile'),
    # kitchen
    'drawer_stack': (24.0, 'cabinet'), 'door_pair_cab': (24.0, 'cabinet'), 'single_door_cab': (24.0, 'cabinet'), 'end_panel': (24.75, 'cabinet'),
    'upper_run': (13.0, 'cabinet'), 'tall_cab': (24.0, 'cabinet'), 'column': (24.0, 'cabinet'), 'counter': (25.0, 'counter'),
    'toe': (21.0, 'black'), 'pro_range': (29.6, 'metal'), 'hood_breast': (27.0, 'wall'), 'hood_canopy': (24.0, 'wall'),
    'floating_shelf': (12.0, 'counter'), 'splash_slab': (0.75, 'counter'), 'sink_cab': (24.0, 'cabinet'), 'light_rail': (13.5, 'cabinet'),
}
SKIP_FILL_DARK = 0.35       # dark fills are poche or screens; poche is skipped, a TV is drawn by its own component


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat(code):
    m = bpy.data.materials.get(code)
    if m: return m
    spec = MATS.get(code, {'hex': '#FF00FF', 'rough': 0.5})
    if 'lin' in spec: rgb = list(spec['lin'])           # measured linear reflectance (metals), used as is
    else:
        hx = spec['hex'].lstrip('#'); rgb = [lin(int(hx[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    m = bpy.data.materials.new(code); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1.0)
    b.inputs['Roughness'].default_value = spec.get('rough', 0.5)
    b.inputs['Metallic'].default_value = spec.get('metal', 0.0)
    if 'f82' in spec: b.inputs['Specular Tint'].default_value = (*spec['f82'], 1.0)
    if spec.get('kind') == 'mirror':
        # an orthographic mirror has nothing to reflect: drawn the elevation way, pale glass with soft diagonal streaks
        tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave')
        wv.wave_type = 'BANDS'; wv.bands_direction = 'DIAGONAL'; wv.inputs['Scale'].default_value = 1.1
        wv.inputs['Distortion'].default_value = 0.0; wv.inputs['Detail'].default_value = 0.0
        cr = nt.nodes.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements
        c0 = [lin(int(spec['hex'].lstrip('#')[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
        e[0].position = 0.55; e[0].color = (*c0, 1); e[1].position = 0.85; e[1].color = (*[min(1.0, v * 1.22) for v in c0], 1)
        nt.links.new(tc.outputs['Generated'], wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'], cr.inputs['Fac'])
        nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
        b.inputs['Metallic'].default_value = 0.0; b.inputs['Roughness'].default_value = 0.35
    return m


_N = [0]
def box(x0, x1, z0, z1, d_back, d_front, code, name='b'):
    """A slab in wall inches: x along the wall, z up, d = distance in front of the wall face (camera side).
    Each slab after the first is nudged forward by a few thousandths of an inch: two coplanar faces shadow each other and render black."""
    if x1 - x0 < 0.05 or z1 - z0 < 0.05 or d_front - d_back < 0.01: return None
    _N[0] += 1; eps = (_N[0] % 40) * 0.004
    d_front += eps; d_back += eps
    me = bpy.data.meshes.new(name)
    X0, X1, Z0, Z1 = x0 * IN, x1 * IN, z0 * IN, z1 * IN
    Y0, Y1 = -d_front * IN, -d_back * IN           # camera looks along +Y from negative Y
    v = [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0), (X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me.from_pydata(v, [], f); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); ob.data.materials.append(mat(code))
    return ob


def prism(pts, d_back, d_front, code, name='p'):
    """An extruded polygon (wall inches) between two depths."""
    n = len(pts)
    if n < 3: return
    me = bpy.data.meshes.new(name)
    vs = [(x * IN, -d_front * IN, y * IN) for x, y in pts] + [(x * IN, -d_back * IN, y * IN) for x, y in pts]
    fs = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me.from_pydata(vs, [], fs); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); ob.data.materials.append(mat(code))


def subtract(rect, holes):
    """Rectangle minus rectangles, as a list of rectangles (strip decomposition)."""
    out = [rect]
    for h in holes:
        nxt = []
        for (a0, a1, b0, b1) in out:
            hx0, hx1, hy0, hy1 = max(a0, h[0]), min(a1, h[1]), max(b0, h[2]), min(b1, h[3])
            if hx0 >= hx1 or hy0 >= hy1: nxt.append((a0, a1, b0, b1)); continue
            if b0 < hy0: nxt.append((a0, a1, b0, hy0))
            if hy1 < b1: nxt.append((a0, a1, hy1, b1))
            if a0 < hx0: nxt.append((a0, hx0, hy0, hy1))
            if hx1 < a1: nxt.append((hx1, a1, hy0, hy1))
        out = nxt
    return out


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'; sc.cycles.denoising_prefilter = 'ACCURATE'
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01
try: sc.cycles.sampling_pattern = 'BLUE_NOISE'
except Exception: pass
sc.cycles.max_bounces = 6; sc.cycles.sample_clamp_indirect = 10.0
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = CAL
sc.display_settings.display_device = 'sRGB'
sc.render.resolution_x, sc.render.resolution_y = int(round(L * PPI)), int(round(H * PPI)); sc.render.resolution_percentage = 100
sc.render.film_transparent = False

# the wall, with its openings cut through
holes = [(o['x0'], o['x1'], o['y0'], o['y1']) for o in V['openings'] if 'x0' in o]
wall_code = roles.get('wall', 'PT-02')
for i, (x0, x1, y0, y1) in enumerate(subtract((0.0, L, 0.0, H), holes)):
    box(x0, x1, y0, y1, -6.0, 0.0, wall_code, 'wall%d' % i)
for o in V['openings']:
    if 'x0' not in o: continue
    back = roles.get('tile', wall_code) if o['kind'] == 'niche' else wall_code
    depth = 4.0 if o['kind'] == 'niche' else 6.0
    box(o['x0'], o['x1'], o['y0'], o['y1'], -depth - 0.5, -depth, back if o['kind'] == 'niche' else 'GLASS-DARK' if o['kind'] == 'window' else wall_code, 'reveal')
    # jamb returns so the opening reads as a recess
    box(o['x0'] - 0.01, o['x0'] + 0.01, o['y0'], o['y1'], -depth, 0.0, wall_code); box(o['x1'] - 0.01, o['x1'] + 0.01, o['y0'], o['y1'], -depth, 0.0, wall_code)
    box(o['x0'], o['x1'], o['y1'] - 0.01, o['y1'] + 0.01, -depth, 0.0, wall_code)

# primitives: per outermost component, nested rects step back (panels, glass in frames, drawer fronts in a box)
groups = []
def comp_of(ctx):
    """The innermost component the depth table knows (a casing drawn by door_pair is a casing, proud of the wall)."""
    for c in reversed(ctx):
        if c in COMP or c == 'view.rect': return c
    return ctx[0] if ctx else 'direct'
for p in V['prims']:
    comp = comp_of(p['ctx'])
    if groups and groups[-1][0] == comp and groups[-1][2] == tuple(p['ctx']): groups[-1][1].append(p)
    else: groups.append((comp, [p], tuple(p['ctx'])))
for gi, (comp, prims, ctx) in enumerate(groups):
    if comp == 'view.rect' or 'view.rect' in ctx: continue
    front, role = COMP.get(comp, (0.5, 'trim'))
    if role is None: continue
    code = roles.get(role, {'porcelain': 'PORCELAIN', 'plate': 'PLATE', 'black': 'BLACK', 'mirror': 'MIRROR'}.get(role, roles.get('trim', 'PT-01')))
    if role == 'porcelain': code = 'PORCELAIN'
    if role == 'plate': code = 'PLATE'
    if role == 'black': code = 'BLACK'
    if role == 'mirror': code = 'MIRROR'
    # pass 1: the solid rects of this component and, for each, its innermost container (a door leaf holds its panels,
    # a frame holds its glass, a cabinet face holds its drawer fronts)
    keep = []
    for p in prims:
        if p.get('fill') and max(p['fill']) < SKIP_FILL_DARK and comp not in ('tv',): continue
        if p.get('dash'): continue                      # hidden lines (a basin under the counter) are not surfaces
        if p['t'] == 'rect':
            (x0, y0), (x1, y1) = p['pts']
            if not p.get('fill') and comp in ('casing', 'cased_opening', 'window', 'arched_opening') and min(x1 - x0, y1 - y0) > 8:
                continue                                    # the outline a trim component draws around an opening is not a solid
        keep.append(p)
    rects = [p for p in keep if p['t'] == 'rect']
    def inside(a, b):
        (ax0, ay0), (ax1, ay1) = a['pts']; (bx0, by0), (bx1, by1) = b['pts']
        return a is not b and bx0 <= ax0 + 0.01 and bx1 >= ax1 - 0.01 and by0 <= ay0 + 0.01 and by1 >= ay1 - 0.01 and (bx1 - bx0) * (by1 - by0) > (ax1 - ax0) * (ay1 - ay0) + 0.01
    par = {}
    for r in rects:
        cs = [q for q in rects if inside(r, q)]
        par[id(r)] = min(cs, key=lambda q: (q['pts'][1][0] - q['pts'][0][0]) * (q['pts'][1][1] - q['pts'][0][1])) if cs else None
    def level(r):
        n = 0
        while par[id(r)] is not None: r = par[id(r)]; n += 1
        return n
    # pass 2: each rect is a slab with its children cut out, so a recessed panel, glass or drawer front is seen, set back
    # 3/8 in. per level behind its parent's face, with the parent's edge throwing a shadow on it
    for p in keep:
        if p['t'] == 'rect':
            (x0, y0), (x1, y1) = p['pts']
            lv = level(p); parent = par[id(p)]
            c = code
            if comp in ('mirror_framed',) and parent is not None: c = 'MIRROR'
            if comp == 'window' and parent is not None: c = 'GLASS-DARK'
            if comp in ('sconce', 'bar_light') and y1 - y0 > 4: c = roles.get('shade', 'SHADE')
            if comp in ('vanity_furniture', 'vanity_floating') and (y1 - y0) <= 2.0 and y1 > 30: c = roles.get('counter', 'STONE-TOP')
            if comp in ('panel_wall', 'paneling') and not p.get('fill') and parent is None:
                # picture-frame moulding: a ring, not a solid panel
                mw = 1.75
                for (a0, a1, b0, b1) in ((x0, x1, y0, y0 + mw), (x0, x1, y1 - mw, y1), (x0, x0 + mw, y0 + mw, y1 - mw), (x1 - mw, x1, y0 + mw, y1 - mw)):
                    box(a0, a1, b0, b1, 0.0, front, c, comp)
                continue
            f = front - 0.375 * lv if front > 0 else front
            b = min(0.0, f - 0.75) if f > 0 else f - 0.75
            kids = [q for q in rects if par[id(q)] is p]
            holes = [(q['pts'][0][0], q['pts'][1][0], q['pts'][0][1], q['pts'][1][1]) for q in kids]
            for (a0, a1, b0, b1) in subtract((x0, x1, y0, y1), holes):
                box(a0, a1, b0, b1, b, f, c, comp)
            for (a0, a1, b0, b1) in holes:              # the back of each opening, so nothing shows through
                box(a0, a1, b0, b1, b - 0.01, b, c, comp)
        elif p['t'] == 'ellipse':
            (cx, cy), (rx, ry) = p['pts']
            n = 24; pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
            prism(pts, front - 1.0, front + 0.25, 'MIRROR' if comp == 'mirror_framed' else code, comp)
        elif p['t'] == 'poly':
            f = front if front > 0 else 0.5
            prism(p['pts'], f - 0.75, f, code, comp)

# a floor in front of the wall, so objects sit on something
box(-24, L + 24, -1.0, 0.0, -2.0, 60.0, roles.get('floor', 'WD-01'), 'floor')

# light: the cube-diagonal convention. Camera looks along +Y, so travel = (+1 right, +1 into the wall, -1 down)
bpy.ops.object.light_add(type='SUN', location=(0, -3, 3))
sun = bpy.context.object; sun.data.energy = SUN_E; sun.data.angle = math.radians(1.0)
sun.rotation_euler = Vector((1.0, 1.0, -1.0)).normalized().to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (1, 1, 1, 1); bg.inputs['Strength'].default_value = WORLD_E
# reflections: glossy rays see a brighter sky graded light above to mid below, so metals and gloss paint read as polished
# instead of mirroring a flat grey; diffuse lighting, and so the exposure calibration, is unchanged
nt = w.node_tree; lp = nt.nodes.new('ShaderNodeLightPath'); g = nt.nodes.new('ShaderNodeBackground')
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (0.30, 0.30, 0.30, 1)
ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
nt.links.new(tc.outputs['Generated'], sep.inputs['Vector']); nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], g.inputs['Color']); g.inputs['Strength'].default_value = 1.1
mix = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(lp.outputs['Is Glossy Ray'], mix.inputs['Fac'])
nt.links.new(bg.outputs['Background'], mix.inputs[1]); nt.links.new(g.outputs['Background'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], nt.nodes['World Output'].inputs['Surface'])

# orthographic camera framed to the view exactly: horizontal fit, so ortho_scale is the wall length whatever the aspect
cam_d = bpy.data.cameras.new('cam'); cam_d.type = 'ORTHO'; cam_d.sensor_fit = 'HORIZONTAL'; cam_d.ortho_scale = L * IN
cam_d.clip_start = 0.01; cam_d.clip_end = 20
cam = bpy.data.objects.new('cam', cam_d); bpy.context.collection.objects.link(cam)
cam.location = (L / 2 * IN, -8.0, H / 2 * IN); cam.rotation_euler = (math.radians(90), 0, 0)
sc.camera = cam
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('rendered', out, sc.render.resolution_x, sc.render.resolution_y)
