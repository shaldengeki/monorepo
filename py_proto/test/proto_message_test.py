# type: ignore

import unittest
from textwrap import dedent

from py_proto.proto_bool import ProtoBool
from py_proto.proto_comment import ProtoMultiLineComment, ProtoSingleLineComment
from py_proto.proto_constant import ProtoConstant
from py_proto.proto_enum import ProtoEnum, ProtoEnumValue
from py_proto.proto_extend import ProtoExtend
from py_proto.proto_extensions import ProtoExtensions
from py_proto.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from py_proto.proto_int import ProtoInt, ProtoIntSign
from py_proto.proto_map import ProtoMap, ProtoMapKeyTypesEnum, ProtoMapValueTypesEnum
from py_proto.proto_message import ProtoMessage, ProtoMessageAdded, ProtoMessageRemoved
from py_proto.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldOption,
    ProtoMessageFieldTypesEnum,
)
from py_proto.proto_oneof import ProtoOneOf
from py_proto.proto_option import ProtoOption
from py_proto.proto_range import ProtoRange, ProtoRangeEnum
from py_proto.proto_reserved import ProtoReserved
from py_proto.proto_string_literal import ProtoStringLiteral


class MessageTest(unittest.TestCase):
    maxDiff = None

    DEFAULT_PARENT = ProtoMessage(ProtoIdentifier("DefaultParent"), [])

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
            ),
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
                    ],
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
            ),
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
            ),
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
            ),
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
            ),
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
            ),
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
            ),
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
                        ],
                    ),
                    ProtoReserved(
                        fields=[
                            ProtoIdentifier("foo"),
                            ProtoIdentifier("barBaz"),
                        ],
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
            ),
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
            ),
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
                    "\n                    multiple\n                    line\n                    comment!\n                    ",
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("baz"),
                    ProtoInt(3, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_message_extends(self):
        parsed_extends = ProtoMessage.match(
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
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("foo"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                ),
                ProtoExtend(
                    ProtoEnumOrMessageIdentifier("SomeOtherMessage"),
                    [
                        ProtoMessageField(
                            ProtoMessageFieldTypesEnum.STRING,
                            ProtoIdentifier("foo"),
                            ProtoInt(2, ProtoIntSign.POSITIVE),
                        )
                    ],
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
            ),
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

    def test_diff_same_message_returns_empty(self):
        pm1 = ProtoMessage(
            ProtoIdentifier("MyMessage"),
            [],
        )
        pm2 = ProtoMessage(
            ProtoIdentifier("MyMessage"),
            [],
        )
        self.assertEqual(ProtoMessage.diff(self.DEFAULT_PARENT, pm1, pm2), [])

    def test_diff_different_message_name_returns_empty(self):
        pm1 = ProtoMessage(
            ProtoIdentifier("MyMessage"),
            [],
        )
        pm2 = ProtoMessage(
            ProtoIdentifier("OtherMessage"),
            [],
        )
        self.assertEqual(ProtoMessage.diff(self.DEFAULT_PARENT, pm1, pm2), [])

    def test_diff_message_added(self):
        pm1 = None
        pm2 = ProtoMessage(ProtoIdentifier("MyMessage"), [])
        self.assertEqual(
            ProtoMessage.diff(self.DEFAULT_PARENT, pm1, pm2),
            [
                ProtoMessageAdded(
                    self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("MyMessage"), [])
                ),
            ],
        )

    def test_diff_message_removed(self):
        pm1 = ProtoMessage(ProtoIdentifier("MyMessage"), [])
        pm2 = None
        self.assertEqual(
            ProtoMessage.diff(self.DEFAULT_PARENT, pm1, pm2),
            [
                ProtoMessageRemoved(
                    self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("MyMessage"), [])
                ),
            ],
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoMessage.diff_sets(self.DEFAULT_PARENT, set1, set2), [])

    def test_diff_sets_no_change_returns_empty(self):
        set1 = [
            ProtoMessage(ProtoIdentifier("FooMessage"), []),
            ProtoMessage(ProtoIdentifier("BarMessage"), []),
            ProtoMessage(ProtoIdentifier("BazMessage"), []),
        ]
        self.assertEqual(ProtoMessage.diff_sets(self.DEFAULT_PARENT, set1, set1), [])

    def test_diff_sets_all_removed(self):
        set1 = [
            ProtoMessage(ProtoIdentifier("FooMessage"), []),
            ProtoMessage(ProtoIdentifier("BarMessage"), []),
            ProtoMessage(ProtoIdentifier("BazMessage"), []),
        ]
        set2 = []
        diff = ProtoMessage.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BarMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BazMessage"), [])
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_all_added(self):
        set1 = []
        set2 = [
            ProtoMessage(ProtoIdentifier("FooMessage"), []),
            ProtoMessage(ProtoIdentifier("BarMessage"), []),
            ProtoMessage(ProtoIdentifier("BazMessage"), []),
        ]

        diff = ProtoMessage.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BarMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BazMessage"), [])
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_mutually_exclusive(self):
        set1 = [
            ProtoMessage(ProtoIdentifier("FooMessage"), []),
            ProtoMessage(ProtoIdentifier("BarMessage"), []),
            ProtoMessage(ProtoIdentifier("BazMessage"), []),
        ]
        set2 = [
            ProtoMessage(ProtoIdentifier("FooMessage2"), []),
            ProtoMessage(ProtoIdentifier("BarMessage2"), []),
            ProtoMessage(ProtoIdentifier("BazMessage2"), []),
        ]
        diff = ProtoMessage.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("FooMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BarMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BazMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BarMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BazMessage"), [])
            ),
            diff,
        )
        self.assertEqual(6, len(diff))

    def test_diff_sets_overlap(self):

        set1 = [
            ProtoMessage(ProtoIdentifier("FooMessage"), []),
            ProtoMessage(ProtoIdentifier("BarMessage"), []),
            ProtoMessage(ProtoIdentifier("BazMessage"), []),
        ]
        set2 = [
            ProtoMessage(ProtoIdentifier("FooMessage2"), []),
            ProtoMessage(ProtoIdentifier("BarMessage"), []),
            ProtoMessage(ProtoIdentifier("BazMessage2"), []),
        ]
        diff = ProtoMessage.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("FooMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageAdded(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BazMessage2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("FooMessage"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoMessageRemoved(
                self.DEFAULT_PARENT, ProtoMessage(ProtoIdentifier("BazMessage"), [])
            ),
            diff,
        )
        self.assertEqual(4, len(diff))


if __name__ == "__main__":
    unittest.main()
