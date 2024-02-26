import unittest
from textwrap import dedent

from src.proto_import import (
    ProtoImport,
    ProtoImportAdded,
    ProtoImportMadeNonWeak,
    ProtoImportMadePublic,
    ProtoImportRemoved,
)
from src.proto_string_literal import ProtoStringLiteral


class ImportTest(unittest.TestCase):
    def test_bare_import(self):
        double_quote_import = ProtoImport.match('import "foo.proto";')
        self.assertEqual(double_quote_import.node.path.value, "foo.proto")
        self.assertEqual(double_quote_import.node.weak, False)
        self.assertEqual(double_quote_import.node.public, False)
        self.assertEqual(double_quote_import.node.serialize(), 'import "foo.proto";')
        self.assertEqual(double_quote_import.remaining_source, "")

        single_quote_import = ProtoImport.match("import 'foo.proto';")
        self.assertEqual(single_quote_import.node.path.value, "foo.proto")
        self.assertEqual(single_quote_import.node.weak, False)
        self.assertEqual(single_quote_import.node.public, False)
        self.assertEqual(single_quote_import.node.serialize(), "import 'foo.proto';")
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
        double_quote_import = ProtoImport.match('import weak "foo.proto";')
        self.assertEqual(double_quote_import.node.weak, True)
        self.assertEqual(
            double_quote_import.node.serialize(), 'import weak "foo.proto";'
        )
        double_quote_import = ProtoImport.match("import weak 'foo.proto';")
        self.assertEqual(double_quote_import.node.weak, True)
        self.assertEqual(
            double_quote_import.node.serialize(), "import weak 'foo.proto';"
        )

    def test_weak_typoed_import(self):
        with self.assertRaises(ValueError):
            ProtoImport.match('import weac "foo.proto";')

    def test_weak_mixed_imports(self):
        first_parsed_import = ProtoImport.match(
            dedent(
                """import "foo.proto";
            import weak "bar/baz.proto";
            import "bat.proto";"""
            ),
        )
        self.assertEqual(first_parsed_import.node.path.value, "foo.proto")
        self.assertEqual(first_parsed_import.node.weak, False)
        self.assertEqual(first_parsed_import.node.serialize(), 'import "foo.proto";')

        second_parsed_import = ProtoImport.match(first_parsed_import.remaining_source)
        self.assertEqual(second_parsed_import.node.path.value, "bar/baz.proto")
        self.assertEqual(second_parsed_import.node.weak, True)
        self.assertEqual(
            second_parsed_import.node.serialize(), 'import weak "bar/baz.proto";'
        )

        third_parsed_import = ProtoImport.match(second_parsed_import.remaining_source)
        self.assertEqual(third_parsed_import.node.path.value, "bat.proto")
        self.assertEqual(third_parsed_import.node.weak, False)
        self.assertEqual(third_parsed_import.node.serialize(), 'import "bat.proto";')

    def test_public_import(self):
        double_quote_import = ProtoImport.match('import public "foo.proto";')
        self.assertEqual(double_quote_import.node.public, True)
        self.assertEqual(
            double_quote_import.node.serialize(), 'import public "foo.proto";'
        )

        single_quote_import = ProtoImport.match("import public 'foo.proto';")
        self.assertEqual(single_quote_import.node.public, True)
        self.assertEqual(
            single_quote_import.node.serialize(), "import public 'foo.proto';"
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
            ),
        )
        self.assertEqual(first_parsed_import.node.path.value, "foo.proto")
        self.assertEqual(first_parsed_import.node.public, False)
        self.assertEqual(first_parsed_import.node.serialize(), 'import "foo.proto";')

        second_parsed_import = ProtoImport.match(first_parsed_import.remaining_source)
        self.assertEqual(second_parsed_import.node.path.value, "bar/baz.proto")
        self.assertEqual(second_parsed_import.node.public, True)
        self.assertEqual(
            second_parsed_import.node.serialize(), 'import public "bar/baz.proto";'
        )

        third_parsed_import = ProtoImport.match(second_parsed_import.remaining_source)
        self.assertEqual(third_parsed_import.node.path.value, "bat.proto")
        self.assertEqual(third_parsed_import.node.public, True)
        self.assertEqual(
            third_parsed_import.node.serialize(), 'import public "bat.proto";'
        )

    def test_diff_sets_same_path_simple(self):
        pf1 = ProtoImport(ProtoStringLiteral("path/to/some.proto"))
        pf2 = ProtoImport(ProtoStringLiteral("path/to/some.proto"))
        self.assertEqual(ProtoImport.diff_sets([pf1], [pf2]), [])

    def test_diff_sets_added_path_simple(self):
        pf1 = ProtoImport(ProtoStringLiteral("path/to/some.proto"))
        self.assertEqual(ProtoImport.diff_sets([pf1], []), [ProtoImportAdded(pf1)])

    def test_diff_sets_removed_path_simple(self):
        pf2 = ProtoImport(ProtoStringLiteral("path/to/some.proto"))
        self.assertEqual(ProtoImport.diff_sets([], [pf2]), [ProtoImportRemoved(pf2)])

    def test_diff_sets_different_path_simple(self):
        pf1 = ProtoImport(ProtoStringLiteral("path/to/some.proto"))
        pf2 = ProtoImport(ProtoStringLiteral("path/to/some/other.proto"))
        self.assertEqual(
            ProtoImport.diff_sets([pf1], [pf2]),
            [ProtoImportAdded(pf1), ProtoImportRemoved(pf2)],
        )

    def test_diff_sets_changed_optional_attributes(self):
        pf1 = ProtoImport(
            ProtoStringLiteral("path/to/some.proto"),
            weak=False,
            public=True,
        )
        pf2 = ProtoImport(
            ProtoStringLiteral("path/to/some.proto"),
            weak=True,
            public=False,
        )
        self.assertEqual(
            ProtoImport.diff_sets([pf1], [pf2]),
            [
                ProtoImportMadeNonWeak(pf2),
                ProtoImportMadePublic(pf2),
            ],
        )


if __name__ == "__main__":
    unittest.main()
