import unittest

from src.proto_string_literal import ProtoStringLiteral
from src.proto_syntax import ProtoSyntax, ProtoSyntaxChanged


class SyntaxTest(unittest.TestCase):
    def test_correct_syntax(self):
        self.assertEqual(
            ProtoSyntax.match(None, "syntax = 'proto3';").node.syntax.value, "proto3"
        )
        self.assertEqual(
            ProtoSyntax.match(None, 'syntax = "proto3";').node.syntax.value, "proto3"
        )
        self.assertEqual(
            ProtoSyntax.match(None, "syntax = 'proto2';").node.syntax.value, "proto2"
        )
        self.assertEqual(
            ProtoSyntax.match(None, 'syntax = "proto2";').node.syntax.value, "proto2"
        )

    def test_serialize(self):
        self.assertEqual(
            ProtoSyntax.match(None, "syntax = 'proto3';").node.serialize(),
            "syntax = 'proto3';",
        )
        self.assertEqual(
            ProtoSyntax.match(None, 'syntax = "proto3";').node.serialize(),
            'syntax = "proto3";',
        )
        self.assertEqual(
            ProtoSyntax.match(None, "syntax = 'proto2';").node.serialize(),
            "syntax = 'proto2';",
        )
        self.assertEqual(
            ProtoSyntax.match(None, 'syntax = "proto2";').node.serialize(),
            'syntax = "proto2";',
        )

    def test_syntax_not_present(self):
        self.assertIsNone(ProtoSyntax.match(None, ""))
        self.assertIsNone(ProtoSyntax.match(None, 'import "foo.proto";'))

    def test_syntax_malformed(self):
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proto3'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, 'syntax = "proto3"')
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proto2'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, 'syntax = "proto2"')
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proto3")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proto3;")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proto3")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proto3;")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proto3'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proto3';")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proton';")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proton'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = 'proton")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proton';")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proton'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match(None, "syntax = proton")

    def test_diff_empty_same_syntax_returns_empty(self):
        pf1 = ProtoSyntax(None, ProtoStringLiteral(None, "proto3"))
        pf2 = ProtoSyntax(None, ProtoStringLiteral(None, "proto3"))
        self.assertEqual(ProtoSyntax.diff(pf1, pf2), [])

    def test_diff_empty_different_syntax_returns_syntax_diff(self):
        pf1 = ProtoSyntax(None, ProtoStringLiteral(None, "proto3"))
        pf2 = ProtoSyntax(None, ProtoStringLiteral(None, "proto2"))
        self.assertEqual(
            ProtoSyntax.diff(pf1, pf2),
            [
                ProtoSyntaxChanged(
                    ProtoSyntax(None, ProtoStringLiteral(None, "proto3")),
                    ProtoSyntax(None, ProtoStringLiteral(None, "proto2")),
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
