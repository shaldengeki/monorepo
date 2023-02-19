import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
from src.proto_comment import ProtoMultiLineComment, ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_enum import ProtoEnum, ProtoEnumValue
from src.proto_extend import ProtoExtend
from src.proto_extensions import ProtoExtensions
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_map import ProtoMap, ProtoMapKeyTypesEnum, ProtoMapValueTypesEnum
from src.proto_message import (
    ProtoMessage,
    ProtoMessageAdded,
    ProtoMessageRemoved,
    ProtoOneOf,
)
from src.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldOption,
    ProtoMessageFieldTypesEnum,
)
from src.proto_option import ProtoOption
from src.proto_range import ProtoRange, ProtoRangeEnum
from src.proto_reserved import ProtoReserved
from src.proto_string_literal import ProtoStringLiteral


class MessageTest(unittest.TestCase):
    maxDiff = None

    def test_message_all_features(self):
        parsed_message_multiple_fields = ProtoMessage.match(
            None,
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
            ),
        )
        self.assertEqual(
            parsed_message_multiple_fields.node.nodes,
            [
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "(foo.bar).baz"),
                    ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                ),
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "MyEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "ME_UNDEFINED"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        ),
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "ME_VALONE"),
                            ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                        ),
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "ME_VALTWO"),
                            ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                        ),
                    ],
                ),
                ProtoMessage(None, ProtoIdentifier(None, "NestedMessage"), []),
                ProtoReserved(None, fields=[ProtoIdentifier(None, "a")]),
                ProtoReserved(
                    None,
                    ranges=[
                        ProtoRange(
                            None,
                            ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                            ProtoInt(None, 3, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
                ProtoSingleLineComment(None, " single-line comment"),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "some_field"),
                    ProtoInt(None, 4, ProtoIntSign.POSITIVE),
                    True,
                    False,
                    None,
                    [
                        ProtoMessageFieldOption(
                            None,
                            ProtoIdentifier(None, "(bar.baz).bat"),
                            ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                        ),
                        ProtoMessageFieldOption(
                            None,
                            ProtoIdentifier(None, "baz.bat"),
                            ProtoConstant(
                                None, ProtoInt(None, 100, ProtoIntSign.NEGATIVE)
                            ),
                        ),
                    ],
                ),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.BOOL,
                    ProtoIdentifier(None, "some_bool_field"),
                    ProtoInt(None, 5, ProtoIntSign.POSITIVE),
                ),
                ProtoOneOf(
                    None,
                    ProtoIdentifier(None, "one_of_field"),
                    [
                        ProtoMessageField(
                            None,
                            ProtoMessageFieldTypesEnum.STRING,
                            ProtoIdentifier(None, "name"),
                            ProtoInt(None, 4, ProtoIntSign.POSITIVE),
                        ),
                        ProtoOption(
                            None,
                            ProtoIdentifier(None, "java_package"),
                            ProtoConstant(
                                None, ProtoStringLiteral(None, "com.example.foo")
                            ),
                        ),
                        ProtoMessageField(
                            None,
                            ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                            ProtoIdentifier(None, "sub_message"),
                            ProtoInt(None, 9, ProtoIntSign.POSITIVE),
                            False,
                            False,
                            ProtoFullIdentifier(None, "SubMessage"),
                            [
                                ProtoMessageFieldOption(
                                    None,
                                    ProtoIdentifier(None, "(bar.baz).bat"),
                                    ProtoConstant(
                                        None, ProtoStringLiteral(None, "bat")
                                    ),
                                ),
                                ProtoMessageFieldOption(
                                    None,
                                    ProtoIdentifier(None, "baz.bat"),
                                    ProtoConstant(
                                        None, ProtoInt(None, 100, ProtoIntSign.NEGATIVE)
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                ProtoMap(
                    None,
                    ProtoMapKeyTypesEnum.SFIXED64,
                    ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                    ProtoIdentifier(None, "my_map"),
                    ProtoInt(None, 10, ProtoIntSign.POSITIVE),
                    ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
                    [],
                ),
                ProtoMap(
                    None,
                    # map <string, string> string_map = 11 [ java_package = "com.example.foo", baz.bat = 48 ];
                    ProtoMapKeyTypesEnum.STRING,
                    ProtoMapValueTypesEnum.STRING,
                    ProtoIdentifier(None, "string_map"),
                    ProtoInt(None, 11, ProtoIntSign.POSITIVE),
                    None,
                    [
                        ProtoMessageFieldOption(
                            None,
                            ProtoIdentifier(None, "java_package"),
                            ProtoConstant(
                                None, ProtoStringLiteral(None, "com.example.foo")
                            ),
                        ),
                        ProtoMessageFieldOption(
                            None,
                            ProtoFullIdentifier(None, "baz.bat"),
                            ProtoConstant(
                                None, ProtoInt(None, 48, ProtoIntSign.POSITIVE)
                            ),
                        ),
                    ],
                ),
                ProtoExtensions(None, [ProtoRange(None, 8, ProtoRangeEnum.MAX)]),
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
        parsed_empty_message = ProtoMessage.match(None, """message FooMessage {}""")
        self.assertIsNotNone(parsed_empty_message)
        self.assertEqual(
            parsed_empty_message.node.name, ProtoIdentifier(None, "FooMessage")
        )

        parsed_spaced_message = ProtoMessage.match(
            None,
            dedent(
                """
            message FooMessage {

            }
        """.strip()
            ),
        )
        self.assertIsNotNone(parsed_spaced_message)
        self.assertEqual(
            parsed_spaced_message.node.name, ProtoIdentifier(None, "FooMessage")
        )

    def test_message_empty_statements(self):
        empty_statement_message = ProtoMessage.match(
            None,
            dedent(
                """
            message FooMessage {
                ;
                ;
            }
        """.strip()
            ),
        )
        self.assertIsNotNone(empty_statement_message)
        self.assertEqual(
            empty_statement_message.node.name, ProtoIdentifier(None, "FooMessage")
        )

    def test_message_optionals(self):
        parsed_message_with_optionals = ProtoMessage.match(
            None,
            dedent(
                """
            message FooMessage {
                option java_package = "foobar";
                option (foo.bar).baz = false;
            }
        """.strip()
            ),
        )
        self.assertIsNotNone(
            parsed_message_with_optionals.node.options,
            [
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "java_package"),
                    ProtoConstant(None, ProtoStringLiteral(None, "foobar")),
                ),
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "(foo.bar).baz"),
                    ProtoConstant(None, ProtoBool(None, False)),
                ),
            ],
        )
        self.assertEqual(
            parsed_message_with_optionals.node.name, ProtoIdentifier(None, "FooMessage")
        )

    def test_message_nested_enum(self):
        parsed_message_with_enum = ProtoMessage.match(
            None,
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
            ),
        )
        self.assertEqual(
            parsed_message_with_enum.node,
            ProtoMessage(
                None,
                ProtoIdentifier(None, "FooMessage"),
                [
                    ProtoEnum(
                        None,
                        ProtoIdentifier(None, "MyEnum"),
                        [
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "ME_UNDEFINED"),
                                ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                            ),
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "ME_NEGATIVE"),
                                ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
                            ),
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "ME_VALONE"),
                                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                            ),
                        ],
                    )
                ],
            ),
        )

    def test_message_nested_message(self):
        parsed_message_with_enum = ProtoMessage.match(
            None,
            dedent(
                """
            message FooMessage {
                message NestedMessage {}
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_message_with_enum.node,
            ProtoMessage(
                None,
                ProtoIdentifier(None, "FooMessage"),
                [
                    ProtoMessage(None, ProtoIdentifier(None, "NestedMessage"), []),
                ],
            ),
        )

    def test_message_reserved_single_field(self):
        parsed_message_with_reserved_single_field = ProtoMessage.match(
            None,
            dedent(
                """
            message FooMessage {
                reserved 38, 48 to 100, 72 to max;
                reserved "foo", "barBaz";
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_message_with_reserved_single_field.node,
            ProtoMessage(
                None,
                ProtoIdentifier(None, "FooMessage"),
                [
                    ProtoReserved(
                        None,
                        ranges=[
                            ProtoRange(None, ProtoInt(None, 38, ProtoIntSign.POSITIVE)),
                            ProtoRange(
                                None,
                                ProtoInt(None, 48, ProtoIntSign.POSITIVE),
                                ProtoInt(None, 100, ProtoIntSign.POSITIVE),
                            ),
                            ProtoRange(
                                None,
                                ProtoInt(None, 72, ProtoIntSign.POSITIVE),
                                ProtoRangeEnum.MAX,
                            ),
                        ],
                    ),
                    ProtoReserved(
                        None,
                        fields=[
                            ProtoIdentifier(None, "foo"),
                            ProtoIdentifier(None, "barBaz"),
                        ],
                    ),
                ],
            ),
        )

    def test_message_simple_field(self):
        parsed_message_with_single_field_simple = ProtoMessage.match(
            None,
            dedent(
                """
            message FooMessage {
                string single_field = 1;
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_message_with_single_field_simple.node,
            ProtoMessage(
                None,
                ProtoIdentifier(None, "FooMessage"),
                [
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier(None, "single_field"),
                        ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        )

    def test_oneof_empty(self):
        parsed_oneof_empty = ProtoOneOf.match(
            None, dedent("oneof one_of_field {}".strip())
        )
        self.assertEqual(
            parsed_oneof_empty.node,
            ProtoOneOf(
                None,
                ProtoIdentifier(None, "one_of_field"),
                [],
            ),
        )

    def test_oneof_empty_statements(self):
        parsed_oneof_empty = ProtoOneOf.match(
            None,
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
                None,
                ProtoIdentifier(None, "one_of_field"),
                [],
            ),
        )

    def test_oneof_basic_fields(self):
        parsed_oneof_basic_fields = ProtoOneOf.match(
            None,
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
                None,
                ProtoIdentifier(None, "one_of_field"),
                [
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier(None, "name"),
                        ProtoInt(None, 4, ProtoIntSign.POSITIVE),
                    ),
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier(None, "sub_message"),
                        ProtoInt(None, 9, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier(None, "SubMessage"),
                        [],
                    ),
                ],
            ),
        )

    def test_oneof_options(self):
        parsed_oneof_options = ProtoOneOf.match(
            None,
            dedent(
                """oneof one_of_field {
                option java_package = "com.example.foo";
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_options.node,
            ProtoOneOf(
                None,
                ProtoIdentifier(None, "one_of_field"),
                [
                    ProtoOption(
                        None,
                        ProtoIdentifier(None, "java_package"),
                        ProtoConstant(
                            None, ProtoStringLiteral(None, "com.example.foo")
                        ),
                    ),
                ],
            ),
        )

    def test_oneof_field_option(self):
        parsed_oneof_field_option = ProtoOneOf.match(
            None,
            dedent(
                """oneof one_of_field {
                string name = 4 [ (bar.baz).bat = "bat", baz.bat = -100 ];
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_field_option.node,
            ProtoOneOf(
                None,
                ProtoIdentifier(None, "one_of_field"),
                [
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier(None, "name"),
                        ProtoInt(None, 4, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        None,
                        [
                            ProtoMessageFieldOption(
                                None,
                                ProtoIdentifier(None, "(bar.baz).bat"),
                                ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                            ),
                            ProtoMessageFieldOption(
                                None,
                                ProtoIdentifier(None, "baz.bat"),
                                ProtoConstant(
                                    None, ProtoInt(None, 100, ProtoIntSign.NEGATIVE)
                                ),
                            ),
                        ],
                    )
                ],
            ),
        )

    def test_oneof_with_comment(self):
        parsed_oneof_with_comment = ProtoOneOf.match(
            None,
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
                None,
                ProtoIdentifier(None, "one_of_field"),
                [
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier(None, "name"),
                        ProtoInt(None, 4, ProtoIntSign.POSITIVE),
                    ),
                    ProtoSingleLineComment(None, " single-line comment!"),
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier(None, "sub_message"),
                        ProtoInt(None, 9, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier(None, "SubMessage"),
                        [],
                    ),
                ],
            ),
        )

    def test_oneof_normalize_removes_comment(self):
        normalized_oneof = ProtoOneOf.match(
            None,
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
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "name"),
                    ProtoInt(None, 4, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                    ProtoIdentifier(None, "sub_message"),
                    ProtoInt(None, 9, ProtoIntSign.POSITIVE),
                    False,
                    False,
                    ProtoFullIdentifier(None, "SubMessage"),
                    [],
                ),
            ],
        )

    def test_simple_map(self):
        parsed_map_simple = ProtoMap.match(
            None, "map <sfixed64, NestedMessage> my_map = 10;"
        )
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                None,
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier(None, "my_map"),
                ProtoInt(None, 10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
                [],
            ),
        )

    def test_map_without_spaces(self):
        map_without_spaces = ProtoMap.match(
            None, "map<sfixed64, NestedMessage> my_map = 10;"
        )
        self.assertEqual(
            map_without_spaces.node,
            ProtoMap(
                None,
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier(None, "my_map"),
                ProtoInt(None, 10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
                [],
            ),
        )

    def test_map_with_options(self):
        parsed_map_simple = ProtoMap.match(
            None,
            "map <sfixed64, NestedMessage> my_map = 10  [ java_package = 'com.example.foo', baz.bat = 48 ];",
        )
        self.assertEqual(parsed_map_simple.node.key_type, ProtoMapKeyTypesEnum.SFIXED64)
        self.assertEqual(
            parsed_map_simple.node.value_type, ProtoMapValueTypesEnum.ENUM_OR_MESSAGE
        )
        self.assertEqual(parsed_map_simple.node.name, ProtoIdentifier(None, "my_map"))
        self.assertEqual(
            parsed_map_simple.node.number, ProtoInt(None, 10, ProtoIntSign.POSITIVE)
        )
        self.assertEqual(
            parsed_map_simple.node.enum_or_message_type_name,
            ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
        )
        self.assertEqual(
            parsed_map_simple.node.options,
            [
                ProtoMessageFieldOption(
                    None,
                    ProtoIdentifier(None, "java_package"),
                    ProtoConstant(None, ProtoStringLiteral(None, "com.example.foo")),
                ),
                ProtoMessageFieldOption(
                    None,
                    ProtoFullIdentifier(None, "baz.bat"),
                    ProtoConstant(None, ProtoInt(None, 48, ProtoIntSign.POSITIVE)),
                ),
            ],
        )

    def test_map_message_value(self):
        parsed_map_simple = ProtoMap.match(
            None, "map <string, string> string_map = 11;"
        )
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                None,
                ProtoMapKeyTypesEnum.STRING,
                ProtoMapValueTypesEnum.STRING,
                ProtoIdentifier(None, "string_map"),
                ProtoInt(None, 11, ProtoIntSign.POSITIVE),
                None,
                [],
            ),
        )

    def test_message_parses_comments(self):
        parsed_comments = ProtoMessage.match(
            None,
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
            ),
        )
        self.assertEqual(
            parsed_comments.node.nodes,
            [
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "foo"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                ),
                ProtoSingleLineComment(None, " single-line comment!"),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.BOOL,
                    ProtoIdentifier(None, "bar"),
                    ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                ),
                ProtoMultiLineComment(
                    None,
                    "\n                    multiple\n                    line\n                    comment!\n                    ",
                ),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "baz"),
                    ProtoInt(None, 3, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_message_extends(self):
        parsed_extends = ProtoMessage.match(
            None,
            dedent(
                """
                message MyMessage {
                    string foo = 1;
                    extend SomeOtherMessage {
                        string foo = 2;
                    }
                }
                """.strip()
            ),
        )
        self.assertEqual(
            parsed_extends.node.nodes,
            [
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "foo"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                ),
                ProtoExtend(
                    None,
                    ProtoEnumOrMessageIdentifier(None, "SomeOtherMessage"),
                    [
                        ProtoMessageField(
                            None,
                            ProtoMessageFieldTypesEnum.STRING,
                            ProtoIdentifier(None, "foo"),
                            ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ],
        )

    def test_message_normalizes_away_comments(self):
        parsed_comments = ProtoMessage.match(
            None,
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
            ),
        ).node.normalize()
        self.assertEqual(
            parsed_comments.nodes,
            [
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "foo"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.BOOL,
                    ProtoIdentifier(None, "bar"),
                    ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    None,
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier(None, "baz"),
                    ProtoInt(None, 3, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_diff_same_message_returns_empty(self):
        pm1 = ProtoMessage(
            None,
            ProtoIdentifier(None, "MyMessage"),
            [],
        )
        pm2 = ProtoMessage(
            None,
            ProtoIdentifier(None, "MyMessage"),
            [],
        )
        self.assertEqual(ProtoMessage.diff(pm1, pm2), [])

    def test_diff_different_message_name_returns_empty(self):
        pm1 = ProtoMessage(
            None,
            ProtoIdentifier(None, "MyMessage"),
            [],
        )
        pm2 = ProtoMessage(
            None,
            ProtoIdentifier(None, "OtherMessage"),
            [],
        )
        self.assertEqual(ProtoMessage.diff(pm1, pm2), [])

    def test_diff_enum_added(self):
        pm1 = None
        pm2 = ProtoMessage(None, ProtoIdentifier(None, "MyMessage"), [])
        self.assertEqual(
            ProtoMessage.diff(pm1, pm2),
            [
                ProtoMessageAdded(
                    ProtoMessage(None, ProtoIdentifier(None, "MyMessage"), [])
                ),
            ],
        )

    def test_diff_message_removed(self):
        pm1 = ProtoMessage(None, ProtoIdentifier(None, "MyMessage"), [])
        pm2 = None
        self.assertEqual(
            ProtoMessage.diff(pm1, pm2),
            [
                ProtoMessageRemoved(
                    ProtoMessage(None, ProtoIdentifier(None, "MyMessage"), [])
                ),
            ],
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoMessage.diff_sets(set1, set2), [])

    def test_diff_sets_no_change_returns_empty(self):
        set1 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), []),
        ]
        self.assertEqual(ProtoMessage.diff_sets(set1, set1), [])

    def test_diff_sets_all_removed(self):
        set1 = []
        set2 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), []),
        ]
        diff = ProtoMessage.diff_sets(set1, set2)
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), [])
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_all_added(self):
        set1 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), []),
        ]
        set2 = []

        diff = ProtoMessage.diff_sets(set1, set2)
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), [])
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_mutually_exclusive(self):
        set1 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), []),
        ]
        set2 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage2"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage2"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage2"), []),
        ]
        diff = ProtoMessage.diff_sets(set1, set2)
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "FooMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "BarMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "BazMessage2"), [])
            ),
            diff,
        )
        self.assertEqual(6, len(diff))

    def test_diff_sets_overlap(self):

        set1 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), []),
        ]
        set2 = [
            ProtoMessage(None, ProtoIdentifier(None, "FooMessage2"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BarMessage"), []),
            ProtoMessage(None, ProtoIdentifier(None, "BazMessage2"), []),
        ]
        diff = ProtoMessage.diff_sets(set1, set2)
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                ProtoMessage(None, ProtoIdentifier(None, "BazMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "FooMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                ProtoMessage(None, ProtoIdentifier(None, "BazMessage2"), [])
            ),
            diff,
        )
        self.assertEqual(4, len(diff))


if __name__ == "__main__":
    unittest.main()
