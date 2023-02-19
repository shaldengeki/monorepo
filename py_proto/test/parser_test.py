import unittest
from textwrap import dedent

from src.parser import ParseError, Parser
from src.proto_bool import ProtoBool
from src.proto_comment import ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_enum import ProtoEnum, ProtoEnumValue
from src.proto_extend import ProtoExtend
from src.proto_extensions import ProtoExtensions
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
from src.proto_range import ProtoRange, ProtoRangeEnum
from src.proto_reserved import ProtoReserved
from src.proto_service import ProtoService, ProtoServiceRPC
from src.proto_string_literal import ProtoStringLiteral
from src.proto_syntax import ProtoSyntaxType


class IntTest(unittest.TestCase):

    maxDiff = None

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

                // Testing top-level single-line comment

                extend SomeExtendableMessage {
                    string some_extendable_field = 1;
                    // yay
                }

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
                    // testing nested comment
                    repeated string field_one = 1;
                    MyNestedMessage field_two = 2 [ bar.baz = true ];
                    extensions 8 to max;
                    oneof foo {
                        string name = 4;
                        option java_package = "com.example.foo";
                        SubMessage sub_message = 9 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                    }
                    map <sfixed64, NestedMessage> my_map = 10;
                }
                service MyGreatService {
                    option (foo.bar).baz = "bat";
                    rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                    rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
                    rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
                }
                """
            )
        )

        self.assertEqual(proto_file.syntax.syntax.value, ProtoSyntaxType.PROTO3.value)
        self.assertEqual(
            proto_file.imports,
            [
                ProtoImport(None, ProtoStringLiteral(None, "foo.proto"), public=True),
                ProtoImport(None, ProtoStringLiteral(None, "bar/baz.proto"), weak=True),
                ProtoImport(None, ProtoStringLiteral(None, "bat.proto")),
            ],
        )
        self.assertEqual(
            proto_file.options,
            [
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "java_package"),
                    ProtoConstant(None, ProtoStringLiteral(None, "my.test.package")),
                ),
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "(fully.qualified).option"),
                    ProtoConstant(
                        None, ProtoFloat(None, 3.14159265, ProtoFloatSign.POSITIVE)
                    ),
                ),
            ],
        )
        self.assertIn(
            ProtoEnum(
                None,
                ProtoIdentifier(None, "MyAwesomeEnum"),
                [
                    ProtoOption(
                        None,
                        ProtoIdentifier(None, "allow_alias"),
                        ProtoConstant(None, ProtoBool(None, True)),
                    ),
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "MAE_UNSPECIFIED"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        [],
                    ),
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "MAE_STARTED"),
                        ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                        [],
                    ),
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "MAE_RUNNING"),
                        ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                        [],
                    ),
                ],
            ),
            proto_file.nodes,
        )
        self.assertIn(
            ProtoMessage(
                None,
                ProtoIdentifier(None, "MyAwesomeMessage"),
                [
                    ProtoOption(
                        None,
                        ProtoFullIdentifier(None, "(bar).baz"),
                        ProtoConstant(
                            None, ProtoFloat(None, 1.2, ProtoFloatSign.POSITIVE)
                        ),
                    ),
                    ProtoEnum(
                        None,
                        ProtoIdentifier(None, "MyNestedEnum"),
                        [
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "MNE_UNDEFINED"),
                                ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                            ),
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "MNE_NEGATIVE"),
                                ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
                            ),
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "MNE_POSITIVE"),
                                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                            ),
                        ],
                    ),
                    ProtoMessage(None, ProtoIdentifier(None, "MyNestedMessage"), []),
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
                    ProtoReserved(None, fields=[ProtoIdentifier(None, "yay")]),
                    ProtoSingleLineComment(None, " testing nested comment"),
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier(None, "field_one"),
                        ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                        True,
                    ),
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier(None, "field_two"),
                        ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoIdentifier(None, "MyNestedMessage"),
                        [
                            ProtoMessageFieldOption(
                                None,
                                ProtoFullIdentifier(None, "bar.baz"),
                                ProtoConstant(None, ProtoBool(None, True)),
                            )
                        ],
                    ),
                    ProtoExtensions(None, [ProtoRange(None, 8, ProtoRangeEnum.MAX)]),
                    ProtoOneOf(
                        None,
                        ProtoIdentifier(None, "foo"),
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
                                            None,
                                            ProtoInt(None, 100, ProtoIntSign.NEGATIVE),
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
                ],
            ),
            proto_file.nodes,
        )

        self.assertIn(
            ProtoService(
                None,
                ProtoIdentifier(None, "MyGreatService"),
                [
                    ProtoOption(
                        None,
                        ProtoIdentifier(None, "(foo.bar).baz"),
                        ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                    ),
                    ProtoServiceRPC(
                        None,
                        ProtoIdentifier(None, "OneRPC"),
                        ProtoEnumOrMessageIdentifier(None, "OneRPCRequest"),
                        ProtoEnumOrMessageIdentifier(None, "OneRPCResponse"),
                    ),
                    ProtoServiceRPC(
                        None,
                        ProtoIdentifier(None, "TwoRPC"),
                        ProtoEnumOrMessageIdentifier(None, "TwoRPCRequest"),
                        ProtoEnumOrMessageIdentifier(None, "TwoRPCResponse"),
                        False,
                        True,
                    ),
                    ProtoServiceRPC(
                        None,
                        ProtoIdentifier(None, "ThreeRPC"),
                        ProtoEnumOrMessageIdentifier(None, "ThreeRPCRequest"),
                        ProtoEnumOrMessageIdentifier(None, "ThreeRPCResponse"),
                        False,
                        False,
                        [
                            ProtoOption(
                                None,
                                ProtoIdentifier(None, "java_package"),
                                ProtoConstant(
                                    None, ProtoStringLiteral(None, "com.example.foo")
                                ),
                            ),
                            ProtoOption(
                                None,
                                ProtoFullIdentifier(None, "(foo.bar).baz"),
                                ProtoConstant(None, ProtoBool(None, False)),
                            ),
                        ],
                    ),
                ],
            ),
            proto_file.nodes,
        )

        self.assertIn(
            ProtoExtend(
                None,
                ProtoIdentifier(None, "SomeExtendableMessage"),
                [
                    ProtoMessageField(
                        None,
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier(None, "some_extendable_field"),
                        ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                    ),
                    ProtoSingleLineComment(None, " yay"),
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

                // Testing top-level comment!

                extend SomeExtendableMessage {
                    string some_extendable_field = 1;
                    // yay
                }

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
                    extensions 11 to max;
                }
                service MyGreatService {
                    option (foo.bar).baz = "bat";
                    // Testing nested comment!
                    rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                    rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
                    rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
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

                    // Testing top-level comment!

                    extend SomeExtendableMessage {
                    string some_extendable_field = 1;
                    // yay
                    }

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
                    extensions 11 to max;
                    }

                    service MyGreatService {
                    option (foo.bar).baz = "bat";
                    // Testing nested comment!
                    rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                    rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
                    rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
                    }
                    """
            ).strip(),
        )


if __name__ == "__main__":
    unittest.main()
