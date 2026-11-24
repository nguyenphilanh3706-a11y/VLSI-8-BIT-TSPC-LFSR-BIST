# So transistor va tai clock (dem tu netlist)

| Cell | So transistor | Cong MOS noi CLK/CLKB (tinh ca inverter tao CLKB) |
|---|---:|---:|
| MS_DFF_SetReset | 26 | 8 |
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
| MS_LFSR_8bit | 234 | 66 |
| TSPC_LFSR_8bit | 144 | 32 |
| TSPC_LFSR_8bit_CMOS | 156 | 32 |
| TSPC_CFSR_8bit | 162 | 32 |
| LT_RTPG_8bit | 362 | 32 |

MS_LFSR_8bit dung MS_DFF_SetReset cua TV1, cac khoi TSPC dung TSPC_DFF_R/S cua TV2. DFF_*_TMP la flip-flop tam cua TV4 (DFF_MS_TMP chi con dung cho dai layout MS).
