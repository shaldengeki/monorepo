/*
  tagd.h
  Provides interface for a network service that compiles tag query-strings into a graph of tag and set cursors
  Then returns specified topics from that graph.
*/

#ifndef TAGD_H
#define TAGD_H

#include <map>
#include <string>
#include "tag.hpp"
#include "topic.hpp"
#include "cursor.hpp"

class TagD {
  private:
    std::map<unsigned long, Tag*> _tags;
  public:
    TagD();
    ~TagD() {}
    void set(Tag& tag);
    Tag& get(unsigned long tag_id);
    void insert_topic(unsigned long tag_id, Topic& topic);
    void parse_insert(std::string& insert_query);
    Cursor& parse_query(std::string& tag_query);
    unsigned int size();
};

#endif