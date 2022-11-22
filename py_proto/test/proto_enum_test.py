import unittest
from textwrap import dedent

from src.proto_enum import ProtoEnum
from src.proto_identifier import ProtoIdentifier


class EnumTest(unittest.TestCase):
    def test_empty_enum(self):
        parsed_empty_enum = ProtoEnum.match("""enum FooEnum {}""")
        self.assertIsNotNone(parsed_empty_enum)
        self.assertEqual(parsed_empty_enum.node.name, ProtoIdentifier("FooEnum"))

        parsed_spaced_enum = ProtoEnum.match(
            dedent(
                """
            enum FooEnum {

            }
        """.strip()
            )
        )
        self.assertIsNotNone(parsed_spaced_enum)
        self.assertEqual(parsed_spaced_enum.node.name, ProtoIdentifier("FooEnum"))

    def test_enum_empty_statements(self):
        empty_statement_enum = ProtoEnum.match(
            dedent(
                """
            enum FooEnum {
                ;
                ;
            }
        """.strip()
            )
        )
        self.assertIsNotNone(empty_statement_enum)
        self.assertEqual(empty_statement_enum.node.name, ProtoIdentifier("FooEnum"))


if __name__ == "__main__":
    unittest.main()
