"""
hugo_extension: a MODULE.lock.bazel extension that defines the @hugo repository.
"""

load("//tools/build_rules/hugo:hugo.bzl", "hugo_dependency")

def _hugo_impl(_ctx):
    hugo_dependency()

hugo_extension = module_extension(
    implementation = _hugo_impl,
)
