from typing import Optional

from src.proto_identifier import ProtoIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoEnum(ProtoNode):
    def __init__(self, name: ProtoIdentifier):
        self.name = name

    def __eq__(self, other: "ProtoEnum") -> bool:
        if not isinstance(other, ProtoEnum):
            return False

        return self.name == other.name

    def __str__(self) -> str:
        return f"<ProtoEnum name={self.name}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("enum "):
            return None

        proto_source = proto_source[5:]
        match = ProtoIdentifier.match(proto_source)
        if not match:
            raise ValueError(f"Proto has invalid enum name: {proto_source}")

        enum_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        proto_source = proto_source[1:]
        for i, c in enumerate(proto_source):
            if c == "}":
                break

        return ParsedProtoNode(ProtoEnum(enum_name), proto_source[i + 1 :].strip())

    def serialize(self) -> str:
        return "\n".join([f"enum {self.name} {{", "\}"])
