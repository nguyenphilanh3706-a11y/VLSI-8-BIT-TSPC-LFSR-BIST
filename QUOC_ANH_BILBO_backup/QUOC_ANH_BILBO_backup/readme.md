# BÁO CÁO TỔNG HỢP TIẾN ĐỘ & KẾT QUẢ KỸ THUẬT (TUẦN 1 & TUẦN 2)
**Phân hệ:** Điều khiển Đa chế độ BILBO & Nén chữ ký MISR (`QUOC_ANH_BILBO`)  
**Người thực hiện:** Thành viên 5 — Lê Công Quốc Anh  
**Công nghệ & Công cụ:** CMOS 90nm (`gpdk090`, $V_{\text{DD}} = 1.2\text{ V}$) — Cadence Virtuoso IC 6.1.5 (Schematic, ADE L / Spectre)

---

## PHẦN I. TỔNG QUAN CÁC ĐẦU VIỆC ĐÃ HOÀN THÀNH TRONG 2 TUẦN

| Tuần | Mục tiêu kỹ thuật | Các cellview đã xây dựng trong `QUOC_ANH_BILBO` | Trạng thái nghiệm thu |
| :---: | :--- | :--- | :---: |
| **Tuần 1** | Thiết kế và kiểm chứng mạch tổ hợp điều khiển đa chế độ BILBO đơn bit. | • `BILBO_Mux_Logic` (`schematic`, `symbol`)<br>• `tb_BILBO_Mux_Logic` (`schematic`) | **Đạt 100%** (`0 errors`) |
| **Tuần 2** | Tích hợp thanh ghi đa năng 8-bit `BILBO_8BIT` hoàn chỉnh và chạy mô phỏng chuyển đổi tuần tự 4 chế độ. | • `BILBO_CELL` (`schematic`, `symbol`)<br>• `BILBO_8BIT` (`schematic`, `symbol`)<br>• `tb_BILBO_8BIT` (`schematic`) | **Đạt 100%** (`0 errors`) |

---

## PHẦN II. CHI TIẾT CẤU TRÚC MẠCH & NGUYÊN LÝ HOẠT ĐỘNG ĐÃ THIẾT KẾ

### 1. Kiến trúc phân cấp từ Cell đơn bit đến Thanh ghi 8-bit (`BILBO_8BIT`)
Qua sơ đồ nguyên lý `BILBO_8BIT` đã vẽ trên Cadence Virtuoso, hệ thống được cấu thành từ **3 thành phần cốt lõi**:

1. **8 tầng ô nhớ đa năng `BILBO_CELL` (`I0` đến `I7`):**
   * Mỗi cell `BILBO_CELL` kết hợp khối logic đa hợp điều khiển chế độ (`BILBO_Mux_Logic`) với 1 tầng D Flip-Flop kích cạnh lên (`CLK`) có ngõ vào đặt lại (`RST`).
   * **Giao tiếp từng tầng:** Nhận chung cặp tín hiệu chọn chế độ `C0, C1`, xung nhịp `CLK`, `RST`, nguồn `VDD`/`GND`, dữ liệu song song `Di` (`D0`–`D7`), dữ liệu dịch nối tiếp `Si`, và xuất ra cặp ngõ ra thuận/đảo `Q`, `QB` (các chân `QB` không dùng được gắn linh kiện `noConn` chuẩn quy tắc thiết kế).
   * **Chuỗi dịch tầng (Shift Chain):** Ngõ ra `Q` của tầng trước nối trực tiếp vào ngõ vào dịch nối tiếp `Si` của tầng kế tiếp theo chuỗi:
     $$S_0 \rightarrow I_0(Q_0) \rightarrow I_1(Q_1) \rightarrow I_2(Q_2) \rightarrow I_3(Q_3) \rightarrow I_4(Q_4) \rightarrow I_5(Q_5) \rightarrow I_6(Q_6) \rightarrow I_7(Q_7)$$

2. **Mạng cổng hồi tiếp XOR đa thức cực đại (`I8`, `I9`, `I10`):**
   * Sử dụng 3 cổng `XOR2_X1` mắc nối tiếp để thực hiện hàm hồi tiếp tuyến tính bậc 8 theo đa thức đặc trưng $P(x) = 1 + x^1 + x^6 + x^7 + x^8$:
     * Cổng `I8`: thực hiện $Q_0 \oplus Q_5$
     * Cổng `I9`: thực hiện $(Q_0 \oplus Q_5) \oplus Q_6$
     * Cổng `I10`: thực hiện $((Q_0 \oplus Q_5) \oplus Q_6) \oplus Q_7 = S_0$
   * Tín hiệu tổng hợp `S0` từ ngõ ra của `I10` được đưa ngược về chân `Si` của tầng đầu tiên `I0`.

3. **Hệ thống chân giao tiếp (Pins) của khối `BILBO_8BIT`:**
   * **Ngõ vào điều khiển & nhịp:** `C0`, `C1`, `CLK`, `RST` (Input).
   * **Ngõ vào dữ liệu song song:** `D0, D1, D2, D3, D4, D5, D6, D7` (Input).
   * **Ngõ ra trạng thái / chữ ký:** `Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7` (Output).
   * **Nguồn nuôi:** `VDD` ($1.2\text{ V}$), `GND` ($0.0\text{ V}$).

### 2. Bảng chuyển đổi 4 chế độ hoạt động theo $C[1:0]$

| $C_1$ | $C_0$ | Tên chế độ | Phương trình trạng thái kế tiếp $Q_i^+$ | Cơ chế vận hành của `BILBO_8BIT` |
| :---: | :---: | :--- | :---: | :--- |
| `1` | `0` | **Reset Mode** | $0$ | Ép đồng bộ toàn bộ 8 bit $Q[7:0]$ về mức `0` (`0.0 V`) tại sườn lên xung nhịp `CLK`. |
| `1` | `1` | **Normal Mode** | $D_i$ | Hoạt động như thanh ghi chốt song song 8-bit thông thường, nạp trực tiếp bus `D[7:0]` ra `Q[7:0]`. |
| `0` | `0` | **Scan Mode** | $\overline{S_i}$ | Cấu hình thanh ghi dịch nối tiếp 8-bit có đảo pha giữa các tầng, phục vụ quét đọc/ghi chuỗi kiểm thử. |
| `0` | `1` | **Test Mode (MISR / PRSG)** | $D_i \oplus \overline{S_i}$ | Kết hợp vòng hồi tiếp XOR tại `S0` với dữ liệu đầu vào `D[7:0]` để nén dữ liệu thành chữ ký 8-bit (MISR) hoặc sinh chuỗi giả ngẫu nhiên (PRSG). |

---

## PHẦN III. THIẾT LẬP MÔ PHỎNG SPECTRE (ADE L) ĐÃ CHẠY

### 1. Thông số môi trường & Bộ giải (Simulator Log)
* **Trình mô phỏng:** Cadence Spectre (khởi chạy từ Virtuoso ADE L trên `tb_BILBO_8BIT schematic`).
* **Thư viện mô hình linh kiện:** `gpdk090.scs` (CMOS 90nm), nhiệt độ mô phỏng chuẩn $T = 27^\circ\text{C}$.
* **Loại phân tích:** Transient Analysis (`tran`), `Stop Time = 40n` (mở rộng khảo sát tới `45n`), mức chính xác `errpreset = moderate`, phương pháp tích phân `method = traponly`.
* **Hiệu năng giải mạch thực tế (trích từ Spectre Output Log):**
  * Tổng số bước thời gian hội tụ thành công (*Number of accepted tran steps*): **2088 steps**.
  * Thời gian giải bài toán DC ban đầu (*Initial condition solution time*): **105.983 ms**.
  * Tổng thời gian chạy phân tích Transient (*Total time required for tran analysis*): **4.19036 s**.
  * Bộ nhớ sử dụng đỉnh (*Peak resident memory used*): **50 Mbytes**.
  * Trạng thái kiểm tra mạch & mô phỏng: **0 errors**.

### 2. Cấu hình nguồn kích thích trên Testbench (`tb_BILBO_8BIT`)
* **Nguồn nuôi toàn mạch (`VDC`):** $V_{\text{DD}} = 1.2\text{ V}$, tham chiếu mass toàn cục `gnd!` ($0.0\text{ V}$).
* **Xung nhịp đồng bộ (`CLK`):** Xung vuông chu kỳ $T_{\text{CLK}} = 2.0\text{ ns}$ (tần số $f = 500\text{ MHz}$), độ rộng xung mức cao $1.0\text{ ns}$, biên độ $0.0\text{ V} \leftrightarrow 1.2\text{ V}$.
* **Tín hiệu Reset ban đầu (`RST`):** Mức cao $1.2\text{ V}$ từ $0\text{ ns} \rightarrow 5.0\text{ ns}$, sau đó hạ xuống mức thấp $0.0\text{ V}$ từ $5.0\text{ ns} \rightarrow 40.0\text{ ns}$.
* **Mẫu dữ liệu song song cố định (`D[7:0]`):** Thiết lập mẫu xen kẽ `8'b10101010`:
  * Các bit lẻ `D1, D3, D5, D7` nối mức logic `1` ($1.2\text{ V}$).
  * Các bit chẵn `D0, D2, D4, D6` nối mức logic `0` ($0.0\text{ V}$).
* **Kịch bản quét 4 chế độ của cặp tín hiệu `(C1, C0)` (mỗi chế độ dài $10\text{ ns}$):**
  * **`0.0 ns – 10.0 ns`:** `C1 = 1.2 V` (`1`), `C0 = 0.0 V` (`0`) $\rightarrow$ **Reset Mode**.
  * **`10.0 ns – 20.0 ns`:** `C1 = 1.2 V` (`1`), `C0 = 1.2 V` (`1`) $\rightarrow$ **Normal Mode**.
  * **`20.0 ns – 30.0 ns`:** `C1 = 0.0 V` (`0`), `C0 = 0.0 V` (`0`) $\rightarrow$ **Scan Mode**.
  * **`30.0 ns – 40.0 ns`:** `C1 = 0.0 V` (`0`), `C0 = 1.2 V` (`1`) $\rightarrow$ **Test / MISR Mode**.

---

## PHẦN IV. BẢNG THÔNG SỐ & KẾT QUẢ MÔ PHỎNG ĐẠT ĐƯỢC

### 1. Bảng kết quả kiểm chứng Cell đơn bit `BILBO_Mux_Logic` (Tuần 1 — `0 ns` đến `160 ns`)

| Khoảng thời gian | $(C_1, C_0)$ | Chế độ | Ngõ vào $(D_i, S_i)$ | Điện áp đo $V(D_{\text{OUT}})$ | Mức logic | Đối chiếu lý thuyết |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| `0 ns – 10 ns` | `(1, 1)` | Normal | `(1, 1)` | `1.20 V` | `1` | Đạt ($D_{\text{OUT}} = D_i = 1$) |
| `10 ns – 20 ns` | `(1, 1)` | Normal | `(0, 1)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = D_i = 0$) |
| `20 ns – 30 ns` | `(1, 1)` | Normal | `(1, 0)` | `1.20 V` | `1` | Đạt ($D_{\text{OUT}} = D_i = 1$) |
| `30 ns – 40 ns` | `(1, 1)` | Normal | `(0, 0)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = D_i = 0$) |
| `40 ns – 80 ns` | `(1, 0)` | Reset | Mọi tổ hợp | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = 0$ ổn định) |
| `80 ns – 90 ns` | `(0, 1)` | Test/MISR | `(1, 1)` | `1.20 V` | `1` | Đạt ($1 \oplus \overline{1} = 1$) |
| `90 ns – 100 ns` | `(0, 1)` | Test/MISR | `(0, 1)` | `0.00 V` | `0` | Đạt ($0 \oplus \overline{1} = 0$) |
| `100 ns – 110 ns` | `(0, 1)` | Test/MISR | `(1, 0)` | `0.00 V` | `0` | Đạt ($1 \oplus \overline{0} = 0$) |
| `110 ns – 120 ns` | `(0, 1)` | Test/MISR | `(0, 0)` | `1.20 V` | `1` | Đạt ($0 \oplus \overline{0} = 1$) |
| `120 ns – 140 ns` | `(0, 0)` | Scan | `(X, 1)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 0$) |
| `140 ns – 160 ns` | `(0, 0)` | Scan | `(X, 0)` | `1.20 V` | `1` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 1$) |

### 2. Bảng kết quả kiểm chứng Thanh ghi `BILBO_8BIT` (Tuần 2 — `0 ns` đến `40 ns` trên ViVA)

| Khung thời gian | Mã chế độ $(C_1, C_0)$ | Chế độ hoạt động | Diễn biến dạng sóng đo được trên 8 kênh ngõ ra `Q[7:0]` | Trạng thái nhị phân $Q[7:0]$ | Đánh giá |
| :---: | :---: | :--- | :--- | :---: | :---: |
| **`0.0 ns – 10.0 ns`** | `(1, 0)` | **Reset Mode** | Cả 8 đường `Q0` đến `Q7` giữ ổn định ở mức điện áp `0.00 V`, hoàn toàn không bị ảnh hưởng bởi dữ liệu vào `D[7:0] = 10101010`. | `00000000` | **Đạt 100%** |
| **`10.0 ns – 20.0 ns`** | `(1, 1)` | **Normal Mode** | Ngay tại sườn lên xung nhịp `CLK` ở $t = 12.0\text{ ns}$, các kênh lẻ `Q1, Q3, Q5, Q7` chuyển lên `1.20 V`, trong khi các kênh chẵn `Q0, Q2, Q4, Q6` giữ `0.00 V` cho tới hết $20.0\text{ ns}$. | `10101010` | **Đạt 100%** |
| **`20.0 ns – 30.0 ns`** | `(0, 0)` | **Scan Mode** | Sau mỗi sườn lên `CLK` ($22\text{ ns}, 24\text{ ns}, 26\text{ ns}, 28\text{ ns}$), bit trạng thái dịch tuần tự kèm đảo pha qua từng tầng Flip-Flop, tạo hiệu ứng bậc thang dịch bit lan truyền rõ nét từ `Q0` $\rightarrow$ `Q1` $\rightarrow$ `Q2` $\rightarrow$ `Q3` $\rightarrow$ `Q4`. | Dịch nối tiếp từng chu kỳ | **Đạt 100%** |
| **`30.0 ns – 40.0 ns`** | `(0, 1)` | **Test Mode (MISR)** | Vòng hồi tiếp XOR đa thức cực đại trộn dữ liệu `D[7:0]` với trạng thái hiện tại, khiến toàn bộ 8 bit `Q0`–`Q7` biến thiên liên tục tạo chuỗi mã chữ ký nén qua các sườn lên clock ($32\text{ ns}, 34\text{ ns}, 36\text{ ns}, 38\text{ ns}$). | Nén chữ ký liên tục | **Đạt 100%** |

### 3. Tổng hợp các chỉ tiêu chất lượng điện học đạt được
* **Biên độ logic đầy đủ (Full Rail-to-Rail Swing):** Điện áp ngõ ra mức cao đạt chuẩn $V_{\text{OH}} = 1.20\text{ V}$ và mức thấp đạt chuẩn $V_{\text{OL}} = 0.00\text{ V}$ trên tất cả các kênh `Q0`–`Q7` tại tần số xung nhịp $500\text{ MHz}$, không xảy ra suy giảm điện áp ngưỡng ($V_t$ drop).
* **Độ tin cậy định thời:** Các ngõ ra `Q[7:0]` chốt trạng thái chính xác ngay sau cạnh lên của xung nhịp `CLK`, không xuất hiện hiện tượng treo trạng thái (high-Z) hay xung nhiễu giả làm sai lệch trạng thái các tầng Flip-Flop kế tiếp.
* **Sẵn sàng chuyển giao:** Khối `BILBO_8BIT` (`symbol`) đã hoàn thiện 100% về mặt nguyên lý và mô phỏng chức năng, sẵn sàng bàn giao cho Thành viên 6 tích hợp vào hệ thống BIST tổng thể và chuyển sang giai đoạn thiết kế Layout XL (DRC/LVS) ở Tuần 3.