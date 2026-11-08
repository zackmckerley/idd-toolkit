"""Quantity takeoff workbook from the room model and the finish rules of the set (for pricing).
Sheets: Inputs (waste, coverage, tile sizes), Floors (SF by room and finish), Walls (SF by wall and finish code, openings deducted),
Trim (base and crown LF), Summary (by code with waste, tile counts and paint gallons), Electrical (counts).
Every quantity on Summary is a formula over the detail sheets; the detail sheets carry the measured numbers with their source."""
import json, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from shapely.geometry import Polygon
import build_elev as BE
from idd_electrical import FIXTURES, DEVICES

PT_PER_FT = 13.5
OUT = '/home/claude/flrwork/261101.HD102.Takeoff.xlsx'
FLOOR_FIN = {'KITCHEN & DINING AREA': 'WD-01', 'PANTRY': 'TL-01', 'GREAT ROOM': 'WD-01', 'PIANO ROOM': 'WD-01', 'FOYER': 'TL-01', 'POWDER ROOM': 'ST-02',
             'GUEST BEDROOM': 'WD-01', 'GUEST BATH': 'TL-02', 'GUEST CLOSET': 'WD-01', 'LAUNDRY': 'TL-04', 'SERVICE AREA': 'TL-04', 'PET AREA': 'TL-04', 'OFFICE': 'WD-01',
             'BEDROOM 3': 'WD-01', 'BATH 3': 'TL-02', 'BATH 2': 'TL-02', 'BEDROOM 2': 'WD-01', 'DEN / PLAYROOM': 'WD-01', 'W.I.C.': 'WD-01', 'MASTER BATHROOM': 'TL-03',
             'MASTER SUITE': 'WD-01', 'HALL': 'WD-01', 'LINEN CLOSET': 'WD-01', 'HIDDEN SAFE': 'WD-01'}
BORDER_ROOMS = {'GREAT ROOM': 'WD-02', 'PIANO ROOM': 'WD-02', 'GUEST BEDROOM': 'WD-02', 'MASTER SUITE': 'WD-02', 'HALL': 'WD-02'}
CODES = ['WD-01', 'WD-02', 'SL-01', 'TL-01', 'TL-02', 'TL-03', 'TL-04', 'ST-01', 'ST-02', 'PT-01', 'PT-02', 'PT-03', 'CM-01', 'WS-01', 'WP-01', 'WP-02', 'WT-01', 'WT-02']

HDR = Font(name='Arial', bold=True, color='FFFFFF'); HFILL = PatternFill('solid', fgColor='404040')
BODY = Font(name='Arial', size=10); INPUT = Font(name='Arial', size=10, color='0000FF'); BOLD = Font(name='Arial', size=10, bold=True)
YEL = PatternFill('solid', fgColor='FFFF00'); THIN = Side(style='thin', color='BBBBBB')

def header(ws, row, cols, widths=None):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c); cell.font = HDR; cell.fill = HFILL; cell.alignment = Alignment(wrap_text=True, vertical='center')
        if widths: ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
    ws.freeze_panes = ws.cell(row=row + 1, column=1)

def build():
    wb = Workbook()
    # ---------------- Inputs
    wi = wb.active; wi.title = 'Inputs'
    wi['A1'] = 'CASA GROVE  HD102  QUANTITY TAKEOFF  11.01.26'; wi['A1'].font = Font(name='Arial', bold=True, size=12)
    wi['A2'] = 'Blue cells are inputs; change waste factors, tile sizes and coverage here. All other sheets are formulas over the measured detail sheets.'; wi['A2'].font = BODY
    header(wi, 4, ['Input', 'Value', 'Unit', 'Note'], [34, 12, 10, 90])
    inputs = [('Waste, wood flooring', 0.10, 'fraction', 'Straight lay. Herringbone in the master suite: use 0.15'), ('Waste, tile floors', 0.12, 'fraction', 'Diagonal checker in foyer and pantry: 0.15'),
              ('Waste, wall tile', 0.12, 'fraction', ''), ('Waste, stone slabs', 0.25, 'fraction', 'Book-matched slabs, verify with the fabricator'), ('Waste, paneling', 0.10, 'fraction', ''),
              ('Waste, trim', 0.10, 'fraction', ''), ('Paint coverage', 350, 'SF per gal per coat', 'Manufacturer data, eggshell on Level 4 gypsum'), ('Paint coats', 2, 'coats', 'Plus one primer coat, same coverage'),
              ('Wall tile module', 2.0, 'SF per piece', '12 x 24 nominal, revise when the tile is selected'), ('Floor tile module', 4.0, 'SF per piece', '24 x 24 nominal (TL-04); revise per selection'),
              ('Base height', 5.5, 'in', 'Detail 1, ID-801'), ('Crown drop', 5.5, 'in', 'Detail 5, ID-801'), ('Door head', 96, 'in', 'Assumed, verify with the architectural set'), ('Ceiling, typical', 120, 'in', 'Assumed, verify')]
    for i, (k, v, u, n) in enumerate(inputs, 5):
        wi.cell(row=i, column=1, value=k).font = BODY; c = wi.cell(row=i, column=2, value=v); c.font = INPUT; c.fill = YEL; wi.cell(row=i, column=3, value=u).font = BODY; wi.cell(row=i, column=4, value=n).font = BODY
    INP = {k: f"Inputs!$B${i}" for i, (k, _, _, _) in enumerate(inputs, 5)}

    # ---------------- Floors
    wf = wb.create_sheet('Floors')
    header(wf, 1, ['Floor', 'Room', 'Floor finish', 'Net area (SF)', 'Perimeter (LF)', 'Border code', 'Border LF', 'Source'], [7, 26, 12, 14, 14, 12, 12, 60])
    r = 2
    for floor in (1, 2):
        model = json.load(open(f'model_f{floor}.json'))
        for room in model['rooms']:
            poly = Polygon(room['poly_pt']); sf = poly.area / PT_PER_FT ** 2; per = poly.length / PT_PER_FT
            vals = [floor, room['name'], FLOOR_FIN.get(room['name'], 'TBC'), round(sf, 1), round(per, 1), BORDER_ROOMS.get(room['name'], ''), None, f'model_f{floor}.json polygon from the architectural base; room area to the wall faces']
            for c, v in enumerate(vals, 1): wf.cell(row=r, column=c, value=v).font = BODY
            wf.cell(row=r, column=7, value=f'=IF(F{r}="","",E{r})').font = BODY
            r += 1
    FL_LAST = r - 1
    wf.cell(row=r + 1, column=2, value='Areas are net room areas inside the finished walls. Stair, landings and exterior spaces are not included; add the stair treads and risers (WD-01) and the landings (ST-01) from the architectural stair section.').font = BODY

    # ---------------- Walls
    ww = wb.create_sheet('Walls')
    header(ww, 1, ['Floor', 'Room', 'Wall', 'Length (in)', 'Height (in)', 'Gross (SF)', 'Openings (SF)', 'Net (SF)', 'Finish code', 'Finish SF', 'Base LF', 'Crown LF', 'Elevation'], [7, 24, 7, 11, 11, 11, 12, 11, 12, 11, 10, 10, 12])
    ix = json.load(open('elev_index.json')); ixmap = {(v['floor'], v['room'], v['wall']): f"{v['number']} / {v['sheet']}" for v in ix}
    r = 2
    for floor in (1, 2):
        model = json.load(open(f'model_f{floor}.json'))
        for room in model['rooms']:
            for w in room['walls']:
                if w.get('guard'): continue
                spec = BE.wall_spec(floor, room, w, room['fixtures'])
                L, H = w['length_in'], room['ceiling_in']
                open_sf = sum(o['w'] * (o['head'] - o.get('sill', 0)) for o in spec['openings']) / 144.0
                door_in = sum(o['w'] for o in spec['openings'] if o.get('sill', 0) == 0)
                fins = [f for f in spec['finishes'] if f['code'] != 'CM-01']
                # one row per finish zone on the wall; paint rows take the wall net minus the special zones
                special = [f for f in fins if not f['code'].startswith('PT')]
                special_sf = sum((f['x1'] - f['x0']) * (f['y1'] - f['y0']) for f in special) / 144.0
                rows = [(f['code'], (f['x1'] - f['x0']) * (f['y1'] - f['y0']) / 144.0) for f in special]
                paint = [f for f in fins if f['code'].startswith('PT')]
                if paint: rows.append((paint[0]['code'], None))     # formula: net minus special
                first = True
                for code, sf in rows:
                    vals = [floor, room['name'], w['id'], round(L, 1), H, None, round(open_sf, 1), None, code, None, None, None, ixmap.get((floor, room['name'], w['id']), '')]
                    for c, v in enumerate(vals, 1): ww.cell(row=r, column=c, value=v).font = BODY
                    ww.cell(row=r, column=6, value=f'=D{r}*E{r}/144').font = BODY
                    ww.cell(row=r, column=8, value=f'=F{r}-G{r}').font = BODY
                    if sf is None:
                        ww.cell(row=r, column=10, value=f'=MAX(0,H{r}-{round(special_sf, 1)})').font = BODY
                    else:
                        ww.cell(row=r, column=10, value=round(sf, 1)).font = BODY
                    if first:
                        ww.cell(row=r, column=11, value=f'=(D{r}-{round(door_in, 1)})/12').font = BODY
                        ww.cell(row=r, column=12, value=f'=D{r}/12' if spec['crown'] else 0).font = BODY
                    first = False
                    r += 1
    WL_LAST = r - 1
    ww.cell(row=r + 1, column=2, value='Lengths and openings from the room model (architectural base), heights from Inputs. Special finish zones (tile, stone, paneling) are the extents drawn on the interior elevations; the paint row of each wall is the remainder.').font = BODY

    # ---------------- Summary
    ws = wb.create_sheet('Summary', 0)
    ws['A1'] = 'CASA GROVE  HD102  TAKEOFF SUMMARY (FOR PRICING)'; ws['A1'].font = Font(name='Arial', bold=True, size=12)
    ws['A2'] = 'Measured from the Helios interior design set 11.01.26. Quantities are net plus the waste factors on Inputs. Verify against the architectural set before ordering.'; ws['A2'].font = BODY
    header(ws, 4, ['Code', 'Material', 'Unit', 'Net quantity', 'Waste', 'Order quantity', 'Pieces / gallons', 'Basis'], [9, 44, 8, 14, 9, 16, 16, 70])
    mats = {'WD-01': ('Wood floor, field', 'SF', 'Waste, wood flooring', f"=SUMIFS(Floors!$D$2:$D${FL_LAST},Floors!$C$2:$C${FL_LAST},A{{r}})", None, 'Floors: net room SF, rooms finished WD-01 (borders included in the field SF)'),
            'WD-02': ('Wood floor border, single board', 'LF', 'Waste, trim', f"=SUMIFS(Floors!$G$2:$G${FL_LAST},Floors!$F$2:$F${FL_LAST},A{{r}})", None, 'Floors: room perimeter where a border is drawn on ID-101 / 102'),
            'SL-01': ('Schluter brass strip', 'LF', 'Waste, trim', f"=SUMIFS(Floors!$G$2:$G${FL_LAST},Floors!$B$2:$B${FL_LAST},\"PIANO ROOM\")+SUMIFS(Floors!$G$2:$G${FL_LAST},Floors!$B$2:$B${FL_LAST},\"GREAT ROOM\")", None, 'Floor 1 border strips at the great room and piano room per ID-101'),
            'TL-01': ('Porcelain tile, foyer and pantry', 'SF', 'Waste, tile floors', f"=SUMIFS(Floors!$D$2:$D${FL_LAST},Floors!$C$2:$C${FL_LAST},A{{r}})", 'Floor tile module', 'Floors'),
            'TL-02': ('Porcelain tile, guest bath, baths 2 and 3', 'SF', 'Waste, tile floors', f"=SUMIFS(Floors!$D$2:$D${FL_LAST},Floors!$C$2:$C${FL_LAST},A{{r}})", 'Floor tile module', 'Floors'),
            'TL-03': ('Porcelain tile, master bath', 'SF', 'Waste, tile floors', f"=SUMIFS(Floors!$D$2:$D${FL_LAST},Floors!$C$2:$C${FL_LAST},A{{r}})", 'Floor tile module', 'Floors'),
            'TL-04': ('Porcelain tile, laundry, service, pet area', 'SF', 'Waste, tile floors', f"=SUMIFS(Floors!$D$2:$D${FL_LAST},Floors!$C$2:$C${FL_LAST},A{{r}})", 'Floor tile module', 'Floors'),
            'ST-01': ('Marble, stair landings', 'SF', 'Waste, stone slabs', "=0", None, 'Not in the room model: measure from the architectural stair plan'),
            'ST-02': ('Marble, powder room floor', 'SF', 'Waste, stone slabs', f"=SUMIFS(Floors!$D$2:$D${FL_LAST},Floors!$C$2:$C${FL_LAST},A{{r}})", None, 'Floors'),
            'PT-01': ('Paint, walls (foyer) and all ceilings', 'SF', None, f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})+SUM(Floors!$D$2:$D${FL_LAST})", 'Paint coverage', 'Walls tagged PT-01 plus ceiling SF (= floor SF); trim and doors not included'),
            'PT-02': ('Paint, walls, eggshell', 'SF', None, f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", 'Paint coverage', 'Walls: net wall SF tagged PT-02 (openings deducted, special finishes deducted)'),
            'PT-03': ('Paint, powder room walls', 'SF', None, f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", 'Paint coverage', 'Walls'),
            'CM-01': ('Crown molding', 'LF', 'Waste, trim', f"=SUM(Walls!$L$2:$L${WL_LAST})", None, 'Walls: wall length of every crowned wall (closets excluded)'),
            'BASE': ('Wood base', 'LF', 'Waste, trim', f"=SUM(Walls!$K$2:$K${WL_LAST})", None, 'Walls: wall length less door openings'),
            'WS-01': ('Stone, great room fireplace wall', 'SF', 'Waste, stone slabs', f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", None, 'Walls: stone zone on the great room east elevation'),
            'WP-01': ('Painted paneling, great room', 'SF', 'Waste, paneling', f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", None, 'Walls'),
            'WP-02': ('Painted paneling, master headboard wall', 'SF', 'Waste, paneling', f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", None, 'Walls'),
            'WT-01': ('Wall tile, guest bath, baths 2 and 3', 'SF', 'Waste, wall tile', f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", 'Wall tile module', 'Walls: tub alcove walls to the ceiling'),
            'WT-02': ('Wall tile, master bath', 'SF', 'Waste, wall tile', f"=SUMIFS(Walls!$J$2:$J${WL_LAST},Walls!$I$2:$I${WL_LAST},A{{r}})", 'Wall tile module', 'Walls: shower and tub alcove walls to the ceiling')}
    r = 5
    for code, (name, unit, waste_key, net_formula, piece_key, basis) in mats.items():
        ws.cell(row=r, column=1, value=code).font = BOLD; ws.cell(row=r, column=2, value=name).font = BODY; ws.cell(row=r, column=3, value=unit).font = BODY
        ws.cell(row=r, column=4, value=net_formula.replace('{r}', str(r))).font = BODY
        ws.cell(row=r, column=5, value=f'={INP[waste_key]}' if waste_key else 0).font = BODY
        ws.cell(row=r, column=6, value=f'=D{r}*(1+E{r})').font = BOLD
        if piece_key == 'Paint coverage':
            ws.cell(row=r, column=7, value=f'=ROUNDUP(D{r}/{INP["Paint coverage"]}*({INP["Paint coats"]}+1),0)').font = BODY
        elif piece_key:
            ws.cell(row=r, column=7, value=f'=ROUNDUP(F{r}/{INP[piece_key]},0)').font = BODY
        ws.cell(row=r, column=8, value=basis).font = BODY
        for c in range(4, 8): ws.cell(row=r, column=c).number_format = '#,##0.0' if c != 5 else '0%'
        r += 1
    ws.cell(row=r + 1, column=1, value='Pieces / gallons: tile pieces at the module on Inputs; paint gallons = net SF / coverage x (coats + primer).').font = BODY
    ws.cell(row=r + 2, column=1, value='Not measured here: stair treads, risers and landings, exterior terraces, closet shelving, countertops, cabinets (per shop drawings), doors and hardware.').font = BODY

    # ---------------- Electrical
    we = wb.create_sheet('Electrical')
    header(we, 1, ['Type', 'Description', 'Floor 1', 'Floor 2', 'Total', 'Source'], [8, 60, 9, 9, 9, 50])
    r = 2
    cnt = {f: json.load(open(f'electrical_f{f}.json')) for f in (1, 2)}
    for code, (fam, desc, mount) in FIXTURES.items():
        n = {f: sum(1 for o in cnt[f]['lights'] if o['type'] == code) for f in (1, 2)}
        if code == 'UC': n = {f: sum(round(o.get('len_in', 0) / 12) for o in cnt[f]['lights'] if o['type'] == code) for f in (1, 2)}; desc += ' (LF)'
        for c, v in enumerate([code, desc, n[1], n[2], None, 'ID-301/302, ID-401/402 rule-based layout'], 1): we.cell(row=r, column=c, value=v).font = BODY
        we.cell(row=r, column=5, value=f'=C{r}+D{r}').font = BOLD; r += 1
    for code, desc in DEVICES.items():
        n = {f: sum(1 for o in cnt[f]['power'] + cnt[f]['switches'] if o['type'] == code) for f in (1, 2)}
        for c, v in enumerate([code, desc, n[1], n[2], None, 'ID-401/402, ID-501/502 rule-based layout'], 1): we.cell(row=r, column=c, value=v).font = BODY
        we.cell(row=r, column=5, value=f'=C{r}+D{r}').font = BOLD; r += 1
    wb.save(OUT); print('saved', OUT)

if __name__ == '__main__':
    build()
