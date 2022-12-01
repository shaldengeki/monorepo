from typing import Optional

from src.proto_identifier import ProtoEnumOrMessageIdentifier, ProtoIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode
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
    ):
        self.name = name
        self.request_type = request_type
        self.response_type = response_type
        self.request_stream = request_stream
        self.response_stream = response_stream

        if options is None:
            options = []
        self.options = options

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

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
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
        options = []
        if proto_source.startswith("{"):
            proto_source = proto_source[1:].strip()
            options = []
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
                name,
                request_name,
                response_name,
                request_stream,
                response_stream,
                options,
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


class ProtoService(ProtoNode):
    def __init__(self, name: ProtoIdentifier, nodes: list[ProtoNode]):
        self.name = name
        self.nodes = nodes

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<ProtoService name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def parse_partial_content(partial_service_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoOption,
            ProtoServiceRPC,
        ):
            try:
                match_result = node_type.match(partial_service_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial service content:\n{partial_service_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(
            f"Could not parse partial service content:\n{partial_service_content}"
        )

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("service "):
            return None

        proto_source = proto_source[8:]
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid service name: {proto_source}")

        enum_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto service has invalid syntax, expecting opening curly brace: {proto_source}"
            )

        proto_source = proto_source[1:].strip()
        parsed_tree = []
        while proto_source:
            # Remove empty statements.
            if proto_source.startswith(";"):
                proto_source = proto_source[1:].strip()
                continue

            if proto_source.startswith("}"):
                proto_source = proto_source[1:].strip()
                break

            match_result = ProtoService.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoNode(ProtoService(enum_name, nodes=parsed_tree), proto_source)

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
