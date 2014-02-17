/* 
  tag.h
  Provides datastructure for tags.
*/
#ifndef TAG_H
#define TAG_H

#include <string>
#include "topic.hpp"

class Tag {
  private:
    unsigned long _id;
    TopicList _topic_list;
  public:
    Tag(unsigned long& id);
    Tag(unsigned long& id, TopicList& topic_list);
    ~Tag();
    unsigned long& id();
    TopicList& topic_list();
    void insert(Topic& topic);
};
#endif