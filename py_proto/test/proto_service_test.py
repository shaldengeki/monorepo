import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
from src.proto_comment import ProtoMultiLineComment, ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_option import ProtoOption
from src.proto_service import ProtoService, ProtoServiceRPC
from src.proto_string_literal import ProtoStringLiteral


class ServiceTest(unittest.TestCase):

    maxDiff = None

    def test_service_all_features(self):
        test_service_all_features = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                option (foo.bar).baz = "bat";
                // single-line comment!
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
                /*
                multiple
                line
                comment
                */
                rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
            }
        """.strip()
            ),
        )
        self.assertEqual(
            test_service_all_features.node,
            ProtoService(
                None,
                ProtoIdentifier(None, "FooService"),
                [
                    ProtoOption(
                        None,
                        ProtoIdentifier(None, "(foo.bar).baz"),
                        ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                    ),
                    ProtoSingleLineComment(None, " single-line comment!"),
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
                    ProtoMultiLineComment(
                        None,
                        "\n                multiple\n                line\n                comment\n                ",
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
        )
        self.assertEqual(
            test_service_all_features.node.serialize(),
            dedent(
                """
            service FooService {
            option (foo.bar).baz = "bat";
            // single-line comment!
            rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
            rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
            /*
                            multiple
                            line
                            comment
                            */
            rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
            }
            """
            ).strip(),
        )

    def test_service_empty(self):
        parsed_empty_service = ProtoService.match(None, """service FooService {}""")
        self.assertIsNotNone(parsed_empty_service)
        self.assertEqual(
            parsed_empty_service.node.name, ProtoIdentifier(None, "FooService")
        )

        parsed_spaced_service = ProtoService.match(
            None,
            dedent(
                """
            service FooService {

            }
        """.strip()
            ),
        )
        self.assertIsNotNone(parsed_spaced_service)
        self.assertEqual(
            parsed_spaced_service.node,
            ProtoService(None, ProtoIdentifier(None, "FooService"), []),
        )

    def test_service_empty_statements(self):
        empty_statement_service = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                ;
                ;
            }
        """.strip()
            ),
        )
        self.assertIsNotNone(empty_statement_service)
        self.assertEqual(
            empty_statement_service.node,
            ProtoService(None, ProtoIdentifier(None, "FooService"), []),
        )

    def test_service_option(self):
        service_with_options = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                option (foo.bar).baz = "bat";
            }
        """.strip()
            ),
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "(foo.bar).baz"),
                    ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                )
            ],
        )

    def test_service_rpc_basic(self):
        service_with_options = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                rpc TwoRPC (TwoRPCRequest) returns (TwoRPCResponse);
                rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse);
            }
        """.strip()
            ),
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
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
                ),
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "ThreeRPC"),
                    ProtoEnumOrMessageIdentifier(None, "ThreeRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "ThreeRPCResponse"),
                ),
            ],
        )

    def test_service_rpc_stream(self):
        service_with_options = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                rpc OneRPC (stream OneRPCRequest) returns (OneRPCResponse);
                rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
            }
        """.strip()
            ),
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "OneRPC"),
                    ProtoEnumOrMessageIdentifier(None, "OneRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "OneRPCResponse"),
                    True,
                    False,
                ),
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "TwoRPC"),
                    ProtoEnumOrMessageIdentifier(None, "TwoRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "TwoRPCResponse"),
                    False,
                    True,
                ),
            ],
        )

    def test_service_rpc_options(self):
        service_with_options = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse) { ; ; ; }
                rpc TwoRPC (TwoRPCRequest) returns (TwoRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
            }
        """.strip()
            ),
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
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
        )

    def test_service_parses_comments(self):
        service_with_comments = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                // single-line comment!
                rpc TwoRPC (TwoRPCRequest) returns (TwoRPCResponse);
                /*
                multiple
                line
                comment
                */
                rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse);
            }
        """.strip()
            ),
        )
        self.assertEqual(
            service_with_comments.node.nodes,
            [
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "OneRPC"),
                    ProtoEnumOrMessageIdentifier(None, "OneRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "OneRPCResponse"),
                ),
                ProtoSingleLineComment(None, " single-line comment!"),
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "TwoRPC"),
                    ProtoEnumOrMessageIdentifier(None, "TwoRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "TwoRPCResponse"),
                ),
                ProtoMultiLineComment(
                    None,
                    "\n                multiple\n                line\n                comment\n                ",
                ),
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "ThreeRPC"),
                    ProtoEnumOrMessageIdentifier(None, "ThreeRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "ThreeRPCResponse"),
                ),
            ],
        )

    def test_service_normalize_removes_comments(self):
        normalized_service = ProtoService.match(
            None,
            dedent(
                """
            service FooService {
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                // single-line comment!
                rpc TwoRPC (TwoRPCRequest) returns (TwoRPCResponse);
                /*
                multiple
                line
                comment
                */
                rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse);
            }
        """.strip()
            ),
        ).node.normalize()
        self.assertEqual(
            normalized_service.nodes,
            [
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "OneRPC"),
                    ProtoEnumOrMessageIdentifier(None, "OneRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "OneRPCResponse"),
                ),
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "ThreeRPC"),
                    ProtoEnumOrMessageIdentifier(None, "ThreeRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "ThreeRPCResponse"),
                ),
                ProtoServiceRPC(
                    None,
                    ProtoIdentifier(None, "TwoRPC"),
                    ProtoEnumOrMessageIdentifier(None, "TwoRPCRequest"),
                    ProtoEnumOrMessageIdentifier(None, "TwoRPCResponse"),
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
