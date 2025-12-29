#ifndef OSSM_UI_H
#define OSSM_UI_H

#include <ncurses.h>
#include "../types.h"

// Color pairs
#define COLOR_TITLE     1
#define COLOR_BORDER    2
#define COLOR_DATA      3
#define COLOR_LABEL     4
#define COLOR_STATUS    5
#define COLOR_ERROR     6
#define COLOR_SUCCESS   7
#define COLOR_STALE     8
#define COLOR_MENU      9
#define COLOR_HIGHLIGHT 10

// Window handles
typedef struct {
    WINDOW* main;
    WINDOW* temp_panel;
    WINDOW* pressure_panel;
    WINDOW* egt_panel;
    WINDOW* ambient_panel;
    WINDOW* status_bar;
    WINDOW* menu_bar;
} TUiWindows;

// Initialize ncurses and create windows
int ui_init(TUiWindows* windows);

// Cleanup ncurses
void ui_cleanup(TUiWindows* windows);

// Draw static elements (borders, labels)
void ui_draw_static(TUiWindows* windows);

// Update sensor displays with current data
void ui_update_sensors(TUiWindows* windows, const TSensorData* data, const TConfigState* config);

// Update status bar
void ui_update_status(TUiWindows* windows, const char* interface, bool connected, int message_count);

// Draw function key menu
void ui_draw_menu(TUiWindows* windows);

// Dialog functions
int ui_dialog_enable_spn(int* spn, int* input, bool* enable);
int ui_dialog_ntc_preset(int* input, int* preset);
int ui_dialog_pressure_preset(int* input, int* preset);
int ui_dialog_tc_type(int* type);
int ui_dialog_confirm(const char* title, const char* message);
void ui_dialog_message(const char* title, const char* message, bool is_error);
void ui_dialog_spn_list(const uint16_t* tempSpns, const uint16_t* presSpns,
                         bool egtEnabled, bool bme280Enabled);

// Get human-readable name for SPN
const char* ui_get_spn_name(uint16_t spn);

// Input handling
int ui_get_input(void);

#endif // OSSM_UI_H
