from enum import Enum
from typing import Optional


class ParsedProtoNode:
    def __init__(self, parsed_node: "ProtoNode", remaining_source: str):
        self.node = parsed_node
        self.remaining_source = remaining_source

    def __eq__(self, other) -> bool:
        return (self.node == other.node) and (
            self.remaining_source == other.remaining_source
        )

    def __str__(self) -> str:
        return f"<ParsedProtoNode node={self.node} remaining_source={self.remaining_source} >"

    def __repr__(self) -> str:
        return str(self)


class ProtoNode:
    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        raise NotImplementedError


class ProtoSyntaxTypes(Enum):
    PROTO2 = "proto2"
    PROTO3 = "proto3"


class ProtoSyntax(ProtoNode):
    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("syntax = "):
            return None
        parts = proto_source.split(";")
        syntax_line = parts[0]
        proto_source = ";".join(parts[1:])
        return ParsedProtoNode(
            ProtoSyntaxTypes[syntax_line.split("syntax = ")[1][1:-1].upper()],
            proto_source.strip(),
        )


class ProtoImport(ProtoNode):
    def __init__(self, path: str, weak: bool = False, public: bool = False):
        self.path = path
        self.weak = weak
        self.public = public

    def __eq__(self, other) -> bool:
        return (
            self.path == other.path
            and self.weak == other.weak
            and self.public == other.public
        )

    def __str__(self) -> str:
        return f"<ProtoImport path='{self.path} weak={self.weak} public={self.public}'>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("import "):
            return None
        proto_source = proto_source[7:]
        parts = proto_source.split(";")
        import_line = parts[0]
        if len(parts) == 1:
            raise ValueError(f"Proto has invalid import syntax: {';'.join(parts)}")
        proto_source = ";".join(parts[1:])

        weak = False
        if import_line.startswith("weak "):
            weak = True
            import_line = import_line[5:]

        public = False
        if import_line.startswith("public "):
            if weak:
                raise ValueError(f"Proto has invalid import syntax: {';'.join(parts)}")
            public = True
            import_line = import_line[7:]

        if import_line[0] not in ('"', "'"):
            raise ValueError(f"Proto has invalid import syntax: {import_line}")
        import_path = import_line[1:-1]

        return ParsedProtoNode(
            ProtoImport(import_path, weak=weak, public=public), proto_source.strip()
        )


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
        # imports: Optional[list[ProtoImport]] = None, options: Optional[list[ProtoOption]] = None, top_level_definitions: Optional[list[ProtoEnum | ProtoMessage | ProtoService]] = None

    @property
    def imports(self) -> list[ProtoImport]:
        return [node for node in self.nodes if isinstance(node, ProtoImport)]
