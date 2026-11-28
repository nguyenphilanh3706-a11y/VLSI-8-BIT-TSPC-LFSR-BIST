#!/bin/bash
# run_tv4.sh - chay Spectre cho testbench TV4 (trong may ao Cadence) roi kiem tra bang check_tv4.awk.
#   bash scripts/run_tv4.sh                          # tat ca tb/*_NN.scs, *_SS.scs, *_FF.scs (tru *_slew)
#   bash scripts/run_tv4.sh tb/tb_TSPC_LFSR_NN.scs   # mot testbench
# Ket qua: out/<ten>/tran.tran (psfascii), out/<ten>.log, out/<ten>.check,
#          dong RESULT them vao out/spectre_results.txt
# Ma thoat 0 khi moi testbench PASS.
cd "$(dirname "$0")/.." || exit 1
mkdir -p out
LIST=("$@")
[ ${#LIST[@]} -eq 0 ] && LIST=($(ls tb/tb_*_NN.scs tb/tb_*_SS.scs tb/tb_*_FF.scs 2>/dev/null | grep -v _slew))
rc=0
for tb in "${LIST[@]}"; do
  n=$(basename "$tb" .scs)
  base=${n%_NN}; base=${base%_SS}; base=${base%_FF}
  echo "== $n"
  [ -f "$tb" ] || { echo "khong co file $tb"; rc=1; continue; }
  ( cd tb && timeout ${TMO:-7200} spectre "$n.scs" -format psfascii -raw "../out/$n" +log "../out/$n.log" < /dev/null > /dev/null 2>&1 )
  r=$?
  grep "completes with" "out/$n.log" | sed 's/^ *//'
  if [ $r -ne 0 ]; then
    echo "Spectre loi (ma $r), xem out/$n.log"; grep -i -A3 "^ *error" "out/$n.log" | head -12; rc=1; continue
  fi
  awk -v TAG="$n" -f scripts/check_tv4.awk "tb/$base.exp" "out/$n/tran.tran" > "out/$n.check" || rc=1
  cat "out/$n.check"
  grep "^RESULT" "out/$n.check" | sed "s/^/$(date +%F_%T) /" >> out/spectre_results.txt
  [ -z "$KEEP_RAW" ] && gzip -f "out/$n/tran.tran"      # nen dang song (dia may ao nho); xem lai: gunzip
done
exit $rc
