#include "meta_cursor.h"

MetaCursor::MetaCursor(std::vector<BaseCursor*>& cursors) {
  _cursors = cursors;
}