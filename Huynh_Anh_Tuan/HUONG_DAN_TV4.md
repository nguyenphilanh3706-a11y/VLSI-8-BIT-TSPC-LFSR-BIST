# Hướng dẫn dùng phần việc của TV4

Dành cho các thành viên ghép khối của TV4 vào phần của mình (TV5, TV6) hoặc chạy lại kết quả. Tóm tắt kết quả: [KET_QUA_TV4.md](KET_QUA_TV4.md).

Công nghệ gpdk090, VDD 1,2 V, L = 0,1 µm. Chân nguồn thống nhất của nhóm: `VDD`, `GND`.

## 1. Lấy khối của TV4

| Cách | Làm gì |
|---|---|
| Virtuoso (schematic/symbol) | Thêm `SOFTINCLUDE <duong_dan>/Huynh_Anh_Tuan/cadence/cds.lib` vào `cds.lib` của bạn, rồi *Create → Instance* từ thư viện `tv4` ([cadence/README.md](cadence/README.md)) |
| Netlist Spectre | `include` theo thứ tự trong mục 4 dưới đây |
| Layout | GDS ở `layout/gds/`, hoặc thư viện `tv4_lay` trong `cadence/` |

## 2. Các khối và chân

| Khối | Chân (theo thứ tự subckt) | Chức năng |
|---|---|---|
| `TSPC_LFSR_8bit` | `CLK RST Q0 Q1 Q2 Q3 Q4 Q5 Q6 Q7 VDD GND` | LFSR 8 bit, P(x) = 1 + x + x⁶ + x⁷ + x⁸, flip-flop TSPC của TV2, **khối đề xuất** |
| `MS_LFSR_8bit` | như trên | cùng hàm, flip-flop master-slave `MS_DFF_SetReset` của TV1, khối chuẩn so sánh |
| `TSPC_LFSR_8bit_CMOS` | như trên | như TSPC_LFSR_8bit nhưng XOR hồi tiếp CMOS 36T (đối chứng) |
| `TSPC_CFSR_8bit` | như trên | 256 trạng thái (có 0x00), khối hồi tiếp CFSR_FB_OPT của TV3 |
| `LT_RTPG_8bit` | `Q0..Q7 CLK RST LP V0..V7 VDD GND` | bộ sinh mẫu ít chuyển mạch: nhận Q0..Q7 từ LFSR, ra V0..V7 tới CUT |

**Hành vi:**
- Thanh ghi dịch Q0 → Q7, D0 = Q0 ⊕ Q5 ⊕ Q6 ⊕ Q7, kích cạnh lên của CLK.
- `RST = 1` (tích cực mức cao): LFSR nạp seed **0x01** (Q0 = 1, Q1..Q7 = 0); CFSR về **0x00** rồi tự thoát; T-flip-flop trong LT_RTPG về 0.
- `LT_RTPG_8bit`: `LP = 0` thì V = Q (LFSR thường, 255 vector khác nhau); `LP = 1` thì chế độ ít chuyển mạch k = 2 (số bit lật giảm 50 %, 101 vector khác nhau).
- Chuỗi giá trị đúng ở từng chu kỳ: `golden_model/out/golden_lfsr_255.csv` (LFSR), `golden_cfsr_256.csv` (CFSR), `golden_lt_rtpg_k2.csv` (V khi LP = 1). Chu kỳ 0 là giá trị ngay sau khi nhả RST.

**Ghép LFSR với LT-RTPG và CUT (gợi ý cho TV5, TV6):** nối `Q0..Q7` của `TSPC_LFSR_8bit` vào `Q0..Q7` của `LT_RTPG_8bit`, dùng chung `CLK` và `RST`; `V0..V7` đưa vào CUT. Golden model đã tính chữ ký MISR tham khảo với CUT là bộ cộng 4 bit, A = V[3:0], B = V[7:4], MISR 8 bit cùng đa thức, reset 0x00, 255 chu kỳ: **0xDE** (LP = 0), **0x79** (LP = 1). Danh sách lỗi stuck-at và chữ ký tương ứng: `golden_model/out/fault_dictionary.csv`. Cấu trúc MISR cuối cùng do TV5 chốt; nếu khác thì báo TV4 để chạy lại golden model.

## 3. Quy tắc khi dùng (bắt buộc)

| Quy tắc | Lý do |
|---|---|
| Chỉ nhả `RST` (1 → 0) khi `CLK = 0` | quy tắc của cell TSPC của TV2; testbench của TV4 nhả ở 0,5T, cạnh clock đầu tiên ở T |
| Sườn clock ≤ 200 ps (testbench của TV4 dùng 2 tầng INV_CLK đệm: sườn tại chân CLK khoảng 85–95 ps (10–90 %) ở bản TSPC, 35–40 ps ở bản MS) | Với netlist TV2 có `as/ad`, TSPC sai từ sườn 300 ps (netlist gốc: từ 600 ps), do race qua các tầng cùng mở |
| Không nối tải vào chân `QB` của TSPC_DFF_R/S | `QB` là nút động bên trong cell TV2 |
| Tải đã kiểm: mỗi Q 1 INV_X1, mỗi V 4 INV_X1 | tải nặng hơn thì chạy lại để kiểm trễ |
| Tần số: 500 MHz là điểm đo chính của mọi khối; riêng dải TSPC_LFSR_8bit sau layout đã kiểm đúng tới 2,63 GHz (NN) và 1,85 GHz (SS) | LT_RTPG_8bit chưa quét tần số; xem [docs/5_layout.md](docs/5_layout.md) |

## 4. Mô phỏng bằng netlist Spectre

Thứ tự `include` (đường dẫn tính từ thư mục `tb/`), giống mọi testbench của TV4:

```text
include "/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs" section=NN
include "../depend/tv3/cells/cells.scs"           // cell TV3: INV_X1, XOR2_X1, XOR2_TG6, NOR3, AOI21, XNOR2...
include "../depend/tv3/blocks/XORTAP8.scs"        // mạng XOR hồi tiếp của TV3
include "../depend/tv3/blocks/CFSR_FB_OPT.scs"    // khối hồi tiếp CFSR của TV3
include "../depend/tv2/cells/cells.scs"           // TSPC_DFF_R, TSPC_DFF_S của TV2 (cells_asad/: bản thêm as/ad)
include "../cells/cells.scs"                      // cell của TV4: AND2_T, MUX2_N, INV_CLK, lớp DFF_MS (tự include MS_DFF_SetReset của TV1)
include "../blocks/LFSR_8bit.scs"                 // MS/TSPC_LFSR_8bit, _CMOS, TSPC_CFSR_8bit
include "../blocks/LT_RTPG_8bit.scs"              // LT_RTPG_8bit
```

Mẫu testbench có sẵn: `tb/tb_TSPC_LFSR.scs` (kích thích, tải, ba nguồn đo công suất riêng). Netlist sau layout của dải TSPC: `layout/rcx/TSPC_LFSR_8bit_post.scs` (thay cho khối trong `LFSR_8bit.scs`, cùng chân).

## 5. Chạy lại kết quả

Mọi lệnh gõ trong **terminal**, đứng ở thư mục `Huynh_Anh_Tuan/`, không gõ trong CIW của Virtuoso.

| Bước | Lệnh | Máy |
|---|---|---|
| Golden model | `cd golden_model && matlab -batch lfsr_golden_tv4` | máy có MATLAB |
| Sinh testbench | `python3 scripts/gen_tb.py` | bất kỳ (Python 3) |
| Spectre 3 corner | `bash scripts/run_tv4.sh` (hoặc `bash scripts/run_tv4.sh tb/tb_TSPC_LFSR_NN.scs`) | máy ảo Cadence |
| Tần số tối đa | `bash scripts/run_fmax.sh tb_TSPC_LFSR NN "500 400 350 320 300 290 280"` | máy ảo Cadence |
| Layout (GDS, CDL, hình) | `python3 scripts/layout/build_layout.py` | bất kỳ (Python 3 + gdstk, matplotlib) |
| DRC / LVS / RCX | `bash scripts/layout/assura.sh drc\|lvs\|rcx TSPC_LFSR_8bit` | máy ảo Cadence (Assura 4.1) |
| So sánh 3 khối CFSR | `python3 scripts/gen_tb_cfsr_cmp.py && bash scripts/run_cfsr_cmp.sh` | máy ảo Cadence |

Chi tiết từng bước: [docs/3_mo_phong.md](docs/3_mo_phong.md), [docs/5_layout.md](docs/5_layout.md) mục 5.6.

## 6. Nguồn gốc file của thành viên khác

Bản sao chỉ đọc trong `depend/`, ghi commit nguồn ở `depend/tv2/NGUON.md` và `depend/tv3/NGUON.md`. Khi TV2/TV3 cập nhật branch, TV4 chép lại rồi chạy lại mô phỏng; không sửa các file này.
