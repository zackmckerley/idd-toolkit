import pymupdf as fitz
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
SRC='/mnt/user-data/uploads/3807f371-Flooring_Plans.pdf'
def polys_from(x, M):
    # build polygons from path items: split into subpaths on discontinuity
    pts=[]; out=[]
    for it in x['items']:
        if it[0]=='l':
            a,b=it[1]*M,it[2]*M
            if pts and (abs(pts[-1][0]-a.x)>1e-3 or abs(pts[-1][1]-a.y)>1e-3 or (len(pts)>2 and abs(pts[-1][0]-pts[0][0])<1e-3 and abs(pts[-1][1]-pts[0][1])<1e-3)):
                out.append(pts); pts=[]
            if not pts: pts.append((a.x,a.y))
            pts.append((b.x,b.y))
        elif it[0]=='re':
            r=it[1]*M; out.append([(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1)])
        elif it[0]=='qu':
            q=it[1]*M; out.append([(q.ul.x,q.ul.y),(q.ur.x,q.ur.y),(q.lr.x,q.lr.y),(q.ll.x,q.ll.y)])
    if pts: out.append(pts)
    res=[]
    for o in out:
        if len(o)>=3:
            pg=Polygon(o).buffer(0)
            if pg.area>1e-4: res.append(pg)
    return res
def layer_union(pn, pred):
    d=fitz.open(SRC); p=d[pn]; M=p.rotation_matrix
    ps=[]
    for x in p.get_drawings():
        if pred(x): ps+=polys_from(x,M)
    return unary_union(ps)
def is_wall(x):
    f=x.get('fill'); return f is not None and x.get('layer') in ('a-bro hatch','a-bro') and f[0]<0.5
def is_gray(x):
    return x.get('layer')=='a-bro hatch 2'
def rays(walls, x, y, far=400):
    P=Point(x,y); res={}
    for name,(dx,dy) in dict(L=(-1,0),R=(1,0),U=(0,-1),D=(0,1)).items():
        ln=LineString([(x,y),(x+dx*far,y+dy*far)])
        it=ln.intersection(walls)
        res[name]=round(P.distance(it),2) if not it.is_empty else None
    return res
