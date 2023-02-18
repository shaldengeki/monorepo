from typing import Optional

from src.proto_bool import ProtoBool
from src.proto_float import ProtoFloat, ProtoFloatSign
from src.proto_identifier import ProtoFullIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_string_literal import ProtoStringLiteral

ProtoConstantTypes = (
    ProtoFullIdentifier | ProtoStringLiteral | ProtoInt | ProtoFloat | ProtoBool
)


class ParsedProtoConstantNode(ParsedProtoNode):
    node: "ProtoConstant"
    remaining_source: str


class ProtoConstant(ProtoNode):
    def __init__(
        self,
        value: ProtoConstantTypes,
    ):
        self.value = value

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return f"<ProtoConstant value={self.value}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoConstant":
        return self

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoConstantNode"]:
        match = ProtoBool.match(proto_source)
        if match is not None:
            return ParsedProtoConstantNode(
                ProtoConstant(match.node),
                match.remaining_source.strip(),
            )

        sign = ProtoIntSign.POSITIVE
        if proto_source.startswith("+") or proto_source.startswith("-"):
            sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
            proto_int_match = ProtoInt.match(proto_source[1:])
        else:
            proto_int_match = ProtoInt.match(proto_source)
        if proto_int_match is not None:
            proto_int_match.node.sign = sign
            return ParsedProtoConstantNode(
                ProtoConstant(proto_int_match.node),
                proto_int_match.remaining_source.strip(),
            )

        float_sign = ProtoFloatSign.POSITIVE
        if proto_source.startswith("+") or proto_source.startswith("-"):
            float_sign = next(x for x in ProtoFloatSign if x.value == proto_source[0])
            float_match = ProtoFloat.match(proto_source[1:])
        else:
            float_match = ProtoFloat.match(proto_source)
        if float_match is not None:
            float_match.node.sign = float_sign
            return ParsedProtoConstantNode(
                ProtoConstant(float_match.node),
                float_match.remaining_source.strip(),
            )

        identifier_match = ProtoFullIdentifier.match(proto_source)
        if identifier_match is not None:
            return ParsedProtoConstantNode(
                ProtoConstant(identifier_match.node),
                identifier_match.remaining_source.strip(),
            )

        string_literal_match = ProtoStringLiteral.match(proto_source)
        if string_literal_match is not None:
            return ParsedProtoConstantNode(
                ProtoConstant(string_literal_match.node),
                string_literal_match.remaining_source.strip(),
            )

        return None

    def serialize(self) -> str:
        if not isinstance(self.value, ProtoNode):
            raise ValueError(
                f"Proto has invalid constant: {self.value} with class: {self.value.__class__.__name__}"
            )

        return self.value.serialize()
