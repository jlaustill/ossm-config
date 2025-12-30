"""
Tests for CMD_NTC_PRESET (0x08) - Apply NTC Preset

This test module validates the NTC preset command which:
- Applies calibration presets for NTC temperature sensors
- Supports AEM, Bosch, and GM sensor types
- Validates input number and preset parameters
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    ERR_INVALID_TEMP_INPUT,
    ERR_INVALID_PRESET,
    NTC_PRESET_AEM,
    NTC_PRESET_BOSCH,
    NTC_PRESET_GM,
    MAX_TEMP_INPUTS,
)
from conftest import OssmCommander


# =============================================================================
# Positive Tests
# =============================================================================

class TestNtcPresetPositive:
    """Positive tests for CMD_NTC_PRESET."""

    @pytest.mark.requires_hardware
    def test_apply_aem_preset_input1(self, ossm: OssmCommander):
        """NP01: Apply AEM preset to temp input 1."""
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_apply_bosch_preset_input2(self, ossm: OssmCommander):
        """NP02: Apply Bosch preset to temp input 2."""
        error = ossm.set_ntc_preset(input_num=2, preset=NTC_PRESET_BOSCH)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_apply_gm_preset_input3(self, ossm: OssmCommander):
        """NP03: Apply GM preset to temp input 3."""
        error = ossm.set_ntc_preset(input_num=3, preset=NTC_PRESET_GM)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("preset,name", [
        (NTC_PRESET_AEM, "AEM"),
        (NTC_PRESET_BOSCH, "Bosch"),
        (NTC_PRESET_GM, "GM"),
    ])
    def test_apply_all_presets(self, ossm: OssmCommander, preset: int, name: str):
        """NP04: Apply each preset type."""
        error = ossm.set_ntc_preset(input_num=1, preset=preset)
        assert error == ERR_OK, f"Failed to apply {name} preset: error 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("input_num", range(1, MAX_TEMP_INPUTS + 1))
    def test_apply_preset_all_inputs(self, ossm: OssmCommander, input_num: int):
        """NP05: Apply AEM preset to each temp input (1-8)."""
        error = ossm.set_ntc_preset(input_num=input_num, preset=NTC_PRESET_AEM)
        assert error == ERR_OK, f"Failed on input {input_num}: error 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_apply_preset_to_max_input(self, ossm: OssmCommander):
        """NP06: Apply preset to max input (8)."""
        error = ossm.set_ntc_preset(input_num=MAX_TEMP_INPUTS, preset=NTC_PRESET_GM)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"


# =============================================================================
# Negative Tests - Invalid Input
# =============================================================================

class TestNtcPresetInvalidInput:
    """Negative tests for invalid input numbers."""

    @pytest.mark.requires_hardware
    def test_input_0_invalid(self, ossm: OssmCommander):
        """NP20: Input 0 should return ERR_INVALID_TEMP_INPUT."""
        error = ossm.set_ntc_preset(input_num=0, preset=NTC_PRESET_AEM)
        assert error == ERR_INVALID_TEMP_INPUT, \
            f"Expected ERR_INVALID_TEMP_INPUT (0x{ERR_INVALID_TEMP_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_input_9_out_of_range(self, ossm: OssmCommander):
        """NP21: Input 9 is out of range (max is 8)."""
        error = ossm.set_ntc_preset(input_num=9, preset=NTC_PRESET_AEM)
        assert error == ERR_INVALID_TEMP_INPUT, \
            f"Expected ERR_INVALID_TEMP_INPUT (0x{ERR_INVALID_TEMP_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_input_255_out_of_range(self, ossm: OssmCommander):
        """NP22: Input 255 (max uint8) should return ERR_INVALID_TEMP_INPUT."""
        error = ossm.set_ntc_preset(input_num=255, preset=NTC_PRESET_AEM)
        assert error == ERR_INVALID_TEMP_INPUT, \
            f"Expected ERR_INVALID_TEMP_INPUT (0x{ERR_INVALID_TEMP_INPUT:02X}), got 0x{error:02X}"


# =============================================================================
# Negative Tests - Invalid Preset
# =============================================================================

class TestNtcPresetInvalidPreset:
    """Negative tests for invalid preset values."""

    @pytest.mark.requires_hardware
    def test_preset_3_invalid(self, ossm: OssmCommander):
        """NP30: Preset 3 is invalid (only 0-2 valid)."""
        error = ossm.set_ntc_preset(input_num=1, preset=3)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_10_invalid(self, ossm: OssmCommander):
        """NP31: Preset 10 is invalid."""
        error = ossm.set_ntc_preset(input_num=1, preset=10)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_255_invalid(self, ossm: OssmCommander):
        """NP32: Preset 255 (max uint8) is invalid."""
        error = ossm.set_ntc_preset(input_num=1, preset=255)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"


# =============================================================================
# Combination Tests
# =============================================================================

class TestNtcPresetCombinations:
    """Tests for various preset and input combinations."""

    @pytest.mark.requires_hardware
    def test_different_presets_on_different_inputs(self, ossm: OssmCommander):
        """NP40: Apply different presets to different inputs."""
        # Input 1: AEM
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK

        # Input 2: Bosch
        error = ossm.set_ntc_preset(input_num=2, preset=NTC_PRESET_BOSCH)
        assert error == ERR_OK

        # Input 3: GM
        error = ossm.set_ntc_preset(input_num=3, preset=NTC_PRESET_GM)
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    def test_change_preset_on_same_input(self, ossm: OssmCommander):
        """NP41: Change preset on the same input multiple times."""
        # Start with AEM
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK

        # Change to Bosch
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_BOSCH)
        assert error == ERR_OK

        # Change to GM
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_GM)
        assert error == ERR_OK

        # Back to AEM
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK
