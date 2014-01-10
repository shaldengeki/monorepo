#ifndef INTERSECT_CURSOR_H
#define INTERSECT_CURSOR_H

#include "meta_cursor.h"

class IntersectCursor : public MetaCursor {
  protected:
    const Topic& position(Topic& out) const;
  public:
    IntersectCursor(std::vector<Cursor*>& cursors);
    const Topic& position() const;
    const Topic& next();
};
#endif