"""Assemble the full Casa Grove interior design set in sheet order with bookmarks and metadata."""
import json, pymupdf as fitz, collections
PARTS = [('261101.HD102.CoverSchedules.pdf', ['ID-000 COVER SHEET, INDEX, SYMBOLS & NOTES', 'ID-001 FINISH, LIGHTING & DEVICE SCHEDULES']),
         ('261101.HD102.FlooringPlans.pdf', ['ID-101 FLOORING PLAN - FLOOR 1', 'ID-102 FLOORING PLAN - FLOOR 2']),
         ('261101.HD102.WallFinishPlans.pdf', ['ID-201 WALL FINISH PLAN - FLOOR 1', 'ID-202 WALL FINISH PLAN - FLOOR 2']),
         ('261101.HD102.RCPPlans.pdf', ['ID-301 REFLECTED CEILING PLAN - FLOOR 1', 'ID-302 REFLECTED CEILING PLAN - FLOOR 2']),
         ('261101.HD102.LightingPlans.pdf', ['ID-401 LIGHTING & SWITCHING PLAN - FLOOR 1', 'ID-402 LIGHTING & SWITCHING PLAN - FLOOR 2']),
         ('261101.HD102.PowerDataPlans.pdf', ['ID-501 POWER & DATA PLAN - FLOOR 1', 'ID-502 POWER & DATA PLAN - FLOOR 2']),
         ('261101.HD102.FurniturePlans.pdf', ['ID-601 FURNITURE PLAN - FLOOR 1', 'ID-602 FURNITURE PLAN - FLOOR 2'])]
ix = json.load(open('elev_index.json'))
by = collections.OrderedDict()
for v in ix: by.setdefault(v['sheet'], []).append(v['room'])
elev_titles = [f"{no} INTERIOR ELEVATIONS - FLOOR {1 if int(no[3:]) < 720 else 2}: " + ', '.join(dict.fromkeys(rooms)) for no, rooms in by.items()]
PARTS += [('261101.HD102.InteriorElevations.pdf', elev_titles), ('261101.HD102.Details.pdf', ['ID-801 TYPICAL DETAILS'])]
out = fitz.open(); toc = []
for path, titles in PARTS:
    d = fitz.open(path); assert len(d) == len(titles), (path, len(d), len(titles))
    start = len(out); out.insert_pdf(d)
    for i, t in enumerate(titles): toc.append([1, t, start + i + 1])
out.set_toc(toc)
out.set_metadata({'title': 'Casa Grove - Interior Design Set (Helios Development, HD102)', 'author': 'Helios Development', 'subject': 'Issued 11.01.26 for pricing and coordination, not for permit',
                  'creator': 'Helios Development', 'producer': 'Helios Development', 'keywords': 'Casa Grove, 3350 Thomas Ave, HD102, interior design set'})
OUT = '261101.HD102.InteriorDesignSet.pdf'
import os, sys  # REFUSE_OVERWRITE: this is the 11.01.26 issued set; never overwrite an existing issue (owner rule: never delete a live file)
if os.path.exists(OUT): sys.exit('refusing to overwrite ' + OUT + '; this script is retired, use build_review_set.py')
out.save(OUT, garbage=3, deflate=True)
print('saved', OUT, len(out), 'pages')
