/*
  tag.cpp
  Provides implementation of tags.
*/

#include "tag.h"

Tag::Tag(unsigned long& id) : _id(id) {

}
Tag::Tag(unsigned long& id, TopicList& topic_list) : _id(id), _topic_list(topic_list) {

}

unsigned long& Tag::id() {
  return _id;
}

TopicList& Tag::topic_list() {
  return _topic_list;
}