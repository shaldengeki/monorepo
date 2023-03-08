from typing import Optional, Sequence

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_enum import ProtoEnum
from src.proto_extend import ProtoExtend
from src.proto_import import ProtoImport
from src.proto_message import ProtoMessage
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff
from src.proto_option import ProtoOption
from src.proto_package import ProtoPackage
from src.proto_service import ProtoService
from src.proto_syntax import ProtoSyntax


class ParsedProtoFileNode(ParsedProtoNode):
    node: "ProtoFile"
    remaining_source: str


class ProtoFile(ProtoNode):
    def __init__(self, syntax: ProtoSyntax, nodes: list[ProtoNode], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.syntax = syntax
        self.nodes = nodes

        if len([node for node in nodes if isinstance(node, ProtoPackage)]) > 1:
            raise ValueError(f"Proto can't have more than one package statement")

    @property
    def imports(self) -> list[ProtoImport]:
        return [node for node in self.nodes if isinstance(node, ProtoImport)]

    @property
    def package(self) -> Optional[ProtoPackage]:
        try:
            return next(node for node in self.nodes if isinstance(node, ProtoPackage))
        except StopIteration:
            return None

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    @property
    def enums(self) -> list[ProtoEnum]:
        return [node for node in self.nodes if isinstance(node, ProtoEnum)]

    @property
    def messages(self) -> list[ProtoMessage]:
        return [node for node in self.nodes if isinstance(node, ProtoMessage)]

    @staticmethod
    def parse_partial_content(partial_proto_content: str) -> ParsedProtoNode:
        node_types: list[type[ProtoNode]] = [
            ProtoImport,
            ProtoMessage,
            ProtoPackage,
            ProtoOption,
            ProtoEnum,
            ProtoExtend,
            ProtoService,
            ProtoSingleLineComment,
            ProtoMultiLineComment,
        ]
        for node_type in node_types:
            try:
                match_result = node_type.match(partial_proto_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse proto content:\n{partial_proto_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(f"Could not parse proto content:\n{partial_proto_content}")

    @staticmethod
    def parse_syntax_and_preceding_comments(
        proto_content: str,
    ) -> tuple[ProtoSyntax, Sequence[ProtoComment], str]:
        # First, parse any preceding comments.
        parsed_tree = []
        while True:
            for node_type in [ProtoSingleLineComment, ProtoMultiLineComment]:
                try:
                    match_result = node_type.match(proto_content)
                except (ValueError, IndexError, TypeError):
                    raise ValueError(f"Could not parse proto content:\n{proto_content}")
                if match_result is not None:
                    parsed_tree.append(match_result.node)
                    proto_content = match_result.remaining_source.strip()
                    break
            if match_result is None:
                break

        # Next, parse syntax.
        try:
            syntax_match = ProtoSyntax.match(proto_content.strip())
        except (ValueError, IndexError, TypeError):
            raise ValueError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        if syntax_match is None:
            raise ValueError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        syntax = syntax_match.node
        proto_content = syntax_match.remaining_source.strip()

        return syntax, parsed_tree, proto_content

    @classmethod
    def match(
        cls, proto_content: str, parent: Optional["ProtoNode"] = None
    ) -> Optional[ParsedProtoFileNode]:
        syntax, parsed_tree, proto_content = cls.parse_syntax_and_preceding_comments(
            proto_content
        )
        new_tree: list[ProtoNode] = list(parsed_tree)
        while proto_content:
            # Remove empty statements.
            if proto_content.startswith(";"):
                proto_content = proto_content[1:].strip()
                continue
            match_result = cls.parse_partial_content(proto_content)
            new_tree.append(match_result.node)
            proto_content = match_result.remaining_source.strip()

        return ParsedProtoFileNode(cls(syntax, new_tree), proto_content)

    def normalize(self) -> Optional["ProtoNode"]:
        normalized_nodes = [n.normalize() for n in self.nodes]
        return ProtoFile(
            syntax=self.syntax.normalize(),
            nodes=[n for n in normalized_nodes if n is not None],
        )

    def serialize(self) -> str:
        serialized_parts = [self.syntax.serialize()]
        previous_type: type[ProtoNode] = self.syntax.__class__
        for node in self.nodes:
            # Attempt to group up lines of the same type.
            if node.__class__ != previous_type:
                previous_type = node.__class__
                serialized_parts.append("")
            serialized_parts.append(node.serialize())

        return "\n".join(serialized_parts)

    def diff(self, other: "ProtoFile") -> Sequence[ProtoNodeDiff]:
        diffs: list[ProtoNodeDiff] = []
        diffs.extend(ProtoSyntax.diff(self.syntax, other.syntax))
        diffs.extend(ProtoImport.diff_sets(self.imports, other.imports))
        diffs.extend(ProtoPackage.diff(self.package, other.package))
        diffs.extend(ProtoEnum.diff_sets(self.enums, other.enums))
        diffs.extend(ProtoMessage.diff_sets(self.messages, other.messages))

        return [d for d in diffs if d is not None]
