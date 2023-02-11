from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoIdentifier(ProtoNode):
    ALPHABETICAL = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    STARTING = ALPHABETICAL | set("_")
    ALL = STARTING | set("0123456789_")

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __eq__(self, other) -> bool:
        return self.identifier == other.identifier

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} identifier={self.identifier}>"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def normalize(self) -> "ProtoIdentifier":
        return self

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if proto_source[0] not in ProtoIdentifier.STARTING:
            return None

        for i, c in enumerate(proto_source):
            if c not in ProtoIdentifier.ALL:
                return ParsedProtoNode(
                    ProtoIdentifier(proto_source[:i]), proto_source[i:]
                )
        return ParsedProtoNode(ProtoIdentifier(proto_source), "")

    def serialize(self) -> str:
        return self.identifier


class ProtoFullIdentifier(ProtoIdentifier):
    STARTING = ProtoIdentifier.STARTING
    ALL = ProtoIdentifier.ALL | set(".")

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if proto_source[0] not in ProtoFullIdentifier.STARTING:
            return None

        last_part_start = 0
        identifier_parts = []
        for i, c in enumerate(proto_source):
            if c not in ProtoFullIdentifier.ALL:
                if i == last_part_start:
                    # We have an invalid character after a period.
                    raise ValueError(
                        f"Proto source has invalid identifier, expecting alphanumeric after .: {proto_source}"
                    )
                identifier_parts.append(proto_source[last_part_start:i])
                return ParsedProtoNode(
                    ProtoFullIdentifier(".".join(identifier_parts)), proto_source[i:]
                )
            elif c == ".":
                identifier_parts.append(proto_source[last_part_start:i])
                last_part_start = i + 1

        # we got to the end while resolving this identifier.
        if last_part_start >= len(proto_source):
            raise ValueError(
                f"Proto source has invalid identifier, expecting alphanumeric after .: {proto_source}"
            )
        identifier_parts.append(proto_source[last_part_start:])
        return ParsedProtoNode(ProtoFullIdentifier(".".join(identifier_parts)), "")


class ProtoEnumOrMessageIdentifier(ProtoIdentifier):
    STARTING = ProtoIdentifier.ALPHABETICAL | set(".")
    ALL = ProtoIdentifier.ALL | set(".")

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if proto_source[0] == ".":
            matched_source = proto_source[1:]
        else:
            matched_source = proto_source

        match = ProtoFullIdentifier.match(matched_source)
        if match is not None:
            match = ParsedProtoNode(
                ProtoEnumOrMessageIdentifier(match.node.identifier),
                match.remaining_source,
            )

            if proto_source[0] == ".":
                match.node.identifier = "." + match.node.identifier
        return match
