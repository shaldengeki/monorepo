import unittest

from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_message_field import ProtoMessageField, ProtoMessageFieldTypesEnum


class MessageFieldTest(unittest.TestCase):
    maxDiff = None

    def test_field_optional_default_false(self):
        string_field = ProtoMessageField.match(None, "string single_field = 1;")
        self.assertEqual(
            string_field.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier(None, "single_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                False,
                False,
            ),
        )

    def test_field_optional_set(self):
        string_field = ProtoMessageField.match(
            None, "optional string single_field = 1;".strip()
        )
        self.assertEqual(
            string_field.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier(None, "single_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                False,
                True,
            ),
        )

    def test_field_cannot_have_repeated_and_optional(self):
        with self.assertRaises(ValueError):
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier(None, "single_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                True,
                True,
            )

    def test_message_field_starts_with_underscore(self):
        parsed_undescored_field = ProtoMessageField.match(
            None, "string _test_field = 1;"
        )
        self.assertEqual(
            parsed_undescored_field.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier(None, "_test_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
        )
        parsed_double_undescored_field = ProtoMessageField.match(
            None, "bool __test_field = 1;"
        )
        self.assertEqual(
            parsed_double_undescored_field.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.STRING,
                ProtoIdentifier(None, "__test_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
        )

    def test_field_repeated(self):
        parsed_message_with_repeated_field_simple = ProtoMessageField.match(
            None, "repeated bool repeated_field = 3;"
        )
        self.assertEqual(
            parsed_message_with_repeated_field_simple.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.BOOL,
                ProtoIdentifier(None, "repeated_field"),
                ProtoInt(None, 3, ProtoIntSign.POSITIVE),
                True,
            ),
        )

    def test_field_enum_or_message(self):
        parsed_message_with_repeated_field_simple = ProtoMessageField.match(
            None, "foo.SomeEnumOrMessage enum_or_message_field = 1;"
        )
        self.assertEqual(
            parsed_message_with_repeated_field_simple.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier(None, "enum_or_message_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                False,
                False,
                ProtoFullIdentifier(None, "foo.SomeEnumOrMessage"),
            ),
        )

    def test_field_starts_with_period(self):
        parsed_field_with_type_starting_with_period = ProtoMessageField.match(
            None, ".google.proto.FooType enum_or_message_field = 1;"
        )
        self.assertEqual(
            parsed_field_with_type_starting_with_period.node,
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier(None, "enum_or_message_field"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                False,
                False,
                ProtoEnumOrMessageIdentifier(None, ".google.proto.FooType"),
            ),
        )
