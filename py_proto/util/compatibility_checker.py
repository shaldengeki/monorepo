import sys
from dataclasses import dataclass
from typing import Type

from py_proto.proto_file import ProtoFile
from py_proto.proto_message import ProtoMessageAdded
from py_proto.proto_node import ProtoNodeDiff
from py_proto.util.parser import Parser


@dataclass
class CompatibilityChecker:
    allowed_diff_types: list[Type[ProtoNodeDiff]]

    def check_compatibility(self, before: ProtoFile, after: ProtoFile):
        for diff in before.diff(after):
            if diff.__class__ in self.allowed_diff_types:
                continue
            yield diff


def main() -> int:
    with open(sys.argv[1], "r") as proto_file:
        before = Parser.loads(proto_file.read())

    with open(sys.argv[2], "r") as proto_file:
        after = Parser.loads(proto_file.read())

    violations = list(
        CompatibilityChecker([ProtoMessageAdded]).check_compatibility(before, after)
    )
    if violations:
        print(f"Violations: {violations}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
