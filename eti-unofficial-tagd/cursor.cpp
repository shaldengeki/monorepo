/*
  cursor.cpp
  Provides cursor implementation for scrolling-forward of topics.
*/

#include "cursor.h"
#include "topic.h"

const Topic& Cursor::end() const {
  /*
  Returns a topic corresponding to "past-the-end" in any cursor.
  */
  Topic* empty_topic = new Topic(0, 0);
  return *empty_topic;
}