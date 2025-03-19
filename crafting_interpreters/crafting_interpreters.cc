#include <ctime>
#include <string>
#include <iostream>

class DoublyLinkedListNode {
    public:
        DoublyLinkedListNode* previous;
        DoublyLinkedListNode* next;
        std::string* value;

};

class DoublyLinkedList {
    public:
        DoublyLinkedListNode* head;
        DoublyLinkedListNode* insert(std::string* v);
        DoublyLinkedListNode* find(std::string* v);
        DoublyLinkedListNode* remove(std::string* v);

};

DoublyLinkedListNode* DoublyLinkedList::insert(std::string* v) {
    return nullptr;
}
DoublyLinkedListNode* DoublyLinkedList::find(std::string* v) {
    return nullptr;
}
DoublyLinkedListNode* DoublyLinkedList::remove(std::string* v) {
    return nullptr;
}

std::string get_greet(const std::string& who) {
  return "Hello " + who;
}

void print_localtime() {
  std::time_t result = std::time(nullptr);
  std::cout << std::asctime(std::localtime(&result));
}

int main(int argc, char** argv) {
  std::string who = "world";
  if (argc > 1) {
    who = argv[1];
  }
  std::cout << get_greet(who) << std::endl;
  print_localtime();
  return 0;
}
