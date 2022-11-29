from enum import Enum
from typing import Optional

from src.proto_enum import ProtoEnum, ProtoEnumValueOption
from src.proto_identifier import ProtoFullIdentifier, ProtoIdentifier
from src.proto_int import ProtoInt
from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_option import ProtoOption
from src.proto_reserved import ProtoReserved


class ProtoMessageFieldOption(ProtoEnumValueOption):
    pass


class ProtoMessageFieldTypesEnum(Enum):
    DOUBLE = "double"
    FLOAT = "float"
    INT32 = "int32"
    INT64 = "int64"
    UINT32 = "uint32"
    UINT64 = "uint64"
    SINT32 = "sint32"
    SINT64 = "sint64"
    FIXED32 = "fixed32"
    FIXED64 = "fixed64"
    SFIXED32 = "sfixed32"
    SFIXED64 = "sfixed64"
    BOOL = "bool"
    STRING = "string"
    BYTES = "bytes"
    ENUM_OR_MESSAGE = "enum_or_message"


class ProtoMessageField(ProtoNode):
    def __init__(
        self,
        type: ProtoMessageFieldTypesEnum,
        name: ProtoIdentifier,
        number: ProtoInt,
        repeated: bool = False,
        enum_or_message_type_name: Optional[ProtoFullIdentifier] = None,
        options: list[ProtoMessageFieldOption] = None,
    ):
        self.type = type
        self.name = name
        self.number = number
        self.repeated = repeated
        self.enum_or_message_type_name = enum_or_message_type_name

        if options is None:
            options = []
        self.options = options

    def __eq__(self, other) -> bool:
        return (
            self.type == other.type
            and self.name == other.name
            and self.number == other.number
            and self.repeated == other.repeated
            and self.enum_or_message_type_name == other.enum_or_message_type_name
            and self.options == other.options
        )

    def __str__(self) -> str:
        return f"<ProtoMessageField type={self.type} name={self.name} number={self.number} repeated={self.repeated} enum_or_message_type_name={self.enum_or_message_type_name} options={self.options}>"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        # First, try to match the optional repeated.
        repeated = False
        if proto_source.startswith("repeated "):
            repeated = True
            proto_source = proto_source[9:].strip()

        # Next, try to match the field type.
        matched_type: Optional[ProtoMessageFieldTypesEnum] = None
        for field_type in ProtoMessageFieldTypesEnum:
            if field_type == ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE:
                # This is special-cased below.
                break
            if proto_source.startswith(f"{field_type.value} "):
                matched_type = field_type
                proto_source = proto_source[len(field_type.value) + 1 :]

        # If this is an enum or message type, try to match a name.
        enum_or_message_type_name = None
        if matched_type is None:
            # See if this is an enum or message type.
            match = ProtoFullIdentifier.match(proto_source)
            if match is None:
                return None
            matched_type = ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE
            enum_or_message_type_name = match.node
            proto_source = match.remaining_source.strip()

        # Match the field name.
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            return None
        name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("= "):
            return None
        proto_source = proto_source[2:].strip()

        # Match the field number.
        match = ProtoInt.match(proto_source)
        if match is None:
            return None
        number = match.node
        proto_source = match.remaining_source.strip()

        options = []
        if proto_source.startswith("["):
            proto_source = proto_source[1:].strip()
            end_bracket = proto_source.find("]")
            if end_bracket == -1:
                raise ValueError(
                    f"Proto has invalid message field option syntax, cannot find ]: {proto_source}"
                )
            for option_part in proto_source[:end_bracket].strip().split(","):
                match = ProtoMessageFieldOption.match(option_part.strip())
                if match is None:
                    raise ValueError(
                        f"Proto has invalid message field option syntax: {proto_source}"
                    )
                options.append(match.node)
            proto_source = proto_source[end_bracket + 1 :].strip()

        if not proto_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid message field syntax, missing ending ;:{proto_source}"
            )

        return ParsedProtoNode(
            ProtoMessageField(
                matched_type, name, number, repeated, enum_or_message_type_name, options
            ),
            proto_source,
        )

    def serialize(self) -> str:
        serialized_parts = []
        if self.repeated:
            serialized_parts.append("repeated")

        if self.type == ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE:
            serialized_parts.append(self.enum_or_message_type_name.serialize())
        else:
            serialized_parts.append(self.type.value)

        serialized_parts = serialized_parts + [
            self.name.serialize(),
            "=",
            self.number.serialize(),
        ]

        if self.options:
            serialized_parts.append("[")
            serialized_parts.append(
                ", ".join(option.serialize() for option in self.options)
            )
            serialized_parts.append("]")

        return " ".join(serialized_parts) + ";"


ProtoOneOfNodeTypes = ProtoOption | ProtoMessageField

class ProtoOneOf(ProtoNode):
    def __init__(self, name: ProtoIdentifier, nodes: list[ProtoOneOfNodeTypes]):
        self.name = name
        self.nodes = nodes

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def parse_partial_content(partial_oneof_content: str) -> ParsedProtoNode:
        for node_type in (ProtoMessageField,):
            try:
                match_result = node_type.match(partial_oneof_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial oneof content:\n{partial_oneof_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(
            f"Could not parse partial oneof content:\n{partial_oneof_content}"
        )

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("oneof "):
            return None

        proto_source = proto_source[6:].strip()

        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid syntax, expecting identifier for oneof: {proto_source}")

        oneof_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto has invalid syntax, expecting opening curly brace: {proto_source}"
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

            match_result = ProtoOneOf.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoNode(ProtoOneOf(oneof_name, nodes=parsed_tree), proto_source)

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    def serialize(self) -> str:
        serialize_parts = [f"oneof {self.name.serialize()} {{"] + [n.serialize() for n in self.nodes] + ["}"]
        return "\n".join(serialize_parts)


class ProtoMessage(ProtoNode):
    def __init__(self, name: ProtoIdentifier, nodes: list[ProtoNode]):
        self.name = name
        self.nodes = nodes

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.nodes == other.nodes

    def __str__(self) -> str:
        return f"<ProtoMessage name={self.name}, nodes={self.nodes}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def parse_partial_content(partial_message_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoEnum,
            ProtoOption,
            ProtoMessage,
            ProtoReserved,
            ProtoMessageField,
            ProtoOneOf,
        ):
            try:
                match_result = node_type.match(partial_message_content)
            except (ValueError, IndexError, TypeError):
                raise ValueError(
                    f"Could not parse partial message content:\n{partial_message_content}"
                )
            if match_result is not None:
                return match_result
        raise ValueError(
            f"Could not parse partial message content:\n{partial_message_content}"
        )

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("message "):
            return None

        proto_source = proto_source[8:]
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            raise ValueError(f"Proto has invalid message name: {proto_source}")

        enum_name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("{"):
            raise ValueError(
                f"Proto message has invalid syntax, expecting opening curly brace: {proto_source}"
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

            match_result = ProtoMessage.parse_partial_content(proto_source)
            parsed_tree.append(match_result.node)
            proto_source = match_result.remaining_source.strip()

        return ParsedProtoNode(ProtoMessage(enum_name, nodes=parsed_tree), proto_source)

    @property
    def options(self) -> list[ProtoOption]:
        return [node for node in self.nodes if isinstance(node, ProtoOption)]

    def serialize(self) -> str:
        serialize_parts = (
            [f"message {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)
