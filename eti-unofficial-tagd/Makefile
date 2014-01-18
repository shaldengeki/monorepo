CXX := g++
CXXFLAGS := -I/usr/include/mysql -I/usr/include/mysql++ -std=c++11 -Wfatal-errors
LDFLAGS := -L/usr/lib -lmysqlpp -lboost_program_options -lnsl -lz -lm
EXECUTABLE := tagd
OBJECTS := tag.o tag_cursor.o meta_cursor.o union_cursor.o intersect_cursor.o difference_cursor.o tagd.o main.o

all: $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $(EXECUTABLE) $(OBJECTS)

clean:
	rm *.o