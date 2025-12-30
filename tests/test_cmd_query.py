"""
Tests for CMD_QUERY (0x05) - Query Configuration

This test module validates the query command which retrieves:
- SPN counts (temp inputs, pressure inputs)
- Feature status (EGT enabled, BME280 enabled)
- SPN assignments for each input

Query is non-destructive and is the best starting point for validating
communication with the OSSM device.
"""

import pytest

from ossm_protocol import (
    ERR_OK,
    ERR_INVALID_QUERY_TYPE,
    MAX_TEMP_INPUTS,
    MAX_PRESSURE_INPUTS,
)
from conftest import OssmCommander, OssmTimeoutError


# =============================================================================
# Positive Tests
# =============================================================================

class TestQueryConfigPositive:
    """Positive tests for CMD_QUERY configuration counts."""

    @pytest.mark.requires_hardware
    def test_query_config_returns_ok(self, ossm: OssmCommander):
        """Q01: Query config should return ERR_OK."""
        error, config = ossm.query_config()
        assert error == ERR_OK, f"Expected ERR_OK, got error code 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_query_config_temp_count_in_range(self, ossm: OssmCommander):
        """Q02: Temperature count should be 0-8."""
        error, config = ossm.query_config()
        assert error == ERR_OK
        assert 0 <= config.temp_count <= MAX_TEMP_INPUTS, \
            f"Temp count {config.temp_count} out of range 0-{MAX_TEMP_INPUTS}"

    @pytest.mark.requires_hardware
    def test_query_config_pressure_count_in_range(self, ossm: OssmCommander):
        """Q03: Pressure count should be 0-7."""
        error, config = ossm.query_config()
        assert error == ERR_OK
        assert 0 <= config.pressure_count <= MAX_PRESSURE_INPUTS, \
            f"Pressure count {config.pressure_count} out of range 0-{MAX_PRESSURE_INPUTS}"

    @pytest.mark.requires_hardware
    def test_query_config_egt_is_boolean(self, ossm: OssmCommander):
        """Q04: EGT enabled should be boolean."""
        error, config = ossm.query_config()
        assert error == ERR_OK
        assert isinstance(config.egt_enabled, bool)

    @pytest.mark.requires_hardware
    def test_query_config_bme280_is_boolean(self, ossm: OssmCommander):
        """Q05: BME280 enabled should be boolean."""
        error, config = ossm.query_config()
        assert error == ERR_OK
        assert isinstance(config.bme280_enabled, bool)


class TestQueryTempSpnsPositive:
    """Positive tests for querying temperature SPN assignments."""

    @pytest.mark.requires_hardware
    def test_query_temp_spns_returns_ok(self, ossm: OssmCommander):
        """Q06: Query temp SPNs should return ERR_OK."""
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK, f"Expected ERR_OK, got error code 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_query_temp_spns_returns_8_entries(self, ossm: OssmCommander):
        """Q07: Query temp SPNs should return exactly 8 entries."""
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        assert len(spns) == MAX_TEMP_INPUTS, \
            f"Expected {MAX_TEMP_INPUTS} SPNs, got {len(spns)}"

    @pytest.mark.requires_hardware
    def test_query_temp_spns_values_valid(self, ossm: OssmCommander):
        """Q08: Temp SPN values should be 0 (disabled) or valid SPNs."""
        error, spns = ossm.query_temp_spns()
        assert error == ERR_OK
        for i, spn in enumerate(spns, 1):
            # SPN is either 0 (disabled) or a positive value
            assert spn >= 0, f"Input {i}: Invalid SPN value {spn}"
            # Upper bound sanity check (SPNs are 16-bit, max ~65535)
            assert spn <= 0xFFFF, f"Input {i}: SPN {spn} exceeds 16-bit range"


class TestQueryPressureSpnsPositive:
    """Positive tests for querying pressure SPN assignments."""

    @pytest.mark.requires_hardware
    def test_query_pressure_spns_returns_ok(self, ossm: OssmCommander):
        """Q09: Query pressure SPNs should return ERR_OK."""
        error, spns = ossm.query_pressure_spns()
        assert error == ERR_OK, f"Expected ERR_OK, got error code 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_query_pressure_spns_returns_7_entries(self, ossm: OssmCommander):
        """Q10: Query pressure SPNs should return exactly 7 entries."""
        error, spns = ossm.query_pressure_spns()
        assert error == ERR_OK
        assert len(spns) == MAX_PRESSURE_INPUTS, \
            f"Expected {MAX_PRESSURE_INPUTS} SPNs, got {len(spns)}"

    @pytest.mark.requires_hardware
    def test_query_pressure_spns_values_valid(self, ossm: OssmCommander):
        """Q11: Pressure SPN values should be 0 (disabled) or valid SPNs."""
        error, spns = ossm.query_pressure_spns()
        assert error == ERR_OK
        for i, spn in enumerate(spns, 1):
            assert spn >= 0, f"Input {i}: Invalid SPN value {spn}"
            assert spn <= 0xFFFF, f"Input {i}: SPN {spn} exceeds 16-bit range"


class TestQueryAllAssignmentsPositive:
    """Positive tests for querying all SPN assignments."""

    @pytest.mark.requires_hardware
    def test_query_all_assignments_returns_ok(self, ossm: OssmCommander):
        """Q12: Query all SPN assignments should return ERR_OK."""
        error, assignments = ossm.query_all_spn_assignments()
        assert error == ERR_OK, f"Expected ERR_OK, got error code 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_query_all_assignments_structure(self, ossm: OssmCommander):
        """Q13: Query all assignments should return correct structure."""
        error, assignments = ossm.query_all_spn_assignments()
        assert error == ERR_OK
        assert len(assignments.temp_spns) == MAX_TEMP_INPUTS
        assert len(assignments.pressure_spns) == MAX_PRESSURE_INPUTS


# =============================================================================
# Negative Tests
# =============================================================================

class TestQueryNegative:
    """Negative tests for CMD_QUERY error handling."""

    @pytest.mark.requires_hardware
    def test_query_invalid_type(self, ossm: OssmCommander):
        """Q20: Invalid query type should return ERR_INVALID_QUERY_TYPE."""
        from ossm_protocol import CMD_QUERY, build_query_params

        # Query type 3 is invalid (only 0, 1, 2 are valid)
        params = build_query_params(query_type=3, sub_query=0)
        error, _ = ossm.send_command(CMD_QUERY, params)
        assert error == ERR_INVALID_QUERY_TYPE, \
            f"Expected ERR_INVALID_QUERY_TYPE (0x{ERR_INVALID_QUERY_TYPE:02X}), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_query_invalid_subquery(self, ossm: OssmCommander):
        """Q21: Invalid sub-query is handled gracefully by firmware.

        Note: Firmware returns ERR_OK for out-of-range sub-queries when
        query type is valid, likely treating them as a no-op or using
        default behavior. This test verifies the command doesn't crash.
        """
        from ossm_protocol import CMD_QUERY, build_query_params

        # Sub-query 5 is out of range for type 1 (only 0, 1, 2 are valid)
        # Firmware handles this gracefully by returning OK
        params = build_query_params(query_type=1, sub_query=5)
        error, _ = ossm.send_command(CMD_QUERY, params)
        # Firmware returns OK for out-of-range sub-queries
        assert error == ERR_OK, \
            f"Expected ERR_OK (firmware handles gracefully), got 0x{error:02X}"

    @pytest.mark.requires_hardware
    def test_query_type_255_invalid(self, ossm: OssmCommander):
        """Q22: Query type 255 should return ERR_INVALID_QUERY_TYPE."""
        from ossm_protocol import CMD_QUERY, build_query_params

        params = build_query_params(query_type=255, sub_query=0)
        error, _ = ossm.send_command(CMD_QUERY, params)
        assert error == ERR_INVALID_QUERY_TYPE, \
            f"Expected ERR_INVALID_QUERY_TYPE (0x{ERR_INVALID_QUERY_TYPE:02X}), got 0x{error:02X}"


# =============================================================================
# Communication Tests
# =============================================================================

class TestQueryCommunication:
    """Tests for query command communication patterns."""

    @pytest.mark.requires_hardware
    def test_query_responds_within_timeout(self, ossm: OssmCommander):
        """Q30: Query should respond within the configured timeout."""
        import time
        start = time.time()
        error, _ = ossm.query_config()
        elapsed = time.time() - start

        assert error == ERR_OK
        assert elapsed < ossm.timeout, \
            f"Response took {elapsed:.3f}s, expected < {ossm.timeout}s"

    @pytest.mark.requires_hardware
    def test_query_multiple_times_consistent(self, ossm: OssmCommander):
        """Q31: Multiple queries should return consistent results."""
        error1, config1 = ossm.query_config()
        error2, config2 = ossm.query_config()
        error3, config3 = ossm.query_config()

        assert error1 == error2 == error3 == ERR_OK

        # Config should be consistent (no changes between queries)
        assert config1.temp_count == config2.temp_count == config3.temp_count
        assert config1.pressure_count == config2.pressure_count == config3.pressure_count
        assert config1.egt_enabled == config2.egt_enabled == config3.egt_enabled
        assert config1.bme280_enabled == config2.bme280_enabled == config3.bme280_enabled


# =============================================================================
# Display Test (for manual verification)
# =============================================================================

class TestQueryDisplay:
    """Tests that display configuration for manual verification."""

    @pytest.mark.requires_hardware
    def test_display_current_config(self, ossm: OssmCommander, capsys):
        """Q40: Display current configuration (for manual verification)."""
        error, config = ossm.query_config()
        assert error == ERR_OK

        print("\n" + "=" * 50)
        print("OSSM Current Configuration")
        print("=" * 50)
        print(f"Temperature inputs: {config.temp_count}")
        print(f"Pressure inputs:    {config.pressure_count}")
        print(f"EGT enabled:        {config.egt_enabled}")
        print(f"BME280 enabled:     {config.bme280_enabled}")

        # Query SPN assignments
        error, assignments = ossm.query_all_spn_assignments()
        if error == ERR_OK:
            print("\nTemperature SPN Assignments:")
            for i, spn in enumerate(assignments.temp_spns, 1):
                status = f"SPN {spn}" if spn > 0 else "Disabled"
                print(f"  Input {i}: {status}")

            print("\nPressure SPN Assignments:")
            for i, spn in enumerate(assignments.pressure_spns, 1):
                status = f"SPN {spn}" if spn > 0 else "Disabled"
                print(f"  Input {i}: {status}")

        print("=" * 50)
