#!/usr/bin/env python3
"""misr_bilbo_tv5.py - chu ky MISR chuan (golden) cho thanh ghi BILBO_8BIT cua TV5, tinh tu golden model TV4.

Chuoi vector V(t) (ngo ra LFSR TSPC_LFSR_8bit, LP = 0; hoac LT_RTPG_8bit, LP = 1) -> CUT cong 4 bit
(A = V[3:0], B = V[7:4], Cin = 0, Z = {Cout,S3,S2,S1,S0} vao D4..D0 cua MISR, D7..D5 = 0) -> MISR 8 bit, 255 chu ky.

Hai cau truc MISR:
  'TV4' : Q(t+1) = buoc_LFSR(Q) xor Z        (cau truc dung trong golden model TV4, ban 15/11)
  'TV5' : Q_i(t+1) = D_i xor NOT(S_i), S_0 = Q0^Q5^Q6^Q7, S_i = Q_(i-1)   (BILBO_8BIT cua TV5, che do Test C1C0 = 01)
Ca hai reset ve 0x00 truoc chu ky dau. Chay:  python3 misr_bilbo_tv5.py
"""
N, TAPS, SEED, M = 8, (0, 5, 6, 7), 0x01, 0xFF


def lfsr_step(s):
    f = 0
    for t in TAPS:
        f ^= (s >> t) & 1
    return ((s << 1) & M) | f


def lfsr_seq(n=300):
    S = [SEED]
    for _ in range(n):
        S.append(lfsr_step(S[-1]))
    return S


def lt_rtpg(Q, k=2):
    V, v = [], 0
    for q in Q:
        V.append(v)
        a = 0
        for i in range(N):
            x = 1
            for j in range(k):
                x &= (q >> ((i + j) % N)) & 1
            a |= x << i
        v ^= a
    return V


def cut(v):
    return ((v & 15) + (v >> 4)) & 31


def misr(z, kind):
    s = 0
    for zz in z:
        if kind == "TV4":
            s = lfsr_step(s) ^ zz
        else:  # TV5: D xor NOT(S), S = Q dich 1 bit co hoi tiep
            s = zz ^ (~lfsr_step(s) & M)
    return s


S = lfsr_seq()
V2 = lt_rtpg(S, 2)
# Cach A (golden model TV4): MISR nhan Z cua V(1)..V(255) (vector sau canh clock 1..255).
# Cach B (phan cung reset chung, nha chung): o canh thu t MISR chot Z cua V(t-1) -> nhan V(0)..V(254), V(0) = seed 0x01 (LP=0) / 0x00 (LP=1).
modes = {"LP0_A": S[1:256], "LP1_A": V2[1:256], "LP0_B": S[0:255], "LP1_B": V2[0:255]}
names = ["S0", "S1", "S2", "S3", "Cout"]
out = ["# Chu ky MISR 8 bit sau 255 chu ky (reset 0x00), CUT = cong 4 bit, Z -> D4..D0",
       "cau_truc,che_do,loi,chu_ky_hex,ket_qua"]
for kind in ("TV4", "TV5"):
    for m, vec in modes.items():
        zg = [cut(v) for v in vec]
        good = misr(zg, kind)
        out.append("%s,%s,khong_loi,%02X," % (kind, m, good))
        det = 0
        for i in range(5):
            for sv in (0, 1):
                z = [(x & ~(1 << i)) | (sv << i) for x in zg]
                sig = misr(z, kind)
                det += sig != good
                out.append("%s,%s,%s_SA%d,%02X,%s" % (kind, m, names[i], sv, sig, "PHAT HIEN" if sig != good else "ALIASING"))
        print("%s %-10s chu ky dung 0x%02X, phat hien %d/10 loi" % (kind, m, good, det))
open("chu_ky_misr.csv", "w").write("\n".join(out) + "\n")
# vector LFSR va CUT tung chu ky cho TV5/TV6 doi chieu
with open("vector_lfsr_cut_misr.csv", "w") as f:
    f.write("# Cach B: canh clock thu t, MISR chot Z(V(t-1)); cot MISR = gia tri MISR TV5 ngay sau canh t\ncanh_clock,V_LP0_hex,Z_LP0_hex,MISR_TV5_LP0_hex,V_LP1_hex,Z_LP1_hex,MISR_TV5_LP1_hex\n")
    s0 = s1 = 0
    for t, (a, b) in enumerate(zip(modes["LP0_B"], modes["LP1_B"]), 1):
        s0 = cut(a) ^ (~lfsr_step(s0) & M); s1 = cut(b) ^ (~lfsr_step(s1) & M)
        f.write("%d,%02X,%02X,%02X,%02X,%02X,%02X\n" % (t, a, cut(a), s0, b, cut(b), s1))
