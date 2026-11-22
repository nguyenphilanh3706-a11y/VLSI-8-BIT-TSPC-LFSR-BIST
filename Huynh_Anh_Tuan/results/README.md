# Kết quả mô phỏng dạng chữ

Spectre, gpdk090, cell TV3 commit `435f6f0`. Bản TSPC trước layout dùng flip-flop của TV2 (commit `25fc686`, chạy 22/11/2026); bản MS dùng flip-flop tạm của TV4 (chạy 19/11/2026); mô phỏng hậu layout: TSPC dùng layout flip-flop TV2 (22/11/2026), MS dùng flip-flop tạm (21/11/2026). Bảng tổng hợp và giải thích: [docs/4_ket_qua.md](../docs/4_ket_qua.md).

| File | Sinh bởi | Nội dung |
|---|---|---|
| `spectre_500MHz.txt` | `scripts/run_tv4.sh` | 18 dòng `RESULT` (6 mạch × NN/SS/FF): PASS/FAIL, số vector đúng, trễ, công suất 3 nguồn |
| `spectre_chi_tiet.txt` | `scripts/run_tv4.sh` | log đầy đủ: vector có trễ lớn nhất, công suất và năng lượng mỗi chu kỳ từng nguồn |
| `fmax/<tb>_<corner>.txt` | `scripts/run_fmax.sh` | quét chu kỳ clock cho MS_LFSR và TSPC_LFSR ở NN/SS/FF; `*_post_*` là bản hậu layout (`tb_TSPC_LFSR_post_ff_tam_NN` là bản 21/11 với flip-flop tạm) |
| `hau_layout.txt` | `scripts/run_tv4.sh` | dòng `RESULT` của 6 testbench hậu layout (TSPC với layout flip-flop TV2), thử đặt khối XOR đầu hàng, bản 21/11 với flip-flop tạm kèm lỗi race và hai cách sửa |
| `slew/<tb>_NN.txt` | `scripts/run_slew.sh` | quét độ dốc sườn clock |
| `cfsr_cmp/` | `scripts/run_cfsr_cmp.sh` | So sánh CFSR_FB_CMOS / CFSR_FB / CFSR_FB_OPT (netlist schematic và RCX của TV3, branch `195bacb`) trong thanh ghi TSPC: `spectre_500MHz*.txt` (18 testbench), `fmax_cmp_CFSR_<khối>_<NN\|SS>.txt` (22/11/2026) |
| `so_transistor.md` | `scripts/count_tx.py` | số transistor và MOS nối clock của mỗi cell/khối |

Cột trong dòng `RESULT`: `T` chu kỳ (s), `tre_ps` trễ CLK→Q lớn nhất, `P_dut_uW` / `P_clk_uW` / `P_tai_uW` công suất trung bình của nguồn VVDD / VVDDCK / VVDDL, `E_*_pJ` năng lượng mỗi chu kỳ.
