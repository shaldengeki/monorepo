import unittest
from textwrap import dedent

from src.proto_import import ProtoImport


class ImportTest(unittest.TestCase):
    def test_bare_import(self):
        double_quote_import = ProtoImport.match('import "foo.proto";')
        self.assertEqual(double_quote_import.node.path, "foo.proto")
        self.assertEqual(double_quote_import.node.weak, False)
        self.assertEqual(double_quote_import.node.public, False)
        self.assertEqual(double_quote_import.remaining_source, "")

        single_quote_import = ProtoImport.match("import 'foo.proto';")
        self.assertEqual(single_quote_import.node.path, "foo.proto")
        self.assertEqual(single_quote_import.node.weak, False)
        self.assertEqual(single_quote_import.node.public, False)
        self.assertEqual(single_quote_import.remaining_source, "")

    def test_import_missing_semicolon(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import "foo.proto"')

    def test_import_missing_starting_quote(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import foo.proto";')

        with self.assertRaises(ValueError):
            ProtoImport.match("import foo.proto';")

    def test_import_missing_ending_quote(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import "foo.proto;')

        with self.assertRaises(ValueError):
            ProtoImport.match("import 'foo.proto;")

    def test_weak_import(self):
        self.assertEqual(ProtoImport.match('import weak "foo.proto";').node.weak, True)
        self.assertEqual(ProtoImport.match("import weak 'foo.proto';").node.weak, True)

    def test_weak_typoed_import(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import weac "foo.proto";')

    def test_weak_mixed_imports(self):
        first_parsed_import = ProtoImport.match(
            dedent(
                """import "foo.proto";
            import weak "bar/baz.proto";
            import "bat.proto";"""
            )
        )
        self.assertEqual(first_parsed_import.node.path, "foo.proto")
        self.assertEqual(first_parsed_import.node.weak, False)

        second_parsed_import = ProtoImport.match(first_parsed_import.remaining_source)
        self.assertEqual(second_parsed_import.node.path, "bar/baz.proto")
        self.assertEqual(second_parsed_import.node.weak, True)

        third_parsed_import = ProtoImport.match(second_parsed_import.remaining_source)
        self.assertEqual(third_parsed_import.node.path, "bat.proto")
        self.assertEqual(third_parsed_import.node.weak, False)

    def test_public_import(self):
        self.assertEqual(
            ProtoImport.match('import public "foo.proto";').node.public, True
        )
        self.assertEqual(
            ProtoImport.match("import public 'foo.proto';").node.public, True
        )

    def test_public_typoed_import(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import publik "foo.proto";')

    def test_public_weak_mutually_exclusive(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import weak public "foo.proto";')

        with self.assertRaises(ValueError):
            ProtoImport.match('import public weak "foo.proto";')

    def test_public_mixed_imports(self):
        first_parsed_import = ProtoImport.match(
            dedent(
                """import "foo.proto";
            import public "bar/baz.proto";
            import public "bat.proto";"""
            )
        )
        self.assertEqual(first_parsed_import.node.path, "foo.proto")
        self.assertEqual(first_parsed_import.node.public, False)

        second_parsed_import = ProtoImport.match(first_parsed_import.remaining_source)
        self.assertEqual(second_parsed_import.node.path, "bar/baz.proto")
        self.assertEqual(second_parsed_import.node.public, True)

        third_parsed_import = ProtoImport.match(second_parsed_import.remaining_source)
        self.assertEqual(third_parsed_import.node.path, "bat.proto")
        self.assertEqual(third_parsed_import.node.public, True)


if __name__ == "__main__":
    unittest.main()
