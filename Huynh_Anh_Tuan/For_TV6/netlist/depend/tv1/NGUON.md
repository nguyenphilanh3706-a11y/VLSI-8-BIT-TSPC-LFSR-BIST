# Nguồn các file của TV1 trong thư mục này

Bản sao từ repo nhóm `nguyenphilanh3706-a11y/VLSI-8-BIT-TSPC-LFSR-BIST`, branch `cell/MS_DFF(1)`, commit `fa999e9` (23/11/2026, Lê Thành Tài), thư viện Virtuoso `VLSI_TV1`.

| File | Cell | Chân | TV4 dùng để |
|---|---|---|---|
| `cells/MS_DFF_SetReset/MS_DFF_SetReset.scs` | D flip-flop master-slave cổng truyền, kích cạnh lên, SET/RESET bất đồng bộ tích cực cao; 26T = 4 NOR2 (16T) + 4 TG (8T) + 1 inverter ra Q_bar (2T) | `D CLK CLKB SET RESET Q Q_bar VDD GND` | 8 flip-flop của `MS_LFSR_8bit` (qua lớp `cells/DFF_MS`) |
| `cells/cells.scs` | file include do TV4 thêm | | |

Cách lấy netlist: schematic `VLSI_TV1/MS_DFF_SetReset` trong máy ảo Cadence, xuất bằng OCEAN `createNetlist` (24/11/2026). Schematic của TV1 gọi cell con từ thư viện tên `24119080`, nên TV4 khai thêm thư viện này (cùng nội dung `VLSI_TV1`) trong `cds.lib` để netlist. Chỉ đổi tên cell con (`NOR`, `TG`, `INV_QB` → `TV1_NOR`, `TV1_TG`, `TV1_INV_QB`) để không trùng tên với cell khác và bỏ `m=(1)*(1)`; kích thước, nối dây và `as/ad/ps/pd` giữ nguyên.

Kích thước: NOR2 pMOS 960n/100n, nMOS 240n/100n; TG pMOS và nMOS 120n/100n; inverter Q_bar 480n/240n. CLKB lấy từ inverter ngoài cell (khối `MS_LFSR_8bit` dùng một `INV_CLK` chung cho 8 flip-flop).

Ghi nhận khi đọc schematic TV1 (để TV1 xem lại, TV4 không sửa):
- Trong cell `NOR`, pMOS `PM1` có thân (bulk) nối vào nút giữa `net17` chứ không nối VDD. Spectre vẫn chạy được, nhưng khi vẽ layout hai pMOS chung một nwell thì thân phải nối VDD, nên mạch sau layout sẽ khác schematic.
- `MS_DFF_SetReset/layout` (commit `fa999e9`) chưa có hình vẽ: không có shape nào, chỉ có 3 instance đặt chính cell `MS_DFF_SetReset`. Vì vậy dải layout `MS_LFSR_8bit` của TV4 vẫn dùng flip-flop tạm `DFF_MS_TMP`, và phần so sánh sau layout MS/TSPC còn chờ layout của TV1.
