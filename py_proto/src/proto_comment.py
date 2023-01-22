import abc
from typing import Optional

from src.proto_identifier import ProtoFullIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoComment(ProtoNode):
    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        return f"<ProtoComment value={self.value}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> Optional["ProtoComment"]:
        return None

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        return None

    def serialize(self) -> str:
        return ""


class ProtoSingleLineComment(ProtoComment):
    def __str__(self) -> str:
        return f"<ProtoSingleLineComment value={self.value}>"

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("//"):
            return None

        proto_source = proto_source[2:]
        newline_pos = proto_source.find("\n")
        if newline_pos == -1:
            newline_pos = len(proto_source)
        return ParsedProtoNode(
            ProtoSingleLineComment(proto_source[:newline_pos]),
            proto_source[newline_pos + 1 :],
        )

    def serialize(self) -> str:
        return f"//{self.value}"


class ProtoMultiLineComment(ProtoComment):
    def __str__(self) -> str:
        return f"<ProtoMultiLineComment value={self.value}>"

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("/*"):
            return None

        proto_source = proto_source[2:]
        close_comment_pos = proto_source.find("*/")
        if close_comment_pos == -1:
            return None
        return ParsedProtoNode(
            ProtoMultiLineComment(proto_source[:close_comment_pos]),
            proto_source[close_comment_pos + 2 :],
        )

    def serialize(self) -> str:
        return f"/*{self.value}*/"
