#ifndef BASE_CURSOR_H
#define BASE_CURSOR_H

#include "topic.h"

/* Base cursor interface. */
class BaseCursor {
  public:
    virtual ~BaseCursor() {}
    virtual const Topic& reset() = 0;
    virtual const Topic& next() = 0;
    virtual const Topic& seek_to(Topic& ref) = 0;
    virtual const Topic& position() const = 0;
};

#endif