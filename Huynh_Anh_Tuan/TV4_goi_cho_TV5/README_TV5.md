# Gói bàn giao của TV4 cho TV5 (BILBO / MISR)

Người gửi: TV4 – Huỳnh Anh Tuấn. Ngày 28/11/2026. Công nghệ gpdk090, VDD 1,2 V, Cadence Virtuoso IC6.1.5.
Nguồn gốc: branch `module/LFSR-8BIT-PRPG(4)`. Gói này gồm những gì TV5 cần để kiểm `BILBO_8BIT` với bộ sinh mẫu (TPG) của TV4: quy ước LFSR, chuỗi vector chuẩn và chữ ký MISR chuẩn tính theo đúng cấu trúc `BILBO_8BIT` của TV5.

Khối TPG để ghép vào top BIST (thư viện Virtuoso, netlist, layout) nằm trong gói của TV6: [`../TV4_goi_cho_TV6/`](../TV4_goi_cho_TV6/README_TV6.md).

## 1. Trong gói có gì

| Thư mục | Nội dung |
|---|---|
| `golden/` | Chuỗi trạng thái LFSR chuẩn, vector V[7:0] tới CUT, **chữ ký MISR chuẩn**, giá trị MISR từng chu kỳ, script tạo lại |
| `netlist/` | `LFSR_8bit.scs` (khối LFSR của TV4, để xem nhánh hồi tiếp và cách nạp seed), `tb_TSPC_LFSR.exp` (bảng giá trị mong đợi 301 chu kỳ mà testbench của TV4 dùng để so) |
| `hinh/` | Ảnh chụp trong Virtuoso: symbol, schematic `TSPC_LFSR_8bit`, symbol `LT_RTPG_8bit`, dạng sóng ViVA của LFSR và LT-RTPG |

## 2. Quy ước LFSR của TV4

| Mục | Giá trị |
|---|---|
| Đa thức | P(x) = 1 + x + x⁶ + x⁷ + x⁸ (nguyên thủy, chu kỳ 255) |
| Chiều dịch | Q0 → Q1 → … → Q7 |
| Hồi tiếp | D0 = Q0 ⊕ Q5 ⊕ Q6 ⊕ Q7 |
| Seed | `RST = 1` nạp **0x01** (Q0 = 1) |
| Chuỗi đầu | `01 03 07 0F 1F 3F 7E FC F9 F2 …`, quay về `01` sau đúng 255 cạnh clock (`golden/golden_lfsr_255.csv`) |

Nếu chế độ sinh mẫu của `BILBO_8BIT` cần cho cùng chuỗi với TV4 thì dùng đúng đa thức, chiều dịch và seed ở trên rồi so với `golden_lfsr_255.csv`.

## 3. Chữ ký MISR chuẩn

Điều kiện: đúng **255 cạnh clock** ở chế độ Test (C1C0 = 01), MISR reset về 0x00, CUT là bộ cộng 4 bit (A = V[3:0], B = V[7:4]), Z[4:0] → D4..D0, D7..D5 = 0.

| Cách lấy mẫu | LP = 0 | LP = 1 |
|---|---|---|
| **A** – MISR nhận Z của V(1)…V(255), tức MISR chậm hơn LFSR một chu kỳ (golden model TV4) | **0xDE** | **0x79** |
| **B** – LFSR và MISR reset và nhả cùng lúc; ở cạnh thứ t, MISR chốt Z của V(t−1), bắt đầu từ seed 0x01 | **0xEF** | **0x3C** |

- `BILBO_8BIT` của TV5 dùng `Q⁺ = D ⊕ ¬S` (đảo bit dịch). Golden model gốc của TV4 dùng `Q⁺ = D ⊕ S`. Sau **đúng 255 chu kỳ**, hai cấu trúc cho **cùng chữ ký**, vì phần đảo là một hằng số cộng thêm mỗi chu kỳ và tổng của nó qua 255 chu kỳ bằng 0 (T²⁵⁵ = I). Các giá trị trung gian thì khác nhau: so từng chu kỳ theo cột `MISR_TV5_*` trong `golden/vector_lfsr_cut_misr.csv` (cách B).
- Với cả hai cấu trúc và cả hai cách lấy mẫu, đủ **10/10 lỗi SA0/SA1** ở ngõ ra CUT đều làm chữ ký khác chữ ký đúng (`golden/chu_ky_misr.csv`). Chạy đúng 255 chu kỳ thì SA0 và SA1 trên cùng một dây cho cùng chữ ký: phát hiện được lỗi nhưng không phân biệt được SA0 với SA1.
- Cách lấy mẫu (A hay B) do TV6 chốt khi ghép top BIST; TV5 kiểm được cả hai bằng các file trong `golden/`.

## 4. Lưu ý khi mô phỏng chung với TPG của TV4

| Lưu ý | Lý do |
|---|---|
| Chạy **ít nhất 255 chu kỳ** ở chế độ Test: 510 ns ở 500 MHz, cộng thời gian reset | Testbench 40 ns chỉ được khoảng 5 chu kỳ ở chế độ Test, chưa so được chữ ký |
| Một nguồn clock chung cho LFSR, LT_RTPG và BILBO | Tránh lệch chuỗi vector so với golden model |
| Chỉ nhả RST (1 → 0) khi CLK = 0; sườn clock ≤ 200 ps | Quy tắc của flip-flop TSPC (TV2) trong LFSR |
| `LP` chỉ đổi khi RST = 1 hoặc giữa hai lần chạy | Đổi giữa chừng làm chuỗi V khác golden model |

## 5. Các file trong `golden/`

| File | Nội dung |
|---|---|
| `golden_lfsr_255.csv`, `.hex` | Q[7:0] ở từng chu kỳ (chu kỳ 0 = 0x01 ngay sau khi nhả RST), qua trọn 255 trạng thái |
| `golden_lfsr_300.csv` | 301 trạng thái cho testbench 300 cạnh clock |
| `golden_lt_rtpg_k2.csv` | V[7:0] khi LP = 1 |
| **`chu_ky_misr.csv`** | Chữ ký sau 255 chu kỳ khi không lỗi và với 10 lỗi stuck-at ở ngõ ra CUT, cho 2 cấu trúc MISR (TV4, TV5) và 2 cách lấy mẫu |
| **`vector_lfsr_cut_misr.csv`** | Từng cạnh clock: V, Z = V[3:0] + V[7:4], và giá trị MISR của `BILBO_8BIT` ngay sau cạnh đó (cách B). Dùng để dò lỗi theo từng chu kỳ |
| `misr_bilbo_tv5.py` | Script tạo hai file trên. Chạy `python3 misr_bilbo_tv5.py` ngay trong `golden/` (Python 3, không cần thư viện thêm). Đổi CUT hay cách nối thì sửa hàm `cut()` rồi chạy lại |
| `fault_dictionary.csv`, `bao_cao_golden_matlab.txt` | Từ golden model MATLAB của TV4 |

## 6. Liên hệ

Đổi cấu trúc MISR, chân `BILBO_8BIT` hay cách nối Z vào D thì báo TV4 để chạy lại golden model và cập nhật chữ ký chuẩn.
