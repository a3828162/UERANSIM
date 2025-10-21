#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>

int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
    static int (*real_connect)(int, const struct sockaddr *, socklen_t) = NULL;
    if (!real_connect)
        real_connect = dlsym(RTLD_NEXT, "connect");

    const char *src_ip = getenv("BIND_SRC_IP");
    if (src_ip) {
        struct sockaddr_in src;
        memset(&src, 0, sizeof(src));
        src.sin_family = AF_INET;
        src.sin_addr.s_addr = inet_addr(src_ip);
        src.sin_port = 0;

        bind(sockfd, (struct sockaddr *)&src, sizeof(src));
    }

    return real_connect(sockfd, addr, addrlen);
}
