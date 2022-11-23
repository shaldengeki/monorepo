from src.proto_import import ProtoImport
from src.proto_node import ProtoNode
from src.proto_option import ProtoOption
from src.proto_package import ProtoPackage
from src.proto_syntax import ProtoSyntax


class ProtoMessage(ProtoNode):
    def __init__(self):
        pass


class ProtoService(ProtoNode):
    def __init__(self):
        pass


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
    def package(self) -> ProtoPackage:
        return next(node for node in self.nodes if isinstance(node, ProtoPackage))

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

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
