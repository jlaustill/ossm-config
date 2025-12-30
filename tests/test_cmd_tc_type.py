"""
Tests for CMD_SET_TC_TYPE (0x04) - Set Thermocouple Type

This test module validates the thermocouple type command which:
- Sets the thermocouple type for EGT measurements
- Supports 8 types: B, E, J, K, N, R, S, T (codes 0-7)
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    ERR_INVALID_TC_TYPE,
    EThermocoupleType,
    TC_TYPE_NAMES,
)
from conftest import OssmCommander


# =============================================================================
# Positive Tests
# =============================================================================

class TestTcTypePositive:
    """Positive tests for CMD_SET_TC_TYPE."""

    @pytest.mark.requires_hardware
    def test_set_type_k_default(self, ossm: OssmCommander):
        """T01: Set type K (most common, default)."""
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_set_type_j(self, ossm: OssmCommander):
        """T02: Set type J."""
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_J)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_set_type_t(self, ossm: OssmCommander):
        """T03: Set type T."""
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_T)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("tc_type", [
        EThermocoupleType.TC_TYPE_B,
        EThermocoupleType.TC_TYPE_E,
        EThermocoupleType.TC_TYPE_J,
        EThermocoupleType.TC_TYPE_K,
        EThermocoupleType.TC_TYPE_N,
        EThermocoupleType.TC_TYPE_R,
        EThermocoupleType.TC_TYPE_S,
        EThermocoupleType.TC_TYPE_T,
    ])
    def test_set_all_valid_types(self, ossm: OssmCommander, tc_type: int):
        """T04: Set each valid thermocouple type (B, E, J, K, N, R, S, T)."""
        name = TC_TYPE_NAMES.get(tc_type, "Unknown")
        error = ossm.set_tc_type(tc_type=tc_type)
        assert error == ERR_OK, f"Failed to set type {name}: error 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_set_type_by_code(self, ossm: OssmCommander):
        """T05: Set type using raw code values 0-7."""
        for code in range(8):
            error = ossm.set_tc_type(tc_type=code)
            assert error == ERR_OK, f"Failed on code {code}: error 0x{error:02X}"


# =============================================================================
# Negative Tests
# =============================================================================

class TestTcTypeNegative:
    """Negative tests for invalid thermocouple type values."""

    @pytest.mark.requires_hardware
    def test_type_8_invalid(self, ossm: OssmCommander):
        """T20: Type 8 is invalid (max is 7)."""
        error = ossm.set_tc_type(tc_type=8)
        assert error == ERR_INVALID_TC_TYPE, \
            f"Expected ERR_INVALID_TC_TYPE (0x{ERR_INVALID_TC_TYPE:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_type_10_invalid(self, ossm: OssmCommander):
        """T21: Type 10 is invalid."""
        error = ossm.set_tc_type(tc_type=10)
        assert error == ERR_INVALID_TC_TYPE, \
            f"Expected ERR_INVALID_TC_TYPE (0x{ERR_INVALID_TC_TYPE:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_type_100_invalid(self, ossm: OssmCommander):
        """T22: Type 100 is invalid."""
        error = ossm.set_tc_type(tc_type=100)
        assert error == ERR_INVALID_TC_TYPE, \
            f"Expected ERR_INVALID_TC_TYPE (0x{ERR_INVALID_TC_TYPE:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_type_255_invalid(self, ossm: OssmCommander):
        """T23: Type 255 (max uint8) is invalid."""
        error = ossm.set_tc_type(tc_type=255)
        assert error == ERR_INVALID_TC_TYPE, \
            f"Expected ERR_INVALID_TC_TYPE (0x{ERR_INVALID_TC_TYPE:02X}), got 0x{error:02X}"


# =============================================================================
# Sequence Tests
# =============================================================================

class TestTcTypeSequence:
    """Tests for changing thermocouple type sequentially."""

    @pytest.mark.requires_hardware
    def test_change_type_multiple_times(self, ossm: OssmCommander):
        """T30: Change type multiple times in sequence."""
        # Start with K
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        assert error == ERR_OK

        # Change to J
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_J)
        assert error == ERR_OK

        # Change to T
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_T)
        assert error == ERR_OK

        # Back to K
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    def test_cycle_through_all_types(self, ossm: OssmCommander):
        """T31: Cycle through all types in order (B through T)."""
        for tc_type in range(8):
            error = ossm.set_tc_type(tc_type=tc_type)
            assert error == ERR_OK, f"Failed on type {tc_type}: error 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_set_same_type_twice(self, ossm: OssmCommander):
        """T32: Setting the same type twice should succeed."""
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        assert error == ERR_OK

        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        assert error == ERR_OK
