"""

worker.bzl: Defines the standard worker application used across the monorepo.

"""

load("//tools/build_rules:cross_platform_image.bzl", "cross_platform_image")
load("//tools/build_rules:py_layer.bzl", "py_oci_image")

def worker(
        name,
        binary,
        repo_tags,
        docker_hub_repository,
        env = None,
        visibility = None):
    """
    Defines the standard worker application, including container images.

    Args:
        name (str): Name to use as a prefix to generated rules.
        binary (Label): py_binary target that should be the entrypoint of the worker.
        repo_tags (list[str]): List of tags to apply to the container. See cross_platform_image.
        docker_hub_repository (str): URL of the dockerhub repository to push to. See cross_platform_image.
        env (dict[str, str]): Additional environment variables to set in the Python image. See py_oci_image.
        visibility: The default visibility to set on the generated rules. Defaults to public.
    """

    binary = Label(binary)

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

    py_oci_image(
        name = name + "_base_image",
        base = "@python3_image",
        binaries = [
            "//scripts:wait_for_postgres",
            binary,
        ],
        cmd = [
            "/" + binary.package + "/" + binary.name,
        ],
        entrypoint = [
            "/scripts/wait_for_postgres",
        ],
        env = all_env,
        visibility = visibility,
        tags = ["manual"],
    )

    # $ bazel run //skeleton/worker:worker_image_tarball
    # $ docker run --rm shaldengeki/skeleton-worker:latest
    cross_platform_image(
        name = name + "_image",
        image = ":" + name + "_base_image",
        repo_tags = repo_tags,
        repository = docker_hub_repository,
        visibility = visibility,
    )
