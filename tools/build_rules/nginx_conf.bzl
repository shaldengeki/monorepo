"""
nginx_conf.bzl

A macro used to define a nginx configuration file used in frontend containers.
"""

def _nginx_conf_impl(ctx):
    nginx_conf_out = ctx.actions.declare_file("default.conf")
    ctx.actions.expand_template(
        output = nginx_conf_out,
        template = ctx.file._nginx_conf_template,
        substitutions = {
            "{server_name}": ctx.attr.server_name,
            "{port}": ctx.attr.port,
        },
    )

    return [DefaultInfo(files = depset([nginx_conf_out]))]

nginx_conf = rule(
    implementation = _nginx_conf_impl,
    attrs = {
        "server_name": attr.string(mandatory = True),
        "port": attr.int(default = 80),
        "_nginx_conf_template": attr.label(
            default = "templates/nginx.conf.tpl",
            allow_single_file = True,
        ),
    },
)
