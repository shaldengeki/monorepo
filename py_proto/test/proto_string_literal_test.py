import unittest

from src.proto_string_literal import ProtoStringLiteral


class StringLiteralTest(unittest.TestCase):
    def test_correct_syntax(self):
        parsed_single_quote = ProtoStringLiteral.match(None, """'foo'""")
        self.assertEqual(parsed_single_quote.node.value, "foo")
        self.assertEqual(parsed_single_quote.remaining_source, "")
        self.assertEqual(parsed_single_quote.node.serialize(), "'foo'")
        parsed_double_quote = ProtoStringLiteral.match(None, """\"foo\"""")
        self.assertEqual(parsed_double_quote.node.value, "foo")
        self.assertEqual(parsed_double_quote.remaining_source, "")
        self.assertEqual(parsed_double_quote.node.serialize(), '"foo"')

    def test_remaining_source(self):
        parsed_single_quote = ProtoStringLiteral.match(None, """'foo'\nbar baz""")
        self.assertEqual(parsed_single_quote.remaining_source, "bar baz")
        parsed_double_quote = ProtoStringLiteral.match(None, """\"foo\"\"foobar\"""")
        self.assertEqual(parsed_double_quote.remaining_source, '"foobar"')

    def test_missing_quote(self):
        self.assertIsNone(ProtoStringLiteral.match(None, """'foo"""))
        self.assertIsNone(ProtoStringLiteral.match(None, """foo'"""))
        self.assertIsNone(ProtoStringLiteral.match(None, """\"foo"""))
        self.assertIsNone(ProtoStringLiteral.match(None, """foo\""""))
        self.assertIsNone(ProtoStringLiteral.match(None, """'foo\""""))
        self.assertIsNone(ProtoStringLiteral.match(None, """\"foo'"""))

    def test_escaped_quote(self):
        self.assertIsNone(ProtoStringLiteral.match(None, """'foo\\'"""))
        self.assertIsNone(ProtoStringLiteral.match(None, """\"foo\\\""""))
        parsed_escaped_quote = ProtoStringLiteral.match(None, """\"foo\\\"barbaz\"""")
        self.assertEqual(parsed_escaped_quote.node.value, 'foo\\"barbaz')
        self.assertEqual(parsed_escaped_quote.remaining_source, "")
        self.assertEqual(parsed_escaped_quote.node.serialize(), '"foo\\"barbaz"')


if __name__ == "__main__":
    unittest.main()
