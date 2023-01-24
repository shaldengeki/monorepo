import unittest
from textwrap import dedent

from src.proto_reserved import ProtoReserved


class ReservedTest(unittest.TestCase):
    def test_reserved_single_int(self):
        self.assertEqual(
            ProtoReserved.match("reserved 21;").node.serialize(), "reserved 21;"
        )
        self.assertEqual(
            ProtoReserved.match("reserved -1;").node.serialize(), "reserved -1;"
        )

    def test_reserved_multiple_ints(self):
        self.assertEqual(
            ProtoReserved.match("reserved 1, 5, 2, 42;").node.serialize(),
            "reserved 1, 5, 2, 42;",
        )

    def test_reserved_range_max(self):
        self.assertEqual(
            ProtoReserved.match("reserved 8 to max;").node.serialize(),
            "reserved 8 to max;",
        )

    def test_reserved_single_string_field(self):
        self.assertEqual(
            ProtoReserved.match("reserved 'foo';").node.serialize(), "reserved 'foo';"
        )
        self.assertEqual(
            ProtoReserved.match('reserved "foo";').node.serialize(), 'reserved "foo";'
        )

    def test_reserved_multiple_string_fields(self):
        self.assertEqual(
            ProtoReserved.match("reserved 'foo', 'bar';").node.serialize(),
            "reserved 'foo', 'bar';",
        )
        self.assertEqual(
            ProtoReserved.match('reserved "foo", "bar", "baz";').node.serialize(),
            'reserved "foo", "bar", "baz";',
        )

    def test_reserved_cannot_have_ints_and_strings(self):
        with self.assertRaises(ValueError):
            ProtoReserved.match("reserved 1, 'foo';")


if __name__ == "__main__":
    unittest.main()
