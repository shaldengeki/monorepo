/*
  tag_cursor.cpp
  Provides implementation of tag cursors.
*/

#include "tag_cursor.h"

TagCursor::TagCursor(Tag& tag) {
  _tag = &tag;
  reset();
}
const Topic& TagCursor::reset() {
  _position = _tag->topic_list().begin();
  return position();
}
const Topic& TagCursor::position() const {
  return *_position;
}
const Topic& TagCursor::next() {
  return *(++_position);
}
const Topic& TagCursor::seek_to(Topic& ref) {
  while (_position != _tag->topic_list().cend() && *_position < ref) {
    _position++;
  }
  return *_position;
}
