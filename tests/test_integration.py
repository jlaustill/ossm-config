"""
Integration Tests - Multi-Command Workflow Validation

These tests verify that multiple commands work together correctly
in realistic configuration workflows.
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    NTC_PRESET_AEM,
    NTC_PRESET_BOSCH,
    NTC_PRESET_GM,
    EPressurePreset,
    EThermocoupleType,
)
from conftest import OssmCommander


# =============================================================================
# Full Sensor Setup Workflows
# =============================================================================

class TestSensorSetupWorkflow:
    """Tests for complete sensor configuration workflows."""

    @pytest.mark.requires_hardware
    def test_setup_three_temp_sensors(self, ossm: OssmCommander):
        """I01: Configure 3 temperature sensors with presets and SPNs."""
        # Apply NTC presets first
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK, "Failed to set NTC preset on input 1"

        error = ossm.set_ntc_preset(input_num=2, preset=NTC_PRESET_BOSCH)
        assert error == ERR_OK, "Failed to set NTC preset on input 2"

        error = ossm.set_ntc_preset(input_num=3, preset=NTC_PRESET_GM)
        assert error == ERR_OK, "Failed to set NTC preset on input 3"

        # Enable SPNs
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)  # Oil temp
        assert error == ERR_OK, "Failed to enable oil temp"

        error = ossm.enable_spn(spn=110, enable=True, input_num=2)  # Coolant temp
        assert error == ERR_OK, "Failed to enable coolant temp"

        error = ossm.enable_spn(spn=174, enable=True, input_num=3)  # Fuel temp
        assert error == ERR_OK, "Failed to enable fuel temp"

        # Verify via query
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 175, f"Expected SPN 175, got {spns[0]}"
        assert spns[1] == 110, f"Expected SPN 110, got {spns[1]}"
        assert spns[2] == 174, f"Expected SPN 174, got {spns[2]}"

    @pytest.mark.requires_hardware
    def test_setup_two_pressure_sensors(self, ossm: OssmCommander):
        """I02: Configure 2 pressure sensors with presets and SPNs."""
        # Apply pressure presets
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_10BAR)
        assert error == ERR_OK, "Failed to set 10 bar preset"

        error = ossm.set_pressure_preset(input_num=2, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK, "Failed to set 100 PSI preset"

        # Enable SPNs
        error = ossm.enable_spn(spn=100, enable=True, input_num=1)  # Oil pressure
        assert error == ERR_OK, "Failed to enable oil pressure"

        error = ossm.enable_spn(spn=94, enable=True, input_num=2)  # Fuel pressure
        assert error == ERR_OK, "Failed to enable fuel pressure"

        # Verify via query
        error, spns = ossm.query_pressure_spns()
        assert error == ERR_OK
        assert spns[0] == 100, f"Expected SPN 100, got {spns[0]}"
        assert spns[1] == 94, f"Expected SPN 94, got {spns[1]}"

    @pytest.mark.requires_hardware
    def test_setup_egt_with_thermocouple_type(self, ossm: OssmCommander):
        """I03: Configure EGT with thermocouple type selection."""
        # Set thermocouple type to K
        error = ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        assert error == ERR_OK, "Failed to set thermocouple type"

        # Enable EGT SPN
        error = ossm.enable_spn(spn=173, enable=True, input_num=1)
        assert error == ERR_OK, "Failed to enable EGT"


# =============================================================================
# Configuration Change Workflows
# =============================================================================

class TestConfigurationChanges:
    """Tests for modifying existing configuration."""

    @pytest.mark.requires_hardware
    def test_reassign_spn_between_inputs(self, ossm: OssmCommander):
        """I10: Move SPN from one input to another."""
        # Enable on input 1
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Verify on input 1
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 175

        # Move to input 3
        error = ossm.enable_spn(spn=175, enable=True, input_num=3)
        assert error == ERR_OK

        # Verify on input 3
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[2] == 175, f"Expected SPN 175 on input 3, got {spns[2]}"

    @pytest.mark.requires_hardware
    def test_change_ntc_preset_after_enable(self, ossm: OssmCommander):
        """I11: Change NTC preset after SPN is already enabled."""
        # Enable SPN first
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Change preset (should still work)
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK

        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_BOSCH)
        assert error == ERR_OK

        # SPN should still be enabled
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert spns[0] == 175

    @pytest.mark.requires_hardware
    def test_change_pressure_preset_after_enable(self, ossm: OssmCommander):
        """I12: Change pressure preset after SPN is already enabled."""
        # Enable SPN first
        error = ossm.enable_spn(spn=100, enable=True, input_num=1)
        assert error == ERR_OK

        # Change preset from Bar to PSI
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_10BAR)
        assert error == ERR_OK

        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK

        # SPN should still be enabled
        error, spns = ossm.query_pressure_spns()
        assert error == ERR_OK
        assert spns[0] == 100


# =============================================================================
# Query Verification Workflows
# =============================================================================

class TestQueryVerification:
    """Tests that verify query reflects configuration changes."""

    @pytest.mark.requires_hardware
    def test_query_config_counts_update(self, ossm: OssmCommander):
        """I20: Config counts should update as SPNs are enabled."""
        # Query initial state
        error, config_before = ossm.query_config()
        assert error == ERR_OK

        # Enable a temp SPN
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

        # Query again - temp count should increase or be at least 1
        error, config_after = ossm.query_config()
        assert error == ERR_OK
        assert config_after.temp_count >= 1, "Temp count should be at least 1 after enable"

    @pytest.mark.requires_hardware
    def test_full_assignment_query(self, ossm: OssmCommander):
        """I21: Query all assignments returns complete picture."""
        # Set up multiple SPNs
        ossm.enable_spn(spn=175, enable=True, input_num=1)
        ossm.enable_spn(spn=110, enable=True, input_num=2)
        ossm.enable_spn(spn=100, enable=True, input_num=1)

        # Query all
        error, assignments = ossm.query_all_spn_assignments()
        assert error == ERR_OK

        # Verify structure
        assert len(assignments.temp_spns) == 8
        assert len(assignments.pressure_spns) == 7

        # Verify assignments
        assert assignments.temp_spns[0] == 175
        assert assignments.temp_spns[1] == 110
        assert assignments.pressure_spns[0] == 100


# =============================================================================
# Error Recovery Workflows
# =============================================================================

class TestErrorRecovery:
    """Tests for handling and recovering from errors."""

    @pytest.mark.requires_hardware
    def test_continue_after_unknown_spn(self, ossm: OssmCommander):
        """I30: Should continue working after unknown SPN error."""
        from ossm_protocol import ERR_UNKNOWN_SPN

        # Try invalid SPN
        error = ossm.enable_spn(spn=9999, enable=True, input_num=1)
        assert error == ERR_UNKNOWN_SPN

        # Valid command should still work
        error = ossm.enable_spn(spn=175, enable=True, input_num=1)
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    def test_continue_after_invalid_temp_input(self, ossm: OssmCommander):
        """I31: Should continue working after invalid temp input error."""
        from ossm_protocol import ERR_INVALID_TEMP_INPUT

        # Try invalid input
        error = ossm.set_ntc_preset(input_num=99, preset=NTC_PRESET_AEM)
        assert error == ERR_INVALID_TEMP_INPUT

        # Valid command should still work
        error = ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        assert error == ERR_OK

    @pytest.mark.requires_hardware
    def test_continue_after_invalid_preset(self, ossm: OssmCommander):
        """I32: Should continue working after invalid preset error."""
        from ossm_protocol import ERR_INVALID_PRESET

        # Try invalid preset
        error = ossm.set_pressure_preset(input_num=1, preset=99)
        assert error == ERR_INVALID_PRESET

        # Valid command should still work
        error = ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_100PSI)
        assert error == ERR_OK


# =============================================================================
# Complete System Setup
# =============================================================================

class TestCompleteSystemSetup:
    """Tests for full system configuration scenarios."""

    @pytest.mark.requires_hardware
    def test_typical_engine_monitoring_setup(self, ossm: OssmCommander):
        """I40: Typical engine monitoring configuration."""
        # Temperature sensors with AEM NTC
        ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_AEM)
        ossm.set_ntc_preset(input_num=2, preset=NTC_PRESET_AEM)
        ossm.set_ntc_preset(input_num=3, preset=NTC_PRESET_AEM)

        ossm.enable_spn(spn=175, enable=True, input_num=1)  # Oil temp
        ossm.enable_spn(spn=110, enable=True, input_num=2)  # Coolant temp
        ossm.enable_spn(spn=174, enable=True, input_num=3)  # Fuel temp

        # Pressure sensors with 10 bar preset
        ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_10BAR)
        ossm.set_pressure_preset(input_num=2, preset=EPressurePreset.PRES_PRESET_10BAR)

        ossm.enable_spn(spn=100, enable=True, input_num=1)  # Oil pressure
        ossm.enable_spn(spn=94, enable=True, input_num=2)   # Fuel pressure

        # EGT with Type K thermocouple
        ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        ossm.enable_spn(spn=173, enable=True, input_num=1)

        # Verify all assignments
        error, config = ossm.query_config()
        assert error == ERR_OK
        assert config.temp_count >= 3, "Should have at least 3 temp sensors"

        error, temp_spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert 175 in temp_spns[:3]
        assert 110 in temp_spns[:3]
        assert 174 in temp_spns[:3]

        error, pres_spns = ossm.query_pressure_spns()
        assert error == ERR_OK
        assert 100 in pres_spns[:2]
        assert 94 in pres_spns[:2]

    @pytest.mark.requires_hardware
    def test_turbo_monitoring_setup(self, ossm: OssmCommander):
        """I41: Turbo-focused monitoring configuration."""
        # Boost temperature
        ossm.set_ntc_preset(input_num=1, preset=NTC_PRESET_BOSCH)
        ossm.enable_spn(spn=105, enable=True, input_num=1)

        # CAC inlet temperature
        ossm.set_ntc_preset(input_num=2, preset=NTC_PRESET_BOSCH)
        ossm.enable_spn(spn=1131, enable=True, input_num=2)

        # Boost pressure (3 bar for turbo)
        ossm.set_pressure_preset(input_num=1, preset=EPressurePreset.PRES_PRESET_3BAR)
        ossm.enable_spn(spn=102, enable=True, input_num=1)

        # CAC inlet pressure
        ossm.set_pressure_preset(input_num=2, preset=EPressurePreset.PRES_PRESET_2BAR)
        ossm.enable_spn(spn=1127, enable=True, input_num=2)

        # EGT
        ossm.set_tc_type(tc_type=EThermocoupleType.TC_TYPE_K)
        ossm.enable_spn(spn=173, enable=True, input_num=1)

        # Verify
        error, temp_spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert 105 in temp_spns[:2]
        assert 1131 in temp_spns[:2]
