from enum import Enum
from typing import Optional, Sequence

from src.proto_enum import ParsedProtoEnumValueOptionNode, ProtoEnumValueOption
from src.proto_identifier import ProtoEnumOrMessageIdentifier, ProtoIdentifier
from src.proto_int import ProtoInt
from src.proto_node import ParsedProtoNode, ProtoNode, ProtoNodeDiff


class ParsedProtoMessageFieldOptionNode(ParsedProtoEnumValueOptionNode):
    node: "ProtoMessageFieldOption"
    remaining_source: str


class ProtoMessageFieldOption(ProtoEnumValueOption):
    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoMessageFieldOptionNode"]:
        match = super().match(parent, proto_source)
        if match is None:
            return None

        return ParsedProtoMessageFieldOptionNode(
            match.node,
            match.remaining_source.strip(),
        )


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


class ParsedProtoMessageFieldNode(ParsedProtoNode):
    node: "ProtoMessageField"
    remaining_source: str


class ProtoMessageField(ProtoNode):
    def __init__(
        self,
        parent: Optional[ProtoNode],
        type: ProtoMessageFieldTypesEnum,
        name: ProtoIdentifier,
        number: ProtoInt,
        repeated: bool = False,
        optional: bool = False,
        enum_or_message_type_name: Optional[ProtoEnumOrMessageIdentifier] = None,
        options: Optional[list[ProtoMessageFieldOption]] = None,
    ):
        super().__init__(parent)
        self.type = type
        self.name = name
        self.name.parent = self
        self.number = number
        self.number.parent = self

        # Only allow one of repeated or optional to be true.
        if repeated and optional:
            raise ValueError(
                f"Only one of repeated,optional can be True in message field {self.name}"
            )

        self.repeated = repeated
        self.optional = optional
        self.enum_or_message_type_name = enum_or_message_type_name
        if self.enum_or_message_type_name is not None:
            self.enum_or_message_type_name.parent = self

        if options is None:
            options = []
        self.options = options
        for option in self.options:
            option.parent = self

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
            parent=self.parent,
            type=self.type,
            name=self.name,
            number=self.number,
            repeated=self.repeated,
            optional=self.optional,
            enum_or_message_type_name=self.enum_or_message_type_name,
            options=sorted(self.options, key=lambda o: str(o.name)),
        )

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoMessageFieldNode"]:
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
            match = ProtoEnumOrMessageIdentifier.match(None, proto_source)
            if match is None:
                return None
            matched_type = ProtoMessageFieldTypesEnum.ENUM_OR_MESSAGE
            enum_or_message_type_name = match.node
            proto_source = match.remaining_source.strip()

        # Match the field name.
        identifier_match = ProtoIdentifier.match(None, proto_source)
        if identifier_match is None:
            return None
        name = identifier_match.node
        proto_source = identifier_match.remaining_source.strip()

        if not proto_source.startswith("= "):
            return None
        proto_source = proto_source[2:].strip()

        # Match the field number.
        int_match = ProtoInt.match(None, proto_source)
        if int_match is None:
            return None
        number = int_match.node
        proto_source = int_match.remaining_source.strip()

        options = []
        if proto_source.startswith("["):
            proto_source = proto_source[1:].strip()
            end_bracket = proto_source.find("]")
            if end_bracket == -1:
                raise ValueError(
                    f"Proto has invalid message field option syntax, cannot find ]: {proto_source}"
                )
            for option_part in proto_source[:end_bracket].strip().split(","):
                message_field_option_match = ProtoMessageFieldOption.match(
                    None, option_part.strip()
                )
                if message_field_option_match is None:
                    raise ValueError(
                        f"Proto has invalid message field option syntax: {proto_source}"
                    )
                options.append(message_field_option_match.node)
            proto_source = proto_source[end_bracket + 1 :].strip()

        if not proto_source.startswith(";"):
            raise ValueError(
                f"Proto has invalid message field syntax, missing ending ;:{proto_source}"
            )

        return ParsedProtoMessageFieldNode(
            ProtoMessageField(
                parent,
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
            if self.enum_or_message_type_name is None:
                raise ValueError(
                    f"Enum or message type name was not set for: {str(self)}"
                )
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

    @staticmethod
    def diff(
        parent: "ProtoNode",
        before: Optional["ProtoMessageField"],
        after: Optional["ProtoMessageField"],
    ) -> Sequence["ProtoNodeDiff"]:
        # TODO: scope these diffs under ProtoMessageField
        diffs: list["ProtoNodeDiff"] = []
        if before is None or after is None:
            if after is not None:
                diffs.append(ProtoMessageFieldAdded(parent, after))
            elif before is not None:
                diffs.append(ProtoMessageFieldRemoved(parent, before))
        else:
            if before.name != after.name:
                diffs.append(ProtoMessageFieldNameChanged(parent, before, after.name))
            if before.number != after.number:
                raise ValueError(
                    f"Don't know how to handle diff between message fields whose names are identical: {before}, {after}"
                )
            diffs.extend(
                ProtoMessageFieldOption.diff_sets(before.options, after.options)
            )
        return diffs

    @staticmethod
    def diff_sets(
        parent: "ProtoNode",
        before: list["ProtoMessageField"],
        after: list["ProtoMessageField"],
    ) -> list["ProtoNodeDiff"]:
        diffs: list[ProtoNodeDiff] = []

        before_number_to_fields = {int(mf.number): mf for mf in before}
        after_number_to_fields = {int(mf.number): mf for mf in after}
        all_numbers = sorted(
            set(before_number_to_fields.keys()).union(
                set(after_number_to_fields.keys())
            )
        )
        for number in all_numbers:
            diffs.extend(
                ProtoMessageField.diff(
                    parent,
                    before_number_to_fields.get(number, None),
                    after_number_to_fields.get(number, None),
                )
            )

        return diffs


class ProtoMessageFieldDiff(ProtoNodeDiff):
    def __init__(self, message: "ProtoNode", message_field: "ProtoMessageField"):
        super().__init__()
        self.message = message
        self.message_field = message_field

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, ProtoMessageFieldDiff)
            and self.message == other.message
            and self.message_field == other.message_field
        )

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} message={self.message} message_field={self.message_field}>"


class ProtoMessageFieldAdded(ProtoMessageFieldDiff):
    pass


class ProtoMessageFieldRemoved(ProtoMessageFieldDiff):
    pass


class ProtoMessageFieldNameChanged(ProtoMessageFieldDiff):
    def __init__(
        self,
        message: ProtoNode,
        message_field: ProtoMessageField,
        new_name: ProtoIdentifier,
    ):
        super().__init__(message, message_field)
        self.new_name = new_name

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, ProtoMessageFieldNameChanged)
            and self.new_name == other.new_name
        )

    def __str__(self) -> str:
        return f"<ProtoMessageFieldNameChanged message={self.message} message_field={self.message_field} new_name={self.new_name}>"
