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
    ProtoEnumValueAdded,
    ProtoEnumValueNameChanged,
    ProtoEnumValueOption,
    ProtoEnumValueRemoved,
)
from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_option import ProtoOption
from src.proto_range import ProtoRange, ProtoRangeEnum
from src.proto_reserved import ProtoReserved
from src.proto_string_literal import ProtoStringLiteral


class EnumTest(unittest.TestCase):
    maxDiff = None
    DEFAULT_PARENT = ProtoEnum(ProtoIdentifier("DefaultParent"), [])

    def test_enum_all_features(self):
        parsed_enum_multiple_values = ProtoEnum.match(
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
                    [
                        ProtoRange(ProtoInt(1, ProtoIntSign.POSITIVE)),
                        ProtoRange(ProtoInt(2, ProtoIntSign.POSITIVE)),
                        ProtoRange(
                            ProtoInt(5, ProtoIntSign.POSITIVE),
                            ProtoRangeEnum.MAX,
                        ),
                    ],
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_NEGATIVE"),
                    ProtoInt(1, ProtoIntSign.NEGATIVE),
                    [
                        ProtoEnumValueOption(
                            ProtoIdentifier("foo"),
                            ProtoConstant(ProtoBool(False)),
                        )
                    ],
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_UNDEFINED"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                ),
                ProtoSingleLineComment(" single-line comment"),
                ProtoOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("foobar")),
                ),
                ProtoMultiLineComment(
                    "\n                multiple\n                line\n                comment\n                ",
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALONE"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                    [
                        ProtoEnumValueOption(
                            ProtoIdentifier("(bar.baz).bat"),
                            ProtoConstant(ProtoStringLiteral("bat")),
                        ),
                        ProtoEnumValueOption(
                            ProtoIdentifier("baz.bat"),
                            ProtoConstant(ProtoInt(100, ProtoIntSign.NEGATIVE)),
                        ),
                    ],
                ),
                ProtoReserved(
                    [],
                    [
                        ProtoIdentifier("FE_RESERVED"),
                        ProtoIdentifier("FE_OLD"),
                    ],
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALTWO"),
                    ProtoInt(2, ProtoIntSign.POSITIVE),
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
        parsed_empty_enum = ProtoEnum.match("""enum FooEnum {}""")
        self.assertIsNotNone(parsed_empty_enum)
        self.assertEqual(parsed_empty_enum.node.name, ProtoIdentifier("FooEnum"))

        parsed_spaced_enum = ProtoEnum.match(
            dedent(
                """
            enum FooEnum {

            }
        """.strip()
            ),
        )
        self.assertIsNotNone(parsed_spaced_enum)
        self.assertEqual(parsed_spaced_enum.node.name, ProtoIdentifier("FooEnum"))

    def test_enum_empty_statements(self):
        empty_statement_enum = ProtoEnum.match(
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
        self.assertEqual(empty_statement_enum.node.name, ProtoIdentifier("FooEnum"))

    def test_enum_optionals(self):
        parsed_enum_with_optionals = ProtoEnum.match(
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
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("foobar")),
                ),
                ProtoOption(
                    ProtoIdentifier("(foo.bar).baz"),
                    ProtoConstant(ProtoBool(False)),
                ),
            ],
        )
        self.assertEqual(
            parsed_enum_with_optionals.node.name, ProtoIdentifier("FooEnum")
        )

    def test_enum_single_value(self):
        parsed_enum_single_value = ProtoEnum.match(
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
                    ProtoIdentifier("FE_UNDEFINED"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                )
            ],
        )

    def test_enum_multiple_values(self):
        parsed_enum_multiple_values = ProtoEnum.match(
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
                    ProtoIdentifier("FE_NEGATIVE"),
                    ProtoInt(1, ProtoIntSign.NEGATIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_UNDEFINED"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALONE"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALTWO"),
                    ProtoInt(2, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_enum_comments(self):
        parsed_enum_multiple_values = ProtoEnum.match(
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
                    ProtoIdentifier("FE_NEGATIVE"),
                    ProtoInt(1, ProtoIntSign.NEGATIVE),
                ),
                ProtoSingleLineComment(" test single-line comment"),
                ProtoEnumValue(
                    ProtoIdentifier("FE_UNDEFINED"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                ),
                ProtoMultiLineComment(
                    " test multiple\n                FE_UNUSED = 200;\n                line comment ",
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALONE"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALTWO"),
                    ProtoInt(2, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_enum_normalize_away_comments(self):
        parsed_enum_multiple_values = ProtoEnum.match(
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
                    ProtoIdentifier("FE_NEGATIVE"),
                    ProtoInt(1, ProtoIntSign.NEGATIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_UNDEFINED"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALONE"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                ),
                ProtoEnumValue(
                    ProtoIdentifier("FE_VALTWO"),
                    ProtoInt(2, ProtoIntSign.POSITIVE),
                ),
            ],
        )

    def test_diff_same_enum_returns_empty(self):
        pe1 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [],
        )
        pe2 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [],
        )
        self.assertEqual(ProtoEnum.diff(self.DEFAULT_PARENT, pe1, pe2), [])

    def test_diff_different_enum_name_returns_empty(self):
        pe1 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [],
        )
        pe2 = ProtoEnum(
            ProtoIdentifier("OtherEnum"),
            [],
        )
        self.assertEqual(ProtoEnum.diff(self.DEFAULT_PARENT, pe1, pe2), [])

    def test_diff_different_enum_value_name_returns_enum_diff(self):
        pe1 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [
                ProtoEnumValue(
                    ProtoIdentifier("ME_UNKNOWN"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        pe2 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [
                ProtoEnumValue(
                    ProtoIdentifier("ME_KNOWN"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        self.assertEqual(
            [
                ProtoEnumValueNameChanged(
                    pe1,
                    pe1.nodes[0],
                    ProtoIdentifier("ME_KNOWN"),
                )
            ],
            ProtoEnum.diff(self.DEFAULT_PARENT, pe1, pe2),
        )

    def test_diff_different_enum_value_value_returns_enum_diff(self):
        pe1 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [
                ProtoEnumValue(
                    ProtoIdentifier("ME_UNKNOWN"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        pe2 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [
                ProtoEnumValue(
                    ProtoIdentifier("ME_UNKNOWN"),
                    ProtoInt(1, ProtoIntSign.POSITIVE),
                )
            ],
        )

        diff = ProtoEnum.diff(self.DEFAULT_PARENT, pe1, pe2)

        self.assertIn(
            ProtoEnumValueRemoved(
                pe1,
                pe1.values[0],
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumValueAdded(
                pe1,
                pe2.values[0],
            ),
            diff,
        )
        self.assertEqual(2, len(diff))

    def test_diff_enum_added(self):
        pe1 = None
        pe2 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [
                ProtoEnumValue(
                    ProtoIdentifier("ME_UNKNOWN"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        self.assertEqual(
            ProtoEnum.diff(self.DEFAULT_PARENT, pe1, pe2),
            [
                ProtoEnumAdded(
                    self.DEFAULT_PARENT,
                    ProtoEnum(
                        ProtoIdentifier("MyEnum"),
                        [
                            ProtoEnumValue(
                                ProtoIdentifier("ME_UNKNOWN"),
                                ProtoInt(0, ProtoIntSign.POSITIVE),
                            )
                        ],
                    ),
                ),
            ],
        )

    def test_diff_enum_removed(self):
        pe1 = ProtoEnum(
            ProtoIdentifier("MyEnum"),
            [
                ProtoEnumValue(
                    ProtoIdentifier("ME_UNKNOWN"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                )
            ],
        )
        pe2 = None
        self.assertEqual(
            ProtoEnum.diff(self.DEFAULT_PARENT, pe1, pe2),
            [
                ProtoEnumRemoved(
                    self.DEFAULT_PARENT,
                    ProtoEnum(
                        ProtoIdentifier("MyEnum"),
                        [
                            ProtoEnumValue(
                                ProtoIdentifier("ME_UNKNOWN"),
                                ProtoInt(0, ProtoIntSign.POSITIVE),
                            )
                        ],
                    ),
                ),
            ],
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoEnum.diff_sets(self.DEFAULT_PARENT, set1, set2), [])

    def test_diff_sets_no_change(self):
        set1 = [
            ProtoEnum(
                ProtoIdentifier("FooEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        self.assertEqual(ProtoEnum.diff_sets(self.DEFAULT_PARENT, set1, set1), [])

    def test_diff_sets_all_removed(self):
        set1 = []
        set2 = [
            ProtoEnum(
                ProtoIdentifier("FooEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        diff = ProtoEnum.diff_sets(self.DEFAULT_PARENT, set1, set2)

        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("FooEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("FE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("BarEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("BE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("TagEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("TE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
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
                ProtoIdentifier("FooEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        set2 = []
        diff = ProtoEnum.diff_sets(self.DEFAULT_PARENT, set1, set2)

        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("FooEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("FE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("BarEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("BE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("TagEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("TE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
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
                ProtoIdentifier("FooEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        set2 = [
            ProtoEnum(
                ProtoIdentifier("FooEnum2"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN2"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum2"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN2"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum2"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN2"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]

        diff = ProtoEnum.diff_sets(self.DEFAULT_PARENT, set1, set2)

        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("FooEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("FE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("BarEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("BE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("TagEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("TE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("FooEnum2"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("FE_UNKNOWN2"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("BarEnum2"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("BE_UNKNOWN2"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("TagEnum2"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("TE_UNKNOWN2"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
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
                ProtoIdentifier("FooEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]
        set2 = [
            ProtoEnum(
                ProtoIdentifier("FooEnum2"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("FE_UNKNOWN2"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("BarEnum"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("BE_UNKNOWN2"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
            ProtoEnum(
                ProtoIdentifier("TagEnum2"),
                [
                    ProtoEnumValue(
                        ProtoIdentifier("TE_UNKNOWN2"),
                        ProtoInt(0, ProtoIntSign.POSITIVE),
                    )
                ],
            ),
        ]

        diff = ProtoEnum.diff_sets(self.DEFAULT_PARENT, set1, set2)

        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("FooEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("FE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )

        self.assertIn(
            ProtoEnumRemoved(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("TagEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("TE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("FooEnum2"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("FE_UNKNOWN2"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumAdded(
                self.DEFAULT_PARENT,
                ProtoEnum(
                    ProtoIdentifier("TagEnum2"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("TE_UNKNOWN2"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
            ),
            diff,
        )
        self.assertIn(
            ProtoEnumValueNameChanged(
                ProtoEnum(
                    ProtoIdentifier("BarEnum"),
                    [
                        ProtoEnumValue(
                            ProtoIdentifier("BE_UNKNOWN"),
                            ProtoInt(0, ProtoIntSign.POSITIVE),
                        )
                    ],
                ),
                ProtoEnumValue(
                    ProtoIdentifier("BE_UNKNOWN"),
                    ProtoInt(0, ProtoIntSign.POSITIVE),
                ),
                ProtoIdentifier("BE_UNKNOWN2"),
            ),
            diff,
        )
        self.assertEqual(5, len(diff))


if __name__ == "__main__":
    unittest.main()
