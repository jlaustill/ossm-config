# OSSM Firmware Test Suite

Automated tests for validating OSSM firmware commands over CAN bus.

## Setup

```bash
# Install dependencies
pip install -r tests/requirements.txt

# Ensure CAN interface is up
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
```

## Running Tests

```bash
# All non-destructive tests (safe for repeated runs)
pytest tests/ -v -m "not destructive"

# Specific command tests
pytest tests/test_cmd_query.py -v
pytest tests/test_cmd_enable_spn.py -v

# Show detailed output
pytest tests/ -v -s

# With timeout (default 1s per command)
pytest tests/ -v --ossm-timeout=2.0

# Use different CAN interface
pytest tests/ -v --can-interface=can1
# Or via environment variable:
OSSM_CAN_INTERFACE=can1 pytest tests/ -v
```

## Test Categories

| Marker | Description |
|--------|-------------|
| `requires_hardware` | Requires real OSSM device |
| `destructive` | Modifies EEPROM (save/reset) |

## Running Destructive Tests

EEPROM tests (save/reset) are marked destructive and skipped by default:

```bash
# Run ALL tests including destructive
pytest tests/ -v

# Run ONLY destructive tests
pytest tests/ -v -m destructive
```

## Test Files

| File | Commands Tested |
|------|-----------------|
| `test_cmd_query.py` | CMD_QUERY (0x05) |
| `test_cmd_enable_spn.py` | CMD_ENABLE_SPN (0x01) |
| `test_cmd_ntc_preset.py` | CMD_NTC_PRESET (0x08) |
| `test_cmd_pressure_preset.py` | CMD_PRESSURE_PRESET (0x09) |
| `test_cmd_tc_type.py` | CMD_SET_TC_TYPE (0x04) |
| `test_cmd_save_reset.py` | CMD_SAVE (0x06), CMD_RESET (0x07) |
| `test_integration.py` | Multi-command workflows |
