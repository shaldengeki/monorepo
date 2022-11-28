from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoPackage(ProtoNode):
    def __init__(self, package: str):
        self.package = package

    def __eq__(self, other: "ProtoPackage") -> bool:
        if not isinstance(other, ProtoPackage):
            return False

        return self.package == other.package

    def __str__(self) -> str:
        return f"<ProtoPackage package={self.package}>"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("package"):
            return None

        if not proto_source.startswith("package "):
            raise ValueError(f"Proto has invalid package: {proto_source}")

        proto_source = proto_source[8:]
        parts = proto_source.split(";")
        package = parts[0]

        if len(parts) == 1:
            raise ValueError(
                f"Proto has invalid package declaration syntax: {';'.join(parts)}"
            )

        if not package:
            raise ValueError(f"Proto cannot have empty package: {proto_source}")

        proto_source = ";".join(parts[1:])

        if package.startswith(".") or package.endswith("."):
            raise ValueError(f"Proto has invalid package: {package}")

        return ParsedProtoNode(ProtoPackage(package), proto_source.strip())

    def serialize(self) -> str:
        return f"package {self.package};"
