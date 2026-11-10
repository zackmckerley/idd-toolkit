# Builders added 11.09.26 for the room renderings: kitchen cabinetry and appliances, the master bedroom pieces, the arched pair.
# Exec'd inside photoreal.py's namespace (box, cyl, sweep, material, R, ...), wall coordinates: x along the wall, y up, d out from the face.
import math as _m

MATS.setdefault('TOE', {'hex': '#2A2826', 'rough': 0.8, 'kind': 'paint'})
MATS.setdefault('STAINLESS', {'hex': '#B9B8B4', 'rough': 0.28, 'kind': 'metal', 'lin': [0.52, 0.51, 0.49], 'brushed': True})
MATS.setdefault('GRATE', {'hex': '#1C1C1C', 'rough': 0.45, 'kind': 'metal', 'lin': [0.03, 0.03, 0.03]})
MATS.setdefault('LED-STRIP', {'kind': 'lamp', 'emit': 2.2})   # 11.09.26 night: 6.0 blew out the shelves and darkened everything else

cab_mat = lambda: material(R('cabinet', 'CAB-01'), '-trim')
stone_mat = lambda: material(R('counter', 'STONE-TOP'))
metal_mat = lambda: material(R('metal', 'METAL-NICKEL'))


def _cab_depth(y0, y1, a=None):
    """The depth the drawing records on the call (11.09.26: the drawings now pass it); 24 in. when a call carries none."""
    return float((a or {}).get('depth') or 24.0)


def _prism(pts, d0, d1, mat, name='prism'):
    """Extrude a 2-D outline (wall x, y) from d0 to d1."""
    n = len(pts)
    v = [(x, y, d1) for x, y in pts] + [(x, y, d0) for x, y in pts]
    f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    o = obj_from(v, f, mat, name)
    me = o.data; bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return o


def _bar_pull(cx, cy, length, vertical, d, metal=None):
    metal = metal or metal_mat()
    if vertical:
        cyl(cx, cy, d + 1.1, 0.25, length, 'y', metal, 'pull')
        for yy in (cy - length / 2 + 0.6, cy + length / 2 - 0.6): cyl(cx, yy, d + 0.55, 0.2, 1.1, 'd', metal, 'post')
    else:
        cyl(cx, cy, d + 1.1, 0.25, length, 'x', metal, 'pull')
        for xx in (cx - length / 2 + 0.6, cx + length / 2 - 0.6): cyl(xx, cy, d + 0.55, 0.2, 1.1, 'd', metal, 'post')


SHAKER = 1.375   # idd_kitchen.SHAKER: the slim shaker frame (owner 11.09.26 night)


def _frame(x0, y0, x1, y1, k, d0, d1, mat, nm):
    """A rectangular frame k wide: stiles full height, rails between them, so no two pieces overlap (overlapping coplanar faces
    render black with the bevel shader: the glass doors' black corners, 11.09.26)."""
    box(x0, x0 + k, y0, y1, d0, d1, mat, nm); box(x1 - k, x1, y0, y1, d0, d1, mat, nm)
    box(x0 + k, x1 - k, y0, y0 + k, d0, d1, mat, nm); box(x0 + k, x1 - k, y1 - k, y1, d0, d1, mat, nm)


def _inset_front(x0, y0, x1, y1, D, mat=None, glass=False, style='slim_shaker', r=0.125):
    """An inset door or drawer front in its face-frame opening, a dark 1/8 in. reveal round it, flush with the frame. A slim shaker
    front is a 1-3/8 in. frame with the panel 1/4 in. back, so its inside edges read as the shaker line."""
    mat = mat or cab_mat()
    if not glass:
        box(x0, x1, y0, y1, D - 0.02, D + 0.01, material('GAP'), 'reveal')
        k = SHAKER
        if style == 'slim_shaker' and x1 - x0 > 2 * (k + r) + 2 and y1 - y0 > 2 * (k + r) + 2:
            _frame(x0 + r, y0 + r, x1 - r, y1 - r, k, D + 0.01, D + 0.31, mat, 'shaker_frame')
            box(x0 + r + k, x1 - r - k, y0 + r + k, y1 - r - k, D + 0.01, D + 0.06, mat, 'shaker_panel')
        else:
            box(x0 + r, x1 - r, y0 + r, y1 - r, D + 0.01, D + 0.31, mat, 'front')
        return
    _frame(x0 + r, y0 + r, x1 - r, y1 - r, 1.75, D - 0.69, D + 0.31, mat, 'glass_frame')
    box(x0 + r + 1.75, x1 - r - 1.75, y0 + r + 1.75, y1 - r - 1.75, D - 0.3, D - 0.25, material('GLASS-CLEAR'), 'glass')


def _carcass(x, w, y0, y1, D, interior=False):
    if interior:   # a glass cabinet: the carcass is hollow, a painted interior with two shelves and a lit top; the sides stop 3/4 in.
        m = cab_mat()  # short of the face so the face frame owns the front (no shared faces)
        box(x, x + w, y0, y1, 0.0, 0.75, m, 'cab_back')
        box(x, x + 0.75, y0, y1, 0.75, D - 0.75, m, 'cab_side'); box(x + w - 0.75, x + w, y0, y1, 0.75, D - 0.75, m, 'cab_side')
        box(x + 0.75, x + w - 0.75, y0, y0 + 0.75, 0.75, D - 0.75, m, 'cab_bottom'); box(x + 0.75, x + w - 0.75, y1 - 0.75, y1, 0.75, D - 0.75, m, 'cab_top')
        for k in (1, 2):
            yy = y0 + (y1 - y0) * k / 3; box(x + 0.75, x + w - 0.75, yy - 0.25, yy + 0.25, 1.0, D - 1.5, material('GLASS-CLEAR'), 'shelf')
        box(x + 2, x + w - 2, y1 - 1.0, y1 - 0.8, 2.0, D - 2.0, material('LED-STRIP'), 'cab_led')
        return
    box(x, x + w, y0, y1, 0.0, D, cab_mat(), 'carcass')


def b_toe(a, ctx):
    # the kick in the cabinet finish, 3 in. back from the cabinet face (owner 11.09.26 PM: "the toe kicks need to match the cabinets")
    D = float(a.get('depth') or 24.0)
    # the run's toe leaves out the spans of undercounter appliances, which build their own toe round a grille: two toes on one face
    # z-fought into black triangles (owner 11.10.26)
    import __main__ as _M
    calls = (getattr(_M, 'V', None) or {}).get('calls', [])
    cut = sorted((c['args']['x'], c['args']['x'] + c['args']['w']) for c in calls if c.get('comp') == 'undercounter_appliance' and c.get('depth', 0) == 0)
    xs = a['x0']
    for c0, c1 in cut:
        if c1 <= xs or c0 >= a['x1']: continue
        if c0 - xs > 0.01: box(xs, c0, 0.0, 4.5, 0.0, D - 3.0, cab_mat(), 'toe')
        xs = max(xs, c1)
    if a['x1'] - xs > 0.01: box(xs, a['x1'], 0.0, 4.5, 0.0, D - 3.0, cab_mat(), 'toe')


def b_frame_opening(a, ctx):
    if ctx.get('depth', 0) != 0: return
    D = _cab_depth(a['y0'], a['y1'], a)
    box(a['x0'], a['x1'], a['y0'], a['y1'], 0.0, D - 0.02, cab_mat(), 'carcass')   # the box behind the opening (no face frame: fronts touch)
    _inset_front(a['x0'], a['y0'], a['x1'], a['y1'], D, style=a.get('style') or 'slim_shaker', r=0.0625)


def b_drawer_stack(a, ctx):
    x, w, n, top, bottom = a['x'], a['w'], a.get('n', 3), a.get('top', 34.75), a.get('bottom', 4.5); st_ = a.get('style', 'flat')
    D = _cab_depth(bottom, top, a); S = float(a.get('stile', 2.0)); r_ = float(a.get('reveal', 0.125))
    _carcass(x, w, bottom, top, D)
    inner = top - bottom - S * (n + 1)
    hs = [inner * 0.22] + [inner * (0.78 / (n - 1))] * (n - 1) if n > 1 else [inner]
    y = top - S
    for h in hs:
        _inset_front(x + S, y - h, x + w - S, y, D, style=st_, r=r_)
        _bar_pull(x + w / 2, y - h / 2, min(12.0, w * 0.4), False, D + 0.31)
        y -= h + S


def _doors(x, w, y0, y1, n, glass, pulls, hinge='L', depth=None, style='flat', S=2.0, r=0.125):
    D = float(depth or 24.0)
    _carcass(x, w, y0, y1, D, interior=glass)
    if glass:   # the face frame around a glass cabinet: stiles full height, rails between, the center stile between the rails
        m = cab_mat()
        if S > 0.01:
            _frame(x, y0, x + w, y1, S, D - 0.75, D, m, 'ff')
            if n == 2: box(x + w / 2 - S / 2, x + w / 2 + S / 2, y0 + S, y1 - S, D - 0.75, D, m, 'ff')
        else:          # no face frame: a thin edge band round the hollow box behind the touching glass doors
            _frame(x, y0, x + w, y1, 0.75, D - 0.75, D, m, 'ff')
    dw = (w - (n + 1) * S) / n
    for i in range(n):
        dx = x + S + i * (dw + S)
        _inset_front(dx, y0 + S, dx + dw, y1 - S, D, glass=glass, style=style, r=r)
        if pulls:
            right = (i == 0 and n == 2) or (n == 1 and hinge == 'L')
            px = dx + dw - 2.2 if right else dx + 2.2
            # exactly where idd_kitchen draws it (owner 11.09.26 night: "door handles in the correct places per the drawing")
            py = (y0 + y1) / 2 if (y1 - y0) < 40 else (y0 + 36 if y1 > 60 else y0 + (y1 - y0) * 0.5)
            _bar_pull(px, py, 6.0, True, D + 0.31)


def b_door_pair_cab(a, ctx):
    _doors(a['x'], a['w'], a['y0'], a['y1'], 2, a.get('glass'), a.get('pulls', True), depth=a.get('depth'), style=a.get('style', 'flat'), S=float(a.get('stile', 2.0)), r=float(a.get('reveal', 0.125)))


def b_single_door_cab(a, ctx):
    _doors(a['x'], a['w'], a['y0'], a['y1'], 1, a.get('glass'), True, a.get('hinge', 'L'), depth=a.get('depth'), style=a.get('style', 'flat'), S=float(a.get('stile', 2.0)), r=float(a.get('reveal', 0.125)))


def b_sink_cab(a, ctx):
    x, w, bottom, top, front = a['x'], a['w'], a.get('bottom', 4.5), a.get('top', 34.75), a.get('front', 7.0)
    st_ = a.get('style', 'flat'); D = float(a.get('depth') or 24.0); S = float(a.get('stile', 2.0)); r_ = float(a.get('reveal', 0.125))
    _doors(x, w, bottom, top - front, 2, False, True, depth=D, style=st_, S=S, r=r_)
    _carcass(x, w, top - front, top, D); _inset_front(x + S, top - front + S / 2, x + w - S, top - S / 2, D, style=st_, r=r_)


def b_counter(a, ctx):
    top, slab, ov = a.get('top', 36.0), a.get('slab', 1.25), a.get('overhang', 0.0) or 0.0
    box(a['x0'] - ov, a['x1'] + ov, top - slab, top, 0.0, 25.5, stone_mat(), 'counter')


def b_splash_slab(a, ctx):
    b_tile_grid({'x0': a['x0'], 'x1': a['x1'], 'y0': a['y0'], 'y1': a['y1'], 'module': (12, 4), 'grout': 0.0625}, ctx)


def b_floating_shelf(a, ctx):
    fin = a.get('finish', 'stone')   # the drawing records it: stone, white oak to the floor (owner 11.10.26), or paint
    sm = stone_mat() if fin == 'stone' else (material(R('shelf', 'WD-SHELF')) if fin == 'wood' else cab_mat())
    box(a['x'], a['x'] + a['w'], a['y'], a['y'] + a.get('thick', 2.0), 0.0, 10.0, sm, 'shelf')
    box(a['x'] + 1, a['x'] + a['w'] - 1, a['y'] - 0.05, a['y'], 1.0, 2.0, material('LED-STRIP'), 'shelf_led')


def b_light_rail(a, ctx):
    """The light rail on the face of the uppers, LS2 tape behind it (11.09.26 night: without it the zone over the bar's top shelf read dark)."""
    h = a.get('h', 1.5); D = float(a.get('depth') or 25.0)
    box(a['x0'], a['x1'], a['y'] - h, a['y'], D - 1.0, D, cab_mat(), 'light_rail')
    if a.get('led', True): box(a['x0'] + 1, a['x1'] - 1, a['y'] - 0.06, a['y'] - 0.01, D - 4.0, D - 2.5, material('LED-STRIP'), 'rail_led')


def b_pot_filler(a, ctx):
    cx, y = a['cx'], a['y']; m = metal_mat()
    cyl(cx, y, 0.6, 1.4, 1.2, 'd', m, 'flange'); cyl(cx, y, 4.5, 0.5, 8.0, 'd', m, 'arm'); cyl(cx, y - 2.5, 8.5, 0.4, 5.0, 'y', m, 'spout')


def b_outlet_splash(a, ctx):
    b_outlet({'cx': a['cx'], 'cy': a.get('cy', 42.0), 'horizontal': True}, ctx)


def b_pro_range(a, ctx):
    """48 in. dual-fuel professional range, built like the real thing: brushed stainless body and front frame, two oven doors
    (30 + 18) with framed dark glass and tubular handles on round brackets, a control rail of eight knobs with bezels, six
    sealed burners under continuous cast-iron grates and a griddle at the right, a vented kick and a low island backguard."""
    x, w, h = a['x'], a.get('w', 48.0), a.get('h', 36.0)
    ss = material('STAINLESS'); ci = material('GRATE'); gl = material('OVEN-GLASS'); gap = material('GAP')
    D = 27.0
    box(x + 0.06, x + w - 0.06, 4.5, h - 1.0, 0.5, D - 0.5, ss, 'range_body')
    box(x + 0.06, x + w - 0.06, 0.0, 4.5, 0.5, D - 2.5, gap, 'range_toe')
    for i in range(10): box(x + 4 + i * (w - 8) / 10, x + 4 + i * (w - 8) / 10 + 2.6, 1.2, 3.4, D - 2.55, D - 2.45, ss, 'kick_vent')
    rail_y = h - 6.0
    box(x + 0.3, x + w - 0.3, rail_y, h - 1.0, D - 0.5, D + 0.6, ss, 'control_rail')
    for i in range(8):
        kx = x + 4.5 + (w - 9) * i / 7
        cyl(kx, rail_y + 2.5, D + 0.75, 1.15, 0.3, 'd', ss, 'bezel'); cyl(kx, rail_y + 2.5, D + 1.6, 0.85, 1.5, 'd', ss, 'knob')
        box(kx - 0.08, kx + 0.08, rail_y + 2.6, rail_y + 3.3, D + 2.32, D + 2.38, gap, 'knob_pointer')
    split = x + 30.0
    for (d0, d1) in ((x + 0.5, split - 0.25), (split + 0.25, x + w - 0.5)):
        box(d0, d1, 5.0, rail_y - 0.6, D - 0.5, D + 0.6, ss, 'oven_door')
        box(d0 + 3.0, d1 - 3.0, 9.5, rail_y - 9.0, D + 0.6, D + 0.64, gl, 'oven_window')
        for (p0, p1, q0, q1) in ((d0 + 2.6, d1 - 2.6, 9.1, 9.5), (d0 + 2.6, d1 - 2.6, rail_y - 9.0, rail_y - 8.6), (d0 + 2.6, d0 + 3.0, 9.1, rail_y - 8.6), (d1 - 3.0, d1 - 2.6, 9.1, rail_y - 8.6)):
            box(p0, p1, q0, q1, D + 0.6, D + 0.7, ss, 'window_frame')
        hy = rail_y - 4.0
        cyl((d0 + d1) / 2, hy, D + 2.4, 0.55, d1 - d0 - 5.0, 'x', ss, 'handle')
        for hx in (d0 + 3.0, d1 - 3.0): cyl(hx, hy, D + 1.5, 0.45, 1.9, 'd', ss, 'handle_bracket')
    box(x, x + w, h - 1.0, h, 0.5, D - 0.5, ss, 'cooktop')
    gw = (w - 2.0) * 2.0 / 3.0; gx0 = x + 1.0
    for i in range(6):                                   # sealed burners: black caps on brass-tone bases under the grates
        bx_ = gx0 + gw / 6.0 + (i % 3) * gw / 3.0; bz = 7.0 if i < 3 else 20.0
        cyl(bx_, h + 0.5, bz, 2.3, 1.0, 'y', ss, 'burner_base'); cyl(bx_, h + 1.05, bz, 1.6, 0.4, 'y', ci, 'burner_cap')
    for k in range(3):                                   # continuous cast-iron grates, three sections, bars both ways
        g0 = gx0 + k * gw / 3.0 + 0.2; g1 = gx0 + (k + 1) * gw / 3.0 - 0.2
        for zz in (2.0, 13.5, 25.0): box(g0, g1, h + 1.6, h + 2.2, zz - 0.3, zz + 0.3, ci, 'grate_bar')
        for xx in (g0 + 0.3, (g0 + g1) / 2, g1 - 0.3): box(xx - 0.3, xx + 0.3, h + 1.6, h + 2.2, 1.7, 25.3, ci, 'grate_bar')
    box(gx0 + gw + 0.4, x + w - 1.0, h + 0.2, h + 0.9, 2.0, 25.0, ss, 'griddle')
    box(x, x + w, h, h + 3.0, 0.5, 2.0, ss, 'backguard')


def b_hood_breast(a, ctx):
    x, w, y0, Hh, dp = a['x'], a['w'], a['y0'], a['H'], float(a.get('depth') or 27.0)
    # a rectangular breast exactly as drawn: straight sides, no taper, floor of the breast at the hood bottom, up to the ceiling
    m = stone_mat() if a.get('style') == 'stone' else material(R('hood', 'HOOD-PLASTER'))
    box(x, x + w, y0, Hh, 0.0, dp, m, 'hood_breast')
    box(x + 3, x + w - 3, y0 - 0.02, y0 + 0.02, 3.0, dp - 3.0, material('GAP'), 'hood_liner')


def b_waterfall(a, ctx):   # the island is built whole by the kitchen staging
    return


def b_chair_rail(a, ctx):
    y, h = a['y'], a.get('h') or T.get('cap', 2.5) if isinstance(T, dict) else 2.5
    box(a['x0'], a['x1'], y, y + (h or 2.5), 0.0, 1.0, trim_mat(), 'chair_rail')


def b_arched_door_pair(a, ctx):
    """A pair under a semicircular head: arched casing swept over the jambs, leaves cut to the arch with a raised panel each,
    wall spandrels closing the corners of the rectangular hole above the spring line, vertical pulls at the meeting stiles."""
    x, w, spring = a['x'], a['w'], a['spring']; r = w / 2.0; cx = x + r; apex = spring + r
    cs = a.get('cs') or T['casing']; wm = wall_mat(); tm = trim_mat(); dm = material(R('door', 'PT-01-SATIN'), '-trim')
    def arcpts(rad, a0, a1, n=28):
        return [(cx + rad * _m.cos(_m.radians(a0 + (a1 - a0) * i / n)), spring + rad * _m.sin(_m.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    # spandrels (the wall hole is cut to the rectangle up to the apex)
    _prism([(x, spring), (x, apex + 0.01)] + arcpts(r, 90, 180, 20)[:-1], -6.0, 0.0, wm, 'wall_spandrel')
    _prism([(x + w, apex + 0.01), (x + w, spring)] + arcpts(r, 0, 90, 20), -6.0, 0.0, wm, 'wall_spandrel')
    # jamb lining in the wall thickness: legs and the arched soffit
    box(x - 0.01, x + 0.75, 0, spring, -5.5, 0.0, dm, 'jamb'); box(x + w - 0.75, x + w + 0.01, 0, spring, -5.5, 0.0, dm, 'jamb')
    pts = arcpts(r, 180, 0, 28)
    for p, q in zip(pts[:-1], pts[1:]):
        v = [(p[0], p[1], 0.0), (q[0], q[1], 0.0), (q[0], q[1], -5.5), (p[0], p[1], -5.5)]
        obj_from(v, [(0, 1, 2, 3), (3, 2, 1, 0)], dm, 'jamb_arch')
    # casing over the jambs and the arch
    sweep([(x, 0.0)] + [(x, spring)] + arcpts(r, 180, 0, 28)[1:-1] + [(x + w, spring), (x + w, 0.0)], casing_profile(cs), tm, 'casing')
    # the leaves
    st = 4.5; rb = 9.0; rt = 4.5; fd = -0.25; back = fd - 1.75
    def top(px, rad): return spring + _m.sqrt(max(0.0, rad * rad - (px - cx) ** 2))
    for (x0, x1, left) in ((x + 0.06, cx - 0.03, True), (cx + 0.03, x + w - 0.06, False)):
        ang0 = _m.degrees(_m.acos(max(-1, min(1, (x1 - cx) / r)))); ang1 = _m.degrees(_m.acos(max(-1, min(1, (x0 - cx) / r))))
        outline = [(x0, 0.5), (x1, 0.5)] + [(cx + (r - 0.06) * _m.cos(_m.radians(ang0 + (ang1 - ang0) * i / 20)), spring + (r - 0.06) * _m.sin(_m.radians(ang0 + (ang1 - ang0) * i / 20))) for i in range(21)]
        _prism(outline, back, fd, dm, 'leaf')
        rp = r - rt; p0, p1 = x0 + st, x1 - st
        a0_ = _m.degrees(_m.acos(max(-1, min(1, (p1 - cx) / rp)))); a1_ = _m.degrees(_m.acos(max(-1, min(1, (p0 - cx) / rp))))
        path = [(p0, rb), (p1, rb)] + [(cx + rp * _m.cos(_m.radians(a0_ + (a1_ - a0_) * i / 16)), spring + rp * _m.sin(_m.radians(a0_ + (a1_ - a0_) * i / 16))) for i in range(17)]
        sweep(path, [(q, d + fd - 0.5) for q, d in sticking_profile()], dm, 'sticking', closed=True)
        _prism(path, fd - 0.75, fd - 0.5, dm, 'panel')
        px = x1 - 2.2 if left else x0 + 2.2
        _bar_pull(px, 40.0, 12.0, True, fd, metal_mat())
    box(x, x + w, 0.0, apex, back - 0.05, back, material('GAP'), 'doorback')


def b_bed_king(a, ctx):
    cx, hb_w, hb_h, w, top = a['cx'], a.get('hb_w', 76), a.get('hb_h', 54), a.get('w', 76), a.get('top', 25)
    up = material(R('upholstery', 'FAB-HEADBOARD')); lin = material(R('bedding', 'FAB-BEDDING'))
    soft_wall = lambda x0, x1, y0, y1, d0, d1, mat, rad, nm: _soft(x0, x1, y0, y1, d0, d1, mat, rad, nm)
    soft_wall(cx - hb_w / 2, cx + hb_w / 2, 0.0, hb_h, 0.0, 4.0, up, 1.2, 'headboard')
    box(cx - w / 2 - 1, cx + w / 2 + 1, 3.0, 13.0, 4.0, 85.0, up, 'bed_base')                       # upholstered platform
    soft_wall(cx - w / 2, cx + w / 2, 13.0, top - 0.5, 4.5, 84.0, lin, 1.2, 'mattress')
    soft_wall(cx - w / 2 - 3.5, cx + w / 2 + 3.5, top - 0.5, top + 0.8, 30.0, 86.5, lin, 0.6, 'duvet')          # duvet over the lower two-thirds
    soft_wall(cx - w / 2 - 3.5, cx + w / 2 + 3.5, 11.0, top + 0.8, 85.2, 86.5, lin, 0.6, 'duvet_drop')
    for sx in (-1, 1): soft_wall(cx + sx * (w / 2 + 2.2) - 0.65, cx + sx * (w / 2 + 2.2) + 0.65, 11.0, top + 0.8, 30.0, 86.5, lin, 0.6, 'duvet_side')
    for px in (cx - w / 4, cx + w / 4):
        soft_wall(px - 13, px + 13, top, top + 25.0, 4.5, 10.5, up, 3.5, 'euro_sham')                          # upright against the headboard
        soft_wall(px - 14, px + 14, top, top + 6.5, 11.0, 30.0, lin, 3.0, 'pillow')
    soft_wall(cx - w / 2 - 3.6, cx + w / 2 + 3.6, top + 0.3, top + 1.6, 64.0, 80.0, material('GARM-6'), 0.5, 'throw')


def b_nightstand(a, ctx):
    x, w, h, n = a['x'], a.get('w', 22), a.get('h', 28), a.get('drawers', 2)
    m = material(R('nightstand', 'WOOD-FURN'))
    box(x, x + w, 0.0, h, 1.0, 19.0, m, 'nightstand')
    for i in range(n):
        y0 = 6 + i * (h - 8) / n; box(x + 1, x + w - 1, y0 + 0.4, y0 + (h - 8) / n - 0.4, 19.0, 19.05, material('GAP'), 'ns_gap')
        _bar_pull(x + w / 2, y0 + (h - 8) / n / 2, 5.0, False, 19.0, material('METAL-BRASS'))
    # a lamp
    cyl(x + w / 2, h + 7, 10.0, 2.2, 14.0, 'y', material('CERAMIC-LAMP') if 'CERAMIC-LAMP' in MATS else material('PLATE-WHITE'), 'lamp_base')
    cyl(x + w / 2, h + 19, 10.0, 6.0, 9.0, 'y', material('LAMP'), 'lamp_shade', cap=True)
    lamp(x + w / 2, h + 19, 10.0, watts=6.0, radius=2.0)


def _soft(x0, x1, y0, y1, d0, d1, mat, rad, nm):
    o = box(x0, x1, y0, y1, d0, d1, mat, nm)
    if o is None: return
    bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = min(rad, (x1 - x0) / 2.2, (y1 - y0) / 2.2, (d1 - d0) / 2.2) * IN; bv.segments = 4; bv.limit_method = 'NONE'
    for pg in o.data.polygons: pg.use_smooth = True


def b_panel_wall(a, ctx):
    """Applied moulding panels: a dado cap at the target height, panels below and above, sized evenly between openings."""
    x0, x1, Hh, tgt = a['x0'], a['x1'], a['H'], a.get('target', 32.0) or 32.0
    tm = trim_mat(); base_h = T['base']; crown_d = T['crown']
    cap = tgt
    box(x0, x1, cap, cap + 2.25, 0.0, 1.25, tm, 'dado_cap')
    ops = [(o[0], o[1]) for o in (a.get('openings') or []) if isinstance(o, (list, tuple))]
    segs = subtract((x0, x1, 0, 1), [(o0 - 6, o1 + 6, 0, 1) for o0, o1 in ops]) if ops else [(x0, x1, 0, 1)]
    for (s0, s1, _, _) in segs:
        span = s1 - s0
        if span < 10: continue
        n = max(1, int(round(span / 30.0))); m = 3.0; pw = (span - m * (n + 1)) / n
        for i in range(n):
            px0 = s0 + m + i * (pw + m); px1 = px0 + pw
            for (py0, py1) in ((base_h + 3.0, cap - 3.0), (cap + 2.25 + 4.0, Hh - crown_d - 4.0)):
                if py1 - py0 < 6: continue
                sweep([(px0, py0), (px1, py0), (px1, py1), (px0, py1)], [(q, d) for q, d in sticking_profile(0.75, 0.6)], tm, 'panel_mold', closed=True)


def b_cabinet_lower(a, ctx):
    x, w, h = a['x'], a['w'], a.get('h', 30)
    _doors(x, w, a.get('toe', 3), h, a.get('doors', 2), False, a.get('pulls', True))
    box(x - 0.5, x + w + 0.5, h, h + 1.25, 0.0, 14.5, trim_mat(), 'cab_top')


def b_shelves(a, ctx):
    x, w, y0, y1, n = a['x'], a['w'], a['y0'], a['y1'], a.get('n', 3)
    for i in range(1, n + 1):
        y = y0 + (y1 - y0) * i / (n + 1); box(x, x + w, y, y + a.get('thick', 1.0), 0.0, 12.0, trim_mat(), 'shelf')


COL_N = [0]


def b_drywall_column(a, ctx):
    """A drywall column floor to ceiling, its depth off the wall as the drawing records it, base and crown wrapped round its face."""
    x, w, dp = a['x'], a['w'], float(a.get('depth') or 26.0)
    COL_N[0] += 1; objs = []
    tm = trim_mat(); hb = T['base']; cd = T['crown']
    top = min(float(a.get('H') or H), H)   # a return that stops under a soffit records its own top; the soffit's crown covers it
    if a.get('finish') == 'millwork':   # clad as cabinetry: a flat panel in the cabinet finish on the runs' recessed toe
        objs += [box(x, x + w, 4.5, top, 0.0, dp, cab_mat(), 'column_panel'), box(x, x + w, 0.0, 4.5, 0.0, dp - 3.0, cab_mat(), 'toe')]
    else:
        objs += [box(x, x + w, 0.0, top, 0.0, dp, wall_mat(), 'wall_column'), box(x - 0.01, x + w + 0.01, 0.0, hb, dp, dp + 0.75, tm, 'column_base')]
    if top >= H - 1.0: objs.append(sweep([(x + w, H), (x, H)], [(q, d_ + dp) for q, d_ in crown_profile(cd, T['crown_proj'])], material(R('crown', R('trim', 'PT-01-SATIN')), '-trim'), 'column_crown'))
    for o in objs:
        if o is not None: o['col_id'] = COL_N[0]


def b_counter_stool(a, ctx):
    """Counter stool tucked at the seating edge: leather seat on a slim brass frame with a foot ring."""
    cx, seat = a['cx'], a.get('seat', 26.0); d = 13.0
    sm = material('BAG-1'); lm = material(R('metal', 'METAL-BRASS'))
    cyl(cx, seat - 1.2, d, 8.0, 2.5, 'y', sm, 'stool_seat')
    for (dx, dd) in ((-5.5, -5.5), (5.5, -5.5), (5.5, 5.5), (-5.5, 5.5)): cyl(cx + dx, (seat - 2.5) / 2, d + dd, 0.35, seat - 2.5, 'y', lm, 'stool_leg')
    for (dx, dd, ax, ln) in ((0, -5.5, 'x', 11.0), (0, 5.5, 'x', 11.0)): cyl(cx + dx, 9.0, d + dd, 0.3, ln, ax, lm, 'stool_ring')
    for dx in (-5.5, 5.5): cyl(cx + dx, 9.0, d, 0.3, 11.0, 'd', lm, 'stool_ring')


def b_veneer_door(a, ctx):
    """A veneer door in its face frame, glass with lit shelves behind when the drawing says glass; long pulls as drawn."""
    x, w, y0, y1 = a['x'], a['w'], a['y0'], a['y1']; D = float(a.get('depth') or 24.0); glass = a.get('glass')
    # paired doors share a 2 in. stile: each carcass takes half of it, so two boxes never overlap (coplanar overlapping faces with
    # the bevel shader render as black slots)
    S = float(a.get('stile', 2.0)); r_ = float(a.get('reveal', 0.125))
    if glass:
        _carcass(x, w, y0, y1, D, interior=True); _frame(x, y0, x + w, y1, max(S, 0.75), D - 0.75, D, cab_mat(), 'ff')
    else:
        _carcass(x, w, y0, y1, D)
    _inset_front(x + S, y0 + S, x + w - S, y1 - S, D, glass=glass, style=a.get('style', 'flat'), r=r_)
    px = x + w - S - 2.2 if a.get('hinge', 'L') == 'L' else x + S + 2.2
    if a.get('pull') == 'long': _bar_pull(px, 48.0, 36.0, True, D + 0.31)        # idd_kitchen: 30 to 66
    elif a.get('pull') == 'bar': _bar_pull(px, (y0 + y1) / 2, 6.0, True, D + 0.31)   # idd_kitchen: centred on the door


def b_filler_panel(a, ctx):
    D = float(a.get('depth') or 25.0)
    if a.get('toe_kick', True) and a['y0'] <= 0.01:   # the run's recessed toe runs through under it (owner 11.09.26 night)
        box(a['x'], a['x'] + a['w'], 4.5, a['y1'], 0.0, D, cab_mat(), 'filler_panel'); box(a['x'], a['x'] + a['w'], 0.0, 4.5, 0.0, D - 3.0, cab_mat(), 'toe')
    else:
        box(a['x'], a['x'] + a['w'], a['y0'], a['y1'], 0.0, D, cab_mat(), 'filler_panel')


def b_soffit(a, ctx):
    """Drywall over a cabinet run, flush with the cabinet face from the cabinet top to the ceiling, the crown on its face."""
    x0, x1, y0, dp = a['x0'], a['x1'], a['y0'], float(a.get('depth') or 24.0); cd = a.get('crown_drop') or T['crown']
    box(x0, x1, y0, H, 0.0, dp, wall_mat(), 'wall_soffit')
    sweep([(x1, H), (x0, H)], [(q, d_ + dp) for q, d_ in crown_profile(cd, T['crown_proj'])], material(R('crown', R('trim', 'PT-01-SATIN')), '-trim'), 'soffit_crown')


def b_undercounter_appliance(a, ctx):
    """Panel-ready undercounter appliance: 'beverage' a glass door in a slim panel frame with lit glass shelves and bottles behind;
    'ice' a shaker panel. Bar pull, a dark grille in the recessed toe."""
    x, w, top, bottom = a['x'], a['w'], a.get('top', 34.75), a.get('bottom', 4.5); D = float(a.get('depth') or 24.0)
    S = float(a.get('stile', 2.0)); r_ = float(a.get('reveal', 0.125)); SB = max(S, 0.75)   # the liner band behind touching fronts
    # the run's toe in the cabinet finish, framing the appliance's grille: a dark plate 1/2 in. back with vertical fins every 3/4 in.
    # (owner 11.10.26: slots laid on the toe face z-fought into black triangles). No two faces within 1/2 in. of each other.
    gx0, gx1, gz0, gz1 = x + 2.0, x + w - 2.0, 1.0, bottom - 1.0
    box(x, x + w, 0.0, gz0, 0.0, D - 3.0, cab_mat(), 'toe'); box(x, x + w, gz1, bottom, 0.0, D - 3.0, cab_mat(), 'toe')
    box(x, gx0, gz0, gz1, 0.0, D - 3.0, cab_mat(), 'toe_frame'); box(gx1, x + w, gz0, gz1, 0.0, D - 3.0, cab_mat(), 'toe_frame')
    gm = material('GRILLE'); box(gx0, gx1, gz0, gz1, 0.0, D - 3.5, gm, 'grille_plate')
    fx = gx0 + 0.5
    while fx < gx1 - 0.5:
        box(fx, fx + 0.12, gz0, gz1, D - 3.5, D - 3.15, gm, 'grille_fin'); fx += 0.75
    if a.get('kind') == 'beverage':
        m = cab_mat(); lm = material('CERAMIC-WHITE')
        box(x, x + w, bottom, top, 0.0, D - 22.0, m, 'bev_box')                       # the appliance body behind its liner
        box(x, x + SB, bottom, top, D - 22.0, D - 0.75, lm, 'bev_liner'); box(x + w - SB, x + w, bottom, top, D - 22.0, D - 0.75, lm, 'bev_liner')
        box(x + SB, x + w - SB, bottom, bottom + SB, D - 22.0, D - 0.75, lm, 'bev_liner'); box(x + SB, x + w - SB, top - SB, top, D - 22.0, D - 0.75, lm, 'bev_liner')
        box(x + SB, x + w - SB, bottom + SB, top - SB, D - 22.5, D - 22.0, lm, 'bev_liner')
        _frame(x, bottom, x + w, top, SB, D - 0.75, D, m, 'ff')
        for gy in (12.0, 19.0, 26.0):
            box(x + SB + 0.5, x + w - SB - 0.5, gy - 0.15, gy + 0.15, D - 21.0, D - 2.0, material('GLASS-CLEAR'), 'bev_shelf')
            for k in range(int((w - 2 * SB - 1) / 3.3)):
                cyl(x + SB + 2.0 + k * 3.3, gy + 1.6, D - 9.0, 1.45, 11.0, 'd', material('GLASS-DARK'), 'bottle')
        box(x + SB + 1, x + w - SB - 1, top - SB - 1.0, top - SB - 0.8, D - 20.0, D - 4.0, material('LED-STRIP'), 'bev_led')
        _inset_front(x + S, bottom + S, x + w - S, top - S, D, glass=True, r=r_)
        _bar_pull(x + w - S - 2.2, 22.0, 10.0, True, D + 0.31)          # idd_kitchen: 17 to 27
    else:
        _carcass(x, w, bottom, top, D)
        _inset_front(x + S, bottom + S, x + w - S, top - S, D, style=a.get('style', 'slim_shaker'), r=r_)
        _bar_pull(x + w / 2, top - S - 4.5, min(8.0, w * 0.5), False, D + 0.31)


EXTRA_BUILDERS = {'undercounter_appliance': b_undercounter_appliance, 'soffit': b_soffit, 'filler_panel': b_filler_panel, 'veneer_door': b_veneer_door, 'drywall_column': b_drywall_column, 'counter_stool': b_counter_stool, 'toe': b_toe, 'frame_opening': b_frame_opening, 'drawer_stack': b_drawer_stack, 'door_pair_cab': b_door_pair_cab,
                  'single_door_cab': b_single_door_cab, 'sink_cab': b_sink_cab, 'counter': b_counter, 'splash_slab': b_splash_slab,
                  'floating_shelf': b_floating_shelf, 'light_rail': b_light_rail, 'pot_filler': b_pot_filler, 'outlet_splash': b_outlet_splash,
                  'pro_range': b_pro_range, 'hood_breast': b_hood_breast, 'waterfall': b_waterfall, 'arched_door_pair': b_arched_door_pair,
                  'bed_king': b_bed_king, 'nightstand': b_nightstand, 'panel_wall': b_panel_wall, 'cabinet_lower': b_cabinet_lower,
                  'shelves': b_shelves, 'chair_rail': b_chair_rail,
                  # line-drawing only, or built whole elsewhere
                  'rev_cloud': None, 'hammered': None, 'glazing': None, 'miter_corner': None, 'sink_undermount_front': None,
                  'data_jack': None, 'jib_door': None, 'arched_opening': None}
