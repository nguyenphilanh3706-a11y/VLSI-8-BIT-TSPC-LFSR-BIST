# do_suon.py - do suon clock 10-90 % tai chan CLK tu tran.tran (psfascii, co the .gz)
# Dung: python scripts/do_suon.py out/<ten_tb> [out/<ten_tb2> ...]   (Python 2 hoac 3)
import sys, gzip, os
def load(p):
    f = gzip.open(p) if p.endswith(".gz") else open(p)
    t = None; ts = []; vs = []; inval = False
    for line in f:
        if not isinstance(line, str): line = line.decode()
        if not inval:
            if line.startswith("VALUE"): inval = True
            continue
        tok = line.split()
        if len(tok) < 2 or not tok[0].startswith('"'): continue
        n = tok[0].strip('"')
        try: v = float(tok[1])
        except ValueError: continue
        if n == "time": t = v
        elif n == "CLK": ts.append(t); vs.append(v)
    return ts, vs
def cross(ts, vs, lvl, i):
    a, b = vs[i-1], vs[i]
    return ts[i-1] + (lvl - a) * (ts[i] - ts[i-1]) / (b - a)
def meas(ts, vs, t0=5e-9):
    lo, hi = 0.12, 1.08
    r = []; fl = []; st = None; sf = None
    for i in range(1, len(ts)):
        if ts[i] < t0: continue
        a, b = vs[i-1], vs[i]
        if a < lo <= b: st = cross(ts, vs, lo, i)
        if a < hi <= b and st is not None: r.append(cross(ts, vs, hi, i) - st); st = None
        if a > hi >= b: sf = cross(ts, vs, hi, i)
        if a > lo >= b and sf is not None: fl.append(cross(ts, vs, lo, i) - sf); sf = None
    sel = [v for t, v in zip(ts, vs) if t >= t0]
    av = lambda x: sum(x) / len(x) * 1e12 if x else float("nan")
    return av(r), (max(r) * 1e12 if r else float("nan")), av(fl), (max(fl) * 1e12 if fl else float("nan")), min(sel), max(sel), len(r)
for d in sys.argv[1:]:
    p = os.path.join(d, "tran.tran")
    if not os.path.exists(p): p += ".gz"
    if not os.path.exists(p): print("%s KHONG_CO" % d); continue
    ts, vs = load(p)
    print("SUON %s rise_tb=%.1f rise_max=%.1f fall_tb=%.1f fall_max=%.1f vmin=%.3f vmax=%.3f n=%d" % ((os.path.basename(d),) + meas(ts, vs)))
