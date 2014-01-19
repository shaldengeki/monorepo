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
#include <boost/algorithm/string/join.hpp>
namespace options = boost::program_options;

#include <sys/un.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#include "topic.h"
#include "cursor.h"
#include "tag_cursor.h"
#include "meta_cursor.h"
#include "union_cursor.h"
#include "intersect_cursor.h"
#include "difference_cursor.h"
#include "tag.h"
#include "tagd.h"

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

  unsigned int local_sock, client_sock, t, len;
  struct sockaddr_un local, remote;
  if ((local_sock = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
    perror("socket");
    exit(1);
  }  

  local.sun_family = AF_UNIX;  /* local is declared before socket() ^ */
  strcpy(local.sun_path, "/home/shaldengeki/tagd.sock");
  unlink(local.sun_path);
  len = strlen(local.sun_path) + sizeof(local.sun_family);
  if (bind(local_sock, (struct sockaddr *)&local, len) == -1) {
    perror("bind");
    exit(1);
  }

 if (listen(local_sock, 5) == -1) {
    perror("listen");
    exit(1);
  }

  const int query_max_len = 500;
  char raw_query[query_max_len];
  for(;;) {
    int done, n;
    printf("Waiting for a connection...\n");
    t = sizeof(remote);
    if ((client_sock = accept(local_sock, (struct sockaddr *)&remote, &t)) == -1) {
      perror("accept");
      exit(1);
    }

    printf("Connected.\n");

    done = 0;
    do {
      n = recv(client_sock, raw_query, query_max_len, 0);
      if (n <= 0) {
        if (n < 0) {
          perror("recv");
        }
        done = 1;
      }

      if (!done) {
        std::string query_string {raw_query};
        Cursor& tagd_cursor = tagd->parse(query_string);

        std::vector<std::string> topic_ids {std::to_string(tagd_cursor.position().id())};
        for (int i = 0; i < 50; i++) {
          Topic next_topic = tagd_cursor.next();
          if (next_topic.id() == 0) {
            break;
          }
          topic_ids.push_back(std::to_string(next_topic.id()));
        }

        std::string tag_ids = boost::algorithm::join(topic_ids, ",");
        char * writable = new char[tag_ids.size() + 1];
        std::copy(tag_ids.begin(), tag_ids.end(), writable);
        writable[tag_ids.size()] = '\0'; // don't forget the terminating 0

        if (send(client_sock, writable, strlen(writable), 0) < 0) {
          perror("send");
          done = 1;
        }
        delete[] writable;
      }
    } while (!done);
    close(client_sock);
  }

  return 0;
}