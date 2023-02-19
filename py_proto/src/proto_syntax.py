from enum import Enum
from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff
from src.proto_string_literal import ProtoStringLiteral


class ParsedProtoSyntaxNode(ParsedProtoNode):
    node: "ProtoSyntax"
    remaining_source: str


class ProtoSyntaxType(Enum):
    PROTO2 = "proto2"
    PROTO3 = "proto3"


class ProtoSyntax(ProtoNode):
    def __init__(self, parent: Optional[ProtoNode], syntax: ProtoStringLiteral):
        super().__init__(parent)
        self.syntax = syntax

    def __eq__(self, other) -> bool:
        return self.syntax == other.syntax

    def __str__(self) -> str:
        return f"<ProtoSyntax syntax={self.syntax.serialize()}>"

    def __repr__(self) -> str:
        return str(self)

    def __dict__(self):
        return {"syntax": self.syntax.serialize()}

    def normalize(self) -> "ProtoSyntax":
        return self

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoSyntaxNode"]:
        if not proto_source.startswith("syntax = "):
            return None
        proto_source = proto_source[9:]
        match = ProtoStringLiteral.match(None, proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid syntax syntax: {proto_source}")
        if not match.remaining_source.startswith(";"):
            raise ValueError(f"Proto has invalid syntax: {proto_source}")
        try:
            syntax_type = ProtoSyntaxType[match.node.value.upper()]
        except KeyError:
            raise ValueError(
                f"Proto has unknown syntax type: {match.node.value}, must be one of: {[proto_type.name for proto_type in ProtoSyntaxType]}"
            )

        return ParsedProtoSyntaxNode(
            ProtoSyntax(parent, match.node),
            match.remaining_source.strip(),
        )

    def serialize(self) -> str:
        return f"syntax = {self.syntax.serialize()};"

    @staticmethod
    def diff(left: "ProtoSyntax", right: "ProtoSyntax") -> list["ProtoNodeDiff"]:
        if left == right:
            return []
        return [ProtoSyntaxChanged(left, right)]


class ProtoSyntaxChanged(ProtoNodeDiff):
    def __init__(self, left: ProtoSyntax, right: ProtoSyntax):
        self.left = left
        self.right = right

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoSyntaxChanged)
            and self.left == other.left
            and self.right == other.right
        )
