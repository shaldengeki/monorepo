/*
  union_cursor.cpp
  Provides implementation for a cursor that performs set union on a set of cursors.
*/

#include "union_cursor.h"

UnionCursor::UnionCursor(std::vector<Cursor*>& cursors) : MetaCursor::MetaCursor(cursors) {
}
const Topic& UnionCursor::position() const { 
  return MetaCursor::position();
}
const Topic& UnionCursor::position(Topic& out) const {
  /* 
    Iterate through each cursor in this metacursor and return the lowest topic that any of the cursors is pointing to.
  */
  for (std::vector<Cursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    Topic cursor_min = (*current_cursor)->position();
    if (out.id() == 0 || (cursor_min.id() != 0 && cursor_min < out)) {
      out = cursor_min;
    }
  }
  return out;
}
const Topic& UnionCursor::next() {
  /* 
    Iterate through each cursor in this metacursor, incrementing those cursors that are pointing to the current cursor's position.
    Return the cursor's position after having incremented said cursors.
  */
  Topic curr_position = position();

  for (std::vector<Cursor*>::iterator current_cursor = _cursors.begin(); current_cursor != _cursors.end(); ++current_cursor) {
    Topic current_topic = (*current_cursor)->position();
    if (current_topic == curr_position) {
      (*current_cursor)->next();
    }
  }
  return position();
}