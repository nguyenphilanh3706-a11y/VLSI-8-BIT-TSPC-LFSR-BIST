# Báo cáo sơ bộ: TSPC D Flip-Flop có Reset và Set

Nguyễn Phước An (TV2) · Công nghệ gpdk090 (90 nm), VDD = 1,2 V · Cadence Virtuoso IC6.1.5, Spectre · Trạng thái: **trước layout** (netlist và schematic)

(Bản PDF `BAO_CAO_SO_BO_TV2.pdf` có thêm các hình chụp schematic từ Virtuoso và symbol.)

## 1. Mục tiêu và kết quả chính

Thiết kế flip-flop D kích cạnh lên kiểu TSPC (true single-phase clock) với một chân điều khiển bất đồng bộ, để dùng làm phần tử nhớ của LFSR/BILBO: `TSPC_DFF_R` (Reset, Q = 0) và `TSPC_DFF_S` (Set, Q = 1). Mỗi cell dùng một pha clock duy nhất, không cần clock đảo.

- Mỗi cell có **15 transistor** (gồm 2 keeper), schematic và symbol hoàn chỉnh trong thư viện `TV2_TSPC`, `schCheck` không lỗi, đã đối chiếu từng transistor với netlist mô phỏng.
- Chức năng: cả sáu lần chạy (R và S, mỗi cell ở góc NN, SS, FF) **PASS 11/11 vector**.
- Độ trễ clock đến Q ở góc danh định: 82,6 / 92,7 ps (cell R, Q lên / xuống). Công suất 1 GHz với dữ liệu ngẫu nhiên: 9,6 µW. Tần số hoạt động tối đa khoảng 6,8 GHz (NN).
- Giữ dữ liệu hơn 20 µs khi clock dừng, ở cả FF 125 °C và NN 27 °C.

## 2. Thiết kế

### 2.1. Cấu trúc bốn tầng

Cell R gồm bốn tầng nối tiếp, chỉ có ba nút động X, Y, QB:

| Tầng | Vai trò | Transistor | Nút ra |
|---|---|---|---|
| 1 | Nửa chốt P: đảo D khi CLK = 0 | M1, M2 (PMOS), M3 (NMOS) | X = D̄ |
| 2 | N-precharge: precharge Y lên VDD khi CLK = 0, lấy mẫu X khi CLK = 1; có Reset bất đồng bộ | M6, MRP (PMOS); M4, M5, MRN (NMOS) | Y = D |
| 3 | N-C²MOS: đảo Y ra QB khi CLK = 1 | M9 (PMOS); M7, M8 (NMOS) | QB = D̄ |
| 4 | Inverter ngõ ra có đệm | MP, MN | Q = D |
| K | Keeper giữ các nút động | MKQ (QB), MKY (Y): PMOS yếu, kênh dài | – |

Nguyên lý: khi CLK = 0, tầng 1 chốt X = D̄ và tầng 2 precharge Y lên 1. Khi CLK lên 1, nếu X = 1 thì chuỗi M4–M5 xả Y về 0, nếu X = 0 thì Y giữ 1; tầng 3 và 4 truyền giá trị đó ra Q. Dữ liệu chỉ được lấy mẫu tại cạnh lên của CLK. Chân Reset (RST = 1) ép Y về 0 qua MRN và chặn precharge qua MRP, nên Q = 0 bất kể CLK.

**Cell S** giống cell R nhưng tầng 2 không có Reset (M6 nối thẳng VDD), và tầng 3 thêm MSP (PMOS, cổng SET, nối tiếp M9) cùng MSN (NMOS, cổng SET, kéo QB xuống GND): khi SET = 1, QB = 0 nên Q = 1.

### 2.2. Kích thước linh kiện (L = 100 nm trừ keeper)

| Transistor | Loại | W | Nối (D, G, S) |
|---|---|---|---|
| M1 | PMOS | 480 nm | pa, D, VDD |
| M2 | PMOS | 480 nm | X, CLK, pa |
| M3 | NMOS | 240 nm | X, D, GND |
| MRP (chỉ cell R) | PMOS | 480 nm | pm, RST, VDD |
| M6 | PMOS | 480 nm | Y, CLK, pm (cell S: Y, CLK, VDD) |
| M4 | NMOS | 480 nm | Y, X, n4 |
| M5 | NMOS | 480 nm | n4, CLK, GND |
| MRN (chỉ cell R) | NMOS | 240 nm | Y, RST, GND |
| M9 | PMOS | 480 nm | QB, Y, VDD (cell S: QB, Y, ps) |
| MSP (chỉ cell S) | PMOS | 480 nm | ps, SET, VDD |
| M7 | NMOS | 240 nm | QB, CLK, n7 |
| M8 | NMOS | 240 nm | n7, Y, GND |
| MSN (chỉ cell S) | NMOS | 240 nm | QB, SET, GND |
| MP | PMOS | 480 nm | Q, QB, VDD |
| MN | NMOS | 240 nm | Q, QB, GND |
| MKQ | PMOS | 120 nm, L = 400 nm | QB, Q, VDD |
| MKY | PMOS | 120 nm, L = 400 nm | Y, QB, VDD |

Tỉ lệ k = W(M4, M5) / W(M7, M8) = 2. Thứ tự chân subckt: cell R `D CLK RST Q QB VDD GND`; cell S `D CLK SET Q QB VDD GND`.

### 2.3. Sơ đồ nguyên lý

Các hình chụp từ Virtuoso Schematic Editor (thư viện `TV2_TSPC`, cell `TSPC_DFF_R` và `TSPC_DFF_S`) nằm trong bản PDF của báo cáo. Mỗi transistor trong hình có tên, loại linh kiện, W, L và tên net ở các chân (drain, gate, source; thân nối `VDD` với PMOS và `GND` với NMOS). Hàng PMOS nằm trên, hàng NMOS nằm dưới. Bảng 2.2 và netlist 2.4 ghi đầy đủ cùng thông tin dạng văn bản.

### 2.4. Netlist

Thứ tự nút là (drain gate source bulk).

Cell R (`cells/TSPC_DFF_R/TSPC_DFF_R.scs`):

```
// TSPC_DFF_R: Reset bat dong bo (RST=1 -> Q=0). 15 transistor (gom 2 keeper).
subckt TSPC_DFF_R D CLK RST Q QB VDD GND
    // tang 1: nua P-latch (X = !D khi CLK=0)
    M1  (pa D VDD VDD)   gpdk090_pmos1v w=480n l=100n
    M2  (X CLK pa VDD)   gpdk090_pmos1v w=480n l=100n
    M3  (X D GND GND)    gpdk090_nmos1v w=240n l=100n
    // tang 2: N-precharge + Reset (Y = D)
    MRP (pm RST VDD VDD) gpdk090_pmos1v w=480n l=100n
    M6  (Y CLK pm VDD)   gpdk090_pmos1v w=480n l=100n
    M4  (Y X n4 GND)     gpdk090_nmos1v w=480n l=100n
    M5  (n4 CLK GND GND) gpdk090_nmos1v w=480n l=100n
    MRN (Y RST GND GND)  gpdk090_nmos1v w=240n l=100n
    // tang 3: N-C2MOS (QB = !D)
    M9  (QB Y VDD VDD)   gpdk090_pmos1v w=480n l=100n
    M7  (QB CLK n7 GND)  gpdk090_nmos1v w=240n l=100n
    M8  (n7 Y GND GND)   gpdk090_nmos1v w=240n l=100n
    // tang 4: inverter ra (Q = D)
    MP  (Q QB VDD VDD)   gpdk090_pmos1v w=480n l=100n
    MN  (Q QB GND GND)   gpdk090_nmos1v w=240n l=100n
    // keeper yeu: giu QB va Y khi clock dung
    MKQ (QB Q VDD VDD)   gpdk090_pmos1v w=120n l=400n
    MKY (Y QB VDD VDD)   gpdk090_pmos1v w=120n l=400n
ends TSPC_DFF_R
```

Cell S (`cells/TSPC_DFF_S/TSPC_DFF_S.scs`):

```
// TSPC_DFF_S: Set bat dong bo (SET=1 -> Q=1). 15 transistor (gom 2 keeper).
// QUY TAC: phai nha SET khi CLK=0.
subckt TSPC_DFF_S D CLK SET Q QB VDD GND
    M1  (pa D VDD VDD)   gpdk090_pmos1v w=480n l=100n
    M2  (X CLK pa VDD)   gpdk090_pmos1v w=480n l=100n
    M3  (X D GND GND)    gpdk090_nmos1v w=240n l=100n
    M6  (Y CLK VDD VDD)  gpdk090_pmos1v w=480n l=100n
    M4  (Y X n4 GND)     gpdk090_nmos1v w=480n l=100n
    M5  (n4 CLK GND GND) gpdk090_nmos1v w=480n l=100n
    MSP (ps SET VDD VDD) gpdk090_pmos1v w=480n l=100n
    M9  (QB Y ps VDD)    gpdk090_pmos1v w=480n l=100n
    M7  (QB CLK n7 GND)  gpdk090_nmos1v w=240n l=100n
    M8  (n7 Y GND GND)   gpdk090_nmos1v w=240n l=100n
    MSN (QB SET GND GND) gpdk090_nmos1v w=240n l=100n
    MP  (Q QB VDD VDD)   gpdk090_pmos1v w=480n l=100n
    MN  (Q QB GND GND)   gpdk090_nmos1v w=240n l=100n
    // keeper yeu: giu QB va Y khi clock dung
    MKQ (QB Q VDD VDD)   gpdk090_pmos1v w=120n l=400n
    MKY (Y QB VDD VDD)   gpdk090_pmos1v w=120n l=400n
ends TSPC_DFF_S
```

### 2.5. Các quyết định thiết kế và lý do

- **Thứ tự stack tầng 3: M7 (cổng CLK) nối sát QB, M8 (cổng Y) nối phía GND.** Nút giữa n7 nằm sau transistor CLK nên không chia sẻ điện tích với QB khi CLK đổi; QB không bị tụt (1 mV, −3 mV, 2 mV ở NN, SS, FF).
- **PMOS precharge tầng 2 (M6) có cổng nối CLK.** Y chỉ được precharge theo CLK, nên D đổi khi CLK = 1 không làm Q đổi theo; dữ liệu chỉ được lấy mẫu tại cạnh lên.
- **Hai keeper MKQ, MKY** (PMOS W = 120 nm, L = 400 nm, đủ yếu để không cản việc chuyển trạng thái) giữ hai nút động QB và Y khi clock dừng hoặc chậm. Nhờ đó dữ liệu được giữ hơn 20 µs và chuỗi 8 FF đúng với cạnh clock tới 300 ps.
- **Tỉ lệ k = W(M4, M5) / W(M7, M8) = 2** (480 nm / 240 nm): cân bằng giữa tốc độ Q xuống (92,7 ps) và tải lên đường clock của M5; Q lên 82,6 ps.

## 3. Kiểm tra chức năng

| Hạng mục | Kết quả |
|---|---|
| 11 vector, Reset/Set ở cả hai pha clock, CLK 500 MHz, tải FO4 ở Q và QB | **PASS 11/11** cho cell R và cell S ở NN, SS, FF |
| Glitch tĩnh ở Q (cell R, cửa sổ đã ổn định) | mức thấp ≤ 2 mV; mức cao ≥ 1199 mV (cả ba góc) |
| Glitch khi D = 0 lặp lại qua cạnh clock (cell R) | 12–13 mV (khoảng 1% VDD) ở NN, SS, FF |
| VDD từ 1,2 xuống 0,7 V (một FF, cell R) | đúng 21/21 ở NN, SS, FF |
| Chuỗi 8 FF, clock lý tưởng | đúng 18/18 với cạnh 100–300 ps ở NN, SS, FF; cạnh 400 ps: sai ở FF (14/18) |
| Chuỗi 8 FF, clock qua đệm 2 tầng (độ dốc 20–80% khoảng 30–53 ps) | đúng 18/18 ở 1 và 2 GHz, ba góc |
| Giữ dữ liệu khi clock dừng 20 µs (R và S; FF 125 °C và NN 27 °C; D = 0 và 1; clock dừng thấp và cao) | 16/16 điều kiện giữ đúng Q |

## 4. Đặc tính (trước layout)

Tải FO4 (4 × INV_X1) ở Q và QB, clock vuông 50 ps trực tiếp (trừ khi ghi khác), ngưỡng 50%.

### 4.1. Trễ clock đến Q (t_pcq) và setup

| Hạng mục | Cell | NN | SS | FF |
|---|---|---|---|---|
| t_pcq Q lên / Q xuống (ps) | R | 82,6 / 92,7 | 115,5 / 130,1 | 65,0 / 72,2 |
| t_pcq Q lên / Q xuống (ps) | S | 88,3 / 121,0 | 123,9 / 172,9 | 69,3 / 93,1 |
| Setup, D xuống (xấu nhất) (ps) | R | 30 | 50 | 30 |
| Setup, D xuống (xấu nhất) (ps) | S | 30 | 50 | 30 |
| Setup, D lên (ps) | R | −10 | −20 | −10 |
| Setup, D lên (ps) | S | −10 | −10 | −10 |

Setup đo bằng cách quét thời điểm D quanh cạnh lên thứ hai (bước 10 ps, độ dốc D 50 ps); setup = −d*, hold ≈ d* (d* là thời điểm D muộn nhất so với cạnh clock mà vẫn được chốt). Cả 12 phép quét đều đơn điệu.

### 4.2. Tần số hoạt động tối đa

| Cell | NN | SS | FF |
|---|---|---|---|
| R | khoảng 6,8 GHz | khoảng 4,8 GHz | khoảng 8,5 GHz |
| S | khoảng 6,3 GHz | khoảng 4,5 GHz | khoảng 8,0 GHz |

Tiêu chí: 22 bit ngẫu nhiên được chốt đúng, Q hợp lệ trước cạnh kế tiếp, clock duty 50% cạnh 20 ps, D đổi ở giữa pha thấp. Giá trị là T nhỏ nhất vẫn đúng trong dãy khảo sát. Đây là giới hạn của một cell riêng lẻ ở điều kiện lý tưởng.

### 4.3. Công suất (NN, 27 °C, 1 GHz, gồm tải FO4)

| Dữ liệu D | Cell R (µW) | Cell S (µW) |
|---|---|---|
| Toàn 0 | 13,46 | 12,07 |
| Toàn 1 | 0,42 | 0,37 |
| Xen kẽ 0101 | 30,11 | 31,78 |
| Ngẫu nhiên | 9,62 | 9,28 |

Công suất theo tần số (cell R, dữ liệu ngẫu nhiên): 1,26 µW ở 100 MHz; 5,01 µW ở 500 MHz; 9,62 µW ở 1 GHz; 14,20 µW ở 1,5 GHz, gần tỉ lệ thuận với tần số. Công suất **phụ thuộc mạnh vào dữ liệu**: khi D = 0 nút Y được precharge rồi xả ở mọi chu kỳ, còn D = 1 liên tục gần như không tiêu thụ. Vì vậy mọi số công suất phải ghi rõ mẫu dữ liệu.

## 5. Giới hạn sử dụng và việc chưa làm

**Giới hạn khi dùng cell:**

- **Cell S:** chỉ nhả `SET` khi `CLK = 0`. Nhả lúc CLK = 1 làm Q tự lật về giá trị D và giá trị nạp sẵn bị mất (đã xác nhận bằng mô phỏng). Cell R: nhả `RST` lúc nào cũng được.
- **Độ dốc clock:** chuỗi 8 FF bị race (một bit đi qua hai tầng) khi cạnh clock chậm; ở góc FF với cạnh 400 ps chuỗi sai (14/18). Nên giữ cạnh clock không quá khoảng 200 ps, hoặc dùng đệm clock.
- **`QB` là nút động bên trong**, không dùng để lái tải; chỉ `Q` là ngõ ra có đệm.

**Chưa làm hoặc chưa đo:**

- Layout, DRC, LVS, trích ký sinh (PEX) và diện tích. Mọi số trong báo cáo là trước layout, số sau layout sẽ khác.
- Glitch tĩnh và quét VDD cho cell S (mới đo cho cell R); quét nhiệt độ ngoài phép đo giữ dữ liệu.
- Quét PVT đầy đủ.

## 6. Dữ liệu đi kèm

Thư mục `cells/`: netlist `TSPC_DFF_R.scs`, `TSPC_DFF_S.scs`, testbench chức năng và bảng kết quả mong đợi (`.exp`) ở ba góc NN, SS, FF, cùng inverter tải `INV_X1_tai.scs`. Số liệu chi tiết nằm trong `KET_QUA_TV2.md` (và `KET_QUA_TV2.pdf`). Chạy lại: vào thư mục cell rồi `spectre tb_TSPC_DFF_R.scs` (đường dẫn model gpdk090 trong testbench cần đổi theo máy).
