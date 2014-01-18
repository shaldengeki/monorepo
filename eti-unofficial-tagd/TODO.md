TODO
====
- std::set::lower_bound in tag_cursor
- tag-query parsing and conversion to cursor graph
  - bugfix: tagd::parse not returning correct results for union, intersect of two tags
- bugfix: cursors sometimes return non-zero results after returning zero (indicating end-of-cursor)
- networking code
- large-tag optimizations (if >= half of topics)
- result total-topic estimates