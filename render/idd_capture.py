"""Capture what a generator draws on each elevation view, as wall-coordinate geometry for the renderer.

Every view the generators draw goes through idd_elevations.ElevationView and the component library (idd_components,
idd_kitchen). With capture on, each primitive (rect, polygon, ellipse) drawn into a view is recorded in wall inches
(x along the wall from the viewer's left, y up from the finished floor) with the stack of components that drew it,
the fill and the stroke. Lines are not recorded: the vector drawing is laid over the render, so lines need no geometry.
Openings (doors, windows, cased and arched openings, niches) are recorded from their component arguments so the
wall can be cut. Nothing about the drawing changes; the PDF is identical with capture on or off.

Usage (from a runner, before the generator is imported):
    import idd_capture; idd_capture.enable()
    ... run the generator ...
    idd_capture.dump('/path/views.json')     # every view with page, placement, scale and primitives
"""
import functools, inspect, json, os, sys
sys.path.insert(0, '/home/claude/flrwork')
import pymupdf as fitz
import idd_elevations as E
import idd_components as C

VIEWS = {}            # id(view) -> record
STACK = []            # component names currently drawing
DOCS = {}             # id(doc) -> output path (filled on save)
OPENINGS = {'door_leaf': ('x', 'w', None, 'head'), 'door_pair': ('x', 'w', None, 'head'), 'cased_opening': ('x', 'w', None, 'head'),
            'window': ('x', 'w', 'sill', 'head'), 'arched_opening': ('x', 'w', None, 'spring'), 'niche': ('x', 'w', 'y', 'h'),
            'jib_door': ('x', 'w', None, 'head'), 'bifold': ('x', 'w', None, 'head'), 'arched_cased_opening': ('x', 'w', None, 'spring')}
_on = False


def _view_rec(v):
    r = VIEWS.get(id(v))
    if r is None:
        w = getattr(v, 'w', {}) or {}
        r = VIEWS[id(v)] = {'doc': id(v.p.parent), 'page': v.p.number, 'origin': [v.ox, v.oy], 'k': v.k,
                            'room': w.get('room'), 'view': w.get('view'), 'length': w.get('length'), 'ceiling': w.get('ceiling'),
                            'prims': [], 'openings': [], 'labels': []}
    return r


def _ctx():
    return list(STACK)


def _jsonable(x):
    if isinstance(x, (int, float, str, bool)) or x is None: return x
    if isinstance(x, (list, tuple)): return [_jsonable(i) for i in x]
    if isinstance(x, dict): return {str(k): _jsonable(v) for k, v in x.items()}
    return str(x)


def _wrap_component(mod, name, fn):
    sig = inspect.signature(fn)
    @functools.wraps(fn)
    def w(*a, **kw):
        if _on and a and hasattr(a[0], 'ox'):
            # every component call with its arguments, so the photoreal renderer builds the real object (a door with its
            # panels and sticking, a profiled crown) instead of extruding the 2-D linework; nested calls carry their parent
            try:
                b = sig.bind(*a, **kw); b.apply_defaults()
                args = {k: _jsonable(v_) for k, v_ in list(b.arguments.items())[1:] if not callable(v_)}
                _view_rec(a[0]).setdefault('calls', []).append({'comp': name, 'args': args, 'parent': STACK[-1] if STACK else None, 'depth': len(STACK)})
            except Exception as e_:
                _view_rec(a[0]).setdefault('calls', []).append({'comp': name, 'error': str(e_), 'depth': len(STACK)})
        STACK.append(name)
        try:
            if _on and a and hasattr(a[0], 'ox') and name in OPENINGS:
                try:
                    b = sig.bind(*a, **kw); b.apply_defaults(); ar = b.arguments
                    xk, wk, y0k, y1k = OPENINGS[name]
                    x, wd = float(ar[xk]), float(ar[wk])
                    if name == 'niche': y0, y1 = float(ar['y']), float(ar['y']) + float(ar['h'])
                    else: y0 = float(ar[y0k]) if y0k else 0.0; y1 = float(ar[y1k])
                    if name == 'arched_opening':
                        r_ = ar.get('r') or wd / 2.0; y1 = y1 + float(r_)
                    if name == 'arched_cased_opening':   # the apex of the segmental head
                        r_ = float(ar['r']); y1 = y1 - (r_ ** 2 - (wd / 2) ** 2) ** 0.5 + r_ + 1.0   # 1 in. over the apex: the spandrels close it
                    _view_rec(a[0])['openings'].append({'kind': name, 'x0': min(x, x + wd), 'x1': max(x, x + wd), 'y0': y0, 'y1': y1, 'ctx': _ctx()})
                except Exception as e_:
                    _view_rec(a[0])['openings'].append({'kind': name, 'error': str(e_)})
            return fn(*a, **kw)
        finally:
            STACK.pop()
    return w


def _rec_rect(orig):
    def r(v, x0, y0, x1, y1, w=C.MED, c=None, fill=None, dashes=None):
        if _on and hasattr(v, 'ox'):
            _view_rec(v)['prims'].append({'t': 'rect', 'pts': [[min(x0, x1), min(y0, y1)], [max(x0, x1), max(y0, y1)]],
                                          'fill': list(fill) if fill else None, 'w': w, 'dash': bool(dashes), 'ctx': _ctx()})
        return orig(v, x0, y0, x1, y1, w, c, fill, dashes)
    return r


def _rec_poly(orig):
    def r(v, pts, w=C.MED, c=None, fill=None, close=True):
        if _on and hasattr(v, 'ox') and close and len(pts) >= 3:
            _view_rec(v)['prims'].append({'t': 'poly', 'pts': [[float(x), float(y)] for x, y in pts], 'fill': list(fill) if fill else None,
                                          'w': w, 'ctx': _ctx()})
        return orig(v, pts, w, c, fill, close)
    return r


def _rec_ellipse(orig):
    def r(v, cx, cy, rx, ry, w=C.MED, c=C.INK, fill=None, dashes=None):
        if _on and hasattr(v, 'ox'):
            _view_rec(v)['prims'].append({'t': 'ellipse', 'pts': [[cx, cy], [rx, ry]], 'fill': list(fill) if fill else None, 'w': w, 'dash': bool(dashes), 'ctx': _ctx()})
        return orig(v, cx, cy, rx, ry, w, c, fill, dashes)
    return r


def _rec_view_rect(orig):
    def r(self, x0, y0, x1, y1, width=0.5, color=E.INK, fill=None, dashes=None):
        # ElevationView.rect takes page points; convert back to wall inches
        if _on:
            xi0, xi1 = (x0 - self.ox) / self.k, (x1 - self.ox) / self.k
            yi0, yi1 = (self.oy - y0) / self.k, (self.oy - y1) / self.k
            _view_rec(self)['prims'].append({'t': 'rect', 'pts': [[min(xi0, xi1), min(yi0, yi1)], [max(xi0, xi1), max(yi0, yi1)]],
                                             'fill': list(fill) if fill else None, 'w': width, 'dash': bool(dashes), 'ctx': _ctx() + ['view.rect']})
        return orig(self, x0, y0, x1, y1, width, color, fill, dashes)
    return r


def _rec_text(orig):
    def r(self, x, y, s, *a, **kw):
        if _on:
            _view_rec(self)['labels'].append({'x': (x - self.ox) / self.k, 'y': (self.oy - y) / self.k, 's': str(s)})
        return orig(self, x, y, s, *a, **kw)
    return r


def enable():
    """Patch the component modules once. Safe to call twice."""
    global _on
    if getattr(C, '_captured', False):
        _on = True; return
    import idd_kitchen as K
    for mod in (C, K):
        for name, fn in list(vars(mod).items()):
            if callable(fn) and not name.startswith('_') and inspect.isfunction(fn) and fn.__module__ == mod.__name__:
                params = list(inspect.signature(fn).parameters)
                if params and params[0] == 'v':
                    setattr(mod, name, _wrap_component(mod, name, fn))
    # primitives: patched in both modules (idd_kitchen bound them by name at import)
    rect0, poly0, ell0 = _ORIG['rect'], _ORIG['poly'], _ORIG['ellipse']
    for mod in (C, K):
        mod._rect, mod._poly, mod._ellipse = _rec_rect(rect0), _rec_poly(poly0), _rec_ellipse(ell0)
    E.ElevationView.rect = _rec_view_rect(E.ElevationView.rect)
    E.ElevationView.text = _rec_text(E.ElevationView.text)
    _save = fitz.Document.save
    def save(self, filename, *a, **kw):
        DOCS[id(self)] = str(filename)
        return _save(self, filename, *a, **kw)
    fitz.Document.save = save
    C._captured = True
    _on = True


_ORIG = {'rect': C._rect, 'poly': C._poly, 'ellipse': C._ellipse}


def dump(path, only_output=None):
    """Write the views that landed in a saved PDF (probe views drawn on scratch documents are dropped)."""
    out = []
    for r in VIEWS.values():
        f = DOCS.get(r['doc'])
        if not f: continue
        if only_output and os.path.basename(f) != os.path.basename(only_output): continue
        rr = dict(r); rr['pdf'] = f; out.append(rr)
    json.dump(out, open(path, 'w'))
    return len(out)
