from enum import Enum
from typing import Optional

from src.proto_identifier import ProtoIdentifier
from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoReservedRangeEnum(Enum):
    MAX = "max"


class ProtoReservedRange:
    def __init__(
        self, min: ProtoInt, max: Optional[ProtoInt | ProtoReservedRangeEnum] = None
    ):
        self.min = min

        if (
            max is not None
            and max != ProtoReservedRangeEnum.MAX
            and int(min) > int(max)
        ):
            raise ValueError(
                f"min {min} was greater than max {max} in ProtoReservedRange"
            )

        self.max = max

    def __eq__(self, other: "ProtoReservedRange") -> bool:
        if not isinstance(other, ProtoReservedRange):
            return False

        return self.min == other.min and self.max == other.max

    def __str__(self) -> str:
        return f"<ProtoReservedRange min={self.min} max={self.max}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        sign = ProtoIntSign.POSITIVE
        if proto_source.startswith("-") and proto_source != "-":
            sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
            match = ProtoInt.match(proto_source[1:])
        else:
            match = ProtoInt.match(proto_source)
        if match is None:
            return None

        match.node.sign = sign
        min = match.node
        proto_source = match.remaining_source

        max = None
        if proto_source.startswith("to "):
            proto_source = proto_source[3:]
            if proto_source.startswith("max"):
                return ParsedProtoNode(
                    ProtoReservedRange(min, ProtoReservedRangeEnum.MAX),
                    proto_source[3:].strip(),
                )
            else:
                sign = ProtoIntSign.POSITIVE
                if proto_source.startswith("-"):
                    sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
                    match = ProtoInt.match(proto_source[1:])
                else:
                    match = ProtoInt.match(proto_source)
                if match is None:
                    raise ValueError(
                        f"Proto source has invalid reserved range, expecting int for max: {proto_source}"
                    )
                match.node.sign = sign
                max = match.node
                proto_source = match.remaining_source

        return ParsedProtoNode(ProtoReservedRange(min, max), proto_source.strip())

    def serialize(self) -> str:
        if self.max is not None:
            if self.max == ProtoReservedRangeEnum.MAX:
                max = self.max.value
            else:
                max = self.max.serialize()

            return f"{self.min.serialize()} to {max}"
        else:
            return str(self.min.serialize())


class ProtoReserved(ProtoNode):
    def __init__(
        self,
        ranges: Optional[list[ProtoReservedRange]] = None,
        fields: Optional[list[ProtoIdentifier]] = None,
    ):
        if (not ranges and not fields) or (ranges and fields):
            raise ValueError(
                "Exactly one of ranges or fields must be set in a ProtoReserved"
            )

        if ranges is None:
            ranges = []

        if fields is None:
            fields = []

        self.ranges = ranges
        self.fields = fields

    def __eq__(self, other: "ProtoReserved") -> bool:
        if not isinstance(other, ProtoReserved):
            return False

        return self.ranges == other.ranges and self.fields == other.fields

    def __str__(self) -> str:
        return f"<ProtoReserved ranges={self.ranges} fields={self.fields}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def match(proto_source: str) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("reserved "):
            return None

        proto_source = proto_source[9:].strip()

        ranges = []
        fields = []
        while True:
            if proto_source[0] == ";":
                proto_source = proto_source[1:].strip()
                break
            if not proto_source:
                raise ValueError(
                    "Proto source has invalid reserved syntax, does not contain ;"
                )
            if proto_source[0] == ",":
                proto_source = proto_source[1:].strip()
            match = ProtoReservedRange.match(proto_source)
            if match is not None:
                ranges.append(match.node)
                proto_source = match.remaining_source
            else:
                # Maybe this is a field identifier.
                if not proto_source.startswith("'") and not proto_source.startswith(
                    '"'
                ):
                    raise ValueError(
                        f"Proto source has invalid reserved syntax, expecting quote for field identifier: {proto_source}"
                    )
                quote_type = proto_source[0]
                proto_source = proto_source[1:]
                match = ProtoIdentifier.match(proto_source)
                if match is None:
                    raise ValueError(
                        f"Proto source has invalid reserved syntax, expecting field identifier: {proto_source}"
                    )

                match.node.identifier = (
                    f"{quote_type}{match.node.identifier}{quote_type}"
                )

                fields.append(match.node)
                proto_source = match.remaining_source
                if not proto_source.startswith(quote_type):
                    raise ValueError(
                        f"Proto source has invalid reserved syntax, expecting closing quote {quote_type}: {proto_source}"
                    )
                proto_source = proto_source[1:].strip()

        return ParsedProtoNode(ProtoReserved(ranges, fields), proto_source.strip())

    def serialize(self) -> str:
        serialize_parts = [
            "reserved",
            ", ".join(r.serialize() for r in self.ranges)
            + ", ".join(f.serialize() for f in self.fields),
        ]
        return " ".join(serialize_parts) + ";"
