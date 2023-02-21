import unittest

from src.proto_int import ProtoInt, ProtoIntSign


class IntTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(ProtoInt.match("1").node, ProtoInt(1, ProtoIntSign.POSITIVE))
        self.assertEqual(
            ProtoInt.match("158912938471293847").node,
            ProtoInt(158912938471293847, ProtoIntSign.POSITIVE),
        )

    def test_octal(self):
        self.assertEqual(
            ProtoInt.match("072342").node,
            ProtoInt(0o72342, ProtoIntSign.POSITIVE),
        )
        with self.assertRaises(ValueError):
            ProtoInt.match("072942")

    def test_hex(self):
        self.assertEqual(
            ProtoInt.match("0x72342").node,
            ProtoInt(0x72342, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoInt.match("0x7A3d2").node,
            ProtoInt(0x7A3D2, ProtoIntSign.POSITIVE),
        )
        with self.assertRaises(ValueError):
            ProtoInt.match("0x72G42")


if __name__ == "__main__":
    unittest.main()
