workspace(
    name = "py_proto",
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
