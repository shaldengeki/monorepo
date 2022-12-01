import unittest
from textwrap import dedent

from src.proto_constant import ProtoConstant
from src.proto_identifier import ProtoIdentifier
from src.proto_option import ProtoOption
from src.proto_service import ProtoService
from src.proto_string_literal import ProtoStringLiteral


class ServiceTest(unittest.TestCase):
    def test_service_all_features(self):
        test_service_all_features = ProtoService.match(
            dedent(
                """
            service FooService {
                option (foo.bar).baz = "bat";
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
                    )
                ],
            ),
        )
        self.assertEqual(
            test_service_all_features.node.serialize(),
            dedent(
                """
            service FooService {
            option (foo.bar).baz = "bat";
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

    def test_service_empty_statements(self):
        service_with_options = ProtoService.match(
            dedent(
                """
            service FooService {
                option (foo.bar).baz = "bat";
            }
        """.strip()
            )
        )
        self.assertIsNotNone(service_with_options)
        self.assertEqual(
            service_with_options.node,
            ProtoService(
                ProtoIdentifier("FooService"),
                [
                    ProtoOption(
                        ProtoIdentifier("(foo.bar).baz"),
                        ProtoConstant(ProtoStringLiteral("bat")),
                    )
                ],
            ),
        )


if __name__ == "__main__":
    unittest.main()
