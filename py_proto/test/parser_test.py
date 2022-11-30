import unittest
from textwrap import dedent

from src.parser import ParseError, Parser
from src.proto_bool import ProtoBool
from src.proto_constant import ProtoConstant
from src.proto_enum import ProtoEnum, ProtoEnumValue
from src.proto_float import ProtoFloat, ProtoFloatSign
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_import import ProtoImport
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
from src.proto_reserved import ProtoReserved, ProtoReservedRange
from src.proto_string_literal import ProtoStringLiteral
from src.proto_syntax import ProtoSyntaxType


class IntTest(unittest.TestCase):
    def test_parser(self):
        proto_file = Parser.loads(
            dedent(
                """
                syntax = "proto3";

                package foo.bar.baz;

                import public "foo.proto";
                import weak "bar/baz.proto";
                import "bat.proto";

                option java_package = "my.test.package";
                option (fully.qualified).option = .314159265e1;

                enum MyAwesomeEnum {
                    option allow_alias = true;
                    MAE_UNSPECIFIED = 0;
                    MAE_STARTED = 1;
                    MAE_RUNNING = 2;
                }

                message MyAwesomeMessage {
                    option (bar).baz = 1.2;
                    enum MyNestedEnum {
                        MNE_UNDEFINED = 0;
                        MNE_NEGATIVE = -1;
                        MNE_POSITIVE = 2;
                    }
                    message MyNestedMessage {
                    }
                    reserved 1 to 3;
                    reserved "yay";
                    repeated string field_one = 1;
                    MyNestedMessage field_two = 2 [ bar.baz = true ];
                    oneof foo {
                        string name = 4;
                        option java_package = "com.example.foo";
                        SubMessage sub_message = 9 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                    }
                    map <sfixed64, NestedMessage> my_map = 10;
                }
                """
            )
        )

        self.assertEqual(proto_file.syntax.syntax.value, ProtoSyntaxType.PROTO3.value)
        self.assertEqual(
            proto_file.imports,
            [
                ProtoImport(ProtoStringLiteral("foo.proto"), public=True),
                ProtoImport(ProtoStringLiteral("bar/baz.proto"), weak=True),
                ProtoImport(ProtoStringLiteral("bat.proto")),
            ],
        )
        self.assertEqual(
            proto_file.options,
            [
                ProtoOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("my.test.package")),
                ),
                ProtoOption(
                    ProtoIdentifier("(fully.qualified).option"),
                    ProtoConstant(ProtoFloat(3.14159265, ProtoFloatSign.POSITIVE)),
                ),
            ],
        )
        self.assertIn(
            ProtoEnum(
                ProtoIdentifier("MyAwesomeEnum"),
                [
                    ProtoOption(
                        ProtoIdentifier("allow_alias"), ProtoConstant(ProtoBool(True))
                    ),
                    ProtoEnumValue(
                        ProtoIdentifier("MAE_UNSPECIFIED"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                        [],
                    ),
                    ProtoEnumValue(
                        ProtoIdentifier("MAE_STARTED"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                        [],
                    ),
                    ProtoEnumValue(
                        ProtoIdentifier("MAE_RUNNING"),
                        ProtoInt(2, ProtoIntSign.POSITIVE),
                        [],
                    ),
                ],
            ),
            proto_file.nodes,
        )
        self.assertIn(
            ProtoMessage(
                ProtoIdentifier("MyAwesomeMessage"),
                [
                    ProtoOption(
                        ProtoIdentifier("(bar).baz"),
                        ProtoConstant(ProtoFloat(1.2, ProtoFloatSign.POSITIVE)),
                    ),
                    ProtoEnum(
                        ProtoIdentifier("MyNestedEnum"),
                        [
                            ProtoEnumValue(
                                ProtoIdentifier("MNE_UNDEFINED"),
                                ProtoInt(0, ProtoIntSign.POSITIVE),
                            ),
                            ProtoEnumValue(
                                ProtoIdentifier("MNE_NEGATIVE"),
                                ProtoInt(1, ProtoIntSign.NEGATIVE),
                            ),
                            ProtoEnumValue(
                                ProtoIdentifier("MNE_POSITIVE"),
                                ProtoInt(2, ProtoIntSign.POSITIVE),
                            ),
                        ],
                    ),
                    ProtoMessage(ProtoIdentifier("MyNestedMessage"), []),
                    ProtoReserved(
                        ranges=[
                            ProtoReservedRange(
                                ProtoInt(1, ProtoIntSign.POSITIVE),
                                ProtoInt(3, ProtoIntSign.POSITIVE),
                            )
                        ]
                    ),
                    ProtoReserved(fields=[ProtoIdentifier("yay")]),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("field_one"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                        True,
                    ),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier("field_two"),
                        ProtoInt(2, ProtoIntSign.POSITIVE),
                        False,
                        ProtoIdentifier("MyNestedMessage"),
                        [
                            ProtoMessageFieldOption(
                                ProtoFullIdentifier("bar.baz"),
                                ProtoConstant(ProtoBool(True)),
                            )
                        ],
                    ),
                    ProtoOneOf(
                        ProtoIdentifier("foo"),
                        [
                            ProtoMessageField(
                                ProtoMessageFieldTypesEnum.STRING,
                                ProtoIdentifier("name"),
                                ProtoInt(4, ProtoIntSign.POSITIVE),
                                False,
                                None,
                                [],
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
                                ProtoFullIdentifier("SubMessage"),
                                [
                                    ProtoMessageFieldOption(
                                        ProtoIdentifier("(bar.baz).bat"),
                                        ProtoConstant(ProtoStringLiteral("bat")),
                                    ),
                                    ProtoMessageFieldOption(
                                        ProtoIdentifier("baz.bat"),
                                        ProtoConstant(
                                            ProtoInt(100, ProtoIntSign.NEGATIVE)
                                        ),
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
                ],
            ),
            proto_file.nodes,
        )

    def test_parser_no_syntax(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """
                    package foo.bar.baz;

                    import public "foo.proto";
                    import weak "bar/baz.proto";
                    import "bat.proto";

                    option java_package = "my.test.package";
                    option (fully.qualified).option = .314159265e1;
                    """
                )
            )

    def test_parser_typo(self):
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """
                    syntax = "proto3";

                    package foo.bar.baz
                    """
                )
            )
        with self.assertRaises(ParseError):
            Parser.loads(
                dedent(
                    """
                    syntax = "proto3";

                    package foo.bar.baz;

                    import public "foo.proto";
                    import weak "ba
                    """
                )
            )

    def test_serialize(self):
        proto_file = Parser.loads(
            dedent(
                """
                syntax = "proto3";

                package foo.bar.baz;

                import public "foo.proto";
                import weak 'bar/baz.proto';
                import "bat.proto";

                option java_package = "my.test.package";
                option (fully.qualified).option = .314159265e1;

                enum MyAwesomeEnum {
                    MAE_UNSPECIFIED = 0;
                    option allow_alias = true;
                    MAE_STARTED = 1;
                    MAE_RUNNING = 2;
                }

                message MyAwesomeMessage {
                    option (bar).baz = 1.2;
                    enum MyNestedEnum {
                        MNE_UNDEFINED = 0;
                        MNE_NEGATIVE = -1;
                        MNE_POSITIVE = 2;
                    }
                    message MyNestedMessage {}
                    reserved 1 to 3;
                    reserved "yay";
                    repeated string field_one = 1;
                    MyNestedMessage field_two = 2 [ .bar.baz = true ];
                    oneof foo {
                        string name = 4;
                        option java_package = "com.example.foo";
                        SubMessage sub_message = 9 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                    }
                    map <sfixed64, NestedMessage> my_map = 10;
                }
                """
            )
        )
        self.assertEqual(
            proto_file.serialize(),
            dedent(
                """
                    syntax = "proto3";

                    package foo.bar.baz;

                    import public "foo.proto";
                    import weak 'bar/baz.proto';
                    import "bat.proto";

                    option java_package = "my.test.package";
                    option (fully.qualified).option = 3.14159265;

                    enum MyAwesomeEnum {
                    MAE_UNSPECIFIED = 0;
                    option allow_alias = true;
                    MAE_STARTED = 1;
                    MAE_RUNNING = 2;
                    }

                    message MyAwesomeMessage {
                    option (bar).baz = 1.2;
                    enum MyNestedEnum {
                    MNE_UNDEFINED = 0;
                    MNE_NEGATIVE = -1;
                    MNE_POSITIVE = 2;
                    }
                    message MyNestedMessage {
                    }
                    reserved 1 to 3;
                    reserved "yay";
                    repeated string field_one = 1;
                    MyNestedMessage field_two = 2 [ .bar.baz = true ];
                    oneof foo {
                    string name = 4;
                    option java_package = "com.example.foo";
                    SubMessage sub_message = 9 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                    }
                    map <sfixed64, NestedMessage> my_map = 10;
                    }
                    """
            ).strip(),
        )


if __name__ == "__main__":
    unittest.main()
