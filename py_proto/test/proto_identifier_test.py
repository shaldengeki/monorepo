import unittest
from textwrap import dedent

from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)


class IdentifierTest(unittest.TestCase):
    def test_ident(self):
        self.assertEqual(ProtoIdentifier.match(None, "a").node.identifier, "a")
        self.assertEqual(ProtoIdentifier.match(None, "a0").node.identifier, "a0")
        self.assertEqual(ProtoIdentifier.match(None, "a_").node.identifier, "a_")
        self.assertEqual(ProtoIdentifier.match(None, "aa").node.identifier, "aa")
        self.assertEqual(ProtoIdentifier.match(None, "ab").node.identifier, "ab")
        self.assertEqual(
            ProtoIdentifier.match(None, "a0b_f_aj").node.identifier, "a0b_f_aj"
        )

    def test_ident_no_leading_letter(self):
        self.assertIsNone(ProtoIdentifier.match(None, "0"))
        self.assertIsNone(ProtoIdentifier.match(None, "0abc_ab"))
        self.assertIsNone(ProtoIdentifier.match(None, "0_ab_0a_a0"))
        self.assertIsNone(ProtoIdentifier.match(None, " "))
        self.assertIsNone(ProtoIdentifier.match(None, " abc"))
        self.assertIsNone(ProtoIdentifier.match(None, "\nabc"))
        self.assertIsNone(ProtoIdentifier.match(None, "\n abc"))
        self.assertIsNone(ProtoIdentifier.match(None, "\tabc"))
        self.assertIsNone(ProtoIdentifier.match(None, "\n\tabc"))
        self.assertIsNone(ProtoIdentifier.match(None, "\t\nabc"))
        self.assertIsNone(ProtoIdentifier.match(None, "\t\n abc"))
        self.assertIsNone(ProtoIdentifier.match(None, ".a"))
        self.assertIsNone(ProtoIdentifier.match(None, " .a"))
        self.assertIsNone(ProtoIdentifier.match(None, "."))
        self.assertIsNone(ProtoIdentifier.match(None, ".0"))

    def test_full_ident(self):
        self.assertEqual(ProtoFullIdentifier.match(None, "a").node.identifier, "a")
        self.assertEqual(
            ProtoFullIdentifier.match(None, "a.bar").node.identifier, "a.bar"
        )
        self.assertEqual(
            ProtoFullIdentifier.match(None, "a.bar.baz").node.identifier, "a.bar.baz"
        )
        self.assertEqual(
            ProtoFullIdentifier.match(None, "a.bar.b0").node.identifier, "a.bar.b0"
        )
        self.assertEqual(
            ProtoFullIdentifier.match(None, "a.bar.b0.c_2a").node.identifier,
            "a.bar.b0.c_2a",
        )

    def test_full_ident_invalid_periods(self):
        with self.assertRaises(ValueError):
            ProtoFullIdentifier.match(None, "a.")

        with self.assertRaises(ValueError):
            ProtoFullIdentifier.match(None, "a.bar.")

        with self.assertRaises(ValueError):
            ProtoFullIdentifier.match(None, "a..")

    def test_message_type(self):
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(None, "a").node.identifier, "a"
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(None, ".a").node.identifier, ".a"
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(None, ".a.bar").node.identifier, ".a.bar"
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(None, "a.bar").node.identifier, "a.bar"
        )

    def test_identifier_serialize(self):
        self.assertEqual(ProtoIdentifier.match(None, "a").node.serialize(), "a")
        self.assertEqual(ProtoIdentifier.match(None, "a0").node.serialize(), "a0")
        self.assertEqual(
            ProtoIdentifier.match(None, "a_").node.serialize(),
            "a_",
        )
        self.assertEqual(
            ProtoIdentifier.match(None, "a0_foo_ba0_0baz").node.serialize(),
            "a0_foo_ba0_0baz",
        )
        self.assertEqual(
            ProtoFullIdentifier.match(None, "a.bar").node.serialize(),
            "a.bar",
        )
        self.assertEqual(
            ProtoFullIdentifier.match(None, "a.bar_baz.foo0").node.serialize(),
            "a.bar_baz.foo0",
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(None, ".a").node.serialize(),
            ".a",
        )
        self.assertEqual(
            ProtoEnumOrMessageIdentifier.match(
                None, ".a.bar0_baz.foo"
            ).node.serialize(),
            ".a.bar0_baz.foo",
        )


if __name__ == "__main__":
    unittest.main()
