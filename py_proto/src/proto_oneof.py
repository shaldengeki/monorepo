from typing import Optional, Sequence

from src.proto_comment import (
    ParsedProtoMultiLineCommentNode,
    ParsedProtoSingleLineCommentNode,
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import ProtoIdentifier
from src.proto_map import ProtoMap
from src.proto_message_field import ParsedProtoMessageFieldNode, ProtoMessageField
from src.proto_node import ParsedProtoNode, ProtoNode
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


class ProtoOneOf(ProtoNode):
    def __init__(
        self,
        parent: Optional[ProtoNode],
        name: ProtoIdentifier,
        nodes: Sequence[ProtoOneOfNodeTypes],
    ):
        super().__init__(parent)
        self.name = name
        self.name.parent = self
        self.nodes = nodes
        for node in self.nodes:
            node.parent = self

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoOneOf":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )
        options = []
        fields = []
        for node in non_comment_nodes:
            if isinstance(node, ProtoOption):
                options.append(node.normalize())
            elif (
                isinstance(node, ProtoMessageField)
                or isinstance(node, ProtoOneOf)
                or isinstance(node, ProtoMap)
            ):
                fields.append(node.normalize())
            else:
                raise ValueError(
                    f"Can't sort message {self} node for normalizing: {node}"
                )

        sorted_nodes_for_normalizing = sorted(
            options, key=lambda o: str(o.normalize())
        ) + sorted(fields, key=lambda f: int(f.number))

        return ProtoOneOf(
            parent=self.parent,
            name=self.name,
            nodes=sorted_nodes_for_normalizing,
        )

    @staticmethod
    def parse_partial_content(partial_oneof_content: str) -> ProtoParsedOneOfNodeTypes:
        supported_types: list[type[ProtoOneOfNodeTypes]] = [
            ProtoMessageField,
            ProtoOption,
            ProtoSingleLineComment,
            ProtoMultiLineComment,
        ]
        for node_type in supported_types:
            try:
                match_result = node_type.match(None, partial_oneof_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial oneof content:\n{partial_oneof_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(
            f"Could not parse partial oneof content:\n{partial_oneof_content}"
        )

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoOneOfNode"]:
        if not proto_source.startswith("oneof "):
            return None

        proto_source = proto_source[6:].strip()

        match = ProtoIdentifier.match(None, proto_source)
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

            match_result = ProtoOneOf.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoOneOfNode(
            ProtoOneOf(parent, oneof_name, nodes=parsed_tree), proto_source
        )

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    def serialize(self) -> str:
        serialize_parts = (
            [f"oneof {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)
