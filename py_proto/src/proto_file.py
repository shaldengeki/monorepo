from typing import Optional

from src.proto_enum import ProtoEnum
from src.proto_import import ProtoImport
from src.proto_message import ProtoMessage
from src.proto_node import ProtoNode, ProtoNodeDiff
from src.proto_option import ProtoOption
from src.proto_package import ProtoPackage
from src.proto_syntax import ProtoSyntax


class ProtoFile:
    def __init__(self, syntax: ProtoSyntax, nodes: list[ProtoNode]):
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

    def serialize(self) -> str:
        serialized_parts = [self.syntax.serialize()]
        previous_type = self.syntax.__class__
        for node in self.nodes:
            # Attempt to group up lines of the same type.
            if node.__class__ != previous_type:
                previous_type = node.__class__
                serialized_parts.append("")
            serialized_parts.append(node.serialize())

        return "\n".join(serialized_parts)

    def diff(self, other: "ProtoFile") -> list[ProtoNodeDiff]:
        diffs = []
        diffs.extend(ProtoSyntax.diff(self.syntax, other.syntax))
        diffs.extend(ProtoImport.diff_sets(self.imports, other.imports))
        diffs.extend(ProtoPackage.diff(self.package, other.package))
        diffs.extend(ProtoEnum.diff_sets(self.enums, other.enums))
        diffs.extend(ProtoMessage.diff_sets(self.messages, other.messages))

        return [d for d in diffs if d is not None]
