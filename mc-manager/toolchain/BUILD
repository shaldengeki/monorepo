load("@rules_python//python:defs.bzl", "py_runtime_pair")

py_runtime(
    name = "container_py2_runtime",
    interpreter_path = "/usr/local/bin/python",
    python_version = "PY2",
)

# Path in the python:slim-3.7 image
py_runtime(
    name = "container_py3_runtime",
    interpreter_path = "/usr/local/bin/python3",
    python_version = "PY3",
)

py_runtime_pair(
    name = "container_py_runtime_pair",
    py2_runtime = ":container_py2_runtime",
    py3_runtime = ":container_py3_runtime",
)

toolchain(
    name = "container_py_toolchain",
    exec_compatible_with = [
        "@io_bazel_rules_docker//platforms:run_in_container",
    ],
    toolchain = ":container_py_runtime_pair",
    toolchain_type = "@bazel_tools//tools/python:toolchain_type",
)

