import unittest
from textwrap import dedent

from src.proto_constant import ProtoConstant
from src.proto_float import ProtoFloat, ProtoFloatSign
from src.proto_identifier import ProtoFullIdentifier, ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_option import ProtoOption
from src.proto_string_literal import ProtoStringLiteral


class OptionTest(unittest.TestCase):
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
            parenthesized_option.node.value.value, ProtoStringLiteral("test value")
        )

        fully_qualified_name_option = ProtoOption.match(
            "option (foo).bar.baz = 'test value';"
        )
        self.assertEqual(
            fully_qualified_name_option.node.name, ProtoFullIdentifier("(foo).bar.baz")
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
            int_option.node.value, ProtoConstant(ProtoInt(0, ProtoIntSign.POSITIVE))
        )
        self.assertEqual(int_option.remaining_source, "")

        int_option = ProtoOption.match("option foo = 12345;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value, ProtoConstant(ProtoInt(12345, ProtoIntSign.POSITIVE))
        )
        self.assertEqual(int_option.remaining_source, "")

        int_option = ProtoOption.match("option foo = +42;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value, ProtoConstant(ProtoInt(42, ProtoIntSign.POSITIVE))
        )
        self.assertEqual(int_option.remaining_source, "")

        int_option = ProtoOption.match("option foo = -12;")
        self.assertEqual(int_option.node.name, ProtoIdentifier("foo"))
        self.assertEqual(
            int_option.node.value, ProtoConstant(ProtoInt(12, ProtoIntSign.NEGATIVE))
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


if __name__ == "__main__":
    unittest.main()
