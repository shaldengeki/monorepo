import sys
from typing import Sequence

from src.proto_comment import (
    ProtoComment,
    ProtoMultiLineComment,
    ProtoSingleLineComment,
)
from src.proto_enum import ProtoEnum
from src.proto_extend import ProtoExtend
from src.proto_file import ProtoFile
from src.proto_import import ProtoImport
from src.proto_message import ProtoMessage
from src.proto_node import ParsedProtoNode, ProtoNode
from src.proto_option import ProtoOption
from src.proto_package import ProtoPackage
from src.proto_service import ProtoService
from src.proto_syntax import ProtoSyntax


class ParseError(ValueError):
    pass


class Parser:
    @staticmethod
    def parse_partial_content(partial_proto_content: str) -> ParsedProtoNode:
        node_types: list[type[ProtoNode]] = [
            ProtoImport,
            ProtoMessage,
            ProtoPackage,
            ProtoOption,
            ProtoEnum,
            ProtoExtend,
            ProtoService,
            ProtoSingleLineComment,
            ProtoMultiLineComment,
        ]
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
    def parse_syntax_and_preceding_comments(
        proto_content: str,
    ) -> tuple[ProtoSyntax, Sequence[ProtoComment], str]:
        # First, parse any preceding comments.
        parsed_tree = []
        while True:
            for node_type in [ProtoSingleLineComment, ProtoMultiLineComment]:
                try:
                    match_result = node_type.match(proto_content)
                except (ValueError, IndexError, TypeError):
                    raise ParseError(f"Could not parse proto content:\n{proto_content}")
                if match_result is not None:
                    parsed_tree.append(match_result.node)
                    proto_content = match_result.remaining_source.strip()
                    break
            if match_result is None:
                break

        # Next, parse syntax.
        try:
            syntax_match = ProtoSyntax.match(proto_content.strip())
        except (ValueError, IndexError, TypeError):
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        if syntax_match is None:
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        syntax = syntax_match.node
        proto_content = syntax_match.remaining_source.strip()

        return syntax, parsed_tree, proto_content

    @staticmethod
    def loads(proto_content: str) -> ProtoFile:
        syntax, parsed_tree, proto_content = Parser.parse_syntax_and_preceding_comments(
            proto_content
        )
        new_tree: list[ProtoNode] = list(parsed_tree)
        while proto_content:
            # Remove empty statements.
            if proto_content.startswith(";"):
                proto_content = proto_content[1:].strip()
                continue
            match_result = Parser.parse_partial_content(proto_content)
            new_tree.append(match_result.node)
            proto_content = match_result.remaining_source.strip()

        return ProtoFile(syntax, new_tree)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as proto_file:
        parsed_proto = Parser.loads(proto_file.read())
    print(parsed_proto.serialize())
