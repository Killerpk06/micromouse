"""One-off: append the OLED header (J8) to the existing schematic without touching other UUIDs."""
import os, sys, re
PRJ = sys.argv[1]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen.py'), encoding='utf-8').read()
src = src[:src.index('# ---------------------------------------------------------------- regions')]
g = {'__name__': 'gen_defs', '__file__': __file__}
sys.argv = [sys.argv[0], PRJ]
exec(compile(src, 'gen.py', 'exec'), g)

sch_path = os.path.join(PRJ, 'micromouse.kicad_sch')
txt = open(sch_path, encoding='utf-8').read()
if 'OLED SSD1306' in txt:
    raise SystemExit('already patched')

part = next(p_ for p_ in g['parts'] if 'OLED' in p_['value'])
assert 'OLED' in part['value']
refs = set(re.findall(r'\(reference "(J\d+)"\)', txt))
n = 1
while f'J{n}' in refs: n += 1
part['ref'] = f'J{n}'
g['pwr_count'][0] = 900

# lowest free y in USB & UI region (x 10..250, y 156..400)
ys = [float(m.group(2)) for m in re.finditer(r'\(at ([\d.]+) ([\d.]+)', txt)
      if 10 < float(m.group(1)) < 250 and 156 < float(m.group(2)) < 400]
top = max(ys) + 15
ops, bb = g['plan'](part)
X = g['snap'](30 - bb[0]); Y = g['snap'](top - bb[1])
g['emit'](part, X, Y, ops)
k = g['k']
note = ('OLED module: 0.96in SSD1306 128x64, I2C addr 0x3C, powered from +3V3.\\n'
        'Bus is 2.8 V (pull-ups R18/R19 2.2k to +2V8). REMOVE the module\'s own SCL/SDA pull-ups.\\n'
        'PCB: place J near the MCU, away from ToF I2C/XSHUT routing.')
g['items'].append(f'(text "{note}" (exclude_from_sim no) (at {X + 15} {Y + bb[1]} 0) '
                  f'(effects (font (size 1.27 1.27)) (justify left top)) (uuid {k.q(g["U"]())}))')

i = txt.rindex('\t(sheet_instances')
txt = txt[:i] + '\n'.join(g['items']) + '\n' + txt[i:]
open(sch_path, 'w', encoding='utf-8').write(txt)
print('added', part['ref'], 'at', X, Y, 'items', len(g['items']))
