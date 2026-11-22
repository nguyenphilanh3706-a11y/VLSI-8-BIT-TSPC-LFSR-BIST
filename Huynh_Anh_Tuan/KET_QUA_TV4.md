# Kết quả TV4 – Lõi PRNG/LFSR 8 bit và kiểm chứng toán học

Huỳnh Anh Tuấn (TV4). Cập nhật 22/11/2026. Trang này tóm tắt kết quả; số liệu đầy đủ ở [docs/4_ket_qua.md](docs/4_ket_qua.md) và [docs/5_layout.md](docs/5_layout.md), cách dùng khối ở [HUONG_DAN_TV4.md](HUONG_DAN_TV4.md).

## Tiến độ theo kế hoạch nhóm

| Tuần | Việc của TV4 | Trạng thái |
|---|---|---|
| 1 | Golden model, bảng giá trị chuẩn | **Xong** (MATLAB) |
| 2 | Ghép MS_LFSR_8bit, TSPC_LFSR_8bit; so khớp golden model; dạng sóng; bảng định thời MS và TSPC | **Xong phần TSPC** (flip-flop TV2); MS chờ cell TV1 |
| 3 | Layout dải LFSR 8 bit (pitch-matching), DRC/LVS | **Xong phần TSPC** (layout flip-flop TV2): DRC 0 lỗi, LVS khớp, RCX, hậu layout PASS; MS dùng flip-flop tạm |
| 4 | Phần viết Chương 1 + Chương 4 | Bản nháp [`report1,4.docx`](report1,4.docx), **chưa hoàn thành**: số của bản MS chờ cell TV1 |

Còn chờ: cell MS_DFF_SetReset của **TV1** (netlist + layout cao 2,76 µm) để thay flip-flop tạm của bản MS.

## Golden model (MATLAB)

| Kiểm tra | Kết quả |
|---|---|
| P(x) = 1 + x + x⁶ + x⁷ + x⁸, seed 0x01 | chu kỳ **255**, không qua 0x00; T²⁵⁵ = I, T⁸⁵, T⁵¹, T¹⁵ ≠ I ⇒ đa thức nguyên thủy |
| Golomb trên Q7 | cân bằng 128/127; phân bố run đúng; tự tương quan hai mức (255 / −1) |
| CFSR từ 0x00 | **256** trạng thái |
| LT-RTPG k = 2 | số bit lật −50,0 % (4,016 → 2,008 mỗi chu kỳ), 101 vector khác nhau |
| MISR tham khảo (CUT cộng 4 bit) | chữ ký đúng 0xDE (LP = 0), 0x79 (LP = 1); phát hiện 10/10 lỗi stuck-at ở ngõ ra |

## Kiểm chứng Spectre trước layout (500 MHz, 300 chu kỳ)

**18/18 testbench PASS 301/301** ở NN, SS, FF: phần cứng khớp golden model ở từng chu kỳ.

| NN, 27 °C | Transistor | Trễ CLK→Q | P_DUT | P_DUT + P_clock | f_max NN / SS |
|---|---:|---:|---:|---:|---:|
| MS_LFSR_8bit (flip-flop tạm) | 218 | 240,1 ps | 94,1 µW | 115,5 µW | 1,82 / 1,25 GHz |
| **TSPC_LFSR_8bit (flip-flop TV2)** | **144** | **186,6 ps** | **63,5 µW** | **87,5 µW** | **3,45 / 2,38 GHz** |
| TSPC so với MS | −33,9 % | −22,3 % | −32,6 % | −24,2 % | ×1,9 |
| TSPC_CFSR_8bit (CFSR_FB_OPT của TV3) | 162 | 165,1 ps | 67,1 µW | 91,2 µW | 3,33 / 2,22 GHz |
| LFSR + LT_RTPG, LP = 0 → 1 | 144 + 362 | 315,6 → 269,4 ps | 168,1 → 161,0 µW | – | – |

- **LT-RTPG bật:** công suất tải ngõ vào CUT 14,44 → 7,97 µW (**−44,8 %**).
- **Tải clock:** 32 cổng MOS nối clock (TSPC) so với 66 (MS), không cần CLKB.
- **Sườn clock:** bản TSPC đúng tới 400 ps, sai từ 600 ps (MS đúng tới 800 ps).
- **CFSR_FB_OPT so với CFSR_FB** trong thanh ghi TSPC: f_max +14–27 %, P_DUT chỉ −1,6–2 %.

## Layout và hậu layout (Assura, gpdk090)

| Sau layout, NN, 500 MHz | Diện tích | Trễ CLK→Q | P_DUT + P_clock | f_max NN |
|---|---:|---:|---:|---:|
| MS_LFSR_8bit (flip-flop tạm) | 235,48 µm² | 381,6 ps | 160,6 µW | 1,33 GHz |
| **TSPC_LFSR_8bit (layout flip-flop TV2)** | **218,10 µm²** | **238,8 ps** | **102,3 µW** | **2,63 GHz** |
| TSPC so với MS | −7,4 % | −37,4 % | −36,3 % | ×2,0 |

- Cả hai dải: một hàng cao 2,76 µm theo khuôn cell TV3, **DRC 0 lỗi, LVS khớp**, trích RC, hậu layout **PASS 301/301** ở NN, SS, FF.
- Dải TSPC chỉ nhỏ hơn MS 7,4 % vì cell TV2 rộng 8,00–8,68 µm (2 keeper L = 0,40 µm). Với flip-flop tạm 17T con số là −32,3 %.
- Sau layout, f_max giới hạn bởi đường hồi tiếp Q0 → XOR → D0 chạy dọc hàng (dây 62–75 µm).

![So sánh sau layout](docs/images/so_sanh_hau_layout.png)

## Kết luận cho báo cáo

1. Golden model chứng minh đại số P(x) nguyên thủy và chuỗi đạt Golomb; phần cứng Spectre khớp golden model ở mọi chu kỳ, mọi corner, trước và sau layout.
2. TSPC (flip-flop TV2) nhanh hơn và tốn ít công suất hơn MS rõ rệt cả trước và sau layout (sau layout: trễ −37 %, công suất −36 %, f_max gấp 2). Mức giảm transistor đạt khoảng 34 % (mục tiêu nhóm 45–50 %), diện tích sau layout −7,4 %.
3. Giới hạn của TSPC: cần sườn clock ≤ 400 ps. Bản MS hiện dùng flip-flop tạm nên mọi so sánh MS/TSPC sẽ chạy lại khi có cell TV1.

## File chính

| Nội dung | File |
|---|---|
| Golden model | [`golden_model/lfsr_golden_tv4.m`](golden_model/lfsr_golden_tv4.m), kết quả [`golden_model/out/`](golden_model/out/) |
| Netlist khối | [`blocks/`](blocks/), cell của TV4 [`cells/`](cells/), bản sao TV2/TV3 [`depend/`](depend/) |
| Kết quả Spectre | [`results/`](results/README.md) |
| Layout | [`layout/`](layout/), ảnh Virtuoso trong [docs/5_layout.md](docs/5_layout.md) |
| Thư viện Virtuoso | [`cadence/`](cadence/README.md) |
