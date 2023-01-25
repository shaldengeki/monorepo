from enum import Enum
from typing import Optional

from src.proto_enum import ProtoEnumValueOption
from src.proto_identifier import (
    ProtoEnumOrMessageIdentifier,
    ProtoFullIdentifier,
    ProtoIdentifier,
)
from src.proto_int import ProtoInt
from src.proto_node import ParsedProtoNode, ProtoNode


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
        optional: bool = False,
        enum_or_message_type_name: Optional[ProtoFullIdentifier] = None,
        options: Optional[list[ProtoMessageFieldOption]] = None,
    ):
        self.type = type
        self.name = name
        self.number = number

        # Only allow one of repeated or optional to be true.
        if repeated and optional:
            raise ValueError(
                f"Only one of repeated,optional can be True in message field {self.name}"
            )

        self.repeated = repeated
        self.optional = optional
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
            and self.optional == other.optional
            and self.enum_or_message_type_name == other.enum_or_message_type_name
            and self.options == other.options
        )

    def __str__(self) -> str:
        return f"<ProtoMessageField type={self.type} name={self.name} number={self.number} repeated={self.repeated} enum_or_message_type_name={self.enum_or_message_type_name} options={self.options}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoMessageField":
        return ProtoMessageField(
            type=self.type,
            name=self.name,
            number=self.number,
            repeated=self.repeated,
            optional=self.optional,
            enum_or_message_type_name=self.enum_or_message_type_name,
            options=sorted(self.options, key=lambda o: o.name),
        )

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
        # First, try to match the optional repeated.
        repeated = False
        if proto_source.startswith("repeated "):
            repeated = True
            proto_source = proto_source[9:].strip()

        optional = False
        if proto_source.startswith("optional "):
            optional = True
            proto_source = proto_source[9:].strip()
            if repeated:
                raise ValueError(
                    "Proto message field has invalid syntax, cannot have both repeated and optional"
                )

        # Next, try to match the field type.
        matched_type: Optional[ProtoMessageFieldTypesEnum] = None
        for field_type in ProtoMessageFieldTypesEnum:
            if field_type == ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE:
                # This is special-cased below.
                continue
            if proto_source.startswith(f"{field_type.value} "):
                matched_type = field_type
                proto_source = proto_source[len(field_type.value) + 1 :]

        # If this is an enum or message type, try to match a name.
        enum_or_message_type_name = None
        if matched_type is None:
            # See if this is an enum or message type.
            match = ProtoEnumOrMessageIdentifier.match(proto_source)
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
                matched_type,
                name,
                number,
                repeated,
                optional,
                enum_or_message_type_name,
                options,
            ),
            proto_source[1:].strip(),
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
