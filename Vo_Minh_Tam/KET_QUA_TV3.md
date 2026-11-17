# Kết quả TV3: cổng XOR, mạng hồi tiếp LFSR, CFSR

Spectre, 27 °C, VDD 1,2 V. Mỗi ngõ vào qua 2 INV_X1 đệm (giống ngõ ra flip-flop), mỗi ngõ ra tải 4 INV_X1.
Trễ = lần cắt 0,6 V cuối cùng của ngõ ra, tính từ giữa sườn vào, lấy lớn nhất trên mọi vector.
Tổng W = tổng bề rộng kênh của các transistor (đại diện diện tích trước khi vẽ layout).

Chạy lại: `bash scripts/run_sim.sh tb/tb_<tên>_<NN|SS|FF>.scs`

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
`scripts/lfsr_model.awk`: LFSR (FB = Q0^Q5^Q6^Q7, dịch Q0 -> Q7) có 255 trạng thái khác nhau;
CFSR có 256 trạng thái, gồm cả 00000000. Bảng giá trị mong đợi của testbench sinh từ cùng công thức.

## 5. Testbench từng cell (`bash scripts/run_cells.sh`, tải FO4, ngõ vào sườn 20 ps)

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
