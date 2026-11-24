# TV2: TSPC D Flip-Flop có Reset và Set (Nguyễn Phước An)

Công nghệ gpdk090, VDD 1,2 V, Spectre, Assura 4.1. Chân nguồn thống nhất của nhóm: VDD, GND. Cấu trúc thư mục theo chuẩn của TV3 (`cadence/`, `anh/`, bảng đối chiếu việc được giao), giữ thêm thư mục theo tuần.

## Đã làm được

| Hạng mục | Kết quả |
|---|---|
| Cell | `TSPC_DFF_R` (Reset bất đồng bộ) và `TSPC_DFF_S` (Set bất đồng bộ); mỗi cell 15 transistor gồm 2 keeper, một pha clock |
| Cellview | 2 cell có schematic, symbol, layout trong thư viện `TV2_TSPC`; chưa có av_extracted (mô phỏng sau layout dùng netlist RC `Tuan3/layout/*_rcx.scs`) |
| Chức năng | 11/11 vector ở NN, SS, FF, trước và sau layout; 90/90 điểm PVT sau layout |
| Layout | R 8,68 × 2,76 µm = 23,96 µm²; S 8,00 × 2,76 µm = 22,08 µm² |
| Kiểm tra vật lý | DRC 0 luật vi phạm, LVS Match cho cả hai cell (chạy lại ngày 24/11/2026 trên thư viện trong `cadence/`) |
| Mô phỏng sau layout | RCX bằng Assura; t_pcq, chuỗi 8 FF, 45 điểm PVT (Tuần 3 và 4) |
| So sánh với MS-DFF của TV1 | `Tuan4/SO_SANH_TV1.md` (Bảng A, trước layout) |
| Báo cáo | Bản nháp Chương 3 phần TV2: `Tuan4/BAO_CAO_TUAN4.md` |

Báo cáo tổng hợp việc đã làm kèm hình minh chứng (theo mẫu nhánh `report`): `BAO_CAO_TV2_MINH_CHUNG.md` / `.pdf`.

## Đối chiếu việc được giao

| Việc trong kế hoạch | Tệp |
|---|---|
| Schematic và Symbol cell TSPC | `cadence/TV2_TSPC`; ảnh `anh/schematic/` |
| Cellview: schematic, symbol, layout | `cadence/TV2_TSPC` (không có Extracted dạng av_extracted) |
| Tuần 1: chức năng, W/L chống chia sẻ điện tích | `Tuan1/` |
| Tuần 2: đo t_pcq, setup, hold, công suất, f_max; bảng so với TV1 | `Tuan2/`, `Tuan4/SO_SANH_TV1.md` |
| Tuần 3: layout, DRC 0 lỗi, LVS Match, diện tích | `Tuan3/`, `anh/layout/`, `anh/drc_lvs/` |
| Tuần 3: stick diagram | chưa làm |
| Tuần 4: PVT, Chương 3 | `Tuan4/` |
| Tuần 4: Chương 2, slide | chưa làm (Chương 2 là phần của TV1) |

## Số liệu chính

Sau layout, NN, 27 °C, tải FO4 trên Q và QB (`Tuan3/KET_QUA_TUAN3.md`, `Tuan4/KET_QUA_TUAN4.md`):

| Cell | Transistor | Diện tích (µm²) | t_pcq lên / xuống, NN (ps) | t_pcq xấu nhất, SS 0,8 V 125 °C (ps) |
|---|---|---|---|---|
| TSPC_DFF_R | 15 | 23,96 | 75,7 / 74,6 | 259,9 |
| TSPC_DFF_S | 15 | 22,08 | 78,9 / 97,3 | 333,9 |

So sánh trước layout với MS-DFF của TV1 (có `as/ad`, Q tải FO4, QB để hở): TSPC ít hơn 42% transistor, t_pcq thấp hơn 20 đến 38%, setup thấp hơn khoảng 60%, T_min bộ chia 2 thấp hơn 25 đến 52%; công suất ngang nhau khi D ngẫu nhiên và khác nhau nhiều theo mẫu D (`Tuan4/SO_SANH_TV1.md`).

## Đối chiếu với chuẩn TV3

| Mục | TV3 | TV2 | Kết quả |
|---|---|---|---|
| Chiều cao cell | 2,76 µm | 2,76 µm | trùng |
| Ray GND dưới, VDD trên, Metal1 | rộng 0,24 µm | rộng 0,24 µm | trùng |
| Chân tín hiệu | Metal1 | Metal1 | trùng |
| Tên chân nguồn | VDD, GND | VDD, GND | trùng |
| Bước cột | 0,27 µm | không theo lưới này (8,68 và 8,00 µm không phải bội của 0,27) | chưa trùng |
| Tên chân Reset | (kế hoạch nhóm: RESET) | `RST` ở cell R, `SET` ở cell S | khác kế hoạch, chưa đổi |
| Cấu trúc thư mục | `cadence/`, `anh/`, `layout/` | `cadence/`, `anh/`, thư mục theo tuần | cùng chuẩn |

Hai điểm chưa trùng cần nhóm thống nhất trước khi TV4 ghép dải 8 bit: đổi `RST` thành `RESET` (phải sửa schematic, layout và chạy lại LVS) và canh chiều rộng cell theo bước cột 0,27 µm.

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `cadence/` | thư viện Virtuoso `TV2_TSPC` (schematic, symbol, layout) và `cds.lib` |
| `anh/` | ảnh chụp thật từ Virtuoso: `schematic/`, `layout/`, `drc_lvs/` |
| `cells/` | netlist và testbench của hai cell |
| `Tuan1/` | thiết kế, kết quả chức năng và định thời Tuần 1 |
| `Tuan2/` | đường t_CQ theo t_DC, setup/hold, công suất, f_max |
| `Tuan3/` | layout, GDS, CDL, netlist RC, kết quả sau layout |
| `Tuan4/` | PVT 45 điểm (Bảng B), bản nháp Chương 3, Bảng A so sánh với TV1 (`SO_SANH_TV1.md`; số đo thô và netlist MS-DFF trong `so_sanh/`) |

Mỗi báo cáo có bản `.md` và `.pdf`.

## Mở thư viện Virtuoso

```
cd Nguyen_Phuoc_An/cadence && virtuoso &
```

Cần gpdk090 v4.6; sửa đường dẫn trong `cadence/cds.lib` nếu cài ở nơi khác. Library Manager → `TV2_TSPC` → `TSPC_DFF_R` hoặc `TSPC_DFF_S` → view `schematic`, `symbol`, `layout`.

## Ghi chú về ảnh

- `anh/schematic/`: mỗi cell hai ảnh (nửa trái và nửa phải), vì schematic nối dây bằng nhãn tên net và quá rộng để đọc được trong một khung.
- `anh/layout/`: cửa sổ Virtuoso Layout Suite, mở chỉ đọc.
- `anh/drc_lvs/`: cửa sổ dòng lệnh hiển thị kết quả Assura DRC (0 luật vi phạm, 6800 luật đã kiểm) và LVS (matched).
- Ảnh trong `Tuan3/img/` được vẽ lại từ dữ liệu layout, không phải ảnh chụp.

## Còn lại

- Stick diagram, slide phần TV2.
- Ghép dải 8 bit với TV4; thống nhất tên chân và bước cột (bảng trên).
- Setup/hold, công suất, f_max trên netlist trích và trên toàn bộ ma trận PVT.
- Tính lại diện tích gắn `as/ad` lấy từ layout để so sánh với MS-DFF sau khi TV1 có layout.
