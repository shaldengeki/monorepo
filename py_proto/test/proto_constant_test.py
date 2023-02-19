import unittest
from textwrap import dedent

from src.proto_bool import ProtoBool
from src.proto_constant import ProtoConstant
from src.proto_float import ProtoFloat, ProtoFloatSign
from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_string_literal import ProtoStringLiteral


class ConstantTest(unittest.TestCase):
    # constant = fullIdent | ( [ "-" | "+" ] intLit ) | ( [ "-" | "+" ] floatLit ) | strLit | boolLit
    def test_ident(self):
        self.assertEqual(
            ProtoConstant.match(None, "a").node.value, ProtoIdentifier(None, "a")
        )
        self.assertEqual(
            ProtoConstant.match(None, "a0").node.value, ProtoIdentifier(None, "a0")
        )
        self.assertEqual(
            ProtoConstant.match(None, "a_").node.value, ProtoIdentifier(None, "a_")
        )
        self.assertEqual(
            ProtoConstant.match(None, "aa").node.value, ProtoIdentifier(None, "aa")
        )
        self.assertEqual(
            ProtoConstant.match(None, "ab").node.value, ProtoIdentifier(None, "ab")
        )
        self.assertEqual(
            ProtoConstant.match(None, "a0b_f_aj").node.value,
            ProtoIdentifier(None, "a0b_f_aj"),
        )
        self.assertEqual(
            ProtoConstant.match(None, "a.bar").node.value,
            ProtoIdentifier(None, "a.bar"),
        )
        self.assertEqual(
            ProtoConstant.match(None, "a.bar.baz").node.value,
            ProtoIdentifier(None, "a.bar.baz"),
        )

    def test_str(self):
        self.assertEqual(
            ProtoConstant.match(None, "'a'").node.value,
            ProtoStringLiteral(None, "a", quote="'"),
        )
        self.assertEqual(
            ProtoConstant.match(None, "'.a'").node.value,
            ProtoStringLiteral(None, ".a", quote="'"),
        )
        self.assertEqual(
            ProtoConstant.match(None, '"a"').node.value,
            ProtoStringLiteral(None, "a", quote='"'),
        )

    def test_bool(self):
        self.assertEqual(
            ProtoConstant.match(None, "true").node.value, ProtoBool(None, True)
        )
        self.assertEqual(
            ProtoConstant.match(None, "false").node.value, ProtoBool(None, False)
        )

    def test_int(self):
        self.assertEqual(
            ProtoConstant.match(None, "1").node.value,
            ProtoInt(None, 1, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "158912938471293847").node.value,
            ProtoInt(None, 158912938471293847, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "+1").node.value,
            ProtoInt(None, 1, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "+158912938471293847").node.value,
            ProtoInt(None, 158912938471293847, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "-1").node.value,
            ProtoInt(None, 1, ProtoIntSign.NEGATIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "-248713857").node.value,
            ProtoInt(None, 248713857, ProtoIntSign.NEGATIVE),
        )

        # Octal
        self.assertEqual(
            ProtoConstant.match(None, "072342").node.value,
            ProtoInt(None, 0o72342, ProtoIntSign.POSITIVE),
        )
        with self.assertRaises(ValueError):
            ProtoConstant.match(None, "072942")

        # Hex
        self.assertEqual(
            ProtoConstant.match(None, "0x72342").node.value,
            ProtoInt(None, 0x72342, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "0x7A3d2").node.value,
            ProtoInt(None, 0x7A3D2, ProtoIntSign.POSITIVE),
        )
        with self.assertRaises(ValueError):
            ProtoConstant.match(None, "0x72G42")

    def test_float(self):
        self.assertEqual(
            ProtoConstant.match(None, "2834.235928").node.value,
            ProtoFloat(None, 2834.235928, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834.e2").node.value,
            ProtoFloat(None, 283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834e2").node.value,
            ProtoFloat(None, 283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834.e0").node.value,
            ProtoFloat(None, 2834, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834e0").node.value,
            ProtoFloat(None, 2834, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834.E3").node.value,
            ProtoFloat(None, 2834000, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834E3").node.value,
            ProtoFloat(None, 2834000, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834.e+2").node.value,
            ProtoFloat(None, 283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834e+2").node.value,
            ProtoFloat(None, 283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834.e-2").node.value,
            ProtoFloat(None, 28.34, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "2834e-2").node.value,
            ProtoFloat(None, 28.34, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, ".0").node.value,
            ProtoFloat(None, 0.0, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, ".0e-1").node.value,
            ProtoFloat(None, 0.00, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, ".0E1").node.value,
            ProtoFloat(None, 0, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, ".0E2").node.value,
            ProtoFloat(None, 0, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, ".3265").node.value,
            ProtoFloat(None, 0.3265, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, ".3265e1").node.value,
            ProtoFloat(None, 3.265, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoConstant.match(None, "inf").node.value,
            ProtoFloat(None, float("inf"), ProtoFloatSign.POSITIVE),
        )


if __name__ == "__main__":
    unittest.main()
