workspace(
    name = "py_proto",
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    sha256 = "a868059c8c6dd6ad45a205cca04084c652cfe1852e6df2d5aca036f6e5438380",
    strip_prefix = "rules_python-0.14.0",
    url = "https://github.com/bazelbuild/rules_python/archive/refs/tags/0.14.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "python_register_toolchains")

python_register_toolchains(
    name = "python3_10",
    # Available versions are listed in @rules_python//python:versions.bzl.
    # We recommend using the same version your team is already standardized on.
    python_version = "3.10.6",
)

load("@python3_10//:defs.bzl", "interpreter")
load("@rules_python//python:pip.bzl", "pip_parse")

pip_parse(
    name = "py_proto_deps",
    python_interpreter_target = interpreter,
    requirements_lock = "//src:requirements.txt",
)

http_archive(
    name = "bazel_skylib",
    sha256 = "97e70364e9249702246c0e9444bccdc4b847bed1eb03c5a3ece4f83dfe6abc44",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/bazel-skylib/releases/download/1.0.2/bazel-skylib-1.0.2.tar.gz",
        "https://github.com/bazelbuild/bazel-skylib/releases/download/1.0.2/bazel-skylib-1.0.2.tar.gz",
    ],
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "com_google_protobuf",
    build_file_content = """
exports_files(
   glob(["src/google/protobuf/**/*.proto"]),
    visibility = ["//visibility:public"],
)

filegroup(
    name = "all_proto",
    srcs = glob(["src/google/protobuf/**/*.proto"]),
    visibility = ["//visibility:public"],
)
""",
    sha256 = "2c6a36c7b5a55accae063667ef3c55f2642e67476d96d355ff0acb13dbb47f09",
    strip_prefix = "protobuf-21.12",
    url = "https://github.com/protocolbuffers/protobuf/releases/download/v21.12/protobuf-all-21.12.tar.gz",
)
