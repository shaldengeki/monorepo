/*
  union_cursor.h
  Provides interface for a cursor that performs set union on a set of cursors.
  Specifically, does the equivalent of CURSOR_1 U CURSOR_2 U CURSOR_3 U ... U CURSOR_N
*/

#ifndef UNION_CURSOR_H
#define UNION_CURSOR_H

#include "meta_cursor.hpp"

class UnionCursor : public MetaCursor {
  protected:
    const Topic& position(Topic& out) const;
  public:
    UnionCursor(std::vector<Cursor*>& cursors);
    const Topic& position() const;
    const Topic& next();
};

#endif