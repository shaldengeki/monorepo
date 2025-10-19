/*
  tagd.cpp
  Provides implementation for a network service that compiles tag query-strings into a graph of tag and set cursors
  Then returns specified topics from that graph.
*/

#include "tagd.hpp"
#include "tag.hpp"
#include "topic.hpp"
#include "cursor.hpp"
#include "tag_cursor.hpp"
#include "union_cursor.hpp"
#include "intersect_cursor.hpp"
#include "difference_cursor.hpp"

#include <algorithm>
#include <functional>
#include <cctype>
#include <locale>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <iostream>
#include <cstddef>

// trim from start
static inline std::string &ltrim(std::string &s) {
  s.erase(s.begin(), std::find_if(s.begin(), s.end(), std::not1(std::ptr_fun<int, int>(std::isspace))));
  return s;
}

// trim from end
static inline std::string &rtrim(std::string &s) {
  s.erase(std::find_if(s.rbegin(), s.rend(), std::not1(std::ptr_fun<int, int>(std::isspace))).base(), s.end());
  return s;
}

// trim from both ends
static inline std::string &trim(std::string &s) {
  return ltrim(rtrim(s));
}

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

void TagD::insert_topic(unsigned long tag_id, Topic& topic) {
  /*
    Inserts a given topic into a tag.
  */
  get(tag_id).insert(topic);
}

unsigned int TagD::size() {
  return _tags.size();
}

void TagD::parse_insert(std::string& insert_query) {
  
}

Cursor& TagD::parse_query(std::string& tag_query) {
  /*
  Parses a string tag_query into a cursor graph.
  Returns the resultant cursor.
  */
  tag_query = trim(tag_query);

  std::vector<Cursor*> union_tags;
  std::vector<Cursor*> difference_tags;
  std::vector<Cursor*> intersect_tags;

  // pick up first tag if it's not an operator.
  std::string::iterator operator_it = tag_query.begin();
  if (std::isdigit(*operator_it)) {
    std::size_t first_op = tag_query.find_first_of("+-&");
    if (first_op == std::string::npos) {
      first_op = tag_query.length();
    }
    std::string first_tag = tag_query.substr(0, first_op);
    
    union_tags.push_back(new TagCursor(get(std::stoul(first_tag))));
    operator_it += first_op;
  }

  for (; operator_it < tag_query.end(); ++operator_it) {
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

    if (id_it >= tag_query.end()) {
      break;
    }
    std::string id_chunk = std::string(operator_it + 1, id_it);
    unsigned long tag_id = std::stoul(id_chunk);

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