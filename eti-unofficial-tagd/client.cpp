#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#include <boost/program_options.hpp>
namespace options = boost::program_options;

int main(int argc, char* argv[]) {
  options::options_description allOptions("Options");

  allOptions.add_options()
    ("help", "produce this help message")
    ("socket", options::value<std::string>()->default_value("/tmp/tagd.sock"), "path to socket")
  ;
  options::variables_map vm;
  options::store(options::parse_command_line(argc, argv, allOptions), vm);
  options::notify(vm);

  if (vm.count("help")) {
    std::cout << allOptions << std::endl;
    return 1;
  }


  int s, t, len;
  struct sockaddr_un remote;
  char* response = new char[500];
  char* message = new char[500];

  if ((s = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
    perror("socket");
    exit(1);
  }

  printf("Trying to connect...\n");

  remote.sun_family = AF_UNIX;

  strcpy(remote.sun_path, vm["socket"].as<std::string>().c_str());
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

    if ((t=recv(s, response, 500, 0)) > 0) {
      std::cout << response << std::endl;
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
