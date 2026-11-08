# Casa Grove (HD102): rendering plan

Status 11.07.26: prepared, not rendered (owner: "get ready").

## Where the renderings go in the set

Each room block runs x0 key plan, x1 to x7 drawings, x8 and x9 renderings. The cover index lists the rendering sheets as TBD.

| Sheet | View | Camera (eye 5'-3" AFF, 24 mm equivalent) | Shows |
|---|---|---|---|
| ID-218 | Entry | In the front door opening, looking in | Vintage mirror wall, stair, the powder room door |
| ID-219 | Powder room | In the door, looking at the vanity | WC-02 wallcovering, floating vanity, framed mirror, bar light |
| ID-238 | Living room, fireplace wall | At the sofa on the gallery line, looking east | The fireplace wall option the owner picks (ID-235/236), TV, art, built-ins |
| ID-239 | Living room, double height | At the fireplace, looking west and up | Gallery with the painted steel guard, clerestory, the slider |
| ID-248 | Kitchen, range wall | In the dining area, looking west | Range, plaster hood, stone shelves with LED, island waterfall |
| ID-249 | Kitchen, refrigerator run and pantry | At the range, looking northeast | Veneer refrigerator run, swing doors into the pantry, arch |
| ID-258 | Mudroom | In the back hall, looking at the lockers | Lockers, shoe drawers, coat closet doors |
| ID-268 | Guest bedroom and bath | In the bedroom door | Dado wainscot with WC-01, bed wall, the bath door |
| ID-318 | Master bedroom | At the nook, looking at the headboard wall | Full-height paneling, bed, sconces |
| ID-319 | Reading nook | At the bed, looking south | Terrace doors, bookcase, art with picture light |
| ID-328 | Master bath, vanities | At the tub alcove, looking north | Two furniture vanities, framed mirrors, wall faucets |
| ID-329 | Master bath, tub alcove | At the vanities, looking south | Freestanding tub, WT-02 slab, shower glass |
| ID-348 | Bedroom 2 and bath 2 | In the bedroom door | Bed wall, wainscot, built-ins |
| ID-358 | Bedroom 3 and bath 3 | In the bedroom door | Bed wall, wainscot, window wall |

16 views. Before any renders go out, each camera is drawn on its room's key plan as a camera symbol with a view cone, labeled with the rendering's sheet number.

## How the scenes get built

Nothing is modeled by hand. The scene is generated from the same data as the drawings:
- Room shells come from FOR REV 1, the same room polygons the finish plans use (rev1/rooms_rev1.py). Walls are extruded to the ceiling heights on the sheets: 10'-0" assumed, living room 22'-10" (VERIFY).
- Every elevation is already a wall in its own coordinates: the wall length, openings (x, width, head, sill) and items (cabinets, vanities, mirrors, sconces, paneling, tile zones). A wall's plan position takes it into 3D, so what is drawn is exactly what is rendered.
- Trim comes from the trim block (idd_std.trim_for): base 8-1/2", crown 8" built up, casing 5", wainscot cap at 3'-4".
- Materials come from the finish codes: one material per code, so a changed pick changes every render that uses it.

## Tool chain

The renderer is Blender 4.2 (the bpy module) in /home/claude/rendervenv, running Python 3.11 headless. The engine is Cycles on the CPU with denoising.
- The smoke test (render/smoke_test.py, a 12' x 14' room at 640 x 400 with 32 samples) took 31 s.
- Estimated per final view, at 2400 x 1500 with 128 samples: about 25 to 30 min. That is about 8 hours for all 16 views, so they run in batches.
- To do before the first real render: AgX view transform with a calibrated exposure, a sky texture and sun for the Coconut Grove latitude, area lights at the fixture locations on the lighting design, and glass and metal materials.

## Material table (finish code to render material)

| Code | Material | Status |
|---|---|---|
| WD-01 | Wood floor, field, finish T.B.C. | Species and stain open |
| WD-02 | Wood border | Follows WD-01 |
| TL-01 | Checkered porcelain, entry and pantry | Tile pick open |
| TL-02, TL-03, TL-04 | Porcelain | Tile picks open |
| ST-01 | Honed marble, stair landing and hearth | Slab open |
| ST-02 | Emerald green marble, powder room floor (option) | Open |
| ST-03 | Kitchen and pantry stone | Slab open |
| PT-01 | SW 7005 Pure White | Decided |
| PT-02 | SW 5971 Solstice (option 2: SW 9583 Sanctuary) | Draw-downs open |
| PT-03 | BM 2041-10 Hunter Green, high-gloss lacquer | Helios proposal |
| WC-01 | Bedroom wallpaper | Pattern open |
| WC-02 | Dark-ground botanical with a metallic line | Sample to approve |
| WS-01 | Light marble, fireplace | Slab open |
| WP-01, WP-02 | Painted paneling | Color follows PT |
| WT-01 | Wall tile, secondary baths | Open |
| WT-02 | 48" x 96" porcelain slab, master bath | Product open |
| FR-01 | White pebbled FRP, dog room | Decided |
| Cabinets | Kitchen painted (color open), north run rift white oak veneer (stain open), pantry greige | Open |
| Metals | Kitchen brass, pantry nickel | Confirm |

## Picks that block a faithful render

Until these are picked, a render shows a placeholder and says so in its caption:
1. Living room fireplace wall option (ID-235/236). Megan is reviewing.
2. Wood floor species and stain.
3. Kitchen cabinet color, veneer stain, stone, hardware, range and hood.
4. PT-02 draw-down (Solstice or Sanctuary).
5. WC-01 and WC-02 patterns.
6. Bath tile and slab products (WT-01, WT-02, TL-02, TL-03).
7. Light fixtures: sconces, pendants, chandeliers. The lighting plans are still on the YL base.
8. Furniture for the living room, bedrooms and dining. No layout exists for floor 1.

## Rendering sheet layout (template)

One sheet per view on the 17:11 sheet:
- The rendering about 1,300 x 810 pt, the main thing on the sheet.
- A strip on the right: a small key plan with the camera and its cone, then the finish codes visible in the view, each with a swatch and its status (PICKED or PLACEHOLDER).
- The title block carries the sheet title only. Renderings are not to scale, so SCALE reads NOT TO SCALE.
