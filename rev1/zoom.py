"""zoom.py page floor x0 y0 x1 y1 out [dpi] : render a FOR-pt box of a FinishPlans page, print the px->FOR mapping."""
import sys; sys.path.insert(0, '/home/claude/flrwork/rev1'); sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz, build_finish_rev1 as B
pg, fl = int(sys.argv[1]), int(sys.argv[2]); x0, y0, x1, y1 = map(float, sys.argv[3:7]); out = sys.argv[7]; dpi = int(sys.argv[8]) if len(sys.argv) > 8 else 200
f = B.to_sheet(fl); a = f(x0, y0); b = f(x1, y1)
d = fitz.open(sys.argv[9] if len(sys.argv) > 9 else '/home/claude/flrwork/261105.HD102.FinishPlans.pdf')
d[pg].get_pixmap(dpi=dpi, clip=fitz.Rect(*a, *b)).save(out)
k = dpi / 72 * 0.75
print(f'FOR = ({x0} + px/{k:.4f}, {y0} + py/{k:.4f})')
