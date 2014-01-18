/*
  main.cpp
  @author shaldengeki
  Loads all ETI tag data into memory and provides a service to search for topics.
  For up-to-date help: tagd --help
*/

#include <iostream>
#include <string>
#include <map>
#include <ctime>
#include <algorithm> 
#include <vector>
#include <utility>

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
  ;
  options::variables_map vm;
  options::store(options::parse_command_line(argc, argv, allOptions), vm);
  options::notify(vm);

  if (vm.count("help")) {
    std::cout << allOptions << std::endl;
    return 1;
  }

  Topic* topic = new Topic(1, 5);
  Topic* topic2 = new Topic(2, 2);
  Topic* topic3 = new Topic(2, 3);
  Topic* topic4 = new Topic(3, 4);

  TopicList* topic_list_one = new TopicList();
  topic_list_one->insert(*topic);
  topic_list_one->insert(*topic2);
  topic_list_one->insert(*topic3);
  unsigned long tag_id_one {1};
  Tag* tag_one = new Tag(tag_id_one, *topic_list_one);

  TagCursor* cursor = new TagCursor(*tag_one);

  std::cout << "Tag pos: " << cursor->position().id() << std::endl;
  std::cout << "Tag next: " << cursor->next().id() << std::endl;
  std::cout << "Tag next: " << cursor->next().id() << std::endl;
  std::cout << "Tag next: " << cursor->next().id() << std::endl;
  cursor->reset();

  TopicList* topic_list_two = new TopicList();
  topic_list_two->insert(*topic2);
  topic_list_two->insert(*topic3);
  topic_list_two->insert(*topic4);
  unsigned long tag_id_two {2};
  Tag* tag_two = new Tag(tag_id_two, *topic_list_two);
  TagCursor* cursor_two = new TagCursor(*tag_two);

  std::vector<Cursor*> cursor_vector {cursor, cursor_two};
  UnionCursor* union_cursor = new UnionCursor(cursor_vector);

  std::cout << "Union pos: " << union_cursor->position().id() << std::endl;
  std::cout << "Union next: " << union_cursor->next().id() << std::endl;
  std::cout << "Union next: " << union_cursor->next().id() << std::endl;
  std::cout << "Union next: " << union_cursor->next().id() << std::endl;
  std::cout << "Union next: " << union_cursor->next().id() << std::endl;

  cursor->reset();
  cursor_two->reset();
  IntersectCursor* intersect_cursor = new IntersectCursor(cursor_vector);

  std::cout << "Intersect pos: " << intersect_cursor->position().id() << std::endl;
  std::cout << "Intersect next: " << intersect_cursor->next().id() << std::endl;
  std::cout << "Intersect next: " << intersect_cursor->next().id() << std::endl;

  cursor->reset();
  cursor_two->reset();
  DifferenceCursor* difference_cursor = new DifferenceCursor(cursor_vector);

  std::cout << "Difference pos: " << difference_cursor->position().id() << std::endl;
  std::cout << "Difference next: " << difference_cursor->next().id() << std::endl;

  TagD* tagd = new TagD();
  tagd->set(*tag_one);
  tagd->set(*tag_two);

  std::string tag_query = "1-2";
  Cursor& tagd_cursor = tagd->parse(tag_query);
  std::cout << "TagD pos: " << tagd_cursor.position().id() << std::endl;
  std::cout << "TagD next: " << tagd_cursor.next().id() << std::endl;

  std::string tag_query_two = "1+2";
  Cursor& tagd_cursor_two = tagd->parse(tag_query_two);
  std::cout << "TagD pos: " << tagd_cursor_two.position().id() << std::endl;
  std::cout << "TagD next: " << tagd_cursor_two.next().id() << std::endl;

  return 0;
}