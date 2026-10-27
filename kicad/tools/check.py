"""Compare intended pin->net map (parts.json) with KiCad-exported netlist."""
import json, sys, os, collections
import xml.etree.ElementTree as ET
d = os.path.dirname(os.path.abspath(__file__))
parts = json.load(open(os.path.join(d, 'parts.json')))
root = ET.parse(os.path.join(d, 'net.xml')).getroot()
actual = {}
netpins = collections.defaultdict(list)
for net in root.iter('net'):
    nm = net.get('name').lstrip('/')
    for n in net.iter('node'):
        actual[(n.get('ref'), n.get('pin'))] = nm
        netpins[nm].append(n.get('ref') + '.' + n.get('pin'))
comps = {c.get('ref'): c for c in root.iter('comp')}
bad = 0
for p in parts:
    ref = p['ref']
    if ref not in comps:
        print('MISSING comp', ref); bad += 1; continue
    c = comps[ref]
    fp = c.findtext('footprint')
    if fp != p['fp']:
        print('FP mismatch', ref, fp, p['fp']); bad += 1
    for pin, net in p['nets'].items():
        a = actual.get((ref, pin))
        if net == 'NC':
            if a and not a.startswith('unconnected-'):
                print('NC pin connected', ref, pin, a); bad += 1
            continue
        if a != net:
            print('NET mismatch', ref, pin, 'want', net, 'got', a); bad += 1
# nets with a single pin
for nm, ps in sorted(netpins.items()):
    if len(ps) < 2 and not nm.startswith('unconnected-'):
        print('single-pin net', nm, ps)
print('components', len(comps), 'nets', len(netpins), 'errors', bad)
if len(sys.argv) > 1:
    for nm in sorted(netpins):
        if not nm.startswith('unconnected-'):
            print(f'{nm:14s} {len(netpins[nm]):3d}  ' + ' '.join(sorted(netpins[nm]))[:200])
