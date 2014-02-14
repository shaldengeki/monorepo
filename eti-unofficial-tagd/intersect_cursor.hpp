/*
  intersect_cursor.h
  Provides interface for a cursor that performs set intersection on a set of cursors.
  Specifically, does the equivalent of CURSOR_1 ^ CURSOR_2 ^ CURSOR_3 ^ ... ^ CURSOR_N
*/

#ifndef INTERSECT_CURSOR_H
#define INTERSECT_CURSOR_H

#include "meta_cursor.hpp"

class IntersectCursor : public MetaCursor {
  protected:
    const Topic& position(Topic& out) const;
  public:
    IntersectCursor(std::vector<Cursor*>& cursors);
    const Topic& position() const;
    const Topic& next();
};
#endif