from typing import Optional

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import (
    ParsedProtoEnumOrMessageIdentifierNode,
    ProtoEnumOrMessageIdentifier,
)
from src.proto_message_field import ProtoMessageField
from src.proto_node import ParsedProtoNode, ProtoContainerNode, ProtoNode


class ProtoExtend(ProtoContainerNode):
    def __init__(
        self,
        name: ProtoEnumOrMessageIdentifier,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.name == other.name

    def __str__(self) -> str:
        return f"<ProtoExtend name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoExtend":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )
        return ProtoExtend(
            name=self.name,
            nodes=sorted(non_comment_nodes, key=lambda f: str(f)),
            parent=self.parent,
        )

    @classmethod
    def container_types(cls) -> list[type[ProtoNode]]:
        return [
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoMessageField,
        ]

    @classmethod
    def match_header(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoEnumOrMessageIdentifierNode"]:
        if not proto_source.startswith("extend "):
            return None

        proto_source = proto_source[7:]
        match = ProtoEnumOrMessageIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto extend has invalid message name: {proto_source}")

        name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto extend has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        return ParsedProtoEnumOrMessageIdentifierNode(name, proto_source[1:].strip())

    @classmethod
    def construct(
        cls,
        header_match: ParsedProtoNode,
        contained_nodes: list[ProtoNode],
        footer_match: str,
        parent: Optional[ProtoNode] = None,
    ) -> ProtoNode:
        assert isinstance(header_match, ParsedProtoEnumOrMessageIdentifierNode)
        return ProtoExtend(name=header_match.node, nodes=contained_nodes, parent=parent)

    def serialize(self) -> str:
        serialize_parts = (
            [f"extend {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)
