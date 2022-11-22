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


class ProtoStringLiteral(ProtoNode):
    QUOTES = {'"', "'"}

    def __init__(self, val: str):
        self.val = val

    def __eq__(self, other) -> bool:
        return self.val == other.val

    def __str__(self) -> str:
        return f"<ProtoStringLiteral val='{self.val}'>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not any(proto_source.startswith(c) for c in ProtoStringLiteral.QUOTES):
            return None
        escaped = False
        starting_quote = proto_source[0]
        for i, c in enumerate(proto_source[1:]):
            if c == "\\":
                escaped = True
                continue
            if c == starting_quote and not escaped:
                return ParsedProtoNode(
                    ProtoStringLiteral(proto_source[1 : i + 1]),
                    proto_source[i + 2 :].strip(),
                )
            escaped = False
        return None


class ProtoSyntaxTypes(Enum):
    PROTO2 = "proto2"
    PROTO3 = "proto3"


class ProtoSyntax(ProtoNode):
    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("syntax = "):
            return None
        parts = proto_source.split(";")
        proto_source = ";".join(parts[1:])
        syntax_line = parts[0][9:]
        match = ProtoStringLiteral.match(syntax_line)
        if match is None:
            raise ValueError(f"Proto has invalid syntax syntax: {';'.join(parts)}")
        return ParsedProtoNode(
            ProtoSyntaxTypes[match.node.val.upper()],
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
        return f"<ProtoImport path='{self.path}' weak={self.weak} public={self.public}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("import "):
            return None
        proto_source = proto_source[7:]

        weak = False
        if proto_source.startswith("weak "):
            weak = True
            proto_source = proto_source[5:]

        public = False
        if proto_source.startswith("public "):
            if weak:
                raise ValueError(f"Proto has invalid import syntax: {proto_source}")
            public = True
            proto_source = proto_source[7:]

        match = ProtoStringLiteral.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid import syntax: {proto_source}")

        if not match.remaining_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid import syntax: {match.remaining_source}"
            )

        return ParsedProtoNode(
            ProtoImport(match.node.val, weak=weak, public=public),
            match.remaining_source[1:].strip(),
        )


class ProtoPackage(ProtoNode):
    def __init__(self, package: str):
        self.package = package

    def __eq__(self, other) -> bool:
        return self.package == other.package

    def __str__(self) -> str:
        return f"<ProtoPackage package={self.package}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("package "):
            return None
        proto_source = proto_source[8:]
        parts = proto_source.split(";")
        package = parts[0]
        if len(parts) == 1:
            raise ValueError(
                f"Proto has invalid package declaration syntax: {';'.join(parts)}"
            )
        proto_source = ";".join(parts[1:])

        if package.startswith(".") or package.endswith("."):
            raise ValueError(f"Proto has invalid package: {package}")

        return ParsedProtoNode(ProtoPackage(package), proto_source.strip())


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
