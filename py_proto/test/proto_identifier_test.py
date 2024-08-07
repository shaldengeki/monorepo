# type: ignore

import unittest
from textwrap import dedent

from py_proto.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)


class IdentifierTest(unittest.TestCase):
    def test_ident(self):
        self.assertEqual(ProtoIdentifier.match("a").node.identifier, "a")
        self.assertEqual(ProtoIdentifier.match("a0").node.identifier, "a0")
        self.assertEqual(ProtoIdentifier.match("a_").node.identifier, "a_")
        self.assertEqual(ProtoIdentifier.match("aa").node.identifier, "aa")
        self.assertEqual(ProtoIdentifier.match("ab").node.identifier, "ab")
        self.assertEqual(ProtoIdentifier.match("a0b_f_aj").node.identifier, "a0b_f_aj")

    def test_ident_no_leading_letter(self):
        self.assertIsNone(ProtoIdentifier.match("0"))
        self.assertIsNone(ProtoIdentifier.match("0abc_ab"))
        self.assertIsNone(ProtoIdentifier.match("0_ab_0a_a0"))
        self.assertIsNone(ProtoIdentifier.match(" "))
        self.assertIsNone(ProtoIdentifier.match(" abc"))
        self.assertIsNone(ProtoIdentifier.match("\nabc"))
        self.assertIsNone(ProtoIdentifier.match("\n abc"))
        self.assertIsNone(ProtoIdentifier.match("\tabc"))
        self.assertIsNone(ProtoIdentifier.match("\n\tabc"))
        self.assertIsNone(ProtoIdentifier.match("\t\nabc"))
        self.assertIsNone(ProtoIdentifier.match("\t\n abc"))
        self.assertIsNone(ProtoIdentifier.match(".a"))
        self.assertIsNone(ProtoIdentifier.match(" .a"))
        self.assertIsNone(ProtoIdentifier.match("."))
        self.assertIsNone(ProtoIdentifier.match(".0"))

    def test_full_ident(self):
        self.assertEqual(ProtoFullIdentifier.match("a").node.identifier, "a")
        self.assertEqual(ProtoFullIdentifier.match("a.bar").node.identifier, "a.bar")
        self.assertEqual(
            ProtoFullIdentifier.match("a.bar.baz").node.identifier, "a.bar.baz"
        )
        self.assertEqual(
            ProtoFullIdentifier.match("a.bar.b0").node.identifier, "a.bar.b0"
        )
        self.assertEqual(
            ProtoFullIdentifier.match("a.bar.b0.c_2a").node.identifier,
            "a.bar.b0.c_2a",
        )

    def test_full_ident_invalid_periods(self):
        with self.assertRaises(ValueError):
            ProtoFullIdentifier.match("a.")

        with self.assertRaises(ValueError):
            ProtoFullIdentifier.match("a.bar.")

        with self.assertRaises(ValueError):
            ProtoFullIdentifier.match("a..")

    def test_message_type(self):
        self.assertEqual(ProtoEnumOrMessageIdentifier.match("a").node.identifier, "a")
        self.assertEqual(ProtoEnumOrMessageIdentifier.match(".a").node.identifier, ".a")
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(".a.bar").node.identifier, ".a.bar"
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match("a.bar").node.identifier, "a.bar"
        )

    def test_identifier_serialize(self):
        self.assertEqual(ProtoIdentifier.match("a").node.serialize(), "a")
        self.assertEqual(ProtoIdentifier.match("a0").node.serialize(), "a0")
        self.assertEqual(
            ProtoIdentifier.match("a_").node.serialize(),
            "a_",
        )
        self.assertEqual(
            ProtoIdentifier.match("a0_foo_ba0_0baz").node.serialize(),
            "a0_foo_ba0_0baz",
        )
        self.assertEqual(
            ProtoFullIdentifier.match("a.bar").node.serialize(),
            "a.bar",
        )
        self.assertEqual(
            ProtoFullIdentifier.match("a.bar_baz.foo0").node.serialize(),
            "a.bar_baz.foo0",
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(".a").node.serialize(),
            ".a",
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(".a.bar0_baz.foo").node.serialize(),
            ".a.bar0_baz.foo",
        )


if __name__ == "__main__":
    unittest.main()
