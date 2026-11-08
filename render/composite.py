"""Lay rendered elevations onto the drawing: each PNG goes on its view's rect in Multiply blend, so the paper takes the
render's color and every line and letter of the drawing stays black and crisp on top of it.
    python3 render/composite.py views.json in.pdf out.pdf  IDX:render.png [IDX:render.png ...]"""
import json, sys
import pymupdf as fitz


def multiply_last_image(page):
    """Wrap the image just inserted (the last 'Do' in the page's last content stream) in a Multiply graphics state."""
    doc = page.parent
    res = doc.xref_get_key(page.xref, 'Resources')
    if res[0] == 'xref':
        rx = int(res[1].split()[0]); doc.xref_set_key(rx, 'ExtGState/GSmul', '<</Type/ExtGState/BM/Multiply>>')
    else:
        doc.xref_set_key(page.xref, 'Resources/ExtGState/GSmul', '<</Type/ExtGState/BM/Multiply>>')
    xref = page.get_contents()[-1]
    s = doc.xref_stream(xref).decode('latin1')
    i = s.rfind(' Do')
    j = s.rfind('q', 0, i)
    s = s[:j + 1] + '\n/GSmul gs\n' + s[j + 1:]
    doc.update_stream(xref, s.encode('latin1'))


def place(page, view, png):
    ox, oy = view['origin']; k = view['k']
    r = fitz.Rect(ox, oy - view['ceiling'] * k, ox + view['length'] * k, oy)
    page.insert_image(r, filename=png, overlay=True, keep_proportion=False)
    multiply_last_image(page)
    return r


if __name__ == '__main__':
    views = json.load(open(sys.argv[1])); doc = fitz.open(sys.argv[2]); out = sys.argv[3]
    for a in sys.argv[4:]:
        i, png = a.split(':', 1); v = views[int(i)]
        place(doc[v['page']], v, png)
    doc.save(out, garbage=3, deflate=True)
    print('saved', out)
