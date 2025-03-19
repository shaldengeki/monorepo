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
        DoublyLinkedListNode* tail;
        DoublyLinkedListNode* insert(std::string* v);
        DoublyLinkedListNode* find(std::string* v);
        DoublyLinkedListNode* remove(std::string* v);

};

DoublyLinkedListNode* DoublyLinkedList::insert(std::string* v) {
    DoublyLinkedListNode* n = new DoublyLinkedListNode();
    n->value = v;
    if (this->tail == nullptr) {
        this->head = n;
        this->tail = n;
    } else {
        this->tail->next = n;
        n->previous = this->tail->next;
        this->tail = n;
    }

    return n;
}
DoublyLinkedListNode* DoublyLinkedList::find(std::string* v) {
    if (this->head == nullptr) {
        return nullptr;
    }
    DoublyLinkedListNode* curr = this->head;
    while (curr != nullptr) {
        std::string currValue = *(curr->value);
        if (currValue == *v) {
            return curr;
        }
        curr = curr->next;
    }
    return nullptr;
}
DoublyLinkedListNode* DoublyLinkedList::remove(std::string* v) {
    return nullptr;
}
