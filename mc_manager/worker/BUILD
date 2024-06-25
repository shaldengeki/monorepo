load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")
load("@py_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary")

_RUNTIME_DEPS = [
    requirement("boto3"),
    requirement("docker"),
    requirement("requests"),
]

py_library(
    name = "library",
    srcs = ["worker.py"],
    visibility = ["//visibility:public"],
)

py_binary(
    name = "binary",
    srcs = ["worker.py"],
    main = "worker.py",
    deps = _RUNTIME_DEPS,
)

py3_image(
    name = "image",
    srcs = glob(["**/*.py"]),
    base = "@py3_image//image",
    main = "worker.py",
    deps = _RUNTIME_DEPS,
)
