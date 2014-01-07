/*
  tagd.cpp
  @author shaldengeki
  Loads all ETI tag data into memory and provides a service to search for topics.
  For up-to-date help: tagd --help
*/

#include <cstdlib>
#include <iostream>
#include <string>
#include <sstream>
#include <limits>
#include <map>
#include <ctime>
#include <algorithm> 
#include <vector>

#include <mysql++.h>
using namespace mysqlpp;
using namespace std;

#include <boost/program_options.hpp>
namespace options = boost::program_options;
using namespace std;


/* Benchmark and timing data structures. */
typedef pair<clock_t, string> Timing;

struct BenchInfo {
  unsigned int    Count;
  float           Sum;
  float           Max;
  float           Min;
};

typedef map< string, BenchInfo > BenchMap;

/* Topic data structures. */
class Topic : public pair<unsigned int, unsigned int> {
  public:
    Topic(unsigned int last_post_time, unsigned int topic_id) : pair<unsigned int, unsigned int>(last_post_time, topic_id) {};
    unsigned int time() const { return first; };
    unsigned int id() const { return second; };
};
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

class TopicList : public set<Topic> {};


/* Base cursor interface. */
class BaseCursor {
  public:
    virtual ~BaseCursor() {}
    virtual const Topic& reset() = 0;
    virtual const Topic& next() = 0;
    virtual const Topic& seek_to(Topic& ref) = 0;
    virtual const Topic& position() const = 0;
};

/* Cursor for single tags. */
class TagCursor : public BaseCursor {
  private:
    TopicList::iterator _position;
    TopicList* _topics;
  public:
    TagCursor(TopicList& topic_list);
    virtual const Topic& reset();
    virtual const Topic& position() const;
    virtual const Topic& next();
    virtual const Topic& seek_to(Topic& ref);
};
TagCursor::TagCursor(TopicList& topic_list) {
  _topics = &topic_list;
  reset();
}
const Topic& TagCursor::reset() {
  _position = _topics->begin();
  return position();
}
const Topic& TagCursor::position() const {
  return *_position;
}
const Topic& TagCursor::next() {
  return *(++_position);
}
const Topic& TagCursor::seek_to(Topic& ref) {
  while (_position != _topics->cend()) {
    if (*_position >= ref) {
      return *_position;
    }
    _position++;
  }
}

/* Metacursor classes for groups of tags. */
class GroupCursor : public BaseCursor {
  protected:
    vector<BaseCursor*> _cursors;
  public:
    GroupCursor(vector<BaseCursor*>& cursors);
    virtual ~GroupCursor() {}
};
GroupCursor::GroupCursor(vector<BaseCursor*>& cursors) {
  _cursors = cursors;
}

class UnionCursor : public GroupCursor {
  protected:
    virtual const Topic& position(Topic& out) const;
  public:
    UnionCursor(vector<BaseCursor*>& cursors);
    virtual const Topic& position() const;
    virtual const Topic& reset();
    virtual const Topic& next();
    virtual const Topic& seek_to(Topic& ref);
};
UnionCursor::UnionCursor(vector<BaseCursor*>& cursors) : GroupCursor::GroupCursor(cursors) {
}
const Topic& UnionCursor::position(Topic& out) const {
  /* 
    Iterate through each tag in this cursor and return the lowest topic that any of the tags is pointing to.
  */
  for (vector<BaseCursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    Topic tag_min = (*current_cursor)->position();
    if (out.id() == 0 || (tag_min.id() != 0 && tag_min < out)) {
      out = tag_min;
    }
  }
  return out;
}
const Topic& UnionCursor::position() const {
  vector<BaseCursor*>::const_iterator first_tag = _cursors.cbegin();
  Topic curr_position = (*first_tag)->position();

  return position(curr_position);
}
const Topic& UnionCursor::reset() {
  for (vector<BaseCursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    (*current_cursor)->reset();
  }
  return position();
}
const Topic& UnionCursor::next() {
  /* 
    Iterate through each tag in this cursor, incrementing those tags that are pointing to the current cursor's position.
    Return the cursor's position after having incremented said tags.
  */
  Topic curr_position = position();

  for (vector<BaseCursor*>::iterator current_tag = _cursors.begin(); current_tag != _cursors.end(); ++current_tag) {
    Topic current_topic = (*current_tag)->position();
    if (current_topic == curr_position) {
      (*current_tag)->next();
    }
  }
  return position();
}
const Topic& UnionCursor::seek_to(Topic& ref) {
  /*
    Iterate through each tag in this cursor, fast-forwarding each tag to (or just past) an input topic.
    Return the cursor's position after having fast-forwarded.
  */
  for (vector<BaseCursor*>::iterator current_tag = _cursors.begin(); current_tag != _cursors.end(); ++current_tag) {
    Topic tag_position = (*current_tag)->seek_to(ref);
  }
  return position();
}

class IntersectCursor : public GroupCursor {
  protected:
    virtual const Topic& position(Topic& out) const;
  public:
    IntersectCursor(vector<BaseCursor*>& cursors);
    virtual const Topic& position() const;
    virtual const Topic& reset();
    virtual const Topic& next();
    virtual const Topic& seek_to(Topic& ref);
};


class DifferenceCursor : public GroupCursor {
  protected:
    virtual const Topic& next(Topic& out);
    virtual const Topic& seek_to(Topic& ref, Topic& out);
    virtual const Topic& position(Topic& out) const;
  public:
    virtual const Topic& next();
    virtual const Topic& seek_to(Topic& ref);
    virtual const Topic& position() const;
};


/* Tag data structure. */
class Tag {
  public:
    Tag(string name, TopicList topic_list);
};


int main(int argc, char* argv[]) {
  options::options_description allOptions("Options");
  allOptions.add_options()
    ("help", "produce this help message")
  ;
  options::variables_map vm;
  options::store(options::parse_command_line(argc, argv, allOptions), vm);
  options::notify(vm);

  if (vm.count("help")) {
    cout << allOptions << endl;
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

  TagCursor* cursor = new TagCursor(*topic_list_one);

  cout << "Tag position: " << cursor->position().id() << endl;
  cout << "Tag next: " << cursor->next().id() << endl;
  cout << "Tag next: " << cursor->next().id() << endl;
  cursor->reset();

  TopicList* topic_list_two = new TopicList();
  topic_list_two->insert(*topic2);
  topic_list_two->insert(*topic3);
  topic_list_two->insert(*topic4);
  TagCursor* cursor_two = new TagCursor(*topic_list_two);

  vector<BaseCursor*> cursor_vector {cursor, cursor_two};
  UnionCursor* union_cursor = new UnionCursor(cursor_vector);

  cout << "Union cursor position: " << union_cursor->position().id() << endl;
  cout << "Union cursor next: " << union_cursor->next().id() << endl;
  cout << "Union cursor next: " << union_cursor->next().id() << endl;
  cout << "Union cursor next: " << union_cursor->next().id() << endl;

  return 0;
}