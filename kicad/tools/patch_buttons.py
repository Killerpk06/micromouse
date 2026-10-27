"""One-off: 4 menu buttons (pull-down, switch to +3V3) on PA4/PA5/PA9/PB0. Keeps existing UUIDs."""
import os, sys, re
PRJ = sys.argv[1]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen.py'), encoding='utf-8').read()
src = src[:src.index('# ---------------------------------------------------------------- regions')]
g = {'__name__': 'gen_defs', '__file__': __file__}
sys.argv = [sys.argv[0], PRJ]
exec(compile(src, 'gen.py', 'exec'), g)
k = g['k']

sch_path = os.path.join(PRJ, 'micromouse.kicad_sch')
txt = open(sch_path, encoding='utf-8').read()
if '"BTN_UP"' in txt:
    raise SystemExit('already patched')

RENAME = {'SPARE_PA4': 'BTN_UP', 'SPARE_PA5': 'BTN_DOWN', 'SPARE_PA9': 'BTN_BACK', 'SPARE_PB0': 'BTN_ENTER'}
for old, new in RENAME.items():
    n1 = txt.count(f'(label "{old}"'); n2 = txt.count(f'"Value" "{old}"')
    assert n1 == 2 and n2 == 1, (old, n1, n2)
    txt = txt.replace(f'(label "{old}"', f'(label "{new}"').replace(f'"Value" "{old}"', f'"Value" "{new}"')

def nextref(pre):
    nums = [int(n) for n in re.findall(rf'\(reference "{pre}(\d+)"\)', txt)]
    return max(nums) + 1

new = []
nr, nc, ns = nextref('R'), nextref('C'), nextref('SW')
for net, swname in [('BTN_UP', 'SW_UP'), ('BTN_DOWN', 'SW_DOWN'), ('BTN_BACK', 'SW_BACK'), ('BTN_ENTER', 'SW_ENTER')]:
    new.append(dict(lib_id='Switch:SW_Push', value=swname, fp=g['BTN'], nets={'1': '+3V3', '2': net}, mpn='TL3342F160QG',
                    lcsc='', note='', ref=f'SW{ns}')); ns += 1
    new.append(dict(lib_id='Device:R', value='10k', fp=g['R06'], nets={'1': net, '2': 'GND'}, mpn='', lcsc='', note='',
                    ref=f'R{nr}')); nr += 1
    new.append(dict(lib_id='Device:C', value='100nF', fp=g['C06'], nets={'1': net, '2': 'GND'}, mpn='', lcsc='', note='',
                    ref=f'C{nc}')); nc += 1

g['pwr_count'][0] = 950
ys = [float(m.group(2)) for m in re.finditer(r'\(at ([\d.]+) ([\d.]+)', txt)
      if 10 < float(m.group(1)) < 250 and 156 < float(m.group(2)) < 400]
cx, cy = 20.0, max(ys) + 12
rowh = 0
for part in new:
    ops, bb = g['plan'](part)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    if cx + w > 246:
        cx = 20.0; cy += rowh + 4; rowh = 0
    X = g['snap'](cx - bb[0] + 1.27); Y = g['snap'](cy - bb[1] + 1.27)
    assert Y + bb[3] < 400, 'region overflow'
    g['emit'](part, X, Y, ops)
    cx = X + bb[2] + 5; rowh = max(rowh, h + 2.54)
g['items'].append(f'(text "Menu buttons: idle LOW (10k pull-down + 100nF), press = +3V3. ENTER = FRONT." (exclude_from_sim no) '
                  f'(at 20 {g["r2"](max(ys) + 8)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {k.q(g["U"]())}))')

i = txt.rindex('\t(sheet_instances')
txt = txt[:i] + '\n'.join(g['items']) + '\n' + txt[i:]
open(sch_path, 'w', encoding='utf-8').write(txt)
print('added', [p['ref'] for p in new])
