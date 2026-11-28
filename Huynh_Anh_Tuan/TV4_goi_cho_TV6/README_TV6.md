# Gói bàn giao của TV4 cho TV6 (CUT, top BIST)

Người gửi: TV4 – Huỳnh Anh Tuấn. Ngày 28/11/2026. Công nghệ gpdk090, VDD 1,2 V, Cadence Virtuoso IC6.1.5.
Nguồn gốc: branch `module/LFSR-8BIT-PRPG(4)`, commit `365c199`. Gói này gồm đủ những gì cần để ghép khối bộ sinh mẫu (TPG) của TV4 vào hệ BIST.

Phần riêng cho TV5 (quy ước LFSR, chữ ký MISR theo `BILBO_8BIT`) nằm ở gói [`../TV4_goi_cho_TV5/`](../TV4_goi_cho_TV5/README_TV5.md); bảng chữ ký ở mục 5 dưới đây giống bên đó.

## 1. Trong gói có gì

| Thư mục | Nội dung | Dùng khi |
|---|---|---|
| `cadence/` | Thư viện Virtuoso `tv4` (schematic + symbol của 26 cell, 3 testbench) và `tv4_lay` (layout dải `TSPC_LFSR_8bit`). Cách mở: [`cadence/README.md`](cadence/README.md) | Ghép bằng schematic: *Create → Instance → Library `tv4`*, view `symbol` |
| `netlist/` | Netlist Spectre: `blocks/` (khối của TV4), `cells/`, `depend/` (cell TV1/TV2/TV3), `tb/` (testbench mẫu), `layout/rcx/` (netlist sau layout), `scripts/` (chạy và so với golden model) | Mô phỏng bằng netlist, hoặc tham khảo cách dựng testbench |
| `layout/` | `TSPC_LFSR_8bit.gds` (đã gồm các cell con), `.cdl` để chạy LVS, `_rcx.sp` (netlist RC trích ra), `dien_tich.json` | Ghép layout top BIST |
| `golden/` | Chuỗi giá trị chuẩn từ golden model, vector V[7:0] tới CUT và **chữ ký MISR chuẩn tính theo cấu trúc BILBO_8BIT của TV5** | So kết quả mô phỏng top BIST |
| `hinh/` | Ảnh chụp trực tiếp trong Virtuoso: symbol, schematic, layout (cell lá và dải), kết quả Assura, dạng sóng ViVA; thêm biểu đồ trễ theo PVT (`pvt_tre.png`) | Đưa vào báo cáo hoặc slide |

## 2. Khối để ghép

| Khối (thư viện `tv4`) | Chân, theo thứ tự subckt | Chức năng |
|---|---|---|
| **`TSPC_LFSR_8bit`** | `CLK RST Q0 Q1 Q2 Q3 Q4 Q5 Q6 Q7 VDD GND` | LFSR 8 bit, P(x) = 1 + x + x⁶ + x⁷ + x⁸, dịch Q0 → Q7, D0 = Q0 ⊕ Q5 ⊕ Q6 ⊕ Q7. Flip-flop TSPC của TV2, XOR của TV3. 144 transistor |
| **`LT_RTPG_8bit`** | `Q0..Q7 CLK RST LP V0..V7 VDD GND` | Nhận Q0..Q7 từ LFSR, xuất V0..V7 tới CUT. `LP = 0`: V = Q (255 vector khác nhau). `LP = 1`: chế độ ít chuyển mạch k = 2 (số bit lật giảm 50 %, 101 vector khác nhau). 362 transistor |

Cách nối đề xuất cho top BIST:

```
CLK, RST ──┬─────────────────────────────┬───────────────────────┐
           ▼                             ▼                       ▼
   TSPC_LFSR_8bit ──Q[7:0]──► LT_RTPG_8bit ──V[7:0]──► CUT (TV6) ──Z[4:0]──► BILBO_8BIT (TV5) D[4:0]
                                  ▲ LP                 A = V[3:0], B = V[7:4]     D[7:5] = 0, C1C0: 10 → 01
```

## 3. Quy tắc bắt buộc

| Quy tắc | Lý do |
|---|---|
| `RST = 1` thì LFSR nạp seed **0x01**, T-flip-flop của LT_RTPG về 0. **Chỉ nhả RST (1 → 0) khi CLK = 0** | Quy tắc của cell TSPC (TV2). Testbench của TV4 nhả RST ở giữa chu kỳ đầu (0,5T) |
| **Sườn clock ≤ 200 ps** | Với netlist TV2 có `as/ad`, TSPC sai từ sườn 300 ps. Testbench của TV4 cho clock qua 2 inverter `INV_CLK`; sườn đo tại chân CLK của `TSPC_LFSR_8bit` khoảng 85–95 ps (10–90 %). Cây clock của top BIST cần giữ sườn cỡ này hoặc nhanh hơn |
| Không nối tải vào chân `QB` của `TSPC_DFF_R/S` | `QB` là nút động bên trong cell |
| Tải đã kiểm tra: mỗi Q một INV_X1, mỗi V bốn INV_X1 | Tải CUT nặng hơn thì chạy lại để kiểm trễ |
| Một nguồn clock chung cho LFSR, LT_RTPG và BILBO; `LP` chỉ đổi khi RST = 1 hoặc giữa hai lần chạy | Tránh làm lệch chuỗi vector so với golden model |

## 4. Số liệu đã kiểm (500 MHz, 300 chu kỳ, so với golden model)

| Khối | Kết quả | Trễ CLK→ra lớn nhất NN / SS / FF | Công suất NN |
|---|---|---|---|
| `TSPC_LFSR_8bit` trước layout | 301/301 ở NN, SS, FF | 186,6 / 263,7 / 145,6 ps | P_DUT 63,5 µW, P_clock 24,0 µW |
| `TSPC_LFSR_8bit` sau layout (RCX) | 301/301 ở NN, SS, FF; PVT 27/27 điểm | 238,8 / 335,7 / 186,8 ps | 61,5 + 40,7 µW |
| `TSPC_LFSR_8bit` + `LT_RTPG_8bit`, LP = 0 | 301/301 ở NN, SS, FF | 315,6 / 446,1 / 246,3 ps | P_tải CUT 14,44 µW |
| `TSPC_LFSR_8bit` + `LT_RTPG_8bit`, LP = 1 | 301/301 ở NN, SS, FF | 269,4 / 380,2 / 210,3 ps | P_tải CUT 7,97 µW (**−44,8 %**) |

- Dải `TSPC_LFSR_8bit` sau layout đúng tới 2,63 GHz (NN) và 1,85 GHz (SS).
- Layout: 79,02 × 2,76 µm = 218,10 µm², một hàng, ray VDD/GND Metal1 dùng khuôn cell của TV3. Assura cho DRC 0 lỗi và LVS khớp.
- Chân ra ở Metal4: `CLK`, `RST`, `Q0..Q7`; nhãn nguồn `VDD`, `GND` ở Metal1.
- **`LT_RTPG_8bit` chưa có layout.** Kế hoạch tuần 3 chỉ yêu cầu dải LFSR; nếu top BIST cần thì báo TV4.

## 5. Chuỗi vector và chữ ký MISR chuẩn (`golden/`)

| File | Nội dung |
|---|---|
| `golden_lfsr_255.csv`, `.hex` | Q[7:0] ở từng chu kỳ (chu kỳ 0 = 0x01 ngay sau khi nhả RST), qua trọn 255 trạng thái |
| `golden_lfsr_300.csv` | 301 trạng thái cho testbench 300 cạnh clock |
| `golden_lt_rtpg_k2.csv` | V[7:0] khi LP = 1 |
| `golden_cfsr_256.csv` | Chuỗi 256 trạng thái của `TSPC_CFSR_8bit`, có trạng thái 0x00 |
| **`chu_ky_misr.csv`** | Chữ ký sau 255 chu kỳ khi không có lỗi và với 10 lỗi stuck-at ở ngõ ra CUT, cho 2 cấu trúc MISR và 2 cách lấy mẫu |
| **`vector_lfsr_cut_misr.csv`** | Từng cạnh clock: V, Z = V[3:0] + V[7:4], và giá trị MISR của `BILBO_8BIT` (TV5) ngay sau cạnh đó. Dùng để dò lỗi theo từng chu kỳ |
| `misr_bilbo_tv5.py` | Script tạo hai file trên (Python 3, không cần thư viện thêm). Đổi CUT hay cách nối thì sửa hàm `cut()` rồi chạy lại |
| `fault_dictionary.csv` | Từ golden model MATLAB của TV4 |

**Chữ ký chuẩn sau đúng 255 cạnh clock ở chế độ Test (C1C0 = 01)**, MISR reset về 0x00, CUT là bộ cộng 4 bit, Z → D4..D0, D7..D5 = 0:

| Cách lấy mẫu | LP = 0 | LP = 1 |
|---|---|---|
| **A** – MISR nhận Z của V(1)…V(255), tức MISR chậm hơn LFSR một chu kỳ (golden model TV4) | **0xDE** | **0x79** |
| **B** – LFSR và MISR reset và nhả cùng lúc; ở cạnh thứ t, MISR chốt Z của V(t−1), bắt đầu từ seed 0x01 | **0xEF** | **0x3C** |

- `BILBO_8BIT` của TV5 dùng `Q⁺ = D ⊕ ¬S`; sau đúng 255 chu kỳ chữ ký vẫn bằng golden model của TV4, chỉ giá trị trung gian khác (giải thích trong gói TV5). So từng chu kỳ theo cột `MISR_TV5_*` trong `vector_lfsr_cut_misr.csv` (cách B).
- Chọn **một** cách lấy mẫu (A hoặc B) cho top BIST rồi báo TV4. Với cả hai cấu trúc và cả hai cách, đủ 10/10 lỗi SA0/SA1 ở ngõ ra CUT đều làm chữ ký khác chữ ký đúng. Lưu ý: chạy đúng 255 chu kỳ thì SA0 và SA1 trên cùng một dây cho cùng chữ ký, nên phát hiện được lỗi nhưng không phân biệt được SA0 với SA1.
- Testbench chỉ chạy 40 ns thì mới được khoảng 5 chu kỳ ở chế độ Test, chưa so được chữ ký. Cần chạy ít nhất 255 chu kỳ: 510 ns ở 500 MHz, cộng thời gian reset.

## 6. Mô phỏng bằng netlist (trong máy ảo Cadence)

```bash
cd netlist
bash scripts/run_tv4.sh tb/tb_TSPC_LFSR_NN.scs      # LFSR: PASS 301/301, kèm trễ và công suất
bash scripts/run_tv4.sh tb/tb_LT_RTPG_LP1_NN.scs    # LFSR + LT-RTPG, LP = 1
```

- Thứ tự `include` có sẵn trong `tb/tb_*_NN.scs`: model gpdk090 → cell TV3 → XORTAP8/CFSR → cell TV2 → cell TV4 → `blocks/`.
- Đường dẫn model: `/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs`. Máy khác thì sửa dòng đầu của file corner.
- Dùng netlist sau layout của dải LFSR: include `layout/rcx/TSPC_LFSR_8bit_post.scs`, cùng chân với `TSPC_LFSR_8bit`. Xem `tb/tb_TSPC_LFSR_post_NN.scs`.

## 7. Liên hệ

Thay đổi khối, chân hay cấu trúc MISR/CUT thì báo TV4 để chạy lại golden model và cập nhật chữ ký chuẩn.
