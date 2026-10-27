# micromouse

A classic-size (18 × 18 cm maze) micromouse robot built around a custom two-layer PCB. An STM32F103C8T6 drives two N20 gearmotors with quadrature encoders through a TB6612FNG. Wall sensing uses four time-of-flight sensors: two long-range VL53L0X facing forward and two short-range VL6180X facing sideways for centring. These sit on one I2C bus with an MPU-6050 IMU and an SSD1306 OLED menu display. Logs go to SPI flash, and USB-C provides firmware updates and a CDC serial console. The board runs from a 2S LiPo through an XT60 connector.

## Hardware

- **MCU:** STM32F103C8T6 (LQFP48, 8 MHz HSE, 72 MHz)
- **Motor driver:** TB6612FNG
- **Motors:** 2× N20 500 RPM 6 V gearmotors with quadrature encoders
- **Front ToF:** 2× VL53L0X
- **Side ToF:** 2× VL6180X
- **IMU:** MPU-6050
- **Log flash:** W25Q32 (SPI)
- **Display:** 0.96" SSD1306 OLED, 128×64, I2C
- **USB:** USB-C (device, full speed)
- **Power:** XT60 connector, 2S 850 mAh LiPo

## Status

- **Schematic:** in progress (phase 1)
- **PCB routing:** not started

## Documentation

- [KiCad build spec](docs/kicad_build_spec.md): full schematic requirements, pin map and block-by-block part list

## Layout

| Folder | Contents |
|---|---|
| `kicad/` | KiCad project (schematic, PCB, libraries) |
| `firmware/` | STM32 firmware |
| `mechanical/` | Chassis CAD and mechanical drawings |
| `docs/` | Specifications and design notes |
