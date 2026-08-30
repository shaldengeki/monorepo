"""
graphql_api_image.bzl

A macro used to define a GraphQL API container image.
"""

load("@rules_img//img:image.bzl", "image_from_binary")
load("@rules_img//img:load.bzl", "image_load")
load("@rules_img//img:push.bzl", "image_push")
load("@rules_python//python:defs.bzl", "py_binary")
load("//tools/build_rules/api:main_py.bzl", "main_py")

def graphql_api_image(
        name,
        app_package,
        deps,
        repository,
        tag,
        registry = "ghcr.io",
        migration_binary = None,
        env = None,
        base = "@python3_image",
        visibility = None,
        tags = None):
    """
    Defines a set of GraphQL API images for our application.

    Args:
        name (str): Prefix to append to the generated targets.
        app_package(str): Python package containing the "app" entrypoint. Should be a Flask.
        deps (list[label]): List of py_library dependencies to bundle with the app.
        repository (str): Repository on Docker Hub that the container images should be pushed to.
        tag (str): Tag that the container images should be loaded under.
        registry (str): Container image registry to push to. Defaults to ghcr.io.
        env (dict[str, str]): Environment variables to set in the image.
        migration_binary (label): Binary target for this API's database migrations. Defaults to //your/api/package/migrations:binary.
        base (label): Base container image to use.
        visibility (list[str]): Visibility to set on all the targets.
        tags (list[str]): List of tags to apply to targets.
    """

    if visibility == None:
        visibility = ["//visibility:public"]

    if migration_binary == None:
        migration_binary = Label("//" + native.package_name() + "/migrations:binary")

    main_py(
        name = name + "_main_py",
        app_package = app_package,
    )

    if env == None:
        env = {}

    container_env = {
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
        "FLASK_SECRET_KEY": "testing",
        "API_WORKER_SECRET": "test-api-worker-secret",
    }
    container_env.update(env)

    py_binary(
        name = name + "_binary",
        srcs = [name + "_main_py"],
        imports = [".."],
        main = "__main__.py",
        data = [
            "//scripts:wait_for_postgres",
        ],
        deps = deps + [
            "@rules_python//python/runfiles",
        ],
        tags = ["manual"],
        env = container_env,
        visibility = visibility,
    )

    image_from_binary(
        name = name,
        base = base,
        binary = name + "_binary",
        tags = tags,
        platforms = [
            "//tools/build_rules:linux_arm64",
            "//tools/build_rules:linux_amd64",
        ],
        visibility = visibility,
    )

    image_push(
        name = name + "_push",
        image = name,
        registry = registry,
        repository = repository,
        tag = tag,
        tags = tags,
        visibility = visibility,
    )

    image_load(
        name = name + "_pull",
        image = name,
        registry = registry,
        repository = repository,
        tag = tag,
        tags = tags,
        visibility = visibility,
    )
