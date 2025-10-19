/*
  tag.cpp
  Provides implementation of tags.
*/

#include "tag.hpp"
#include "topic.hpp"

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

void Tag::insert(Topic& topic) {
  /*
    find the given topic_id with the given last_post_time
    if it exists, remove it
    insert the given topic.
  */
  TopicList::iterator search_iter = _topic_list.find_topic(topic);

  if (search_iter != _topic_list.end() && (*search_iter).time() != topic.time()) {
    _topic_list.erase(search_iter);
    _topic_list.insert(topic);
  } else {
    _topic_list.insert(topic);
  }
}