# Thư viện Virtuoso của TV4

Hai thư viện OpenAccess (Virtuoso IC6.1.5, gpdk090) lấy từ máy ảo Cadence ngày 22/11/2026. Đã bỏ file khóa `*.cdslck`. Đã thử mở ở một thư mục mới bằng `cds.lib` dưới đây: mọi cellview mở được.

| Thư viện | Nội dung | Kích thước |
|---|---|---|
| `tv4/` | 26 cell schematic + symbol và 3 testbench schematic (29 cell) | ~2,7 MB |
| `tv4_lay/` | layout hai dải `TSPC_LFSR_8bit`, `MS_LFSR_8bit` và các cell con (8 cell) | ~0,3 MB |

## Mở thư viện

1. `cds.lib` của bạn phải có sẵn `DEFINE gpdk090 ...` (đường dẫn PDK trên máy bạn).
2. Thêm một dòng vào `cds.lib` đó (đổi `<duong_dan>` thành chỗ bạn clone repo):

   ```text
   SOFTINCLUDE <duong_dan>/Huynh_Anh_Tuan/TV4_goi_cho_TV6/cadence/cds.lib
   ```

   File [`cds.lib`](cds.lib) ở đây chỉ có `DEFINE tv4 ./tv4` và `DEFINE tv4_lay ./tv4_lay`. Đường dẫn tương đối được tính theo vị trí của chính file này, nên không cần sửa.
3. Mở Virtuoso, vào *Library Manager*, sẽ thấy `tv4` và `tv4_lay`.

Muốn dùng khối của TV4 trong mạch của mình (ví dụ TV5/TV6 ghép BIST): *Create → Instance*, Library `tv4`, Cell `LT_RTPG_8bit` (hoặc `TSPC_LFSR_8bit`, `TSPC_CFSR_8bit`), View `symbol`. Chân và quy tắc reset/clock: [HUONG_DAN_TV4.md](../../HUONG_DAN_TV4.md).

## Thư viện `tv4`

| Nhóm | Cell | Ghi chú |
|---|---|---|
| Khối của TV4 | `TSPC_LFSR_8bit`, `TSPC_LFSR_8bit_CMOS`, `TSPC_CFSR_8bit`, `MS_LFSR_8bit`, `LT_RTPG_8bit` | khối chính |
| Cell của TV4 | `AND2_T`, `MUX2_N`, `INV_CLK`, `DFF_MS` (lớp chuyển đổi), `DFF_MS_TMP`, `DFF_TSPC_TMP` (flip-flop tạm) | `DFF_TSPC_TMP` không còn dùng |
| Testbench | `tb_TSPC_LFSR_8bit`, `tb_TSPC_CFSR_8bit`, `tb_LT_RTPG_8bit` | mô phỏng từ schematic khớp golden model 301/301 |
| **Bản sao** cell TV2 | `TSPC_DFF_S`, `TSPC_DFF_R` | vẽ lại từ netlist của TV2 để mở được schematic khối; **bản gốc là của TV2** |
| **Bản sao** cell TV3 | `INV_X1`, `NAND2_X1`, `NOR2_X1`, `NOR3_X1`, `AOI21_X1`, `XNOR2_X1`, `XOR2_X1`, `XOR2_TG6`, `XORTAP8`, `XORTAP8_CMOS`, `ZERO7`, `CFSR_FB`, `CFSR_FB_OPT` | vẽ lại từ netlist của TV3; **bản gốc là thư viện `TV3_CELLS` của TV3** |

Schematic và symbol được vẽ tự động từ netlist Spectre bằng SKILL (`scripts/cadence/gen_skill.py`, `scripts/cadence/ve_khoi_de_doc.il`), nên luôn khớp với netlist đã mô phỏng. Kiểm tra: 26/26 cell schCheck 0 lỗi 0 cảnh báo. Netlist mới là nguồn chính: khi sửa mạch thì sửa netlist rồi vẽ lại, không sửa tay trong thư viện này.

Ảnh của thư viện: [docs/2_thiet_ke_mach.md](../../docs/2_thiet_ke_mach.md) mục 2.6.

## Thư viện `tv4_lay`

Layout **nhập từ GDS** (`layout/gds/*.gds`, sinh bằng `scripts/layout/build_layout.py`) bằng lệnh:

```bash
strmin -library tv4_lay -strmFile layout/gds/TSPC_LFSR_8bit.gds -attachTechFileOfLib gpdk090 -topCell TSPC_LFSR_8bit
```

Thư viện chỉ có view `layout`, không có schematic đi kèm. LVS so với netlist CDL trong `layout/cdl/` bằng `scripts/layout/assura.sh`. Cell `TSPC_DFF_S`, `TSPC_DFF_R` trong thư viện này là layout của TV2 (GDS `depend/tv2/layout/gds/TV2_TSPC.gds`); `XOR2_TG6`, `XOR2_X1` là layout của TV3.

| Cell | Nội dung |
|---|---|
| `TSPC_LFSR_8bit` | dải TSPC: TSPC_DFF_S + 7 TSPC_DFF_R (TV2) + 2 XOR2_TG6 + XOR2_X1 (TV3), 79,02 × 2,76 µm |
| `MS_LFSR_8bit` | dải MS: INV_CLK + 8 DFF_MS_TMP (flip-flop tạm) + 2 XOR2_TG6 + XOR2_X1, 85,32 × 2,76 µm |
| `TSPC_DFF_S`, `TSPC_DFF_R`, `DFF_MS_TMP`, `INV_CLK`, `XOR2_TG6`, `XOR2_X1` | cell con |

Mở layout thấy cả nội dung cell con: *Options → Display*, đặt *Stop level* = 20 (hoặc bấm Shift+F).
