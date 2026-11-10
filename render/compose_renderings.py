"""Rendering sheets for the review set (render plan: each room block's x8 sheet). One rendering per 17:11 sheet with the
Helios title block, the finishes visible in the view and whether each is the owner's pick or a placeholder.
Usage: python3 render/compose_renderings.py  ->  261109.HD102.Renderings.pdf"""
import sys, os
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
from PIL import Image
from idd_sheet import Sheet, FR, TB_X, fix_soft_hyphen
from idd_std import INK, MID

OUT = '/home/claude/flrwork/261109.HD102.Renderings.pdf'
SHEETS = [
    ('ID-219', 'POWDER ROOM', '/tmp/rc/powder_final.png', 'FROM THE DOOR, LOOKING AT THE VANITY',
     [('CALACATTA VIOLA MARBLE, VANITY TOP AND SPLASH', 'OWNER PICK 11.09.26'), ('WC-02 WALLCOVERING (DARK GROUND, SHOWN PLAIN)', 'PATTERN OPEN'),
      ('PT-04 LOWER WALL, DEEP COLOR', 'COLOR OPEN'), ('FLOATING VANITY, WHITE OAK', 'PLACEHOLDER'), ('BRASS FAUCET, MIRROR FRAME, SCONCE', 'PLACEHOLDER')]),
    ('ID-248', 'KITCHEN', '/tmp/rc/kitchen_final.png', 'FROM THE SLIDER, LOOKING WEST AT THE RANGE WALL',
     [('CALACATTA MONET MARBLE, COUNTERS AND WATERFALL ISLAND', 'OWNER PICK 11.09.26'), ('BACKSPLASH TILE, LIGHT NEUTRAL GLAZED 4x12', 'OWNER: NEUTRAL, PRODUCT OPEN'),
      ('CABINET PAINT, WARM WHITE', 'PLACEHOLDER'), ('NORTH RUN, RIFT WHITE OAK VENEER', 'STAIN OPEN'), ('PLASTER HOOD, 48" RANGE', 'PER ID-240 SET'),
      ('WIDE PLANK WHITE OAK FLOOR', 'SPECIES AND STAIN OPEN'), ('PENDANTS, STOOLS', 'PLACEHOLDER')]),
    ('ID-318', 'MASTER BEDROOM', '/tmp/rc/mbr_final.png', 'FROM THE SOUTHWEST CORNER, LOOKING AT THE HEADBOARD WALL',
     [('FULL-HEIGHT PANELING, PT-02', 'PER ID-310 SET'), ('HERRINGBONE WHITE OAK FLOOR', 'SPECIES AND STAIN OPEN'),
      ('BED, NIGHTSTANDS, LAMPS, RUG', 'STAGING'), ('SCONCES', 'FIXTURE OPEN')]),
    ('ID-328', 'MASTER BATH', '/tmp/rc/bath_final.png', 'FROM THE TUB ALCOVE, LOOKING NORTHWEST',
     [('CALACATTA MONET MARBLE, VANITY TOPS', 'OWNER PICK 11.09.26'), ('ARCHED PAIR TO THE CLOSET, DOOR 19A', 'OWNER 11.09.26'),
      ('FURNITURE VANITIES, PAINTED', 'COLOR OPEN'), ('POLISHED NICKEL FITTINGS, SCONCES', 'PLACEHOLDER'), ('WOOD FLOOR', 'SPECIES AND STAIN OPEN')]),
    ('ID-338', 'MASTER CLOSET', '/tmp/rc/closet_final2.png', 'FROM DOOR 19A, LOOKING NORTH AT THE PURSE SHOWCASE',
     [('CALACATTA MONET MARBLE, WATERFALL ISLAND AND VANITY', 'OWNER PICK 11.09.26'), ('MW-01 GREIGE MATTE MILLWORK', 'COLOR OPEN'),
      ('MW-02 SHAGREEN-LOOK DRAWER FRONTS', 'SAMPLE OPEN'), ('ONE-PIECE GLASS SHOWCASE SHELVES, LINEN BACK', 'PER ID-331'),
      ('BRONZE RODS, PULLS, GLASS DOOR FRAMES', 'FINISH OPEN'), ('CH1 CHANDELIER', 'FIXTURE OPEN'), ('CLOTHES, BAGS, SHOES', 'STAGING')]),
    ('ID-408', 'POOL HOUSE', '/tmp/rc/pool_final.png', 'LOUNGE AND OFFICE, FROM THE NORTHWEST CORNER',
     [('WAINSCOT PANELING, PT-01 TRIM', 'PER ID-400 SET'), ('PT-05 LIMEWASH', 'COLOR OPEN'), ('ST-05 HONED LIMESTONE FLOOR', 'STONE OPEN'),
      ('SOFA, TABLE, TV, RUG', 'STAGING')]),
]


def build():
    doc = fitz.open(); made = []
    for num, room, png, view, rows in SHEETS:
        if not os.path.exists(png): print('missing', png); continue
        jpg = png.replace('.png', '.jpg'); Image.open(png).convert('RGB').save(jpg, quality=92)
        sh = Sheet(doc); sh.frame(room, 'NOT TO SCALE', [room, 'RENDERING'], num, legend_rule=False)
        x0, y0, x1, y1 = FR.x0 + 18, FR.y0 + 18, TB_X - 18, FR.y1 - 18
        im = Image.open(jpg); ar = im.width / im.height
        iw = x1 - x0; ih = iw / ar
        if ih > (y1 - y0) - 150: ih = (y1 - y0) - 150; iw = ih * ar
        r = fitz.Rect(x0, y0 + 26, x0 + iw, y0 + 26 + ih)
        sh.p.insert_image(r, filename=jpg)
        sh.text(x0, y0 + 14, '%s, %s' % (room, view), 13, INK, serif=True, raw=True)
        sh.text(x0, r.y1 + 16, 'RENDERED FROM THE DRAWINGS (3-D MODEL BUILT FROM THE ELEVATIONS AND PLANS). NOT TO SCALE. STAGING AND PLACEHOLDER FINISHES ARE NOT SELECTIONS.', 7.5, MID, raw=True)
        cy0 = r.y1 + 40
        sh.text(x0, cy0, 'FINISHES IN THIS VIEW', 9, INK, bold=True, raw=True)
        colw = (x1 - x0) / 4
        for i, (name, status) in enumerate(rows):
            cx = x0 + (i % 4) * colw; cy = cy0 + 18 + (i // 4) * 34
            sh.text(cx, cy, name, 7.5, INK, raw=True); sh.text(cx, cy + 11, status, 7.0, MID, bold=True, raw=True)
        made.append(num)
    fix_soft_hyphen(doc); doc.save(OUT, garbage=3, deflate=True); print('saved', OUT, made)


if __name__ == '__main__':
    build()
