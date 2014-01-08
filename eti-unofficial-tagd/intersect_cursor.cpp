#include "intersect_cursor.h"

IntersectCursor::IntersectCursor(std::vector<BaseCursor*>& cursors) : MetaCursor::MetaCursor(cursors) {
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
  if (out.id() == 0) {
    // We've run out of topics in at least one cursor.
    return out;
  }
  for (std::vector<BaseCursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    Topic tag_min = (*current_cursor)->seek_to(out);
    if (tag_min > out) {
      // this tag points past out.
      return position(tag_min);
    }
  }
  // all the contained tags point to out.
  return out;
}
const Topic& IntersectCursor::next() {
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