"""
cross_platform_image.bzl

A macro used to define a cross-platform container image.
"""

load("@aspect_bazel_lib//lib:transitions.bzl", "platform_transition_filegroup")
load("@rules_oci//oci:defs.bzl", "oci_load", "oci_push")

def cross_platform_image(
        name,
        image,
        repository,
        repo_tags,
        stamp_file = "//:stamped",
        visibility = None,
        tags = None):
    """
    Defines a cross-platform container image, usable on both arm64 and x86_64.

    Args:
        name (str): Name of rule to generate.
        image (label): Base image to build across archs.
        repository (str): Repository on Docker Hub that the container images should be pushed to.
        repo_tags (list[str]): List of repo + tag pairs that the container images should be loaded under.
        stamp_file (file): File containing image tags that the image should be pushed under.
        visibility (list[str]): Visibility to set on all the targets.
        tags (dict): Tags to pass to the underlying rules.
    """
    if visibility == None:
        visibility = ["//visibility:public"]

    if tags == None:
        tags = []
    if "manual" not in tags:
        tags.append("manual")

    platform_transition_filegroup(
        name = name,
        srcs = [image],
        target_platform = select({
            "@platforms//cpu:arm64": "//tools/build_rules:linux_arm64",
            "@platforms//cpu:x86_64": "//tools/build_rules:linux_amd64",
        }),
        tags = tags,
        visibility = visibility,
    )

    oci_load(
        name = name + "_tarball",
        image = name,
        repo_tags = repo_tags,
        visibility = visibility,
        tags = tags,
    )

    oci_push(
        name = name + "_dockerhub",
        image = name,
        remote_tags = stamp_file,
        repository = repository,
        visibility = visibility,
        tags = tags,
    )
