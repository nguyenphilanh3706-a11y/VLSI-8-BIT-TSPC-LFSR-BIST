# Kết quả Tuần 4: Ma trận PVT 45 điểm trên netlist sau layout (TSPC D Flip-Flop R và S)

Người thực hiện: Nguyễn Phước An (TV2). Công nghệ gpdk090, Spectre. Netlist: trích RC từ layout (`../Tuan3/layout/TSPC_DFF_R_rcx.scs`, `TSPC_DFF_S_rcx.scs`). Tải: 4 × `INV_X1` (FO4) ở Q (và QB ở testbench chức năng). Hai cell × 45 điểm = 90 điểm; mỗi điểm chạy đủ ba phép đo dưới đây.

## 1. Ma trận và phép đo

- **Góc:** NN, SS, FF, FS, SF (section của `gpdk090.scs`).
- **VDD:** 0,8 / 1,0 / 1,2 V. **Nhiệt độ:** 0 / 27 / 125 °C.
- **Chức năng:** testbench 11 vector của Tuần 3 (T = 2 ns, cạnh 50 ps), biên độ D, RST/SET và clock theo VDD. Đạt khi cả 11 vector đúng và Q cách rail không quá 10% VDD khi lấy mẫu.
- **t_pcq:** trễ clock → Q ở ngưỡng 50% VDD, lấy giá trị lớn hơn trong hai hướng (Q lên, Q xuống) trên testbench trên.
- **T_min (f_max):** bộ chia 2 (Q → `INV_X1` → D, clock 50%, cạnh 20 ps, 19 chu kỳ kiểm tra). Dãy T khảo sát: 4000, 3000, 2000, 1500, 1000, 700, 500, 400, 300, 250, 220, 200, 180, 160, 150, 140, 130, 120, 110, 100, 90, 80 ps; T_min là giá trị nhỏ nhất còn đúng, tìm bằng chia đôi (giả định đúng ở T lớn thì đúng ở mọi T lớn hơn). Độ phân giải bằng bước của dãy.

## 2. Bảng B

Mỗi ô ghi **t_pcq (ps) / T_min (ps)**. Ô có "FAIL" là chức năng sai; trong bảng dưới không có ô nào như vậy.

### Cell R (`TSPC_DFF_R`)

| Góc | VDD (V) | 0 °C | 27 °C | 125 °C |
|---|---|---|---|---|
| NN | 0,8 | 112,8 / 200 | 123,3 / 220 | 172,2 / 300 |
| NN | 1,0 | 82,9 / 140 | 91,4 / 150 | 128,2 / 220 |
| NN | 1,2 | 68,6 / 110 | 75,9 / 130 | 106,2 / 180 |
| SS | 0,8 | 163,0 / 300 | 181,4 / 400 | 259,9 / 500 |
| SS | 1,0 | 117,2 / 200 | 130,3 / 220 | 188,0 / 400 |
| SS | 1,2 | 94,4 / 160 | 105,8 / 180 | 152,7 / 250 |
| FF | 0,8 | 85,8 / 140 | 92,9 / 160 | 126,6 / 220 |
| FF | 1,0 | 64,6 / 110 | 70,9 / 120 | 96,6 / 160 |
| FF | 1,2 | 54,8 / 90 | 60,0 / 100 | 81,5 / 130 |
| FS | 0,8 | 112,7 / 200 | 122,7 / 220 | 162,1 / 300 |
| FS | 1,0 | 81,4 / 140 | 89,0 / 160 | 119,0 / 220 |
| FS | 1,2 | 65,9 / 120 | 72,2 / 130 | 96,9 / 180 |
| SF | 0,8 | 147,5 / 250 | 164,8 / 300 | 236,8 / 400 |
| SF | 1,0 | 105,0 / 160 | 117,5 / 180 | 169,0 / 300 |
| SF | 1,2 | 85,1 / 130 | 95,0 / 150 | 136,1 / 220 |

### Cell S (`TSPC_DFF_S`)

| Góc | VDD (V) | 0 °C | 27 °C | 125 °C |
|---|---|---|---|---|
| NN | 0,8 | 153,8 / 200 | 167,4 / 220 | 220,3 / 300 |
| NN | 1,0 | 109,7 / 140 | 120,0 / 150 | 159,7 / 200 |
| NN | 1,2 | 88,9 / 110 | 97,4 / 130 | 129,8 / 180 |
| SS | 0,8 | 226,8 / 300 | 248,8 / 400 | 333,9 / 500 |
| SS | 1,0 | 158,1 / 200 | 174,3 / 220 | 237,1 / 300 |
| SS | 1,2 | 125,8 / 160 | 138,9 / 180 | 189,5 / 250 |
| FF | 0,8 | 115,1 / 150 | 124,4 / 160 | 160,4 / 200 |
| FF | 1,0 | 83,7 / 110 | 90,9 / 120 | 118,4 / 150 |
| FF | 1,2 | 69,1 / 100 | 75,1 / 100 | 97,8 / 130 |
| FS | 0,8 | 169,7 / 220 | 184,8 / 250 | 241,5 / 400 |
| FS | 1,0 | 117,4 / 150 | 128,5 / 180 | 170,7 / 220 |
| FS | 1,2 | 92,9 / 120 | 101,8 / 130 | 135,7 / 180 |
| SF | 0,8 | 164,3 / 250 | 180,1 / 300 | 246,9 / 400 |
| SF | 1,0 | 118,2 / 160 | 130,0 / 180 | 176,5 / 300 |
| SF | 1,2 | 96,2 / 130 | 105,9 / 140 | 143,5 / 220 |

## 3. Tổng hợp

| | R | S |
|---|---|---|
| Chức năng | 45/45 điểm đúng | 45/45 điểm đúng |
| t_pcq nhỏ nhất | 54,8 ps (FF, 1,2 V, 0 °C) | 69,1 ps (FF, 1,2 V, 0 °C) |
| t_pcq lớn nhất | 259,9 ps (SS, 0,8 V, 125 °C) | 333,9 ps (SS, 0,8 V, 125 °C) |
| T_min nhỏ nhất | 90 ps (11,1 GHz; FF, 1,2 V, 0 °C) | 100 ps (10 GHz; FF, 1,2 V, 27 °C và 0 °C) |
| T_min lớn nhất | 500 ps (2,0 GHz; SS, 0,8 V, 125 °C) | 500 ps (2,0 GHz; SS, 0,8 V, 125 °C) |

- t_pcq và T_min đều tăng khi VDD giảm và khi nhiệt độ tăng, ở mọi góc. Góc xấu nhất là SS, 0,8 V, 125 °C; góc tốt nhất là FF, 1,2 V, 0 °C.
- Ở 1,2 V và 27 °C, kết quả NN khớp Tuần 3 (R: 75,9 ps so với 75,7 ps; S: 97,4 ps so với 97,3 ps).
- Ở mọi điều kiện, t_pcq của FS và SF nằm giữa t_pcq của FF và SS cùng VDD, nhiệt độ; không góc nào làm sai chức năng.

## 4. Giới hạn của phép đo

- Chức năng chỉ đo ở T = 2 ns (500 MHz); T_min dùng bộ chia 2 một cell, không phải chuỗi nhiều FF.
- Không đo hold/race trong chuỗi dịch, glitch, charge sharing và f_min ở 45 điểm này (chuỗi 8 FF chỉ đo ở 3 góc, 1,2 V, 27 °C trong Tuần 3).
- Phép tìm T_min bằng chia đôi cho một giá trị mỗi điểm; không kiểm tra tính đơn điệu ở từng điểm.
- Không có mô hình biến thiên cục bộ (Monte Carlo).
