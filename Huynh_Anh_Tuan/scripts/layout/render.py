import gdstk, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
COL={(2,0):("#b0e0b0",.35),(1,0):("#3cb043",.75),(4,0):("#ffd700",.15),(5,0):("#ff8c00",.15),(3,0):("#d62728",.8),
     (6,0):("#000000",1),(7,0):("#1f77b4",.45),(8,0):("#111111",1),(9,0):("#9467bd",.45),(10,0):("#333",1),(11,0):("#17becf",.4),(30,0):("#555",1),(31,0):("#e377c2",.35)}
def draw(gds, top, out, scale=1.0):
    lib=gdstk.read_gds(gds); c=[x for x in lib.cells if x.name==top][0]
    (x0,y0),(x1,y1)=c.bounding_box()
    fig,ax=plt.subplots(figsize=(max(6,(x1-x0)*scale),max(3,(y1-y0)*scale)))
    for p in sorted(c.get_polygons(), key=lambda p:[2,1,4,5,3,6,7,8,9,10,11,30,31].index(p.layer) if p.layer in [2,1,4,5,3,6,7,8,9,10,11,30,31] else 99):
        k=(p.layer,p.datatype)
        if k not in COL: continue
        col,a=COL[k]; ax.add_patch(Polygon(p.points,closed=True,fc=col,ec=col,alpha=a,lw=0.3))
    for l in c.get_labels(depth=0): ax.text(l.origin[0],l.origin[1],l.text,fontsize=7,ha='center',va='center',color='k',weight='bold')
    ax.set_xlim(x0-0.2,x1+0.2); ax.set_ylim(y0-0.2,y1+0.2); ax.set_aspect('equal'); ax.grid(False)
    ax.set_title(top); fig.tight_layout(); fig.savefig(out,dpi=110)
if __name__=="__main__": draw(sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]) if len(sys.argv)>4 else 1.6)
