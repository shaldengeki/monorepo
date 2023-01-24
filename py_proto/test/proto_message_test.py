import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
from src.proto_comment import ProtoMultiLineComment, ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_enum import ProtoEnum, ProtoEnumValue
from src.proto_extensions import ProtoExtensions
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_message import (
    ProtoMap,
    ProtoMapKeyTypesEnum,
    ProtoMapValueTypesEnum,
    ProtoMessage,
    ProtoMessageField,
    ProtoMessageFieldOption,
    ProtoMessageFieldTypesEnum,
    ProtoOneOf,
)
from src.proto_option import ProtoOption
from src.proto_range import ProtoRange, ProtoRangeEnum
from src.proto_reserved import ProtoReserved
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
                // single-line comment
                repeated string some_field = 4 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                bool some_bool_field = 5;
                oneof one_of_field {
                    string name = 4;
                    option java_package = "com.example.foo";
                    SubMessage sub_message = 9 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                }
                map <sfixed64, NestedMessage> my_map = 10;
                map <string, string> string_map = 11 [ java_package = "com.example.foo", baz.bat = 48 ];
                extensions 8 to max;
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
                        ProtoRange(
                            ProtoInt(1, ProtoIntSign.POSITIVE),
                            ProtoInt(3, ProtoIntSign.POSITIVE),
                        )
                    ]
                ),
                ProtoSingleLineComment(" single-line comment"),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("some_field"),
                    ProtoInt(4, ProtoIntSign.POSITIVE),
                    True,
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
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.BOOL,
                    ProtoIdentifier("some_bool_field"),
                    ProtoInt(5, ProtoIntSign.POSITIVE),
                ),
                ProtoOneOf(
                    ProtoIdentifier("one_of_field"),
                    [
                        ProtoMessageField(
                            ProtoMessageFieldTypesEnum.STRING,
                            ProtoIdentifier("name"),
                            ProtoInt(4, ProtoIntSign.POSITIVE),
                        ),
                        ProtoOption(
                            ProtoIdentifier("java_package"),
                            ProtoConstant(ProtoStringLiteral("com.example.foo")),
                        ),
                        ProtoMessageField(
                            ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                            ProtoIdentifier("sub_message"),
                            ProtoInt(9, ProtoIntSign.POSITIVE),
                            False,
                            False,
                            ProtoFullIdentifier("SubMessage"),
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
                        ),
                    ],
                ),
                ProtoMap(
                    ProtoMapKeyTypesEnum.SFIXED64,
                    ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                    ProtoIdentifier("my_map"),
                    ProtoInt(10, ProtoIntSign.POSITIVE),
                    ProtoEnumOrMessageIdentifier("NestedMessage"),
                    [],
                ),
                ProtoMap(
                    # map <string, string> string_map = 11 [ java_package = "com.example.foo", baz.bat = 48 ];
                    ProtoMapKeyTypesEnum.STRING,
                    ProtoMapValueTypesEnum.STRING,
                    ProtoIdentifier("string_map"),
                    ProtoInt(11, ProtoIntSign.POSITIVE),
                    None,
                    [
                        ProtoMessageFieldOption(
                            ProtoIdentifier("java_package"),
                            ProtoConstant(ProtoStringLiteral("com.example.foo")),
                        ),
                        ProtoMessageFieldOption(
                            ProtoFullIdentifier("baz.bat"),
                            ProtoConstant(ProtoInt(48, ProtoIntSign.POSITIVE)),
                        ),
                    ],
                ),
                ProtoExtensions([ProtoRange(8, ProtoRangeEnum.MAX)]),
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
            // single-line comment
            repeated string some_field = 4 [ (bar.baz).bat = "bat", baz.bat = -100 ];
            bool some_bool_field = 5;
            oneof one_of_field {
            string name = 4;
            option java_package = "com.example.foo";
            SubMessage sub_message = 9 [ (bar.baz).bat = "bat", baz.bat = -100 ];
            }
            map <sfixed64, NestedMessage> my_map = 10;
            map <string, string> string_map = 11 [ java_package = "com.example.foo", baz.bat = 48 ];
            extensions 8 to max;
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
                            ProtoRange(ProtoInt(38, ProtoIntSign.POSITIVE)),
                            ProtoRange(
                                ProtoInt(48, ProtoIntSign.POSITIVE),
                                ProtoInt(100, ProtoIntSign.POSITIVE),
                            ),
                            ProtoRange(
                                ProtoInt(72, ProtoIntSign.POSITIVE),
                                ProtoRangeEnum.MAX,
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

    def test_message_simple_field(self):
        parsed_message_with_single_field_simple = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                string single_field = 1;
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_single_field_simple.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("single_field"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        )

    def test_message_field_starts_with_underscore(self):
        parsed_message_with_single_field_simple = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                string _test_field = 1;
                string __test_field2 = 1;
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_single_field_simple.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("_test_field"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                    ),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("__test_field2"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                    ),
                ],
            ),
        )

    def test_message_repeated_field(self):
        parsed_message_with_repeated_field_simple = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                repeated bool repeated_field = 3;
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_repeated_field_simple.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.BOOL,
                        ProtoIdentifier("repeated_field"),
                        ProtoInt(3, ProtoIntSign.POSITIVE),
                        True,
                    )
                ],
            ),
        )

    def test_message_field_enum_or_message(self):
        parsed_message_with_repeated_field_simple = ProtoMessage.match(
            dedent(
                """
            message FooMessage {
                foo.SomeEnumOrMessage enum_or_message_field = 1;
            }
        """.strip()
            )
        )
        self.assertEqual(
            parsed_message_with_repeated_field_simple.node,
            ProtoMessage(
                ProtoIdentifier("FooMessage"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier("enum_or_message_field"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier("foo.SomeEnumOrMessage"),
                    )
                ],
            ),
        )

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
            )
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
            )
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
            )
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
            )
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
            )
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
            )
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

    def test_simple_map(self):
        parsed_map_simple = ProtoMap.match("map <sfixed64, NestedMessage> my_map = 10;")
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier("my_map"),
                ProtoInt(10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier("NestedMessage"),
                [],
            ),
        )

    def test_map_without_spaces(self):
        map_without_spaces = ProtoMap.match("map<sfixed64, NestedMessage> my_map = 10;")
        self.assertEqual(
            map_without_spaces.node,
            ProtoMap(
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier("my_map"),
                ProtoInt(10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier("NestedMessage"),
                [],
            ),
        )

    def test_map_with_options(self):
        parsed_map_simple = ProtoMap.match(
            "map <sfixed64, NestedMessage> my_map = 10  [ java_package = 'com.example.foo', baz.bat = 48 ];"
        )
        self.assertEqual(parsed_map_simple.node.key_type, ProtoMapKeyTypesEnum.SFIXED64)
        self.assertEqual(
            parsed_map_simple.node.value_type, ProtoMapValueTypesEnum.ENUM_OR_MESSAGE
        )
        self.assertEqual(parsed_map_simple.node.name, ProtoIdentifier("my_map"))
        self.assertEqual(
            parsed_map_simple.node.number, ProtoInt(10, ProtoIntSign.POSITIVE)
        )
        self.assertEqual(
            parsed_map_simple.node.enum_or_message_type_name,
            ProtoEnumOrMessageIdentifier("NestedMessage"),
        )
        self.assertEqual(
            parsed_map_simple.node.options,
            [
                ProtoMessageFieldOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("com.example.foo")),
                ),
                ProtoMessageFieldOption(
                    ProtoFullIdentifier("baz.bat"),
                    ProtoConstant(ProtoInt(48, ProtoIntSign.POSITIVE)),
                ),
            ],
        )

    def test_map_message_value(self):
        parsed_map_simple = ProtoMap.match("map <string, string> string_map = 11;")
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                ProtoMapKeyTypesEnum.STRING,
                ProtoMapValueTypesEnum.STRING,
                ProtoIdentifier("string_map"),
                ProtoInt(11, ProtoIntSign.POSITIVE),
                None,
                [],
            ),
        )

    def test_field_optional_default_false(self):
        string_field = ProtoMessageField.match("string single_field = 1;")
        self.assertEqual(
            string_field.node,
            ProtoMessageField(
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier("single_field"),
                ProtoInt(1, ProtoIntSign.POSITIVE),
                False,
                False,
            ),
        )

    def test_field_optional_set(self):
        string_field = ProtoMessageField.match(
            "optional string single_field = 1;".strip()
        )
        self.assertEqual(
            string_field.node,
            ProtoMessageField(
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier("single_field"),
                ProtoInt(1, ProtoIntSign.POSITIVE),
                False,
                True,
            ),
        )

    def test_field_cannot_have_repeated_and_optional(self):
        with self.assertRaises(ValueError):
            ProtoMessageField(
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier("single_field"),
                ProtoInt(1, ProtoIntSign.POSITIVE),
                True,
                True,
            )

    def test_message_parses_comments(self):
        parsed_comments = ProtoMessage.match(
            dedent(
                """
                message MyMessage {
                    string foo = 1;
                    // single-line comment!
                    bool bar = 2;
                    /*
                    multiple
                    line
                    comment!
                    */
                    string baz = 3;
                }
                """.strip()
            )
        )
        self.assertEqual(
            parsed_comments.node.nodes,
            [
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("foo"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                ),
                ProtoSingleLineComment(" single-line comment!"),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.BOOL,
                    ProtoIdentifier("bar"),
                    ProtoInt(2, ProtoIntSign.POSITIVE),
                ),
                ProtoMultiLineComment(
                    "\n                    multiple\n                    line\n                    comment!\n                    "
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("baz"),
                    ProtoInt(3, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_message_normalizes_away_comments(self):
        parsed_comments = ProtoMessage.match(
            dedent(
                """
                message MyMessage {
                    string foo = 1;
                    // single-line comment!
                    bool bar = 2;
                    /*
                    multiple
                    line
                    comment!
                    */
                    string baz = 3;
                }
                """.strip()
            )
        ).node.normalize()
        self.assertEqual(
            parsed_comments.nodes,
            [
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("foo"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.BOOL,
                    ProtoIdentifier("bar"),
                    ProtoInt(2, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("baz"),
                    ProtoInt(3, ProtoIntSign.POSITIVE),
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
