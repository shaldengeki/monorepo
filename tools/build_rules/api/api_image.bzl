"""
api_image.bzl

A macro used to define an API container image.
"""

load("@rules_python//python:defs.bzl", "py_binary")
load("//tools/build_rules:cross_platform_image.bzl", "cross_platform_image")
load("//tools/build_rules:py_layer.bzl", "py_oci_image")
load("//tools/build_rules/api:main_py.bzl", "main_py")

def api_image(
        name,
        app_package,
        deps,
        repo_tags,
        docker_hub_repository,
        migration_binary = None,
        env = None,
        stamp_file = "//:stamped",
        base_image = "@python3_image",
        visibility = None):
    """
    Defines a set of API images for our application.

    Args:
        name (str): Prefix to append to the generated targets.
        app_package(str): Python package containing the "app" entrypoint. Should be a Flask.
        deps (list[label]): List of py_library dependencies to bundle with the app.
        env (dict[str, str]): Environment variables to set in the image.
        repo_tags (list[str]): List of repo + tag pairs that the container images should be loaded under.
        docker_hub_repository (str): Repository on Docker Hub that the container images should be pushed to.
        migration_binary (label): Binary target for this API's database migrations. Defaults to //your/api/package/migrations:binary.
        stamp_file (file): File containing image tags that the image should be pushed under.
        base_image (label): Base container image to use.
        visibility (list[str]): Visibility to set on all the targets.
    """

    if visibility == None:
        visibility = ["//visibility:public"]

    if migration_binary == None:
        migration_binary = Label("//" + native.package_name() + "/migrations:binary")

    main_py(
        name = name + "_main_py",
        app_package = app_package,
    )

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

    py_oci_image(
        name = name + "_base_image",
        base = base_image,
        binaries = [
            "//scripts:wait_for_postgres",
            name + "_binary",
            migration_binary,
        ],
        entrypoint = [
            "/scripts/wait_for_postgres",
        ],
        cmd = [
            "/" + native.package_name() + "/" + name + "_binary",
        ],
        env = container_env,
        visibility = visibility,
        tags = ["manual"],
    )

    cross_platform_image(
        name = name + "_image",
        image = name + "_base_image",
        repo_tags = repo_tags,
        repository = docker_hub_repository,
        stamp_file = stamp_file,
        visibility = visibility,
    )
