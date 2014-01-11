/*
  tag_cursor.cpp
  Provides implementation of tag cursors.
*/

#include "tag_cursor.h"

TagCursor::TagCursor(TopicList& topic_list) {
  _topics = &topic_list;
  reset();
}
const Topic& TagCursor::reset() {
  _position = _topics->begin();
  return position();
}
const Topic& TagCursor::position() const {
  return *_position;
}
const Topic& TagCursor::next() {
  return *(++_position);
}
const Topic& TagCursor::seek_to(Topic& ref) {
  while (_position != _topics->cend() && *_position < ref) {
    _position++;
  }
  return *_position;
}
