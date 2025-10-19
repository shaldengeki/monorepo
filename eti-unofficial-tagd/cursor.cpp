/*
  cursor.cpp
  Provides cursor implementation for scrolling-forward of topics.
*/

#include "cursor.hpp"
#include "topic.hpp"

const Topic& Cursor::end() const {
  /*
  Returns a topic corresponding to "past-the-end" in any cursor.
  */
  Topic* empty_topic = new Topic(0, 0);
  return *empty_topic;
}