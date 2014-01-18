/*
  tag_cursor.h
  Provides tag-cursor interface for reading the topics in a tag.
*/

#ifndef TAG_CURSOR_H
#define TAG_CURSOR_H

#include "cursor.h"
#include "tag.h"

/* Cursor for single tags. */
class TagCursor : public Cursor {
  private:
    TopicList::iterator _position;
    Tag* _tag;
  public:
    TagCursor(Tag& tag);
    ~TagCursor() {}
    virtual const Topic& reset();
    virtual const Topic& position() const;
    virtual const Topic& next();
    virtual const Topic& seek_to(Topic& ref);
};

#endif