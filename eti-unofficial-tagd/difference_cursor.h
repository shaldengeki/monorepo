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