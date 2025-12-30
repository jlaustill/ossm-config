"""
Pytest configuration and fixtures for OSSM firmware tests.

This module provides:
- CAN bus fixtures for connecting to SocketCAN interfaces
- OssmCommander class for sending commands and receiving responses
- Test markers for categorizing tests
"""

import os
import time
from dataclasses import dataclass
from typing import Optional

import pytest

try:
    import can
except ImportError:
    pytest.skip("python-can is required", allow_module_level=True)

from ossm_protocol import (
    OSSM_SOURCE_ADDRESS,
    PGN_OSSM_COMMAND,
    PGN_OSSM_RESPONSE,
    RESPONSE_TIMEOUT_S,
    INITIAL_DELAY_S,
    CMD_ENABLE_SPN,
    CMD_SET_NTC_PARAM,
    CMD_SET_PRESSURE_RANGE,
    CMD_SET_TC_TYPE,
    CMD_QUERY,
    CMD_SAVE,
    CMD_RESET,
    CMD_NTC_PRESET,
    CMD_PRESSURE_PRESET,
    ERR_OK,
    TConfigState,
    build_command_frame,
    parse_response,
    is_ossm_response,
    build_enable_spn_params,
    build_ntc_preset_params,
    build_pressure_preset_params,
    build_tc_type_params,
    build_query_params,
    parse_query_config_response,
    parse_query_spn_response,
)


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "destructive: marks tests that modify EEPROM (deselect with '-m \"not destructive\"')"
    )
    config.addinivalue_line(
        "markers", "requires_hardware: marks tests that require real OSSM hardware"
    )
    config.addinivalue_line(
        "markers", "vcan_compatible: marks tests that can run with virtual CAN"
    )


def pytest_addoption(parser):
    """Add command-line options."""
    parser.addoption(
        "--can-interface",
        action="store",
        default=None,
        help="CAN interface to use (overrides OSSM_CAN_INTERFACE env var)"
    )
    parser.addoption(
        "--ossm-timeout",
        action="store",
        type=float,
        default=None,
        help="Response timeout in seconds (default: 1.0)"
    )


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def can_interface(request) -> str:
    """Get CAN interface from CLI option, environment, or default to can0."""
    cli_iface = request.config.getoption("--can-interface")
    if cli_iface:
        return cli_iface
    return os.environ.get("OSSM_CAN_INTERFACE", "can0")


@pytest.fixture(scope="session")
def response_timeout(request) -> float:
    """Get response timeout from CLI option or default."""
    cli_timeout = request.config.getoption("--ossm-timeout")
    if cli_timeout is not None:
        return cli_timeout
    return RESPONSE_TIMEOUT_S


@pytest.fixture(scope="session")
def use_vcan(can_interface) -> bool:
    """Check if we're using virtual CAN for dry runs."""
    return can_interface.startswith("vcan")


@pytest.fixture(scope="function")
def can_bus(can_interface):
    """
    Create CAN bus connection for a single test.

    Uses function scope to ensure clean state between tests.
    """
    bus = can.interface.Bus(
        channel=can_interface,
        interface="socketcan",
        receive_own_messages=False
    )
    # Flush any pending messages
    while bus.recv(timeout=0.01) is not None:
        pass
    yield bus
    bus.shutdown()


@pytest.fixture(scope="function")
def ossm(can_bus, response_timeout) -> "OssmCommander":
    """
    Create OssmCommander instance for sending commands.

    This is the primary fixture for interacting with the OSSM device.
    """
    return OssmCommander(can_bus, timeout=response_timeout)


# =============================================================================
# OssmCommander Class
# =============================================================================

class OssmCommandError(Exception):
    """Exception raised when OSSM returns an error code."""

    def __init__(self, error_code: int, command: int, message: str = ""):
        self.error_code = error_code
        self.command = command
        super().__init__(message or f"OSSM error 0x{error_code:02X} for command 0x{command:02X}")


class OssmTimeoutError(Exception):
    """Exception raised when OSSM doesn't respond in time."""

    def __init__(self, command: int, timeout: float):
        self.command = command
        self.timeout = timeout
        super().__init__(f"No response for command 0x{command:02X} after {timeout}s")


@dataclass
class TSpnAssignments:
    """SPN assignments for all inputs."""
    temp_spns: list[int]      # SPNs for temp inputs 1-8 (0 = disabled)
    pressure_spns: list[int]  # SPNs for pressure inputs 1-7 (0 = disabled)


class OssmCommander:
    """
    Helper class for sending commands to OSSM and receiving responses.

    This class provides high-level methods matching the C API in j1939.h:35-42.
    Each method sends a command and waits for the response, returning the
    error code or raising an exception on timeout.
    """

    def __init__(self, bus: can.Bus, timeout: float = RESPONSE_TIMEOUT_S):
        """
        Initialize OssmCommander.

        Args:
            bus: python-can Bus instance
            timeout: Response timeout in seconds
        """
        self.bus = bus
        self.timeout = timeout

    def send_command(self, cmd: int, params: bytes = b'') -> tuple[int, bytes]:
        """
        Send command and wait for response.

        Mirrors the pattern in j1939_check_response() from j1939.c:208-242.

        Args:
            cmd: Command code
            params: Parameter bytes

        Returns:
            Tuple of (error_code, response_data)

        Raises:
            OssmTimeoutError: If no response within timeout
        """
        frame = build_command_frame(cmd, params)
        self.bus.send(frame)

        # Wait for response (50ms initial delay then poll)
        time.sleep(INITIAL_DELAY_S)

        start = time.time()
        while (time.time() - start) < self.timeout:
            msg = self.bus.recv(timeout=0.1)
            if msg is None:
                continue

            if not is_ossm_response(msg):
                continue

            try:
                return parse_response(msg, cmd)
            except ValueError:
                # Not our response, keep waiting
                continue

        raise OssmTimeoutError(cmd, self.timeout)

    # =========================================================================
    # High-Level Commands (matching j1939.h API)
    # =========================================================================

    def enable_spn(self, spn: int, enable: bool, input_num: int) -> int:
        """
        Enable or disable an SPN on a specific input.

        Mirrors j1939_enable_spn() in j1939.c:244-262.

        Args:
            spn: SPN number to enable/disable
            enable: True to enable, False to disable
            input_num: Input index (1-8 for temp, 1-7 for pressure)

        Returns:
            Error code (0 = success)
        """
        params = build_enable_spn_params(spn, enable, input_num)
        error, _ = self.send_command(CMD_ENABLE_SPN, params)
        return error

    def set_ntc_preset(self, input_num: int, preset: int) -> int:
        """
        Apply NTC preset to a temperature input.

        Mirrors j1939_set_ntc_preset() in j1939.c:264-274.

        Args:
            input_num: Temperature input index (1-8)
            preset: NTC preset (0=AEM, 1=Bosch, 2=GM)

        Returns:
            Error code (0 = success)
        """
        params = build_ntc_preset_params(input_num, preset)
        error, _ = self.send_command(CMD_NTC_PRESET, params)
        return error

    def set_pressure_preset(self, input_num: int, preset: int) -> int:
        """
        Apply pressure preset to a pressure input.

        Mirrors j1939_set_pressure_preset() in j1939.c:276-286.

        Args:
            input_num: Pressure input index (1-7)
            preset: Pressure preset (0-15 for Bar, 20-30 for PSI)

        Returns:
            Error code (0 = success)
        """
        params = build_pressure_preset_params(input_num, preset)
        error, _ = self.send_command(CMD_PRESSURE_PRESET, params)
        return error

    def set_tc_type(self, tc_type: int) -> int:
        """
        Set thermocouple type for EGT.

        Mirrors j1939_set_tc_type() in j1939.c:288-297.

        Args:
            tc_type: Thermocouple type (0-7 for B,E,J,K,N,R,S,T)

        Returns:
            Error code (0 = success)
        """
        params = build_tc_type_params(tc_type)
        error, _ = self.send_command(CMD_SET_TC_TYPE, params)
        return error

    def query_config(self) -> tuple[int, TConfigState]:
        """
        Query SPN counts and feature status.

        Mirrors j1939_query_config() in j1939.c:299-317.

        Returns:
            Tuple of (error_code, TConfigState)
        """
        params = build_query_params(query_type=0)
        error, data = self.send_command(CMD_QUERY, params)
        config = parse_query_config_response(data)
        return error, config

    def query_temp_spns(self) -> tuple[int, list[int]]:
        """
        Query temperature SPN assignments for all 8 inputs.

        Mirrors j1939_query_spn_assignments() in j1939.c:319-370 (type 1).

        Returns:
            Tuple of (error_code, list of 8 SPNs)
        """
        all_spns = []

        # Sub-query 0: inputs 1-3
        params = build_query_params(query_type=1, sub_query=0)
        error, data = self.send_command(CMD_QUERY, params)
        if error != ERR_OK:
            return error, []
        all_spns.extend(parse_query_spn_response(data))

        # Sub-query 1: inputs 4-6
        params = build_query_params(query_type=1, sub_query=1)
        error, data = self.send_command(CMD_QUERY, params)
        if error != ERR_OK:
            return error, all_spns
        all_spns.extend(parse_query_spn_response(data))

        # Sub-query 2: inputs 7-8 (only first 2 valid)
        params = build_query_params(query_type=1, sub_query=2)
        error, data = self.send_command(CMD_QUERY, params)
        if error != ERR_OK:
            return error, all_spns
        spns = parse_query_spn_response(data)
        all_spns.extend(spns[:2])  # Only 2 more inputs

        return ERR_OK, all_spns

    def query_pressure_spns(self) -> tuple[int, list[int]]:
        """
        Query pressure SPN assignments for all 7 inputs.

        Mirrors j1939_query_spn_assignments() in j1939.c:319-370 (type 2).

        Returns:
            Tuple of (error_code, list of 7 SPNs)
        """
        all_spns = []

        # Sub-query 0: inputs 1-3
        params = build_query_params(query_type=2, sub_query=0)
        error, data = self.send_command(CMD_QUERY, params)
        if error != ERR_OK:
            return error, []
        all_spns.extend(parse_query_spn_response(data))

        # Sub-query 1: inputs 4-6
        params = build_query_params(query_type=2, sub_query=1)
        error, data = self.send_command(CMD_QUERY, params)
        if error != ERR_OK:
            return error, all_spns
        all_spns.extend(parse_query_spn_response(data))

        # Sub-query 2: input 7 (only first 1 valid)
        params = build_query_params(query_type=2, sub_query=2)
        error, data = self.send_command(CMD_QUERY, params)
        if error != ERR_OK:
            return error, all_spns
        spns = parse_query_spn_response(data)
        all_spns.extend(spns[:1])  # Only 1 more input

        return ERR_OK, all_spns

    def query_all_spn_assignments(self) -> tuple[int, TSpnAssignments]:
        """
        Query all SPN assignments (temp and pressure).

        Returns:
            Tuple of (error_code, TSpnAssignments)
        """
        error, temp_spns = self.query_temp_spns()
        if error != ERR_OK:
            return error, TSpnAssignments([], [])

        error, pressure_spns = self.query_pressure_spns()
        return error, TSpnAssignments(temp_spns, pressure_spns)

    def save_config(self) -> int:
        """
        Save configuration to EEPROM.

        Mirrors j1939_save_config() in j1939.c:372-378.

        Returns:
            Error code (0 = success)
        """
        error, _ = self.send_command(CMD_SAVE)
        return error

    def reset_config(self) -> int:
        """
        Reset configuration to factory defaults.

        Mirrors j1939_reset_config() in j1939.c:380-386.

        Returns:
            Error code (0 = success)
        """
        error, _ = self.send_command(CMD_RESET)
        return error
