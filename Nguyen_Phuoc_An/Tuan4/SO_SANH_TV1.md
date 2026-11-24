# Bảng A: so sánh MS-DFF (TV1) với TSPC R/S (TV2)

Nguyễn Phước An (TV2) · gpdk090, VDD = 1,2 V, NN 27 °C · Trước layout (TV1 chưa có layout) · Cùng một testbench cho cả ba cell.

## 1. Cách đo

- **MS-DFF:** `MS_DFF_SetReset` của TV1, đọc từ schematic trong thư viện `VLSI_TV1` (26 transistor: 4 cổng NOR, 4 cổng truyền, 1 inverter ra). Clock đảo CLKB lấy từ một inverter 2 transistor ngoài cell, cấp nguồn riêng, như testbench của TV1.
- **TSPC R/S:** netlist ở `../cells/`.
- **Tải:** Q có tải FO4 (4 inverter INV_X1). **QB của TSPC và Q̄ của MS-DFF để hở.** Lý do: QB của TSPC là nút động bên trong cell, chỉ có keeper yếu giữ, nên tải ở QB làm chậm cả đường ra (R, NN, Q lên: 54,0 ps khi chỉ tải Q 5 fF, 64,0 ps khi chỉ tải QB 5 fF, 89,2 ps khi tải cả hai). Trong sử dụng chỉ Q có tải.
- **Điều kiện chung:** cạnh clock 50 ps, T = 2 ns (setup, t_pcq), 4 mẫu D (công suất), `as/ad/ps/pd` thêm cho mọi transistor theo W × 0,28 µm. Giá trị này trùng với CDF trong schematic của TV1.
- **Vì sao phải thêm `as/ad`:** thiếu các tham số này mô hình dùng diện tích tiếp giáp mặc định (lớn), nên mạch chậm và tốn công suất hơn. Số trong Tuần 1–2 của TV2 đo không có `as/ad` và có tải FO4 trên cả QB, nên chậm hơn số ở bảng này (R, NN: t_pcq lên 75,9 ps so với 45,9 ps).
- **Kiểm tra với số của TV1:** TV1 báo t_pcq 67,4 ps (lên) và 88,4 ps (xuống) ở NN với tải 5 fF. Đo lại MS-DFF với `as/ad` và tải 5 fF cho 65,9 và 87,0 ps, lệch dưới 1,5 ps. Hai bộ số khớp khi dùng cùng điều kiện.

## 2. Bảng A

TSPC so với MS-DFF: số âm là TSPC tốt hơn.

| | R | S | MS-DFF | R so với MS | S so với MS |
|---|---|---|---|---|---|
| Số transistor | 15 | 15 | 26 (+2 inverter clock) | −42% | −42% |
| Tổng W×L cổng (µm²) | 0,600 | 0,600 | 1,128 | −47% | −47% |
| Số pha clock | 1 | 1 | 2 | | |
| Chức năng 11/11 (NN, SS, FF) | đúng | đúng | đúng | | |
| t_pcq lên, NN (ps) | 45,9 | 47,3 | 60,0 | −24% | −21% |
| t_pcq xuống, NN (ps) | 50,3 | 61,4 | 79,1 | −36% | −22% |
| t_pcq lên, SS (ps) | 62,8 | 65,0 | 83,0 | −24% | −22% |
| t_pcq xuống, SS (ps) | 70,7 | 87,7 | 109,1 | −35% | −20% |
| t_pcq lên, FF (ps) | 36,4 | 37,6 | 47,7 | −24% | −21% |
| t_pcq xuống, FF (ps) | 39,0 | 47,2 | 62,9 | −38% | −25% |
| Setup xấu nhất, NN (ps) | 20 | 20 | 50 | −60% | −60% |
| Setup xấu nhất, SS (ps) | 30 | 30 | 70 | −57% | −57% |
| Setup xấu nhất, FF (ps) | 20 | 20 | 50 | −60% | −60% |
| t_su để t_pcq tăng không quá 10%, NN / SS / FF (ps) | 30 / 40 / 30 | 30 / 40 / 30 | 70 / 100 / 60 | −57 / −60 / −50% | −57 / −60 / −50% |
| T_min bộ chia 2, D từ QB, NN (ps) | 90 | 110 | 160 | −44% | −31% |
| T_min bộ chia 2, D từ QB, SS (ps) | 120 | 140 | 220 | −45% | −36% |
| T_min bộ chia 2, D từ QB, FF (ps) | 80 | 90 | 120 | −33% | −25% |
| T_min bộ chia 2, D từ Q qua inverter, NN (ps) | 90 | 100 | 180 | −50% | −44% |
| T_min bộ chia 2, D từ Q qua inverter, SS (ps) | 120 | 120 | 250 | −52% | −52% |
| T_min bộ chia 2, D từ Q qua inverter, FF (ps) | 80 | 80 | 140 | −43% | −43% |

Setup lấy giá trị xấu nhất của D lên và D xuống (ngưỡng chốt). Với MS-DFF, D lên là xấu nhất.

**Công suất** (NN, 27 °C; MS-DFF = cell + inverter clock cấp nguồn riêng):

| Mẫu D | f | R (µW) | S (µW) | MS-DFF cell + inverter clock (µW) | MS-DFF tổng (µW) | R so với MS | S so với MS |
|---|---|---|---|---|---|---|---|
| ngẫu nhiên | 500 MHz | 2,38 | 2,33 | 1,89 + 0,68 | 2,57 | −7% | −9% |
| ngẫu nhiên | 1 GHz | 4,51 | 4,43 | 3,43 + 1,35 | 4,78 | −6% | −7% |
| 0101 | 1 GHz | 12,03 | 12,26 | 23,01 + 1,37 | 24,38 | −51% | −50% |
| toàn 0 | 1 GHz | 6,91 | 6,69 | 0,47 + 1,33 | 1,80 | +284% | +272% |
| toàn 1 | 1 GHz | 0,27 | 0,22 | 0,30 + 1,35 | 1,65 | −84% | −87% |

## 3. Đọc bảng

- **Số transistor và diện tích cổng:** TSPC dùng 15 transistor so với 26 (28 nếu tính inverter clock, −46%). Tổng W×L cổng bằng 53% của MS-DFF. Đây là diện tích cổng, **không phải diện tích layout**; TV1 chưa vẽ layout nên chưa có số so sánh. Layout của R và S là 23,96 và 22,08 µm².
- **t_pcq:** với Q có tải và QB để hở, TSPC nhanh hơn MS-DFF ở cả chuyển lên và xuống, ở cả ba góc (R nhanh hơn 24 đến 38%, S nhanh hơn 20 đến 25%).
- **Setup:** cửa sổ lấy mẫu của TSPC hẹp hơn (20 đến 30 ps so với 50 đến 70 ps).
- **Tần số:** T_min của bộ chia 2 nhỏ hơn MS-DFF 25 đến 52%.
- **Công suất:** phụ thuộc mạnh vào dữ liệu. Với D ngẫu nhiên, TSPC thấp hơn 6 đến 9%. Với D = 0101, TSPC thấp hơn khoảng một nửa. Với D toàn 0, MS-DFF ít hơn nhiều (1,80 so với 6,9 µW). Với D toàn 1, TSPC ít hơn. Số công suất của MS-DFF phải cộng inverter clock (khoảng 28% tổng ở 1 GHz với D ngẫu nhiên).
- **Giới hạn của phép so sánh:**
  - Chỉ trước layout.
  - Chưa có `as/ad` lấy từ layout; so sánh dùng giá trị W × 0,28 µm cho cả ba cell.
  - TSPC chỉ có Q làm ngõ ra có tải. Nếu mạch cần cả Q và Q̄ thì phải thêm một inverter ở Q, và t_pcq sẽ tăng.
  - Với tải FO4 trên cả hai ngõ ra thì chênh lệch t_pcq nhỏ hơn nhiều (R, NN: 67,5 / 64,0 ps; S: 69,0 / 83,5 ps; MS-DFF: 59,7 / 78,9 ps), lúc đó MS-DFF nhanh hơn ở chuyển lên.

## 4. Tình trạng phần của TV1 (đã kiểm tra trong thư viện `VLSI_TV1`)

- Có: schematic `MS_DFF_SetReset` (26 transistor) và các cell con `NOR`, `TG`, `INV_QB`; testbench; báo cáo số liệu.
- Chưa có: layout (view rỗng), DRC/LVS, RCX, mô phỏng sau layout; Chương 2; đường t_pcq theo setup; số ở góc SS, FF.
- Con số "diện tích" trong báo cáo của TV1 là tổng W×L cổng, không phải diện tích layout.
- Các câu trong README về "tối đa 13 transistor" và "tiết kiệm 44% diện tích" không khớp: cell hiện tại có 26 transistor.
