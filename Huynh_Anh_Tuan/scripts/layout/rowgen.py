"""rowgen.py - ghep dai LFSR 8 bit thanh mot hang cell (pitch-matching ngang) va di day tren Metal3/Metal4.

Cach noi:
  - cell xep lien nhau, ray VDD/GND Metal1 noi lien qua cac cell;
  - moi chan co mot diem dat Via2 tren Metal2 cua chinh net do trong cell (tinh tu GDS, pinaccess.py);
  - tu diem do: Metal3 doc (rong 0,15) toi ray Metal4 ngang cua net, Via3 o dau doan;
  - chan noi GND (SET cua FF1..7, RST cua FF0): Metal2 doc tu dem chan xuong ray GND, Via1 len ray Metal1.
"""
import gdstk
from cellgen import rect, label, via, H, r

M4_TRACKS = [0.38, 0.67, 0.96, 1.25, 1.54, 1.83, 2.12, 2.41]


class Row:
    def __init__(self, name):
        self.name = name
        self.cell = gdstk.Cell(name)
        self.x = 0.0
        self.insts = []        # (ten instance, cell, x)
        self.pins = {}         # (inst, chan) -> (x, y) tuyet doi
        self.nets = {}         # net -> list (x, y) diem dat Via2
        self.ties = []         # (x, y) chan can noi GND

    def place(self, iname, cell, width, access, extra=()):
        """extra: hinh ve them o muc hang, toa do trong cell: (lop, x0, y0, x1, y1)."""
        self.cell.add(gdstk.Reference(cell, (r(self.x), 0)))
        for (lay, a, b, c2, d) in extra:
            rect(self.cell, lay, self.x + a, b, self.x + c2, d)
        self.insts.append((iname, cell.name, self.x))
        for pin, (px, py) in access.items():
            self.pins[(iname, pin)] = (r(self.x + px), py)
        self.x += width

    def connect(self, net, *ends):
        for e in ends:
            self.nets.setdefault(net, []).append(self.pins[e])

    def rail(self, net, x):
        """diem xuong ray GND tai x (tuyet doi): Via1 + dem Metal2 tren ray, Via2 len Metal3."""
        self.nets.setdefault(net, []).append((r(x), 0.12))
        self.rails = getattr(self, "rails", []) + [r(x)]

    def tie_gnd(self, *ends):
        for e in ends:
            self.ties.append(self.pins[e])

    def route(self, top_pins):
        c = self.cell
        # ---- gan ray Metal4 (thuat toan left-edge)
        spans = sorted(((min(x for x, y in pts), max(x for x, y in pts), n) for n, pts in self.nets.items()))
        track_end = [-1e9] * len(M4_TRACKS)
        self.track_of = {}
        for x0, x1, n in spans:
            # uu tien ray gan y trung binh cua cac chan (Metal3 ngan)
            ym = sum(y for x, y in self.nets[n]) / len(self.nets[n])
            order = sorted(range(len(M4_TRACKS)), key=lambda t: abs(M4_TRACKS[t] - ym))
            for t in order:
                if track_end[t] + 0.30 <= x0 - 0.13:
                    track_end[t] = x1 + 0.13
                    self.track_of[n] = t
                    break
            else:
                raise RuntimeError("het ray Metal4 cho net %s" % n)
        # ---- kiem tra Metal3 doc khong qua gan nhau
        stubs = []
        for n, pts in self.nets.items():
            ty = M4_TRACKS[self.track_of[n]]
            for (x, y) in pts:
                lo, hi = min(y, ty) - 0.13, max(y, ty) + 0.13
                if hi - lo < 0.54:
                    m = (lo + hi) / 2
                    lo, hi = m - 0.27, m + 0.27
                stubs.append((x, lo, hi, n))
        for i, (xa, la, ha, na) in enumerate(stubs):
            for (xb, lb, hb, nb) in stubs[:i]:
                if na != nb and abs(xa - xb) < 0.29 and la < hb + 0.14 and lb < ha + 0.14:
                    raise RuntimeError("Metal3 %s @%.3f qua gan %s @%.3f" % (na, xa, nb, xb))
        # ---- ve
        for (x, lo, hi, n) in stubs:
            rect(c, "M3", x - 0.075, lo, x + 0.075, hi)
        for n, pts in self.nets.items():
            ty = M4_TRACKS[self.track_of[n]]
            xs = [x for x, y in pts]
            x0, x1 = min(xs) - 0.13, max(xs) + 0.13
            if x1 - x0 < 0.54:
                m = (x0 + x1) / 2
                x0, x1 = m - 0.27, m + 0.27
            rect(c, "M4", x0, ty - 0.075, x1, ty + 0.075)
            for (x, y) in pts:
                via(c, "Via2", x, y)
                via(c, "Via3", x, ty)
            if n in top_pins:
                xp = top_pins[n] if top_pins[n] is not None else (x0 + x1) / 2
                rect(c, "M4pin", xp - 0.075, ty - 0.075, xp + 0.075, ty + 0.075)
                label(c, "M4", n, xp, ty)
        for x in getattr(self, "rails", []):
            rect(c, "M2", x - 0.28, 0.045, x + 0.28, 0.195)
            via(c, "Via1", x, 0.12)
        # ---- noi GND: Metal2 doc tu dem chan xuong ray GND + Via1
        for (x, y) in self.ties:
            rect(c, "M2", x - 0.075, 0.045, x + 0.075, y + 0.075)
            rect(c, "M2", x - 0.28, 0.045, x + 0.28, 0.195)
            via(c, "Via1", x, 0.12)
        # ---- nhan nguon o muc tren
        rect(c, "M1", 0, 0, 0.56, 0.24)
        rect(c, "M1", 0, 2.52, 0.56, 2.76)
        rect(c, "M1pin", 0, 0, 0.56, 0.24)
        rect(c, "M1pin", 0, 2.52, 0.56, 2.76)
        label(c, "M1", "GND", 0.28, 0.12)
        label(c, "M1", "VDD", 0.28, 2.64)
        rect(c, "prB", 0, 0, self.x, H)
        self.width = self.x
        return c
