from enum import Enum
from typing import Optional

from src.proto_identifier import ProtoFullIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoIntSign(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"


class ParsedProtoIntNode(ParsedProtoNode):
    node: "ProtoInt"
    remaining_source: str


class ProtoInt(ProtoNode):
    OCTAL = set("01234567")
    DECIMAL = OCTAL | set("89")
    HEX = DECIMAL | set("ABCDEFabcdef")

    def __init__(self, parent: Optional[ProtoNode], value: int, sign: ProtoIntSign):
        super().__init__(parent)
        self.value = value
        self.sign = sign

    def __int__(self) -> int:
        if self.sign == ProtoIntSign.NEGATIVE:
            return self.value * -1
        else:
            return self.value

    def __eq__(self, other) -> bool:
        return int(self) == int(other)

    def __str__(self) -> str:
        return f"<ProtoInt value={self.value} sign={self.sign}>"

    def __repr__(self) -> str:
        return str(self)

    def normalize(self) -> "ProtoInt":
        return self

    @classmethod
    def match(
        cls, parent: Optional[ProtoNode], proto_source: str
    ) -> Optional["ParsedProtoIntNode"]:
        if proto_source[0] not in ProtoInt.DECIMAL:
            return None

        if proto_source != "0" and proto_source.startswith("0"):
            # Octal or hex.
            proto_source = proto_source[1:]
            if proto_source.startswith("x") or proto_source.startswith("X"):
                # Hex.
                proto_source = proto_source[1:]
                for i, c in enumerate(proto_source):
                    if c not in ProtoInt.HEX:
                        if c in ProtoFullIdentifier.ALL:
                            raise ValueError(f"Proto has invalid hex: {proto_source}")
                        i -= 1
                        break
                try:
                    value = int(f"0x{proto_source[:i + 1]}", 16)
                except ValueError:
                    raise ValueError(f"Proto has invalid hex: {proto_source}")
                return ParsedProtoIntNode(
                    ProtoInt(parent, value, ProtoIntSign.POSITIVE),
                    proto_source[i + 1 :].strip(),
                )
            else:
                # Octal.
                for i, c in enumerate(proto_source):
                    if c not in ProtoInt.OCTAL:
                        if c in ProtoFullIdentifier.ALL:
                            raise ValueError(f"Proto has invalid octal: {proto_source}")
                        i -= 1
                        break
                try:
                    value = int(f"0{proto_source[:i + 1]}", 8)
                except ValueError:
                    raise ValueError(f"Proto has invalid octal: {proto_source}")
                return ParsedProtoIntNode(
                    ProtoInt(parent, value, ProtoIntSign.POSITIVE),
                    proto_source[i + 1 :].strip(),
                )
        else:
            # Decimal.
            for i, c in enumerate(proto_source):
                if c not in ProtoInt.DECIMAL | set("."):
                    if c in ProtoFullIdentifier.ALL:
                        return None
                    i -= 1
                    break
            try:
                value = int(proto_source[: i + 1])
            except ValueError:
                return None

            return ParsedProtoIntNode(
                ProtoInt(parent, value, ProtoIntSign.POSITIVE),
                proto_source[i + 1 :].strip(),
            )

    def serialize(self) -> str:
        if self.sign == ProtoIntSign.NEGATIVE:
            return f"-{self.value}"

        return str(self.value)
