#ifndef META_CURSOR_H
#define META_CURSOR_H

#include "base_cursor.h"
#include <vector>

/* Metacursor classes for groups of tags. */
class MetaCursor : public BaseCursor {
  protected:
    std::vector<BaseCursor*> _cursors;
  public:
    MetaCursor(std::vector<BaseCursor*>& cursors);
    virtual ~MetaCursor() {}
};
#endif