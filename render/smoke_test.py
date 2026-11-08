"""Headless render smoke test: a 12' x 14' room, 10' ceiling, one window, Cycles CPU. Proves the tool chain before the real scenes."""
import bpy, math, sys
FT = 0.3048
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 32; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 640, 400
def mat(name, rgb, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    return m
def box(name, x, y, z, w, d, h, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x + w / 2) * FT, (y + d / 2) * FT, (z + h / 2) * FT))
    o = bpy.context.object; o.name = name; o.scale = (w * FT, d * FT, h * FT); o.data.materials.append(m); return o
wall = mat('PT-02', (0.80, 0.76, 0.68)); floor = mat('WD-01', (0.45, 0.30, 0.18), 0.4); ceil = mat('PT-01', (0.92, 0.92, 0.90))
box('floor', 0, 0, -0.1, 12, 14, 0.1, floor); box('ceiling', 0, 0, 10, 12, 14, 0.1, ceil)
box('wall_w', -0.5, 0, 0, 0.5, 14, 10, wall); box('wall_e', 12, 0, 0, 0.5, 14, 10, wall); box('wall_s', 0, -0.5, 0, 12, 0.5, 10, wall)
box('wall_n_l', 0, 14, 0, 4, 0.5, 10, wall); box('wall_n_r', 8, 14, 0, 4, 0.5, 10, wall)
box('wall_n_sill', 4, 14, 0, 4, 0.5, 2, wall); box('wall_n_head', 4, 14, 8, 4, 0.5, 2, wall)
bpy.ops.object.light_add(type='SUN', location=(6 * FT, 30 * FT, 20 * FT)); s = bpy.context.object; s.data.energy = 4; s.rotation_euler = (math.radians(-60), 0, math.radians(180))
bpy.ops.object.light_add(type='AREA', location=(6 * FT, 7 * FT, 9.8 * FT)); a = bpy.context.object; a.data.energy = 300; a.data.size = 2
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
bpy.ops.object.camera_add(location=(6 * FT, 1 * FT, 5.25 * FT), rotation=(math.radians(90), 0, 0)); cam = bpy.context.object; cam.data.lens = 18; sc.camera = cam
sc.render.filepath = sys.argv[-1]; bpy.ops.render.render(write_still=True)
