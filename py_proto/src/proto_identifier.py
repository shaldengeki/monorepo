from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoIdentifier(ProtoNode):
    ALPHABETICAL = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    STARTING = ALPHABETICAL | set(".")
    PART = ALPHABETICAL | set("0123456789_")
    ALL = PART | set(".")

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __eq__(self, other: "ProtoIdentifier") -> bool:
        if not isinstance(other, ProtoIdentifier):
            return False

        return self.identifier == other.identifier

    def __str__(self) -> str:
        return f"<ProtoIdentifier identifier={self.identifier}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if proto_source[0] not in ProtoIdentifier.STARTING:
            return None

        in_part = True
        for i, c in enumerate(proto_source):
            if c == ".":
                if not in_part:
                    raise ValueError(f"Proto has invalid identifier: {proto_source}")
                in_part = False
            else:
                if not in_part and c not in ProtoIdentifier.STARTING:
                    raise ValueError(f"Proto has invalid identifier: {proto_source}")

                if c in ProtoIdentifier.PART:
                    in_part = True
                else:
                    return ParsedProtoNode(
                        ProtoIdentifier(proto_source[:i]), proto_source[i:]
                    )

        if not in_part:
            raise ValueError(f"Proto has invalid identifier: {proto_source}")

        return ParsedProtoNode(ProtoIdentifier(proto_source), "")

    def serialize(self) -> str:
        return self.identifier
