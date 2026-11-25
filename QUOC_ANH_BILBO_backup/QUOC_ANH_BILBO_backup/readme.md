# Khối Logic Đa hợp BILBO (`BILBO_Mux_Logic`) - Thư viện `QUOC_ANH_BILBO`

## 1. Mục tiêu & Phạm vi Thiết kế (Phân hệ Thành viên 5)

Dự án thuộc đề tài **Hệ thống 8-bit TSPC-LFSR kết hợp BIST** trên công nghệ **CMOS 90nm (`gpdk090`, $V_{\text{DD}} = 1.2\text{ V}$)**, công cụ **Cadence Virtuoso IC 6.1.5**[cite: 6]. Khối **`BILBO_Mux_Logic`** giải quyết bài toán điều khiển đa chế độ cho ô nhớ kiểm thử tự động **BILBO (Built-In Logic Block Observer)** theo kiến trúc chuẩn của giáo trình *CMOS VLSI Design* (Weste & Harris, Hình 15.20)[cite: 6]:

* **Đa hợp 4 chế độ hoạt động trên cùng một ngõ ra ($D_{\text{OUT}}$):** Chuyển đổi linh hoạt giữa 4 chế độ hoạt động bằng hai tín hiệu điều khiển $C_1, C_0$ (`Normal`, `Reset`, `Test/MISR`, `Scan`)[cite: 6].
* **Thiết kế phân cấp (Hierarchical Design):** Xây dựng khối `BILBO_Mux_Logic` từ thư viện cổng chuẩn (`INV_X1`, `NAND2_X1`, `NOR2_X1`, `XOR2_X1`) và đóng gói thành khối `symbol` sẵn sàng ghép nối với D Flip-Flop (`TSPC_DFF_SetReset` / `MS_DFF_SetReset`) thành thanh ghi `BILBO_8bit`[cite: 6].
* **Kiểm chứng dạng sóng thời gian thực (Transient Analysis):** Đánh giá đáp ứng logic và biên độ điện áp chuẩn công nghệ ($0.0\text{ V} - 1.2\text{ V}$) qua mạch Testbench `tb_BILBO_Mux_Logic` trên trình mô phỏng **Cadence ADE L / Spectre**[cite: 5, 6].

---

## 2. Cấu trúc Thư viện (`QUOC_ANH_BILBO`)

```text
QUOC_ANH_BILBO/
├── INV_X1/                  # Cổng NOT (schematic, symbol, layout, av_extracted)
├── NAND2_X1/                # Cổng NAND 2 ngõ vào (schematic, symbol, layout, av_extracted)
├── NOR2_X1/                 # Cổng NOR 2 ngõ vào (schematic, symbol, layout, av_extracted)
├── XOR2_X1/                 # Cổng XOR 2 ngõ vào (schematic, symbol, layout, av_extracted)
├── BILBO_Mux_Logic/         # Khối logic điều khiển 4 chế độ chính (schematic, symbol)
└── tb_BILBO_Mux_Logic/      # Mạch Testbench kiểm chứng 4 chế độ ở VDD = 1.2 V (schematic)
```

---

## 3. Thông số Các chân giao tiếp (Pinout) - `BILBO_Mux_Logic`

| Tên chân | Hướng | Kiểu chân (Pin Type) | Mức điện áp logic (`gpdk090`) | Chức năng chi tiết |
| :--- | :---: | :---: | :---: | :--- |
| `C0` | Input | Signal | `0.0 V` (Logic `0`) / `1.2 V` (Logic `1`)[cite: 5, 6] | Tín hiệu điều khiển chế độ bit thấp (LSB) |
| `C1` | Input | Signal | `0.0 V` (Logic `0`) / `1.2 V` (Logic `1`)[cite: 5, 6] | Tín hiệu điều khiển chế độ bit cao (MSB) |
| `Di` | Input | Signal | `0.0 V` (Logic `0`) / `1.2 V` (Logic `1`)[cite: 5, 6] | Ngõ vào dữ liệu song song (Parallel Data Input) |
| `Si` | Input | Signal | `0.0 V` (Logic `0`) / `1.2 V` (Logic `1`)[cite: 5, 6] | Ngõ vào dịch nối tiếp / hồi tiếp (Serial Scan / Feedback Input) |
| `VDD` | Input / Power | Supply | `1.2 V`[cite: 6] | Nguồn nuôi dương toàn mạch |
| `GND` | Input / Ground | Supply | `0.0 V` | Điểm tham chiếu mass chung |
| `D_OUT` (`net2`) | Output | Signal | `0.0 V` (Logic `0`) / `1.2 V` (Logic `1`)[cite: 5] | Ngõ ra logic tổ hợp đưa tới đầu vào `D` của D Flip-Flop |

---

## 4. Bảng chân trị & Biểu thức Logic hoạt động (Chuẩn Weste & Harris)

| $C_1$ | $C_0$ | Tên chế độ | Biểu thức Logic ($D_{\text{OUT}}$) | Trạng thái hoạt động |
| :---: | :---: | :--- | :---: | :--- |
| `1` | `1` | **Normal Mode** | $D_i$ | Truyền thẳng dữ liệu song song $D_i$ ra ngõ ra $D_{\text{OUT}}$. |
| `1` | `0` | **Reset Mode** | `0` | Ép ngõ ra $D_{\text{OUT}}$ về mức `0` (`0.0 V`) để khởi tạo trạng thái đồng bộ. |
| `0` | `1` | **Test Mode (LFSR / MISR)** | $D_i \oplus \overline{S_i}$ | Trộn dữ liệu $D_i$ với bit hồi tiếp đảo $\overline{S_i}$ để tạo chuỗi giả ngẫu nhiên hoặc nén chữ ký. |
| `0` | `0` | **Scan Mode** | $\overline{S_i}$ | Cấu hình thanh ghi dịch nối tiếp có đảo pha giữa các tầng từ ngõ vào $S_i$. |

---

## 5. Thông số Thiết lập & Kết quả Mô phỏng (Cadence ADE L / Spectre)

### 5.1. Thông số kích thích đầu vào (`tb_BILBO_Mux_Logic`)
* **Công nghệ & Nguồn nuôi:** PDK `gpdk090`, $V_{\text{DD}} = 1.2\text{ V}$, $V_{\text{GND}} = 0.0\text{ V}$[cite: 5, 6].
* **Thời gian mô phỏng Transient:** $0\text{ ns} \rightarrow 160\text{ ns}$ (`no error`)[cite: 5].
* **Tín hiệu điều khiển $(C_1, C_0)$:** Thay đổi tuần tự theo 4 khung thời gian, mỗi chế độ kéo dài $40\text{ ns}$[cite: 5].
* **Tín hiệu dữ liệu $(D_i, S_i)$:** Quét qua đủ 4 tổ hợp nhị phân $(11, 01, 10, 00)$ trong mỗi chu kỳ $40\text{ ns}$ (chu kỳ $D_i = 20\text{ ns}$, độ rộng xung $10\text{ ns}$; chu kỳ $S_i = 40\text{ ns}$, độ rộng xung $20\text{ ns}$)[cite: 5].

### 5.2. Bảng số liệu Kết quả Mô phỏng Chi tiết theo Thời gian (`VDD = 1.2 V`)

| Khoảng thời gian | Trạng thái $(C_1, C_0)$ | Chế độ | Ngõ vào $(D_i, S_i)$ | Điện áp $V(D_{\text{OUT}})$ đo được | Mức logic $D_{\text{OUT}}$ | Kết quả đối chiếu lý thuyết |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **`0 ns – 10 ns`** | `(1.2 V, 1.2 V)` | Normal | `(1.2 V, 1.2 V)` | `1.20 V` | `1` | Đạt ($D_{\text{OUT}} = D_i = 1$)[cite: 5] |
| **`10 ns – 20 ns`** | `(1.2 V, 1.2 V)` | Normal | `(0.0 V, 1.2 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = D_i = 0$)[cite: 5] |
| **`20 ns – 30 ns`** | `(1.2 V, 1.2 V)` | Normal | `(1.2 V, 0.0 V)` | `1.20 V` | `1` | Đạt ($D_{\text{OUT}} = D_i = 1$)[cite: 5] |
| **`30 ns – 40 ns`** | `(1.2 V, 1.2 V)` | Normal | `(0.0 V, 0.0 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = D_i = 0$)[cite: 5] |
| **`40 ns – 80 ns`** | `(1.2 V, 0.0 V)` | Reset | Mọi tổ hợp | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = 0$ ổn định)[cite: 5] |
| **`80 ns – 90 ns`** | `(0.0 V, 1.2 V)` | Test (LFSR/MISR) | `(1.2 V, 1.2 V)` | `1.20 V` | `1` | Đạt ($1 \oplus \overline{1} = 1$)[cite: 5] |
| **`90 ns – 100 ns`** | `(0.0 V, 1.2 V)` | Test (LFSR/MISR) | `(0.0 V, 1.2 V)` | `0.00 V` | `0` | Đạt ($0 \oplus \overline{1} = 0$)[cite: 5] |
| **`100 ns – 110 ns`** | `(0.0 V, 1.2 V)` | Test (LFSR/MISR) | `(1.2 V, 0.0 V)` | `0.00 V` | `0` | Đạt ($1 \oplus \overline{0} = 0$)[cite: 5] |
| **`110 ns – 120 ns`** | `(0.0 V, 1.2 V)` | Test (LFSR/MISR) | `(0.0 V, 0.0 V)` | `1.20 V` | `1` | Đạt ($0 \oplus \overline{0} = 1$)[cite: 5] |
| **`120 ns – 140 ns`** | `(0.0 V, 0.0 V)` | Scan | `(X, 1.2 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 0$)[cite: 5] |
| **`140 ns – 160 ns`** | `(0.0 V, 0.0 V)` | Scan | `(X, 0.0 V)` | `1.20 V` | `1` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 1$)[cite: 5] |

### 5.3. Đánh giá chất lượng tín hiệu
* **Biên độ logic (Rail-to-Rail Swing):** Mức cao đạt chuẩn $V_{\text{OH}} = 1.20\text{ V}$ và mức thấp đạt chuẩn $V_{\text{OL}} = 0.00\text{ V}$, không xảy ra suy giảm ngưỡng điện áp ($V_t$ drop) ở cả 4 chế độ[cite: 5].
* **Độ ổn định chuyển mạch:** Mạch hoạt động ổn định, không xuất hiện trạng thái lơ lửng (high-Z); xung nhiễu chuyển tiếp (glitch) tại thời điểm chuyển chế độ $t = 40\text{ ns}$ có biên độ thấp ($\approx 0.45\text{ V} < V_{\text{DD}}/2$), nằm dưới ngưỡng chuyển mạch của tầng D Flip-Flop kế tiếp[cite: 5].