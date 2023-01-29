import unittest

from src.proto_string_literal import ProtoStringLiteral
from src.proto_syntax import ProtoSyntax, ProtoSyntaxChanged


class SyntaxTest(unittest.TestCase):
    def test_correct_syntax(self):
        self.assertEqual(
            ProtoSyntax.match("syntax = 'proto3';").node.syntax.value, "proto3"
        )
        self.assertEqual(
            ProtoSyntax.match('syntax = "proto3";').node.syntax.value, "proto3"
        )
        self.assertEqual(
            ProtoSyntax.match("syntax = 'proto2';").node.syntax.value, "proto2"
        )
        self.assertEqual(
            ProtoSyntax.match('syntax = "proto2";').node.syntax.value, "proto2"
        )

    def test_serialize(self):
        self.assertEqual(
            ProtoSyntax.match("syntax = 'proto3';").node.serialize(),
            "syntax = 'proto3';",
        )
        self.assertEqual(
            ProtoSyntax.match('syntax = "proto3";').node.serialize(),
            'syntax = "proto3";',
        )
        self.assertEqual(
            ProtoSyntax.match("syntax = 'proto2';").node.serialize(),
            "syntax = 'proto2';",
        )
        self.assertEqual(
            ProtoSyntax.match('syntax = "proto2";').node.serialize(),
            'syntax = "proto2";',
        )

    def test_syntax_not_present(self):
        self.assertIsNone(ProtoSyntax.match(""))
        self.assertIsNone(ProtoSyntax.match('import "foo.proto";'))

    def test_syntax_malformed(self):
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proto3'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match('syntax = "proto3"')
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proto2'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match('syntax = "proto2"')
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proto3")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proto3;")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proto3")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proto3;")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proto3'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proto3';")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proton';")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proton'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = 'proton")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proton';")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proton'")
        with self.assertRaises(ValueError):
            ProtoSyntax.match("syntax = proton")

    def test_diff_empty_same_syntax_returns_empty(self):
        pf1 = ProtoSyntax(ProtoStringLiteral("proto3"))
        pf2 = ProtoSyntax(ProtoStringLiteral("proto3"))
        self.assertEqual(ProtoSyntax.diff(pf1, pf2), [])

    def test_diff_empty_different_syntax_returns_syntax_diff(self):
        pf1 = ProtoSyntax(ProtoStringLiteral("proto3"))
        pf2 = ProtoSyntax(ProtoStringLiteral("proto2"))
        self.assertEqual(
            ProtoSyntax.diff(pf1, pf2),
            [
                ProtoSyntaxChanged(
                    ProtoSyntax(ProtoStringLiteral("proto3")),
                    ProtoSyntax(ProtoStringLiteral("proto2")),
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
