#include "difference_cursor.h"

DifferenceCursor::DifferenceCursor(std::vector<Cursor*>& cursors) : MetaCursor::MetaCursor(cursors) {
}
const Topic& DifferenceCursor::position() const { 
  return MetaCursor::position();
}
const Topic& DifferenceCursor::position(Topic& out) const {
  /* 
    Given an input lower-bound "reference topic" at out:
    For each of the cursors in this metacursor, seek_to out and see if the resultant topic is out.
    If any of the cursors seek to out, find the next-highest topic.
  */
  // ensure that the first cursor has at least one topic at or after the reference topic.
  std::vector<Cursor*>::const_iterator current_cursor = _cursors.cbegin();
  Cursor* first_cursor = *current_cursor;

  out = first_cursor->seek_to(out);

  if (out.id() == 0) {
    // We've run out of topics in the first cursor.
    return out;
  }

  // compare out to every cursor past the first in our list.
  ++current_cursor;
  for (; current_cursor != _cursors.cend(); ++current_cursor) {
    Topic cursor_min = (*current_cursor)->seek_to(out);
    if (cursor_min == out) {
      // this cursor points to out. get the next one (if there is any).
      Topic next_topic = first_cursor->next();
      return position(next_topic);
    }
  }
  // none of the contained cursors point to out.
  return out;
}
const Topic& DifferenceCursor::next() {
  /* 
    Increments the first cursor (from which all topics are selected) until the current position differs from the previous position (or the current position is zero)
  */
  Topic prev_position = position();

  std::vector<Cursor*>::const_iterator current_cursor = _cursors.cbegin();
  Cursor* first_cursor = *current_cursor;

  for (Topic current_position = first_cursor->next(); position().id() != 0 && position().id() != prev_position.id(); first_cursor->next()) {
  }
  
  return position();
}