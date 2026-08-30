"""
frontend_image.bzl

A macro used to define a frontend container image,
built using webpack.
"""

load("@aspect_rules_webpack//webpack:defs.bzl", "webpack_bundle")
load("@rules_img//img:image.bzl", "image_index", "image_manifest")
load("@rules_img//img:layer.bzl", "layer_from_tar")
load("@rules_img//img:load.bzl", "image_load")
load("@rules_img//img:push.bzl", "image_push")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load("//tools/build_rules:nginx_conf.bzl", "nginx_conf")

# Third-party dependencies required to build our application.
BUILD_DEPS = [
    "//:node_modules/@apollo/client",
    "//:node_modules/d3-array",
    "//:node_modules/d3-collection",
    "//:node_modules/d3-dispatch",
    "//:node_modules/d3-path",
    "//:node_modules/d3-quadtree",
    "//:node_modules/d3-shape",
    "//:node_modules/d3-timer",
    "//:node_modules/elementary-circuits-directed-graph",
    "//:node_modules/history",
    "//:node_modules/lodash",
    "//:node_modules/plotly.js-basic-dist",
    "//:node_modules/react",
    "//:node_modules/react-canvas-confetti",
    "//:node_modules/react-dom",
    "//:node_modules/react-plotly.js",
    "//:node_modules/react-router-dom",
]

def frontend_image(
        name,
        srcs,
        server_name,
        node_modules,
        webpack_conf,
        repository,
        tag,
        registry = "ghcr.io",
        base = "@nginx_mainline_alpine",
        build_env = {},
        webpack_deps = [],
        visibility = None,
        entry_point = "src/index.js",
        tags = None):
    """
    Defines a set of frontend images for our application.

    Args:
        name (str): Prefix to append to the generated targets.
        srcs (list[label]): List of source files (js, css, assets, etc) to include in the build.
        server_name (str): Name of the application to use in the nginx configuration.
        node_modules (label): Target containing the node_modules deps. Should have at least webpack in it.
        webpack_conf (file): Webpack configuration file.
        repository (str): Repository on Docker Hub that the container images should be pushed to.
        tag (str): Tag that the container images should be loaded under.
        registry (str): Container image registry to push to. Defaults to ghcr.io.
        base (label): Base container image to use.
        build_env (dict[str, str]): Environment variables to set in the build.
        webpack_deps (list[label]): Dependencies to inject into the webpack build.
        visibility (list[str]): Visibility to set on all the targets.
        entry_point (file): JS entrypoint file for the image.
        tags (list[str]): List of tags to apply to targets.
    """

    if visibility == None:
        visibility = ["//visibility:public"]

    if tags == None:
        tags = ["manual"]

    nginx_conf(
        name = name + "_nginx_conf",
        server_name = server_name,
        visibility = visibility,
        tags = tags,
    )

    # Define a container layer for just our nginx configuration.
    pkg_tar(
        name = name + "_nginx_default_tar",
        srcs = [name + "_nginx_conf"],
        package_dir = "/etc/nginx/conf.d",
        visibility = visibility,
        tags = tags,
    )

    layer_from_tar(
        name = name + "_layer_nginx",
        src = name + "_webpack_tar",
        compress = "zstd",
        optimize = True,
        tags = tags,
    )

    # Bundle our application.
    webpack_bundle(
        name = name + "_webpack",
        node_modules = node_modules,
        srcs = srcs,
        entry_point = entry_point,
        deps = BUILD_DEPS + webpack_deps + [
            "//:node_modules/copy-webpack-plugin",
            "//:node_modules/css-loader",
            "//:node_modules/file-loader",
            "//:node_modules/html-webpack-plugin",
            "//:node_modules/mini-css-extract-plugin",
            "//:node_modules/process",
            "//:node_modules/style-loader",
        ],
        chdir = native.package_name(),
        webpack_config = webpack_conf,
        output_dir = True,
        env = build_env,
        visibility = visibility,
        tags = tags,
    )

    # Define a container layer for our application, for use in nginx.
    pkg_tar(
        name = name + "_webpack_tar",
        srcs = [name + "_webpack"],
        package_dir = "/usr/share/nginx/html",
        strip_prefix = name + "_webpack",
        visibility = visibility,
        tags = tags,
    )

    layer_from_tar(
        name = name + "_layer_app",
        src = name + "_webpack_tar",
        compress = "zstd",
        optimize = True,
        tags = tags,
    )

    image_manifest(
        name = name,
        base = base,
        layers = [
            name + "_layer_nginx",
            name + "_layer_app",
        ],
        tags = tags,
        visibility = visibility,
    )

    image_index(
        name = name + "_multiarch",
        manifests = [name],  # Single manifest
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
