from src.proto_file import ProtoFile
from src.proto_import import ProtoImport
from src.proto_node import ParsedProtoNode
from src.proto_package import ProtoPackage
from src.proto_syntax import ProtoSyntax


class ParseError(ValueError):
    pass


class Parser:
    @staticmethod
    def parse_partial_content(partial_proto_content: str) -> ParsedProtoNode:
        for node_type in (
            ProtoImport,
            ProtoPackage,
        ):
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
        parsed_tree = []

        # First, parse syntax out of the first line.
        try:
            match_result = ProtoSyntax.match(proto_content)
        except (ValueError, IndexError, TypeError):
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        if match_result is None:
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")
        parsed_tree.append(match_result.node)
        proto_content = match_result.remaining_source

        # Next, parse the rest.
        while proto_content:
            match_result = Parser.parse_partial_content(proto_content)
            parsed_tree.append(match_result.node)
            proto_content = match_result.remaining_source

        return ProtoFile(parsed_tree[0], parsed_tree[1:])
