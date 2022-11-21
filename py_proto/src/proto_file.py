from enum import Enum
from typing import Optional

class ProtoSyntax(Enum):
    PROTO2 = 'proto2'
    PROTO3 = 'proto3'

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
