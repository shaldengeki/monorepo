from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff


class ProtoPackage(ProtoNode):
    def __init__(self, package: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.package = package

    def __eq__(self, other) -> bool:
        return hasattr(other, "package") and self.package == other.package

    def __str__(self) -> str:
        return f"<ProtoPackage package={self.package}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoPackage":
        return self

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoNode"]:
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

        return ParsedProtoNode(
            ProtoPackage(package=package, parent=parent), proto_source.strip()
        )

    def serialize(self) -> str:
        return f"package {self.package};"

    @staticmethod
    def diff(
        before: Optional["ProtoPackage"], after: Optional["ProtoPackage"]
    ) -> list["ProtoNodeDiff"]:
        if before == after:
            return []
        elif before is not None and after is None:
            return [ProtoPackageRemoved(before)]
        elif before is None and after is not None:
            return [ProtoPackageAdded(after)]

        assert before is not None and after is not None
        return [ProtoPackageChanged(before, after)]


class ProtoPackageChanged(ProtoNodeDiff):
    def __init__(self, before: ProtoPackage, after: ProtoPackage):
        self.before = before
        self.after = after

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoPackageChanged)
            and self.before == other.before
            and self.after == other.after
        )


class ProtoPackageAdded(ProtoNodeDiff):
    def __init__(self, after: ProtoPackage):
        self.after = after

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProtoPackageAdded) and self.after == other.after


class ProtoPackageRemoved(ProtoNodeDiff):
    def __init__(self, before: ProtoPackage):
        self.before = before

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProtoPackageRemoved) and self.before == other.before
