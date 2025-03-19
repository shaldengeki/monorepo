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
