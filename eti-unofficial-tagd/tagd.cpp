/*
  tagd.cpp
  @author shaldengeki
  Loads all ETI tag data into memory and provides a service to search for topics.
  For up-to-date help: tagd --help
*/

#include <cstdlib>
#include <iostream>
#include <string>
#include <sstream>
#include <limits>
#include <map>
#include <ctime>
#include <algorithm> 

#include <mysql++.h>
using namespace mysqlpp;
using namespace std;

#include <boost/program_options.hpp>
namespace options = boost::program_options;
using namespace std;

