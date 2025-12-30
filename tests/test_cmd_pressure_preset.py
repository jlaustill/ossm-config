"""
Tests for CMD_PRESSURE_PRESET (0x09) - Apply Pressure Preset

This test module validates the pressure preset command which:
- Applies calibration presets for pressure sensors
- Supports Bar (PSIA) presets 0-15
- Supports PSI (PSIG) presets 20-30
- Note: Values 16-19 are a gap and should be invalid
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    ERR_INVALID_PRESSURE_INPUT,
    ERR_INVALID_PRESET,
    EPressurePreset,
    VALID_PRESSURE_PRESETS,
    MAX_PRESSURE_INPUTS,
)
from conftest import OssmCommander


# =============================================================================
# Positive Tests - Bar (PSIA) Presets
# =============================================================================

class TestPressurePresetBarPositive:
    """Positive tests for Bar/PSIA pressure presets (0-15)."""

    @pytest.mark.requires_hardware
    def test_apply_1bar_preset(self, ossm: OssmCommander):
        """PP01: Apply 1 bar preset to pressure input 1."""
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_1BAR)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_apply_10bar_preset(self, ossm: OssmCommander):
        """PP02: Apply 10 bar preset to pressure input 2."""
        error = ossm.set_pressure_preset(input_num=2, preset=EPressurePreset.PRES_PRESET_10BAR)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_apply_3000bar_preset(self, ossm: OssmCommander):
        """PP03: Apply 3000 bar (max) preset to pressure input 3."""
        error = ossm.set_pressure_preset(input_num=3, preset=EPressurePreset.PRES_PRESET_3000BAR)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("preset,name", [
        (EPressurePreset.PRES_PRESET_1BAR, "1 Bar"),
        (EPressurePreset.PRES_PRESET_1_5BAR, "1.5 Bar"),
        (EPressurePreset.PRES_PRESET_2BAR, "2 Bar"),
        (EPressurePreset.PRES_PRESET_2_5BAR, "2.5 Bar"),
        (EPressurePreset.PRES_PRESET_3BAR, "3 Bar"),
        (EPressurePreset.PRES_PRESET_4BAR, "4 Bar"),
        (EPressurePreset.PRES_PRESET_5BAR, "5 Bar"),
        (EPressurePreset.PRES_PRESET_7BAR, "7 Bar"),
        (EPressurePreset.PRES_PRESET_10BAR, "10 Bar"),
        (EPressurePreset.PRES_PRESET_50BAR, "50 Bar"),
        (EPressurePreset.PRES_PRESET_100BAR, "100 Bar"),
        (EPressurePreset.PRES_PRESET_150BAR, "150 Bar"),
        (EPressurePreset.PRES_PRESET_200BAR, "200 Bar"),
        (EPressurePreset.PRES_PRESET_1000BAR, "1000 Bar"),
        (EPressurePreset.PRES_PRESET_2000BAR, "2000 Bar"),
        (EPressurePreset.PRES_PRESET_3000BAR, "3000 Bar"),
    ])
    def test_apply_all_bar_presets(self, ossm: OssmCommander, preset: int, name: str):
        """PP04: Apply each valid Bar preset."""
        error = ossm.set_pressure_preset(input_num=1, preset=preset)
        assert error == ERR_OK, f"Failed to apply {name} preset: error 0x{error:02X}"


# =============================================================================
# Positive Tests - PSI (PSIG) Presets
# =============================================================================

class TestPressurePresetPsiPositive:
    """Positive tests for PSI/PSIG pressure presets (20-30)."""

    @pytest.mark.requires_hardware
    def test_apply_100psi_preset(self, ossm: OssmCommander):
        """PP10: Apply 100 PSI preset to pressure input 4."""
        error = ossm.set_pressure_preset(input_num=4, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_apply_500psi_preset(self, ossm: OssmCommander):
        """PP11: Apply 500 PSI (max) preset to pressure input 5."""
        error = ossm.set_pressure_preset(input_num=5, preset=EPressurePreset.PRES_PRESET_500PSI)
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("preset,name", [
        (EPressurePreset.PRES_PRESET_15PSI, "15 PSI"),
        (EPressurePreset.PRES_PRESET_30PSI, "30 PSI"),
        (EPressurePreset.PRES_PRESET_50PSI, "50 PSI"),
        (EPressurePreset.PRES_PRESET_100PSI, "100 PSI"),
        (EPressurePreset.PRES_PRESET_150PSI, "150 PSI"),
        (EPressurePreset.PRES_PRESET_200PSI, "200 PSI"),
        (EPressurePreset.PRES_PRESET_250PSI, "250 PSI"),
        (EPressurePreset.PRES_PRESET_300PSI, "300 PSI"),
        (EPressurePreset.PRES_PRESET_350PSI, "350 PSI"),
        (EPressurePreset.PRES_PRESET_400PSI, "400 PSI"),
        (EPressurePreset.PRES_PRESET_500PSI, "500 PSI"),
    ])
    def test_apply_all_psi_presets(self, ossm: OssmCommander, preset: int, name: str):
        """PP12: Apply each valid PSI preset."""
        error = ossm.set_pressure_preset(input_num=1, preset=preset)
        assert error == ERR_OK, f"Failed to apply {name} preset: error 0x{error:02X}"


# =============================================================================
# Positive Tests - Input Range
# =============================================================================

class TestPressurePresetInputRange:
    """Positive tests for valid input number range."""

    @pytest.mark.requires_hardware
    @pytest.mark.parametrize("input_num", range(1, MAX_PRESSURE_INPUTS + 1))
    def test_apply_preset_all_inputs(self, ossm: OssmCommander, input_num: int):
        """PP15: Apply preset to each pressure input (1-7)."""
        error = ossm.set_pressure_preset(input_num=input_num, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK, f"Failed on input {input_num}: error 0x{error:02X}"


# =============================================================================
# Negative Tests - Invalid Input
# =============================================================================

class TestPressurePresetInvalidInput:
    """Negative tests for invalid input numbers."""

    @pytest.mark.requires_hardware
    def test_input_0_invalid(self, ossm: OssmCommander):
        """PP20: Input 0 should return ERR_INVALID_PRESSURE_INPUT."""
        error = ossm.set_pressure_preset(input_num=0, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_INVALID_PRESSURE_INPUT, \
            f"Expected ERR_INVALID_PRESSURE_INPUT (0x{ERR_INVALID_PRESSURE_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_input_8_out_of_range(self, ossm: OssmCommander):
        """PP21: Input 8 is out of range for pressure (max is 7)."""
        error = ossm.set_pressure_preset(input_num=8, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_INVALID_PRESSURE_INPUT, \
            f"Expected ERR_INVALID_PRESSURE_INPUT (0x{ERR_INVALID_PRESSURE_INPUT:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_input_255_out_of_range(self, ossm: OssmCommander):
        """PP22: Input 255 (max uint8) should return ERR_INVALID_PRESSURE_INPUT."""
        error = ossm.set_pressure_preset(input_num=255, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_INVALID_PRESSURE_INPUT, \
            f"Expected ERR_INVALID_PRESSURE_INPUT (0x{ERR_INVALID_PRESSURE_INPUT:02X}), got 0x{error:02X}"


# =============================================================================
# Negative Tests - Invalid Preset (Gap 16-19)
# =============================================================================

class TestPressurePresetInvalidPreset:
    """Negative tests for invalid preset values (especially the 16-19 gap)."""

    @pytest.mark.requires_hardware
    def test_preset_16_invalid_gap(self, ossm: OssmCommander):
        """PP30: Preset 16 is in the gap (16-19) and should be invalid."""
        error = ossm.set_pressure_preset(input_num=1, preset=16)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_17_invalid_gap(self, ossm: OssmCommander):
        """PP31: Preset 17 is in the gap and should be invalid."""
        error = ossm.set_pressure_preset(input_num=1, preset=17)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_18_invalid_gap(self, ossm: OssmCommander):
        """PP32: Preset 18 is in the gap and should be invalid."""
        error = ossm.set_pressure_preset(input_num=1, preset=18)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_19_invalid_gap(self, ossm: OssmCommander):
        """PP33: Preset 19 is in the gap and should be invalid."""
        error = ossm.set_pressure_preset(input_num=1, preset=19)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_31_out_of_range(self, ossm: OssmCommander):
        """PP34: Preset 31 is out of range (max is 30)."""
        error = ossm.set_pressure_preset(input_num=1, preset=31)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_preset_255_out_of_range(self, ossm: OssmCommander):
        """PP35: Preset 255 (max uint8) should be invalid."""
        error = ossm.set_pressure_preset(input_num=1, preset=255)
        assert error == ERR_INVALID_PRESET, \
            f"Expected ERR_INVALID_PRESET (0x{ERR_INVALID_PRESET:02X}), got 0x{error:02X}"


# =============================================================================
# Combination Tests
# =============================================================================

class TestPressurePresetCombinations:
    """Tests for various preset and input combinations."""

    @pytest.mark.requires_hardware
    def test_mix_bar_and_psi_presets(self, ossm: OssmCommander):
        """PP40: Apply Bar preset to one input, PSI to another."""
        # Input 1: 10 Bar (PSIA)
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_10BAR)
        assert error == ERR_OK

        # Input 2: 100 PSI (PSIG)
        error = ossm.set_pressure_preset(input_num=2, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    def test_change_preset_bar_to_psi(self, ossm: OssmCommander):
        """PP41: Change preset from Bar to PSI on same input."""
        # Start with 10 Bar
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_10BAR)
        assert error == ERR_OK

        # Change to 100 PSI
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    def test_apply_all_valid_presets_sequentially(self, ossm: OssmCommander):
        """PP42: Apply all valid presets sequentially to input 1."""
        for preset in VALID_PRESSURE_PRESETS:
            error = ossm.set_pressure_preset(input_num=1, preset=preset)
            assert error == ERR_OK, f"Failed on preset {preset}: error 0x{error:02X}"
