import unittest

from src.proto_string_literal import ProtoStringLiteral
from src.proto_syntax import ProtoSyntax, ProtoSyntaxType


class SyntaxTest(unittest.TestCase):
    def test_correct_syntax(self):
        self.assertEqual(
            ProtoSyntax.match("syntax = 'proto3';").node.syntax.val, "proto3"
        )
        self.assertEqual(
            ProtoSyntax.match('syntax = "proto3";').node.syntax.val, "proto3"
        )
        self.assertEqual(
            ProtoSyntax.match("syntax = 'proto2';").node.syntax.val, "proto2"
        )
        self.assertEqual(
            ProtoSyntax.match('syntax = "proto2";').node.syntax.val, "proto2"
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


if __name__ == "__main__":
    unittest.main()
