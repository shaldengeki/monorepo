#ifndef META_CURSOR_H
#define META_CURSOR_H

#include "base_cursor.h"
#include <vector>

/* Metacursor classes for groups of cursors. */
class MetaCursor : public BaseCursor {
  protected:
    std::vector<BaseCursor*> _cursors;
    virtual const Topic& position(Topic& out) const = 0;
  public:
    MetaCursor(std::vector<BaseCursor*>& cursors);
    virtual ~MetaCursor() {}
    virtual const Topic& reset();
    virtual const Topic& position() const;
    virtual const Topic& seek_to(Topic& ref);
};
#endif