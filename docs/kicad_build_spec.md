# Micromouse main board — KiCad schematic build spec (STM32F103C8T6, ToF sensing)

> Rebuilt from the original build prompt (`micromouse_kicad_prompt.md`, which was not available as a file). Later change requests are kept verbatim in the appendices at the end.

You are designing the complete schematic (with footprints assigned) for a classic-size micromouse robot in KiCad, using the KiCad MCP tools. Build it block by block, run ERC after each block, and do not move on until it is clean. When something in this spec conflicts with a datasheet, the datasheet wins — fix it and tell me what you changed.

## 0. Project setup

- Project name: `micromouse`
- KiCad 8 (or whatever version is installed)
- **Single flat schematic sheet** (`micromouse.kicad_sch`) — no hierarchical sub-sheets. Use an A3 (or larger) page.
- Lay the sheet out in clearly separated, boxed and titled regions (graphic rectangle + text label for each):
  1. POWER (top-left)
  2. MCU (center)
  3. MOTORS & ENCODERS (top-right)
  4. RANGE SENSORS (ToF, bottom, full width)
  5. IMU & FLASH (right of MCU)
  6. USB & UI (left of MCU)
- Connect blocks with **local/global net labels** using the exact net names below rather than long wires across the sheet. Use power symbols for `+3V3`, `VBAT_SW`, `VBUS`, `GND`.
- Every symbol gets: Reference, Value, **Footprint**, and custom fields `MPN` and `LCSC` (leave `LCSC` blank if unknown — never invent part numbers).
- Default passive footprint: **0603** (`Resistor_SMD:R_0603_1608Metric`, `Capacitor_SMD:C_0603_1608Metric`) — board is hand-assembled.
- Before assigning any footprint, check it exists in the installed libraries. If one doesn't, pick the closest correct standard footprint (or create it from the datasheet) and list it in your final report.
- Annotate references sequentially after everything is placed.

## 1. System overview

- 2S LiPo (7.4 V nominal, 8.4 V max) via **XT60** → slide switch → `VBAT_SW`
- `VBAT_SW` powers the motor driver (VM) and the fan directly
- 3.3 V buck generates `+3V3` from `VBAT_SW`. USB provides data only, so the board needs the battery connected to run and to program
- MCU: **STM32F103C8T6 (LQFP48)**, 8 MHz HSE crystal, 72 MHz
- 2× N20 500 RPM 6 V gearmotors with quadrature encoders (off-board, via connectors)
- **Range sensing: 4× ToF**
  - **Front-left and front-right:** VL53L0X (longer range, sees the wall ahead)
  - **Left and right side:** VL6180X (short range, fast, centring)
  - All four on **I2C1**, each with its own XSHUT pin so addresses can be assigned at boot
- IMU: **MPU-6050 on I2C1** (same bus as the ToF sensors), polled — no interrupt line to the MCU
- Log flash: W25Q32JV on SPI2
- USB-C (device, FS) for flashing (via a USB bootloader) and a USB CDC serial console
- No wireless module, no separate debug UART (USB CDC replaces it)
- Two user buttons read on **one ADC pin** through a resistor ladder
- One status LED (plus power LED and buzzer)
- Display: 0.96" SSD1306 OLED, 128×64, I2C address 0x3C, on I2C1 (see Appendix A)

## 2. MCU pin map (STM32F103C8T6, LQFP48)

Firmware must set AFIO: **SWJ_CFG = SWD only (JTAG disabled)** to free PA15/PB3/PB4, **TIM2 partial remap 1** (CH1 = PA15, CH2 = PB3), **TIM3 partial remap** (CH1 = PB4, CH2 = PB5). I2C1 uses its **default** pins (PB6/PB7, no remap). Verify every function against the STM32F103x8 datasheet pinout and the RM0008 remap tables before wiring. If any pin is wrong, fix it, keep the net name, and report the change.

| Pin | Net name | Function |
|---|---|---|
| PA0 | TOF_XSHUT_FL | GPIO out, front-left ToF XSHUT |
| PA1 | TOF_XSHUT_FR | GPIO out, front-right ToF XSHUT |
| PA2 | TOF_XSHUT_L | GPIO out, left side ToF XSHUT |
| PA3 | TOF_XSHUT_R | GPIO out, right side ToF XSHUT |
| PA4 | SPARE_PA4 | test pad |
| PA5 | SPARE_PA5 | test pad |
| PA6 | VBAT_SENSE | ADC12_IN6 |
| PA7 | BTN_ADC | ADC12_IN7 (2-button resistor ladder) |
| PA8 | FAN_PWM | TIM1_CH1 |
| PA9 | SPARE_PA9 | test pad |
| PA10 | BUZZER | TIM1_CH3 |
| PA11 | USB_DM | USB D− |
| PA12 | USB_DP | USB D+ (1.5 kΩ pull-up to +3V3 required) |
| PA13 | SWDIO | SWD |
| PA14 | SWCLK | SWD |
| PA15 | ENC_L_A | TIM2_CH1 (partial remap 1) |
| PB0 | SPARE_PB0 | test pad |
| PB1 | SPARE_PB1 | test pad |
| PB2 | BOOT1 | 10 kΩ pull-down only (BOOT1 must stay low at boot) |
| PB3 | ENC_L_B | TIM2_CH2 (partial remap 1) |
| PB4 | ENC_R_A | TIM3_CH1 (partial remap) |
| PB5 | ENC_R_B | TIM3_CH2 (partial remap) |
| PB6 | I2C1_SCL | I2C1 SCL → MPU-6050, all ToF |
| PB7 | I2C1_SDA | I2C1 SDA → MPU-6050, all ToF |
| PB8 | MOT_PWMA | TIM4_CH3 |
| PB9 | MOT_PWMB | TIM4_CH4 |
| PB10 | MOT_AIN1 | GPIO out |
| PB11 | MOT_AIN2 | GPIO out |
| PB12 | FLASH_CS | GPIO out |
| PB13 | SPI2_SCK | SPI2 → flash |
| PB14 | SPI2_MISO | SPI2 → flash |
| PB15 | SPI2_MOSI | SPI2 → flash |
| PC13 | LED1 | GPIO out, LED wired to sink current (≤3 mA) |
| PC14 | MOT_BIN1 | GPIO out (low-speed pin — fine for direction) |
| PC15 | MOT_BIN2 | GPIO out (low-speed pin — fine for direction) |
| PD0 / PD1 | OSC_IN / OSC_OUT | 8 MHz HSE crystal |
| NRST | NRST | reset button + 100 nF |
| BOOT0 | BOOT0 | 10 kΩ pull-down + test pad (short to 3V3 for the ROM bootloader) |

> PA4, PA5, PA9 and PB0 were later allocated to menu buttons. See Appendix B.

TB6612 STBY is tied to `+3V3` (no GPIO left). Motors stay stopped at boot because AIN/BIN/PWM have pull-downs.

## 3. Block-by-block details (all on the single sheet)

### 3.1 POWER

| Ref | Part | Value / notes | Footprint |
|---|---|---|---|
| J1 | **XT60 male** (board side) | Battery input, `VBAT_RAW` / GND (no reverse-polarity MOSFET — XT60 is keyed). | `Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical` (or the horizontal `AMASS_XT60PW-M` variant if available — tell me which you used) |
| SW1 | SPDT slide switch | `VBAT_RAW` → `VBAT_SW` | `Button_Switch_SMD:SW_SPDT_PCM12` |
| C | Bulk | 100 µF 16 V + 10 µF 25 V on `VBAT_SW` | `Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D`, `Capacitor_SMD:C_1206_3216Metric` |
| — | Buck input | `VBAT_SW` → `VIN_BUCK` directly. No Schottky and no USB power-OR, so the board runs from the battery only. | — |
| U1 | AP63203WU-7 buck, 3.3 V fixed | Follow the datasheet typical application exactly (input caps, bootstrap cap, inductor, output caps) | `Package_TO_SOT_SMD:TSOT-23-6` |
| L1 | Buck inductor | Value per datasheet (~4.7 µH, ≥2 A, shielded) | `Inductor_SMD:L_Taiyo-Yuden_NR-40xx` (or closest 4×4 mm shielded) |
| R | Battery divider | `VBAT_SW` → 20 kΩ → `VBAT_SENSE` → 10 kΩ → GND, plus 100 nF on `VBAT_SENSE` | 0603 |
| LED + R | Power LED | On `+3V3`, ~1 kΩ | `LED_SMD:LED_0603_1608Metric` |
| TP | Test points | `VBAT_SW`, `+3V3`, `GND` | `TestPoint:TestPoint_Pad_D1.5mm` |

### 3.2 MCU

| Ref | Part | Value / notes | Footprint |
|---|---|---|---|
| U2 | STM32F103C8T6 | Symbol `MCU_ST_STM32F1:STM32F103C8Tx` | `Package_QFP:LQFP-48_7x7mm_P0.5mm` |
| C | Decoupling | 100 nF on each VDD pin (3) + 4.7 µF bulk on `+3V3` | 0603 |
| C | VDDA | 1 µF + 100 nF from `+3V3` (no ferrite bead) | 0603 |
| — | VBAT pin | Tie to `+3V3` with 100 nF | 0603 |
| Y1 | 8 MHz crystal | With 2× load caps (~20 pF, calculate from crystal CL) | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` |
| R | BOOT0 | 10 kΩ pull-down, plus BOOT0 test pad | 0603 |
| R | BOOT1 (PB2) | 10 kΩ pull-down | 0603 |
| SW | Reset button | NRST to GND, 100 nF on NRST | `Button_Switch_SMD:SW_SPST_TL3342` |
| J | SWD header (1.27 mm) | Cortex 10-pin (SWDIO, SWCLK, NRST, +3V3, GND) — symbol `Connector:Conn_ARM_JTAG_SWD_10` | `Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD` |
| J | SWD header (2.54 mm) | 4-pin: 3V3, SWDIO, SWCLK, GND — for ST-Link V2 clone | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |

### 3.3 MOTORS & ENCODERS

| Ref | Part | Value / notes | Footprint |
|---|---|---|---|
| U3 | TB6612FNG | Symbol `Driver_Motor:TB6612FNG`. VM = `VBAT_SW`, VCC = `+3V3`, STBY = `+3V3`, all GND/PGND to GND. AO1/AO2 → left motor, BO1/BO2 → right motor. | `Package_SO:SSOP-24_5.3x8.2mm_P0.65mm` |
| C | VM caps | 10 µF + 100 nF close to VM pins, plus 47 µF bulk | 1206 / 0603 / tantalum |
| C | VCC cap | 100 nF | 0603 |
| R | Input pull-downs | 10 kΩ on MOT_PWMA, MOT_PWMB, MOT_AIN1/2, MOT_BIN1/2 | 0603 |
| J | Left motor + encoder | 6-pin: M+, M−, ENC_VCC (+3V3), GND, ENC_L_A, ENC_L_B. **Pinout to be confirmed against the Robu GA12-N20 500 RPM wire harness before PCB.** | `Connector_JST:JST_PH_S6B-PH-K_1x06_P2.00mm_Horizontal` |
| J | Right motor + encoder | Same, ENC_R_A / ENC_R_B | same |
| R | Encoder pull-ups | 4.7 kΩ to `+3V3` on all 4 encoder lines (DNP-able if encoders are push-pull) | 0603 |
| C | Encoder filter | 100 pF on each encoder line (DNP-able) | 0603 |
| Q | AO3400A fan switch | Gate from `FAN_PWM` via 100 Ω, 100 kΩ gate pull-down | `Package_TO_SOT_SMD:SOT-23` |
| — | Fan flyback | Not fitted (Schottky removed). Add a flyback diode across the fan only when you populate it. | — |
| J | Fan connector | 2-pin, `VBAT_SW` and fan drain | `Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal` |

### 3.4 RANGE SENSORS (ToF)

All four sensors share I2C1 (`I2C1_SCL`, `I2C1_SDA`). Each has an XSHUT pin: on boot, hold all XSHUT low, then bring them up one at a time and assign each a unique I2C address in firmware before enabling the next. The VL53L0X and VL6180X both default to 0x29, so this step is mandatory.

| Ref | Part | Value / notes | Footprint |
|---|---|---|---|
| U_TFL | VL53L0X, front-left | Chip-down LGA-12. XSHUT → `TOF_XSHUT_FL`. VDD from `+3V3` with decoupling per datasheet (100 nF + 1 µF). GPIO1 → test pad (optional interrupt). Sensor window faces forward. | `Package_LGA:ST_VL53L0X_LGA-12` (or closest in the ST library — verify against datasheet) |
| U_TFR | VL53L0X, front-right | Same as above, XSHUT → `TOF_XSHUT_FR` | same |
| U_TL | VL6180X, left side | Chip-down LGA. XSHUT → `TOF_XSHUT_L`. Follow the datasheet for VDD (2.8 V nominal) and VDDIO; if the datasheet requires 2.8 V, add a small LDO from `+3V3` (e.g. a 2.8 V regulator) and label that rail `+2V8`. Sensor window faces sideways. | `Package_LGA:ST_VL6180X_LGA-18` (or closest — verify) |
| U_TR | VL6180X, right side | Same as above, XSHUT → `TOF_XSHUT_R` | same |
| R | I2C pull-ups | 2.2 kΩ to `+3V3` on `I2C1_SCL` and `I2C1_SDA` (shared with MPU-6050) | 0603 |
| R | XSHUT pull-downs | 100 kΩ on each XSHUT net (sensors held in reset at boot) | 0603 |
| C | Per-sensor decoupling | 100 nF + 1 µF close to each VDD pin | 0603 |
| TP | Test pads | `TOF_XSHUT_*`, `I2C1_SCL`, `I2C1_SDA` | `TestPoint:TestPoint_Pad_D1.5mm` |

**Notes for the report:** the VL6180X may need its own 2.8 V rail, which changes the power block. Check the datasheet before committing and report what you chose. Keep the ToF sensors' windows unobstructed by the board edge, and keep I2C traces short.

### 3.5 IMU & FLASH

| Ref | Part | Value / notes | Footprint |
|---|---|---|---|
| U4 | **MPU-6050** | Symbol `Sensor_Motion:MPU-6050`. VDD and VLOGIC to `+3V3` (100 nF + 10 nF on VDD, 10 nF on VLOGIC — follow datasheet). AD0 → GND (address 0x68). FSYNC → GND. CLKIN → GND. REGOUT → 100 nF to GND. CPOUT → 2.2 nF (≥50 V) to GND. SCL → `I2C1_SCL`, SDA → `I2C1_SDA`. INT → test pad only. AUX_DA / AUX_CL no-connect. Handle RESV pins and exposed pad exactly as the datasheet says. | `Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm` (verify against datasheet) |
| U5 | W25Q32JVSSIQ | SPI2 nets; CS = `FLASH_CS`; /WP and /HOLD pulled up to `+3V3` via 10 kΩ; 100 nF decoupling | `Package_SO:SOIC-8_5.23x5.23mm_P1.27mm` |
| R | Flash CS pull-up | 10 kΩ to `+3V3` on `FLASH_CS` | 0603 |
| TP | IMU test pad | `IMU_INT` | `TestPoint:TestPoint_Pad_D1.5mm` |

### 3.6 USB & UI

| Ref | Part | Value / notes | Footprint |
|---|---|---|---|
| J | USB-C receptacle (USB 2.0, 16-pin) | Symbol `Connector:USB_C_Receptacle_USB2.0_16P`; CC1 and CC2 each 5.1 kΩ to GND; shield to GND via 1 MΩ ‖ 4.7 nF | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` |
| R | USB D+ pull-up | 1.5 kΩ from `USB_DP` to `+3V3` (required for F103 USB enumeration) | 0603 |
| R | USB series resistors | 22 Ω on D+ and D− (optional, DNP-able) | 0603 |
| — | Button ladder on `BTN_ADC` | 10 kΩ pull-up to `+3V3`; SW_A shorts `BTN_ADC` directly to GND (≈0 V); SW_B shorts `BTN_ADC` to GND through 10 kΩ (≈1.65 V); 100 nF on `BTN_ADC` | 0603 |
| SW_A, SW_B | User buttons | See ladder above | `Button_Switch_SMD:SW_SPST_TL3342` |
| LED1 | Status LED | `+3V3` → 1 kΩ → LED → `LED1` (PC13 sinks) | `LED_SMD:LED_0603_1608Metric` |
| BZ1 | Magnetic buzzer (3 V) | Low side via MMBT3904; base 1 kΩ from `BUZZER` | `Buzzer_Beeper:Buzzer_12x9.5RM7.6` (or closest SMD magnetic buzzer) |
| Q | MMBT3904 | Buzzer driver | `Package_TO_SOT_SMD:SOT-23` |
| TP | Test pads | `BOOT0`, `GND` | `TestPoint:TestPoint_Pad_D1.5mm` |
| H1–H4 | Mounting holes | M3, plated, connected to GND | `MountingHole:MountingHole_3.2mm_M3_Pad_Via` |

## 4. Rules

- One flat sheet only. ERC must be clean. Mark intentionally unconnected pins with no-connect flags.
- Every footprint field filled — no blanks. Run footprint assignment check.
- Net names exactly as written above (they map to firmware).
- Keep the sheet readable: power flows left to right within each block, signals connected with net labels rather than long wires between blocks.
- Do not add parts I haven't listed unless a datasheet requires them (e.g. a missing decoupling cap or the VL6180X 2.8 V regulator). List every addition in the report.
- Every MCU pin is allocated or marked as a spare — if you need a pin for anything, tell me instead of reassigning one silently.

## 5. When finished, report back with

1. Any pin-map or footprint changes you made, and why
2. Any symbols or footprints you had to create
3. Full BOM export (Reference, Value, Footprint, MPN, Qty)
4. ERC result
5. Anything you think is wrong or risky in this design, especially the VL6180X supply voltage and the ToF address-assignment sequence

## 6. Phase 2 (only when I ask)

PCB setup: **2-layer, 1.6 mm, 1 oz copper**. Top = components, signals and power traces. Bottom = solid GND pour kept as unbroken as possible (only short jumpers on bottom, never long traces that slice the ground plane). Stitch top and bottom GND pours with vias every ~5 mm and around the board edge. Power traces: `VBAT_SW` / motor ≥ 0.8 mm, `+3V3` ≥ 0.4 mm, signals 0.25 mm. Keep the buck switching loop and TB6612 motor loops small and at the rear/edges, away from the ToF I2C and XSHUT traces; keep the crystal and its load caps within a few mm of the MCU with ground pour around them. Round board outline ~95 mm diameter, wheel cutouts at the left and right edges on the center axle line, 4× M3 mounting holes (positions to match my chassis CAD — ask me for the coordinates). Front ToF sensors at the front edge facing forward, side ToF sensors at the left and right edges facing sideways, MPU-6050 at the board center, motor driver and buck at the rear, XT60 at the rear edge.

---

## Appendix A — ADDITION: 0.96" OLED display (I2C1)

- Add a 0.96" SSD1306 OLED, 128x64, I2C, address 0x3C, on the existing I2C1 bus (PB6/PB7). No extra MCU pins.
- Add a 4-pin 2.54 mm header in section 3.6 (USB & UI):
  J_OLED: GND, +3V3, I2C1_SCL, I2C1_SDA
  Footprint: Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical
  Place it close to the MCU, away from the ToF sensor traces.
- Do not add new pull-ups. The 2.2 kΩ pull-ups in section 3.4 cover the whole bus. If the OLED module has its own pull-ups, leave them off the schematic and note it in the BOM.
- Update section 1 (System overview) to list the OLED.
- Update the report (section 5) to confirm the total I2C pull-up resistance and the device addresses on the bus: MPU-6050 at 0x68, OLED at 0x3C, four ToF sensors reassigned at boot.

## Appendix B — CHANGE: menu buttons to pull-down (replaces the earlier pull-up)

Four menu buttons, each read as a GPIO input with a pull-down:
- BTN_UP on PA4
- BTN_DOWN on PA5
- BTN_BACK on PA9
- BTN_ENTER on PB0 (ENTER and FRONT are the same button)

For each net:
- Add a 10 kΩ pull-down from the net to GND (idle = low).
- Add a 100 nF debounce cap from the net to GND.
- The tactile switch (SW_UP, SW_DOWN, SW_BACK, SW_ENTER, Button_Switch_SMD:SW_SPST_TL3342) connects the net to +3V3 when pressed, with one side on +3V3 and the other on the net.
- Remove any pull-up to +3V3 on these nets.

Do not change the OLED, ToF, IMU or motor sections.
Update the BOM and the report to list the four pull-downs.
