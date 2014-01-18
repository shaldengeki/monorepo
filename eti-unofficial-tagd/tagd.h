/*
  tagd.h
  Provides interface for a network service that compiles tag query-strings into a graph of tag and set cursors
  Then returns specified topics from that graph.
*/

#ifndef TAGD_H
#define TAGD_H

#include <map>
#include <string>
#include "tag.h"
#include "cursor.h"

class TagD {
  private:
    std::map<unsigned long, Tag*> _tags;
  public:
    TagD();
    ~TagD() {}
    void set(Tag& tag);
    Tag& get(unsigned long tag_id);
    Cursor& parse(std::string& tag_query);
    unsigned int size();
};

#endif