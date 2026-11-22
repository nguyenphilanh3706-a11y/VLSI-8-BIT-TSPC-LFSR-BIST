"""scs2cdl.py - chuyen subckt Spectre (gpdk090) sang CDL cho Assura LVS."""
import re, sys

def parse(files):
    subs = {}
    cur = None
    for f in files:
        for line in open(f):
            line = line.split("//")[0].strip()
            if not line:
                continue
            m = re.match(r"subckt\s+(\S+)\s+(.*)", line)
            if m:
                cur = m.group(1); subs[cur] = {"pins": m.group(2).split(), "body": []}; continue
            if line.startswith("ends"):
                cur = None; continue
            if cur:
                m = re.match(r"(\S+)\s*\(([^)]*)\)\s*(\S+)\s*(.*)", line)
                if m:
                    subs[cur]["body"].append((m.group(1), m.group(2).split(), m.group(3), m.group(4)))
    return subs

def emit(subs, top, out):
    done, lines = set(), []
    def rec(name):
        if name in done: return
        s = subs[name]
        for inst, nets, master, params in s["body"]:
            if master in subs: rec(master)
        done.add(name)
        lines.append(".SUBCKT %s %s" % (name, " ".join(s["pins"])))
        for inst, nets, master, params in s["body"]:
            if master.startswith("gpdk090_"):
                dev = master.replace("gpdk090_", "")
                p = {k.lower(): v for k, v in re.findall(r"(\w+)=(\S+)", params)}
                lines.append("M%s %s %s w=%s l=%s" % (inst, " ".join(nets), dev, p["w"], p["l"]))
            else:
                lines.append("X%s %s %s" % (inst, " ".join(nets), master))
        lines.append(".ENDS")
        lines.append("")
    rec(top)
    open(out, "w").write("\n".join(lines))

if __name__ == "__main__":
    top, out = sys.argv[1], sys.argv[2]
    emit(parse(sys.argv[3:]), top, out)


def flatten(subs, name, inline):
    """tra ve subckt 'name' voi cac instance thuoc 'inline' duoc trai phang (de khop layout phang)."""
    s = subs[name]
    body = []
    for inst, nets, master, params in s["body"]:
        if master in inline:
            sub = subs[master]
            mp = dict(zip(sub["pins"], nets))
            for i2, n2, m2, p2 in sub["body"]:
                body.append((inst + "_" + i2, [mp.get(n, inst + "_" + n) for n in n2], m2, p2))
        else:
            body.append((inst, nets, master, params))
    out = dict(subs)
    out[name] = {"pins": s["pins"], "body": body}
    return out
