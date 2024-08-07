# type: ignore

import unittest

from py_proto.proto_constant import ProtoConstant
from py_proto.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from py_proto.proto_int import ProtoInt, ProtoIntSign
from py_proto.proto_map import ProtoMap, ProtoMapKeyTypesEnum, ProtoMapValueTypesEnum
from py_proto.proto_message_field import ProtoMessageFieldOption
from py_proto.proto_string_literal import ProtoStringLiteral


class MapTest(unittest.TestCase):
    maxDiff = None

    def test_simple_map(self):
        parsed_map_simple = ProtoMap.match("map <sfixed64, NestedMessage> my_map = 10;")
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier("my_map"),
                ProtoInt(10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier("NestedMessage"),
                [],
            ),
        )

    def test_map_without_spaces(self):
        map_without_spaces = ProtoMap.match("map<sfixed64, NestedMessage> my_map = 10;")
        self.assertEqual(
            map_without_spaces.node,
            ProtoMap(
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier("my_map"),
                ProtoInt(10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier("NestedMessage"),
                [],
            ),
        )

    def test_map_with_options(self):
        parsed_map_simple = ProtoMap.match(
            "map <sfixed64, NestedMessage> my_map = 10  [ java_package = 'com.example.foo', baz.bat = 48 ];",
        )
        self.assertEqual(parsed_map_simple.node.key_type, ProtoMapKeyTypesEnum.SFIXED64)
        self.assertEqual(
            parsed_map_simple.node.value_type, ProtoMapValueTypesEnum.ENUM_OR_MESSAGE
        )
        self.assertEqual(parsed_map_simple.node.name, ProtoIdentifier("my_map"))
        self.assertEqual(
            parsed_map_simple.node.number, ProtoInt(10, ProtoIntSign.POSITIVE)
        )
        self.assertEqual(
            parsed_map_simple.node.enum_or_message_type_name,
            ProtoEnumOrMessageIdentifier("NestedMessage"),
        )
        self.assertEqual(
            parsed_map_simple.node.options,
            [
                ProtoMessageFieldOption(
                    ProtoIdentifier("java_package"),
                    ProtoConstant(ProtoStringLiteral("com.example.foo")),
                ),
                ProtoMessageFieldOption(
                    ProtoFullIdentifier("baz.bat"),
                    ProtoConstant(ProtoInt(48, ProtoIntSign.POSITIVE)),
                ),
            ],
        )

    def test_map_message_value(self):
        parsed_map_simple = ProtoMap.match("map <string, string> string_map = 11;")
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                ProtoMapKeyTypesEnum.STRING,
                ProtoMapValueTypesEnum.STRING,
                ProtoIdentifier("string_map"),
                ProtoInt(11, ProtoIntSign.POSITIVE),
                None,
                [],
            ),
        )


if __name__ == "__main__":
    unittest.main()
