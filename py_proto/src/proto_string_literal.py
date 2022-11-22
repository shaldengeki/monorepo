from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoStringLiteral(ProtoNode):
    QUOTES = {'"', "'"}

    def __init__(self, val: str):
        self.val = val

    def __eq__(self, other) -> bool:
        return self.val == other.val

    def __str__(self) -> str:
        return f"<ProtoStringLiteral val='{self.val}'>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not any(proto_source.startswith(c) for c in ProtoStringLiteral.QUOTES):
            return None
        escaped = False
        starting_quote = proto_source[0]
        for i, c in enumerate(proto_source[1:]):
            if c == "\\":
                escaped = True
                continue
            if c == starting_quote and not escaped:
                return ParsedProtoNode(
                    ProtoStringLiteral(proto_source[1 : i + 1]),
                    proto_source[i + 2 :].strip(),
                )
            escaped = False
        return None
