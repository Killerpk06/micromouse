"""Generate micromouse.kicad_sch (single flat A2 sheet)."""
import os, sys, math, uuid, json
import kilib as k

PRJ = sys.argv[1]
G = 2.54
U = lambda: str(uuid.uuid4())
ROOT = U()
OLD_UUID = {}
_old = os.path.join(PRJ, 'micromouse.kicad_sch')
if os.path.exists(_old):
    _t = k.parse(open(_old, encoding='utf-8').read())[0]
    ROOT = k.unq(k.find(_t, 'uuid')[0][1])
    for _s in k.find(_t, 'symbol'):
        _ref = [e for e in _s if isinstance(e, list) and e[0] == 'property' and k.unq(e[1]) == 'Reference']
        if _ref:
            OLD_UUID[k.unq(_ref[0][2])] = k.unq(k.find(_s, 'uuid')[0][1])

projlib = k.parse(open(os.path.join(PRJ, 'micromouse.kicad_sym'), encoding='utf-8').read())[0]

def sym(lib_id):
    l, s = lib_id.split(':')
    return k.get_symbol(l, s, projlib if l == 'micromouse' else None)

POWER = {'GND': 'power:GND', '+3V3': 'power:+3V3', '+2V8': 'power:+2V8',
         'VBUS': 'power:VBUS', 'VBAT_SW': 'micromouse:VBAT_SW'}
BODY_UP = {'power:+3V3', 'power:+2V8', 'power:VBUS', 'micromouse:VBAT_SW', 'power:PWR_FLAG'}

# ---------------------------------------------------------------- parts
R06 = 'Resistor_SMD:R_0603_1608Metric'
C06 = 'Capacitor_SMD:C_0603_1608Metric'
C08 = 'Capacitor_SMD:C_0805_2012Metric'
C12 = 'Capacitor_SMD:C_1206_3216Metric'
TAN = 'Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D'
TPF = 'TestPoint:TestPoint_Pad_D1.5mm'
LED = 'LED_SMD:LED_0603_1608Metric'
BTN = 'Button_Switch_SMD:SW_SPST_TL3342'

parts = []  # dicts
def P(region, lib_id, value, fp, nets, mpn='', lcsc='', note=''):
    parts.append(dict(region=region, lib_id=lib_id, value=value, fp=fp, nets=nets, mpn=mpn, lcsc=lcsc, note=note))

def R(region, val, a, b, mpn=''): P(region, 'Device:R', val, R06, {'1': a, '2': b}, mpn)
def C(region, val, a, b, fp=C06, mpn=''): P(region, 'Device:C', val, fp, {'1': a, '2': b}, mpn)
def TP(region, net): P(region, 'Connector:TestPoint', net, TPF, {'1': net})

# ---- POWER
p = 'POWER'
P(p, 'Connector_Generic:Conn_01x02', 'XT60PW-M', 'Connector_AMASS:AMASS_XT60PW-M_1x02_P7.20mm_Horizontal',
  {'1': 'GND', '2': 'VBAT_RAW'}, 'XT60PW-M')
P(p, 'Switch:SW_SPDT', 'PCM12SMTR', 'Button_Switch_SMD:SW_SPDT_PCM12', {'2': 'VBAT_RAW', '1': 'VBAT_SW', '3': 'NC'}, 'PCM12SMTR')
P(p, 'Device:C_Polarized', '100uF 16V', TAN, {'1': 'VBAT_SW', '2': 'GND'})
C(p, '10uF 25V', 'VBAT_SW', 'GND', C12)
P(p, 'Regulator_Switching:AP63203WU', 'AP63203WU-7', 'Package_TO_SOT_SMD:TSOT-23-6',
  {'3': 'VBAT_SW', '2': 'VBAT_SW', '4': 'GND', '5': 'BUCK_SW', '6': 'BUCK_BST', '1': '+3V3'}, 'AP63203WU-7')
C(p, '10uF 25V', 'VBAT_SW', 'GND', C12)            # datasheet C1 at VIN
C(p, '100nF', 'BUCK_BST', 'BUCK_SW')                # datasheet C3 BST-SW
P(p, 'Device:L', '3.9uH', 'Inductor_SMD:L_Taiyo-Yuden_NR-40xx', {'1': 'BUCK_SW', '2': '+3V3'}, 'NR4018T3R9M')
C(p, '22uF 10V', '+3V3', 'GND', C08)                # datasheet C2 2x22uF
C(p, '22uF 10V', '+3V3', 'GND', C08)
R(p, '20k 1%', 'VBAT_SW', 'VBAT_SENSE')
R(p, '10k 1%', 'VBAT_SENSE', 'GND')
C(p, '100nF', 'VBAT_SENSE', 'GND')
R(p, '1k', '+3V3', 'PWR_LED_A')
P(p, 'Device:LED', 'Green', LED, {'2': 'PWR_LED_A', '1': 'GND'})
P(p, 'Regulator_Linear:ME6211C28M5', 'ME6211C28M5G-N', 'Package_TO_SOT_SMD:SOT-23-5',
  {'1': '+3V3', '3': '+3V3', '2': 'GND', '5': '+2V8', '4': 'NC'}, 'ME6211C28M5G-N')
C(p, '1uF', '+3V3', 'GND')
C(p, '1uF', '+2V8', 'GND')
TP(p, 'VBAT_SW'); TP(p, '+3V3'); TP(p, 'GND')

# ---- MCU
p = 'MCU'
mcu = {'1': '+3V3', '24': '+3V3', '36': '+3V3', '48': '+3V3', '9': '+3V3', '23': 'GND', '35': 'GND', '47': 'GND', '8': 'GND',
       '10': 'TOF_XSHUT_FL', '11': 'TOF_XSHUT_FR', '12': 'TOF_XSHUT_L', '13': 'TOF_XSHUT_R', '14': 'BTN_UP', '15': 'BTN_DOWN',
       '16': 'VBAT_SENSE', '17': 'BTN_ADC', '29': 'FAN_PWM', '30': 'BTN_BACK', '31': 'BUZZER', '32': 'USB_DM', '33': 'USB_DP',
       '34': 'SWDIO', '37': 'SWCLK', '38': 'ENC_L_A', '18': 'BTN_ENTER', '19': 'SPARE_PB1', '20': 'BOOT1', '39': 'ENC_L_B',
       '40': 'ENC_R_A', '41': 'ENC_R_B', '42': 'I2C1_SCL', '43': 'I2C1_SDA', '45': 'MOT_PWMA', '46': 'MOT_PWMB', '21': 'MOT_AIN1',
       '22': 'MOT_AIN2', '25': 'FLASH_CS', '26': 'SPI2_SCK', '27': 'SPI2_MISO', '28': 'SPI2_MOSI', '2': 'LED1', '3': 'MOT_BIN1',
       '4': 'MOT_BIN2', '5': 'OSC_IN', '6': 'OSC_OUT', '7': 'NRST', '44': 'BOOT0'}
P(p, 'MCU_ST_STM32F1:STM32F103C8Tx', 'STM32F103C8T6', 'Package_QFP:LQFP-48_7x7mm_P0.5mm', mcu, 'STM32F103C8T6')
for _ in range(3): C(p, '100nF', '+3V3', 'GND')     # VDD 24/36/48
C(p, '4.7uF', '+3V3', 'GND')
C(p, '1uF', '+3V3', 'GND'); C(p, '100nF', '+3V3', 'GND')   # VDDA
C(p, '100nF', '+3V3', 'GND')                        # VBAT pin
P(p, 'Device:Crystal_GND24', '8MHz CL=20pF', 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
  {'1': 'OSC_IN', '3': 'OSC_OUT', '2': 'GND', '4': 'GND'}, 'X322508MSB4SI')
C(p, '30pF C0G', 'OSC_IN', 'GND'); C(p, '30pF C0G', 'OSC_OUT', 'GND')
R(p, '10k', 'BOOT0', 'GND'); TP(p, 'BOOT0')
R(p, '10k', 'BOOT1', 'GND')
P(p, 'Switch:SW_Push', 'RESET', BTN, {'1': 'NRST', '2': 'GND'}, 'TL3342F160QG')
C(p, '100nF', 'NRST', 'GND')
P(p, 'Connector:Conn_ARM_JTAG_SWD_10', 'SWD 1.27mm', 'Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD',
  {'1': '+3V3', '2': 'SWDIO', '3': 'GND', '5': 'GND', '4': 'SWCLK', '6': 'NC', '7': 'NC', '8': 'NC', '9': 'GND', '10': 'NRST'})
P(p, 'Connector_Generic:Conn_01x04', 'SWD ST-Link', 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
  {'1': '+3V3', '2': 'SWDIO', '3': 'SWCLK', '4': 'GND'})
for n in ['BTN_UP', 'BTN_DOWN', 'BTN_BACK', 'BTN_ENTER', 'SPARE_PB1']: TP(p, n)

# ---- MOTORS & ENCODERS
p = 'MOTORS & ENCODERS'
P(p, 'Driver_Motor:TB6612FNG', 'TB6612FNG', 'Package_SO:SSOP-24_5.3x8.2mm_P0.65mm',
  {'24': 'VBAT_SW', '13': 'VBAT_SW', '14': 'VBAT_SW', '20': '+3V3', '19': '+3V3', '18': 'GND', '3': 'GND', '4': 'GND', '9': 'GND',
   '10': 'GND', '23': 'MOT_PWMA', '21': 'MOT_AIN1', '22': 'MOT_AIN2', '15': 'MOT_PWMB', '17': 'MOT_BIN1', '16': 'MOT_BIN2',
   '1': 'MOTL_P', '2': 'MOTL_P', '5': 'MOTL_N', '6': 'MOTL_N', '11': 'MOTR_P', '12': 'MOTR_P', '7': 'MOTR_N', '8': 'MOTR_N'},
  'TB6612FNG,C,8,EL')
C(p, '10uF 25V', 'VBAT_SW', 'GND', C12); C(p, '100nF', 'VBAT_SW', 'GND')
P(p, 'Device:C_Polarized', '47uF 16V', TAN, {'1': 'VBAT_SW', '2': 'GND'})
C(p, '100nF', '+3V3', 'GND')
for n in ['MOT_PWMA', 'MOT_AIN1', 'MOT_AIN2', 'MOT_PWMB', 'MOT_BIN1', 'MOT_BIN2']: R(p, '10k', n, 'GND')
JPH6 = 'Connector_JST:JST_PH_S6B-PH-K_1x06_P2.00mm_Horizontal'
P(p, 'Connector_Generic:Conn_01x06', 'MOTOR_L', JPH6,
  {'1': 'MOTL_P', '2': 'MOTL_N', '3': '+3V3', '4': 'GND', '5': 'ENC_L_A', '6': 'ENC_L_B'}, 'S6B-PH-K-S')
P(p, 'Connector_Generic:Conn_01x06', 'MOTOR_R', JPH6,
  {'1': 'MOTR_P', '2': 'MOTR_N', '3': '+3V3', '4': 'GND', '5': 'ENC_R_A', '6': 'ENC_R_B'}, 'S6B-PH-K-S')
for n in ['ENC_L_A', 'ENC_L_B', 'ENC_R_A', 'ENC_R_B']: R(p, '4.7k', '+3V3', n)
for n in ['ENC_L_A', 'ENC_L_B', 'ENC_R_A', 'ENC_R_B']: C(p, '100pF', n, 'GND')
R(p, '100', 'FAN_PWM', 'FAN_G'); R(p, '100k', 'FAN_G', 'GND')
P(p, 'Transistor_FET:AO3400A', 'AO3400A', 'Package_TO_SOT_SMD:SOT-23', {'1': 'FAN_G', '2': 'GND', '3': 'FAN_N'}, 'AO3400A')
P(p, 'Connector_Generic:Conn_01x02', 'FAN', 'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal',
  {'1': 'VBAT_SW', '2': 'FAN_N'}, 'S2B-PH-K-S')

# ---- IMU & FLASH
p = 'IMU & FLASH'
P(p, 'Sensor_Motion:MPU-6050', 'MPU-6050', 'Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm',
  {'13': '+3V3', '8': '+2V8', '9': 'GND', '11': 'GND', '1': 'GND', '18': 'GND', '10': 'IMU_REGOUT', '20': 'IMU_CPOUT',
   '23': 'I2C1_SCL', '24': 'I2C1_SDA', '12': 'IMU_INT', '6': 'NC', '7': 'NC',
   '2': 'NC', '3': 'NC', '4': 'NC', '5': 'NC', '14': 'NC', '15': 'NC', '16': 'NC', '17': 'NC', '19': 'NC', '21': 'NC', '22': 'NC'},
  'MPU-6050')
C(p, '100nF', '+3V3', 'GND')          # VDD bypass
C(p, '10nF', '+2V8', 'GND')           # VLOGIC bypass
C(p, '100nF', 'IMU_REGOUT', 'GND')
C(p, '2.2nF 50V', 'IMU_CPOUT', 'GND')
TP(p, 'IMU_INT')
P(p, 'Memory_Flash:W25Q32JVSS', 'W25Q32JVSSIQ', 'Package_SO:SOIC-8_5.3x5.3mm_P1.27mm',
  {'1': 'FLASH_CS', '2': 'SPI2_MISO', '5': 'SPI2_MOSI', '6': 'SPI2_SCK', '3': 'FLASH_WP', '7': 'FLASH_HOLD', '8': '+3V3', '4': 'GND'},
  'W25Q32JVSSIQ')
C(p, '100nF', '+3V3', 'GND')
R(p, '10k', '+3V3', 'FLASH_CS'); R(p, '10k', '+3V3', 'FLASH_WP'); R(p, '10k', '+3V3', 'FLASH_HOLD')

# ---- USB & UI
p = 'USB & UI'
P(p, 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
  {'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS', 'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A6': 'USB_C_DP', 'B6': 'USB_C_DP',
   'A7': 'USB_C_DM', 'B7': 'USB_C_DM', 'A8': 'NC', 'B8': 'NC', 'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'USB_SHIELD'},
  'USB4105-GF-A')
R(p, '5.1k', 'USB_CC1', 'GND'); R(p, '5.1k', 'USB_CC2', 'GND')
R(p, '1M', 'USB_SHIELD', 'GND'); C(p, '4.7nF', 'USB_SHIELD', 'GND')
R(p, '22', 'USB_C_DP', 'USB_DP'); R(p, '22', 'USB_C_DM', 'USB_DM')
R(p, '1.5k', '+3V3', 'USB_DP')
R(p, '10k', '+3V3', 'BTN_ADC')
P(p, 'Switch:SW_Push', 'SW_A', BTN, {'1': 'BTN_ADC', '2': 'GND'}, 'TL3342F160QG')
P(p, 'Switch:SW_Push', 'SW_B', BTN, {'1': 'BTN_ADC', '2': 'BTN_B_R'}, 'TL3342F160QG')
R(p, '10k', 'BTN_B_R', 'GND')
C(p, '100nF', 'BTN_ADC', 'GND')
R(p, '1k', '+3V3', 'LED1_A')
P(p, 'Device:LED', 'Blue', LED, {'2': 'LED1_A', '1': 'LED1'})
P(p, 'Device:Buzzer', 'Magnetic 3V', 'Buzzer_Beeper:Buzzer_12x9.5RM7.6', {'1': '+3V3', '2': 'BUZ_N'})
P(p, 'Device:D', '1N4148W', 'Diode_SMD:D_SOD-123', {'1': '+3V3', '2': 'BUZ_N'}, '1N4148W')
P(p, 'Transistor_BJT:MMBT3904', 'MMBT3904', 'Package_TO_SOT_SMD:SOT-23', {'1': 'BUZ_B', '2': 'GND', '3': 'BUZ_N'}, 'MMBT3904')
R(p, '1k', 'BUZZER', 'BUZ_B')
TP(p, 'GND')
for _ in range(4):
    P(p, 'Mechanical:MountingHole_Pad', 'M3', 'MountingHole:MountingHole_3.2mm_M3_Pad_Via', {'1': 'GND'})
for net, sw in [('BTN_UP', 'SW_UP'), ('BTN_DOWN', 'SW_DOWN'), ('BTN_BACK', 'SW_BACK'), ('BTN_ENTER', 'SW_ENTER')]:
    P(p, 'Switch:SW_Push', sw, BTN, {'1': '+3V3', '2': net}, 'TL3342F160QG')   # press = high
    R(p, '10k', net, 'GND'); C(p, '100nF', net, 'GND')                       # idle low + debounce
P(p, 'Connector_Generic:Conn_01x04', 'OLED SSD1306 0.96in', 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
  {'1': 'GND', '2': '+3V3', '3': 'I2C1_SCL', '4': 'I2C1_SDA'}, '',
  note='Off-board 0.96in SSD1306 128x64 I2C module, addr 0x3C. REMOVE module SCL/SDA pull-ups: bus is 2.8V (+2V8 pull-ups R18/R19)')

# ---- RANGE SENSORS
p = 'RANGE SENSORS (ToF)'
R(p, '2.2k', '+2V8', 'I2C1_SCL'); R(p, '2.2k', '+2V8', 'I2C1_SDA')
TP(p, 'I2C1_SCL'); TP(p, 'I2C1_SDA')
for pos in ['FL', 'FR']:
    P(p, 'Sensor_Distance:VL53L0CXV0DH1', 'VL53L0X', 'Sensor_Distance:ST_VL53L1x',
      {'1': '+2V8', '11': '+2V8', '2': 'GND', '3': 'GND', '4': 'GND', '6': 'GND', '12': 'GND', '5': f'TOF_XSHUT_{pos}',
       '7': f'TOF_GPIO1_{pos}', '8': 'NC', '9': 'I2C1_SDA', '10': 'I2C1_SCL'}, 'VL53L0CXV0DH/1')
    C(p, '4.7uF', '+2V8', 'GND'); C(p, '100nF', '+2V8', 'GND')
    R(p, '10k', '+2V8', f'TOF_XSHUT_{pos}')
    TP(p, f'TOF_XSHUT_{pos}'); TP(p, f'TOF_GPIO1_{pos}')
for pos in ['L', 'R']:
    P(p, 'micromouse:VL6180X', 'VL6180X', 'micromouse:ST_VL6180X_LGA-12',
      {'10': '+2V8', '8': '+2V8', '12': 'GND', '9': 'GND', '4': f'TOF_XSHUT_{pos}', '1': f'TOF_GPIO1_{pos}',
       '6': 'I2C1_SDA', '5': 'I2C1_SCL', '2': 'NC', '3': 'NC', '7': 'NC', '11': 'NC'}, 'VL6180XV0NR/1')
    C(p, '4.7uF', '+2V8', 'GND'); C(p, '100nF', '+2V8', 'GND')
    R(p, '47k', '+2V8', f'TOF_XSHUT_{pos}')
    TP(p, f'TOF_XSHUT_{pos}'); TP(p, f'TOF_GPIO1_{pos}')

# ---------------------------------------------------------------- geometry helpers
def rot(x, y, r):
    a = math.radians(r)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)

def r2(v): return round(v, 3)
def sch_pt(X, Y, x, y, r=0):
    xr, yr = rot(x, y, r)
    return r2(X + xr), r2(Y - yr)

def outdir(angle):  # pin angle (tip->body, y-up) -> outward unit vector in screen coords
    a = math.radians(angle + 180)
    return round(math.cos(a)), -round(math.sin(a))

CW = 1.1  # mm per char at 1.27 text

items = []      # s-expr strings
pwr_count = [0]

def eff(justify=None, hide=False, size=1.27):
    s = f'(effects (font (size {size} {size}))'
    if justify: s += f' (justify {justify})'
    return s + ')'

def prop(name, val, x, y, hide=False, justify=None, ang=0):
    h = ' (hide yes)' if hide else ''
    return f'(property {k.q(name)} {k.q(val)} (at {x} {y} {ang}){h} {eff(justify)})'

def place_symbol(lib_id, ref, value, X, Y, r=0, fp='', ds='', desc='', mpn=None, lcsc=None, pins_=(), refpos=None, valpos=None,
                 hide_ref=False, hide_val=False, in_bom=True, on_board=True, valang=0, extra=None):
    rp = refpos or (X, Y)
    vp = valpos or (X, Y)
    s = [f'(symbol (lib_id {k.q(lib_id)}) (at {X} {Y} {r}) (unit 1) (exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) '
         f'(on_board {"yes" if on_board else "no"}) (dnp no) (uuid {k.q(OLD_UUID.get(ref) or U())})']
    s.append(prop('Reference', ref, rp[0], rp[1], hide_ref, rp[2] if len(rp) > 2 else None))
    s.append(prop('Value', value, vp[0], vp[1], hide_val, vp[2] if len(vp) > 2 else None, valang))
    s.append(prop('Footprint', fp, X, Y, True))
    s.append(prop('Datasheet', ds, X, Y, True))
    s.append(prop('Description', desc, X, Y, True))
    if mpn is not None: s.append(prop('MPN', mpn, X, Y, True))
    if lcsc is not None: s.append(prop('LCSC', lcsc, X, Y, True))
    for fk, fv in (extra or {}).items(): s.append(prop(fk, fv, X, Y, True))
    for pn in pins_:
        s.append(f'(pin {k.q(pn)} (uuid {k.q(U())}))')
    s.append(f'(instances (project "micromouse" (path {k.q("/" + ROOT)} (reference {k.q(ref)}) (unit 1))))')
    s.append(')')
    items.append('\n'.join(s))

def wire(x1, y1, x2, y2):
    items.append(f'(wire (pts (xy {r2(x1)} {r2(y1)}) (xy {r2(x2)} {r2(y2)})) (stroke (width 0) (type default)) (uuid {k.q(U())}))')

def label(name, x, y, d):
    ang, just = {(1, 0): (0, 'left bottom'), (-1, 0): (180, 'right bottom'), (0, -1): (90, 'left bottom'), (0, 1): (270, 'right bottom')}[d]
    items.append(f'(label {k.q(name)} (at {r2(x)} {r2(y)} {ang}) (fields_autoplaced yes) {eff(just)} (uuid {k.q(U())}))')

def noconn(x, y):
    items.append(f'(no_connect (at {r2(x)} {r2(y)}) (uuid {k.q(U())}))')

def power(net, x, y, d):
    """power symbol whose pin is at (x,y) with body extending in screen direction d."""
    lib_id = POWER[net]
    body_up = lib_id in BODY_UP
    want = {(0, -1): 90, (1, 0): 0, (-1, 0): 180, (0, 1): 270}[d]
    base = 90 if body_up else 270
    r = (want - base) % 360
    pwr_count[0] += 1
    ref = f'#PWR{pwr_count[0]:03d}'
    vx, vy = x + d[0] * 5.6, y + d[1] * 5.6
    just = None
    if d == (1, 0): just = 'left'
    if d == (-1, 0): just = 'right'
    place_symbol(lib_id, ref, net, r2(x), r2(y), r, refpos=(r2(x), r2(y)), valpos=(r2(vx), r2(vy)) + ((just,) if just else ()) ,
                 valang=90 if r in (90, 270) else 0,
                 hide_ref=True, in_bom=False, on_board=False, pins_=['1'])

def pwr_flag(net, x, y):
    """power symbol at (x,y) + PWR_FLAG wired 5.08 in the other direction."""
    body_up = POWER[net] in BODY_UP
    d = (0, -1) if body_up else (0, 1)
    power(net, x, y, d)
    fy = y - d[1] * 5.08
    wire(x, y, x, fy)
    pwr_count[0] += 1
    fd = (0, -d[1])
    r = 0 if fd == (0, -1) else 180
    place_symbol('power:PWR_FLAG', f'#FLG{pwr_count[0]:03d}', 'PWR_FLAG', x, r2(fy), r, refpos=(x, r2(fy)),
                 valpos=(r2(x), r2(fy + fd[1] * 3.81)), hide_ref=True, in_bom=False, on_board=False, pins_=['1'])

# ---------------------------------------------------------------- per-part layout (relative), bbox
STUB = G

def plan(part):
    """return list of draw-ops relative to origin and bbox (minx,miny,maxx,maxy) in screen coords"""
    s = sym(part['lib_id'])
    pins_ = k.pins(s)
    seen = {}
    ops = []
    bb = [0, 0, 0, 0]
    def ext(x, y):
        bb[0] = min(bb[0], x); bb[1] = min(bb[1], y); bb[2] = max(bb[2], x); bb[3] = max(bb[3], y)
    for num, name, typ, x, y, a in pins_:
        tx, ty = r2(x), r2(-y)
        ext(tx, ty)
        net = part['nets'].get(num)
        if net is None:
            raise SystemExit(f"unassigned pin {part['lib_id']} {num} {name}")
        key = (tx, ty)
        if key in seen:
            if seen[key] != net:
                raise SystemExit(f'stacked pin net mismatch {part["lib_id"]} {num}')
            continue
        seen[key] = net
        d = outdir(a)
        if net == 'NC':
            ops.append(('nc', tx, ty)); continue
        ex, ey = tx + d[0] * STUB, ty + d[1] * STUB
        ops.append(('wire', tx, ty, ex, ey))
        if net in POWER:
            ops.append(('power', net, ex, ey, d))
            ext(ex + d[0] * 7 + d[1] * 2, ey + d[1] * 7 + d[0] * 2); ext(ex - d[1] * 2, ey - d[0] * 2)
            ext(ex + d[0] * 7 - abs(d[1]) * 2, ey + d[1] * 7 - abs(d[0]) * 2)
        else:
            ops.append(('label', net, ex, ey, d))
            L = len(net) * CW + 1
            ext(ex + d[0] * L, ey + d[1] * L)
            ext(ex + abs(d[1]) * 1.5, ey + abs(d[0]) * 1.5); ext(ex - abs(d[1]) * 1.5, ey - abs(d[0]) * 1.5)
    # merge runs of same-net power pins on one edge into a single power symbol
    ends = {(o[2], o[3]): o[1] for o in ops if o[0] in ('power', 'label')}
    groups = {}
    for o in ops:
        if o[0] == 'power':
            d = o[4]
            line = o[3] if d[1] else o[2]
            groups.setdefault((o[1], d, line), []).append(o)
    for (net, d, line), g in groups.items():
        if len(g) < 2: continue
        along = (lambda o: o[2]) if d[1] else (lambda o: o[3])
        g.sort(key=along)
        run = [g[0]]
        def flush(run):
            if len(run) < 2: return
            a0, a1 = along(run[0]), along(run[-1])
            for (px, py), nn in ends.items():
                pa, pl = (px, py) if d[1] else (py, px)
                if abs(pl - line) < 0.01 and a0 < pa < a1 and nn != net:
                    return
            for o in run[1:]:
                ops.remove(o)
            pts = [along(o) for o in run]
            for i in range(len(pts) - 1):
                if d[1]: ops.append(('wire', pts[i], line, pts[i + 1], line))
                else: ops.append(('wire', line, pts[i], line, pts[i + 1]))
            for pmid in pts[1:-1] + [pts[0]]:
                ops.append(('junction', pmid, line) if d[1] else ('junction', line, pmid))
        for o in g[1:]:
            if along(o) - along(run[-1]) <= 5.09: run.append(o)
            else: flush(run); run = [o]
        flush(run)
    # body extents from graphics are inside pin extents for these symbols; ref/value text
    two_vert = len(seen) == 2 and all(abs(x) < 0.01 for (x, y) in seen)
    vlen = max(len(part['value']), 4) * CW
    if two_vert or part['lib_id'] in ('Connector:TestPoint', 'Mechanical:MountingHole_Pad'):
        ops.append(('text_side',))
        ext(2.54 + vlen + 2, 0)
        ext(-1.5, 0)
    else:
        top = bb[1]
        ops.append(('text_top', bb[0], top))
        ext(bb[0] + vlen + 6, top - 5.5)
    return ops, bb

def snap(v): return round(v / 1.27) * 1.27

def emit(part, X, Y, ops):
    s = sym(part['lib_id'])
    pin_nums = sorted({p_[0] for p_ in k.pins(s)}, key=lambda t: (len(t), t))
    ref = part['ref']
    refpos = valpos = None
    for op in ops:
        if op[0] == 'nc': noconn(X + op[1], Y + op[2])
        elif op[0] == 'junction': items.append(f'(junction (at {r2(X + op[1])} {r2(Y + op[2])}) (diameter 0) (color 0 0 0 0) (uuid {k.q(U())}))')
        elif op[0] == 'wire': wire(X + op[1], Y + op[2], X + op[3], Y + op[4])
        elif op[0] == 'power': power(op[1], X + op[2], Y + op[3], op[4])
        elif op[0] == 'label': label(op[1], X + op[2], Y + op[3], op[4])
        elif op[0] == 'text_side':
            refpos = (r2(X + 2.54), r2(Y - 1.27), 'left'); valpos = (r2(X + 2.54), r2(Y + 1.27), 'left')
            if part['lib_id'] == 'Connector:TestPoint':
                refpos = (r2(X + 2.54), r2(Y - 3.81), 'left'); valpos = (r2(X + 2.54), r2(Y - 1.27), 'left')
        elif op[0] == 'text_top':
            refpos = (r2(X + op[1]), r2(Y + op[2] - 3.81), 'left'); valpos = (r2(X + op[1]), r2(Y + op[2] - 1.27), 'left')
    place_symbol(part['lib_id'], ref, part['value'], X, Y, 0, fp=part['fp'], ds=k.prop(s, 'Datasheet') or '',
                 desc=k.prop(s, 'Description') or '', mpn=part['mpn'], lcsc=part['lcsc'], pins_=pin_nums,
                 refpos=refpos, valpos=valpos, extra={'Note': part['note']} if part['note'] else None)

# ---------------------------------------------------------------- regions (A1: 841 x 594)
REG = {
    'POWER':               (10, 10, 400, 150),
    'MOTORS & ENCODERS':   (406, 10, 831, 150),
    'USB & UI':            (10, 156, 250, 400),
    'MCU':                 (256, 156, 560, 400),
    'IMU & FLASH':         (566, 156, 831, 400),
    'RANGE SENSORS (ToF)': (10, 406, 831, 545),
}

# references
prefix = {'Device:R': 'R', 'Device:C': 'C', 'Device:C_Polarized': 'C', 'Device:L': 'L', 'Device:LED': 'D', 'Device:D': 'D',
          'Connector:TestPoint': 'TP', 'Mechanical:MountingHole_Pad': 'H', 'Switch:SW_Push': 'SW', 'Switch:SW_SPDT': 'SW',
          'Device:Crystal_GND24': 'Y', 'Device:Buzzer': 'BZ', 'Transistor_FET:AO3400A': 'Q', 'Transistor_BJT:MMBT3904': 'Q'}
cnt = {}
order = ['POWER', 'MCU', 'MOTORS & ENCODERS', 'RANGE SENSORS (ToF)', 'IMU & FLASH', 'USB & UI']
for rg in order:
    for part in [x for x in parts if x['region'] == rg]:
        pre = prefix.get(part['lib_id'], 'J' if part['lib_id'].startswith('Connector') else 'U')
        cnt[pre] = cnt.get(pre, 0) + 1
        part['ref'] = f'{pre}{cnt[pre]}'

# PWR_FLAG placement spots inside POWER region (bottom-right corner)
flag_nets = ['GND', '+3V3', 'VBAT_SW', 'VBUS']

for rg, (x0, y0, x1, y1) in REG.items():
    items.append(f'(rectangle (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.4) (type dash)) (fill (type none)) (uuid {k.q(U())}))')
    items.append(f'(text {k.q(rg)} (exclude_from_sim no) (at {x0 + 2} {y0 + 6} 0) (effects (font (size 3 3) (thickness 0.6) (bold yes)) (justify left bottom)) (uuid {k.q(U())}))')
    cx, cy = x0 + 6, y0 + 12
    rowh = 0
    plist = [x for x in parts if x['region'] == rg]
    for part in plist:
        ops, bb = plan(part)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        if cx + w > x1 - 4:
            cx = x0 + 6; cy += rowh + 4; rowh = 0
        X = snap(cx - bb[0] + 1.27); Y = snap(cy - bb[1] + 1.27)
        if Y + bb[3] > y1:
            print('WARNING overflow', rg, part['ref'], round(Y + bb[3], 1), file=sys.stderr)
        emit(part, X, Y, ops)
        part['pos'] = (X, Y)
        cx = X + bb[2] + 5
        rowh = max(rowh, h + 2.54)
    if rg == 'POWER':
        fx = x1 - 4 * 12.7
        for i, n in enumerate(flag_nets):
            pwr_flag(n, snap(fx + i * 12.7), snap(y1 - 12.7))

# ---------------------------------------------------------------- lib_symbols
used = sorted({p_['lib_id'] for p_ in parts} | set(POWER.values()) | {'power:PWR_FLAG'})
libsyms = '\n'.join(k.dump(sym(u)) for u in used)

title = ('(title_block (title "Micromouse main board") (date "2026-10-27") (rev "A") (company "")'
         ' (comment 1 "STM32F103C8T6, TB6612FNG, 4x ToF (2x VL53L0X + 2x VL6180X on +2V8 I2C domain), MPU-6050, W25Q32JV")'
         ' (comment 2 "Firmware: SWJ_CFG=SWD only, TIM2 partial remap 1, TIM3 partial remap, I2C1 default; TOF_XSHUT_* = open-drain"))')
out = (f'(kicad_sch (version 20250610) (generator "eeschema") (generator_version "9.99") (uuid {k.q(ROOT)}) (paper "A1")\n'
       f'{title}\n(lib_symbols\n{libsyms}\n)\n' + '\n'.join(items) +
       '\n(sheet_instances (path "/" (page "1")))\n(embedded_fonts no)\n)\n')
open(os.path.join(PRJ, 'micromouse.kicad_sch'), 'w', encoding='utf-8').write(out)

pro = {"meta": {"filename": "micromouse.kicad_pro", "version": 3}, "sheets": [[ROOT, "Root"]],
       "schematic": {"drawing": {"default_line_thickness": 6.0}}, "boards": [], "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []}}
open(os.path.join(PRJ, 'micromouse.kicad_pro'), 'w').write(json.dumps(pro, indent=2))
json.dump([{k_: v for k_, v in p_.items() if k_ != 'pos'} for p_ in parts], open(os.path.join(os.path.dirname(__file__), 'parts.json'), 'w'), indent=1)
print('parts', len(parts), 'items', len(items))
