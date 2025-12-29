#ifndef OSSM_J1939_H
#define OSSM_J1939_H

#include "../types.h"
#include "../can/socketcan.h"

// Extract PGN from J1939 CAN ID
uint32_t j1939_get_pgn(uint32_t can_id);

// Extract source address from J1939 CAN ID
uint8_t j1939_get_source(uint32_t can_id);

// Build J1939 CAN ID
uint32_t j1939_build_id(uint32_t pgn, uint8_t priority, uint8_t source);

// Parse received J1939 message and update sensor data
// Returns true if data was updated
bool j1939_parse_message(const TCanFrame* frame, TSensorData* data);

// Send OSSM command
// Returns 0 on success, -1 on failure
int j1939_send_command(int sock, EOssmCommand cmd, const uint8_t* params, uint8_t param_len);

// Check for OSSM response
// Returns error code (0 = success), or -1 if no response/timeout
int j1939_check_response(int sock, uint8_t expected_cmd, uint8_t* response_data, uint8_t* response_len);

// SPN assignment structure
typedef struct {
    uint16_t tempSpns[8];     // SPN assigned to each temp input (0 = disabled)
    uint16_t presSpns[7];     // SPN assigned to each pressure input (0 = disabled)
} TSpnAssignments;

// High-level commands
int j1939_enable_spn(int sock, uint16_t spn, bool enable, uint8_t input);
int j1939_set_ntc_preset(int sock, uint8_t input, ENtcPreset preset);
int j1939_set_pressure_preset(int sock, uint8_t input, EPressurePreset preset);
int j1939_set_tc_type(int sock, uint8_t type);
int j1939_query_config(int sock, TConfigState* state);
int j1939_query_spn_assignments(int sock, TSpnAssignments* assignments);
int j1939_save_config(int sock);
int j1939_reset_config(int sock);

#endif // OSSM_J1939_H
