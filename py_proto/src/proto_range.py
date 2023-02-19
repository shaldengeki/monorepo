from enum import Enum
from typing import Optional

from src.proto_int import ProtoInt, ProtoIntSign
from src.proto_node import ParsedProtoNode, ProtoNode


class ParsedProtoRangeNode(ParsedProtoNode):
    node: "ProtoRange"
    remaining_source: str


class ProtoRangeEnum(Enum):
    MAX = "max"


class ProtoRange(ProtoNode):
    def __init__(
        self,
        parent: Optional[ProtoNode],
        min: ProtoInt,
        max: Optional[ProtoInt | ProtoRangeEnum] = None,
    ):
        super().__init__(parent)
        self.min = min

        if (
            max is not None
            and not isinstance(max, ProtoRangeEnum)
            and int(min) > int(max)
        ):
            raise ValueError(f"min {min} was greater than max {max} in ProtoRange")

        self.max = max

    def __eq__(self, other) -> bool:
        return self.min == other.min and self.max == other.max

    def __str__(self) -> str:
        return f"<ProtoRange min={self.min} max={self.max}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoRange":
        return self

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoRangeNode"]:
        sign = ProtoIntSign.POSITIVE
        if proto_source.startswith("-") and proto_source != "-":
            sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
            match = ProtoInt.match(None, proto_source[1:])
        else:
            match = ProtoInt.match(None, proto_source)
        if match is None:
            return None

        match.node.sign = sign
        min = match.node
        proto_source = match.remaining_source

        max = None
        if proto_source.startswith("to "):
            proto_source = proto_source[3:]
            if proto_source.startswith("max"):
                proto_range = ProtoRange(parent, min, ProtoRangeEnum.MAX)
                min.parent = proto_range
                return ParsedProtoRangeNode(
                    proto_range,
                    proto_source[3:].strip(),
                )
            else:
                sign = ProtoIntSign.POSITIVE
                if proto_source.startswith("-"):
                    sign = next(x for x in ProtoIntSign if x.value == proto_source[0])
                    match = ProtoInt.match(None, proto_source[1:])
                else:
                    match = ProtoInt.match(None, proto_source)
                if match is None:
                    raise ValueError(
                        f"Proto source has invalid range, expecting int for max: {proto_source}"
                    )
                match.node.sign = sign
                max = match.node
                proto_source = match.remaining_source

        proto_range = ProtoRange(parent, min, max)
        min.parent = proto_range
        if isinstance(max, ProtoNode):
            max.parent = proto_range
        return ParsedProtoRangeNode(proto_range, proto_source.strip())

    def serialize(self) -> str:
        if self.max is not None:
            if isinstance(self.max, ProtoRangeEnum):
                max = self.max.value
            else:
                max = self.max.serialize()

            return f"{self.min.serialize()} to {max}"
        else:
            return str(self.min.serialize())
