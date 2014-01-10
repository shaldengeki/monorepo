#ifndef UNION_CURSOR_H
#define UNION_CURSOR_H

#include "meta_cursor.h"

class UnionCursor : public MetaCursor {
  protected:
    const Topic& position(Topic& out) const;
  public:
    UnionCursor(std::vector<Cursor*>& cursors);
    const Topic& position() const;
    const Topic& next();
};

#endif