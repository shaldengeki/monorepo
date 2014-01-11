/*
  cursor.h
  Provides cursor interface for scrolling-forward of topics.
*/

#ifndef CURSOR_H
#define CURSOR_H

#include "topic.h"

/* Base cursor interface. */
class Cursor {
  public:
    virtual ~Cursor() {}
    virtual const Topic& reset() = 0;
    virtual const Topic& next() = 0;
    virtual const Topic& seek_to(Topic& ref) = 0;
    virtual const Topic& position() const = 0;
};

#endif