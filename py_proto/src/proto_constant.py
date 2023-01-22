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
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        match = ProtoBool.match(proto_source)
        if match is not None:
            return ParsedProtoNode(
                ProtoConstant(match.node),
                match.remaining_source.strip(),
            )

        sign = ProtoIntSign.POSITIVE
        if proto_source.startswith("+") or proto_source.startswith("-"):
            sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
            match = ProtoInt.match(proto_source[1:])
        else:
            match = ProtoInt.match(proto_source)
        if match is not None:
            match.node.sign = sign
            return ParsedProtoNode(
                ProtoConstant(match.node),
                match.remaining_source.strip(),
            )

        sign = ProtoFloatSign.POSITIVE
        if proto_source.startswith("+") or proto_source.startswith("-"):
            sign = next(x for x in ProtoFloatSign if x.value == proto_source[0])
            match = ProtoFloat.match(proto_source[1:])
        else:
            match = ProtoFloat.match(proto_source)
        if match is not None:
            match.node.sign = sign
            return ParsedProtoNode(
                ProtoConstant(match.node),
                match.remaining_source.strip(),
            )

        match = ProtoFullIdentifier.match(proto_source)
        if match is not None:
            return ParsedProtoNode(
                ProtoConstant(match.node),
                match.remaining_source.strip(),
            )

        match = ProtoStringLiteral.match(proto_source)
        if match is not None:
            return ParsedProtoNode(
                ProtoConstant(match.node),
                match.remaining_source.strip(),
            )

        return None

    def serialize(self) -> str:
        if not isinstance(self.value, ProtoNode):
            raise ValueError(
                f"Proto has invalid constant: {self.value} with class: {self.value.__class__.__name__}"
            )

        return self.value.serialize()
