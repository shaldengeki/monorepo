import unittest

from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldAdded,
    ProtoMessageFieldNameChanged,
    ProtoMessageFieldRemoved,
    ProtoMessageFieldTypesEnum,
)


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
                ProtoMessageFieldTypesEnum.BOOL,
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

    def test_diff_same_field_returns_empty(self):
        pmf1 = ProtoMessageField(
            None,
            ProtoMessageFieldTypesEnum.FLOAT,
            ProtoIdentifier(None, "my_message_field"),
            ProtoInt(None, 10, ProtoIntSign.POSITIVE),
        )
        pmf2 = ProtoMessageField(
            None,
            ProtoMessageFieldTypesEnum.FLOAT,
            ProtoIdentifier(None, "my_message_field"),
            ProtoInt(None, 10, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(ProtoMessageField.diff(None, pmf1, pmf2), [])

    def test_diff_different_field_name_same_number_returns_field_diff(self):
        pmf1 = ProtoMessageField(
            None,
            ProtoMessageFieldTypesEnum.FLOAT,
            ProtoIdentifier(None, "foo"),
            ProtoInt(None, 10, ProtoIntSign.POSITIVE),
        )
        pmf2 = ProtoMessageField(
            None,
            ProtoMessageFieldTypesEnum.FLOAT,
            ProtoIdentifier(None, "bar"),
            ProtoInt(None, 10, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            [
                ProtoMessageFieldNameChanged(
                    None,
                    pmf1,
                    pmf2.name,
                )
            ],
            ProtoMessageField.diff(None, pmf1, pmf2),
        )

    def test_diff_field_removed(self):
        pmf1 = ProtoMessageField(
            None,
            ProtoMessageFieldTypesEnum.FLOAT,
            ProtoIdentifier(None, "foo"),
            ProtoInt(None, 10, ProtoIntSign.POSITIVE),
        )
        pmf2 = None
        self.assertEqual(
            [
                ProtoMessageFieldRemoved(None, pmf1),
            ],
            ProtoMessageField.diff(None, pmf1, pmf2),
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoMessageField.diff_sets(None, set1, set2), [])

    def test_diff_sets_no_change(self):
        set1 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar"),
                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz"),
                ProtoInt(None, 3, ProtoIntSign.POSITIVE),
            ),
        ]
        self.assertEqual([], ProtoMessageField.diff_sets(None, set1, set1))

    def test_diff_sets_all_removed(self):
        set1 = []
        set2 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar"),
                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz"),
                ProtoInt(None, 3, ProtoIntSign.POSITIVE),
            ),
        ]
        diff = ProtoMessageField.diff_sets(None, set1, set2)

        for pmf in set2:
            self.assertIn(
                ProtoMessageFieldRemoved(None, pmf),
                diff,
            )
        self.assertEqual(3, len(diff))

    def test_diff_sets_all_added(self):
        set1 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar"),
                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz"),
                ProtoInt(None, 3, ProtoIntSign.POSITIVE),
            ),
        ]
        set2 = []
        diff = ProtoMessageField.diff_sets(None, set1, set2)

        for pmf in set1:
            self.assertIn(
                ProtoMessageFieldAdded(None, pmf),
                diff,
            )

        self.assertEqual(3, len(diff))

    def test_diff_sets_mutually_exclusive(self):
        set1 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar"),
                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz"),
                ProtoInt(None, 3, ProtoIntSign.POSITIVE),
            ),
        ]
        set2 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo2"),
                ProtoInt(None, 4, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar2"),
                ProtoInt(None, 5, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz2"),
                ProtoInt(None, 6, ProtoIntSign.POSITIVE),
            ),
        ]

        diff = ProtoMessageField.diff_sets(None, set1, set2)

        for pmf in set1:
            self.assertIn(
                ProtoMessageFieldAdded(None, pmf),
                diff,
            )

        for pmf in set2:
            self.assertIn(
                ProtoMessageFieldRemoved(None, pmf),
                diff,
            )

        self.assertEqual(6, len(diff))

    def test_diff_sets_overlap(self):
        set1 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo"),
                ProtoInt(None, 1, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar"),
                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz"),
                ProtoInt(None, 3, ProtoIntSign.POSITIVE),
            ),
        ]
        set2 = [
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "foo2"),
                ProtoInt(None, 4, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "bar"),
                ProtoInt(None, 2, ProtoIntSign.POSITIVE),
            ),
            ProtoMessageField(
                None,
                ProtoMessageFieldTypesEnum.FLOAT,
                ProtoIdentifier(None, "baz2"),
                ProtoInt(None, 6, ProtoIntSign.POSITIVE),
            ),
        ]

        diff = ProtoMessageField.diff_sets(None, set1, set2)

        self.assertIn(
            ProtoMessageFieldRemoved(None, set1[0]),
            diff,
        )

        self.assertIn(
            ProtoMessageFieldRemoved(None, set1[2]),
            diff,
        )
        self.assertIn(
            ProtoMessageFieldAdded(None, set2[0]),
            diff,
        )
        self.assertIn(
            ProtoMessageFieldAdded(None, set2[2]),
            diff,
        )

        self.assertEqual(4, len(diff))


if __name__ == "__main__":
    unittest.main()
