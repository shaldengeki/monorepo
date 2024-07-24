"""
env_py.bzl

A macro used to define a env.py used for our API migrations.
"""

def _env_py_impl(ctx):
    env_py_out = ctx.actions.declare_file("env.py")
    ctx.actions.expand_template(
        output = env_py_out,
        template = ctx.file._env_py_template,
        substitutions = {},
    )

    return [DefaultInfo(files = depset([env_py_out]))]

env_py = rule(
    implementation = _env_py_impl,
    attrs = {
        "_env_py_template": attr.label(
            default = "env.py.tpl",
            allow_single_file = True,
        ),
    },
)
