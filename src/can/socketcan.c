#include "socketcan.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int socketcan_init(const char* interface) {
    int sock;
    struct sockaddr_can addr;
    struct ifreq ifr;

    // Create socket
    sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (sock < 0) {
        perror("socket");
        return -1;
    }

    // Get interface index
    strncpy(ifr.ifr_name, interface, IFNAMSIZ - 1);
    ifr.ifr_name[IFNAMSIZ - 1] = '\0';

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("ioctl SIOCGIFINDEX");
        close(sock);
        return -1;
    }

    // Bind socket to interface
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        return -1;
    }

    return sock;
}

void socketcan_close(int sock) {
    if (sock >= 0) {
        close(sock);
    }
}

int socketcan_send(int sock, const TCanFrame* frame) {
    struct can_frame cf;

    memset(&cf, 0, sizeof(cf));
    cf.can_id = frame->id;
    if (frame->extended) {
        cf.can_id |= CAN_EFF_FLAG;
    }
    cf.can_dlc = frame->len;
    memcpy(cf.data, frame->data, frame->len);

    ssize_t nbytes = write(sock, &cf, sizeof(cf));
    if (nbytes != sizeof(cf)) {
        return -1;
    }

    return 0;
}

int socketcan_receive(int sock, TCanFrame* frame) {
    struct can_frame cf;
    ssize_t nbytes;

    nbytes = read(sock, &cf, sizeof(cf));
    if (nbytes < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return 0;  // No data available
        }
        return -1;  // Error
    }

    if (nbytes < (ssize_t)sizeof(cf)) {
        return -1;  // Incomplete frame
    }

    frame->id = cf.can_id & CAN_EFF_MASK;
    frame->extended = (cf.can_id & CAN_EFF_FLAG) != 0;
    frame->len = cf.can_dlc;
    memcpy(frame->data, cf.data, cf.can_dlc);

    return 1;  // Frame received
}

int socketcan_set_nonblocking(int sock) {
    int flags = fcntl(sock, F_GETFL, 0);
    if (flags < 0) {
        return -1;
    }
    return fcntl(sock, F_SETFL, flags | O_NONBLOCK);
}
