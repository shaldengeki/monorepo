from enum import Enum
from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_string_literal import ProtoStringLiteral


class ProtoSyntaxType(Enum):
    PROTO2 = "proto2"
    PROTO3 = "proto3"


class ProtoSyntax(ProtoNode):
    def __init__(self, syntax: ProtoStringLiteral):
        self.syntax = syntax

    def __eq__(self, other: "ProtoSyntax") -> bool:
        if not isinstance(other, ProtoSyntax):
            return False

        return self.syntax == other.syntax

    def __str__(self) -> str:
        return f"<ProtoSyntax syntax={self.syntax.serialize()}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("syntax = "):
            return None
        proto_source = proto_source[9:]
        match = ProtoStringLiteral.match(proto_source)
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

        return ParsedProtoNode(
            ProtoSyntax(match.node),
            match.remaining_source.strip(),
        )

    def serialize(self) -> str:
        return f"syntax = {self.syntax.serialize()};"
