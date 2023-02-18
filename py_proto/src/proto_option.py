from typing import Optional, Sequence

from src.proto_constant import ProtoConstant
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff


class ParsedProtoOptionNode(ParsedProtoNode):
    node: "ProtoOption"
    remaining_source: str


class ProtoOption(ProtoNode):
    def __init__(self, name: ProtoIdentifier, value: ProtoConstant):
        self.name = name
        self.value = value

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.value == other.value

    def __str__(self) -> str:
        return f"<ProtoOption name={self.name} value={self.value}>"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def normalize(self) -> "ProtoOption":
        return self

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoOptionNode"]:
        if not proto_source.startswith("option "):
            return None
        proto_source = proto_source[7:]

        name_parts = []
        if proto_source.startswith("("):
            proto_source = proto_source[1:]
            match = ProtoFullIdentifier.match(proto_source)
            if match is None or not match.remaining_source.startswith(")"):
                # This might be a regular identifier.
                identifier_match = ProtoIdentifier.match(proto_source)
                if (
                    not identifier_match
                    or not identifier_match.remaining_source.startswith(")")
                ):
                    raise ValueError(
                        f"Proto has invalid option when expecting ): {proto_source}"
                    )
                name_parts.append(
                    ProtoIdentifier(f"({identifier_match.node.identifier})")
                )
                proto_source = identifier_match.remaining_source[1:]
            else:
                name_parts.append(ProtoFullIdentifier(f"({match.node.identifier})"))
                proto_source = match.remaining_source[1:]

        while True:
            identifier_match = ProtoEnumOrMessageIdentifier.match(proto_source)
            if identifier_match is None:
                identifier_match = ProtoIdentifier.match(proto_source)
                if identifier_match is None:
                    break
            name_parts.append(identifier_match.node)
            proto_source = identifier_match.remaining_source

        proto_source = proto_source.strip()
        if not proto_source.startswith("="):
            raise ValueError(
                f"Proto has invalid option when expecting =: {proto_source}"
            )
        proto_source = proto_source[1:].strip()
        constant_match = ProtoConstant.match(proto_source)
        if constant_match is None:
            raise ValueError(
                f"Proto has invalid option when expecting constant: {proto_source}"
            )

        proto_source = constant_match.remaining_source
        if not constant_match.remaining_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid option when expecting ;: {proto_source}"
            )

        identifier: ProtoFullIdentifier | ProtoIdentifier
        if len(name_parts) > 1:
            identifier = ProtoFullIdentifier("".join(x.identifier for x in name_parts))
        else:
            identifier = ProtoIdentifier(name_parts[0].identifier)

        return ParsedProtoOptionNode(
            ProtoOption(
                name=identifier,
                value=constant_match.node,
            ),
            proto_source[1:],
        )

    def serialize(self) -> str:
        return f"option {self.name.serialize()} = {self.value.serialize()};"

    @staticmethod
    def diff(left: "ProtoOption", right: "ProtoOption") -> Sequence["ProtoOptionDiff"]:
        if left is None and right is not None:
            return [ProtoOptionAdded(right)]
        elif left is not None and right is None:
            return [ProtoOptionRemoved(left)]
        elif left is None and right is None:
            return []
        elif left.name != right.name:
            return []
        elif left == right:
            return []
        return [ProtoOptionValueChanged(left.name, left.value, right.value)]

    @staticmethod
    def diff_sets(
        left: Sequence["ProtoOption"], right: Sequence["ProtoOption"]
    ) -> list["ProtoOptionDiff"]:
        diffs: list[ProtoOptionDiff] = []
        left_names = set(o.name.identifier for o in left)
        right_names = set(o.name.identifier for o in right)
        for name in left_names - right_names:
            diffs.append(
                ProtoOptionAdded(next(i for i in left if i.name.identifier == name))
            )
        for name in right_names - left_names:
            diffs.append(
                ProtoOptionRemoved(next(i for i in right if i.name.identifier == name))
            )
        for name in left_names & right_names:
            left_option = next(i for i in left if i.name.identifier == name)
            right_option = next(i for i in right if i.name.identifier == name)
            diffs.extend(ProtoOption.diff(left_option, right_option))

        return diffs


class ProtoOptionDiff(ProtoNodeDiff):
    pass


class ProtoOptionValueChanged(ProtoOptionDiff):
    def __init__(
        self, name: ProtoIdentifier, left: ProtoConstant, right: ProtoConstant
    ):
        self.name = name
        self.left = left
        self.right = right

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoOptionValueChanged)
            and self.name == other.name
            and self.left == other.left
            and self.right == other.right
        )

    def __str__(self) -> str:
        return f"<ProtoOptionValueChanged name={self.name} left={self.left} right={self.right}>"


class ProtoOptionAdded(ProtoOptionDiff):
    def __init__(self, left: ProtoOption):
        self.left = left

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProtoOptionAdded) and self.left == other.left

    def __str__(self) -> str:
        return f"<ProtoOptionAdded left={self.left}>"


class ProtoOptionRemoved(ProtoOptionDiff):
    def __init__(self, right: ProtoOption):
        self.right = right

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProtoOptionRemoved) and self.right == other.right

    def __str__(self) -> str:
        return f"<ProtoOptionRemoved right={self.right}>"
