import sys

from src.proto_enum import ProtoEnum
from src.proto_file import ProtoFile
from src.proto_import import ProtoImport
from src.proto_message import ProtoMessage
from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_option import ProtoOption
from src.proto_package import ProtoPackage
from src.proto_syntax import ProtoSyntax


class ParseError(ValueError):
    pass


class Parser:
    @staticmethod
    def parse_partial_content(partial_proto_content: str) -> ParsedProtoNode:
        node_types = [
            ProtoImport,
            ProtoMessage,
            ProtoPackage,
            ProtoOption,
            ProtoEnum,
        ] # type: list[type[ProtoImport] | type[ProtoMessage] | type[ProtoPackage] | type[ProtoOption] | type[ProtoEnum]]
        for node_type in node_types:
            try:
                match_result = node_type.match(partial_proto_content)
            except (ValueError, IndexError, TypeError):
                raise ParseError(
                    f"Could not parse proto content:\n{partial_proto_content}"
                )
            if match_result is not None:
                return match_result
        raise ParseError(f"Could not parse proto content:\n{partial_proto_content}")

    @staticmethod
    def loads(proto_content: str) -> ProtoFile:
        # First, parse syntax out of the first line.
        try:
            match_result = ProtoSyntax.match(proto_content.strip())
        except (ValueError, IndexError, TypeError):
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        if match_result is None:
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        syntax = match_result.node
        proto_content = match_result.remaining_source.strip()

        # Next, parse the rest.
        parsed_tree = []
        while proto_content:
            # Remove empty statements.
            if proto_content.startswith(";"):
                proto_content = proto_content[1:].strip()
                continue
            match_result = Parser.parse_partial_content(proto_content)
            parsed_tree.append(match_result.node)
            proto_content = match_result.remaining_source.strip()

        return ProtoFile(syntax, parsed_tree)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as proto_file:
        parsed_proto = Parser.loads(proto_file.read())
    print(parsed_proto.serialize())
