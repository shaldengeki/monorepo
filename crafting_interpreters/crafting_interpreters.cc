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

// Create a new node containing the given string, and append it to the end.
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

// Return the node in the list with the same value as the given string, or nullptr if it wasn't found.
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

// Remove the node in the list with the same value as the given string.
// Return the removed node, or nullptr if it wasn't found.
DoublyLinkedListNode* DoublyLinkedList::remove(std::string* v) {
    DoublyLinkedListNode* n = this->find(v);
    if (n == nullptr) {
        return nullptr;
    }

    if (n->previous != nullptr) {
        n->previous->next = n->next;
    } else {
        this->head = n->next;
    }
    if (n->next != nullptr) {
        n->next->previous = n->previous;
    } else {
        this->tail = n->previous;
    }

    return n;
}
