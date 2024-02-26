from typing import Optional, Sequence

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import ParsedProtoIdentifierNode, ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoContainerNode, ProtoNode, ProtoNodeDiff
from src.proto_option import ParsedProtoOptionNode, ProtoOption
from src.proto_reserved import ProtoReserved


class ParsedProtoEnumValueOptionNode(ParsedProtoOptionNode):
    node: "ProtoEnumValueOption"
    remaining_source: str


class ProtoEnumValueOption(ProtoOption):
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, value={self.value}>"

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoEnumValueOptionNode"]:
        test_source = "option " + proto_source.strip() + ";"
        match = ProtoOption.match(proto_source=test_source)
        if match is None:
            return None
        return ParsedProtoEnumValueOptionNode(
            cls(name=match.node.name, value=match.node.value, parent=parent),
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
        identifier: ProtoIdentifier,
        value: ProtoInt,
        options: Optional[list[ProtoEnumValueOption]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
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
            self.identifier,
            self.value,
            sorted(self.options, key=lambda o: str(o.name)),
            parent=self.parent,
        )

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoEnumValueNode"]:
        match = ProtoIdentifier.match(proto_source=proto_source)
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
            int_match = ProtoInt.match(proto_source=proto_source[1:])
        else:
            int_match = ProtoInt.match(proto_source=proto_source)
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
                    proto_source=option_part.strip(), parent=None
                )
                if proto_enum_value_option_match is None:
                    raise ValueError(
                        f"Proto has invalid enum value option syntax: {proto_source}"
                    )
                options.append(proto_enum_value_option_match.node)
            proto_source = proto_source[end_bracket + 1 :].strip()

        return ParsedProtoEnumValueNode(
            ProtoEnumValue(
                identifier=enum_value_name,
                value=enum_value,
                options=options,
                parent=parent,
            ),
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
        enum: "ProtoEnum",
        before: Optional["ProtoEnumValue"],
        after: Optional["ProtoEnumValue"],
    ) -> Sequence["ProtoNodeDiff"]:
        diffs: list["ProtoNodeDiff"] = []
        # TODO: scope these diffs under ProtoEnumValue
        if before is None or after is None:
            if after is not None:
                diffs.append(ProtoEnumValueAdded(enum, after))
            elif before is not None:
                diffs.append(ProtoEnumValueRemoved(enum, before))
        else:
            if before.identifier != after.identifier:
                diffs.append(ProtoEnumValueNameChanged(enum, before, after.identifier))
            else:
                raise ValueError(
                    f"Don't know how to handle diff between enums whose names aren't identical: {before}, {after}"
                )

            diffs.extend(
                ProtoEnumValueOption.diff_sets(before, before.options, after.options)
            )
        return diffs

    @staticmethod
    def diff_sets(
        enum: "ProtoEnum", before: list["ProtoEnumValue"], after: list["ProtoEnumValue"]
    ) -> list["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []

        before_number_to_enum_values = {int(mf.value): mf for mf in before}
        after_number_to_enum_values = {int(mf.value): mf for mf in after}
        all_numbers = sorted(
            set(before_number_to_enum_values.keys()).union(
                set(after_number_to_enum_values.keys())
            )
        )
        for number in all_numbers:
            diffs.extend(
                ProtoEnumValue.diff(
                    enum,
                    before_number_to_enum_values.get(number, None),
                    after_number_to_enum_values.get(number, None),
                )
            )

        return diffs


class ProtoEnum(ProtoContainerNode):
    def __init__(self, name: ProtoIdentifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoEnum)
            and super().__eq__(other)
            and self.name == other.name
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
            name=self.name,
            nodes=sorted(non_comment_nodes, key=lambda n: str(n.normalize())),
            parent=self.parent,
        )

    @classmethod
    def container_types(cls) -> list[type[ProtoNode]]:
        return [
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoOption,
            ProtoReserved,
            ProtoEnumValue,
        ]

    @classmethod
    def match_header(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoIdentifierNode"]:
        if not proto_source.startswith("enum "):
            return None

        proto_source = proto_source[5:]
        match = ProtoIdentifier.match(proto_source=proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid enum name: {proto_source}")

        enum_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        return ParsedProtoIdentifierNode(enum_name, proto_source[1:].strip())

    @classmethod
    def construct(
        cls,
        header_match: ParsedProtoNode,
        contained_nodes: list[ProtoNode],
        footer_match: str,
        parent: Optional[ProtoNode] = None,
    ) -> ProtoNode:
        assert isinstance(header_match, ParsedProtoIdentifierNode)
        return ProtoEnum(name=header_match.node, nodes=contained_nodes, parent=parent)

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
    def diff(
        parent: ProtoNode, before: "ProtoEnum", after: "ProtoEnum"
    ) -> list["ProtoNodeDiff"]:
        if before is None and after is not None:
            return [ProtoEnumAdded(parent, after)]
        elif before is not None and after is None:
            return [ProtoEnumRemoved(parent, before)]
        elif before is None and after is None:
            return []
        elif before.name != after.name:
            return []
        elif before == after:
            return []
        diffs: list[ProtoNodeDiff] = []
        # TODO: scope these diffs under ProtoEnum
        diffs.extend(ProtoOption.diff_sets(parent, before.options, after.options))
        diffs.extend(ProtoEnumValue.diff_sets(before, before.values, after.values))
        return diffs

    @staticmethod
    def diff_sets(
        parent: ProtoNode, before: list["ProtoEnum"], after: list["ProtoEnum"]
    ) -> list["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
        before_names = set(o.name.identifier for o in before)
        after_names = set(o.name.identifier for o in after)
        for name in before_names - after_names:
            diffs.append(
                ProtoEnumRemoved(
                    parent, next(i for i in before if i.name.identifier == name)
                )
            )
        for name in after_names - before_names:
            diffs.append(
                ProtoEnumAdded(
                    parent, next(i for i in after if i.name.identifier == name)
                )
            )
        for name in before_names & after_names:
            before_enum = next(i for i in before if i.name.identifier == name)
            after_enum = next(i for i in after if i.name.identifier == name)
            diffs.extend(ProtoEnum.diff(parent, before_enum, after_enum))

        return diffs


class ProtoEnumDiff(ProtoNodeDiff):
    def __init__(self, parent: ProtoNode, enum: ProtoEnum):
        self.parent = parent
        self.enum = enum

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoEnumDiff)
            and self.parent == other.parent
            and self.enum == other.enum
        )

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} enum={self.enum} parent={self.parent}>"


class ProtoEnumAdded(ProtoEnumDiff):
    pass


class ProtoEnumRemoved(ProtoEnumDiff):
    pass


class ProtoEnumValueDiff(ProtoNodeDiff):
    def __init__(self, enum: "ProtoEnum", enum_value: "ProtoEnumValue"):
        self.enum = enum
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
