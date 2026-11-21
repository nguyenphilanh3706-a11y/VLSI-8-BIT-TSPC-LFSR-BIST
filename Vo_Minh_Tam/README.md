# TV3: cổng XOR, thư viện cổng cơ bản, CFSR (Võ Minh Tâm)

Công nghệ gpdk090, VDD 1,2 V, Spectre, Assura 4.1, Encounter. Chân nguồn thống nhất của nhóm: VDD, GND.

## Đã làm được

| Hạng mục | Kết quả |
|---|---|
| Cổng XOR2 | 3 cấu trúc: CMOS tĩnh 12T (XOR2_X1), cổng truyền 8T (XOR2_TG), cổng truyền 6T (XOR2_TG6); so sánh trễ, năng lượng, diện tích ở NN/SS/FF, tải FO4 và FO8, trước và sau layout |
| Thư viện cổng cơ bản | INV_X1, NAND2_X1, NOR2_X1, NOR3_X1; testbench từng cell PASS cả 3 corner |
| Mạng hồi tiếp LFSR | XORTAP8: FB = Q0 ^ Q5 ^ Q6 ^ Q7 (đa thức 1 + x + x^6 + x^7 + x^8), 24T thay cho 36T |
| Chống kẹt trạng thái 0 | ZERO7 (phát hiện Q0..Q6 = 0) và CFSR_FB: LFSR 255 trạng thái thành 256 trạng thái, đúng 256/256 tổ hợp |
| Cellview | 7 cell lá có schematic, symbol, layout, extracted; 5 khối có schematic, symbol, layout, extracted |
| Kiểm tra vật lý | DRC 0 lỗi, LVS Match cho cả 12 cell và khối |
| Mô phỏng sau layout | Trích R + C bằng Assura RCX, mọi testbench PASS ở NN/SS/FF |
| Báo cáo | Phần Chương 3: mạng hồi tiếp, XOR, chống kẹt trạng thái 0 |

## Số liệu chính (sau layout, corner NN)

| Cell / khối | Transistor | Diện tích (µm²) | Trễ | Năng lượng |
|---|---|---|---|---|
| XOR2_X1 (CMOS 12T) | 12 | 13,41 | 121,6 ps | 0,017 pJ |
| XOR2_TG (8T) | 8 | 8,94 | 113,9 ps | 0,017 pJ |
| XOR2_TG6 (6T) | 6 | 7,45 | 113,9 ps | 0,016 pJ |
| XORTAP8 | 24 | 28,3 | 195,2 ps | 0,024 pJ |
| CFSR_FB | 56 | 62,6 | 275,5 ps (SS 390,6 ps) | 0,040 pJ |
| CFSR_FB_CMOS (đối chứng) | 74 | 83,5 | 281,0 ps (SS 398,5 ps) | 0,043 pJ |

XOR2_TG6 nhỏ hơn XOR CMOS 44 %. CFSR_FB nhỏ hơn bản CMOS 25 %, nhanh hơn 2 %, tốn ít hơn 7 % năng lượng.
Diện tích khối là tổng diện tích cell lá.

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `cells/` | netlist và testbench 7 cell lá |
| `blocks/` | XORTAP8, ZERO7, CFSR_FB và bản đối chứng CMOS |
| `tb/` | testbench khối, so sánh XOR (FO4, FO8), bản NN/SS/FF |
| `layout/gds/` | GDS cell lá, cell lấp (FILL) và khối |
| `layout/assura/` | báo cáo DRC/LVS khối |
| `layout/rcx/` | netlist trích ký sinh và testbench sau layout |
| `layout/hinh/` | ảnh layout |
| `KET_QUA_TV3.md` | bảng kết quả đầy đủ |
| `HUONG_DAN_TV3.md` | mô tả cell, cách chạy testbench, ADE L, layout |
| `BAO_CAO_CHUONG3_TV3.md` | phần Chương 3 của báo cáo |

Thư viện Virtuoso trong VM: `~/TV3_PROJ/TV3_CELLS` (cell lá, schematic và symbol khối), `~/TV3_PROJ/TV3_BLK` (layout khối).

## Còn lại

- Ảnh chụp màn hình DRC/LVS trong Virtuoso cho báo cáo (đã có báo cáo dạng text).
- Ghép CFSR_FB với flip-flop TSPC (TV2) thành LFSR 8 bit (TV4).
