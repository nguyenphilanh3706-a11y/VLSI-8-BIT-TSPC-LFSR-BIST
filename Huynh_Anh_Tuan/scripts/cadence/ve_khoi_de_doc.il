;; ve_khoi_de_doc.il - ve lai schematic cac khoi LFSR cua thu vien tv4 cho DE DOC (de chup anh bao cao):
;;   8 flip-flop xep mot hang, Q(k-1) -> D(k) noi bang day that, mang hoi tiep o duoi, CLK/RST/VDD/GND bang nhan.
;; Ket noi giong het netlist blocks/LFSR_8bit.scs. Can thu vien tv4 da co symbol cua cac cell con (tv4_build.il).
;; Chay trong CIW:  load("<thu muc>/scripts/cadence/ve_khoi_de_doc.il")   roi  vkAll()
;; Xuat anh: vkExport(cell view file) -> PNG nen trang.

vkLib = "tv4"
vkFont = 0.075

procedure(vkPt(inst termName)
  let((term)
    term = dbFindTermByName(inst~>master termName)
    unless(term error("vkPt: %s khong co chan %s\n" inst~>name termName))
    dbTransformPoint(centerBox(car(term~>pins)~>fig~>bBox) inst~>transform)))

procedure(vkWire(cv pts)
  schCreateWire(cv "draw" "direct" pts 0.0625 0.0625 0.0))

procedure(vkLabel(cv w pt name @optional (orient "R0"))
  schCreateWireLabel(cv car(w) pt name "lowerLeft" orient "stick" vkFont nil))

;; doan day ngan tu chan ra ngoai than instance + nhan ten net (hoac noConn neu net = nil)
procedure(vkStub(cv inst termName netName)
  let((p bb cx cy dx dy q w d)
    d = 0.375
    p = vkPt(inst termName)
    bb = inst~>bBox
    cx = (xCoord(car(bb)) + xCoord(cadr(bb))) / 2.0
    cy = (yCoord(car(bb)) + yCoord(cadr(bb))) / 2.0
    dx = xCoord(p) - cx  dy = yCoord(p) - cy
    q = if(abs(dx) >= abs(dy)
          then if(dx < 0 then list(xCoord(p) - d yCoord(p)) else list(xCoord(p) + d yCoord(p)))
          else if(dy < 0 then list(xCoord(p) yCoord(p) - d) else list(xCoord(p) yCoord(p) + d)))
    w = vkWire(cv list(p q))
    if(netName
      then vkLabel(cv w q netName if(abs(dx) >= abs(dy) "R0" "R90"))
      else schCreateInst(cv dbOpenCellViewByType("basic" "noConn" "symbol" "" "r") nil q "R0"))
    q))

;; dat instance sao cho goc duoi-trai cua bBox nam o (x y)
procedure(vkInst(cv name cell x y)
  let((inst bb)
    inst = schCreateInst(cv dbOpenCellViewByType(vkLib cell "symbol" "" "r") name list(0 0) "R0")
    bb = inst~>bBox
    inst~>xy = list(x - xCoord(car(bb)) y - yCoord(car(bb)))
    inst))

;; pin cua cell o cot ben trai
procedure(vkPin(cv name dir x y)
  let((m w)
    m = dbOpenCellViewByType("basic" cond((dir == "input" "ipin") (dir == "output" "opin") (t "iopin")) "symbol" "" "r")
    schCreatePin(cv m name dir nil list(x y) "R0")
    w = vkWire(cv list(list(x y) list(x + 0.5 y)))
    vkLabel(cv w list(x + 0.5 y) name)
    t))

;; day that tu chan Q cua ff truoc sang chan D cua ff sau (hinh chu Z), dat nhan ten net giua day
procedure(vkChain(cv a b net)
  let((p q mx w)
    p = vkPt(a "Q")  q = vkPt(b "D")
    mx = (xCoord(p) + xCoord(q)) / 2.0
    w = vkWire(cv list(p list(mx yCoord(p)) list(mx yCoord(q)) q))
    vkLabel(cv w list(xCoord(p) + 0.1 yCoord(p)) net)
    w))

;; LFSR / CFSR 8 bit voi flip-flop TSPC cua TV2. fb: "XORTAP8" | "XORTAP8_CMOS" | "CFSR_FB_OPT"
procedure(vkLfsr(cell fb)
  let((cv ff prev inst y0 sx pins)
    cv = dbOpenCellViewByType(vkLib cell "schematic" "schematic" "w")
    pins = '(("CLK" "input") ("RST" "input") ("Q0" "output") ("Q1" "output") ("Q2" "output") ("Q3" "output")
             ("Q4" "output") ("Q5" "output") ("Q6" "output") ("Q7" "output") ("VDD" "inputOutput") ("GND" "inputOutput"))
    y0 = 2.0
    foreach(p pins vkPin(cv car(p) cadr(p) -4.0 y0) y0 = y0 - 0.5)
    sx = 3.0
    prev = nil
    for(k 0 7
      ff = if(k == 0 && fb != "CFSR_FB_OPT" "TSPC_DFF_S" "TSPC_DFF_R")
      inst = vkInst(cv sprintf(nil "IF%d" k) ff sx * k 0.0)
      if(prev then vkChain(cv prev inst sprintf(nil "Q%d" k - 1)) else vkStub(cv inst "D" "D0"))
      vkStub(cv inst "CLK" "CLK")
      vkStub(cv inst if(ff == "TSPC_DFF_S" "SET" "RST") "RST")
      vkStub(cv inst "QB" nil)
      vkStub(cv inst "VDD" "VDD")
      vkStub(cv inst "GND" "GND")
      when(k == 7 vkStub(cv inst "Q" "Q7"))
      prev = inst)
    inst = vkInst(cv "IFB" fb 9.0 -4.0)
    foreach(tm inst~>master~>terminals
      vkStub(cv inst tm~>name if(tm~>name == "FB" "D0" tm~>name)))
    printf("%-22s schCheck=%L instances=%d\n" cell schCheck(cv) length(cv~>instances))
    dbSave(cv) dbClose(cv)
    t))

;; LT-RTPG: 8 cot (moi bit: AND2_T, XOR2_X1, TSPC_DFF_R, MUX2_N), INV_X1 tao LPB
procedure(vkLt()
  let((cv y0 i x a xo f m pins nx)
    cv = dbOpenCellViewByType(vkLib "LT_RTPG_8bit" "schematic" "schematic" "w")
    pins = append(append(mapcar(lambda((k) list(sprintf(nil "Q%d" k) "input")) '(0 1 2 3 4 5 6 7))
                         '(("CLK" "input") ("RST" "input") ("LP" "input")))
                  append(mapcar(lambda((k) list(sprintf(nil "V%d" k) "output")) '(0 1 2 3 4 5 6 7))
                         '(("VDD" "inputOutput") ("GND" "inputOutput"))))
    y0 = 4.0
    foreach(p pins vkPin(cv car(p) cadr(p) -5.0 y0) y0 = y0 - 0.5)
    i = vkInst(cv "ILPB" "INV_X1" -2.0 -8.0)
    vkStub(cv i "A" "LP") vkStub(cv i "Y" "LPB") vkStub(cv i "VDD" "VDD") vkStub(cv i "GND" "GND")
    for(k 0 7
      x = 3.0 * k
      nx = mod(k + 1 8)
      a = vkInst(cv sprintf(nil "IA%d" k) "AND2_T" x 3.0)
      vkStub(cv a "A" sprintf(nil "Q%d" k)) vkStub(cv a "B" sprintf(nil "Q%d" nx))
      vkStub(cv a "Y" sprintf(nil "a%d" k)) vkStub(cv a "VDD" "VDD") vkStub(cv a "GND" "GND")
      xo = vkInst(cv sprintf(nil "IX%d" k) "XOR2_X1" x 0.5)
      vkStub(cv xo "A" sprintf(nil "tq%d" k)) vkStub(cv xo "B" sprintf(nil "a%d" k))
      vkStub(cv xo "Y" sprintf(nil "dt%d" k)) vkStub(cv xo "VDD" "VDD") vkStub(cv xo "GND" "GND")
      f = vkInst(cv sprintf(nil "IT%d" k) "TSPC_DFF_R" x -2.5)
      vkStub(cv f "D" sprintf(nil "dt%d" k)) vkStub(cv f "CLK" "CLK") vkStub(cv f "RST" "RST")
      vkStub(cv f "Q" sprintf(nil "tq%d" k)) vkStub(cv f "QB" nil) vkStub(cv f "VDD" "VDD") vkStub(cv f "GND" "GND")
      m = vkInst(cv sprintf(nil "IM%d" k) "MUX2_N" x -5.5)
      vkStub(cv m "A" sprintf(nil "Q%d" k)) vkStub(cv m "B" sprintf(nil "tq%d" k))
      vkStub(cv m "S" "LP") vkStub(cv m "SB" "LPB")
      vkStub(cv m "Y" sprintf(nil "V%d" k)) vkStub(cv m "VDD" "VDD") vkStub(cv m "GND" "GND"))
    printf("%-22s schCheck=%L instances=%d\n" "LT_RTPG_8bit" schCheck(cv) length(cv~>instances))
    dbSave(cv) dbClose(cv)
    t))

;; ---------------- testbench schematic (giong tb/*.scs: nguon rieng DUT/clock/tai, 2 INV_CLK dem clock) ----------------
procedure(vkSet(inst name value)
  let((cdf p)
    cdf = cdfGetInstCDF(inst)
    p = cdf && cdfFindParamByName(cdf name)
    if(p then p~>value = value t else printf("!! %s khong co tham so %s\n" inst~>name name) nil)))

procedure(vkSrc(cv name cell x y plus params)
  let((i)
    i = schCreateInst(cv dbOpenCellViewByType("analogLib" cell "symbol" "" "r") name list(x y) "R0")
    foreach(pv params vkSet(i car(pv) cadr(pv)))
    vkStub(cv i "PLUS" plus)
    vkStub(cv i "MINUS" "gnd!")
    i))

;; dut: "TSPC_LFSR_8bit" | "TSPC_CFSR_8bit" | "LT" (TSPC_LFSR_8bit + LT_RTPG_8bit, LP = bien thiet ke lp)
procedure(vkTb(tbcell dut)
  let((cv i x g)
    cv = dbOpenCellViewByType(vkLib tbcell "schematic" "schematic" "w")
    vkSrc(cv "VVDD" "vdc" 0.0 0.0 "VDD" '(("vdc" "1.2")))
    vkSrc(cv "VVDDCK" "vdc" 1.5 0.0 "VDDCK" '(("vdc" "1.2")))
    vkSrc(cv "VVDDL" "vdc" 3.0 0.0 "VDDL" '(("vdc" "1.2")))
    vkSrc(cv "VGND" "vdc" 4.5 0.0 "GND" '(("vdc" "0")))
    vkSrc(cv "VCK" "vpulse" 6.0 0.0 "ck0" '(("v1" "0") ("v2" "1.2") ("td" "tclk") ("tr" "trf") ("tf" "trf") ("pw" "tclk/2-trf") ("per" "tclk")))
    vkSrc(cv "VRST" "vpulse" 7.5 0.0 "RST" '(("v1" "1.2") ("v2" "0") ("td" "tclk/2") ("tr" "20p") ("tf" "20p") ("pw" "1") ("per" "2")))
    when(dut == "LT" vkSrc(cv "VLP" "vdc" 9.0 0.0 "LP" '(("vdc" "lp"))))
    schCreateInst(cv dbOpenCellViewByType("analogLib" "gnd" "symbol" "" "r") "G0" list(-1.0 -0.5) "R0")
    g = vkInst(cv "XCK1" "INV_CLK" 0.0 -3.5)
    vkStub(cv g "A" "ck0") vkStub(cv g "VDD" "VDDCK") vkStub(cv g "GND" "GND")
    i = vkInst(cv "XCK2" "INV_CLK" 2.5 -3.5)
    vkStub(cv i "Y" "CLK") vkStub(cv i "VDD" "VDDCK") vkStub(cv i "GND" "GND")
    let((p q w) p = vkPt(g "Y") q = vkPt(i "A")
      w = vkWire(cv list(p q)) vkLabel(cv w list(xCoord(p) + 0.15 yCoord(p)) "ckb"))
    i = vkInst(cv "XDUT" if(dut == "LT" "TSPC_LFSR_8bit" dut) 5.5 -4.0)
    foreach(tm i~>master~>terminals vkStub(cv i tm~>name tm~>name))
    if(dut == "LT"
      then
        i = vkInst(cv "XLT" "LT_RTPG_8bit" 9.0 -4.5)
        foreach(tm i~>master~>terminals vkStub(cv i tm~>name tm~>name))
        for(k 0 7 for(j 0 3
          i = vkInst(cv sprintf(nil "XL_V%d_%d" k j) "INV_X1" 14.0 + 2.6*j -2.0 - 1.4*k)
          vkStub(cv i "A" sprintf(nil "V%d" k)) vkStub(cv i "Y" nil)
          vkStub(cv i "VDD" "VDDL") vkStub(cv i "GND" "GND")))
      else
        for(k 0 7
          i = vkInst(cv sprintf(nil "XL_Q%d_0" k) "INV_X1" 10.0 + 2.6*mod(k 4) -3.0 - 2.0*(k / 4))
          vkStub(cv i "A" sprintf(nil "Q%d" k)) vkStub(cv i "Y" nil)
          vkStub(cv i "VDD" "VDDL") vkStub(cv i "GND" "GND")))
    printf("%-22s schCheck=%L instances=%d\n" tbcell schCheck(cv) length(cv~>instances))
    dbSave(cv) dbClose(cv)
    t))

;; xuat anh PNG nen trang, vua khung thiet ke
procedure(vkExport(cell view file @optional (wd 2400) (ht 1350))
  let((w r)
    w = geOpen(?lib vkLib ?cell cell ?view view ?mode "r")
    errset(hiResizeWindow(w list(0:0 1440:900)))
    errset(hiZoomAbsoluteScale(w 1.0))
    errset(hiZoomIn(w list(car(w~>cellView~>bBox) cadr(w~>cellView~>bBox))))
    r = errset(hiExportImage(?fileName file ?window w ?width wd ?height ht ?bgType 'white ?exportRegion 'fullDesign))
    printf("export %s/%s -> %s : %L %L\n" cell view file r errset.errset)
    hiCloseWindow(w)
    r))

;; chay an toan: neu ve loi thi bo cellview dang mo (khong luu) de khong hien hop thoai Save Changes
procedure(vkSafe(fn @rest args)
  let((r)
    r = errset(apply(fn args) t)
    unless(r
      printf("!! %L loi: %L\n" fn errset.errset)
      foreach(cv dbGetOpenCellViews() when(cv~>libName == vkLib && cv~>mode != "r" dbPurge(cv))))
    r))

procedure(vkAll()
  vkSafe('vkLfsr "TSPC_LFSR_8bit" "XORTAP8")
  vkSafe('vkLfsr "TSPC_LFSR_8bit_CMOS" "XORTAP8_CMOS")
  vkSafe('vkLfsr "TSPC_CFSR_8bit" "CFSR_FB_OPT")
  vkSafe('vkLt)
  t)

;; ---------------- mo phong testbench schematic bang OCEAN (giong ADE L) ----------------
;; vkSim("tb_TSPC_LFSR_8bit" "NN" '("CLK" "RST" "Q0" ...) '(("lp" 1)))  -> ket qua psf o /home/buet/simulation/tv4_sch/<tb>_<corner>
;; ghi file mau: gia tri cac tin hieu tai (k+1)T - 0.1 ns, k = 0..300  -> <out>/<tb>_<corner>_mau.txt
procedure(vkSim(tb corner sigs vars outdir)
  let((rd f tclk)
    rd = sprintf(nil "/home/buet/simulation/tv4_sch/%s_%s" tb corner)
    simulator('spectre)
    design(vkLib tb "schematic")
    resultsDir(rd)
    modelFile(list("/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs" corner))
    desVar("tclk" 2n) desVar("trf" 20p)
    foreach(v vars desVar(car(v) cadr(v)))
    analysis('tran ?stop "602.4n" ?maxstep "20p" ?errpreset "moderate")
    temp(27)
    apply('save cons('v mapcar(lambda((x) strcat("/" x)) sigs)))
    run()
    openResults(strcat(rd "/psf")) selectResult('tran)
    f = outfile(sprintf(nil "%s/%s_%s_mau.txt" outdir tb corner) "w")
    fprintf(f "k %s\n" buildString(sigs " "))
    tclk = 2e-9
    for(k 0 300
      fprintf(f "%d" k)
      foreach(x sigs fprintf(f " %.3f" value(VT(strcat("/" x)) (k + 1) * tclk - 1e-10)))
      fprintf(f "\n"))
    close(f)
    printf("vkSim %s %s xong -> %s\n" tb corner rd)
    rd))
