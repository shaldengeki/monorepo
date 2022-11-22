from textwrap import dedent
import unittest
from src.parser import Parser, ParseError
from src.proto_package import ProtoPackage


class PackageTest(unittest.TestCase):
    def test_correct_package(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
            package foo;
        """
                )
            ).package,
            ProtoPackage("foo"),
        )
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
            package foo.bar;
        """
                )
            ).package,
            ProtoPackage("foo.bar"),
        )
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
            package foo.bar.baz;
        """
                )
            ).package,
            ProtoPackage("foo.bar.baz"),
        )

    def test_package_not_set(self):
        with self.assertRaises(StopIteration):
            Parser.loads("syntax = 'proto3';").package

    def test_package_malformed(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                package
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                package
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                packagefoo
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                package foo.
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                packagefoo.
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                package foo.;
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                package foo.bar
            """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                packagefoo.bar;
            """
                )
            )


if __name__ == "__main__":
    unittest.main()
