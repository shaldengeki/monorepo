/* 
  tag.h
  Provides datastructure for tags.
*/
#ifndef TAG_H
#define TAG_H

#include <string>
#include "topic.h"

class Tag {
  private:
    std::string name;
    TopicList topic_list;
  public:
    Tag(std::string& name) : name(name) {};
    Tag(std::string& name, TopicList& topic_list);
};
#endif