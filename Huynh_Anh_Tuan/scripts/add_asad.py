#!/usr/bin/env python3
"""add_asad.py - tao ban sao netlist flip-flop TV2 co them as/ad/ps/pd (dien tich, chu vi vung khuech tan) cho moi MOS,
theo cung quy uoc trong schematic cua TV1 va bang so sanh cua TV2 (Tuan4/SO_SANH_TV1.md):
    as = ad = W x 0,28 um,  ps = pd = 2 x (W + 0,28 um)
Netlist goc cua TV2 khong co as/ad nen mo hinh dung dien tich tiep giap mac dinh (lon) -> cham va ton cong suat hon;
de so sanh truoc layout cong bang voi MS_DFF_SetReset cua TV1 (co as/ad), cac testbench *_asad dung ban sao nay.
    python3 scripts/add_asad.py   ->  depend/tv2/cells_asad/ (khong sua depend/tv2/cells/)"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "depend", "tv2", "cells")
DST = os.path.join(ROOT, "depend", "tv2", "cells_asad")
LD = 0.28  # um


def um(v):
    v = v.strip()
    m = re.match(r"([0-9.]+)([nu]?)$", v)
    x = float(m.group(1))
    return x * 1e-3 if m.group(2) == "n" else x


for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".scs"):
            continue
        rel = os.path.relpath(os.path.join(root, f), SRC)
        out = []
        for line in open(os.path.join(root, f)):
            m = re.search(r"gpdk090_[np]mos1v\s+w=([0-9.]+[nu]?)", line)
            if m and "as=" not in line:
                w = um(m.group(1))
                a = w * LD
                p = 2 * (w + LD)
                code, sep, cmt = line.rstrip("\n").partition("//")
                line = "%s as=%.4fp ad=%.4fp ps=%.3fu pd=%.3fu%s\n" % (code.rstrip(), a, a, p, p, ("  //" + cmt) if sep else "")
            out.append(line)
        os.makedirs(os.path.dirname(os.path.join(DST, rel)), exist_ok=True)
        open(os.path.join(DST, rel), "w").write("".join(out).replace("cells.scs - flip-flop TSPC cua TV2", "cells.scs - flip-flop TSPC cua TV2, BAN THEM as/ad (scripts/add_asad.py)"))
        print("->", os.path.join("depend/tv2/cells_asad", rel))
