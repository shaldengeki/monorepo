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

# Environments that we build our application for.
# Each top-level key defines a new container image.
# "vars" specifies the environment variables that should be present during the build for that environment.
ENV_CONFIGS = {
    "dev": {
        "vars": {},
    },
    "prod": {
        "vars": {
            "REACT_APP_API_HOST": "api.fitbit.ouguo.us",
            "REACT_APP_API_PORT": "443",
            "REACT_APP_API_PROTOCOL": "https",
        },
    },
}

def frontend_images():
    # Defines a set of frontend images for our application.
    # You're probably interested in the oci_tarball & oci_push targets,
    # which build a container image & push it to Docker Hub, respectively.

    # Define a container layer for just our nginx configuration.
    pkg_tar(
        name = "nginx_conf_tar",
        srcs = [":nginx/default.conf"],
        package_dir = "/etc/nginx/conf.d",
    )

    for env, config in ENV_CONFIGS.items():

        # Bundle our application.
        webpack_bundle(
            name = "webpack_" + env,
            node_modules = ":node_modules",
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
            webpack_config = ":webpack.config.js",
            output_dir = True,
            env = config['vars'],
        )

        # Define a container layer for our application, for use in nginx.
        pkg_tar(
            name = "webpack_" + env + "_tar",
            srcs = [":webpack_" + env],
            package_dir = "/usr/share/nginx/html",
            strip_prefix = "webpack_" + env,
        )

        # Define an nginx container image with all of our layers.
        oci_image(
            name = "image_" + env,
            base = "@nginx_debian_slim",
            tars = [
            ":webpack_" + env + "_tar",
            ":nginx_conf_tar",
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
            name = "tarball_" + env,
            image = ":image_" + env,
            repo_tags = ["shaldengeki/fitbit-challenges-frontend:latest"],
        )

        # A runnable target that pushes our container image to Docker Hub.
        # bazel run --stamp --embed_label $(git rev-parse HEAD) //fitbit_challenges/frontend:dockerhub_prod
        oci_push(
            name = "dockerhub_" + env,
            image = ":image_" + env,
            remote_tags = "//:stamped",
            repository = "docker.io/shaldengeki/fitbit-challenges-frontend",
        )
