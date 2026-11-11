"""The whole property in one model (owner 11.11.26: "get the whole property modelled in a really amazing way, interior and
exterior; incorporate the landscape and civil plans"). exec'd by stages.py; STAGES['house'].

  shell      walls per floor from FOR REV 1 (render/house_geom.json, house_geom.py), banded at every sill and head so each
             opening is a real hole; outside faces stucco, inside faces PT-02; floor finishes and ceilings per room
  openings   FOR's windows and doors by A-600 type: dark bronze frames, clear glass, mullions per panel count; interior
             doorways cased
  roof       A-203: 6:12 standing-seam metal hips from a 23'-0" heel to the low-slope field at 26'-0-1/2", 18 in. eaves with a
             white soffit, fascia and a 5 in. box gutter; floor 1 roof decks and the two front balconies with planters and
             picket railings (A-202 P-WALL / P-RAILING)
  site       A-100 (lot 50 x 124 ft, setbacks, pool, deck, driveway and car gate, entry walk, planters, ancillary structure,
             fences), C1.0 (grades: FFE 11.70, yard about 11.2, street edge about 10.5 NGVD), L-1/L-2 (the plant schedule:
             crape myrtle, privet, Simpson's stopper, relocated and existing trees, clusia hedges, mondo grass, sod, turf),
             Thomas Avenue (sidewalk, parkway, 22 ft asphalt), the neighbours as massing
Detailed rooms (living, kitchen, master suite) load over the shell with --context; this stage is the walk-through's base."""

_HG = {}


def hg():
    if not _HG: _HG.update(json.load(open(os.path.join(HERE, 'house_geom.json'))))
    return _HG


def _inside(pt, ring):
    x, y = pt; n = len(ring); c = False
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1: c = not c
    return c


def stone_zone(cx, cy, cz, nx, ny):
    """FOR's stone veneer (E-7, A-301/A-302): the whole ground floor of the street front, and the living room bay (its two
    outside faces on the ground floor, and its glazed rear face to the eave)."""
    if cz < 150.0 and ny < -0.7 and cy < -270.0: return True
    if cz < 150.0 and cx > 88.0 and -70.0 < cy < 212.0 and (nx > 0.7 or ny > 0.7): return True
    if ny > 0.7 and cx > 88.0 and 188.0 < cy < 212.0: return True
    return False


def prism(ext, holes, z0, z1, mats, name, enc=None, smooth=False):
    """Extrude a plan polygon (inches, holes allowed) from z0 to z1. mats: dict side_in, side_out, top, bottom (materials).
    A side face is 'out' when the point 3 in. off it along its normal is outside `enc` (a ring), or always when enc is None."""
    bm_ = bmesh.new(); edges = []
    for ring in [ext] + list(holes or []):
        pts = ring[:-1] if len(ring) > 2 and ring[0] == ring[-1] else ring
        if len(pts) < 3: continue
        vs = [bm_.verts.new((x * IN, y * IN, z0 * IN)) for x, y in pts]
        for i in range(len(vs)):
            try: edges.append(bm_.edges.new((vs[i], vs[(i + 1) % len(vs)])))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm_, verts=bm_.verts, dist=0.001)
    edges = list(bm_.edges)
    r_ = bmesh.ops.triangle_fill(bm_, use_beauty=True, use_dissolve=True, edges=edges, normal=(0, 0, 1))
    faces = [f for f in r_['geom'] if isinstance(f, bmesh.types.BMFace)]
    if not faces: bm_.free(); return None
    ex = bmesh.ops.extrude_face_region(bm_, geom=faces)
    bmesh.ops.translate(bm_, vec=(0, 0, (z1 - z0) * IN), verts=[v for v in ex['geom'] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.delete(bm_, geom=[e for e in bm_.edges if not e.link_faces], context='EDGES')
    bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces)
    keys = ['side_in', 'side_out', 'top', 'bottom', 'side_stone']; slots = {}
    me = bpy.data.meshes.new(name)
    for k in keys:
        m = mats.get(k) or mats.get('side_out') or mats.get('side_in')
        if m.name not in slots: slots[m.name] = len(slots); me.materials.append(m)
    for f in bm_.faces:
        n = f.normal
        if n.z > 0.9: k = 'top'
        elif n.z < -0.9: k = 'bottom'
        else:
            c = f.calc_center_median(); p_ = ((c.x + n.x * 3 * IN) / IN, (c.y + n.y * 3 * IN) / IN)
            k = 'side_out' if (enc is None or not _inside(p_, enc)) else 'side_in'
            if k == 'side_out' and mats.get('side_stone') is not None and stone_zone(c.x / IN, c.y / IN, c.z / IN, n.x, n.y): k = 'side_stone'
        m = mats.get(k) or mats.get('side_out') or mats.get('side_in'); f.material_index = slots[m.name]
        f.smooth = smooth
    bm_.to_mesh(me); bm_.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    return o


def stone_veneer():
    """Light limestone ashlar (E-7): 24 x 12 in. coursed blocks, thin pale joints, each block its own tone, a honed face."""
    m = bpy.data.materials.get('STONE-VENEER')
    if m: return m
    m = bpy.data.materials.new('STONE-VENEER'); m.use_nodes = True; N_ = m.node_tree.nodes; L_ = m.node_tree.links
    bs = N_['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.75
    tc = N_.new('ShaderNodeTexCoord'); sep = N_.new('ShaderNodeSeparateXYZ'); L_.new(tc.outputs['Object'], sep.inputs[0])
    nm = N_.new('ShaderNodeNewGeometry'); sn = N_.new('ShaderNodeSeparateXYZ'); L_.new(nm.outputs['Normal'], sn.inputs[0])
    ab = N_.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L_.new(sn.outputs['X'], ab.inputs[0])
    mx = N_.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; L_.new(ab.outputs[0], mx.inputs['Factor']); L_.new(sep.outputs['X'], mx.inputs['A']); L_.new(sep.outputs['Y'], mx.inputs['B'])
    cmb = N_.new('ShaderNodeCombineXYZ'); L_.new(mx.outputs['Result'], cmb.inputs['X']); L_.new(sep.outputs['Z'], cmb.inputs['Y'])
    br = N_.new('ShaderNodeTexBrick'); br.offset = 0.5; br.inputs['Scale'].default_value = 1.0
    br.inputs['Brick Width'].default_value = 24 * IN; br.inputs['Row Height'].default_value = 12 * IN; br.inputs['Mortar Size'].default_value = 0.3 * IN
    br.inputs['Color1'].default_value = (0.66, 0.60, 0.50, 1); br.inputs['Color2'].default_value = (0.74, 0.68, 0.57, 1); br.inputs['Mortar'].default_value = (0.58, 0.55, 0.50, 1)
    br.inputs['Bias'].default_value = 0.0
    L_.new(cmb.outputs[0], br.inputs['Vector'])
    no = N_.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 40.0; L_.new(cmb.outputs[0], no.inputs['Vector'])
    mc = N_.new('ShaderNodeMix'); mc.data_type = 'RGBA'; mc.blend_type = 'MULTIPLY'; mc.inputs['Factor'].default_value = 0.18
    L_.new(br.outputs['Color'], mc.inputs['A']); L_.new(no.outputs['Color'], mc.inputs['B']); L_.new(mc.outputs['Result'], bs.inputs['Base Color'])
    bp = N_.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.004
    L_.new(br.outputs['Fac'], bp.inputs['Height']); L_.new(bp.outputs['Normal'], bs.inputs['Normal'])
    return m


def roof_metal():
    """Standing-seam metal, light and high-albedo (A-203): 18 in. pans, a raised seam running down each slope (the seams follow
    whichever plan axis the face does not face)."""
    m = bpy.data.materials.get('ROOF-SEAM')
    if m: return m
    m = bpy.data.materials.new('ROOF-SEAM'); m.use_nodes = True; N_ = m.node_tree.nodes; L_ = m.node_tree.links
    bs = N_['Principled BSDF']; bs.inputs['Base Color'].default_value = (0.40, 0.42, 0.43, 1); bs.inputs['Metallic'].default_value = 0.6
    bs.inputs['Roughness'].default_value = 0.42
    tc = N_.new('ShaderNodeTexCoord'); sep = N_.new('ShaderNodeSeparateXYZ'); L_.new(tc.outputs['Object'], sep.inputs[0])
    nm = N_.new('ShaderNodeNewGeometry'); sn = N_.new('ShaderNodeSeparateXYZ'); L_.new(nm.outputs['Normal'], sn.inputs[0])
    ax_ = N_.new('ShaderNodeMath'); ax_.operation = 'ABSOLUTE'; L_.new(sn.outputs['X'], ax_.inputs[0])
    ay_ = N_.new('ShaderNodeMath'); ay_.operation = 'ABSOLUTE'; L_.new(sn.outputs['Y'], ay_.inputs[0])
    gt = N_.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; L_.new(ax_.outputs[0], gt.inputs[0]); L_.new(ay_.outputs[0], gt.inputs[1])
    mx = N_.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; L_.new(gt.outputs[0], mx.inputs['Factor']); L_.new(sep.outputs['X'], mx.inputs['A']); L_.new(sep.outputs['Y'], mx.inputs['B'])
    dv = N_.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; L_.new(mx.outputs['Result'], dv.inputs[0]); dv.inputs[1].default_value = 18 * IN
    fr = N_.new('ShaderNodeMath'); fr.operation = 'FRACT'; L_.new(dv.outputs[0], fr.inputs[0])
    rg = N_.new('ShaderNodeMapRange'); rg.inputs['From Min'].default_value = 0.0; rg.inputs['From Max'].default_value = 0.04
    rg.inputs['To Min'].default_value = 1.0; rg.inputs['To Max'].default_value = 0.0; L_.new(fr.outputs[0], rg.inputs['Value'])
    bp = N_.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.8; bp.inputs['Distance'].default_value = 0.01
    L_.new(rg.outputs['Result'], bp.inputs['Height']); L_.new(bp.outputs['Normal'], bs.inputs['Normal'])
    return m


def house_materials():
    MATS.setdefault('STUCCO-HOUSE', {'hex': '#F1EEE7', 'rough': 0.85, 'kind': 'stone', 'texture': 'white_stucco'})
    MATS.setdefault('ROOF-METAL', {'hex': '#C7CACB', 'rough': 0.32, 'kind': 'metal'})          # light, high-albedo (A-203 note)
    MATS.setdefault('SOFFIT-WHITE', {'hex': '#F3F1EC', 'rough': 0.6, 'kind': 'paint'})
    MATS.setdefault('LAWN', {'hex': '#5E7A3A', 'rough': 0.95, 'kind': 'stone', 'texture': 'leafy_grass', 'tint': [0.8, 1.0, 0.62]})
    MATS.setdefault('TURF', {'hex': '#5F8240', 'rough': 0.9, 'kind': 'stone', 'texture': 'leafy_grass', 'tint': [0.95, 1.05, 0.9]})
    MATS.setdefault('ASPHALT', {'hex': '#3C3C3B', 'rough': 0.9, 'kind': 'stone', 'texture': 'asphalt_02'})
    MATS.setdefault('SIDEWALK', {'hex': '#BDB8AE', 'rough': 0.85, 'kind': 'stone', 'texture': 'concrete_floor'})
    MATS.setdefault('DRIVE-PAVER', {'hex': '#D9D0C0', 'rough': 0.8, 'kind': 'stone', 'texture': 'concrete_pavement_02'})
    MATS.setdefault('MULCH', {'hex': '#5A4232', 'rough': 0.95, 'kind': 'stone', 'texture': 'forrest_ground_01'})
    MATS.setdefault('PLANTING-LOW', {'hex': '#2F4A26', 'rough': 0.9, 'kind': 'paint'})
    MATS.setdefault('CURB', {'hex': '#C9C4BA', 'rough': 0.8, 'kind': 'stone', 'texture': 'brushed_concrete'})
    MATS.setdefault('NEIGHBOR', {'hex': '#D6CFC2', 'rough': 0.9, 'kind': 'stone', 'texture': 'white_stucco', 'tint': [0.86, 0.83, 0.78]})
    MATS.setdefault('NEIGHBOR-ROOF', {'hex': '#5E5C59', 'rough': 0.7, 'kind': 'paint'})
    MATS.setdefault('ALU-BLK', {'hex': '#1E1E1E', 'rough': 0.4, 'kind': 'metal'})


FLOOR_FIN = [(('BATH', 'POWDER', 'SHOWER', 'WATER CLOSET'), 'TL-02'), (('LAUNDRY', 'UTILITY', 'STORAGE', 'AHU', 'BACK HALL'), 'TL-04'),
             (('ENTRY',), 'ST-01'), (('PANTRY',), 'TL-01')]


def floor_code(name):
    for keys, code in FLOOR_FIN:
        if any(k in name for k in keys): return code
    return 'WD-01'


def shell():
    G = hg(); house_materials()
    stucco = material('STUCCO-HOUSE'); paint = material(R('wall', 'PT-02')); clg = material(R('ceiling', 'PT-01'))
    cope = material('ST-05')
    enc = {fl: G['enc'][fl] for fl in ('1', '2')}
    for k, p in enumerate(G['prisms']):
        fl = str(p['floor']); z0 = p['z0']
        if fl == '1' and abs(z0) < 0.01: z0 = -10.0                                   # the stucco runs down to grade
        if p.get('low'):
            prism(p['ext'], p['holes'], z0, p['z1'], {'side_out': stucco, 'top': cope, 'bottom': stucco, 'side_stone': stone_veneer()}, 'parapet')
        else:
            prism(p['ext'], p['holes'], z0, p['z1'], {'side_in': paint, 'side_out': stucco, 'top': stucco, 'bottom': stucco, 'side_stone': stone_veneer()}, 'house_wall', enc=enc[fl])
    for fl, ff in (('1', 0.0), ('2', 154.0)):
        for name, ring in G['floors'][fl]['rooms'].items():
            if fl == '1' and name in ('LIVING ROOM', 'KITCHEN AND DINING') and ('living' in CONTEXT or os.environ.get('PR_GLB')): continue   # the detailed rooms bring their own
            prism(ring, [], ff - 0.75, ff, {'top': material(R('floor', floor_code(name))) if floor_code(name) != 'WD-01' else material('WD-01'),
                                             'side_out': clg, 'bottom': clg}, 'floor_' + name.lower().replace(' ', '_'))
            c = G['ceil'].get('%s|%s' % (fl, name), 130.0 if fl == '1' else 272.0)
            prism(ring, [], c, c + 0.75, {'bottom': clg, 'side_out': clg, 'top': clg}, 'ceiling_' + name.lower().replace(' ', '_'))
    for s_ in G['f2_struct']:
        prism(s_['ext'], s_['holes'], 131.0, 153.2, {'side_out': stucco, 'bottom': clg, 'top': clg}, 'f2_structure')
    prism(G['roof']['outline'], [], 272.8, 276.0, {'side_out': stucco, 'bottom': clg, 'top': clg}, 'attic_floor')
    # floor 1 roof decks, the front balconies and their planters
    for d_ in G['f1_roofs']:
        prism(d_['ext'], d_['holes'], 131.0, 154.0, {'side_out': stucco, 'bottom': material('SOFFIT-WHITE'), 'top': material('ST-05')}, 'roof_deck')
    for b_ in G['balconies']:
        prism(b_['ext'], b_['holes'], 131.0, 154.0, {'side_out': stucco, 'bottom': material('SOFFIT-WHITE'), 'top': material('DECK-01')}, 'balcony')
    trim_ = material(R('trim', 'PT-01-SATIN'))
    for b_ in G.get('bases', []):                                                       # base round the shell rooms
        ff_ = 0.0 if b_['floor'] == 1 else 154.0
        prism(b_['ext'], b_['holes'], ff_, ff_ + 8.5, {'side_out': trim_, 'top': trim_, 'bottom': trim_}, 'shell_base')
    alu = material('ALU-BLK')
    for p_ in G['planters2']:
        front = max(c[1] for c in p_['ext']) < -380
        if front:                                                                      # E-4 pickets across the front, the planter behind
            x0_ = min(c[0] for c in p_['ext']); x1_ = max(c[0] for c in p_['ext']); yf = min(c[1] for c in p_['ext'])
            for k in range(int((x1_ - x0_ - 2) / 4.5) + 1):
                wbox(x0_ + 1 + k * 4.5, x0_ + 1.75 + k * 4.5, yf + 0.5, yf + 1.25, 154.0, 196.0, alu, 'rail_picket')
            for z_ in ((154.0, 156.0), (194.0, 196.5)): wbox(x0_, x1_, yf, yf + 1.75, z_[0], z_[1], alu, 'rail_bar')
        prism(p_['ext'], p_['holes'], 154.0, 170.0 if front else 176.0, {'side_out': material('FRAME-BLK') if front else stucco, 'top': material('MULCH'),
              'bottom': stucco}, 'balcony_planter')
        x0 = min(c[0] for c in p_['ext']); x1 = max(c[0] for c in p_['ext']); y0 = min(c[1] for c in p_['ext']); y1 = max(c[1] for c in p_['ext'])
        o = wbox(x0 + 3, x1 - 3, y0 + 3, y1 - 3, 168.0, 186.0, material('PLANTING-LOW'), 'balcony_planting', soft=4.0)
        if o is not None: leafy([o], density=500.0)
    alu = material('ALU-BLK')
    for (xa, ya, xb, yb) in G['railings']['2']:
        L = math.hypot(xb - xa, yb - ya)
        if L < 30: continue
        n = int(L / 4.5)
        ux, uy = (xb - xa) / L, (yb - ya) / L
        for k in range(n + 1):
            px, py = xa + ux * k * 4.5, ya + uy * k * 4.5
            wbox(px - 0.375, px + 0.375, py - 0.375, py + 0.375, 156.0, 194.0, alu, 'rail_picket')
        for z_ in ((154.0, 156.0), (193.5, 196.0)):
            wbox(min(xa, xb) - 0.75, max(xa, xb) + 0.75, min(ya, yb) - 0.75, max(ya, yb) + 0.75, z_[0], z_[1], alu, 'rail_bar')
    for b_ in G['belt']:
        prism(b_['ext'], b_['holes'], 147.0, 154.0, {'side_out': stucco, 'top': stucco, 'bottom': stucco}, 'belt_course')
        prism(b_['ext'], b_['holes'], 145.5, 147.0, {'side_out': stucco, 'top': stucco, 'bottom': stucco}, 'belt_bed')
    rm_ = roof_metal(); z_e = G['roof']['heel'] - G['roof']['slope'] * 18.0
    for (x_, y_) in G['downspouts']:                                                   # E-9: 3 x 4 in. leaders to grade
        wbox(x_ - 2.0, x_ + 2.0, y_ - 1.5, y_ + 1.5, -6.0, z_e, rm_, 'downspout')
    sconce_d = bpy.data.materials.get('LANTERN')
    MATS.setdefault('LANTERN-GLASS', {'kind': 'lamp', 'emit': 1.2})
    for (x_, y_) in ((66.0, -411.0), (154.0, -411.0), (190.0, -416.0), (270.0, -416.0)):   # wall lanterns by the entry and office window
        wbox(x_ - 3.0, x_ + 3.0, y_ - 4.0, y_, 76.0, 90.0, material('FRAME-BLK'), 'lantern')
        wbox(x_ - 2.4, x_ + 2.4, y_ - 3.6, y_ - 0.4, 77.0, 89.0, material('LANTERN-GLASS'), 'lantern_glass')
    openings_units(G)
    roof(G)


def openings_units(G):
    fr = material('FRAME-BLK'); gl = material('GLASS-CLEAR'); trim = material(R('trim', 'PT-01-SATIN'))
    NPAN = {'G': 3, 'H': 2, 'M': 2}
    for o in G['openings_all']:
        if o['kind'] == 'open': continue
        ax = o['along']; a0, a1 = (o['x0'], o['x1']) if ax == 'x' else (o['y0'], o['y1']); c0, c1 = (o['y0'], o['y1']) if ax == 'x' else (o['x0'], o['x1'])
        z0, z1 = o['z0'], o['z1']; cm = (c0 + c1) / 2
        def B(u0, u1, v0, v1, w0, w1, mat, nm):
            return wbox(u0, u1, v0, v1, w0, w1, mat, nm) if ax == 'x' else wbox(v0, v1, u0, u1, w0, w1, mat, nm)
        if not o['exterior']:
            if o['kind'] == 'door':                                                       # an interior doorway, cased both sides
                for s_ in (c0 - 0.75, c1):
                    B(a0 - 3.5, a0 + 0.5, s_, s_ + 0.75, o['z0'], z1 + 3.5, trim, 'casing'); B(a1 - 0.5, a1 + 3.5, s_, s_ + 0.75, o['z0'], z1 + 3.5, trim, 'casing')
                    B(a0 + 0.5, a1 - 0.5, s_, s_ + 0.75, z1 - 0.5, z1 + 3.5, trim, 'casing_head')
                lw = min(36.0, a1 - a0 - 1.0)                                            # the leaf, open 90 degrees (A-600: 8 ft panel doors)
                if lw > 20 and a1 - a0 < 44:
                    B(a0 + 0.5, a0 + 2.25, c1, c1 + lw, o['z0'] + 0.5, z1 - 0.25, material(R('door', 'PT-01-SATIN'), '-trim'), 'door_leaf')
            continue
        f = 2.25; d0, d1 = cm - 1.5, cm + 1.5
        B(a0, a0 + f, d0, d1, z0, z1, fr, 'frame'); B(a1 - f, a1, d0, d1, z0, z1, fr, 'frame')
        B(a0 + f, a1 - f, d0, d1, z1 - f, z1, fr, 'frame')
        B(a0 + f, a1 - f, d0, d1, z0, z0 + f, fr, 'frame')
        span = a1 - a0
        n = NPAN.get(o.get('type'), 0) or (max(2, round(span / 48.0)) if o['kind'] == 'slider' else 2 if (o['kind'] == 'door' and span > 52) else 2 if span > 76 else 1)
        pw = (span - 2 * f) / n
        for k in range(1, n):
            m_ = a0 + f + k * pw; B(m_ - 1.25, m_ + 1.25, d0, d1, z0 + f, z1 - f, fr, 'mullion')
        if o['kind'] in ('door', 'slider'):                                               # leaf stiles and a mid rail on glass doors
            for k in range(n):
                p0 = a0 + f + k * pw; p1 = p0 + pw
                for (u0, u1) in ((p0, p0 + 2.5), (p1 - 2.5, p1)): B(u0, u1, d0 + 0.3, d1 - 0.3, z0 + f, z1 - f, fr, 'leaf_stile')
                B(p0 + 2.5, p1 - 2.5, d0 + 0.3, d1 - 0.3, z0 + f, z0 + f + 4.0, fr, 'leaf_rail')
        B(a0 + f, a1 - f, cm - 0.12, cm + 0.12, z0 + f, z1 - f, gl, 'glass')
        if o.get('type') not in ('G', 'H') and o['kind'] != 'slider':               # divided lites, panes 75% larger (owner 11.11.26)
            for k in range(n):
                p0 = a0 + f + k * pw + (2.5 if o['kind'] == 'door' else 0); p1 = a0 + f + (k + 1) * pw - (2.5 if o['kind'] == 'door' else 0)
                q0 = z0 + f + (4.0 if o['kind'] == 'door' else 0); q1 = z1 - f
                nc = max(1, round((p1 - p0) / 21.0)); nr = max(1, round((q1 - q0) / 30.0))
                for c_ in range(1, nc):
                    u_ = p0 + (p1 - p0) * c_ / nc
                    for s_ in (-1, 1): B(u_ - 0.4, u_ + 0.4, cm + s_ * 0.12, cm + s_ * 0.6, q0, q1, fr, 'muntin')
                for r_ in range(1, nr):
                    w_ = q0 + (q1 - q0) * r_ / nr
                    for s_ in (-1, 1): B(p0, p1, cm + s_ * 0.12, cm + s_ * 0.6, w_ - 0.4, w_ + 0.4, fr, 'muntin')
        inn = c1 if not _inside(((a0 + a1) / 2, c0 - 6) if ax == 'x' else (c0 - 6, (a0 + a1) / 2), G['enc'][str(o['floor'])]) else c0
        sg_ = 1 if inn == c1 else -1                                                      # the room side: casing, and a stool under windows
        for (u0, u1) in ((a0 - 3.5, a0), (a1, a1 + 3.5)):
            B(u0, u1, *sorted((inn, inn + sg_ * 0.75)), z0 - (0 if o['kind'] != 'window' else 1.0), z1 + 3.5, trim, 'ext_casing')
        B(a0, a1, *sorted((inn, inn + sg_ * 0.75)), z1, z1 + 3.5, trim, 'ext_casing_head')
        if o['kind'] == 'window' and o['z0'] > 6:
            B(a0 - 4.5, a1 + 4.5, *sorted((inn - sg_ * 0.5, inn + sg_ * 1.5)), z0 - 1.0, z0, trim, 'stool')
        if o['kind'] == 'window':                                                         # outside sill, a stucco wash
            out_side = c0 if not _inside(((a0 + a1) / 2, c0 - 6) if ax == 'x' else (c0 - 6, (a0 + a1) / 2), G['enc'][str(o['floor'])]) else c1
            s0, s1 = (out_side - 1.5, out_side) if out_side == c0 else (out_side, out_side + 1.5)
            B(a0 - 1.0, a1 + 1.0, s0, s1, z0 - 1.5, z0, material('ST-05'), 'ext_sill')


def roof(G):
    rf = G['roof']; rm = roof_metal(); sof = material('SOFFIT-WHITE')
    heel, sl, top = rf['heel'], rf['slope'], rf['top']
    levels = [(-18.0, [rf['eave']])] + [(r['d'], r['polys']) for r in rf['rings']]
    for (da, pa), (db, pb) in zip(levels[:-1], levels[1:]):
        bm_ = bmesh.new(); zmap = {}
        for rings_, d_ in ((pa, da), (pb, db)):
            for ring in rings_:
                pts = ring[:-1] if ring[0] == ring[-1] else ring
                vs = [bm_.verts.new((x * IN, y * IN, 0.0)) for x, y in pts]
                for v in vs: zmap[v] = heel + sl * d_
                for i in range(len(vs)):
                    try: bm_.edges.new((vs[i], vs[(i + 1) % len(vs)]))
                    except ValueError: pass
        bmesh.ops.triangle_fill(bm_, use_beauty=True, use_dissolve=False, edges=list(bm_.edges), normal=(0, 0, 1))
        for v in bm_.verts: v.co.z = zmap.get(v, heel) * IN
        for fc in bm_.faces:
            if fc.normal.z < 0: fc.normal_flip()
        me = bpy.data.meshes.new('roof'); bm_.to_mesh(me); bm_.free(); me.materials.append(rm)
        o = bpy.data.objects.new('roof', me); bpy.context.collection.objects.link(o)
        so = o.modifiers.new('solid', 'SOLIDIFY'); so.thickness = 0.75 * IN; so.offset = -1.0
    for ring in levels[-1][1]:
        prism(ring, [], top, top + 0.75, {'top': rm, 'side_out': rm, 'bottom': sof}, 'roof_field')
    z_eave = heel - sl * 18.0
    for s_ in rf['soffit']: prism(s_['ext'], s_['holes'], z_eave - 3.0, z_eave - 2.25, {'bottom': sof, 'side_out': sof, 'top': sof}, 'soffit')
    for s_ in rf['fascia']: prism(s_['ext'], s_['holes'], z_eave - 3.0, z_eave + 1.0, {'side_out': sof, 'top': sof, 'bottom': sof}, 'fascia')
    for s_ in rf['gutter']: prism(s_['ext'], s_['holes'], z_eave - 2.0, z_eave + 2.5, {'side_out': rm, 'top': rm, 'bottom': rm, 'side_in': rm}, 'gutter')


# --------------------------------------------------------------------------------------------------------------- site
PL = dict(x0=-250.0, x1=350.0, y0=-658.0, y1=830.0)            # the lot, 50 x 124 ft (A-100), on the house grid


def ground_plane(x0, x1, y0, y1, z, mat, name, z1=None):
    return wbox(x0, x1, y0, y1, (z1 if z1 is not None else z) - 2.0, z1 if z1 is not None else z, mat, name)


def plant(model, height, X, Y, Z=0.0, rot=0.0):
    """A planting model placed as a collection instance: imported once (a 1k Poly Haven tree is 50 to 200 MB), normalised to a
    100 in. height with its base at the origin, then instanced wherever the plan has one."""
    coll = bpy.data.collections.get('PL_' + model)
    if coll is None:
        try: bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
        except Exception: pass
        before = set(bpy.data.objects)
        try: bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, 'models', model, model + '.gltf'))
        except Exception as e: print('plant', model, e); return None
        new = [o for o in set(bpy.data.objects) - before]; meshes = [o for o in new if o.type == 'MESH']
        if not meshes: return None
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
        cx_, cy_ = (min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        k = 100.0 * IN / max(zmax - zmin, 1e-6)
        for o in [o for o in new if o.parent is None]:
            o.matrix_world = Matrix.Scale(k, 4) @ Matrix.Translation((-cx_, -cy_, -zmin)) @ o.matrix_world
        coll = bpy.data.collections.new('PL_' + model)
        for o in new:
            for c in list(o.users_collection): c.objects.unlink(o)
            coll.objects.link(o)
    e = bpy.data.objects.new('plant_' + model, None); e.instance_type = 'COLLECTION'; e.instance_collection = coll
    bpy.context.collection.objects.link(e)
    e.matrix_world = Matrix.Translation((X * IN, Y * IN, Z * IN)) @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Scale(height / 100.0, 4)
    return e


def site():
    house_materials(); G = hg()
    lawn = material('LAWN'); turf = material('TURF'); asph = material('ASPHALT'); walk = material('SIDEWALK'); pav = material('DRIVE-PAVER')
    mul = material('MULCH'); curb = material('CURB'); ext = material('STUCCO-HOUSE')
    g_yard = -6.0                                       # yard grade about 11.2 NGVD against FFE 11.70 (C1.0)
    # beyond the lot: the neighbours' yards and the street
    ground_plane(-1400, 1500, -1400, 1600, -12.0, lawn, 'ground_far')
    ground_plane(PL['x0'], PL['x1'], PL['y0'], PL['y1'], g_yard, lawn, 'lawn')
    # Thomas Avenue (A-100, C1.0): 6'-6" sidewalk, 6'-6" parkway, 22 ft asphalt; the curb and the far side
    y_pl = PL['y0']
    wbox(-1400, 1500, y_pl - 78, y_pl, -12.0, -9.0, walk, 'sidewalk')
    wbox(-1400, 1500, y_pl - 156, y_pl - 78, -12.0, -10.0, lawn, 'parkway')
    wbox(-1400, 1500, y_pl - 160, y_pl - 156, -16.0, -9.5, curb, 'curb')
    wbox(-1400, 1500, y_pl - 424, y_pl - 160, -16.0, -14.5, asph, 'street')
    wbox(-1400, 1500, y_pl - 428, y_pl - 424, -16.0, -9.5, curb, 'curb_far')
    wbox(-1400, 1500, y_pl - 580, y_pl - 428, -12.0, -10.0, lawn, 'parkway_far')
    # driveway to the carport: 18'-8" wide (A-100) over the sidewalk to the street, a sliding car gate at the line
    dx0, dx1 = -176.0, 48.0
    wbox(dx0, dx1, y_pl - 160, -414.0, -12.0, -5.5, pav, 'driveway')
    wbox(dx0, dx1, -414.0, -190.0, -2.0, -0.5, pav, 'carport_floor')
    # entry walk and steps from the sidewalk to the front door (pavers), the two planters flanking it (A-SITE-PLANTER)
    wbox(74.0, 146.0, y_pl, -290.0, -6.0, -1.0, pav, 'entry_walk')
    for (x0, x1) in ((34.0, 50.0), (170.0, 186.0)):
        wbox(x0, x1, -474.0, -414.0, -6.0, 30.0, ext, 'entry_planter'); wbox(x0 + 1.5, x1 - 1.5, -472.5, -415.5, 29.0, 29.5, mul, 'planter_soil')
        o = wbox(x0 + 2, x1 - 2, -472.0, -416.0, 29.0, 44.0, material('PLANTING-LOW'), 'planter_shrub', soft=3.0)
        if o is not None: leafy([o], density=600.0)
    # front fence and gates 1 ft inside the line (A-100): stucco piers, black aluminium pickets, the sliding car gate
    alu = material('ALU-BLK'); fy = y_pl + 12.0
    for (x0, x1) in ((PL['x0'] + 12, dx0 - 6), (dx1 + 6, 66.0), (154.0, PL['x1'] - 12)):
        for k in range(int((x1 - x0) / 4.5) + 1):
            wbox(x0 + k * 4.5, x0 + k * 4.5 + 0.75, fy - 0.375, fy + 0.375, -6.0, 54.0, alu, 'fence_picket')
        for z_ in (-4.0, 52.0): wbox(x0, x1, fy - 0.75, fy + 0.75, z_, z_ + 2.0, alu, 'fence_rail')
    for px in (PL['x0'] + 6, dx0 - 12, dx1, 66.0, 146.0, 154.0, PL['x1'] - 18):
        wbox(px, px + 12, fy - 6, fy + 6, -6.0, 60.0, ext, 'fence_pier'); wbox(px - 1, px + 13, fy - 7, fy + 7, 60.0, 62.0, material('ST-05'), 'pier_cap')
    for k in range(int((dx1 - dx0) / 4.5) + 1):                                          # the car gate, closed
        wbox(dx0 + k * 4.5, dx0 + k * 4.5 + 0.75, fy + 2 - 0.375, fy + 2 + 0.375, -4.0, 60.0, alu, 'gate_picket')
    for z_ in (-3.0, 30.0, 58.0): wbox(dx0, dx1, fy + 1.25, fy + 2.75, z_, z_ + 2.0, alu, 'gate_rail')
    for (x0, x1) in ((66.0, 74.0), (146.0, 154.0)): pass
    for k in range(int((146.0 - 74.0) / 4.5) + 1):                                       # the pedestrian gate
        wbox(74.0 + k * 4.5, 74.75 + k * 4.5, fy - 0.375, fy + 0.375, -4.0, 54.0, alu, 'gate_picket')
    # side fences and clusia hedges (L-2 CLG: 48 in. at 36 in. o.c., grown to 6 ft), mondo grass and mulch beds in front
    hed = []
    for (x0, x1) in ((PL['x0'] + 1, PL['x0'] + 4), (PL['x1'] - 4, PL['x1'] - 1)):
        wbox(x0, x1, y_pl + 12, PL['y1'] - 12, -6.0, 72.0, ext, 'side_fence')
    hed.append(wbox(PL['x0'] + 4, PL['x0'] + 30, y_pl + 24, -200.0, -6.0, 72.0, material('PLANTING-LOW'), 'hedge_w', soft=8.0))
    hed.append(wbox(PL['x1'] - 30, PL['x1'] - 4, y_pl + 24, -200.0, -6.0, 72.0, material('PLANTING-LOW'), 'hedge_e', soft=8.0))
    hed.append(wbox(-238.0, -214.0, 220.0, 560.0, -6.0, 84.0, material('PLANTING-LOW'), 'hedge_w_rear', soft=8.0))
    leafy([h for h in hed if h is not None], density=700.0)
    wbox(PL['x0'] + 30, dx0 - 6, y_pl + 18, -420.0, -6.0, -5.2, mul, 'bed_w')
    wbox(186.0, PL['x1'] - 30, y_pl + 18, -420.0, -6.0, -5.2, mul, 'bed_e')
    import random as _r
    for k in range(26):                                                                    # bromeliads, spider lilies, liriope in the beds
        rr = _r.Random(k); x_ = rr.uniform(200, 315) if k % 2 else rr.uniform(-212, -192); y_ = rr.uniform(y_pl + 40, -440)
        plant(('shrub_04', 'shrub_02', 'grass_medium_01')[k % 3], rr.uniform(18, 34), x_, y_, -5.5, rr.uniform(0, 360))
    # artificial turf along the west side and the rear (L-2)
    wbox(PL['x0'] + 30, -192.0, -190.0, 560.0, -6.0, -5.0, turf, 'turf_w')
    wbox(PL['x0'] + 12, 330.0, 480.0, 575.0, -6.0, -5.0, turf, 'turf_rear')
    # trees (L-1 / L-2, positions scaled off the plan; VERIFY): relocated gumbo limbos front right and at the rear corners,
    # Simpson's stoppers by the street, crape myrtles and privets at the rear, the neighbours' live oaks, mango and royal palm
    for (m, h, X_, Y_, r) in (('island_tree_02', 216.0, 268.0, -540.0, 30), ('island_tree_02', 150.0, 300.0, -640.0, 0), ('island_tree_02', 150.0, -60.0, -640.0, 70),
                              ('island_tree_01', 240.0, -225.0, 790.0, 10), ('island_tree_01', 240.0, 320.0, 790.0, 140), ('island_tree_02', 168.0, 60.0, 800.0, 200),
                              ('island_tree_02', 168.0, 170.0, 800.0, 40), ('shrub_01', 96.0, -200.0, 720.0, 0), ('shrub_02', 96.0, -170.0, 700.0, 0),
                              ('island_tree_01', 420.0, -560.0, 760.0, 60), ('island_tree_01', 400.0, -520.0, 1000.0, 200), ('island_tree_01', 330.0, -470.0, 130.0, 80),
                              ('island_tree_01', 300.0, 620.0, 980.0, 20), ('island_tree_02', 260.0, 650.0, -560.0, 100), ('island_tree_02', 180.0, -520.0, -560.0, 250)):
        plant(m, h, X_, Y_, -6.0 if abs(X_) < 400 else -12.0, r)
    for (X_, Y_) in ((-120.0, -470.0), (-60.0, -470.0), (0.0, -470.0)):
        plant('shrub_04', 30.0, X_, Y_ - 30, -6.0, 0)
    # the neighbours (Lots 30 and 32) as two-storey stucco massing with hip roofs, 5 ft off their lines
    for (x0, x1) in ((PL['x1'] + 60, PL['x1'] + 540), (PL['x0'] - 540, PL['x0'] - 60)):
        nb = wbox(x0, x1, -420.0, 560.0, -12.0, 270.0, material('NEIGHBOR'), 'neighbour')
        for zz in ((24.0, 96.0), (170.0, 236.0)):
            for k in range(5):
                xa = x0 + 40 + k * (x1 - x0 - 80) / 4.0
                wbox(xa - 20, xa + 20, -421.0, -419.9, zz[0], zz[1], material('FRAME-BLK'), 'nb_window')
            for k in range(7):
                ya = -380.0 + k * 140.0; xf = x0 - 0.1 if x0 > 0 else x1 + 0.1
                wbox(min(xf, xf + (1 if x0 < 0 else -1)), max(xf, xf + (1 if x0 < 0 else -1)), ya - 18, ya + 18, zz[0] + 10, zz[1] - 6, material('FRAME-BLK'), 'nb_window')
        bm_ = bmesh.new(); cx, cy = (x0 + x1) / 2, 70.0
        vs = [bm_.verts.new(((x0 - 18) * IN, (-438) * IN, 262 * IN)), bm_.verts.new(((x1 + 18) * IN, (-438) * IN, 262 * IN)),
              bm_.verts.new(((x1 + 18) * IN, 578 * IN, 262 * IN)), bm_.verts.new(((x0 - 18) * IN, 578 * IN, 262 * IN)),
              bm_.verts.new((cx * IN, -200 * IN, 380 * IN)), bm_.verts.new((cx * IN, 340 * IN, 380 * IN))]
        for f_ in ((0, 1, 4), (1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5)): bm_.faces.new([vs[i] for i in f_])
        me = bpy.data.meshes.new('neighbour_roof'); bm_.to_mesh(me); bm_.free(); me.materials.append(material('NEIGHBOR-ROOF'))
        o = bpy.data.objects.new('neighbour_roof', me); bpy.context.collection.objects.link(o)
    pool_and_ancillary()


def pool_and_ancillary():
    """The pool, deck, rear fence and ancillary structure as stage_living builds them (FOR A-100 / A-303)."""
    st1 = material('ST-01'); ext = material('STUCCO-HOUSE'); deck = material('DECK-01'); steel = material('ALU-BLK'); RD = 194.0
    px0, px1, py0, py1 = 197.0, 277.0, 286.0, 418.0
    for r_ in ((px0 - 12, px1 + 12, py0 - 12, py0), (px0 - 12, px1 + 12, py1, py1 + 12), (px0 - 12, px0, py0, py1), (px1, px1 + 12, py0, py1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -0.5, 1.0, st1, 'coping', soft=0.4)
    MATS.setdefault('POOL-PLASTER', {'hex': '#BFDCDC', 'rough': 0.5, 'kind': 'paint'}); pp = material('POOL-PLASTER')
    wbox(px0, px1, py0, py1, -54.0, -52.0, pp, 'pool_floor')
    for r_ in ((px0 - 1, px0, py0, py1), (px1, px1 + 1, py0, py1), (px0, px1, py0 - 1, py0), (px0, px1, py1, py1 + 1)):
        wbox(r_[0], r_[1], r_[2], r_[3], -54.0, 1.0, pp, 'pool_wall')
    for r_ in ((95.0, 330.0, RD + 6.0, py0 - 12), (95.0, 330.0, py1 + 12, 575.0), (95.0, px0 - 12, py0 - 12, py1 + 12), (px1 + 12, 330.0, py0 - 12, py1 + 12)):
        wbox(r_[0], r_[1], r_[2], r_[3], -6.0, -0.5, deck, 'deck')
    wm = bpy.data.materials.get('POOL-WATER')
    if wm is None:
        wm = bpy.data.materials.new('POOL-WATER'); wm.use_nodes = True; bw_ = wm.node_tree.nodes['Principled BSDF']
        bw_.inputs['Base Color'].default_value = (0.36, 0.70, 0.74, 1); bw_.inputs['Roughness'].default_value = 0.04
        bw_.inputs['Transmission Weight'].default_value = 1.0; bw_.inputs['IOR'].default_value = 1.33
    pw_ = wbox(px0, px1, py0, py1, -6.5, -6.0, wm, 'pool_water'); pw_.visible_shadow = False   # the sun reaches the pool floor (no caustics)
    wbox(-250.0, 350.0, 818.0, 821.0, -6.0, 72.0, ext, 'fence_rear')
    leafy([wbox(-238.0, 338.0, 790.0, 818.0, -6.0, 120.0, material('PLANTING-LOW'), 'hedge_rear', soft=8.0)], density=700.0)
    ax0, ax1, ay0, ay1 = -129.0, 216.0, 575.0, 698.0
    wbox(ax0, ax1, ay0, ay1, -6.0, 132.0, ext, 'ancillary')
    wbox(ax0, ax1, ay0, ay0 + 6, 132.0, 168.0, ext, 'parapet'); wbox(ax0, ax1, ay1 - 6, ay1, 132.0, 168.0, ext, 'parapet')
    wbox(ax0, ax0 + 6, ay0 + 6, ay1 - 6, 132.0, 168.0, ext, 'parapet'); wbox(ax1 - 6, ax1, ay0 + 6, ay1 - 6, 132.0, 150.0, ext, 'parapet')
    wbox(ax0 - 1, ax1 + 1, ay0 - 1, ay1 + 1, 168.0, 170.0, material('ST-05'), 'anc_coping')
    fr = material('FRAME-BLK'); gl = material('GLASS-CLEAR')
    for (x0_, x1_, z0_, z1_) in ((23.0, 55.0, 0.0, 96.0), (99.0, 178.0, 36.0, 96.0)):
        wbox(x0_, x1_, ay0 - 0.5, ay0 + 0.2, z0_, z1_, gl, 'anc_glass')
        for r_ in ((x0_, x0_ + 2, z0_, z1_), (x1_ - 2, x1_, z0_, z1_), (x0_, x1_, z1_ - 2, z1_), (x0_, x1_, z0_, z0_ + 2)):
            wbox(r_[0], r_[1], ay0 - 1.0, ay0 + 0.5, r_[2], r_[3], fr, 'anc_frame')
    for k in range(18):
        z_ = (k + 1) * 132.0 / 18.0; y_ = ay0 - 10 + k * 7.4
        wbox(ax1, ax1 + 40.0, y_, y_ + 11.0, z_ - 1.5, z_, ext, 'anc_step')
        wbox(ax1 + 0.5, ax1 + 39.5, y_ + 0.5, y_ + 7.9, -6.0, z_ - 1.5, ext, 'anc_stair_mass')
    MATS.setdefault('WOOD-FURN', {'hex': '#7A5A3E', 'rough': 0.6, 'kind': 'wood', 'texture': 'oak_veneer_01'})
    for (x_, y_) in ((-40.0, 590.0), (130.0, 590.0), (-40.0, 683.0), (130.0, 683.0)):
        wbox(x_, x_ + 6, y_, y_ + 6, 170.0, 228.0, material('WOOD-FURN'), 'pergola_post')
    for k in range(14):
        wbox(-46.0, 142.0, 586.0 + k * 7.5, 588.0 + k * 7.5, 222.0, 228.0, material('WOOD-FURN'), 'pergola_slat')


def stage_house():
    for o in list(bpy.data.objects):                     # the dummy view's wall, returns, floor and ceiling
        if o.type == 'MESH' and o.name.split('.')[0] in ('wall', 'return_l', 'return_r', 'front_wall', 'floor', 'ceiling', 'beyond', 'beyond_floor', 'wall_plain'):
            o.hide_render = True; o.hide_viewport = True
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT' and o.data.type in ('POINT', 'SPOT', 'AREA') and not o.data.cycles.is_portal: o.hide_render = True
    shell()
    if os.environ.get('PR_NOSITE') != '1': site()
    if not any(o.type == 'LIGHT' and o.data.type == 'SUN' for o in bpy.data.objects):
        sd = bpy.data.lights.new('sun', 'SUN'); sd.energy = 4.0; sd.color = (1.0, 0.96, 0.9)
        so = bpy.data.objects.new('sun', sd); bpy.context.collection.objects.link(so)


STAGES['house'] = stage_house
