import unittest

from src.proto_bool import ProtoBool


class BoolTest(unittest.TestCase):
    def test_true(self):
        self.assertEqual(ProtoBool.match("true").node.value, True)
        self.assertIsNone(ProtoBool.match("True"))
        self.assertIsNone(ProtoBool.match("truee"))
        self.assertIsNone(ProtoBool.match("true_true"))
        self.assertIsNone(ProtoBool.match("true.false"))

    def test_false(self):
        self.assertEqual(ProtoBool.match("false").node.value, False)
        self.assertIsNone(ProtoBool.match("False"))
        self.assertIsNone(ProtoBool.match("falsee"))
        self.assertIsNone(ProtoBool.match("false_false"))
        self.assertIsNone(ProtoBool.match("false.true"))


if __name__ == "__main__":
    unittest.main()
