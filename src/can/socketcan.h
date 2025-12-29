#ifndef OSSM_SOCKETCAN_H
#define OSSM_SOCKETCAN_H

#include <stdint.h>
#include <stdbool.h>

// CAN frame structure
typedef struct {
    uint32_t id;
    uint8_t len;
    uint8_t data[8];
    bool extended;
} TCanFrame;

// Initialize SocketCAN interface
// Returns socket fd on success, -1 on failure
int socketcan_init(const char* interface);

// Close SocketCAN interface
void socketcan_close(int sock);

// Send a CAN frame
// Returns 0 on success, -1 on failure
int socketcan_send(int sock, const TCanFrame* frame);

// Receive a CAN frame (non-blocking)
// Returns 1 if frame received, 0 if no data, -1 on error
int socketcan_receive(int sock, TCanFrame* frame);

// Set socket to non-blocking mode
int socketcan_set_nonblocking(int sock);

#endif // OSSM_SOCKETCAN_H
