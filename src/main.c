#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <getopt.h>

#include "types.h"
#include "can/socketcan.h"
#include "protocol/j1939.h"
#include "ui/ui.h"

static volatile bool running = true;

static void signal_handler(int sig) {
    (void)sig;
    running = false;
}

static void print_usage(const char* prog) {
    printf("OSSM Config Tool - J1939 Sensor Module Configuration\n\n");
    printf("Usage: %s [options]\n\n", prog);
    printf("Options:\n");
    printf("  -i, --interface <name>  CAN interface (default: can0)\n");
    printf("  -h, --help              Show this help message\n");
    printf("\nExample:\n");
    printf("  %s -i can0\n", prog);
    printf("\nMake sure the CAN interface is up:\n");
    printf("  sudo ip link set can0 type can bitrate 250000\n");
    printf("  sudo ip link set can0 up\n");
}

int main(int argc, char* argv[]) {
    const char* interface = "can0";

    // Parse command line arguments
    static struct option long_options[] = {
        {"interface", required_argument, 0, 'i'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "i:h", long_options, NULL)) != -1) {
        switch (opt) {
            case 'i':
                interface = optarg;
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Initialize SocketCAN
    int sock = socketcan_init(interface);
    if (sock < 0) {
        fprintf(stderr, "Failed to initialize CAN interface '%s'\n", interface);
        fprintf(stderr, "Make sure the interface is up:\n");
        fprintf(stderr, "  sudo ip link set %s type can bitrate 250000\n", interface);
        fprintf(stderr, "  sudo ip link set %s up\n", interface);
        return 1;
    }

    if (socketcan_set_nonblocking(sock) < 0) {
        fprintf(stderr, "Failed to set non-blocking mode\n");
        socketcan_close(sock);
        return 1;
    }

    // Initialize UI
    TUiWindows windows;
    if (ui_init(&windows) < 0) {
        socketcan_close(sock);
        fprintf(stderr, "Terminal too small (need at least 80x30)\n");
        return 1;
    }

    // Initialize data structures
    TSensorData sensor_data;
    TConfigState config_state;
    memset(&sensor_data, 0, sizeof(sensor_data));
    memset(&config_state, 0, sizeof(config_state));

    // Set initial values to "not available"
    sensor_data.oilTemperatureC = -999.0f;
    sensor_data.coolantTemperatureC = -999.0f;
    sensor_data.fuelTemperatureC = -999.0f;
    sensor_data.boostTemperatureC = -999.0f;
    sensor_data.cacInletTemperatureC = -999.0f;
    sensor_data.transferPipeTemperatureC = -999.0f;
    sensor_data.airInletTemperatureC = -999.0f;
    sensor_data.engineBayTemperatureC = -999.0f;
    sensor_data.ambientTemperatureC = -999.0f;
    sensor_data.egtTemperatureC = -999.0f;
    sensor_data.oilPressurekPa = -999.0f;
    sensor_data.coolantPressurekPa = -999.0f;
    sensor_data.fuelPressurekPa = -999.0f;
    sensor_data.boostPressurekPa = -999.0f;
    sensor_data.airInletPressurekPa = -999.0f;
    sensor_data.cacInletPressurekPa = -999.0f;
    sensor_data.transferPipePressurekPa = -999.0f;
    sensor_data.absoluteBarometricPressurekPa = -999.0f;
    sensor_data.humidity = -999.0f;

    // Draw static UI elements
    ui_draw_static(&windows);
    ui_draw_menu(&windows);

    int message_count = 0;
    bool connected = false;

    // Main loop
    while (running) {
        // Process incoming CAN messages
        TCanFrame frame;
        int result = socketcan_receive(sock, &frame);

        if (result > 0) {
            if (j1939_parse_message(&frame, &sensor_data)) {
                message_count++;
                connected = true;
            }
        } else if (result < 0) {
            connected = false;
        }

        // Update displays
        ui_update_sensors(&windows, &sensor_data, &config_state);
        ui_update_status(&windows, interface, connected, message_count);

        // Handle keyboard input
        int ch = ui_get_input();
        if (ch != ERR) {
            switch (ch) {
                case KEY_F(1):  // Help
                    ui_dialog_message("Help",
                        "F2=Enable/Disable SPN\n"
                        "F3=NTC Preset  F4=Pressure Preset\n"
                        "F5=TC Type  F6=Query  F7=Save  F8=Reset",
                        false);
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;

                case KEY_F(2): {  // Enable SPN
                    int spn, input;
                    bool enable;
                    if (ui_dialog_enable_spn(&spn, &input, &enable)) {
                        int err = j1939_enable_spn(sock, (uint16_t)spn, enable, (uint8_t)input);
                        if (err == 0) {
                            ui_dialog_message("Success",
                                enable ? "SPN enabled" : "SPN disabled", false);
                        } else if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(3): {  // NTC Preset
                    int input, preset;
                    if (ui_dialog_ntc_preset(&input, &preset)) {
                        int err = j1939_set_ntc_preset(sock, (uint8_t)input, (ENtcPreset)preset);
                        if (err == 0) {
                            ui_dialog_message("Success", "NTC preset applied", false);
                        } else if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(4): {  // Pressure Preset
                    int input, preset;
                    if (ui_dialog_pressure_preset(&input, &preset)) {
                        int err = j1939_set_pressure_preset(sock, (uint8_t)input, (EPressurePreset)preset);
                        if (err == 0) {
                            ui_dialog_message("Success", "Pressure preset applied", false);
                        } else if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(5): {  // TC Type
                    int type;
                    if (ui_dialog_tc_type(&type)) {
                        int err = j1939_set_tc_type(sock, (uint8_t)type);
                        if (err == 0) {
                            ui_dialog_message("Success", "TC type set", false);
                        } else if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(6): {  // Query
                    // First get counts and status
                    int err = j1939_query_config(sock, &config_state);
                    if (err != 0) {
                        if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    } else {
                        // Get SPN assignments
                        TSpnAssignments assignments;
                        err = j1939_query_spn_assignments(sock, &assignments);
                        if (err == 0) {
                            ui_dialog_spn_list(assignments.tempSpns, assignments.presSpns,
                                               config_state.egtEnabled, config_state.bme280Enabled);
                        } else {
                            // Fall back to basic display
                            char msg[128];
                            snprintf(msg, sizeof(msg),
                                "Temp inputs: %d\nPressure inputs: %d\n"
                                "EGT: %s\nBME280: %s\n\n(SPN details unavailable)",
                                config_state.tempCount,
                                config_state.pressureCount,
                                config_state.egtEnabled ? "Enabled" : "Disabled",
                                config_state.bme280Enabled ? "Enabled" : "Disabled");
                            ui_dialog_message("Configuration", msg, false);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(7): {  // Save
                    if (ui_dialog_confirm("Save", "Save configuration to EEPROM?")) {
                        int err = j1939_save_config(sock);
                        if (err == 0) {
                            ui_dialog_message("Success", "Configuration saved", false);
                        } else if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(8): {  // Reset
                    if (ui_dialog_confirm("Reset", "Reset to factory defaults?")) {
                        int err = j1939_reset_config(sock);
                        if (err == 0) {
                            ui_dialog_message("Success", "Configuration reset", false);
                        } else if (err > 0) {
                            char msg[64];
                            snprintf(msg, sizeof(msg), "Error code: %d", err);
                            ui_dialog_message("Error", msg, true);
                        } else {
                            ui_dialog_message("Error", "No response from OSSM", true);
                        }
                    }
                    ui_draw_static(&windows);
                    ui_draw_menu(&windows);
                    break;
                }

                case KEY_F(10):  // Quit
                case 'q':
                case 'Q':
                    running = false;
                    break;
            }
        }
    }

    // Cleanup
    ui_cleanup(&windows);
    socketcan_close(sock);

    printf("OSSM Config Tool exited.\n");
    return 0;
}
