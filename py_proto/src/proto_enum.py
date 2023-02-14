from typing import Optional

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff
from src.proto_option import ProtoOption
from src.proto_reserved import ProtoReserved


class ProtoEnumValueOption(ProtoOption):
    def __eq__(self, other) -> bool:
        return super().__eq__(other)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, value={self.value}>"

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        test_source = "option " + proto_source.strip() + ";"
        match = ProtoOption.match(test_source)
        if match is None:
            return None
        return ParsedProtoNode(
            cls(match.node.name, match.node.value),
            match.remaining_source.strip(),
        )

    def serialize(self) -> str:
        return f"{self.name.serialize()} = {self.value.serialize()}"


class ProtoEnumValue(ProtoNode):
    def __init__(
        self,
        identifier: ProtoIdentifier,
        value: ProtoInt,
        options: Optional[list[ProtoEnumValueOption]] = None,
    ):
        self.identifier = identifier
        self.value = value

        if options is None:
            self.options = []
        else:
            self.options = options

    def __eq__(self, other) -> bool:
        return (
            self.identifier == other.identifier
            and self.value == other.value
            and self.options == other.options
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValue identifier={self.identifier}, value={self.value}, options={self.options}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoEnumValue":
        return ProtoEnumValue(
            self.identifier,
            self.value,
            sorted(self.options, key=lambda o: o.name),
        )

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
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
        proto_source = match.remaining_source.strip()

        options = []
        if proto_source.startswith("["):
            proto_source = proto_source[1:].strip()
            end_bracket = proto_source.find("]")
            if end_bracket == -1:
                raise ValueError(
                    f"Proto has invalid enum value option syntax, cannot find ]: {proto_source}"
                )
            for option_part in proto_source[:end_bracket].strip().split(","):
                match = ProtoEnumValueOption.match(option_part.strip())
                if match is None:
                    raise ValueError(
                        f"Proto has invalid enum value option syntax: {proto_source}"
                    )
                options.append(match.node)
            proto_source = proto_source[end_bracket + 1 :].strip()

        return ParsedProtoNode(
            ProtoEnumValue(enum_value_name, enum_value, options), proto_source.strip()
        )

    def serialize(self) -> str:
        serialized_parts = [self.identifier.serialize(), "=", self.value.serialize()]
        if self.options:
            serialized_parts.append("[")
            serialized_parts.append(
                ", ".join(option.serialize() for option in self.options)
            )
            serialized_parts.append("]")
        return " ".join(serialized_parts) + ";"


class ProtoEnum(ProtoNode):
    def __init__(self, name: ProtoIdentifier, nodes: list[ProtoNode]):
        self.name = name
        self.nodes = nodes

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<ProtoEnum name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoEnum":
        non_comment_nodes = filter(
            lambda n1: not isinstance(n1, ProtoComment), self.nodes
        )
        return ProtoEnum(
            self.name,
            sorted(non_comment_nodes, key=lambda n: str(n.normalize())),
        )

    @staticmethod
    def parse_partial_content(partial_enum_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoOption,
            ProtoReserved,
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

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
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

    @staticmethod
    def diff(left: "ProtoEnum", right: "ProtoEnum") -> list["ProtoNodeDiff"]:
        if left is None and right is not None:
            return [ProtoEnumAdded(right)]
        elif left is not None and right is None:
            return [ProtoEnumRemoved(left)]
        elif left is None and right is None:
            return []
        elif left.name != right.name:
            return []
        elif left == right:
            return []
        # TODO: process the enum options and values.
        return []

    @staticmethod
    def diff_sets(
        left: list["ProtoEnum"], right: list["ProtoEnum"]
    ) -> list["ProtoNodeDiff"]:
        diffs = []
        left_names = set(o.name.identifier for o in left)
        right_names = set(o.name.identifier for o in right)
        for name in left_names - right_names:
            diffs.append(
                ProtoEnumAdded(next(i for i in left if i.name.identifier == name))
            )
        for name in right_names - left_names:
            diffs.append(
                ProtoEnumRemoved(next(i for i in right if i.name.identifier == name))
            )
        for name in left_names & right_names:
            left_option = next(i for i in left if i.name.identifier == name)
            right_option = next(i for i in right if i.name.identifier == name)
            diffs.extend(ProtoEnum.diff(left_option, right_option))

        return diffs


class ProtoEnumAdded(ProtoNodeDiff):
    def __init__(self, enum: ProtoEnum):
        self.enum = enum

    def __eq__(self, other: "ProtoEnumAdded") -> bool:
        return isinstance(other, ProtoEnumAdded) and self.enum == other.enum

    def __str__(self) -> str:
        return f"<ProtoEnumAdded enum={self.enum}>"

    def __repr__(self) -> str:
        return str(self)


class ProtoEnumRemoved(ProtoNodeDiff):
    def __init__(self, enum: ProtoEnum):
        self.enum = enum

    def __eq__(self, other: "ProtoEnumRemoved") -> bool:
        return isinstance(other, ProtoEnumRemoved) and self.enum == other.enum

    def __str__(self) -> str:
        return f"<ProtoEnumRemoved enum={self.enum}>"

    def __repr__(self) -> str:
        return str(self)


class ProtoEnumValueAdded(ProtoNodeDiff):
    def __init__(self, enum: "ProtoEnum", enum_value: "ProtoEnumValue"):
        self.enum = enum
        self.enum_value = enum_value

    def __eq__(self, other: "ProtoEnumValueAdded") -> bool:
        return (
            isinstance(other, ProtoEnumValueAdded)
            and self.enum == other.enum
            and self.enum_value == other.enum_value
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValueAdded enum={self.enum} enum_value={self.enum_value}>"

    def __repr__(self) -> str:
        return str(self)


class ProtoEnumValueRemoved(ProtoNodeDiff):
    def __init__(self, enum: "ProtoEnum", enum_value: "ProtoEnumValue"):
        self.enum = enum
        self.enum_value = enum_value

    def __eq__(self, other: "ProtoEnumValueRemoved") -> bool:
        return (
            isinstance(other, ProtoEnumValueRemoved)
            and self.enum == other.enum
            and self.enum_value == other.enum_value
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValueRemoved enum={self.enum} enum_value={self.enum_value}>"

    def __repr__(self) -> str:
        return str(self)


class ProtoEnumValueNameChanged(ProtoNodeDiff):
    def __init__(
        self, enum: ProtoEnum, enum_value: ProtoEnumValue, new_name: ProtoIdentifier
    ):
        self.enum = enum
        self.enum_value = enum_value
        self.new_name = new_name

    def __eq__(self, other: "ProtoEnumValueNameChanged") -> bool:
        return (
            isinstance(other, ProtoEnumValueNameChanged)
            and self.enum == other.enum
            and self.enum_value == other.enum_value
            and self.new_name == other.new_name
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValueNameChanged enum={self.enum} enum_value={self.enum_value} new_name={self.new_name}>"

    def __repr__(self) -> str:
        return str(self)


class ProtoEnumValueValueChanged(ProtoNodeDiff):
    def __init__(
        self, enum: ProtoEnum, enum_value: ProtoEnumValue, new_value: ProtoInt
    ):
        self.enum = enum
        self.enum_value = enum_value
        self.new_value = new_value

    def __eq__(self, other: "ProtoEnumValueNameChanged") -> bool:
        return (
            isinstance(other, ProtoEnumValueNameChanged)
            and self.enum == other.enum
            and self.enum_value == other.enum_value
            and self.new_value == other.new_value
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValueNameChanged enum={self.enum} enum_value={self.enum_value} new_value={self.new_value}>"

    def __repr__(self) -> str:
        return str(self)
