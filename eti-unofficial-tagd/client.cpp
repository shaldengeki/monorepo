#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

int main(void)
{
    int s, t, len;
    struct sockaddr_un remote;
    char* message = new char[500];

    if ((s = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        perror("socket");
        exit(1);
    }

    printf("Trying to connect...\n");

    remote.sun_family = AF_UNIX;

    strcpy(remote.sun_path, "/home/shaldengeki/tagd.sock");
    len = strlen(remote.sun_path) + sizeof(remote.sun_family);
    if (connect(s, (struct sockaddr *)&remote, len) == -1) {
        perror("connect");
        exit(1);
    }

    printf("Connected.\n");

    while(printf("> "), fgets(message, 500, stdin), !feof(stdin)) {
        if (send(s, message, strlen(message), 0) == -1) {
            perror("send");
            exit(1);
        }

        if ((t=recv(s, message, 500, 0)) > 0) {
            unsigned int* int_buffer = reinterpret_cast<unsigned int*>(message);
            for (int i = 0; i < 50; ++i) {
                std::cout << int_buffer[i] << std::endl;
            }
        } else {
            if (t < 0) perror("recv");
            else printf("Server closed connection\n");
            exit(1);
        }
    }

    delete message;
    close(s);

    return 0;
}
