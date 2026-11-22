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
Bản tối ưu thêm AOI21_X1, XNOR2_X1, CFSR_FB_OPT: schCheck 0 lỗi 0 cảnh báo; 153 chân khớp netlist.

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
Cellview: cell lá và khối đều có schematic, symbol, layout, av_extracted trong `TV3_CELLS` (`TV3_BLK` giữ layout cell con và via của khối).
LVS trên thư viện Virtuoso so với netlist xuất từ schematic (`layout/cdl/`) Match cả 15 cell và bản XOR2_X1 nén.
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

## 10. Bản tối ưu CFSR_FB_OPT (so sánh với CFSR_FB)

Bản cũ CFSR_FB, CFSR_FB_CMOS giữ nguyên để so sánh. Bản tối ưu thêm các file:
`blocks/CFSR_FB_OPT.scs`, `cells/AOI21_X1`, `cells/XNOR2_X1`, `tb/tb_CFSR_FB_OPT*`, `tb/tb_XNOR2_X1_*`,
`layout/gds/{CFSR_FB_OPT,AOI21_X1,XNOR2_X1,XOR2_X1_OPT}.gds`, `layout/rcx/*OPT*`, `layout/rcx/*XNOR2_X1*`, `layout/rcx/AOI21_X1_rcx.scs`.

### 10.1 Rút gọn logic
Khi Z = NOR(Q0..Q6) = 1 thì Q0 = Q5 = Q6 = 0, nên (Q0 ^ Q5) và Z không thể cùng bằng 1: phép XOR giữa chúng
thay được bằng phép OR. Thêm nữa, khi Q0 ^ Q5 = 0 và Q0 = 0 thì Q5 = 0, nên nhánh phát hiện 0 bỏ được Q5:

  FB = (Q6 ^ Q7) ^ W,  W = (Q0 ^ Q5) | NOR3(Q0, Q1, Q2) & NOR3(Q3, Q4, Q6)

!W lấy từ một cổng AOI21 (6T) thay cho NAND2 + NOR2 + một XOR CMOS. Tầng cuối là XNOR2 CMOS (phục hồi mức logic):
FB = XNOR(Q6 ^ Q7, !W). Đúng cả 256/256 tổ hợp (kiểm tra bằng mô hình và mô phỏng ở NN/SS/FF).

| Khối | Cấu trúc | Transistor | Tổng W | Số tầng trên đường dài nhất |
|---|---|---|---|---|
| CFSR_FB_CMOS | 4 XOR CMOS + NOR2/NAND2/INV | 74 | 21,48 µm | 4 |
| CFSR_FB | XORTAP8 + ZERO7 + XOR CMOS | 56 | 15,84 µm | 4 |
| CFSR_FB_OPT | 2 XOR2_TG6 + 2 NOR3 + AOI21 + XNOR2 CMOS | 42 | 12,12 µm | 3 |

Kích thước giữ như cell gốc sau khi quét 5 phương án (giảm pMOS của AOI21, NOR3, XNOR2 xuống 0,36 µm; inverter XNOR2
0,18 µm; tăng nMOS ngõ B của AOI21 lên 0,24 µm): mọi phương án đều chậm hơn từ 1 đến 6 % mà năng lượng gần như không đổi.

### 10.2 Cell mới và cell nén lại

| Cell | Hàm | T | Rộng x cao (µm) | Diện tích (µm²) | Trễ FO4 NN / SS / FF | DRC | LVS |
|---|---|---|---|---|---|---|---|
| AOI21_X1 | Y = !(A1.A2 + B) | 6 | 2,16 x 2,76 | 5,96 | 51,6 / 73,0 / 39,8 ps | 0 lỗi | Match |
| XNOR2_X1 | Y = !(A ^ B) | 12 | 4,32 x 2,76 | 11,92 | 92,7 / 129,4 / 73,0 ps | 0 lỗi | Match |
| XOR2_X1 bản nén (thư viện TV3_OPT) | Y = A ^ B | 12 | 4,32 x 2,76 | 11,92 | như XOR2_X1 | 0 lỗi | Match |

XOR2_X1 cũ rộng 17 cột (4,86 µm, 2 chỗ đứt khuếch tán). Thứ tự transistor mới chỉ còn 1 chỗ đứt: 15 cột, nhỏ hơn 11 %.
Cấu trúc 2 inverter + cổng phức không đặt được trên một vệt khuếch tán liền cho cả hai hàng, nên 15 cột là mức nhỏ nhất.
Sau layout bản nén có trễ và năng lượng như bản cũ (FO4 NN 121,5 / 121,6 ps; FO8 NN 137,8 / 137,8 ps; 0,017 pJ).
Ảnh so sánh: `layout/hinh/XOR2_X1.png`, `layout/hinh/XOR2_X1_OPT.png`.

### 10.3 Layout khối
Đặt và đi dây lại bằng Encounter: mật độ lõi 0,9 (cũ 0,6), lề 1,4 µm, vòng nguồn Metal2/Metal3 rộng 0,3 µm (cũ 0,6 µm).
Các cấu hình đã thử: mật độ 0,95 còn 4 lỗi DRC; 0,9 / 0,85 / 0,8 / 0,7 đều sạch.

| Khối | Diện tích cell | Khung cả vòng nguồn | DRC | LVS |
|---|---|---|---|---|
| CFSR_FB (layout cũ, mật độ 0,6, vòng 0,6 µm) | 62,6 µm² | 18,79 x 14,47 = 271,9 µm² | 0 lỗi | Match |
| CFSR_FB (cùng cấu hình P&R mới, để so công bằng) | 62,6 µm² | 14,79 x 8,37 = 123,8 µm² | 0 lỗi | Match |
| CFSR_FB_OPT | 44,7 µm² | 11,85 x 8,37 = 99,2 µm² | 0 lỗi | Match |

Cellview: CFSR_FB_OPT, AOI21_X1, XNOR2_X1 đủ 4 view trong TV3_CELLS; XOR2_X1 bản nén đủ 4 view trong TV3_OPT.

### 10.4 Kết quả (256 tổ hợp, mọi corner PASS)

| Khối | Trễ NN trước → sau | Trễ SS sau | Trễ FF sau | Năng lượng NN sau |
|---|---|---|---|---|
| CFSR_FB_CMOS | 305,8 → 281,0 ps | 398,5 ps | 218,5 ps | 0,043 pJ |
| CFSR_FB | 316,7 → 275,5 ps | 390,6 ps | 214,9 ps | 0,040 pJ |
| CFSR_FB_OPT | 275,1 → 244,8 ps | 350,5 ps | 188,4 ps | 0,036 pJ |

| CFSR_FB_OPT so với | Transistor | Diện tích cell | Trễ NN | Trễ SS | Năng lượng | Diện tích x trễ x năng lượng |
|---|---|---|---|---|---|---|
| CFSR_FB | -25 % | -29 % | -11 % | -10 % | -10 % | -43 % |
| CFSR_FB_CMOS | -43 % | -46 % | -13 % | -12 % | -16 % | -61 % |

Trễ lớn nhất sau layout ở cả 3 corner rơi vào vector 128 (Q0..Q6 từ 1 về 0, Q7 từ 0 lên 1): tín hiệu đi qua
NOR3 (3 pMOS nối tiếp), AOI21 rồi XNOR2.
Chạy lại: `layout/rcx/tb_CFSR_FB_OPT_post_<NN|SS|FF>.scs`, cách chạy ở `HUONG_DAN_TV3.md` mục 4.

## 11. Trễ và công suất XOR2 (sau layout)

| Cổng | Tải | Trễ NN | Trễ SS | Trễ FF | Công suất NN | Công suất SS | Công suất FF |
|---|---|---|---|---|---|---|---|
| XOR2_X1 (CMOS 12T) | FO4 | 121,6 ps | 170,7 ps | 95,4 ps | 16,8 µW | 16,1 µW | 17,6 µW |
| XOR2_TG (8T) | FO4 | 113,9 ps | 159,1 ps | 89,7 ps | 17,3 µW | 16,5 µW | 18,3 µW |
| XOR2_TG6 (6T) | FO4 | 113,9 ps | 160,6 ps | 88,8 ps | 15,7 µW | 15,0 µW | 16,5 µW |
| XOR2_X1 (CMOS 12T) | 8 cổng | 137,8 ps | 193,3 ps | 108,3 ps | 26,8 µW | 25,6 µW | 28,3 µW |
| XOR2_TG (8T) | 8 cổng | 135,4 ps | 188,7 ps | 107,1 ps | 30,5 µW | 28,7 µW | 32,7 µW |
| XOR2_TG6 (6T) | 8 cổng | 135,0 ps | 190,1 ps | 106,4 ps | 29,2 µW | 27,6 µW | 31,1 µW |

Công suất là công suất trung bình lấy từ nguồn VDD của cả testbench (cổng, inverter đệm và tải) khi mỗi vector kéo dài
1 ns. Tính cả bộ đệm vì cổng truyền lấy một phần dòng từ ngõ vào.
XOR2_TG6 tốn ít công suất nhất ở FO4; với tải 8 cổng XOR2_X1 tốn ít nhất.

## 12. CFSR trong vòng kín

Testbench `tb/tb_CFSR_loop_<NN|SS|FF>.scs`: khối hồi tiếp sau layout nối với 8 flip-flop mẫu (`tb/dff_mau.scs`, lý tưởng).
Bảng `tb/tb_CFSR_loop.exp` so cả 40 bit ở từng chu kỳ: 258/258 đúng ở mỗi corner.

| Thanh ghi | Trạng thái đầu | Kết quả sau 258 chu kỳ 1 GHz (NN, SS, FF) |
|---|---|---|
| LFSR thuần (XORTAP8) | 00000000 | kẹt ở 00000000 |
| LFSR thuần (XORTAP8) | 00000001 | 255 trạng thái, không qua 00000000, lặp lại ở chu kỳ 255 |
| CFSR_FB_CMOS | 00000000 | tự thoát, 256 trạng thái, về 00000000 ở chu kỳ 256 |
| CFSR_FB | 00000000 | tự thoát, 256 trạng thái, về 00000000 ở chu kỳ 256 |
| CFSR_FB_OPT | 00000000 | tự thoát, 256 trạng thái, về 00000000 ở chu kỳ 256 |

Dạng sóng: `anh/dang_song/CFSR_loop.png`. Flip-flop mẫu không có trễ và tải của TSPC, vì vậy kết quả này kiểm chức năng,
không phải f_max.

## 13. Testbench schematic trong Virtuoso

TV3_CELLS có `tb_<CELL>` cho 15 cell, khối và `tb_XOR2_FO8`. Mô phỏng NN từ schematic: mọi tổ hợp ngõ vào đều đúng
(tới 256/256 với các khối CFSR). Schematic không chạy callback CDF nên mọi transistor giữ ad, as mặc định 0,0696 µm²;
trễ đo từ các testbench này khác bảng trước layout và chỉ dùng để xem chức năng. Số liệu chính thức là bảng sau layout.
