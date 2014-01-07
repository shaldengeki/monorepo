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
  while (_position != _topics->cend()) {
    if (*_position >= ref) {
      return *_position;
    }
    _position++;
  }
}
