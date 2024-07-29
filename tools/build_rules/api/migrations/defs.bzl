"""
defs.bzl

Contains the public interfaces for migrations rules.
"""

load("@rules_python//python:defs.bzl", "py_binary")
load("//tools/build_rules/api/migrations:migrations_files.bzl", "migrations_files")

def migrations(
        app_package,
        app_config,
        versions,
        name = "migrations",
        deps = []):
    migrations_files(
        name = name + "_files",
        app_package = app_package,
    )

    py_binary(
        name = "binary",
        srcs = versions + [":migrations_files"],
        data = [":" + name + "_files"],
        main = "__main__.py",
        visibility = ["//visibility:public"],
        deps = [
            app_config,
            "//base:flask_app_py",
            "@py_deps//alembic",
            "@py_deps//flask",
            "@py_deps//flask_migrate",
        ] + deps,
    )
