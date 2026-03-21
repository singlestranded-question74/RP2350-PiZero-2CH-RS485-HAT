# Waveshare 2-CH RS485 HAT & RP2350-PiZero Communication Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: RP2350](https://img.shields.io/badge/Platform-RP2350-blue.svg)](https://www.raspberrypi.com/documentation/microcontrollers/rp2350.html)
[![Language: C/C++](https://img.shields.io/badge/Language-C%2FC%2B%2B-green.svg)](https://pico-wrapper.readthedocs.io/en/latest/)
[![Language: MicroPython](https://img.shields.io/badge/Language-MicroPython-red.svg)](https://micropython.org/)

A high-performance dual-channel RS485 communication library and example suite for the **2-CH RS485 HAT**, specifically ported and optimized for the **Raspberry Pi RP2350 (Pico 2)**. 

This project leverages the **SC16IS752** SPI-to-Dual-UART bridge to provide two independent RS485 channels with automatic hardware flow control, managed via a clean C-based configuration layer or a lightweight MicroPython driver.

---

## 📸 Hardware Overview
![2-CH RS485 HAT](2-CH-RS485-HAT-1.jpg)
![RP2350 PiZero](rp2350-pizero.jpg)

The 2-CH RS485 HAT is an expansion board designed for the Raspberry Pi form factor, featuring:
* **Dual RS485 Channels**: Fully independent communication on two ports.
* **SC16IS752 Controller**: High-speed SPI interface to dual UART, offloading UART processing from the main MCU.
* **Level Conversion**: Built-in logic level conversion for stable 3.3V/5V operation.
* **Onboard Protection**: TVS (Transient Voltage Suppressor) and lightning protection.

### 🛒 Purchase Links
- **Module**: [Waveshare 2-CH RS485 HAT](https://www.waveshare.com/2-ch-rs485-hat.htm)
- **Controller**: [Waveshare RP2350-PiZero](https://www.waveshare.com/rp2350-pizero.htm)

---

## ✨ Key Features
- **Multi-Language Support**: Full implementation for both **C/C++ (Pico SDK)** and **MicroPython**.
- **Native RP2350 Support**: Optimized for the new RP2350 (Pico 2) architecture.
- **Dual-Channel Management**: Simple API to initialize and control both RS485 channels independently.
- **Direction Control**: Dedicated `TXDEN` pins for manual or automatic half-duplex direction switching.
- **Comprehensive Examples**: Includes robust dual-channel ping-pong communication tests for both languages.
- **Efficient SPI Interface**: High-speed communication with the SC16IS752 bridge.

---

## 🛠 Hardware Mapping (RP2350)
The library is configured to use the following GPIO pins on the RP2350 (mapped to the standard 40-pin header):

| Component | Function | RP2350 GPIO | Header Pin (Pi Zero) |
|-----------|----------|-------------|----------------------|
| **SPI**   | MISO     | **GP19**    | Pin 35               |
| **SPI**   | MOSI     | **GP20**    | Pin 38               |
| **SPI**   | SCK      | **GP21**    | Pin 40               |
| **SPI**   | CS       | **GP18**    | Pin 12               |
| **IRQ**   | Interrupt| **GP24**    | Pin 18               |
| **RS485** | TXDEN 1  | **GP27**    | Pin 13               |
| **RS485** | TXDEN 2  | **GP22**    | Pin 15               |

---

## 🚀 Getting Started

### 1. C/C++ SDK (Pico SDK)
Navigate to the `RP2350` folder to build the firmware.

#### **Prerequisites**
- **Raspberry Pi Pico SDK** (v2.1.0 or higher)
- **CMake** (3.13+)
- **GCC ARM Embedded Toolchain**

#### **Build Instructions**
**Linux/macOS:**
```bash
cd RP2350
mkdir build && cd build
cmake ..
make -j$(nproc)
```

**Windows:**
```powershell
cd RP2350
mkdir build
cd build
cmake -G "MinGW Makefiles" ..
cmake --build . -j4
```

> [!TIP]
> **Recommended for Windows:** Use the [Raspberry Pi Pico VS Code Extension](https://marketplace.visualstudio.com/items?itemName=raspberry-pi.raspberry-pi-pico). It handles the environment setup automatically.

#### **🎯 Build Targets**
- **`rs485_hat.uf2`**: Compiled from `examples/main.c`. Single-channel communication entry point.
- **`rs485_pingpong.uf2`**: Compiled from `examples/dual_ping_pong.c`. Comprehensive test for CH1 ↔ CH2 communication.

---

### 2. MicroPython
Navigate to the `Micropython` folder.

#### **Prerequisites**
- **MicroPython Firmware** installed on your RP2350.
- A MicroPython IDE (like **Thonny** or **VS Code with Pymakr**).

#### **Installation**
1. Copy `Micropython/sc16is752.py` (the driver) to your board.
2. Run `Micropython/main.py` to start the dual-channel ping-pong test.

#### **Usage Example**
```python
from sc16is752 import RS485Port, SC16IS752

# Initialize the SPI-to-UART bridge
bridge = SC16IS752(cs_pin=18, irq_pin=24)

# Setup RS485 Channels
ch1 = RS485Port(bridge, SC16IS752.CHANNEL_A, txden_pin=27, baudrate=9600)
ch2 = RS485Port(bridge, SC16IS752.CHANNEL_B, txden_pin=22, baudrate=9600)

# Transmit and Receive
ch1.write("Hello World")
data = ch2.read_line()
```

---

## 📂 Project Structure
* `RP2350/` - Main development folder for Pico SDK (C/C++).
    * `lib/` - Core driver files for RS485 and SC16IS752.
    * `lib/Config/` - Hardware abstraction layer and pin definitions.
    * `examples/` - Ready-to-run C demo applications.
* `Micropython/` - MicroPython implementation.
    * `sc16is752.py` - Lightweight MicroPython driver for the SPI bridge.
    * `main.py` - MicroPython loopback/ping-pong demo.

---

## 🧪 Demo: Dual Channel Ping-Pong
The ping-pong test (available in both C and MicroPython) verifies the hardware by looping data between the two channels.

**Wiring Instructions:**
1. Connect **CH1 A** to **CH2 A**.
2. Connect **CH1 B** to **CH2 B**.

**Expected Output:**
The program will transmit "Hello from CH1" and verify receipt on CH2, then perform the reverse. All logs are output via **USB Serial (stdio)** at 115200 baud.

---

## 👤 Author
Developed and ported by the Waveshare team & community contributors.

## 📄 License
This project is licensed under the MIT License.
