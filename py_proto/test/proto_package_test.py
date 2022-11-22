import unittest
from textwrap import dedent

from src.proto_package import ProtoPackage


class PackageTest(unittest.TestCase):
    def test_correct_package(self):
        self.assertEqual(ProtoPackage.match("package foo;").node.package, "foo")
        self.assertEqual(ProtoPackage.match("package foo.bar;").node.package, "foo.bar")
        self.assertEqual(
            ProtoPackage.match("package foo.bar.baz;").node.package, "foo.bar.baz"
        )

    def test_package_serialize(self):
        self.assertEqual(
            ProtoPackage.match("package foo;").node.serialize(), "package foo;"
        )
        self.assertEqual(
            ProtoPackage.match("package foo.bar;").node.serialize(), "package foo.bar;"
        )
        self.assertEqual(
            ProtoPackage.match("package foo.bar.baz;").node.serialize(),
            "package foo.bar.baz;",
        )

    def test_package_malformed(self):
        with self.assertRaises(ValueError):
            ProtoPackage.match("package")

        with self.assertRaises(ValueError):
            ProtoPackage.match("package;")

        with self.assertRaises(ValueError):
            ProtoPackage.match("package ")

        with self.assertRaises(ValueError):
            ProtoPackage.match("package ;")

        with self.assertRaises(ValueError):
            ProtoPackage.match("packagefoo")

        with self.assertRaises(ValueError):
            ProtoPackage.match("package foo.")

        with self.assertRaises(ValueError):
            ProtoPackage.match("packagefoo.")

        with self.assertRaises(ValueError):
            ProtoPackage.match("package foo.;")

        with self.assertRaises(ValueError):
            ProtoPackage.match("package foo.bar")

        with self.assertRaises(ValueError):
            ProtoPackage.match("packagefoo.bar;")


if __name__ == "__main__":
    unittest.main()
