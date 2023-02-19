from typing import Optional

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import ProtoEnumOrMessageIdentifier
from src.proto_message_field import ProtoMessageField
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoExtend(ProtoNode):
    def __init__(
        self,
        parent: Optional[ProtoNode],
        name: ProtoEnumOrMessageIdentifier,
        nodes: list[ProtoNode],
    ):
        super().__init__(parent)
        self.name = name
        self.name.parent = self
        self.nodes = nodes
        for node in self.nodes:
            node.parent = self

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<ProtoExtend name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoExtend":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )
        return ProtoExtend(
            self.parent,
            name=self.name,
            nodes=sorted(non_comment_nodes, key=lambda f: str(f)),
        )

    @staticmethod
    def parse_partial_content(partial_content: str) -> ParsedProtoNode:
        supported_types: list[type[ProtoNode]] = [
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoMessageField,
        ]
        for node_type in supported_types:
            try:
                match_result = node_type.match(None, partial_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial extend content:\n{partial_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(f"Could not parse partial extend content:\n{partial_content}")

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("extend "):
            return None

        proto_source = proto_source[7:]
        match = ProtoEnumOrMessageIdentifier.match(None, proto_source)
        if match is None:
            raise ValueError(f"Proto extend has invalid message name: {proto_source}")

        name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto extend has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        proto_source = proto_source[1:].strip()
        parsed_tree = []
        while proto_source:
            # Remove empty statements.
            if proto_source.startswith(";"):
                proto_source = proto_source[1:].strip()
                continue

            if proto_source.startswith("}"):
                proto_source = proto_source[1:].strip()
                break

            match_result = ProtoExtend.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoNode(
            ProtoExtend(parent, name, nodes=parsed_tree), proto_source
        )

    def serialize(self) -> str:
        serialize_parts = (
            [f"extend {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)
