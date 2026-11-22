# TV3: cổng XOR, thư viện cổng cơ bản, CFSR (Võ Minh Tâm)

Công nghệ gpdk090, VDD 1,2 V, Spectre, Assura 4.1, Encounter. Chân nguồn thống nhất của nhóm: VDD, GND.

## Đã làm được

| Hạng mục | Kết quả |
|---|---|
| Cổng XOR2 | 3 cấu trúc: CMOS tĩnh 12T (XOR2_X1), cổng truyền 8T (XOR2_TG), cổng truyền 6T (XOR2_TG6); so sánh trễ, năng lượng, diện tích ở NN/SS/FF, tải FO4 và FO8, trước và sau layout |
| Thư viện cổng cơ bản | INV_X1, NAND2_X1, NOR2_X1, NOR3_X1, AOI21_X1, XNOR2_X1; testbench từng cell PASS cả 3 corner |
| Mạng hồi tiếp LFSR | XORTAP8: FB = Q0 ^ Q5 ^ Q6 ^ Q7 (đa thức 1 + x + x^6 + x^7 + x^8), 24T thay cho 36T |
| Chống kẹt trạng thái 0 | ZERO7 (phát hiện Q0..Q6 = 0) và CFSR_FB: LFSR 255 trạng thái thành 256 trạng thái, đúng 256/256 tổ hợp |
| Bản tối ưu | CFSR_FB_OPT (42T): cùng hàm CFSR_FB, gộp nhánh phát hiện 0 vào cổng AOI21; XOR2_X1 layout nén 17 xuống 15 cột |
| Cellview | 9 cell lá và 6 khối có đủ schematic, symbol, layout, av_extracted trong cùng thư viện TV3_CELLS; 16 testbench schematic |
| Kiểm tra vật lý | DRC 0 lỗi, LVS Match với netlist xuất từ schematic Virtuoso cho mọi cell và khối |
| Chống kẹt trong vòng kín | khối sau layout + flip-flop mẫu, 1 GHz: LFSR thuần kẹt ở 00000000, CFSR tự thoát và đi đủ 256 trạng thái ở NN/SS/FF |
| Mô phỏng sau layout | Trích R + C bằng Assura RCX, mọi testbench PASS ở NN/SS/FF |
| Báo cáo | Phần Chương 3: mạng hồi tiếp, XOR, chống kẹt trạng thái 0, tối ưu |

## Đối chiếu việc được giao

| Việc trong kế hoạch | File bàn giao |
|---|---|
| Schematic, Symbol, Layout, Extracted của INV, NAND2, NOR2, XOR2 | `cadence/TV3_CELLS`: INV_X1, NAND2_X1, NOR2_X1, XOR2_X1, XOR2_TG, XOR2_TG6 |
| XOR2 CMOS 12T và cổng truyền 6T/8T, chọn bản tối ưu | `KET_QUA_TV3.md` mục 1, 9, 11; chọn XOR2_TG6 cho tầng đầu, XOR CMOS/XNOR CMOS cho tầng lái ngõ D |
| Mạch CFSR theo Hình 15.19b, hoạt động đúng | `cadence/TV3_CELLS`: CFSR_FB, CFSR_FB_OPT; `tb/tb_CFSR_loop_*.scs` |
| Tuần 1: dạng sóng chứng minh bảng chân trị | `anh/dang_song/`; testbench schematic `tb_<CELL>` trong TV3_CELLS |
| Tuần 2: trễ và công suất XOR2 tải 8 bit | `KET_QUA_TV3.md` mục 9, 11; `tb_XOR2_FO8` |
| Tuần 3: stick diagram | `anh/stick/` (vẽ từ layout) |
| Tuần 3: layout, ảnh DRC 0 lỗi và LVS Match, diện tích | `anh/drc_lvs/`, `layout/assura/cell_view/`, `KET_QUA_TV3.md` mục 7 |
| Tuần 4: phần Chương 3 | `BAO_CAO_CHUONG3_TV3.docx`, `BAO_CAO_CHUONG3_TV3.md` |
| Cung cấp thư viện cổng cho nhóm | `cadence/`, cách dùng ở `HUONG_DAN_TV3.md` mục 7 |

## Số liệu chính (sau layout, corner NN)

| Cell / khối | Transistor | Diện tích cell (µm²) | Trễ | Năng lượng |
|---|---|---|---|---|
| XOR2_X1 (CMOS 12T) | 12 | 13,41 (bản nén 11,92) | 121,6 ps | 0,017 pJ |
| XOR2_TG (8T) | 8 | 8,94 | 113,9 ps | 0,017 pJ |
| XOR2_TG6 (6T) | 6 | 7,45 | 113,9 ps | 0,016 pJ |
| XORTAP8 | 24 | 28,3 | 195,2 ps | 0,024 pJ |
| CFSR_FB_CMOS (đối chứng) | 74 | 83,5 | 281,0 ps (SS 398,5 ps) | 0,043 pJ |
| CFSR_FB | 56 | 62,6 | 275,5 ps (SS 390,6 ps) | 0,040 pJ |
| CFSR_FB_OPT (tối ưu) | 42 | 44,7 | 244,8 ps (SS 350,5 ps) | 0,036 pJ |

So với CFSR_FB, CFSR_FB_OPT giảm 25 % transistor, 29 % diện tích cell, 11 % trễ, 10 % năng lượng;
khung layout cả vòng nguồn 99,2 µm² (CFSR_FB: 271,9 µm²; cùng cấu hình P&R mới: 123,8 µm²).
So sánh đầy đủ: `KET_QUA_TV3.md` mục 10.

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `cells/` | netlist và testbench 9 cell lá |
| `blocks/` | XORTAP8, ZERO7, CFSR_FB, CFSR_FB_OPT và bản đối chứng CMOS |
| `tb/` | testbench khối, so sánh XOR/XNOR (FO4, FO8), bản NN/SS/FF |
| `cadence/` | thư viện Virtuoso TV3_CELLS, TV3_BLK, TV3_OPT và `cds.lib` |
| `layout/gds/` | GDS cell lá, cell lấp (FILL), khối; `*_OPT.gds` là bản tối ưu |
| `layout/assura/` | báo cáo DRC/LVS khối; `cell_view/` là báo cáo của từng cellview trong thư viện |
| `layout/cdl/` | netlist xuất từ schematic Virtuoso, dùng cho LVS |
| `layout/rcx/` | netlist trích ký sinh và testbench sau layout |
| `layout/hinh/` | ảnh layout vẽ từ GDS |
| `anh/` | ảnh chụp Virtuoso (schematic, dạng sóng, DRC/LVS) và stick diagram |
| `KET_QUA_TV3.md` | bảng kết quả đầy đủ |
| `HUONG_DAN_TV3.md` | mô tả cell, cách chạy testbench, ADE L, layout |
| `BAO_CAO_CHUONG3_TV3.md`, `.docx` | phần Chương 3 của báo cáo |

Thư viện Virtuoso trong `cadence/`: `TV3_CELLS` (cell lá và khối, đủ 4 view), `TV3_BLK` (layout cell con và via của khối, phải giữ kèm),
`TV3_OPT` (XOR2_X1 bản nén). Mở: `cd cadence && virtuoso &` (cần cài sẵn gpdk090 v4.6).

## Còn lại

- Ghép CFSR_FB_OPT (hoặc CFSR_FB) với flip-flop TSPC (TV2) thành LFSR 8 bit (TV4).
  Vòng kín hiện mô phỏng bằng flip-flop mẫu lý tưởng nên chưa phải số f_max của hệ thống.
