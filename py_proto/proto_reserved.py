from enum import Enum
from typing import Optional

from py_proto.proto_identifier import ProtoIdentifier
from py_proto.proto_node import ParsedProtoNode, ProtoNode
from py_proto.proto_range import ProtoRange


class ProtoReservedFieldQuoteEnum(Enum):
    SINGLE = "'"
    DOUBLE = '"'


class ProtoReserved(ProtoNode):
    def __init__(
        self,
        ranges: Optional[list[ProtoRange]] = None,
        fields: Optional[list[ProtoIdentifier]] = None,
        quote_type: Optional[
            ProtoReservedFieldQuoteEnum
        ] = ProtoReservedFieldQuoteEnum.DOUBLE,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if (not ranges and not fields) or (ranges and fields):
            raise ValueError(
                "Exactly one of ranges or fields must be set in a ProtoReserved"
            )

        if ranges is None:
            ranges = []
            if quote_type is None:
                raise ValueError("Quote type must be specified when reserving fields")

        self.ranges = ranges
        for range in self.ranges:
            range.parent = self

        if fields is None:
            fields = []

        self.fields = fields
        for field in self.fields:
            field.parent = self

        self.quote_type = quote_type

    def __eq__(self, other) -> bool:
        return self.ranges == other.ranges and self.fields == other.fields

    def __str__(self) -> str:
        return f"<ProtoReserved ranges={self.ranges} fields={self.fields}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoReserved":
        # sort the ranges.
        return ProtoReserved(
            parent=self.parent,
            ranges=sorted(self.ranges, key=lambda r: int(r.min)),
            fields=sorted(self.fields, key=lambda f: str(f)),
            quote_type=self.quote_type,
        )

    @property
    def min(self) -> str | int:
        if self.ranges:
            return int(min(self.ranges, key=lambda r: int(r.min)).min)
        else:
            return str(min(self.fields, key=lambda f: str(f)))

    @classmethod
    def match(
        cls, proto_source: str, parent: Optional[ProtoNode] = None
    ) -> Optional["ParsedProtoNode"]:
        if not proto_source.startswith("reserved "):
            return None

        proto_source = proto_source[9:].strip()

        ranges = []
        fields = []
        quote_type = None
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
            range_match = ProtoRange.match(proto_source)
            if range_match is not None:
                ranges.append(range_match.node)
                proto_source = range_match.remaining_source
            else:
                # Maybe this is a field identifier.
                quote_types = [
                    q
                    for q in ProtoReservedFieldQuoteEnum
                    if proto_source.startswith(q.value)
                ]
                if not quote_types:
                    raise ValueError(
                        f"Proto source has invalid reserved syntax, expecting quote for field identifier: {proto_source}"
                    )
                quote_type = quote_types[0]
                proto_source = proto_source[1:]
                match = ProtoIdentifier.match(proto_source)
                if match is None:
                    raise ValueError(
                        f"Proto source has invalid reserved syntax, expecting field identifier: {proto_source}"
                    )

                fields.append(match.node)
                proto_source = match.remaining_source
                if not proto_source.startswith(quote_type.value):
                    raise ValueError(
                        f"Proto source has invalid reserved syntax, expecting closing quote {quote_type.value}: {proto_source}"
                    )
                proto_source = proto_source[1:].strip()

        return ParsedProtoNode(
            ProtoReserved(
                ranges=ranges, fields=fields, quote_type=quote_type, parent=parent
            ),
            proto_source.strip(),
        )

    def serialize(self) -> str:
        serialize_parts = [
            "reserved",
            ", ".join(r.serialize() for r in self.ranges)
            + ", ".join(
                f"{self.quote_type.value}{f.serialize()}{self.quote_type.value}"
                for f in self.fields
                if self.quote_type is not None
            ),
        ]
        return " ".join(serialize_parts) + ";"
