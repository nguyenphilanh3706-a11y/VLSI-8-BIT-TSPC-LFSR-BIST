"""build_layout.py - sinh toan bo layout cua TV4 (GDS) va netlist CDL de chay LVS.

  python3 scripts/layout/build_layout.py
Ket qua:
  layout/gds/DFF_TSPC_TMP.gds, DFF_MS_TMP.gds, INV_CLK.gds   cell la (khuon cell TV3); DFF_TSPC_TMP khong con dung
                                                              tu 22/11 (dai TSPC dung TSPC_DFF_S/R cua TV2)
  layout/gds/TSPC_LFSR_8bit.gds, MS_LFSR_8bit.gds            dai LFSR 8 bit (1 hang, gom ca cell la)
  layout/cdl/<ten>.cdl                                        netlist so sanh LVS (sinh tu netlist Spectre)
  out/hinh_layout/layout_<ten>.png                            hinh xem nhanh (anh trong docs/images
                                                              chup tu Virtuoso, khong ghi de)
Can: Python 3, gdstk, matplotlib. Cell XOR cua TV3 lay tu depend/tv3/layout/gds/,
flip-flop TSPC_DFF_S / TSPC_DFF_R cua TV2 lay tu depend/tv2/layout/gds/TV2_TSPC.gds.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import gdstk
import cellgen, rowgen, scs2cdl, render

TV3G = os.path.join(ROOT, "depend", "tv3", "layout", "gds")
TV2G = os.path.join(ROOT, "depend", "tv2", "layout", "gds", "TV2_TSPC.gds")
TV2C = os.path.join(ROOT, "depend", "tv2", "layout", "cdl")
GDS = os.path.join(ROOT, "layout", "gds")
CDL = os.path.join(ROOT, "layout", "cdl")
IMG = os.path.join(ROOT, "out", "hinh_layout")

# diem dat Via2 cho cap tren (toa do trong cell), chon trong vung pinaccess.access() tra ve
ACC = {
    "DFF_TSPC_TMP": {"RST": (0.39, 0.79), "D": (0.93, 2.24), "CLK": (3.00, 1.37), "SET": (5.01, 0.79), "Q": (5.40, 2.24)},
    "DFF_MS_TMP": {"D": (0.54, 2.24), "CLKB": (1.08, 1.66), "CLK": (2.43, 1.95), "RST": (3.24, 0.50), "SET": (5.13, 2.24), "Q": (7.56, 1.08)},
    "INV_CLK": {"A": (0.54, 0.50), "Y": (0.96, 0.79)},
    "XOR2_TG6": {"A": (0.54, 1.95), "Y": (1.62, 1.37), "B": (2.43, 1.08)},
    "XOR2_X1": {"B": (0.54, 1.37), "Y": (2.16, 0.79), "A": (3.78, 1.66)},
    # cell TV2: CLK, Q dat Via2 thang tren Metal2 co san (y 1,10); D, SET, RST chi co pad Metal1 o y 1,2..1,6
    # (Metal2 cua net khac chay ngang phia tren) nen keo Metal1 xuong y 0,50 roi len Via1 + dem Metal2 (DROP)
    "TSPC_DFF_S": {"D": (1.32, 0.50), "SET": (4.34, 0.50), "CLK": (3.20, 1.10), "Q": (7.10, 1.10)},
    "TSPC_DFF_R": {"D": (1.32, 0.50), "RST": (2.00, 0.50), "CLK": (3.40, 1.10), "Q": (7.80, 1.10)},
}
DROP = {"TSPC_DFF_S": ("D", "SET"), "TSPC_DFF_R": ("D", "RST")}
# vi tri khoi XORTAP8 trong hang (xem lfsr_row); doi bang bien moi truong TSPC_XOR de so sanh
XOR_POS = {"TSPC": int(os.environ.get("TSPC_XOR", "7")), "MS": 7}


def drop(cell):
    """hinh ve o muc hang cho chan chi co Metal1 (cell TV2): soc Metal1 rong 0,12 tu pad xuong y 0,37,
    pad Metal1 0,26 x 0,26 + Via1 + pad Metal2 0,26 x 0,32 (METAL2.A.1) quanh (x, 0,50); Via2 do rowgen dat tai cung diem."""
    out = []
    for pin in DROP.get(cell, ()):
        x, y = ACC[cell][pin]
        out += [("M1", x - 0.06, y - 0.13, x + 0.06, 1.30), ("M1", x - 0.13, y - 0.13, x + 0.13, y + 0.13),
                ("Via1", x - 0.07, y - 0.07, x + 0.07, y + 0.07), ("M2", x - 0.13, y - 0.16, x + 0.13, y + 0.16)]  # M2 >= 0,08 um2
    return out
QN = ["Q%d" % i for i in range(8)]


def netlists():
    f = lambda *p: os.path.join(ROOT, *p)
    subs = scs2cdl.parse([f("depend/tv3/cells/NOR2_X1/NOR2_X1.scs"), f("depend/tv3/cells/XOR2_TG6/XOR2_TG6.scs"),
                          f("depend/tv3/cells/XOR2_X1/XOR2_X1.scs"), f("cells/DFF_TSPC_TMP/DFF_TSPC_TMP.scs"),
                          f("cells/DFF_MS_TMP/DFF_MS_TMP.scs"), f("cells/INV_CLK/INV_CLK.scs")])
    # layout DFF_MS_TMP ve phang (4 NOR2 trong cung cell) nen netlist so sanh cung trai phang NOR2
    return scs2cdl.flatten(subs, "DFF_MS_TMP", {"NOR2_X1"})


def cdl_text(subs, names):
    import tempfile
    out = []
    for n in names:
        t = tempfile.mktemp()
        scs2cdl.emit({k: v for k, v in subs.items()}, n, t)
        out.append(open(t).read())
        os.remove(t)
    seen, txt = set(), []
    for block in "\n".join(out).split(".ENDS"):
        b = block.strip()
        if not b:
            continue
        head = b.splitlines()[0]
        if head in seen:
            continue
        seen.add(head)
        txt.append(b + "\n.ENDS\n")
    return "\n".join(txt)


def lfsr_row(kind, cells, wid, xor_after=7):
    """kind = 'TSPC' hoac 'MS'. xor_after: dat khoi XOR ngay sau flip-flop so nay (7 = cuoi hang, -1 = dau hang).
    Tra ve (Row da di day, dong CDL muc tren)."""
    name = "%s_LFSR_8bit" % kind
    ff = "DFF_%s_TMP" % kind
    ffk = (lambda k: ff) if kind == "MS" else (lambda k: "TSPC_DFF_S" if k == 0 else "TSPC_DFF_R")
    row = rowgen.Row(name)
    if kind == "MS":
        row.place("CK", cells["INV_CLK"], wid["INV_CLK"], ACC["INV_CLK"])
    def xors():
        row.place("X0", cells["XOR2_TG6"], wid["XOR2_TG6"], ACC["XOR2_TG6"])
        row.place("X1", cells["XOR2_TG6"], wid["XOR2_TG6"], ACC["XOR2_TG6"])
        row.place("X2", cells["XOR2_X1"], wid["XOR2_X1"], ACC["XOR2_X1"])
    if xor_after < 0:  # khoi XOR dat dau hang, truoc FF0
        xors()
    x0 = row.x
    for k in range(8):
        f = ffk(k)
        row.place("F%d" % k, cells[f], wid[f], ACC[f], drop(f))
        if k == xor_after:
            xors()
    F = lambda k, p: ("F%d" % k, p)
    if kind == "MS":
        row.connect("CLK", ("CK", "A"), *[F(k, "CLK") for k in range(8)])
        row.connect("CLKB", ("CK", "Y"), *[F(k, "CLKB") for k in range(8)])
    else:
        row.connect("CLK", *[F(k, "CLK") for k in range(8)])
    # RST: FF0 nap 1 qua chan SET, FF1..7 nap 0 qua chan RST; chan con lai noi GND (chi cell tam MS co ca hai)
    row.connect("RST", F(0, "SET"), *[F(k, "RST") for k in range(1, 8)])
    if kind == "MS":
        row.tie_gnd(F(0, "RST"))
        # SET cua DFF_MS_TMP nam o ray Metal2 cao: noi GND qua Metal4 ngan + diem xuong ray
        for k in range(1, 8):
            row.connect("G%d" % k, F(k, "SET"))
            row.rail("G%d" % k, x0 + k * wid[ff] + 5.94)
    row.connect("D0", ("X2", "Y"), F(0, "D"))
    for k in range(7):
        row.connect("Q%d" % k, F(k, "Q"), F(k + 1, "D"))
    row.connect("Q7", F(7, "Q"))
    row.connect("Q0", ("X0", "A")); row.connect("Q5", ("X0", "B"))
    row.connect("Q6", ("X1", "A")); row.connect("Q7", ("X1", "B"))
    row.connect("t05", ("X0", "Y"), ("X2", "A"))
    row.connect("t67", ("X1", "Y"), ("X2", "B"))
    top = dict((n, None) for n in ["CLK", "RST"] + QN)
    row.route(top)
    ck = "CLK CLKB" if kind == "MS" else "CLK"
    cdl = [".SUBCKT %s CLK RST %s VDD GND" % (name, " ".join(QN))]
    if kind == "MS":
        cdl.append("XCK CLK CLKB VDD GND INV_CLK")
        cdl.append("XF0 D0 %s RST GND Q0 VDD GND %s" % (ck, ff))
        for k in range(1, 8):
            cdl.append("XF%d Q%d %s GND RST Q%d VDD GND %s" % (k, k - 1, ck, k, ff))
    else:  # cell TV2: D CLK SET|RST Q QB VDD GND, QB de ho
        cdl.append("XF0 D0 CLK RST Q0 qb0 VDD GND TSPC_DFF_S")
        for k in range(1, 8):
            cdl.append("XF%d Q%d CLK RST Q%d qb%d VDD GND TSPC_DFF_R" % (k, k - 1, k, k))
    cdl += ["XX0 Q0 Q5 t05 VDD GND XOR2_TG6", "XX1 Q6 Q7 t67 VDD GND XOR2_TG6", "XX2 t05 t67 D0 VDD GND XOR2_X1", ".ENDS"]
    return row, "\n".join(cdl) + "\n"


def main():
    for d in (GDS, CDL, IMG):
        os.makedirs(d, exist_ok=True)
    subs = netlists()
    gen = {"DFF_TSPC_TMP": cellgen.dff_tspc_tmp(), "DFF_MS_TMP": cellgen.dff_ms_tmp(), "INV_CLK": cellgen.inv_clk()}
    cells, wid = {}, {}
    for n, g in gen.items():
        cells[n] = g.build(); wid[n] = round(g.width, 3)
    for c in gdstk.read_gds(TV2G).cells:  # TSPC_DFF_S, TSPC_DFF_R (TV2); rong = prBoundary
        cells[c.name] = c
        wid[c.name] = round([p for p in c.polygons if (p.layer, p.datatype) == (99, 0)][0].bounding_box()[1][0], 3)
    tv2cdl = "".join(open(os.path.join(TV2C, n + ".cdl")).read().replace("* CDL\n", "")
                     for n in ("TSPC_DFF_S", "TSPC_DFF_R"))
    for n in ("XOR2_TG6", "XOR2_X1"):
        cells[n] = gdstk.read_gds(os.path.join(TV3G, n + ".gds")).top_level()[0]
        wid[n] = round(cells[n].bounding_box()[1][0] - 0.12, 3)
    info = {}
    for n in gen:  # cell la
        lib = gdstk.Library("tv4_lay", unit=1e-6, precision=5e-10)
        lib.add(cells[n]); lib.write_gds(os.path.join(GDS, n + ".gds"))
        open(os.path.join(CDL, n + ".cdl"), "w").write(cdl_text(subs, [n]))
        info[n] = {"width": wid[n], "height": cellgen.H, "area": round(wid[n] * cellgen.H, 2)}
    for kind in ("TSPC", "MS"):
        row, top = lfsr_row(kind, cells, wid, XOR_POS[kind])
        lib = gdstk.Library("tv4_lay", unit=1e-6, precision=5e-10)
        if kind == "MS":
            used, ext = ["DFF_MS_TMP", "XOR2_TG6", "XOR2_X1", "INV_CLK"], ""
        else:
            used, ext = ["XOR2_TG6", "XOR2_X1"], tv2cdl
        for u in used + ([] if kind == "MS" else ["TSPC_DFF_S", "TSPC_DFF_R"]):
            lib.add(cells[u])
        lib.add(row.cell)
        lib.write_gds(os.path.join(GDS, row.name + ".gds"))
        open(os.path.join(CDL, row.name + ".cdl"), "w").write(ext + cdl_text(subs, used) + "\n" + top)
        info[row.name] = {"width": round(row.width, 3), "height": cellgen.H, "area": round(row.width * cellgen.H, 2),
                          "metal4_tracks": row.track_of}
    for n in list(gen) + ["TSPC_LFSR_8bit", "MS_LFSR_8bit"]:
        render.draw(os.path.join(GDS, n + ".gds"), n, os.path.join(IMG, "layout_%s.png" % n),
                    1.8 if n in gen else 0.3)
    json.dump(info, open(os.path.join(ROOT, "layout", "dien_tich.json"), "w"), indent=1)
    print(json.dumps({k: v["area"] for k, v in info.items()}))


if __name__ == "__main__":
    main()
