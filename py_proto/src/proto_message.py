from enum import Enum
from typing import Optional

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_enum import ProtoEnum
from src.proto_extend import ProtoExtend
from src.proto_extensions import ProtoExtensions
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt
from src.proto_message_field import (
    ProtoMessageField,
    ProtoMessageFieldOption,
    ProtoMessageFieldTypesEnum,
)
from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_option import ProtoOption
from src.proto_reserved import ProtoReserved

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

    def normalize(self) -> "ProtoOneOf":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )
        options = []
        fields = []
        for node in non_comment_nodes:
            if isinstance(node, ProtoOption):
                options.append(node.normalize())
            elif (
                isinstance(node, ProtoMessageField)
                or isinstance(node, ProtoOneOf)
                or isinstance(node, ProtoMap)
            ):
                fields.append(node.normalize())
            else:
                raise ValueError(
                    f"Can't sort message {self} node for normalizing: {node}"
                )

        sorted_nodes_for_normalizing = sorted(
            options, key=lambda o: str(o.normalize())
        ) + sorted(fields, key=lambda f: int(f.number))

        return ProtoOneOf(
            self.name,
            nodes=sorted_nodes_for_normalizing,
        )

    @staticmethod
    def parse_partial_content(partial_oneof_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoMessageField,
            ProtoOption,
            ProtoSingleLineComment,
            ProtoMultiLineComment,
        ):
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
            raise ValueError(
                f"Proto has invalid syntax, expecting identifier for oneof: {proto_source}"
            )

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
        serialize_parts = (
            [f"oneof {self.name.serialize()} {{"]
            + [n.serialize() for n in self.nodes]
            + ["}"]
        )
        return "\n".join(serialize_parts)


class ProtoMapKeyTypesEnum(Enum):
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


ProtoMapValueTypesEnum = ProtoMessageFieldTypesEnum


class ProtoMap(ProtoNode):
    def __init__(
        self,
        key_type: ProtoMapKeyTypesEnum,
        value_type: ProtoMapValueTypesEnum,
        name: ProtoIdentifier,
        number: ProtoInt,
        enum_or_message_type_name: Optional[ProtoFullIdentifier] = None,
        options: Optional[list[ProtoMessageFieldOption]] = None,
    ):
        self.key_type = key_type
        self.value_type = value_type
        self.name = name
        self.number = number
        self.enum_or_message_type_name = enum_or_message_type_name

        if options is None:
            options = []
        self.options = options

    def __eq__(self, other) -> bool:
        return (
            self.key_type == other.key_type
            and self.value_type == other.value_type
            and self.name == other.name
            and self.number == other.number
            and self.enum_or_message_type_name == other.enum_or_message_type_name
            and self.options == other.options
        )

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} key_type={self.key_type} value_type={self.value_type} name={self.name} number={self.number} enum_or_message_type_name={self.enum_or_message_type_name} options={self.options}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoMap":
        return ProtoMap(
            key_type=self.key_type,
            value_type=self.value_type,
            name=self.name,
            number=self.number,
            enum_or_message_type_name=self.enum_or_message_type_name,
            options=sorted(self.options, key=lambda o: str(o.normalize())),
        )

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        if proto_source.startswith("map "):
            proto_source = proto_source[4:].strip()
        elif proto_source.startswith("map<"):
            proto_source = proto_source[3:].strip()
        else:
            return None

        # Try to match the map key type.
        proto_source = proto_source[1:].strip()
        key_type = None
        for potential_key_type in ProtoMapKeyTypesEnum:
            if proto_source.startswith(potential_key_type.value):
                key_type = potential_key_type
                proto_source = proto_source[len(potential_key_type.value) :].strip()
                break
        if key_type is None:
            return None

        if not proto_source.startswith(","):
            return None
        proto_source = proto_source[1:].strip()

        # Next, try to match the map value type.
        value_type: Optional[ProtoMapValueTypesEnum] = None
        for potential_value_type in ProtoMapValueTypesEnum:
            if potential_value_type == ProtoMapValueTypesEnum.ENUM_OR_MESSAGE:
                # This is special-cased below.
                break
            if proto_source.startswith(potential_value_type.value):
                value_type = potential_value_type
                proto_source = proto_source[len(potential_value_type.value) :].strip()

        # If this is an enum or message type, try to match a name.
        enum_or_message_type_name = None
        if value_type is None:
            # See if this is an enum or message type.
            match = ProtoEnumOrMessageIdentifier.match(proto_source)
            if match is None:
                return None
            value_type = ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE
            enum_or_message_type_name = match.node
            proto_source = match.remaining_source.strip()

        if not proto_source.startswith(">"):
            return None
        proto_source = proto_source[1:].strip()

        # Try to match the map field's name.
        match = ProtoIdentifier.match(proto_source)
        if match is None:
            return None
        name = match.node
        proto_source = match.remaining_source.strip()

        if not proto_source.startswith("="):
            return None
        proto_source = proto_source[1:].strip()

        # Try to match the map field number.
        match = ProtoInt.match(proto_source)
        if match is None:
            return None
        number = match.node
        proto_source = match.remaining_source.strip()

        # Try to match map field options, if any.
        options = []
        if proto_source.startswith("["):
            proto_source = proto_source[1:].strip()
            end_bracket = proto_source.find("]")
            if end_bracket == -1:
                raise ValueError(
                    f"Proto has invalid map field option syntax, cannot find ]: {proto_source}"
                )
            for option_part in proto_source[:end_bracket].strip().split(","):
                match = ProtoMessageFieldOption.match(option_part.strip())
                if match is None:
                    raise ValueError(
                        f"Proto has invalid map field option syntax: {proto_source}"
                    )
                options.append(match.node)
            proto_source = proto_source[end_bracket + 1 :].strip()

        if not proto_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid map field syntax, missing ending ;:{proto_source}"
            )

        return ParsedProtoNode(
            ProtoMap(
                key_type, value_type, name, number, enum_or_message_type_name, options
            ),
            proto_source[1:].strip(),
        )

    def serialize(self) -> str:
        serialized_parts = [
            f"map",
            f"<{self.key_type.value},",
        ]

        if self.value_type == ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE:
            serialized_parts.append(f"{self.enum_or_message_type_name.serialize()}>")
        else:
            serialized_parts.append(f"{self.value_type.value}>")

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

    def normalize(self) -> "ProtoMessage":
        non_comment_nodes = filter(
            lambda n: not isinstance(n, ProtoComment), self.nodes
        )

        options = []
        enums = []
        messages = []
        fields = []
        reserveds = []
        for node in non_comment_nodes:
            if isinstance(node, ProtoOption):
                options.append(node.normalize())
            elif isinstance(node, ProtoEnum):
                options.append(node.normalize())
            elif isinstance(node, ProtoMessage):
                messages.append(node.normalize())
            elif (
                isinstance(node, ProtoMessageField)
                or isinstance(node, ProtoOneOf)
                or isinstance(node, ProtoMap)
            ):
                fields.append(node.normalize())
            elif isinstance(node, ProtoReserved):
                reserveds.append(node.normalize())
            else:
                raise ValueError(
                    f"Can't sort message {self} node for normalizing: {node}"
                )

        sorted_nodes_for_normalizing = (
            sorted(options, key=lambda o: str(o.normalize()))
            + sorted(enums, key=lambda e: str(e))
            + sorted(messages, key=lambda m: str(m))
            + sorted(fields, key=lambda f: int(f.number))
            + sorted(reserveds, key=lambda r: (r.min, r.max))
        )

        return ProtoMessage(
            name=self.name,
            nodes=sorted_nodes_for_normalizing,
        )

    @staticmethod
    def parse_partial_content(partial_message_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoSingleLineComment,
            ProtoMultiLineComment,
            ProtoEnum,
            ProtoExtend,
            ProtoExtensions,
            ProtoOption,
            ProtoMessage,
            ProtoReserved,
            ProtoMessageField,
            ProtoOneOf,
            ProtoMap,
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
