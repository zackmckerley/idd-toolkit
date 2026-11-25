"""2191 SW 23rd St (HD103): the owner's changes made on FOR Architecture's own plans (presentation 11.24.26, raster).

Nothing is redrawn that does not change. The house keeps FOR's U shape around the pool court; the west bar moves 3'-0" toward
SW 22nd Ave and the garage side of the east wing moves 5'-2" to FOR's 7'-6" setback line.

Coordinates: feet from the SW lot corner (x east, y north). 37.40 px/ft read on the 95'-0" north line and checked on the
74'-6" east line (74.47').

    python3 hd103/revise_plans.py OUTDIR
"""
import sys, os, json
sys.path.insert(0, '/home/claude/flrwork')
from idd_revise import Plan, BLACK, THIN, FURN, WHITE

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/rev/out'
os.makedirs(OUT, exist_ok=True)
SRC1 = '/home/claude/deck/img_p3_11.png'; SRC2 = '/home/claude/deck/img_p4_22.png'
DRIVE_END = -13.4            # where FOR's driveway edge stops at the street
DW, DE = 3.0, 5.2            # widening: west bar, east wing (garage side)
EW = 86.83                   # inside face of the new east wall (outside face 87.50, FOR's 7'-6" line)


def ground():
    p = Plan(SRC1, 37.40, 1115, 3020)
    # ------------------------------------------------ 1. west bar 3'-0" wider
    p.slide(24.9, 17.5, 41.0, 29.15, dx=-DW, fill='smear')      # dining: table, dry bar and wall move together
    p.slide(24.9, 29.15, 37.5, 30.35, dx=-DW, fill='white')     # the head chair, clear of the powder room door swing
    p.slide(24.9, 30.35, 28.8, 49.0, dx=-DW, fill='smear')     # kitchen: the counter run moves with the wall
    p.slide(24.9, 49.0, 26.4, 67.5, dx=-DW, fill='smear')      # living: wall and windows
    p.slide(31.4, 34.2, 37.4, 46.7, dx=-1.5)                   # island and stools back to the middle of the wider room
    p.slide(26.6, 50.0, 39.9, 63.4, dx=-1.5)                   # living room furniture, same
    p.change(1, [(22.2, 49.0, 25.3, 67.1), (22.2, 17.8, 25.3, 49.0)], "West wall moved 3'-0\" toward SW 22nd Ave. Great room 18'-4\" wide (was 15'-4\"); the dining room keeps 14'-10\" beside the scullery.", at=(23.8, 58.0))
    # ------------------------------------------------ 2. scullery in place of the pantry
    p.white(37.0, 18.52, 45.26, 26.9)
    p.wall(37.75, 17.81, 41.2, 18.5); p.line([(37.0, 18.57), (37.8, 18.57)], 2, BLACK)   # the dining window stops at the scullery wall
    p.copy(31.0, 17.6, 33.75, 18.62, 35.0, 17.6, from_orig=False)   # the stretched end of the window, redrawn from FOR's own
    p.partition(37.8, 18.5, 38.22, 27.3)                        # west wall, backs the dining room
    p.line([(38.22, 27.1), (41.1, 27.1)], 1, FURN, dash=(8, 6))  # 2'-10" cased opening to the kitchen
    p.rect(43.2, 18.52, 45.26, 26.9, 2, BLACK)                  # counter on the east wall
    p.copy(26.05, 38.2, 28.0, 40.95, 43.25, 21.0, flip='h')       # FOR's kitchen sink, turned to the east wall
    p.rect(43.2, 24.3, 45.26, 26.3, 1, THIN, dash=(10, 6)); p.label(44.23, 25.3, 'DW')
    p.rect(38.22, 18.52, 43.2, 20.1, 2, BLACK)
    p.label(40.7, 19.32, 'TALL PANTRY', px=17)
    p.label(40.7, 23.3, 'SCULLERY')
    p.change(2, (37.8, 18.5, 45.3, 27.3), "Scullery (7'-0\" x 8'-4\") replaces the pantry: sink, dishwasher, pantry wall, opening on its north side toward the kitchen.", at=(39.2, 25.6))
    # ------------------------------------------------ 6. pool
    p.white(49.5, 50.9, 65.35, 64.8)
    p.rect(47.3, 50.5, 60.3, 69.5, 3, BLACK, fill=WHITE)        # coping, 5'-0" off the north lot line
    p.rect(47.8, 51.0, 59.8, 69.0, 3, BLACK)                    # water, 12 x 18
    p.line([(47.8, 56.0), (59.8, 56.0)], 2, THIN, dash=(16, 10))
    p.label(53.8, 53.5, 'SUN SHELF', px=18)
    p.label(53.8, 62.5, 'POOL\n12\'-0" x 18\'-0"')
    p.change(6, (47.3, 50.5, 60.3, 69.5), "Pool 12' x 18' with a sun shelf (was about 7' x 12'), in FOR's court. It runs 2'-6\" past the rear wall line; the coping stops 5'-0\" off the north lot line. FOR's two loungers are not redrawn: the deck is 5'-4\" each side.", at=(48.7, 68.0))
    # ------------------------------------------------ 3, 4, 5. mudroom, two-car garage, storage
    p.white(62.27, 18.52, 69.12, 36.02)                         # laundry, its door wall, the old garage door and wall
    p.white(67.84, 18.52, 81.62, 38.52)                         # garage interior
    p.white(62.27, 36.0, 67.2, 38.9)
    p.white(81.6, 17.55, 82.36, 38.52)                          # old east wall at the garage
    p.white(69.3, 17.55, 82.36, 18.55)                          # old garage door wall
    p.white(82.32, 17.3, 87.6, 18.1)                            # fence line where the wall now stands
    p.erase_line_v(81.63, -15.4, 17.75)                         # old driveway edge; the lines that cross it stay
    p.wall(EW, 17.81, 87.5, 46.9)                               # new east wall
    p.wall(82.3, 46.23, 87.5, 46.9)                             # return to FOR's guest wing wall
    p.wall(85.33, 17.81, 87.5, 18.5); p.wall(67.16, 17.81, 69.33, 18.5)
    p.line([(69.33, 18.5), (85.33, 18.5)], 2, THIN); p.line([(69.33, 18.15), (85.33, 18.15)], 2, THIN, dash=(14, 8))
    p.line([(85.6, 17.8), (85.6, DRIVE_END)], 2, THIN)              # driveway edge for the 16' door
    p.wall(67.16, 18.5, 67.83, 35.5); p.wall(67.16, 38.5, 67.83, 39.22)     # garage west wall, 3'-0" door ahead of the cars
    p.wall(67.16, 38.53, 68.45, 39.22)
    p.door((67.5, 38.5), 3.0, 'S', 'W')
    p.wall(82.3, 38.53, 83.3, 39.22); p.wall(85.97, 38.53, EW, 39.22)       # storage door in the garage north wall
    p.door((83.3, 39.15), 2.67, 'E', 'N')
    p.rect(67.83, 35.5, 69.33, 38.5, 1, THIN)                   # step, as FOR drew it
    for cx in (69.4, 78.4): p.copy(72.75, 19.45, 79.8, 35.75, cx, 19.0)    # FOR's car, twice
    p.label(78.0, 37.3, 'GARAGE')
    p.label(84.55, 43.0, 'STOR.', px=19)
    p.rect(62.27, 19.2, 63.77, 31.0, 2, BLACK)                  # bench and lockers on the west wall
    for yy in (21.56, 23.92, 26.28, 28.64): p.line([(62.27, yy), (63.77, yy)], 1, FURN)
    p.label(63.02, 25.1, 'BENCH + LOCKERS', px=17, rotate=90)
    p.label(65.5, 28.0, 'MUD\nROOM')
    p.line([(62.27, 38.9), (67.16, 38.9)], 1, FURN, dash=(8, 6))
    p.change(3, (62.25, 18.5, 67.16, 38.9), "Mudroom (4'-11\" x 20'-4\") where the laundry was, open to the stair hall, with a bench and lockers. The garage door opens into it ahead of the cars.", at=(65.6, 20.2))
    p.change(4, [(67.83, 18.5, EW, 38.53), (81.8, 0.2, 85.6, 17.8)], "Two-car garage, 19'-0\" x 20'-0\" clear, 16'-0\" door, driveway widened to match. The east wall moves 5'-2\" to FOR's 7'-6\" setback line.", at=(77.3, 23.0))
    p.change(5, (82.3, 39.22, EW, 46.23), "Storage beside the stair, reached from the garage.", at=(84.5, 41.0))
    return p


def second(g):
    p = Plan(SRC2, 37.40, 1126, 3020)
    # ------------------------------------------------ 7. west bar 3'-0" wider (the planter ledge moves with the wall)
    p.slide(24.9, 17.3, 31.0, 21.75, dx=-DW, fill='tile')       # south planter
    p.slide(24.9, 21.75, 29.15, 28.69, dx=-DW, fill='smear')    # wall at the bath
    p.slide(24.9, 28.69, 29.6, 35.1, dx=-1.5, fill='smear')    # closets: his takes 1'-6" at the wall ...
    p.slide(23.4, 28.69, 46.5, 35.1, dx=-1.5, fill='smear')     # ... and hers 1'-6" as the passage moves over
    p.slide(24.9, 35.1, 45.6, 46.6, dx=-DW, fill='white')       # bedroom: bed, bench and chairs move with the wall
    p.slide(24.9, 46.6, 41.0, 47.9, dx=-DW, fill='smear')       # north wall
    p.slide(24.9, 47.9, 29.2, 63.5, dx=-DW, fill='smear')       # terrace
    p.slide(24.9, 63.5, 29.2, 67.6, dx=-DW, fill='tile')        # north planter
    p.change(7, [(25.2, 35.1, 28.3, 47.6), (25.2, 47.6, 28.3, 63.6)], "West wall moved 3'-0\" with the floor below. Master bedroom 22'-2\" wide (was 19'-2\"); the terrace grows with it.", at=(26.9, 36.5))
    # ------------------------------------------------ 8. wet room at the west end of the master bath
    p.white(25.97, 22.55, 34.5, 28.66)
    p.rect(34.1, 22.55, 34.32, 26.0, 2, BLACK, fill=WHITE)      # glass wall, moved 1'-6" east of FOR's; 2'-8" entry at the north end
    p.line([(34.21, 26.0), (34.21, 28.66)], 1, FURN, dash=(8, 6))
    p.line([(34.32, 24.33), (35.0, 24.33)], 2, THIN)            # vanity front line back to the glass
    p.rrect(26.2, 22.95, 28.8, 28.3, r=0.9, w=2, color=BLACK); p.ellipse(26.55, 23.45, 28.45, 27.8, 1, FURN)    # freestanding tub under the window
    p.ellipse(27.35, 27.4, 27.65, 27.7, 2, BLACK)
    p.line([(29.3, 22.6), (34.05, 28.6)], 1, FURN); p.line([(29.3, 28.6), (34.05, 22.6)], 1, FURN)              # shower floor, as FOR draws it
    p.rect(31.25, 25.18, 32.1, 26.03, 1, THIN, dash=(8, 5))
    p.copy(30.5, 22.56, 31.2, 23.2, 31.4, 22.56)                # FOR's shower valve, back on the south wall
    p.label(31.7, 27.9, 'WET ROOM', px=17, bg=True)
    p.change(8, (25.96, 22.5, 34.32, 28.7), "Wet room, 8'-1\" x 6'-2\": freestanding tub under the window and a 4'-9\" open shower (was a 3'-6\" shower, no tub). FOR's glass wall moves 1'-6\" east; the double vanity is 9'-10\" (was 11'-2\").", at=(33.0, 23.6))
    p.line([(41.6, 28.98), (44.4, 28.98)], 3, BLACK); p.line([(41.6, 28.72), (44.25, 28.72)], 3, BLACK)   # bath north wall made whole where the closet moved
    p.change(9, [(25.96, 28.95, 34.95, 34.65), (39.3, 28.95, 48.1, 34.65)], "His and her closets each 1'-6\" wider: about 8'-9\" x 5'-7\" (were 7'-4\").", at=(27.2, 33.6))
    # ------------------------------------------------ 10, 11. laundry between the baths; bath 3 and bedroom 3 move 5'-2" east
    p.slide(65.1, 17.3, 82.6, 21.75, dx=DE, fill='white')       # planter, then its gap filled from the moved piece
    p.copy(70.4, 17.3, 75.6, 21.75, 65.1, 17.3, from_orig=False)
    p.slide(65.1, 21.75, 82.6, 22.55, dx=DE, fill='smear')      # south wall
    p.slide(65.1, 22.55, 82.6, 32.45, dx=DE, fill='white')      # bath 3 and the bedroom
    p.slide(70.45, 32.45, 82.6, 36.1, dx=DE, fill='white')      # the bedroom beside its old entry
    p.slide(72.55, 36.1, 82.6, 38.95, dx=DE, fill='white')      # its closet
    p.white(82.36, 39.25, EW, 46.23)
    # laundry
    p.partition(69.85, 22.5, 70.3, 32.38)
    p.partition(70.25, 32.06, 75.65, 32.38)                     # bath 3's north wall, made whole after the move
    p.partition(64.95, 32.06, 67.2, 32.38); p.partition(69.87, 32.06, 70.3, 32.38)
    p.door((67.2, 32.1), 2.67, 'E', 'S')
    p.window(66.2, 21.82, 68.9, 22.51)
    p.copy_from(g, 65.87, 27.6, 68.24, 29.91, 65.13, 22.58); p.copy_from(g, 65.87, 25.27, 68.24, 27.58, 67.47, 22.58)   # FOR's washer and dryer
    p.rect(65.1, 26.6, 66.6, 29.4, 2, BLACK); p.rrect(65.3, 27.3, 66.4, 28.7, r=0.2, w=2, color=BLACK)   # sink counter on the west wall, 1'-8" clear of the machines
    p.label(68.25, 26.0, 'LAUNDRY', px=19)
    p.change(10, (65.1, 22.5, 69.85, 32.1), "Laundry room upstairs, 4'-9\" x 9'-7\", between Bath 4 and Bath 3: washer and dryer side by side, sink counter, window.", at=(68.6, 30.6))
    # corridor to bedroom 3
    p.white(66.96, 32.45, 70.44, 36.08); p.white(66.96, 36.1, 69.78, 36.6)
    p.line([(66.97, 36.35), (69.78, 36.35)], 1, FURN, dash=(8, 6))
    p.partition(75.3, 32.38, 75.65, 33.0); p.partition(75.3, 35.67, 75.65, 36.18)
    p.door((75.6, 33.0), 2.67, 'N', 'E')
    p.partition(72.57, 36.18, 72.9, 38.98); p.partition(75.3, 36.18, 75.65, 38.98)
    p.partition(72.57, 36.18, 72.95, 36.52); p.bifold(72.95, 75.3, 36.35, 'S')
    p.label(74.1, 37.75, 'STOR.', px=17)
    p.white(77.7, 36.56, 78.2, 38.94); p.partition(75.65, 36.18, 78.2, 36.52)
    p.line([(75.7, 37.67), (78.3, 37.67)], 1, FURN, dash=(14, 8))
    p.change(11, [(70.3, 22.5, EW, 36.2), (66.95, 32.4, 75.3, 36.2)], "Bath 3 and Bedroom 3 move 5'-2\" east, unchanged in size. Bedroom 3's entry becomes a short hall (3'-9\" wide) with a storage closet.", at=(73.0, 34.3))
    # east wall at the stair, bedroom 3 walk-in closet over the garage storage
    p.wall(EW, 38.9, 87.5, 46.9); p.wall(82.3, 46.23, 87.5, 46.9)
    p.white(83.3, 38.96, 85.9, 39.27)
    p.line([(85.6, 39.5), (85.6, 46.0)], 1, FURN, dash=(14, 8))
    p.label(84.2, 42.8, 'W.I.C.', px=19)
    p.change(12, (82.3, 39.25, EW, 46.23), "Walk-in closet for Bedroom 3 (4'-6\" x 7'-0\") in the widened bay beside the stair, opening off its reach-in closet.", at=(84.5, 45.0))
    return p


if __name__ == '__main__':
    g = ground(); g.save(os.path.join(OUT, 'f1_rev.png')); g.save_marked(os.path.join(OUT, 'f1_marked.png'))
    json.dump(g.changes, open(os.path.join(OUT, 'f1_changes.json'), 'w'), indent=1)
    u = second(g); u.save(os.path.join(OUT, 'f2_rev.png')); u.save_marked(os.path.join(OUT, 'f2_marked.png'))
    json.dump(u.changes, open(os.path.join(OUT, 'f2_changes.json'), 'w'), indent=1)
    print('done')
