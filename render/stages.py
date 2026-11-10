# Room staging for the 11.09.26 renderings, exec'd inside photoreal.py after the walls, floor and lights exist.
# World coordinates in inches: X east from the west wall face, Y north from the south wall face, Z up from the floor.
import random as _rnd
import math as _m


def wbox(x0, x1, y0, y1, z0, z1, mat, name='piece', soft=0.0):
    if x1 - x0 < 0.01 or y1 - y0 < 0.01 or z1 - z0 < 0.01: return None
    o = world_box(x0, x1, y0, y1, z0, z1, mat, name)
    if soft:
        bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = min(soft, (x1 - x0) / 2.2, (y1 - y0) / 2.2, (z1 - z0) / 2.2) * IN
        bv.segments = 3; bv.limit_method = 'NONE'
        for pg in o.data.polygons: pg.use_smooth = True
    return o


def wcyl(X, Y, Z, r, length, axis, mat, name='cyl', n=32):
    """Cylinder centred at (X, Y, Z); axis 'x', 'y' or 'z'."""
    verts = []; faces = []
    for k in (0, 1):
        t = -length / 2 + k * length
        for i in range(n):
            a = 2 * _m.pi * i / n; u, w_ = r * _m.cos(a), r * _m.sin(a)
            p = {'x': (X + t, Y + u, Z + w_), 'y': (X + u, Y + t, Z + w_), 'z': (X + u, Y + w_, Z + t)}[axis]
            verts.append(p)
    for i in range(n):
        j = (i + 1) % n; faces.append((i, j, n + j, n + i))
    faces.append(tuple(range(n - 1, -1, -1))); faces.append(tuple(range(n, 2 * n)))
    me = bpy.data.meshes.new(name); me.from_pydata([(a_ * IN, b_ * IN, c_ * IN) for a_, b_, c_ in verts], [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    for pg in me.polygons: pg.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def wsphere(X, Y, Z, r, mat, name='sphere'):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r * IN)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for pg in me.polygons: pg.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); o.location = (X * IN, Y * IN, Z * IN)
    return o


def wlight(X, Y, Z, sx, sy, energy, name='strip', color=(1.0, 0.93, 0.82)):
    """A small area light facing down (LED tape under a shelf, a pendant's glow)."""
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = sx * IN; ld.size_y = sy * IN; ld.energy = energy; ld.color = color
    o = bpy.data.objects.new(name, ld); bpy.context.collection.objects.link(o); o.location = (X * IN, Y * IN, Z * IN)
    o.visible_glossy = False; o.visible_camera = False
    return o


def wpoint(X, Y, Z, watts, radius=1.0, color=(1.0, 0.86, 0.68)):
    ld = bpy.data.lights.new('pt', 'POINT'); ld.energy = watts; ld.shadow_soft_size = radius * IN; ld.color = color
    o = bpy.data.objects.new('pt', ld); bpy.context.collection.objects.link(o); o.location = (X * IN, Y * IN, Z * IN); return o


def _garment(axis, p, t, c, ztop, zbot, depth, mat, rnd):
    """One garment on a hanger: a soft slab with sloped shoulders, a little flare to the hem, a hook to the rod."""
    hd = depth / 2; sh = rnd.uniform(3.0, 4.5); fl = rnd.uniform(0.0, 1.2)
    prof = [(-hd + 3.0, ztop), (hd - 3.0, ztop), (hd, ztop - sh), (hd + fl, zbot), (-hd - fl, zbot), (-hd, ztop - sh)]
    n = len(prof); verts = []
    for s_ in (0.0, t):
        for (u, z) in prof:
            verts.append((p + s_, c + u, z) if axis == 'x' else (c + u, p + s_, z))
    faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new('garment'); me.from_pydata([(a_ * IN, b_ * IN, z_ * IN) for a_, b_, z_ in verts], [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('garment', me); bpy.context.collection.objects.link(o); o.data.materials.append(mat)
    bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = min(0.45, t / 2.2) * IN; bv.segments = 3; bv.limit_method = 'NONE'
    for pg in me.polygons: pg.use_smooth = True
    hx, hy = (p + t / 2, c) if axis == 'x' else (c, p + t / 2)
    wcyl(hx, hy, ztop + 0.9, 0.12, 1.8, 'z', material('BRONZE'), 'hook')


def garments(axis, a0, a1, c, z_rod, lengths, rnd, gap=(1.6, 2.6), depth=19.0, name='garment'):
    """Clothes on a rod running along `axis` ('x' or 'y') from a0 to a1, the rod line at c (the other coordinate), hung at z_rod.
    Each garment is a soft slab across the rod, a hanger hook above it."""
    p = a0 + 1.2
    while p < a1 - 1.5:
        t = rnd.uniform(0.8, 2.2); ln = rnd.uniform(*lengths); col = material('GARM-%d' % rnd.randint(0, 7))
        _garment(axis, p, t, c, z_rod - 1.8, z_rod - 1.8 - ln, depth * rnd.uniform(0.9, 1.05), col, rnd)
        p += t + rnd.uniform(*gap)


def rod(axis, a0, a1, c, z):
    br = material('BRONZE')
    if axis == 'x': wcyl((a0 + a1) / 2, c, z, 0.55, a1 - a0, 'x', br, 'rod')
    else: wcyl(c, (a0 + a1) / 2, z, 0.55, a1 - a0, 'y', br, 'rod')


def stage_closet():
    """Master closet per ID-330 to ID-333 (11.09.26 PM): runs, uppers, hanging, showcase, the chute cabinet, the vanity, the
    shoe tower, the waterfall island, clothes, bags and shoes for the picture."""
    Lc = json.load(open(os.path.join(HERE, 'closet_layout.json')))
    W, D = Lc['W'], Lc['D']; DN, DW, DE, DV = Lc['DN'], Lc['DW'], Lc['DE'], Lc['DV']
    TOP, UP0, RH, RL, RLONG = Lc['TOP'], Lc['UP0'], Lc['ROD_HI'], Lc['ROD_LO'], Lc['ROD_LONG']
    NA, NB, VY0, VY1, VTOP = Lc['NA'], Lc['NB'], Lc['VY0'], Lc['VY1'], Lc['VTOP']
    EB, WB = Lc['EB'], Lc['WB']; CH_Y0, CH_Y1, CH_TOP = Lc['CH_Y0'], Lc['CH_Y1'], Lc['CH_TOP']
    Y = lambda yp: D - yp                                    # plan y (south from the north wall) to world Y
    mw = material('MW-01', '-trim'); mw2 = material('MW-02'); br = material('BRONZE'); gl = material('GLASS-CLEAR')
    stone = material('CAL-MONET'); fb = material('FB-01'); led = material('LED-STRIP'); gap = material('GAP'); toe_m = material('TOE')
    rnd = _rnd.Random(11)

    def run_box(x0, x1, yp0, yp1, z0, z1, mat=mw, name='mw', soft=0.0):
        return wbox(x0, x1, Y(yp1), Y(yp0), z0, z1, mat, name, soft)

    def slab_doors_x(x0, x1, face_y, z0, z1, n, name='wall_upper'):     # doors on a north-run face (plan y = face_y), facing south
        w = (x1 - x0) / n
        for i in range(n):
            a, b_ = x0 + i * w, x0 + (i + 1) * w
            wbox(a + 0.06, b_ - 0.06, Y(face_y), Y(face_y) + 0.75, z0 + 0.06, z1 - 0.06, mw, name)
            wbox(a, b_, Y(face_y) + 0.5, Y(face_y) + 0.75, z0, z1, gap, 'reveal')
            px = b_ - 1.6 if i % 2 == 0 else a + 1.6
            wcyl(px, Y(face_y) - 1.3, z0 + 4.0, 0.22, 6.0, 'z', br, 'pull')

    def slab_doors_y(yp0, yp1, face_x, z0, z1, n, facing, name='wall_upper'):   # doors on a west (facing +1) or east (facing -1) run
        w = (yp1 - yp0) / n
        for i in range(n):
            a, b_ = yp0 + i * w, yp0 + (i + 1) * w
            fx0, fx1 = (face_x - 0.75, face_x) if facing > 0 else (face_x, face_x + 0.75)
            wbox(fx0, fx1, Y(b_ - 0.06), Y(a + 0.06), z0 + 0.06, z1 - 0.06, mw, name)
            py = b_ - 1.6 if i % 2 == 0 else a + 1.6
            wcyl(face_x + facing * 1.3, Y(py), z0 + 4.0, 0.22, 6.0, 'z', br, 'pull')

    def uppers_x(x0, x1):
        run_box(x0, x1, 0.0, DN - 0.75, UP0, TOP)
        wbox(x0 + 1, x1 - 1, Y(DN - 1.5), Y(DN - 0.6), UP0 - 1.05, UP0 - 0.95, led, 'led')
        wlight((x0 + x1) / 2, Y(DN - 1.0), UP0 - 1.2, x1 - x0 - 2, 0.6, 1.2 * (x1 - x0) / 24)
        slab_doors_x(x0, x1, DN, UP0, TOP, max(1, round((x1 - x0) / 24)))

    def uppers_y(yp0, yp1, side):          # side 'W' (face at x=DW, facing east) or 'E' (face at x=W-DE, facing west)
        if side == 'W': run_box(0.0, DW - 0.75, yp0, yp1, UP0, TOP); fx, f = DW, 1
        else: run_box(W - DE + 0.75, W, yp0, yp1, UP0, TOP); fx, f = W - DE, -1
        wlight(fx + f * 1.0, Y((yp0 + yp1) / 2), UP0 - 1.2, 0.6, yp1 - yp0 - 2, 1.2 * (yp1 - yp0) / 24)
        slab_doors_y(yp0, yp1, fx, UP0, TOP, max(1, round((yp1 - yp0) / 24)), f)

    def side_x(x, yp0=0.0, yp1=DN, z1=TOP): run_box(x - 0.375, x + 0.375, yp0, yp1, 0.0, z1, mw, 'side')
    def side_y(yp, x0, x1, z1=TOP): run_box(x0, x1, yp - 0.375, yp + 0.375, 0.0, z1, mw, 'side')

    # ---------------------------------------------------------------- north run: corner double hang, the showcase
    for (x0, x1) in ((0.0, NA), (NB, W)):
        run_box(x0, x1, 0.0, 0.75, 0, TOP, mw, 'back')
        run_box(x0, x1, 0.0, DN, RH + 1.5, RH + 2.25, mw, 'shelf'); run_box(x0, x1, 0.0, DN, RL + 1.5, RL + 2.25, mw, 'shelf')
        wlight((x0 + x1) / 2, Y(DN - 1.5), RL + 1.3, x1 - x0 - 2, 0.6, 0.8)
        rod('x', x0 + 0.5, x1 - 0.5, Y(DN / 2), RH); rod('x', x0 + 0.5, x1 - 0.5, Y(DN / 2), RL)
        garments('x', x0, x1, Y(DN / 2), RH, (26, 36), rnd); garments('x', x0, x1, Y(DN / 2), RL, (22, 32), rnd)
        run_box(x0, x1, 3.0, DN - 3.0, 0, 4.0, toe_m, 'toe'); uppers_x(x0, x1)
    for x in (NA, NB): side_x(x)
    # showcase: drawers, cap, linen back, one-piece glass shelves, bags
    run_box(NA, NB, 3.0, DN - 3.0, 0, 4.0, toe_m, 'toe')
    cw = (NB - NA) / 2
    for i in range(2):
        a = NA + i * cw
        for k in range(4):
            z0 = 4.0 + k * (Lc['SC_TOP_DRW'] - 4.0) / 4; z1 = z0 + (Lc['SC_TOP_DRW'] - 4.0) / 4
            run_box(a + 0.2, a + cw - 0.2, 0.75, DN, z0 + 0.1, z1 - 0.1, mw2, 'drawer', soft=0.15)
            wcyl(a + cw / 2, Y(DN) - 1.0, z0 + (z1 - z0) * 0.62, 0.22, min(10.0, cw * 0.44), 'x', br, 'pull')
    run_box(NA, NB, 0.0, DN, Lc['SC_TOP_DRW'], Lc['SC_TOP_DRW'] + 1.0, mw, 'cap')
    z0s = Lc['SC_TOP_DRW'] + 1.0; rh = (TOP - z0s) / Lc['SC_ROWS']
    run_box(NA + 0.4, NB - 0.4, 0.0, 0.75, z0s, TOP, fb, 'linen_back')
    run_box(NA, NB, 0.0, DN, TOP - 0.75, TOP, mw, 'sc_top')
    for j in range(Lc['SC_ROWS']):
        zs = z0s + j * rh
        if j: run_box(NA + 0.4, NB - 0.4, 0.75, 14.75, zs - 0.75, zs, gl, 'glass_shelf')
        ztop = z0s + (j + 1) * rh - (0.75 if j < Lc['SC_ROWS'] - 1 else 0.75)
        run_box(NA + 1, NB - 1, 13.5, 14.5, ztop - 0.12, ztop - 0.02, led, 'led')
        wlight((NA + NB) / 2, Y(10.0), ztop - 0.3, NB - NA - 4, 3.0, 9.0)
        for k in range(4):
            cx = NA + (NB - NA) * (0.125 + 0.25 * k); bw_ = rnd.uniform(10.5, 13.0); bh = rnd.uniform(8.5, min(11.5, rh - 5.0)); bd = rnd.uniform(4.5, 6.0)
            bag = material('BAG-%d' % rnd.randint(0, 5))
            run_box(cx - bw_ / 2, cx + bw_ / 2, 7.0 - bd / 2, 7.0 + bd / 2, zs, zs + bh, bag, 'bag', soft=1.2)
            hz = zs + bh; hw = bw_ * 0.32
            for sx in (-1, 1): wcyl(cx + sx * hw, Y(7.0), hz + 1.6, 0.25, 3.4, 'z', bag, 'handle')
            wcyl(cx, Y(7.0), hz + 3.2, 0.25, 2 * hw, 'x', bag, 'handle')
    # ---------------------------------------------------------------- west run: double hang north, vanity, dresses south
    def bay_y(yp0, yp1, side, dbl=True, long_=False, glass=False):
        x0, x1, c = (0.0, DW, DW / 2) if side == 'W' else (W - DE, W, W - DE / 2)
        back = (0.0, 0.75) if side == 'W' else (W - 0.75, W)
        run_box(back[0], back[1], yp0, yp1, 0, TOP, mw, 'back')
        run_box(x0 + 3 if side == 'W' else x0 + 3, x1 - 3, yp0, yp1, 0, 4.0, toe_m, 'toe')
        if dbl:
            for zr in (RH, RL):
                run_box(x0, x1, yp0, yp1, zr + 1.5, zr + 2.25, mw, 'shelf'); rod('y', Y(yp1) + 0.5, Y(yp0) - 0.5, c, zr)
            garments('y', Y(yp1), Y(yp0), c, RH, (26, 36), rnd); garments('y', Y(yp1), Y(yp0), c, RL, (22, 32), rnd)
            wlight(x1 - 1.5 if side == 'W' else x0 + 1.5, Y((yp0 + yp1) / 2), RL + 1.3, 0.6, yp1 - yp0 - 2, 0.8)
        if long_:
            run_box(x0, x1, yp0, yp1, RLONG + 1.5, RLONG + 2.25, mw, 'shelf'); rod('y', Y(yp1) + 0.5, Y(yp0) - 0.5, c, RLONG)
            garments('y', Y(yp1), Y(yp0), c, RLONG, (46, 60), rnd, gap=(2.0, 3.2))
        if glass:   # GL-01 bronze-framed glass doors, 4 in. to the uppers
            fx = x1 if side == 'W' else x0; f = 1 if side == 'W' else -1
            n = 2; w = (yp1 - yp0) / n
            for i in range(n):
                a, b_ = yp0 + i * w + 0.06, yp0 + (i + 1) * w - 0.06
                fr = (fx, fx + f * 1.0)
                xa, xb = min(fr), max(fr)
                for (p0, p1, z0, z1) in ((a, a + 1.0, 4.0, UP0 - 1.0), (b_ - 1.0, b_, 4.0, UP0 - 1.0), (a, b_, 4.0, 5.0), (a, b_, UP0 - 2.0, UP0 - 1.0)):
                    wbox(xa, xb, Y(p1), Y(p0), z0, z1, br, 'gl_frame')
                wbox(xa + 0.4, xb - 0.4, Y(b_ - 1.0), Y(a + 1.0), 5.0, UP0 - 2.0, gl, 'gl_glass')
                py = b_ - 0.6 if i == 0 else a + 0.6
                wcyl(fx + f * 1.6, Y(py), (4.0 + UP0) / 2, 0.25, 10.0, 'z', br, 'pull')
        uppers_y(yp0, yp1, side)
    bay_y(WB['dbl'][0], WB['dbl'][1], 'W', dbl=True)
    bay_y(WB['dress'][0], WB['dress'][1], 'W', dbl=False, long_=True, glass=True)
    for yp in (WB['dbl'][1], WB['dress'][0]): side_y(yp, 0.0, DW)
    # the vanity: stone top, two apron drawers, knee space, lit mirror, uppers, two poufs
    run_box(0.0, 0.75, VY0, VY1, 0, UP0, material(R('wall', 'PT-02')), 'wall_vanity')
    run_box(0.0, DV + 0.75, VY0, VY1, VTOP - 1.5, VTOP, stone, 'vanity_top')
    for (a, b_) in ((VY0, (VY0 + VY1) / 2), ((VY0 + VY1) / 2, VY1)):
        run_box(DV - 0.75, DV, a + 0.15, b_ - 0.15, VTOP - 5.5, VTOP - 1.6, mw2, 'apron', soft=0.15)
        wcyl(DV + 0.9, Y((a + b_) / 2), VTOP - 3.5, 0.22, 7.0, 'y', br, 'pull')
    run_box(0.75, DV - 0.75, VY0, VY1, VTOP - 5.5, VTOP - 1.5, mw, 'apron_box')
    run_box(0.75, 1.25, VY0 + 4, VY1 - 4, 36.0, 80.0, material('MIRROR-SILVER'), 'mirror')
    run_box(0.75, 1.0, VY0 + 3.4, VY1 - 3.4, 35.4, 80.6, led, 'mirror_halo')
    wlight(3.0, Y((VY0 + VY1) / 2), 58.0, 0.6, 30.0, 6.0)
    uppers_y(VY0, VY1, 'W')
    fab = material('FAB-SOFA')
    for c_ in (VY0 + 12, VY1 - 12): wcyl(DV + 9, Y(c_), 9.0, 7.5, 18.0, 'z', fab, 'pouf')
    # ---------------------------------------------------------------- east run: double hang over the chute cabinet, dresses, shoes
    yp0, yp1 = EB['dbl'][0], EB['chute'][1]
    run_box(W - 0.75, W, yp0, yp1, 0, TOP, mw, 'back')
    run_box(W - DE + 3, W - 3, yp0, yp1, 0, 4.0, toe_m, 'toe')
    run_box(W - DE, W, yp0, yp1, RH + 1.5, RH + 2.25, mw, 'shelf'); rod('y', Y(yp1) + 0.5, Y(yp0) - 0.5, W - DE / 2, RH)
    garments('y', Y(yp1), Y(yp0), W - DE / 2, RH, (26, 36), rnd)
    run_box(W - DE, W, yp0, yp1, CH_TOP, CH_TOP + 0.75, mw, 'shelf')
    rod('y', Y(CH_Y0) + 0.5, Y(yp0) - 0.5, W - DE / 2, RL); garments('y', Y(CH_Y0), Y(yp0), W - DE / 2, RL, (22, 32), rnd)
    run_box(W - DE, W - 0.75, CH_Y0, CH_Y1, 4.0, CH_TOP, mw, 'chute_cab')
    side_y(CH_Y0, W - DE, W, CH_TOP)
    wbox(W - DE - 0.75, W - DE, Y(CH_Y1 - 0.1), Y(CH_Y0 + 0.1), 4.1, CH_TOP - 0.1, mw, 'chute_door')
    wcyl(W - DE - 1.3, Y(CH_Y1 - 2.0), (4 + CH_TOP) / 2, 0.22, 8.0, 'z', br, 'pull')
    wlight(W - DE + 1.5, Y((yp0 + yp1) / 2), CH_TOP - 0.3, 0.6, yp1 - yp0 - 2, 0.8)
    uppers_y(yp0, yp1, 'E')
    bay_y(EB['dress'][0], EB['dress'][1], 'E', dbl=False, long_=True, glass=True)
    for yp in (EB['chute'][1], EB['dress'][1]): side_y(yp, W - DE, W)
    # shoe tower: nine pitched lit shelves behind full-height glass doors
    s0, s1 = EB['shoes']
    run_box(W - 0.75, W, s0, s1, 0, TOP, mw, 'back'); run_box(W - DE + 3, W - 3, s0, s1, 0, 4.0, toe_m, 'toe')
    run_box(W - DE, W, s0, s1, TOP - 0.75, TOP, mw, 'top')
    for k in range(9):
        z = 8.0 + k * 10.6
        run_box(W - DE + 1.5, W - 0.75, s0 + 0.5, s1 - 0.5, z, z + 0.75, mw, 'shoe_shelf')
        wlight(W - DE + 2.5, Y((s0 + s1) / 2), z + 9.4, 0.6, s1 - s0 - 4, 0.6)
        for p in range(4):
            cy = s0 + 2.0 + (s1 - s0 - 4.0) * (p + 0.5) / 4
            col = material('BAG-%d' % rnd.randint(0, 5))
            for sx in (-1.9, 1.9):
                hh = rnd.choice((3.5, 4.5, 6.0))
                run_box(W - DE + 5, W - 4, cy + sx - 1.6, cy + sx + 1.6, z + 0.75, z + 0.75 + hh, col, 'shoe', soft=1.2)
    fx = W - DE; w2 = (s1 - s0) / 2
    for i in range(2):
        a, b_ = s0 + i * w2 + 0.06, s0 + (i + 1) * w2 - 0.06
        for (p0, p1, z0, z1) in ((a, a + 1.0, 4.0, TOP), (b_ - 1.0, b_, 4.0, TOP), (a, b_, 4.0, 5.0), (a, b_, TOP - 1.0, TOP)):
            wbox(fx - 1.0, fx, Y(p1), Y(p0), z0, z1, br, 'gl_frame')
        wbox(fx - 0.6, fx - 0.4, Y(b_ - 1.0), Y(a + 1.0), 5.0, TOP - 1.0, gl, 'gl_glass')
        wcyl(fx - 1.6, Y(b_ - 0.6 if i == 0 else a + 0.6), 52.0, 0.25, 12.0, 'z', br, 'pull')
    # ---------------------------------------------------------------- the island: waterfall ends, two drawer stacks west, panels east
    x0, y0p, x1, y1p = Lc['ISL']; WF = Lc['WF']; IT = Lc['ITOP']
    run_box(x0 - 1, x1 + 1, y0p - 1, y1p + 1, IT - 1.5, IT, stone, 'island_top')
    run_box(x0 - 1, x1 + 1, y0p - 1, y0p - 1 + WF, 0.0, IT - 1.5, stone, 'waterfall')
    run_box(x0 - 1, x1 + 1, y1p + 1 - WF, y1p + 1, 0.0, IT - 1.5, stone, 'waterfall')
    run_box(x0 + 0.75, x1 - 0.75, y0p + 0.5, y1p - 0.5, 4.0, IT - 1.5, mw, 'island_body')
    run_box(x0 + 3, x1 - 3, y0p + 0.5, y1p - 0.5, 0.0, 4.0, toe_m, 'toe')
    Li = (y1p + 1 - WF) - (y0p - 1 + WF); sw = Li / 2
    for i in range(2):
        a = y0p - 1 + WF + i * sw
        for (z0, z1) in ((4.0, Lc['DRW_DEEP']), (Lc['DRW_DEEP'], 25.875), (25.875, 33.75)):
            run_box(x0, x0 + 0.8, a + 0.15, a + sw - 0.15, z0 + 0.06, z1 - 0.06, mw2, 'island_drawer', soft=0.12)
            wcyl(x0 - 0.9, Y(a + sw / 2), z0 + (z1 - z0) * 0.62, 0.22, 10.0, 'y', br, 'pull')
            for yy in (a + sw / 2 - 4.4, a + sw / 2 + 4.4): wcyl(x0 - 0.45, Y(yy), z0 + (z1 - z0) * 0.62, 0.15, 0.9, 'x', br, 'post')
    for k in range(3):
        a = y0p + 0.5 + k * (Li - 1) / 3
        run_box(x1 - 0.8, x1, a + 0.2, a + (Li - 1) / 3 - 0.2, 4.2, IT - 1.7, mw, 'panel', soft=0.1)
    # a jewelry tray on the island, a vase
    import_model('ceramic_vase_01', 8.0, (x0 + x1) / 2 + 7, Y((y0p + y1p) / 2 + 16), IT, 15)
    import_model('wooden_bowl_01', 2.5, (x0 + x1) / 2 - 6, Y((y0p + y1p) / 2 - 12), IT, 0)
    # CH1: a bronze ring of eight small glass globes over the island
    cx, cy = (x0 + x1) / 2, Y((y0p + y1p) / 2); zc = 84.0
    wcyl(cx, cy, (zc + Lc['H']) / 2, 0.3, Lc['H'] - zc, 'z', br, 'ch_rod')
    ring_r = 12.0
    for k in range(24):
        a0 = 2 * _m.pi * k / 24; a1 = 2 * _m.pi * (k + 1) / 24
        p0 = (cx + ring_r * _m.cos(a0), cy + ring_r * _m.sin(a0)); p1 = (cx + ring_r * _m.cos(a1), cy + ring_r * _m.sin(a1))
        mxp, myp = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2; ln = _m.hypot(p1[0] - p0[0], p1[1] - p0[1])
        o = wcyl(mxp, myp, zc, 0.35, ln, 'x', br, 'ch_ring'); o.rotation_euler = (0, 0, _m.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        o.location = (mxp * IN, myp * IN, zc * IN); o.data.transform(Matrix.Translation((-mxp * IN, -myp * IN, -zc * IN)))
    for k in range(4): wcyl(cx + ring_r / 2 * _m.cos(k * _m.pi / 2), cy + ring_r / 2 * _m.sin(k * _m.pi / 2), zc, 0.25, ring_r, 'x' if k % 2 == 0 else 'y', br, 'ch_spoke')
    for k in range(8):
        a0 = 2 * _m.pi * k / 8; gx, gy = cx + ring_r * _m.cos(a0), cy + ring_r * _m.sin(a0)
        wsphere(gx, gy, zc + 2.6, 2.2, material('LAMP'), 'globe'); wpoint(gx, gy, zc + 2.6, 6.0, 1.5)


def stage_kitchen():
    """The island (FOR's position, owner's 42 in. aisle): carcass, 2 in. Calacatta Monet top with waterfall ends and a 15 in.
    seating overhang, the working-side cabinets from ID-243 view captures, three pendants, four stools."""
    # the island where the drawing records it (K.island_place in the working-side view); Casa Grove's numbers only as a fallback
    rec = next((c['args'] for v in ALL for c in v.get('calls', []) if c['comp'] == 'island_place'), None)
    if rec:
        ISL_X, ISL_N, ISL_L, ISL_W = rec['x'], rec['from_north'], rec['length'], rec['cab_depth']
        WF, TOPD, TOFF = rec.get('waterfall', 2.0), rec['top_depth'], rec.get('top_offset', 1.0)
    else:
        print('WARNING no island_place call in the views: Casa Grove island position used')
        ISL_X, ISL_N, ISL_L, ISL_W, WF, TOPD, TOFF = 72.625, 67.0, 110.9375, 49.0, 2.0, 65.0, 1.0
    yN = DEP - ISL_N; yS = yN - ISL_L
    stone = material(R('counter', 'CAL-MONET')); cab = material(R('cabinet', 'CAB-01'), '-trim')
    top_x0, top_x1 = ISL_X - TOFF, ISL_X - TOFF + TOPD
    wbox(top_x0, top_x1, yS, yN, 34.0, 36.0, stone, 'island_top')
    wbox(top_x0, top_x1, yS, yS + WF, 0.0, 34.0, stone, 'waterfall'); wbox(top_x0, top_x1, yN - WF, yN, 0.0, 34.0, stone, 'waterfall')
    wbox(ISL_X + 0.5, ISL_X + ISL_W, yS + WF, yN - WF, 4.5, 34.0, cab, 'island_body')
    wbox(ISL_X + 3.0, ISL_X + ISL_W - 3, yS + WF, yN - WF, 0.0, 4.5, cab, 'island_toe')   # the toe in the cabinet finish on both faces (owner 11.09.26 night)
    # working side (west face): the captured cabinets, placed like an east-facing wall at the island face
    for vi, v in enumerate(ALL):
        if v['view'] == 'ISLAND - WORKING SIDE':
            # the builders put base cabinet faces 24 in. out from their wall: the 'wall' here is 24 in. behind the island face
            M = Matrix.Translation(((ISL_X + 24.0) * IN, yN * IN, 0)) @ Matrix.Rotation(_m.radians(-90), 4, 'Z')
            before = set(bpy.data.objects)
            for c in v['calls']:
                if c['depth'] != 0 or c['comp'] in ('counter', 'waterfall', 'miter_corner', 'toe'): continue
                fn = BUILDERS.get(c['comp'])
                if fn: fn(c['args'], c)
            for o in set(bpy.data.objects) - before:
                o.matrix_world = M @ o.matrix_world
    # seating side: three inset panels under the overhang
    # (ID-243 view 6: three flat recessed panels in a 2 in. face frame, on the toe; built as slim shaker panels like every front)
    pw_ = (ISL_L - 2 * WF - 4 * 2.0) / 3
    for k in range(3):
        a = yS + WF + 2.0 + k * (pw_ + 2.0); b_ = a + pw_
        for (p0, p1, q0, q1) in ((a, a + 1.375, 6.5, 32.75), (b_ - 1.375, b_, 6.5, 32.75), (a + 1.375, b_ - 1.375, 6.5, 7.875), (a + 1.375, b_ - 1.375, 31.375, 32.75)):
            wbox(ISL_X + ISL_W, ISL_X + ISL_W + 0.3, p0, p1, q0, q1, cab, 'seat_panel_frame')
    # faucet at the sink (bridge gooseneck), brass
    br = material(R('metal', 'METAL-BRASS'))
    sk = next((c['args'] for v in ALL if v['view'] == 'ISLAND - WORKING SIDE' for c in v.get('calls', []) if c['comp'] == 'sink_cab' and c['depth'] == 0), None)
    sink_y = yN - (sk['x'] + sk['w'] / 2) if sk else yN - 2.0 - 35.25 - 18.0      # the sink on its cabinet's centre, from the drawing
    wcyl(ISL_X + 3.0, sink_y, 36 + 5.5, 0.6, 11.0, 'z', br, 'faucet'); wcyl(ISL_X + 3.0 + 4.0, sink_y, 36 + 11.2, 0.5, 8.0, 'x', br, 'spout')
    wcyl(ISL_X + 3.0 + 8.0, sink_y, 36 + 9.5, 0.45, 3.5, 'z', br, 'spout_tip')
    wbox(ISL_X + 4.0, ISL_X + 22.0, sink_y - 15.0, sink_y + 15.0, 35.9, 36.01, material('GAP'), 'sink_bowl')
    # pendants over the island: three brass and opal globes on the island axis
    px = top_x0 + TOPD / 2
    pend = [(l_['X'], l_['Y']) for l_ in (LIGHTPLAN or []) if l_['type'] == 'pendant'] or [(px, yN - ISL_L / 2 + dy) for dy in (-33.0, 0.0, 33.0)]
    for (px, py) in pend:          # P1 at the lighting plan's J-boxes (ID-121)
        # P1 (fixture open): an alabaster cylinder on a brass stem, as in the owner's inspiration image, glowing softly
        wcyl(px, py, (H + 76) / 2, 0.2, H - 76, 'z', br, 'pendant_rod'); wcyl(px, py, H - 0.4, 2.2, 0.8, 'z', br, 'pendant_canopy')
        wcyl(px, py, 69.0, 3.0, 10.0, 'z', material('ALABASTER'), 'pendant_alabaster'); wcyl(px, py, 74.4, 3.1, 0.8, 'z', br, 'pendant_cap')
        wpoint(px, py, 69.0, 12.0, 2.5)
    for vi, v in enumerate(ALL):          # the stools the seating-side elevation draws (owner 11.09.26 PM: five)
        if v['view'] == 'ISLAND - SEATING SIDE':
            M2 = Matrix.Translation(((ISL_X + ISL_W) * IN, yS * IN, 0)) @ Matrix.Rotation(_m.radians(90), 4, 'Z')
            before = set(bpy.data.objects)
            for c in v['calls']:
                if c['depth'] == 0 and c['comp'] == 'counter_stool': BUILDERS['counter_stool'](c['args'], c)
            for o in set(bpy.data.objects) - before: o.matrix_world = M2 @ o.matrix_world
    import_model('ceramic_vase_01', 11.0, ISL_X + 30, yN - 18, 36.0, 10)
    import_model('wooden_bowl_01', 3.0, ISL_X + 32, yS + 26, 36.0, 0)


def stage_mbr():
    """Master bedroom dressing: a wool rug under the bed, a bench at its foot."""
    rug = material('FAB-RUG')
    wbox(WID / 2 - 60, WID / 2 + 60, DEP - 140, DEP - 10, 0.0, 0.4, rug, 'rug', soft=0.15)


def stage_powder():
    """Powder room (ID-772/773): PT-04 below the 3'-2" rail, the floating vanity with a Calacatta Viola top and splash, the
    wall-hung toilet, the linear LED sconce over the mirror. East wall local x runs south from the north corner."""
    Yl = lambda x: DEP - x
    VN, V_D, V_TOP, SLAB, SPL, V_BOX, T_CL, CHAIR, BAR = 30.875, 18.0, 32.75, 1.25, 41.0, 14.0, 15.0, 38.0, 105.0
    pt4 = material('PT-04'); viola = material('CAL-VIOLA'); oak = material('OAK-VENEER'); br = material('METAL-BRASS'); ch = material('CERAMIC-WHITE')
    for (x0, x1, y0, y1) in ((0, WID, DEP - 0.3, DEP), (0, WID, 0, 0.3), (0, 0.3, 0, DEP), (WID - 0.3, WID, 0, DEP)):
        wbox(x0, x1, y0, y1, 8.5, CHAIR - 1.0, pt4, 'wall_wainscot')
    wbox(WID - V_D, WID, Yl(DEP), Yl(VN), V_TOP - V_BOX, V_TOP, oak, 'vanity', soft=0.1)
    wbox(WID - V_D - 0.06, WID - V_D, Yl(DEP) + 0.3, Yl(VN) - 0.3, V_TOP - V_BOX / 2 - 0.06, V_TOP - V_BOX / 2 + 0.06, material('GAP'), 'drawer_line')
    wbox(WID - V_D - 0.75, WID, Yl(DEP), Yl(VN), V_TOP, V_TOP + SLAB, viola, 'vanity_top')
    wbox(WID - 0.75, WID, Yl(DEP), Yl(VN), V_TOP + SLAB, SPL, viola, 'splash')
    wbox(WID - V_D + 3, WID - 3, Yl(DEP) + 3, Yl(VN) - 3, V_TOP - 0.2, V_TOP + SLAB + 0.01, material('GAP'), 'bowl') if False else None
    # wall-hung toilet: rounded bowl off the wall, seat and lid, a brass flush plate
    wbox(WID - 21.5, WID - 0.5, Yl(T_CL) - 7.2, Yl(T_CL) + 7.2, 8.0, 15.0, ch, 'toilet', soft=3.0)
    wbox(WID - 21.8, WID - 2.5, Yl(T_CL) - 7.4, Yl(T_CL) + 7.4, 15.0, 16.2, ch, 'toilet_lid', soft=1.5)
    wbox(WID - 0.6, WID, Yl(T_CL) - 4.5, Yl(T_CL) + 4.5, 41.0, 47.0, br, 'flush_plate')
    # linear LED sconce over the mirror
    cy = Yl((VN + DEP) / 2)
    wbox(WID - 2.2, WID, cy - 12, cy + 12, BAR - 1.0, BAR + 1.0, br, 'linear_sconce')
    wbox(WID - 2.25, WID - 2.15, cy - 11.5, cy + 11.5, BAR - 0.8, BAR + 0.8, material('LED-STRIP'), 'linear_led')
    wlight(WID - 3.0, cy, BAR - 1.2, 2.0, 22.0, 18.0)
    import_model('ceramic_vase_01', 7.0, WID - 9.0, Yl(DEP - 7.0), V_TOP + SLAB, 0)


def stage_pool():
    """Pool house lounge-office (ID-401 to 405): a wool rug, a linen sofa facing the TV wall, a stone coffee table, the TV."""
    fab = material('FAB-SOFA'); rug = material('FAB-RUG'); st = material('ST-01'); wood = material('WOOD-FURN')
    cy = DEP / 2
    wbox(18, WID - 22, cy - 42, cy + 42, 0.0, 0.4, rug, 'rug', soft=0.15)
    sx0 = 30.0                                                   # sofa in the room, facing the TV wall
    wbox(sx0, sx0 + 36, cy - 44, cy + 44, 4.0, 17.0, fab, 'sofa_base', soft=2.0)
    wbox(sx0, sx0 + 10, cy - 44, cy + 44, 17.0, 31.0, fab, 'sofa_back', soft=3.0)
    for sy in (-1, 1): wbox(sx0, sx0 + 36, cy + sy * 44 - (8 if sy > 0 else 0), cy + sy * 44 + (0 if sy > 0 else 8), 17.0, 25.0, fab, 'sofa_arm', soft=3.0)
    for k in range(3): wbox(sx0 + 10, sx0 + 34, cy - 36 + k * 24 + 0.5, cy - 36 + (k + 1) * 24 - 0.5, 17.0, 21.0, fab, 'cushion', soft=2.5)
    for sy in (-24, 24): wbox(sx0 + 9, sx0 + 15, cy + sy - 10, cy + sy + 10, 21.0, 37.0, material('GARM-6'), 'pillow', soft=3.5)
    wcyl(94.0, cy, 8.0, 15.0, 16.0, 'z', st, 'coffee_table')
    import_model('wooden_bowl_01', 2.5, 92.0, cy - 4, 16.0, 0); import_model('ceramic_vase_01', 7.0, 98.0, cy + 6, 16.0, 0)
    tw, th = 57.0, 32.0                                          # 65 in. TV on the east wall
    wbox(WID - 1.6, WID - 0.1, cy - tw / 2, cy + tw / 2, 50.0, 50.0 + th, material('TV-BLACK'), 'tv')
    import_model('potted_plant_04', 34.0, WID - 14, 12.0, 0.0, 0)


STAGES = {'pool': stage_pool, 'closet': stage_closet, 'kitchen': stage_kitchen, 'mbr': stage_mbr, 'powder': stage_powder}


# ================================================================== living room (ID-230 to ID-234, owner's pick 11.09.26)
def stage_living():
    """The living room from build_great_rev1b's numbers: the fireplace wall (ID-231 view 1: plaster breast, WS-01 surround, flush
    hearth, the art-mode TV in its niche, open bookcases each side with 30 in. base cabinets, belt course with the brass rail and
    rolling ladder, the panel band, the gallery cap, the upper cases, CM-02 with its LED cove), the window wall (ID-232: FOR's
    three-panel slider and clerestory with divided lites, the band between, the 22'-4" band with the drapery pocket), the west and
    south galleries with the steel picket guard, and outside the site from FOR A-100 and A-303: the paved deck, the pool, the dining
    wing, the side fence and hedge, and the ancillary structure with its stair and pergola. World inches: X east from the west end's
    west wall, Y north from the south gallery line, Z up. Plan north is true south on this site (A-303), so the window wall faces
    the true south sun."""
    G = dict(RD=194.0, H=272.0, GFW=92.0, BELT0=117.0, BELT1=124.0, SOFFIT=128.0, FF2=154.0, GT=196.0, CROWN_B=256.0, COVE=4.0,
             BAND=268.0, BAND_W=12.0, SL0=120.0, SL1=252.0, SL_HEAD=117.0, CL_HEAD=250.0, BW=84.0, BD=24.0, BI_D=14.0, CAB_H=30.0,
             TOP_T=1.25, FB_W=42.0, FB_B=6.0, FB_T=36.0, LEG=9.0, SHELF_B=45.5, SHELF_T=48.0, TV_W=66.25, TV_H=37.75, TV_B=56.0)
    E = 280.0; RD = G['RD']; Hh = G['H']
    wallm = material(R('wall', 'PT-02')); trim = material('PT-01-SATIN'); case_m = material('PT-01-SATIN')
    ws = material('WS-01'); st1 = material('ST-01'); brass = material('METAL-BRASS'); steel = material('STEEL-PT')
    def Yw(x): return RD - x                                         # east wall view x (from the north wall) to world Y
    CX = RD / 2; B0 = (RD - G['BW']) / 2; B1 = B0 + G['BW']
    BF = E - G['BD']                                                 # breast face
    IF = E - G['BI_D']                                               # built-in face
    # ---- the breast, one plaster plane floor to the crown
    wbox(BF, E, Yw(B1), Yw(B0), 0.0, G['CROWN_B'], wallm, 'breast')
    # firebox: listed direct-vent unit, 42 x 30 opening 6 in. above the flush hearth, black glass
    h = G['FB_W'] / 2; yc = Yw(CX)
    wbox(BF - 0.01, BF + 0.4, yc - h, yc + h, G['FB_B'], G['FB_T'], material('OVEN-GLASS'), 'firebox_glass')
    wbox(BF + 0.4, BF + 12, yc - h, yc + h, G['FB_B'], G['FB_T'], material('GAP'), 'firebox')
    for k in range(5):                                               # a low gas flame bed, warm
        wbox(BF + 3, BF + 9, yc - 15 + k * 7, yc - 11 + k * 7, G['FB_B'] + 1.5, G['FB_B'] + 3.0, material('LAMP'), 'ember')
    # WS-01 surround: 9 in. legs, frieze, a 2-1/2 in. shelf at 4'-0" projecting 6 in.; bolection bead round the opening
    L_ = G['LEG']; S0 = yc - h - L_; S1 = yc + h + L_
    wbox(BF - 1.5, BF, S0, yc - h, 0.0, G['SHELF_B'], ws, 'surround_leg', soft=0.15)
    wbox(BF - 1.5, BF, yc + h, S1, 0.0, G['SHELF_B'], ws, 'surround_leg', soft=0.15)
    wbox(BF - 1.5, BF, yc - h, yc + h, G['FB_T'], G['SHELF_B'], ws, 'surround_frieze', soft=0.15)
    wbox(BF - 6.0, BF, S0 - 1.0, S1 + 1.0, G['SHELF_B'], G['SHELF_T'], ws, 'mantel_shelf', soft=0.2)
    for (a_, b_, z0, z1) in ((yc - h - 1.5, yc - h, 0, G['FB_T'] + 1.5), (yc + h, yc + h + 1.5, 0, G['FB_T'] + 1.5), (yc - h - 1.5, yc + h + 1.5, G['FB_T'], G['FB_T'] + 1.5)):
        wbox(BF - 2.25, BF - 1.5, a_, b_, z0, z1, ws, 'bolection', soft=0.3)
    wbox(BF - 20.0, BF, yc - 33.0, yc + 33.0, -0.02, 0.03, st1, 'hearth')          # flush ST-01 hearth 5'-6" x 1'-8"
    # TV: the art-mode set nearly flush in a 4 in. niche 2 in. larger each way
    tb = G['TV_B']; tw = G['TV_W']; th = G['TV_H']
    wbox(BF + 0.01, BF + 4.0, yc - tw / 2 - 2, yc + tw / 2 + 2, tb - 2, tb + th + 2, material('GAP'), 'tv_niche')
    wbox(BF + 2.6, BF + 4.0, yc - tw / 2 - 2, yc + tw / 2 + 2, tb - 2, tb + th + 2, wallm, 'niche_back')
    wbox(BF + 0.4, BF + 1.5, yc - tw / 2, yc + tw / 2, tb, tb + th, material('TV-BLACK'), 'tv')
    wbox(BF + 0.3, BF + 0.45, yc - tw / 2 + 0.6, yc + tw / 2 - 0.6, tb + 0.6, tb + th - 0.6, material('PLATE-WHITE'), 'tv_mat')
    wbox(BF + 0.25, BF + 0.35, yc - tw / 2 + 4.5, yc + tw / 2 - 4.5, tb + 4.5, tb + th - 4.5, material('ART-01'), 'tv_art')
    # ---- the built-ins each side: base cabinet, open cases, belt with the brass rail, the panel band, cap, upper cases, frieze
    rnd = _rnd.Random(23)
    books_m = [material(f'BOOK-{i}') for i in range(8)]
    def books(y0_, y1_, z, depth=9.0):
        y = y0_ + 0.5
        while y < y1_ - 1.5:
            if rnd.random() < 0.30:                                  # a gap or an object
                if rnd.random() < 0.35 and y1_ - y > 10:
                    wcyl(IF + 6, y + 4, z + 4.5, 2.6, 9.0, 'z', material('CERAMIC-WHITE'), 'vase'); y += 9; continue
                y += rnd.uniform(5, 14); continue
            run = rnd.randint(5, 14); lean = rnd.random() < 0.15
            for _ in range(run):
                t = rnd.uniform(0.8, 1.7); hh = rnd.uniform(8.0, 11.5)
                if y + t > y1_ - 1.0: break
                wbox(IF + 1.0 + rnd.uniform(0, 1.2), IF + 1.0 + depth, y, y + t, z, z + hh, rnd.choice(books_m), 'book')
                y += t + 0.05
            if rnd.random() < 0.25 and y1_ - y > 12:                  # a short horizontal stack
                for k in range(rnd.randint(3, 5)):
                    wbox(IF + 1.5, IF + 9.5, y + 0.5, y + 9.5, z + k * 1.3, z + k * 1.3 + 1.2, rnd.choice(books_m), 'book_flat')
                y += 11
            y += rnd.uniform(1.0, 3.0)
    def case(ya, yb, z0, z1, pitch=18.0, thick=2.0):
        side = 1.5
        wbox(E - 0.75, E, ya, yb, z0, z1, case_m, 'case_back')
        wbox(IF, E, ya, ya + side, z0, z1, case_m, 'case_side'); wbox(IF, E, yb - side, yb, z0, z1, case_m, 'case_side')
        n = max(1, int(round((z1 - z0) / pitch))); p_ = (z1 - z0) / n
        for k in range(1, n + 1):
            zt = z0 + k * p_
            if k < n:
                wbox(IF, E - 0.75, ya + side, yb - side, zt - thick, zt, case_m, 'shelf', soft=0.12)
                wbox(IF + 0.5, IF + 2.5, ya + side, yb - side, zt - thick - 0.25, zt - thick, steel, 'shelf_flat')   # steel flat under the nose
            books(ya + side, yb - side, z0 + (k - 1) * p_ + (0 if k == 1 else 0))
    for (ya, yb) in ((Yw(G['RD']), Yw(B1)), (Yw(B0), Yw(0.0))):      # south flank, north flank (world Y order)
        # 30 in. inset base cabinet: 4-1/2 in. toe 3 in. back, a pair of inset doors in a face frame, WS-01 top
        wbox(IF + 3, E, ya, yb, 0.0, 4.5, case_m, 'toe')
        wbox(IF, E, ya, yb, 4.5, G['CAB_H'], case_m, 'cab_frame', soft=0.1)
        dw = (yb - ya - 3.0) / 2
        for j in range(2):
            a_ = ya + 1.5 + j * (dw) + (0.0625 if j else 0); b_ = a_ + dw - 0.125
            wbox(IF - 0.02, IF + 0.75, a_, b_, 6.0, G['CAB_H'] - 1.5, case_m, 'cab_door', soft=0.1)
            wbox(IF + 0.75, IF + 1.0, a_, b_, 6.0, G['CAB_H'] - 1.5, material('GAP'), 'door_reveal')
            px = b_ - 2.0 if j == 0 else a_ + 2.0
            wcyl(IF - 0.6, px, G['CAB_H'] - 7.0, 0.25, 6.0, 'z', brass, 'pull')
        wbox(IF - 1.0, E, ya, yb, G['CAB_H'], G['CAB_H'] + G['TOP_T'], ws, 'cab_top', soft=0.15)
        case(ya, yb, G['CAB_H'] + G['TOP_T'], G['BELT0'])
        wbox(IF - 1.5, E, ya, yb, G['BELT0'], G['BELT1'], trim, 'belt', soft=0.2)
        wcyl(IF - 2.6, (ya + yb) / 2, (G['BELT0'] + G['BELT1']) / 2, 0.625, yb - ya - 1.0, 'y', brass, 'ladder_rail')
        wbox(IF, E, ya, yb, G['BELT1'], G['FF2'] - 1.5, case_m, 'panel_band')
        wbox(IF - 0.6, IF, ya + 4, yb - 4, G['BELT1'] + 4, G['FF2'] - 5.5, case_m, 'panel', soft=0.25)
        wbox(IF - 1.2, E, ya, yb, G['FF2'] - 1.5, G['FF2'], trim, 'cap', soft=0.15)
        case(ya, yb, G['FF2'], G['CL_HEAD'])
        wbox(IF, E, ya, yb, G['CL_HEAD'], G['CROWN_B'], case_m, 'frieze')
    # rolling ladder, parked at the north end: two oak stiles leaning from the floor to the brass rail, rungs on the shelf pitch
    oak = material('OAK-STAINED'); lx0 = 248.0; rz = (G['BELT0'] + G['BELT1']) / 2
    for yy in (Yw(3.0) - 1.75, Yw(21.0)):
        dx = (IF - 2.6) - lx0
        o = wbox(-0.875, 0.875, -0.875, 0.875, 0.0, math.hypot(dx, rz), oak, 'ladder_stile')
        if o:
            o.location = (lx0 * IN, (yy + 0.875) * IN, 0.0); o.rotation_euler = (0, math.atan2(dx, rz), 0)
    for k in range(1, 8):
        f_ = k / 8.0
        x_ = lx0 + f_ * ((IF - 2.6) - lx0); z_ = f_ * rz
        wbox(x_ - 0.6, x_ + 0.6, Yw(21.0), Yw(3.0) - 1.75 + 1.75, z_ - 0.5, z_ + 0.5, oak, 'ladder_rung')
    wcyl(lx0, Yw(3.0) - 0.9, 1.2, 1.2, 1.0, 'y', brass, 'ladder_wheel'); wcyl(lx0, Yw(21.0) + 0.9, 1.2, 1.2, 1.0, 'y', brass, 'ladder_wheel')
    # CM-02 crown held 4 in. under the ceiling on the east wall (cases and breast), LED cove on its top
    def crown_run(x_face, ya, yb, top):
        for k, (dz, pr) in enumerate(((0.0, 1.0), (3.0, 2.5), (6.0, 4.0), (9.0, 5.5))):
            wbox(x_face - pr, x_face, ya, yb, top - 12.0 + dz, top - 12.0 + dz + 3.0, trim, 'crown', soft=0.6)
        wbox(x_face - 5.0, x_face - 4.4, ya, yb, top, top + 0.4, material('LAMP'), 'cove_led')
    top = Hh - G['COVE']
    crown_run(IF, Yw(RD), Yw(B1), top); crown_run(BF, Yw(B1), Yw(B0), top); crown_run(IF, Yw(B0), Yw(0.0), top)
    # ---- the window wall: FOR's 3-panel slider and 3-lite clerestory, divided lites, dark bronze frames, drywall returns
    fr = material('FRAME-BLK'); gl = material('GLASS-CLEAR')
    def glazed(x0, x1, z0, z1, n, operable, y_face=RD + 2.5):
        pw = (x1 - x0) / n
        wbox(x0, x1, RD, RD + 6.0, z0, z0 + 0.5, fr, 'sill')
        for i in range(n):
            a_ = x0 + i * pw; b_ = a_ + pw
            yo = y_face + (0 if not operable else (i % 2) * 1.6)        # the sliding panels on their own tracks
            for r_ in ((a_, a_ + 2.5, z0, z1), (b_ - 2.5, b_, z0, z1), (a_, b_, z0, z0 + 3.0), (a_, b_, z1 - 2.5, z1)):
                wbox(r_[0], r_[1], yo, yo + 2.0, r_[2], r_[3], fr, 'frame', soft=0.08)
            gx0, gx1, gz0, gz1 = a_ + 2.5, b_ - 2.5, z0 + 3.0, z1 - 2.5
            wbox(gx0, gx1, yo + 0.9, yo + 1.1, gz0, gz1, gl, 'glass')
            cols, rows = 3, 7
            for c in range(1, cols):
                mx = gx0 + (gx1 - gx0) * c / cols; wbox(mx - 0.4375, mx + 0.4375, yo + 0.3, yo + 1.7, gz0, gz1, fr, 'muntin')
            for r in range(1, rows):
                mz = gz0 + (gz1 - gz0) * r / rows; wbox(gx0, gx1, yo + 0.3, yo + 1.7, mz - 0.4375, mz + 0.4375, fr, 'muntin')
            if operable and i > 0:
                wbox(a_ + 0.8, a_ + 1.6, yo - 1.2, yo, 38.0, 46.0, fr, 'pull')
    glazed(G['SL0'], G['SL1'], 0.0, G['SL_HEAD'], 3, True)
    glazed(G['SL0'], G['SL1'], G['BELT1'], G['CL_HEAD'], 3, False)
    # FOR's 22'-4" band at the window wall with the 5 in. drapery pocket 14 in. past each jamb; CM-02 under the band beside it
    PK0, PK1 = G['SL0'] - 15, G['SL1'] + 15
    wbox(G['GFW'], E, RD - G['BAND_W'], RD, G['BAND'], Hh + 0.01, material(R('ceiling', 'PT-01')), 'band')
    wbox(PK0, PK1, RD - 7.0, RD - 2.0, G['BAND'] - 0.01, Hh, material('GAP'), 'drapery_pocket')
    for (a_, b_) in ((G['GFW'], PK0), (PK1, IF)):
        for k, (dz, pr) in enumerate(((0.0, 1.0), (3.0, 2.5), (6.0, 4.0), (9.0, 5.5))):
            wbox(a_, b_, RD - pr, RD, G['BAND'] - G['COVE'] - 12.0 + dz, G['BAND'] - G['COVE'] - 9.0 + dz, trim, 'crown', soft=0.6)
    for (a_, b_) in ((G['GFW'], G['SL0']), (G['SL1'], IF)):
        wbox(a_, b_, RD - 0.6, RD, 0.0, 8.5, trim, 'base', soft=0.15)
    # ---- galleries: floor 2 over the west end and the south end, the fascia, cap and steel picket guard
    pt1 = material(R('ceiling', 'PT-01'))
    wbox(0.0, G['GFW'], 0.0, RD, G['SOFFIT'], G['FF2'], pt1, 'gallery_slab_w')
    wbox(0.0, E, -60.0, 0.0, G['SOFFIT'], G['FF2'], pt1, 'gallery_slab_s')
    wbox(0.0, G['GFW'] - 3, 0.0, RD, G['FF2'], G['FF2'] + 0.5, material(R('floor', 'WD-01')), 'floor2_w')
    wbox(0.0, E, -60.0, -3.0, G['FF2'], G['FF2'] + 0.5, material(R('floor', 'WD-01')), 'floor2_s')
    wbox(G['GFW'] - 0.6, G['GFW'], 0.0, RD, G['SOFFIT'], G['FF2'], trim, 'fascia_w')
    wbox(G['GFW'], E, -0.6, 0.0, G['SOFFIT'], G['FF2'], trim, 'fascia_s')
    wbox(G['GFW'] - 1.5, G['GFW'] + 0.5, 0.0, RD, G['FF2'] - 1.5, G['FF2'], trim, 'fascia_cap_w')
    wbox(G['GFW'], E, -1.5, 0.5, G['FF2'] - 1.5, G['FF2'], trim, 'fascia_cap_s')
    wbox(0.0, G['GFW'] - 3.0, 0.0, RD, G['SOFFIT'] - 8.0, G['SOFFIT'], trim, 'crown_w_end')   # CM-01 in the west end, simplified
    def guard(axis, a0, a1, c):
        for k in range(int((a1 - a0) / 4.5) + 1):
            p = a0 + k * 4.5
            if axis == 'y': wbox(c - 0.375, c + 0.375, p, p + 0.75, G['FF2'] + 2.0, G['GT'] - 1.5, steel, 'picket')
            else: wbox(p, p + 0.75, c - 0.375, c + 0.375, G['FF2'] + 2.0, G['GT'] - 1.5, steel, 'picket')
        for z0, z1 in ((G['FF2'] + 2.0, G['FF2'] + 3.5), (G['GT'] - 2.5, G['GT'])):
            if axis == 'y': wbox(c - 0.75, c + 0.75, a0, a1, z0, z1, steel, 'guard_rail')
            else: wbox(a0, a1, c - 0.75, c + 0.75, z0, z1, steel, 'guard_rail')
        posts = [a0] + [a0 + k * 72.0 for k in range(1, int((a1 - a0) / 72.0) + 1)] + [a1 - 2.0]
        for p in posts:
            if axis == 'y': wbox(c - 1.0, c + 1.0, p, p + 2.0, G['FF2'], G['GT'], steel, 'guard_post')
            else: wbox(p, p + 2.0, c - 1.0, c + 1.0, G['FF2'], G['GT'], steel, 'guard_post')
    guard('y', 0.0, RD - 1.0, G['GFW'] - 2.0); guard('x', G['GFW'], E - 1.0, -2.0)
    wbox(0.0, E, -60.0, -54.0, G['FF2'], Hh, wallm, 'hall_wall_s')
    wbox(0.0, 4.0, -60.0, RD, G['FF2'], Hh, wallm, 'hall_wall_w_face')
    # ---- staging (captioned): a sofa with its back on the west gallery line facing the TV, a rug and a coffee table
    fab = material('FAB-SOFA'); rug = material('FAB-RUG'); wood = material('WOOD-FURN')
    cy = yc
    wbox(110.0, 232.0, cy - 54, cy + 54, 0.0, 0.4, rug, 'rug', soft=0.15)
    sx0 = G['GFW'] + 1.0
    wbox(sx0, sx0 + 38, cy - 48, cy + 48, 4.0, 17.0, fab, 'sofa_base', soft=2.0)
    wbox(sx0, sx0 + 10, cy - 48, cy + 48, 17.0, 31.0, fab, 'sofa_back', soft=3.0)
    for sy in (-1, 1): wbox(sx0, sx0 + 38, cy + sy * 48 - (8 if sy > 0 else 0), cy + sy * 48 + (0 if sy > 0 else 8), 17.0, 25.0, fab, 'sofa_arm', soft=3.0)
    for k in range(3): wbox(sx0 + 10, sx0 + 36, cy - 40 + k * 26.7 + 0.5, cy - 40 + (k + 1) * 26.7 - 0.5, 17.0, 21.0, fab, 'cushion', soft=2.5)
    wbox(160.0, 196.0, cy - 22, cy + 22, 0.0, 15.0, wood, 'coffee_table', soft=0.6)
    import_model('wooden_bowl_01', 2.5, 176.0, cy - 6, 15.0, 0); import_model('ceramic_vase_01', 8.0, 184.0, cy + 10, 15.0, 0)
    # ---- outside (FOR A-100 at 1/8 in., A-303): X = 92 + (site x - 773) / 0.75, Y = 202 + (705 - site y) / 0.75
    ext = material('STUCCO-EXT'); deck = material('DECK-01'); hedge = material('HEDGE')
    wbox(-200.0, 360.0, RD + 6.0, 830.0, -6.0, -0.5, deck, 'deck')
    wbox(-193.0, 86.0, RD + 6.0, 481.0, -6.0, 300.0, ext, 'dining_wing')            # the kitchen and dining wing, its east face on the notch
    # the pool: 6'-8" x 11'-0" (A-100), stone coping 12 in., water 6 in. below the coping
    px0, px1, py0, py1 = 197.0, 277.0, 286.0, 418.0
    for r_ in ((px0 - 12, px1 + 12, py0 - 12, py0), (px0 - 12, px1 + 12, py1, py1 + 12), (px0 - 12, px0, py0, py1), (px1, px1 + 12, py0, py1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -0.5, 1.0, st1, 'coping', soft=0.4)
    pp = material('POOL-PLASTER')
    wbox(px0, px1, py0, py1, -54.0, -52.0, pp, 'pool_floor')
    for r_ in ((px0 - 1, px0, py0, py1), (px1, px1 + 1, py0, py1), (px0, px1, py0 - 1, py0), (px0, px1, py1, py1 + 1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -54.0, 1.0, pp, 'pool_wall')
    wbox(px0, px1, py0, py0 + 20, -54.0, -18.0, pp, 'pool_bench')        # the step and bench at the house end (A-100 lines)
    wm = bpy.data.materials.new('POOL-WATER'); wm.use_nodes = True; bw_ = wm.node_tree.nodes['Principled BSDF']
    bw_.inputs['Base Color'].default_value = (0.78, 0.93, 0.95, 1); bw_.inputs['Roughness'].default_value = 0.03
    bw_.inputs['Transmission Weight'].default_value = 1.0; bw_.inputs['IOR'].default_value = 1.33
    tex = wm.node_tree.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 6.0
    bump = wm.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08
    wm.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height']); wm.node_tree.links.new(bump.outputs['Normal'], bw_.inputs['Normal'])
    wbox(px0, px1, py0, py1, -6.5, -6.0, wm, 'pool_water')
    # the side yard: fence 1 ft inside the east line with a hedge in front (landscape plan, placeholder)
    wbox(338.0, 341.0, RD + 6.0, 818.0, 0.0, 72.0, ext, 'fence')
    wbox(306.0, 338.0, RD + 30.0, 818.0, 0.0, 108.0, hedge, 'hedge', soft=6.0)
    wbox(-200.0, 341.0, 818.0, 821.0, 0.0, 72.0, ext, 'fence_rear'); wbox(-200.0, 341.0, 790.0, 818.0, 0.0, 120.0, hedge, 'hedge_rear', soft=8.0)
    # the ancillary structure (A-204, A-303): 28'-9" x 10'-3", slab 11'-0", parapet 14'-0"; its north face (toward the house):
    # a full-lite door, a picture window; the exterior stair on its plan-east side to the roof deck, metal picket railing; pergola
    ax0, ax1, ay0, ay1 = -129.0, 216.0, 575.0, 698.0
    wbox(ax0, ax1, ay0, ay1, -6.0, 132.0, ext, 'ancillary')
    wbox(ax0, ax1, ay0, ay0 + 6, 132.0, 168.0, ext, 'parapet'); wbox(ax0, ax1, ay1 - 6, ay1, 132.0, 168.0, ext, 'parapet')
    wbox(ax0, ax0 + 6, ay0, ay1, 132.0, 168.0, ext, 'parapet'); wbox(ax1 - 6, ax1, ay0, ay1, 132.0, 150.0, ext, 'parapet')
    wbox(23.0, 55.0, ay0 - 0.5, ay0 + 0.5, 0.0, 96.0, fr, 'anc_door_frame')
    wbox(25.0, 53.0, ay0 - 0.7, ay0 - 0.4, 2.0, 94.0, material('GLASS-DARK'), 'anc_door_glass')
    wbox(99.0, 178.0, ay0 - 0.5, ay0 + 0.5, 36.0, 96.0, fr, 'anc_window_frame')
    wbox(101.0, 176.0, ay0 - 0.7, ay0 - 0.4, 38.0, 94.0, material('GLASS-DARK'), 'anc_window_glass')
    for k in range(18):                                               # stair, 18 risers to the slab top, rising plan north
        z_ = (k + 1) * 132.0 / 18.0; y_ = ay0 - 10 + k * 7.4
        wbox(ax1, ax1 + 40.0, y_, y_ + 11.0, z_ - 1.5, z_, ext, 'anc_step')
    wbox(ax1, ax1 + 40.0, ay0 - 10, ay0 + 120, -6.0, 6.0, material('ST-05'), 'anc_stair_base')
    for k in range(30):
        y_ = ay0 - 6 + k * 4.4; z_ = max(0.0, (y_ - ay0 + 10) / 7.4 * 132.0 / 18.0)
        wbox(ax1 + 38.5, ax1 + 39.25, y_, y_ + 0.75, z_, z_ + 36.0, steel, 'anc_picket')
    for (x_, y_) in ((-40.0, 590.0), (130.0, 590.0), (-40.0, 683.0), (130.0, 683.0)):   # pergola by others (A-303: top 19'-0")
        wbox(x_, x_ + 6, y_, y_ + 6, 132.0, 228.0, material('WOOD-FURN'), 'pergola_post')
    for k in range(14):
        wbox(-46.0, 142.0, 586.0 + k * 7.5, 588.0 + k * 7.5, 222.0, 228.0, material('WOOD-FURN'), 'pergola_slat')
    # daylight through the slider and the clerestory: portals (the shell has no glass doors for photoreal to find), and the sun
    for (x0, x1, z0, z1) in ((G['SL0'] + 2, G['SL1'] - 2, 3.0, G['SL_HEAD'] - 3), (G['SL0'] + 2, G['SL1'] - 2, G['BELT1'] + 3, G['CL_HEAD'] - 3)):
        ld = bpy.data.lights.new('portal', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = (x1 - x0) * IN; ld.size_y = (z1 - z0) * IN
        ld.cycles.is_portal = True
        po = bpy.data.objects.new('portal', ld); bpy.context.collection.objects.link(po)
        po.location = ((x0 + x1) / 2 * IN, (RD + 7.0) * IN, (z0 + z1) / 2 * IN); po.rotation_euler = (math.radians(90), 0, 0)
    if not any(o.type == 'LIGHT' and o.data.type == 'SUN' for o in bpy.data.objects):
        sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 10.0; sun_d.color = (1.0, 0.96, 0.9)
        sun_o = bpy.data.objects.new('sun', sun_d); bpy.context.collection.objects.link(sun_o)


STAGES['living'] = stage_living
