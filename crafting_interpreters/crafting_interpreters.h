#include <string>

#ifndef CRAFTING_INTERPETERS_PUBLIC_CRAFTING_INTERPETERS_H_
#define CRAFTING_INTERPETERS_PUBLIC_CRAFTING_INTERPETERS_H_

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

#endif  // CRAFTING_INTERPETERS_PUBLIC_CRAFTING_INTERPETERS_H_
