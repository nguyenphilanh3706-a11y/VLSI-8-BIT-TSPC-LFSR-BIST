#!/usr/bin/env python3
"""gen_tb_cfsr_cmp.py - sinh testbench so sanh 3 khoi hoi tiep CFSR cua TV3 trong thanh ghi TSPC 8 bit.

Moi bien the = TSPC_CFSR_8bit (8 TSPC_DFF_R cua TV2) voi khoi hoi tiep thay doi:
  CMOS / FB / OPT          : CFSR_FB_CMOS (74T) / CFSR_FB (56T) / CFSR_FB_OPT (42T), netlist schematic
  CMOS_rcx / FB_rcx / OPT_rcx : cung khoi, netlist sau layout (Assura RCX) cua TV3
Flip-flop va phan con lai giu nguyen; kich thich, tai va bang .exp giong tb_TSPC_CFSR.
Chay:  python3 scripts/gen_tb_cfsr_cmp.py      ->  tb/cmp_CFSR_<V>.scs, .exp, _NN/_SS/_FF.scs
"""
import os, re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
tb = lambda f: os.path.join(R, 'tb', f)
base = open(tb('tb_TSPC_CFSR.scs')).read()
exp = open(tb('tb_TSPC_CFSR.exp')).read()
sub = re.search(r'subckt TSPC_CFSR_8bit.*?ends TSPC_CFSR_8bit',
                open(os.path.join(R, 'blocks', 'LFSR_8bit.scs')).read(), re.S).group(0)
MODEL = '"/home/buet/cadence/gpdk090_v4.6/models/spectre/gpdk090.scs"'
T3 = '../depend/tv3/'
HEAD = [T3 + 'cells/cells.scs', T3 + 'blocks/XORTAP8.scs']
TAIL = ['../depend/tv2/cells/cells.scs', '../cells/cells.scs', '../blocks/LFSR_8bit.scs', '../blocks/LT_RTPG_8bit.scs']
SCH = [T3 + 'blocks/CFSR_FB.scs', T3 + 'blocks/CFSR_FB_OPT.scs']
RCX = lambda c: T3 + 'layout/rcx/%s_rcx.scs' % c
VAR = {  # ten: (khoi hoi tiep, file khoi)  -- LFSR_8bit.scs can CFSR_FB_OPT nen luon co mot ban
    'CMOS':     ('CFSR_FB_CMOS', SCH),
    'FB':       ('CFSR_FB',      SCH),
    'OPT':      ('CFSR_FB_OPT',  SCH),
    'CMOS_rcx': ('CFSR_FB_CMOS', [RCX('CFSR_FB_CMOS'), T3 + 'blocks/CFSR_FB_OPT.scs']),
    'FB_rcx':   ('CFSR_FB',      [RCX('CFSR_FB'), T3 + 'blocks/CFSR_FB_OPT.scs']),
    'OPT_rcx':  ('CFSR_FB_OPT',  [RCX('CFSR_FB_OPT')]),
}
for v, (fb, blk) in VAR.items():
    n, dut = 'cmp_CFSR_' + v, 'CMP_CFSR_' + v
    s = sub.replace('TSPC_CFSR_8bit', dut).replace('CFSR_FB_OPT', fb)
    note = '// So sanh khoi hoi tiep: %s, %s. Sinh boi scripts/gen_tb_cfsr_cmp.py.' % (
        fb, 'netlist sau layout (RCX cua TV3)' if v.endswith('_rcx') else 'netlist schematic')
    t = base.replace('// Sinh boi scripts/gen_tb.py - khong sua tay (sua gen_tb.py roi chay lai).', note)
    t = t.replace(') TSPC_CFSR_8bit', ') ' + dut).replace('global 0\n', 'global 0\n' + s + '\n', 1)
    open(tb(n + '.scs'), 'w').write(t)
    open(tb(n + '.exp'), 'w').write(exp)
    for c in ('NN', 'SS', 'FF'):
        inc = ''.join('include "%s"\n' % f for f in HEAD + blk + TAIL)
        open(tb('%s_%s.scs' % (n, c)), 'w').write('// %s, corner %s\nsimulator lang=spectre\ninclude %s section=%s\n%sinclude "%s.scs"\n' % (n, c, MODEL, c, inc, n))
print('sinh %d testbench (x3 corner) trong tb/' % len(VAR))
