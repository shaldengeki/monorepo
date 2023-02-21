# py_proto

This is a Python-based protobuf parser. It is intended to serve as a reference implementation and is _not_ production-ready.

![Build status](https://github.com/shaldengeki/py_proto/actions/workflows/main.yml/badge.svg)

## Usage

Right now, the primary way to use this as a library in your Bazelified Python code.

Mount this repo in your Bazel workspace, then add `@py_proto//src/util:parser` as a dependency:
```
py_library(
    name = "your_python_code",
    # ...
    deps = [
        "@py_proto//src/util:parser",
    ]
)
```

Then, in your Python code, use the parser:
```python
from src.util.parser import ParseError, Parser
with open("your.proto", "r") as proto_file:
    parsed_proto = Parser.loads(proto_file.read())

print(parsed_proto.syntax)
```

## Development

We support building & running via Bazel. See the `TODO.md` for what's on the roadmap.

### Bazel

Do `bazel test //...`.
