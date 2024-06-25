load("@py_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary")
load("//tools/build_rules:cross_platform_image.bzl", "cross_platform_image")
load("//tools/build_rules:py_layer.bzl", "py_oci_image")

py_library(
    name = "config_py",
    srcs = ["config.py"],
    data = [
        requirement("pg8000"),
    ],
    visibility = ["//mc_manager:__subpackages__"],
    deps = [
        requirement("flask_cors"),
        requirement("flask_migrate"),
        requirement("flask_sqlalchemy"),
        requirement("pg8000"),
    ],
)

py_library(
    name = "api_lib",
    srcs = glob(["**/*.py"]),
    imports = [".."],
    visibility = ["//mc_manager/api:__subpackages__"],
    deps = [
        requirement("Flask"),
        requirement("flask-cors"),
        requirement("Flask-Migrate"),
        requirement("Flask-SQLAlchemy"),
        requirement("graphql-core"),
        requirement("graphql-server"),
        requirement("pg8000"),
        requirement("sqlalchemy"),
    ],
)

py_binary(
    name = "binary",
    srcs = ["__main__.py"],
    imports = [".."],
    main = "__main__.py",
    deps = [
        ":api_lib",
        "//scripts:wait_for_postgres",
    ],
)

py_oci_image(
    name = "base_image",
    base = "@python3_image",
    binary = ":binary",
    cmd = [
        "/mc_manager/api/binary.runfiles/_main/scripts/wait_for_postgres",
        "/mc_manager/api/binary",
    ],
    env = {
        "FLASK_APP": "app.py",
        "FLASK_DEBUG": "True",
        "API_PORT": "5000",
        "FRONTEND_PROTOCOL": "http",
        "FRONTEND_HOST": "frontend",
        "FRONTEND_PORT": "5001",
        "DB_HOST": "pg",
        "DB_USERNAME": "admin",
        "DB_PASSWORD": "development",
        "DATABASE_NAME": "api_development",
        "FITBIT_CLIENT_ID": "testing",
        "FITBIT_CLIENT_SECRET": "testing",
        "FITBIT_VERIFICATION_CODE": "testing",
        "FLASK_SECRET_KEY": "testing",
    },
    visibility = ["//mc_manager/api:__subpackages__"],
)

# $ bazel run //mc_manager/api:image_tarball
# $ docker run --rm shaldengeki/mc-manager-api:latest
cross_platform_image(
    name = "image",
    image = ":base_image",
    repo_tags = ["shaldengeki/mc-manager-api:latest"],
    repository = "docker.io/shaldengeki/mc-manager-api",
    visibility = ["//mc_manager/api:__subpackages__"],
)
