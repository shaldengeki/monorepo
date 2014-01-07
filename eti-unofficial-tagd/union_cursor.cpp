#include "union_cursor.h"

UnionCursor::UnionCursor(std::vector<BaseCursor*>& cursors) : MetaCursor::MetaCursor(cursors) {
}
const Topic& UnionCursor::position(Topic& out) const {
  /* 
    Iterate through each tag in this cursor and return the lowest topic that any of the tags is pointing to.
  */
  for (std::vector<BaseCursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    Topic tag_min = (*current_cursor)->position();
    if (out.id() == 0 || (tag_min.id() != 0 && tag_min < out)) {
      out = tag_min;
    }
  }
  return out;
}
const Topic& UnionCursor::position() const {
  std::vector<BaseCursor*>::const_iterator first_tag = _cursors.cbegin();
  Topic curr_position = (*first_tag)->position();

  return position(curr_position);
}
const Topic& UnionCursor::reset() {
  for (std::vector<BaseCursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    (*current_cursor)->reset();
  }
  return position();
}
const Topic& UnionCursor::next() {
  /* 
    Iterate through each tag in this cursor, incrementing those tags that are pointing to the current cursor's position.
    Return the cursor's position after having incremented said tags.
  */
  Topic curr_position = position();

  for (std::vector<BaseCursor*>::iterator current_tag = _cursors.begin(); current_tag != _cursors.end(); ++current_tag) {
    Topic current_topic = (*current_tag)->position();
    if (current_topic == curr_position) {
      (*current_tag)->next();
    }
  }
  return position();
}
const Topic& UnionCursor::seek_to(Topic& ref) {
  /*
    Iterate through each tag in this cursor, fast-forwarding each tag to (or just past) an input topic.
    Return the cursor's position after having fast-forwarded.
  */
  for (std::vector<BaseCursor*>::iterator current_tag = _cursors.begin(); current_tag != _cursors.end(); ++current_tag) {
    (*current_tag)->seek_to(ref);
  }
  return position();
}
