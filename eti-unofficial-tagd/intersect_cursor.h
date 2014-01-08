#ifndef INTERSECT_CURSOR_H
#define INTERSECT_CURSOR_H

#include "meta_cursor.h"

class IntersectCursor : public MetaCursor {
  protected:
    virtual const Topic& position(Topic& out) const;
  public:
    IntersectCursor(std::vector<BaseCursor*>& cursors);
    virtual const Topic& position() const;
    virtual const Topic& next();
};
#endif