# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands

```bash
# Build the project
make

# Debug build (includes -g and -DDEBUG flags)
make debug

# Clean build artifacts
make clean

# Install to /usr/local/bin
sudo make install
```

## Running

```bash
# Setup CAN interface first (required)
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up

# Run with default interface (can0)
./ossm-config

# Run with specific interface
./ossm-config -i can1
```

## Architecture

This is a C11 ncurses TUI application for configuring OSSM (Open Source Sensor Module) devices over J1939 CAN bus.

### Layer Structure

```
src/
├── main.c              # Application entry, main loop, input handling
├── types.h             # Shared types, enums, constants, SPN database
├── ui/                 # ncurses TUI layer
│   ├── ui.h            # Window structures, dialog declarations
│   └── ui.c            # Display rendering, user dialogs
├── can/                # Hardware abstraction layer
│   ├── socketcan.h     # CAN frame structure, socket operations
│   └── socketcan.c     # Linux SocketCAN implementation
└── protocol/           # Protocol layer
    ├── j1939.h         # J1939 message parsing, OSSM commands
    └── j1939.c         # PGN handling, command/response protocol
```

### Key Data Flow

1. **Incoming**: SocketCAN receives frames → J1939 parses PGN → Updates `TSensorData` struct → UI displays values
2. **Outgoing**: UI dialog → J1939 command builder → SocketCAN send → Wait for response on PGN 65281

### Custom Protocol

- Commands sent on **PGN 65280** (0xFF00) to OSSM source address 0x95
- Responses received on **PGN 65281** (0xFF01)
- Standard J1939 PGNs (65262, 65263, 65269, 65270, etc.) used for sensor data

### Type Naming Conventions

- `T` prefix for struct types (e.g., `TSensorData`, `TCanFrame`)
- `E` prefix for enums (e.g., `EOssmCommand`, `ENtcPreset`)

## Dependencies

- Linux with SocketCAN support
- ncurses library (`libncurses-dev`)
- pthreads (linked but not actively used for threading)
