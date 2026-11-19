#!/usr/bin/env python3
"""precheck_ngspice.py - KIEM TRA LOGIC SO BO bang ngspice (khong phai Spectre, khong phai gpdk090).
Dich cac file netlist Spectre (dang con: subckt/ends/instance) sang SPICE, dung mo hinh MOS level 1
"gia" ten gpdk090_nmos1v/pmos1v (VT 0.35 V), mo phong cung kich thich nhu tb/*.scs va so voi tb/*.exp.
Muc dich: bat loi noi day / logic / thu tu chan TRUOC khi chay Spectre that trong may ao.
So lieu tre/nang luong o day KHONG dung cho bao cao.
    python3 scripts/ngspice/precheck_ngspice.py [ten_tb ...]
"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(HERE, "build")
VDD = 1.2
MODELS = """* mo hinh MOS level 1 gia lap (chi de kiem tra logic)
.model gpdk090_nmos1v nmos level=1 vto=0.35 kp=280u lambda=0.15 gamma=0.3 phi=0.8 tox=2.5n cgso=0.3n cgdo=0.3n
.model gpdk090_pmos1v pmos level=1 vto=-0.35 kp=90u lambda=0.15 gamma=0.3 phi=0.8 tox=2.5n cgso=0.3n cgdo=0.3n
"""


def conv_file(src, dst):
    out = []
    for raw in open(src):
        line = re.sub(r"\bGND\b", "gnd_x", raw.rstrip("\n"))   # ngspice coi 'gnd' la nut 0
        s = line.strip()
        if not s or s.startswith("simulator") or s.startswith("global"):
            continue
        if s.startswith("//"):
            out.append("*" + s[2:]); continue
        s = re.sub(r"\s*//.*$", "", s)
        m = re.match(r'include\s+"([^"]+)"', s)
        if m:
            p = m.group(1)
            out.append('.include "%s"' % (p[:-4] + ".sp")); continue
        if s.startswith("subckt "):
            out.append("." + s); continue
        if s.startswith("ends"):
            out.append(".ends"); continue
        m = re.match(r"(\S+)\s*\(([^)]*)\)\s*(\S+)\s*(.*)$", s)
        if m:
            name, nodes, master, params = m.groups()
            if master.startswith("gpdk090"):
                nm = name if name[0] in "Mm" else "M" + name
                out.append("%s %s %s %s" % (nm, nodes, master, params))
            else:
                out.append("X%s %s %s" % (name, nodes, master))
            continue
        raise SystemExit("khong dich duoc dong: %s (%s)" % (line, src))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w").write("\n".join(out) + "\n")


def build_lib():
    for sub in ["deps/tv3/cells", "deps/tv3/blocks", "cells", "blocks"]:
        for dp, _, fs in os.walk(os.path.join(ROOT, sub)):
            for f in fs:
                if f.endswith(".scs") and not f.startswith("tb_"):
                    src = os.path.join(dp, f)
                    rel = os.path.relpath(src, ROOT)
                    conv_file(src, os.path.join(BUILD, rel[:-4] + ".sp"))


def read_exp(p):
    d = {"V": []}
    for l in open(p):
        t = l.split()
        if not t or t[0].startswith("#"):
            continue
        if t[0] == "V":
            d["V"].append(t[3])
        elif t[0] == "OUT":
            d["OUT"] = t[1:]
        else:
            d[t[0]] = float(t[1])
    return d


def tb_to_spice(name):
    """Dich than testbench Spectre (tb/<name>.scs) sang SPICE (chi cac dang dung trong gen_tb.py)."""
    body = open(os.path.join(ROOT, "tb", name + ".scs")).read().splitlines()
    par = {}
    out = ["* %s (ngspice)" % name, MODELS]
    for inc in ["deps/tv3/cells/cells.sp", "deps/tv3/blocks/XORTAP8.sp", "deps/tv3/blocks/CFSR_FB.sp",
                "cells/cells.sp", "blocks/LFSR_8bit.sp", "blocks/LT_RTPG_8bit.sp"]:
        out.append('.include "%s"' % os.path.join(BUILD, inc))
    saves = []
    for l in body:
        s = re.sub(r"\s*//.*$", "", re.sub(r"\bGND\b", "gnd_x", l)).strip()
        if not s or s.startswith(("simulator", "global", "opts")):
            continue
        if s.startswith("parameters"):
            for kv in s.split()[1:]:
                k, v = kv.split("="); par[k] = v
            out.append(".param " + " ".join("%s=%s" % kv for kv in par.items()))
            continue
        if s.startswith("save"):
            saves = [w for w in s.split()[1:] if ":" not in w]; continue
        if s.startswith("tran"):
            m = re.search(r"stop=(\S+)", s)
            stop = m.group(1).replace("tclk", "{tclk}")
            out.append(".tran 20p {%s}" % m.group(1)); continue
        m = re.match(r"(\S+)\s*\(([^)]*)\)\s*(\S+)\s*(.*)$", s)
        name_, nodes, master, params = m.groups()
        if master == "vsource":
            kv = dict(x.split("=", 1) for x in params.split())
            if kv.get("type") == "pulse":
                out.append("%s %s PULSE(%s %s {%s} {%s} {%s} {%s} {%s})" % (
                    name_, nodes, kv["val0"], kv["val1"], kv["delay"], kv["rise"], kv["fall"], kv["width"], kv["period"]))
            else:
                out.append("%s %s DC %s" % (name_, nodes, kv["dc"]))
        else:
            out.append("X%s %s %s" % (name_, nodes, master))
    return out, saves


def run(name):
    exp = read_exp(os.path.join(ROOT, "tb", name + ".exp"))
    lines, saves = tb_to_spice(name)
    outs = exp["OUT"]
    data = os.path.join(BUILD, name + ".dat")
    lines += [".options method=gear reltol=1e-3", ".control", "set wr_singlescale", "set wr_vecnames", "run",
              "wrdata %s %s" % (data, " ".join("v(%s)" % o for o in outs)),
              "meas tran iavg AVG i(VVDD) from=0 to=%g" % (len(exp["V"]) * exp["T"]),
              "quit", ".endc", ".end"]
    if os.path.exists(data):
        os.remove(data)          # khong doc nham ket qua cu
    sp = os.path.join(BUILD, name + ".sp")
    open(sp, "w").write("\n".join(lines) + "\n")
    r = subprocess.run(["ngspice", "-b", sp], capture_output=True, text=True, timeout=1800)
    if not os.path.exists(data):
        print(r.stdout[-2000:], r.stderr[-2000:]); return False
    rows = [l.split() for l in open(data)]
    hdr = rows[0]; rows = [[float(x) for x in r_] for r_ in rows[1:]]
    T, M = exp["T"], exp["MARGIN"]
    idx = 0; bad = 0; ok = 0
    for k, want in enumerate(exp["V"]):
        ts = (k + 1) * T - M
        while idx + 1 < len(rows) and rows[idx + 1][0] <= ts:
            idx += 1
        r0 = rows[idx]
        e = []
        for i, w in enumerate(want):
            if w == "x":
                continue
            v = r0[i + 1]
            good = v > 0.9 * VDD if w == "1" else v < 0.1 * VDD
            if not good:
                e.append("%s=%.2f(can %s)" % (outs[i], v, w))
        if e:
            bad += 1
            if bad <= 8:
                print("  SAI vector %d: %s" % (k, " ".join(e)))
        else:
            ok += 1
    print("%s %-22s %d/%d vector dung" % ("PASS" if not bad else "FAIL", name, ok, len(exp["V"])))
    return bad == 0


if __name__ == "__main__":
    build_lib()
    names = sys.argv[1:] or ["tb_MS_LFSR", "tb_TSPC_LFSR", "tb_TSPC_LFSR_CMOS", "tb_TSPC_CFSR",
                             "tb_LT_RTPG_LP1", "tb_LT_RTPG_LP0"]
    allok = True
    for n in names:
        allok &= run(n)
    sys.exit(0 if allok else 1)
