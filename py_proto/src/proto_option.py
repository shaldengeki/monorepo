from typing import Optional

from src.proto_constant import ProtoConstant
from src.proto_identifier import ProtoIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoOption(ProtoNode):
    def __init__(self, name: ProtoIdentifier, value: ProtoConstant):
        self.name = name
        self.value = value

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.value == other.value

    def __str__(self) -> str:
        return f"<ProtoOption name={self.name} value={self.value.serialize()}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("option "):
            return None
        proto_source = proto_source[7:]

        name_parts = []
        if proto_source.startswith("("):
            proto_source = proto_source[1:]
            match = ProtoIdentifier.match(proto_source)
            if not match or not match.remaining_source.startswith(")"):
                raise ValueError(
                    f"Proto has invalid option when expecting ): {proto_source}"
                )

            name_parts.append(ProtoIdentifier(f"({match.node.identifier})"))
            proto_source = match.remaining_source[1:]

        while True:
            match = ProtoIdentifier.match(proto_source)
            if match is None:
                break
            name_parts.append(match.node)
            proto_source = match.remaining_source

        proto_source = proto_source.strip()
        if not proto_source.startswith("="):
            raise ValueError(
                f"Proto has invalid option when expecting =: {proto_source}"
            )
        proto_source = proto_source[1:].strip()
        match = ProtoConstant.match(proto_source)
        if not match:
            raise ValueError(
                f"Proto has invalid option when expecting constant: {proto_source}"
            )

        proto_source = match.remaining_source
        if not match.remaining_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid option when expecting ;: {proto_source}"
            )

        return ParsedProtoNode(
            ProtoOption(
                name=ProtoIdentifier("".join(x.identifier for x in name_parts)),
                value=match.node,
            ),
            proto_source[1:],
        )

    def serialize(self) -> str:
        return f"option {self.name.serialize()} = {self.value.serialize()};"
