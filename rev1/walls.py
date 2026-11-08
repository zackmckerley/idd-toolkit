"""Wall polygons from FOR's REV 1 wall layers: rasterize the wall lines, close each wall between its two faces with a square
kernel (walls up to 16 in. thick, nothing wider closes), vectorize. Coordinates stay in FOR's sheet points (1/4 in. scale)."""
import numpy as np, cv2, pymupdf as fitz, json, sys
import replay as R
Z = 4.0                                  # px per pt (6 px per inch at 1/4 in. = 1 ft)
WALL_LAYERS = ('A-WALL-BLOCK', 'A-WALL-DRYWALL', 'A-WALL-PART', '|A-Wall', 'A-WALL-HATCH-NEW', '|P-WALL')

def is_wall(n): return n.startswith('PROPOSED FLOOR PLANS|') and any(n.endswith(k.lstrip('|')) and (k.startswith('|') or k in n) for k in WALL_LAYERS)

def line_mask(floor, layers_pred, lw=0.5):
    W, H = int(R.PLAN.width * Z), int(R.PLAN.height * Z)
    doc = fitz.open(); pg = doc.new_page(width=R.PLAN.width, height=R.PLAN.height)
    T = lambda p: fitz.Point(p.x - R.PLAN.x0, p.y - R.PLAN.y0)
    for dr in R.drawings(floor):
        if layers_pred(R.lname(dr)) and R.inplan(dr):
            sh = pg.new_shape(); R.replay(sh, dr, T=T, color=(0, 0, 0), width=lw, dashes='[] 0'); sh.commit()
    pix = pg.get_pixmap(matrix=fitz.Matrix(Z, Z), colorspace=fitz.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    return (a < 200).astype(np.uint8)

def wall_mask(floor, k_in=16):
    m = line_mask(floor, is_wall)
    k = int(k_in * 1.5 * Z) | 1
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    c = cv2.morphologyEx(m, cv2.MORPH_CLOSE, ker)
    # closing along each axis separately so a wall is closed between its faces without bridging corners diagonally
    kx = cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)); ky = cv2.getStructuringElement(cv2.MORPH_RECT, (1, k))
    cx = cv2.morphologyEx(m, cv2.MORPH_CLOSE, ky)    # vertical kernel closes horizontal walls (faces above and below)
    cy = cv2.morphologyEx(m, cv2.MORPH_CLOSE, kx)    # horizontal kernel closes vertical walls
    return m, (cx | cy)

def polygons(mask, eps=0.6):
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for i, c in enumerate(cs):
        if cv2.contourArea(c) < 4: continue
        a = cv2.approxPolyDP(c, eps, True).reshape(-1, 2)
        out.append({'hole': bool(hier[0][i][3] >= 0), 'pts': [(float(x) / Z + R.PLAN.x0, float(y) / Z + R.PLAN.y0) for x, y in a]})
    return out

if __name__ == '__main__':
    for fl in (1, 2):
        m, w = wall_mask(fl)
        cv2.imwrite(f'wallmask_{fl}.png', cv2.resize((1 - w) * 255, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA))
        np.save(f'wallmask_{fl}.npy', w)
        print(fl, w.sum())
