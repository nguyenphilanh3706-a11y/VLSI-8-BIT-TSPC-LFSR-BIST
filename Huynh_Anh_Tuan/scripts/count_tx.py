#!/usr/bin/env python3
"""count_tx.py - dem so transistor (phang hoa) va so cong MOS noi vao CLK cua tung cell TV4 tu netlist Spectre.
    python3 scripts/count_tx.py  ->  in bang + ghi results/so_transistor.md"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "cadence"))
from gen_skill import FILES, parse

cells = {}
for f in FILES:
    for c in parse(f):
        cells[c["name"]] = c


def flat(name, ports=None):
    """tra ve (so MOS, so cong MOS noi vao net 'CLK'/'CLKB' cua cell goc)"""
    c = cells[name]
    m = dict(zip(c["pins"], ports or c["pins"]))
    n = clk = 0
    for (iname, nodes, master, kv) in c["inst"]:
        nodes = [m[x] if x in m else "_" + x for x in nodes]      # net noi bo: them "_"
        if master.startswith("gpdk090"):
            n += 1
            if nodes[1].lstrip("_") in ("CLK", "CLKB"):     # cong noi CLK hoac CLKB (ke ca CLKB noi bo)
                clk += 1
        else:
            a, b = flat(master, nodes)
            n += a; clk += b
    return n, clk


rows = []
for nmx in ["DFF_MS_TMP", "DFF_TSPC_TMP", "XORTAP8", "XORTAP8_CMOS", "ZERO7", "CFSR_FB", "AND2_T", "MUX2_N",
            "MS_LFSR_8bit", "TSPC_LFSR_8bit", "TSPC_LFSR_8bit_CMOS", "TSPC_CFSR_8bit", "LT_RTPG_8bit"]:
    n, k = flat(nmx)
    rows.append((nmx, n, k))
out = ["| Cell | So transistor | Cong MOS noi CLK/CLKB (tinh ca inverter tao CLKB) |", "|---|---:|---:|"]
out += ["| %s | %d | %d |" % r for r in rows]
txt = "\n".join(out)
print(txt)
os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
open(os.path.join(ROOT, "results", "so_transistor.md"), "w").write(
    "# So transistor va tai clock (dem tu netlist, flip-flop TAM THOI cua TV4)\n\n" + txt +
    "\n\nLuu y: DFF_*_TMP la cell tam; khi thay bang cell TV1/TV2 thi chay lai `python3 scripts/count_tx.py`.\n")
