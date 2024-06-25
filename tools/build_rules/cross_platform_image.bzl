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
        stamp_file = "//:stamped"):
    platform_transition_filegroup(
        name = name,
        srcs = [image],
        target_platform = select({
            "@platforms//cpu:arm64": ":aarch64_linux",
            "@platforms//cpu:x86_64": ":x86_64_linux",
        }),
    )

    oci_tarball(
        name = name + "_tarball",
        image = name,
        repo_tags = repo_tags,
    )

    oci_push(
        name = name + "_dockerhub",
        image = name,
        remote_tags = stamp_file,
        repository = repository,
    )
