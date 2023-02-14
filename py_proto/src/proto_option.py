from typing import Optional

from src.proto_constant import ProtoConstant
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff


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
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("option "):
            return None
        proto_source = proto_source[7:]

        name_parts = []
        if proto_source.startswith("("):
            proto_source = proto_source[1:]
            match = ProtoFullIdentifier.match(proto_source)
            if not match or not match.remaining_source.startswith(")"):
                # This might be a regular identifier.
                match = ProtoIdentifier.match(proto_source)
                if not match or not match.remaining_source.startswith(")"):
                    raise ValueError(
                        f"Proto has invalid option when expecting ): {proto_source}"
                    )
                name_parts.append(ProtoIdentifier(f"({match.node.identifier})"))
            else:
                name_parts.append(ProtoFullIdentifier(f"({match.node.identifier})"))

            proto_source = match.remaining_source[1:]

        while True:
            match = ProtoEnumOrMessageIdentifier.match(proto_source)
            if match is None:
                match = ProtoIdentifier.match(proto_source)
                if match is None:
                    break
            name_parts.append(match.node)
            proto_source = match.remaining_source

        proto_source = proto_source.strip()
        if not proto_source.startswith("="):
            raise ValueError(
                f"Proto has invalid option when expecting =: {proto_source}"
            )
        proto_source = proto_source[1:].strip()
        match = ProtoConstant.match(proto_source)
        if not match:
            raise ValueError(
                f"Proto has invalid option when expecting constant: {proto_source}"
            )

        proto_source = match.remaining_source
        if not match.remaining_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid option when expecting ;: {proto_source}"
            )

        if len(name_parts) > 1:
            identifier = ProtoFullIdentifier("".join(x.identifier for x in name_parts))
        else:
            identifier = ProtoIdentifier(name_parts[0].identifier)

        return ParsedProtoNode(
            ProtoOption(
                name=identifier,
                value=match.node,
            ),
            proto_source[1:],
        )

    def serialize(self) -> str:
        return f"option {self.name.serialize()} = {self.value.serialize()};"

    @staticmethod
    def diff(left: "ProtoOption", right: "ProtoOption") -> list["ProtoNodeDiff"]:
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
        left: list["ProtoOption"], right: list["ProtoOption"]
    ) -> list["ProtoNodeDiff"]:
        diffs = []
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


class ProtoOptionValueChanged(ProtoNodeDiff):
    def __init__(self, name: ProtoIdentifier, left: str, right: str):
        self.name = name
        self.left = left
        self.right = right

    def __eq__(self, other: "ProtoOptionValueChanged") -> bool:
        return (
            isinstance(other, ProtoOptionValueChanged)
            and self.name == other.name
            and self.left == other.left
            and self.right == other.right
        )

    def __str__(self) -> str:
        return f"<ProtoOptionValueChanged name={self.name} left={self.left} right={self.right}>"


class ProtoOptionAdded(ProtoNodeDiff):
    def __init__(self, left: str):
        self.left = left

    def __eq__(self, other: "ProtoOptionAdded") -> bool:
        return isinstance(other, ProtoOptionAdded) and self.left == other.left

    def __str__(self) -> str:
        return f"<ProtoOptionAdded left={self.left}>"


class ProtoOptionRemoved(ProtoNodeDiff):
    def __init__(self, right: str):
        self.right = right

    def __eq__(self, other: "ProtoOptionRemoved") -> bool:
        return isinstance(other, ProtoOptionRemoved) and self.right == other.right

    def __str__(self) -> str:
        return f"<ProtoOptionRemoved right={self.right}>"
