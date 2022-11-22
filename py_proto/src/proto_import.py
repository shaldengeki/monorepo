from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_string_literal import ProtoStringLiteral


class ProtoImport(ProtoNode):
    def __init__(
        self, path: ProtoStringLiteral, weak: bool = False, public: bool = False
    ):
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
        return f"<ProtoImport path={self.path.serialize()} weak={self.weak} public={self.public}>"

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
            ProtoImport(match.node, weak=weak, public=public),
            match.remaining_source[1:].strip(),
        )

    def serialize(self) -> str:
        parts = ["import"]
        if self.weak:
            parts.append("weak")
        elif self.public:
            parts.append("public")
        parts.append(f"{self.path.serialize()};")
        return " ".join(parts)
