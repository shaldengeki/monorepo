#include <gtest/gtest.h>
#include <string>

#include "crafting_interpreters.h"

TEST(Static, ProperlyLinked) {
    DoublyLinkedList* x = new DoublyLinkedList();
    std::string* val = new std::string("hello");
    EXPECT_EQ(x->insert(val), nullptr);
}
