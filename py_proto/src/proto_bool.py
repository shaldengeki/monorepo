from typing import Optional

from src.proto_identifier import ProtoIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoBool(ProtoNode):
    def __init__(self, value: bool):
        self.value = value

    def __eq__(self, other: "ProtoBool") -> bool:
        if not isinstance(other, ProtoBool):
            return False

        return self.value == other.value

    def __str__(self) -> str:
        return f"<ProtoBool value={self.serialize()}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if proto_source.startswith("true") and (
            len(proto_source) == 4 or proto_source[4] not in ProtoIdentifier.ALL
        ):
            return ParsedProtoNode(ProtoBool(True), proto_source[4:].strip())
        elif proto_source.startswith("false") and (
            len(proto_source) == 5 or proto_source[5] not in ProtoIdentifier.ALL
        ):
            return ParsedProtoNode(ProtoBool(False), proto_source[5:].strip())
        return None

    def serialize(self) -> str:
        return str(self.value).lower()
