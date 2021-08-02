load("@rules_python//python:defs.bzl", "py_test")
load("@worker_deps//:requirements.bzl", "requirement")

_RUNTIME_DEPS = [
    requirement("boto3"),
    requirement("docker"),
    requirement("requests")
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
