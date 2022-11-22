import unittest
from textwrap import dedent
from src.parser import Parser, ParseError
from src.proto_file import ProtoImport


class ImportTest(unittest.TestCase):
    def test_empty_imports(self):
        self.assertEqual(Parser.loads("syntax = 'proto3'").imports, [])

    def test_bare_import(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
            import "foo.proto";
        """
                )
            ).imports,
            [ProtoImport("foo.proto")],
        )
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
            import 'foo.proto';
        """
                )
            ).imports,
            [ProtoImport("foo.proto")],
        )

    def test_import_missing_semicolon(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import "foo.proto"
            """
                )
            )

    def test_weak_default(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import "foo.proto";
                """
                )
            ).imports,
            [ProtoImport("foo.proto", weak=False)],
        )

    def test_weak_import(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import weak "foo.proto";
                """
                )
            ).imports,
            [ProtoImport("foo.proto", weak=True)],
        )
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import weak 'foo.proto';
                """
                )
            ).imports,
            [ProtoImport("foo.proto", weak=True)],
        )

    def test_weak_typoed_import(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                    import weac "foo.proto";
                """
                )
            )

    def test_weak_mixed_imports(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import "foo.proto";
                import weak "bar/baz.proto";
                import "bat.proto";
                """
                )
            ).imports,
            [
                ProtoImport("foo.proto", weak=False),
                ProtoImport("bar/baz.proto", weak=True),
                ProtoImport("bat.proto", weak=False),
            ],
        )

    def test_public_default(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import "foo.proto";
                """
                )
            ).imports,
            [ProtoImport("foo.proto", public=False)],
        )

    def test_public_import(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import public "foo.proto";
                """
                )
            ).imports,
            [ProtoImport("foo.proto", public=True)],
        )
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import public 'foo.proto';
                """
                )
            ).imports,
            [ProtoImport("foo.proto", public=True)],
        )

    def test_public_typoed_import(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                    import publik "foo.proto";
                """
                )
            )

    def test_public_weak_mutually_exclusive(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                    import weak public "foo.proto";
                """
                )
            )

        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                    import public weak "foo.proto";
                """
                )
            )

    def test_public_mixed_imports(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
                import "foo.proto";
                import public "bar/baz.proto";
                import public "bat.proto";
                """
                )
            ).imports,
            [
                ProtoImport("foo.proto", weak=False),
                ProtoImport("bar/baz.proto", weak=False, public=True),
                ProtoImport("bat.proto", weak=False, public=True),
            ],
        )

    def test_multiple_imports(self):
        self.assertEqual(
            Parser.loads(
                dedent(
                    """syntax = 'proto3';
            import "foo.proto";
            import 'bar/baz.proto';
            import "foo2.proto";
        """
                )
            ).imports,
            [
                ProtoImport("foo.proto"),
                ProtoImport("bar/baz.proto"),
                ProtoImport("foo2.proto"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
