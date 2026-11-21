# Kết quả TV3: cổng XOR, mạng hồi tiếp LFSR, CFSR

Spectre, 27 °C, VDD 1,2 V. Mỗi ngõ vào qua 2 INV_X1 đệm (giống ngõ ra flip-flop), mỗi ngõ ra tải 4 INV_X1.
Trễ = lần cắt 0,6 V cuối cùng của ngõ ra, tính từ giữa sườn vào, lấy lớn nhất trên mọi vector.
Tổng W = tổng bề rộng kênh của các transistor (đại diện diện tích trước khi vẽ layout).

Cách chạy testbench: `HUONG_DAN_TV3.md` mục 4.

## 1. Cổng XOR2 (9 vector, duyệt mọi cạnh của 2 ngõ vào)

| Cell | Transistor | Tổng W | Trễ NN | Trễ SS | Trễ FF | Năng lượng NN |
|---|---|---|---|---|---|---|
| XOR2_X1 (CMOS tĩnh) | 12 | 3,60 µm | 136,0 ps | 191,8 ps | 106,3 ps | 0,020 pJ |
| XOR2_TG (cổng truyền) | 8 | 2,16 µm | 147,4 ps | 207,1 ps | 115,6 ps | 0,021 pJ |
| XOR2_TG6 (6T) | 6 | 1,44 µm | 137,6 ps | 194,9 ps | 106,6 ps | 0,019 pJ |

XOR2_TG6 giảm 50% transistor và 60% tổng W so với CMOS, trễ chỉ chậm hơn 1,6 ps (NN), năng lượng thấp hơn 5%.
Kích thước chọn sau khi quét 8 bộ: cặp đảo B (MN1/MP1) 0,24/0,48 µm, cổng truyền và inverter nhỏ nhất.
Làm cặp đảo lớn hơn nữa (0,36/0,72) không nhanh thêm mà tốn năng lượng.

## 2. Mạng XOR hồi tiếp FB = Q0 ^ Q5 ^ Q6 ^ Q7 (16 tổ hợp)

| Khối | Transistor | Tổng W | Trễ NN | Trễ SS | Trễ FF | Năng lượng NN |
|---|---|---|---|---|---|---|
| XORTAP8_CMOS (3 XOR CMOS) | 36 | 10,80 µm | 220,0 ps | 312,7 ps | 170,8 ps | 0,029 pJ |
| XORTAP8 (2 XOR 6T + 1 XOR CMOS) | 24 | 6,48 µm | 225,0 ps | 321,5 ps | 173,1 ps | 0,026 pJ |

Tầng cuối giữ XOR CMOS: hai XOR 6T nối tiếp làm suy mức logic, trễ tăng 25% (đo được 274,9 ps NN).

## 3. CFSR_FB: hồi tiếp đầy đủ (256 tổ hợp)

| Khối | Transistor | Tổng W | Trễ NN | Trễ SS | Trễ FF | Năng lượng NN |
|---|---|---|---|---|---|---|
| CFSR_FB_CMOS (XOR CMOS, cây NOR2/NAND2) | 74 | 21,48 µm | 305,8 ps | 434,6 ps | 237,6 ps | 0,048 pJ |
| CFSR_FB (XORTAP8 + ZERO7 + XOR CMOS) | 56 | 15,84 µm | 316,7 ps | 437,3 ps | 250,1 ps | 0,045 pJ |

CFSR_FB giảm 24% transistor, 26% tổng W, 6% năng lượng; ở SS (corner quyết định tần số) trễ chỉ tăng 0,6%.
ZERO7 phát hiện Q0..Q6 = 0 bằng 2 NOR3 + NAND2 + NOR2 (20T, thay cho 26T).
Các phương án đã thử và bỏ: dùng XOR 6T cả 4 cổng (44T, 468 ps NN), XOR 6T hai tầng đầu (50T, 326 ps NN).

## 4. Mô hình chuẩn
LFSR (FB = Q0^Q5^Q6^Q7, dịch Q0 -> Q7) có 255 trạng thái khác nhau;
CFSR có 256 trạng thái, gồm cả 00000000. Bảng giá trị mong đợi của testbench sinh từ cùng công thức.

## 5. Testbench từng cell (tải FO4, ngõ vào sườn 20 ps)

| Cell | Vector | Trễ NN | Trễ SS | Trễ FF |
|---|---|---|---|---|
| INV_X1 | 3/3 | 34,1 ps | 45,6 ps | 28,1 ps |
| NAND2_X1 | 9/9 | 53,4 ps | 72,2 ps | 43,4 ps |
| NOR2_X1 | 9/9 | 50,1 ps | 67,2 ps | 40,4 ps |
| NOR3_X1 | 9/9 | 64,8 ps | 86,9 ps | 52,2 ps |
| XOR2_X1 | 9/9 | 77,3 ps | 108,5 ps | 60,6 ps |
| XOR2_TG | 9/9 | 82,6 ps | 114,5 ps | 65,7 ps |
| XOR2_TG6 | 9/9 | 75,5 ps | 106,4 ps | 58,5 ps |

Ngõ vào lấy trực tiếp từ nguồn PWL (không qua INV đệm) nên trễ nhỏ hơn bảng mục 1.
Cách dùng testbench và mô tả từng cell: `HUONG_DAN_TV3.md`.

## 6. Schematic và symbol (thư viện TV3_CELLS)
Chân thống nhất của nhóm: VDD, GND. 12 cell: INV_X1, NAND2_X1, NOR2_X1, NOR3_X1, XOR2_X1, XOR2_TG, XOR2_TG6,
XORTAP8, XORTAP8_CMOS, ZERO7, CFSR_FB, CFSR_FB_CMOS.
Dây nối thật: PMOS trên, NMOS dưới, MOS nối tiếp chồng dọc, ray VDD/GND.
Kết quả: 12 cell, schCheck 0 lỗi 0 cảnh báo; 288 chân khớp netlist.

## 7. Layout và kiểm tra DRC/LVS (Assura 4.1, luật gpdk090)
Cell lá cao 2,76 µm, bước cột 0,27 µm, ray VDD/GND Metal1 dùng chung khi xếp liền hàng; chân Metal1.
Khối ghép đặt và đi dây bằng Encounter từ các cell lá (mật độ lõi 60 %, vòng nguồn Metal2/Metal3).

| Cell | Rộng x cao (µm) | Diện tích (µm²) | DRC | LVS |
|---|---|---|---|---|
| INV_X1 | 1,08 x 2,76 | 2,98 | 0 lỗi | Match |
| NAND2_X1 | 1,62 x 2,76 | 4,47 | 0 lỗi | Match |
| NOR2_X1 | 1,62 x 2,76 | 4,47 | 0 lỗi | Match |
| NOR3_X1 | 2,16 x 2,76 | 5,96 | 0 lỗi | Match |
| XOR2_X1 (CMOS 12T) | 4,86 x 2,76 | 13,41 | 0 lỗi | Match |
| XOR2_TG (8T) | 3,24 x 2,76 | 8,94 | 0 lỗi | Match |
| XOR2_TG6 (6T) | 2,70 x 2,76 | 7,45 | 0 lỗi | Match |

| Khối | Diện tích cell (µm²) | Lõi (µm²) | Cả vòng nguồn (µm) | DRC | LVS |
|---|---|---|---|---|---|
| XORTAP8 | 28,3 | 47,2 | 14,74 x 11,71 | 0 lỗi | Match |
| XORTAP8_CMOS | 40,2 | 67,1 | 18,34 x 11,71 | 0 lỗi | Match |
| ZERO7 | 20,9 | 34,8 | 12,49 x 11,71 | 0 lỗi | Match |
| CFSR_FB | 62,6 | 104,3 | 18,79 x 14,47 | 0 lỗi | Match |
| CFSR_FB_CMOS | 83,5 | 139,1 | 18,79 x 17,23 | 0 lỗi | Match |

XOR2_TG6 nhỏ hơn XOR2_X1 44 %; CFSR_FB nhỏ hơn CFSR_FB_CMOS 25 % (diện tích cell).
Cellview: cell lá có schematic, symbol, layout, av_extracted trong `TV3_CELLS`; khối có layout, av_extracted trong `TV3_BLK`
(schematic, symbol của khối ở `TV3_CELLS`). LVS chạy lại trên thư viện Virtuoso cũng Match cả 12 cell.
GDS: `layout/gds/`; báo cáo LVS khối: `layout/assura/`; ảnh layout: `layout/hinh/`.

## 8. Mô phỏng sau layout (Assura RCX, R + C)
Netlist trích ký sinh: `layout/rcx/<CELL>_rcx.scs`; testbench `layout/rcx/tb_*_post_<corner>.scs` dùng lại bảng mong đợi cũ.
Mọi testbench sau layout PASS (XOR 9/9, XORTAP8 16/16, CFSR_FB 256/256 ở cả NN/SS/FF).

| Cell / khối | Trễ NN trước → sau | Trễ SS sau | Trễ FF sau | Năng lượng NN sau |
|---|---|---|---|---|
| XOR2_X1 | 136,0 → 121,6 ps | 170,7 ps | 95,4 ps | 0,017 pJ |
| XOR2_TG | 147,4 → 113,9 ps | 159,1 ps | 89,7 ps | 0,017 pJ |
| XOR2_TG6 | 137,6 → 113,9 ps | 160,6 ps | 88,8 ps | 0,016 pJ |
| XORTAP8_CMOS | 220,0 → 196,5 ps | 278,0 ps | 153,0 ps | 0,026 pJ |
| XORTAP8 | 225,0 → 195,2 ps | 277,9 ps | 150,8 ps | 0,024 pJ |
| CFSR_FB_CMOS | 305,8 → 281,0 ps | 398,5 ps | 218,5 ps | 0,043 pJ |
| CFSR_FB | 316,7 → 275,5 ps | 390,6 ps | 214,9 ps | 0,040 pJ |

Trễ sau layout nhỏ hơn trước layout vì netlist trước layout không ghi diện tích/chu vi cực nguồn, máng (ad, as, pd, ps):
model `gpdk090_nmos1v`/`pmos1v` khi đó lấy mặc định ad = as = 1 µm², pd = ps = 1 µm, lớn gấp khoảng 20 lần
giá trị đo trên layout (MOS 0,24 µm có ad khoảng 0,05 µm²). Điện dung tiếp giáp bị tính dư nhiều hơn phần điện dung dây thêm vào.
Sau layout, XOR cổng truyền nhanh hơn CMOS (113,9 so với 121,6 ps ở NN); CFSR_FB nhanh hơn CFSR_FB_CMOS
2 % ở NN và SS, tốn ít hơn 7 % năng lượng.

## 9. XOR2 với tải 8 cổng (FO8)
Testbench `tb/tb_XOR2_*_fo8_<corner>.scs` giống bản so sánh mục 1 nhưng ngõ ra tải 8 INV_X1 (tương đương 8 ngõ vào D
của thanh ghi 8 bit). Sau layout: `layout/rcx/tb_XOR2_*_fo8_post_<corner>.scs`.

| Cell | Trễ NN trước / sau | Trễ SS trước / sau | Trễ FF trước / sau | Năng lượng NN trước / sau |
|---|---|---|---|---|
| XOR2_X1 | 152,5 / 137,8 ps | 214,8 / 193,3 ps | 119,5 / 108,3 ps | 0,031 / 0,027 pJ |
| XOR2_TG | 169,2 / 135,4 ps | 237,0 / 188,7 ps | 133,3 / 107,1 ps | 0,035 / 0,031 pJ |
| XOR2_TG6 | 158,2 / 135,0 ps | 223,7 / 190,1 ps | 122,7 / 106,4 ps | 0,034 / 0,029 pJ |

Với tải 8 cổng, sau layout ba cấu trúc chênh nhau dưới 3 ps ở NN và dưới 5 ps ở SS; XOR2_X1 tốn ít năng lượng nhất (ngõ ra được kéo thẳng về ray),
XOR2_TG6 có diện tích nhỏ nhất. Vì vậy tầng đầu mạng hồi tiếp (ngõ vào từ flip-flop, tải 1 cổng) dùng XOR2_TG6,
tầng cuối (lái ngõ D) dùng XOR2_X1.
