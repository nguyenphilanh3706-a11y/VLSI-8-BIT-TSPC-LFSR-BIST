"""cellgen.py - sinh layout cell CMOS theo khuon cell cua TV3 (gpdk090).

Khuon (lay tu GDS cua TV3, commit 435f6f0):
  cao 2,76 um; cot cach nhau 0,27 um; cot chan C (tiep xuc khuech tan) va cot cong G (poly) xen ke,
  C_i o x = 0,27*(i+1) voi i chan, G_i o i le; ray GND (duoi) va VDD (tren) Metal1 dung chung khi xep lien hang.
  NMOS: oxide day 0,52 um (W >= 0,24) hoac tam 0,64 um (W < 0,24); PMOS: tam 2,00 um.
  Chan pad poly 0,20 x 0,24 tai y 1,20..1,44. Day noi bo: Metal1 doc trong tung cot, Metal2 ngang theo ray.
Moi so lieu tinh bang um.
"""
import gdstk

L = {  # (layer, datatype) theo gpdk090.layermap
    "Oxide": (1, 0), "Nwell": (2, 0), "Poly": (3, 0), "Nimp": (4, 0), "Pimp": (5, 0),
    "Cont": (6, 0), "M1": (7, 0), "M1pin": (7, 1), "Via1": (8, 0), "M2": (9, 0), "M2pin": (9, 1),
    "Via2": (10, 0), "M3": (11, 0), "M3pin": (11, 1), "Via3": (30, 0), "M4": (31, 0), "M4pin": (31, 1),
    "prB": (99, 0),
}
TXT = {"M1": (7, 3), "M2": (9, 3), "M3": (11, 3), "M4": (31, 3)}

H = 2.76
PITCH = 0.27
TRACK = {"Z": 0.50, "A": 0.79, "B": 1.08, "C": 1.37, "D": 1.66, "E": 1.95, "F": 2.24}  # ray Metal2 noi bo
RAIL_GND = 0.12
RAIL_VDD = 2.64
N_CONT_Y = 0.64
P_CONT_Y = 2.00


def r(x):
    return round(x * 1000) / 1000.0


def rect(cell, lay, x0, y0, x1, y1):
    l, d = L[lay]
    cell.add(gdstk.rectangle((r(x0), r(y0)), (r(x1), r(y1)), layer=l, datatype=d))


def label(cell, lay, text, x, y):
    l, t = TXT[lay]
    cell.add(gdstk.Label(text, (r(x), r(y)), layer=l, texttype=t))


def via(cell, vlay, x, y):
    rect(cell, vlay, x - 0.07, y - 0.07, x + 0.07, y + 0.07)


def n_oxide_y(w):
    return (0.52, 0.52 + w) if w >= 0.24 else (N_CONT_Y - w / 2, N_CONT_Y + w / 2)


def p_oxide_y(w):
    return (P_CONT_Y - w / 2, P_CONT_Y + w / 2)


def frame(cell, width, nimp_top=1.06):
    """ray nguon, tiep dat de/giéng, implant, Nwell, prBoundary (giong TV3)."""
    W = width
    rect(cell, "prB", 0, 0, W, H)
    # ray Metal1 + chan
    rect(cell, "M1", 0, -0.06, W, 0.24)
    rect(cell, "M1", 0, 2.52, W, 2.82)
    rect(cell, "M1pin", 0, 0, W, 0.24)
    rect(cell, "M1pin", 0, 2.52, W, 2.76)
    label(cell, "M1", "GND", W / 2, RAIL_GND)
    label(cell, "M1", "VDD", W / 2, RAIL_VDD)
    # tiep xuc de (P+) duoi ray GND, tiep xuc giếng (N+) duoi ray VDD
    rect(cell, "Oxide", 0, -0.12, W, 0.24)
    rect(cell, "Oxide", 0, 2.52, W, 2.88)
    rect(cell, "Pimp", -0.02, -0.14, W + 0.02, 0.26)
    rect(cell, "Nimp", -0.02, 2.42, W + 0.02, 2.90)
    k = 1
    while PITCH * k < W - 0.1:
        x = PITCH * k
        rect(cell, "Cont", x - 0.06, -0.06, x + 0.06, 0.06)
        rect(cell, "Cont", x - 0.06, 2.70, x + 0.06, 2.82)
        k += 1
    # implant cho transistor
    rect(cell, "Nimp", 0, 0.26, W, nimp_top)
    rect(cell, "Pimp", 0, 1.50, W, 2.42)
    rect(cell, "Nwell", -0.12, 1.38, W + 0.12, 3.00)


class Cell:
    """Mo ta cell kieu ma tran cong.

    cols: danh sach cot, chi so i; i chan = cot C, i le = cot G.
      C: dict(n=net|None, p=net|None, nc=bool tiep xuc N, pc=bool tiep xuc P)
      G: dict(n=net|None, p=net|None, wn=.., wp=.., nstrap=bool, pstrap=bool)
         nstrap/pstrap: khong co cong nhung khuech tan noi lien (cung net hai ben)
    route: {net: track} - noi cac chan cua net bang Metal2 tren ray do
    pins:  {net: (track, x)} - diem dat Via2 cho cap tren (dem Metal2 0,15 x 0,56)
    labels: {net: x} - dat nhan chan Metal1 tai cot x (pad cong hoac cot C)
    """

    def __init__(self, name, cols, route, pins, extra_m1=None):
        self.name, self.cols, self.route, self.pins = name, cols, route, pins
        self.extra_m1 = extra_m1 or []
        self.width = PITCH * (len(cols) + 1)

    def x(self, i):
        return PITCH * (i + 1)


    def autoroute(self, pin_x):
        """gan ray Metal2 cho moi net tin hieu (backtracking), thoa rang buoc cot C co N/P khac net."""
        cols = self.cols
        terms = {}
        for i, col in enumerate(cols):
            if i % 2 == 0:
                if col.get("nc") and col.get("pc") and col["n"] == col["p"]:
                    terms.setdefault(col["n"], []).append((i, "np"))
                    continue
                if col.get("nc"):
                    terms.setdefault(col["n"], []).append((i, "n"))
                if col.get("pc"):
                    terms.setdefault(col["p"], []).append((i, "p"))
            else:
                g = col.get("n") or col.get("p")
                if g is not None:
                    terms.setdefault(g, []).append((i, "g"))
        for k in ("GND", "VDD"):
            terms.pop(k, None)
        nets = [n for n in terms if len(terms[n]) >= 2 or n in pin_x]
        def span(n):
            xs = [self.x(i) for i, k in terms[n]] + ([pin_x[n]] if n in pin_x else [])
            x0, x1 = min(xs) - 0.13, max(xs) + 0.13
            if x1 - x0 < 0.56:
                m = (x0 + x1) / 2
                x0, x1 = m - 0.28, m + 0.28
            return max(x0, 0.14), min(max(x1, max(x0, 0.14) + 0.56), self.width - 0.14)
        sp = {n: span(n) for n in nets}
        order = sorted(nets, key=lambda n: -(sp[n][1] - sp[n][0]))
        names = list(TRACK)
        assign = {}
        def ok(n, t):
            x0, x1 = sp[n]
            for m, tm in assign.items():
                if tm == t:
                    a0, a1 = sp[m]
                    if not (a1 + 0.14 <= x0 or x1 + 0.14 <= a0):
                        return False
            # rang buoc cot C: N va P khac net
            ty = TRACK[t]
            for i, k in terms[n]:
                if k not in ("n", "p"):
                    continue
                col = cols[i]
                other = col["p"] if k == "n" else col["n"]
                ocont = col.get("pc") if k == "n" else col.get("nc")
                if not ocont:
                    continue
                if k == "n":
                    ntop = max(0.76, ty + 0.13)
                    if other == "VDD":
                        pbot = 1.88
                    elif other in assign:
                        pbot = min(1.88, TRACK[assign[other]] - 0.13)
                    else:
                        pbot = 1.88
                    if pbot - ntop < 0.12:
                        return False
                else:
                    pbot = min(1.88, ty - 0.13)
                    if other == "GND":
                        ntop = 0.76
                    elif other in assign:
                        ntop = max(0.76, TRACK[assign[other]] + 0.13)
                    else:
                        ntop = 0.76
                    if pbot - ntop < 0.12:
                        return False
            return True
        def bt(j):
            if j == len(order):
                return True
            n = order[j]
            for t in names:
                if ok(n, t):
                    assign[n] = t
                    if bt(j + 1):
                        return True
                    del assign[n]
            return False
        if not bt(0):
            raise RuntimeError("khong gan duoc ray Metal2")
        self.route = {n: assign[n] for n in nets if len(terms[n]) >= 2}
        self.pins = {n: (assign[n], pin_x[n]) for n in pin_x}
        self.pinonly = {n for n in pin_x if len(terms[n]) < 2}
        return assign

    def build(self):
        c = gdstk.Cell(self.name)
        cols = self.cols
        frame(c, self.width)
        # ---- khuech tan (oxide) + poly
        for side in ("n", "p"):
            oy = n_oxide_y if side == "n" else p_oxide_y
            cy = N_CONT_Y if side == "n" else P_CONT_Y
            for i, col in enumerate(cols):
                x = self.x(i)
                if i % 2 == 0:  # cot C
                    if col.get(side) is None:
                        continue
                    ys = []
                    if col.get(side + "c"):
                        ys.append((cy - 0.12, cy + 0.12))
                    for j in (i - 1, i + 1):
                        if 0 <= j < len(cols):
                            g = cols[j]
                            if g.get(side) is not None:
                                ys.append(oy(g["w" + side]))
                            elif g.get(side + "strap"):
                                ys.append(oy(g.get("w" + side, 0.24)))
                    y0 = min(a for a, b in ys)
                    y1 = max(b for a, b in ys)
                    rect(c, "Oxide", x - 0.12, y0, x + 0.12, y1)
                else:  # cot G
                    if col.get(side) is not None or col.get(side + "strap"):
                        y0, y1 = oy(col.get("w" + side, 0.24))
                        rect(c, "Oxide", x - 0.15, y0, x + 0.15, y1)
        for i, col in enumerate(cols):
            if i % 2 == 0:
                continue
            x = self.x(i)
            gn, gp = col.get("n"), col.get("p")
            if gn is None and gp is None:
                continue
            if gn is not None and gp is not None:
                assert gn == gp, "cot %d: cong N, P khac net" % i
            lo = (n_oxide_y(col["wn"])[0] - 0.18) if gn is not None else 1.20
            hi = (p_oxide_y(col["wp"])[1] + 0.18) if gp is not None else 1.44
            rect(c, "Poly", x - 0.05, lo, x + 0.05, hi)
            rect(c, "Poly", x - 0.10, 1.20, x + 0.10, 1.44)
            rect(c, "Cont", x - 0.06, 1.26, x + 0.06, 1.38)
        # ---- Metal1: moi cot mot (hoac hai) doan doc
        need = {}  # (i, 'n'|'p'|'g') -> list of y can phu
        for i, col in enumerate(cols):
            if i % 2 == 0:
                if col.get("nc"):
                    need[(i, "n")] = [N_CONT_Y - 0.12, N_CONT_Y + 0.12]
                if col.get("pc"):
                    need[(i, "p")] = [P_CONT_Y - 0.12, P_CONT_Y + 0.12]
            else:
                if col.get("n") is not None or col.get("p") is not None:
                    need[(i, "g")] = [1.08, 1.56]
        net_of = {}
        for (i, k) in need:
            col = cols[i]
            net_of[(i, k)] = col["n"] if k == "n" else col["p"] if k == "p" else (col.get("n") or col.get("p"))
        vias1 = []
        # noi nguon
        for (i, k), net in net_of.items():
            if net == "GND":
                need[(i, k)][0] = 0.0
            if net == "VDD":
                need[(i, k)][1] = 2.76
        # noi N va P cung net trong mot cot C
        for i, col in enumerate(cols):
            if i % 2 == 0 and col.get("nc") and col.get("pc") and col["n"] == col["p"]:
                need[(i, "n")][1] = need[(i, "p")][1]
                del need[(i, "p")]
        # via len ray Metal2
        segs = {}
        for (i, k) in list(need):
            net = net_of[(i, k)]
            if net in self.route:
                ty = TRACK[self.route[net]]
                lo, hi = need[(i, k)]
                need[(i, k)] = [min(lo, ty - 0.13), max(hi, ty + 0.13)]
                vias1.append((self.x(i), ty))
                segs.setdefault(net, []).append(self.x(i))
        for net, (tr, px) in self.pins.items():
            ty = TRACK[tr]
            # tim cot co M1 cua net gan px nhat
            cands = [(abs(self.x(i) - px), i, k) for (i, k) in need if net_of[(i, k)] == net]
            if net not in self.route:
                _, i, k = min(cands)
                lo, hi = need[(i, k)]
                need[(i, k)] = [min(lo, ty - 0.13), max(hi, ty + 0.13)]
                vias1.append((self.x(i), ty))
        for (i, k), (lo, hi) in need.items():
            x = self.x(i)
            if hi - lo < 0.48:  # dien tich Metal1 toi thieu
                m = (lo + hi) / 2
                lo, hi = m - 0.24, m + 0.24
            rect(c, "M1", x - 0.075, lo, x + 0.075, hi)
        for i, col in enumerate(cols):
            if i % 2 == 0:
                x = self.x(i)
                if col.get("nc"):
                    rect(c, "Cont", x - 0.06, N_CONT_Y - 0.06, x + 0.06, N_CONT_Y + 0.06)
                if col.get("pc"):
                    rect(c, "Cont", x - 0.06, P_CONT_Y - 0.06, x + 0.06, P_CONT_Y + 0.06)
        # hai via cung net cung ray o hai cot ke nhau (cach 0,27) qua gan (Via1.SP.1 0,15):
        # bo via o cot sau, noi hai cot bang cau Metal1 ngang
        vset = sorted(set(vias1))
        drop = set()
        for (xa, ya) in vset:
            for (xb, yb) in vset:
                if ya == yb and 0 < xb - xa < 0.30 and (xa, ya) not in drop:
                    drop.add((xb, yb))
                    rect(c, "M1", xa - 0.075, ya - 0.075, xb + 0.075, ya + 0.075)
        for (x, y) in vset:
            if (x, y) not in drop:
                via(c, "Via1", x, y)
        # Metal2 ray noi
        for net, xs in segs.items():
            ty = TRACK[self.route[net]]
            x0, x1 = min(xs) - 0.13, max(xs) + 0.13
            if x1 - x0 < 0.56:
                m = (x0 + x1) / 2
                x0, x1 = m - 0.28, m + 0.28
            rect(c, "M2", x0, ty - 0.075, x1, ty + 0.075)
        # dem Metal2 cho chan (cap tren dat Via2 tai (px, ty))
        self.pin_xy = {}
        for net, (tr, px) in self.pins.items():
            ty = TRACK[tr]
            if net not in self.route:
                x0 = max(px - 0.28, 0.14)
                x1 = x0 + 0.56
                if x1 > self.width - 0.14:
                    x1 = self.width - 0.14
                    x0 = x1 - 0.56
                rect(c, "M2", x0, ty - 0.075, x1, ty + 0.075)
            self.pin_xy[net] = (r(px), ty)
        # nhan chan Metal1 tai pad cong / cot C
        for net, (tr, px) in self.pins.items():
            cands = [(abs(self.x(i) - px), i, k) for (i, k) in net_of if net_of[(i, k)] == net and (i, k) in need]
            if not cands:
                cands = [(abs(self.x(i) - px), i, k) for (i, k) in net_of if net_of[(i, k)] == net]
            _, i, k = min(cands)
            x = self.x(i)
            yc = 1.32 if k == "g" else (N_CONT_Y if k == "n" else P_CONT_Y)
            rect(c, "M1pin", x - 0.075, yc - 0.12, x + 0.075, yc + 0.12)
            label(c, "M1", net, x, yc)
        self.cell = c
        return c


def dff_tspc_tmp():
    """DFF_TSPC_TMP (17T) - thu tu cot xem docs/5_layout.md."""
    C = lambda n=None, p=None, nc=False, pc=False: dict(n=n, p=p, nc=nc, pc=pc)
    G = lambda n=None, p=None, wn=0.24, wp=0.48, **k: dict(n=n, p=p, wn=wn, wp=wp, **k)
    cols = [
        C("RSTB", "RSTB", True, True),          # C0
        G("RST", "RST", wn=0.12, wp=0.24),      # G1  MN6 / MP6
        C("GND", "VDD", True, True),            # C2
        G("D", "D", wn=0.12, wp=0.48),          # G3  MN1 / MP1 (MN1 0,12: chong race, xem docs/5_layout.md)
        C("X", "p1", True, False),              # C4
        G(None, "CLK", wp=0.48),                # G5  MP2
        C("Y", "X", True, True),                # C6
        G("X", None, wn=0.36),                  # G7  MN2
        C("n1", "Y", False, True),              # C8
        G("CLK", "CLK", wn=0.36, wp=0.48),      # G9  MN3 / MP3
        C("GND", "VDD", True, True),            # C10
        G("RSTB", "RSTB", wn=0.36, wp=0.24),    # G11 MNR / MPR
        C("n3", "QB", False, True),             # C12
        G("Y", "Y", wn=0.36, wp=0.48),          # G13 MN5 / MP4
        C("n2", "p2", False, False),            # C14
        G("CLK", None, wn=0.36, wp=0.48, pstrap=True),  # G15 MN4 (P: p2 lien tuc)
        C("QB", "p2", True, False),             # C16
        G("SET", "SET", wn=0.24, wp=0.48),      # G17 MNS / MPS
        C("GND", "VDD", True, True),            # C18
        G("QB", "QB", wn=0.24, wp=0.48),        # G19 MN7 / MP7
        C("Q", "Q", True, True),                # C20
    ]
    route = {"Y": "B", "X": "D", "CLK": "C", "RSTB": "E", "QB": "D"}
    pins = {"RST": ("A", 0.54), "D": ("F", 1.08), "CLK": ("C", 2.70), "SET": ("A", 4.86), "Q": ("F", 5.67)}
    return Cell("DFF_TSPC_TMP", cols, route, pins)


if __name__ == "__main__":
    import sys
    cl = dff_tspc_tmp()
    lib = gdstk.Library("tv4_lay", unit=1e-6, precision=5e-10)
    lib.add(cl.build())
    out = sys.argv[1] if len(sys.argv) > 1 else "DFF_TSPC_TMP.gds"
    lib.write_gds(out)
    print(cl.name, "width", cl.width, "pins", cl.pin_xy)


def _C(n=None, p=None, nc=False, pc=False):
    return dict(n=n, p=p, nc=nc, pc=pc)


def _G(n=None, p=None, wn=0.24, wp=0.48, **k):
    return dict(n=n, p=p, wn=wn, wp=wp, **k)


def dff_ms_tmp():
    """DFF_MS_TMP (24T): 4 cong truyen + 4 NOR2 (cung kich thuoc NOR2_X1 cua TV3), trai phang."""
    C, G = _C, _G
    cols = [
        C("D", None, True, False),                 # c0
        G("CLKB", None, wn=0.24),                  # g1  MN1
        C("n1", "D", True, True),                  # c2
        G("CLK", "CLK", wn=0.24, wp=0.48),         # g3  MN2 / MP1
        C("n1f", "n1", True, True),                # c4
        G(None, "CLKB", wp=0.48),                  # g5  MP2
        C("n1f", "n1f", True, True),               # c6
        G("RST", "RST", wn=0.12, wp=0.48),         # g7  NOR I2 (B)
        C("GND", "pa", True, False),               # c8
        G("mb", "mb", wn=0.12, wp=0.48),           # g9  NOR I2 (A)
        C("n1f", "VDD", True, True),               # c10
        G(),                                        # g11 trong
        C("mb", "VDD", True, True),                # c12
        G("n1", "n1", wn=0.12, wp=0.48),           # g13 NOR I1 (A)
        C("GND", "pb", True, False),               # c14
        G("SET", "SET", wn=0.12, wp=0.48),         # g15 NOR I1 (B)
        C("mb", "mb", True, True),                 # c16
        G("CLK", None, wn=0.24, wp=0.48, pstrap=True),  # g17 MN3 (P: mb lien tuc)
        C("n2", "mb", True, False),                # c18
        G("CLKB", "CLKB", wn=0.24, wp=0.48),       # g19 MN4 / MP3
        C("n2f", "n2", True, True),                # c20
        G(None, "CLK", wp=0.48),                   # g21 MP4
        C("n2f", "n2f", True, True),               # c22
        G("SET", "SET", wn=0.12, wp=0.48),         # g23 NOR I4 (B)
        C("GND", "pc", True, False),               # c24
        G("Q", "Q", wn=0.12, wp=0.48),             # g25 NOR I4 (A)
        C("n2f", "VDD", True, True),               # c26
        G(),                                        # g27 trong
        C("Q", "VDD", True, True),                 # c28
        G("n2", "n2", wn=0.12, wp=0.48),           # g29 NOR I3 (A)
        C("GND", "pd", True, False),               # c30
        G("RST", "RST", wn=0.12, wp=0.48),         # g31 NOR I3 (B)
        C("Q", "Q", True, True),                   # c32
    ]
    c = Cell("DFF_MS_TMP", cols, {}, {})
    c.autoroute({"D": 0.54, "CLKB": 1.62, "CLK": 3.24, "RST": 5.13, "SET": 5.40, "Q": 8.37})
    return c


def inv_clk():
    """INV_CLK: N 0,48 / P 0,96 lam 2 ngon song song (0,24 / 0,48 moi ngon)."""
    C, G = _C, _G
    cols = [C("GND", "VDD", True, True), G("A", "A", wn=0.24, wp=0.48), C("Y", "Y", True, True),
            G("A", "A", wn=0.24, wp=0.48), C("GND", "VDD", True, True)]
    c = Cell("INV_CLK", cols, {}, {})
    c.autoroute({"A": 0.54, "Y": 0.81})
    return c
