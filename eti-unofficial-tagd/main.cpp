/*
  main.cpp
  @author shaldengeki
  Loads all ETI tag data into memory and provides a service to search for topics.
  For up-to-date help: tagd --help
*/

#include <algorithm> 
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <locale>
#include <map>
#include <string>
#include <utility>
#include <vector>

#include <mysql++.h>
#include <boost/program_options.hpp>
namespace options = boost::program_options;
#include <boost/algorithm/string/join.hpp>
#include <boost/algorithm/string/predicate.hpp>
#include <boost/lexical_cast.hpp>

#include <sys/un.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#include "topic.hpp"
#include "cursor.hpp"
#include "tag_cursor.hpp"
#include "meta_cursor.hpp"
#include "union_cursor.hpp"
#include "intersect_cursor.hpp"
#include "difference_cursor.hpp"
#include "tag.hpp"
#include "tagd.hpp"

/* Benchmark and timing data structures. */
typedef std::pair<clock_t, std::string> Timing;

struct BenchInfo {
  unsigned int    Count;
  float           Sum;
  float           Max;
  float           Min;
};

typedef std::map<std::string, BenchInfo> BenchMap;

bool operator< (Topic& t1, Topic& t2) {
  return (t1.time() < t2.time()) || (t1.time() == t2.time() && t1.id() < t2.id());
}
bool operator> (Topic& t1, Topic& t2) {
  return (t1.time() > t2.time()) || (t1.time() == t2.time() && t1.id() > t2.id());
}
bool operator== (Topic& t1, Topic& t2) {
  return (t1.time() == t2.time()) && (t1.id() == t2.id());
}
bool operator!= (Topic& t1, Topic& t2) {
  return !(t1 == t2);
}
bool operator<= (Topic& t1, Topic& t2) {
  return t1 < t2 || t1 == t2;
}
bool operator>= (Topic& t1, Topic& t2) {
  return t1 > t2 || t1 == t2;
}

int main(int argc, char* argv[]) {
  options::options_description allOptions("Options");

  allOptions.add_options()
    ("help", "produce this help message")
    ("host", options::value<std::string>()->default_value("localhost"), "MySQL host")
    ("username", options::value<std::string>()->default_value("root"), "MySQL username")
    ("password", options::value<std::string>()->default_value(""), "MySQL password")
    ("database", options::value<std::string>()->default_value("eti"), "MySQL database")
    ("join-table", options::value<std::string>(), "tags-topics join table")
    ("topic-table", options::value<std::string>(), "topics table")
    ("socket", options::value<std::string>()->default_value("/tmp/tagd.sock"), "path to socket")
  ;
  options::variables_map vm;
  options::store(options::parse_command_line(argc, argv, allOptions), vm);
  options::notify(vm);

  if (vm.count("help")) {
    std::cout << allOptions << std::endl;
    return 1;
  }

  // load tag, topic data from the database.
  std::cout << "Connecting to database and loading tag-topic data..." << std::endl;
  mysqlpp::Connection database;
  mysqlpp::UseQueryResult tag_iter;
  try {
    database = mysqlpp::Connection(vm["database"].as<std::string>().c_str(), vm["host"].as<std::string>().c_str(), vm["username"].as<std::string>().c_str(), vm["password"].as<std::string>().c_str());
  } catch (mysqlpp::ConnectionFailed er) {
    std::cerr << "Could not connect to MySQL database." << std::endl;
    throw er;
  }

  mysqlpp::Query tag_query = database.query();
  tag_query << "LOCK TABLES tags_topics READ, topics READ;";
  tag_query.exec();

  tag_query.reset();
  tag_query << "SELECT tag_id, topic_id, topics.lastPostTime AS last_post_time FROM tags_topics INNER JOIN topics ON topics.ll_topicid = tags_topics.topic_id ORDER BY tag_id ASC, last_post_time DESC, topic_id DESC";
  tag_iter = tag_query.use();

  // insert tag, topic data into TagD.
  TagD* tagd = new TagD();
  unsigned long curr_tag_id = 1;
  TopicList tag_topics = TopicList();
  while (mysqlpp::Row row = tag_iter.fetch_row()) {
    unsigned long tag_id = std::strtoul(row["tag_id"].c_str(), NULL, 0);
    if (tag_id != curr_tag_id) {
      // new tag. create tag with all prior topics and reset topic list.
      Tag* curr_tag = new Tag(curr_tag_id, tag_topics);
      tagd->set(*curr_tag);
      curr_tag_id = tag_id;
      tag_topics = TopicList();
    }

    unsigned int last_post_time = (unsigned int) std::strtoul(row["last_post_time"].c_str(), NULL, 0);
    unsigned int topic_id = (unsigned int) std::strtoul(row["topic_id"].c_str(), NULL, 0);

    Topic curr_topic = Topic(last_post_time, topic_id);
    tag_topics.insert(curr_topic);
  }
  Tag* curr_tag = new Tag(curr_tag_id, tag_topics);
  tagd->set(*curr_tag);

  tag_query.reset();
  tag_query << "UNLOCK TABLES;";
  tag_query.exec();

  // All done!
  std::cout << "Loaded " << tagd->size() << " tags." << std::endl;

  int local_sock, client_sock, t, len;
  struct sockaddr_un local, remote;
  if ((local_sock = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
    perror("socket");
    exit(1);
  }  

  local.sun_family = AF_UNIX;  /* local is declared before socket() ^ */
  strcpy(local.sun_path, vm["socket"].as<std::string>().c_str());
  unlink(local.sun_path);
  len = strlen(local.sun_path) + sizeof(local.sun_family);
  if (bind(local_sock, (struct sockaddr *)&local, len) == -1) {
    perror("bind");
    exit(1);
  }

 if (listen(local_sock, 5) == -1) {
    perror("listen");
    exit(2);
  }

  const int query_max_len = 500;
  char raw_query[query_max_len];

  fd_set master, read_fds;
  int fdmax;

  FD_SET(local_sock, &master);
  fdmax = local_sock;

  int new_fd, curr_fd, n;
  char remote_ip[INET6_ADDRSTRLEN];
  socklen_t addr_len;

  while(true) {
    read_fds = master;
    if (select(fdmax + 1, &read_fds, NULL, NULL, NULL) == -1) {
      perror("select");
      exit(3);
    }

    for (curr_fd = 0; curr_fd <= fdmax; ++curr_fd) {
      if (FD_ISSET(curr_fd, &read_fds)) {
        // something's here!
        if (curr_fd == local_sock) {
          // new connection.
          addr_len = sizeof(remote);
          new_fd = accept(local_sock, (struct sockaddr*) &remote, &addr_len);
          if (new_fd == -1) {
            perror("accept");
          } else {
            // add this connection to the master set.
            FD_SET(new_fd, &master);
            if (new_fd > fdmax) {
              fdmax = new_fd;
            }
            printf("selectserver: new connection on socket %d\n", new_fd);
          }

        } else {
          // handle data from a client.
          n = recv(curr_fd, raw_query, query_max_len, 0);
          if (n <= 0) {
            // client has hung up or some error occurred.
            if (n < 0) {
              perror("recv");
            } else {
              printf("selectserver: socket %d hung up\n", curr_fd);
            }
            close(curr_fd);
            FD_CLR(curr_fd, &master);
          } else {
            std::string query_string {raw_query};
            if (boost::starts_with(query_string, "insert")) {
              // client has sent us a topic update.
              try {
                tagd->parse_insert(query_string);
                std::string message {"OK"};
                if (send(curr_fd, message.c_str(), message.length(), 0) < 0) {
                  perror("send");
                }
              } catch (std::out_of_range& e) {
                // client has specified a tag that doesn't exist.
                perror("tag out of range");
              }
            } else {
              // client has sent us a tag query string.
              std::vector<std::string> topic_ids;
              try {
                Cursor& tagd_cursor = tagd->parse_query(query_string);

                for (int curr_topic = 0; curr_topic < 50; curr_topic++) {
                  Topic next_topic = tagd_cursor.next();
                  if (next_topic.id() == 0) {
                    break;
                  }
                  topic_ids.push_back(std::to_string(next_topic.id()));
                }
              } catch (std::out_of_range& e) {
                // client specified a tag that doesn't exist.
                perror("tag out of range");
              }
              std::string joined_ids = "{" + boost::algorithm::join(topic_ids, ", ") + "}";
              if (send(curr_fd, joined_ids.c_str(), joined_ids.size(), 0) < 0) {
                perror("send");
              }

            }
          }
        }
      }
    }
  }
  return 0;
}