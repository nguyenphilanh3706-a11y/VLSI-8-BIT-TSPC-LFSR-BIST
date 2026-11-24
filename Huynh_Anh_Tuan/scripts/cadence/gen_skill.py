#!/usr/bin/env python3
"""gen_skill.py - sinh script SKILL ve schematic + symbol trong thu vien Virtuoso "tv4" tu cac netlist Spectre.
    python3 scripts/cadence/gen_skill.py  ->  scripts/cadence/tv4_build.il
Moi subckt -> 1 cell (schematic + symbol). Linh kien MOS: gpdk090 nmos1v/pmos1v (chan D G S B).
Noi day kieu "doan day ngan + nhan ten net" (cung ten = cung net), dat instance theo hang luoi.
Cell cua TV3 (INV_X1, NAND2_X1, NOR2_X1, NOR3_X1, XOR2_X1, XOR2_TG6, AOI21_X1, XNOR2_X1, XORTAP8, CFSR_FB, CFSR_FB_OPT) duoc chep lai
vao tv4 (BAN SAO de mo phong/ve layout duoc ngay); khi TV3 co thu vien rieng thi doi master sang thu vien do.
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # scripts/cadence -> goc

FILES = [  # thu tu phu thuoc: cell con truoc
    "depend/tv3/cells/INV_X1/INV_X1.scs", "depend/tv3/cells/NAND2_X1/NAND2_X1.scs",
    "depend/tv3/cells/NOR2_X1/NOR2_X1.scs", "depend/tv3/cells/XOR2_X1/XOR2_X1.scs",
    "depend/tv3/cells/NOR3_X1/NOR3_X1.scs", "depend/tv3/cells/XOR2_TG6/XOR2_TG6.scs",
    "depend/tv3/cells/AOI21_X1/AOI21_X1.scs", "depend/tv3/cells/XNOR2_X1/XNOR2_X1.scs",
    "depend/tv3/blocks/XORTAP8.scs", "depend/tv3/blocks/CFSR_FB.scs", "depend/tv3/blocks/CFSR_FB_OPT.scs",
    "cells/INV_CLK/INV_CLK.scs", "cells/AND2_T/AND2_T.scs", "cells/MUX2_N/MUX2_N.scs",
    "cells/DFF_MS_TMP/DFF_MS_TMP.scs", "cells/DFF_TSPC_TMP/DFF_TSPC_TMP.scs",
    "depend/tv1/cells/MS_DFF_SetReset/MS_DFF_SetReset.scs", "cells/DFF_MS/DFF_MS.scs",
    "depend/tv2/cells/TSPC_DFF_R/TSPC_DFF_R.scs", "depend/tv2/cells/TSPC_DFF_S/TSPC_DFF_S.scs",
    "blocks/LFSR_8bit.scs", "blocks/LT_RTPG_8bit.scs",
]
OUTPUTS = {"Y", "FB", "Z", "Q", "QB", "Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7",
           "V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7"}
SUPPLY = {"VDD", "VSS", "GND"}
SKIP_CELLS = {"CFSR_FB_CMOS"}   # ban doi chung cua TV3, TV4 khong dung
Q_INPUT_CELLS = {"XORTAP8", "XORTAP8_CMOS", "ZERO7", "CFSR_FB", "CFSR_FB_OPT", "LT_RTPG_8bit"}   # o cac cell nay Q0..Q7 la NGO VAO
MOS = {"gpdk090_nmos1v": "nmos1v", "gpdk090_pmos1v": "pmos1v"}
TV3_CELLS = {"INV_X1", "NAND2_X1", "NOR2_X1", "NOR3_X1", "XOR2_X1", "XOR2_TG6", "AOI21_X1", "XNOR2_X1", "XORTAP8", "XORTAP8_CMOS", "ZERO7", "CFSR_FB", "CFSR_FB_OPT"}


def parse(path):
    cells, cur = [], None
    for raw in open(os.path.join(ROOT, path)):
        s = re.sub(r"//.*$", "", raw).strip()
        if not s or s.startswith(("simulator", "include", "global")):
            continue
        if s.startswith("subckt "):
            t = s.split()
            cur = {"name": t[1], "pins": t[2:], "inst": [], "src": path}
            continue
        if s.startswith("ends"):
            cells.append(cur); cur = None; continue
        m = re.match(r"(\S+)\s*\(([^)]*)\)\s*(\S+)\s*(.*)$", s)
        if m and cur is not None:
            n, nodes, master, params = m.groups()
            kv = dict(x.split("=", 1) for x in params.split()) if params else {}
            cur["inst"].append((n, nodes.split(), master, kv))
    return cells


def nm(v):
    """0.24u -> 240n"""
    m = re.match(r"([\d.]+)u$", v)
    return "%gn" % (float(m.group(1)) * 1000) if m else v


def skill_str(s):
    return '"%s"' % s


def main():
    cells = []
    for f in FILES:
        cells += [c for c in parse(f) if c["name"] not in SKIP_CELLS]
    known = {c["name"]: c for c in cells}
    L = [HEAD]
    for c in cells:
        L.append(";; ---- %s  (nguon: %s%s)" % (c["name"], c["src"], ", BAN SAO cell TV3" if c["name"] in TV3_CELLS else ""))
        L.append('when(tv4Begin("%s")' % c["name"])
        L.append('  unless(errset(progn(')
        for i, p in enumerate(c["pins"]):
            isout = p in OUTPUTS and not (c["name"] in Q_INPUT_CELLS and p.startswith("Q"))
            d = "inputOutput" if p in SUPPLY else ("output" if isout else "input")
            L.append('  tv4Pin(tv4Cv "%s" "%s" %d)' % (p, d, i))
        for (n, nodes, master, kv) in c["inst"]:
            if master in MOS:
                L.append('  tv4Mos("%s" "%s" list(%s) "%s" "%s")' % (
                    n, MOS[master], " ".join(skill_str(x) for x in nodes), nm(kv.get("w", "")), nm(kv.get("l", "100n"))))
            else:
                if master not in known:
                    raise SystemExit("master %s chua co (thu tu FILES?)" % master)
                pins = known[master]["pins"]
                assert len(pins) == len(nodes), (c["name"], n)
                # net chi noi vao dung mot chan (vd QB cua flip-flop TV2 de ho) -> ve noConn thay vi nhan ten
                nodes = ["__NC__" if (x not in c["pins"] and sum(y.count(x) for (_, y, _, _) in c["inst"]) == 1) else x
                         for x in nodes]
                L.append('  tv4Sub("%s" "%s" list(%s) list(%s))' % (
                    n, master, " ".join(skill_str(x) for x in pins), " ".join(skill_str(x) for x in nodes)))
        L.append('  tv4End()) t)')
        L.append('    tv4Out("!! %s LOI: %L\\n" tv4Cell errset.errset)'
                 '    when(tv4Cv dbClose(tv4Cv))))')
        L.append("")
    L.append(TAIL)
    out = os.path.join(ROOT, "scripts", "cadence", "tv4_build.il")
    open(out, "w").write("\n".join(L) + "\n")
    print("Da ghi", out, "-", len(cells), "cell")


HEAD = r""";; tv4_build.il - SINH TU DONG boi scripts/cadence/gen_skill.py (khong sua tay; sua netlist roi sinh lai).
;; Ve schematic + symbol cho moi subckt cua TV4 trong thu vien "tv4" (tao truoc bang tv4_lib.il).
;; Chay trong CIW:  load("<thu muc>/scripts/cadence/tv4_build.il")
;; Mac dinh KHONG ghi de cell da co schematic. Muon ve lai:  tv4Overwrite = t  roi load lai.
;; Nhat ky: /home/buet/pjck_tv4/tv4_build_log.txt
unless(boundp('tv4Overwrite) tv4Overwrite = nil)
tv4Lib = "tv4"
tv4Pdk = "gpdk090"
tv4Grid = 0.0625
tv4MaxW = 24.0
tv4Log = outfile("/home/buet/pjck_tv4/tv4_build_log.txt" "w")
tv4Done = nil
tv4Skip = nil

procedure(tv4Out(fmt @rest args)
  apply('printf cons(fmt args))
  when(tv4Log apply('fprintf cons(tv4Log cons(fmt args)))))

procedure(tv4Snap(v) round(v / tv4Grid) * tv4Grid)

;; toa do chan termName cua instance (he toa do cellview)
procedure(tv4TermPt(inst termName)
  let((term pin)
    term = dbFindTermByName(inst~>master termName)
    unless(term error("tv4TermPt: %s khong co chan %s\n" inst~>name termName))
    pin = car(term~>pins)
    dbTransformPoint(centerBox(pin~>fig~>bBox) inst~>transform)))

;; doan day ngan 0.25 tu chan, huong ra ngoai than instance, nhan ten net o dau day
procedure(tv4Stub(inst termName netName)
  let((p bb cx cy dx dy q w d)
    d = 0.25
    p = tv4TermPt(inst termName)
    bb = inst~>bBox
    cx = (xCoord(car(bb)) + xCoord(cadr(bb))) / 2.0
    cy = (yCoord(car(bb)) + yCoord(cadr(bb))) / 2.0
    dx = xCoord(p) - cx
    dy = yCoord(p) - cy
    q = if(abs(dx) >= abs(dy)
          then if(dx < 0 then list(xCoord(p) - d yCoord(p)) else list(xCoord(p) + d yCoord(p)))
          else if(dy < 0 then list(xCoord(p) yCoord(p) - d) else list(xCoord(p) yCoord(p) + d)))
    w = schCreateWire(tv4Cv "draw" "direct" list(p q) tv4Grid tv4Grid 0.0)
    if(netName == "__NC__"
      then schCreateInst(tv4Cv tv4Master("basic" "noConn") nil q "R0")   ; chan de ho co chu dich (QB cua TV2)
      else schCreateWireLabel(tv4Cv car(w) q netName "lowerLeft" "R0" "stick" tv4Grid nil))
    q))

;; dat instance vao o tiep theo cua luoi (goc tren-trai cua bBox trung con tro)
procedure(tv4Place(master name)
  let((inst bb wd ht ox oy)
    inst = schCreateInst(tv4Cv master name list(0 0) "R0")
    bb = inst~>bBox
    wd = xCoord(cadr(bb)) - xCoord(car(bb))
    ht = yCoord(cadr(bb)) - yCoord(car(bb))
    when(tv4X > 0.0 && tv4X + wd > tv4MaxW
      tv4X = 0.0  tv4Y = tv4Y - tv4RowH - 1.5  tv4RowH = 0.0)
    ox = tv4Snap(tv4X - xCoord(car(bb)))
    oy = tv4Snap(tv4Y - yCoord(cadr(bb)))
    inst~>xy = list(ox oy)
    tv4X = tv4X + wd + 1.5
    tv4RowH = max(tv4RowH ht)
    inst))

procedure(tv4Master(lib cell)
  let((m)
    m = dbOpenCellViewByType(lib cell "symbol" "" "r")
    unless(m error("tv4Master: khong mo duoc %s/%s/symbol\n" lib cell))
    m))

;; gan tham so CDF (w, l; neu PDK co fw thi gan fw = w de khop khi khong chay callback)
procedure(tv4Param(inst name value)
  let((cdf p)
    cdf = cdfGetInstCDF(inst)
    p = cdf && cdfFindParamByName(cdf name)
    if(p then p~>value = value t else nil)))

procedure(tv4Mos(name dev nodes w l)
  let((inst)
    inst = tv4Place(tv4Master(tv4Pdk dev) name)
    unless(tv4Param(inst "w" w) tv4Out("  !! %s: khong co tham so w (xem CDF)\n" name))
    unless(tv4Param(inst "l" l) tv4Out("  !! %s: khong co tham so l (xem CDF)\n" name))
    tv4Param(inst "fw" w)
    tv4Param(inst "fingers" "1")
    foreach((term net) '("D" "G" "S" "B") nodes
      tv4Stub(inst term net))
    inst))

procedure(tv4Sub(name cell terms nodes)
  let((inst)
    inst = tv4Place(tv4Master(tv4Lib cell) name)
    foreach((term net) terms nodes
      tv4Stub(inst term net))
    inst))

;; pin cua cell: cot ben trai, x = -4
procedure(tv4Pin(cv name dir idx)
  let((master pt q w)
    master = dbOpenCellViewByType("basic"
               cond((dir == "input" "ipin") (dir == "output" "opin") (t "iopin")) "symbol" "" "r")
    pt = list(-4.0 tv4Snap(0.0 - 0.5 * idx))
    schCreatePin(cv master name dir nil pt "R0")
    q = list(-3.75 yCoord(pt))
    w = schCreateWire(cv "draw" "direct" list(pt q) tv4Grid tv4Grid 0.0)
    schCreateWireLabel(cv car(w) q name "lowerLeft" "R0" "stick" tv4Grid nil)
    t))

procedure(tv4Begin(cell)
  if(!tv4Overwrite && ddGetObj(tv4Lib cell "schematic") then
    tv4Out("-- %s: da co schematic, bo qua (tv4Overwrite = t de ve lai)\n" cell)
    tv4Skip = cons(cell tv4Skip)
    nil
  else
    tv4Cell = cell
    ;; ve lai: bo ca cell cu (cell cua TV4, gom CDF) de schViewToView khong mo hop thoai hoi ghi de
    when(ddGetObj(tv4Lib cell)
      unless(ddDeleteObj(ddGetObj(tv4Lib cell))
        ;; khong xoa duoc (vd. cell dang mo): xoa CDF cua cell de schViewToView khong hoi
        when(cdfGetBaseCellCDF(ddGetObj(tv4Lib cell)) cdfDeleteCDF(cdfGetBaseCellCDF(ddGetObj(tv4Lib cell))))
        tv4Out("  (khong xoa duoc cell %s, da xoa CDF cu)\n" cell)))
    tv4Cv = dbOpenCellViewByType(tv4Lib cell "schematic" "schematic" "w")
    tv4X = 0.0  tv4Y = 0.0  tv4RowH = 0.0
    tv4Cv != nil))

procedure(tv4End()
  let((chk)
    chk = schCheck(tv4Cv)
    dbSave(tv4Cv)
    dbClose(tv4Cv)
    schViewToView(tv4Lib tv4Cell tv4Lib tv4Cell "schematic" "symbol" "schSchemToPinList" "schPinListToSymbol")
    tv4Out("-- %s: schCheck (loi canh_bao) = %L, symbol %s\n" tv4Cell chk
           if(ddGetObj(tv4Lib tv4Cell "symbol") "OK" "!! CHUA CO"))
    tv4Done = cons(list(tv4Cell chk) tv4Done)
    t))

unless(ddGetObj(tv4Lib) error("Chua co thu vien tv4: load tv4_lib.il truoc\n"))
tv4Out("== tv4_build.il bat dau, thu vien %s tai %s\n" tv4Lib ddGetObj(tv4Lib)~>readPath)
"""

TAIL = r"""tv4Out("== Xong: %d cell ve moi, %d cell bo qua. Tong ket schCheck:\n" length(tv4Done) length(tv4Skip))
foreach(x reverse(tv4Done) tv4Out("   %-20s %L\n" car(x) cadr(x)))
close(tv4Log)
tv4Log = nil
printf("Nhat ky: /home/buet/pjck_tv4/tv4_build_log.txt\n")
"""

if __name__ == "__main__":
    main()
