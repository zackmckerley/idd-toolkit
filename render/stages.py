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
    wbox_abs(86.2, 268.0, ys - 6.0, -12.0, -2.0, 0.0, wd, 'south_floor')
    FW, FE, FS = 37.2, 247.0, -301.7       # the foyer: its tray (X 55.1..235.9) and the front wall the sconces sit on (plan RCP)
    wbox_abs(FW, FE, FS, ys - 6.0, -2.0, 0.0, material('TL-01'), 'foyer_floor')   # not R(): the room's floor role would give the living room's oak
    # west wall with door 12
    for y0_, y1_, z0_ in ((ys - 6.0, -122.0, 0.0), (-89.0, -6.0, 0.0), (-122.0, -89.0, 96.0)):
        wbox(86.2, 92.2, y0_, y1_, z0_, CH, wallm, 'se_wall_w')
    door_in_x_wall(92.2, 1, -122.0, -89.0, 96.0, trim, leafm)
    # closet 27's wall (its face toward the room is west) with its door; the landing's north wall closes the upper flight off
    for y0_, y1_, z0_ in ((-148.0, -88.0, 0.0), (-59.0, -6.0, 0.0), (-88.0, -59.0, 96.0)):
        wbox(230.7, 236.7, y0_, y1_, z0_, CH, wallm, 'se_wall_closet')
    door_in_x_wall(230.7, -1, -88.0, -59.0, 96.0, trim, leafm)
    wbox(236.7, 262.0, -148.0, -142.0, 51.2, CH, wallm, 'se_wall_landing')
    wbox(262.0, 268.0, ys - 6.0, -142.0, 0.0, CH, wallm, 'se_wall_stair_e')
    # south wall with the entry arch; the foyer beyond it
    AX, AW, AP = 103.0, 52.3, 100.75
    asp = AP - AW * 0.62 + _m.sqrt((AW * 0.62) ** 2 - (AW / 2) ** 2)
    for x0_, x1_, z0_ in ((86.2, AX, 0.0), (AX + AW, 262.0, 0.0), (AX, AX + AW, AP + 1.0)):
        wbox(x0_, x1_, ys - 6.0, ys, z0_, CH, wallm, 'se_wall_s')
    arch_xz(AX, AW, asp, AP + 1.0, ys - 6.0, ys, ys, ys + 0.75, wallm, trim)
    wbox(FW - 6.0, FW, FS, ys - 6.0, 0.0, CH, wallm, 'foyer_wall_w'); wbox(FE, FE + 6.0, FS, ys - 6.0, 0.0, CH, wallm, 'foyer_wall_e')
    wbox(FW, 86.2, ys - 6.0, ys, 0.0, CH, wallm, 'foyer_wall_n'); wbox(262.0, FE, ys - 6.0, ys, 0.0, CH, wallm, 'foyer_wall_n')
    # the front wall: the entry pair centred between the plan's sconces (X 64.5 and 154.5), 6'-0" x 8'-0", oak, with its casing
    DX0, DX1, DH = 109.5 - 36.0, 109.5 + 36.0, 96.0
    for x0_, x1_, z0_ in ((FW - 6.0, DX0, 0.0), (DX1, FE + 6.0, 0.0), (DX0, DX1, DH)):
        wbox(x0_, x1_, FS - 6.0, FS, z0_, CH, wallm, 'foyer_wall_s')
    oak = material('WD-02')
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
    # the lower flight: oak treads stepping up east to the landing, a raking half wall on its north side, its top 36 in. over
    # the nosings, a wood cap
    RS, n_, x_b, x_t = 7.3125, 7, 169.3, 235.3
    run = (x_t - x_b) / (n_ - 1)
    for k in range(1, n_):
        x0_ = x_b + (k - 1) * run
        wbox(x0_, min(x0_ + run + 0.5, x_t), ys, -153.0, 0.0, k * RS - 1.0, wd, 'stair_step')   # the tread sits on it: no shared top
        wbox(x0_ - 0.75, x0_ + run, ys, -153.0, k * RS - 1.0, k * RS, wd, 'tread')
    wbox(x_t, 262.0, ys, -148.0, 0.0, n_ * RS, wd, 'landing')
    hw = [(165.9, 0.0), (235.9, 0.0), (235.9, n_ * RS + 36.0), (x_b, RS + 36.0), (165.9, RS + 36.0)]
    wprism_xz(hw, -153.0, -148.0, wallm, 'half_wall')
    wprism_xz([(165.4, RS + 36.0), (x_b, RS + 36.0), (236.4, n_ * RS + 36.0), (236.4, n_ * RS + 37.25), (x_b, RS + 37.25), (165.4, RS + 37.25)],
              -153.5, -147.5, material('WD-SHELF'), 'half_wall_cap')
    # base: stopped at every casing, none on the stair side
    B_ = lambda x0_, x1_, y0_, y1_: wbox(x0_, x1_, y0_, y1_, 0.0, 8.5, trim, 'se_base', soft=0.15)
    B_(92.2, 92.8, ys, -125.5); B_(92.2, 92.8, -85.5, 0.6)   # round the jamb return to the living room's base
    B_(230.1, 230.7, -148.0, -91.5); B_(230.1, 230.7, -55.5, 0.6)
    B_(92.8, AX - 5.0, ys, ys + 0.6); B_(AX + AW + 5.0, 165.9, ys, ys + 0.6)
    B_(165.9, 230.1, -148.0, -147.4)
    # lights, from the plan's RCP (build_rcp.for_items, converted as above): in the south end a centre fixture at (161.3, -74.8),
    # wall washers along the west wall at X 113 and two cans by the stair and arch at Y -172; a sconce on the closet wall at
    # Y -119.5; in the foyer a pendant in the tray at (109.7, -244.5) and sconces each side of the entry at X 64.5 and 154.5
    MATS.setdefault('TRIM-RING', {'hex': '#F4F3EF', 'rough': 0.3, 'kind': 'plastic'}); MATS.setdefault('LENS', {'kind': 'lamp', 'emit': 6.0})
    MATS.setdefault('SHADE', {'kind': 'lamp', 'emit': 3.0})
    can = ceiling_can
    for X_, Y_ in ((113.1, -29.0), (113.1, -60.0), (113.1, -151.0), (113.1, -177.0), (129.6, -172.1), (199.1, -172.1)):
        can(X_, Y_, CH)
    for X_, Y_ in ((241.8, -236.5), (48.7, -219.0), (48.7, -261.6)):
        can(X_, Y_, CH, 10.0)
    def drum(X_, Y_, zb, d, h, watts, rod_top):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=d / 2 * IN, depth=h * IN, location=(X_ * IN, Y_ * IN, (zb + h / 2) * IN))
        o = bpy.context.active_object; o.name = 'drum_shade'; o.data.materials.append(material('SHADE'))
        for pg in o.data.polygons: pg.use_smooth = True
        if rod_top > zb + h: wbox(X_ - 0.25, X_ + 0.25, Y_ - 0.25, Y_ + 0.25, zb + h, rod_top, material('STEEL-SS'), 'pendant_rod')
        wpoint(X_, Y_, zb + h / 2, watts, radius=d / 3, color=(1.0, 0.86, 0.68))
    drum(161.3, -74.8, CH - 7.0, 16.0, 6.0, 45.0, CH)                 # semi-flush: 10'-8" is too low to hang a drum
    drum(109.7, -244.5, 92.0, 18.0, 12.0, 60.0, CH + 6.0)             # the foyer pendant, in its tray
    def sconce_y(X_, yf, side, z_=66.0, watts=12.0):   # on a wall whose face is Y = yf, the room on `side`
        y0_, y1_ = sorted((yf, yf + side * 1.0)); wbox(X_ - 2.5, X_ + 2.5, y0_, y1_, z_ - 6.0, z_ + 6.0, material('STEEL-SS'), 'sconce_plate', soft=0.3)
        y0_, y1_ = sorted((yf + side * 1.0, yf + side * 5.5)); wbox(X_ - 2.25, X_ + 2.25, y0_, y1_, z_ - 3.0, z_ + 7.0, material('SHADE'), 'sconce_shade', soft=1.0)
        wpoint(X_, yf + side * 3.5, z_ + 2.0, watts, radius=1.5, color=(1.0, 0.86, 0.68))
    sconce_y(64.5, FS, 1); sconce_y(154.5, FS, 1)
    # the closet-wall sconce: round backplate and a 5 in. opal cylinder, lit (a small white box read as an intercom, review 11.10.26)
    xf_ = 230.7
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.75 * IN, depth=0.75 * IN, location=((xf_ - 0.375) * IN, -119.5 * IN, 66.0 * IN), rotation=(0, _m.pi / 2, 0))
    o_ = bpy.context.active_object; o_.name = 'sconce_plate'; o_.data.materials.append(material('STEEL-SS'))
    wbox(xf_ - 3.0, xf_ - 0.75, -119.9, -119.1, 65.6, 66.4, material('STEEL-SS'), 'sconce_arm')
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.5 * IN, depth=10.0 * IN, location=((xf_ - 5.25) * IN, -119.5 * IN, 67.0 * IN))
    o_ = bpy.context.active_object; o_.name = 'sconce_shade'; o_.data.materials.append(material('SHADE'))
    for pg in o_.data.polygons: pg.use_smooth = True
    wpoint(xf_ - 5.25, -119.5, 67.0, 25.0, radius=1.5)
    wbox(xf_ - 5.5, xf_ - 1.0, -121.75, -117.25, 63.0, 73.0, material('SHADE'), 'sconce_shade', soft=1.0); wpoint(xf_ - 3.5, -119.5, 68.0, 12.0, radius=1.5)

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
    # ---- the breast, one plaster plane floor to the crown, with the 4 in. TV niche and the firebox opening cut out of its front
    yc_ = Yw(RD / 2); h_ = G['FB_W'] / 2; tw_ = G['TV_W']; tb_ = G['TV_B']; th_ = G['TV_H']
    nb, nt, ny0, ny1 = tb_ - 2, tb_ + th_ + 2, yc_ - tw_ / 2 - 2, yc_ + tw_ / 2 + 2
    wbox(BF + 4.0, E, Yw(B1), Yw(B0), 0.0, G['CROWN_B'], wallm, 'breast')                       # the core behind the niche
    wbox(BF, BF + 4.0, Yw(B1), ny0, 0.0, G['CROWN_B'], wallm, 'breast_face')                    # the front 4 in., round the niche
    wbox(BF, BF + 4.0, ny1, Yw(B0), 0.0, G['CROWN_B'], wallm, 'breast_face')
    wbox(BF, BF + 4.0, ny0, ny1, nt, G['CROWN_B'], wallm, 'breast_face')
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
    wbox(BF - 20.0, BF, yc - 33.0, yc + 33.0, -0.02, 0.03, st1, 'hearth')          # flush ST-01 hearth 5'-6" x 1'-8"
    # TV: the art-mode set nearly flush in a 4 in. niche 2 in. larger each way
    tb = G['TV_B']; tw = G['TV_W']; th = G['TV_H']
    # the set sits nearly flush: its face 1/2 in. behind the breast face, the niche's 2 in. margin dark round it
    wbox(BF + 1.6, BF + 4.0, yc - tw / 2 - 2, yc + tw / 2 + 2, tb - 2, tb + th + 2, wallm, 'niche_back')   # painted returns in shadow, not a void
    wbox(BF + 0.5, BF + 1.6, yc - tw / 2, yc + tw / 2, tb, tb + th, material('TV-BLACK'), 'tv')
    wbox(BF + 0.3, BF + 0.45, yc - tw / 2 + 0.6, yc + tw / 2 - 0.6, tb + 0.6, tb + th - 0.6, material('PLATE-WHITE'), 'tv_mat')
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
    wbox(BF + 0.25, BF + 0.35, yc - tw / 2 + 4.5, yc + tw / 2 - 4.5, tb + 4.5, tb + th - 4.5, art_, 'tv_art')
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
    crown_run(IF, Yw(RD), Yw(B1), top); crown_run(BF, Yw(B1), Yw(B0), top); crown_run(IF, Yw(B0), Yw(0.0), top)
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
    wbox(4.0, E, RD - G['BAND_W'], RD, G['BAND'], Hh + 0.01, material(R('ceiling', 'PT-01')), 'band')   # wall to wall: it stopped at the gallery line with its end showing
    MATS.setdefault('POCKET', {'hex': '#8A857E', 'rough': 0.8, 'kind': 'paint'})   # the slot's inside in shadow, not a black bar
    wbox(PK0, PK1, RD - 7.0, RD - 2.0, G['BAND'] - 0.01, Hh, material('POCKET'), 'drapery_pocket')
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
    wbox(0.0, E, -202.7, -6.0, G['SOFFIT'], G['FF2'] - 1.5, pt1, 'gallery_slab_s')   # its underside is the south end's 10'-8" ceiling
    wbox(0.0, G['GFW'] - 3, 0.0, RD, G['FF2'], G['FF2'] + 0.5, material(R('floor', 'WD-01')), 'floor2_w')
    wbox(0.0, E, -60.0, -3.0, G['FF2'], G['FF2'] + 0.5, material(R('floor', 'WD-01')), 'floor2_s')
    wbox(G['GFW'] - 0.6, G['GFW'], 0.0, RD, G['SOFFIT'], G['FF2'], trim, 'fascia_w')
    wbox(G['GFW'], E, 0.0, 0.25, G['SOFFIT'], G['FF2'], trim, 'fascia_s')   # proud of the wall below it: no shared face
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
        for z0, z1 in ((G['FF2'] + 2.0, G['FF2'] + 3.5), (G['GT'] - 2.5, G['GT'])):
            if axis == 'y': wbox(c - 0.75, c + 0.75, a0, a1, z0, z1, steel, 'guard_rail')
            else: wbox(a0, a1, c - 0.75, c + 0.75, z0, z1, steel, 'guard_rail')
        posts = [a0] + [a0 + k * 72.0 for k in range(1, int((a1 - a0) / 72.0) + 1)] + [a1 - 2.0]
        for p in posts:
            if axis == 'y': wbox(c - 1.0, c + 1.0, p, p + 2.0, G['FF2'], G['GT'], steel, 'guard_post')
            else: wbox(p, p + 2.0, c - 1.0, c + 1.0, G['FF2'], G['GT'], steel, 'guard_post')
    guard('y', 0.0, RD - 1.0, G['GFW'] - 2.0); guard('x', G['GFW'], E - 1.0, -2.0)
    wbox(0.0, E, -60.0, -54.0, G['FF2'], Hh, wallm, 'hall_wall_s')
    wbox(0.0, E, -60.0, -11.0, 268.0, 272.0, material(R('ceiling', 'PT-01')), 'hall_ceiling')   # floor 2 hall, 9'-6" (FOR)
    wbox(0.0, 4.0, -60.0, RD, G['FF2'], Hh, wallm, 'hall_wall_w_face')
    wbox(E - 4.0, E, -60.0, 0.0, G['FF2'], Hh, wallm, 'hall_wall_e_face')   # the hall's east end (R6: it was open to the sky)
    # ---- staging (captioned): a sofa with its back on the west gallery line facing the TV, a rug and a coffee table
    fab = material('FAB-SOFA'); rug = material('FAB-RUG'); wood = material('WOOD-FURN')
    cy = yc
    wbox(110.0, 232.0, cy - 54, cy + 54, 0.0, 0.4, rug, 'rug', soft=0.15)
    sx0 = G['GFW'] + 1.0
    # a tailored 8 ft sofa: recessed dark plinth, track arms, two seat and two back cushions with real gaps, two pillows.
    # Mid oatmeal, not white: a white sofa against white walls reads as a blob (owner review of the first preview, 11.10.26)
    wbox(sx0 + 2.0, sx0 + 36.0, cy - 46.0, cy + 46.0, 0.0, 4.0, material('SOFA-PLINTH'), 'sofa_plinth')
    wbox(sx0, sx0 + 38, cy - 48, cy + 48, 4.0, 14.0, fab, 'sofa_base', soft=1.5)
    wbox(sx0, sx0 + 9, cy - 47.5, cy + 47.5, 14.0, 30.0, fab, 'sofa_back', soft=2.5)
    for sy in (-1, 1):
        a0_, a1_ = (cy + 40.5, cy + 47.75) if sy > 0 else (cy - 47.75, cy - 40.5)
        wbox(sx0 + 0.5, sx0 + 37.5, a0_, a1_, 14.0, 25.0, fab, 'sofa_arm', soft=2.5)
    for k in range(2):
        y0_, y1_ = cy - 40.25 + k * 40.5, cy - 40.25 + (k + 1) * 40.5 - 0.5
        wbox(sx0 + 9.25, sx0 + 37.0, y0_, y1_, 14.0, 19.5, fab, 'seat_cushion', soft=2.2)
        wbox(sx0 + 9.25, sx0 + 15.5, y0_ + 0.25, y1_ - 0.25, 19.5, 32.5, fab, 'back_cushion', soft=2.8)
    for y_, pm in ((cy - 39.5, 'FAB-PILLOW-A'), (cy + 21.5, 'FAB-PILLOW-B')):
        wbox(sx0 + 15.0, sx0 + 21.0, y_, y_ + 18.0, 19.5, 36.0, material(pm), 'pillow', soft=4.5)
    wbox(160.0, 196.0, cy - 22, cy + 22, 0.0, 15.0, wood, 'coffee_table', soft=0.6)
    import_model('wooden_bowl_01', 2.5, 176.0, cy - 6, 15.0, 0); import_model('ceramic_vase_01', 8.0, 184.0, cy + 10, 15.0, 0)
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
