/*
  topic.cpp
  Provides implementation of topics.
*/

#include "topic.hpp"
#include <algorithm>

struct topic_id_compare : public std::unary_function<Topic&, bool>{
  explicit topic_id_compare(const Topic& search_topic) : search_topic(search_topic) {}
  bool operator() (const Topic& comp_topic) {
    return comp_topic.id() == search_topic.id();
  }
  Topic search_topic;
};

TopicList::iterator TopicList::find_topic(Topic& search_topic) {
  return std::find_if(this->begin(), this->end(), topic_id_compare(search_topic));
}