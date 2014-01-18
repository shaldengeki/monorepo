/*
  intersect_cursor.cpp
  Provides implementation for a cursor that performs set intersection on a set of cursors.
*/

#include "intersect_cursor.h"
#include "topic.h"

IntersectCursor::IntersectCursor(std::vector<Cursor*>& cursors) : MetaCursor::MetaCursor(cursors) {
}
const Topic& IntersectCursor::position() const { 
  return MetaCursor::position();
}
const Topic& IntersectCursor::position(Topic& out) const {
  /* 
    Given an input lower-bound "reference topic" at out:
    For each of the cursors in this metacursor, seek_to out and see if the resultant topic is out.
    If any of the cursors seek past out, set this sought-to topic as the new "reference topic" and repeat.
  */
  if (out.id() == end().id()) {
    // We've run out of topics in at least one cursor.
    return out;
  }
  for (std::vector<Cursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    Topic cursor_min = (*current_cursor)->seek_to(out);
    if (cursor_min.id() == end().id()) {
      return end();
    }

    if (cursor_min > out) {
      // this cursor points past out.
      return position(cursor_min);
    }
  }
  // all the contained cursors point to out.
  return out;
}
const Topic& IntersectCursor::next() {
  /* 
    Iterate through each cursor in this cursor, incrementing those cursors that are pointing to the current cursor's position.
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