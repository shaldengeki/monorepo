"""

worker.bzl: Defines the standard worker application used across the monorepo.

"""

load("@rules_img//img:image.bzl", "image_from_binary")
load("@rules_img//img:load.bzl", "image_load")
load("@rules_img//img:push.bzl", "image_push")
load("@rules_python//python:defs.bzl", "py_binary")

def worker(
        name,
        repository,
        tag,
        registry = "ghcr.io",
        base = "@python3_image",
        env = None,
        visibility = None,
        tags = None,
        deps = None):
    """
    Defines the standard worker application, including container images.

    Args:
        name (str): Name to use as a prefix to generated rules.
        repository (str): Repository on Docker Hub that the container images should be pushed to.
        tag (str): Tag that the container images should be loaded under.
        registry (str): Container image registry to push to. Defaults to ghcr.io.
        base (label): Base container image to use.
        env (dict[str, str]): Additional environment variables to set in the Python image.
        visibility: The default visibility to set on the generated rules. Defaults to public.
        tags (list[str]): List of tags to apply to targets.
        deps (list[label]): List of dependencies for the binary.
    """

    if env == None:
        env = {}

    all_env = {
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
    all_env.update(env)

    if visibility == None:
        visibility = ["//visibility:public"]

    if tags == None:
        tags = ["manual"]

    py_binary(
        name = name + "_binary",
        srcs = [
            "__init__.py",
            "app.py",
        ],
        imports = [".."],
        main = "app.py",
        visibility = visibility,
        deps = deps,
        env = all_env,
        tags = tags,
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
