import unittest
from textwrap import dedent

from src.proto_comment import ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_identifier import ProtoFullIdentifier, ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldOption,
    ProtoMessageFieldTypesEnum,
)
from src.proto_oneof import ProtoOneOf
from src.proto_option import ProtoOption
from src.proto_string_literal import ProtoStringLiteral


class OneOfTest(unittest.TestCase):
    maxDiff = None

    def test_oneof_empty(self):
        parsed_oneof_empty = ProtoOneOf.match(dedent("oneof one_of_field {}".strip()))
        self.assertEqual(
            parsed_oneof_empty.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [],
            ),
        )

    def test_oneof_empty_statements(self):
        parsed_oneof_empty = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                ;
                ;
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_empty.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [],
            ),
        )

    def test_oneof_basic_fields(self):
        parsed_oneof_basic_fields = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4;
                SubMessage sub_message = 9;
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_basic_fields.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("name"),
                        ProtoInt(4, ProtoIntSign.POSITIVE),
                    ),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier("sub_message"),
                        ProtoInt(9, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier("SubMessage"),
                        [],
                    ),
                ],
            ),
        )

    def test_oneof_options(self):
        parsed_oneof_options = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                option java_package = "com.example.foo";
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_options.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoOption(
                        ProtoIdentifier("java_package"),
                        ProtoConstant(ProtoStringLiteral("com.example.foo")),
                    ),
                ],
            ),
        )

    def test_oneof_field_option(self):
        parsed_oneof_field_option = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4 [ (bar.baz).bat = "bat", baz.bat = -100 ];
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_field_option.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("name"),
                        ProtoInt(4, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        None,
                        [
                            ProtoMessageFieldOption(
                                ProtoIdentifier("(bar.baz).bat"),
                                ProtoConstant(ProtoStringLiteral("bat")),
                            ),
                            ProtoMessageFieldOption(
                                ProtoIdentifier("baz.bat"),
                                ProtoConstant(ProtoInt(100, ProtoIntSign.NEGATIVE)),
                            ),
                        ],
                    )
                ],
            ),
        )

    def test_oneof_with_comment(self):
        parsed_oneof_with_comment = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4;
                // single-line comment!
                SubMessage sub_message = 9;
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_with_comment.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("name"),
                        ProtoInt(4, ProtoIntSign.POSITIVE),
                    ),
                    ProtoSingleLineComment(" single-line comment!"),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier("sub_message"),
                        ProtoInt(9, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier("SubMessage"),
                        [],
                    ),
                ],
            ),
        )

    def test_oneof_normalize_removes_comment(self):
        normalized_oneof = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4;
                // single-line comment!
                SubMessage sub_message = 9;
            }""".strip()
            ),
        ).node.normalize()
        self.assertEqual(
            normalized_oneof.nodes,
            [
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("name"),
                    ProtoInt(4, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                    ProtoIdentifier("sub_message"),
                    ProtoInt(9, ProtoIntSign.POSITIVE),
                    False,
                    False,
                    ProtoFullIdentifier("SubMessage"),
                    [],
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
