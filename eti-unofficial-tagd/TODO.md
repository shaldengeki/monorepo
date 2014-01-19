TODO
====
- std::set::lower_bound in tag_cursor
- bugfix: cursor graphs not returning correct topic sets (see: 5&99)
- reverse order of std::set so that topics are listed last-post-time descending, topic-id descending
- networking code
  - bugfix: std::invalid_argument on stoul within tagd::parse (caused by empty characters at end of string?)
- large-tag optimizations (if >= half of topics)
- result total-topic estimates