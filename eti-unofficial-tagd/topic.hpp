/*
  topic.h
  Provides interface for topics.
*/

#ifndef TOPIC_H
#define TOPIC_H

#include <utility>
#include <set>

class Topic : public std::pair<unsigned int, unsigned int> {
  public:
    Topic(unsigned int last_post_time, unsigned int topic_id) : std::pair<unsigned int, unsigned int>(last_post_time, topic_id) {};
    unsigned int time() const { return first; };
    unsigned int id() const { return second; };
};

class TopicList : public std::set<Topic> {
  public:
    TopicList::iterator find_topic(Topic& search_topic);
};
#endif