#!/bin/bash
# Chạy Assura 4.1 (gpdk090) trực tiếp trên file GDS, không cần mở Virtuoso.
#
#   bash scripts/layout/assura.sh drc <cell>          DRC
#   bash scripts/layout/assura.sh lvs <cell>          LVS so với layout/cdl/<cell>.cdl
#   bash scripts/layout/assura.sh rcx <cell>          LVS + trích RC (netlist HSPICE)
#
# Đầu vào : layout/gds/<cell>.gds (cell TV3 lấy ở depend/tv3/layout/gds), layout/cdl/<cell>.cdl
# Đầu ra  : out/assura/<mode>_<cell>/  (<cell>.err/.sum với DRC, <cell>.csm với LVS,
#           <cell>_rcx.sp với RCX). Đổi biến PDK nếu gpdk090 cài ở chỗ khác.
set -u
MODE=${1:?drc|lvs|rcx}; CELL=${2:?ten cell}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PDK=${PDK:-/home/buet/cadence/gpdk090_v4.6}
P=$PDK/assura
GDS=$ROOT/layout/gds/$CELL.gds
[ -f "$GDS" ] || GDS=$ROOT/depend/tv3/layout/gds/$CELL.gds
CDL=$ROOT/layout/cdl/$CELL.cdl
R=$ROOT/out/assura/${MODE}_$CELL
mkdir -p "$R" && cd "$R" || exit 1
cp -f "$GDS" ./in.gds
echo "DEFINE gpdk090 $P" > tech.lib

if [ "$MODE" = drc ]; then
cat > run.rsf <<RSF
avParameters(
  ?inputLayout ( "GDS2" "./in.gds" )
  ?cellName "$CELL"
  ?rulesFile "$P/drc.rul"
  ?runName "$CELL"
  ?workingDirectory "."
  ?flagNon45 t
  ?flagOffGrid .005
  ?userUnits "micron"
  ?overwrite t
  ?avrpt t
)
RSF
assura run.rsf > assura.out 2>&1
grep -i 'total' "$CELL.sum" 2>/dev/null | tail -3
grep -q 'Total  *errors: *0 ' "$CELL.err" 2>/dev/null || cat "$CELL.err" 2>/dev/null | head -40
exit 0
fi

[ -f "$CDL" ] || { echo "thieu $CDL"; exit 1; }
cp -f "$CDL" ./sch.cdl
cat > run.rsf <<RSF
avParameters(
  ?inputLayout ( "GDS2" "./in.gds" )
  ?cellName "$CELL"
  ?rulesFile "$P/extract.rul"
  ?runName "$CELL"
  ?workingDirectory "."
  ?avrpt t
  ?technology "gpdk090"
  ?techLib "./tech.lib"
  ?overwrite t
)
load( "$P/compare.rul" )
avCompareRules(
  schematic( netlist( cdl "./sch.cdl" ) )
  bind( net("*[*]" "*<*>") )
  mergeSplitGate( sameOrder )
  autoPinSwap(t 3000)
  expandOnError((pins t) (swap t) (reduce t) (swapThres t))
)
avLVS()
RSF
assura run.rsf > assura.out 2>&1
cat "$CELL.csm" 2>/dev/null | grep -E 'matched|Match|mismatch|errors' | head -20

if [ "$MODE" = rcx ]; then
cat > rcx.rsf <<RSF
avParameters(
  ?inputLayout ( "GDS2" "./in.gds" )
  ?cellName "$CELL"
  ?rulesFile "$P/extract.rul"
  ?runName "$CELL"
  ?workingDirectory "."
  ?technology "gpdk090"
  ?techLib "./tech.lib"
)
rcxParameters(
  ?runName "$CELL"
  ?outputFormat "spectre"
  ?output "${CELL}_rcx.sp"
  ?extract "both"
  ?type "full"
  ?capExtractMode "decoupled"
  ?capGround "GND"
  ?rcxSetupDir "$P/rcx"
)
avRCX()
RSF
assura rcx.rsf > rcx.out 2>&1
ls -l "${CELL}_rcx.sp"
echo "Chuyen sang Spectre: python3 scripts/layout/rcx2scs.py $R/${CELL}_rcx.sp layout/rcx/${CELL}_post.scs $CELL \"CLK RST Q0 Q1 Q2 Q3 Q4 Q5 Q6 Q7 VDD GND\""
fi
