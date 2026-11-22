# Khối Logic Đa hợp BILBO (`BILBO_Mux_Logic`) - Thư viện `QUOC_ANH_BILBO`

## 1. Các vấn đề thực hiện & Mục tiêu thiết kế

Dự án tập trung giải quyết bài toán thiết kế mạch tổ hợp điều khiển đầu vào cho một ô nhớ kiểm thử tự động **BILBO (Built-In Logic Block Observer)** theo phương pháp thiết kế phân cấp (Hierarchical Design) trên công cụ **Cadence Virtuoso** (`VDD = 1.0 V`)[cite: 2]:

* **Đa hợp 4 chế độ hoạt động trên cùng một ngõ ra ($D_{\text{OUT}}$):** Tích hợp logic chọn dữ liệu từ hai tín hiệu điều khiển $C_1, C_0$ để chuyển đổi linh hoạt giữa 4 chế độ: hoạt động bình thường (`Normal`), xóa đồng bộ (`Reset`), dịch nối tiếp (`Scan`) và phân tích chữ ký (`LFSR/MISR`).
* **Thiết kế phân cấp từ thư viện cổng chuẩn (Leaf Cells):** Tái sử dụng các cell cơ sở đã hoàn thiện đầy đủ các view (`schematic`, `symbol`, `layout`, `av_extracted`) gồm `INV_X1`, `NAND2_X1`, `NOR2_X1`, `XOR2_X1` để xây dựng khối `BILBO_Mux_Logic` và đóng gói thành khối `symbol` chuẩn hóa.
* **Kiểm chứng dạng sóng thời gian thực (Transient Analysis):** Đánh giá đáp ứng logic và biên độ điện áp ($0.0\text{ V} - 1.0\text{ V}$) qua mạch Testbench `tb_BILBO_Mux_Logic` trên trình mô phỏng **Cadence ADE L / Spectre** với đầy đủ tổ hợp đầu vào $(C_1, C_0, D_i, S_i)$.
* **Đóng gói & Bảo toàn dữ liệu giữa Linux và Windows:** Lưu trữ toàn bộ cấu trúc OpenAccess của thư viện `QUOC_ANH_BILBO` (dung lượng `86 KB`) và tệp ánh xạ `cds.lib` thành gói `QUOC_ANH_BILBO_backup.tar.gz` sạch khóa tạm thời (`.cdslck`).

---

## 2. Cấu trúc Thư viện (`QUOC_ANH_BILBO`)

```text
QUOC_ANH_BILBO/
├── INV_X1/                  # Cổng NOT (schematic, symbol, layout, av_extracted)
├── NAND2_X1/                # Cổng NAND 2 ngõ vào (schematic, symbol, layout, av_extracted)
├── NOR2_X1/                 # Cổng NOR 2 ngõ vào (schematic, symbol, layout, av_extracted)
├── XOR2_X1/                 # Cổng XOR 2 ngõ vào (schematic, symbol, layout, av_extracted)
├── BILBO_Mux_Logic/         # Khối logic điều khiển chính (schematic, symbol)
└── tb_BILBO_Mux_Logic/      # Mạch Testbench kiểm chứng 4 chế độ (schematic)
```

---

## 3. Thông số Các chân giao tiếp (Pinout) - `BILBO_Mux_Logic`

| Tên chân | Hướng | Kiểu chân (Pin Type) | Mức điện áp logic | Chức năng chi tiết |
| :--- | :---: | :---: | :---: | :--- |
| `C0` | Input | Signal | `0.0 V` (Logic `0`) / `1.0 V` (Logic `1`)[cite: 2] | Tín hiệu điều khiển chế độ bit thấp (LSB) |
| `C1` | Input | Signal | `0.0 V` (Logic `0`) / `1.0 V` (Logic `1`)[cite: 2] | Tín hiệu điều khiển chế độ bit cao (MSB) |
| `Di` | Input | Signal | `0.0 V` (Logic `0`) / `1.0 V` (Logic `1`)[cite: 2] | Ngõ vào dữ liệu song song (Parallel Data Input) |
| `Si` | Input | Signal | `0.0 V` (Logic `0`) / `1.0 V` (Logic `1`)[cite: 2] | Ngõ vào dịch nối tiếp / hồi tiếp (Serial Scan / Feedback Input) |
| `VDD` | Input / Power | Supply | `1.0 V`[cite: 2] | Nguồn nuôi dương toàn mạch |
| `GND` | Input / Ground | Supply | `0.0 V`[cite: 2] | Điểm tham chiếu mass chung |
| `D_OUT` | Output | Signal | `0.0 V` (Logic `0`) / `1.0 V` (Logic `1`)[cite: 2] | Ngõ ra logic tổ hợp đưa tới đầu vào `D` của D Flip-Flop |

---

## 4. Bảng chân trị & Biểu thức Logic hoạt động

| $C_1$ | $C_0$ | Tên chế độ | Biểu thức Logic ($D_{\text{OUT}}$) | Trạng thái hoạt động |
| :---: | :---: | :--- | :---: | :--- |
| `1` | `1` | **Normal Mode** | $D_i$ | Truyền thẳng dữ liệu song song $D_i$ ra ngõ ra $D_{\text{OUT}}$[cite: 2]. |
| `1` | `0` | **Reset Mode** | `0` | Ép ngõ ra $D_{\text{OUT}}$ về mức `0` (`0.0 V`) để khởi tạo trạng thái[cite: 2]. |
| `0` | `1` | **Test Mode (LFSR / MISR)** | $D_i \oplus \overline{S_i}$ | Trộn dữ liệu $D_i$ với bit hồi tiếp đảo $\overline{S_i}$ để tạo chuỗi giả ngẫu nhiên hoặc nén chữ ký[cite: 2]. |
| `0` | `0` | **Scan Mode** | $\overline{S_i}$ | Cấu hình thanh ghi dịch nối tiếp có đảo pha giữa các tầng từ ngõ vào $S_i$[cite: 2]. |

---

## 5. Thông số Thiết lập & Kết quả Mô phỏng (Cadence ADE L / Spectre)

### 5.1. Thông số kích thích đầu vào (Testbench `tb_BILBO_Mux_Logic`)
* **Nguồn nuôi & Tải:** $V_{\text{DD}} = 1.0\text{ V}$, $V_{\text{GND}} = 0.0\text{ V}$[cite: 2], tụ tải ngõ ra $C_L = 10\text{ fF}$.
* **Thời gian mô phỏng Transient:** $0\text{ ns} \rightarrow 160\text{ ns}$ (thời gian sườn lên/xuống xung $t_r = t_f = 50\text{ ps}$).
* **Tín hiệu điều khiển $(C_1, C_0)$:** Thay đổi tuần tự theo 4 khung thời gian, mỗi chế độ kéo dài $40\text{ ns}$.
* **Tín hiệu dữ liệu $(D_i, S_i)$:** Quét qua đủ 4 tổ hợp nhị phân $(00, 01, 10, 11)$ trong mỗi chu kỳ $40\text{ ns}$ (chu kỳ $D_i = 20\text{ ns}$, độ rộng xung $10\text{ ns}$; chu kỳ $S_i = 10\text{ ns}$, độ rộng xung $5\text{ ns}$).

### 5.2. Bảng số liệu Kết quả Mô phỏng Chi tiết theo Thời gian

| Khoảng thời gian | Trạng thái $(C_1, C_0)$ | Chế độ | Ngõ vào $(D_i, S_i)$ | Điện áp $V(D_{\text{OUT}})$ đo được | Mức logic $D_{\text{OUT}}$ | Kết quả đối chiếu lý thuyết |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **`0 ns – 10 ns`** | `(1.0 V, 1.0 V)` | Normal | `(0 V, 0 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = D_i = 0$) |
| **`10 ns – 20 ns`** | `(1.0 V, 1.0 V)` | Normal | `(0 V, 1.0 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = D_i = 0$) |
| **`20 ns – 30 ns`** | `(1.0 V, 1.0 V)` | Normal | `(1.0 V, 0 V)` | `1.00 V` | `1` | Đạt ($D_{\text{OUT}} = D_i = 1$) |
| **`30 ns – 40 ns`** | `(1.0 V, 1.0 V)` | Normal | `(1.0 V, 1.0 V)` | `1.00 V` | `1` | Đạt ($D_{\text{OUT}} = D_i = 1$) |
| **`40 ns – 80 ns`** | `(1.0 V, 0.0 V)` | Reset | Mọi tổ hợp | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = 0$ ổn định) |
| **`80 ns – 90 ns`** | `(0.0 V, 1.0 V)` | Test (LFSR/MISR) | `(0 V, 0 V)` | `1.00 V` | `1` | Đạt ($0 \oplus \overline{0} = 1$) |
| **`90 ns – 100 ns`** | `(0.0 V, 1.0 V)` | Test (LFSR/MISR) | `(0 V, 1.0 V)` | `0.00 V` | `0` | Đạt ($0 \oplus \overline{1} = 0$) |
| **`100 ns – 110 ns`** | `(0.0 V, 1.0 V)` | Test (LFSR/MISR) | `(1.0 V, 0 V)` | `0.00 V` | `0` | Đạt ($1 \oplus \overline{0} = 0$) |
| **`110 ns – 120 ns`** | `(0.0 V, 1.0 V)` | Test (LFSR/MISR) | `(1.0 V, 1.0 V)` | `1.00 V` | `1` | Đạt ($1 \oplus \overline{1} = 1$) |
| **`120 ns – 130 ns`** | `(0.0 V, 0.0 V)` | Scan | `(0 V, 0 V)` | `1.00 V` | `1` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 1$) |
| **`130 ns – 140 ns`** | `(0.0 V, 0.0 V)` | Scan | `(0 V, 1.0 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 0$) |
| **`140 ns – 150 ns`** | `(0.0 V, 0.0 V)` | Scan | `(1.0 V, 0 V)` | `1.00 V` | `1` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 1$) |
| **`150 ns – 160 ns`** | `(0.0 V, 0.0 V)` | Scan | `(1.0 V, 1.0 V)` | `0.00 V` | `0` | Đạt ($D_{\text{OUT}} = \overline{S_i} = 0$) |

### 5.3. Đánh giá chất lượng tín hiệu
* **Biên độ logic (Rail-to-Rail Swing):** Mức cao đạt chuẩn $V_{\text{OH}} = 1.00\text{ V}$ và mức thấp đạt chuẩn $V_{\text{OL}} = 0.00\text{ V}$, không xảy ra suy giảm ngưỡng điện áp ($V_t$ drop) ở cả 4 chế độ.
* **Độ ổn định chuyển mạch:** Không xuất hiện xung nhiễu (glitch) hay trạng thái lơ lửng (high-Z) tại các điểm chuyển giao chế độ ($t = 40\text{ ns}, 80\text{ ns}, 120\text{ ns}$).