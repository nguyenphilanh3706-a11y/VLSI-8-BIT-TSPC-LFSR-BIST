#!/bin/bash
# run_pvt.sh - quet PVT (corner x VDD x nhiet do) o tan so testbench (mac dinh T = 2 ns, 500 MHz), moi diem chay du 301 vector.
#   bash scripts/run_pvt.sh [ten_tb] ["corner"] ["VDD (V)"] ["nhiet do (C)"]
#   bash scripts/run_pvt.sh tb_TSPC_LFSR_post "NN SS FF" "0.8 1.0 1.2" "0 27 125"
# Moi nguon 1,2 V trong testbench (VDD, clock, tai, xung CLK/RST) doi thanh VDD dang quet; nguong kiem tra VDD/2,
# muc logic phai cach ray <= 10 % VDD (check_tv4.awk -v VDDV=...). Luoi giong PVT cua TV2 (Tuan4/data/pvt_*.txt).
# Ket qua: out/pvt_<tb>.txt. File tam pv_* trong tb/ va out/ co the xoa sau khi xem.
cd "$(dirname "$0")/.." || exit 1
TBN=${1:-tb_TSPC_LFSR}; CS=${2:-"NN SS FF"}; VS=${3:-"0.8 1.0 1.2"}; TS=${4:-"0 27 125"}
mkdir -p out
res=out/pvt_${TBN}.txt
echo "# $TBN  PVT  $(date)" > "$res"
for C in $CS; do for V in $VS; do for T in $TS; do
  fx=pv_${TBN}_${V/./p}V_${T}C
  sed -e "s/vsource dc=1\.2/vsource dc=$V/g" -e "s/val0=1\.2/val0=$V/g" -e "s/val1=1\.2/val1=$V/g" \
      -e "s/temp=27/temp=$T/" "tb/$TBN.scs" > "tb/$fx.scs"
  sed "s/\"$TBN.scs\"/\"$fx.scs\"/" "tb/${TBN}_$C.scs" > "tb/${fx}_$C.scs"
  ( cd tb && timeout ${TMO:-3600} spectre "${fx}_$C.scs" -format psfascii -raw "../out/${fx}_$C" +log "../out/${fx}_$C.log" < /dev/null > /dev/null 2>&1 )
  line=$(awk -v TAG="${fx}_$C" -v VDDV=$V -f scripts/check_tv4.awk "tb/$TBN.exp" "out/${fx}_$C/tran.tran" 2>/dev/null | grep "^RESULT")
  [ -z "$line" ] && line="RESULT ${fx}_$C LOI_SPECTRE (xem out/${fx}_$C.log)"
  echo "$C ${V}V ${T}C  $line" | tee -a "$res"
  [ -z "$KEEP_RAW" ] && gzip -f "out/${fx}_$C/tran.tran" 2>/dev/null
done; done; done
echo "Xem $res"
