import unittest

from src.proto_range import ProtoRange


class RangeTest(unittest.TestCase):
    def test_range_single_int(self):
        self.assertEqual(ProtoRange.match(None, "42").node.serialize(), "42")
        self.assertEqual(ProtoRange.match(None, "-1").node.serialize(), "-1")

    def test_range_invalid_non_ints(self):
        self.assertIsNone(ProtoRange.match(None, "42.5"))
        self.assertIsNone(ProtoRange.match(None, "a"))
        self.assertIsNone(ProtoRange.match(None, "-"))

    def test_range_int_range(self):
        self.assertEqual(ProtoRange.match(None, "1 to 1").node.serialize(), "1 to 1")
        self.assertEqual(ProtoRange.match(None, "1 to 7").node.serialize(), "1 to 7")
        self.assertEqual(
            ProtoRange.match(None, "-100 to -5").node.serialize(), "-100 to -5"
        )

    def test_range_invalid_range(self):
        with self.assertRaises(ValueError):
            ProtoRange.match(None, "8 to 2")

        with self.assertRaises(ValueError):
            ProtoRange.match(None, "3 to 0")

        with self.assertRaises(ValueError):
            ProtoRange.match(None, "1 to -1")

    def test_range_invalid_range_non_int(self):
        with self.assertRaises(ValueError):
            ProtoRange.match(None, "1 to c")

        with self.assertRaises(ValueError):
            ProtoRange.match(None, "1 to -bc3")

    def test_range_max(self):
        self.assertEqual(
            ProtoRange.match(None, "7 to max").node.serialize(), "7 to max"
        )


if __name__ == "__main__":
    unittest.main()
