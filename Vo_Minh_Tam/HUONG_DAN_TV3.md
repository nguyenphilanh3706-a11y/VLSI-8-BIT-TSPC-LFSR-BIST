# Huong dan TV3: cell, testbench, cach mo phong

Cong nghe gpdk090, VDD 1,2 V, L = 0,1 um cho moi transistor. Chan nguon thong nhat cua nhom: VDD, GND.

## 1. Thu muc
| Thu muc | Noi dung |
|---|---|
| `cells/<CELL>/<CELL>.scs` | netlist cell (subckt) |
| `cells/<CELL>/tb_<CELL>.scs`, `.exp` | testbench cell va bang gia tri mong doi |
| `cells/cells.scs` | include chung cac cell co ban |
| `blocks/` | khoi ghep: XORTAP8, ZERO7, CFSR_FB va ban doi chung |
| `tb/` | testbench khoi va testbench so sanh XOR (`*_cmp`), moi cai co ban NN/SS/FF |
| `scripts/` | chay mo phong (`run_cells.sh`, `run_sim.sh`) va kiem tra ket qua (`check.awk`) |

## 2. Gioi thieu cell

### Cong co ban
| Cell | Ham | T | Kich thuoc (W, um) | Ghi chu |
|---|---|---|---|---|
| INV_X1 | Y = !A | 2 | N 0,12 / P 0,24 | P gap doi N de can bang suon len/xuong |
| NAND2_X1 | Y = !(A.B) | 4 | N 0,24 noi tiep / P 0,24 song song | N noi tiep nen rong gap doi |
| NOR2_X1 | Y = !(A+B) | 4 | N 0,12 song song / P 0,48 noi tiep | P noi tiep (p1) rong gap 4 lan N |
| NOR3_X1 | Y = !(A+B+C) | 6 | N 0,12 song song / P 0,48 noi tiep 3 tang | dung trong ZERO7 |

### Cong XOR2 (Y = A ^ B)
| Cell | Kieu | T | Tong W | Nguyen ly |
|---|---|---|---|---|
| XOR2_X1 | CMOS tinh | 12 | 3,60 um | 2 inverter tao An, Bn + cong phuc Y = !(A.B + An.Bn); ngo ra luon duoc keo ve ray |
| XOR2_TG | cong truyen 8T | 8 | 2,16 um | 2 inverter + 2 cong truyen: A=0 cho B qua, A=1 cho Bn qua |
| XOR2_TG6 | cong truyen 6T | 6 | 1,44 um | 1 inverter (An) + 1 cong truyen + cap MP1/MN1 lay nguon tu A/An dao B; cap nay rong gap doi de keo Y nhanh |

XOR2_TG6 it transistor nhat nhung ngo ra khong phuc hoi muc logic, nen khong dat hai tang 6T noi tiep.

### Khoi ghep
| Khoi | Chuc nang | T |
|---|---|---|
| XORTAP8 | FB = Q0 ^ Q5 ^ Q6 ^ Q7 (da thuc 1 + x + x^6 + x^7 + x^8): tang 1 hai XOR2_TG6, tang 2 XOR2_X1 phuc hoi muc | 24 |
| XORTAP8_CMOS | ban doi chung, 3 XOR2_X1 | 36 |
| ZERO7 | Z = 1 khi Q0..Q6 = 0: NOR(NAND(NOR3(Q0,Q1,Q2), NOR3(Q3,Q4,Q5)), Q6) | 20 |
| CFSR_FB | FB = XORTAP8 ^ ZERO7: dua trang thai 00000000 vao chuoi, LFSR 255 -> 256 trang thai | 56 |
| CFSR_FB_CMOS | ban doi chung: XOR CMOS + cay NOR2/NAND2/INV | 74 |

So lieu tre, nang luong va so sanh: `KET_QUA_TV3.md`.

## 3. Testbench

Moi testbench cell co cung cau truc:
- model `gpdk090.scs section=NN` (doi thanh SS / FF cho corner cham / nhanh);
- nguon `Vvdd` 1,2 V, `Vgnd` 0 V;
- ngo vao la nguon PWL, moi vector giu 500 ps, suon 20 ps; day vector di qua moi to hop va moi lan doi mot ngo vao;
- DUT `XDUT`, ngo ra Y tai 4 INV_X1 (FO4);
- phan tich `tran`, `maxstep=1p`, `errpreset=conservative`, luu ngo vao va Y.

| Testbench | Vector |
|---|---|
| tb_INV_X1 | A: 0 1 0 |
| tb_NAND2_X1, tb_NOR2_X1, tb_XOR2_X1, tb_XOR2_TG, tb_XOR2_TG6 | AB: 00 10 00 01 11 10 11 01 00 |
| tb_NOR3_X1 | ABC: 000 100 110 010 011 111 101 001 000 |
| tb/tb_XOR2_*_cmp | 9 vector, ngo vao qua 2 INV dem, co do nang luong |
| tb/tb_XORTAP8*, tb/tb_CFSR_FB* | 16 / 256 to hop, ngo vao qua 2 INV dem |

File `.exp` canh testbench ghi gia tri mong doi cua Y o cuoi moi vector:
```
T 5e-10          chu ky vector (s)
MARGIN 1e-11     lay mau tai (k+1)T - MARGIN
STRICT 1         muc ra phai cach ray <= 10% VDD
OUT Y
V <k> <do tre 0|1> <Y mong doi> ; <mo ta>
```

## 4. Chay mo phong (trong VM, tai thu muc Vo_Minh_Tam)

Mot cell, mot corner:
```
ONLY="NOR3_X1" bash scripts/run_cells.sh NN
```
Tat ca cell, ca 3 corner: `bash scripts/run_cells.sh`. Ket qua: `out/cells/<corner>/<CELL>/tr.tran`, log `spectre.log`.
Dong cuoi `TAT CA CELL: PASS` la dat.

Khoi va testbench so sanh:
```
bash scripts/run_sim.sh tb/tb_CFSR_FB_NN.scs
bash scripts/run_sim.sh tb/tb_XOR2_*_cmp_NN.scs
```
In ra so vector dung, tre lon nhat, nang luong; ket qua o `out/<ten testbench>/`.

Chay tay mot testbench:
```
cd cells/NOR3_X1 && spectre tb_NOR3_X1.scs -raw ../../out/nor3 +log ../../out/nor3.log
cd ../.. && viva -datadir out/nor3 &
```

## 5. Mo phong bang ADE L

1. `cd ~/TV3_PROJ && virtuoso &`, thu vien `TV3_CELLS`.
2. Tao cell `tb_<CELL>` view `schematic`: DUT, 4 INV_X1 tai tren Y, `analogLib/vdc` 1,2 V cho VDD, `vdc` 0 V cho GND,
   `analogLib/vpulse` cho moi ngo vao (v1 0, v2 1.2, tr = tf = 20p), `analogLib/gnd`. Check and Save.
3. Launch -> ADE L. Setup -> Model Libraries: `/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs`, section `NN`.
4. Analyses -> `tran`, stop 1.5n (INV) hoac 4.5n (cong 2-3 ngo vao), `conservative`.
5. Outputs -> To Be Plotted -> chon ngo vao va Y tren schematic. Netlist and Run.
6. Do tre: Calculator -> `delay`, nguong 0,6 V ca hai tin hieu. Session -> Save State de dung lai.
