from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ParsedProtoIdentifierNode(ParsedProtoNode):
    node: "ProtoIdentifier"
    remaining_source: str


class ParsedProtoFullIdentifierNode(ParsedProtoIdentifierNode):
    node: "ProtoFullIdentifier"
    remaining_source: str


class ParsedProtoEnumOrMessageIdentifierNode(ParsedProtoIdentifierNode):
    node: "ProtoEnumOrMessageIdentifier"
    remaining_source: str


class ProtoIdentifier(ProtoNode):
    ALPHABETICAL = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    STARTING = ALPHABETICAL | set("_")
    ALL = STARTING | set("0123456789_")

    def __init__(self, identifier: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoIdentifierNode"]:
        if proto_source[0] not in ProtoIdentifier.STARTING:
            return None

        for i, c in enumerate(proto_source):
            if c not in ProtoIdentifier.ALL:
                return ParsedProtoIdentifierNode(
                    ProtoIdentifier(identifier=proto_source[:i], parent=parent),
                    proto_source[i:],
                )
        return ParsedProtoIdentifierNode(
            ProtoIdentifier(identifier=proto_source, parent=parent), ""
        )

    def serialize(self) -> str:
        return self.identifier


class ProtoFullIdentifier(ProtoIdentifier):
    STARTING = ProtoIdentifier.STARTING
    ALL = ProtoIdentifier.ALL | set(".")

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoFullIdentifierNode"]:
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
                return ParsedProtoFullIdentifierNode(
                    ProtoFullIdentifier(
                        identifier=".".join(identifier_parts), parent=parent
                    ),
                    proto_source[i:],
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
        return ParsedProtoFullIdentifierNode(
            ProtoFullIdentifier(identifier=".".join(identifier_parts), parent=parent),
            "",
        )


class ProtoEnumOrMessageIdentifier(ProtoIdentifier):
    STARTING = ProtoIdentifier.ALPHABETICAL | set(".")
    ALL = ProtoIdentifier.ALL | set(".")

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoEnumOrMessageIdentifierNode"]:
        if proto_source[0] == ".":
            matched_source = proto_source[1:]
        else:
            matched_source = proto_source

        identifier_match = ProtoFullIdentifier.match(matched_source, parent=parent)
        if identifier_match is not None:
            match = ParsedProtoEnumOrMessageIdentifierNode(
                ProtoEnumOrMessageIdentifier(
                    identifier=identifier_match.node.identifier, parent=parent
                ),
                identifier_match.remaining_source,
            )

            if proto_source[0] == ".":
                match.node.identifier = "." + match.node.identifier
            return match
        return identifier_match
