"""
OSSM Protocol Constants and Message Builders

This module mirrors the protocol definitions from src/types.h and
provides Python functions for building J1939 CAN frames.
"""

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

try:
    import can
except ImportError:
    can = None  # Allow importing for type checking even without python-can


# =============================================================================
# J1939 Addresses (from types.h:9)
# =============================================================================
OSSM_SOURCE_ADDRESS = 0x95  # 149
TESTER_SOURCE_ADDRESS = 0x00


# =============================================================================
# PGNs (from types.h:12-22)
# =============================================================================
PGN_OSSM_COMMAND = 0xFF00   # 65280 - Commands TO OSSM
PGN_OSSM_RESPONSE = 0xFF01  # 65281 - Responses FROM OSSM

# Data PGNs we receive
PGN_AMBIENT_CONDITIONS = 0xFEF5   # 65269
PGN_INLET_EXHAUST = 0xFEF6        # 65270
PGN_ENGINE_TEMP = 0xFEEE          # 65262
PGN_ENGINE_FLUID_PRESS = 0xFEEF   # 65263
PGN_ENGINE_TEMP_2 = 0xFE69        # 65129
PGN_ENGINE_TEMP_3 = 0xFE95        # 65189
PGN_TURBO_PRESS = 0xFE96          # 65190


# =============================================================================
# Command Codes (from types.h:25-35 EOssmCommand)
# =============================================================================
class EOssmCommand(IntEnum):
    CMD_ENABLE_SPN = 0x01
    CMD_SET_NTC_PARAM = 0x02
    CMD_SET_PRESSURE_RANGE = 0x03
    CMD_SET_TC_TYPE = 0x04
    CMD_QUERY = 0x05
    CMD_SAVE = 0x06
    CMD_RESET = 0x07
    CMD_NTC_PRESET = 0x08
    CMD_PRESSURE_PRESET = 0x09


# Convenience aliases
CMD_ENABLE_SPN = EOssmCommand.CMD_ENABLE_SPN
CMD_SET_NTC_PARAM = EOssmCommand.CMD_SET_NTC_PARAM
CMD_SET_PRESSURE_RANGE = EOssmCommand.CMD_SET_PRESSURE_RANGE
CMD_SET_TC_TYPE = EOssmCommand.CMD_SET_TC_TYPE
CMD_QUERY = EOssmCommand.CMD_QUERY
CMD_SAVE = EOssmCommand.CMD_SAVE
CMD_RESET = EOssmCommand.CMD_RESET
CMD_NTC_PRESET = EOssmCommand.CMD_NTC_PRESET
CMD_PRESSURE_PRESET = EOssmCommand.CMD_PRESSURE_PRESET


# =============================================================================
# Error Codes (must match OSSM firmware CommandHandler.h ECommandError)
# =============================================================================
class EOssmError(IntEnum):
    ERR_OK = 0x00
    ERR_UNKNOWN_CMD = 0x01
    ERR_PARSE_FAILED = 0x02
    ERR_UNKNOWN_SPN = 0x03
    ERR_INVALID_TEMP_INPUT = 0x04
    ERR_INVALID_PRESSURE_INPUT = 0x05
    ERR_INVALID_NTC_PARAM = 0x06
    ERR_INVALID_TC_TYPE = 0x07
    ERR_INVALID_QUERY_TYPE = 0x08
    ERR_SAVE_FAILED = 0x09
    ERR_INVALID_PRESET = 0x0A


# Convenience aliases
ERR_OK = EOssmError.ERR_OK
ERR_UNKNOWN_CMD = EOssmError.ERR_UNKNOWN_CMD
ERR_PARSE_FAILED = EOssmError.ERR_PARSE_FAILED
ERR_UNKNOWN_SPN = EOssmError.ERR_UNKNOWN_SPN
ERR_INVALID_TEMP_INPUT = EOssmError.ERR_INVALID_TEMP_INPUT
ERR_INVALID_PRESSURE_INPUT = EOssmError.ERR_INVALID_PRESSURE_INPUT
ERR_INVALID_NTC_PARAM = EOssmError.ERR_INVALID_NTC_PARAM
ERR_INVALID_TC_TYPE = EOssmError.ERR_INVALID_TC_TYPE
ERR_INVALID_QUERY_TYPE = EOssmError.ERR_INVALID_QUERY_TYPE
ERR_SAVE_FAILED = EOssmError.ERR_SAVE_FAILED
ERR_INVALID_PRESET = EOssmError.ERR_INVALID_PRESET


# =============================================================================
# NTC Presets (from types.h:106-110 ENtcPreset)
# =============================================================================
class ENtcPreset(IntEnum):
    NTC_PRESET_AEM = 0
    NTC_PRESET_BOSCH = 1
    NTC_PRESET_GM = 2


NTC_PRESET_AEM = ENtcPreset.NTC_PRESET_AEM
NTC_PRESET_BOSCH = ENtcPreset.NTC_PRESET_BOSCH
NTC_PRESET_GM = ENtcPreset.NTC_PRESET_GM


# =============================================================================
# Pressure Presets (from types.h:113-144 EPressurePreset)
# =============================================================================
class EPressurePreset(IntEnum):
    # Bar presets (0-15) - PSIA absolute
    PRES_PRESET_1BAR = 0
    PRES_PRESET_1_5BAR = 1
    PRES_PRESET_2BAR = 2
    PRES_PRESET_2_5BAR = 3
    PRES_PRESET_3BAR = 4
    PRES_PRESET_4BAR = 5
    PRES_PRESET_5BAR = 6
    PRES_PRESET_7BAR = 7
    PRES_PRESET_10BAR = 8
    PRES_PRESET_50BAR = 9
    PRES_PRESET_100BAR = 10
    PRES_PRESET_150BAR = 11
    PRES_PRESET_200BAR = 12
    PRES_PRESET_1000BAR = 13
    PRES_PRESET_2000BAR = 14
    PRES_PRESET_3000BAR = 15

    # PSI presets (20-30) - PSIG gauge
    PRES_PRESET_15PSI = 20
    PRES_PRESET_30PSI = 21
    PRES_PRESET_50PSI = 22
    PRES_PRESET_100PSI = 23
    PRES_PRESET_150PSI = 24
    PRES_PRESET_200PSI = 25
    PRES_PRESET_250PSI = 26
    PRES_PRESET_300PSI = 27
    PRES_PRESET_350PSI = 28
    PRES_PRESET_400PSI = 29
    PRES_PRESET_500PSI = 30


# Valid pressure preset values (note the gap 16-19)
VALID_PRESSURE_PRESETS = list(range(0, 16)) + list(range(20, 31))


# =============================================================================
# Thermocouple Types
# =============================================================================
class EThermocoupleType(IntEnum):
    TC_TYPE_B = 0
    TC_TYPE_E = 1
    TC_TYPE_J = 2
    TC_TYPE_K = 3
    TC_TYPE_N = 4
    TC_TYPE_R = 5
    TC_TYPE_S = 6
    TC_TYPE_T = 7


TC_TYPE_NAMES = {
    0: "B", 1: "E", 2: "J", 3: "K",
    4: "N", 5: "R", 6: "S", 7: "T"
}


# =============================================================================
# Known SPNs (from types.h:147-177 KNOWN_SPNS)
# =============================================================================
class ESpnCategory(IntEnum):
    SPN_CAT_TEMPERATURE = 0
    SPN_CAT_PRESSURE = 1
    SPN_CAT_EGT = 2
    SPN_CAT_BME280 = 3
    SPN_CAT_UNKNOWN = 4


@dataclass
class TSpnInfo:
    spn: int
    name: str
    unit: str
    category: ESpnCategory


# Temperature SPNs
TEMP_SPNS = {
    175: TSpnInfo(175, "Engine Oil Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    110: TSpnInfo(110, "Coolant Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    174: TSpnInfo(174, "Fuel Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    105: TSpnInfo(105, "Boost Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    1131: TSpnInfo(1131, "CAC Inlet Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    1132: TSpnInfo(1132, "Transfer Pipe Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    1133: TSpnInfo(1133, "Air Inlet Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    172: TSpnInfo(172, "Air Inlet Temp 2", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
    441: TSpnInfo(441, "Engine Bay Temp", "C", ESpnCategory.SPN_CAT_TEMPERATURE),
}

# Pressure SPNs
PRESSURE_SPNS = {
    100: TSpnInfo(100, "Engine Oil Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
    109: TSpnInfo(109, "Coolant Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
    94: TSpnInfo(94, "Fuel Delivery Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
    102: TSpnInfo(102, "Boost Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
    106: TSpnInfo(106, "Air Inlet Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
    1127: TSpnInfo(1127, "CAC Inlet Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
    1128: TSpnInfo(1128, "Transfer Pipe Pres", "kPa", ESpnCategory.SPN_CAT_PRESSURE),
}

# EGT SPN
EGT_SPN = 173
EGT_SPN_INFO = TSpnInfo(173, "EGT", "C", ESpnCategory.SPN_CAT_EGT)

# BME280 SPNs
BME280_SPNS = {
    171: TSpnInfo(171, "Ambient Temp", "C", ESpnCategory.SPN_CAT_BME280),
    108: TSpnInfo(108, "Barometric Pres", "kPa", ESpnCategory.SPN_CAT_BME280),
    354: TSpnInfo(354, "Humidity", "%", ESpnCategory.SPN_CAT_BME280),
}

# All known SPNs combined
ALL_KNOWN_SPNS = {**TEMP_SPNS, **PRESSURE_SPNS, EGT_SPN: EGT_SPN_INFO, **BME280_SPNS}

# Lists for easy iteration
VALID_TEMP_SPNS = list(TEMP_SPNS.keys())
VALID_PRESSURE_SPNS = list(PRESSURE_SPNS.keys())
VALID_ALL_SPNS = list(ALL_KNOWN_SPNS.keys())


# =============================================================================
# Input Limits
# =============================================================================
MAX_TEMP_INPUTS = 8      # Inputs 1-8 (0 is invalid)
MAX_PRESSURE_INPUTS = 7  # Inputs 1-7 (0 is invalid)


# =============================================================================
# Response Timeout
# =============================================================================
RESPONSE_TIMEOUT_MS = 1000
RESPONSE_TIMEOUT_S = 1.0
INITIAL_DELAY_MS = 50
INITIAL_DELAY_S = 0.05


# =============================================================================
# J1939 ID Functions (from j1939.c:10-33)
# =============================================================================

def j1939_get_pgn(can_id: int) -> int:
    """
    Extract PGN from J1939 CAN ID.

    Mirrors j1939_get_pgn() in j1939.c:10-22
    """
    pf = (can_id >> 16) & 0xFF
    if pf < 240:
        # PDU1 format - destination specific
        return pf << 8
    else:
        # PDU2 format - broadcast
        ps = (can_id >> 8) & 0xFF
        return (pf << 8) | ps


def j1939_get_source(can_id: int) -> int:
    """
    Extract source address from J1939 CAN ID.

    Mirrors j1939_get_source() in j1939.c:24-26
    """
    return can_id & 0xFF


def j1939_build_id(pgn: int, priority: int = 6, source: int = TESTER_SOURCE_ADDRESS) -> int:
    """
    Build J1939 CAN ID from components.

    Mirrors j1939_build_id() in j1939.c:28-33
    """
    return ((priority & 0x07) << 26) | ((pgn & 0x3FFFF) << 8) | (source & 0xFF)


# =============================================================================
# Message Builder Functions
# =============================================================================

def build_command_frame(cmd: int, params: bytes = b'') -> "can.Message":
    """
    Build an OSSM command CAN frame.

    Mirrors j1939_send_command() in j1939.c:190-206

    Args:
        cmd: Command code (see EOssmCommand)
        params: Parameter bytes (0-7 bytes)

    Returns:
        can.Message ready to send
    """
    if can is None:
        raise ImportError("python-can is required")

    can_id = j1939_build_id(PGN_OSSM_COMMAND, priority=6, source=TESTER_SOURCE_ADDRESS)

    # Build 8-byte data: [cmd][params...][0xFF padding]
    data = bytes([cmd]) + params
    data = data + bytes([0xFF] * (8 - len(data)))

    return can.Message(
        arbitration_id=can_id,
        data=data[:8],
        is_extended_id=True
    )


def parse_response(msg: "can.Message", expected_cmd: int) -> tuple[int, bytes]:
    """
    Parse an OSSM response frame.

    Args:
        msg: Received CAN message
        expected_cmd: The command code we expect in the response

    Returns:
        Tuple of (error_code, response_data)

    Raises:
        ValueError: If message is not an OSSM response or command mismatch
    """
    pgn = j1939_get_pgn(msg.arbitration_id)
    source = j1939_get_source(msg.arbitration_id)

    if pgn != PGN_OSSM_RESPONSE:
        raise ValueError(f"Not a response PGN: got 0x{pgn:04X}, expected 0x{PGN_OSSM_RESPONSE:04X}")

    if source != OSSM_SOURCE_ADDRESS:
        raise ValueError(f"Wrong source address: got 0x{source:02X}, expected 0x{OSSM_SOURCE_ADDRESS:02X}")

    if msg.data[0] != expected_cmd:
        raise ValueError(f"Command mismatch: got 0x{msg.data[0]:02X}, expected 0x{expected_cmd:02X}")

    error_code = msg.data[1]
    response_data = bytes(msg.data[2:8])

    return error_code, response_data


def is_ossm_response(msg: "can.Message") -> bool:
    """Check if a CAN message is an OSSM response."""
    pgn = j1939_get_pgn(msg.arbitration_id)
    source = j1939_get_source(msg.arbitration_id)
    return pgn == PGN_OSSM_RESPONSE and source == OSSM_SOURCE_ADDRESS


# =============================================================================
# Command Parameter Builders
# =============================================================================

def build_enable_spn_params(spn: int, enable: bool, input_num: int) -> bytes:
    """Build parameters for CMD_ENABLE_SPN."""
    return bytes([
        (spn >> 8) & 0xFF,  # SPN high byte
        spn & 0xFF,          # SPN low byte
        1 if enable else 0,  # Enable flag
        input_num & 0xFF     # Input index
    ])


def build_ntc_preset_params(input_num: int, preset: int) -> bytes:
    """Build parameters for CMD_NTC_PRESET."""
    return bytes([input_num & 0xFF, preset & 0xFF])


def build_pressure_preset_params(input_num: int, preset: int) -> bytes:
    """Build parameters for CMD_PRESSURE_PRESET."""
    return bytes([input_num & 0xFF, preset & 0xFF])


def build_tc_type_params(tc_type: int) -> bytes:
    """Build parameters for CMD_SET_TC_TYPE."""
    return bytes([tc_type & 0xFF])


def build_query_params(query_type: int, sub_query: int = 0) -> bytes:
    """Build parameters for CMD_QUERY."""
    return bytes([query_type & 0xFF, sub_query & 0xFF])


# =============================================================================
# Response Data Parsers
# =============================================================================

@dataclass
class TConfigState:
    """Configuration state returned by CMD_QUERY type 0."""
    temp_count: int
    pressure_count: int
    egt_enabled: bool
    bme280_enabled: bool


def parse_query_config_response(data: bytes) -> TConfigState:
    """
    Parse response data from CMD_QUERY type 0 (config counts).

    Response format (from j1939.c:299-317):
        data[0] = temp_count
        data[1] = pressure_count
        data[2] = egt_enabled
        data[3] = bme280_enabled
    """
    return TConfigState(
        temp_count=data[0],
        pressure_count=data[1],
        egt_enabled=data[2] != 0,
        bme280_enabled=data[3] != 0
    )


def parse_query_spn_response(data: bytes) -> list[int]:
    """
    Parse response data from CMD_QUERY type 1 or 2 (SPN assignments).

    Response format (from j1939.c:319-370):
        data[0-1] = SPN 1 (high, low)
        data[2-3] = SPN 2 (high, low)
        data[4-5] = SPN 3 (high, low)

    Returns list of 3 SPNs (0xFFFF = disabled)
    """
    spns = []
    for i in range(0, 6, 2):
        spn = (data[i] << 8) | data[i + 1]
        spns.append(spn if spn != 0xFFFF else 0)
    return spns
