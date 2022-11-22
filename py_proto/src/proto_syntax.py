from enum import Enum
from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_string_literal import ProtoStringLiteral


class ProtoSyntaxTypes(Enum):
    PROTO2 = "proto2"
    PROTO3 = "proto3"


class ProtoSyntax(ProtoNode):
    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("syntax = "):
            return None
        parts = proto_source.split(";")
        proto_source = ";".join(parts[1:])
        syntax_line = parts[0][9:]
        match = ProtoStringLiteral.match(syntax_line)
        if match is None:
            raise ValueError(f"Proto has invalid syntax syntax: {';'.join(parts)}")
        return ParsedProtoNode(
            ProtoSyntaxTypes[match.node.val.upper()],
            proto_source.strip(),
        )
