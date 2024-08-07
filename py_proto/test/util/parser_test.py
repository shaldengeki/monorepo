# type: ignore

import unittest
from textwrap import dedent

from py_proto.proto_bool import ProtoBool
from py_proto.proto_comment import ProtoSingleLineComment
from py_proto.proto_constant import ProtoConstant
from py_proto.proto_enum import ProtoEnum, ProtoEnumValue
from py_proto.proto_extend import ProtoExtend
from py_proto.proto_extensions import ProtoExtensions
from py_proto.proto_float import ProtoFloat, ProtoFloatSign
from py_proto.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from py_proto.proto_import import ProtoImport
from py_proto.proto_int import ProtoInt, ProtoIntSign
from py_proto.proto_map import ProtoMap, ProtoMapKeyTypesEnum, ProtoMapValueTypesEnum
from py_proto.proto_message import ProtoMessage, ProtoOneOf
from py_proto.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldOption,
    ProtoMessageFieldTypesEnum,
)
from py_proto.proto_option import ProtoOption
from py_proto.proto_range import ProtoRange, ProtoRangeEnum
from py_proto.proto_reserved import ProtoReserved
from py_proto.proto_service import ProtoService, ProtoServiceRPC
from py_proto.proto_string_literal import ProtoStringLiteral
from py_proto.proto_syntax import ProtoSyntaxType
from py_proto.util.parser import ParseError, Parser


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
                        ProtoIdentifier("allow_alias"),
                        ProtoConstant(ProtoBool(True)),
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
                        ProtoFullIdentifier("(bar).baz"),
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
                            ProtoRange(
                                ProtoInt(1, ProtoIntSign.POSITIVE),
                                ProtoInt(3, ProtoIntSign.POSITIVE),
                            )
                        ],
                    ),
                    ProtoReserved(fields=[ProtoIdentifier("yay")]),
                    ProtoSingleLineComment(" testing nested comment"),
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
                        False,
                        ProtoIdentifier("MyNestedMessage"),
                        [
                            ProtoMessageFieldOption(
                                ProtoFullIdentifier("bar.baz"),
                                ProtoConstant(ProtoBool(True)),
                            )
                        ],
                    ),
                    ProtoExtensions([ProtoRange(8, ProtoRangeEnum.MAX)]),
                    ProtoOneOf(
                        ProtoIdentifier("foo"),
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
                                        ProtoConstant(
                                            ProtoInt(100, ProtoIntSign.NEGATIVE),
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

        self.assertIn(
            ProtoService(
                ProtoIdentifier("MyGreatService"),
                [
                    ProtoOption(
                        ProtoIdentifier("(foo.bar).baz"),
                        ProtoConstant(ProtoStringLiteral("bat")),
                    ),
                    ProtoServiceRPC(
                        ProtoIdentifier("OneRPC"),
                        ProtoEnumOrMessageIdentifier("OneRPCRequest"),
                        ProtoEnumOrMessageIdentifier("OneRPCResponse"),
                    ),
                    ProtoServiceRPC(
                        ProtoIdentifier("TwoRPC"),
                        ProtoEnumOrMessageIdentifier("TwoRPCRequest"),
                        ProtoEnumOrMessageIdentifier("TwoRPCResponse"),
                        False,
                        True,
                    ),
                    ProtoServiceRPC(
                        ProtoIdentifier("ThreeRPC"),
                        ProtoEnumOrMessageIdentifier("ThreeRPCRequest"),
                        ProtoEnumOrMessageIdentifier("ThreeRPCResponse"),
                        False,
                        False,
                        [
                            ProtoOption(
                                ProtoIdentifier("java_package"),
                                ProtoConstant(ProtoStringLiteral("com.example.foo")),
                            ),
                            ProtoOption(
                                ProtoFullIdentifier("(foo.bar).baz"),
                                ProtoConstant(ProtoBool(False)),
                            ),
                        ],
                    ),
                ],
            ),
            proto_file.nodes,
        )

        self.assertIn(
            ProtoExtend(
                ProtoIdentifier("SomeExtendableMessage"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("some_extendable_field"),
                        ProtoInt(1, ProtoIntSign.POSITIVE),
                    ),
                    ProtoSingleLineComment(" yay"),
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
