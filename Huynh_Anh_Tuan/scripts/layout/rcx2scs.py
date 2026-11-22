"""rcx2scs.py - chuyen netlist Assura RCX (dang HSPICE) sang file Spectre dung duoc trong testbench.

  python3 scripts/layout/rcx2scs.py <rcx.sp> <out.scs> <TEN_KHOI> "<chan theo thu tu testbench>"
Vi du: python3 scripts/layout/rcx2scs.py layout/rcx/TSPC_LFSR_8bit_rcx.sp layout/rcx/TSPC_LFSR_8bit_post.scs \
         TSPC_LFSR_8bit "CLK RST Q0 Q1 Q2 Q3 Q4 Q5 Q6 Q7 VDD GND"
- doi model nmos1v/pmos1v -> gpdk090_nmos1v/gpdk090_pmos1v (ten trong gpdk090.scs);
- bo chu thich '$...', bo tham so simW/fw (model khong nhan), doi '#' trong ten nut thanh '_h';
- doi ten subckt RCX thanh <TEN>_RCX va them subckt <TEN> boc ngoai theo thu tu chan cua testbench.
"""
import re, sys

src, dst, name, pins = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split()
out, rcx_pins = [], None
for line in open(src):
    line = line.rstrip("\n")
    if line.startswith("*") or not line.strip():
        continue
    line = line.split("$")[0].rstrip()
    line = line.replace("#", "_h")
    line = re.sub(r"\bsimW=\S+", "", line)
    line = re.sub(r"\bfw=\S+", "", line)
    m = re.match(r"\.SUBCKT\s+(\S+)\s+(.*)", line, re.I)
    if m:
        rcx_pins = m.group(2).split()
        line = ".SUBCKT %s_RCX %s" % (name, m.group(2))
    if re.match(r"\.ENDS", line, re.I):
        line = ".ENDS %s_RCX" % name
    line = re.sub(r"\s(n|p)mos1v(\s|$)", lambda k: " gpdk090_%smos1v%s" % (k.group(1), k.group(2)), line)
    if line.strip() == "+":
        continue
    out.append(line)
assert set(rcx_pins) == set(pins), (rcx_pins, pins)
hdr = ["// %s sau layout: Assura RCX (R + C), sinh boi scripts/layout/rcx2scs.py" % name,
       "simulator lang=spice"]
tail = ["simulator lang=spectre",
        "subckt %s %s" % (name, " ".join(pins)),
        "    XR (%s) %s_RCX" % (" ".join(rcx_pins), name),
        "ends %s" % name]
open(dst, "w").write("\n".join(hdr + out + tail) + "\n")
print("%s: %d transistor, %d R, %d C" % (dst, sum(l.startswith("M") for l in out),
      sum(l.startswith("R") for l in out), sum(l.startswith("C") for l in out)))
