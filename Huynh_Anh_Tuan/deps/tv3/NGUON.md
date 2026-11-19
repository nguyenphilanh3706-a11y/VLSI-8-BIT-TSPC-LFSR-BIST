# Nguồn các file của TV3 trong thư mục này

Bản sao **chỉ đọc** từ repo nhóm `nguyenphilanh3706-a11y/VLSI-8-BIT-TSPC-LFSR-BIST`, branch `cell/XOR-CFSR-LOGIC(3)` (= `main` lúc chép), commit `86e42ee` (17/11/2026, "Chỉnh chính tả"; trước đó dùng `44ee63c` ngày 14/11), thư mục `Vo_Minh_Tam/`.

| File | Nội dung | TV4 dùng để |
|---|---|---|
| `cells/INV_X1, NAND2_X1, NOR2_X1, NOR3_X1, XOR2_X1, XOR2_TG6` (+ `XOR2_TG` cũ, không dùng nữa) | Cổng cơ bản, nguồn `VDD GND` | Ghép LFSR, AND2, MUX, flip-flop tạm |
| `blocks/XORTAP8.scs` | `XORTAP8` (2 × XOR2_TG6 + 1 × XOR2_X1, 24T) và `XORTAP8_CMOS` (3 × XOR2_X1, 36T, đối chứng): FB = Q0 ^ Q5 ^ Q6 ^ Q7 | Mạng hồi tiếp của MS/TSPC_LFSR_8bit (XORTAP8), TSPC_LFSR_8bit_CMOS (XORTAP8_CMOS) |
| `blocks/CFSR_FB.scs` | `CFSR_FB` 56T (XORTAP8 + `ZERO7` dùng NOR3) và `CFSR_FB_CMOS` 74T | TSPC_CFSR_8bit (256 trạng thái) |
| `check.awk` | Bộ kiểm tra kết quả Spectre của TV3 | Gốc của `scripts/check_tv4.awk` |
| `lfsr_model.awk` | Mô hình LFSR/CFSR của TV3 | Đối chiếu với golden model MATLAB của TV4 (trùng kết quả) |

Không sửa các file này. Khi TV3 cập nhật repo: chép lại đè thư mục này rồi chạy lại `python3 scripts/ngspice/precheck_ngspice.py` và các mô phỏng Spectre.

**19/11/2026**: cập nhật lên `86e42ee`. Thay đổi kéo theo ở TV4: chân nguồn `VSS` → `GND` trong mọi netlist TV4; khối `TSPC_LFSR_8bit_TG` (dùng `XORTAP8_TG` đã bị TV3 bỏ) đổi thành `TSPC_LFSR_8bit_CMOS` (dùng `XORTAP8_CMOS`); testbench `tb_TSPC_LFSR_TG` → `tb_TSPC_LFSR_CMOS`.
