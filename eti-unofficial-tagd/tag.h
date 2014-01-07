#ifndef TAG_H
#define TAG_H

#include "topic.h"

/* Tag data structure. */
class Tag {
  public:
    Tag(std::string name, TopicList topic_list);
};
#endif