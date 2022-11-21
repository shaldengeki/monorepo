from src.proto_file import ProtoFile, ProtoSyntax

class Parser:
    @staticmethod
    def loads(proto_content: str):
        parts = proto_content.split(';')
        syntax_line = parts[0]
        proto_content = ';'.join(parts[1:])
        syntax = ProtoSyntax[syntax_line.split("syntax = ")[1][1:-1].upper()]
        return ProtoFile(syntax)