import sys

from src.proto_file import ProtoFile


class ParseError(ValueError):
    pass


class Parser:
    @staticmethod
    def loads(proto_content: str) -> ProtoFile:
        try:
            parsed_file = ProtoFile.match(proto_content, None)
        except ValueError as e:
            raise ParseError(f"Proto doesn't have parseable syntax:\n{e}")
        if parsed_file is None:
            raise ParseError(f"Proto doesn't have parseable syntax:\n{proto_content}")

        assert isinstance(parsed_file.node, ProtoFile)
        return parsed_file.node


if __name__ == "__main__":
    with open(sys.argv[1], "r") as proto_file:
        parsed_proto = Parser.loads(proto_file.read())
    print(parsed_proto.serialize())
