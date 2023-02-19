import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
from src.proto_comment import ProtoMultiLineComment, ProtoSingleLineComment
from src.proto_constant import ProtoConstant
from src.proto_enum import (
    ProtoEnum,
    ProtoEnumAdded,
    ProtoEnumRemoved,
    ProtoEnumValue,
    ProtoEnumValueNameChanged,
    ProtoEnumValueOption,
    ProtoEnumValueValueChanged,
)
from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_option import ProtoOption
from src.proto_range import ProtoRange, ProtoRangeEnum
from src.proto_reserved import ProtoReserved
from src.proto_string_literal import ProtoStringLiteral


class EnumTest(unittest.TestCase):
    maxDiff = None

    def test_enum_all_features(self):
        parsed_enum_multiple_values = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                reserved 1, 2, 5 to max;
                FE_NEGATIVE = -1 [ foo = false ];
                FE_UNDEFINED = 0; // single-line comment
                option java_package = "foobar";
                /*
                multiple
                line
                comment
                */
                FE_VALONE = 1 [ (bar.baz).bat = "bat", baz.bat = -100 ];
                reserved "FE_RESERVED", "FE_OLD";
                FE_VALTWO = 2;
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_enum_multiple_values.node.nodes,
            [
                ProtoReserved(
                    None,
                    [
                        ProtoRange(None, ProtoInt(None, 1, ProtoIntSign.POSITIVE)),
                        ProtoRange(None, ProtoInt(None, 2, ProtoIntSign.POSITIVE)),
                        ProtoRange(
                            None,
                            ProtoInt(None, 5, ProtoIntSign.POSITIVE),
                            ProtoRangeEnum.MAX,
                        ),
                    ],
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_NEGATIVE"),
                    ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
                    [
                        ProtoEnumValueOption(
                            None,
                            ProtoIdentifier(None, "foo"),
                            ProtoConstant(None, ProtoBool(None, False)),
                        )
                    ],
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_UNDEFINED"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                ),
                ProtoSingleLineComment(None, " single-line comment"),
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "java_package"),
                    ProtoConstant(None, ProtoStringLiteral(None, "foobar")),
                ),
                ProtoMultiLineComment(
                    None,
                    "\n                multiple\n                line\n                comment\n                ",
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALONE"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                    [
                        ProtoEnumValueOption(
                            None,
                            ProtoIdentifier(None, "(bar.baz).bat"),
                            ProtoConstant(None, ProtoStringLiteral(None, "bat")),
                        ),
                        ProtoEnumValueOption(
                            None,
                            ProtoIdentifier(None, "baz.bat"),
                            ProtoConstant(
                                None, ProtoInt(None, 100, ProtoIntSign.NEGATIVE)
                            ),
                        ),
                    ],
                ),
                ProtoReserved(
                    None,
                    [],
                    [
                        ProtoIdentifier(None, "FE_RESERVED"),
                        ProtoIdentifier(None, "FE_OLD"),
                    ],
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALTWO"),
                    ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                ),
            ],
        )
        # TODO: The serialization of the multi-line comment here is obviously off.
        self.assertEqual(
            parsed_enum_multiple_values.node.serialize(),
            dedent(
                """
            enum FooEnum {
            reserved 1, 2, 5 to max;
            FE_NEGATIVE = -1 [ foo = false ];
            FE_UNDEFINED = 0;
            // single-line comment
            option java_package = "foobar";
            /*
                            multiple
                            line
                            comment
                            */
            FE_VALONE = 1 [ (bar.baz).bat = "bat", baz.bat = -100 ];
            reserved "FE_RESERVED", "FE_OLD";
            FE_VALTWO = 2;
            }
            """
            ).strip(),
        )

    def test_empty_enum(self):
        parsed_empty_enum = ProtoEnum.match(None, """enum FooEnum {}""")
        self.assertIsNotNone(parsed_empty_enum)
        self.assertEqual(parsed_empty_enum.node.name, ProtoIdentifier(None, "FooEnum"))

        parsed_spaced_enum = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {

            }
        """.strip()
            ),
        )
        self.assertIsNotNone(parsed_spaced_enum)
        self.assertEqual(parsed_spaced_enum.node.name, ProtoIdentifier(None, "FooEnum"))

    def test_enum_empty_statements(self):
        empty_statement_enum = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                ;
                ;
            }
        """.strip()
            ),
        )
        self.assertIsNotNone(empty_statement_enum)
        self.assertEqual(
            empty_statement_enum.node.name, ProtoIdentifier(None, "FooEnum")
        )

    def test_enum_optionals(self):
        parsed_enum_with_optionals = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                option java_package = "foobar";
                option (foo.bar).baz = false;
            }
        """.strip()
            ),
        )
        self.assertIsNotNone(
            parsed_enum_with_optionals.node.options,
            [
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "java_package"),
                    ProtoConstant(None, ProtoStringLiteral(None, "foobar")),
                ),
                ProtoOption(
                    None,
                    ProtoIdentifier(None, "(foo.bar).baz"),
                    ProtoConstant(None, ProtoBool(None, False)),
                ),
            ],
        )
        self.assertEqual(
            parsed_enum_with_optionals.node.name, ProtoIdentifier(None, "FooEnum")
        )

    def test_enum_single_value(self):
        parsed_enum_single_value = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                FE_UNDEFINED = 0;
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_enum_single_value.node.nodes,
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_UNDEFINED"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                )
            ],
        )

    def test_enum_multiple_values(self):
        parsed_enum_multiple_values = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                FE_NEGATIVE = -1;
                FE_UNDEFINED = 0;
                FE_VALONE = 1;
                FE_VALTWO = 2;
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_enum_multiple_values.node.nodes,
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_NEGATIVE"),
                    ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_UNDEFINED"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALONE"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALTWO"),
                    ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_enum_comments(self):
        parsed_enum_multiple_values = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                FE_NEGATIVE = -1; // test single-line comment
                FE_UNDEFINED = 0; /* test multiple
                FE_UNUSED = 200;
                line comment */
                FE_VALONE = 1;
                FE_VALTWO = 2;
            }
        """.strip()
            ),
        )
        self.assertEqual(
            parsed_enum_multiple_values.node.nodes,
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_NEGATIVE"),
                    ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
                ),
                ProtoSingleLineComment(None, " test single-line comment"),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_UNDEFINED"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                ),
                ProtoMultiLineComment(
                    None,
                    " test multiple\n                FE_UNUSED = 200;\n                line comment ",
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALONE"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALTWO"),
                    ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_enum_normalize_away_comments(self):
        parsed_enum_multiple_values = ProtoEnum.match(
            None,
            dedent(
                """
            enum FooEnum {
                FE_NEGATIVE = -1; // test single-line comment
                FE_UNDEFINED = 0; /* test multiple
                FE_UNUSED = 200;
                line comment */
                FE_VALONE = 1;
                FE_VALTWO = 2;
            }
        """.strip()
            ),
        ).node.normalize()
        self.assertEqual(
            parsed_enum_multiple_values.nodes,
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_NEGATIVE"),
                    ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_UNDEFINED"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALONE"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "FE_VALTWO"),
                    ProtoInt(None, 2, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_diff_same_enum_returns_empty(self):
        pe1 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [],
        )
        pe2 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [],
        )
        self.assertEqual(ProtoEnum.diff(pe1, pe2), [])

    def test_diff_different_enum_name_returns_empty(self):
        pe1 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [],
        )
        pe2 = ProtoEnum(
            None,
            ProtoIdentifier(None, "OtherEnum"),
            [],
        )
        self.assertEqual(ProtoEnum.diff(pe1, pe2), [])

    def test_diff_different_enum_value_name_returns_enum_diff(self):
        pe1 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "ME_UNKNOWN"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        pe2 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "ME_KNOWN"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        self.assertEqual(
            ProtoEnum.diff(pe1, pe2),
            [
                ProtoEnumValueNameChanged(
                    pe1,
                    pe2.nodes[0],
                    ProtoIdentifier(None, "ME_UNKNOWN"),
                )
            ],
        )

    def test_diff_different_enum_value_value_returns_enum_diff(self):
        pe1 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "ME_UNKNOWN"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        pe2 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "ME_UNKNOWN"),
                    ProtoInt(None, 1, ProtoIntSign.POSITIVE),
                )
            ],
        )

        diff = ProtoEnum.diff(pe1, pe2)

        self.assertIn(
            ProtoEnumValueValueChanged(
                pe1,
                pe2.values[0],
                ProtoInt(None, 0, ProtoIntSign.POSITIVE),
            ),
            diff,
        )
        self.assertEqual(1, len(diff))

    def test_diff_enum_added(self):
        pe1 = None
        pe2 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "ME_UNKNOWN"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        self.assertEqual(
            ProtoEnum.diff(pe1, pe2),
            [
                ProtoEnumAdded(
                    ProtoEnum(
                        None,
                        ProtoIdentifier(None, "MyEnum"),
                        [
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "ME_UNKNOWN"),
                                ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                            )
                        ],
                    )
                ),
            ],
        )

    def test_diff_enum_removed(self):
        pe1 = ProtoEnum(
            None,
            ProtoIdentifier(None, "MyEnum"),
            [
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "ME_UNKNOWN"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        pe2 = None
        self.assertEqual(
            ProtoEnum.diff(pe1, pe2),
            [
                ProtoEnumRemoved(
                    ProtoEnum(
                        None,
                        ProtoIdentifier(None, "MyEnum"),
                        [
                            ProtoEnumValue(
                                None,
                                ProtoIdentifier(None, "ME_UNKNOWN"),
                                ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                            )
                        ],
                    )
                ),
            ],
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoEnum.diff_sets(set1, set2), [])

    def test_diff_sets_no_change(self):
        set1 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        self.assertEqual(ProtoEnum.diff_sets(set1, set1), [])

    def test_diff_sets_all_removed(self):
        set1 = []
        set2 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        diff = ProtoEnum.diff_sets(set1, set2)

        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "FooEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "FE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "BarEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "BE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "TagEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "TE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_all_added(self):
        set1 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        set2 = []
        diff = ProtoEnum.diff_sets(set1, set2)

        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "FooEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "FE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "BarEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "BE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "TagEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "TE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_mutually_exclusive(self):
        set1 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        set2 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum2"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN2"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum2"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN2"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum2"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN2"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]

        diff = ProtoEnum.diff_sets(set1, set2)

        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "FooEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "FE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "BarEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "BE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "TagEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "TE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "FooEnum2"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "FE_UNKNOWN2"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "BarEnum2"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "BE_UNKNOWN2"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "TagEnum2"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "TE_UNKNOWN2"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertEqual(6, len(diff))

    def test_diff_sets_overlap(self):
        set1 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        set2 = [
            ProtoEnum(
                None,
                ProtoIdentifier(None, "FooEnum2"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "FE_UNKNOWN2"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "BarEnum"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "BE_UNKNOWN2"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                None,
                ProtoIdentifier(None, "TagEnum2"),
                [
                    ProtoEnumValue(
                        None,
                        ProtoIdentifier(None, "TE_UNKNOWN2"),
                        ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]

        diff = ProtoEnum.diff_sets(set1, set2)

        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "FooEnum2"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "FE_UNKNOWN2"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "TagEnum2"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "TE_UNKNOWN2"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "FooEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "FE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "TagEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "TE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumValueNameChanged(
                ProtoEnum(
                    None,
                    ProtoIdentifier(None, "BarEnum"),
                    [
                        ProtoEnumValue(
                            None,
                            ProtoIdentifier(None, "BE_UNKNOWN"),
                            ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
                ProtoEnumValue(
                    None,
                    ProtoIdentifier(None, "BE_UNKNOWN2"),
                    ProtoInt(None, 0, ProtoIntSign.POSITIVE),
                ),
                ProtoIdentifier(None, "BE_UNKNOWN"),
            ),
            diff,
        )
        self.assertEqual(5, len(diff))


if __name__ == "__main__":
    unittest.main()
