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


def wprism_xz(pts, y0, y1, mat, name='prism'):
    """A flat shape in an elevation plane (X, Z points in order, concave allowed) extruded along Y from y0 to y1."""
    n = len(pts); v = [(x_ * IN, y0 * IN, z_ * IN) for x_, z_ in pts] + [(x_ * IN, y1 * IN, z_ * IN) for x_, z_ in pts]
    f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 4])   # ear-clipped caps: a concave n-gon left a hole by the apex
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def leafy(objs, density=900.0, seed=3):
    """Clip a hedge: instance real leaves over each box's surface with geometry nodes (3-1/2 x 1-3/4 in. leaves, tilted at
    random, standing off the surface up to 1-1/2 in.). A textured box read as green foam (R6 review 11.10.26)."""
    leaf_me = bpy.data.meshes.get('leaf_src')
    if leaf_me is None:
        n_ = 10; pts = [(1.75 * _m.cos(2 * _m.pi * i / n_) * IN, 0.875 * _m.sin(2 * _m.pi * i / n_) * IN, 0.15 * IN * (_m.cos(2 * _m.pi * i / n_)) ** 2) for i in range(n_)]
        leaf_me = bpy.data.meshes.new('leaf_src'); leaf_me.from_pydata([(0, 0, -0.08 * IN)] + pts, [], [(0, 1 + i, 1 + (i + 1) % n_) for i in range(n_)])
        lm = bpy.data.materials.new('LEAF'); lm.use_nodes = True; ln = lm.node_tree.nodes; ll = lm.node_tree.links
        pb = ln['Principled BSDF']; pb.inputs['Roughness'].default_value = 0.45
        oi_ = ln.new('ShaderNodeObjectInfo'); cr_ = ln.new('ShaderNodeValToRGB')
        cr_.color_ramp.elements[0].color = (0.018, 0.045, 0.012, 1); cr_.color_ramp.elements[1].color = (0.10, 0.20, 0.04, 1)
        ll.new(oi_.outputs['Random'], cr_.inputs['Fac']); ll.new(cr_.outputs['Color'], pb.inputs['Base Color'])
        tr_ = ln.new('ShaderNodeBsdfTranslucent'); ll.new(cr_.outputs['Color'], tr_.inputs['Color'])
        mx_ = ln.new('ShaderNodeMixShader'); mx_.inputs['Fac'].default_value = 0.25
        ll.new(pb.outputs['BSDF'], mx_.inputs[1]); ll.new(tr_.outputs['BSDF'], mx_.inputs[2]); ll.new(mx_.outputs['Shader'], ln['Material Output'].inputs['Surface'])
        leaf_me.materials.append(lm)
        for pg in leaf_me.polygons: pg.use_smooth = True
        lo = bpy.data.objects.new('leaf_src', leaf_me); bpy.context.collection.objects.link(lo); lo.location = (0, 0, -500 * IN)
    lo = bpy.data.objects['leaf_src']
    ng = bpy.data.node_groups.get('LEAVES')
    if ng is None:
        ng = bpy.data.node_groups.new('LEAVES', 'GeometryNodeTree')
        ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        N = ng.nodes; L = ng.links
        gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
        ds = N.new('GeometryNodeDistributePointsOnFaces'); ds.inputs['Density'].default_value = density; ds.inputs['Seed'].default_value = seed
        oi = N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = lo; oi.inputs['As Instance'].default_value = False
        ip = N.new('GeometryNodeInstanceOnPoints')
        rv = N.new('FunctionNodeRandomValue'); rv.data_type = 'FLOAT_VECTOR'
        rv.inputs['Min'].default_value = (-0.7, -0.7, -3.14); rv.inputs['Max'].default_value = (0.7, 0.7, 3.14)
        e2r = N.new('FunctionNodeEulerToRotation'); rr = N.new('FunctionNodeRotateRotation'); rr.rotation_space = 'LOCAL'
        rs = N.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.inputs[2].default_value = 0.7; rs.inputs[3].default_value = 1.3
        ro = N.new('FunctionNodeRandomValue'); ro.data_type = 'FLOAT'; ro.inputs[2].default_value = 0.0; ro.inputs[3].default_value = 1.5 * IN; ro.inputs['Seed'].default_value = 7
        vm = N.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'
        sp = N.new('GeometryNodeSetPosition'); jn = N.new('GeometryNodeJoinGeometry')
        L.new(gi.outputs[0], ds.inputs['Mesh'])
        L.new(ds.outputs['Normal'], vm.inputs[0]); L.new(ro.outputs[1], vm.inputs['Scale'])
        L.new(ds.outputs['Points'], sp.inputs['Geometry']); L.new(vm.outputs['Vector'], sp.inputs['Offset'])
        L.new(sp.outputs['Geometry'], ip.inputs['Points']); L.new(oi.outputs['Geometry'], ip.inputs['Instance'])
        L.new(rv.outputs[0], e2r.inputs[0]); L.new(ds.outputs['Rotation'], rr.inputs[0]); L.new(e2r.outputs[0], rr.inputs[1])
        L.new(rr.outputs[0], ip.inputs['Rotation']); L.new(rs.outputs[1], ip.inputs['Scale'])
        L.new(gi.outputs[0], jn.inputs[0]); L.new(ip.outputs['Instances'], jn.inputs[0]); L.new(jn.outputs[0], go.inputs[0])
    for o in objs:
        if o is None: continue
        md = o.modifiers.new('leaves', 'NODES'); md.node_group = ng


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
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 4])   # ear-clipped caps: a concave n-gon left a hole by the apex
    bm.to_mesh(me); bm.free()
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
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 4])   # ear-clipped caps: a concave n-gon left a hole by the apex
    bm.to_mesh(me); bm.free()
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
    # the dining end (owner 11.11.26, his reference): a 94 x 40 soft-rectangle travertine top on a dark bronze tulip pedestal,
    # six camel velvet chairs on bronze frames, an oval two-tier glass-rod chandelier in aged brass 33 in. over the top.
    # Placed east of the island: 58 in. from the island top's seating edge to the table (stools and chairs back to back,
    # VERIFY 60 in.), 37-3/8 in. from the table to the slider; on the island's centre line.
    # slider 04 on the east wall (FOR A-201: 15'-9" four-panel slider, head 9'-9"): the view captured its glazing but the
    # glazing builder is a no-op, so the wall rendered solid (found 11.11.26). Frames in FOR's dark bronze, clear glass, the
    # deck and planting outside. View x maps to world Y = DEP - (x - 24) (the east view's --shift EAST=-24).
    ev = next((v for v in ALL if v['view'].startswith('EAST ELEVATION - SLIDER')), None)
    if ev:
        fr_ = material('FRAME-BLK'); gl_ = material('GLASS-CLEAR'); E_ = WID
        SH_ = 111.5                                                         # head lowered from 9'-9" so the 8-1/4" crown runs over it (owner 11.11.26)
        gz = sorted((c['args']['x0'], c['args']['x1']) for c in ev['calls'] if c['comp'] == 'glazing')
        Yv = lambda x: DEP - (x - 24.0)
        edges = [52.0] + [q for g in gz for q in g] + [241.0]
        for k in range(0, len(edges), 2):                                   # jambs and mullions between the lites
            a_, b_ = edges[k], edges[k + 1]
            if b_ - a_ > 0.2: wbox(E_ + 1.0, E_ + 4.5, Yv(b_), Yv(a_), 0.0, SH_, fr_, 'slider_stile')
        for (a_, b_) in gz:
            wbox(E_ + 1.0, E_ + 4.5, Yv(b_), Yv(a_), 0.0, 3.0, fr_, 'slider_sill'); wbox(E_ + 1.0, E_ + 4.5, Yv(b_), Yv(a_), SH_ - 2.5, SH_, fr_, 'slider_head')
            wbox(E_ + 2.6, E_ + 2.85, Yv(b_), Yv(a_), 3.0, SH_ - 2.5, gl_, 'slider_glass')
            wcyl(E_ + 0.6, Yv(b_) + 2.5, 40.0, 0.35, 14.0, 'z', fr_, 'slider_pull')
        # outside: render with --context living, which brings the deck, the pool, the living wing and the yard (stage_living)
    MATS.setdefault('FAB-VELVET-CAMEL', {'hex': '#A07A52', 'rough': 0.74, 'kind': 'fabric', 'texture': 'acg/Fabric062'})
    camel = material('FAB-VELVET-CAMEL')
    DX_ = ISL_X - TOFF + TOPD + 58.0 + 20.0; DY_ = yN - ISL_L / 2
    dining_table(DX_, DY_, 94.0, 40.0, 'y')
    for dy in (-28.0, 0.0, 28.0):
        dining_chair(DX_ - 27.6, DY_ + dy, '+x', camel, 'dchair_w'); dining_chair(DX_ + 27.6, DY_ + dy, '-x', camel, 'dchair_e')
    dining_chair(DX_, DY_ + 53.5, '-y', camel, 'dchair_n'); dining_chair(DX_, DY_ - 53.5, '+y', camel, 'dchair_s')   # one at each end (owner 11.11.26)
    oval_rod_chandelier(DX_, DY_, 63.0, H, 60.0, 30.0, 'y')


def board_material(code='WD-01'):
    """Per-board wood (floors_gen.py): the grain scan along each board (UVMap, inches), its own cut and tone from the 'rnd'
    UV (two random numbers per board), the floor code's tint, a micro-bevel at the board edges (the joints between them are
    real gaps over a dark underlay)."""
    key = code + '-boards'
    m = bpy.data.materials.get(key)
    if m: return m
    spec = MATS.get(code, {}); m = bpy.data.materials.new(key); m.use_nodes = True
    N_ = m.node_tree.nodes; L_ = m.node_tree.links; b = N_['Principled BSDF']
    folder = spec.get('texture', 'oak_veneer_01'); tsz_in = 39.37 * _tex_size(spec, folder, 1.0)
    uv = N_.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'
    rn = N_.new('ShaderNodeUVMap'); rn.uv_map = 'rnd'
    sep = N_.new('ShaderNodeSeparateXYZ'); L_.new(rn.outputs['UV'], sep.inputs[0])
    def mth(op, a_, b_):
        n_ = N_.new('ShaderNodeMath'); n_.operation = op
        for i_, v_ in enumerate((a_, b_)):
            (L_.new(v_, n_.inputs[i_]) if not isinstance(v_, (int, float)) else n_.inputs[i_].__setattr__('default_value', v_))
        return n_.outputs[0]
    sc = N_.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; L_.new(uv.outputs['UV'], sc.inputs[0]); sc.inputs['Scale'].default_value = 1.0 / tsz_in
    off = N_.new('ShaderNodeCombineXYZ'); L_.new(mth('MULTIPLY', sep.outputs['X'], 7.0), off.inputs['X']); L_.new(mth('MULTIPLY', sep.outputs['Y'], 5.0), off.inputs['Y'])
    ad = N_.new('ShaderNodeVectorMath'); ad.operation = 'ADD'; L_.new(sc.outputs[0], ad.inputs[0]); L_.new(off.outputs[0], ad.inputs[1])
    def tex(name, cs):
        t_ = N_.new('ShaderNodeTexImage'); t_.image = bpy.data.images.load(_map(folder, name), check_existing=True)
        t_.image.colorspace_settings.name = cs; L_.new(ad.outputs[0], t_.inputs['Vector']); return t_
    d_ = tex('Diffuse.jpg', 'sRGB'); r_ = tex('Rough.jpg', 'Non-Color'); n_ = tex('nor_gl.jpg', 'Non-Color')
    mx1 = N_.new('ShaderNodeMix'); mx1.data_type = 'RGBA'; mx1.blend_type = 'MULTIPLY'; mx1.inputs['Factor'].default_value = 1.0
    L_.new(d_.outputs['Color'], mx1.inputs[6]); mx1.inputs[7].default_value = (*spec.get('tint', [1, 1, 1]), 1)
    tone = mth('ADD', mth('MULTIPLY', mth('FRACT', mth('ADD', mth('MULTIPLY', sep.outputs['X'], 7.31), mth('MULTIPLY', sep.outputs['Y'], 3.17)), 0), 0.30), 0.84)
    gg = N_.new('ShaderNodeCombineColor'); L_.new(tone, gg.inputs[0]); L_.new(tone, gg.inputs[1]); L_.new(mth('MULTIPLY', tone, 0.97), gg.inputs[2])
    mx2 = N_.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; mx2.blend_type = 'MULTIPLY'; mx2.inputs['Factor'].default_value = 1.0
    L_.new(mx1.outputs[2], mx2.inputs[6]); L_.new(gg.outputs[0], mx2.inputs[7]); L_.new(mx2.outputs[2], b.inputs['Base Color'])
    mr = N_.new('ShaderNodeMapRange'); base_r = spec.get('rough', 0.35)
    mr.inputs['To Min'].default_value = max(0.05, base_r - 0.12); mr.inputs['To Max'].default_value = base_r + 0.12
    L_.new(r_.outputs['Color'], mr.inputs['Value']); L_.new(mr.outputs['Result'], b.inputs['Roughness'])
    nm = N_.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.6; nm.uv_map = 'UVMap'; L_.new(n_.outputs['Color'], nm.inputs['Color'])
    bv = N_.new('ShaderNodeBevel'); bv.samples = 6; bv.inputs['Radius'].default_value = 0.045 * IN
    L_.new(nm.outputs['Normal'], bv.inputs['Normal']); L_.new(bv.outputs['Normal'], b.inputs['Normal'])
    return m


def board_floor(key, code='WD-01', top=0.0, thick=0.75, under=('floor', 'nook_floor')):
    """Build render/floors/<key>.json (floors_gen.py): one mesh of every board, top at `top`, its UVs along the board in
    inches; the room's own floor slabs drop 0.8 in. and turn dark, the underlay seen in the joints."""
    d = json.load(open(os.path.join(HERE, 'floors', key + '.json')))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap'); rl = bm.loops.layers.uv.new('rnd')
    for b_ in d['field'] + d['border']:
        pts = b_['pts']; a_ = _m.radians(b_['ang']); ca, sa = _m.cos(a_), _m.sin(a_)
        loc = lambda p: (p[0] * ca + p[1] * sa, -p[0] * sa + p[1] * ca)
        tv = [bm.verts.new((x * IN, y * IN, top * IN)) for x, y in pts]
        bv_ = [bm.verts.new((x * IN, y * IN, (top - thick) * IN)) for x, y in pts]
        try:
            ft = bm.faces.new(tv)
        except ValueError:
            continue
        for lp in ft.loops:
            u_, v_ = loc((lp.vert.co.x / IN, lp.vert.co.y / IN)); lp[uvl].uv = (u_, v_); lp[rl].uv = tuple(b_['r'])
        n_ = len(pts)
        for i in range(n_):
            f_ = bm.faces.new((tv[(i + 1) % n_], tv[i], bv_[i], bv_[(i + 1) % n_]))
            for lp in f_.loops:
                u_, v_ = loc((lp.vert.co.x / IN, lp.vert.co.y / IN)); lp[uvl].uv = (u_, v_ + lp.vert.co.z / IN); lp[rl].uv = tuple(b_['r'])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('board_floor'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('board_floor', me); bpy.context.collection.objects.link(o); o.data.materials.append(board_material(code))
    MATS.setdefault('FLOOR-UNDER', {'hex': '#17110C', 'rough': 0.9, 'kind': 'paint'})
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH' and ob.name.split('.')[0] in under:
            ob.location[2] -= (thick + 0.05) * IN; ob.data.materials.clear(); ob.data.materials.append(material('FLOOR-UNDER'))
    return o


def terrace(x0, x1, y0, y1, z=-2.0, rails=(), tile=24.0, joint=0.125):
    """A floor-2 terrace outside the doors and windows (owner 11.11.26: the windows are on the second floor with a terrace
    outside): porcelain tile (owner, Sept 2026: terraces porcelain) 24 x 24 with 1/8 in. joints over a dark bed, top at z
    (VERIFY the step down), and a 42 in. matte black aluminum picket guard on each open edge in `rails` ((xa, ya, xb, yb),
    VERIFY: guard type not yet drawn)."""
    MATS.setdefault('PORC-TERR', {'hex': '#D9D0C1', 'rough': 0.55, 'kind': 'paint'})
    MATS.setdefault('ALU-BLK', {'hex': '#141414', 'rough': 0.42, 'kind': 'paint'})
    MATS.setdefault('TERR-BED', {'hex': '#5E5850', 'rough': 0.9, 'kind': 'paint'})
    wbox_abs(x0, x1, y0, y1, z - 3.0, z - 0.1, material('TERR-BED'), 'terrace_bed')
    bm = bmesh.new(); pm = material('PORC-TERR')
    nx_ = int((x1 - x0) / tile) + 1; ny_ = int((y1 - y0) / tile) + 1
    for i in range(nx_):
        for j in range(ny_):
            a0, a1 = x0 + i * tile + joint / 2, min(x1, x0 + (i + 1) * tile) - joint / 2
            b0, b1 = y0 + j * tile + joint / 2, min(y1, y0 + (j + 1) * tile) - joint / 2
            if a1 - a0 < 0.5 or b1 - b0 < 0.5: continue
            v = [bm.verts.new((xx * IN, yy * IN, zz * IN)) for zz in (z - 0.4, z) for xx, yy in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
            for f_ in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[k] for k in f_])
    me = bpy.data.meshes.new('terrace_tile'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('terrace_tile', me); bpy.context.collection.objects.link(o); o.data.materials.append(pm)
    alu = material('ALU-BLK')
    for xa, ya, xb, yb in rails:
        Lr = _m.hypot(xb - xa, yb - ya); ux, uy = (xb - xa) / Lr, (yb - ya) / Lr; n_ = int(Lr / 4.0)
        for k in range(n_ + 1):
            cx_, cy_ = xa + ux * Lr * k / n_, ya + uy * Lr * k / n_
            wbox_abs(cx_ - 0.375, cx_ + 0.375, cy_ - 0.375, cy_ + 0.375, z + 2.0, z + 40.5, alu, 'terr_picket')
        for zb, zt in ((z + 1.0, z + 2.5), (z + 40.5, z + 42.0)):
            wbox_abs(min(xa, xb) - 0.75, max(xa, xb) + 0.75, min(ya, yb) - 0.75, max(ya, yb) + 0.75, zb, zt, alu, 'terr_rail')
        for cx_, cy_ in ((xa, ya), (xb, yb)): wbox_abs(cx_ - 1, cx_ + 1, cy_ - 1, cy_ + 1, z, z + 42.0, alu, 'terr_post')


def planter(x0, x1, y0, y1, h=24.0, z=-2.0):
    """A built-in planter bed (ID-102: PLANTER BED outside the master bedroom window): stucco walls, soil, a clipped hedge."""
    MATS.setdefault('STUCCO', {'hex': '#E8E2D6', 'rough': 0.85, 'kind': 'paint'}); MATS.setdefault('SOIL', {'hex': '#3B2E24', 'rough': 1.0, 'kind': 'paint'})
    MATS.setdefault('HEDGE', {'hex': '#3E5A2E', 'rough': 0.95, 'kind': 'fabric', 'texture': 'acg/Fabric086'})
    st = material('STUCCO')
    for a in ((x0, x1, y0, y0 + 6), (x0, x1, y1 - 6, y1), (x0, x0 + 6, y0, y1), (x1 - 6, x1, y0, y1)): wbox_abs(a[0], a[1], a[2], a[3], z - 12, z + h, st, 'planter_wall')
    wbox_abs(x0 + 6, x1 - 6, y0 + 6, y1 - 6, z - 12, z + h - 4, material('SOIL'), 'planter_soil')
    rr = _rnd.Random(5)
    for k in range(int((x1 - x0 - 12) / 14)):
        cx_ = x0 + 13 + k * 14 + rr.uniform(-1, 1); cy_ = (y0 + y1) / 2 + rr.uniform(-2, 2); hh = rr.uniform(16, 20)
        wbox(cx_ - 9, cx_ + 9, cy_ - (y1 - y0) / 2 + 9, cy_ + (y1 - y0) / 2 - 9, z + h - 4, z + h - 4 + hh, material('HEDGE'), 'hedge', soft=6.0)


def slot_diffuser(x0, x1, y0, y1, z, slots=1, name='slot_diffuser'):
    """A linear slot diffuser or return in a ceiling at z (RCP, FOR M-100/M-101): a dark plenum seen through 3/4 in. slots
    in a white flanged frame, long side along the longer of the two spans."""
    MATS.setdefault('DIFF-WHITE', {'hex': '#F2F1EC', 'rough': 0.35, 'kind': 'paint'})
    fw = material('DIFF-WHITE'); gap = material('GAP'); fl = 0.6
    wbox_abs(x0, x1, y0, y1, z - 0.1, z - 0.01, gap, name + '_plenum')
    along_y = (y1 - y0) >= (x1 - x0)
    a0, a1 = (x0, x1) if along_y else (y0, y1)
    n_ = max(1, slots); sw = (a1 - a0 - fl * (n_ + 1)) / n_
    cuts = [a0] + [a0 + fl + k * (sw + fl) for k in range(1, n_)] + [a1 - fl]
    for c_ in cuts:
        if along_y: wbox_abs(c_, c_ + fl, y0, y1, z - 0.3, z - 0.1, fw, name)
        else: wbox_abs(x0, x1, c_, c_ + fl, z - 0.3, z - 0.1, fw, name)
    if along_y:
        for yy in (y0, y1 - fl): wbox_abs(x0, x1, yy, yy + fl, z - 0.3, z - 0.1, fw, name)
    else:
        for xx in (x0, x1 - fl): wbox_abs(xx, xx + fl, y0, y1, z - 0.3, z - 0.1, fw, name)


def pillow(cx, cy, cz, facing, mat, w=19.0, h=19.0, t=6.0, tilt=14.0, spin=0.0, name='pillow'):
    """A throw pillow leaning on a sofa back: a rounded, puffed cushion (subdivided bevelled box), its back against the back
    cushion, tilted `tilt` degrees toward it. facing: the way the seat faces ('-x', '+x', '-y', '+y'). (A square box stood
    upright read as a block, owner 11.11.26.)"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx * IN, cy * IN, cz * IN)); o = bpy.context.active_object; o.name = name
    along_x = facing in ('-x', '+x'); sg = -1 if facing in ('-x', '-y') else 1
    o.scale = ((t if along_x else w) * IN, (w if along_x else t) * IN, h * IN)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = 2.2 * IN; bv.segments = 3; bv.limit_method = 'NONE'
    ss = o.modifiers.new('subsurf', 'SUBSURF'); ss.levels = 2; ss.render_levels = 2
    # puff: the faces bulge (scale the middle out along the thickness)
    for v in o.data.vertices:
        u = v.co.y / (w * IN / 2) if along_x else v.co.x / (w * IN / 2); vv = v.co.z / (h * IN / 2)
        k = max(0.0, 1 - u * u) * max(0.0, 1 - vv * vv)
        if along_x: v.co.x *= (1 + 0.6 * k)
        else: v.co.y *= (1 + 0.6 * k)
    a_ = _m.radians(tilt) * (-sg)
    o.rotation_euler = ((0, a_, _m.radians(spin)) if along_x else (-a_, 0, _m.radians(spin)))
    for pg in o.data.polygons: pg.use_smooth = True
    o.data.materials.append(mat); return o


def lounge_chair(cx, cy, facing='-x', name='lounge'):
    """Owner's reference (11.11.26, the reading nook): a low lounge chair, walnut frame with splayed legs and flat arms, a
    cream boucle seat and a raked back cushion. (cx, cy) the seat centre; facing '-x' or '+x' or '-y' or '+y'."""
    MATS.setdefault('WALNUT', {'hex': '#4A2F1E', 'rough': 0.45, 'kind': 'wood', 'texture': 'oak_veneer_01', 'tint': [0.42, 0.29, 0.21]})
    wal = material('WALNUT'); bou = boucle_material('FAB-BOUCLE-CREAM', '#E2D9CA', '#EFE8DC')
    sgn = {'-x': -1, '+x': 1, '-y': -1, '+y': 1}[facing]; along_x = facing in ('-x', '+x')
    def P(u, v):          # chair local: u from the front edge toward the back, v across (left to right seen from the front)
        return (cx - sgn * (u - 15.0), cy + sgn * v) if along_x else (cx + sgn * v, cy - sgn * (u - 15.0))
    def B(u0, u1, v0, v1, z0, z1, mat, nm, soft=0.0):
        (xa, ya), (xb, yb) = P(u0, v0), P(u1, v1)
        return wbox(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), z0, z1, mat, nm, soft=soft)
    for v in (-14.0, 12.75):                                               # side frames: front and back legs, flat arm
        B(1.0, 3.0, v, v + 1.25, 0.0, 24.0, wal, nm=name + '_leg', soft=0.25)
        B(26.0, 28.0, v, v + 1.25, 0.0, 22.0, wal, nm=name + '_leg', soft=0.25)
        B(-0.5, 29.0, v - 0.25, v + 1.5, 23.0, 24.4, wal, nm=name + '_arm', soft=0.4)
        B(2.0, 27.0, v, v + 1.25, 11.0, 13.0, wal, nm=name + '_rail', soft=0.2)
    B(2.0, 27.5, -12.75, 12.75, 11.5, 13.0, wal, nm=name + '_deck')
    B(2.5, 26.0, -12.6, 12.6, 13.0, 18.5, bou, nm=name + '_seat', soft=2.2)
    pts = [(21.5, 17.0), (27.0, 17.0), (32.5, 36.0), (27.0, 37.5)]           # the raked back cushion, in (u, z)
    if along_x: o_ = wprism_xz([(P(u, 0)[0], z) for u, z in pts], cy - 12.4, cy + 12.4, bou, name + '_back')
    else: o_ = wprism_yz([(P(u, 0)[1], z) for u, z in pts], cx - 12.4, cx + 12.4, bou, name + '_back')
    bv = o_.modifiers.new('bevel', 'BEVEL'); bv.width = 2.0 * IN; bv.segments = 4; bv.limit_method = 'NONE'
    for pg in o_.data.polygons: pg.use_smooth = True
    for v_ in (-11.5, 11.5): B(23.0, 31.5, v_ - 1.25, v_ + 1.25, 14.0, 34.0, wal, nm=name + '_back_post', soft=0.3) if False else None


def drum_table(cx, cy, r=9.0, h=20.0):
    """A cognac leather drum side table (owner's reference)."""
    MATS.setdefault('LEATHER-COGNAC', {'hex': '#8A4E2A', 'rough': 0.45, 'kind': 'fabric', 'texture': 'acg/Leather026'})
    lt = material('LEATHER-COGNAC'); o = wcyl(cx, cy, h / 2, r, h, 'z', lt, 'drum_table')
    wcyl(cx, cy, h + 0.25, r - 0.6, 0.5, 'z', lt, 'drum_top')
    import_model('wooden_bowl_01', 2.0, cx, cy, h + 0.5, 0)


def stage_mbr():
    """Master bedroom (ID-310 to ID-313; shell from build_mbr_shell.py, room frame X east of the west wall face, Y north of the
    window wall face). The reading nook open to the room at its southeast: its four walls built from their own elevations at
    their own places, its floor and its 9'-6" ceiling (RCP: 9'-10" in the room, the step at the window wall line), the two
    L1 downlights of the RCP, the arched bookcase frame, jib door 21. A wool rug under the bed."""
    global V, roles
    if 'NOOK' not in ' '.join(v_['view'] or '' for v_ in ALL):    # the old 117 in. box (mbr_views.json): the rug only
        wbox(WID / 2 - 60, WID / 2 + 60, DEP - 140, DEP - 10, 0.0, 0.4, material('FAB-RUG'), 'rug', soft=0.15); return
    V0, R0 = V, roles
    NX0, NX1, NY0, NY1, NH = 132.2, 231.8, -49.9, 44.0, 114.0
    at = lambda name: next(i for i, v_ in enumerate(ALL) if v_['view'] == name)
    place = lambda X, Y, rot: Matrix.Translation((X * IN, Y * IN, 0)) @ Matrix.Rotation(_m.radians(rot), 4, 'Z')
    build_wall(at('READING NOOK - NORTH WALL'), place(NX0, NY1, 0), 100.0)
    build_wall(at('READING NOOK - EAST WALL'), place(NX1, NY1, -90), 100.0)
    build_wall(at('READING NOOK - SOUTH WALL'), place(NX1, NY0, 180), 100.0)
    build_wall(at('READING NOOK - WEST WALL, BOOKCASE'), place(NX0, NY0, 90), 100.0)
    V, roles = V0, R0
    by = DEP - 58.625                                                                         # the bed axis (ID-312)
    wd = material(R('floor', 'WD-01')); clg = material(R('ceiling', 'PT-01')); trim = material(R('cabinet', 'CAB-CREAM'), '-trim')   # the bookcase: cabinetry colour
    # floor: the room's floor reaches X 195.375 and Y -12; the rest of the nook in the same world-mapped boards, no overlap
    wbox_abs(WID + 12, NX1 + 8, NY0 - 8, NY1 + 8, -2.0, 0.0, wd, 'nook_floor')
    wbox_abs(NX0 - 8, WID + 12, NY0 - 8, -12.0, -2.0, 0.0, wd, 'nook_floor')
    # ceilings: the nook south of the window wall line at 9'-6"; the strip east of the bed wall at the room's 9'-10"
    # owner 11.11.26: the cove runs on round the nook: its field at the room's 9'-10" (FOR's 9'-6" there to confirm), the
    # cove ledge at 9'-6" on its walls
    wbox_abs(NX0 - 0.02, NX1 + 8, NY0 - 8, -12.0, H, H + 4.0, clg, 'nook_ceiling')    # the room's ceiling reaches Y -12 and X 195.375:
    wbox_abs(WID + 12, NX1 + 8, -12.0, NY1 + 8, H, H + 4.0, clg, 'nook_ceiling')     # no overlap (a shared face rendered a black bar)
    for X_ in (156.6, 208.0): ceiling_can(X_, -22.5, H, watts=14.0)                           # L1 x2 (RCP, 3/16" scale), now in the 9'-10" field
    # jib door 21 (32 in., head 8'-0"): a flush painted leaf; its 1/8 in. reveals cut the base, cap and panel moulding
    gap = material('GAP'); jx0, jx1 = NX0 + 59.75, NX0 + 91.75
    for z0_, z1_, dd in ((0.0, 9.5, 1.0), (9.5, 31.5, 0.04), (31.5, 35.0, 1.4), (35.0, 96.0, 0.04)):   # deep only through base and cap
        for x_ in (jx0, jx1 - 0.125): wbox(x_, x_ + 0.125, NY1 - dd, NY1 - 0.01, z0_, z1_, gap, 'jib_reveal')
    wbox(jx0, jx1, NY1 - 0.04, NY1 - 0.01, 96.0 - 0.125, 96.0, gap, 'jib_reveal')
    # bench at the foot of the bed (staging)
    bx_ = WID - 86.5 - 10.0; fabB = material('FAB-SOFA'); wdF = material('WOOD-FURN')
    wbox(bx_ - 16.0, bx_, by - 27.0, by + 27.0, 14.0, 18.0, fabB, 'bench_seat', soft=1.2)
    for lx_ in (bx_ - 15.0, bx_ - 2.0):
        for ly_ in (by - 26.0, by + 24.5): wbox(lx_, lx_ + 1.5, ly_, ly_ + 1.5, 0.0, 14.0, wdF, 'bench_leg')
    # the arched bookcase (ID-313 view 4): 1-1/2 in. sides and an arched head 12-3/4 in. deep, the cabinet and shelves inside
    yb0, yb1, sp, dB = NY0 + 3.975, NY0 + 45.975, 80.0, 12.75
    for y_ in (yb0, yb1 - 1.5): wbox(NX0, NX0 + dB, y_, y_ + 1.5, 0.0, sp, trim, 'bookcase_side', soft=0.1)
    yc, r_ = (yb0 + yb1) / 2, (yb1 - yb0) / 2 - 1.5
    arc_ = [(yc + r_ * _m.cos(_m.radians(a_)), sp + r_ * _m.sin(_m.radians(a_))) for a_ in range(0, 181, 6)]
    wprism_yz([(yb0, sp), (yb0, sp + r_ + 4.5), (yb1, sp + r_ + 4.5), (yb1, sp)] + arc_, NX0, NX0 + dB, trim, 'bookcase_arch')
    board_floor('mbr', 'WD-01')                                                  # ID-102: WD-01 herringbone, WD-02 6 in. border
    # outside (ID-102 floor 2): the terrace south of the nook's doors, its guard on the open west and south edges; the planter
    # bed outside the window, open to below beyond it
    terrace(122.0, 256.0, -178.0, NY0 - 10.0, -2.0, rails=((122.0, -178.0, 122.0, NY0 - 10.0), (122.0, -178.0, 256.0, -178.0)))
    planter(-6.0, 122.0, -55.0, -10.0)
    # HVAC (RCP-Lighting 261109 floor 2, FOR M-100/M-101 symbols): the supply slot near the TV wall and the one moved clear
    # of the headboard wall ("MOVE (FOR/MECH)"); sheet points converted at 1.125 pt/in. from the wall faces (VERIFY types)
    slot_diffuser(5.5, 8.0, 50.6, 110.6, H - 4.0, slots=1)    # in the underside of FOR's 14 in. cove soffit, not across its edge (COORD)
    slot_diffuser(145.0, 149.3, 50.7, 110.7, H, slots=2)
    # the reading nook (owner's reference, 11.11.26): two boucle lounge chairs facing the bookcase across a small rug, a
    # cognac drum table between them (staging; the furniture plan ID-152 to match)
    # owner 11.11.26 (second pass): one sofa, its back against the nook's east wall, facing the bookcase: the reference's olive
    # velvet, 6'-4" long, 3'-0" deep, 10" clear of the north wall (jib door 21's swing to VERIFY); the drum table in front
    MATS.setdefault('FAB-RUG-NOOK', {'hex': '#B8AD9C', 'rough': 0.95, 'kind': 'fabric', 'texture': 'acg/Carpet016'})
    MATS.setdefault('FAB-VELVET-OLIVE', {'hex': '#45432C', 'rough': 0.7, 'kind': 'fabric', 'texture': 'acg/Fabric062'})
    wbox(146.0, 224.0, -44.0, 34.0, 0.0, 0.4, material('FAB-RUG-NOOK'), 'nook_rug', soft=0.2)
    boucle_sofa(NX1, -42.0, 76.0, 36.0, '-x', modules=2, name='nook_sofa', fab=material('FAB-VELVET-OLIVE'))
    painting('meadow', NX1, -4.0, 65.0, 60.0, 38.0, '-x', frame='walnut', light=False, name='art_nook')   # owner 11.11.26: wide, over the sofa
    drum_table(176.0, -4.0, r=10.0, h=17.0)
    MATS.setdefault('FAB-PILLOW-CREAM', {'hex': '#E8E0D2', 'rough': 0.95, 'kind': 'fabric', 'texture': 'rough_linen'})
    # no throw pillows on the sofa (owner 11.11.26: remove them)
    # rug under the bed: the bed (ID-312) is centered on the bed wall, Y 102.8
    rug = material('FAB-RUG'); by = DEP - 58.625
    wbox(WID - 120.0, WID - 18.0, by - 54.0, by + 54.0, 0.0, 0.4, rug, 'rug', soft=0.15)


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
def wprism_yz(pts, x0, x1, mat, name='prism'):
    """A flat shape in a plane across X (Y, Z points in order) extruded along X from x0 to x1: raked rails, the knee wall."""
    n = len(pts); v = [(x0 * IN, y_ * IN, z_ * IN) for y_, z_ in pts] + [(x1 * IN, y_ * IN, z_ * IN) for y_, z_ in pts]
    f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 4]); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def wbox_abs(x0, x1, y0, y1, z0, z1, mat, name):
    """A box whose object coordinates are world coordinates, like the room floor: a board floor continues across the seam."""
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    me = bpy.data.meshes.new(name); me.from_pydata([(a_ * IN, b_ * IN, c_ * IN) for a_, b_, c_ in v], [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def arch_xz(ax_, aw_, asp, top, yw0, yw1, yc0, yc1, wallm, trim, cs=5.0):
    """The arched cased opening (arched_cased_opening): radius 0.62 x width, springing at asp. Spandrels fill the wall (yw0..yw1)
    from `top` down to the arc; the casing (yc0..yc1, on the room face) follows the arc and runs to the floor."""
    ar_ = aw_ * 0.62; acx = ax_ + aw_ / 2; acz = asp - _m.sqrt(ar_ ** 2 - (aw_ / 2) ** 2)
    def arc(rr, xa, xb, k=36):
        a0 = _m.atan2(_m.sqrt(max(rr ** 2 - (xa - acx) ** 2, 0)), xa - acx); a1 = _m.atan2(_m.sqrt(max(rr ** 2 - (xb - acx) ** 2, 0)), xb - acx)
        return [(acx + rr * _m.cos(a0 + (a1 - a0) * i / k), acz + rr * _m.sin(a0 + (a1 - a0) * i / k)) for i in range(k + 1)]
    inner_ = arc(ar_, ax_, ax_ + aw_)
    wprism_xz([(ax_, top), (ax_ + aw_, top)] + inner_[::-1], yw0, yw1, wallm, 'arch_spandrel')
    outer_ = arc(ar_ + cs, ax_ - cs, ax_ + aw_ + cs)
    wprism_xz([(ax_ - cs, 0.0)] + outer_ + [(ax_ + aw_ + cs, 0.0), (ax_ + aw_, 0.0)] + inner_[::-1] + [(ax_, 0.0)], yc0, yc1, trim, 'arch_casing')
    return acz + ar_


def door_in_x_wall(xf, side, y0, y1, head, trim, leafm, cs=3.5):
    """A closed two-panel door in a wall whose face is the plane X = xf, the room on the `side` (+1 east, -1 west): the leaf set
    1 in. back in the jamb, raised panels, a knob at the latch, 3-1/2 in. casing on the face. The wall's hole is the caller's."""
    lf0, lf1 = sorted((xf - side * 1.0, xf - side * 2.75))
    wbox(lf0, lf1, y0, y1, 0.0, head, leafm, 'door_leaf', soft=0.06)
    pf0, pf1 = sorted((xf - side * 1.0, xf - side * 0.8))
    for z0_, z1_ in ((8.0, head * 0.42), (head * 0.42 + 5.0, head - 5.0)):
        wbox(pf0, pf1, y0 + 5.0, y1 - 5.0, z0_, z1_, leafm, 'door_panel', soft=0.12)
    kx0, kx1 = sorted((xf - side * 0.8, xf + side * 1.4))
    wbox(kx0, kx1, y0 + 2.0, y0 + 4.2, 35.0, 37.2, material('STEEL-SS'), 'knob', soft=0.5)
    c0, c1 = sorted((xf, xf + side * 0.75))
    wbox(c0, c1, y0 - cs, y0, 0.0, head + cs, trim, 'door_casing', soft=0.1)
    wbox(c0, c1, y1, y1 + cs, 0.0, head + cs, trim, 'door_casing', soft=0.1)
    wbox(c0, c1, y0, y1, head, head + cs, trim, 'door_casing', soft=0.1)


def ceiling_can(X_, Y_, z_, watts=14.0):
    """A recessed can at a ceiling of height z_ (a stage ceiling, not the room's H): 3000 K spot, trim ring, the lens seen lit."""
    MATS.setdefault('TRIM-RING', {'hex': '#F4F3EF', 'rough': 0.3, 'kind': 'plastic'}); MATS.setdefault('LENS', {'kind': 'lamp', 'emit': 6.0})
    ld = bpy.data.lights.new('downlight', 'SPOT'); ld.energy = watts; ld.spot_size = _m.radians(80); ld.spot_blend = 0.6
    ld.shadow_soft_size = 1.25 * IN; ld.use_nodes = True
    bb = ld.node_tree.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = 3000
    ld.node_tree.links.new(bb.outputs['Color'], ld.node_tree.nodes['Emission'].inputs['Color'])
    o = bpy.data.objects.new('downlight', ld); bpy.context.collection.objects.link(o); o.location = (X_ * IN, Y_ * IN, (z_ - 0.5) * IN)
    o.visible_glossy = False
    wbox_abs(X_ - 2.25, X_ + 2.25, Y_ - 2.25, Y_ + 2.25, z_ - 0.05, z_, material('TRIM-RING'), 'trim_ring')
    wbox_abs(X_ - 1.8, X_ + 1.8, Y_ - 1.8, Y_ + 1.8, z_ - 0.08, z_ - 0.04, material('LENS'), 'downlight_lens')


def SE_open_stair(wallm, trim, wd, ys, CH, UOP, UKW):
    """The stair opened (owner 11.10.26, ID-235): the lower flight with an aluminum picket guard on its open side, the knee wall
    under the east flight with the flight's painted cut stringer and oak treads above it, the guard up the flight to the 10'-8"
    head, wall handrails, the landings. u = inches south of the gallery line (Y = -u). FOR A-411: 21 risers at 7-5/16", 11" treads."""
    RS, TR, ST = 7.3125, 11.0, 12.0
    LSE, LNE = 7 * RS, 17 * RS
    UTOP, UBOT = 45.1, 45.1 + 9 * TR
    XS, XE = 230.75, 280.0
    nose = lambda u: LSE + RS + (UBOT - u) * RS / TR
    under = lambda u: nose(u) - ST
    XL0, XL1 = 169.4, 235.4                                   # the lower flight's bottom and top risers
    nlf = lambda X: RS + (X - XL0) * (LSE - RS) / (XL1 - XL0)
    MATS.setdefault('ALU-BLK', {'hex': '#141414', 'rough': 0.42, 'kind': 'paint'})   # powder-coated matte black aluminum
    alu = bronze_mat(); oakr = rail_oak()   # dark bronze, white oak handrails (owner 11.11.26)
    # knee wall on the east flight's underside
    wprism_yz([(-UOP, 0.0), (-UOP, under(UOP)), (-UBOT, under(UBOT)), (-UBOT, LSE - ST), (-UKW, LSE - ST), (-UKW, 0.0)], 230.7, 236.7, wallm, 'knee_wall')
    # east flight: painted blocks (the cut stringer flush with the knee wall), oak treads returned past it; north of the opening
    # the treads stop inside the wall
    def tread(x0, x1, y0, y1, z):
        if y1 > -UOP and y0 < -UOP:
            wbox(x0, x1, y0, -UOP, z - 1.0, z, wd, 'tread'); wbox(236.7, x1, -UOP, y1, z - 1.0, z, wd, 'tread')
        elif y0 >= -UOP: wbox(236.7, x1, y0, y1, z - 1.0, z, wd, 'tread')
        else: wbox(x0, x1, y0, y1, z - 1.0, z, wd, 'tread')
    for i in range(1, 10):
        u_i = UBOT - TR * (i - 1); z_i = LSE + i * RS
        wbox(XS, XE, -u_i, -u_i + TR, 0.0, z_i - 1.0, trim, 'stair_step')
        tread(XS - 0.75, XE, -u_i - 1.0, -u_i + TR, z_i)
    wbox(XS, XE, -UTOP, -6.0, 0.0, LNE - 1.0, trim, 'landing_ne'); tread(236.7, XE, -UTOP - 1.0, -6.0, LNE)
    # the lower flight, its north stringer 2" wider for the guard posts, and the southeast landing
    for k in range(1, 7):
        x0_ = XL0 + (k - 1) * TR
        wbox(x0_, x0_ + TR, ys, -150.3, 0.0, k * RS - 1.0, trim, 'stair_step')
        wbox(x0_ - 0.75, x0_ + TR, ys, -149.55, k * RS - 1.0, k * RS, wd, 'tread')
    wbox(XL1, XE, ys, -UBOT, 0.0, LSE - 1.0, trim, 'landing_se'); wbox(XL1 - 0.75, XE, ys, -UBOT, LSE - 1.0, LSE, wd, 'tread')
    wbox(XS, XL1, -150.3, -UBOT, 0.0, LSE - 1.0, wallm, 'landing_se_w'); wbox(XS - 0.75, XL1, -150.3, -UBOT, LSE - 1.0, LSE, wd, 'tread')
    # ---- the guard: 2" posts, 1-1/2 x 2-1/2 top rail 36" over the nosings, 1-1/2 bottom rail 3-1/2" over, 3/4" pickets at 3-3/4" clear
    def pickets_between(a, b, zbot, ztop, place):
        lo, hi = a + 1.0, b - 1.0
        n = max(1, _m.ceil((hi - lo - 3.75) / 4.5 - 1e-6)); clr = (hi - lo - n * 0.75) / (n + 1); t = lo + clr
        for _ in range(n):
            c = t + 0.375; z0, z1 = zbot(c), min(ztop(c), CH)
            if z1 > z0: place(t, z0, z1)
            t += 0.75 + clr
    # lower flight, along Y -151.3
    GY = -151.3; px = [XL0 + 1.0, (XL0 + 1.0 + 231.75) / 2, 231.75]
    step_top = lambda X: (min(6, int((X - XL0) // TR) + 1)) * RS
    for X in px: wbox(X - 1.0, X + 1.0, GY - 1.0, GY + 1.0, step_top(X), nlf(X) + 36.75, alu, 'guard_post')
    for z_lo, h in ((1.0, 1.5), (33.5, 2.5)):
        wprism_xz([(px[0], nlf(px[0]) + z_lo), (px[-1], nlf(px[-1]) + z_lo), (px[-1], nlf(px[-1]) + z_lo + h), (px[0], nlf(px[0]) + z_lo + h)], GY - 0.75, GY + 0.75, alu, 'guard_rail')
    for a, b in zip(px, px[1:]):
        pickets_between(a, b, lambda X: nlf(X) + 2.5, lambda X: nlf(X) + 33.5,
                        lambda t, z0, z1: wbox(t, t + 0.75, GY - 0.375, GY + 0.375, z0, z1, alu, 'picket'))
    # round the landing's edge and up the east flight, along X 231.75; clipped at the 10'-8" head where the rail meets the header
    GX = 231.75
    gz = lambda u: LSE if u >= UBOT else nose(u)
    us = [-GY, UBOT - 1.0]
    n_ = max(1, _m.ceil((UBOT - 1.0 - (UOP + 1.0)) / 72.0)); us += [UBOT - 1.0 - j * (UBOT - UOP - 2.0) / n_ for j in range(1, n_ + 1)]
    for u in us[1:]:
        step_i = max(1, min(9, int((UBOT - u) // TR) + 1)); z0 = LSE + step_i * RS
        wbox(GX - 1.0, GX + 1.0, -u - 1.0, -u + 1.0, z0, min(gz(u) + 36.75, CH), alu, 'guard_post')
    for z_lo, h in ((1.0, 1.5), (33.5, 2.5)):
        wbox(GX - 0.75, GX + 0.75, -us[0], -us[1], LSE + z_lo, LSE + z_lo + h, alu, 'guard_rail')        # level over the landing edge
        ua, ub = us[1], us[-1]
        zt = lambda u: nose(u) + z_lo + h
        if zt(ub) > CH: ub = UBOT - (CH - z_lo - h - LSE - RS) * TR / RS          # where the rail meets the head
        wprism_yz([(-ua, nose(ua) + z_lo), (-ub, nose(ub) + z_lo), (-ub, nose(ub) + z_lo + h), (-ua, nose(ua) + z_lo + h)], GX - 0.75, GX + 0.75, alu, 'guard_rail')
    for a, b in zip(sorted(us), sorted(us)[1:]):
        pickets_between(a, b, lambda u: gz(u) + 2.5, lambda u: gz(u) + 33.5 if gz(u) + 36.0 <= CH else CH - 1.5,
                        lambda t, z0, z1: wbox(GX - 0.375, GX + 0.375, -t - 0.75, -t, z0, z1, alu, 'picket'))
    uc_ = UBOT - (CH - 36.0 - LSE - RS) * TR / RS                # where the top rail meets the head: a channel takes the pickets from there
    wbox(GX - 0.75, GX + 0.75, -uc_, -(UOP), CH - 1.5, CH - 0.01, alu, 'guard_channel')
    # wall handrails, 1-1/2", 3'-0" over the nosings (FOR A-411), black to match
    wprism_yz([(-UBOT, nose(UBOT) + 34.5), (-UTOP, nose(UTOP) + 34.5), (-UTOP, nose(UTOP) + 36.0), (-UBOT, nose(UBOT) + 36.0)], 277.0, 278.5, oakr, 'handrail')
    wbox(277.0, 278.5, ys + 2.0, -UBOT, LSE + 34.5, LSE + 36.0, oakr, 'handrail', soft=0.5)
    wbox(XL1, 277.0, ys + 2.0, ys + 3.5, LSE + 34.5, LSE + 36.0, oakr, 'handrail', soft=0.5)
    wprism_xz([(XL0, nlf(XL0) + 34.5), (XL1, nlf(XL1) + 34.5), (XL1, nlf(XL1) + 36.0), (XL0, nlf(XL0) + 36.0)], ys + 2.0, ys + 3.5, oakr, 'handrail')
    # the stairwell: its east wall, the floor 2 wall over the opening's head, the cap at the floor 2 ceiling
    wbox(XE, XE + 6.0, ys - 6.0, -6.0, 0.0, 272.0, wallm, 'stairwell_e')
    wbox(230.7, 236.7, -158.0, -UTOP, CH + 24.0, 268.0, wallm, 'stairwell_w')
    wbox(236.7, XE + 6.0, ys - 6.0, ys, CH + 4.0, 272.0, wallm, 'stairwell_s')   # on top of the south wall (now to 11'-0")
    wbox(230.7, XE + 6.0, ys - 6.0, -60.0, 268.0, 272.0, material('PT-CEIL') if 'PT-CEIL' in MATS else wallm, 'stairwell_cap')   # the floor 2 hall ceiling covers north of -60


def grand_piano(xb, yk):
    """Staging, owner 11.10.26 ("one rendering with a grand piano", then "rotate the piano about 90 degrees counterclockwise so it
    takes up minimal space but still looks comfortable"): a 6'-2" grand in black polish, its straight (bass) side along the knee
    wall a foot off it, keyboard at the north end (the pianist faces south, toward the arch), tail to the south, the lid open
    toward the room. xb: the bass side (world X); yk: the keyboard's front edge (world Y). Local x across (0 bass, east .. 58
    treble, west), y along (0 keyboard .. 74 tail, south)."""
    MATS.setdefault('PIANO-BLK', {'hex': '#070707', 'rough': 0.06, 'kind': 'paint'})
    MATS.setdefault('PIANO-KEY', {'hex': '#F2EFE6', 'rough': 0.25, 'kind': 'paint'})
    MATS.setdefault('PIANO-RIM-IN', {'hex': '#5A3A22', 'rough': 0.35, 'kind': 'paint'})
    MATS.setdefault('BRASS', {'hex': '#B08D57', 'rough': 0.25, 'kind': 'metal'})
    blk, key, brass = material('PIANO-BLK'), material('PIANO-KEY'), material('BRASS')
    W_ = lambda lx, ly: (xb - lx, yk - ly)                        # local to world X, Y
    outline = [(0, 0), (58, 0), (58, 12), (57.5, 20), (55, 27), (50, 34), (44, 41), (38.5, 48), (34, 55), (30.5, 62), (26.5, 68),
               (20, 72.5), (12, 74), (0, 74)]
    def solid(poly, z0, z1, mat, name):
        pts = [W_(*p) for p in poly]
        bm = bmesh.new()
        bot = [bm.verts.new((x * IN, y * IN, z0 * IN)) for x, y in pts]; top = [bm.verts.new((x * IN, y * IN, z1 * IN)) for x, y in pts]
        bm.faces.new(bot[::-1]); bm.faces.new(top)
        for i in range(len(pts)): bm.faces.new((bot[i], bot[(i + 1) % len(pts)], top[(i + 1) % len(pts)], top[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat)
        bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = 0.25 * IN; bv.segments = 2; bv.limit_method = 'ANGLE'
        return o
    # case: the rim 11" deep from 23" up; the plate and strings inside read dark under the open lid (an inner floor 3" down)
    solid(outline, 23.0, 34.0, blk, 'piano_rim')
    inner = [(1.5 + (x - 29) * 0.94 + 27.5, y * 0.96 + 1.5) for x, y in outline]
    solid(inner, 30.9, 31.0, material('BRASS'), 'piano_plate')
    # keyboard: 88 keys, 48" across, on a keybed projecting 6" in front of the case, cheek blocks each side
    solid([(3.0, -6.0), (55.0, -6.0), (55.0, 2.0), (3.0, 2.0)], 24.0, 27.0, blk, 'piano_keybed')
    for lx0, lx1 in ((0.0, 5.0), (53.0, 58.0)): solid([(lx0, -6.5), (lx1, -6.5), (lx1, 2.0), (lx0, 2.0)], 24.0, 30.0, blk, 'piano_cheek')
    kx0, kw = 5.0, 48.0 / 52
    for k in range(52): solid([(kx0 + k * kw + 0.04, -6.0), (kx0 + (k + 1) * kw - 0.04, -6.0), (kx0 + (k + 1) * kw - 0.04, 0.0), (kx0 + k * kw + 0.04, 0.0)], 27.0, 27.9, key, 'piano_key')
    for k in range(51):
        if k % 7 in (2, 6): continue
        c = kx0 + (k + 1) * kw; solid([(c - 0.26, -2.3), (c + 0.26, -2.3), (c + 0.26, 0.0), (c - 0.26, 0.0)], 27.9, 28.4, blk, 'piano_key_b')
    solid([(5.0, 0.0), (53.0, 0.0), (53.0, 3.0), (5.0, 3.0)], 27.0, 31.0, blk, 'piano_fallboard')
    # music desk, tilted back, and the lid open on its prop (hinged on the bass side, lifted on the treble side, 38 degrees)
    solid([(14.0, 5.0), (44.0, 5.0), (44.0, 6.0), (14.0, 6.0)], 34.0, 46.0, blk, 'piano_desk')
    lid = solid(outline, 0.0, 0.75, blk, 'piano_lid')
    import mathutils
    hx, hy = W_(0, 0)                                              # the hinge line runs along the bass side (world Y), at the rim top
    ang = _m.radians(38.0)
    lid.data.transform(mathutils.Matrix.Translation((-hx * IN, -hy * IN, 0)))
    lid.data.transform(mathutils.Matrix.Rotation(ang, 4, 'Y'))  # local x is world -X: lift the treble (west) edge
    lid.location = (hx * IN, hy * IN, 34.0 * IN)
    # the prop stick from the rim's treble side up to the lid
    lx_ = 44.0; px_ = hx - lx_ * _m.cos(ang); py_ = W_(lx_, 34.0)[1]      # the lid swings in toward the hinge as it lifts: aim the stick at it
    wbox(px_ - 0.5, px_ + 0.5, py_ - 0.5, py_ + 0.5, 34.0, 34.0 + lx_ * _m.sin(ang) - 0.2, blk, 'piano_prop')
    # three legs with brass casters, the pedal lyre, a bench
    for lx, ly in ((4.0, 3.0), (54.0, 3.0), (16.0, 66.0)):
        X, Y = W_(lx, ly); wbox(X - 2.0, X + 2.0, Y - 2.0, Y + 2.0, 2.5, 23.0, blk, 'piano_leg', soft=0.4)
        wbox(X - 1.0, X + 1.0, Y - 1.0, Y + 1.0, 0.0, 2.5, brass, 'piano_caster', soft=0.4)
    X, Y = W_(29.0, 9.0)
    wbox(X - 6.0, X + 6.0, Y - 1.0, Y + 1.0, 4.0, 23.0, blk, 'piano_lyre', soft=0.3)
    wbox(X - 6.5, X + 6.5, Y - 2.0, Y + 2.0, 1.0, 4.0, blk, 'piano_lyre_box', soft=0.3)
    for dx in (-3.0, 0.0, 3.0): wbox(X + dx - 0.6, X + dx + 0.6, Y + 2.0, Y + 6.0, 2.2, 2.8, brass, 'piano_pedal', soft=0.2)
    BX, BY = W_(32.0, -22.0)                                       # the bench a little toward the treble, clear of door 27's swing
    wbox(BX - 15.0, BX + 15.0, BY - 7.0, BY + 7.0, 17.0, 19.5, blk, 'bench_top', soft=0.5)
    wbox(BX - 14.5, BX + 14.5, BY - 6.5, BY + 6.5, 19.5, 20.75, material('FAB-SOFA'), 'bench_cushion', soft=0.6)
    for sx in (-13.5, 13.5):
        for sy in (-5.5, 5.5): wbox(BX + sx - 0.75, BX + sx + 0.75, BY + sy - 0.75, BY + sy + 0.75, 0.0, 17.0, blk, 'bench_leg')


def south_end(wallm, trim, pt1):
    """The south end under floor 2 (build_great_rev1b south_wall: OPEN TO THE SOUTH END UNDER THE GALLERY BEAM, HEAD 10'-8"),
    modelled so the living room sees into it (owner 11.10.26: through a door opening you must see the other room). World X east,
    Y north from the gallery line; the plan's numbers converted with X = (x_pt - 626.2) / 1.5, Y = (844.5 - y_pt) / 1.5:
    west wall face 92.2 with back hall door 12; closet 27's wall face 230.7 (door at Y -88..-59); south wall face -196.7 with the
    entry's arched cased opening (X 103.0..155.3, apex 8'-4-3/4", the kitchen arch's language); the lower stair flight along the
    south wall behind a raking half wall (7 risers at 7-5/16 in. to the SE landing). Ceiling 10'-8" (the gallery soffit)."""
    CH = 128.0; ys = -196.7; wd = material(R('floor', 'WD-01')); leafm = material('PT-01-SATIN')
    MATS.setdefault('STEEL-SS', {'hex': '#B8B5AE', 'rough': 0.3, 'kind': 'metal'})
    # floor: the living room's boards continue (world coordinates, same material: no seam); the foyer's checkerboard past the arch
    wbox_abs(86.2, 280.0, ys - 6.0, -12.0, -2.0, 0.0, wd, 'south_floor')
    FW, FE, FS = 37.2, 247.0, -301.7       # the foyer: its tray (X 55.1..235.9) and the front wall the sconces sit on (plan RCP)
    wbox_abs(FW, FE, FS, ys - 6.0, -2.0, 0.0, material('TL-01'), 'foyer_floor')   # not R(): the room's floor role would give the living room's oak
    # west wall with door 12
    for y0_, y1_, z0_ in ((ys - 6.0, -122.0, 0.0), (-89.0, -6.0, 0.0), (-122.0, -89.0, 96.0)):
        wbox(86.2, 92.2, y0_, y1_, z0_, CH + 4.0, wallm, 'se_wall_w')
    door_in_x_wall(92.2, 1, -122.0, -89.0, 96.0, trim, leafm)
    # closet 27's wall, opened (owner 11.10.26, ID-235): full height north of the opening with door 27 against FOR's concrete beam
    # (13-5/8" south of the gallery line), then a knee wall on the east flight's underside, open above it to the 10'-8" head
    UD0, UD1, UOP, UKW = 13.75, 41.75, 48.75, 147.3
    for y0_, y1_, z0_ in ((-UOP, -UD1, 0.0), (-UD0, -6.0, 0.0), (-UD1, -UD0, 80.0)):
        wbox(230.7, 236.7, y0_, y1_, z0_, CH, wallm, 'se_wall_closet')
    door_in_x_wall(230.7, -1, -UD1, -UD0, 80.0, trim, leafm, cs=3.5)
    SE_open_stair(wallm, trim, wd, ys, CH, UOP, UKW)
    # south wall with the entry arch; the foyer beyond it
    AX, AW, AP = 103.0, 52.3, 100.75
    asp = AP - AW * 0.62 + _m.sqrt((AW * 0.62) ** 2 - (AW / 2) ** 2)
    for x0_, x1_, z0_ in ((86.2, AX, 0.0), (AX + AW, 286.0, 0.0), (AX, AX + AW, AP + 1.0)):
        wbox(x0_, x1_, ys - 6.0, ys, z0_, CH + 4.0, wallm, 'se_wall_s')
    arch_xz(AX, AW, asp, AP + 1.0, ys - 6.0, ys, ys, ys + 0.75, wallm, trim)
    wbox(FW - 6.0, FW, FS, ys - 6.0, 0.0, CH, wallm, 'foyer_wall_w'); wbox(FE, FE + 6.0, FS, ys - 6.0, 0.0, CH, wallm, 'foyer_wall_e')
    wbox(FW, 86.2, ys - 6.0, ys, 0.0, CH, wallm, 'foyer_wall_n'); wbox(262.0, FE, ys - 6.0, ys, 0.0, CH, wallm, 'foyer_wall_n')
    # the front wall: the entry pair centred between the plan's sconces (X 64.5 and 154.5), 6'-0" x 8'-0", oak, with its casing
    DX0, DX1, DH = 109.5 - 36.0, 109.5 + 36.0, 96.0
    for x0_, x1_, z0_ in ((FW - 6.0, DX0, 0.0), (DX1, FE + 6.0, 0.0), (DX0, DX1, DH)):
        wbox(x0_, x1_, FS - 6.0, FS, z0_, CH, wallm, 'foyer_wall_s')
    oak = material('WD-SHELF')   # honey oak to the floor (WD-02, the border stain, read espresso)
    for a_, b_ in ((DX0, 109.4), (109.6, DX1)):
        wbox(a_, b_, FS - 2.75, FS - 1.0, 0.0, DH, oak, 'entry_leaf', soft=0.06)
        for z0_, z1_ in ((10.0, 38.0), (44.0, DH - 6.0)):
            wbox(a_ + 5.0, b_ - 5.0, FS - 1.0, FS - 0.8, z0_, z1_, oak, 'entry_panel', soft=0.12)
        wbox(b_ - 3.0 if a_ < 109.5 else a_ + 1.0, b_ - 2.0 if a_ < 109.5 else a_ + 2.0, FS - 0.8, FS + 0.6, 34.0, 46.0, material('STEEL-SS'), 'entry_pull', soft=0.3)
    wbox(109.25, 109.75, FS - 0.9, FS - 0.6, 0.0, DH, material('STEEL-SS'), 'entry_astragal')   # the meeting stile's astragal: no daylight seam
    wbox(DX0, DX1, FS - 6.0, FS + 0.5, -2.0, 0.375, material('ST-01'), 'entry_threshold')        # marble saddle across the jamb depth
    wbox(DX0 - 0.5, DX1 + 0.5, FS - 6.6, FS - 6.0, -2.0, DH + 0.5, oak, 'entry_outer')            # the pair's exterior face closes the hole
    wbox(DX0 - 4.5, DX0, FS, FS + 0.75, 0.0, DH + 4.5, trim, 'entry_casing', soft=0.1); wbox(DX1, DX1 + 4.5, FS, FS + 0.75, 0.0, DH + 4.5, trim, 'entry_casing', soft=0.1)
    wbox(DX0, DX1, FS, FS + 0.75, DH, DH + 4.5, trim, 'entry_casing', soft=0.1)
    # the tray (plan RCP: 180 x 81 in. at X 145.5, Y -244.5), 6 in. up, the flat ceiling round it
    TX0, TX1, TY0, TY1 = 55.1, 235.9, -285.25, -203.75
    for x0_, x1_, y0_, y1_ in ((FW, FE, FS, TY0), (FW, FE, TY1, ys - 6.0), (FW, TX0, TY0, TY1), (TX1, FE, TY0, TY1)):
        wbox(x0_, x1_, y0_, y1_, CH, CH + 6.0, pt1, 'foyer_ceiling')
    wbox(FW, FE, FS, ys - 6.0, CH + 6.0, CH + 10.0, pt1, 'foyer_tray')
    B_f = lambda x0_, x1_, y0__, y1__: wbox(x0_, x1_, y0__, y1__, 0.0, 8.5, trim, 'foyer_base', soft=0.15)
    B_f(FW, DX0 - 4.5, FS, FS + 0.6); B_f(DX1 + 4.5, FE, FS, FS + 0.6)
    B_f(FW, FW + 0.6, FS + 0.6, ys - 6.0); B_f(FE - 0.6, FE, FS + 0.6, ys - 6.0)
    B_f(FW + 0.6, AX - 5.0, ys - 6.6, ys - 6.0); B_f(AX + AW + 5.0, FE - 0.6, ys - 6.6, ys - 6.0)
    # base: stopped at every casing, none on the stair side
    B_ = lambda x0_, x1_, y0_, y1_: wbox(x0_, x1_, y0_, y1_, 0.0, 8.5, trim, 'se_base', soft=0.15)
    B_(92.2, 92.8, ys, -125.5); B_(92.2, 92.8, -85.5, 0.6)   # round the jamb return to the living room's base
    B_(230.1, 230.7, -150.3, -UD1 - 3.5); B_(230.1, 230.7, -UD0 + 3.5, 0.6)   # the knee wall runs on to the lower flight
    B_(92.8, AX - 5.0, ys, ys + 0.6); B_(AX + AW + 5.0, 169.4, ys, ys + 0.6)
    # lights, from the plan's RCP (build_rcp.for_items, converted as above): in the south end a centre fixture at (161.3, -74.8),
    # wall washers along the west wall at X 113 and two cans by the stair and arch at Y -172; a sconce on the closet wall at
    # Y -119.5; in the foyer a pendant in the tray at (109.7, -244.5) and sconces each side of the entry at X 64.5 and 154.5
    MATS.setdefault('TRIM-RING', {'hex': '#F4F3EF', 'rough': 0.3, 'kind': 'plastic'}); MATS.setdefault('LENS', {'kind': 'lamp', 'emit': 6.0})
    MATS.setdefault('SHADE', {'kind': 'lamp', 'emit': 3.0})
    can = ceiling_can
    for X_, Y_ in ((113.1, -29.0), (113.1, -60.0), (113.1, -151.0), (113.1, -177.0), (129.6, -172.1), (199.1, -172.1)):
        can(X_, Y_, CH if Y_ > -148.0 else 132.0)
    for X_, Y_ in ((241.8, -236.5), (48.7, -219.0), (48.7, -261.6)):
        can(X_, Y_, CH, 10.0)
    def drum(X_, Y_, zb, d, h, watts, rod_top):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=d / 2 * IN, depth=h * IN, location=(X_ * IN, Y_ * IN, (zb + h / 2) * IN))
        o = bpy.context.active_object; o.name = 'drum_shade'; o.data.materials.append(material('SHADE'))
        for pg in o.data.polygons: pg.use_smooth = True
        if rod_top > zb + h: wbox(X_ - 0.25, X_ + 0.25, Y_ - 0.25, Y_ + 0.25, zb + h, rod_top, material('STEEL-SS'), 'pendant_rod')
        wpoint(X_, Y_, zb + h / 2, watts, radius=d / 3, color=(1.0, 0.86, 0.68))
    rod_flush(161.3, -74.8, CH)                                         # owner 11.11.26: glass-rod flush mount at the piano end, aged brass
    drum(109.7, -244.5, 92.0, 18.0, 12.0, 60.0, CH + 6.0)             # the foyer pendant, in its tray
    def sconce_y(X_, yf, side, z_=66.0, watts=12.0):   # on a wall whose face is Y = yf, the room on `side`
        y0_, y1_ = sorted((yf, yf + side * 1.0)); wbox(X_ - 2.5, X_ + 2.5, y0_, y1_, z_ - 6.0, z_ + 6.0, material('STEEL-SS'), 'sconce_plate', soft=0.3)
        y0_, y1_ = sorted((yf + side * 1.0, yf + side * 5.5)); wbox(X_ - 2.25, X_ + 2.25, y0_, y1_, z_ - 3.0, z_ + 7.0, material('SHADE'), 'sconce_shade', soft=1.0)
        wpoint(X_, yf + side * 3.5, z_ + 2.0, watts, radius=1.5, color=(1.0, 0.86, 0.68))
    sconce_y(64.5, FS, 1); sconce_y(154.5, FS, 1)
    def sconce_x(xf, side, Y_, z_, watts):   # a round plate and an opal cylinder on a wall whose face is X = xf, the room on `side`
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.75 * IN, depth=0.75 * IN, location=((xf + side * 0.375) * IN, Y_ * IN, z_ * IN), rotation=(0, _m.pi / 2, 0))
        o_ = bpy.context.active_object; o_.name = 'sconce_plate'; o_.data.materials.append(material('STEEL-SS'))
        x0_, x1_ = sorted((xf + side * 0.75, xf + side * 3.0)); wbox(x0_, x1_, Y_ - 0.4, Y_ + 0.4, z_ - 0.4, z_ + 0.4, material('STEEL-SS'), 'sconce_arm')
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.5 * IN, depth=10.0 * IN, location=((xf + side * 5.25) * IN, Y_ * IN, (z_ + 1.0) * IN))
        o_ = bpy.context.active_object; o_.name = 'sconce_shade'; o_.data.materials.append(material('SHADE'))
        for pg in o_.data.polygons: pg.use_smooth = True
        wpoint(xf + side * 5.25, Y_, z_ + 1.0, watts, radius=1.5)
    LSE_ = 7 * 7.3125
    # FOR's closet-wall sconce moves to the stairwell's east wall, 6'-6" over the nosings; FOR's C-1 at the southeast landing
    sconce_x(280.0, -1, -95.0, 169.0, 70.0); sconce_y(257.7, ys, 1, LSE_ + 66.0, 20.0)   # the stairwell read black behind the pickets at 25 W (review 11.10.26)
    if os.environ.get('PR_PIANO'): grand_piano(218.0, -64.0)

def cove_w(axis, c, a0, a1, side, top, P=14.0, F=None, crown=True, name='cove'):
    """The LED cove soffit in world inches per FOR's detail (A-401 section 2, owner 11.11.26): a 5/8 in. gypsum soffit P deep
    off a face line c (X = c for axis 'y', Y = c for axis 'x'), the room on `side` (+1 toward +X or +Y), its underside at `top`
    = 4 in. under the ceiling, the room edge open: the slot between the board and the ceiling is the cove, the LED on the
    hanger 3 in. back from the edge throwing out across the ceiling, which runs on over the soffit. Crown in the corner under
    it (walls only). F is ignored (kept so old calls still run)."""
    MATS.setdefault('LED-STRIP', {'kind': 'lamp', 'emit': 2.2})
    clg = material(R('ceiling', 'PT-01')); trm = material('PT-01-SATIN')
    lo_, hi_ = min(a0, a1), max(a0, a1); B_, S_ = 0.625, 3.0; ceil_ = top + 4.0
    def bx(p0, p1, z0, z1, mat, nm):
        q0, q1 = sorted((c + side * p0, c + side * p1))
        return wbox(q0, q1, lo_, hi_, z0, z1, mat, nm) if axis == 'y' else wbox(lo_, hi_, q0, q1, z0, z1, mat, nm)
    bx(0.0, P, top, top + B_, clg, name + '_soffit')
    bx(P - S_ - 1.5, P - S_, top + B_, ceil_ - 0.02, clg, name + '_hanger')
    bx(P - S_, P - S_ + 0.3, top + B_ + 1.0, top + B_ + 1.6, material('LED-STRIP'), name + '_led')
    Lr = hi_ - lo_
    if Lr > 4:
        ld = bpy.data.lights.new('cove_led', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = (Lr - 2) * IN; ld.size_y = 1.0 * IN
        ld.energy = 3.0 * Lr / 12.0; ld.color = (1.0, 0.83, 0.62)
        o_ = bpy.data.objects.new('cove_led', ld); bpy.context.collection.objects.link(o_); o_.visible_glossy = False
        mid = (lo_ + hi_) / 2; q = c + side * (P - S_ + 0.6)
        o_.location = ((q, mid, top + B_ + 1.3) if axis == 'y' else (mid, q, top + B_ + 1.3)); o_.location = tuple(v * IN for v in o_.location)
        # area lights shine down their -Z; tip it out of the slot toward the room (side) and 25 deg up
        tilt = _m.radians(115)
        o_.rotation_euler = ((0, -side * tilt, 0) if axis == 'y' else (side * tilt, 0, 0))
    if crown and os.environ.get('PR_COVECROWN', '1') != '0':
        zc = top - 0.02; pr = [(0.0, zc), (0.0, zc - 3.75), (0.5, zc - 3.75), (0.6, zc - 3.25)]
        for i in range(1, 13):
            t = i / 12.0; pr.append((0.6 + 2.65 * (0.5 - 0.5 * _m.cos(_m.pi * t)), zc - 3.25 + 2.75 * t))
        pr += [(3.25, zc - 0.5), (3.25, zc)]
        if axis == 'y': o_ = wprism_xz([(c + side * d_, z_) for d_, z_ in pr], lo_, hi_, trm, name + '_crown')
        else: o_ = wprism_yz([(c + side * d_, z_) for d_, z_ in pr], lo_, hi_, trm, name + '_crown')
        for pg in o_.data.polygons: pg.use_smooth = True


def band_panels(axis, c, a0, a1, side, z0, z1, mold=1.5, inset=3.0, target=40.0, name='band_panel'):
    """Applied panel moulding on a band (owner 11.11.26: something decorative across the fascia): panels about `target` long
    with 4 in. between and at the ends, `inset` from the band's top and bottom; a 1-1/2 in. moulding 5/8 in. proud."""
    trm = material(R('trim', 'PT-01-SATIN')); lo_, hi_ = min(a0, a1), max(a0, a1); Lr = hi_ - lo_   # tonal with the wall
    if Lr < 14: return
    n = max(1, int(round((Lr - 4) / (target + 4)))); pw = (Lr - 4 * (n + 1)) / n
    for k in range(n):
        p0 = lo_ + 4 + k * (pw + 4); p1 = p0 + pw
        # rails full length, stiles between them: overlapping corner boxes shared faces and rendered black corners (owner 11.11.26)
        for (u0, u1, v0, v1) in ((p0, p1, z0 + inset, z0 + inset + mold), (p0, p1, z1 - inset - mold, z1 - inset),
                                 (p0, p0 + mold, z0 + inset + mold, z1 - inset - mold), (p1 - mold, p1, z0 + inset + mold, z1 - inset - mold)):
            q0, q1 = sorted((c, c + side * 0.625))
            if axis == 'y': wbox(q0, q1, u0, u1, v0, v1, trm, name, soft=0.2)
            else: wbox(u0, u1, q0, q1, v0, v1, trm, name, soft=0.2)


def boucle_material(key='FAB-BOUCLE', c0='#4A3B2F', c1='#66523F'):
    """Boucle (Megan's reference sofa, 11.11.26): a warm taupe-brown loop yarn: base colour with a fine loop-scale tone
    variation, a strong small-scale bump from a Voronoi of 1/8 in. cells, full roughness and a soft sheen."""
    m = bpy.data.materials.get(key)
    if m: return m
    m = bpy.data.materials.new(key); m.use_nodes = True; N_ = m.node_tree.nodes; L_ = m.node_tree.links; b = N_['Principled BSDF']
    tc = N_.new('ShaderNodeTexCoord'); vo = N_.new('ShaderNodeTexVoronoi'); vo.feature = 'SMOOTH_F1'; vo.inputs['Scale'].default_value = 1.0 / (0.16 * IN)
    L_.new(tc.outputs['Object'], vo.inputs['Vector'])
    nz = N_.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0 / (0.6 * IN); L_.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N_.new('ShaderNodeValToRGB'); L_.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = (*hex_lin(c0), 1); ramp.color_ramp.elements[1].color = (*hex_lin(c1), 1)
    L_.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.95
    try:   # a little warm sheen at grazing angles; a white sheen washed the brown out to grey (test 11.11.26)
        b.inputs['Sheen Weight'].default_value = 0.2; b.inputs['Sheen Roughness'].default_value = 0.7
        b.inputs['Sheen Tint'].default_value = (*hex_lin('#9C8670'), 1)
    except Exception: pass
    b.inputs['Specular IOR Level'].default_value = 0.2
    bp = N_.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.85; bp.inputs['Distance'].default_value = 0.08 * IN
    L_.new(vo.outputs['Distance'], bp.inputs['Height']); L_.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def boucle_sofa(ox, oy, length, depth, facing, modules=3, name='sofa', fab=None):
    """A low modular boucle sofa like the owner's reference: rounded drum arms, block seat cushions with deep rounded edges,
    a continuous rounded back bolster, a recessed plinth. (ox, oy) is the back-left corner seen from the front; facing
    '+x' or '+y' (the direction the seat looks), length along the back, depth back to front. Inches, world."""
    fab = fab or boucle_material(); MATS.setdefault('SOFA-PLINTH', {'hex': '#2A231D', 'rough': 0.6, 'kind': 'paint'}); pl = material('SOFA-PLINTH')
    def W(u0, u1, v0, v1):        # local (u along the back from its left end, v from the back toward the front) to world
        if facing == '+x': return (ox + v0, ox + v1, oy - u1, oy - u0)
        if facing == '+y': return (ox + u0, ox + u1, oy + v0, oy + v1)
        if facing == '-y': return (ox - u1, ox - u0, oy - v1, oy - v0)
        return (ox - v1, ox - v0, oy + u0, oy + u1)
    def B(u0, u1, v0, v1, z0, z1, mat, nm, soft=0.0):
        x0, x1, y0, y1 = W(u0, u1, v0, v1); return wbox(x0, x1, y0, y1, z0, z1, mat, nm, soft=soft)
    AW = 11.0; L_, D_ = length, depth
    B(3, L_ - 3, 3, D_ - 3, 0.0, 2.5, pl, name + '_plinth')
    B(AW - 1, L_ - AW + 1, 0.5, D_ - 0.5, 2.5, 15.0, fab, name + '_base', soft=3.0)
    for k in (0, 1):                                                     # drum arms, rounded hard
        u0 = 0.0 if k == 0 else L_ - AW
        B(u0, u0 + AW, 0.0, D_, 2.5, 25.0, fab, name + '_arm', soft=5.0)
    B(AW - 1.5, L_ - AW + 1.5, 0.0, 11.0, 15.0, 31.0, fab, name + '_back', soft=5.0)
    mw = (L_ - 2 * AW) / modules
    for k in range(modules):                                             # seat blocks: deep, soft, a real gap between them
        u0 = AW + k * mw + 0.25; u1 = AW + (k + 1) * mw - 0.25
        B(u0, u1, 10.5, D_ - 0.25, 15.0, 22.5, fab, name + '_seat', soft=3.2)
        B(u0 + 0.5, u1 - 0.5, 10.0, 17.0, 21.0, 32.5, fab, name + '_back_cushion', soft=3.5)


def mosaic(x0, x1, y0, y1, z=0.0, tile=2.0, joint=0.0625, code='TL-03', name='mosaic'):
    """Small square floor tile (the shower's TL-03 2 x 2 in. porcelain mosaic, ID-320 note 10), one mesh, joints over a dark bed."""
    pm = material(code); bm = bmesh.new()
    nx_ = int((x1 - x0) / tile) + 1; ny_ = int((y1 - y0) / tile) + 1
    for i in range(nx_):
        for j in range(ny_):
            a0, a1 = x0 + i * tile + joint / 2, min(x1, x0 + (i + 1) * tile) - joint / 2
            b0, b1 = y0 + j * tile + joint / 2, min(y1, y0 + (j + 1) * tile) - joint / 2
            if a1 - a0 < 0.2 or b1 - b0 < 0.2: continue
            v = [bm.verts.new((xx * IN, yy * IN, zz * IN)) for zz in (z - 0.3, z) for xx, yy in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
            for f_ in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[k] for k in f_])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(pm)
    MATS.setdefault('GROUT-DK', {'hex': '#8E8A83', 'rough': 0.9, 'kind': 'paint'})
    wbox_abs(x0, x1, y0, y1, z - 0.6, z - 0.05, material('GROUT-DK'), name + '_bed')


def bath_compartments():
    """The master bath's shower, tub alcove and W.C. behind the alcove line (build_bath_shell.py): their walls from their own
    elevations (ID-322, ID-323) at their places, their 9'-10" ceilings, floors (herringbone into the alcove and the W.C., TL-03
    in the shower), the hammered glass shower door, the wall-hung toilet, the terraces outside (owner 11.11.26: floor 2, a
    terrace outside the windows)."""
    global V, roles
    V0, R0 = V, roles
    at = lambda name: next(i for i, v_ in enumerate(ALL) if v_['view'] == name)
    place = lambda X, Y, rot: Matrix.Translation((X * IN, Y * IN, 0)) @ Matrix.Rotation(_m.radians(rot), 4, 'Z')
    YB, YF = -63.0, -6.0                       # the compartments' back and front faces (57 deep behind a 6 in. line)
    for nm, X, Y, rot in (('SHOWER - WEST WALL', 0.0, YB + 0.1, 90), ('SHOWER - SOUTH WALL', 43.625, YB, 180),
                          ('SHOWER - EAST WALL', 43.625, YF - 0.1, -90), ('SHOWER - NORTH WALL', 0.0, YF, 0),
                          ('TUB ALCOVE - WEST WALL', 48.625, YB + 0.1, 90), ('TUB ALCOVE - SOUTH WALL', 113.375, YB, 180),
                          ('TUB ALCOVE - EAST WALL', 113.375, YF - 0.1, -90), ('WATER CLOSET - NORTH WALL', 118.375, YF, 0),
                          ('WATER CLOSET - EAST WALL', 162.0, YF - 0.1, -90), ('WATER CLOSET - SOUTH WALL', 162.0, YB, 180),
                          ('WATER CLOSET - WEST WALL', 118.375, YB + 0.1, 90)):
        build_wall(at(nm), place(X, Y, rot), 60.0)
    V, roles = V0, R0
    clg = material(R('ceiling', 'PT-01')); wd = material(R('floor', 'WD-01'))
    # the alcove's stone wraps its two jamb returns to the room face (a painted return read as a dark stripe, 11.11.26)
    stn = material(R('tile', 'CAL-MONET-HONED'))
    wbox_abs(48.625, 49.0, -6.15, -0.01, 0.0, H, stn, 'alcove_jamb_stone'); wbox_abs(113.0, 113.375, -6.15, -0.01, 0.0, H, stn, 'alcove_jamb_stone')
    wbox_abs(-6.0, 168.0, YB - 8, -12.0, H, H + 4.0, clg, 'comp_ceiling')
    wbox_abs(-6.0, 168.0, YB - 8, -12.0, -2.0, 0.0, wd, 'nook_floor')          # underlay, dropped and darkened by board_floor
    board_floor('bath', 'WD-01')
    mosaic(0.0, 43.625, YB, 0.0, 0.0)                                         # the shower floor, TL-03, on through the door to the line's face
    wbox_abs(4.0, 39.6, YB + 2.0, YB + 4.0, -0.05, 0.01, material('METAL-ABRASS') if 'METAL-ABRASS' in MATS else material('METAL-BRASS'), 'linear_drain')
    # the shower door: one panel of 1/2 in. hammered tempered glass, no frame, glass hinges on the pier side, a pull
    hg = bpy.data.materials.get('GLASS-HAMMERED-X') or bpy.data.materials.new('GLASS-HAMMERED-X')
    if not hg.node_tree or 'hammer' not in hg.node_tree.nodes:
        hg.use_nodes = True; N_ = hg.node_tree.nodes; L_ = hg.node_tree.links; b_ = N_['Principled BSDF']
        b_.inputs['Base Color'].default_value = (0.93, 0.95, 0.94, 1); b_.inputs['Transmission Weight'].default_value = 1.0
        b_.inputs['Roughness'].default_value = 0.12; b_.inputs['IOR'].default_value = 1.5
        vo = N_.new('ShaderNodeTexVoronoi'); vo.name = 'hammer'; vo.feature = 'SMOOTH_F1'; vo.inputs['Scale'].default_value = 1.0 / (0.9 * IN)
        bp = N_.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6; bp.inputs['Distance'].default_value = 0.12 * IN
        L_.new(vo.outputs['Distance'], bp.inputs['Height']); L_.new(bp.outputs['Normal'], b_.inputs['Normal'])
    wbox_abs(7.25, 36.75, -3.25, -2.75, 0.5, 95.5, hg, 'shower_door')
    hw = material('METAL-ABRASS') if 'METAL-ABRASS' in MATS else material('METAL-BRASS')
    for hz in (18.0, 78.0): wbox_abs(36.0, 38.5, -3.6, -2.4, hz, hz + 3.5, hw, 'glass_hinge')
    wcyl(9.5, -1.6, 48.0, 0.375, 18.0, 'z', hw, 'shower_pull')
    # the W.C.: a wall-hung toilet on its carrier (ID-320 note 7), centred on the back wall, the flush plate over it
    ch = material('CERAMIC-WHITE'); cx_ = (118.375 + 162.0) / 2
    wbox(cx_ - 7.2, cx_ + 7.2, YB + 0.5, YB + 21.5, 8.0, 15.0, ch, 'toilet', soft=3.0)
    wbox(cx_ - 7.4, cx_ + 7.4, YB + 2.5, YB + 21.8, 15.0, 16.2, ch, 'toilet_lid', soft=1.5)
    wbox(cx_ - 4.5, cx_ + 4.5, YB, YB + 0.6, 41.0, 47.0, hw, 'flush_plate')
    # the compartments' RCP (same sheet as bath_lights.json): an L2 over the tub, in the shower and in the W.C., the W.C.'s
    # exhaust fan; the supply slot by the vanities (FOR M-101, grey)
    for X_, Y_, w_ in ((81.3, -42.8, 12.0), (22.4, -21.2, 20.0), (139.4, -33.2, 12.0)): ceiling_can(X_, Y_, H, watts=w_)
    MATS.setdefault('DIFF-WHITE', {'hex': '#F2F1EC', 'rough': 0.35, 'kind': 'paint'})
    wbox_abs(133.7, 143.7, -53.6, -43.6, H - 0.3, H - 0.01, material('DIFF-WHITE'), 'exhaust_fan')
    for k in range(5): wbox_abs(134.7, 142.7, -52.6 + k * 1.8, -51.9 + k * 1.8, H - 0.35, H - 0.3, material('GAP'), 'exhaust_slot')
    slot_diffuser(69.0, 93.0, 59.4, 61.9, H, slots=1)
    # outside, floor 2 (ID-102): the terrace south of the bath under the tub and shower windows, and west of the terrace doors
    terrace(-96.0, 232.0, -190.0, YB - 10.0, -2.0, rails=((-96.0, -190.0, 232.0, -190.0), (-96.0, -190.0, -96.0, 79.0)))
    terrace(-96.0, -6.0, YB - 10.0, 79.0, -2.0)


def wainscot_w(axis, c, a0, a1, side, top, cuts=(), rail=(41.0, 44.0), base=8.5, target=30.0, name='wains'):
    """Floor 1 wainscot (owner 11.11.26: "are we doing wainscot in the 1st level too? ... the walls look bare"): the master
    bedroom's language at floor 1's height: a 3 in. chair rail with its top at 1/3 of the 10'-8" ceiling (3'-8"), picture-frame
    panels below and above it in matching bays, rails full length and stiles between them (no shared faces), all in the
    tonal trim. `cuts` are door and opening extents (casing included); bays are laid out per solid segment."""
    trm = material(R('trim', 'PT-01-SATIN')); lo_, hi_ = min(a0, a1), max(a0, a1)
    segs = [(lo_, hi_)]
    for c0, c1 in sorted(cuts):
        nxt = []
        for s0, s1 in segs:
            if c1 <= s0 or c0 >= s1: nxt.append((s0, s1)); continue
            if c0 > s0: nxt.append((s0, c0))
            if c1 < s1: nxt.append((c1, s1))
        segs = nxt
    def B(u0, u1, z0, z1, d0, d1, nm, soft=0.2):
        q0, q1 = sorted((c + side * d0, c + side * d1))
        return wbox(q0, q1, u0, u1, z0, z1, trm, nm, soft=soft) if axis == 'y' else wbox(u0, u1, q0, q1, z0, z1, trm, nm, soft=soft)
    for s0, s1 in segs:
        L_ = s1 - s0
        if L_ < 10: continue
        B(s0, s1, rail[0], rail[1], 0.0, 0.7, name + '_rail', soft=0.3)                    # chair rail, less proud than the casing
        n = max(1, int(round((L_ - 4) / (target + 4)))); pw = (L_ - 4 * (n + 1)) / n
        if pw < 6: continue
        for k in range(n):
            p0 = s0 + 4 + k * (pw + 4); p1 = p0 + pw
            for z0, z1 in ((base + 3.0, rail[0] - 3.0), (rail[1] + 4.0, top - 5.0)):
                if z1 - z0 < 8: continue
                m = 1.5
                for (u0, u1, v0, v1) in ((p0, p1, z0, z0 + m), (p0, p1, z1 - m, z1), (p0, p0 + m, z0 + m, z1 - m), (p1 - m, p1, z0 + m, z1 - m)):
                    B(u0, u1, v0, v1, 0.0, 0.625, name + '_mold')


def crystal_chandelier(X, Y, zb, ceiling, name='chandelier'):
    """Owner's reference (11.11.26, living room): a tiered crystal chandelier, champagne gold rings and five tiers of clear
    crystal prisms, wide second tier tapering below, on a chain to a canopy. Bottom at zb (13'-0": just above the gallery
    floor, so it hangs in the upper volume and sits at eye level from the gallery). About 34 in. across and 46 in. tall."""
    MATS.setdefault('METAL-CHAMPAGNE', {'hex': '#C9B48A', 'rough': 0.25, 'kind': 'metal'})
    gold = material('METAL-CHAMPAGNE')
    cm = bpy.data.materials.get('CRYSTAL')
    if cm is None:
        # thin-glass crystal: transparent plus a Fresnel mirror reflection. Refractive glass through a dozen overlapping
        # prisms ran out of bounces and read as a dark smoked cage (test 11.11.26)
        cm = bpy.data.materials.new('CRYSTAL'); cm.use_nodes = True; N_ = cm.node_tree.nodes; L_ = cm.node_tree.links
        out_ = N_['Material Output']; N_.remove(N_['Principled BSDF'])
        tr = N_.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1)
        gl = N_.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.0
        fr = N_.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.9
        mx = N_.new('ShaderNodeMixShader'); L_.new(fr.outputs['Fac'], mx.inputs['Fac']); L_.new(tr.outputs[0], mx.inputs[1]); L_.new(gl.outputs[0], mx.inputs[2])
        em = N_.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (1.0, 0.94, 0.85, 1); em.inputs['Strength'].default_value = 0.05
        ad = N_.new('ShaderNodeAddShader'); L_.new(mx.outputs[0], ad.inputs[0]); L_.new(em.outputs[0], ad.inputs[1])   # the lit glow inside cut crystal
        L_.new(ad.outputs[0], out_.inputs['Surface'])
    tiers = [(8.0, 7.0), (17.0, 11.0), (13.5, 11.0), (9.5, 10.0), (5.0, 8.0)]       # (radius, prism length), top to bottom
    bm_ = bmesh.new(); z = zb + sum(h for _, h in tiers) * 0.72
    zt = z
    for i, (r, h) in enumerate(tiers):
        n = max(10, int(2 * _m.pi * r / 1.4))
        ztop = zt; zbot = ztop - h
        for k in range(n):
            a_ = 2 * _m.pi * (k + 0.5 * (i % 2)) / n; cx_, cy_ = X + r * _m.cos(a_), Y + r * _m.sin(a_)
            w_, t_ = 0.55, 0.4; ca, sa = _m.cos(a_), _m.sin(a_)
            pts = [(cx_ + ca * dx - sa * dy, cy_ + sa * dx + ca * dy) for dx, dy in ((-t_, -w_), (t_, -w_), (t_, w_), (-t_, w_))]
            vb = [bm_.verts.new((x_ * IN, y_ * IN, zbot * IN)) for x_, y_ in pts]; vt = [bm_.verts.new((x_ * IN, y_ * IN, ztop * IN)) for x_, y_ in pts]
            bm_.faces.new(vb[::-1]); bm_.faces.new(vt)
            for j in range(4): bm_.faces.new((vb[j], vb[(j + 1) % 4], vt[(j + 1) % 4], vt[j]))
        bpy.ops.mesh.primitive_torus_add(major_radius=(r + 0.4) * IN, minor_radius=0.45 * IN, major_segments=64, minor_segments=10,
                                         location=(X * IN, Y * IN, (ztop + 0.4) * IN))
        rg = bpy.context.active_object; rg.name = name + '_ring'; rg.data.materials.append(gold)   # a ring, not a disc (a solid disc read as a dark plate)
        for pg in rg.data.polygons: pg.use_smooth = True
        zt = ztop - h * 0.42                                                          # tiers overlap like the reference
    me = bpy.data.meshes.new(name + '_crystal'); bm_.to_mesh(me); bm_.free()
    o = bpy.data.objects.new(name + '_crystal', me); bpy.context.collection.objects.link(o); o.data.materials.append(cm)
    o.visible_shadow = False
    wcyl(X, Y, z + 1.5, 4.0, 2.0, 'z', gold, name + '_crown_plate')
    for r, _ in tiers:                                                               # thin spokes from the crown to each ring
        for k in range(4):
            a_ = _m.pi / 4 + _m.pi * k / 2
            wbox_abs(min(X, X + r * _m.cos(a_)) - 0.2, max(X, X + r * _m.cos(a_)) + 0.2, min(Y, Y + r * _m.sin(a_)) - 0.2, max(Y, Y + r * _m.sin(a_)) + 0.2, z + 0.2, z + 0.5, gold, name + '_spoke') if False else None
    bpy.context.scene.cycles.transparent_max_bounces = 64; bpy.context.scene.cycles.glossy_bounces = max(bpy.context.scene.cycles.glossy_bounces, 6)   # layered crystal
    k = 0; zc = z + 2.5
    while zc < ceiling - 3.0:                                                         # chain links to the canopy
        wbox_abs(X - 0.35, X + 0.35, Y - (0.15 if k % 2 else 0.5), Y + (0.15 if k % 2 else 0.5), zc, zc + 2.2, gold, name + '_chain'); zc += 2.0; k += 1
    wcyl(X, Y, ceiling - 1.0, 3.5, 2.0, 'z', gold, name + '_canopy')
    for k in range(6):                                                                # candle lamps inside the second tier
        ld = bpy.data.lights.new('chandelier', 'POINT'); ld.energy = 22.0; ld.shadow_soft_size = 0.8 * IN; ld.color = (1.0, 0.82, 0.6)
        ol = bpy.data.objects.new(name + '_lamp', ld); bpy.context.collection.objects.link(ol)
        ol.location = ((X + 8.0 * _m.cos(_m.pi * k / 3)) * IN, (Y + 8.0 * _m.sin(_m.pi * k / 3)) * IN, (z - 8.0) * IN)


def stage_living():
    """The living room from build_great_rev1b's numbers: the fireplace wall (ID-231 view 1: plaster breast, WS-01 surround, flush
    hearth, the art-mode TV in its niche, open bookcases each side with 30 in. base cabinets, belt course with the brass rail and
    rolling ladder, the panel band, the gallery cap, the upper cases, CM-02 with its LED cove), the window wall (ID-232: FOR's
    three-panel slider and clerestory with divided lites, the band between, the 22'-4" band with the drapery pocket), the west and
    south galleries with the steel picket guard, and outside the site from FOR A-100 and A-303: the paved deck, the pool, the dining
    wing, the side fence and hedge, and the ancillary structure with its stair and pergola. World inches: X east from the west end's
    west wall, Y north from the south gallery line, Z up. Plan north is true south on this site (A-303), so the window wall faces
    the true south sun."""
    G = dict(RD=194.0, H=272.0, GFW=92.0, BELT0=128.0, BELT1=154.0, SOFFIT=128.0, FF2=154.0, GT=196.0, CROWN_B=256.0, COVE=4.0,
             BAND=268.0, BAND_W=12.0, SL0=120.0, SL1=252.0, SL_HEAD=117.0, CL_HEAD=250.0, BW=84.0, BD=24.0, BI_D=14.0, CAB_H=30.0,
             TOP_T=1.25, FB_W=42.0, FB_B=6.0, FB_T=36.0, LEG=9.0, SHELF_B=45.5, SHELF_T=48.0, TV_W=66.25, TV_H=37.75, TV_B=56.0)
    E = 280.0; RD = G['RD']; Hh = G['H']
    wallm = material(R('wall', 'PT-02')); trim = material(R('trim', 'PT-01-SATIN')); case_m = material('CAB-CREAM', '-trim')   # tonal trim; cases the kitchen's cabinet colour (owner 11.11.26)
    ws = material('TRAV-01'); st1 = material('ST-01'); brass = material('METAL-BRASS'); steel = bronze_mat()   # guard in dark bronze (owner 11.11.26: railing colour); surround and mantel in the breast's travertine (11.11.26)
    def Yw(x): return RD - x                                         # east wall view x (from the north wall) to world Y
    CX = RD / 2; B0 = (RD - G['BW']) / 2; B1 = B0 + G['BW']
    BF = E - G['BD']                                                 # breast face
    IF = E - G['BI_D']                                               # built-in face
    # ---- the breast (owner 11.11.26): light vein-cut travertine floor to the cove, slabs in three courses bookmatched on the
    # centre line, its 10 in. returns clad too; the 4 in. TV niche and the firebox opening cut out of its front
    wallm_ = wallm; wallm = material('TRAV-01')
    yc_ = Yw(RD / 2); h_ = G['FB_W'] / 2; tw_ = G['TV_W']; tb_ = G['TV_B']; th_ = G['TV_H']
    nb, nt, ny0, ny1 = tb_ - 2, tb_ + th_ + 2, yc_ - tw_ / 2 - 2, yc_ + tw_ / 2 + 2
    wbox(BF + 4.0, E, Yw(B1), Yw(B0), 0.0, G['H'] - 9.0, wallm, 'breast')                       # the core behind the niche
    wbox(BF, BF + 4.0, Yw(B1), ny0, 0.0, G['H'] - 9.0, wallm, 'breast_face')                    # the front 4 in., round the niche
    wbox(BF, BF + 4.0, ny1, Yw(B0), 0.0, G['H'] - 9.0, wallm, 'breast_face')
    wbox(BF, BF + 4.0, ny0, ny1, nt, G['H'] - 9.0, wallm, 'breast_face')
    wbox(BF, BF + 4.0, ny0, ny1, G['FB_T'], nb, wallm, 'breast_face')
    wbox(BF, BF + 4.0, ny0, yc_ - h_, 0.0, G['FB_T'], wallm, 'breast_face'); wbox(BF, BF + 4.0, yc_ + h_, ny1, 0.0, G['FB_T'], wallm, 'breast_face')
    # firebox: listed direct-vent unit, 42 x 30 opening 6 in. above the flush hearth, black glass
    h = G['FB_W'] / 2; yc = Yw(CX)
    wbox(BF - 0.01, BF + 0.4, yc - h, yc + h, G['FB_B'], G['FB_T'], material('OVEN-GLASS'), 'firebox_glass')
    wbox(BF + 4.0, BF + 14, yc - h, yc + h, G['FB_B'], G['FB_T'], material('GAP'), 'firebox')
    wbox(BF + 0.4, BF + 4.0, yc - h, yc + h, 0.0, G['FB_B'], wallm, 'firebox_sill')
    for k in range(5):                                               # a low gas flame bed, warm
        wbox(BF + 3, BF + 9, yc - 15 + k * 7, yc - 11 + k * 7, G['FB_B'] + 1.5, G['FB_B'] + 3.0, material('LAMP'), 'ember')
    # WS-01 surround: 9 in. legs, frieze, a 2-1/2 in. shelf at 4'-0" projecting 6 in.; bolection bead round the opening
    L_ = G['LEG']; S0 = yc - h - L_; S1 = yc + h + L_
    wbox(BF - 1.5, BF, S0, yc - h, 0.0, G['SHELF_B'], ws, 'surround_leg', soft=0.15)
    wbox(BF - 1.5, BF, yc + h, S1, 0.0, G['SHELF_B'], ws, 'surround_leg', soft=0.15)
    wbox(BF - 1.5, BF, yc - h, yc + h, G['FB_T'], G['SHELF_B'], ws, 'surround_frieze', soft=0.15)
    wbox(BF - 6.0, BF, S0 - 1.0, S1 + 1.0, G['SHELF_B'], G['SHELF_T'], ws, 'mantel_shelf', soft=0.2)
    for (a_, b_, z0, z1) in ((yc - h - 1.5, yc - h, 0, G['FB_T']), (yc + h, yc + h + 1.5, 0, G['FB_T']), (yc - h - 1.5, yc + h + 1.5, G['FB_T'], G['FB_T'] + 1.5)):   # legs stop under the head: lapped corners rendered black
        wbox(BF - 2.25, BF - 1.5, a_, b_, z0, z1, ws, 'bolection', soft=0.3)
    wbox(BF - 20.0, BF, yc - 33.0, yc + 33.0, -0.02, 0.03, material('TRAV-01'), 'hearth')   # flush hearth 5'-6" x 1'-8", the breast's travertine
    MATS.setdefault('GROUT-TRAV', {'hex': '#CDBFA9', 'rough': 0.8, 'kind': 'paint'})
    gt = material('GROUT-TRAV'); ztop = G['H'] - 9.0
    for zj in (112.0, 188.0):                                                  # course joints, face and returns
        wbox(BF - 0.03, BF, Yw(B1), Yw(B0), zj - 0.03, zj + 0.03, gt, 'trav_joint')
        for yy in (Yw(B1), Yw(B0)): wbox(BF, IF, yy - 0.03, yy + 0.03, zj - 0.03, zj + 0.03, gt, 'trav_joint')
    wbox(BF - 0.03, BF, yc - 0.03, yc + 0.03, nt, ztop, gt, 'trav_joint')      # the bookmatch line above the TV
    wallm = wallm_
    # TV: the art-mode set nearly flush in a 4 in. niche 2 in. larger each way
    tb = G['TV_B']; tw = G['TV_W']; th = G['TV_H']
    # the set sits nearly flush: its face 1/2 in. behind the breast face, the niche's 2 in. margin dark round it
    wbox(BF + 1.6, BF + 4.0, yc - tw / 2 - 2, yc + tw / 2 + 2, tb - 2, tb + th + 2, wallm, 'niche_back')   # painted returns in shadow, not a void
    wbox(BF + 0.5, BF + 1.6, yc - tw / 2, yc + tw / 2, tb, tb + th, material('TV-BLACK'), 'tv')
    # (owner 11.11.26: a painting over the TV, so the set is shown off, black glass, not in art mode)
    art_ = bpy.data.materials.new('ART-ABSTRACT'); art_.use_nodes = True; an = art_.node_tree.nodes; al = art_.node_tree.links
    # staging: an abstract landscape on the art-mode screen (soft ochre ground, sage band, pale sky), not a blank beige panel (R6)
    ab_ = an['Principled BSDF']; ab_.inputs['Roughness'].default_value = 0.7
    atc = an.new('ShaderNodeTexCoord'); asep = an.new('ShaderNodeSeparateXYZ'); al.new(atc.outputs['Generated'], asep.inputs['Vector'])
    anz = an.new('ShaderNodeTexNoise'); anz.inputs['Scale'].default_value = 3.0; anz.inputs['Detail'].default_value = 8.0; anz.inputs['Roughness'].default_value = 0.65
    al.new(atc.outputs['Generated'], anz.inputs['Vector'])
    amx = an.new('ShaderNodeMath'); amx.operation = 'MULTIPLY_ADD'; amx.inputs[1].default_value = 0.22; amx.inputs[2].default_value = -0.11
    al.new(anz.outputs['Fac'], amx.inputs[0]); aad = an.new('ShaderNodeMath'); aad.operation = 'ADD'
    al.new(asep.outputs['Z'], aad.inputs[0]); al.new(amx.outputs['Value'], aad.inputs[1])
    arp = an.new('ShaderNodeValToRGB'); el = arp.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.32, 0.20, 0.10, 1); el[1].position = 1.0; el[1].color = (0.80, 0.78, 0.72, 1)
    for pos_, col_ in ((0.30, (0.55, 0.38, 0.20, 1)), (0.42, (0.36, 0.40, 0.30, 1)), (0.55, (0.52, 0.55, 0.48, 1)), (0.70, (0.74, 0.70, 0.62, 1))):
        e_ = el.new(pos_); e_.color = col_
    al.new(aad.outputs['Value'], arp.inputs['Fac']); al.new(arp.outputs['Color'], ab_.inputs['Base Color'])
    # paintings (owner 11.11.26): a tall narrow canvas on the breast over the TV, 36 x 96 to the frame's outside, aligned top and
    # foot with the upper cases (owner: centre it on the top section of shelves); before that its foot sat 16 in. over the set and its
    # middle level with the band each side; the two drawn ART, N.I.C. places under the galleries (ID-231 view 2, ID-233
    # view 4), hung above the wainscot rail with brass picture lights
    painting('landscape', BF, yc, (G['BELT1'] + G['CL_HEAD']) / 2, 34.25, 94.25, '-x', frame='oak', light=False, name='art_breast')   # owner 11.11.26: top and foot on the upper cases' 12'-10" and 20'-10"
    painting('abstract', 0.0, 134.5, 78.0, 48.0, 48.0, '+x', frame=None, name='art_west')
    painting('pinkfield', 46.0, 0.0, 76.0, 36.0, 48.0, '+y', frame='black', name='art_south')
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
                wbox(IF - 0.06, IF, ya + side, yb - side, zt - thick, zt - thick + 0.5, steel, 'shelf_flat')   # the steel flat in the shelf's front edge
            books(ya + side, yb - side, z0 + (k - 1) * p_ + (0 if k == 1 else 0))
    for (ya, yb) in ((Yw(G['RD']), Yw(B1)), (Yw(B0), Yw(0.0))):      # south flank, north flank (world Y order)
        # 30 in. inset base cabinet: 4-1/2 in. toe 3 in. back, a pair of inset doors in a face frame, WS-01 top
        wbox(IF + 3, E, ya, yb, 0.0, 4.5, case_m, 'toe')
        wbox(IF, E, ya, yb, 4.5, G['CAB_H'], case_m, 'cab_frame', soft=0.1)
        dw = (yb - ya - 3.0) / 2
        for j in range(2):
            a_ = ya + 1.5 + j * (dw) + (0.0625 if j else 0); b_ = a_ + dw - 0.125
            shaker_door_x(IF, a_, b_, 6.0, G['CAB_H'] - 1.5, case_m)      # the kitchen's slim shaker (owner 11.11.26)
            wbox(IF + 0.75, IF + 1.0, a_, b_, 6.0, G['CAB_H'] - 1.5, material('GAP'), 'door_reveal')
            px = b_ - 2.0 if j == 0 else a_ + 2.0
            wcyl(IF - 0.6, px, G['CAB_H'] - 7.0, 0.25, 6.0, 'z', brass, 'pull')
        wbox(IF - 1.0, E, ya, yb, G['CAB_H'], G['CAB_H'] + G['TOP_T'], ws, 'cab_top', soft=0.15)
        # owner 11.11.26: the cases run right up to and down from a drywall band at the gallery fascia's elevation (10'-8" to
        # 12'-10"), the band panelled like the fascia, the brass ladder rail centred in it
        case(ya, yb, G['CAB_H'] + G['TOP_T'], G['BELT0'])
        wbox(IF, E, ya, yb, G['BELT0'], G['BELT1'], wallm, 'band_drywall')
        band_panels('y', IF, ya, yb, -1, G['BELT0'], G['BELT1'])
        wcyl(IF - 2.6, (ya + yb) / 2, (G['BELT0'] + G['BELT1']) / 2, 0.625, yb - ya - 1.0, 'y', brass, 'ladder_rail')
        for yy in (ya + 6.0, yb - 6.0):                                # rail brackets back to the band
            wcyl(IF - 1.3, yy, (G['BELT0'] + G['BELT1']) / 2, 0.35, 2.6, 'x', brass, 'rail_bracket')
        case(ya, yb, G['BELT1'], G['CL_HEAD'])
        wbox(IF, E, ya, yb, G['CL_HEAD'], G['H'] - 4.0 - 5.0 - 3.77, case_m, 'frieze')
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
        wbox(x_ - 0.6, x_ + 0.6, Yw(21.0) + 1.75, Yw(3.0) - 1.75, z_ - 0.5, z_ + 0.5, oak, 'ladder_rung')   # between the stiles, not through them
    wcyl(lx0, Yw(3.0) - 0.9, 1.2, 1.2, 1.0, 'y', brass, 'ladder_wheel'); wcyl(lx0, Yw(21.0) + 0.9, 1.2, 1.2, 1.0, 'y', brass, 'ladder_wheel')
    # CM-02 crown held 4 in. under the ceiling on the east wall (cases and breast), LED cove on its top
    def crown_run(x_face, ya, yb, top):
        # a moulded CM-02 profile (bead, cyma recta, top fillet), 12 in. high, 5-1/2 in. projection, extruded along the run.
        # Four stacked bevelled boxes read as bolsters (R6 review 11.10.26)
        z0 = top - 12.0; pr = [(0.0, z0), (0.6, z0), (0.6, z0 + 0.5), (0.9, z0 + 0.9)]
        for i in range(1, 25):
            t = i / 24.0; pr.append((0.9 + 4.1 * (0.5 - 0.5 * _m.cos(_m.pi * t)), z0 + 0.9 + 9.6 * t))
        pr += [(5.5, z0 + 10.5), (5.5, z0 + 12.0), (0.0, z0 + 12.0)]
        o_ = wprism_xz([(x_face - p_, z_) for p_, z_ in pr], min(ya, yb), max(ya, yb), trim, 'crown')
        for pg in o_.data.polygons: pg.use_smooth = True
        o_.data.set_sharp_from_angle(angle=_m.radians(25))          # smooth along the cyma, crisp at the fillets so the profile reads
        wbox(x_face - 5.0, x_face - 4.4, ya, yb, top, top + 0.4, material('LAMP'), 'cove_led')
    top = Hh - G['COVE']
    # owner 11.11.26: one rectangular LED cove all round the volume at 22'-4": the east wall (cases, breast and its sides), the
    # window wall (12 in. deep, the drapery pocket in it), and the two gallery edges (no crown there, no wall under them)
    # FOR's detail (A-401 sect. 2): 14 in. soffits, 19-1/2 in. on the window wall with the 5 in. drapery pocket in it. The pieces
    # tile without overlapping (overlapping coplanar boards render black): the flanks run to the breast sides, the breast's
    # 10 in. returns are shorter than the soffit so a short piece closes each corner, the window and gallery pieces stop at
    # the flank and gallery soffits.
    PS_ = 14.0; PW_ = 19.5; GE_ = G['GFW'] - 5.5
    cove_w('y', IF, 0.0, Yw(B1), -1, top, P=PS_); cove_w('y', IF, Yw(B0), RD, -1, top, P=PS_)
    cove_w('y', BF, Yw(B1), Yw(B0), -1, top, P=PS_)
    cove_w('x', Yw(B1), BF - PS_, IF - PS_, -1, top, P=PS_, crown=False, name='cove_bs')
    cove_w('x', Yw(B0), BF - PS_, IF - PS_, +1, top, P=PS_, crown=False, name='cove_bn')
    cove_w('x', RD, GE_ + PS_, IF - PS_, -1, top, P=PW_, name='cove_win')
    cove_w('x', 0.0, GE_ + PS_, IF - PS_, +1, top, P=PS_, crown=False, name='cove_gs')   # off the south header's face (Y 0)
    cove_w('y', GE_, 0.0, RD, +1, top, P=PS_, crown=False, name='cove_gw')
    wbox(0.0, G['GFW'] - 5.5, -5.5, RD, top, Hh, material(R('ceiling', 'PT-01')), 'gallery_w_ceiling')   # floor 2 hall, 9'-6" (FOR)
    # ---- the window wall: FOR's 3-panel slider and 3-lite clerestory, divided lites, dark bronze frames, drywall returns
    fr = material('FRAME-BLK'); gl = material('GLASS-CLEAR')
    def glazed(x0, x1, z0, z1, n, operable, y_face=RD + 2.5):
        pw = (x1 - x0) / n
        wbox(x0, x1, RD, RD + 6.0, z0, z0 + 0.5, fr, 'sill')
        for i in range(n):
            a_ = x0 + i * pw; b_ = a_ + pw
            yo = y_face + (0 if not operable else (i % 2) * 1.6)        # the sliding panels on their own tracks
            for r_ in ((a_, a_ + 2.5, z0, z1), (b_ - 2.5, b_, z0, z1), (a_ + 2.5, b_ - 2.5, z0, z0 + 3.0), (a_ + 2.5, b_ - 2.5, z1 - 2.5, z1)):   # rails between stiles
                wbox(r_[0], r_[1], yo, yo + 2.0, r_[2], r_[3], fr, 'frame', soft=0.08)
            gx0, gx1, gz0, gz1 = a_ + 2.5, b_ - 2.5, z0 + 3.0, z1 - 2.5
            g_ = wbox(gx0, gx1, yo + 0.9, yo + 1.1, gz0, gz1, gl, 'glass')
            if g_: g_['exterior'] = True
            cols, rows = max(1, round(3 / PANE)), max(1, round(7 / PANE))   # FOR's 3 x 7 lites, panes 75% larger each way (owner 11.11.26)
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
    # (the 22'-4" band is now the window wall's 12 in. cove soffit, cove_win above)
    MATS.setdefault('POCKET', {'hex': '#8A857E', 'rough': 0.8, 'kind': 'paint'})   # the slot's inside in shadow, not a black bar
    wbox(PK0, PK1, RD - 7.0, RD - 2.0, top - 0.02, top + 0.55, material('POCKET'), 'drapery_pocket')   # the pocket in FOR's soffit
    # the band on the window wall's solid ends, stopped at FOR's jambs (owner 11.11.26)
    band_panels('x', RD, G['GFW'], G['SL0'] - 1.0, -1, G['BELT0'], G['BELT1']); band_panels('x', RD, G['SL1'] + 1.0, IF, -1, G['BELT0'], G['BELT1'])
    # no crown on the window wall: the pocket runs 14 in. past each jamb, leaving 13 in. west and none east (R6: a corbel)
    for (a_, b_) in ((G['GFW'], G['SL0']), (G['SL1'], IF)):
        wbox(a_, b_, RD - 0.6, RD, 0.0, 8.5, trim, 'base', soft=0.15)
    for (a_, b_) in ((4.0, 92.2), (230.7, IF)):   # the south wall under the gallery (R6), stopped at the open south end's jambs
        wbox(a_, b_, 0.0, 0.6, 0.0, 8.5, trim, 'base_s', soft=0.15)
    # ---- the kitchen's arched opening in the west end's north wall (build_great_rev1b ARCH, arched_cased_opening): 1'-5" pier,
    # 4'-10" wide, the arc meeting the jambs at 7'-2", radius 0.62 x width, apex 8'-4-3/4"; the shell's hole runs to 101.5, the
    # spandrels fill it back to the arc through the wall's 6 in., and the 5 in. casing follows the arc on the room face
    ax_, aw_, asp = 17.0, 58.0, 86.0; ar_ = aw_ * 0.62; acx = ax_ + aw_ / 2; acz = asp - _m.sqrt(ar_ ** 2 - (aw_ / 2) ** 2); acs = 5.0
    def _arc(rr, xa, xb, k=36):
        a0 = _m.atan2(_m.sqrt(max(rr ** 2 - (xa - acx) ** 2, 0)), xa - acx); a1 = _m.atan2(_m.sqrt(max(rr ** 2 - (xb - acx) ** 2, 0)), xb - acx)
        return [(acx + rr * _m.cos(a0 + (a1 - a0) * i / k), acz + rr * _m.sin(a0 + (a1 - a0) * i / k)) for i in range(k + 1)]
    inner_ = _arc(ar_, ax_, ax_ + aw_)                              # left jamb top to right jamb top, over the apex
    wprism_xz([(ax_, 101.5), (ax_ + aw_, 101.5)] + inner_[::-1], RD, RD + 6.0, wallm, 'arch_spandrel')
    sp_out = acz + _m.sqrt((ar_ + acs) ** 2 - (aw_ / 2 + acs) ** 2)
    outer_ = _arc(ar_ + acs, ax_ - acs, ax_ + aw_ + acs)
    wprism_xz([(ax_ - acs, 0.0)] + outer_ + [(ax_ + aw_ + acs, 0.0), (ax_ + aw_, 0.0)] + inner_[::-1] + [(ax_, 0.0)],
              RD - 0.75, RD, trim, 'arch_casing')
    # ---- galleries: floor 2 over the west end and the south end, the fascia, cap and steel picket guard
    pt1 = material(R('ceiling', 'PT-01'))
    wbox(0.0, G['GFW'] - 0.6, 0.0, RD, G['SOFFIT'], G['FF2'] - 1.5, pt1, 'gallery_slab_w')   # stops at the fascia and the cap: no shared faces
    wbox(0.0, 236.7, -148.0, -6.0, G['SOFFIT'], G['FF2'] - 1.5, pt1, 'gallery_slab_s')   # its underside is the south end's 10'-8" ceiling
    wbox(0.0, 236.7, -202.7, -148.0, 132.0, G['FF2'] - 1.5, pt1, 'gallery_slab_s2')   # 11'-0" south of the stair line, over the lower flight (6'-8" headroom, FOR): one clean soffit line across the room
    wbox(236.7, E, -202.7, -158.0, 132.0, G['FF2'] - 1.5, pt1, 'gallery_slab_se')   # over the southeast landing, 6'-8" headroom (FOR); the stairwell open
    wbox_abs(0.0, G['GFW'] - 3, -3.0, RD, G['FF2'], G['FF2'] + 0.5, material(R('floor', 'WD-01')), 'floor2_w')   # world coordinates and on to the south corridor: one floor round the corner (a seam showed, 11.11.26)
    wbox_abs(0.0, 236.7, -60.0, -3.0, G['FF2'], G['FF2'] + 0.5, material(R('floor', 'WD-01')), 'floor2_s')   # the stairwell east of 236.7
    board_floor('hall', 'WD-01', top=G['FF2'] + 0.5, under=('floor2_w', 'floor2_s'))   # board by board with the 4-1/2 in. WD-02 border (ID-102)
    wbox(G['GFW'] - 0.6, G['GFW'], 0.0, RD, G['SOFFIT'], G['FF2'], wallm, 'fascia_w')
    wbox(G['GFW'], E, 0.0, 0.25, G['SOFFIT'], G['FF2'], wallm, 'fascia_s')   # proud of the wall below it: no shared face
    band_panels('y', G['GFW'], 0.0, RD, +1, G['SOFFIT'], G['FF2'] - 1.5)
    band_panels('x', 0.25, G['GFW'], IF, +1, G['SOFFIT'], G['FF2'] - 1.5)
    # owner 11.11.26: a drywall return at the south end of the east cases, no deeper than the cases, that the cases and the
    # gallery guard die into
    wbox(IF, E, -4.5, 0.0, G['FF2'], Hh, wallm, 'return_wall')
    wbox(G['GFW'] - 1.5, G['GFW'] + 0.5, 0.0, RD, G['FF2'] - 1.5, G['FF2'], trim, 'fascia_cap_w')
    wbox(G['GFW'], E, -1.5, 0.5, G['FF2'] - 1.5, G['FF2'], trim, 'fascia_cap_s')
    south_end(wallm, trim, pt1)
    for Y_ in (31.1, 128.2, 160.5):   # the plan's cans under the west gallery (RCP X 45.1), at its 10'-8" soffit
        ceiling_can(45.1, Y_, G['SOFFIT'], 10.0)
    def guard(axis, a0, a1, c):
        posts_ = [a0] + [a0 + k * 72.0 for k in range(1, int((a1 - a0) / 72.0) + 1)] + [a1 - 2.0]
        for k in range(int((a1 - a0) / 4.5) + 1):
            p = a0 + k * 4.5
            if any(q - 0.75 < p < q + 2.0 for q in posts_): continue        # no picket inside a post
            if axis == 'y': wbox(c - 0.375, c + 0.375, p, p + 0.75, G['FF2'] + 2.0, G['GT'] - 1.5, steel, 'picket')
            else: wbox(p, p + 0.75, c - 0.375, c + 0.375, G['FF2'] + 2.0, G['GT'] - 1.5, steel, 'picket')
        for z0, z1 in ((G['FF2'] + 2.0, G['FF2'] + 3.5), (G['GT'] - 2.5, G['GT'] - 1.25)):
            if axis == 'y': wbox(c - 0.75, c + 0.75, a0, a1, z0, z1, steel, 'guard_rail')
            else: wbox(a0, a1, c - 0.75, c + 0.75, z0, z1, steel, 'guard_rail')
        oak_ = rail_oak()                                                  # white oak cap, 2-3/4 x 1-1/2, eased (owner 11.11.26)
        if axis == 'y': wbox(c - 1.375, c + 1.375, a0 - 1.0, a1 + 1.0, G['GT'] - 1.25, G['GT'] + 0.25, oak_, 'guard_cap', soft=0.4)
        else: wbox(a0 - 1.0, a1 + 1.0, c - 1.375, c + 1.375, G['GT'] - 1.25, G['GT'] + 0.25, oak_, 'guard_cap', soft=0.4)
        posts = [a0 + k * 72.0 for k in range(1, int((a1 - a0) / 72.0) + 1)] + [a1 - 2.0]   # the shared corner post stands at a0
        for p in posts:
            if axis == 'y': wbox(c - 1.0, c + 1.0, p, p + 2.0, G['FF2'], G['GT'] - 1.25, steel, 'guard_post')
            else: wbox(p, p + 2.0, c - 1.0, c + 1.0, G['FF2'], G['GT'] - 1.25, steel, 'guard_post')
    guard('y', -3.0, RD - 1.0, G['GFW'] - 2.0); guard('x', G['GFW'] - 1.0, IF, -2.0)   # the two runs share the corner post (a gap showed from the corridor, 11.11.26)
    wbox(G['GFW'] - 3.0, G['GFW'] + 1.0, -3.0, -1.0, G['FF2'], G['GT'] - 1.25, steel, 'guard_corner_post')   # one 4 x 2 corner post, a hair over the rails
    wbox(0.0, 230.7, -60.0, -54.0, G['FF2'], Hh, wallm, 'hall_wall_s')
    wbox(0.0, IF, -60.0, -5.5, 268.0, 272.0, material(R('ceiling', 'PT-01')), 'hall_ceiling')   # floor 2 hall, 9'-6" (FOR), to the gallery cove
    wbox(0.0, 4.0, -60.0, RD, G['FF2'], Hh, wallm, 'hall_wall_w_face')
    wbox(E - 4.0, E, -60.0, 0.0, G['FF2'], Hh, wallm, 'hall_wall_e_face')   # the hall's east end (R6: it was open to the sky)
    # ---- floor 1 wainscot (owner 11.11.26) on the lower story's solid walls: the west wall under the gallery, the window wall
    # west of the slider's drapery stack, the south wall under the west gallery, the south end hall's west wall (door 12 cut)
    wbox(0.0, 0.6, 0.6, RD - 0.6, 0.0, 8.5, trim, 'base_w', soft=0.15)            # the west wall had no base
    wainscot_w('y', 0.0, 0.6, RD - 0.6, +1, G['SOFFIT'], name='wains_w')
    wainscot_w('x', RD, 80.0, G['SL0'] - 6.0, -1, G['SOFFIT'], name='wains_n')
    wainscot_w('x', 0.0, 4.0, 92.2, +1, G['SOFFIT'], name='wains_s')
    wainscot_w('y', 92.2, -190.0, -6.0, +1, 128.0, cuts=((-126.0, -85.0),), name='wains_hall')
    # the living room chandelier (owner 11.11.26): centred over the seating, its bottom at 13'-0"
    crystal_chandelier(176.0, yc, 156.0, Hh)
    # ---- staging (captioned; furniture plan ID-60x to match, owner 11.11.26): Megan's boucle sofa (10 ft) with its back on the
    # west gallery line facing the fireplace, the smaller one (7 ft) perpendicular on the south side facing the windows, a
    # modern coffee table, all on one 12 x 14 ft rug
    MATS.setdefault('SOFA-PLINTH', {'hex': '#2A231D', 'rough': 0.6, 'kind': 'paint'})
    MATS.setdefault('FAB-RUG-LIV', {'hex': '#9C9283', 'rough': 0.95, 'kind': 'fabric', 'texture': 'acg/Carpet016'})   # a mid greige wool, the reference's
    rug = material('FAB-RUG-LIV'); cy = yc
    wbox(100.0, 244.0, 14.0, 182.0, 0.0, 0.45, rug, 'rug', soft=0.2)
    boucle_sofa(G['GFW'] + 4.0, cy + 60.0, 120.0, 42.0, '+x', modules=3, name='sofa')
    boucle_sofa(146.0, 18.0, 84.0, 40.0, '+y', modules=2, name='sofa2')
    # pillows and a throw (the reference's): dark, ochre, gold, a cream throw over the arm
    # no throw pillows on the sofas (owner 11.11.26: remove them)
    MATS.setdefault('FAB-THROW', {'hex': '#E4DCCB', 'rough': 0.95, 'kind': 'fabric', 'texture': 'rough_linen'})
    # the throw over the south arm (a flat sheet across the seat read as a white board, 11.11.26)
    # (no throw: a box can't drape, and it read as a white board on the arm, 11.11.26)
    # coffee table: a low rounded travertine slab on a recessed plinth, 54 x 30 x 14
    MATS.setdefault('TRAV-TABLE', {'hex': '#D8CDBB', 'rough': 0.45, 'kind': 'stone', 'texture': 'marble_01', 'tint': [0.95, 0.9, 0.82]})
    tx0, tx1 = 166.0, 196.0
    wbox(tx0 + 4, tx1 - 4, cy - 23.0, cy + 23.0, 0.0, 10.5, material('TRAV-TABLE'), 'coffee_base', soft=1.0)
    wbox(tx0, tx1, cy - 27.0, cy + 27.0, 10.5, 14.0, material('TRAV-TABLE'), 'coffee_top', soft=1.2)
    import_model('wooden_bowl_01', 2.5, 178.0, cy - 8, 14.0, 0); import_model('ceramic_vase_01', 8.0, 186.0, cy + 12, 14.0, 0)
    # ---- outside (FOR A-100 at 1/8 in., A-303): X = 92 + (site x - 773) / 0.75, Y = 202 + (705 - site y) / 0.75
    ext = material('STUCCO-EXT'); deck = material('DECK-01')
    # the hedge: leaf-scale colour variation and a deep bump, so it reads as planting and not a green-painted wall
    hedge = bpy.data.materials.new('HEDGE'); hedge.use_nodes = True; hn = hedge.node_tree.nodes; hl = hedge.node_tree.links
    hb = hn['Principled BSDF']; hb.inputs['Roughness'].default_value = 0.85
    tco_ = hn.new('ShaderNodeTexCoord'); vo = hn.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 32.0   # cells about 1-1/4 in., in object space (meters)
    no = hn.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 2.5; no.inputs['Detail'].default_value = 6.0
    hl.new(tco_.outputs['Object'], vo.inputs['Vector']); hl.new(tco_.outputs['Object'], no.inputs['Vector'])
    cr = hn.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (0.012, 0.028, 0.008, 1); cr.color_ramp.elements[1].color = (0.04, 0.08, 0.02, 1)   # the hedge's shaded inside, under the leaves
    mx = hn.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'
    hl.new(vo.outputs['Distance'], mx.inputs[0]); hl.new(no.outputs['Fac'], mx.inputs[1]); hl.new(mx.outputs['Value'], cr.inputs['Fac'])
    hl.new(cr.outputs['Color'], hb.inputs['Base Color'])
    bu = hn.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = 0.9; bu.inputs['Distance'].default_value = 0.03
    hl.new(vo.outputs['Distance'], bu.inputs['Height']); hl.new(bu.outputs['Normal'], hb.inputs['Normal'])
    if 'kitchen' not in CONTEXT:   # with the kitchen loaded through the arch, the wing is the real kitchen, not a massing block
        wbox(-193.0, 86.0, RD + 6.0, 481.0, -6.0, 300.0, ext, 'dining_wing')            # the kitchen and dining wing, its east face on the notch
        wbox(-195.0, 88.0, RD + 4.0, 483.0, 300.0, 304.0, material('ST-05'), 'wing_coping')   # stone coping (FOR A-301 parapet cap)
        wbox(86.0, 86.3, RD + 6.0, 481.0, 154.0, 155.0, material('POCKET'), 'wing_reveal')   # floor-line reveal in the stucco
    # the living wing's own north face, seen from the kitchen's slider across the deck (owner 11.11.26: the dining view showed
    # no building): stucco over the window wall's outside from the kitchen wing's notch to the east corner, cut round FOR's
    # slider and clerestory, the floor-line reveal and the stone coping
    for (x0_, x1_, z0_, z1_) in ((86.0, G['SL0'], -6.0, 300.0), (G['SL1'], E + 6.0, -6.0, 300.0), (G['SL0'], G['SL1'], G['SL_HEAD'], 124.0),
                                 (G['SL0'], G['SL1'], 250.0, 300.0)):
        wbox(x0_, x1_, RD + 6.0, RD + 7.0, z0_, z1_, ext, 'living_facade')
    wbox(86.0, E + 8.0, RD + 4.0, RD + 9.0, 300.0, 304.0, material('ST-05'), 'living_coping')
    # the pool: 6'-8" x 11'-0" (A-100), stone coping 12 in., water 6 in. below the coping
    px0, px1, py0, py1 = 197.0, 277.0, 286.0, 418.0
    for r_ in ((px0 - 12, px1 + 12, py0 - 12, py0), (px0 - 12, px1 + 12, py1, py1 + 12), (px0 - 12, px0, py0, py1), (px1, px1 + 12, py0, py1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -0.5, 1.0, st1, 'coping', soft=0.4)
    pp = material('POOL-PLASTER')
    wbox(px0, px1, py0, py1, -54.0, -52.0, pp, 'pool_floor')
    for r_ in ((px0 - 1, px0, py0, py1), (px1, px1 + 1, py0, py1), (px0, px1, py0 - 1, py0), (px0, px1, py1, py1 + 1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -54.0, 1.0, pp, 'pool_wall')
    wbox(px0, px1, py0, py0 + 20, -54.0, -18.0, pp, 'pool_bench')        # the step and bench at the house end (A-100 lines)
    # the deck around the pool's water (it covered the pool in the first preview), 24 in. pavers with joints
    for r_ in ((-200.0, 360.0, RD + 6.0, py0 - 1), (-200.0, 360.0, py1 + 1, 830.0), (-200.0, px0 - 1, py0 - 1, py1 + 1), (px1 + 1, 360.0, py0 - 1, py1 + 1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -6.0, -0.5, deck, 'deck')
    jm = material('PAVER-JOINT')
    def _cut(a0, a1, h0, h1):   # a joint run, broken across the pool and its coping
        return [(a0, a1)] if not h0 < h1 else [(a0, min(a1, h0)), (max(a0, h1), a1)]
    for k in range(1, 16):                                          # joints across the deck (constant Y)
        y_ = RD + 6.0 + 24.0 * k
        if y_ > 575.0: break
        hit = py0 - 12 <= y_ <= py1 + 12
        for a0, a1 in _cut(86.0, 338.0, px0 - 12 if hit else 1, px1 + 12 if hit else 0):
            pass   # the paver texture carries its own joints
    for k in range(0, 11):                                          # joints along the deck (constant X), on the pool's grid
        x_ = px0 - 12 - 24.0 * 4 + 24.0 * k
        if not 86.0 < x_ < 338.0: continue
        hit = px0 - 12 <= x_ <= px1 + 12
        for a0, a1 in _cut(RD + 6.0, 575.0, py0 - 12 if hit else 1, py1 + 12 if hit else 0):
            pass
    wm = bpy.data.materials.new('POOL-WATER'); wm.use_nodes = True; bw_ = wm.node_tree.nodes['Principled BSDF']
    bw_.inputs['Base Color'].default_value = (0.36, 0.70, 0.74, 1); bw_.inputs['Roughness'].default_value = 0.04   # aqua: clear water over white plaster reads as nothing
    bw_.inputs['Transmission Weight'].default_value = 1.0; bw_.inputs['IOR'].default_value = 1.33
    tex = wm.node_tree.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 6.0
    bump = wm.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08
    wm.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height']); wm.node_tree.links.new(bump.outputs['Normal'], bw_.inputs['Normal'])
    wbox(px0, px1, py0, py1, -6.5, -6.0, wm, 'pool_water')
    # the side yard: fence 1 ft inside the east line with a hedge in front (landscape plan, placeholder)
    wbox(338.0, 341.0, RD + 6.0, 818.0, 0.0, 72.0, ext, 'fence')
    h1_ = wbox(306.0, 338.0, RD + 30.0, 818.0, 0.0, 108.0, hedge, 'hedge', soft=6.0)
    wbox(-200.0, 341.0, 818.0, 821.0, 0.0, 72.0, ext, 'fence_rear'); h2_ = wbox(-200.0, 341.0, 790.0, 818.0, 0.0, 120.0, hedge, 'hedge_rear', soft=8.0)
    leafy([h1_, h2_])
    # the ancillary structure (A-204, A-303): 28'-9" x 10'-3", slab 11'-0", parapet 14'-0"; its north face (toward the house):
    # a full-lite door, a picture window; the exterior stair on its plan-east side to the roof deck, metal picket railing; pergola
    ax0, ax1, ay0, ay1 = -129.0, 216.0, 575.0, 698.0
    # the body behind a 10 in. front wall that has the door and window cut through it, so the openings have depth
    wbox(ax0, ax1, ay0 + 10.0, ay1, -6.0, 132.0, ext, 'ancillary')
    for (x0_, x1_, z0_, z1_) in ((ax0, 23.0, -6.0, 132.0), (23.0, 55.0, 96.0, 132.0), (55.0, 99.0, -6.0, 132.0), (99.0, 178.0, -6.0, 36.0),
                                 (99.0, 178.0, 96.0, 132.0), (178.0, ax1, -6.0, 132.0)):
        wbox(x0_, x1_, ay0, ay0 + 10.0, z0_, z1_, ext, 'anc_front')
    wbox(ax0, ax1, ay0, ay0 + 6, 132.0, 168.0, ext, 'parapet'); wbox(ax0, ax1, ay1 - 6, ay1, 132.0, 168.0, ext, 'parapet')
    wbox(ax0, ax0 + 6, ay0 + 6, ay1 - 6, 132.0, 168.0, ext, 'parapet'); wbox(ax1 - 6, ax1, ay0 + 6, ay1 - 6, 132.0, 150.0, ext, 'parapet')   # between the long parapets: lapped corners showed a black slot
    # openings cut as recesses with frames as rings and the glass in front of a dark room (R6: a solid black slab read as a board)
    for (x0_, x1_, z0_, z1_, nm) in ((23.0, 55.0, 0.0, 96.0, 'anc_door'), (99.0, 178.0, 36.0, 96.0, 'anc_window')):
        wbox(x0_ + 2, x1_ - 2, ay0 + 9.0, ay0 + 10.0, z0_ + 2 if z0_ else 0.0, z1_ - 2, wallm, nm + '_room')        # the room's back wall, 9 in. in
        for sx_ in (x0_ + 2, x1_ - 3):
            wbox(sx_, sx_ + 1, ay0 - 0.2, ay0 + 9.0, z0_ + 2 if z0_ else 0.0, z1_ - 2, ext, nm + '_jamb')
        wbox(x0_ + 3, x1_ - 3, ay0 - 0.2, ay0 + 9.0, z1_ - 3, z1_ - 2, ext, nm + '_head')
        if z0_: wbox(x0_ - 1, x1_ + 1, ay0 - 3.0, ay0 + 0.5, z0_ - 1.5, z0_, ext, nm + '_sill')
        for r_ in ((x0_, x0_ + 2, z0_, z1_), (x1_ - 2, x1_, z0_, z1_), (x0_ + 2, x1_ - 2, z1_ - 2, z1_)) + (((x0_ + 2, x1_ - 2, z0_, z0_ + 2),) if z0_ else ()):
            wbox(r_[0], r_[1], ay0 - 1.5, ay0 + 0.5, r_[2], r_[3], fr, nm + '_frame')
        wbox(x0_ + 2, x1_ - 2, ay0 - 0.9, ay0 - 0.6, (z0_ + 2) if z0_ else 0.0, z1_ - 2, gl, nm + '_glass')
    for k in range(18):                                               # stair, 18 risers to the slab top, rising plan north
        z_ = (k + 1) * 132.0 / 18.0; y_ = ay0 - 10 + k * 7.4
        wbox(ax1, ax1 + 40.0, y_, y_ + 11.0, z_ - 1.5, z_, ext, 'anc_step')
        wbox(ax1 + 0.5, ax1 + 39.5, y_ + 0.5, y_ + 7.9, -6.0, z_ - 1.5, ext, 'anc_stair_mass')   # solid stucco under the treads (R6: floating louvers)
        wbox(ax1 + 38.0, ax1 + 40.0, y_, y_ + 7.4, z_ + 34.0, z_ + 36.0, steel, 'anc_rail')
    wbox(ax1, ax1 + 40.0, ay0 - 10, ay0 + 120, -6.0, 6.0, material('ST-05'), 'anc_stair_base')
    for k in range(30):
        y_ = ay0 - 6 + k * 4.4; z_ = max(0.0, (y_ - ay0 + 10) / 7.4 * 132.0 / 18.0)
        if z_ > 128.0: break
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
        po.location = ((x0 + x1) / 2 * IN, (RD + 7.0) * IN, (z0 + z1) / 2 * IN); po.rotation_euler = (math.radians(-90), 0, 0)   # facing into the room
    if not any(o.type == 'LIGHT' and o.data.type == 'SUN' for o in bpy.data.objects):
        sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 10.0; sun_d.color = (1.0, 0.96, 0.9)
        sun_o = bpy.data.objects.new('sun', sun_d); bpy.context.collection.objects.link(sun_o)


STAGES['living'] = stage_living


# ======================================================================================================================
# Decor, owner 11.11.26: paintings with picture lights, the kitchen dining set and its oval glass-rod chandelier, the piano
# end's glass-rod flush mount, the dark bronze metal family. Paintings are our own (render/art_gen.py), after the owner's
# references for palette and mood.
# ======================================================================================================================
_FACE = {'-y': ((1, 0), (0, -1), 0.0), '+x': ((0, 1), (1, 0), 90.0), '+y': ((-1, 0), (0, 1), 180.0), '-x': ((0, -1), (-1, 0), -90.0)}


def rail_oak():
    MATS.setdefault('OAK-RAIL', {'hex': '#C2A47F', 'rough': 0.35, 'kind': 'wood', 'texture': 'oak_veneer_01', 'tint': [1.205, 1.30, 1.46]})
    return material('OAK-RAIL')                                           # stained to the WD-01 floor


def shaker_door_x(xf, y0, y1, z0, z1, mat, k=1.375, rec=0.25, name='cab_door'):
    """A slim shaker door facing -X with its face at xf (the kitchen's: a 1-3/8 in. frame, the panel 1/4 in. back), built as
    stiles full height and rails between them so no two pieces share a face."""
    f0, f1 = xf - 0.02, xf + 0.75
    wbox(f0, f1, y0, y0 + k, z0, z1, mat, name + '_stile', soft=0.05); wbox(f0, f1, y1 - k, y1, z0, z1, mat, name + '_stile', soft=0.05)
    wbox(f0, f1, y0 + k, y1 - k, z0, z0 + k, mat, name + '_rail', soft=0.05); wbox(f0, f1, y0 + k, y1 - k, z1 - k, z1, mat, name + '_rail', soft=0.05)
    wbox(f0 + rec, f1 - 0.01, y0 + k, y1 - k, z0 + k, z1 - k, mat, name + '_panel')


def bronze_mat():
    MATS.setdefault('METAL-BRONZE-DK', {'hex': '#3A3029', 'rough': 0.38, 'kind': 'metal'})   # warm dark bronze, satin
    return material('METAL-BRONZE-DK')


def _tn_box(cx, cy, facing, t0, t1, n0, n1, z0, z1, mat, nm, soft=0.0):
    """A box in a wall's frame: t along the wall (to the viewer's right), n out from the face at (cx, cy)."""
    (tx, ty), (nx, ny), _ = _FACE[facing]
    xs = [cx + tx * t + nx * n for t in (t0, t1) for n in (n0, n1)]; ys = [cy + ty * t + ny * n for t in (t0, t1) for n in (n0, n1)]
    return wbox(min(xs), max(xs), min(ys), max(ys), z0, z1, mat, nm, soft=soft)


def art_material(key):
    m = bpy.data.materials.get('ART-' + key)
    if m: return m
    m = bpy.data.materials.new('ART-' + key); m.use_nodes = True; N_ = m.node_tree.nodes; L_ = m.node_tree.links
    bs = N_['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.42
    ic = N_.new('ShaderNodeTexImage'); ic.image = bpy.data.images.load(os.path.join(HERE, 'art', key + '_col.png'))
    ih = N_.new('ShaderNodeTexImage'); ih.image = bpy.data.images.load(os.path.join(HERE, 'art', key + '_h.png')); ih.image.colorspace_settings.name = 'Non-Color'
    bp = N_.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.55; bp.inputs['Distance'].default_value = 0.004
    L_.new(ic.outputs['Color'], bs.inputs['Base Color']); L_.new(ih.outputs['Color'], bp.inputs['Height']); L_.new(bp.outputs['Normal'], bs.inputs['Normal'])
    return m


def painting(key, cx, cy, zc, w, h, facing, frame='oak', depth=1.5, light=True, light_w=None, name='art'):
    """A stretched canvas `w` x `h` centred at (cx, cy) on a wall face, its centre at height zc, facing the room ('+x' etc.);
    a floater frame (oak, walnut, black, brass or None) with a 3/8 in. shadow gap; a brass picture light over it."""
    (tx, ty), (nx, ny), zr = _FACE[facing]
    MATS.setdefault('OAK-FRAME', {'hex': '#B48A5A', 'rough': 0.45, 'kind': 'wood', 'texture': 'oak_veneer_01', 'tint': [1.1, 1.15, 1.25]})
    MATS.setdefault('WALNUT-FRAME', {'hex': '#5A3A26', 'rough': 0.4, 'kind': 'wood', 'texture': 'oak_veneer_01', 'tint': [0.5, 0.36, 0.27]})
    MATS.setdefault('FRAME-BLACK', {'hex': '#141414', 'rough': 0.45, 'kind': 'paint'})
    fm = {'oak': 'OAK-FRAME', 'walnut': 'WALNUT-FRAME', 'black': 'FRAME-BLACK', 'brass': 'METAL-BRASS'}.get(frame)
    _tn_box(cx, cy, facing, -w / 2, w / 2, 0.05, depth - 0.01, zc - h / 2, zc + h / 2, material('GAP'), name + '_stretcher')
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=((cx + nx * depth) * IN, (cy + ny * depth) * IN, zc * IN))
    pl = bpy.context.active_object; pl.name = name + '_canvas'; pl.scale = (w * IN, h * IN, 1.0)
    pl.rotation_euler = (_m.radians(90), 0.0, _m.radians(zr)); pl.data.materials.append(art_material(key))
    zt = zc + h / 2
    if fm:
        g, fw = 0.375, (0.375 if frame == 'black' else 0.5); fmat = material(fm); D = depth + 0.25
        _tn_box(cx, cy, facing, -w / 2 - g, w / 2 + g, 0.05, 0.45, zc - h / 2 - g, zc + h / 2 + g, material('GAP'), name + '_backer')
        for s_ in (-1, 1):
            _tn_box(cx, cy, facing, *sorted((s_ * (w / 2 + g), s_ * (w / 2 + g + fw))), 0.05, D, zc - h / 2 - g - fw, zc + h / 2 + g + fw, fmat, name + '_frame', soft=0.06)
            _tn_box(cx, cy, facing, -w / 2 - g, w / 2 + g, 0.05, D, *sorted((zc + s_ * (h / 2 + g), zc + s_ * (h / 2 + g + fw))), fmat, name + '_frame', soft=0.06)
        zt += g + fw
    if light: picture_light(cx, cy, zt + 3.0, light_w or min(36.0, max(14.0, round(w * 0.55))), facing, name=name + '_light')


def picture_light(cx, cy, z, L, facing, name='picture_light', watts=None):
    """A slim brass picture light: round backplate on the wall at z, an arm reaching 7 in. out and down, a 1-3/4 in. tubular
    hood L long with its lamp along the bottom aimed back at the canvas."""
    (tx, ty), (nx, ny), zr = _FACE[facing]; br = material(R('metal', 'METAL-BRASS'))
    _tn_box(cx, cy, facing, -1.6, 1.6, 0.0, 0.5, z - 1.6, z + 1.6, br, name + '_plate', soft=0.5)
    for k in range(6):                                                    # the arm, out and up to the hood
        t_ = k / 5; n_ = 0.5 + 6.3 * t_; z_ = z + 1.2 * _m.sin(_m.pi * t_ * 0.9)
        _tn_box(cx, cy, facing, -0.3, 0.3, n_ - 0.7, n_ + 0.7, z_ - 0.3, z_ + 0.3, br, name + '_arm', soft=0.2)
    hx, hy, hz = cx + nx * 7.3, cy + ny * 7.3, z + 1.6
    wcyl(hx, hy, hz, 0.9, L, 'x' if tx else 'y', br, name + '_hood')
    for s_ in (-1, 1): wcyl(hx + tx * s_ * L / 2, hy + ty * s_ * L / 2, hz, 0.95, 0.3, 'x' if tx else 'y', br, name + '_cap')
    MATS.setdefault('LED-STRIP', {'kind': 'lamp', 'emit': 2.2})
    _tn_box(hx, hy, facing, -L / 2 + 0.5, L / 2 - 0.5, -0.5, 0.2, hz - 0.95, hz - 0.85, material('LED-STRIP'), name + '_lens')
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = (L - 1.0) * IN; ld.size_y = 0.6 * IN
    ld.energy = watts if watts is not None else 0.32 * L; ld.color = (1.0, 0.84, 0.66)
    o_ = bpy.data.objects.new(name, ld); bpy.context.collection.objects.link(o_); o_.visible_glossy = False
    o_.location = (hx * IN, hy * IN, (hz - 1.0) * IN)
    d_ = Vector((-nx * _m.sin(_m.radians(28)), -ny * _m.sin(_m.radians(28)), -_m.cos(_m.radians(28))))
    o_.rotation_mode = 'QUATERNION'; o_.rotation_quaternion = d_.to_track_quat('-Z', 'Y')


def _loft(rings, mat, name, cap_top=True, cap_bot=True, smooth=True):
    """A closed surface through rings of world-inch points (each ring the same count), bottom to top."""
    bm_ = bmesh.new(); vs = [[bm_.verts.new((x_ * IN, y_ * IN, z_ * IN)) for x_, y_, z_ in r] for r in rings]; n = len(rings[0])
    for a_, b_ in zip(vs[:-1], vs[1:]):
        for k in range(n): bm_.faces.new((a_[k], a_[(k + 1) % n], b_[(k + 1) % n], b_[k]))
    if cap_bot: bm_.faces.new(vs[0][::-1])
    if cap_top: bm_.faces.new(vs[-1])
    me = bpy.data.meshes.new(name); bm_.to_mesh(me); bm_.free()
    if smooth:
        for p_ in me.polygons: p_.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def _squircle(X, Y, a, b, z, n=4.5, k=96, along='y'):
    pts = []
    for i in range(k):
        t = 2 * _m.pi * i / k; c_, s_ = _m.cos(t), _m.sin(t)
        u = a * _m.copysign(abs(c_) ** (2 / n), c_); v = b * _m.copysign(abs(s_) ** (2 / n), s_)
        pts.append((X + v, Y + u, z) if along == 'y' else (X + u, Y + v, z))
    return pts


def dining_table(X, Y, L=94.0, W=40.0, along='y', top_mat=None, name='dining'):
    """Owner's reference (11.11.26): a soft-rectangle stone top on a single tulip pedestal. Top 1-1/2 in. with a chamfered
    underside, 30 in. high; the pedestal an elongated tulip in dark bronze, its oval foot 46 x 24."""
    tm = top_mat or material('TRAV-01'); bz = bronze_mat()
    a, b = L / 2, W / 2
    rings = [_squircle(X, Y, a - 1.2, b - 1.2, 28.6, along=along), _squircle(X, Y, a, b, 29.35, along=along), _squircle(X, Y, a, b, 30.0, along=along)]
    _loft(rings, tm, name + '_top', smooth=False)
    prof = [(0.0, 23.0, 12.0), (0.6, 23.0, 12.0), (1.2, 22.0, 11.2), (2.4, 17.0, 8.6), (4.5, 11.5, 6.4), (8.0, 7.4, 4.6), (13.0, 5.2, 3.7),
            (18.0, 4.8, 3.5), (22.0, 6.4, 4.4), (25.5, 10.5, 6.2), (27.5, 16.0, 8.4), (28.6, 20.0, 9.6)]
    _loft([_squircle(X, Y, ra, rb, z_, n=2.4, k=72, along=along) for z_, ra, rb in prof], bz, name + '_pedestal')


def dining_chair(X, Y, facing, fab, name='dchair'):
    """Owner's reference (11.11.26): an upholstered seat and a curved pad back on a slim dark bronze frame, the back legs
    rising to carry the pad. (X, Y) the seat centre; facing the way the sitter faces ('+x', '-x', '+y', '-y')."""
    bz = bronze_mat(); sg = {'+x': 1, '-x': -1, '+y': 1, '-y': -1}[facing]; ax = facing in ('+x', '-x')
    def B(u0, u1, v0, v1, z0, z1, mat, nm, soft=0.0):        # u toward the table (front), v across
        if ax: return wbox(min(X + sg * u0, X + sg * u1), max(X + sg * u0, X + sg * u1), Y + v0, Y + v1, z0, z1, mat, nm, soft=soft)
        return wbox(X + v0, X + v1, min(Y + sg * u0, Y + sg * u1), max(Y + sg * u0, Y + sg * u1), z0, z1, mat, nm, soft=soft)
    for v in (-9.0, 8.4):
        B(7.6, 8.2, v, v + 0.6, 0.0, 15.2, bz, name + '_leg')                        # front legs
        B(-9.4, -8.8, v, v + 0.6, 0.0, 35.0, bz, name + '_post')                     # back legs up to the pad
        B(-9.0, 8.0, v, v + 0.6, 14.4, 15.2, bz, name + '_rail')
    B(-8.8, 7.8, -8.4, 8.4, 14.6, 15.1, bz, name + '_pan')
    B(-9.6, 9.6, -9.9, 9.9, 15.2, 19.2, fab, name + '_seat', soft=2.4)
    # the back: a pad curved round the sitter (a 24 in. radius in plan), 10 in. high, 2-3/4 in. thick, soft all round
    bm_ = bmesh.new(); n_ = 12; ring = []
    for i in range(n_ + 1):
        v = -10.4 + 20.8 * i / n_; du = v * v / 48.0
        pts = []
        for (u, z) in ((-9.0 + du, 26.0), (-11.75 + du, 26.0), (-11.75 + du, 36.2), (-9.0 + du, 36.2)):
            if ax: pts.append(bm_.verts.new(((X + sg * u) * IN, (Y + v) * IN, z * IN)))
            else: pts.append(bm_.verts.new(((X + v) * IN, (Y + sg * u) * IN, z * IN)))
        ring.append(pts)
    for r0, r1 in zip(ring[:-1], ring[1:]):
        for k in range(4):
            try: bm_.faces.new((r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]))
            except ValueError: pass
    bm_.faces.new(ring[0][::-1]); bm_.faces.new(ring[-1])
    bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces)
    me = bpy.data.meshes.new(name + '_back'); bm_.to_mesh(me); bm_.free()
    o = bpy.data.objects.new(name + '_back', me); bpy.context.collection.objects.link(o); o.data.materials.append(fab)
    bv = o.modifiers.new('round', 'BEVEL'); bv.width = 1.1 * IN; bv.segments = 4; bv.limit_method = 'ANGLE'
    ss = o.modifiers.new('smooth', 'SUBSURF'); ss.levels = ss.render_levels = 1
    for p_ in me.polygons: p_.use_smooth = True


def rod_glass():
    m = bpy.data.materials.get('GLASS-ROD')
    if m: return m
    m = bpy.data.materials.new('GLASS-ROD'); m.use_nodes = True; N_ = m.node_tree.nodes; L_ = m.node_tree.links
    out_ = N_['Material Output']; N_.remove(N_['Principled BSDF'])
    tr = N_.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (0.97, 0.94, 0.88, 1)
    gl = N_.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.02
    fr = N_.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.7
    mx = N_.new('ShaderNodeMixShader'); L_.new(fr.outputs['Fac'], mx.inputs['Fac']); L_.new(tr.outputs[0], mx.inputs[1]); L_.new(gl.outputs[0], mx.inputs[2])
    em = N_.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (1.0, 0.92, 0.8, 1); em.inputs['Strength'].default_value = 0.06
    ad = N_.new('ShaderNodeAddShader'); L_.new(mx.outputs[0], ad.inputs[0]); L_.new(em.outputs[0], ad.inputs[1]); L_.new(ad.outputs[0], out_.inputs['Surface'])
    bpy.context.scene.cycles.transparent_max_bounces = 64
    return m


def _rods(path, z0, z1, r, bm_):
    for (x_, y_) in path:
        ring0 = [bm_.verts.new(((x_ + r * _m.cos(2 * _m.pi * k / 8)) * IN, (y_ + r * _m.sin(2 * _m.pi * k / 8)) * IN, z0 * IN)) for k in range(8)]
        ring1 = [bm_.verts.new(((x_ + r * _m.cos(2 * _m.pi * k / 8)) * IN, (y_ + r * _m.sin(2 * _m.pi * k / 8)) * IN, z1 * IN)) for k in range(8)]
        for k in range(8): bm_.faces.new((ring0[k], ring0[(k + 1) % 8], ring1[(k + 1) % 8], ring1[k]))
        bm_.faces.new(ring0[::-1]); bm_.faces.new(ring1)


def _track(X, Y, a, b, step, along='y', n=4.0):
    """Points every `step` inches round a soft oval (squircle exponent n), semi-axes a (along) and b."""
    dense = _squircle(X, Y, a, b, 0.0, n=n, k=720, along=along); out = [dense[0][:2]]; acc = 0.0
    for p0, p1 in zip(dense, dense[1:] + dense[:1]):
        acc += _m.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if acc >= step: out.append(p1[:2]); acc = 0.0
    return out


def _ring_tube(path, z, r, mat, name):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r * IN; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(path) - 1)
    for i, (x_, y_) in enumerate(path): sp.points[i].co = (x_ * IN, y_ * IN, z * IN, 1)
    sp.use_cyclic_u = True; o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def oval_rod_chandelier(X, Y, zb, ceiling, L=60.0, W=30.0, along='y', name='dining_chand'):
    """Owner's reference (11.11.26): two staggered tiers of clear fluted glass rods round a soft oval brass frame, the lower
    tier smaller; brass to the house's aged brass. 60 x 30 for a 94 in. table, bottom at zb on two rods to a canopy."""
    br = material(R('metal', 'METAL-BRASS')); gm = rod_glass(); bm_ = bmesh.new()
    tiers = [(L / 2, W / 2, zb + 9.0, 11.0), (L / 2 - 7.0, W / 2 - 5.0, zb, 11.0)]          # (a, b, bottom, rod length)
    for (a, b, z0, h) in tiers:
        _rods(_track(X, Y, a, b, 1.15, along), z0, z0 + h, 0.42, bm_)
        for z_ in (z0 + h + 0.3, z0 - 0.2): _ring_tube(_track(X, Y, a, b, 2.0, along), z_, 0.35, br, name + '_ring')
        for k, p in enumerate(_track(X, Y, a - 3.0, b - 3.0, 9.0, along)):
            ld = bpy.data.lights.new(name, 'POINT'); ld.energy = 7.0; ld.shadow_soft_size = 0.7 * IN; ld.color = (1.0, 0.83, 0.62)
            o_ = bpy.data.objects.new(name + '_lamp', ld); bpy.context.collection.objects.link(o_); o_.location = (p[0] * IN, p[1] * IN, (z0 + h / 2) * IN)
    me = bpy.data.meshes.new(name + '_rods'); bm_.to_mesh(me); bm_.free()
    o = bpy.data.objects.new(name + '_rods', me); bpy.context.collection.objects.link(o); o.data.materials.append(gm); o.visible_shadow = False
    zt = tiers[0][2] + tiers[0][3] + 0.6
    for s_ in (-1, 1):                                                           # spokes and the two drop rods
        dx, dy = ((0, s_ * L / 4) if along == 'y' else (s_ * L / 4, 0))
        wbox_abs(min(X, X + dx) - 0.3 if dx else X - 0.3, max(X, X + dx) + 0.3 if dx else X + 0.3,
                 min(Y, Y + dy) - 0.3 if dy else Y - 0.3, max(Y, Y + dy) + 0.3 if dy else Y + 0.3, zt - 0.4, zt, br, name + '_spoke')
        wcyl(X + dx, Y + dy, (zt + ceiling) / 2, 0.3, ceiling - zt, 'z', br, name + '_rod')
    wbox_abs(X - (2.5 if along == 'y' else L / 4 + 2.5), X + (2.5 if along == 'y' else L / 4 + 2.5),
             Y - (L / 4 + 2.5 if along == 'y' else 2.5), Y + (L / 4 + 2.5 if along == 'y' else 2.5), ceiling - 1.0, ceiling - 0.02, br, name + '_canopy')


def rod_flush(X, Y, ceiling, D=22.0, H_=7.0, name='flush'):
    """Owner's reference (11.11.26, the piano end): a flush drum of clear glass rods between scalloped brass bands, a frosted
    glass diffuser below with a brass finial; in aged brass to match the house rather than the reference's nickel."""
    br = material(R('metal', 'METAL-BRASS')); gm = rod_glass(); r = D / 2
    MATS.setdefault('GLASS-FROST', {'hex': '#F2EFE8', 'rough': 0.6, 'kind': 'lamp', 'emit': 0.6})
    bm_ = bmesh.new(); n = int(2 * _m.pi * r / 0.95)
    _rods([(X + (r - 0.4) * _m.cos(2 * _m.pi * k / n), Y + (r - 0.4) * _m.sin(2 * _m.pi * k / n)) for k in range(n)], ceiling - H_ + 1.0, ceiling - 1.0, 0.42, bm_)
    me = bpy.data.meshes.new(name + '_rods'); bm_.to_mesh(me); bm_.free()
    o = bpy.data.objects.new(name + '_rods', me); bpy.context.collection.objects.link(o); o.data.materials.append(gm); o.visible_shadow = False
    for z_ in (ceiling - H_ + 0.6, ceiling - 0.8):
        _ring_tube([(X + (r - 0.2) * _m.cos(2 * _m.pi * k / 96) + 0.25 * _m.cos(2 * _m.pi * k / 96 * 1) * _m.cos(48 * 2 * _m.pi * k / 96),
                     Y + (r - 0.2) * _m.sin(2 * _m.pi * k / 96) + 0.25 * _m.sin(2 * _m.pi * k / 96) * _m.cos(48 * 2 * _m.pi * k / 96)) for k in range(96)],
                   z_, 0.55, br, name + '_band')
    wcyl(X, Y, ceiling - H_ + 0.5, r - 0.6, 0.4, 'z', material('GLASS-FROST'), name + '_diffuser')
    wcyl(X, Y, ceiling - 0.5, r - 0.5, 0.8, 'z', br, name + '_pan')
    wcyl(X, Y, ceiling - H_ + 0.05, 0.9, 0.7, 'z', br, name + '_finial')
    for k in range(4):
        ld = bpy.data.lights.new(name, 'POINT'); ld.energy = 14.0; ld.shadow_soft_size = 1.0 * IN; ld.color = (1.0, 0.83, 0.62)
        o_ = bpy.data.objects.new(name + '_lamp', ld); bpy.context.collection.objects.link(o_)
        o_.location = ((X + 4.5 * _m.cos(_m.pi * k / 2)) * IN, (Y + 4.5 * _m.sin(_m.pi * k / 2)) * IN, (ceiling - H_ / 2) * IN)


exec(open(os.path.join(HERE, 'house_stage.py')).read())   # the whole property (owner 11.11.26)
