"""
grpc_api_image.bzl

A macro used to define a GRPC API container image.
"""

load("@aspect_bazel_lib//lib:tar.bzl", "tar")
load("@rules_oci//oci:defs.bzl", "oci_image")
load("//tools/build_rules:cross_platform_image.bzl", "cross_platform_image")

def grpc_api_image(
        name,
        binary,
        repository,
        repo_tags,
        stamp_file = "//:stamped",
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
        repo_tags (list[str]): List of repo + tag pairs that the container images should be loaded under.
        stamp_file (file): File containing image tags that the image should be pushed under.
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

    tar(
        name = name + "_grpc_tar",
        srcs = [binary] + additional_srcs,
        tags = tags,
    )

    oci_image(
        name = name + "_grpc_base",
        base = base,
        cmd = [binary.package + "/" + binary.name + "_/" + binary.name],
        tars = [":" + name + "_grpc_tar"],
        tags = tags,
    )

    cross_platform_image(
        name = name + "_grpc",
        image = name + "_grpc_base",
        repo_tags = repo_tags,
        repository = repository,
        stamp_file = stamp_file,
        visibility = visibility,
    )
