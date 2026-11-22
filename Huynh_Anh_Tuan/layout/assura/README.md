# Kết quả Assura 4.1 (gpdk090)

Chạy bằng `scripts/layout/assura.sh` trên GDS trong `layout/gds/`, ngày 21/11/2026.

| Cell / dải | DRC (`drc.rul`) | LVS (`extract.rul` + `compare.rul`) |
|---|---|---|
| DFF_TSPC_TMP | 0 lỗi | khớp |
| DFF_MS_TMP | 0 lỗi | khớp |
| INV_CLK | 0 lỗi | khớp |
| TSPC_LFSR_8bit | 0 lỗi | khớp ([`TSPC_LFSR_8bit_lvs.csm`](TSPC_LFSR_8bit_lvs.csm)) |
| MS_LFSR_8bit | 0 lỗi | khớp ([`MS_LFSR_8bit_lvs.csm`](MS_LFSR_8bit_lvs.csm)) |
| XOR2_TG6, XOR2_X1 (GDS của TV3, `depend/tv3/layout/gds/`) | 0 lỗi | khớp |

DRC 0 lỗi nghĩa là file `<cell>.err` của Assura rỗng. LVS so layout với `layout/cdl/<cell>.cdl` (sinh từ netlist Spectre đã mô phỏng); với hai dải, Assura so theo phân cấp: từng cell lá rồi tới cell top.
