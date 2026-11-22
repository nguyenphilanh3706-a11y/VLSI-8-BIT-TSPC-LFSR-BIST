# Hướng dẫn TV3: cell, testbench, cách mô phỏng

Công nghệ gpdk090, VDD 1,2 V, L = 0,1 µm cho mọi transistor. Chân nguồn thống nhất của nhóm: VDD, GND.

## 1. Thư mục
| Thư mục | Nội dung |
|---|---|
| `cadence/` | thư viện Virtuoso (schematic, symbol, layout, av_extracted) và `cds.lib` |
| `cells/<CELL>/<CELL>.scs` | netlist cell (subckt) |
| `cells/<CELL>/tb_<CELL>.scs`, `.exp` | testbench cell và bảng giá trị mong đợi |
| `cells/cells.scs` | include chung các cell cơ bản |
| `blocks/` | khối ghép: XORTAP8, ZERO7, CFSR_FB và bản đối chứng |
| `tb/` | testbench khối và testbench so sánh XOR (`*_cmp`), mỗi cái có bản NN/SS/FF |

## 2. Giới thiệu cell

### Cổng cơ bản
| Cell | Hàm | T | Kích thước (W, µm) | Ghi chú |
|---|---|---|---|---|
| INV_X1 | Y = !A | 2 | N 0,12 / P 0,24 | P gấp đôi N để cân bằng sườn lên/xuống |
| NAND2_X1 | Y = !(A.B) | 4 | N 0,24 nối tiếp / P 0,24 song song | N nối tiếp nên rộng gấp đôi |
| NOR2_X1 | Y = !(A+B) | 4 | N 0,12 song song / P 0,48 nối tiếp | P nối tiếp (p1) rộng gấp 4 lần N |
| NOR3_X1 | Y = !(A+B+C) | 6 | N 0,12 song song / P 0,48 nối tiếp 3 tầng | dùng trong ZERO7, CFSR_FB_OPT |
| AOI21_X1 | Y = !(A1.A2 + B) | 6 | N A1-A2 0,24 nối tiếp, B 0,12 / P 0,48 | dùng trong CFSR_FB_OPT |

### Cổng XOR2 (Y = A ^ B)
| Cell | Kiểu | T | Tổng W | Nguyên lý |
|---|---|---|---|---|
| XOR2_X1 | CMOS tĩnh | 12 | 3,60 µm | 2 inverter tạo An, Bn + cổng phức Y = !(A.B + An.Bn); ngõ ra luôn được kéo về ray |
| XOR2_TG | cổng truyền 8T | 8 | 2,16 µm | 2 inverter + 2 cổng truyền: A=0 cho B qua, A=1 cho Bn qua |
| XOR2_TG6 | cổng truyền 6T | 6 | 1,44 µm | 1 inverter (An) + 1 cổng truyền + cặp MP1/MN1 lấy nguồn từ A/An đảo B; cặp này rộng gấp đôi để kéo Y nhanh |
| XNOR2_X1 | CMOS tĩnh (Y = !(A ^ B)) | 12 | 3,60 µm | như XOR2_X1, cổng phức Y = !(A.Bn + An.B); tầng cuối của CFSR_FB_OPT |

XOR2_TG6 ít transistor nhất nhưng ngõ ra không phục hồi mức logic, nên không đặt hai tầng 6T nối tiếp.

### Khối ghép
| Khối | Chức năng | T |
|---|---|---|
| XORTAP8 | FB = Q0 ^ Q5 ^ Q6 ^ Q7 (đa thức 1 + x + x^6 + x^7 + x^8): tầng 1 hai XOR2_TG6, tầng 2 XOR2_X1 phục hồi mức | 24 |
| XORTAP8_CMOS | bản đối chứng, 3 XOR2_X1 | 36 |
| ZERO7 | Z = 1 khi Q0..Q6 = 0: NOR(NAND(NOR3(Q0,Q1,Q2), NOR3(Q3,Q4,Q5)), Q6) | 20 |
| CFSR_FB | FB = XORTAP8 ^ ZERO7: đưa trạng thái 00000000 vào chuỗi, LFSR 255 -> 256 trạng thái | 56 |
| CFSR_FB_CMOS | bản đối chứng: XOR CMOS + cây NOR2/NAND2/INV | 74 |
| CFSR_FB_OPT | bản tối ưu, cùng hàm CFSR_FB: FB = (Q6 ^ Q7) ^ [(Q0 ^ Q5) + NOR3(Q0,Q1,Q2).NOR3(Q3,Q4,Q6)] | 42 |

Số liệu trễ, năng lượng và so sánh: `KET_QUA_TV3.md`.

## 3. Testbench

Mỗi testbench cell có cùng cấu trúc:
- model `gpdk090.scs section=NN` (đổi thành SS / FF cho corner chậm / nhanh);
- nguồn `Vvdd` 1,2 V, `Vgnd` 0 V;
- ngõ vào là nguồn PWL, mỗi vector giữ 500 ps, sườn 20 ps; dãy vector đi qua mọi tổ hợp và mỗi lần đổi một ngõ vào;
- DUT `XDUT`, ngõ ra Y tải 4 INV_X1 (FO4);
- phân tích `tran`, `maxstep=1p`, `errpreset=conservative`, lưu ngõ vào và Y.

| Testbench | Vector |
|---|---|
| tb_INV_X1 | A: 0 1 0 |
| tb_NAND2_X1, tb_NOR2_X1, tb_XOR2_X1, tb_XOR2_TG, tb_XOR2_TG6 | AB: 00 10 00 01 11 10 11 01 00 |
| tb_NOR3_X1 | ABC: 000 100 110 010 011 111 101 001 000 |
| tb_AOI21_X1 | A1 A2 B: 000 100 110 010 011 111 101 001 000 |
| tb_XNOR2_X1 | AB: như tb_XOR2_X1, Y mong đợi đảo lại |
| tb/tb_XOR2_*_cmp | 9 vector, ngõ vào qua 2 INV đệm, có đo năng lượng |
| tb/tb_XORTAP8*, tb/tb_CFSR_FB* | 16 / 256 tổ hợp, ngõ vào qua 2 INV đệm |

File `.exp` cạnh testbench ghi giá trị mong đợi của Y ở cuối mỗi vector:
```
T 5e-10          chu kỳ vector (s)
MARGIN 1e-11     lấy mẫu tại (k+1)T - MARGIN
STRICT 1         mức ra phải cách ray <= 10% VDD
OUT Y
V <k> <đo trễ 0|1> <Y mong đợi> ; <mô tả>
```

## 4. Chạy mô phỏng (trong VM, tại thư mục Vo_Minh_Tam)

Một testbench cell:
```
cd cells/NOR3_X1 && spectre tb_NOR3_X1.scs -raw ../../out/nor3 +log ../../out/nor3.log
cd ../.. && viva -datadir out/nor3 &
```
Testbench khối, so sánh XOR (bản NN/SS/FF) chạy giống vậy trong thư mục `tb`:
```
cd tb && spectre tb_CFSR_FB_NN.scs -raw ../out/cfsr_nn +log ../out/cfsr_nn.log
```
So Y ở cuối mỗi vector với bảng `.exp` cạnh testbench. Trễ: Calculator -> `delay`, ngưỡng 0,6 V;
năng lượng mỗi phép = VDD x |dòng VVDD trung bình| x chu kỳ vector.

## 5. Mô phỏng bằng ADE L

1. `cd cadence && virtuoso &`, thư viện `TV3_CELLS`.
2. Mở `tb_<CELL>` view `schematic` có sẵn (so sánh XOR tải 8 cổng: `tb_XOR2_FO8`), bỏ qua phần còn lại của bước này.
   Nếu tự tạo testbench mới: DUT, 4 INV_X1 tải trên Y, `analogLib/vdc` 1,2 V cho VDD, `vdc` 0 V cho GND,
   `analogLib/vpulse` cho mỗi ngõ vào (v1 0, v2 1.2, tr = tf = 20p), `analogLib/gnd`. Check and Save.
3. Launch -> ADE L. Setup -> Model Libraries: `/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs`, section `NN`.
4. Analyses -> `tran`, `conservative`, stop: 1.5n (INV), 2n (cổng 2 ngõ vào), 4n (cổng 3 ngõ vào), 8n (tb_XOR2_FO8),
   16n (XORTAP8), 128n (ZERO7), 256n (CFSR_FB).
5. Outputs -> To Be Plotted -> chọn ngõ vào và Y trên schematic. Netlist and Run.
6. Đo trễ: Calculator -> `delay`, ngưỡng 0,6 V cả hai tín hiệu. Session -> Save State để dùng lại.

## 6. Layout, extracted và mô phỏng sau layout

| Nội dung | Vị trí |
|---|---|
| Layout + av_extracted 9 cell lá, gồm AOI21_X1, XNOR2_X1 (và FILL1/2/4/8 lấp chỗ trống) | `cadence/TV3_CELLS` |
| Layout + av_extracted 6 khối (XORTAP8, ZERO7, CFSR_FB, CFSR_FB_OPT, bản CMOS) | `cadence/TV3_CELLS` (cell con và via: `cadence/TV3_BLK`) |
| XOR2_X1 bản nén 15 cột (so sánh với XOR2_X1 17 cột) | `cadence/TV3_OPT` |
| GDS từng cell và từng khối (khối đã gộp cell lá) | `layout/gds/` |
| Báo cáo DRC/LVS | `layout/assura/`, `layout/assura/cell_view/`, ảnh `anh/drc_lvs/` |
| Ảnh layout | `layout/hinh/` |
| Netlist trích ký sinh (Spectre) và testbench sau layout | `layout/rcx/` |

Mở xem: `cd cadence && virtuoso &` (cần gpdk090 v4.6, sửa đường dẫn trong `cadence/cds.lib` nếu cài nơi khác), Library Manager -> `TV3_CELLS` hoặc `TV3_BLK` -> view `layout` / `av_extracted`.
Khuôn cell: cao 2,76 µm, bước cột 0,27 µm, ray GND (dưới) và VDD (trên) Metal1 rộng 0,24 µm, chân tín hiệu Metal1.
Cell khác nhóm làm cùng khuôn này thì xếp liền hàng với cell TV3 được (dùng chung ray).

Mô phỏng sau layout (trong VM, thư mục Vo_Minh_Tam):
```
cd layout/rcx && spectre tb_CFSR_FB_post_NN.scs -raw ../../out/cfsr_post +log ../../out/cfsr_post.log
spectre tb_CFSR_FB_OPT_post_NN.scs -raw ../../out/cfsr_opt_post +log ../../out/cfsr_opt_post.log   # ban toi uu
cd ../../tb && spectre tb_XOR2_TG6_fo8_NN.scs -raw ../out/tg6_fo8 +log ../out/tg6_fo8.log   # XOR tải 8 cổng, trước layout
```
Testbench sau layout dùng lại phần thân `tb/*.scs` và bảng `.exp` cũ, chỉ thay mạch DUT bằng `layout/rcx/<CELL>_rcx.scs`.

## 7. Thành viên khác dùng thư viện TV3

Thêm vào `cds.lib` của mình (thay `<repo>` bằng đường dẫn đã clone), cần cả ba dòng:
```
DEFINE TV3_CELLS <repo>/Vo_Minh_Tam/cadence/TV3_CELLS
DEFINE TV3_BLK <repo>/Vo_Minh_Tam/cadence/TV3_BLK
DEFINE TV3_OPT <repo>/Vo_Minh_Tam/cadence/TV3_OPT
```
Schematic: Create -> Instance -> `TV3_CELLS`, view `symbol`. Layout: cùng thư viện, view `layout`.

| Tên trong kế hoạch | Cell | Chân |
|---|---|---|
| INV | INV_X1 | A, Y, VDD, GND |
| NAND2 | NAND2_X1 | A, B, Y, VDD, GND |
| NOR2 | NOR2_X1 | A, B, Y, VDD, GND |
| XOR2 CMOS 12T | XOR2_X1 | A, B, Y, VDD, GND |
| XOR2 TG 8T / 6T | XOR2_TG / XOR2_TG6 | A, B, Y, VDD, GND |
| Mạng XOR hồi tiếp | XORTAP8 | Q0, Q5, Q6, Q7, FB, VDD, GND |
| CFSR | CFSR_FB_OPT (bản cũ: CFSR_FB) | Q0..Q7, FB, VDD, GND |

Nối FB vào ngõ D của flip-flop Q0. Mô phỏng vòng kín mẫu: `cd tb && spectre tb_CFSR_loop_NN.scs -raw ../out/loop +log ../out/loop.log`.
