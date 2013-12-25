eti-unofficial-tagd
===================
tagd is a C++ service on ETI to provide an interface by which topic lists can be retrieved for arbitrary tag queries. For example, given a query string like "[LUE]-[NWS]+[Starcraft]", tagd responds with a list of topic IDs corresponding to topics that are tagged with LUE and Starcraft, but not NWS.

This repository is __not__ the official tagd on ETI; it's purely my own attempt at replicating ETI's official implementation, [as described by Sabretooth and LG here](https://gist.github.com/shaldengeki/8125720).

Dependencies
============
tagd requires [mysql++](http://tangentsoft.net/mysql++/) to query a database and load tag-topic information upon start, and [boost program-options](http://www.boost.org/doc/libs/1_55_0/doc/html/program_options.html) to provide command-line options.