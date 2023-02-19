import unittest
from textwrap import dedent

from src.proto_package import (
    ProtoPackage,
    ProtoPackageAdded,
    ProtoPackageChanged,
    ProtoPackageRemoved,
)


class PackageTest(unittest.TestCase):
    def test_correct_package(self):
        self.assertEqual(ProtoPackage.match(None, "package foo;").node.package, "foo")
        self.assertEqual(
            ProtoPackage.match(None, "package foo.bar;").node.package, "foo.bar"
        )
        self.assertEqual(
            ProtoPackage.match(None, "package foo.bar.baz;").node.package, "foo.bar.baz"
        )

    def test_package_serialize(self):
        self.assertEqual(
            ProtoPackage.match(None, "package foo;").node.serialize(), "package foo;"
        )
        self.assertEqual(
            ProtoPackage.match(None, "package foo.bar;").node.serialize(),
            "package foo.bar;",
        )
        self.assertEqual(
            ProtoPackage.match(None, "package foo.bar.baz;").node.serialize(),
            "package foo.bar.baz;",
        )

    def test_package_malformed(self):
        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package;")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package ")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package ;")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "packagefoo")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package foo.")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "packagefoo.")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package foo.;")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "package foo.bar")

        with self.assertRaises(ValueError):
            ProtoPackage.match(None, "packagefoo.bar;")

    def test_diff_same_package_returns_empty(self):
        pp1 = ProtoPackage(None, "my.awesome.package")
        pp2 = ProtoPackage(None, "my.awesome.package")
        self.assertEqual(ProtoPackage.diff(pp1, pp2), [])

    def test_diff_different_package_returns_package_diff(self):
        pp1 = ProtoPackage(None, "my.awesome.package")
        pp2 = ProtoPackage(None, "my.other.awesome.package")
        self.assertEqual(
            ProtoPackage.diff(pp1, pp2),
            [
                ProtoPackageChanged(
                    ProtoPackage(None, "my.awesome.package"),
                    ProtoPackage(None, "my.other.awesome.package"),
                )
            ],
        )

    def test_diff_package_added(self):
        pp1 = ProtoPackage(None, "my.new.package")
        pp2 = None
        self.assertEqual(
            ProtoPackage.diff(pp1, pp2),
            [
                ProtoPackageAdded(ProtoPackage(None, "my.new.package")),
            ],
        )

    def test_diff_package_removed(self):
        pp1 = None
        pp2 = ProtoPackage(None, "my.old.package")
        self.assertEqual(
            ProtoPackage.diff(pp1, pp2),
            [
                ProtoPackageRemoved(ProtoPackage(None, "my.old.package")),
            ],
        )


if __name__ == "__main__":
    unittest.main()
