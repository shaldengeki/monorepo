load("@bazel_skylib//rules:write_file.bzl", "write_file")
load("@build_bazel_rules_nodejs//:index.bzl", "copy_to_bin", "npm_package_bin")
load("@io_bazel_rules_docker//container:image.bzl", "container_image")
load("@npm//react-scripts:index.bzl", "react_scripts")

# We don't want to teach react-scripts to include from multiple directories
# So we copy everything it wants to read to the output "bin" directory
copy_to_bin(
    name = "copy_static_files",
    srcs = glob([
        "public/*",
        "src/**/*",
    ]) + [
        "package.json",
        "tailwind.config.js",
        "tsconfig.json",
    ],
)

# react-scripts can only work if the working directory is the root of the application.
# So we'll need to chdir before it runs.
write_file(
    name = "write_chdir_script",
    out = "chdir.js",
    content = ["process.chdir(__dirname)"],
)

_RUNTIME_DEPS = [
    "chdir.js",
    "copy_static_files",
    "@npm//@apollo/react-hooks",
    "@npm//@tsconfig/recommended",
    "@npm//apollo-cache-inmemory",
    "@npm//apollo-client",
    "@npm//apollo-link-http",
    "@npm//autoprefixer",
    "@npm//graphql",
    "@npm//graphql-tag",
    "@npm//moment",
    "@npm//postcss",
    "@npm//react",
    "@npm//react-dom",
    "@npm//react-router-dom",
    "@npm//tailwindcss",
    "@npm//web-vitals",
]

react_scripts(
    # Note: If you want to change the name make sure you update BUILD_PATH below accordingly
    # https://create-react-app.dev/docs/advanced-configuration/
    name = "build",
    args = [
        "--node_options=--require=./$(execpath chdir.js)",
        "build",
    ],
    data = _RUNTIME_DEPS + [
        "@npm//@types",
        "tailwind.config.js",
    ],
    env = {
        "BUILD_PATH": "./build",
    },
    output_dir = True,
)

npm_package_bin(
    name = "style_processed",
    tool = "@npm//tailwindcss/bin:tailwindcss",
    data = ["src/index.css", "@npm//@bazel/postcss"],
    args = ["--input=$(rootpath src/index.css)", "--output=$@"],
    outs = ["index_processed.css"],
)

container_image(
    name = "image",
    base = "@nginx_image//image",
    files = [":build", ":index_processed.css"],
    directory = "/usr/share/nginx/html_content",
    symlinks = {
        "/usr/share/nginx/html": "/usr/share/nginx/html_content/build",
        "/usr/share/nginx/html_content/build/index.css": "/usr/share/nginx/html_content/index_processed.css",
    },
)

react_scripts(
    name = "start",
    args = [
        "--node_options=--require=./$(rootpath chdir.js)",
        "start",
    ],
    data = _RUNTIME_DEPS + [
        "tailwind.config.js",
    ],
    tags = [
        # This tag instructs ibazel to pipe into stdin a event describing actions.
        # ibazel send EOF to stdin by default and `react-scripts start` will stop when getting EOF in stdin.
        # So use this to prevent EOF.
        "ibazel_notify_changes",
    ],
)
