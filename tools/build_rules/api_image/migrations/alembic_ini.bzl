"""
alembic_ini.bzl

A macro used to define a alembic.ini used for our API migrations.
"""

def _alembic_ini_impl(ctx):
    alembic_ini_out = ctx.actions.declare_file("alembic.ini")
    ctx.actions.expand_template(
        output = alembic_ini_out,
        template = ctx.file._alembic_ini_template,
        substitutions = {},
    )

    return [DefaultInfo(files = depset([alembic_ini_out]))]

alembic_ini = rule(
    implementation = _alembic_ini_impl,
    attrs = {
        "_alembic_ini_template": attr.label(
            default = "__main__.py.tpl",
            allow_single_file = True,
        ),
    },
)
