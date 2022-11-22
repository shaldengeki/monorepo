import unittest
from src.parser import Parser
from src.proto_file import ProtoSyntaxTypes

class SyntaxTest(unittest.TestCase):
    def test_correct_syntax(self):
        self.assertEqual(Parser.loads("syntax = 'proto3'").syntax, ProtoSyntaxTypes.PROTO3)
        self.assertEqual(Parser.loads("syntax = \"proto3\"").syntax, ProtoSyntaxTypes.PROTO3)
        self.assertEqual(Parser.loads("syntax = 'proto2'").syntax, ProtoSyntaxTypes.PROTO2)
        self.assertEqual(Parser.loads("syntax = \"proto2\"").syntax, ProtoSyntaxTypes.PROTO2)

    def test_syntax_not_present(self):
        with self.assertRaises(Exception):
            Parser.loads("")
        with self.assertRaises(Exception):
            Parser.loads("import \"foo.proto\";")

    def test_syntax_malformed(self):
        with self.assertRaises(Exception):
            Parser.loads("syntax = proto3")
        with self.assertRaises(Exception):
            Parser.loads("syntax = proto3;")
        with self.assertRaises(Exception):
            Parser.loads("syntax = 'proto3")
        with self.assertRaises(Exception):
            Parser.loads("syntax = 'proto3;")
        with self.assertRaises(Exception):
            Parser.loads("syntax = proto3'")
        with self.assertRaises(Exception):
            Parser.loads("syntax = proto3';")
        with self.assertRaises(Exception):
            Parser.loads("syntax = 'proton';")
        with self.assertRaises(Exception):
            Parser.loads("syntax = 'proton'")
        with self.assertRaises(Exception):
            Parser.loads("syntax = 'proton")
        with self.assertRaises(Exception):
            Parser.loads("syntax = proton';")
        with self.assertRaises(Exception):
            Parser.loads("syntax = proton'")
        with self.assertRaises(Exception):
            Parser.loads("syntax = proton")

if __name__ == '__main__':
    unittest.main()