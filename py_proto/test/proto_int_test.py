import unittest

from src.proto_int import ProtoInt, ProtoIntSign


class IntTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(
            ProtoInt.match(None, "1").node, ProtoInt(None, 1, ProtoIntSign.POSITIVE)
        )
        self.assertEqual(
            ProtoInt.match(None, "158912938471293847").node,
            ProtoInt(None, 158912938471293847, ProtoIntSign.POSITIVE),
        )

    def test_octal(self):
        self.assertEqual(
            ProtoInt.match(None, "072342").node,
            ProtoInt(None, 0o72342, ProtoIntSign.POSITIVE),
        )
        with self.assertRaises(ValueError):
            ProtoInt.match(None, "072942")

    def test_hex(self):
        self.assertEqual(
            ProtoInt.match(None, "0x72342").node,
            ProtoInt(None, 0x72342, ProtoIntSign.POSITIVE),
        )
        self.assertEqual(
            ProtoInt.match(None, "0x7A3d2").node,
            ProtoInt(None, 0x7A3D2, ProtoIntSign.POSITIVE),
        )
        with self.assertRaises(ValueError):
            ProtoInt.match(None, "0x72G42")


if __name__ == "__main__":
    unittest.main()
