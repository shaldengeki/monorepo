"""
migrations_files.bzl

A macro used to define files used for our API database migrations.
"""

def _migrations_files_impl(ctx):
    main_py_out = ctx.actions.declare_file("__main__.py")
    ctx.actions.expand_template(
        output = main_py_out,
        template = ctx.file._main_py_template,
        substitutions = {
            "{app_package}": ctx.attr.app_package,
        },
    )

    alembic_ini_out = ctx.actions.declare_file("alembic.ini")
    ctx.actions.expand_template(
        output = alembic_ini_out,
        template = ctx.file._alembic_ini_template,
        substitutions = {},
    )

    env_py_out = ctx.actions.declare_file("env.py")
    ctx.actions.expand_template(
        output = env_py_out,
        template = ctx.file._env_py_template,
        substitutions = {},
    )

    script_py_mako_out = ctx.actions.declare_file("script.py.mako")
    ctx.actions.expand_template(
        output = script_py_mako_out,
        template = ctx.file._script_py_mako_template,
        substitutions = {},
    )

    return [
        DefaultInfo(
            files = depset(
                [
                    main_py_out,
                    alembic_ini_out,
                    env_py_out,
                    script_py_mako_out,
                ],
            ),
        ),
    ]

migrations_files = rule(
    implementation = _migrations_files_impl,
    attrs = {
        "app_package": attr.string(mandatory = True),
        "_main_py_template": attr.label(
            default = "templates/__main__.py.tpl",
            allow_single_file = True,
        ),
        "_alembic_ini_template": attr.label(
            default = "templates/alembic.ini.tpl",
            allow_single_file = True,
        ),
        "_env_py_template": attr.label(
            default = "templates/env.py.tpl",
            allow_single_file = True,
        ),
        "_script_py_mako_template": attr.label(
            default = "templates/script.py.mako.tpl",
            allow_single_file = True,
        ),
    },
)
