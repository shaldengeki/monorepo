"""
cross_platform_image.bzl

A macro used to define a cross-platform container image.
"""

load("@aspect_bazel_lib//lib:transitions.bzl", "platform_transition_filegroup")
load("@rules_oci//oci:defs.bzl", "oci_push", "oci_tarball")

def cross_platform_image(
        name,
        image,
        repository,
        repo_tags,
        stamp_file = "//:stamped",
        visibility = None):
    """
    Defines a cross-platform container image, usable on both arm64 and x86_64.

    Args:
        name (str): Name of rule to generate.
        image (label): Base image to build across archs.
        repository (str): Repository on Docker Hub that the container images should be pushed to.
        repo_tags (list[str]): List of repo + tag pairs that the container images should be loaded under.
        stamp_file (file): File containing image tags that the image should be pushed under.
        visibility (list[str]): Visibility to set on all the targets.
    """
    if visibility == None:
        visibility = ["//visibility:public"]

    platform_transition_filegroup(
        name = name,
        srcs = [image],
        target_platform = select({
            "@platforms//cpu:arm64": "//tools/build_rules:aarch64_linux",
            "@platforms//cpu:x86_64": "//tools/build_rules:x86_64_linux",
        }),
        visibility = visibility,
    )

    oci_tarball(
        name = name + "_tarball",
        image = name,
        repo_tags = repo_tags,
        visibility = visibility,
    )

    oci_push(
        name = name + "_dockerhub",
        image = name,
        remote_tags = stamp_file,
        repository = repository,
        visibility = visibility,
    )
