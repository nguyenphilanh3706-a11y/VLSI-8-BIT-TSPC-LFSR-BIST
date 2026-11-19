# lfsr_model.awk -- mo hinh chuan LFSR 8 bit, dich Q0 -> Q7, hoi tiep vao Q0.
#   awk -v mode=lfsr -v seed=1 -f scripts/lfsr_model.awk      # dem chu ky, in chuoi trang thai (hex)
#   awk -v mode=cfsr -v seed=0 -f scripts/lfsr_model.awk
# mode=lfsr: FB = Q0^Q5^Q6^Q7 (255 trang thai, toan 0 la trang thai chet)
# mode=cfsr: them ^ NOR(Q0..Q6) (256 trang thai, co ca trang thai toan 0)
function bit(s, i) { return int(s / 2 ^ i) % 2 }
function fb(s,   f, z, i) {
    f = (bit(s, 0) + bit(s, 5) + bit(s, 6) + bit(s, 7)) % 2
    if (mode == "cfsr") { z = 1; for (i = 0; i < 7; i++) if (bit(s, i)) z = 0; f = (f + z) % 2 }
    return f
}
function next_state(s) { return (s * 2) % 256 + fb(s) }
BEGIN {
    s = seed + 0; start = s; n = 0
    do { printf "%02X%s", s, (++n % 16 ? " " : "\n"); seen[s]++; s = next_state(s) } while (s != start && n < 1000)
    printf "\nchu ky %d, %d trang thai khac nhau, quay ve %02X: %s\n", n, length(seen), start, (s == start ? "dong" : "khong dong")
}
