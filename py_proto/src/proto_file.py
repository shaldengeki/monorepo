from src.proto_node import ProtoNode
from src.proto_syntax import ProtoSyntax
from src.proto_import import ProtoImport
from src.proto_package import ProtoPackage


class ProtoOption(ProtoNode):
    def __init__(self):
        pass


class ProtoEnum(ProtoNode):
    def __init__(self):
        pass


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
