"""
frontend_image.bzl

A macro used to define a frontend container image,
built using webpack.
"""

load("@aspect_rules_webpack//webpack:defs.bzl", "webpack_bundle")
load("@rules_oci//oci:defs.bzl", "oci_image")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load("//tools/build_rules:cross_platform_image.bzl", "cross_platform_image")
load("//tools/build_rules:nginx_conf.bzl", "nginx_conf")

# Third-party dependencies required to build our application.
BUILD_DEPS = [
    "//:node_modules/@apollo/client",
    "//:node_modules/history",
    "//:node_modules/lodash",
    "//:node_modules/plotly.js-basic-dist",
    "//:node_modules/react",
    "//:node_modules/react-canvas-confetti",
    "//:node_modules/react-dom",
    "//:node_modules/react-plotlyjs",
    "//:node_modules/react-router-dom",
]

def frontend_image(
        name,
        srcs,
        server_name,
        node_modules,
        webpack_conf,
        repo_tags,
        docker_hub_repository,
        build_env = {},
        base_image = "@nginx_debian_slim",
        stamp_file = "//:stamped",
        webpack_deps = [],
        visibility = None):
    """
    Defines a set of frontend images for our application.

    Args:
        name (str): Prefix to append to the generated targets.
        srcs (list[label]): List of source files (js, css, assets, etc) to include in the build.
        server_name (str): Name of the application to use in the nginx configuration.
        node_modules (label): Target containing the node_modules deps. Should have at least webpack in it.
        webpack_conf (file): Webpack configuration file.
        repo_tags (list[str]): List of repo + tag pairs that the container images should be loaded under.
        docker_hub_repository (str): Repository on Docker Hub that the container images should be pushed to.
        build_env (dict[str, str]): Environment variables to set in the build.
        base_image (label): Base container image to use.
        stamp_file (file): File containing image tags that the image should be pushed under.
        webpack_deps (list[label]): Dependencies to inject into the webpack build.
        visibility (list[str]): Visibility to set on all the targets.

    You're probably interested in the oci_tarball & oci_push targets,
    which build a container image & push it to Docker Hub, respectively.
    """

    if visibility == None:
        visibility = ["//visibility:public"]

    nginx_conf(
        name = name + "_nginx_conf",
        server_name = server_name,
        visibility = visibility,
    )

    # Define a container layer for just our nginx configuration.
    pkg_tar(
        name = name + "_nginx_default_tar",
        srcs = [name + "_nginx_conf"],
        package_dir = "/etc/nginx/conf.d",
        visibility = visibility,
    )

    # Bundle our application.
    webpack_bundle(
        name = name + "_webpack",
        node_modules = node_modules,
        srcs = srcs,
        entry_point = "src/index.js",
        deps = BUILD_DEPS + webpack_deps + [
            "//:node_modules/copy-webpack-plugin",
            "//:node_modules/css-loader",
            "//:node_modules/file-loader",
            "//:node_modules/html-webpack-plugin",
            "//:node_modules/process",
            "//:node_modules/style-loader",
        ],
        chdir = native.package_name(),
        webpack_config = webpack_conf,
        output_dir = True,
        env = build_env,
        visibility = visibility,
    )

    # Define a container layer for our application, for use in nginx.
    pkg_tar(
        name = name + "_webpack_tar",
        srcs = [name + "_webpack"],
        package_dir = "/usr/share/nginx/html",
        strip_prefix = name + "_webpack",
        visibility = visibility,
    )

    # Define an nginx container image with all of our layers.
    oci_image(
        name = name + "_image",
        base = base_image,
        tars = [
            name + "_webpack_tar",
            name + "_nginx_default_tar",
        ],
        # Intentionally omit cmd/entrypoint to default to the base nginx container's cmd/entrypoint.
        # entrypoint = [],
        # cmd = [],
        visibility = visibility,
    )

    cross_platform_image(
        name = name + "_cross_platform_image",
        image = name + "_image",
        repository = docker_hub_repository,
        repo_tags = repo_tags,
        stamp_file = stamp_file,
        visibility = visibility,
    )
