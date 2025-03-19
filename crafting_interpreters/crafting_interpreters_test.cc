#include <gtest/gtest.h>
#include <string>

#include "crafting_interpreters.h"

TEST(CraftingInterpretersTest, EmptyList) {
    DoublyLinkedList* x = new DoublyLinkedList();
    EXPECT_EQ(x->head, nullptr);

    std::string* v = new std::string("not found");
    EXPECT_EQ(x->find(v), nullptr);
    EXPECT_EQ(x->remove(v), nullptr);
}

TEST(CraftingInterpretersTest, InsertsNewValue) {
    DoublyLinkedList* x = new DoublyLinkedList();
    std::string* v = new std::string("new value");

    DoublyLinkedListNode* n = x->insert(v);
    EXPECT_NE(n, nullptr);
    EXPECT_EQ(x->head, n);
    EXPECT_EQ(n->value, v);

    DoublyLinkedListNode* n2 = x->insert(v);
    EXPECT_NE(n2, nullptr);
    EXPECT_NE(n2, n);
}

TEST(CraftingInterpretersTest, FindsExistingValue) {
    DoublyLinkedList* x = new DoublyLinkedList();
    std::string* v = new std::string("new value");
    std::string* v2 = new std::string("alt value");
    std::string* v3 = new std::string("not found value");

    DoublyLinkedListNode* n = x->insert(v);
    DoublyLinkedListNode* n2 = x->insert(v2);

    ASSERT_EQ(x->find(v), n);
    ASSERT_EQ(x->find(v2), n2);
    ASSERT_EQ(x->find(v3), nullptr);
}

TEST(CraftingInterpretersTest, RemovesExistingValues) {
    DoublyLinkedList* x = new DoublyLinkedList();
    std::string* v = new std::string("new value");
    std::string* v2 = new std::string("alt value");
    std::string* v3 = new std::string("not found value");

    DoublyLinkedListNode* n = x->insert(v);
    DoublyLinkedListNode* n2 = x->insert(v2);

    ASSERT_EQ(x->remove(v), n);
    ASSERT_EQ(x->remove(v2), n2);
    ASSERT_EQ(x->remove(v3), nullptr);
}
