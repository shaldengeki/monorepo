from enum import Enum
from typing import Optional

from src.proto_identifier import ProtoFullIdentifier
from src.proto_node import ParsedProtoNode, ProtoNode


class ProtoIntSign(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"


class ProtoInt(ProtoNode):
    OCTAL = set("01234567")
    DECIMAL = OCTAL | set("89")
    HEX = DECIMAL | set("ABCDEFabcdef")

    def __init__(self, value: int, sign: ProtoIntSign):
        self.value = value
        self.sign = sign

    def __eq__(self, other: "ProtoInt") -> bool:
        if not isinstance(other, ProtoInt):
            return False

        return self.value == other.value and self.sign == other.sign

    def __str__(self) -> str:
        return f"<ProtoInt value={self.value} sign={self.sign}>"

    def __repr__(self) -> str:
        return str(self)

    def __int__(self):
        value = self.value
        if self.sign == ProtoIntSign.NEGATIVE:
            value *= -1
        return value

    @classmethod
    def match(cls, proto_source: str) -> Optional["ParsedProtoNode"]:
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
                return ParsedProtoNode(
                    ProtoInt(value, ProtoIntSign.POSITIVE),
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
                return ParsedProtoNode(
                    ProtoInt(value, ProtoIntSign.POSITIVE),
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

            return ParsedProtoNode(
                ProtoInt(value, ProtoIntSign.POSITIVE),
                proto_source[i + 1 :].strip(),
            )

    def serialize(self) -> str:
        if self.sign == ProtoIntSign.NEGATIVE:
            return f"-{self.value}"

        return str(self.value)
