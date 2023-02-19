import unittest

from src.proto_bool import ProtoBool


class BoolTest(unittest.TestCase):
    def test_true(self):
        self.assertEqual(ProtoBool.match(None, "true").node.value, True)
        self.assertIsNone(ProtoBool.match(None, "True"))
        self.assertIsNone(ProtoBool.match(None, "truee"))
        self.assertIsNone(ProtoBool.match(None, "true_true"))
        self.assertIsNone(ProtoBool.match(None, "true.false"))

    def test_false(self):
        self.assertEqual(ProtoBool.match(None, "false").node.value, False)
        self.assertIsNone(ProtoBool.match(None, "False"))
        self.assertIsNone(ProtoBool.match(None, "falsee"))
        self.assertIsNone(ProtoBool.match(None, "false_false"))
        self.assertIsNone(ProtoBool.match(None, "false.true"))


if __name__ == "__main__":
    unittest.main()
