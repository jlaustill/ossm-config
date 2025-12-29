# OSSM Config Tool

A ncurses-based TUI (Text User Interface) for configuring the Open Source Sensor Module (OSSM) over J1939 CAN bus.

## Features

- **Real-time sensor display**: View all temperature, pressure, EGT, and ambient readings live
- **SPN Configuration**: Enable/disable sensor SPNs and assign them to hardware inputs
- **NTC Presets**: Apply preset calibration values for AEM, Bosch, or GM temperature sensors
- **Pressure Presets**: Configure pressure sensor ranges (Bar/PSIA or PSI/PSIG)
- **Thermocouple Type**: Select thermocouple type for EGT (B, E, J, K, N, R, S, T)
- **Configuration Management**: Query, save, and reset OSSM configuration via CAN

## Requirements

- Linux with SocketCAN support
- ncurses library
- CAN interface (CANable, PEAK, etc.) configured for 250kbps

## Building

```bash
# Install dependencies (Debian/Ubuntu)
sudo apt-get install build-essential libncurses-dev

# Build
make

# Install (optional)
sudo make install
```

## Usage

### Setup CAN Interface

```bash
# Configure CAN interface (adjust interface name as needed)
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up

# Verify interface is up
ip -details link show can0
```

### Run the Tool

```bash
# Default interface (can0)
./ossm-config

# Specify interface
./ossm-config -i can1
```

### Keyboard Commands

| Key | Function |
|-----|----------|
| F1 | Help |
| F2 | Enable/Disable SPN |
| F3 | NTC Sensor Preset |
| F4 | Pressure Sensor Preset |
| F5 | Thermocouple Type |
| F6 | Query Configuration |
| F7 | Save to EEPROM |
| F8 | Reset to Defaults |
| F10/Q | Quit |

### Navigation in Dialogs

- **Arrow keys**: Navigate options
- **+/-**: Adjust input numbers
- **Enter**: Confirm selection
- **ESC**: Cancel dialog

## Display Layout

```
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ TEMPERATURES                    │ │ PRESSURES                       │
│                                 │ │                                 │
│ Oil Temp:           85.5 C      │ │ Oil Pres:          420.0 kPa    │
│ Coolant Temp:       92.0 C      │ │ Coolant Pres:      101.3 kPa    │
│ Fuel Temp:          45.2 C      │ │ Fuel Pres:         310.0 kPa    │
│ ...                             │ │ ...                             │
└─────────────────────────────────┘ └─────────────────────────────────┘

┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ EGT                             │ │ AMBIENT                         │
│                                 │ │                                 │
│ EGT:               650.0 C      │ │ Ambient Temp:       25.0 C      │
│                                 │ │ Barometric:        101.3 kPa    │
└─────────────────────────────────┘ │ Humidity:           45.0 %      │
                                    └─────────────────────────────────┘

CAN: can0  Status: CONNECTED  Messages: 1234
F1Help F2Enable F3NTC F4Pres F5TC F6Query F7Save F8Reset F10Quit
```

## Color Coding

- **Green**: Live sensor values
- **Yellow**: Stale data (>2 seconds old)
- **Red**: N/A or error values
- **Cyan**: Titles and highlights

## J1939 Protocol

The tool communicates with OSSM using proprietary PGNs:

- **PGN 65280 (0xFF00)**: Commands TO OSSM
- **PGN 65281 (0xFF01)**: Responses FROM OSSM

Standard J1939 PGNs are used for sensor data:
- 65262: Engine Temperature
- 65263: Engine Fluid Pressure
- 65269: Ambient Conditions
- 65270: Inlet/Exhaust Conditions
- 65129, 65189: Additional Temperatures
- 65190: Turbocharger Pressures

## Troubleshooting

### No CAN traffic visible
1. Verify CAN interface is up: `ip link show can0`
2. Check baud rate matches OSSM (250kbps)
3. Ensure common ground between CAN adapter and OSSM
4. Verify CAN-H and CAN-L wiring

### Permission denied
```bash
# Add user to dialout group (may require logout/login)
sudo usermod -aG dialout $USER

# Or run as root
sudo ./ossm-config
```

### Terminal too small
The tool requires a minimum terminal size of 80x30 characters.

## License

Same license as the OSSM project.
