# OSSM Config Tool - ncurses TUI for J1939 configuration
CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -D_GNU_SOURCE -I./src
LDFLAGS = -lncurses -lpthread

SRC_DIR = src
BUILD_DIR = build
TARGET = ossm-config

SRCS = $(wildcard $(SRC_DIR)/*.c) \
       $(wildcard $(SRC_DIR)/ui/*.c) \
       $(wildcard $(SRC_DIR)/can/*.c) \
       $(wildcard $(SRC_DIR)/protocol/*.c)

OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SRCS))

.PHONY: all clean install

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(BUILD_DIR) $(TARGET)

install: $(TARGET)
	install -m 755 $(TARGET) /usr/local/bin/

# Debug build
debug: CFLAGS += -g -DDEBUG
debug: clean all
