import unittest
from textwrap import dedent

from src.proto_comment import ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_identifier import ProtoFullIdentifier, ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldAdded,
    ProtoMessageFieldNameChanged,
    ProtoMessageFieldOption,
    ProtoMessageFieldRemoved,
    ProtoMessageFieldTypesEnum,
)
from src.proto_oneof import ProtoOneOf, ProtoOneOfAdded, ProtoOneOfRemoved
from src.proto_option import ProtoOption
from src.proto_string_literal import ProtoStringLiteral


class OneOfTest(unittest.TestCase):
    maxDiff = None

    DEFAULT_PARENT = ProtoOneOf(
        ProtoIdentifier("default_parent"),
        [],
    )

    def test_oneof_empty(self):
        parsed_oneof_empty = ProtoOneOf.match(dedent("oneof one_of_field {}".strip()))
        self.assertEqual(
            parsed_oneof_empty.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [],
            ),
        )

    def test_oneof_empty_statements(self):
        parsed_oneof_empty = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                ;
                ;
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_empty.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [],
            ),
        )

    def test_oneof_basic_fields(self):
        parsed_oneof_basic_fields = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4;
                SubMessage sub_message = 9;
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_basic_fields.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("name"),
                        ProtoInt(4, ProtoIntSign.POSITIVE),
                    ),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier("sub_message"),
                        ProtoInt(9, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier("SubMessage"),
                        [],
                    ),
                ],
            ),
        )

    def test_oneof_options(self):
        parsed_oneof_options = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                option java_package = "com.example.foo";
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_options.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoOption(
                        ProtoIdentifier("java_package"),
                        ProtoConstant(ProtoStringLiteral("com.example.foo")),
                    ),
                ],
            ),
        )

    def test_oneof_field_option(self):
        parsed_oneof_field_option = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4 [ (bar.baz).bat = "bat", baz.bat = -100 ];
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_field_option.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("name"),
                        ProtoInt(4, ProtoIntSign.POSITIVE),
                        False,
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
                    )
                ],
            ),
        )

    def test_oneof_with_comment(self):
        parsed_oneof_with_comment = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4;
                // single-line comment!
                SubMessage sub_message = 9;
            }""".strip()
            ),
        )
        self.assertEqual(
            parsed_oneof_with_comment.node,
            ProtoOneOf(
                ProtoIdentifier("one_of_field"),
                [
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.STRING,
                        ProtoIdentifier("name"),
                        ProtoInt(4, ProtoIntSign.POSITIVE),
                    ),
                    ProtoSingleLineComment(" single-line comment!"),
                    ProtoMessageField(
                        ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                        ProtoIdentifier("sub_message"),
                        ProtoInt(9, ProtoIntSign.POSITIVE),
                        False,
                        False,
                        ProtoFullIdentifier("SubMessage"),
                        [],
                    ),
                ],
            ),
        )

    def test_oneof_normalize_removes_comment(self):
        normalized_oneof = ProtoOneOf.match(
            dedent(
                """oneof one_of_field {
                string name = 4;
                // single-line comment!
                SubMessage sub_message = 9;
            }""".strip()
            ),
        ).node.normalize()
        self.assertEqual(
            normalized_oneof.nodes,
            [
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.STRING,
                    ProtoIdentifier("name"),
                    ProtoInt(4, ProtoIntSign.POSITIVE),
                ),
                ProtoMessageField(
                    ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE,
                    ProtoIdentifier("sub_message"),
                    ProtoInt(9, ProtoIntSign.POSITIVE),
                    False,
                    False,
                    ProtoFullIdentifier("SubMessage"),
                    [],
                ),
            ],
        )

    def test_diff_same_oneof_returns_empty(self):
        po1 = ProtoOneOf(
            ProtoIdentifier("my_one_of"),
            [],
        )
        po2 = ProtoOneOf(
            ProtoIdentifier("my_one_of"),
            [],
        )
        self.assertEqual(ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2), [])

    def test_diff_different_oneof_name_returns_empty(self):
        po1 = ProtoOneOf(
            ProtoIdentifier("my_one_of"),
            [],
        )
        po2 = ProtoOneOf(
            ProtoIdentifier("other_one_of"),
            [],
        )
        self.assertEqual(ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2), [])

    def test_diff_oneof_added(self):
        po1 = None
        po2 = ProtoOneOf(ProtoIdentifier("my_one_of"), [])
        self.assertEqual(
            ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2),
            [
                ProtoOneOfAdded(
                    self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("my_one_of"), [])
                ),
            ],
        )

    def test_diff_oneof_removed(self):
        po1 = ProtoOneOf(ProtoIdentifier("my_one_of"), [])
        po2 = None
        self.assertEqual(
            [
                ProtoOneOfRemoved(
                    self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("my_one_of"), [])
                ),
            ],
            ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2),
        )

    def test_diff_member_added(self):
        po1 = ProtoOneOf(ProtoIdentifier("my_one_of"), [])
        mf = ProtoMessageField(
            ProtoMessageFieldTypesEnum.BOOL,
            ProtoIdentifier("new_member"),
            ProtoInt(1, ProtoIntSign.POSITIVE),
        )
        po2 = ProtoOneOf(ProtoIdentifier("my_one_of"), [mf])
        self.assertEqual(
            [ProtoMessageFieldAdded(po1, mf)],
            ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2),
        )

    def test_diff_member_removed(self):
        mf = ProtoMessageField(
            ProtoMessageFieldTypesEnum.BOOL,
            ProtoIdentifier("new_member"),
            ProtoInt(1, ProtoIntSign.POSITIVE),
        )
        po1 = ProtoOneOf(ProtoIdentifier("my_one_of"), [mf])
        po2 = ProtoOneOf(ProtoIdentifier("my_one_of"), [])
        self.assertEqual(
            [ProtoMessageFieldRemoved(po1, mf)],
            ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2),
        )

    def test_diff_member_changed(self):
        mf1 = ProtoMessageField(
            ProtoMessageFieldTypesEnum.BOOL,
            ProtoIdentifier("new_member"),
            ProtoInt(1, ProtoIntSign.POSITIVE),
        )
        po1 = ProtoOneOf(ProtoIdentifier("my_one_of"), [mf1])
        mf2 = ProtoMessageField(
            ProtoMessageFieldTypesEnum.BOOL,
            ProtoIdentifier("new_member_changed"),
            ProtoInt(1, ProtoIntSign.POSITIVE),
        )
        po2 = ProtoOneOf(ProtoIdentifier("my_one_of"), [mf2])
        self.assertEqual(
            [ProtoMessageFieldNameChanged(po1, mf1, mf2.name)],
            ProtoOneOf.diff(self.DEFAULT_PARENT, po1, po2),
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoOneOf.diff_sets(self.DEFAULT_PARENT, set1, set2), [])

    def test_diff_sets_no_change_returns_empty(self):
        set1 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of"), []),
        ]
        self.assertEqual(ProtoOneOf.diff_sets(self.DEFAULT_PARENT, set1, set1), [])

    def test_diff_sets_all_removed(self):
        set1 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of"), []),
        ]
        set2 = []
        diff = ProtoOneOf.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("foo_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("bar_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("baz_one_of"), [])
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_all_added(self):
        set1 = []
        set2 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of"), []),
        ]

        diff = ProtoOneOf.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("foo_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("bar_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("baz_one_of"), [])
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_mutually_exclusive(self):
        set1 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of"), []),
        ]
        set2 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of2"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of2"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of2"), []),
        ]
        diff = ProtoOneOf.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("foo_one_of2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("bar_one_of2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("baz_one_of2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("foo_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("bar_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("baz_one_of"), [])
            ),
            diff,
        )
        self.assertEqual(6, len(diff))

    def test_diff_sets_overlap(self):

        set1 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of"), []),
        ]
        set2 = [
            ProtoOneOf(ProtoIdentifier("foo_one_of2"), []),
            ProtoOneOf(ProtoIdentifier("bar_one_of"), []),
            ProtoOneOf(ProtoIdentifier("baz_one_of2"), []),
        ]
        diff = ProtoOneOf.diff_sets(self.DEFAULT_PARENT, set1, set2)
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("foo_one_of2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfAdded(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("baz_one_of2"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("foo_one_of"), [])
            ),
            diff,
        )
        self.assertIn(
            ProtoOneOfRemoved(
                self.DEFAULT_PARENT, ProtoOneOf(ProtoIdentifier("baz_one_of"), [])
            ),
            diff,
        )
        self.assertEqual(4, len(diff))


if __name__ == "__main__":
    unittest.main()
