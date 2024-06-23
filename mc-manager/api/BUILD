load("@rules_python//python:defs.bzl", "py_binary")
load("@api_deps//:requirements.bzl", "requirement")
load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")

py_binary(
    name = "binary",
    srcs = glob(["**/*.py"]),
    main = "app.py",
    deps = [
        requirement("Flask"),
        requirement("Flask-Migrate"),
        requirement("psycopg2"),
        requirement("sqlalchemy"),
        requirement("Flask-SQLAlchemy"),
        requirement("graphql-core"),
        requirement("graphql-server"),
        requirement("flask-cors")
    ]
)

py3_image(
    name = "image",
    srcs = glob(["**/*.py"]),
    main = "app.py",
    base = "@py3_image//image",
    deps = [
        requirement("Flask"),
        requirement("Flask-Migrate"),
        requirement("psycopg2"),
        requirement("sqlalchemy"),
        requirement("Flask-SQLAlchemy"),
        requirement("graphql-core"),
        requirement("graphql-server"),
        requirement("flask-cors")
    ]
)
