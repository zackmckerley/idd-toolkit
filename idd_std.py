"""Drawing standards for the interior-design-drawings skill (Helios Development house standard).

Everything a sheet draws should take its weights, text sizes, sheet numbers and keynotes from here, so the set reads as one hand.
Units: points on a 22 x 17 in. sheet. Imperial throughout the drawings.
"""

# ---------------------------------------------------------------- line weights (pt), after AIA / NCS practice
LW = {
    'border': 1.2,        # sheet border, cut walls in section
    'heavy': 0.9,         # wall and floor lines in elevation, object outlines cut by the section plane
    'medium': 0.6,        # fixtures, cabinets, openings, finish extents
    'light': 0.4,         # trim detail, secondary edges, hatch boundaries
    'fine': 0.3,          # hatch lines, leaders, dimension lines, grid
    'hairline': 0.25,     # glazing reflection strokes, tile joints at small scale
}
DASH = {
    'hidden': '[3 2] 0',      # above the cut plane or behind the surface (soffits, TV, door swing)
    'extent': '[6 3] 0',      # finish extent lines in plan
    'center': '[8 2 1 2] 0',  # centerlines
}

# ---------------------------------------------------------------- text (Century Gothic subset embedded in the base plot)
TXT = {
    'sheet_title': 14.0, 'header': 11.0, 'view_title': 7.5, 'label': 9.4, 'tag': 5.8748, 'note': 7.6,
    'dim': 5.5, 'small': 5.0, 'keynote': 6.5, 'min': 5.0,     # nothing on a sheet below 5 pt (reads at 1/2 size prints)
}

# ---------------------------------------------------------------- colors (grayscale set; one accent for view numbers)
INK = (0.20, 0.20, 0.20); MID = (0.45, 0.45, 0.45); LIGHT = (0.70, 0.70, 0.70); HATCH = (0.78, 0.78, 0.78)
ACCENT = (0.85, 0.35, 0.10)
FILL_WALL = (0.35, 0.35, 0.35)

# ---------------------------------------------------------------- sheet numbering (NCS discipline ID, series by content)
SERIES = {
    '000': 'COVER SHEET, INDEX, SYMBOLS & GENERAL NOTES',
    '001': 'FINISH SCHEDULES',
    '100': 'FLOOR FINISH PLANS',
    '200': 'WALL FINISH PLANS',
    '300': 'REFLECTED CEILING PLANS',
    '400': 'LIGHTING & SWITCHING PLANS',
    '500': 'POWER & DATA PLANS',
    '600': 'FURNITURE PLANS',
    '700': 'INTERIOR ELEVATIONS',
    '800': 'MILLWORK & TYPICAL DETAILS',
}
def sheet_no(series, n):
    """ID-101 style: series 100 + sheet 1 -> ID-101."""
    return f"ID-{int(series) + n:03d}"

# ---------------------------------------------------------------- CSI MasterFormat keynotes used on the set
KEYNOTES = {
    '06 41 00': 'ARCHITECTURAL WOOD CASEWORK',
    '06 46 00': 'WOOD TRIM (BASE, CASING, CROWN)',
    '09 21 16': 'GYPSUM BOARD ASSEMBLIES',
    '09 30 00': 'TILING',
    '09 64 00': 'WOOD FLOORING',
    '09 72 00': 'WALL COVERINGS / WOOD PANELING',
    '09 75 00': 'STONE FACING',
    '09 91 23': 'INTERIOR PAINTING',
    '26 51 00': 'INTERIOR LIGHTING',
    '26 27 26': 'WIRING DEVICES',
}

# ---------------------------------------------------------------- residential mounting heights (in. AFF) used for checks and defaults
HEIGHTS = {
    'door_head': 96.0, 'window_head': 96.0, 'ceiling_f1': 120.0, 'ceiling_f2': 120.0,
    'counter': 36.0, 'bath_counter': 34.0, 'upper_cab_bottom': 54.0, 'backsplash_top': 54.0,
    'mirror_bottom': 40.0, 'sconce': 66.0, 'towel_bar': 48.0, 'robe_hook': 66.0, 'tp_holder': 26.0,
    'shower_head': 80.0, 'shower_valve': 48.0, 'tub_valve': 30.0, 'grab_bar_blocking': (33.0, 36.0),
    'receptacle': 15.0, 'counter_receptacle': 42.0, 'switch': 42.0, 'tv_center': 42.0, 'tv_center_bed': 50.0,
    'chair_rail': 40.0, 'base': 8.5, 'crown': 8.0, 'tempered_zone_tub': 60.0, 'shower_tile_min': 72.0,
}

# ---------------------------------------------------------------- TRIM block (skill: Trim and paneling proportions), sized from the ceiling height
def trim_for(ceiling=120.0):
    """Luxury default = upper half of each range. Base 7 percent of ceiling (rounded to 1/4), crown 0.8 to 1.1 x base and under 10 percent,
    crown plus base under 15 percent, casing 50 to 60 percent of base, cap 2-1/2 to 3-1/2 (never wider than the casing), picture-frame molding
    1-3/4 to 2-1/4 at 10 ft and up, one 4 in. margin, low wainscot cap at one third, tall wainscot 60 to 67 percent."""
    c = float(ceiling)
    base = round(c * 0.07 * 4) / 4                       # 8-1/2 at 10 ft (range 7-3/4 to 9)
    crown = min(round(base * 0.95 * 4) / 4, c * 0.10)    # 8 at 10 ft (range 7 to 9); over 7 is built up
    if crown + base > c * 0.15: crown = c * 0.15 - base
    casing = round(base * 0.58 * 4) / 4                  # 5 at 10 ft (range 4-1/2 to 5-1/2)
    return {'ceiling': c,
            'base': base,                                # base height, shoe excluded
            'crown': crown,                              # crown drop
            'crown_proj': round(crown * 0.9 * 4) / 4,    # projection 0.8 to 1.0 x drop
            'crown_built_up': crown > 7.0,               # bed mould + crown + frieze board when over 7 in.
            'casing': casing,                            # casing face with backband
            'casing_thick': 1.0,                         # casing at least 1/8 thicker than the base (base 7/8)
            'cap': 3.0,                                  # chair rail or wainscot cap
            'panel_mold': 2.0 if c >= 120 else 1.375,    # picture-frame molding face
            'margin': 4.0,                               # one margin per room: between boxes, above the base cap, below the cap, at corners and casings
            'dado': round(c / 3.0),                      # low wainscot, top of cap (one third)
            'tall': (round(c * 0.60), round(c * 0.67)),  # tall wainscot range, top of cap
            'stile': 3.5,                                # frame-and-panel stile (3 to 4-1/2)
            'head_clear_min': 4.0}                       # wall between head casing and crown: zero or at least 4 in.
TRIM = trim_for(HEIGHTS['ceiling_f2'])

# ---------------------------------------------------------------- sheet purity: what each sheet type may show
SHEET_CONTENT = {
    '100': {'show': ['floor finish fills', 'borders', 'transitions', 'floor finish tags', 'room names'], 'hide': ['dimensions', 'furniture', 'rugs', 'wall finish tags', 'ceiling', 'electrical']},
    '200': {'show': ['wall finish tags', 'extent lines', 'elevation markers', 'room names'], 'hide': ['dimensions', 'furniture', 'rugs', 'floor fills', 'ceiling', 'electrical']},
    '300': {'show': ['ceiling heights', 'soffits', 'crown', 'ceiling finish tags', 'fixture symbols'], 'hide': ['dimensions', 'furniture', 'floor fills', 'wall finish tags']},
    '400': {'show': ['lighting fixtures', 'switches', 'circuits (dashed)', 'fixture tags'], 'hide': ['dimensions', 'furniture (except as light reference)', 'floor fills', 'finish tags']},
    '500': {'show': ['receptacles', 'data', 'GFCI', 'USB', 'mounting heights'], 'hide': ['dimensions', 'floor fills', 'finish tags', 'lighting']},
    '600': {'show': ['furniture', 'rugs', 'clearances', 'furniture tags'], 'hide': ['dimensions', 'floor fills', 'finish tags', 'electrical']},
    '700': {'show': ['wall elevations', 'finish tags', 'dimension strings', 'mounting heights', 'keynotes'], 'hide': ['plan content']},
    '800': {'show': ['details at 1-1/2 in. or 3 in.', 'keynotes', 'dimensions'], 'hide': ['plan content']},
}

PROJECT = {'name': 'CASA GROVE', 'address1': '3350 THOMAS AVE', 'address2': 'COCONUT GROVE, FL 33133', 'no': 'HD102', 'date': '11.01.26',
           'issue': ('FOR PRICING & COORDINATION', 'NOT FOR PERMIT'), 'base': 'FOR ARCHITECTURE CO.', 'drawn': 'ZM', 'checked': 'ZM',
           'base_set': 'FOR ARCHITECTURE CO. ARCHITECTURAL SET', 'base_date': 'LATEST ISSUE ON FILE, VERIFY BEFORE PRICING',
           'designer_set': 'YL DESIGNS SET YLD.068, 09.25.26'}
