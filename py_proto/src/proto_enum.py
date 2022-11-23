from typing import Optional

from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_option import ProtoOption


class ProtoEnumValue(ProtoNode):
    def __init__(
        self,
        identifier: ProtoIdentifier,
        value: ProtoInt,
        options: Optional[list[ProtoOption]] = None,
    ):
        self.identifier = identifier
        self.value = value

        if options is None:
            self.options = []
        else:
            self.options = options

    def __eq__(self, other: "ProtoEnum") -> bool:
        if not isinstance(other, ProtoEnumValue):
            return False

        return (
            self.identifier == other.identifier
            and self.value == other.value
            and self.options == other.options
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValue identifier={self.identifier}, value={self.value}, options={self.options}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid enum value name: {proto_source}")

        enum_value_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("="):
            raise ValueError(
                f"Proto has invalid enum value syntax, expecting =: {proto_source}"
            )

        proto_source = proto_source[1:].strip()

        sign = ProtoIntSign.POSITIVE
        if proto_source.startswith("-"):
            sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
            match = ProtoInt.match(proto_source[1:])
        else:
            match = ProtoInt.match(proto_source)
        if match is None:
            raise ValueError(
                f"Proto has invalid enum value, expecting int: {proto_source}"
            )

        match.node.sign = sign
        enum_value = match.node
        proto_source = match.remaining_source

        # TODO: parse options.

        return ParsedProtoNode(
            ProtoEnumValue(enum_value_name, enum_value, []), proto_source.strip()
        )

    def serialize(self) -> str:
        serialized_parts = [self.identifier.serialize(), "=", self.value.serialize()]
        if self.options:
            serialized_parts.append("[")
            # TODO: serialize options.
            serialized_parts.append("]")
        return " ".join(serialized_parts) + ";"


class ProtoEnum(ProtoNode):
    def __init__(self, name: ProtoIdentifier, nodes: list[ProtoNode]):
        self.name = name
        self.nodes = nodes

    def __eq__(self, other: "ProtoEnum") -> bool:
        if not isinstance(other, ProtoEnum):
            return False

        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<ProtoEnum name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def parse_partial_content(partial_enum_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoOption,
            ProtoEnumValue,
        ):
            try:
                match_result = node_type.match(partial_enum_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial enum content:\n{partial_enum_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(
            f"Could not parse partial enum content:\n{partial_enum_content}"
        )

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("enum "):
            return None

        proto_source = proto_source[5:]
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid enum name: {proto_source}")

        enum_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        proto_source = proto_source[1:].strip()
        parsed_tree = []
        while proto_source:
            # Remove empty statements.
            if proto_source.startswith(";"):
                proto_source = proto_source[1:].strip()
                continue

            if proto_source.startswith("}"):
                proto_source = proto_source[1:].strip()
                break

            match_result = ProtoEnum.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoNode(ProtoEnum(enum_name, nodes=parsed_tree), proto_source)

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    def serialize(self) -> str:
        serialize_parts = (
            [f"enum {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)
