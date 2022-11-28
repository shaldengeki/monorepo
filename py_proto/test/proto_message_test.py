import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
from src.proto_constant import ProtoConstant
from src.proto_enum import ProtoEnum, ProtoEnumValue
from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_message import ProtoMessage
from src.proto_option import ProtoOption
from src.proto_reserved import ProtoReserved, ProtoReservedRange, ProtoReservedRangeEnum
from src.proto_string_literal import ProtoStringLiteral


class MessageTest(unittest.TestCase):
    maxDiff = None

    def test_message_all_features(self):
        parsed_message_multiple_fields = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                option (foo.bar).baz = "bat";
                enum MyEnum {
                    ME_UNDEFINED = 0;
                    ME_VALONE = 1;
                    ME_VALTWO = 2;
                }
                message NestedMessage {}
                reserved "a";
                reserved 1 to 3;
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_multiple_fields.node.nodes,
            [
                ProtoOption(
                    ProtoIdentifier("(foo.bar).baz"),
                    ProtoConstant(ProtoStringLiteral("bat")),
                ),
                ProtoEnum(
                    ProtoIdentifier("MyEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("ME_UNDEFINED"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        ),
                        ProtoEnumValue(
                            ProtoIdentifier("ME_VALONE"),
                            ProtoInt(1, ProtoIntSign.POSITIVE),
                        ),
                        ProtoEnumValue(
                            ProtoIdentifier("ME_VALTWO"),
                            ProtoInt(2, ProtoIntSign.POSITIVE),
                        ),
                    ],
                ),
                ProtoMessage(ProtoIdentifier("NestedMessage"), []),
                ProtoReserved(fields=[ProtoIdentifier("a")]),
                ProtoReserved(
                    ranges=[
                        ProtoReservedRange(
                            ProtoInt(1, ProtoIntSign.POSITIVE),
                            ProtoInt(3, ProtoIntSign.POSITIVE),
                        )
                    ]
                ),
            ],
        )
        self.assertEqual(
            parsed_message_multiple_fields.node.serialize(),
            dedent(
                """
            message FooMessage {
            option (foo.bar).baz = "bat";
            enum MyEnum {
            ME_UNDEFINED = 0;
            ME_VALONE = 1;
            ME_VALTWO = 2;
            }
            message NestedMessage {
            }
            reserved "a";
            reserved 1 to 3;
            }
            """
            ).strip(),
        )

    def test_empty_message(self):
        parsed_empty_message = ProtoMessage.match("""message FooMessage {}""")
        self.assertIsNotNone(parsed_empty_message)
        self.assertEqual(parsed_empty_message.node.name, ProtoIdentifier("FooMessage"))

        parsed_spaced_message = ProtoMessage.match(
            dedent(
                """
            message FooMessage {

            }
        """.strip()
            )
        )
        self.assertIsNotNone(parsed_spaced_message)
        self.assertEqual(parsed_spaced_message.node.name, ProtoIdentifier("FooMessage"))

    def test_message_empty_statements(self):
        empty_statement_message = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                ;
                ;
            }
        """.strip()
            )
        )
        self.assertIsNotNone(empty_statement_message)
        self.assertEqual(
            empty_statement_message.node.name, ProtoIdentifier("FooMessage")
        )

    def test_message_optionals(self):
        parsed_message_with_optionals = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                option java_package = "foobar";
                option (foo.bar).baz = false;
            }
        """.strip()
            )
        )
        self.assertIsNotNone(
            parsed_message_with_optionals.node.options,
            [
                ProtoOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("foobar")),
                ),
                ProtoOption(
                    ProtoIdentifier("(foo.bar).baz"),
                    ProtoConstant(ProtoBool(False)),
                ),
            ],
        )
        self.assertEqual(
            parsed_message_with_optionals.node.name, ProtoIdentifier("FooMessage")
        )

    def test_message_nested_enum(self):
        parsed_message_with_enum = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                enum MyEnum {
                    ME_UNDEFINED = 0;
                    ME_NEGATIVE = -1;
                    ME_VALONE = 1;
                }
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_enum.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoEnum(
                        ProtoIdentifier("MyEnum"),
                        [
                            ProtoEnumValue(
                                ProtoIdentifier("ME_UNDEFINED"),
                                ProtoInt(0, ProtoIntSign.POSITIVE),
                            ),
                            ProtoEnumValue(
                                ProtoIdentifier("ME_NEGATIVE"),
                                ProtoInt(1, ProtoIntSign.NEGATIVE),
                            ),
                            ProtoEnumValue(
                                ProtoIdentifier("ME_VALONE"),
                                ProtoInt(1, ProtoIntSign.POSITIVE),
                            ),
                        ],
                    )
                ],
            ),
        )

    def test_message_nested_message(self):
        parsed_message_with_enum = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                message NestedMessage {}
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_enum.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoMessage(ProtoIdentifier("NestedMessage"), []),
                ],
            ),
        )

    def test_message_reserved_single_field(self):
        parsed_message_with_reserved_single_field = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                reserved 38, 48 to 100, 72 to max;
                reserved "foo", "barBaz";
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_reserved_single_field.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoReserved(
                        ranges=[
                            ProtoReservedRange(ProtoInt(38, ProtoIntSign.POSITIVE)),
                            ProtoReservedRange(
                                ProtoInt(48, ProtoIntSign.POSITIVE),
                                ProtoInt(100, ProtoIntSign.POSITIVE),
                            ),
                            ProtoReservedRange(
                                ProtoInt(72, ProtoIntSign.POSITIVE),
                                ProtoReservedRangeEnum.MAX,
                            ),
                        ]
                    ),
                    ProtoReserved(
                        fields=[
                            ProtoIdentifier("foo"),
                            ProtoIdentifier("barBaz"),
                        ]
                    ),
                ],
            ),
        )


if __name__ == "__main__":
    unittest.main()
