from typing import Optional, Sequence

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff
from src.proto_option import ParsedProtoOptionNode, ProtoOption, ProtoOptionDiff
from src.proto_reserved import ProtoReserved


class ParsedProtoEnumValueOptionNode(ParsedProtoOptionNode):
    node: "ProtoEnumValueOption"
    remaining_source: str


class ProtoEnumValueOption(ProtoOption):
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, value={self.value}>"

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoEnumValueOptionNode"]:
        test_source = "option " + proto_source.strip() + ";"
        match = ProtoOption.match(None, test_source)
        if match is None:
            return None
        return ParsedProtoEnumValueOptionNode(
            cls(parent, match.node.name, match.node.value),
            match.remaining_source.strip(),
        )

    def serialize(self) -> str:
        return f"{self.name.serialize()} = {self.value.serialize()}"


class ParsedProtoEnumValueNode(ParsedProtoNode):
    node: "ProtoEnumValue"
    remaining_source: str


class ProtoEnumValue(ProtoNode):
    def __init__(
        self,
        parent: Optional[ProtoNode],
        identifier: ProtoIdentifier,
        value: ProtoInt,
        options: Optional[list[ProtoEnumValueOption]] = None,
    ):
        super().__init__(parent)
        self.identifier = identifier
        self.identifier.parent = self
        self.value = value
        self.value.parent = self

        if options is None:
            self.options = []
        else:
            self.options = options
        for option in self.options:
            option.parent = self

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

    def __hash__(self) -> int:
        return hash(str(self))

    def normalize(self) -> "ProtoEnumValue":
        return ProtoEnumValue(
            self.parent,
            self.identifier,
            self.value,
            sorted(self.options, key=lambda o: str(o.name)),
        )

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoEnumValueNode"]:
        match = ProtoIdentifier.match(None, proto_source)
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
            int_match = ProtoInt.match(None, proto_source[1:])
        else:
            int_match = ProtoInt.match(None, proto_source)
        if int_match is None:
            raise ValueError(
                f"Proto has invalid enum value, expecting int: {proto_source}"
            )

        int_match.node.sign = sign
        enum_value = int_match.node
        proto_source = int_match.remaining_source.strip()

        options: list[ProtoEnumValueOption] = []
        if proto_source.startswith("["):
            proto_source = proto_source[1:].strip()
            end_bracket = proto_source.find("]")
            if end_bracket == -1:
                raise ValueError(
                    f"Proto has invalid enum value option syntax, cannot find ]: {proto_source}"
                )
            for option_part in proto_source[:end_bracket].strip().split(","):
                proto_enum_value_option_match = ProtoEnumValueOption.match(
                    None, option_part.strip()
                )
                if proto_enum_value_option_match is None:
                    raise ValueError(
                        f"Proto has invalid enum value option syntax: {proto_source}"
                    )
                options.append(proto_enum_value_option_match.node)
            proto_source = proto_source[end_bracket + 1 :].strip()

        return ParsedProtoEnumValueNode(
            ProtoEnumValue(parent, enum_value_name, enum_value, options),
            proto_source.strip(),
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

    @staticmethod
    def diff(
        enum: "ProtoEnum", left: "ProtoEnumValue", right: "ProtoEnumValue"
    ) -> Sequence["ProtoNodeDiff"]:
        if left is None and right is not None:
            return [ProtoEnumValueAdded(right)]
        elif left is not None and right is None:
            return [ProtoEnumValueRemoved(left)]
        elif left is None and right is None:
            return []
        elif left.identifier != right.identifier:
            return []
        elif left == right:
            return []
        diffs: list["ProtoNodeDiff"] = []
        # TODO: scope these diffs under ProtoEnumValue
        diffs.extend(ProtoEnumValueOption.diff_sets(left.options, right.options))
        diffs.append(ProtoEnumValueValueChanged(enum, right, left.value))

        return diffs

    @staticmethod
    def diff_sets(
        enum: "ProtoEnum", left: list["ProtoEnumValue"], right: list["ProtoEnumValue"]
    ) -> list["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
        left_names = set(o.identifier.identifier for o in left)
        left_values = set(int(o.value) for o in left)
        right_names = set(o.identifier.identifier for o in right)
        right_values = set(int(o.value) for o in right)

        for name in left_names - right_names:
            # Check to see if this is a renamed field number.
            left_value = next(i for i in left if i.identifier.identifier == name)
            if int(left_value.value) in right_values:
                # This is a renamed field number.
                right_value = next(
                    i for i in right if int(i.value) == int(left_value.value)
                )
                diffs.append(
                    ProtoEnumValueNameChanged(enum, right_value, left_value.identifier)
                )
            else:
                diffs.append(ProtoEnumValueAdded(enum, left_value))
        for name in right_names - left_names:
            # Check to see if this is a renamed field number.
            right_value = next(i for i in right if i.identifier.identifier == name)
            if int(right_value.value) not in left_values:
                diffs.append(
                    ProtoEnumValueRemoved(
                        enum, next(i for i in right if i.identifier.identifier == name)
                    )
                )
        for name in left_names & right_names:
            left_enum_value = next(i for i in left if i.identifier.identifier == name)
            right_enum_value = next(i for i in right if i.identifier.identifier == name)
            diffs.extend(ProtoEnumValue.diff(enum, left_enum_value, right_enum_value))

        return diffs


class ProtoEnum(ProtoNode):
    def __init__(
        self, parent: Optional[ProtoNode], name: ProtoIdentifier, nodes: list[ProtoNode]
    ):
        super().__init__(parent)
        self.name = name
        self.name.parent = self
        self.nodes = nodes
        for option in self.options:
            option.parent = self

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoEnum)
            and self.name == other.name
            and self.nodes == other.nodes
        )

    def __str__(self) -> str:
        return f"<ProtoEnum name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoEnum":
        non_comment_nodes = filter(
            lambda n1: not isinstance(n1, ProtoComment), self.nodes
        )
        return ProtoEnum(
            self.parent,
            self.name,
            sorted(non_comment_nodes, key=lambda n: str(n.normalize())),
        )

    @staticmethod
    def parse_partial_content(partial_enum_content: str) -> ParsedProtoNode:
        supported_types: list[type[ProtoNode]] = [
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoOption,
            ProtoReserved,
            ProtoEnumValue,
        ]
        for node_type in supported_types:
            try:
                match_result = node_type.match(None, partial_enum_content)
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
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("enum "):
            return None

        proto_source = proto_source[5:]
        match = ProtoIdentifier.match(None, proto_source)
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

        return ParsedProtoNode(
            ProtoEnum(parent, enum_name, nodes=parsed_tree), proto_source
        )

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    @property
    def values(self) -> list[ProtoEnumValue]:
        return [node for node in self.nodes if isinstance(node, ProtoEnumValue)]

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
        diffs: list[ProtoNodeDiff] = []
        # TODO: scope these diffs under ProtoEnum
        diffs.extend(ProtoOption.diff_sets(left.options, right.options))
        diffs.extend(ProtoEnumValue.diff_sets(left, left.values, right.values))
        return diffs

    @staticmethod
    def diff_sets(
        left: list["ProtoEnum"], right: list["ProtoEnum"]
    ) -> list["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
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
            left_enum = next(i for i in left if i.name.identifier == name)
            right_enum = next(i for i in right if i.name.identifier == name)
            diffs.extend(ProtoEnum.diff(left_enum, right_enum))

        return diffs


class ProtoEnumDiff(ProtoNodeDiff):
    def __init__(self, enum: ProtoEnum):
        self.enum = enum

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProtoEnumDiff) and self.enum == other.enum

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} enum={self.enum}>"


class ProtoEnumAdded(ProtoEnumDiff):
    pass


class ProtoEnumRemoved(ProtoEnumDiff):
    pass


class ProtoEnumValueDiff(ProtoEnumDiff):
    def __init__(self, enum: "ProtoEnum", enum_value: "ProtoEnumValue"):
        super().__init__(enum)
        self.enum_value = enum_value

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, ProtoEnumValueDiff)
            and self.enum_value == other.enum_value
        )

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} enum={self.enum} enum_value={self.enum_value}>"
        )


class ProtoEnumValueAdded(ProtoEnumValueDiff):
    pass


class ProtoEnumValueRemoved(ProtoEnumValueDiff):
    pass


class ProtoEnumValueNameChanged(ProtoEnumValueDiff):
    def __init__(
        self, enum: ProtoEnum, enum_value: ProtoEnumValue, new_name: ProtoIdentifier
    ):
        super().__init__(enum, enum_value)
        self.new_name = new_name

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, ProtoEnumValueNameChanged)
            and self.new_name == other.new_name
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValueNameChanged enum={self.enum} enum_value={self.enum_value} new_name={self.new_name}>"


class ProtoEnumValueValueChanged(ProtoEnumValueDiff):
    def __init__(
        self, enum: ProtoEnum, enum_value: ProtoEnumValue, new_value: ProtoInt
    ):
        super().__init__(enum, enum_value)
        self.new_value = new_value

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, ProtoEnumValueValueChanged)
            and self.new_value == other.new_value
        )

    def __str__(self) -> str:
        return f"<ProtoEnumValueValueChanged enum={self.enum} enum_value={self.enum_value} new_value={self.new_value}>"
