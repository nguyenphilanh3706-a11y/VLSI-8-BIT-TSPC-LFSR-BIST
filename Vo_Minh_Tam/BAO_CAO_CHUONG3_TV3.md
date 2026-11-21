# Chương 3 (phần TV3): Mạng hồi tiếp đa thức, cổng XOR và cơ chế chống kẹt trạng thái 0

Phần này trình bày mạng hồi tiếp tuyến tính của bộ LFSR 8 bit, ba cấu trúc cổng XOR2 được thiết kế và so sánh,
mạch chống kẹt trạng thái toàn 0 (CFSR) cùng layout và kết quả kiểm tra DRC/LVS trên công nghệ gpdk090
(VDD = 1,2 V, L = 0,1 µm). Số liệu mô phỏng lấy từ Spectre ở 27 °C với ba góc công nghệ NN, SS, FF.

## 3.x.1 Mạng hồi tiếp đa thức

Bộ LFSR 8 bit dùng đa thức nguyên thủy P(x) = 1 + x + x⁶ + x⁷ + x⁸ [1, Mục 11.5.4]. Với thanh ghi dịch Q0 → Q7,
giá trị hồi tiếp về ngõ vào D0 là

  FB = Q0 ⊕ Q5 ⊕ Q6 ⊕ Q7.

Vì P(x) nguyên thủy, chuỗi trạng thái có chu kỳ cực đại 2⁸ − 1 = 255 và đi qua mọi trạng thái khác 00000000.
Mô hình chuẩn `scripts/lfsr_model.awk` xác nhận 255 trạng thái khác nhau; bảng giá trị mong đợi của các testbench
được sinh từ cùng công thức này.

Bốn tín hiệu được XOR theo cây hai tầng (khối XORTAP8): tầng 1 gồm XOR(Q0, Q5) và XOR(Q6, Q7), tầng 2 XOR hai kết quả.
Cây hai tầng có độ trễ bằng hai cổng XOR thay vì ba cổng nếu nối tiếp.

## 3.x.2 Cổng XOR2

Ba cấu trúc được thiết kế (Bảng 3.1). Kích thước nhỏ nhất: nMOS 0,12 µm, pMOS 0,24 µm; nhánh nối tiếp được nhân đôi
bề rộng để giữ dòng kéo tương đương inverter chuẩn.

Bảng 3.1. Ba cấu trúc cổng XOR2

| Cell | Cấu trúc | Số transistor | Tổng W | Diện tích layout |
|---|---|---|---|---|
| XOR2_X1 | CMOS tĩnh: 2 inverter + cổng phức Y = !(A·B + Ā·B̄) | 12 | 3,60 µm | 13,41 µm² |
| XOR2_TG | 2 inverter + 2 cổng truyền (A = 0 cho B qua, A = 1 cho B̄ qua) | 8 | 2,16 µm | 8,94 µm² |
| XOR2_TG6 | 1 inverter + 1 cổng truyền + cặp đảo B lấy nguồn từ A/Ā | 6 | 1,44 µm | 7,45 µm² |

Ở XOR2_TG6, khi A = 0 cổng truyền (nMOS cổng Ā, pMOS cổng A) đưa B ra Y; khi A = 1 cặp MP1/MN1 hoạt động như
inverter cấp nguồn bởi A và Ā, cho Y = B̄. Cặp này được làm rộng gấp đôi (0,24/0,48 µm) để kéo Y nhanh; quét 8 bộ kích
thước cho thấy làm rộng hơn nữa (0,36/0,72 µm) không giảm trễ mà tăng năng lượng.

Bảng 3.2 so sánh ba cổng khi ngõ vào đi qua 2 inverter đệm (giống ngõ ra flip-flop), ngõ ra tải 4 inverter (FO4),
duyệt cả 9 cạnh chuyển của hai ngõ vào. Số "sau layout" dùng netlist trích ký sinh R và C bằng Assura RCX.

Bảng 3.2. Trễ lớn nhất và năng lượng mỗi phép của cổng XOR2 (FO4)

| Cell | NN trước layout | NN sau layout | SS sau layout | FF sau layout | Năng lượng NN sau layout |
|---|---|---|---|---|---|
| XOR2_X1 | 136,0 ps | 121,6 ps | 170,7 ps | 95,4 ps | 0,017 pJ |
| XOR2_TG | 147,4 ps | 113,9 ps | 159,1 ps | 89,7 ps | 0,017 pJ |
| XOR2_TG6 | 137,6 ps | 113,9 ps | 160,6 ps | 88,8 ps | 0,016 pJ |

Trễ sau layout nhỏ hơn trước layout vì netlist trước layout không ghi diện tích cực nguồn, máng; model gpdk090 khi đó
lấy mặc định 1 µm² cho mỗi cực, lớn gấp khoảng 20 lần giá trị thực trên layout, nên điện dung tiếp giáp bị tính dư.

Để đánh giá trong bộ 8 bit, ngõ ra được tải 8 inverter (FO8), tương đương 8 ngõ vào D của thanh ghi (Bảng 3.3).

Bảng 3.3. Cổng XOR2 với tải 8 cổng, sau layout

| Cell | Trễ NN | Trễ SS | Trễ FF | Năng lượng NN |
|---|---|---|---|---|
| XOR2_X1 | 137,8 ps | 193,3 ps | 108,3 ps | 0,027 pJ |
| XOR2_TG | 135,4 ps | 188,7 ps | 107,1 ps | 0,031 pJ |
| XOR2_TG6 | 135,0 ps | 190,1 ps | 106,4 ps | 0,029 pJ |

Nhận xét: sau layout ba cấu trúc có trễ gần bằng nhau (chênh dưới 3 ps ở NN, dưới 5 ps ở SS). XOR2_TG6 dùng ít hơn
50 % transistor và nhỏ hơn 44 % diện tích so với CMOS 12T. XOR2_X1 tốn ít năng lượng nhất khi tải lớn và luôn phục hồi
mức logic về ray. Hai cổng cổng truyền không phục hồi mức: nối tiếp hai XOR 6T làm suy mức logic, trễ tăng khoảng 25 %
(274,9 ps NN trước layout). Do đó XORTAP8 dùng XOR2_TG6 ở tầng 1 (ngõ vào lấy từ flip-flop) và XOR2_X1 ở tầng 2.

Bảng 3.4. Mạng hồi tiếp XORTAP8 (16 tổ hợp, sau layout)

| Khối | Transistor | Diện tích cell | Trễ NN | Trễ SS | Năng lượng NN |
|---|---|---|---|---|---|
| XORTAP8_CMOS (3 XOR CMOS) | 36 | 40,2 µm² | 196,5 ps | 278,0 ps | 0,026 pJ |
| XORTAP8 (2 XOR 6T + 1 XOR CMOS) | 24 | 28,3 µm² | 195,2 ps | 277,9 ps | 0,024 pJ |

## 3.x.3 Cơ chế chống kẹt trạng thái 0 (CFSR)

LFSR thuần không bao giờ đi vào trạng thái 00000000; nếu vì nhiễu hoặc khởi tạo sai mà rơi vào trạng thái này,
FB = 0 và thanh ghi kẹt mãi. Theo Hình 15.19b [1], hồi tiếp được bổ sung một nhánh NOR của các bit Q0…Q6:

  FB = Q0 ⊕ Q5 ⊕ Q6 ⊕ Q7 ⊕ NOR(Q0, Q1, …, Q6).

Khi Q0…Q6 đều bằng 0, nhánh NOR bằng 1 và đảo giá trị hồi tiếp, chèn trạng thái 00000000 vào chuỗi. Bộ đếm trở thành
thanh ghi hồi tiếp đầy đủ với 2⁸ = 256 trạng thái và tự thoát khỏi trạng thái toàn 0. Mô hình chuẩn xác nhận 256 trạng thái.

NOR 7 ngõ vào trực tiếp cần 7 pMOS nối tiếp, rất chậm. Khối ZERO7 thực hiện cùng hàm bằng cây
Z = NOR(NAND(NOR3(Q0,Q1,Q2), NOR3(Q3,Q4,Q5)), Q6), chỉ 20 transistor, tối đa 3 pMOS nối tiếp. Khối CFSR_FB gồm
XORTAP8 + ZERO7 + một XOR2_X1 cuối. Bản đối chứng CFSR_FB_CMOS dùng XOR CMOS và cây NOR2/NAND2/INV.

Bảng 3.5. Khối hồi tiếp đầy đủ CFSR (256 tổ hợp ngõ vào, sau layout)

| Khối | Transistor | Diện tích cell | Trễ NN | Trễ SS | Trễ FF | Năng lượng NN |
|---|---|---|---|---|---|---|
| CFSR_FB_CMOS | 74 | 83,5 µm² | 281,0 ps | 398,5 ps | 218,5 ps | 0,043 pJ |
| CFSR_FB | 56 | 62,6 µm² | 275,5 ps | 390,6 ps | 214,9 ps | 0,040 pJ |

CFSR_FB đúng cả 256/256 tổ hợp ở ba góc công nghệ, giảm 24 % transistor, 25 % diện tích, 7 % năng lượng và nhanh hơn
2 % so với bản CMOS. Trễ 390,6 ps ở SS là phần tổ hợp giữa hai flip-flop của bộ LFSR.

## 3.x.4 Layout và kiểm tra DRC/LVS

Cell lá dùng chung một khuôn: cao 2,76 µm, bước cột 0,27 µm, hàng nMOS tâm y = 0,64 µm, hàng pMOS tâm y = 2,00 µm,
ray GND và VDD bằng Metal1 ở hai biên để các cell xếp liền hàng dùng chung ray (Hình 3.1, Hình 3.2). MOS nối tiếp dùng
chung vùng khuếch tán; dây nội bộ chạy Metal1 dọc theo cột và Metal2 theo hàng. Các khối ghép được đặt và đi dây tự động
bằng Encounter từ các cell lá, có vòng nguồn Metal2/Metal3 (Hình 3.3). Kết quả kiểm tra bằng Assura 4.1 với bộ luật
gpdk090 cho ở Bảng 3.6.

Bảng 3.6. Kết quả layout

| Cell / khối | Kích thước | Diện tích | DRC | LVS |
|---|---|---|---|---|
| INV_X1 | 1,08 × 2,76 µm | 2,98 µm² | 0 lỗi | Match |
| NAND2_X1 | 1,62 × 2,76 µm | 4,47 µm² | 0 lỗi | Match |
| NOR2_X1 | 1,62 × 2,76 µm | 4,47 µm² | 0 lỗi | Match |
| NOR3_X1 | 2,16 × 2,76 µm | 5,96 µm² | 0 lỗi | Match |
| XOR2_X1 | 4,86 × 2,76 µm | 13,41 µm² | 0 lỗi | Match |
| XOR2_TG | 3,24 × 2,76 µm | 8,94 µm² | 0 lỗi | Match |
| XOR2_TG6 | 2,70 × 2,76 µm | 7,45 µm² | 0 lỗi | Match |
| XORTAP8 | 14,74 × 11,71 µm (cả vòng nguồn) | 28,3 µm² cell | 0 lỗi | Match |
| ZERO7 | 12,49 × 11,71 µm | 20,9 µm² cell | 0 lỗi | Match |
| CFSR_FB | 18,79 × 14,47 µm | 62,6 µm² cell | 0 lỗi | Match |

![Hình 3.1](layout/hinh/XOR2_TG6.png)
Hình 3.1. Layout XOR2_TG6 (6 transistor).

![Hình 3.2](layout/hinh/XOR2_X1.png)
Hình 3.2. Layout XOR2_X1 (CMOS 12 transistor).

![Hình 3.3](layout/hinh/CFSR_FB.png)
Hình 3.3. Layout khối CFSR_FB sau đặt và đi dây.

## 3.x.5 Kết luận phần

Phần TV3 đã xây dựng thư viện cổng INV, NAND2, NOR2, NOR3, ba cấu trúc XOR2 và khối hồi tiếp CFSR 8 bit với đủ
schematic, symbol, layout và view trích ký sinh; toàn bộ 12 cell và khối đạt DRC 0 lỗi, LVS khớp. So với bản dùng toàn
cổng CMOS, khối CFSR_FB đề xuất giảm 24 % transistor và 25 % diện tích, nhanh hơn 2 % và tốn ít hơn 7 % năng lượng,
đồng thời bảo đảm thanh ghi không kẹt ở trạng thái toàn 0. Hướng tiếp theo: ghép CFSR_FB với flip-flop TSPC của TV2
thành TSPC_LFSR_8bit và đo trễ trên đường hồi tiếp thực tế.

## Tài liệu tham khảo

[1] N. H. E. Weste and D. M. Harris, *CMOS VLSI Design: A Circuits and Systems Perspective*, 4th ed. Boston, MA, USA:
Addison-Wesley, 2011.
