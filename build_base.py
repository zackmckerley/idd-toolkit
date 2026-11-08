"""Neutral base plans for the RCP, lighting, power and furniture sheets: the designer's wall covering pages (id 01, id 07)
with everything that is not walls, doors, windows, fixtures, cabinets and room names stripped.
Two variants per floor: 'clean' (no furniture) and 'furn' (furniture and rugs kept, Floor 2 only has them).
Output: 261101.3350THOMAS.Base-clean.pdf and 261101.3350THOMAS.Base-furn.pdf (pages 0,1 = floors 1,2)."""
import os, re
os.environ['IDD_SRC'] = '/mnt/user-data/uploads/f4877d18-Pages_from_Casa_Grove_ID_Set_-_Wall_Coverings.pdf'
import wf_helpers as H
from wf_helpers import doc, fitz, Draw, FREG, strip_oc, strip_text_in, strip_paths_in, edit_text, find, neutralize

DARK = (0.251, 0.251, 0.251)
# Floor 1 back-of-house labels as placed on the flooring plan (flooring coords) -> wall sheet coords (+2.6, +22.7)
F1_LABELS = [('GUEST RM', 350.5, 619.0), ('FOYER', 350.5, 629.0)]     # the only room the designer's wall sheet leaves unnamed

def clean_page(p, floor, keep_furniture):
    for lyr in ('a-bro hatch 2', 'a-fin flr', 'a-dim', 'a-tag fnshs', 'a-elev mrk', 'ELEV-1', 'ELEV-2'):
        if H.oc_tags(p, lyr): strip_oc(p, lyr)
    if not keep_furniture:
        for lyr in ('a-furniture', 'a-rug'):
            if H.oc_tags(p, lyr): strip_oc(p, lyr)
    if floor == 1:
        strip_paths_in(p, (180, 455, 560, 940), '0')
        edits = [('Coconut Grove, FL 33143', None, 'Coconut Grove, FL 33133')]
        for o in find(p, 'CARTPORT'): edits.append(('CARTPORT', o, 'CARPORT'))
        for t in ('22\'-8" x 22\'-5"', '15\'-6" x 16\'-2"', '15\'-9" x 15\'-2"'):
            for o in find(p, t):
                if o[0] < 760: edits.append((t, o, None))
        edit_text(p, edits)
        # PANTRY is already named on this sheet; add the rest as on ID-101
        d = Draw(p)
        have = {t for t, *_ in [(x[0],) for x in []]}
        for t, x, y in F1_LABELS:
            if t == 'PANTRY' and find(p, 'PANTRY'): continue
            d.text(x + 2.6, y + 22.7, t, 9.4, DARK, align='c')
    else:
        for xref in p.get_contents():
            s_ = doc.xref_stream(xref).decode('latin1')
            if re.search(r'/Xop[234] Do', s_):
                doc.update_stream(xref, neutralize(s_).encode('latin1'))
        strip_text_in(p, (730, 45, 1390, 340))
        edits = []
        for txt in ('W.I.C.', 'MASTER', 'BATHRM'):
            for o in find(p, txt, 0xff8c1a): edits.append((txt, o, None))
        for txt in ('MASTER', 'BEDROOM'):
            for o in find(p, txt, 0x404040, 10.1825):
                if 350 < o[0] < 450 and 830 < o[1] < 880: edits.append((txt, o, None))
        for o in find(p, 'TERRACE', 0x404040, 11.7491):
            if o[0] > 450: edits.append(('TERRACE', o, None))
        for t in ('15\'-6" x 16\'-2"', '15\' x 17\'-6"'):
            for o in find(p, t): edits.append((t, o, None))
        edits.append(('Coconut Grove, FL 33143', None, 'Coconut Grove, FL 33133'))
        edit_text(p, edits)
        Draw(p).text(316.0, 566.0, 'HALL', 9.4, DARK, align='c')      # unnamed on the designer's sheet

def build(keep_furniture, out):
    global doc
    doc = fitz.open(H.SRC); H.doc = doc
    clean_page(doc[1], 1, keep_furniture)
    clean_page(doc[2], 2, keep_furniture)
    doc.delete_page(0)
    doc.save(out, garbage=3, deflate=True)
    print('saved', out)

if __name__ == '__main__':
    build(False, '/home/claude/flrwork/261101.3350THOMAS.Base-clean.pdf')
    build(True, '/home/claude/flrwork/261101.3350THOMAS.Base-furn.pdf')
