#!/bin/bash
# run_fmax.sh - tim f_max: quet chu ky clock, moi diem chay du 301 vector (300 canh clock, qua tron chu ky 255) va kiem tra.
#   bash scripts/run_fmax.sh [ten_tb] [corner] ["danh sach chu ky, ps"]
#   bash scripts/run_fmax.sh tb_TSPC_LFSR NN "2000 1500 1200 1000 800 700 600 500 450 400 350 300"
# f_max = tan so cao nhat ma moi vector PASS (lay mau truoc canh ke tiep 5% chu ky, muc logic cach ray <= 10%),
# va moi chu ky lon hon cung PASS.
# Ket qua: out/fmax_<tb>_<corner>.txt. File tam fx_* trong tb/ va out/ co the xoa sau khi xem.
cd "$(dirname "$0")/.." || exit 1
TBN=${1:-tb_TSPC_LFSR}; C=${2:-NN}
PS_LIST=${3:-"2000 1500 1200 1000 800 700 600 500 450 400 350 300 250"}
mkdir -p out
res=out/fmax_${TBN}_${C}.txt
echo "# $TBN corner $C  $(date)" > "$res"
for ps in $PS_LIST; do
  fx=fx_${TBN}_${ps}ps
  sed "s/^parameters tclk=[^ ]*/parameters tclk=${ps}p/" "tb/$TBN.scs" > "tb/$fx.scs"
  sed "s/\"$TBN.scs\"/\"$fx.scs\"/" "tb/${TBN}_$C.scs" > "tb/${fx}_$C.scs"
  awk -v T="${ps}e-12" '$1=="T"{print "T", T; next} $1=="MARGIN"{printf "MARGIN %g\n", 0.05*T; next} {print}' "tb/$TBN.exp" > "tb/$fx.exp"
  ( cd tb && timeout ${TMO:-3600} spectre "${fx}_$C.scs" -format psfascii -raw "../out/${fx}_$C" +log "../out/${fx}_$C.log" < /dev/null > /dev/null 2>&1 )
  line=$(awk -v TAG="${fx}_$C" -f scripts/check_tv4.awk "tb/$fx.exp" "out/${fx}_$C/tran.tran" 2>/dev/null | grep "^RESULT")
  [ -z "$line" ] && line="RESULT ${fx}_$C LOI_SPECTRE (xem out/${fx}_$C.log)"
  echo "T=${ps}ps f=$(awk -v p=$ps 'BEGIN{printf "%.0f", 1e6/p}')MHz  $line" | tee -a "$res"
  [ -z "$KEEP_RAW" ] && gzip -f "out/${fx}_$C/tran.tran" 2>/dev/null
done
echo "Xem $res"
