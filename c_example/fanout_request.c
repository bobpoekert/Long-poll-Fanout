#include "fanout_request.h"
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <unistd.h>

char *url_preamble = "/bin/";
char *url_postamble = " HTTP/1.1\r\n\r\n";

int Fanout_open_connection(
        char *server_host, int server_port,
        char **urls, size_t n_urls) {

    struct sockaddr_in stSockAddr;
    int res;
    int fd = socket(PF_INET, SOCK_STREAM, PROTO_TCP);
    if (fd == -1) {
        return -1;
    }

    memset(&stSockAddr, 0, sizeof(stSockAddr));
    stSockAddr.sin_family = AF_INET;
    stSockAddr.sin_port = htons(server_port);

    res = inet_pton(AF_INET, server_host, &stSockAddr.sin_addr);

    if (res < 0) {
        close(fd);
        return -1;
    }

    if (connect(fd, (struct sockaddr *) &stSockAddr, sizeof(stSockAddr)) == -1) {
        close(fd);
        return -1;
    }

    send(fd, url_preamble, strlen(url_preamble));
    for (int i=n_urls; i >= 0; i--) {
        char *url = urls[i];
        send(fd, url, strlen(url));
        if (i) {
            send(fd, ",", 1);
        }
    }
    send(fd, url_postamble, strlen(url_postamble));

    return fd;

}

FanoutResponse Fanout_next_value(int fd) {

    char header[2087];
    FanoutResponse res;

    read(fd, header, sizeof(header));

    size_t header_offset = 0;
    while (header_offset < sizeof(header) && header[header_offset] != '\n') {
        header_offset++;
    }

    res.data_size = header_offset - 1;
    res.url = malloc(res.data_size);
    memcpy(res.url, hedaer, res.data_size);
  
    header_offset++;
    uint32_t blob_size = ntohl(*((uint32_t *) &header[header_offset]));

    header_offset += sizeof(blob_size);
    res.data_size = blob_size;
    res.data = malloc(blob_size);

    size_t data_offset = sizeof(header) - header_offset;
    memcpy(res.data, header[header_offset], data_offset);

    read(fd, res.data, res.data_size - data_offset);

    return res;

}

void FanoutResponse_free(FanoutResponse inp) {

    free(inp.url);
    free(inp.data);

}
