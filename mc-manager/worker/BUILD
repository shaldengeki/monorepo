load("@rules_python//python:defs.bzl", "py_binary")
load("@worker_deps//:requirements.bzl", "requirement")
load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")

py_binary(
    name = "binary",
    srcs = ["worker.py"],
    main = "worker.py",
    deps = [
        requirement("boto3"),
        requirement("docker"),
        requirement("requests")
    ]
)

py3_image(
    name = "image",
    srcs = glob(["**/*.py"]),
    main = "worker.py",
    base = "@py3_image//image",
    deps = [
        requirement("boto3"),
        requirement("docker"),
        requirement("requests")
    ]
)
