from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ParsedProtoStringLiteralNode(ParsedProtoNode):
    node: "ProtoStringLiteral"
    remaining_source: str


class ProtoStringLiteral(ProtoNode):
    QUOTES = ['"', "'"]

    def __init__(self, parent: Optional[ProtoNode], val: str, quote: str = QUOTES[0]):
        super().__init__(parent)
        self.value = val
        self.quote = quote

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return f"<ProtoStringLiteral value={self.serialize()}>"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def normalize(self) -> "ProtoStringLiteral":
        return self

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoStringLiteralNode"]:
        if not any(proto_source.startswith(c) for c in ProtoStringLiteral.QUOTES):
            return None
        escaped = False
        starting_quote = proto_source[0]
        for i, c in enumerate(proto_source[1:]):
            if c == "\\":
                escaped = True
                continue
            if c == starting_quote and not escaped:
                return ParsedProtoStringLiteralNode(
                    ProtoStringLiteral(
                        parent, proto_source[1 : i + 1], quote=starting_quote
                    ),
                    proto_source[i + 2 :].strip(),
                )
            escaped = False
        return None

    def serialize(self) -> str:
        return "".join([self.quote, self.value, self.quote])
