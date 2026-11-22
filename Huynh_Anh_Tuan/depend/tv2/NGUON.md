# Nguồn các file của TV2 trong thư mục này

Bản sao **chỉ đọc** từ repo nhóm `nguyenphilanh3706-a11y/VLSI-8-BIT-TSPC-LFSR-BIST`, branch `cell/TSPC_DFF(2)`, commit `25fc686` (22/11/2026, "Week 1 - Summary"), thư mục `Nguyen_Phuoc_An/cells/`. Giữ nguyên nội dung; `cells/cells.scs` là file include do TV4 thêm.

| File | Cell | Chân | TV4 dùng để |
|---|---|---|---|
| `cells/TSPC_DFF_R/TSPC_DFF_R.scs` | TSPC DFF kích cạnh lên, Reset bất đồng bộ (RST = 1 → Q = 0), 15T có 2 keeper | `D CLK RST Q QB VDD GND` | FF1..FF7 của các LFSR TSPC, 8 FF của TSPC_CFSR_8bit, 8 T-FF của LT_RTPG_8bit |
| `cells/TSPC_DFF_S/TSPC_DFF_S.scs` | TSPC DFF kích cạnh lên, Set bất đồng bộ (SET = 1 → Q = 1), 15T có 2 keeper | `D CLK SET Q QB VDD GND` | FF0 của các LFSR TSPC (nạp seed 0x01) |

Quy tắc của TV2 được giữ: chỉ nhả `SET` khi `CLK = 0` (testbench của TV4 nhả RST/SET ở 0,5T, trước cạnh clock đầu tiên ở T); `QB` là nút động bên trong, để hở, không nối tải.

TV2 chưa có layout: layout dải LFSR (`layout/`) vẫn dùng flip-flop tạm DFF_TSPC_TMP của TV4.

Không sửa các file này. Khi TV2 cập nhật: chép lại đè rồi chạy lại mô phỏng.
