#ifndef OSSM_TYPES_H
#define OSSM_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// J1939 Source Address for OSSM
#define OSSM_SOURCE_ADDRESS 0x95  // 149

// Command PGNs
#define PGN_OSSM_COMMAND   0xFF00  // 65280 - Commands TO OSSM
#define PGN_OSSM_RESPONSE  0xFF01  // 65281 - Responses FROM OSSM

// Data PGNs we receive
#define PGN_AMBIENT_CONDITIONS  0xFEF5  // 65269
#define PGN_INLET_EXHAUST       0xFEF6  // 65270
#define PGN_ENGINE_TEMP         0xFEEE  // 65262
#define PGN_ENGINE_FLUID_PRESS  0xFEEF  // 65263
#define PGN_ENGINE_TEMP_2       0xFE69  // 65129
#define PGN_ENGINE_TEMP_3       0xFE95  // 65189
#define PGN_TURBO_PRESS         0xFE96  // 65190

// Command codes
typedef enum {
    CMD_ENABLE_SPN = 0x01,
    CMD_SET_NTC_PARAM = 0x02,
    CMD_SET_PRESSURE_RANGE = 0x03,
    CMD_SET_TC_TYPE = 0x04,
    CMD_QUERY = 0x05,
    CMD_SAVE = 0x06,
    CMD_RESET = 0x07,
    CMD_NTC_PRESET = 0x08,
    CMD_PRESSURE_PRESET = 0x09
} EOssmCommand;

// Error codes (must match OSSM firmware CommandHandler.h ECommandError)
typedef enum {
    ERR_OK = 0x00,
    ERR_UNKNOWN_CMD = 0x01,
    ERR_PARSE_FAILED = 0x02,
    ERR_UNKNOWN_SPN = 0x03,
    ERR_INVALID_TEMP_INPUT = 0x04,
    ERR_INVALID_PRESSURE_INPUT = 0x05,
    ERR_INVALID_NTC_PARAM = 0x06,
    ERR_INVALID_TC_TYPE = 0x07,
    ERR_INVALID_QUERY_TYPE = 0x08,
    ERR_SAVE_FAILED = 0x09,
    ERR_INVALID_PRESET = 0x0A
} EOssmError;

// SPN Categories
typedef enum {
    SPN_CAT_TEMPERATURE,
    SPN_CAT_PRESSURE,
    SPN_CAT_EGT,
    SPN_CAT_BME280,
    SPN_CAT_UNKNOWN
} ESpnCategory;

// Known SPNs
typedef struct {
    uint16_t spn;
    const char* name;
    const char* unit;
    ESpnCategory category;
} TSpnInfo;

// Sensor data structure
typedef struct {
    // Temperatures (Celsius)
    float oilTemperatureC;
    float coolantTemperatureC;
    float fuelTemperatureC;
    float boostTemperatureC;
    float cacInletTemperatureC;
    float transferPipeTemperatureC;
    float airInletTemperatureC;
    float engineBayTemperatureC;
    float ambientTemperatureC;
    float egtTemperatureC;

    // Pressures (kPa)
    float oilPressurekPa;
    float coolantPressurekPa;
    float fuelPressurekPa;
    float boostPressurekPa;
    float airInletPressurekPa;
    float cacInletPressurekPa;
    float transferPipePressurekPa;
    float absoluteBarometricPressurekPa;

    // Other
    float humidity;

    // Timestamps for freshness
    uint32_t lastUpdateMs;
} TSensorData;

// Configuration state
typedef struct {
    uint8_t tempCount;
    uint8_t pressureCount;
    bool egtEnabled;
    bool bme280Enabled;
    uint8_t sourceAddress;
    uint8_t thermocoupleType;
} TConfigState;

// NTC Presets
typedef enum {
    NTC_PRESET_AEM = 0,
    NTC_PRESET_BOSCH = 1,
    NTC_PRESET_GM = 2
} ENtcPreset;

// Pressure Presets (Bar = PSIA, PSI = PSIG)
typedef enum {
    // Bar presets (0-15) - PSIA absolute
    PRES_PRESET_1BAR = 0,
    PRES_PRESET_1_5BAR = 1,
    PRES_PRESET_2BAR = 2,
    PRES_PRESET_2_5BAR = 3,
    PRES_PRESET_3BAR = 4,
    PRES_PRESET_4BAR = 5,
    PRES_PRESET_5BAR = 6,
    PRES_PRESET_7BAR = 7,
    PRES_PRESET_10BAR = 8,
    PRES_PRESET_50BAR = 9,
    PRES_PRESET_100BAR = 10,
    PRES_PRESET_150BAR = 11,
    PRES_PRESET_200BAR = 12,
    PRES_PRESET_1000BAR = 13,
    PRES_PRESET_2000BAR = 14,
    PRES_PRESET_3000BAR = 15,

    // PSI presets (20-30) - PSIG gauge
    PRES_PRESET_15PSI = 20,
    PRES_PRESET_30PSI = 21,
    PRES_PRESET_50PSI = 22,
    PRES_PRESET_100PSI = 23,
    PRES_PRESET_150PSI = 24,
    PRES_PRESET_200PSI = 25,
    PRES_PRESET_250PSI = 26,
    PRES_PRESET_300PSI = 27,
    PRES_PRESET_350PSI = 28,
    PRES_PRESET_400PSI = 29,
    PRES_PRESET_500PSI = 30
} EPressurePreset;

// Known SPN database
static const TSpnInfo KNOWN_SPNS[] = {
    // Temperature SPNs
    {175, "Engine Oil Temp", "C", SPN_CAT_TEMPERATURE},
    {110, "Coolant Temp", "C", SPN_CAT_TEMPERATURE},
    {174, "Fuel Temp", "C", SPN_CAT_TEMPERATURE},
    {105, "Boost Temp", "C", SPN_CAT_TEMPERATURE},
    {1131, "CAC Inlet Temp", "C", SPN_CAT_TEMPERATURE},
    {1132, "Transfer Pipe Temp", "C", SPN_CAT_TEMPERATURE},
    {1133, "Air Inlet Temp", "C", SPN_CAT_TEMPERATURE},
    {172, "Air Inlet Temp 2", "C", SPN_CAT_TEMPERATURE},
    {441, "Engine Bay Temp", "C", SPN_CAT_TEMPERATURE},

    // Pressure SPNs
    {100, "Engine Oil Pres", "kPa", SPN_CAT_PRESSURE},
    {109, "Coolant Pres", "kPa", SPN_CAT_PRESSURE},
    {94, "Fuel Delivery Pres", "kPa", SPN_CAT_PRESSURE},
    {102, "Boost Pres", "kPa", SPN_CAT_PRESSURE},
    {106, "Air Inlet Pres", "kPa", SPN_CAT_PRESSURE},
    {1127, "CAC Inlet Pres", "kPa", SPN_CAT_PRESSURE},
    {1128, "Transfer Pipe Pres", "kPa", SPN_CAT_PRESSURE},

    // EGT
    {173, "EGT", "C", SPN_CAT_EGT},

    // BME280
    {171, "Ambient Temp", "C", SPN_CAT_BME280},
    {108, "Barometric Pres", "kPa", SPN_CAT_BME280},
    {354, "Humidity", "%", SPN_CAT_BME280},

    {0, NULL, NULL, SPN_CAT_UNKNOWN}  // Terminator
};

#define KNOWN_SPN_COUNT (sizeof(KNOWN_SPNS) / sizeof(KNOWN_SPNS[0]) - 1)

#endif // OSSM_TYPES_H
