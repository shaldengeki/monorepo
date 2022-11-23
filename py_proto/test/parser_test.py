import unittest
from textwrap import dedent

from src.parser import ParseError, Parser
from src.proto_bool import ProtoBool
from src.proto_constant import ProtoConstant
from src.proto_enum import ProtoEnum, ProtoEnumValue
from src.proto_float import ProtoFloat, ProtoFloatSign
from src.proto_identifier import ProtoIdentifier
from src.proto_import import ProtoImport
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_option import ProtoOption
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
                    """
            ).strip(),
        )


if __name__ == "__main__":
    unittest.main()
