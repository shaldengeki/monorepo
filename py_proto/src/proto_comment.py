import abc
from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ParsedProtoCommentNode(ParsedProtoNode):
    node: "ProtoComment"
    remaining_source: str


class ProtoComment(ProtoNode):
    def __init__(self, value: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoCommentNode"]:
        return None

    def serialize(self) -> str:
        return ""


class ParsedProtoSingleLineCommentNode(ParsedProtoCommentNode):
    node: "ProtoSingleLineComment"
    remaining_source: str


class ProtoSingleLineComment(ProtoComment):
    def __str__(self) -> str:
        return f"<ProtoSingleLineComment value={self.value}>"

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoSingleLineCommentNode"]:
        if not proto_source.startswith("//"):
            return None

        proto_source = proto_source[2:]
        newline_pos = proto_source.find("\n")
        if newline_pos == -1:
            newline_pos = len(proto_source)
        return ParsedProtoSingleLineCommentNode(
            ProtoSingleLineComment(value=proto_source[:newline_pos], parent=parent),
            proto_source[newline_pos + 1 :],
        )

    def serialize(self) -> str:
        return f"//{self.value}"


class ParsedProtoMultiLineCommentNode(ParsedProtoCommentNode):
    node: "ProtoMultiLineComment"
    remaining_source: str


class ProtoMultiLineComment(ProtoComment):
    def __str__(self) -> str:
        return f"<ProtoMultiLineComment value={self.value}>"

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoMultiLineCommentNode"]:
        if not proto_source.startswith("/*"):
            return None

        proto_source = proto_source[2:]
        close_comment_pos = proto_source.find("*/")
        if close_comment_pos == -1:
            return None
        return ParsedProtoMultiLineCommentNode(
            ProtoMultiLineComment(
                value=proto_source[:close_comment_pos], parent=parent
            ),
            proto_source[close_comment_pos + 2 :],
        )

    def serialize(self) -> str:
        return f"/*{self.value}*/"
