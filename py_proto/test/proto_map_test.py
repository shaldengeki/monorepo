import unittest

from src.proto_constant import ProtoConstant
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_map import ProtoMap, ProtoMapKeyTypesEnum, ProtoMapValueTypesEnum
from src.proto_message_field import ProtoMessageFieldOption
from src.proto_string_literal import ProtoStringLiteral


class MapTest(unittest.TestCase):
    maxDiff = None

    def test_simple_map(self):
        parsed_map_simple = ProtoMap.match(
            None, "map <sfixed64, NestedMessage> my_map = 10;"
        )
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                None,
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier(None, "my_map"),
                ProtoInt(None, 10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
                [],
            ),
        )

    def test_map_without_spaces(self):
        map_without_spaces = ProtoMap.match(
            None, "map<sfixed64, NestedMessage> my_map = 10;"
        )
        self.assertEqual(
            map_without_spaces.node,
            ProtoMap(
                None,
                ProtoMapKeyTypesEnum.SFIXED64,
                ProtoMapValueTypesEnum.ENUM_OR_MESSAGE,
                ProtoIdentifier(None, "my_map"),
                ProtoInt(None, 10, ProtoIntSign.POSITIVE),
                ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
                [],
            ),
        )

    def test_map_with_options(self):
        parsed_map_simple = ProtoMap.match(
            None,
            "map <sfixed64, NestedMessage> my_map = 10  [ java_package = 'com.example.foo', baz.bat = 48 ];",
        )
        self.assertEqual(parsed_map_simple.node.key_type, ProtoMapKeyTypesEnum.SFIXED64)
        self.assertEqual(
            parsed_map_simple.node.value_type, ProtoMapValueTypesEnum.ENUM_OR_MESSAGE
        )
        self.assertEqual(parsed_map_simple.node.name, ProtoIdentifier(None, "my_map"))
        self.assertEqual(
            parsed_map_simple.node.number, ProtoInt(None, 10, ProtoIntSign.POSITIVE)
        )
        self.assertEqual(
            parsed_map_simple.node.enum_or_message_type_name,
            ProtoEnumOrMessageIdentifier(None, "NestedMessage"),
        )
        self.assertEqual(
            parsed_map_simple.node.options,
            [
                ProtoMessageFieldOption(
                    None,
                    ProtoIdentifier(None, "java_package"),
                    ProtoConstant(None, ProtoStringLiteral(None, "com.example.foo")),
                ),
                ProtoMessageFieldOption(
                    None,
                    ProtoFullIdentifier(None, "baz.bat"),
                    ProtoConstant(None, ProtoInt(None, 48, ProtoIntSign.POSITIVE)),
                ),
            ],
        )

    def test_map_message_value(self):
        parsed_map_simple = ProtoMap.match(
            None, "map <string, string> string_map = 11;"
        )
        self.assertEqual(
            parsed_map_simple.node,
            ProtoMap(
                None,
                ProtoMapKeyTypesEnum.STRING,
                ProtoMapValueTypesEnum.STRING,
                ProtoIdentifier(None, "string_map"),
                ProtoInt(None, 11, ProtoIntSign.POSITIVE),
                None,
                [],
            ),
        )
