"""
api_main_py.bzl

A macro used to define a __main__.py used for our API images.
"""

def _api_main_py_impl(ctx):
    main_py_out = ctx.actions.declare_file("__main__.py")
    ctx.actions.expand_template(
        output = main_py_out,
        template = ctx.file._main_py_template,
        substitutions = {
            "{app_package}": ctx.attr.app_package,
        },
    )

    return [DefaultInfo(files = depset([main_py_out]))]

api_main_py = rule(
    implementation = _api_main_py_impl,
    attrs = {
        "app_package": attr.string(mandatory = True),
        "_main_py_template": attr.label(
            default = "__main__.py.tpl",
            allow_single_file = True,
        ),
    },
)
