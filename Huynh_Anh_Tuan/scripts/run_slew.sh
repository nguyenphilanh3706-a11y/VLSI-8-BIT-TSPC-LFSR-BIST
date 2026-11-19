#!/bin/bash
# run_slew.sh - do nhay cua flip-flop voi do doc suon clock (TSPC de bi race/hold khi suon cham).
# Clock dua thang tu nguon (khong qua dem), quet thoi gian len/xuong trf, T = 2 ns, corner mac dinh NN.
#   bash scripts/run_slew.sh [tb_TSPC_LFSR_slew|tb_MS_LFSR_slew] [corner] ["20 50 100 200 400 600 800"]
# Ket qua: out/slew_<tb>_<corner>.txt (trf lon nhat van PASS = gioi han do doc clock).
cd "$(dirname "$0")/.." || exit 1
TBN=${1:-tb_TSPC_LFSR_slew}; C=${2:-NN}
LIST=${3:-"20 50 100 200 400 600 800"}
mkdir -p out
res=out/slew_${TBN}_${C}.txt
echo "# $TBN corner $C  $(date)" > "$res"
for tr in $LIST; do
  fx=sx_${TBN}_${tr}ps
  sed "s/trf=20p/trf=${tr}p/" "tb/$TBN.scs" > "tb/$fx.scs"
  sed "s/\"$TBN.scs\"/\"$fx.scs\"/" "tb/${TBN}_$C.scs" > "tb/${fx}_$C.scs"
  ( cd tb && timeout ${TMO:-3600} spectre "${fx}_$C.scs" -format psfascii -raw "../out/${fx}_$C" +log "../out/${fx}_$C.log" < /dev/null > /dev/null 2>&1 )
  line=$(awk -v TAG="${fx}_$C" -f scripts/check_tv4.awk "tb/$TBN.exp" "out/${fx}_$C/tran.tran" 2>/dev/null | grep "^RESULT")
  [ -z "$line" ] && line="RESULT ${fx}_$C LOI_SPECTRE (xem out/${fx}_$C.log)"
  echo "trf=${tr}ps  $line" | tee -a "$res"
  [ -z "$KEEP_RAW" ] && gzip -f "out/${fx}_$C/tran.tran" 2>/dev/null
done
echo "Xem $res"
