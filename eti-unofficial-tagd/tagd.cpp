/*
  tagd.cpp
  Provides implementation for a network service that compiles tag query-strings into a graph of tag and set cursors
  Then returns specified topics from that graph.
*/

#include "tagd.h"
#include "tag.h"
#include "cursor.h"
#include "tag_cursor.h"
#include "union_cursor.h"
#include "intersect_cursor.h"
#include "difference_cursor.h"

#include <locale>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

TagD::TagD() {

}

void TagD::set(Tag& tag) {
  _tags[tag.id()] = &tag;
}

Tag& TagD::get(unsigned long tag_id) {
  /*
  Returns a tag stored under tag_id.
  Throws out_of_range if not found.
  */
  std::map<unsigned long, Tag*>::iterator tag_iter = _tags.find(tag_id);
  if (tag_iter == _tags.end()) {
    throw std::out_of_range("no such tag found");
  }
  return *(tag_iter->second);
}

unsigned int TagD::size() {
  return _tags.size();
}

Cursor& TagD::parse(std::string& tag_query) {
  /*
  Parses a string tag_query into a cursor graph.
  Returns the resultant cursor.
  */
  std::vector<Cursor*> union_tags;
  std::vector<Cursor*> difference_tags;
  std::vector<Cursor*> intersect_tags;

  // pick up first tag if it's not a negative.
  std::string first_char {tag_query[0]};

  if (std::isdigit(tag_query[0])) {
    union_tags.push_back(new TagCursor(get(std::stoul(first_char))));
  }

  for (std::string::iterator operator_it = tag_query.begin(); operator_it < tag_query.end(); ++operator_it) {
    // scroll forwards till we hit an operator.
    if (std::isdigit(*operator_it)) {
      continue;
    }
    // operator_it points to an operator.
    // scroll forwards till we hit an operator to fetch the tag id.
    std::string::iterator id_it;
    for (id_it = operator_it+1; id_it < tag_query.end() ; ++id_it) {
      if (!std::isdigit(*id_it)) {
        break;
      }
    }
    unsigned long tag_id = std::stoul(std::string(operator_it + 1, id_it));

    if (*operator_it == '+') {
      union_tags.push_back(new TagCursor(get(tag_id)));
    } else if (*operator_it == '-') {
      difference_tags.push_back(new TagCursor(get(tag_id)));
    } else if (*operator_it == '&') {
      intersect_tags.push_back(new TagCursor(get(tag_id)));
    }
  }

  // create metacursors.
  Cursor* union_result;
  if (union_tags.size() == 0) {
    union_result = new UnionCursor(union_tags);
    return *union_result;
  } else if (union_tags.size() == 1) {
    union_result = union_tags[0];
  } else {
    union_result = new UnionCursor(union_tags);
  }

  std::vector<Cursor*> union_and_diff_cursors {union_result};
  Cursor* diff_result;
  if (difference_tags.size() > 0) {
    for (std::vector<Cursor*>::iterator diff_iter = difference_tags.begin(); diff_iter != difference_tags.end(); ++diff_iter) {
      union_and_diff_cursors.push_back(*diff_iter);
    }
    diff_result = new DifferenceCursor(union_and_diff_cursors);
  } else {
    diff_result = union_result;
  }

  std::vector<Cursor*> diff_and_intersect_cursors {diff_result};
  Cursor* inter_result;
  if (intersect_tags.size() > 0) {
    for (std::vector<Cursor*>::iterator intersect_iter = intersect_tags.begin(); intersect_iter != intersect_tags.end(); ++intersect_iter) {
      diff_and_intersect_cursors.push_back(*intersect_iter);
    }
    inter_result = new IntersectCursor(diff_and_intersect_cursors);
  } else {
    inter_result = diff_result;
  }

  return *inter_result;
}