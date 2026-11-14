# Ket qua mo phong TV3 (Spectre, 27 do C, VDD 1.2 V, tai 4x INV_X1)

Chay: `bash scripts/run_sim.sh tb/tb_<ten>_<NN|SS|FF>.scs` (xem README goc).

## Cong XOR2: CMOS 12T so voi cong truyen 8T
Cung bo kich thich 9 vector (moi canh cua khoi lap phuong 2 ngo vao); moi ngo vao qua 2 INV_X1 dem.
Tre la lan cat 0,6 V cuoi cung cua Y tinh tu giua suon vao; nang luong tinh tren ca phan dem.

| Cell | Transistor | Vector dung | Tre NN | Tre SS | Tre FF | Nang luong/vector NN |
|---|---|---|---|---|---|---|
| XOR2_X1 (CMOS) | 12 | 9/9 | 136,0 ps | 191,8 ps | 106,3 ps | 0,020 pJ |
| XOR2_TG | 8 | 9/9 | 147,4 ps | 207,1 ps | 115,6 ps | 0,021 pJ |

XOR2_TG it hon 4 transistor (giam 33%) nhung cham hon khoang 8% o ca ba corner va nang luong tuong duong.

## Mang XOR hoi tiep FB = Q0 ^ Q5 ^ Q6 ^ Q7 (16 to hop, NN)
| Khoi | Vector dung | Tre |
|---|---|---|
| XORTAP8 (XOR CMOS) | 16/16 | 161,4 ps |
| XORTAP8_TG (XOR TG) | 16/16 | 130,5 ps |

Luu y: ngo vao cua phep do nay la nguon ly tuong, khong qua dem, nen cong truyen duoc loi.
So sanh o muc cell (bang tren, co dem) moi phan anh dung tai that.

## CFSR_FB (hoi tiep day du, 256 to hop)
| Corner | Vector dung | Tre |
|---|---|---|
| NN | 256/256 | 239,4 ps |
| SS | 256/256 | 340,4 ps |
| FF | 256/256 | 185,7 ps |

Mo hinh chuan (`scripts/lfsr_model.awk`): LFSR 255 trang thai khac nhau, CFSR 256 trang thai (gom 00000000).
