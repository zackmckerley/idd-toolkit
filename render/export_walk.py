"""Export the built scene as the walk-through model (owner 11.11.26: "save it in 3D form so I'm able to walk through it").
exec'd by photoreal.py when PR_GLB is set, after the stage and its --context rooms are built. glTF carries plain PBR: every
material is reduced to its colour, roughness and metalness (images kept where a texture feeds the colour directly, e.g. the
paintings); planting models and leaf instancing become light proxies; Draco-compressed. Lights stay out: the viewer lights it."""


def _hex_lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]


SPECIAL = {'STONE-VENEER': ('#B8AA94', 0.8, 0.0), 'ROOF-SEAM': ('#8E9294', 0.45, 0.6), 'GLASS-ROD': ('#F2EEE6', 0.05, 0.0),
           'CRYSTAL': ('#F4F2EE', 0.05, 0.0), 'POOL-WATER': ('#5DB4BE', 0.05, 0.0), 'HEDGE': ('#2F4A26', 0.9, 0.0), 'LEAF': ('#3A5A2C', 0.8, 0.0)}


def _simple(m):
    if m is None: return None
    key = m.name.split('.')[0]; base = key[:-5] if key.endswith('-trim') else key
    spec = MATS.get(base, {})
    col, rough, metal = None, spec.get('rough', 0.5), 1.0 if spec.get('kind') == 'metal' else 0.0
    img = None
    if base in SPECIAL: col, rough, metal = SPECIAL[base][0], SPECIAL[base][1], SPECIAL[base][2]
    elif 'hex' in spec: col = spec['hex']
    if m.use_nodes and m.node_tree:
        bs = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bs is not None:
            ln = bs.inputs['Base Color'].links
            if ln and ln[0].from_node.type == 'TEX_IMAGE' and base.startswith('ART-'): img = ln[0].from_node.image
            if col is None and not ln:
                c = bs.inputs['Base Color'].default_value; col = '#%02x%02x%02x' % tuple(int(max(0, min(1, v ** (1 / 2.2))) * 255) for v in c[:3])
    if col is None: col = '#d9d4ca'
    g = bpy.data.materials.new(m.name + '_gl'); g.use_nodes = True; b = g.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*_hex_lin(col), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    kind = spec.get('kind', '')
    if base.startswith('GLASS') or kind == 'glass' or base in ('CRYSTAL', 'GLASS-ROD', 'POOL-WATER'):
        b.inputs['Alpha'].default_value = 0.25 if base != 'POOL-WATER' else 0.75; g.blend_method = 'BLEND' if hasattr(g, 'blend_method') else None
    if kind == 'lamp' or base in ('LED-STRIP', 'LAMP', 'LENS', 'SHADE'):
        b.inputs['Emission Color'].default_value = (1.0, 0.85, 0.65, 1); b.inputs['Emission Strength'].default_value = 1.5
    if img is not None:
        t = g.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; g.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    return g


def export_walk(path):
    import bmesh as _bm
    cache = {}
    # planting: each collection-instance tree becomes a trunk and three canopy spheres (a 1k tree model is 50 to 200 MB)
    trunk = _simple(bpy.data.materials.get('WOOD-FURN') or material('WOOD-FURN')); leafm = bpy.data.materials.new('CANOPY_gl'); leafm.use_nodes = True
    leafm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*_hex_lin('#4E6B34'), 1)
    for e in [o for o in bpy.data.objects if o.type == 'EMPTY' and o.instance_type == 'COLLECTION']:
        h = e.matrix_world.to_scale()[2] * 100.0 * IN; loc = e.matrix_world.translation
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06 * h, depth=0.45 * h, location=(loc.x, loc.y, loc.z + 0.22 * h))
        t = bpy.context.active_object; t.name = 'tree_trunk'; t.data.materials.append(trunk)
        for k, (dx, dy, dz, r) in enumerate(((0, 0, 0.62, 0.32), (0.14, 0.08, 0.72, 0.24), (-0.12, -0.1, 0.78, 0.22))):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * h, location=(loc.x + dx * h, loc.y + dy * h, loc.z + dz * h))
            c = bpy.context.active_object; c.name = 'tree_canopy'; c.data.materials.append(leafm); c.scale[2] = 0.8
        e.instance_type = 'NONE'
    for o in list(bpy.data.objects):
        if o.type != 'MESH': continue
        for md in list(o.modifiers):
            if md.type == 'NODES': o.modifiers.remove(md)                  # leaf instancing on the hedges: the box stays, green
        for i, sl in enumerate(o.material_slots):
            m = sl.material
            if m is None: continue
            if m.name not in cache: cache[m.name] = _simple(m)
            sl.material = cache[m.name]
    part = os.environ.get('PR_GLB_PART', 'all')            # base: what this stage built; context: only the rooms loaded with --context
    SITE = ('coping', 'pool', 'deck', 'fence', 'hedge', 'ancillary', 'anc_', 'parapet', 'pergola', 'living_facade', 'living_coping',
            'wing_', 'dining_wing', 'sun', 'portal', 'beyond', 'paver')
    def keep(o):
        try:
            if o.type != 'MESH' or o.hide_render or not o.visible_get(): return False
        except RuntimeError: return False
        new = o.name not in PRE_CTX
        if part == 'base': return not new
        if part == 'context': return new and not o.name.split('.')[0].startswith(SITE)
        return True
    for o in bpy.data.objects:
        try: o.select_set(keep(o))
        except RuntimeError: pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_draco_mesh_compression_enable=True,
                              export_draco_mesh_compression_level=6, export_image_format='JPEG', export_lights=False, export_cameras=False,
                              export_yup=True)
    print('exported', path, os.path.getsize(path) // 1024, 'KB')
