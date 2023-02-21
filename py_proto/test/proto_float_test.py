import unittest

from src.proto_float import ProtoFloat, ProtoFloatSign


class FloatTest(unittest.TestCase):
    def test_float(self):
        self.assertEqual(
            ProtoFloat.match("2834.235928").node,
            ProtoFloat(2834.235928, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match(".0").node,
            ProtoFloat(0.0, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match(".3265").node,
            ProtoFloat(0.3265, ProtoFloatSign.POSITIVE),
        )

    def test_inf(self):
        self.assertEqual(
            ProtoFloat.match("inf").node,
            ProtoFloat(float("inf"), ProtoFloatSign.POSITIVE),
        )

    def test_nan(self):
        match = ProtoFloat.match("nan")
        self.assertNotEqual(match.node.value, match.node.value)
        self.assertEqual(match.remaining_source, "")
        self.assertEqual(match.node.sign, ProtoFloatSign.POSITIVE)

    def test_exponential_positive(self):
        self.assertEqual(
            ProtoFloat.match("2834.e2").node,
            ProtoFloat(283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834e2").node,
            ProtoFloat(283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834.e0").node,
            ProtoFloat(2834, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834e0").node,
            ProtoFloat(2834, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834.E3").node,
            ProtoFloat(2834000, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834E3").node,
            ProtoFloat(2834000, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834.e+2").node,
            ProtoFloat(283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834e+2").node,
            ProtoFloat(283400, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match(".0E1").node,
            ProtoFloat(0, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match(".0E2").node,
            ProtoFloat(0, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match(".3265e1").node,
            ProtoFloat(3.265, ProtoFloatSign.POSITIVE),
        )

    def test_exponential_negative(self):
        self.assertEqual(
            ProtoFloat.match("2834.e-2").node,
            ProtoFloat(28.34, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match("2834e-2").node,
            ProtoFloat(28.34, ProtoFloatSign.POSITIVE),
        )
        self.assertEqual(
            ProtoFloat.match(".0e-1").node,
            ProtoFloat(0.00, ProtoFloatSign.POSITIVE),
        )


if __name__ == "__main__":
    unittest.main()
