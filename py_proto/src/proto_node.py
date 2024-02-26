import abc
from typing import NamedTuple, Optional, Sequence


class ProtoNode(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def match(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoNode"]:
        raise NotImplementedError

    def __init__(self, parent: Optional["ProtoNode"] = None):
        self.parent = parent

    @abc.abstractmethod
    def serialize(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def normalize(self) -> Optional["ProtoNode"]:
        raise NotImplementedError


class ProtoContainerNode(ProtoNode):
    def __init__(
        self,
        nodes: Sequence[ProtoNode],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.nodes = nodes
        for node in self.nodes:
            node.parent = self

    def __eq__(self, other) -> bool:
        return self.nodes == other.nodes

    @classmethod
    @abc.abstractmethod
    def match_header(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoNode"]:
        raise NotImplementedError

    @classmethod
    def match_footer(
        cls,
        proto_source: str,
        parent: Optional[ProtoNode] = None,
    ) -> Optional[str]:
        if proto_source.startswith("}"):
            return proto_source[1:].strip()

        return None

    @classmethod
    @abc.abstractmethod
    def container_types(cls) -> list[type[ProtoNode]]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def construct(
        cls,
        header_match: "ParsedProtoNode",
        contained_nodes: list[ProtoNode],
        footer_match: str,
        parent: Optional[ProtoNode] = None,
    ) -> ProtoNode:
        raise NotImplementedError

    @classmethod
    def parse_partial_content(cls, partial_content: str) -> "ParsedProtoNode":
        for node_type in cls.container_types():
            try:
                match_result = node_type.match(partial_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(f"Could not parse partial content:\n{partial_content}")
            if match_result is not None:
                return match_result
        raise ValueError(f"Could not parse partial content:\n{partial_content}")

    @classmethod
    def match(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoNode"]:
        header_match = cls.match_header(proto_source, parent=parent)
        if header_match is None:
            return None

        proto_source = header_match.remaining_source.strip()
        nodes = []
        footer_match: Optional[str] = None
        while proto_source:
            # Remove empty statements.
            if proto_source.startswith(";"):
                proto_source = proto_source[1:].strip()
                continue

            footer_match = cls.match_footer(proto_source, parent)
            if footer_match is not None:
                proto_source = footer_match.strip()
                break

            match_result = cls.parse_partial_content(proto_source)
            nodes.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        if footer_match is None:
            footer_match = cls.match_footer(proto_source, parent)
            if footer_match is None:
                raise ValueError(
                    f"Footer was not found when matching container node {cls} for remaining proto source {proto_source}"
                )

        return ParsedProtoNode(
            cls.construct(header_match, nodes, footer_match, parent=parent),
            proto_source.strip(),
        )


class ParsedProtoNode(NamedTuple):
    node: ProtoNode
    remaining_source: str

    def __str__(self) -> str:
        return f"<ParsedProtoNode node={self.node} remaining_source={self.remaining_source} >"

    def __repr__(self) -> str:
        return str(self)


class ProtoNodeDiff(abc.ABC):
    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(str(self))
