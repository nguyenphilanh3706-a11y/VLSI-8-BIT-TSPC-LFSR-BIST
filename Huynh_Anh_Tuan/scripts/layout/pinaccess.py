"""pinaccess.py - tim diem dat Via2 tren Metal2 cua tung chan trong cell (GDS phang)."""
import gdstk

def bbs(c, l, d=0):
    return [tuple(map(tuple, p.bounding_box())) for p in c.polygons if p.layer == l and p.datatype == d]

def ov(a, b):
    return a[0][0] < b[1][0] and b[0][0] < a[1][0] and a[0][1] < b[1][1] and b[0][1] < a[1][1]

def inside(pt, b):
    return b[0][0] <= pt[0] <= b[1][0] and b[0][1] <= pt[1] <= b[1][1]

def nets(cell):
    shapes = []
    for lay in ("Poly", "Cont", "M1", "Via1", "M2"):
        l = {"Poly": 3, "Cont": 6, "M1": 7, "Via1": 8, "M2": 9}[lay]
        for b in bbs(cell, l):
            shapes.append((lay, b))
    par = list(range(len(shapes)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    conn = {("Poly", "Cont"), ("Cont", "M1"), ("M1", "Via1"), ("Via1", "M2"), ("M1", "M1"), ("M2", "M2"), ("Poly", "Poly")}
    for i, (la, a) in enumerate(shapes):
        for j in range(i):
            lb, b = shapes[j]
            if ((la, lb) in conn or (lb, la) in conn) and ov(a, b):
                par[f(i)] = f(j)
    res = {}
    for lab in cell.labels:
        if lab.text in ("VDD", "GND"):
            continue
        k = [i for i, (la, b) in enumerate(shapes) if la == "M1" and inside(lab.origin, b)]
        root = f(k[0])
        res[lab.text] = [b for i, (la, b) in enumerate(shapes) if la == "M2" and f(i) == root]
    return res

def access(cell):
    """chan -> danh sach (x0, x1, y): doan tren Metal2 dat duoc tam Via2 (enclosure 0,06 + 0,07)."""
    out = {}
    for net, m2 in nets(cell).items():
        out[net] = []
        for (x0, y0), (x1, y1) in m2:
            if y1 - y0 >= 0.14 and x1 - x0 >= 0.26:
                out[net].append((round(x0 + 0.13, 3), round(x1 - 0.13, 3), round((y0 + y1) / 2, 3)))
    return out

if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        c = gdstk.read_gds(f).top_level()[0]
        print(c.name, access(c))
