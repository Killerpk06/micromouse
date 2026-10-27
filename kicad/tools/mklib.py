"""Create project-local symbol lib, footprint lib, lib tables and project file."""
import os, sys, json, uuid
import kilib as k

PRJ = sys.argv[1]

def eff(hide=False, justify=None):
    s = '(effects (font (size 1.27 1.27))'
    if justify: s += f' (justify {justify})'
    s += ')'
    return s + (' (hide yes)' if hide else '')

def prop(name, val, x, y, hide=False, justify=None):
    return f'(property {k.q(name)} {k.q(val)} (at {x} {y} 0) {eff(hide, justify)})'

# ---------------- VL6180X symbol ----------------
pins = [  # num, name, type, x, y, angle
    ('1', 'GPIO1', 'open_collector', -10.16, 5.08, 0),
    ('6', 'SDA', 'bidirectional', -10.16, 0, 0),
    ('5', 'SCL', 'input', -10.16, -2.54, 0),
    ('4', 'GPIO0/CE', 'input', -10.16, -7.62, 0),
    ('10', 'AVDD', 'power_in', 0, 12.7, 270),
    ('8', 'AVDD_VCSEL', 'power_in', 2.54, 12.7, 270),
    ('12', 'AVSS', 'power_in', 0, -12.7, 90),
    ('9', 'AVSS_VCSEL', 'power_in', 2.54, -12.7, 90),
    ('2', 'NC', 'no_connect', 7.62, 5.08, 180),
    ('3', 'NC', 'no_connect', 7.62, 2.54, 180),
    ('7', 'NC', 'no_connect', 7.62, 0, 180),
    ('11', 'NC', 'no_connect', 7.62, -2.54, 180),
]
pin_s = ''
for n, nm, t, x, y, a in pins:
    style = 'line'
    ln = 0 if t == 'no_connect' else 2.54
    if t == 'no_connect':
        style = 'line'
    pin_s += (f'(pin {t} {style} (at {x} {y} {a}) (length {ln}) (hide {"yes" if t=="no_connect" else "no"}) '
              f'(name {k.q(nm)} {eff()}) (number {k.q(n)} {eff()}))\n')
vl = f'''(symbol "VL6180X" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
 {prop("Reference","U",-7.62,13.97,justify="left")}
 {prop("Value","VL6180X",2.54,13.97,justify="left")}
 {prop("Footprint","micromouse:ST_VL6180X_LGA-12",0,-16.51,True)}
 {prop("Datasheet","https://www.st.com/resource/en/datasheet/vl6180x.pdf",0,-19.05,True)}
 {prop("Description","Proximity and ambient light sensing (ALS) ToF module, I2C, 2.6-3.0V, LGA-12 4.8x2.8mm",0,-21.59,True)}
 (symbol "VL6180X_0_1" (rectangle (start -7.62 10.16) (end 7.62 -10.16) (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "VL6180X_1_1"
 {pin_s} )
 (embedded_fonts no))'''

# ---------------- VBAT_SW power symbol (clone of power:+3V3) ----------------
p3 = k.get_symbol('power', '+3V3')
txt = k.dump(p3).replace('"power:+3V3"', '"VBAT_SW"').replace('"+3V3_', '"VBAT_SW_')
txt = txt.replace('(property "Value" "+3V3"', '(property "Value" "VBAT_SW"')
txt = txt.replace('label with name \\"+3V3\\"', 'label with name \\"VBAT_SW\\"')

lib = '(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n' + vl + '\n' + txt + '\n)\n'
open(os.path.join(PRJ, 'micromouse.kicad_sym'), 'w', encoding='utf-8').write(lib)

# ---------------- VL6180X footprint ----------------
os.makedirs(os.path.join(PRJ, 'micromouse.pretty'), exist_ok=True)
pads = ''
for i in range(6):
    x = round(-1.875 + 0.75 * i, 3)
    pads += f'(pad "{i+1}" smd rect (at {x} 1) (size 0.55 0.6) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
    pads += f'(pad "{12-i}" smd rect (at {x} -1) (size 0.55 0.6) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
def line(x1, y1, x2, y2, layer, w):
    return f'(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (layer "{layer}"))\n'
g = ''
bx, by = 2.4, 1.4
for a, b in [((-bx, -by), (bx, -by)), ((bx, -by), (bx, by)), ((bx, by), (-bx, by)), ((-bx, by), (-bx, -by))]:
    g += line(*a, *b, 'F.Fab', 0.1)
cx, cy = 2.65, 1.65
for a, b in [((-cx, -cy), (cx, -cy)), ((cx, -cy), (cx, cy)), ((cx, cy), (-cx, cy)), ((-cx, cy), (-cx, -cy))]:
    g += line(*a, *b, 'F.CrtYd', 0.05)
sx, sy = 2.51, 1.51
g += line(-sx, -sy, sx, -sy, 'F.SilkS', 0.12) + line(sx, sy, -sx, sy, 'F.SilkS', 0.12)
g += line(-sx, -sy, -sx, sy, 'F.SilkS', 0.12) + line(sx, -sy, sx, sy, 'F.SilkS', 0.12)
g += '(fp_circle (center -2.2 1.9) (end -2.1 1.9) (stroke (width 0.2) (type solid)) (fill solid) (layer "F.SilkS"))\n'
fp = f'''(footprint "ST_VL6180X_LGA-12" (version 20241229) (generator "pcbnew") (generator_version "9.0") (layer "F.Cu")
(descr "ST VL6180X ToF/ALS module, LGA-12, 4.8x2.8mm, pitch 0.75mm, land pattern per DocID026171 Rev 6 Fig.4 (pads 0.55x0.60, row gap 1.40)")
(tags "VL6180X LGA-12 ToF")
(property "Reference" "REF**" (at 0 -2.6 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
(property "Value" "ST_VL6180X_LGA-12" (at 0 2.6 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1))))
(property "Datasheet" "https://www.st.com/resource/en/datasheet/vl6180x.pdf" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1))))
(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1))))
(attr smd)
(fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))
{g}{pads}(embedded_fonts no))
'''
open(os.path.join(PRJ, 'micromouse.pretty', 'ST_VL6180X_LGA-12.kicad_mod'), 'w', encoding='utf-8').write(fp)

open(os.path.join(PRJ, 'sym-lib-table'), 'w').write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "micromouse")(type "KiCad")(uri "${KIPRJMOD}/micromouse.kicad_sym")(options "")(descr "Project symbols"))\n)\n')
open(os.path.join(PRJ, 'fp-lib-table'), 'w').write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "micromouse")(type "KiCad")(uri "${KIPRJMOD}/micromouse.pretty")(options "")(descr "Project footprints"))\n)\n')
print('libs written')
