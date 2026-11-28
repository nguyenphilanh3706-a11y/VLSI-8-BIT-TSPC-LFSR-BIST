# Nguồn các file của TV3 trong thư mục này

Bản sao **chỉ đọc** từ repo nhóm `nguyenphilanh3706-a11y/VLSI-8-BIT-TSPC-LFSR-BIST`, branch `cell/XOR-CFSR-LOGIC(3)`, commit `435f6f0` (21/11/2026, "Thêm bản tối ưu CFSR_FB_OPT, cell AOI21_X1, XNOR2_X1 và XOR2_X1 nén"; đang chờ gộp vào `main` qua PR #2), thư mục `Vo_Minh_Tam/`. Giữ nguyên đường dẫn như trong repo của TV3.

| File | Nội dung | TV4 dùng để |
|---|---|---|
| `cells/INV_X1, NAND2_X1, NOR2_X1, NOR3_X1, XOR2_X1, XOR2_TG6` (+ `XOR2_TG`, TV4 không dùng) | Cổng cơ bản, nguồn `VDD GND` | Ghép LFSR, AND2, MUX, flip-flop tạm |
| `cells/AOI21_X1, XNOR2_X1` | Cổng thêm cho bản tối ưu (`cells.scs` của TV3 đã include) | Bên trong CFSR_FB_OPT |
| `blocks/XORTAP8.scs` | `XORTAP8` (2 × XOR2_TG6 + 1 × XOR2_X1, 24T) và `XORTAP8_CMOS` (3 × XOR2_X1, 36T, đối chứng): FB = Q0 ^ Q5 ^ Q6 ^ Q7 | Mạng hồi tiếp của MS/TSPC_LFSR_8bit (XORTAP8), TSPC_LFSR_8bit_CMOS (XORTAP8_CMOS) |
| `blocks/CFSR_FB_OPT.scs` | `CFSR_FB_OPT` 42T, bản tối ưu của CFSR_FB (cùng hàm) | **TSPC_CFSR_8bit** (256 trạng thái) |
| `blocks/CFSR_FB.scs` | `CFSR_FB` 56T và `CFSR_FB_CMOS` 74T, TV3 giữ để so sánh | Chỉ để đối chiếu số liệu cũ |
| `layout/gds/XOR2_TG6.gds, XOR2_X1.gds` | Layout cell của TV3 | Đặt trong hai dải LFSR 8 bit |
| `layout/gds/AOI21_X1.gds, XNOR2_X1.gds` | Layout cell của TV3 | Dự phòng cho layout TSPC_CFSR_8bit |
| `layout/rcx/CFSR_FB_rcx.scs, CFSR_FB_OPT_rcx.scs, CFSR_FB_CMOS_rcx.scs` | Netlist sau layout (Assura RCX, R + C) của 3 khối hồi tiếp CFSR | So sánh 3 khối trong thanh ghi TSPC ([docs/4_ket_qua.md](../../../../docs/4_ket_qua.md) mục 4.3) |

Không sửa các file này. Khi TV3 cập nhật repo: chép lại đè thư mục này rồi chạy lại mô phỏng Spectre.

Lịch sử đồng bộ:
- **19/11/2026**, `86e42ee`: chân nguồn `VSS` → `GND`; `TSPC_LFSR_8bit_TG` đổi thành `TSPC_LFSR_8bit_CMOS`.
- **22/11/2026**, `435f6f0`: thêm AOI21_X1, XNOR2_X1, CFSR_FB_OPT; `TSPC_CFSR_8bit` chuyển từ CFSR_FB (56T) sang CFSR_FB_OPT (42T). Các cell còn lại giống hệt `86e42ee`. Bỏ `check.awk`, `lfsr_model.awk` vì branch của TV3 không còn hai file này.
- **22/11/2026**, `195bacb` ("Hoàn thiện tài liệu và Chương 3 của TV3"): TV3 thêm thư viện Virtuoso, testbench vòng kín, ảnh, báo cáo. Các file netlist và GDS ở đây **giống hệt** `435f6f0` (đã so bằng `git diff`). Lấy thêm 3 netlist RCX của khối hồi tiếp vào `layout/rcx/`.
