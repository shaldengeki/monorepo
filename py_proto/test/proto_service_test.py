import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
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
            dedent(
                """
            service FooService {
                option (foo.bar).baz = "bat";
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
                rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
            }
        """.strip()
            )
        )
        self.assertEqual(
            test_service_all_features.node,
            ProtoService(
                ProtoIdentifier("FooService"),
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
        )
        self.assertEqual(
            test_service_all_features.node.serialize(),
            dedent(
                """
            service FooService {
            option (foo.bar).baz = "bat";
            rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
            rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
            rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
            }
            """
            ).strip(),
        )

    def test_service_empty(self):
        parsed_empty_service = ProtoService.match("""service FooService {}""")
        self.assertIsNotNone(parsed_empty_service)
        self.assertEqual(parsed_empty_service.node.name, ProtoIdentifier("FooService"))

        parsed_spaced_service = ProtoService.match(
            dedent(
                """
            service FooService {

            }
        """.strip()
            )
        )
        self.assertIsNotNone(parsed_spaced_service)
        self.assertEqual(
            parsed_spaced_service.node, ProtoService(ProtoIdentifier("FooService"), [])
        )

    def test_service_empty_statements(self):
        empty_statement_service = ProtoService.match(
            dedent(
                """
            service FooService {
                ;
                ;
            }
        """.strip()
            )
        )
        self.assertIsNotNone(empty_statement_service)
        self.assertEqual(
            empty_statement_service.node,
            ProtoService(ProtoIdentifier("FooService"), []),
        )

    def test_service_option(self):
        service_with_options = ProtoService.match(
            dedent(
                """
            service FooService {
                option (foo.bar).baz = "bat";
            }
        """.strip()
            )
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
                ProtoOption(
                    ProtoIdentifier("(foo.bar).baz"),
                    ProtoConstant(ProtoStringLiteral("bat")),
                )
            ],
        )

    def test_service_rpc_basic(self):
        service_with_options = ProtoService.match(
            dedent(
                """
            service FooService {
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse);
                rpc TwoRPC (TwoRPCRequest) returns (TwoRPCResponse);
                rpc ThreeRPC (ThreeRPCRequest) returns (ThreeRPCResponse);
            }
        """.strip()
            )
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
                ProtoServiceRPC(
                    ProtoIdentifier("OneRPC"),
                    ProtoEnumOrMessageIdentifier("OneRPCRequest"),
                    ProtoEnumOrMessageIdentifier("OneRPCResponse"),
                ),
                ProtoServiceRPC(
                    ProtoIdentifier("TwoRPC"),
                    ProtoEnumOrMessageIdentifier("TwoRPCRequest"),
                    ProtoEnumOrMessageIdentifier("TwoRPCResponse"),
                ),
                ProtoServiceRPC(
                    ProtoIdentifier("ThreeRPC"),
                    ProtoEnumOrMessageIdentifier("ThreeRPCRequest"),
                    ProtoEnumOrMessageIdentifier("ThreeRPCResponse"),
                ),
            ],
        )

    def test_service_rpc_stream(self):
        service_with_options = ProtoService.match(
            dedent(
                """
            service FooService {
                rpc OneRPC (stream OneRPCRequest) returns (OneRPCResponse);
                rpc TwoRPC (TwoRPCRequest) returns (stream TwoRPCResponse);
            }
        """.strip()
            )
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
                ProtoServiceRPC(
                    ProtoIdentifier("OneRPC"),
                    ProtoEnumOrMessageIdentifier("OneRPCRequest"),
                    ProtoEnumOrMessageIdentifier("OneRPCResponse"),
                    True,
                    False,
                ),
                ProtoServiceRPC(
                    ProtoIdentifier("TwoRPC"),
                    ProtoEnumOrMessageIdentifier("TwoRPCRequest"),
                    ProtoEnumOrMessageIdentifier("TwoRPCResponse"),
                    False,
                    True,
                ),
            ],
        )

    def test_service_rpc_options(self):
        service_with_options = ProtoService.match(
            dedent(
                """
            service FooService {
                rpc OneRPC (OneRPCRequest) returns (OneRPCResponse) { ; ; ; }
                rpc TwoRPC (TwoRPCRequest) returns (TwoRPCResponse) { option java_package = "com.example.foo"; option (foo.bar).baz = false; }
            }
        """.strip()
            )
        )
        self.assertEqual(
            service_with_options.node.nodes,
            [
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
        )


if __name__ == "__main__":
    unittest.main()
