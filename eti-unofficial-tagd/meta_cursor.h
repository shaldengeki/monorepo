#ifndef META_CURSOR_H
#define META_CURSOR_H

#include "cursor.h"
#include <vector>

/* Metacursor classes for groups of cursors. */
class MetaCursor : public Cursor {
  protected:
    std::vector<Cursor*> _cursors;
    virtual const Topic& position(Topic& out) const = 0;
  public:
    MetaCursor(std::vector<Cursor*>& cursors);
    virtual ~MetaCursor() {}
    virtual const Topic& reset();
    virtual const Topic& position() const;
    virtual const Topic& seek_to(Topic& ref);
};
#endif