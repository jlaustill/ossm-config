#include "j1939.h"
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <stdio.h>

// J1939 ID structure: PPP RRRR PPPPPPPP PPPPPPPP SSSSSSSS
// P = Priority (3 bits), R = Reserved/DP (1 bit), PGN (18 bits), S = Source (8 bits)

uint32_t j1939_get_pgn(uint32_t can_id) {
    // PDU Format (PF) is bits 16-23
    uint8_t pf = (can_id >> 16) & 0xFF;

    if (pf < 240) {
        // PDU1 format: PGN = PF * 256 (PS is destination)
        return ((uint32_t)pf) << 8;
    } else {
        // PDU2 format: PGN = PF * 256 + PS
        uint8_t ps = (can_id >> 8) & 0xFF;
        return (((uint32_t)pf) << 8) | ps;
    }
}

uint8_t j1939_get_source(uint32_t can_id) {
    return can_id & 0xFF;
}

uint32_t j1939_build_id(uint32_t pgn, uint8_t priority, uint8_t source) {
    // Priority in bits 26-28, PGN in bits 8-25, source in bits 0-7
    return ((uint32_t)(priority & 0x07) << 26) |
           ((pgn & 0x3FFFF) << 8) |
           source;
}

// Convert J1939 temperature byte to Celsius (1°C/bit, +40 offset)
static float decode_temp_byte(uint8_t byte) {
    if (byte == 0xFF) return -999.0f;  // Not available
    return (float)byte - 40.0f;
}

// Convert J1939 16-bit temperature to Celsius (0.03125 deg/bit, -273 offset)
// J1939 uses little-endian (low byte first)
static float decode_temp_16bit_le(uint8_t low, uint8_t high) {
    if (high == 0xFF && low == 0xFF) return -999.0f;
    uint16_t val = ((uint16_t)high << 8) | low;
    return (float)val * 0.03125f - 273.0f;
}

// Convert J1939 pressure byte to kPa (2 kPa/bit)
static float decode_pressure_2kpa(uint8_t byte) {
    if (byte == 0xFF) return -999.0f;
    return (float)byte * 2.0f;
}

// Convert J1939 pressure byte to kPa (4 kPa/bit)
static float decode_pressure_4kpa(uint8_t byte) {
    if (byte == 0xFF) return -999.0f;
    return (float)byte * 4.0f;
}

// Convert J1939 barometric pressure to kPa (0.5 kPa/bit)
static float decode_baro_pressure(uint8_t byte) {
    if (byte == 0xFF) return -999.0f;
    return (float)byte * 0.5f;
}

// Convert humidity (0.4%/bit)
static float decode_humidity(uint8_t byte) {
    if (byte == 0xFF) return -999.0f;
    return (float)byte * 0.4f;
}

static uint32_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

bool j1939_parse_message(const TCanFrame* frame, TSensorData* data) {
    if (!frame->extended) return false;

    uint8_t source = j1939_get_source(frame->id);
    if (source != OSSM_SOURCE_ADDRESS) return false;

    uint32_t pgn = j1939_get_pgn(frame->id);
    const uint8_t* d = frame->data;
    bool updated = false;

    switch (pgn) {
        case PGN_AMBIENT_CONDITIONS:  // 65269
            // OSSM encoding (J1939 little-endian):
            // buf[0] = barometric * 2 (0.5 kPa/bit)
            // buf[3-4] = ambient temp 16-bit LE (0.03125°C/bit, +273 offset)
            // buf[5] = air inlet temp (1°C/bit, +40 offset)
            data->absoluteBarometricPressurekPa = decode_baro_pressure(d[0]);
            data->ambientTemperatureC = decode_temp_16bit_le(d[3], d[4]);
            data->airInletTemperatureC = decode_temp_byte(d[5]);
            updated = true;
            break;

        case PGN_INLET_EXHAUST:  // 65270
            // OSSM encoding (J1939 little-endian):
            // buf[1] = boost pressure / 2 (2 kPa/bit)
            // buf[2] = air inlet temp + 40 (boost temp, 1°C/bit)
            // buf[3] = air inlet pressure / 2 (2 kPa/bit)
            // buf[5-6] = EGT 16-bit LE (0.03125°C/bit, +273 offset)
            data->boostPressurekPa = decode_pressure_2kpa(d[1]);
            data->boostTemperatureC = decode_temp_byte(d[2]);
            data->airInletPressurekPa = decode_pressure_2kpa(d[3]);
            data->egtTemperatureC = decode_temp_16bit_le(d[5], d[6]);
            updated = true;
            break;

        case PGN_ENGINE_TEMP:  // 65262
            // OSSM encoding (J1939 little-endian):
            // buf[0] = coolant temp + 40 (1°C/bit)
            // buf[1] = fuel temp + 40 (1°C/bit)
            // buf[2-3] = oil temp 16-bit LE (0.03125°C/bit, +273 offset)
            data->coolantTemperatureC = decode_temp_byte(d[0]);
            data->fuelTemperatureC = decode_temp_byte(d[1]);
            data->oilTemperatureC = decode_temp_16bit_le(d[2], d[3]);
            updated = true;
            break;

        case PGN_ENGINE_FLUID_PRESS:  // 65263
            // OSSM encoding:
            // buf[0] = fuel pressure / 4 (4 kPa/bit)
            // buf[3] = oil pressure / 4 (4 kPa/bit)
            // buf[6] = coolant pressure / 2 (2 kPa/bit)
            data->fuelPressurekPa = decode_pressure_4kpa(d[0]);
            data->oilPressurekPa = decode_pressure_4kpa(d[3]);
            data->coolantPressurekPa = decode_pressure_2kpa(d[6]);
            updated = true;
            break;

        case PGN_ENGINE_TEMP_2:  // 65129
            // OSSM encoding:
            // buf[0-1] = intake manifold 1 temp 16-bit big-endian (hi-res boost temp)
            // buf[2-3] = coolant temp 16-bit big-endian (hi-res)
            // Note: we already get boost temp from 65270, this is hi-res version
            // data->boostTemperatureC = decode_temp_16bit_be(d[0], d[1]);
            updated = true;
            break;

        case PGN_ENGINE_TEMP_3:  // 65189
            // OSSM encoding:
            // buf[0] = intake manifold 2 temp (CAC inlet, 1°C/bit, +40)
            // buf[1] = intake manifold 3 temp (transfer pipe, 1°C/bit, +40)
            // buf[2] = intake manifold 4 temp (air inlet, 1°C/bit, +40)
            data->cacInletTemperatureC = decode_temp_byte(d[0]);
            data->transferPipeTemperatureC = decode_temp_byte(d[1]);
            updated = true;
            break;

        case PGN_TURBO_PRESS:  // 65190
            // OSSM encoding (J1939 little-endian):
            // buf[0-1] = turbo 1 boost 16-bit LE (0.125 kPa/bit)
            // buf[2-3] = turbo 2 boost 16-bit LE (0.125 kPa/bit)
            if (d[0] != 0xFF || d[1] != 0xFF) {
                uint16_t val = ((uint16_t)d[1] << 8) | d[0];
                data->cacInletPressurekPa = (float)val * 0.125f;
            }
            if (d[2] != 0xFF || d[3] != 0xFF) {
                uint16_t val = ((uint16_t)d[3] << 8) | d[2];
                data->transferPipePressurekPa = (float)val * 0.125f;
            }
            updated = true;
            break;

        case 65164:  // PGN_SUPPLY_PRESSURE - OSSM uses for humidity & engine bay
            // OSSM encoding:
            // buf[0] = engine bay temp + 40 (1°C/bit)
            // buf[6] = humidity / 0.4 (0.4%/bit)
            data->engineBayTemperatureC = decode_temp_byte(d[0]);
            data->humidity = decode_humidity(d[6]);
            updated = true;
            break;

        default:
            break;
    }

    if (updated) {
        data->lastUpdateMs = get_time_ms();
    }

    return updated;
}

int j1939_send_command(int sock, EOssmCommand cmd, const uint8_t* params, uint8_t param_len) {
    TCanFrame frame;

    frame.id = j1939_build_id(PGN_OSSM_COMMAND, 6, 0x00);  // Priority 6, source 0
    frame.extended = true;
    frame.len = 8;

    memset(frame.data, 0xFF, 8);
    frame.data[0] = (uint8_t)cmd;

    if (params && param_len > 0) {
        if (param_len > 7) param_len = 7;
        memcpy(&frame.data[1], params, param_len);
    }

    return socketcan_send(sock, &frame);
}

int j1939_check_response(int sock, uint8_t expected_cmd, uint8_t* response_data, uint8_t* response_len) {
    TCanFrame frame;
    int timeout_ms = 1000;
    int elapsed = 0;

    // Small delay to let OSSM process the command
    usleep(50000);  // 50ms

    while (elapsed < timeout_ms) {
        int result = socketcan_receive(sock, &frame);
        if (result > 0) {
            uint32_t pgn = j1939_get_pgn(frame.id);
            uint8_t source = j1939_get_source(frame.id);

            // Debug: uncomment to see what we're receiving
            // fprintf(stderr, "RX: ID=%08X PGN=%u SRC=%02X CMD=%02X\n",
            //         frame.id, pgn, source, frame.data[0]);

            if (pgn == PGN_OSSM_RESPONSE && source == OSSM_SOURCE_ADDRESS) {
                if (frame.data[0] == expected_cmd) {
                    uint8_t error = frame.data[1];
                    if (response_data && response_len) {
                        *response_len = 6;
                        memcpy(response_data, &frame.data[2], 6);
                    }
                    return error;
                }
            }
        }
        usleep(5000);  // 5ms
        elapsed += 5;
    }

    return -1;  // Timeout
}

int j1939_enable_spn(int sock, uint16_t spn, bool enable, uint8_t input) {
    // OSSM format: [cmd, spn_high, spn_low, enable, input]
    uint8_t params[4];
    params[0] = (spn >> 8) & 0xFF;  // spn_high
    params[1] = spn & 0xFF;          // spn_low
    params[2] = enable ? 1 : 0;      // enable
    params[3] = input;               // input

    #ifdef DEBUG
    fprintf(stderr, "TX enable_spn: SPN=%u enable=%d input=%d -> [%02X %02X %02X %02X]\n",
            spn, enable, input, params[0], params[1], params[2], params[3]);
    #endif

    if (j1939_send_command(sock, CMD_ENABLE_SPN, params, 4) < 0) {
        return -1;
    }

    return j1939_check_response(sock, CMD_ENABLE_SPN, NULL, NULL);
}

int j1939_set_ntc_preset(int sock, uint8_t input, ENtcPreset preset) {
    uint8_t params[2];
    params[0] = input;
    params[1] = (uint8_t)preset;

    if (j1939_send_command(sock, CMD_NTC_PRESET, params, 2) < 0) {
        return -1;
    }

    return j1939_check_response(sock, CMD_NTC_PRESET, NULL, NULL);
}

int j1939_set_pressure_preset(int sock, uint8_t input, EPressurePreset preset) {
    uint8_t params[2];
    params[0] = input;
    params[1] = (uint8_t)preset;

    if (j1939_send_command(sock, CMD_PRESSURE_PRESET, params, 2) < 0) {
        return -1;
    }

    return j1939_check_response(sock, CMD_PRESSURE_PRESET, NULL, NULL);
}

int j1939_set_tc_type(int sock, uint8_t type) {
    uint8_t params[1];
    params[0] = type;

    if (j1939_send_command(sock, CMD_SET_TC_TYPE, params, 1) < 0) {
        return -1;
    }

    return j1939_check_response(sock, CMD_SET_TC_TYPE, NULL, NULL);
}

int j1939_query_config(int sock, TConfigState* state) {
    uint8_t params[1] = {0};  // Query type 0 = SPN counts
    uint8_t response[6];
    uint8_t len;

    if (j1939_send_command(sock, CMD_QUERY, params, 1) < 0) {
        return -1;
    }

    int result = j1939_check_response(sock, CMD_QUERY, response, &len);
    if (result == 0 && state) {
        state->tempCount = response[0];
        state->pressureCount = response[1];
        state->egtEnabled = response[2] != 0;
        state->bme280Enabled = response[3] != 0;
    }

    return result;
}

int j1939_query_spn_assignments(int sock, TSpnAssignments* assignments) {
    uint8_t response[6];
    uint8_t len;
    int result;

    // Initialize to zero
    memset(assignments, 0, sizeof(TSpnAssignments));

    // Query temp SPNs (3 sub-queries for 8 inputs)
    for (uint8_t subQuery = 0; subQuery < 3; subQuery++) {
        uint8_t params[2] = {1, subQuery};  // Query type 1 = temp SPNs
        if (j1939_send_command(sock, CMD_QUERY, params, 2) < 0) {
            return -1;
        }
        result = j1939_check_response(sock, CMD_QUERY, response, &len);
        if (result != 0) return result;

        // Parse 3 SPNs from response (high byte, low byte pairs)
        for (uint8_t i = 0; i < 3; i++) {
            uint8_t idx = subQuery * 3 + i;
            if (idx < 8) {
                uint16_t spn = ((uint16_t)response[i * 2] << 8) | response[i * 2 + 1];
                if (spn != 0xFFFF) {
                    assignments->tempSpns[idx] = spn;
                }
            }
        }
    }

    // Query pressure SPNs (3 sub-queries for 7 inputs)
    for (uint8_t subQuery = 0; subQuery < 3; subQuery++) {
        uint8_t params[2] = {2, subQuery};  // Query type 2 = pressure SPNs
        if (j1939_send_command(sock, CMD_QUERY, params, 2) < 0) {
            return -1;
        }
        result = j1939_check_response(sock, CMD_QUERY, response, &len);
        if (result != 0) return result;

        // Parse 3 SPNs from response
        for (uint8_t i = 0; i < 3; i++) {
            uint8_t idx = subQuery * 3 + i;
            if (idx < 7) {
                uint16_t spn = ((uint16_t)response[i * 2] << 8) | response[i * 2 + 1];
                if (spn != 0xFFFF) {
                    assignments->presSpns[idx] = spn;
                }
            }
        }
    }

    return 0;
}

int j1939_save_config(int sock) {
    if (j1939_send_command(sock, CMD_SAVE, NULL, 0) < 0) {
        return -1;
    }

    return j1939_check_response(sock, CMD_SAVE, NULL, NULL);
}

int j1939_reset_config(int sock) {
    if (j1939_send_command(sock, CMD_RESET, NULL, 0) < 0) {
        return -1;
    }

    return j1939_check_response(sock, CMD_RESET, NULL, NULL);
}
