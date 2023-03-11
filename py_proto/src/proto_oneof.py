from typing import Optional, Sequence

from src.proto_comment import (
    ParsedProtoMultiLineCommentNode,
    ParsedProtoSingleLineCommentNode,
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import ParsedProtoIdentifierNode, ProtoIdentifier
from src.proto_map import ProtoMap
from src.proto_message_field import ParsedProtoMessageFieldNode, ProtoMessageField
from src.proto_node import ParsedProtoNode, ProtoContainerNode, ProtoNode, ProtoNodeDiff
from src.proto_option import ParsedProtoOptionNode, ProtoOption

ProtoOneOfNodeTypes = (
    ProtoOption | ProtoMessageField | ProtoSingleLineComment | ProtoMultiLineComment
)
ProtoParsedOneOfNodeTypes = (
    ParsedProtoOptionNode
    | ParsedProtoMessageFieldNode
    | ParsedProtoSingleLineCommentNode
    | ParsedProtoMultiLineCommentNode
)


class ParsedProtoOneOfNode(ParsedProtoNode):
    node: "ProtoOneOf"
    remaining_source: str


class ProtoOneOf(ProtoContainerNode):
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
        return f"<{self.__class__.__name__} name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoOneOf":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )
        options = []
        fields: list[ProtoMessageField | ProtoMap] = []
        oneofs: list[ProtoOneOf] = []
        for node in non_comment_nodes:
            if isinstance(node, ProtoOption):
                options.append(node.normalize())
            elif isinstance(node, ProtoMessageField) or isinstance(node, ProtoMap):
                fields.append(node.normalize())
            elif isinstance(node, ProtoOneOf):
                oneofs.append(node.normalize())
            else:
                raise ValueError(
                    f"Can't sort message {self} node for normalizing: {node}"
                )

        sorted_options = sorted(options, key=lambda o: str(o.normalize()))
        sorted_fields = sorted(fields, key=lambda f: int(f.number))
        sorted_oneofs = sorted(
            oneofs,
            key=lambda x: min(int(f.number) for f in x.message_fields),
        )

        return ProtoOneOf(
            name=self.name,
            nodes=(sorted_options + sorted_fields + sorted_oneofs),
            parent=self.parent,
        )

    @classmethod
    def match_header(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoIdentifierNode"]:
        if not proto_source.startswith("oneof "):
            return None

        proto_source = proto_source[6:].strip()

        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(
                f"Proto has invalid syntax, expecting identifier for oneof: {proto_source}"
            )

        oneof_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        return ParsedProtoIdentifierNode(oneof_name, proto_source[1:].strip())

    @classmethod
    def container_types(cls) -> list[type[ProtoNode]]:
        return [
            ProtoMessageField,
            ProtoOption,
            ProtoSingleLineComment,
            ProtoMultiLineComment,
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
        return ProtoOneOf(name=header_match.node, nodes=contained_nodes, parent=parent)

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    @property
    def message_fields(self) -> list[ProtoMessageField]:
        return [node for node in self.nodes if isinstance(node, ProtoMessageField)]

    def serialize(self) -> str:
        serialize_parts = (
            [f"oneof {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)

    @staticmethod
    def diff(
        parent: ProtoNode, before: "ProtoOneOf", after: "ProtoOneOf"
    ) -> Sequence["ProtoNodeDiff"]:
        if before is None and after is not None:
            return [ProtoOneOfAdded(parent, after)]
        elif before is not None and after is None:
            return [ProtoOneOfRemoved(parent, before)]
        elif before is None and after is None:
            return []
        elif before.name != after.name:
            return []
        elif before == after:
            return []
        diffs: list[ProtoNodeDiff] = []
        diffs.extend(ProtoOption.diff_sets(before, before.options, after.options))
        diffs.extend(
            ProtoMessageField.diff_sets(
                before, before.message_fields, after.message_fields
            )
        )
        return diffs

    @staticmethod
    def diff_sets(
        parent: ProtoNode,
        before: list["ProtoOneOf"],
        after: list["ProtoOneOf"],
    ) -> Sequence["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
        before_names = set(o.name.identifier for o in before)
        after_names = set(o.name.identifier for o in after)
        for name in before_names - after_names:
            diffs.append(
                ProtoOneOfRemoved(
                    parent, next(i for i in before if i.name.identifier == name)
                )
            )
        for name in after_names - before_names:
            diffs.append(
                ProtoOneOfAdded(
                    parent, next(i for i in after if i.name.identifier == name)
                )
            )
        for name in before_names & after_names:
            before_oneof = next(i for i in before if i.name.identifier == name)
            after_oneof = next(i for i in after if i.name.identifier == name)
            diffs.extend(ProtoOneOf.diff(parent, before_oneof, after_oneof))

        return diffs


class ProtoOneOfDiff(ProtoNodeDiff):
    def __init__(self, parent: ProtoNode, oneof: ProtoOneOf):
        self.parent = parent
        self.oneof = oneof

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoOneOfDiff)
            and self.oneof == other.oneof
            and self.parent == other.parent
        )

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} oneof={self.oneof} parent={self.parent}>"


class ProtoOneOfAdded(ProtoOneOfDiff):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ProtoOneOfAdded)


class ProtoOneOfRemoved(ProtoOneOfDiff):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ProtoOneOfRemoved)
