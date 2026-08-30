"""
grpc_api_image.bzl

A macro used to define a GRPC API container image.
"""

load("@rules_img//img:image.bzl", "image_from_binary")
load("@rules_img//img:load.bzl", "image_load")
load("@rules_img//img:push.bzl", "image_push")

def grpc_api_image(
        name,
        binary,
        repository,
        tag,
        registry = "ghcr.io",
        additional_srcs = None,
        base = "@ubuntu_image",
        visibility = None,
        tags = None):
    """
    Defines a cross-platform GRPC API container image, usable on both arm64 and x86_64.

    Args:
        name (str): Name of rule to generate.
        binary (label): Binary that should be invoked by the container.
        repository (str): Repository on Docker Hub that the container images should be pushed to.
        tag (str): List of repo + tag pairs that the container images should be loaded under.
        registry (str): Container image registry to push to. Defaults to ghcr.io.
        additional_srcs (list[label]): Additional source files to bundle with the binary.
        base (label): Base image to build off of.
        visibility (list[str]): Visibility to set on all the targets. Defaults to public.
        tags (dict): Tags to pass to the underlying rules.
    """

    if visibility == None:
        visibility = ["//visibility:public"]

    binary = Label(binary)

    if additional_srcs == None:
        additional_srcs = []

    if tags == None:
        tags = []
    if "manual" not in tags:
        tags.append("manual")

    image_from_binary(
        name = name,
        base = base,
        binary = binary,
        tags = tags,
        platforms = [
            "//tools/build_rules:linux_arm64",
            "//tools/build_rules:linux_amd64",
        ],
    )

    image_push(
        name = name + "_push",
        image = name,
        registry = registry,
        repository = repository,
        tag = tag,
    )

    image_load(
        name = name + "_pull",
        image = name,
        registry = registry,
        repository = repository,
        tag = tag,
    )
