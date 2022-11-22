from src.proto_file import ProtoFile, ParsedProtoNode, SUPPORTED_NODES

class ParseError(ValueError):
    pass

class Parser:
    @staticmethod
    def parse_partial_content(partial_proto_content: str) -> ParsedProtoNode:
        for node_type in SUPPORTED_NODES:
            match_result = node_type.match(partial_proto_content)
            if match_result is not None:
                return match_result
        raise ParseError(f"Could not parse proto content:\n{partial_proto_content}")


    @staticmethod
    def loads(proto_content: str) -> ProtoFile:
        parsed_tree = []
        while proto_content:
            match_result = Parser.parse_partial_content(proto_content)
            parsed_tree.append(match_result.node)
            proto_content = match_result.remaining_source

        return ProtoFile(parsed_tree[0])