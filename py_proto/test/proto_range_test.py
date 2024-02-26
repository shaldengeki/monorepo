import unittest

from src.proto_range import ProtoRange


class RangeTest(unittest.TestCase):
    def test_range_single_int(self):
        self.assertEqual(ProtoRange.match("42").node.serialize(), "42")
        self.assertEqual(ProtoRange.match("-1").node.serialize(), "-1")

    def test_range_invalid_non_ints(self):
        self.assertIsNone(ProtoRange.match("42.5"))
        self.assertIsNone(ProtoRange.match("a"))
        self.assertIsNone(ProtoRange.match("-"))

    def test_range_int_range(self):
        self.assertEqual(ProtoRange.match("1 to 1").node.serialize(), "1 to 1")
        self.assertEqual(ProtoRange.match("1 to 7").node.serialize(), "1 to 7")
        self.assertEqual(ProtoRange.match("-100 to -5").node.serialize(), "-100 to -5")

    def test_range_invalid_range(self):
        with self.assertRaises(ValueError):
            ProtoRange.match("8 to 2")

        with self.assertRaises(ValueError):
            ProtoRange.match("3 to 0")

        with self.assertRaises(ValueError):
            ProtoRange.match("1 to -1")

    def test_range_invalid_range_non_int(self):
        with self.assertRaises(ValueError):
            ProtoRange.match("1 to c")

        with self.assertRaises(ValueError):
            ProtoRange.match("1 to -bc3")

    def test_range_max(self):
        self.assertEqual(ProtoRange.match("7 to max").node.serialize(), "7 to max")


if __name__ == "__main__":
    unittest.main()
