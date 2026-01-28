# OSSM Config Tool

A CLI tool for configuring the Open Source Sensor Module (OSSM) over J1939 CAN bus.

## Features

- **Live sensor monitoring**: View all temperature, pressure, EGT, and ambient readings
- **SPN Configuration**: Enable/disable sensor SPNs and assign them to hardware inputs
- **NTC Presets**: Apply preset calibration values for AEM, Bosch, or GM temperature sensors
- **Pressure Presets**: Configure pressure sensor ranges (Bar/PSIA or PSI/PSIG)
- **Thermocouple Type**: Select thermocouple type for EGT (B, E, J, K, N, R, S, T)
- **Configuration Management**: Query, save, and reset OSSM configuration via CAN

## Requirements

- Node.js 18+
- Linux with SocketCAN support
- CAN interface (CANable, PEAK, etc.) configured for 250kbps

## Installation

```bash
npm install
npm run build
```

## Usage

### Setup CAN Interface

```bash
# Configure CAN interface
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
```

### Run the Tool

```bash
# Default interface (can0)
npm start

# Or specify interface
npm start -- -i can1

# Or after global install
ossm-config -i can0
```

## Menu Options

```
=== OSSM Config (can0) ===

1. Query configuration
2. Enable/Disable SPN
3. NTC Sensor Preset
4. Pressure Sensor Preset
5. Thermocouple Type
6. Monitor live data
7. Save to EEPROM
8. Reset to defaults
0. Exit
```

## J1939 Protocol

The tool communicates with OSSM using proprietary PGNs:

- **PGN 65280 (0xFF00)**: Commands TO OSSM
- **PGN 65281 (0xFF01)**: Responses FROM OSSM

Standard J1939 PGNs are decoded for sensor data:
- 65262: Engine Temperature
- 65263: Engine Fluid Pressure
- 65269: Ambient Conditions
- 65270: Inlet/Exhaust Conditions

## License

MIT
