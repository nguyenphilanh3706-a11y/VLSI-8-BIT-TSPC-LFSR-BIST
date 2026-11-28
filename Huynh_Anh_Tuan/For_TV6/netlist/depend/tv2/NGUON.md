# Nguồn các file của TV2 trong thư mục này

Bản sao **chỉ đọc** từ repo nhóm `nguyenphilanh3706-a11y/VLSI-8-BIT-TSPC-LFSR-BIST`, branch `cell/TSPC_DFF(2)`, commit `25fc686` (22/11/2026, "Week 1 - Summary"), thư mục `Nguyen_Phuoc_An/cells/`. Giữ nguyên nội dung; `cells/cells.scs` là file include do TV4 thêm.

| File | Cell | Chân | TV4 dùng để |
|---|---|---|---|
| `cells/TSPC_DFF_R/TSPC_DFF_R.scs` | TSPC DFF kích cạnh lên, Reset bất đồng bộ (RST = 1 → Q = 0), 15T có 2 keeper | `D CLK RST Q QB VDD GND` | FF1..FF7 của các LFSR TSPC, 8 FF của TSPC_CFSR_8bit, 8 T-FF của LT_RTPG_8bit |
| `cells/TSPC_DFF_S/TSPC_DFF_S.scs` | TSPC DFF kích cạnh lên, Set bất đồng bộ (SET = 1 → Q = 1), 15T có 2 keeper | `D CLK SET Q QB VDD GND` | FF0 của các LFSR TSPC (nạp seed 0x01) |

Quy tắc của TV2 được giữ: chỉ nhả `SET` khi `CLK = 0` (testbench của TV4 nhả RST/SET ở 0,5T, trước cạnh clock đầu tiên ở T); `QB` là nút động bên trong, để hở, không nối tải.

Layout (thêm 22/11/2026), từ commit `ac228bf` ("Week 3 - summary"), thư mục `Nguyen_Phuoc_An/Tuan3/layout/`:

| File | Nội dung | TV4 dùng để |
|---|---|---|
| `layout/gds/TV2_TSPC.gds` | GDS hai cell `TSPC_DFF_S` (8,00 × 2,76 µm) và `TSPC_DFF_R` (8,68 × 2,76 µm), cao 2,76 µm như khuôn TV3 | Đặt vào dải `TSPC_LFSR_8bit` (`scripts/layout/build_layout.py`) |
| `layout/cdl/TSPC_DFF_S.cdl`, `TSPC_DFF_R.cdl` | Netlist LVS của TV2 | Ghép vào `layout/cdl/TSPC_LFSR_8bit.cdl` |
| `layout/rcx/TSPC_DFF_S_rcx.scs`, `TSPC_DFF_R_rcx.scs` | Netlist trích RC của từng cell (TV2) | Đối chiếu; testbench hậu layout của TV4 dùng RCX của cả dải |

Netlist cell trong `cells/` ở `ac228bf` giống hệt `25fc686`. Cell TV2 chỉ có pad Metal1 ở chân D, SET, RST; TV4 nối các chân này ở mức dải (không sửa cell), xem [docs/5_layout.md](../../../../docs/5_layout.md).

Không sửa các file này. Khi TV2 cập nhật: chép lại đè rồi chạy lại mô phỏng.

`cells_asad/` (thêm 24/11/2026): bản sao của `cells/` có thêm `as/ad/ps/pd` cho mọi MOS (as = ad = W × 0,28 µm, ps = pd = 2(W + 0,28 µm)), sinh bằng [`scripts/add_asad.py`](../../../../scripts/add_asad.py). Netlist gốc của TV2 không có các tham số này nên mô hình dùng diện tích tiếp giáp mặc định (lớn hơn), chậm và tốn công suất hơn; netlist của TV1 thì có. Testbench `tb_TSPC_LFSR_asad*` dùng bản này để so sánh trước layout với MS của TV1 trong cùng điều kiện, đúng cách TV2 làm trong `Tuan4/SO_SANH_TV1.md`. `cells/` giữ nguyên.
