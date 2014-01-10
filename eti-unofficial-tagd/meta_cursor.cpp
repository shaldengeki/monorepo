#include "meta_cursor.h"

MetaCursor::MetaCursor(std::vector<Cursor*>& cursors) {
  _cursors = cursors;
}
const Topic& MetaCursor::position() const {
  /*
    Returns the position of the metacursor, as implemented by position(Topic& ref).
  */
  std::vector<Cursor*>::const_iterator first_tag = _cursors.cbegin();
  Topic curr_position = (*first_tag)->position();

  return position(curr_position);
}
const Topic& MetaCursor::reset() {
  /*
    Resets all contained cursors and returns the current position.
  */
  for (std::vector<Cursor*>::const_iterator current_cursor = _cursors.cbegin(); current_cursor != _cursors.cend(); ++current_cursor) {
    (*current_cursor)->reset();
  }
  return position();
}
const Topic& MetaCursor::seek_to(Topic& ref) {
  /*
    Iterate through each cursor in this metacursor, fast-forwarding each cursor to (or just past) an input topic.
    Return the metacursor's position after having fast-forwarded.
  */
  for (std::vector<Cursor*>::iterator current_tag = _cursors.begin(); current_tag != _cursors.end(); ++current_tag) {
    (*current_tag)->seek_to(ref);
  }
  return position();
}
