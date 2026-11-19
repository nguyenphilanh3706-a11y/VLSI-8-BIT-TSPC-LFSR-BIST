# Kết quả mô phỏng dạng chữ

Spectre, gpdk090, flip-flop tạm của TV4, cell TV3 commit `86e42ee`, chạy ngày 19/11/2026. Bảng tổng hợp và giải thích: [docs/4_ket_qua.md](../docs/4_ket_qua.md).

| File | Sinh bởi | Nội dung |
|---|---|---|
| `spectre_500MHz.txt` | `scripts/run_tv4.sh` | 18 dòng `RESULT` (6 mạch × NN/SS/FF): PASS/FAIL, số vector đúng, trễ, công suất 3 nguồn |
| `spectre_chi_tiet.txt` | `scripts/run_tv4.sh` | log đầy đủ: vector có trễ lớn nhất, công suất và năng lượng mỗi chu kỳ từng nguồn |
| `fmax/<tb>_<corner>.txt` | `scripts/run_fmax.sh` | quét chu kỳ clock cho MS_LFSR và TSPC_LFSR ở NN/SS/FF |
| `slew/<tb>_NN.txt` | `scripts/run_slew.sh` | quét độ dốc sườn clock |
| `so_transistor.md` | `scripts/count_tx.py` | số transistor và MOS nối clock của mỗi cell/khối |

Cột trong dòng `RESULT`: `T` chu kỳ (s), `tre_ps` trễ CLK→Q lớn nhất, `P_dut_uW` / `P_clk_uW` / `P_tai_uW` công suất trung bình của nguồn VVDD / VVDDCK / VVDDL, `E_*_pJ` năng lượng mỗi chu kỳ.
