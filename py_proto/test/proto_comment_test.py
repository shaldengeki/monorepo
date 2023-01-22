import unittest

from src.proto_comment import ProtoMultiLineComment, ProtoSingleLineComment


class ProtoSingleLineCommentTest(unittest.TestCase):
    def test_matches_normal_comment(self):
        node = ProtoSingleLineComment.match("// hello there, this is a comment").node
        self.assertEqual(node.value, " hello there, this is a comment")
        self.assertEqual(node.serialize(), "// hello there, this is a comment")
        self.assertIsNone(node.normalize())

    def test_matches_without_space(self):
        node = ProtoSingleLineComment.match("//comment without space").node
        self.assertEqual(node.value, "comment without space")
        self.assertEqual(node.serialize(), "//comment without space")
        self.assertIsNone(node.normalize())

    def test_does_not_match_multiple_lines(self):
        node = ProtoSingleLineComment.match("//line one\nbut not this").node
        self.assertEqual(node.value, "line one")
        self.assertEqual(node.serialize(), "//line one")
        self.assertIsNone(node.normalize())

    def test_does_not_match_single_slash(self):
        self.assertIsNone(
            ProtoSingleLineComment.match("/hello there, this is a comment")
        )
        self.assertIsNone(
            ProtoSingleLineComment.match("/ /hello there, this is a comment")
        )


class ProtoMultiLineCommentTest(unittest.TestCase):
    def test_matches_single_line_comment(self):
        node = ProtoMultiLineComment.match("/* hello there, this is a comment */").node
        self.assertEqual(node.value, " hello there, this is a comment ")
        self.assertEqual(node.serialize(), "/* hello there, this is a comment */")
        self.assertIsNone(node.normalize())

    def test_matches_multi_line_comment(self):
        node = ProtoMultiLineComment.match(
            "/* hello there,\nthis is a \nmulti-line comment */"
        ).node
        self.assertEqual(node.value, " hello there,\nthis is a \nmulti-line comment ")
        self.assertEqual(
            node.serialize(), "/* hello there,\nthis is a \nmulti-line comment */"
        )
        self.assertIsNone(node.normalize())

    def test_does_not_match_unclosed_comment(self):
        self.assertIsNone(
            ProtoMultiLineComment.match(
                "/* hello there, this\n /is an unclosed\n*multiple-line comment/"
            )
        )

    def test_matches_without_space(self):
        node = ProtoMultiLineComment.match("/*comment without space*/").node
        self.assertEqual(node.value, "comment without space")
        self.assertEqual(node.serialize(), "/*comment without space*/")
        self.assertIsNone(node.normalize())

    def test_does_not_match_partial_opening(self):
        self.assertIsNone(
            ProtoMultiLineComment.match("/hello there, this is a comment*/")
        )
        self.assertIsNone(
            ProtoMultiLineComment.match("*/hello there, this is a comment*/")
        )
        self.assertIsNone(
            ProtoMultiLineComment.match("*hello there, this is a comment*/")
        )


if __name__ == "__main__":
    unittest.main()
