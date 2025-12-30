"""
Tests for CMD_SAVE (0x06) and CMD_RESET (0x07)

These tests are marked as DESTRUCTIVE because:
- CMD_SAVE writes to EEPROM (finite write cycles)
- CMD_RESET erases current configuration

Run these tests explicitly with: pytest -v -m destructive
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    ERR_SAVE_FAILED,
)
from conftest import OssmCommander


# =============================================================================
# CMD_SAVE Tests
# =============================================================================

class TestSaveConfig:
    """Tests for CMD_SAVE - Save configuration to EEPROM."""

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_save_config_returns_ok(self, ossm: OssmCommander):
        """S01: Save config should return ERR_OK."""
        error = ossm.save_config()
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_save_after_changes(self, ossm: OssmCommander):
        """S02: Save after making configuration changes."""
        # Make a change
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Save it
        error = ossm.save_config()
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_save_multiple_times(self, ossm: OssmCommander):
        """S03: Multiple saves should all succeed."""
        for i in range(3):
            error = ossm.save_config()
            assert error == ERR_OK, f"Save {i+1} failed: error 0x{error:02X}"


# =============================================================================
# CMD_RESET Tests
# =============================================================================

class TestResetConfig:
    """Tests for CMD_RESET - Reset to factory defaults."""

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_reset_config_returns_ok(self, ossm: OssmCommander):
        """R01: Reset config should return ERR_OK."""
        error = ossm.reset_config()
        assert error == ERR_OK, f"Expected ERR_OK, got 0x{error:02X}"

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_reset_clears_configuration(self, ossm: OssmCommander):
        """R02: Reset should clear all SPN assignments."""
        # First make some changes
        ossm.enable_spn(spn=175, enable=True, input_num=1)
        ossm.enable_spn(spn=110, enable=True, input_num=2)

        # Reset
        error = ossm.reset_config()
        assert error == ERR_OK

        # Query and verify cleared
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK

        # All SPNs should be 0 (disabled) after reset
        for i, spn in enumerate(spns, 1):
            assert spn == 0, f"Input {i} still has SPN {spn} after reset"

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_reset_clears_pressure_spns(self, ossm: OssmCommander):
        """R03: Reset should clear all pressure SPN assignments."""
        # First make some changes
        ossm.enable_spn(spn=100, enable=True, input_num=1)
        ossm.enable_spn(spn=109, enable=True, input_num=2)

        # Reset
        error = ossm.reset_config()
        assert error == ERR_OK

        # Query and verify cleared
        error, spns = ossm.query_pressure_spns()
        assert error == ERR_OK

        # All SPNs should be 0 (disabled) after reset
        for i, spn in enumerate(spns, 1):
            assert spn == 0, f"Pressure input {i} still has SPN {spn} after reset"


# =============================================================================
# Save/Reset Interaction Tests
# =============================================================================

class TestSaveResetInteraction:
    """Tests for save/reset interaction patterns."""

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_configure_save_reset_verify(self, ossm: OssmCommander):
        """SR01: Configure -> Save -> Reset -> Query shows defaults."""
        # Configure
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Save
        error = ossm.save_config()
        assert error == ERR_OK

        # Reset
        error = ossm.reset_config()
        assert error == ERR_OK

        # Query - should show defaults (all disabled)
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 0, "SPN should be cleared after reset"

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_reset_then_save(self, ossm: OssmCommander):
        """SR02: Reset -> Save should save the default state."""
        # Reset to defaults
        error = ossm.reset_config()
        assert error == ERR_OK

        # Save the default state
        error = ossm.save_config()
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    @pytest.mark.destructive
    def test_save_preserves_config(self, ossm: OssmCommander):
        """SR03: After save, config should persist through reset only if re-saved."""
        # Configure
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Save
        error = ossm.save_config()
        assert error == ERR_OK

        # Query to verify it's set
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 175, "SPN 175 should be set on input 1"

        # Reset clears RAM but EEPROM still has the config
        # (Note: actual persistence test would require power cycle)
        error = ossm.reset_config()
        assert error == ERR_OK

        # After reset, RAM config is cleared
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        # Note: This tests RAM state after reset, not EEPROM persistence
