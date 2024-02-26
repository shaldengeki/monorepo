from typing import Optional, Sequence

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_enum import ProtoEnum
from src.proto_extend import ProtoExtend
from src.proto_extensions import ProtoExtensions
from src.proto_identifier import ParsedProtoIdentifierNode, ProtoIdentifier
from src.proto_map import ProtoMap
from src.proto_message_field import ProtoMessageField
from src.proto_node import ParsedProtoNode, ProtoContainerNode, ProtoNode, ProtoNodeDiff
from src.proto_oneof import ProtoOneOf
from src.proto_option import ProtoOption
from src.proto_reserved import ProtoReserved


class ProtoMessage(ProtoContainerNode):
    def __init__(
        self,
        name: ProtoIdentifier,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.name == other.name

    def __str__(self) -> str:
        return f"<ProtoMessage name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoMessage":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )

        options = []
        enums = []
        messages = []
        fields = []
        oneofs = []
        reserveds = []
        for node in non_comment_nodes:
            if isinstance(node, ProtoOption):
                options.append(node.normalize())
            elif isinstance(node, ProtoEnum):
                enums.append(node.normalize())
            elif isinstance(node, ProtoMessage):
                messages.append(node.normalize())
            elif isinstance(node, ProtoMessageField) or isinstance(node, ProtoMap):
                fields.append(node.normalize())
            elif isinstance(node, ProtoOneOf):
                oneofs.append(node.normalize())
            elif isinstance(node, ProtoReserved):
                reserveds.append(node.normalize())
            else:
                raise ValueError(
                    f"Can't sort message {self} node for normalizing: {node}"
                )

        sorted_nodes_for_normalizing = (
            sorted(options, key=lambda o: str(o.normalize()))
            + sorted(enums, key=lambda e: str(e))
            + sorted(messages, key=lambda m: str(m))
            + sorted(fields, key=lambda f: int(f.number))
            + sorted(oneofs, key=lambda o: str(o))
            + sorted(reserveds, key=lambda r: int(r.min))
        )

        return ProtoMessage(
            name=self.name,
            nodes=sorted_nodes_for_normalizing,
            parent=self.parent,
        )

    @classmethod
    def match_header(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoIdentifierNode"]:
        if not proto_source.startswith("message "):
            return None

        proto_source = proto_source[8:]
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid message name: {proto_source}")

        enum_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto message has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        return ParsedProtoIdentifierNode(enum_name, proto_source[1:].strip())

    @classmethod
    def container_types(cls) -> list[type[ProtoNode]]:
        return [
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoEnum,
            ProtoExtend,
            ProtoExtensions,
            ProtoOption,
            ProtoMessage,
            ProtoReserved,
            ProtoMessageField,
            ProtoOneOf,
            ProtoMap,
        ]

    @classmethod
    def construct(
        cls,
        header_match: ParsedProtoNode,
        contained_nodes: list[ProtoNode],
        footer_match: str,
        parent: Optional[ProtoNode] = None,
    ) -> ProtoNode:
        assert isinstance(header_match, ParsedProtoIdentifierNode)
        return ProtoMessage(
            name=header_match.node, nodes=contained_nodes, parent=parent
        )

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    @property
    def maps(self) -> list[ProtoMap]:
        return [node for node in self.nodes if isinstance(node, ProtoMap)]

    @property
    def message_fields(self) -> list[ProtoMessageField]:
        return [node for node in self.nodes if isinstance(node, ProtoMessageField)]

    @property
    def oneofs(self) -> list[ProtoOneOf]:
        return [node for node in self.nodes if isinstance(node, ProtoOneOf)]

    def serialize(self) -> str:
        serialize_parts = (
            [f"message {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)

    @staticmethod
    def diff(
        parent: ProtoNode,
        before: "ProtoMessage",
        after: "ProtoMessage",
    ) -> Sequence["ProtoNodeDiff"]:
        if before is None and after is not None:
            return [ProtoMessageAdded(parent, after)]
        elif before is not None and after is None:
            return [ProtoMessageRemoved(parent, before)]
        elif before is None and after is None:
            return []
        elif before.name != after.name:
            return []
        elif before == after:
            return []
        diffs: list[ProtoNodeDiff] = []

        # TODO:
        # ProtoEnum,
        # ProtoExtend,
        # ProtoExtensions,
        # ProtoMessage,
        # ProtoReserved,
        diffs.extend(ProtoOption.diff_sets(before, before.options, after.options))
        diffs.extend(ProtoOneOf.diff_sets(before, before.oneofs, after.oneofs))
        diffs.extend(ProtoMap.diff_sets(before, before.maps, after.maps))
        diffs.extend(
            ProtoMessageField.diff_sets(
                before, before.message_fields, after.message_fields
            )
        )
        return diffs

    @staticmethod
    def diff_sets(
        parent: ProtoNode,
        before: list["ProtoMessage"],
        after: list["ProtoMessage"],
    ) -> Sequence["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
        before_names = set(o.name.identifier for o in before)
        after_names = set(o.name.identifier for o in after)
        for name in before_names - after_names:
            diffs.append(
                ProtoMessageRemoved(
                    parent,
                    next(i for i in before if i.name.identifier == name),
                )
            )
        for name in after_names - before_names:
            diffs.append(
                ProtoMessageAdded(
                    parent, next(i for i in after if i.name.identifier == name)
                )
            )
        for name in before_names & after_names:
            before_message = next(i for i in before if i.name.identifier == name)
            after_message = next(i for i in after if i.name.identifier == name)
            diffs.extend(ProtoMessage.diff(parent, before_message, after_message))

        return diffs


class ProtoMessageDiff(ProtoNodeDiff):
    def __init__(self, parent: ProtoNode, message: ProtoMessage):
        self.parent = parent
        self.message = message

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoMessageDiff)
            and self.message == other.message
            and self.parent == other.parent
        )

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} message={self.message} parent={self.parent}>"
        )


class ProtoMessageAdded(ProtoMessageDiff):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ProtoMessageAdded)


class ProtoMessageRemoved(ProtoMessageDiff):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ProtoMessageRemoved)
