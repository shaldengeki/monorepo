# type: ignore

import unittest
from textwrap import dedent

from py_proto.proto_package import (
    ProtoPackage,
    ProtoPackageAdded,
    ProtoPackageChanged,
    ProtoPackageRemoved,
)


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
            ProtoPackage.match("package foo.bar;").node.serialize(),
            "package foo.bar;",
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

    def test_diff_same_package_returns_empty(self):
        pp1 = ProtoPackage("my.awesome.package")
        pp2 = ProtoPackage("my.awesome.package")
        self.assertEqual(ProtoPackage.diff(pp1, pp2), [])

    def test_diff_different_package_returns_package_diff(self):
        pp1 = ProtoPackage("my.awesome.package")
        pp2 = ProtoPackage("my.other.awesome.package")
        self.assertEqual(
            ProtoPackage.diff(pp1, pp2),
            [
                ProtoPackageChanged(
                    ProtoPackage("my.awesome.package"),
                    ProtoPackage("my.other.awesome.package"),
                )
            ],
        )

    def test_diff_package_added(self):
        pp1 = None
        pp2 = ProtoPackage("my.new.package")
        self.assertEqual(
            [
                ProtoPackageAdded(ProtoPackage("my.new.package")),
            ],
            ProtoPackage.diff(pp1, pp2),
        )

    def test_diff_package_removed(self):
        pp1 = ProtoPackage("my.old.package")
        pp2 = None
        self.assertEqual(
            [
                ProtoPackageRemoved(ProtoPackage("my.old.package")),
            ],
            ProtoPackage.diff(pp1, pp2),
        )


if __name__ == "__main__":
    unittest.main()
