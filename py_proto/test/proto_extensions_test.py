import unittest

from src.proto_extensions import ProtoExtensions


class ExtensionsTest(unittest.TestCase):
    def test_extension_single_int(self):
        self.assertEqual(
            ProtoExtensions.match(None, "extensions 21;").node.serialize(),
            "extensions 21;",
        )
        self.assertEqual(
            ProtoExtensions.match(None, "extensions -1;").node.serialize(),
            "extensions -1;",
        )

    def test_extension_multiple_ints(self):
        self.assertEqual(
            ProtoExtensions.match(None, "extensions 1, 5, 2, 42;").node.serialize(),
            "extensions 1, 5, 2, 42;",
        )

    def test_extension_with_max(self):
        self.assertEqual(
            ProtoExtensions.match(None, "extensions 8 to max;").node.serialize(),
            "extensions 8 to max;",
        )

    def test_extension_cannot_have_strings(self):
        self.assertIsNone(ProtoExtensions.match(None, "extensions 1, 'foo';"))
        self.assertIsNone(ProtoExtensions.match(None, "extensions 'bar';"))


if __name__ == "__main__":
    unittest.main()
