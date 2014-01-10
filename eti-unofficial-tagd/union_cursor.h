#ifndef UNION_CURSOR_H
#define UNION_CURSOR_H

#include "meta_cursor.h"

class UnionCursor : public MetaCursor {
  protected:
    virtual const Topic& position(Topic& out) const;
  public:
    UnionCursor(std::vector<Cursor*>& cursors);
    virtual const Topic& position() const;
    virtual const Topic& next();
};

#endif