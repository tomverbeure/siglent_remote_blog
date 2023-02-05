#include <stdio.h>
#include <string.h>
#include <lxi.h>

int main(int argc, char **argv)
{
     char response[65536];
     int device, length, timeout = 1000;
     char *command = "*IDN?";

     lxi_init();
     device = lxi_connect(argv[1], 0, "inst0", timeout, VXI11);
     lxi_send(device, command, strlen(command), timeout);
     lxi_receive(device, response, sizeof(response), timeout);
     printf("%s\n", response);
     lxi_disconnect(device);
}
