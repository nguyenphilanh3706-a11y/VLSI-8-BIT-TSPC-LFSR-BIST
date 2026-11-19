# 2. Thiết kế mạch: cell, khối, chân

[← 1. Golden model](1_golden_model.md) · [README](../README.md) · [3. Mô phỏng →](3_mo_phong.md)

Công nghệ gpdk090 (`gpdk090_nmos1v`, `gpdk090_pmos1v`), VDD 1,2 V, L = 0,1 µm cho mọi transistor. Chân nguồn thống nhất của nhóm: `VDD`, `GND`.
Mỗi cell là một file Spectre (`subckt`), ghép theo thứ tự include: model → cell TV3 → `cells/cells.scs` → `blocks/`.

## 2.1. Cell của TV4 (`cells/`)

| Cell | Chân | Chức năng | T |
|---|---|---|---:|
| `INV_CLK` | A Y VDD GND | inverter gấp 4 lần INV_X1 (N 0,48 / P 0,96 µm): đệm clock, tạo CLKB | 2 |
| `AND2_T` | A B Y VDD GND | NAND2_X1 + INV_X1, tính a_i trong LT-RTPG | 6 |
| `MUX2_N` | A B S SB Y VDD GND | Y = S ? B : A bằng 3 NAND2_X1; SB đưa từ ngoài vào để 8 mux dùng chung một inverter | 12 |
| `DFF_MS_TMP` | D CLK CLKB SET RST Q VDD GND | flip-flop master-slave cổng truyền, 4 TG + 4 NOR2 (NOR làm luôn SET/RST) | 24 |
| `DFF_TSPC_TMP` | D CLK SET RST Q VDD GND | flip-flop TSPC 9T (Yuan–Svensson) kích cạnh lên + SET/RST, chưa có keeper | 17 |
| `DFF_MS`, `DFF_TSPC` | như hai dòng trên | **lớp chuyển đổi**: các khối chỉ gọi hai tên này; hiện trỏ tới bản tạm | – |

SET/RST tích cực mức cao, bất đồng bộ. Hai flip-flop `*_TMP` chỉ để ghép và kiểm chứng lõi LFSR trong lúc chờ cell của TV1 (MS) và TV2 (TSPC); không dùng làm số liệu cuối cùng.

**DFF_TSPC_TMP**: tầng 1 p-C2MOS (X = D̅ khi CLK = 0), tầng 2 n-precharge (Y = 1 khi CLK = 0, Y = X̅ khi CLK = 1), tầng 3 n-C2MOS ra QB, cộng một inverter ra Q. pMOS SET đặt sát VDD, nMOS RST̅ đặt sát GND để tránh chia sẻ điện tích vào nút QB khi nhả SET/RST (lỗi này từng làm Q0 chỉ lên ~0,75 V, đã sửa).

## 2.2. Cell của TV3 dùng lại (`deps/tv3/`)

INV_X1, NAND2_X1, NOR2_X1, NOR3_X1, XOR2_X1 (CMOS 12T), XOR2_TG6 (6T) và hai khối:

| Khối | Chức năng | T |
|---|---|---:|
| `XORTAP8` | D0 = Q0 ⊕ Q5 ⊕ Q6 ⊕ Q7: tầng 1 hai XOR2_TG6, tầng 2 XOR2_X1 phục hồi mức | 24 |
| `XORTAP8_CMOS` | cùng hàm, 3 XOR2_X1 (đối chứng) | 36 |
| `CFSR_FB` | D0 = XORTAP8 ⊕ ZERO7(Q0..Q6): thêm trạng thái 0x00 | 56 |

Bản sao lấy từ branch `cell/XOR-CFSR-LOGIC(3)`, commit `86e42ee`, không sửa ([`deps/tv3/NGUON.md`](../deps/tv3/NGUON.md)).

## 2.3. Khối của TV4 (`blocks/`)

| Khối | Chân | Cấu tạo | T | MOS nối clock |
|---|---|---|---:|---:|
| `MS_LFSR_8bit` | CLK RST Q0..Q7 VDD GND | 8 DFF_MS + XORTAP8 + INV_CLK tạo CLKB dùng chung | 218 | 66 |
| `TSPC_LFSR_8bit` | CLK RST Q0..Q7 VDD GND | 8 DFF_TSPC + XORTAP8, chỉ một pha clock | 160 | 32 |
| `TSPC_LFSR_8bit_CMOS` | như trên | 8 DFF_TSPC + XORTAP8_CMOS (đối chứng mạng hồi tiếp) | 172 | 32 |
| `TSPC_CFSR_8bit` | như trên | 8 DFF_TSPC + CFSR_FB, reset về 0x00, 256 trạng thái | 192 | 32 |
| `LT_RTPG_8bit` | Q0..Q7 CLK RST LP V0..V7 VDD GND | mỗi bit: AND2_T + XOR2_X1 + DFF_TSPC (T-FF) + MUX2_N; 1 INV_X1 tạo LPB | 378 | 32 |

Nối dây LFSR (giống nhau ở cả 4 khối):

```text
FF0: D = D0 (từ XORTAP8),  SET = RST, RST = GND   → nạp 1
FF1: D = Q0,               SET = GND, RST = RST   → nạp 0
...
FF7: D = Q6,               SET = GND, RST = RST   → nạp 0
XORTAP8: (Q0, Q5, Q6, Q7) → D0
```

Seed 0x01 nạp bằng chân SET của FF0, nên không cần mạch nạp seed riêng. CFSR không cần seed: reset cả 8 FF về 0, ZERO7 tự đưa chuỗi ra khỏi 0x00.

LT-RTPG: T-FF reset về 0 cùng RST của LFSR. LP = 0 thì V = Q (LFSR thường), LP = 1 thì V = tq (chuỗi ít lật). Ngõ ra V[7:0] đi tới CUT của TV6.

Số transistor và MOS nối clock đếm tự động từ netlist: `python3 scripts/count_tx.py` → [`results/so_transistor.md`](../results/so_transistor.md).

## 2.4. Thay flip-flop tạm

Mọi khối chỉ gọi `DFF_MS` và `DFF_TSPC`, nên khi TV1/TV2 nộp cell chỉ phải sửa hai file:

1. Thêm `include` netlist của TV1/TV2 vào [`cells/cells.scs`](../cells/cells.scs).
2. Trong [`cells/DFF_MS/DFF_MS.scs`](../cells/DFF_MS/DFF_MS.scs) và [`cells/DFF_TSPC/DFF_TSPC.scs`](../cells/DFF_TSPC/DFF_TSPC.scs), đổi dòng instance `X0` sang cell mới, sắp lại thứ tự chân (thêm inverter nếu reset tích cực thấp).
3. Chạy lại `scripts/ngspice/precheck_ngspice.py`, `scripts/run_tv4.sh`, `run_fmax.sh`, `run_slew.sh`, `count_tx.py`; cập nhật [`4_ket_qua.md`](4_ket_qua.md).
4. Trong Virtuoso: mở schematic `tv4/DFF_MS` (hoặc `DFF_TSPC`), đổi master sang cell mới, Check and Save.

Khối, testbench và golden model giữ nguyên.

## 2.5. Schematic và symbol (Virtuoso)

Thư viện `tv4` (gắn gpdk090) có 22 cell: bản sao cell TV3, cell TV4 và 5 khối trên, vẽ tự động từ chính các netlist đã mô phỏng bằng script SKILL ([3. Mô phỏng, mục 3.5](3_mo_phong.md#35-virtuoso-thư-viện-tv4)). Kết quả 19/11/2026: 22/22 cell schCheck 0 lỗi 0 cảnh báo.
