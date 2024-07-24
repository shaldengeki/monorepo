"""
api_image.bzl

A macro used to define an API container image.
"""

load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("//tools/build_rules:cross_platform_image.bzl", "cross_platform_image")
load("//tools/build_rules:py_layer.bzl", "py_oci_image")
load("//tools/build_rules/api_image:api_main_py.bzl", "api_main_py")
load("//tools/build_rules/api_image/migrations:alembic_ini.bzl", "alembic_ini")
load("//tools/build_rules/api_image/migrations:env_py.bzl", "env_py")
load("//tools/build_rules/api_image/migrations:migrations_main_py.bzl", "migrations_main_py")

def api_image(
        name,
        app_package,
        deps,
        repo_tags,
        docker_hub_repository,
        config,
        migration_binary = None,
        migrations = False,
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
        config (label): Label (py_library) of the Flask configuration object.
        migration_binary (label): Binary target for this API's database migrations. Defaults to //your/api/package/migrations:binary.
        stamp_file (file): File containing image tags that the image should be pushed under.
        base_image (label): Base container image to use.
        migrations (bool): Whether to generate migration targets.
        visibility (list[str]): Visibility to set on all the targets.
    """

    if visibility == None:
        visibility = ["//visibility:public"]

    if migration_binary == None:
        migration_binary = Label("//" + native.package_name() + "/migrations:binary")

    api_main_py(
        name = name + "_api_main_py",
        app_package = app_package,
    )

    py_binary(
        name = name + "_binary",
        srcs = [name + "_api_main_py"],
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

    if migrations:
        migrations_main_py(
            name = name + "_migrations_main_py",
            app_package = app_package,
            api_package_path = native.package_name(),
        )

        alembic_ini(
            name = name + "_migrations_alembic_ini",
        )

        env_py(
            name = name + "_migrations_env_py",
        )

        py_library(
            name = name + "_migrations_lib",
            srcs = native.glob(["migrations/**/*.py"]) + [
                name + "_migrations_env_py",
            ],
            imports = ["."],
            visibility = [":__subpackages__"],
            deps = [
                "//base:flask_app_py",
                "@py_deps//alembic",
                "@py_deps//flask",
            ],
        )

        py_binary(
            name = name + "_migrations_binary",
            srcs = native.glob(["migrations/**/*.py"]) + [
                name + "_migrations_env_py",
            ],
            data = [name + "_migrations_alembic_ini"],
            imports = ["."],
            main = name + "_migrations_main_py",
            visibility = [":__subpackages__"],
            deps = [
                config,
                "//scripts:wait_for_postgres",
                "@py_deps//flask_migrate",
            ],
        )
