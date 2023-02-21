from typing import Optional

from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff
from src.proto_string_literal import ProtoStringLiteral


class ProtoImport(ProtoNode):
    def __init__(
        self,
        path: ProtoStringLiteral,
        weak: bool = False,
        public: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.path = path
        self.path.parent = self
        self.weak = weak
        self.public = public

    def __eq__(self, other) -> bool:
        return (
            (hasattr(other, "path") and self.path == other.path)
            and (hasattr(other, "weak") and self.weak == other.weak)
            and (hasattr(other, "public") and self.public == other.public)
        )

    def __str__(self) -> str:
        return f"<ProtoImport path={self.path.serialize()} weak={self.weak} public={self.public}>"

    def __repr__(self) -> str:
        return str(self)

    def __dict__(self):
        return {
            "path": self.path.serialize(),
            "weak": self.weak,
            "public": self.public,
        }

    def normalize(self) -> "ProtoImport":
        return self

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoNode"]:
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
            ProtoImport(path=match.node, weak=weak, public=public, parent=parent),
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

    @staticmethod
    def diff_sets(
        before: list["ProtoImport"], after: list["ProtoImport"]
    ) -> list["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []
        before_names = set(i.path for i in before)
        after_names = set(i.path for i in after)
        for name in before_names - after_names:
            diffs.append(ProtoImportRemoved(next(i for i in before if i.path == name)))
        for name in after_names - before_names:
            diffs.append(ProtoImportAdded(next(i for i in after if i.path == name)))
        for name in before_names & after_names:
            before_import = next(i for i in before if i.path == name)
            after_import = next(i for i in after if i.path == name)
            if before_import.weak and not after_import.weak:
                diffs.append(ProtoImportMadeNonWeak(after_import))
            elif not before_import.weak and after_import.weak:
                diffs.append(ProtoImportMadeWeak(after_import))
            if before_import.public and not after_import.public:
                diffs.append(ProtoImportMadeNonPublic(after_import))
            elif not before_import.public and after_import.public:
                diffs.append(ProtoImportMadePublic(after_import))

        return diffs


class ProtoImportAdded(ProtoNodeDiff):
    def __init__(self, proto_import: ProtoImport):
        self.proto_import = proto_import

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ProtoImportAdded)
            and self.proto_import == other.proto_import
        )


class ProtoImportRemoved(ProtoImportAdded):
    pass


class ProtoImportMadeWeak(ProtoImportAdded):
    pass


class ProtoImportMadeNonWeak(ProtoImportAdded):
    pass


class ProtoImportMadePublic(ProtoImportAdded):
    pass


class ProtoImportMadeNonPublic(ProtoImportAdded):
    pass
