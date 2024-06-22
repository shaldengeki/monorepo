load("@aspect_rules_webpack//webpack:defs.bzl", "webpack_bundle")
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_push", "oci_tarball")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

BUILD_DEPS = [
    ":node_modules/@apollo/client",
    ":node_modules/lodash",
    ":node_modules/react",
    ":node_modules/react-canvas-confetti",
    ":node_modules/react-dom",
    ":node_modules/react-router-dom",
]

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
    pkg_tar(
        name = "nginx_conf_tar",
        srcs = [":nginx/default.conf"],
        package_dir = "/etc/nginx/conf.d",
    )
    for env, config in ENV_CONFIGS.items():
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

        pkg_tar(
            name = "webpack_" + env + "_tar",
            srcs = [":webpack_" + env],
            package_dir = "/usr/share/nginx/html",
            strip_prefix = "webpack_" + env,
        )

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

        # $ bazel run //fitbit_challenges/frontend:tarball_prod
        # $ docker run --rm shaldengeki/fitbit-challenges-frontend:latest
        oci_tarball(
            name = "tarball_" + env,
            image = ":image_" + env,
            repo_tags = ["shaldengeki/fitbit-challenges-frontend:latest"],
        )

        oci_push(
            name = "dockerhub_" + env,
            image = ":image_" + env,
            remote_tags = ["latest"],
            repository = "docker.io/shaldengeki/fitbit-challenges-frontend",
        )
