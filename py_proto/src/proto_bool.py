from typing import Optional

from src.proto_identifier import ProtoFullIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ParsedProtoBoolNode(ParsedProtoNode):
    node: "ProtoBool"
    remaining_source: str


class ProtoBool(ProtoNode):
    def __init__(self, value: bool):
        self.value = value

    def __bool__(self) -> bool:
        return self.value

    def __eq__(self, other) -> bool:
        return bool(self) == bool(other)

    def __str__(self) -> str:
        return f"<ProtoBool value={self.value}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoBool":
        return self

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoBoolNode"]:
        if proto_source.startswith("true") and (
            len(proto_source) == 4 or proto_source[4] not in ProtoFullIdentifier.ALL
        ):
            return ParsedProtoBoolNode(ProtoBool(True), proto_source[4:].strip())
        elif proto_source.startswith("false") and (
            len(proto_source) == 5 or proto_source[5] not in ProtoFullIdentifier.ALL
        ):
            return ParsedProtoBoolNode(ProtoBool(False), proto_source[5:].strip())
        return None

    def serialize(self) -> str:
        return str(self.value).lower()
