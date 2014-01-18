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
  mysqlpp::Connection database;
  mysqlpp::UseQueryResult tag_iter;
  try {
    database = mysqlpp::Connection(vm["database"].as<std::string>().c_str(), vm["host"].as<std::string>().c_str(), vm["username"].as<std::string>().c_str(), vm["password"].as<std::string>().c_str());
    mysqlpp::Query tag_query = database.query();
    tag_query << "LOCK TABLES tags_topics READ, topics READ;";
    tag_query.exec();

    tag_query.reset();
    tag_query << "SELECT tag_id, topic_id, topics.lastPostTime AS last_post_time FROM tags_topics INNER JOIN topics ON topics.ll_topicid = tags_topics.topic_id ORDER BY tag_id ASC, last_post_time DESC, topic_id DESC";
    tag_iter = tag_query.use();
  } catch (mysqlpp::ConnectionFailed er) {
    std::cerr << "Could not connect to MySQL database." << std::endl;
    throw er;
  }

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

  mysqlpp::Query tag_query = database.query();
  tag_query << "UNLOCK TABLES;";
  tag_query.exec();

  std::string query_string = "5-99";
  Cursor& tagd_cursor = tagd->parse(query_string);
  std::cout << "TagD pos: " << tagd_cursor.position().id() << std::endl;
  std::cout << "TagD next: " << tagd_cursor.next().id() << std::endl;
  std::cout << "TagD next: " << tagd_cursor.next().id() << std::endl;
  std::cout << "TagD next: " << tagd_cursor.next().id() << std::endl;
  std::cout << "TagD next: " << tagd_cursor.next().id() << std::endl;

  return 0;
}