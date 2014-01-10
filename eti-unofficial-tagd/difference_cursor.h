#ifndef DIFFERENCE_CURSOR_H
#define DIFFERENCE_CURSOR_H

#include "meta_cursor.h"

class DifferenceCursor : public MetaCursor {
  protected:
    virtual const Topic& position(Topic& out) const;
  public:
    DifferenceCursor(std::vector<Cursor*>& cursors);
    virtual const Topic& position() const;
    virtual const Topic& next();
};
#endif