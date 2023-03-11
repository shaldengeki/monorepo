from typing import Optional

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_identifier import (
    ParsedProtoIdentifierNode,
    ProtoEnumOrMessageIdentifier,
    ProtoIdentifier,
)
from src.proto_node import ParsedProtoNode, ProtoContainerNode, ProtoNode
from src.proto_option import ProtoOption


class ProtoServiceRPC(ProtoNode):
    def __init__(
        self,
        name: ProtoIdentifier,
        request_type: ProtoEnumOrMessageIdentifier,
        response_type: ProtoEnumOrMessageIdentifier,
        request_stream: bool = False,
        response_stream: bool = False,
        options: Optional[list[ProtoOption]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self
        self.request_type = request_type
        self.request_type.parent = self
        self.response_type = response_type
        self.response_type.parent = self
        self.request_stream = request_stream
        self.response_stream = response_stream

        if options is None:
            options = []
        self.options = options
        for option in self.options:
            option.parent = self

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name
            and self.request_type == other.request_type
            and self.response_type == other.response_type
            and self.request_stream == other.request_stream
            and self.response_stream == other.response_stream
            and self.options == other.options
        )

    def __str__(self) -> str:
        return f"<ProtoServiceRPC name={self.name} request_type={self.request_type} response_type={self.response_type} request_stream={self.request_stream} response_stream={self.response_stream} options={self.options}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoServiceRPC":
        return ProtoServiceRPC(
            name=self.name,
            request_type=self.request_type,
            response_type=self.response_type,
            request_stream=self.request_stream,
            response_stream=self.response_stream,
            options=sorted(self.options, key=lambda o: str(o.normalize())),
            parent=self.parent,
        )

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("rpc "):
            return None
        proto_source = proto_source[4:].strip()

        # Match the RPC name.
        name_match = ProtoIdentifier.match(proto_source)
        if name_match is None:
            return None
        name = name_match.node
        proto_source = name_match.remaining_source.strip()

        if not proto_source.startswith("("):
            return None
        proto_source = proto_source[1:].strip()

        # Try to parse the request type.
        stream_or_request_name_match = ProtoEnumOrMessageIdentifier.match(proto_source)
        if stream_or_request_name_match is None:
            return None

        request_stream = False
        if stream_or_request_name_match.remaining_source.startswith(")"):
            request_name = stream_or_request_name_match.node
            proto_source = stream_or_request_name_match.remaining_source.strip()
        elif stream_or_request_name_match.node.identifier == "stream":
            # Try matching the request name.
            potential_request_name_match = ProtoEnumOrMessageIdentifier.match(
                stream_or_request_name_match.remaining_source.strip()
            )
            if potential_request_name_match is None:
                # No further name.
                request_name = stream_or_request_name_match.node
                proto_source = stream_or_request_name_match.remaining_source.strip()
            else:
                # There's a further name!
                request_name = potential_request_name_match.node
                request_stream = True
                proto_source = potential_request_name_match.remaining_source.strip()
        else:
            return None

        if not proto_source.startswith(")"):
            return None
        proto_source = proto_source[1:].strip()

        if not proto_source.startswith("returns "):
            return None
        proto_source = proto_source[8:].strip()

        if not proto_source.startswith("("):
            return None
        proto_source = proto_source[1:].strip()

        # Try to parse the response type.
        stream_or_response_name_match = ProtoEnumOrMessageIdentifier.match(proto_source)
        if stream_or_response_name_match is None:
            return None

        response_stream = False
        if stream_or_response_name_match.remaining_source.startswith(")"):
            response_name = stream_or_response_name_match.node
            proto_source = stream_or_response_name_match.remaining_source.strip()
        elif stream_or_response_name_match.node.identifier == "stream":
            # Try matching the response name.
            potential_response_name_match = ProtoEnumOrMessageIdentifier.match(
                stream_or_response_name_match.remaining_source.strip()
            )
            if potential_response_name_match is None:
                # No further name.
                response_name = stream_or_response_name_match.node
                proto_source = stream_or_response_name_match.remaining_source.strip()
            else:
                # There's a further name!
                response_name = potential_response_name_match.node
                response_stream = True
                proto_source = potential_response_name_match.remaining_source.strip()
        else:
            return None

        if not proto_source.startswith(")"):
            return None
        proto_source = proto_source[1:].strip()

        # Try to parse options.
        options: list[ProtoOption] = []
        if proto_source.startswith("{"):
            proto_source = proto_source[1:].strip()
            while proto_source:
                # Remove empty statements.
                if proto_source.startswith(";"):
                    proto_source = proto_source[1:].strip()
                    continue

                if proto_source.startswith("}"):
                    proto_source = proto_source[1:].strip()
                    break

                option_match = ProtoOption.match(proto_source)
                if option_match is None:
                    return None
                options.append(option_match.node)
                proto_source = option_match.remaining_source.strip()
        else:
            if not proto_source.startswith(";"):
                return None
            proto_source = proto_source[1:].strip()

        return ParsedProtoNode(
            ProtoServiceRPC(
                name=name,
                request_type=request_name,
                response_type=response_name,
                request_stream=request_stream,
                response_stream=response_stream,
                options=options,
                parent=parent,
            ),
            proto_source.strip(),
        )

    def serialize(self) -> str:
        serialized_parts = [
            "rpc",
            self.name.serialize(),
        ]

        if self.request_stream:
            serialized_parts.append(f"(stream {self.request_type.serialize()})")
        else:
            serialized_parts.append(f"({self.request_type.serialize()})")

        serialized_parts.append("returns")

        if self.response_stream:
            serialized_parts.append(f"(stream {self.response_type.serialize()})")
        else:
            serialized_parts.append(f"({self.response_type.serialize()})")

        if self.options:
            serialized_parts.append("{")
            serialized_parts.append(
                " ".join(option.serialize() for option in self.options)
            )
            serialized_parts.append("}")
            return " ".join(serialized_parts)
        else:
            return " ".join(serialized_parts) + ";"


class ProtoService(ProtoContainerNode):
    def __init__(self, name: ProtoIdentifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name.parent = self

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.name == other.name

    def __str__(self) -> str:
        return f"<ProtoService name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoService":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )
        return ProtoService(
            name=self.name,
            nodes=sorted(non_comment_nodes, key=lambda n: str(n.normalize())),
            parent=self.parent,
        )

    @classmethod
    def match_header(
        cls,
        proto_source: str,
        parent: Optional["ProtoNode"] = None,
    ) -> Optional["ParsedProtoIdentifierNode"]:
        if not proto_source.startswith("service "):
            return None

        proto_source = proto_source[8:]
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid service name: {proto_source}")

        service_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto service has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        return ParsedProtoIdentifierNode(service_name, proto_source[1:].strip())

    @classmethod
    def container_types(cls) -> list[type[ProtoNode]]:
        return [
            ProtoOption,
            ProtoServiceRPC,
            ProtoSingleLineComment,
            ProtoMultiLineComment,
        ]

    @classmethod
    def construct(
        cls,
        header_match: ParsedProtoNode,
        contained_nodes: list[ProtoNode],
        footer_match: str,
        parent: Optional[ProtoNode] = None,
    ) -> ProtoNode:
        assert isinstance(header_match, ParsedProtoIdentifierNode)
        return ProtoService(
            name=header_match.node, nodes=contained_nodes, parent=parent
        )

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    def serialize(self) -> str:
        serialize_parts = (
            [f"service {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)
