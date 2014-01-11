/* 
  tag.h
  Provides datastructure for tags.
*/
#ifndef TAG_H
#define TAG_H

#include "topic.h"

class Tag {
  public:
    Tag(std::string name, TopicList topic_list);
};
#endif