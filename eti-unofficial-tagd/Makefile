CXX := g++
CXXFLAGS := -I/usr/include/mysql -I/usr/include/mysql++ -std=c++0x -Wfatal-errors
LDFLAGS := -L/usr/lib -lmysqlpp -lboost_program_options -lnsl -lz -lm
EXECUTABLE := tagd
OBJECTS := tagd.o tag_cursor.o meta_cursor.o union_cursor.o

all: $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $(EXECUTABLE) $(OBJECTS)

tagd.o: tagd.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -c -o tagd.o tagd.cpp

tag_cursor.o: tag_cursor.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -c -o tag_cursor.o tag_cursor.cpp

meta_cursor.o: meta_cursor.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -c -o meta_cursor.o meta_cursor.cpp

union_cursor.o: union_cursor.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -c -o union_cursor.o union_cursor.cpp

clean:
	rm *.o