load("@aspect_rules_webpack//webpack:defs.bzl", "webpack_bundle")
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_push", "oci_tarball")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

# Third-party dependencies required to build our application.
BUILD_DEPS = [
    ":node_modules/@apollo/client",
    ":node_modules/lodash",
    ":node_modules/react",
    ":node_modules/react-canvas-confetti",
    ":node_modules/react-dom",
    ":node_modules/react-router-dom",
]

def _frontend_images_impl(ctx):
    # Defines a set of frontend images for our application.
    # You're probably interested in the oci_tarball & oci_push targets,
    # which build a container image & push it to Docker Hub, respectively.

    nginx_conf_out = ctx.actions.declare_file(ctx.label.name + "_nginx_default.conf")
    ctx.actions.expand_template(
        output = nginx_conf_out,
        template = ctx.file._nginx_conf_template,
        substitutions = {
            "{server_name}": ctx.attr.server_name,
        }
    )

    # Define a container layer for just our nginx configuration.
    pkg_tar(
        name = ctx.label.name + "_nginx_default_tar",
        srcs = [nginx_conf_out],
        package_dir = "/etc/nginx/conf.d",
    )

    # Bundle our application.
    webpack_bundle(
        name = ctx.label + "_webpack",
        node_modules = ctx.attr.node_modules,
        srcs = native.glob(["public/**/*"]) + [":ts", ":tailwindcss"],
        entry_point = "src/index.js",
        deps = BUILD_DEPS + [
            ":node_modules/copy-webpack-plugin",
            ":node_modules/css-loader",
            ":node_modules/file-loader",
            ":node_modules/html-webpack-plugin",
            ":node_modules/process",
            ":node_modules/style-loader",
        ],
        chdir = native.package_name(),
        webpack_config = ctx.attr.webpack_conf,
        output_dir = True,
        env = ctx.attr.build_env,
    )

    # Define a container layer for our application, for use in nginx.
    pkg_tar(
        name = ctx.label + "_webpack_tar",
        srcs = [ctx.label + "_webpack"],
        package_dir = "/usr/share/nginx/html",
        strip_prefix = ctx.label + "_webpack",
    )

    # Define an nginx container image with all of our layers.
    oci_image(
        name = ctx.label + "_image",
        base = ctx.attr._base_image,
        tars = [
            ctx.label + "_webpack_tar",
            ctx.label + "_nginx_default_tar",
        ],
        # Intentionally omit cmd/entrypoint to default to the base nginx container's cmd/entrypoint.
        # entrypoint = [],
        # cmd = [],
    )

    # A runnable target that loads our container image:
    # bazel run //fitbit_challenges/frontend:tarball_prod
    # To run it:
    # docker run --rm shaldengeki/fitbit-challenges-frontend:latest
    oci_tarball(
        name = ctx.label + "_tarball",
        image = ctx.label + "_image",
        repo_tags = ctx.attr.repo_tags,
    )

    # A runnable target that pushes our container image to Docker Hub.
    # bazel run --stamp --embed_label $(git rev-parse HEAD) //fitbit_challenges/frontend:dockerhub_prod
    oci_push(
        name = ctx.label + "_dockerhub",
        image = ctx.label + "_image",
        remote_tags = ctx.attr._stamp_file,
        repository = ctx.attr.docker_hub_repository,
    )

frontend_image = rule(
    implementation = _frontend_images_impl,
    attrs = {
        "server_name": attr.string(mandatory=True),
        "node_modules": attr.label(mandatory=True),
        "webpack_conf": attr.label(
            mandatory = True,
            allow_single_file=True
        ),
        "build_env": attr.string_dict(
            allow_empty = True,
        ),
        "repo_tags": attr.string_list(
            mandatory = True,
            allow_empty = False,
        ),
        "docker_hub_repository": attr.string(
            mandatory = True,
        ),
        "_nginx_conf_template": attr.label(
            default = "templates/nginx.conf.tpl",
            allow_single_file = True,
        ),
        "_base_image": attr.label(
            default = "@nginx_debian_slim",
        ),
        "_stamp_file": attr.label(
            default = "//:stamped",
            allow_single_file=True,
        ),
    }
)