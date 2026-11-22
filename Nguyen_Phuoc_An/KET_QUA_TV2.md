# Kết quả đo đặc tính TV2: TSPC D Flip-Flop (R và S)

Người thực hiện: Nguyễn Phước An (TV2). Công nghệ gpdk090, VDD = 1,2 V, Spectre (MMSIM 12.1), **trước layout** (chưa có ký sinh).
Cell đo: `TSPC_DFF_R` (Reset) và `TSPC_DFF_S` (Set), **15 transistor mỗi cell**, gồm 2 keeper (`MKQ`, `MKY`); k = W(M4,M5)/W(M7,M8) = 2; stack tầng 3: M7 (cổng CLK) sát QB, M8 (cổng Y) phía GND.
Tải: Q và QB mỗi nút 4 × `INV_X1` (FO4). Nguồn clock: xung vuông đặt trực tiếp, không qua đệm, trừ khi ghi khác.
Dữ liệu trong repo: `cells/` (netlist, testbench NN/SS/FF). Các số đo nâng cao (t_pcq, setup/hold, công suất, f_max, f_min) do script đo riêng tạo ra; script không đưa vào repo.

## 0. Phạm vi và giới hạn

- Đây là số đo **pre-layout**. Netlist chưa có `ad/as` nên model dùng diện tích mặc định; số sau layout sẽ khác.
- Chưa đo diện tích. Chưa quét nhiệt độ ngoài f_min.
- Setup/hold, công suất, f_max, f_min đã đo cho **cả cell R và S**. Glitch tĩnh chỉ đo cho cell R.
- Độ phân giải quét setup/hold là 10 ps, độ dốc D là 50 ps. f_max là kết quả của một dãy 22 bit ngẫu nhiên (hạt giống cố định), nên chỉ phân biệt được tới một bước T trong bảng.

## 1. Chức năng và glitch

| Hạng mục | Kết quả |
|---|---|
| Testbench chức năng (11 vector, Reset/Set ở cả hai pha clock) | R và S: **PASS 11/11** ở NN, SS, FF |
| Glitch tĩnh ở Q, cell R (cửa sổ Q đã ổn định) | mức thấp tối đa 1–2 mV, mức cao tối thiểu 1199 mV ở NN, SS, FF |
| Glitch khi D = 0 lặp lại qua cạnh clock thứ hai (cell R) | **12–13 mV** (khoảng 1% VDD) ở NN, SS, FF |
| Sụt điện tích nút QB khi CLK xuống (cell R) | NN 1 mV; SS −3 mV; FF 2 mV: không sụt |

Ghi chú: cửa sổ đo phải bắt đầu sau khi Q đã chuyển xong. Ở góc SS, Q còn đang chuyển khoảng 175 ps sau cạnh clock.

## 2. Trễ clock → Q (t_pcq), nguồn clock dốc 50 ps, ngưỡng 50%

| Cell | Góc | Q lên (ps) | Q xuống (ps) |
|---|---|---|---|
| R | NN | 82,6 | 92,7 |
| R | SS | 115,5 | 130,1 |
| R | FF | 65,0 | 72,2 |
| S | NN | 88,3 | 121,0 |
| S | SS | 123,9 | 172,9 |
| S | FF | 69,3 | 93,1 |

## 3. Setup / hold (góc ghi trong bảng, 27 °C)

Cách đo: D chuyển một lần quanh cạnh lên thứ hai của clock, quét thời điểm D so với cạnh CLK (mốc 50%), d = −300 … +100 ps. Chốt đúng khi Q cuối bằng giá trị mới của D. Setup = −d*, hold ≈ d* (cùng một ngưỡng lấy mẫu, nhìn từ hai phía).

| Cell | Hướng D | Góc | t_pcq danh định (ps) | Ngưỡng chốt d* | **Setup** (ps) | tsu để t_CQ ≤ +10% (ps) |
|---|---|---|---|---|---|---|
| R | 0 → 1 | NN | 82,5 | +10 | −10 | 0 |
| R | 1 → 0 | NN | 92,5 | −30 | **+30** | 50 |
| R | 0 → 1 | SS | 115,3 | +20 | −20 | 0 |
| R | 1 → 0 | SS | 129,7 | −50 | **+50** | 70 |
| R | 0 → 1 | FF | 65,0 | +10 | −10 | 0 |
| R | 1 → 0 | FF | 72,1 | −30 | **+30** | 40 |
| S | 0 → 1 | NN | 88,3 | +10 | −10 | 0 |
| S | 1 → 0 | NN | 120,9 | −30 | **+30** | 50 |
| S | 0 → 1 | SS | 123,9 | +10 | −10 | 0 |
| S | 1 → 0 | SS | 172,6 | −50 | **+50** | 60 |
| S | 0 → 1 | FF | 69,3 | +10 | −10 | 10 |
| S | 1 → 0 | FF | 93,0 | −30 | **+30** | 40 |

Ghi chú:
- Ở cả 12 trường hợp, kết quả đơn điệu (không có vùng chốt xen kẽ).
- Setup xấu nhất là D xuống: **30 ps (NN, FF) và 50 ps (SS)** cho cả hai cell.
- Hold ≈ d* của hướng tương ứng: D lên khoảng +10 đến +20 ps, D xuống khoảng −30 đến −50 ps (tức hold âm khi D xuống).

## 4. Công suất (NN, 27 °C, VDD = 1,2 V)

Công suất trung bình nguồn VDD trong cửa sổ chu kỳ 5–20, **gồm cả dòng của tải FO4**. Mẫu D: toàn 0, toàn 1, 0101 (đổi mỗi chu kỳ), ngẫu nhiên (hạt giống cố định). Cạnh clock 50 ps.

**Cell R**

| Tần số | T | D toàn 0 (µW) | D toàn 1 (µW) | 0101 (µW) | Ngẫu nhiên (µW) |
|---|---|---|---|---|---|
| 100 MHz | 10 ns | 1,66 | 0,32 | 3,31 | 1,26 |
| 250 MHz | 4 ns | 3,66 | 0,34 | 7,80 | 2,67 |
| 500 MHz | 2 ns | 6,96 | 0,37 | 15,25 | 5,01 |
| 750 MHz | 1,333 ns | 10,23 | 0,40 | 22,69 | 7,32 |
| 1 GHz | 1 ns | 13,46 | 0,42 | 30,11 | 9,62 |
| 1,25 GHz | 0,8 ns | 16,68 | 0,43 | 37,53 | 11,92 |
| 1,5 GHz | 0,667 ns | 19,87 | 0,44 | 44,93 | 14,20 |

**Cell S**

| Tần số | T | D toàn 0 (µW) | D toàn 1 (µW) | 0101 (µW) | Ngẫu nhiên (µW) |
|---|---|---|---|---|---|
| 100 MHz | 10 ns | 1,55 | 0,27 | 3,46 | 1,21 |
| 250 MHz | 4 ns | 3,33 | 0,29 | 8,20 | 2,57 |
| 500 MHz | 2 ns | 6,27 | 0,33 | 16,07 | 4,82 |
| 750 MHz | 1,333 ns | 9,19 | 0,35 | 23,93 | 7,06 |
| 1 GHz | 1 ns | 12,07 | 0,37 | 31,78 | 9,28 |
| 1,25 GHz | 0,8 ns | 14,94 | 0,38 | 39,62 | 11,49 |
| 1,5 GHz | 0,667 ns | 17,78 | 0,40 | 47,44 | 13,69 |

Năng lượng mỗi chu kỳ ở 1 GHz (fJ = µW tại 1 GHz): cell R: toàn 0 = 13,5; toàn 1 = 0,42; 0101 = 30,1; ngẫu nhiên = 9,6. Cell S: 12,1; 0,37; 31,8; 9,3.

Nhận xét: công suất **phụ thuộc mạnh vào dữ liệu**. D = 1 liên tục gần như không tốn (Y đứng yên ở 1), D = 0 liên tục vẫn tốn vì Y precharge rồi xả ở mọi chu kỳ, và chuỗi 0101 tốn nhất. Khi báo cáo công suất phải nêu rõ mẫu dữ liệu.

## 5. Tần số hoạt động tối đa (f_max)

Tiêu chí: 22 bit ngẫu nhiên được chốt đúng, Q hợp lệ trước cạnh kế tiếp, clock duty 50%, cạnh 20 ps, D đổi ở giữa pha thấp (biên setup = 0,25 T). Tải FO4.

| Cell | Góc | Đúng ở (T nhỏ nhất đạt) | Sai ở (T kế tiếp) | f_max ước lượng |
|---|---|---|---|---|
| R | NN | 148 ps (6,8 GHz) | 143 ps (21/22) | khoảng 6,8 GHz |
| R | SS | 210 ps (4,8 GHz) | 200 ps (20/22) | khoảng 4,8 GHz |
| R | FF | 118 ps (8,5 GHz) | 111 ps (20/22) | khoảng 8,5 GHz |
| S | NN | 160 ps (6,3 GHz) | 154 ps (21/22) | khoảng 6,3 GHz |
| S | SS | 220 ps (4,5 GHz) | 210 ps (20/22) | khoảng 4,5 GHz |
| S | FF | 125 ps (8,0 GHz) | 118 ps (20/22) | khoảng 8,0 GHz |

Chỉ là giới hạn của một cell riêng lẻ trong điều kiện lý tưởng (clock vuông 20 ps, không đệm). Tần số của cả LFSR sẽ thấp hơn vì còn đường XOR hồi tiếp và tải thực.

## 6. Tần số hoạt động tối thiểu (f_min), clock bị dừng

Cell R và S, D cố định (0 hoặc 1), clock dừng ở mức thấp (kịch bản A) hoặc mức cao (kịch bản B) trong **20 µs**. Tiêu chí: Q còn đúng cuối 20 µs.

| Cell | Điều kiện | Kịch bản A (CLK thấp), D = 0 / 1 | Kịch bản B (CLK cao), D = 0 / 1 |
|---|---|---|---|
| R | FF, 125 °C | Q đúng / Q đúng (QB nổi lên 0,14 V) | Q đúng / Q đúng |
| R | NN, 27 °C | Q đúng / Q đúng (QB nổi lên 0,18 V) | Q đúng / Q đúng |
| S | FF, 125 °C | Q đúng / Q đúng (QB nổi lên 0,04 V) | Q đúng / Q đúng |
| S | NN, 27 °C | Q đúng / Q đúng (QB nổi lên 0,09 V) | Q đúng / Q đúng |

QB và Y đứng yên ở mức cuối (ví dụ QB 0,14–0,18 V, Y 1,18–1,20 V), cách xa ngưỡng đảo của inverter ngõ ra (khoảng 0,6 V). Cả 16 điều kiện giữ dữ liệu hơn 20 µs, tức **f_min dưới 50 kHz** (chưa thử dừng clock lâu hơn 20 µs).

## 7. Số transistor

| | TSPC_DFF_R | TSPC_DFF_S |
|---|---|---|
| Transistor | 15 | 15 |

Gồm các transistor của bốn tầng và 2 keeper (`MKQ`, `MKY`).

## 8. Kiểm tra bổ sung

Schematic đã được đối chiếu với netlist mô phỏng (khớp loại, chân, W, L từng transistor).

| Hạng mục | Kết quả |
|---|---|
| Chức năng R và S (NN, SS, FF) | PASS 11/11 cả sáu lần chạy |
| VDD 1,2 → 0,7 V, 1 FF, cell R (NN, SS, FF) | đúng 21/21 ở mọi điểm |
| Chuỗi 8 FF, clock lý tưởng, cạnh 100–300 ps | đúng 18/18 ở NN, SS, FF; cạnh 400 ps: NN, SS đúng, **FF sai (14/18)** |
| Chuỗi 8 FF, clock có đệm (20–80% khoảng 30–53 ps), 1 và 2 GHz | đúng 18/18 ở NN, SS, FF |
| S: nhả SET lúc CLK = 1 | **Q tự lật về 0** ngay sau khi nhả (D = 0 đã giữ sẵn ở tầng 2) |
| S: nhả SET lúc CLK = 0 | Q giữ 1 đến cạnh kế tiếp, đúng |

Giới hạn sử dụng:
- **Cell S:** chỉ nhả `SET` khi `CLK = 0`; nhả khi CLK = 1 làm giá trị nạp sẵn bị ghi đè bằng D. Cell R nhả `RST` lúc nào cũng được.
- **Độ dốc clock:** chuỗi 8 FF bị race khi cạnh clock chậm (FF, 400 ps sai), đúng như đặc điểm của TSPC (nút động, nhạy với độ dốc clock). Nên giữ cạnh clock không quá khoảng 200 ps hoặc dùng đệm clock.
- `QB` là nút động bên trong, không dùng để lái tải; chỉ `Q` là ngõ ra có đệm.

## 9. Việc còn lại

- Glitch tĩnh và quét VDD cho cell S; quét nhiệt độ ngoài f_min.
- Giới hạn f_min thực (clock dừng lâu hơn 20 µs) nếu cần một con số.
- Đo diện tích sau layout, PEX.
- Layout, DRC/LVS; quét PVT đầy đủ.
