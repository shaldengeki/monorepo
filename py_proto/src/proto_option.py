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
    def __init__(self, name: ProtoIdentifier, value: ProtoConstant, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self
        self.value = value
        self.value.parent = self

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
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoOptionNode"]:
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
                    ProtoIdentifier(identifier=f"({identifier_match.node.identifier})")
                )
                proto_source = identifier_match.remaining_source[1:]
            else:
                name_parts.append(
                    ProtoFullIdentifier(identifier=f"({match.node.identifier})")
                )
                proto_source = match.remaining_source[1:]

        while True:
            identifier_match = ProtoEnumOrMessageIdentifier.match(
                proto_source=proto_source
            )
            if identifier_match is None:
                identifier_match = ProtoIdentifier.match(proto_source=proto_source)
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
            identifier = ProtoFullIdentifier(
                identifier="".join(x.identifier for x in name_parts)
            )
        else:
            identifier = ProtoIdentifier(identifier=name_parts[0].identifier)

        proto_option = ProtoOption(
            name=identifier,
            value=constant_match.node,
            parent=parent,
        )
        identifier.parent = proto_option
        constant_match.node.parent = proto_option

        return ParsedProtoOptionNode(
            proto_option,
            proto_source[1:],
        )

    def serialize(self) -> str:
        return f"option {self.name.serialize()} = {self.value.serialize()};"

    @staticmethod
    def diff(
        parent: ProtoNode,
        before: "ProtoOption",
        after: "ProtoOption",
    ) -> Sequence["ProtoOptionDiff"]:
        if before is None and after is not None:
            return [ProtoOptionAdded(parent, after)]
        elif before is not None and after is None:
            return [ProtoOptionRemoved(parent, before)]
        elif before is None and after is None:
            return []
        elif before.name != after.name:
            return []
        elif before == after:
            return []
        return [ProtoOptionValueChanged(parent, before.name, before.value, after.value)]

    @staticmethod
    def diff_sets(
        parent: ProtoNode,
        before: Sequence["ProtoOption"],
        after: Sequence["ProtoOption"],
    ) -> list["ProtoOptionDiff"]:
        diffs: list[ProtoOptionDiff] = []
        before_names = set(o.name.identifier for o in before)
        after_names = set(o.name.identifier for o in after)
        for name in before_names - after_names:
            diffs.append(
                ProtoOptionRemoved(
                    parent, next(i for i in before if i.name.identifier == name)
                )
            )
        for name in after_names - before_names:
            diffs.append(
                ProtoOptionAdded(
                    parent, next(i for i in after if i.name.identifier == name)
                )
            )
        for name in before_names & after_names:
            before_option = next(i for i in before if i.name.identifier == name)
            after_option = next(i for i in after if i.name.identifier == name)
            diffs.extend(ProtoOption.diff(parent, before_option, after_option))

        return diffs


class ProtoOptionDiff(ProtoNodeDiff):
    pass


class ProtoOptionValueChanged(ProtoOptionDiff):
    def __init__(
        self,
        parent: ProtoNode,
        name: ProtoIdentifier,
        before: ProtoConstant,
        after: ProtoConstant,
    ):
        self.name = name
        self.before = before
        self.after = after
        self.parent = parent

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoOptionValueChanged)
            and self.name == other.name
            and self.before == other.before
            and self.after == other.after
            and self.parent == other.parent
        )

    def __str__(self) -> str:
        return f"<ProtoOptionValueChanged name={self.name} before={self.before} after={self.after} parent={self.parent}>"


class ProtoOptionAdded(ProtoOptionDiff):
    def __init__(self, parent: ProtoNode, before: ProtoOption):
        self.parent = parent
        self.before = before

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoOptionAdded)
            and self.before == other.before
            and self.parent == other.parent
        )

    def __str__(self) -> str:
        return f"<ProtoOptionAdded before={self.before} parent={self.parent}>"


class ProtoOptionRemoved(ProtoOptionDiff):
    def __init__(self, parent: ProtoNode, after: ProtoOption):
        self.parent = parent
        self.after = after

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoOptionRemoved)
            and self.after == other.after
            and self.parent == other.parent
        )

    def __str__(self) -> str:
        return f"<ProtoOptionRemoved after={self.after} parent={self.parent}>"
