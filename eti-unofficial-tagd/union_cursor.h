#ifndef UNION_CURSOR_H
#define UNION_CURSOR_H

#include "meta_cursor.h"

class UnionCursor : public MetaCursor {
  protected:
    virtual const Topic& position(Topic& out) const;
  public:
    UnionCursor(std::vector<BaseCursor*>& cursors);
    virtual const Topic& position() const;
    virtual const Topic& reset();
    virtual const Topic& next();
    virtual const Topic& seek_to(Topic& ref);
};
#endif