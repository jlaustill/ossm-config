"""
Tests for CMD_ENABLE_SPN (0x01) - Enable/Disable SPN on Input

This test module validates the enable SPN command which:
- Enables a specific SPN on a hardware input
- Disables a previously enabled SPN
- Validates SPN and input number parameters
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    ERR_UNKNOWN_SPN,
    ERR_INVALID_TEMP_INPUT,
    ERR_INVALID_PRESSURE_INPUT,
    VALID_TEMP_SPNS,
    VALID_PRESSURE_SPNS,
    TEMP_SPNS,
    PRESSURE_SPNS,
    EGT_SPN,
    BME280_SPNS,
    MAX_TEMP_INPUTS,
    MAX_PRESSURE_INPUTS,
)
from conftest import OssmCommander


# =============================================================================
# Positive Tests - Temperature SPNs
# =============================================================================

class TestEnableSpnTempPositive:
    """Positive tests for enabling temperature SPNs."""

    @pytest.mark.requires_hardware
    def test_enable_oil_temp_on_input1(self, ossm: OssmCommander):
        """E01: Enable oil temp SPN 175 on temp input 1."""
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_enable_coolant_temp_on_input2(self, ossm: OssmCommander):
        """E02: Enable coolant temp SPN 110 on temp input 2."""
        error = ossm.enable_spn(spn=110, enable=True, input_num=2)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_enable_fuel_temp_on_input3(self, ossm: OssmCommander):
        """E03: Enable fuel temp SPN 174 on temp input 3."""
        error = ossm.enable_spn(spn=174, enable=True, input_num=3)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_disable_previously_enabled_spn(self, ossm: OssmCommander):
        """E04: Disable a previously enabled SPN."""
        # First enable
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Then disable
        error = ossm.enable_spn(spn=175, enable=False, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("spn,name", [
        (175, "Engine Oil Temp"),
        (110, "Coolant Temp"),
        (174, "Fuel Temp"),
        (105, "Boost Temp"),
        (1131, "CAC Inlet Temp"),
        (1132, "Transfer Pipe Temp"),
        (1133, "Air Inlet Temp"),
        (172, "Air Inlet Temp 2"),
        (441, "Engine Bay Temp"),
    ])
    def test_enable_all_temp_spns(self, ossm: OssmCommander, spn: int, name: str):
        """E05: Enable each valid temperature SPN."""
        error = ossm.enable_spn(spn=spn, enable=True, input_num=1)
        assert error == ERR_OK, f"Failed to enable {name} (SPN {spn}): error 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("input_num", range(1, MAX_TEMP_INPUTS + 1))
    def test_enable_on_all_temp_inputs(self, ossm: OssmCommander, input_num: int):
        """E06: Enable SPN on each valid temperature input (1-8)."""
        error = ossm.enable_spn(spn=175, enable=True, input_num=input_num)
        assert error == ERR_OK, f"Failed on input {input_num}: error 0x{error:02X}"


# =============================================================================
# Positive Tests - Pressure SPNs
# =============================================================================

class TestEnableSpnPressurePositive:
    """Positive tests for enabling pressure SPNs."""

    @pytest.mark.requires_hardware
    def test_enable_oil_pressure_on_input1(self, ossm: OssmCommander):
        """E10: Enable oil pressure SPN 100 on pressure input 1."""
        error = ossm.enable_spn(spn=100, enable=True, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("spn,name", [
        (100, "Engine Oil Pres"),
        (109, "Coolant Pres"),
        (94, "Fuel Delivery Pres"),
        (102, "Boost Pres"),
        (106, "Air Inlet Pres"),
        (1127, "CAC Inlet Pres"),
        (1128, "Transfer Pipe Pres"),
    ])
    def test_enable_all_pressure_spns(self, ossm: OssmCommander, spn: int, name: str):
        """E11: Enable each valid pressure SPN."""
        error = ossm.enable_spn(spn=spn, enable=True, input_num=1)
        assert error == ERR_OK, f"Failed to enable {name} (SPN {spn}): error 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("input_num", range(1, MAX_PRESSURE_INPUTS + 1))
    def test_enable_on_all_pressure_inputs(self, ossm: OssmCommander, input_num: int):
        """E12: Enable SPN on each valid pressure input (1-7)."""
        error = ossm.enable_spn(spn=100, enable=True, input_num=input_num)
        assert error == ERR_OK, f"Failed on input {input_num}: error 0x{error:02X}"


# =============================================================================
# Positive Tests - Special SPNs (EGT, BME280)
# =============================================================================

class TestEnableSpnSpecialPositive:
    """Positive tests for enabling special SPNs (EGT, BME280)."""

    @pytest.mark.requires_hardware
    def test_enable_egt_spn(self, ossm: OssmCommander):
        """E15: Enable EGT SPN 173."""
        error = ossm.enable_spn(spn=EGT_SPN, enable=True, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_enable_ambient_temp_spn(self, ossm: OssmCommander):
        """E16: Enable BME280 ambient temp SPN 171."""
        error = ossm.enable_spn(spn=171, enable=True, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_enable_barometric_pressure_spn(self, ossm: OssmCommander):
        """E17: Enable BME280 barometric pressure SPN 108."""
        error = ossm.enable_spn(spn=108, enable=True, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_enable_humidity_spn(self, ossm: OssmCommander):
        """E18: Enable BME280 humidity SPN 354."""
        error = ossm.enable_spn(spn=354, enable=True, input_num=1)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"


# =============================================================================
# Negative Tests - Invalid SPN
# =============================================================================

class TestEnableSpnInvalidSpn:
    """Negative tests for invalid SPN values."""

    @pytest.mark.requires_hardware
    def test_invalid_spn_9999(self, ossm: OssmCommander):
        """E20: SPN 9999 (not in database) should return ERR_UNKNOWN_SPN."""
        error = ossm.enable_spn(spn=9999, enable=True, input_num=1)
        assert error == ERR_UNKNOWN_SPN, \
            f"Expected ERR_UNKNOWN_SPN (0x{ERR_UNKNOWN_SPN:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_invalid_spn_0(self, ossm: OssmCommander):
        """E21: SPN 0 should return ERR_UNKNOWN_SPN."""
        error = ossm.enable_spn(spn=0, enable=True, input_num=1)
        assert error == ERR_UNKNOWN_SPN, \
            f"Expected ERR_UNKNOWN_SPN (0x{ERR_UNKNOWN_SPN:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_invalid_spn_65535(self, ossm: OssmCommander):
        """E22: SPN 65535 (max uint16) should return ERR_UNKNOWN_SPN."""
        error = ossm.enable_spn(spn=65535, enable=True, input_num=1)
        assert error == ERR_UNKNOWN_SPN, \
            f"Expected ERR_UNKNOWN_SPN (0x{ERR_UNKNOWN_SPN:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_invalid_spn_random(self, ossm: OssmCommander):
        """E23: Random invalid SPN should return ERR_UNKNOWN_SPN."""
        # 12345 is not a known SPN
        error = ossm.enable_spn(spn=12345, enable=True, input_num=1)
        assert error == ERR_UNKNOWN_SPN, \
            f"Expected ERR_UNKNOWN_SPN (0x{ERR_UNKNOWN_SPN:02X}), got 0x{error:02X}"


# =============================================================================
# Negative Tests - Invalid Input Number
# =============================================================================

class TestEnableSpnInvalidInput:
    """Negative tests for invalid input numbers."""

    @pytest.mark.requires_hardware
    def test_input_0_invalid(self, ossm: OssmCommander):
        """E30: Input 0 should return ERR_INVALID_TEMP_INPUT (inputs are 1-indexed)."""
        error = ossm.enable_spn(spn=175, enable=True, input_num=0)
        assert error == ERR_INVALID_TEMP_INPUT, \
            f"Expected ERR_INVALID_TEMP_INPUT (0x{ERR_INVALID_TEMP_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_temp_input_9_out_of_range(self, ossm: OssmCommander):
        """E31: Temp input 9 is out of range (max is 8)."""
        error = ossm.enable_spn(spn=175, enable=True, input_num=9)
        assert error == ERR_INVALID_TEMP_INPUT, \
            f"Expected ERR_INVALID_TEMP_INPUT (0x{ERR_INVALID_TEMP_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_pressure_input_8_out_of_range(self, ossm: OssmCommander):
        """E32: Pressure input 8 is out of range (max is 7)."""
        error = ossm.enable_spn(spn=100, enable=True, input_num=8)
        assert error == ERR_INVALID_PRESSURE_INPUT, \
            f"Expected ERR_INVALID_PRESSURE_INPUT (0x{ERR_INVALID_PRESSURE_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_input_255_out_of_range(self, ossm: OssmCommander):
        """E33: Input 255 (max uint8) should return ERR_INVALID_TEMP_INPUT."""
        error = ossm.enable_spn(spn=175, enable=True, input_num=255)
        assert error == ERR_INVALID_TEMP_INPUT, \
            f"Expected ERR_INVALID_TEMP_INPUT (0x{ERR_INVALID_TEMP_INPUT:02X}), got 0x{error:02X}"


# =============================================================================
# Verification Tests
# =============================================================================

class TestEnableSpnVerification:
    """Tests that verify enable/disable actually takes effect."""

    @pytest.mark.requires_hardware
    def test_enable_then_query_shows_spn(self, ossm: OssmCommander):
        """E40: After enabling SPN, query should show it assigned."""
        # Enable oil temp on input 1
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Query temp SPNs
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 175, f"Expected SPN 175 on input 1, got {spns[0]}"

    @pytest.mark.requires_hardware
    def test_disable_then_query_shows_zero(self, ossm: OssmCommander):
        """E41: After disabling SPN, query should show 0 (disabled)."""
        # First enable
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Then disable
        error = ossm.enable_spn(spn=175, enable=False, input_num=1)
        assert error == ERR_OK

        # Query temp SPNs
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 0, f"Expected SPN 0 (disabled) on input 1, got {spns[0]}"

    @pytest.mark.requires_hardware
    def test_reassign_spn_to_different_input(self, ossm: OssmCommander):
        """E42: Moving SPN from input 1 to input 3 should update correctly."""
        # Enable on input 1
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Enable on input 3 (should move it)
        error = ossm.enable_spn(spn=175, enable=True, input_num=3)
        assert error == ERR_OK

        # Query - input 3 should have the SPN
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[2] == 175, f"Expected SPN 175 on input 3, got {spns[2]}"

    @pytest.mark.requires_hardware
    def test_enable_multiple_spns(self, ossm: OssmCommander):
        """E43: Enable multiple SPNs on different inputs."""
        # Enable oil temp on input 1
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Enable coolant temp on input 2
        error = ossm.enable_spn(spn=110, enable=True, input_num=2)
        assert error == ERR_OK

        # Enable fuel temp on input 3
        error = ossm.enable_spn(spn=174, enable=True, input_num=3)
        assert error == ERR_OK

        # Query and verify
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 175, f"Expected SPN 175 on input 1, got {spns[0]}"
        assert spns[1] == 110, f"Expected SPN 110 on input 2, got {spns[1]}"
        assert spns[2] == 174, f"Expected SPN 174 on input 3, got {spns[2]}"
