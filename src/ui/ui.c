#include "ui.h"
#include <string.h>
#include <stdlib.h>
#include <time.h>

// Get human-readable name for SPN
const char* ui_get_spn_name(uint16_t spn) {
    switch (spn) {
        case 175:  return "Oil Temp";
        case 110:  return "Coolant Temp";
        case 174:  return "Fuel Temp";
        case 105:  return "Boost Temp";
        case 1131: return "CAC Inlet Temp";
        case 1132: return "Xfer Pipe Temp";
        case 1133: return "Air Inlet Temp 4";
        case 172:  return "Air Inlet Temp";
        case 441:  return "Eng Bay Temp";
        case 100:  return "Oil Pres";
        case 109:  return "Coolant Pres";
        case 94:   return "Fuel Pres";
        case 102:  return "Boost Pres";
        case 106:  return "Air Inlet Pres";
        case 1127: return "CAC Inlet Pres";
        case 1128: return "Xfer Pipe Pres";
        case 173:  return "EGT";
        case 171:  return "Ambient Temp";
        case 108:  return "Baro Pres";
        case 354:  return "Humidity";
        default:   return "Unknown";
    }
}

// Panel dimensions
#define TEMP_PANEL_H    14
#define TEMP_PANEL_W    35
#define PRES_PANEL_H    11
#define PRES_PANEL_W    35
#define EGT_PANEL_H     5
#define EGT_PANEL_W     35
#define AMBIENT_PANEL_H 7
#define AMBIENT_PANEL_W 35

static uint32_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

int ui_init(TUiWindows* windows) {
    initscr();
    start_color();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);
    timeout(100);  // Non-blocking input with 100ms timeout

    // Initialize color pairs
    init_pair(COLOR_TITLE, COLOR_CYAN, COLOR_BLACK);
    init_pair(COLOR_BORDER, COLOR_BLUE, COLOR_BLACK);
    init_pair(COLOR_DATA, COLOR_GREEN, COLOR_BLACK);
    init_pair(COLOR_LABEL, COLOR_WHITE, COLOR_BLACK);
    init_pair(COLOR_STATUS, COLOR_BLACK, COLOR_CYAN);
    init_pair(COLOR_ERROR, COLOR_RED, COLOR_BLACK);
    init_pair(COLOR_SUCCESS, COLOR_GREEN, COLOR_BLACK);
    init_pair(COLOR_STALE, COLOR_YELLOW, COLOR_BLACK);
    init_pair(COLOR_MENU, COLOR_BLACK, COLOR_WHITE);
    init_pair(COLOR_HIGHLIGHT, COLOR_BLACK, COLOR_CYAN);

    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);

    // Check minimum size
    if (max_y < 30 || max_x < 80) {
        endwin();
        return -1;
    }

    windows->main = stdscr;

    // Create panels - left column
    int col1_x = 2;
    int col2_x = col1_x + TEMP_PANEL_W + 2;

    windows->temp_panel = newwin(TEMP_PANEL_H, TEMP_PANEL_W, 2, col1_x);
    windows->pressure_panel = newwin(PRES_PANEL_H, PRES_PANEL_W, 2, col2_x);
    windows->egt_panel = newwin(EGT_PANEL_H, EGT_PANEL_W, TEMP_PANEL_H + 3, col1_x);
    windows->ambient_panel = newwin(AMBIENT_PANEL_H, AMBIENT_PANEL_W, PRES_PANEL_H + 3, col2_x);

    // Status and menu bars
    windows->status_bar = newwin(1, max_x, max_y - 2, 0);
    windows->menu_bar = newwin(1, max_x, max_y - 1, 0);

    return 0;
}

void ui_cleanup(TUiWindows* windows) {
    if (windows->temp_panel) delwin(windows->temp_panel);
    if (windows->pressure_panel) delwin(windows->pressure_panel);
    if (windows->egt_panel) delwin(windows->egt_panel);
    if (windows->ambient_panel) delwin(windows->ambient_panel);
    if (windows->status_bar) delwin(windows->status_bar);
    if (windows->menu_bar) delwin(windows->menu_bar);
    endwin();
}

static void draw_box_with_title(WINDOW* win, const char* title) {
    wattron(win, COLOR_PAIR(COLOR_BORDER));
    box(win, 0, 0);
    wattroff(win, COLOR_PAIR(COLOR_BORDER));

    wattron(win, COLOR_PAIR(COLOR_TITLE) | A_BOLD);
    mvwprintw(win, 0, 2, " %s ", title);
    wattroff(win, COLOR_PAIR(COLOR_TITLE) | A_BOLD);
}

void ui_draw_static(TUiWindows* windows) {
    // Main title
    attron(COLOR_PAIR(COLOR_TITLE) | A_BOLD);
    mvprintw(0, 2, "OSSM Config Tool v1.0");
    attroff(COLOR_PAIR(COLOR_TITLE) | A_BOLD);

    // Draw panel borders with titles
    draw_box_with_title(windows->temp_panel, "TEMPERATURES");
    draw_box_with_title(windows->pressure_panel, "PRESSURES");
    draw_box_with_title(windows->egt_panel, "EGT");
    draw_box_with_title(windows->ambient_panel, "AMBIENT");

    // Temperature labels - format: "Name(SPN XXX)"
    wattron(windows->temp_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->temp_panel, 2, 2, "Oil Temp(SPN 175)");
    mvwprintw(windows->temp_panel, 3, 2, "Coolant(SPN 110)");
    mvwprintw(windows->temp_panel, 4, 2, "Fuel Temp(SPN 174)");
    mvwprintw(windows->temp_panel, 5, 2, "Boost Temp(SPN 105)");
    mvwprintw(windows->temp_panel, 6, 2, "CAC Inlet(SPN 1131)");
    mvwprintw(windows->temp_panel, 7, 2, "Xfer Pipe(SPN 1132)");
    mvwprintw(windows->temp_panel, 8, 2, "Air Inlet(SPN 172)");
    mvwprintw(windows->temp_panel, 9, 2, "Eng Bay(SPN 441)");
    wattroff(windows->temp_panel, COLOR_PAIR(COLOR_LABEL));

    // Pressure labels - format: "Name(SPN XXX)"
    wattron(windows->pressure_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->pressure_panel, 2, 2, "Oil Pres(SPN 100)");
    mvwprintw(windows->pressure_panel, 3, 2, "Coolant(SPN 109)");
    mvwprintw(windows->pressure_panel, 4, 2, "Fuel Pres(SPN 94)");
    mvwprintw(windows->pressure_panel, 5, 2, "Boost Pres(SPN 102)");
    mvwprintw(windows->pressure_panel, 6, 2, "Air Inlet(SPN 106)");
    mvwprintw(windows->pressure_panel, 7, 2, "CAC Inlet(SPN 1127)");
    mvwprintw(windows->pressure_panel, 8, 2, "Xfer Pipe(SPN 1128)");
    wattroff(windows->pressure_panel, COLOR_PAIR(COLOR_LABEL));

    // EGT label - format: "Name(SPN XXX)"
    wattron(windows->egt_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->egt_panel, 2, 2, "EGT(SPN 173)");
    wattroff(windows->egt_panel, COLOR_PAIR(COLOR_LABEL));

    // Ambient labels - format: "Name(SPN XXX)"
    wattron(windows->ambient_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->ambient_panel, 2, 2, "Ambient(SPN 171)");
    mvwprintw(windows->ambient_panel, 3, 2, "Baro Pres(SPN 108)");
    mvwprintw(windows->ambient_panel, 4, 2, "Humidity(SPN 354)");
    wattroff(windows->ambient_panel, COLOR_PAIR(COLOR_LABEL));

    wrefresh(windows->temp_panel);
    wrefresh(windows->pressure_panel);
    wrefresh(windows->egt_panel);
    wrefresh(windows->ambient_panel);
    refresh();
}

static void print_value(WINDOW* win, int y, int x, float value, const char* unit, bool is_stale) {
    int color = is_stale ? COLOR_STALE : COLOR_DATA;

    // Clear previous value
    mvwprintw(win, y, x, "          ");

    if (value < -900.0f) {
        wattron(win, COLOR_PAIR(COLOR_ERROR));
        mvwprintw(win, y, x, "N/A");
        wattroff(win, COLOR_PAIR(COLOR_ERROR));
    } else {
        wattron(win, COLOR_PAIR(color));
        mvwprintw(win, y, x, "%7.1f %s", value, unit);
        wattroff(win, COLOR_PAIR(color));
    }
}

void ui_update_sensors(TUiWindows* windows, const TSensorData* data, const TConfigState* config) {
    (void)config;  // May use later for showing enabled/disabled state

    uint32_t now = get_time_ms();
    bool stale = (now - data->lastUpdateMs) > 2000;  // 2 second timeout

    // Redraw borders and labels (ncurses needs this for proper refresh)
    draw_box_with_title(windows->temp_panel, "TEMPERATURES");
    draw_box_with_title(windows->pressure_panel, "PRESSURES");
    draw_box_with_title(windows->egt_panel, "EGT");
    draw_box_with_title(windows->ambient_panel, "AMBIENT");

    // Temperature labels - format: "Name(SPN XXX)"
    wattron(windows->temp_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->temp_panel, 2, 2, "Oil Temp(SPN 175)");
    mvwprintw(windows->temp_panel, 3, 2, "Coolant(SPN 110)");
    mvwprintw(windows->temp_panel, 4, 2, "Fuel Temp(SPN 174)");
    mvwprintw(windows->temp_panel, 5, 2, "Boost Temp(SPN 105)");
    mvwprintw(windows->temp_panel, 6, 2, "CAC Inlet(SPN 1131)");
    mvwprintw(windows->temp_panel, 7, 2, "Xfer Pipe(SPN 1132)");
    mvwprintw(windows->temp_panel, 8, 2, "Air Inlet(SPN 172)");
    mvwprintw(windows->temp_panel, 9, 2, "Eng Bay(SPN 441)");
    wattroff(windows->temp_panel, COLOR_PAIR(COLOR_LABEL));

    // Pressure labels - format: "Name(SPN XXX)"
    wattron(windows->pressure_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->pressure_panel, 2, 2, "Oil Pres(SPN 100)");
    mvwprintw(windows->pressure_panel, 3, 2, "Coolant(SPN 109)");
    mvwprintw(windows->pressure_panel, 4, 2, "Fuel Pres(SPN 94)");
    mvwprintw(windows->pressure_panel, 5, 2, "Boost Pres(SPN 102)");
    mvwprintw(windows->pressure_panel, 6, 2, "Air Inlet(SPN 106)");
    mvwprintw(windows->pressure_panel, 7, 2, "CAC Inlet(SPN 1127)");
    mvwprintw(windows->pressure_panel, 8, 2, "Xfer Pipe(SPN 1128)");
    wattroff(windows->pressure_panel, COLOR_PAIR(COLOR_LABEL));

    // EGT label - format: "Name(SPN XXX)"
    wattron(windows->egt_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->egt_panel, 2, 2, "EGT(SPN 173)");
    wattroff(windows->egt_panel, COLOR_PAIR(COLOR_LABEL));

    // Ambient labels - format: "Name(SPN XXX)"
    wattron(windows->ambient_panel, COLOR_PAIR(COLOR_LABEL));
    mvwprintw(windows->ambient_panel, 2, 2, "Ambient(SPN 171)");
    mvwprintw(windows->ambient_panel, 3, 2, "Baro Pres(SPN 108)");
    mvwprintw(windows->ambient_panel, 4, 2, "Humidity(SPN 354)");
    wattroff(windows->ambient_panel, COLOR_PAIR(COLOR_LABEL));

    // Temperatures
    print_value(windows->temp_panel, 2, 20, data->oilTemperatureC, "C", stale);
    print_value(windows->temp_panel, 3, 20, data->coolantTemperatureC, "C", stale);
    print_value(windows->temp_panel, 4, 20, data->fuelTemperatureC, "C", stale);
    print_value(windows->temp_panel, 5, 20, data->boostTemperatureC, "C", stale);
    print_value(windows->temp_panel, 6, 20, data->cacInletTemperatureC, "C", stale);
    print_value(windows->temp_panel, 7, 20, data->transferPipeTemperatureC, "C", stale);
    print_value(windows->temp_panel, 8, 20, data->airInletTemperatureC, "C", stale);
    print_value(windows->temp_panel, 9, 20, data->engineBayTemperatureC, "C", stale);

    // Pressures
    print_value(windows->pressure_panel, 2, 20, data->oilPressurekPa, "kPa", stale);
    print_value(windows->pressure_panel, 3, 20, data->coolantPressurekPa, "kPa", stale);
    print_value(windows->pressure_panel, 4, 20, data->fuelPressurekPa, "kPa", stale);
    print_value(windows->pressure_panel, 5, 20, data->boostPressurekPa, "kPa", stale);
    print_value(windows->pressure_panel, 6, 20, data->airInletPressurekPa, "kPa", stale);
    print_value(windows->pressure_panel, 7, 20, data->cacInletPressurekPa, "kPa", stale);
    print_value(windows->pressure_panel, 8, 20, data->transferPipePressurekPa, "kPa", stale);

    // EGT
    print_value(windows->egt_panel, 2, 20, data->egtTemperatureC, "C", stale);

    // Ambient
    print_value(windows->ambient_panel, 2, 20, data->ambientTemperatureC, "C", stale);
    print_value(windows->ambient_panel, 3, 20, data->absoluteBarometricPressurekPa, "kPa", stale);
    print_value(windows->ambient_panel, 4, 20, data->humidity, "%", stale);

    // Main title
    attron(COLOR_PAIR(COLOR_TITLE) | A_BOLD);
    mvprintw(0, 2, "OSSM Config Tool v1.0");
    attroff(COLOR_PAIR(COLOR_TITLE) | A_BOLD);
    refresh();

    wrefresh(windows->temp_panel);
    wrefresh(windows->pressure_panel);
    wrefresh(windows->egt_panel);
    wrefresh(windows->ambient_panel);
}

void ui_update_status(TUiWindows* windows, const char* interface, bool connected, int message_count) {
    werase(windows->status_bar);
    wbkgd(windows->status_bar, COLOR_PAIR(COLOR_STATUS));

    if (connected) {
        wattron(windows->status_bar, A_BOLD);
        mvwprintw(windows->status_bar, 0, 2, "CAN: %s", interface);
        wattroff(windows->status_bar, A_BOLD);
        mvwprintw(windows->status_bar, 0, 20, "Status: CONNECTED");
        mvwprintw(windows->status_bar, 0, 45, "Messages: %d", message_count);
    } else {
        mvwprintw(windows->status_bar, 0, 2, "CAN: %s - DISCONNECTED", interface);
    }

    wrefresh(windows->status_bar);
}

void ui_draw_menu(TUiWindows* windows) {
    werase(windows->menu_bar);
    wbkgd(windows->menu_bar, COLOR_PAIR(COLOR_MENU));

    mvwprintw(windows->menu_bar, 0, 1, "F1");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Help ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F2");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Enable ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F3");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "NTC ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F4");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Pres ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F5");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "TC ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F6");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Query ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F7");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Save ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F8");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Reset ");
    wattroff(windows->menu_bar, A_BOLD);

    wprintw(windows->menu_bar, "F10");
    wattron(windows->menu_bar, A_BOLD);
    wprintw(windows->menu_bar, "Quit");
    wattroff(windows->menu_bar, A_BOLD);

    wrefresh(windows->menu_bar);
}

int ui_get_input(void) {
    return getch();
}

// Dialog helper - create centered window
static WINDOW* create_dialog(int height, int width, const char* title) {
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);

    int start_y = (max_y - height) / 2;
    int start_x = (max_x - width) / 2;

    WINDOW* win = newwin(height, width, start_y, start_x);
    draw_box_with_title(win, title);

    return win;
}

void ui_dialog_message(const char* title, const char* message, bool is_error) {
    WINDOW* dialog = create_dialog(7, 50, title);

    int color = is_error ? COLOR_ERROR : COLOR_SUCCESS;
    wattron(dialog, COLOR_PAIR(color));
    mvwprintw(dialog, 3, 3, "%s", message);
    wattroff(dialog, COLOR_PAIR(color));

    mvwprintw(dialog, 5, 18, "[ OK ]");

    wrefresh(dialog);

    // Wait for any key
    nodelay(stdscr, FALSE);
    getch();
    nodelay(stdscr, TRUE);

    delwin(dialog);
    touchwin(stdscr);
    refresh();
}

int ui_dialog_confirm(const char* title, const char* message) {
    WINDOW* dialog = create_dialog(7, 50, title);

    mvwprintw(dialog, 3, 3, "%s", message);

    int selected = 0;  // 0 = Yes, 1 = No

    while (1) {
        if (selected == 0) {
            wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 5, 14, "[ YES ]");
            wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 5, 26, "[ NO ]");
        } else {
            mvwprintw(dialog, 5, 14, "[ YES ]");
            wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 5, 26, "[ NO ]");
            wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
        }

        wrefresh(dialog);

        int ch = getch();
        if (ch == KEY_LEFT || ch == KEY_RIGHT || ch == '\t') {
            selected = 1 - selected;
        } else if (ch == '\n' || ch == ' ') {
            delwin(dialog);
            touchwin(stdscr);
            refresh();
            return selected == 0 ? 1 : 0;
        } else if (ch == 27) {  // ESC
            delwin(dialog);
            touchwin(stdscr);
            refresh();
            return 0;
        }
    }
}

int ui_dialog_enable_spn(int* spn, int* input, bool* enable) {
    WINDOW* dialog = create_dialog(16, 55, "Enable/Disable SPN");

    // SPN list (simplified - show categories)
    const char* temp_spns[] = {"175-Oil", "110-Coolant", "174-Fuel", "105-Boost",
                               "1131-CAC", "1132-TransPipe", "172-AirInlet", "441-EngBay"};
    const char* pres_spns[] = {"100-Oil", "109-Coolant", "94-Fuel", "102-Boost",
                               "106-AirInlet", "1127-CAC", "1128-TransPipe"};

    int selection = 0;
    int category = 0;  // 0=temp, 1=pres, 2=egt, 3=bme
    *input = 1;
    *enable = true;

    while (1) {
        // Draw categories
        mvwprintw(dialog, 2, 3, "Category: ");
        const char* cats[] = {"Temperature", "Pressure", "EGT", "BME280"};
        for (int i = 0; i < 4; i++) {
            if (i == category) {
                wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
            mvwprintw(dialog, 2, 14 + i * 12, "[%s]", cats[i]);
            if (i == category) {
                wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
        }

        // Draw SPNs based on category
        mvwprintw(dialog, 4, 3, "SPN: ");
        werase(dialog);
        draw_box_with_title(dialog, "Enable/Disable SPN");
        mvwprintw(dialog, 2, 3, "Category: ");
        for (int i = 0; i < 4; i++) {
            if (i == category) wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 2, 14 + i * 12, "[%s]", cats[i]);
            if (i == category) wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
        }

        if (category == 0) {  // Temperature
            mvwprintw(dialog, 4, 3, "SPN (select with UP/DOWN):");
            for (int i = 0; i < 8; i++) {
                if (i == selection) wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
                mvwprintw(dialog, 5 + i, 5, "%s", temp_spns[i]);
                if (i == selection) wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
            mvwprintw(dialog, 13, 3, "Input (1-8): %d", *input);
        } else if (category == 1) {  // Pressure
            mvwprintw(dialog, 4, 3, "SPN (select with UP/DOWN):");
            for (int i = 0; i < 7; i++) {
                if (i == selection) wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
                mvwprintw(dialog, 5 + i, 5, "%s", pres_spns[i]);
                if (i == selection) wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
            mvwprintw(dialog, 12, 3, "Input (1-4): %d", *input);
        } else if (category == 2) {  // EGT
            mvwprintw(dialog, 5, 5, "SPN 173 - Exhaust Gas Temperature");
        } else {  // BME280
            mvwprintw(dialog, 5, 5, "SPN 171 - Ambient Temp");
            mvwprintw(dialog, 6, 5, "SPN 108 - Barometric Pressure");
            mvwprintw(dialog, 7, 5, "SPN 354 - Humidity");
        }

        // Enable/Disable toggle
        mvwprintw(dialog, 14, 3, "Action: ");
        if (*enable) {
            wattron(dialog, COLOR_PAIR(COLOR_SUCCESS));
            mvwprintw(dialog, 14, 11, "[ENABLE]");
            wattroff(dialog, COLOR_PAIR(COLOR_SUCCESS));
            mvwprintw(dialog, 14, 21, " DISABLE ");
        } else {
            mvwprintw(dialog, 14, 11, " ENABLE ");
            wattron(dialog, COLOR_PAIR(COLOR_ERROR));
            mvwprintw(dialog, 14, 21, "[DISABLE]");
            wattroff(dialog, COLOR_PAIR(COLOR_ERROR));
        }

        // Help text
        wattron(dialog, A_DIM);
        mvwprintw(dialog, 15, 3, "+/- Input  E/D Action  Enter=OK  ESC=Cancel");
        wattroff(dialog, A_DIM);

        wrefresh(dialog);

        int ch = getch();
        switch (ch) {
            case KEY_LEFT:
                if (category > 0) { category--; selection = 0; }
                break;
            case KEY_RIGHT:
                if (category < 3) { category++; selection = 0; }
                break;
            case KEY_UP:
                if (selection > 0) selection--;
                break;
            case KEY_DOWN:
                if (category == 0 && selection < 7) selection++;
                else if (category == 1 && selection < 6) selection++;
                break;
            case '+':
            case '=':
                if (category == 0 && *input < 8) (*input)++;
                else if (category == 1 && *input < 4) (*input)++;
                break;
            case '-':
                if (*input > 1) (*input)--;
                break;
            case 'e':
            case 'E':
                *enable = true;
                break;
            case 'd':
            case 'D':
                *enable = false;
                break;
            case '\n':
            case ' ':
                // Set SPN based on selection
                if (category == 0) {
                    int temp_spn_vals[] = {175, 110, 174, 105, 1131, 1132, 172, 441};
                    *spn = temp_spn_vals[selection];
                } else if (category == 1) {
                    int pres_spn_vals[] = {100, 109, 94, 102, 106, 1127, 1128};
                    *spn = pres_spn_vals[selection];
                } else if (category == 2) {
                    *spn = 173;
                } else {
                    *spn = 171;  // BME280 ambient
                }
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 1;
            case 27:  // ESC
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 0;
        }
    }
}

int ui_dialog_ntc_preset(int* input, int* preset) {
    WINDOW* dialog = create_dialog(10, 40, "NTC Sensor Preset");

    const char* presets[] = {"AEM", "Bosch", "GM"};
    *preset = 0;
    *input = 1;

    while (1) {
        mvwprintw(dialog, 3, 3, "Input (1-8): %d  [+/-]", *input);

        mvwprintw(dialog, 5, 3, "Preset:");
        for (int i = 0; i < 3; i++) {
            if (i == *preset) {
                wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
            mvwprintw(dialog, 5, 12 + i * 8, "[%s]", presets[i]);
            if (i == *preset) {
                wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
        }

        mvwprintw(dialog, 8, 10, "ENTER=Apply  ESC=Cancel");

        wrefresh(dialog);

        int ch = getch();
        switch (ch) {
            case KEY_LEFT:
                if (*preset > 0) (*preset)--;
                break;
            case KEY_RIGHT:
                if (*preset < 2) (*preset)++;
                break;
            case '+':
            case '=':
                if (*input < 8) (*input)++;
                break;
            case '-':
                if (*input > 1) (*input)--;
                break;
            case '\n':
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 1;
            case 27:
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 0;
        }
    }
}

int ui_dialog_pressure_preset(int* input, int* preset) {
    WINDOW* dialog = create_dialog(18, 50, "Pressure Sensor Preset");

    const char* bar_presets[] = {"1 bar", "1.5 bar", "2 bar", "2.5 bar", "3 bar",
                                  "4 bar", "5 bar", "7 bar", "10 bar", "50 bar",
                                  "100 bar", "150 bar", "200 bar"};
    const char* psi_presets[] = {"15 PSI", "30 PSI", "50 PSI", "100 PSI",
                                  "150 PSI", "200 PSI", "250 PSI", "300 PSI",
                                  "350 PSI", "400 PSI", "500 PSI"};

    int category = 0;  // 0 = bar, 1 = psi
    int selection = 0;
    *input = 1;

    while (1) {
        werase(dialog);
        draw_box_with_title(dialog, "Pressure Sensor Preset");

        mvwprintw(dialog, 2, 3, "Input (1-4): %d  [+/-]", *input);

        mvwprintw(dialog, 4, 3, "Type: ");
        if (category == 0) {
            wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 4, 10, "[Bar/PSIA]");
            wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 4, 22, " PSI/PSIG ");
        } else {
            mvwprintw(dialog, 4, 10, " Bar/PSIA ");
            wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            mvwprintw(dialog, 4, 22, "[PSI/PSIG]");
            wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
        }

        if (category == 0) {
            for (int i = 0; i < 13; i++) {
                if (i == selection) wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
                mvwprintw(dialog, 6 + i, 5, "%s", bar_presets[i]);
                if (i == selection) wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
        } else {
            for (int i = 0; i < 11; i++) {
                if (i == selection) wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
                mvwprintw(dialog, 6 + i, 5, "%s", psi_presets[i]);
                if (i == selection) wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
        }

        wrefresh(dialog);

        int ch = getch();
        switch (ch) {
            case KEY_LEFT:
            case KEY_RIGHT:
                category = 1 - category;
                selection = 0;
                break;
            case KEY_UP:
                if (selection > 0) selection--;
                break;
            case KEY_DOWN:
                if (category == 0 && selection < 12) selection++;
                else if (category == 1 && selection < 10) selection++;
                break;
            case '+':
            case '=':
                if (*input < 4) (*input)++;
                break;
            case '-':
                if (*input > 1) (*input)--;
                break;
            case '\n':
                if (category == 0) {
                    *preset = selection;  // 0-12 for bar
                } else {
                    *preset = 20 + selection;  // 20-30 for PSI
                }
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 1;
            case 27:
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 0;
        }
    }
}

int ui_dialog_tc_type(int* type) {
    WINDOW* dialog = create_dialog(12, 35, "Thermocouple Type");

    const char* types[] = {"B", "E", "J", "K", "N", "R", "S", "T"};
    *type = 3;  // Default to K

    while (1) {
        for (int i = 0; i < 8; i++) {
            if (i == *type) {
                wattron(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
            mvwprintw(dialog, 3 + i, 10, "Type %s", types[i]);
            if (i == *type) {
                wattroff(dialog, COLOR_PAIR(COLOR_HIGHLIGHT));
            }
        }

        wrefresh(dialog);

        int ch = getch();
        switch (ch) {
            case KEY_UP:
                if (*type > 0) (*type)--;
                break;
            case KEY_DOWN:
                if (*type < 7) (*type)++;
                break;
            case '\n':
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 1;
            case 27:
                delwin(dialog);
                touchwin(stdscr);
                refresh();
                return 0;
        }
    }
}

void ui_dialog_spn_list(const uint16_t* tempSpns, const uint16_t* presSpns,
                         bool egtEnabled, bool bme280Enabled) {
    WINDOW* dialog = create_dialog(22, 55, "Enabled SPNs");

    int line = 2;

    // Temperature SPNs
    wattron(dialog, COLOR_PAIR(COLOR_TITLE) | A_BOLD);
    mvwprintw(dialog, line++, 3, "Temperature Inputs:");
    wattroff(dialog, COLOR_PAIR(COLOR_TITLE) | A_BOLD);

    bool anyTemp = false;
    for (int i = 0; i < 8; i++) {
        if (tempSpns[i] != 0) {
            mvwprintw(dialog, line++, 5, "temp%d: %s(SPN %d)",
                      i + 1, ui_get_spn_name(tempSpns[i]), tempSpns[i]);
            anyTemp = true;
        }
    }
    if (!anyTemp) {
        wattron(dialog, A_DIM);
        mvwprintw(dialog, line++, 5, "(none)");
        wattroff(dialog, A_DIM);
    }

    line++;

    // Pressure SPNs
    wattron(dialog, COLOR_PAIR(COLOR_TITLE) | A_BOLD);
    mvwprintw(dialog, line++, 3, "Pressure Inputs:");
    wattroff(dialog, COLOR_PAIR(COLOR_TITLE) | A_BOLD);

    bool anyPres = false;
    for (int i = 0; i < 7; i++) {
        if (presSpns[i] != 0) {
            mvwprintw(dialog, line++, 5, "pres%d: %s(SPN %d)",
                      i + 1, ui_get_spn_name(presSpns[i]), presSpns[i]);
            anyPres = true;
        }
    }
    if (!anyPres) {
        wattron(dialog, A_DIM);
        mvwprintw(dialog, line++, 5, "(none)");
        wattroff(dialog, A_DIM);
    }

    line++;

    // EGT
    if (egtEnabled) {
        wattron(dialog, COLOR_PAIR(COLOR_SUCCESS));
        mvwprintw(dialog, line++, 3, "EGT(SPN 173): Enabled");
        wattroff(dialog, COLOR_PAIR(COLOR_SUCCESS));
    } else {
        wattron(dialog, A_DIM);
        mvwprintw(dialog, line++, 3, "EGT: Disabled");
        wattroff(dialog, A_DIM);
    }

    // BME280
    if (bme280Enabled) {
        wattron(dialog, COLOR_PAIR(COLOR_SUCCESS));
        mvwprintw(dialog, line++, 3, "BME280: Ambient(SPN 171), Baro(SPN 108), Humidity(SPN 354)");
        wattroff(dialog, COLOR_PAIR(COLOR_SUCCESS));
    } else {
        wattron(dialog, A_DIM);
        mvwprintw(dialog, line++, 3, "BME280: Disabled");
        wattroff(dialog, A_DIM);
    }

    mvwprintw(dialog, 20, 20, "Press any key");

    wrefresh(dialog);

    // Wait for any key
    nodelay(stdscr, FALSE);
    getch();
    nodelay(stdscr, TRUE);

    delwin(dialog);
    touchwin(stdscr);
    refresh();
}
