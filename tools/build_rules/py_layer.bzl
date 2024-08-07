"Wrapper macro to make three separate layers for python applications"

load("@aspect_bazel_lib//lib:tar.bzl", "mtree_spec", "tar")
load("@rules_oci//oci:defs.bzl", "oci_image")

# match *only* external repositories that have the string "python"
# e.g. this will match
#   `/hello_world/hello_world_bin.runfiles/rules_python~0.21.0~python~python3_9_aarch64-unknown-linux-gnu/bin/python3`
# but not match
#   `/hello_world/hello_world_bin.runfiles/_main/python_app`
PY_INTERPRETER_REGEX = "\\.runfiles/.*python.*-.*"

# match *only* external pip like repositories that contain the string "site-packages"
SITE_PACKAGES_REGEX = "\\.runfiles/.*/site-packages/.*"

def py_layers(name, binaries):
    """Create three layers for a list of py_binary targets: interpreter, third-party dependencies, and application code.

    This allows a container image to have smaller uploads, since the application layer usually changes more
    than the other two.

    Args:
        name: prefix for generated targets, to ensure they are unique within the package
        binaries: a list of py_binary targets
    Returns:
        a list of labels for the layers, which are tar files
    """

    # Produce layers in this order, as the app changes most often
    layers = ["interpreter", "packages", "app"]

    # Produce the manifest for a tar file of our py_binary, but don't tar it up yet, so we can split
    # into fine-grained layers for better docker performance.
    mtree_spec(
        name = name + ".mf",
        srcs = binaries,
        tags = ["manual"],
    )

    native.genrule(
        name = name + ".interpreter_tar_manifest",
        srcs = [name + ".mf"],
        outs = [name + ".interpreter_tar_manifest.spec"],
        cmd = "grep '{}' $< >$@".format(PY_INTERPRETER_REGEX),
        tags = ["manual"],
    )

    native.genrule(
        name = name + ".packages_tar_manifest",
        srcs = [name + ".mf"],
        outs = [name + ".packages_tar_manifest.spec"],
        cmd = "grep '{}' $< >$@".format(SITE_PACKAGES_REGEX),
        tags = ["manual"],
    )

    # Any lines that didn't match one of the two grep above
    native.genrule(
        name = name + ".app_tar_manifest",
        srcs = [name + ".mf"],
        outs = [name + ".app_tar_manifest.spec"],
        cmd = "grep -v '{}' $< | grep -v '{}' >$@".format(SITE_PACKAGES_REGEX, PY_INTERPRETER_REGEX),
        tags = ["manual"],
    )

    result = []
    for layer in layers:
        layer_target = "{}.{}_layer".format(name, layer)
        result.append(layer_target)
        tar(
            name = layer_target,
            srcs = binaries,
            mtree = "{}.{}_tar_manifest".format(name, layer),
            tags = ["manual"],
        )

    return result

def py_oci_image(name, binaries, tars = [], **kwargs):
    """
    Wrapper around oci_image that splits the py_binary into layers.

    Args:
        name: Name that the generated oci_image should have.
        binaries: list of py_binary targets that should be a part of this image.
        tars: (optional) list of tar targets to also bundle into this image.
        **kwargs: Arguments to pass to oci_image.
    """

    oci_image(
        name = name,
        tars = tars + py_layers(name, binaries),
        **kwargs
    )
