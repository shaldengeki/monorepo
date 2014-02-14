/*
  meta_cursor.h
  Provides interface for cursors that contain other cursors.
*/

#ifndef META_CURSOR_H
#define META_CURSOR_H

#include "cursor.hpp"
#include <vector>

/* Metacursor classes for groups of cursors. */
class MetaCursor : public Cursor {
  protected:
    std::vector<Cursor*> _cursors;
    virtual const Topic& position(Topic& out) const = 0;
  public:
    MetaCursor(std::vector<Cursor*>& cursors);
    virtual ~MetaCursor() {}
    const Topic& reset();
    const Topic& position() const;
    const Topic& seek_to(Topic& ref);
};
#endif