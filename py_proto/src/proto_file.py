from enum import Enum
from typing import Optional

class ParsedProtoNode:
    def __init__(self, parsed_node: 'ProtoNode', remaining_source: str):
        self.node = parsed_node
        self.remaining_source = remaining_source

class ProtoNode:
    @staticmethod
    def match(proto_source: str) -> Optional['ParsedProtoNode']:
        raise NotImplementedError

class ProtoSyntaxTypes(Enum):
    PROTO2 = 'proto2'
    PROTO3 = 'proto3'

class ProtoSyntax(ProtoNode):
    @staticmethod
    def match(proto_source: str) -> Optional['ParsedProtoNode']:
        if not proto_source.startswith('syntax = '):
            return None
        parts = proto_source.split(';')
        syntax_line = parts[0]
        proto_source = ';'.join(parts[1:])
        return ParsedProtoNode(
            ProtoSyntaxTypes[syntax_line.split("syntax = ")[1][1:-1].upper()],
            proto_source
        )

class ProtoImport:
    def __init__(self):
        pass

class ProtoOption:
    def __init__(self):
        pass

class ProtoEnum:
    def __init__(self):
        pass

class ProtoMessage:
    def __init__(self):
        pass

class ProtoService:
    def __init__(self):
        pass

SUPPORTED_NODES = [
    ProtoSyntax,
    ProtoImport,
    ProtoOption,
    ProtoEnum,
    ProtoMessage,
    ProtoService
]

class ProtoFile:
    def __init__(self, syntax: ProtoSyntax, imports: Optional[list[ProtoImport]] = None, options: Optional[list[ProtoOption]] = None, top_level_definitions: Optional[list[ProtoEnum | ProtoMessage | ProtoService]] = None):
        self.syntax = syntax

        if imports is None:
            self.imports = []
        else:
            self.imports = imports

        if options is None:
            self.options = []
        else:
            self.options = options

        if top_level_definitions is None:
            self.top_level_definitions = []
        else:
            self.top_level_definitions = top_level_definitions
