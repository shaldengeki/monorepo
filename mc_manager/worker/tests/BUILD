load("@py_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_test")

_RUNTIME_DEPS = [
    requirement("boto3"),
    requirement("docker"),
    requirement("requests"),
]

py_test(
    name = "tests",
    srcs = ["worker_test.py"],
    main = "worker_test.py",
    deps = [
        requirement("pytest"),
        requirement("pysocks"),
        "//worker:library",
    ] + _RUNTIME_DEPS,
)
