# Ket qua TV3: cong XOR, mang hoi tiep LFSR, CFSR

Spectre, 27 do C, VDD 1,2 V. Moi ngo vao qua 2 INV_X1 dem (giong ngo ra flip-flop), moi ngo ra tai 4 INV_X1.
Tre = lan cat 0,6 V cuoi cung cua ngo ra, tinh tu giua suon vao, lay lon nhat tren moi vector.
Tong W = tong be rong kenh cua cac transistor (dai dien dien tich truoc khi ve layout).

Chay lai: `bash scripts/run_sim.sh tb/tb_<ten>_<NN|SS|FF>.scs`

## 1. Cong XOR2 (9 vector, duyet moi canh cua 2 ngo vao)

| Cell | Transistor | Tong W | Tre NN | Tre SS | Tre FF | Nang luong NN |
|---|---|---|---|---|---|---|
| XOR2_X1 (CMOS tinh) | 12 | 3,60 um | 136,0 ps | 191,8 ps | 106,3 ps | 0,020 pJ |
| XOR2_TG (cong truyen) | 8 | 2,16 um | 147,4 ps | 207,1 ps | 115,6 ps | 0,021 pJ |
| XOR2_TG6 (6T) | 6 | 1,44 um | 137,6 ps | 194,9 ps | 106,6 ps | 0,019 pJ |

XOR2_TG6 giam 50% transistor va 60% tong W so voi CMOS, tre chi cham hon 1,6 ps (NN), nang luong thap hon 5%.
Kich thuoc chon sau khi quet 8 bo: cap dao B (MN1/MP1) 0,24/0,48 um, cong truyen va inverter nho nhat.
Lam cap dao lon hon nua (0,36/0,72) khong nhanh them ma ton nang luong.

## 2. Mang XOR hoi tiep FB = Q0 ^ Q5 ^ Q6 ^ Q7 (16 to hop)

| Khoi | Transistor | Tong W | Tre NN | Tre SS | Tre FF | Nang luong NN |
|---|---|---|---|---|---|---|
| XORTAP8_CMOS (3 XOR CMOS) | 36 | 10,80 um | 220,0 ps | 312,7 ps | 170,8 ps | 0,029 pJ |
| XORTAP8 (2 XOR 6T + 1 XOR CMOS) | 24 | 6,48 um | 225,0 ps | 321,5 ps | 173,1 ps | 0,026 pJ |

Tang cuoi giu XOR CMOS: hai XOR 6T noi tiep lam suy muc logic, tre tang 25% (do duoc 274,9 ps NN).

## 3. CFSR_FB: hoi tiep day du (256 to hop)

| Khoi | Transistor | Tong W | Tre NN | Tre SS | Tre FF | Nang luong NN |
|---|---|---|---|---|---|---|
| CFSR_FB_CMOS (XOR CMOS, cay NOR2/NAND2) | 74 | 21,48 um | 305,8 ps | 434,6 ps | 237,6 ps | 0,048 pJ |
| CFSR_FB (XORTAP8 + ZERO7 + XOR CMOS) | 56 | 15,84 um | 316,7 ps | 437,3 ps | 250,1 ps | 0,045 pJ |

CFSR_FB giam 24% transistor, 26% tong W, 6% nang luong; o SS (corner quyet dinh tan so) tre chi tang 0,6%.
ZERO7 phat hien Q0..Q6 = 0 bang 2 NOR3 + NAND2 + NOR2 (20T, thay cho 26T).
Cac phuong an da thu va bo: dung XOR 6T ca 4 cong (44T, 468 ps NN), XOR 6T hai tang dau (50T, 326 ps NN).

## 4. Mo hinh chuan
`scripts/lfsr_model.awk`: LFSR (FB = Q0^Q5^Q6^Q7, dich Q0 -> Q7) co 255 trang thai khac nhau;
CFSR co 256 trang thai, gom ca 00000000. Bang gia tri mong doi cua testbench sinh tu cung cong thuc.
NOR3_X1 chua co testbench rieng; moi to hop ngo vao cua no da duoc phu trong 256 vector cua CFSR_FB.
