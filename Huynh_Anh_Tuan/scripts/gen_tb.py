#!/usr/bin/env python3
"""gen_tb.py - sinh testbench Spectre + bang gia tri mong doi (.exp) cho TV4 tu golden model MATLAB.
Gia tri mong doi doc tu golden_model/out/*.csv (chay golden_model/lfsr_golden_tv4.m truoc).
Chay o may co Python 3 (khong can trong may ao):  python3 scripts/gen_tb.py
Ket qua: tb/tb_<ten>.scs (than), tb/tb_<ten>_{NN,SS,FF}.scs (corner), tb/tb_<ten>.exp
Dinh dang .exp giong scripts/check.awk cua TV3 (T, MARGIN, STRICT, OUT, V k do_tre bit ; mo ta).
Thoi gian: RST = 1 tu 0 den 0.5T ; canh len clock thu k tai kT (k >= 1) ; mau vector k tai (k+1)T - MARGIN.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GOLD = os.path.join(ROOT, "golden_model", "out")


def read_hex(fname, col):
    """Doc cot hex (dem tu 0) cua file CSV do golden model MATLAB xuat, bo dong tieu de."""
    p = os.path.join(GOLD, fname)
    if not os.path.isfile(p):
        sys.exit("Thieu %s - chay golden_model/lfsr_golden_tv4.m trong MATLAB truoc." % p)
    rows = [l.strip().split(",") for l in open(p) if l.strip()][1:]
    return [int(r[col], 16) for r in rows]


def extend(seq, period, n):
    """Lap lai chuoi tuan hoan (chu ky period) cho du n phan tu."""
    return [seq[k % period] for k in range(n)]


def golden(mode, n):
    """n trang thai Q (k = 0..n-1) tu golden model MATLAB."""
    if mode == "lfsr":
        return extend(read_hex("golden_lfsr_300.csv", 1), 255, n)
    return extend(read_hex("golden_cfsr_256.csv", 1), 256, n)      # CFSR tu 0x00


def golden_lt(n):
    """n gia tri V (LP = 1, k = 2) tu golden model MATLAB; T-FF tro ve 0 sau 255 chu ky."""
    return extend(read_hex("golden_lt_rtpg_k2.csv", 2), 255, n)

TB = os.path.join(ROOT, "tb")
MODEL = "/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs"
INCLUDES = [
    "../deps/tv3/cells/cells.scs",          # cell TV3 (ban sao, xem deps/tv3/NGUON.md)
    "../deps/tv3/blocks/XORTAP8.scs",
    "../deps/tv3/blocks/CFSR_FB.scs",
    "../cells/cells.scs",                    # cell TV4 (INV_CLK, AND2_T, MUX2_N, DFF_*)
    "../blocks/LFSR_8bit.scs",
    "../blocks/LT_RTPG_8bit.scs",
]
NCYC = 300          # so canh clock -> 301 vector (0..300); ke hoach nhom: 300 chu ky
TCLK = "2n"         # 500 MHz mac dinh ; run_fmax.sh thay dong "parameters"
QN = ["Q%d" % i for i in range(8)]
VN = ["V%d" % i for i in range(8)]


def bits(x, n=8):
    return "".join(str((x >> i) & 1) for i in range(n))     # thu tu Q0..Q7


def common_head(title, direct_clock=False):
    s = ["// %s" % title,
         "// Sinh boi scripts/gen_tb.py - khong sua tay (sua gen_tb.py roi chay lai).",
         "simulator lang=spectre",
         "global 0",
         "parameters tclk=%s trf=20p" % TCLK,
         "VVDD (VDD 0) vsource dc=1.2          // nguon rieng cua DUT -> do nang luong DUT",
         "VVDDCK (VDDCK 0) vsource dc=1.2      // nguon rieng bo dem clock -> do cong suat clock",
         "VVDDL (VDDL 0) vsource dc=1.2        // nguon rieng tai (gia lap ngo vao CUT)",
         "VGND (GND 0) vsource dc=0",
         "VRST (RST 0) vsource type=pulse val0=1.2 val1=0 delay=0.5*tclk rise=20p fall=20p width=1 period=2"]
    if direct_clock:
        s += ["// clock dua thang tu nguon (khong dem) de quet do doc suon trf",
              "VCK (CLK 0) vsource type=pulse val0=0 val1=1.2 delay=tclk rise=trf fall=trf width=0.5*tclk-trf period=tclk"]
    else:
        s += ["VCK (ck0 0) vsource type=pulse val0=0 val1=1.2 delay=tclk rise=trf fall=trf width=0.5*tclk-trf period=tclk",
              "XCK1 (ck0 ckb VDDCK GND) INV_CLK",
              "XCK2 (ckb CLK VDDCK GND) INV_CLK"]
    return s


def tail(saves, nvec):
    return ["save CLK RST %s VVDD:p VVDDCK:p VVDDL:p" % " ".join(saves),
            "opts options save=selected temp=27 reltol=1e-3",
            "tran tran stop=%d*tclk+0.2*tclk maxstep=20p errpreset=moderate" % nvec]


def loads(nets, fo=1):
    s = []
    for n in nets:
        for j in range(fo):
            s.append("XL_%s_%d (%s ld_%s_%d VDDL GND) INV_X1" % (n, j, n, n, j))
    return s


def write_exp(name, outs, vecs, tclk=2e-9, note=""):
    p = os.path.join(TB, name + ".exp")
    with open(p, "w") as f:
        f.write("# %s: gia tri mong doi (sinh tu golden model MATLAB, golden_model/out). %s\n" % (name, note))
        f.write("T %.6g\nMARGIN %.6g\nSTRICT 1\nOUT %s\n" % (tclk, 0.05 * tclk, " ".join(outs)))
        for k, (w, d) in enumerate(vecs):
            f.write("V %d %d %s ; %s\n" % (k, 0 if k == 0 else 1, w, d))


def write_tb(name, lines, corners=("NN", "SS", "FF")):
    with open(os.path.join(TB, name + ".scs"), "w") as f:
        f.write("\n".join(lines) + "\n")
    for c in corners:
        w = ["// %s, corner %s" % (name, c), "simulator lang=spectre",
             'include "%s" section=%s' % (MODEL, c)]
        w += ['include "%s"' % i for i in INCLUDES]
        w += ['include "%s.scs"' % name]
        with open(os.path.join(TB, "%s_%s.scs" % (name, c)), "w") as f:
            f.write("\n".join(w) + "\n")


def lfsr_tb(name, cell, mode="lfsr", direct=False):
    seed = 0x01 if mode == "lfsr" else 0x00
    seq = golden(mode, NCYC + 1)                # NCYC+1 trang thai
    L = common_head("%s: %s, %d canh clock, seed %02X sau RST" % (name, cell, NCYC, seed), direct)
    L += ["XDUT (CLK RST %s VDD GND) %s" % (" ".join(QN), cell)]
    L += loads(QN)
    L += tail(QN, NCYC + 1)
    write_tb(name, L, ("NN",) if direct else ("NN", "SS", "FF"))
    write_exp(name, QN, [(bits(s), "k=%d Q=%02X" % (k, s)) for k, s in enumerate(seq)],
              note="%s, %d vector" % (mode.upper(), len(seq)))


def lt_tb(name, lp):
    seq = golden("lfsr", NCYC + 1)
    out = golden_lt(NCYC + 1) if lp else seq
    L = common_head("%s: TSPC_LFSR_8bit + LT_RTPG_8bit, LP=%d, moi V_i co 4 INV tai (FO4)" % (name, lp))
    L += ["VLP (LP 0) vsource dc=%s" % ("1.2" if lp else "0")]
    L += ["XLFSR (CLK RST %s VDD GND) TSPC_LFSR_8bit" % " ".join(QN),
          "XLT (%s CLK RST LP %s VDD GND) LT_RTPG_8bit" % (" ".join(QN), " ".join(VN))]
    L += loads(VN, 4)
    L += tail(QN + VN, NCYC + 1)
    write_tb(name, L)
    vecs = [(bits(q) + bits(v), "k=%d Q=%02X V=%02X" % (k, q, v)) for k, (q, v) in enumerate(zip(seq, out))]
    write_exp(name, QN + VN, vecs, note="LT-RTPG k=2, LP=%d" % lp)


if __name__ == "__main__":
    os.makedirs(TB, exist_ok=True)
    lfsr_tb("tb_MS_LFSR", "MS_LFSR_8bit")
    lfsr_tb("tb_TSPC_LFSR", "TSPC_LFSR_8bit")
    lfsr_tb("tb_TSPC_LFSR_CMOS", "TSPC_LFSR_8bit_CMOS")
    lfsr_tb("tb_TSPC_CFSR", "TSPC_CFSR_8bit", mode="cfsr")
    lfsr_tb("tb_TSPC_LFSR_slew", "TSPC_LFSR_8bit", direct=True)
    lfsr_tb("tb_MS_LFSR_slew", "MS_LFSR_8bit", direct=True)
    lt_tb("tb_LT_RTPG_LP1", 1)
    lt_tb("tb_LT_RTPG_LP0", 0)
    print("Da sinh testbench trong", TB)
    for f in sorted(os.listdir(TB)):
        print("  ", f)
