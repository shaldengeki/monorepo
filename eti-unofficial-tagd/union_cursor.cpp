#include "union_cursor.h"

UnionCursor::UnionCursor(std::vector<BaseCursor*>& cursors) : MetaCursor::MetaCursor(cursors) {
}
const Topic& UnionCursor::position() const { 
  return MetaCursor::position();
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