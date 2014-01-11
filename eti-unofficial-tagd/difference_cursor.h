/*
  difference_cursor.h
  Provides interface for a cursor that performs set difference on a set of cursors.
  Specifically, does the equivalent of CURSOR_1 - CURSOR_2 - CURSOR_3 - ... - CURSOR_N
*/

#ifndef DIFFERENCE_CURSOR_H
#define DIFFERENCE_CURSOR_H

#include "meta_cursor.h"

class DifferenceCursor : public MetaCursor {
  protected:
    const Topic& position(Topic& out) const;
  public:
    DifferenceCursor(std::vector<Cursor*>& cursors);
    const Topic& position() const;
    const Topic& next();
};
#endif