# So transistor va tai clock (dem tu netlist, flip-flop TAM THOI cua TV4)

| Cell | So transistor | Cong MOS noi CLK/CLKB (tinh ca inverter tao CLKB) |
|---|---:|---:|
| DFF_MS_TMP | 24 | 8 |
| DFF_TSPC_TMP | 17 | 4 |
| TSPC_DFF_R | 15 | 4 |
| TSPC_DFF_S | 15 | 4 |
| XORTAP8 | 24 | 0 |
| XORTAP8_CMOS | 36 | 0 |
| ZERO7 | 20 | 0 |
| CFSR_FB | 56 | 0 |
| CFSR_FB_OPT | 42 | 0 |
| AND2_T | 6 | 0 |
| MUX2_N | 12 | 0 |
| MS_LFSR_8bit | 218 | 66 |
| TSPC_LFSR_8bit | 144 | 32 |
| TSPC_LFSR_8bit_CMOS | 156 | 32 |
| TSPC_CFSR_8bit | 162 | 32 |
| LT_RTPG_8bit | 362 | 32 |

Luu y: DFF_*_TMP la cell tam; khi thay bang cell TV1/TV2 thi chay lai `python3 scripts/count_tx.py`.
