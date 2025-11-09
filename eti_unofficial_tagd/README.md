eti_unofficial_tagd
===================
tagd is a C++ service on ETI to provide an interface by which topic lists can be retrieved for arbitrary tag queries. For example, given a query string like "[LUE]-[NWS]+[Starcraft]", tagd responds with a list of topic IDs corresponding to topics that are tagged with LUE and Starcraft, but not NWS.

This repository is __not__ the official tagd on ETI; it's purely my own attempt at replicating ETI's official implementation, [as described by Sabretooth and LG here](https://gist.github.com/shaldengeki/8125720).

Usage
========
To build and then use tagd:
- Do `bazel run //eti_unofficial_tagd:main -- --help` to see a list of command-line options.

A small client is included. To build and run:
- Do `bazel run //eti_unofficial_tagd:client -- --help`
