import unittest
from textwrap import dedent

from src.proto_constant import ProtoConstant
from src.proto_float import ProtoFloat, ProtoFloatSign
from src.proto_identifier import ProtoFullIdentifier, ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_option import (
    ProtoOption,
    ProtoOptionAdded,
    ProtoOptionRemoved,
    ProtoOptionValueChanged,
)
from src.proto_string_literal import ProtoStringLiteral


class OptionTest(unittest.TestCase):

    maxDiff = None

    def test_string_option(self):
        string_option = ProtoOption.match("option foo = 'test value';")
        self.assertEqual(string_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            string_option.node.value.value, ProtoStringLiteral("test value")
        )
        self.assertEqual(string_option.remaining_source, "")

        string_option = ProtoOption.match('option foo = "test value";')
        self.assertEqual(string_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            string_option.node.value.value, ProtoStringLiteral("test value")
        )
        self.assertEqual(string_option.remaining_source, "")

    def test_packaged_name(self):
        packaged_option = ProtoOption.match("option foo.bar.baz = 'test value';")
        self.assertEqual(packaged_option.node.name, ProtoFullIdentifier("foo.bar.baz"))
        self.assertEqual(
            packaged_option.node.value.value, ProtoStringLiteral("test value")
        )

    def test_parenthesized_name(self):
        parenthesized_option = ProtoOption.match("option (foo) = 'test value';")
        self.assertEqual(parenthesized_option.node.name, ProtoIdentifier("(foo)"))
        self.assertEqual(
            parenthesized_option.node.value.value,
            ProtoStringLiteral("test value"),
        )

        fully_qualified_name_option = ProtoOption.match(
            "option (foo).bar.baz = 'test value';"
        )
        self.assertEqual(
            fully_qualified_name_option.node.name,
            ProtoFullIdentifier("(foo).bar.baz"),
        )
        self.assertEqual(
            fully_qualified_name_option.node.value.value,
            ProtoStringLiteral("test value"),
        )

    def test_string_option_missing_semicolon(self):
        with self.assertRaises(ValueError):
            ProtoOption.match("option foo = 'test value'")

        with self.assertRaises(ValueError):
            ProtoOption.match('option foo = "test value"')

    def test_string_option_missing_quote(self):
        with self.assertRaises(ValueError):
            ProtoOption.match("option foo = test value;")

        with self.assertRaises(ValueError):
            ProtoOption.match("option foo = 'test value;")

        with self.assertRaises(ValueError):
            ProtoOption.match('option foo = "test value;')

        with self.assertRaises(ValueError):
            ProtoOption.match("option foo = test value';")

        with self.assertRaises(ValueError):
            ProtoOption.match('option foo = test value";')

        with self.assertRaises(ValueError):
            ProtoOption.match("option foo = 'test value\";")

        with self.assertRaises(ValueError):
            ProtoOption.match("option foo = \"test value';")

    def test_identifier_option(self):
        identifier_option = ProtoOption.match("option foo = test_identifier;")
        self.assertEqual(identifier_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            identifier_option.node.value,
            ProtoConstant(ProtoIdentifier("test_identifier")),
        )
        self.assertEqual(identifier_option.remaining_source, "")

        identifier_option = ProtoOption.match("option bar = foo.bar.baz;")
        self.assertEqual(identifier_option.node.name, ProtoIdentifier("bar"))
        self.assertEqual(
            identifier_option.node.value,
            ProtoConstant(ProtoFullIdentifier("foo.bar.baz")),
        )
        self.assertEqual(identifier_option.remaining_source, "")

    def test_int_option(self):
        int_option = ProtoOption.match("option foo = 0;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value,
            ProtoConstant(ProtoInt(0, ProtoIntSign.POSITIVE)),
        )
        self.assertEqual(int_option.remaining_source, "")

        int_option = ProtoOption.match("option foo = 12345;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value,
            ProtoConstant(ProtoInt(12345, ProtoIntSign.POSITIVE)),
        )
        self.assertEqual(int_option.remaining_source, "")

        int_option = ProtoOption.match("option foo = +42;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value,
            ProtoConstant(ProtoInt(42, ProtoIntSign.POSITIVE)),
        )
        self.assertEqual(int_option.remaining_source, "")

        int_option = ProtoOption.match("option foo = -12;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value,
            ProtoConstant(ProtoInt(12, ProtoIntSign.NEGATIVE)),
        )
        self.assertEqual(int_option.remaining_source, "")

    def test_float_option(self):
        float_option = ProtoOption.match("option foo = inf;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float("inf"), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = nan;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float("nan"), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = 12.1;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(12.1), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = .1;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(0.1), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = .1e3;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(100), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = +12.1;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(12.1), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = +.1;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(0.1), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = +.1e2;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(10), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = +.1e-2;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(0.001), ProtoFloatSign.POSITIVE)),
        )

        float_option = ProtoOption.match("option foo = -.1e0;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(0.1), ProtoFloatSign.NEGATIVE)),
        )

        float_option = ProtoOption.match("option foo = -12E+1;")
        self.assertEqual(
            float_option.node.value,
            ProtoConstant(ProtoFloat(float(120), ProtoFloatSign.NEGATIVE)),
        )

    def test_diff_same_option_returns_empty(self):
        po1 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        po2 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        self.assertEqual(ProtoOption.diff(po1, po2), [])

    def test_diff_different_option_name_returns_empty(self):
        po1 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        po2 = ProtoOption(
            ProtoIdentifier("other.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        self.assertEqual(ProtoOption.diff(po1, po2), [])

    def test_diff_different_option_value_returns_option_diff(self):
        po1 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        po2 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("other value")),
        )
        self.assertEqual(
            ProtoOption.diff(po1, po2),
            [
                ProtoOptionValueChanged(
                    ProtoIdentifier("some.custom.option"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                    ProtoConstant(ProtoStringLiteral("other value")),
                )
            ],
        )

    def test_diff_option_added(self):
        po1 = None
        po2 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        self.assertEqual(
            ProtoOption.diff(po1, po2),
            [
                ProtoOptionAdded(
                    ProtoOption(
                        ProtoIdentifier("some.custom.option"),
                        ProtoConstant(ProtoStringLiteral("some value")),
                    )
                ),
            ],
        )

    def test_diff_option_removed(self):
        po1 = ProtoOption(
            ProtoIdentifier("some.custom.option"),
            ProtoConstant(ProtoStringLiteral("some value")),
        )
        po2 = None
        self.assertEqual(
            ProtoOption.diff(po1, po2),
            [
                ProtoOptionRemoved(
                    ProtoOption(
                        ProtoIdentifier("some.custom.option"),
                        ProtoConstant(ProtoStringLiteral("some value")),
                    )
                ),
            ],
        )

    def test_diff_sets_empty_returns_empty(self):
        set1 = []
        set2 = []
        self.assertEqual(ProtoOption.diff_sets(set1, set2), [])

    def test_diff_sets_no_change(self):
        set1 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]
        self.assertEqual(ProtoOption.diff_sets(set1, set1), [])

    def test_diff_sets_all_removed(self):
        set1 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]
        set2 = []
        diff = ProtoOption.diff_sets(set1, set2)

        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("some.custom.option"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("other.option"),
                    ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
                )
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_all_added(self):
        set1 = []
        set2 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]
        diff = ProtoOption.diff_sets(set1, set2)

        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("some.custom.option"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("other.option"),
                    ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
                )
            ),
            diff,
        )
        self.assertEqual(3, len(diff))

    def test_diff_sets_mutually_exclusive(self):
        set1 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]
        set2 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option.but.not.prior"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("ruby_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option.but.stil.not.prior"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]

        diff = ProtoOption.diff_sets(set1, set2)

        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("some.custom.option.but.not.prior"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("other.option.but.stil.not.prior"),
                    ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
                )
            ),
            diff,
        )

        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("ruby_package"),
                    ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
                )
            ),
            diff,
        )

        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("other.option"),
                    ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
                )
            ),
            diff,
        )

        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("some.custom.option"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                )
            ),
            diff,
        )

        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
                )
            ),
            diff,
        )

        self.assertEqual(6, len(diff))

    def test_diff_sets_overlap(self):
        set1 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]
        set2 = [
            ProtoOption(
                ProtoIdentifier("some.custom.option.but.not.prior"),
                ProtoConstant(ProtoStringLiteral("some value")),
            ),
            ProtoOption(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.bat")),
            ),
            ProtoOption(
                ProtoIdentifier("other.option.but.stil.not.prior"),
                ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
            ),
        ]

        diff = ProtoOption.diff_sets(set1, set2)

        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("some.custom.option"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                )
            ),
            diff,
        )

        self.assertIn(
            ProtoOptionRemoved(
                ProtoOption(
                    ProtoIdentifier("other.option"),
                    ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("some.custom.option.but.not.prior"),
                    ProtoConstant(ProtoStringLiteral("some value")),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionAdded(
                ProtoOption(
                    ProtoIdentifier("other.option.but.stil.not.prior"),
                    ProtoConstant(ProtoInt(100, ProtoIntSign.POSITIVE)),
                )
            ),
            diff,
        )
        self.assertIn(
            ProtoOptionValueChanged(
                ProtoIdentifier("java_package"),
                ProtoConstant(ProtoStringLiteral("foo.bar.baz")),
                ProtoConstant(ProtoStringLiteral("foo.bar.bat")),
            ),
            diff,
        )
        self.assertEqual(5, len(diff))


if __name__ == "__main__":
    unittest.main()
