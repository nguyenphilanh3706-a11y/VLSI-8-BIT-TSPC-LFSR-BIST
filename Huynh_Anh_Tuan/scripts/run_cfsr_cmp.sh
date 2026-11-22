#!/bin/bash
# run_cfsr_cmp.sh - so sanh 3 khoi hoi tiep CFSR (schematic va sau layout) trong thanh ghi TSPC (may ao Cadence).
#   python3 scripts/gen_tb_cfsr_cmp.py && bash scripts/run_cfsr_cmp.sh
# 1) 500 MHz, NN/SS/FF: out/spectre_results.txt; 2) quet f_max NN va SS: out/fmax_cmp_CFSR_<V>_<corner>.txt
# 6 bien the chay song song (may ao 6 nhan).
cd "$(dirname "$0")/.." || exit 1
bash scripts/run_tv4.sh $(ls tb/cmp_CFSR_*_NN.scs tb/cmp_CFSR_*_SS.scs tb/cmp_CFSR_*_FF.scs)
NN="400 390 380 370 360 350 330 320 310 300 290 280 270 260"
SS="550 500 470 450 430 410 400 390 380 360"
for v in CMOS FB OPT CMOS_rcx FB_rcx OPT_rcx; do
  # NN roi SS cua cung bien the chay noi tiep (hai corner dung chung file tam fx_<tb>_<ps>.scs)
  ( bash scripts/run_fmax.sh cmp_CFSR_$v NN "$NN"; bash scripts/run_fmax.sh cmp_CFSR_$v SS "$SS" ) > /dev/null 2>&1 &
  while [ $(jobs -r | wc -l) -ge 6 ]; do sleep 5; done
done
wait
grep -h "^T=" out/fmax_cmp_CFSR_* | awk '{print $4, $5, $6}'
