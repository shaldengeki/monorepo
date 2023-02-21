from typing import Optional, Sequence

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_enum import ProtoEnum
from src.proto_extend import ProtoExtend
from src.proto_extensions import ProtoExtensions
from src.proto_identifier import ProtoIdentifier
from src.proto_map import ProtoMap
from src.proto_message_field import ProtoMessageField
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff
from src.proto_oneof import ProtoOneOf
from src.proto_option import ProtoOption
from src.proto_reserved import ProtoReserved


class ProtoMessage(ProtoNode):
    def __init__(
        self,
        name: ProtoIdentifier,
        nodes: Sequence[ProtoNode],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self
        self.nodes = nodes
        for node in self.nodes:
            node.parent = self

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

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

    @staticmethod
    def parse_partial_content(partial_message_content: str) -> ParsedProtoNode:
        supported_types: list[type[ProtoNode]] = [
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
        for node_type in supported_types:
            try:
                match_result = node_type.match(partial_message_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial message content:\n{partial_message_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(
            f"Could not parse partial message content:\n{partial_message_content}"
        )

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoNode"]:
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

            match_result = ProtoMessage.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoNode(
            ProtoMessage(name=enum_name, nodes=parsed_tree, parent=parent), proto_source
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

    def serialize(self) -> str:
        serialize_parts = (
            [f"message {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)

    @staticmethod
    def diff(
        before: "ProtoMessage", after: "ProtoMessage"
    ) -> Sequence["ProtoNodeDiff"]:
        if before is None and after is not None:
            return [ProtoMessageAdded(after)]
        elif before is not None and after is None:
            return [ProtoMessageRemoved(before)]
        elif before is None and after is None:
            return []
        elif before.name != after.name:
            return []
        elif before == after:
            return []
        diffs: list[ProtoNodeDiff] = []
        diffs.extend(ProtoOption.diff_sets(before.options, after.options))
        # diffs.extend(ProtoOneOf.diff_sets(before, before.oneofs, after.oneofs))
        diffs.extend(ProtoMap.diff_sets(before, before.maps, after.maps))
        diffs.extend(
            ProtoMessageField.diff_sets(
                before, before.message_fields, after.message_fields
            )
        )
        return diffs

    @staticmethod
    def diff_sets(
        before: list["ProtoMessage"], after: list["ProtoMessage"]
    ) -> Sequence["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
        before_names = set(o.name.identifier for o in before)
        after_names = set(o.name.identifier for o in after)
        for name in before_names - after_names:
            diffs.append(
                ProtoMessageRemoved(
                    next(i for i in before if i.name.identifier == name)
                )
            )
        for name in after_names - before_names:
            diffs.append(
                ProtoMessageAdded(next(i for i in after if i.name.identifier == name))
            )
        for name in before_names & after_names:
            before_enum = next(i for i in before if i.name.identifier == name)
            after_enum = next(i for i in after if i.name.identifier == name)
            diffs.extend(ProtoMessage.diff(before_enum, after_enum))

        return diffs


class ProtoMessageDiff(ProtoNodeDiff):
    def __init__(self, message: ProtoMessage):
        self.message = message

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProtoMessageDiff) and self.message == other.message

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} message={self.message}>"


class ProtoMessageAdded(ProtoMessageDiff):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ProtoMessageAdded)


class ProtoMessageRemoved(ProtoMessageDiff):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ProtoMessageRemoved)
