from typing import Optional


class ProtoNode:
    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        raise NotImplementedError

    def serialize(self) -> str:
        raise NotImplementedError


class ParsedProtoNode:
    def __init__(self, parsed_node: "ProtoNode", remaining_source: str):
        self.node = parsed_node
        self.remaining_source = remaining_source

    def __eq__(self, other: "ParsedProtoNode") -> bool:
        return (self.node == other.node) and (
            self.remaining_source == other.remaining_source
        )

    def __str__(self) -> str:
        return f"<ParsedProtoNode node={self.node} remaining_source={self.remaining_source} >"

    def __repr__(self) -> str:
        return str(self)
